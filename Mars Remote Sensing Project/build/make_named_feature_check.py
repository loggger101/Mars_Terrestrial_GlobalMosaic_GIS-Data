# -*- coding: utf-8 -*-
r"""A15: the named-feature check extended to the three new classes (NEXT-STEPS §12.2 A15).

Every map's score carries the IAU-crater check: 'Crater' inside 0.7 R of a named crater against a 1.5-2.5 R ring
(svmcheck.crater_score, KB §30-§31). The seven-class maps add volcanic edifice, apron and fluvial channel, and lava
tube keeps no check of its own. Here, on the two seven-class maps (the SVM at 200 m, 11 x 11 mode, and the U-Net,
both read at the scorer's 400 m), from MARS_nomenclature_misc_March2019 within +-60°, sorted by the first word of
`type`:

  edifice     every Mons, Tholus and Patera: 'volcanic edifice' inside 0.7 R against a 1.5-2.5 R ring, R from
              the gazetteer's `diameter` (the crater rule, the same pixel geometry). Primary set: names whose last
              word is Mons, Tholus, Tholi, Patera or Paterae; Montes (ranges, most of them crater-rim massifs such
              as Ausonia or Charitum Montes) are reported apart.
  fluvial     every Vallis: 'fluvial channel' within 2 km of the Alemanno & Orofino (2017) valley lines inside the
              vallis's extent box (`min_lon`..`max_lat`) against a 10-20 km band around the same lines. A vallis
              with no valley line in its box is counted, not scored.
  lava tube   every Catena, one by one: 'lava tube' inside its extent box against a ring of boxes 1.5-2.5 times
              its half-size about the same centre.

Only names with no v2 label polygon (train or test) at their centre are scored. Even so the check is not
independent: the edifice and fluvial labels were drawn from these names, the SIM 3292 units and the same valley map
(propose_label_changes.py, KB §68.5), so a pass shows the maps consistent with their labels' sources, not accurate.
A feature needs >= 9 valid pixels in each of its two zones, as the crater check does.

Predictions, written before the first run:
  P1  edifice, primary set: on each map 'volcanic edifice' is more common inside than in the ring for more than
      half of the scored names, and its mean inside exceeds its mean in the ring.
  P2  fluvial: on each map 'fluvial channel' is more common within 2 km of the lines than in the 10-20 km band for
      more than half of the scored valles, and its mean near the lines exceeds its mean in the band.
  P3  lava tube: listed, n <= 8, no verdict.
Each is reported held or not held per map; none is adjusted after the run.
Added after the first run (2026-11-01), as diagnostics that change no verdict: each scored edifice name's SIM 3292
unit at its centre and every class's share inside its 0.7 R disc, because P1 failed on both maps.

Checks that the check can fail:
  --shift DEG    rolls each map DEG degrees in longitude before scoring (the misregistration of KB §16's three
                 frames); at 180 the inside-over-ring shares should fall towards one half. Written to *_shift<DEG>.
  --self-test    scores the IAU craters >= 5 km with this script's ring function and the scorer's exclusion boxes
                 and requires svmcheck.crater_score's numbers exactly, on both maps.

  "<ArcGIS Pro Python>" make_named_feature_check.py [--shift 180] [--self-test]
Reads the cached 400 m class arrays verify_global60_classification.py wrote (refuses one older than its raster) and
the gdb. Writes logs\named_feature_check_v2.json. Read-only on the drive's data.
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from scipy.ndimage import distance_transform_edt
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from svmcheck import KPD, crater_score
from labelsets import SEVEN

MARS = arcpy.SpatialReference(104905)
GAZ = "MARS_nomenclature_misc_March2019"
VALLEYS = on_drive(r"Mars Project\Reference\Alemanno2017_valleys\Giulia Valleys.shp")
LABELS = ["Landform_TrainingSamples_v2_60_train", "Landform_TrainingSamples_v2_60_test"]
MAPS = [("svm_v2", "global60_landforms_v2_200m_mode11_ov400.npy",
         r"Mars Project\Global60\global60_landforms_svm_v2_200m_mode11.tif"),
        ("unet_v2", "global60_landforms_global60_landforms_unet_v2_200m_seamfix_ov400.npy",
         r"Mars Project\Global60\global60_landforms_unet_v2_200m_seamfix.tif")]
EDIFICE, APRON, FLUVIAL, TUBE = (SEVEN.index(n) for n in ("volcanic edifice", "apron", "fluvial channel",
                                                          "lava tube"))
NEAR_KM, BAND_KM = 2.0, (10.0, 20.0)
MIN_PX = 9
SHIFT = float(sys.argv[sys.argv.index("--shift") + 1]) if "--shift" in sys.argv else 0.0
OUT = os.path.join(HERE, "logs", "named_feature_check_v2%s.json" % ("_shift%g" % SHIFT if SHIFT else ""))


def load(npy, tif):
    p, t = os.path.join(HERE, npy), on_drive(tif)
    if os.path.getmtime(p) < os.path.getmtime(t):
        sys.exit("%s is older than %s: rerun verify_global60_classification.py on it first" % (npy, tif))
    a = np.load(p, mmap_mode="r")
    if SHIFT:
        a = np.roll(a, int(round(SHIFT / 360.0 * a.shape[1])), axis=1)
    H, W = a.shape
    g = dict(dpx=360.0 / W, dpy=2 * G.G100.lat_of(G.G100.oy) / H,
             lat_top=G.G100.lat_of(G.G100.oy), lon_left=G.G100.lon_of(G.G100.ox))
    return a, a != 255, g


def l180(x):
    return (x + 180) % 360 - 180


def disc_ring(a, m, g, clat, clon, R, cls):
    """crater_score's geometry for one feature of radius R km and any class: the class's share inside 0.7 R and in
    the 1.5-2.5 R ring, or None where crater_score would skip it (too near the extent's edge, < 9 pixels)."""
    H, W = a.shape
    rlat = R / KPD; rlon = rlat / max(np.cos(np.radians(clat)), .05)
    if abs(clat) + 2.5 * rlat > g["lat_top"] - .5:
        return None
    cc0 = ((clon % 360 - g["lon_left"]) % 360) / g["dpx"]; rc0 = (g["lat_top"] - clat) / g["dpy"]
    hw = int(np.ceil(2.5 * rlon / g["dpx"])) + 1; hh = int(np.ceil(2.5 * rlat / g["dpy"])) + 1
    r0, r1 = int(rc0) - hh, int(rc0) + hh + 1
    if r0 < 0 or r1 > H:
        return None
    cols = np.arange(int(cc0) - hw, int(cc0) + hw + 1)
    win = a[r0:r1][:, cols % W]; wm = m[r0:r1][:, cols % W]
    dy = (np.arange(r0, r1) + .5 - rc0) * g["dpy"]; dx = (cols + .5 - cc0) * g["dpx"]
    dist = np.hypot(dy[:, None] * KPD, dx[None, :] * KPD * np.cos(np.radians(clat - dy[:, None]))) / R
    ins = (dist < .7) & wm; ring = (dist > 1.5) & (dist < 2.5) & wm
    if ins.sum() < MIN_PX or ring.sum() < MIN_PX:
        return None
    top = np.bincount(win[ins], minlength=len(SEVEN)) / ins.sum()        # every class's share inside
    return (float((win[ins] == cls).mean()), float((win[ring] == cls).mean()), int(ins.sum()), int(ring.sum()),
            top)


def window(g, H, W, lat0, lat1, lon0, lon1):
    """Rows r0:r1 and the column indices (unwrapped, take % W) covering lat0..lat1, lon0..lon1 (lon1 may pass 360)."""
    r0 = max(int(np.floor((g["lat_top"] - lat1) / g["dpy"])), 0)
    r1 = min(int(np.ceil((g["lat_top"] - lat0) / g["dpy"])), H)
    c0 = int(np.floor(((lon0 % 360 - g["lon_left"]) % 360) / g["dpx"]))
    c1 = c0 + int(np.ceil((lon1 - lon0) / g["dpx"])) + 1
    return r0, r1, np.arange(c0, c1)


def box_ring(a, m, g, f, cls):
    """The class's share inside the extent box and in boxes 1.5-2.5 times its half-size about the same centre."""
    H, W = a.shape
    lat0, lat1 = f["min_lat"], f["max_lat"]
    w = (f["max_lon"] - f["min_lon"]) % 360
    clat, clon = (lat0 + lat1) / 2, f["min_lon"] + w / 2
    hy, hx = (lat1 - lat0) / 2, w / 2
    if abs(clat) + 2.5 * hy > g["lat_top"] - .5:
        return None
    r0, r1, cols = window(g, H, W, clat - 2.5 * hy, clat + 2.5 * hy, clon - 2.5 * hx, clon + 2.5 * hx)
    win = a[r0:r1][:, cols % W]; wm = m[r0:r1][:, cols % W]
    lat = g["lat_top"] - (np.arange(r0, r1) + .5) * g["dpy"]
    lon = g["lon_left"] + (cols + .5) * g["dpx"]
    u = np.abs(lat - clat)[:, None] / max(hy, 1e-9)
    v = np.abs(l180(lon - clon))[None, :] / max(hx, 1e-9)
    s = np.maximum(u, v)                                          # 1 on the box's edge
    ins = (s <= 1) & wm; ring = (s > 1.5) & (s <= 2.5) & wm
    if ins.sum() < MIN_PX or ring.sum() < MIN_PX:
        return None
    return float((win[ins] == cls).mean()), float((win[ring] == cls).mean()), int(ins.sum()), int(ring.sum())


def valley_points(step):
    """Every Alemanno valley line in GCS_Mars_2000, densified to <= step degrees: (lon -180..180, lat)."""
    xs, ys = [], []
    with arcpy.da.SearchCursor(VALLEYS, ["SHAPE@"], spatial_reference=MARS) as c:
        for (shp,) in c:
            for part in shp:
                xy = np.array([(p.X, p.Y) for p in part if p is not None], float)
                for (x0, y0), (x1, y1) in zip(xy[:-1], xy[1:]):
                    dx = l180(x1 - x0)
                    n = max(int(np.ceil(max(abs(dx), abs(y1 - y0)) / step)), 1)
                    t = np.arange(n + 1) / n
                    xs.append(l180(x0 + t * dx)); ys.append(y0 + t * (y1 - y0))
    return np.concatenate(xs), np.concatenate(ys)


def near_band(a, m, g, f, vx, vy, cls):
    """The class's share within NEAR_KM of the valley lines inside the vallis's box, and in the BAND_KM band around
    the same lines; None when the box holds no line or a zone has < 9 pixels."""
    H, W = a.shape
    lat0, lat1 = f["min_lat"], f["max_lat"]
    w = (f["max_lon"] - f["min_lon"]) % 360
    lon0 = f["min_lon"] % 360
    sel = ((vy >= lat0) & (vy <= lat1) & (((vx - lon0) % 360) <= w))
    if not sel.any():
        return "no line"
    clat = (lat0 + lat1) / 2
    pad_lat = (BAND_KM[1] + 1) / KPD
    pad_lon = pad_lat / max(np.cos(np.radians(max(abs(lat0), abs(lat1)) + pad_lat)), .05)
    if max(abs(lat0), abs(lat1)) + pad_lat > g["lat_top"] - .5:
        return None
    r0, r1, cols = window(g, H, W, lat0 - pad_lat, lat1 + pad_lat, lon0 - pad_lon, lon0 + w + pad_lon)
    win = a[r0:r1][:, cols % W]; wm = m[r0:r1][:, cols % W]
    line = np.zeros(win.shape, bool)
    rr = ((g["lat_top"] - vy[sel]) / g["dpy"]).astype(int) - r0
    cc = (((vx[sel] % 360 - g["lon_left"]) % 360) / g["dpx"]).astype(int)
    cc = (cc - cols[0]) % W
    ok = (rr >= 0) & (rr < line.shape[0]) & (cc < line.shape[1])
    line[rr[ok], cc[ok]] = True
    d = distance_transform_edt(~line, sampling=(g["dpy"] * KPD, g["dpx"] * KPD * np.cos(np.radians(clat))))
    lat = g["lat_top"] - (np.arange(r0, r1) + .5) * g["dpy"]
    lon = (g["lon_left"] + (cols + .5) * g["dpx"]) % 360
    inbox = ((lat >= lat0) & (lat <= lat1))[:, None] & ((((lon - lon0) % 360) <= w))[None, :]
    near = (d <= NEAR_KM) & inbox & wm
    band = (d > BAND_KM[0]) & (d <= BAND_KM[1]) & wm
    if near.sum() < MIN_PX or band.sum() < MIN_PX:
        return None
    return float((win[near] == cls).mean()), float((win[band] == cls).mean()), int(near.sum()), int(band.sum())


def unit_at(lat, lon):
    """The SIM 3292 unit and unit group under a point, or ("", "")."""
    pt = arcpy.PointGeometry(arcpy.Point(l180(lon), lat), MARS)
    with arcpy.da.SearchCursor(os.path.join(GDB, "Ref_SIM3292_GeologicUnits"), ["Unit", "UnitGroup"],
                               spatial_filter=pt) as c:
        for u, grp in c:
            return u, grp
    return "", ""


def label_polygons():
    out = []
    for fc in LABELS:
        with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@"], spatial_reference=MARS) as c:
            out += [s for (s,) in c]
    return out


def at_label(polys, lat, lon):
    pt = arcpy.PointGeometry(arcpy.Point(l180(lon), lat), MARS)
    for p in polys:
        e = p.extent
        if e.XMin <= l180(lon) <= e.XMax and e.YMin <= lat <= e.YMax and p.contains(pt):
            return True
    return False


def gazetteer(lat_top):
    rows = []
    flds = ["name", "clean_name", "type", "diameter", "center_lat", "center_lon",
            "min_lon", "max_lon", "min_lat", "max_lat"]
    with arcpy.da.SearchCursor(os.path.join(GDB, GAZ), flds) as c:
        for r in c:
            f = dict(zip(flds, r))
            f["kind"] = f["type"].split(",")[0].split()[0].strip()
            if abs(f["center_lat"]) <= 60:
                rows.append(f)
    return rows


def summary(scored, label, verdict=True):
    if not scored:
        return dict(n=0)
    fin = np.array([s["inside"] for s in scored]); frg = np.array([s["outside"] for s in scored])
    pct = 100 * (fin > frg).mean()
    held = bool(pct > 50 and fin.mean() > frg.mean())
    print("  %-34s n %3d  inside %.3f vs outside %.3f; inside > outside %.1f%%  -> %s"
          % (label, len(fin), fin.mean(), frg.mean(), pct,
             ("held" if held else "NOT held") if verdict else "no verdict"))
    out = dict(n=len(fin), inside_mean=round(float(fin.mean()), 3), outside_mean=round(float(frg.mean()), 3),
               pct_inside_gt_outside=round(float(pct), 1))
    if verdict:
        out["held"] = held
    return out


def self_test(polys_all):
    """This script's ring function against svmcheck.crater_score on the IAU craters, both maps."""
    craters = []
    for fc in ["MARS_nomenclature_craters_lt100km_March2019", "MARS_nomenclature_craters_gt100km_March2019"]:
        with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["name", "diameter", "center_lat", "center_lon"]) as c:
            craters += list(c)
    tbox = np.array([[p.extent.XMin, p.extent.XMax, p.extent.YMin, p.extent.YMax] for p in polys_all])
    for key, npy, tif in MAPS:
        a, m, g = load(npy, tif)
        fin, frg = crater_score(a, m, g, craters, tbox)
        mine = []
        for name, D, clat, clon in craters:
            if D is None or D < 5:
                continue
            R = D / 2; rlat = R / KPD; rlon = rlat / max(np.cos(np.radians(clat)), .05); x = l180(clon)
            if ((tbox[:, 0] <= x + 2.5 * rlon) & (tbox[:, 1] >= x - 2.5 * rlon) &
                    (tbox[:, 2] <= clat + 2.5 * rlat) & (tbox[:, 3] >= clat - 2.5 * rlat)).any():
                continue
            s = disc_ring(a, m, g, clat, clon, R, 0)
            if s:
                mine.append(s[:2])
        mine = np.array(mine)
        same = len(mine) == len(fin) and np.array_equal(mine[:, 0], fin) and np.array_equal(mine[:, 1], frg)
        print("self-test %s: crater_score n %d (%.3f vs %.3f), this script n %d (%.3f vs %.3f): %s"
              % (key, len(fin), fin.mean(), frg.mean(), len(mine), mine[:, 0].mean(), mine[:, 1].mean(),
                 "identical" if same else "DIFFERENT"))
        if not same:
            sys.exit(1)


def main():
    t0 = time.time()
    polys_all = label_polygons()
    print("%d v2 label polygons" % len(polys_all))
    if "--self-test" in sys.argv:
        self_test(polys_all)
        return
    lat_top = G.G100.lat_of(G.G100.oy)
    gaz = gazetteer(lat_top)
    for f in gaz:
        f["at_label"] = at_label(polys_all, f["center_lat"], f["center_lon"])
        if f["kind"] in ("Mons", "Tholus", "Patera") and not f["at_label"]:
            f["unit"], f["unit_group"] = unit_at(f["center_lat"], f["center_lon"])
    sets = {}
    for f in gaz:
        last = f["clean_name"].split()[-1]
        if f["kind"] in ("Mons", "Tholus", "Patera"):
            sets.setdefault("edifice" if last in ("Mons", "Tholus", "Tholi", "Patera", "Paterae")
                            else "edifice_montes", []).append(f)
        elif f["kind"] == "Vallis":
            sets.setdefault("fluvial", []).append(f)
        elif f["kind"] == "Catena":
            sets.setdefault("lava_tube", []).append(f)
    res = dict(shift_deg=SHIFT, near_km=NEAR_KM, band_km=list(BAND_KM), counts={})
    for k, fs in sets.items():
        res["counts"][k] = dict(within_60=len(fs), no_label_at_centre=sum(not f["at_label"] for f in fs))
    print("names within +-60 (no v2 label at centre):",
          {k: "%d (%d)" % (v["within_60"], v["no_label_at_centre"]) for k, v in res["counts"].items()})
    print("valley points ...", end=" ", flush=True)
    a0, _, g0 = load(*MAPS[0][1:])
    vx, vy = valley_points(g0["dpx"] / 4)
    del a0
    print("%d (%.0f s)" % (len(vx), time.time() - t0))

    for key, npy, tif in MAPS:
        a, m, g = load(npy, tif)
        w = np.cos(np.radians(g["lat_top"] - (np.arange(a.shape[0]) + .5) * g["dpy"]))
        share = np.zeros(len(SEVEN))
        for i in range(0, a.shape[0], 2000):
            blk = a[i:i + 2000]; mm = blk != 255
            share += np.bincount(blk[mm], weights=np.broadcast_to(w[i:i + 2000, None], blk.shape)[mm],
                                 minlength=len(SEVEN))
        share /= share.sum()
        out = dict(map=tif, area_share=dict(zip(SEVEN, share.round(4).tolist())))
        print("\n%s  (area shares: edifice %.3f, fluvial %.3f, lava tube %.3f)"
              % (key, share[EDIFICE], share[FLUVIAL], share[TUBE]))
        for k, fs in sorted(sets.items()):
            cls = dict(edifice=EDIFICE, edifice_montes=EDIFICE, fluvial=FLUVIAL, lava_tube=TUBE)[k]
            scored, skipped = [], dict(label_at_centre=0, no_line=0, edge_or_small=0)
            for f in fs:
                if f["at_label"]:
                    skipped["label_at_centre"] += 1
                    continue
                if k.startswith("edifice"):
                    s = disc_ring(a, m, g, f["center_lat"], f["center_lon"], f["diameter"] / 2, cls)
                elif k == "fluvial":
                    s = near_band(a, m, g, f, vx, vy, cls)
                else:
                    s = box_ring(a, m, g, f, cls)
                if s == "no line":
                    skipped["no_line"] += 1
                elif s is None:
                    skipped["edge_or_small"] += 1
                else:
                    row = dict(name=f["clean_name"], lat=round(f["center_lat"], 2),
                               lon=round(f["center_lon"], 2), diameter_km=round(f["diameter"], 1),
                               inside=round(s[0], 4), outside=round(s[1], 4), px_inside=s[2], px_outside=s[3])
                    if k.startswith("edifice"):
                        row.update(unit=f["unit"], unit_group=f["unit_group"],
                                   inside_classes=dict(zip(SEVEN, s[4].round(3).tolist())))
                    scored.append(row)
            out[k] = dict(summary(scored, "%s (%s)" % (k, SEVEN[cls]), k != "lava_tube"), skipped=skipped,
                          features=sorted(scored, key=lambda s: s["name"]))
            if k.startswith("edifice"):
                for s in out[k]["features"]:
                    t = max(s["inside_classes"], key=s["inside_classes"].get)
                    print("      %-22s %5.0f km  unit %-6s (%-2s)  edifice inside %.3f vs ring %.3f; inside most "
                          "%s %.2f" % (s["name"], s["diameter_km"], s["unit"], s["unit_group"], s["inside"],
                                       s["outside"], t, s["inside_classes"][t]))
            if k == "lava_tube":
                for s in out[k]["features"]:
                    print("      %-22s %6.1f km  lava tube inside %.3f vs ring %.3f"
                          % (s["name"], s["diameter_km"], s["inside"], s["outside"]))
        res[key] = out
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("\nwrote %s  (%.0f s)" % (OUT, time.time() - t0))


if __name__ == "__main__":
    main()
