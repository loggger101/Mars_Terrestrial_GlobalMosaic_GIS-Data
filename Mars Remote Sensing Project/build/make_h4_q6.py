# -*- coding: utf-8 -*-
r"""H4 as the prospectus wrote it, and Q6, the one research question never examined (KB §69.132). ArcGIS Python.

    "<ArcGIS Pro Python>" make_h4_q6.py          both tests -> logs\h4_q6.json

Both read the 7-band classification stack (KB §31.2: Viking R, G, B, night IR, day IR, slope, relief; 8-bit, 0 =
no data) at its 1.6 km overview, and the gradient of each band: a 3 x 3 mean, then central differences in metres on
the ground (east-west spacing times cos latitude). "composite" is the multiband gradient of the five spectral bands
(each band divided by its standard deviation, then the root of the summed squared gradients), the gradient of the
visible + thermal mosaic the project is about. Slope (band 6) is the terrain reference: it is not a DN gradient.

H4 (prospectus): "crater rims from DN gradient recover most of the 141 IAU craters > 100 km". The interim answered it
with fill depth instead (68 % of 117, KB §28.11); this tests the method as written. Craters: the IAU gazetteer's
craters >= 100 km centred within 58 deg of the equator (the ring must fit inside the stack). For each, the mean of
the input in annuli of 0.05 R from 0.3 R to 2.0 R (ground distance from the centre). A rim is FOUND when the annulus
with the highest mean between 0.5 R and 1.5 R lies at 0.8-1.2 R and the rim contrast, mean(0.9-1.1 R) /
mean(0.5-0.7 R and 1.3-1.6 R), exceeds the 95th percentile of the same contrast at 1,000 random placements (radii
drawn from the craters', centres within 58 deg and at least 1.5 R from any IAU crater >= 50 km). So chance is <= 5 %
per input. A crater with under 80 % valid pixels inside 2 R is dropped and counted.

Q6 (interim plan §5): "does DN gradient reveal unit boundaries beyond the source image?" Read as: does the composite's
gradient mark the contacts of the USGS geologic map (SIM 3292, units rasterised on a 0.02 deg grid, KB §43) better
than any single source image's does? Contact pixels are those whose 4-neighbour falls in another unit; for each
input, AUC of its gradient within 3 px (~5 km) of a contact against 10-25 px away, the pixels drawn with probability
proportional to cos latitude. Null: the contacts rotated in longitude by 30, 60, ..., 330 deg. Interval: 15 deg
blocks resampled 1,000 times (histograms of each input, 512 quantile bins, summed per block).

Predictions, written 2026-11-12 before the first run:
  H4-1  The composite's gradient finds more than half of the craters (H4 as stated: "most").
  H4-2  Each spectral input finds more craters than its 5 % chance, the binomial 95 % lower bound above 0.05.
  H4-3  Slope finds more craters than the composite, and the composite fewer than fill depth's 68 % (KB §28.11).
  Expected by the agent: H4-1 not held (the mosaics are stretched region by region, §28.10, and degraded rims are
  the commonest, §69.45); H4-2 held for Viking and slope at least; H4-3 held.
  Q6-1  The composite's AUC exceeds that of every single spectral band, the difference over the best one resolved
        (block interval above 0): the composite reveals contacts beyond any one source image.
  Q6-2  Every spectral input's AUC exceeds the largest of its 11 rotated-contact AUCs.
  Q6-3  Slope's AUC exceeds every spectral input's: the contacts are mostly where terrain changes.
  Reading: Q6 is answered "yes" only if Q6-1 holds; Q6-2 failing for a band means its gradient does not mark the
  contacts at all at this scale.
"""
import os, sys, json, math
import numpy as np
from osgeo import gdal, ogr
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import grid60 as G

gdal.UseExceptions(); ogr.UseExceptions()
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
OUT = os.path.join(HERE, "logs", "h4_q6.json")
BANDS = {"Viking red": 1, "Viking green": 2, "Viking blue": 3, "night IR": 4, "day IR": 5}
SPECTRAL = list(BANDS)
RNG = np.random.default_rng(20261112)
STEP = 0.02


def read_stack():
    ds = gdal.Open(STACK)
    gt = ds.GetGeoTransform()
    b1 = ds.GetRasterBand(1)
    k = min(range(b1.GetOverviewCount()), key=lambda i: abs(gt[1] * b1.XSize / b1.GetOverview(i).XSize - 1600))
    arr = {}
    for i in range(1, 8):
        arr[i] = ds.GetRasterBand(i).GetOverview(k).ReadAsArray().astype(np.float32)
    H, W = arr[1].shape
    cell = gt[1] * b1.XSize / W
    ys = gt[3] - (np.arange(H) + .5) * cell
    lat = np.degrees(ys / G.R_MARS)
    xs = gt[0] + (np.arange(W) + .5) * cell
    lon = (180.0 + np.degrees(xs / G.R_MARS) + 180.0) % 360.0 - 180.0
    return arr, cell, lat, lon, gt


def gradients(arr, cell, lat):
    valid = np.ones(arr[1].shape, bool)
    for i in range(1, 8):
        valid &= arr[i] > 0
    valid = ndimage.binary_erosion(valid, np.ones((3, 3), bool), border_value=0)
    coslat = np.cos(np.radians(lat))[:, None]
    out, comp = {}, None
    for name, i in BANDS.items():
        a = np.where(arr[i] > 0, arr[i], np.nan)
        a = a / np.nanstd(a)
        a = ndimage.uniform_filter(np.nan_to_num(a, nan=np.nanmean(a)), 3)
        gy, gx = np.gradient(a)
        gx = gx / (cell * coslat) * 1000.0      # per km on the ground
        gy = gy / cell * 1000.0
        m2 = gx * gx + gy * gy
        out[name] = np.sqrt(m2).astype(np.float32)
        comp = m2 if comp is None else comp + m2
    out["composite"] = np.sqrt(comp).astype(np.float32)
    out["slope"] = arr[6]
    for k in out:
        out[k] = np.where(valid, out[k], np.nan).astype(np.float32)
    return out, valid


def gazetteer():
    """The IAU craters: the gazetteer's two crater layers (> 100 km and < 100 km)."""
    import arcpy
    rows = []
    for lyr in ("MARS_nomenclature_craters_gt100km_March2019", "MARS_nomenclature_craters_lt100km_March2019"):
        with arcpy.da.SearchCursor(os.path.join(GDB, lyr), ["name", "diameter", "center_lat", "center_lon"]) as c:
            for n, d, la, lo in c:
                if d:
                    rows.append((n, float(d), float(la), (float(lo) + 180) % 360 - 180))
    return rows


EDGES = np.arange(0.3, 2.0001, 0.05)
MID = (EDGES[:-1] + EDGES[1:]) / 2


def profile(img, valid, lat, cell, gt, clat, clon, Rkm):
    """Mean of img in annuli of 0.05 R around (clat, clon); None if under 80 % valid inside 2 R."""
    H, W = img.shape
    R = Rkm * 1000.0
    r0 = (gt[3] - G.R_MARS * math.radians(clat)) / cell
    x = G.R_MARS * math.radians((clon - 180.0 + 180.0) % 360.0 - 180.0)
    c0 = (x - gt[0]) / cell
    hy = int(2.05 * R / cell) + 2
    cl = math.cos(math.radians(clat))
    hx = int(2.05 * R / (cell * max(cl, 0.2))) + 2
    rows = np.arange(int(r0) - hy, int(r0) + hy + 1)
    if rows[0] < 0 or rows[-1] >= H:
        return None
    cols = np.arange(int(c0) - hx, int(c0) + hx + 1)
    sub = np.take(img[rows], cols, axis=1, mode="wrap")
    ok = np.take(valid[rows], cols, axis=1, mode="wrap")
    dy = (rows[:, None] + .5 - r0) * cell
    dx = (cols[None, :] + .5 - c0) * cell * np.cos(np.radians(lat[rows]))[:, None]
    r = np.sqrt(dx * dx + dy * dy) / R
    inside = r < 2.0
    if ok[inside].mean() < 0.8:
        return None
    idx = np.digitize(r, EDGES) - 1
    sel = ok & (idx >= 0) & (idx < len(MID)) & np.isfinite(sub)
    s = np.bincount(idx[sel], weights=sub[sel], minlength=len(MID))
    n = np.bincount(idx[sel], minlength=len(MID))
    with np.errstate(invalid="ignore", divide="ignore"):
        return s / n


def rim_stats(p):
    win = (MID >= 0.5) & (MID <= 1.5)
    peak = MID[win][np.nanargmax(p[win])]
    rim = np.nanmean(p[(MID >= 0.9) & (MID <= 1.1)])
    bg = np.nanmean(p[((MID >= 0.5) & (MID <= 0.7)) | ((MID >= 1.3) & (MID <= 1.6))])
    return float(peak), float(rim / bg)


def h4(grads, valid, lat, cell, gt):
    gaz = gazetteer()
    craters = [c for c in gaz if c[1] >= 100 and abs(c[2]) <= 58]
    avoid = [c for c in gaz if c[1] >= 50]
    print("H4: %d IAU craters >= 100 km within 58 deg" % len(craters))
    radii = [c[1] / 2 for c in craters]
    nulls, tries = [], 0
    while len(nulls) < 1000 and tries < 20000:
        tries += 1
        Rk = float(RNG.choice(radii))
        la = math.degrees(math.asin(RNG.uniform(math.sin(math.radians(-58)), math.sin(math.radians(58)))))
        lo = RNG.uniform(-180, 180)
        far = True
        for _, d, a, o in avoid:
            dist = G.R_MARS / 1000 * math.acos(min(1, max(-1, math.sin(math.radians(la)) * math.sin(math.radians(a))
                   + math.cos(math.radians(la)) * math.cos(math.radians(a)) * math.cos(math.radians(lo - o)))))
            if dist < 1.5 * (Rk + d / 2):
                far = False
                break
        if far:
            nulls.append((la, lo, Rk))
    res = {"n_craters": len(craters), "n_null": len(nulls), "inputs": {}}
    for name, img in grads.items():
        null_c = []
        for la, lo, Rk in nulls:
            p = profile(img, valid, lat, cell, gt, la, lo, Rk)
            if p is not None and np.isfinite(p).all():
                null_c.append(rim_stats(p))
        thr = float(np.percentile([c for _, c in null_c], 95))
        chance = float(np.mean([(0.8 <= pk <= 1.2) and c > thr for pk, c in null_c]))
        found, dropped, per = 0, 0, {}
        for n, d, la, lo in craters:
            p = profile(img, valid, lat, cell, gt, la, lo, d / 2)
            if p is None or not np.isfinite(p).all():
                dropped += 1
                continue
            pk, c = rim_stats(p)
            ok = (0.8 <= pk <= 1.2) and c > thr
            found += ok
            per[n] = {"peak_r": pk, "contrast": c, "found": bool(ok)}
        m = len(per)
        lo95 = binom_lower(found, m)
        res["inputs"][name] = {"found": found, "scored": m, "dropped": dropped, "share": found / m,
                               "lower95": lo95, "null_threshold": thr, "chance": chance,
                               "null_scored": len(null_c), "craters": per}
        print("  %-13s found %3d of %3d (%.1f%%, 95%% lower %.1f%%), dropped %d; chance %.1f%% (contrast > %.3f)"
              % (name, found, m, 100 * found / m, 100 * lo95, dropped, 100 * chance, thr))
    I = res["inputs"]
    res["verdicts"] = {
        "H4-1": I["composite"]["share"] > 0.5,
        "H4-2": {k: I[k]["lower95"] > 0.05 for k in SPECTRAL + ["composite"]},
        "H4-3": I["slope"]["share"] > I["composite"]["share"] and I["composite"]["share"] < 0.68}
    return res


def binom_lower(k, n, z=1.959964):
    if n == 0:
        return float("nan")
    p = k / n
    den = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - half) / den           # Wilson


def unit_raster():
    import arcpy
    feats, codes = [], {}
    with arcpy.da.SearchCursor(os.path.join(GDB, "Ref_SIM3292_GeologicUnits"), ["SHAPE@WKT", "Unit"]) as c:
        for wkt, u in c:
            codes.setdefault(u, len(codes) + 1)
            feats.append((wkt, codes[u]))
    mem = ogr.GetDriverByName("MEM").CreateDataSource("u")
    lyr = mem.CreateLayer("u", geom_type=ogr.wkbMultiPolygon)
    lyr.CreateField(ogr.FieldDefn("code", ogr.OFTInteger))
    for wkt, k in feats:
        f = ogr.Feature(lyr.GetLayerDefn()); f.SetGeometry(ogr.CreateGeometryFromWkt(wkt)); f.SetField("code", k)
        lyr.CreateFeature(f)
    W, H = int(360 / STEP), int(120 / STEP)
    ds = gdal.GetDriverByName("MEM").Create("", W, H, 1, gdal.GDT_UInt16)
    ds.SetGeoTransform((-180.0, STEP, 0, 60.0, 0, -STEP))
    gdal.RasterizeLayer(ds, [1], lyr, options=["ATTRIBUTE=code"])
    return ds.ReadAsArray(), len(codes)


def auc_from_hist(hn, hf):
    """P(near > far) + 0.5 P(tie), from histograms on shared bins."""
    cf = np.cumsum(hf) - hf
    tot = hn.sum() * hf.sum()
    return float((hn * (cf + 0.5 * hf)).sum() / tot) if tot else float("nan")


def q6(grads, valid, lat, lon, units_ll):
    H, W = valid.shape
    col = ((lon + 180.0) / STEP).astype(int).clip(0, units_ll.shape[1] - 1)
    row = ((60.0 - lat) / STEP).astype(int).clip(0, units_ll.shape[0] - 1)
    u = units_ll[row[:, None], col[None, :]]

    def contact_dist(uu):
        c = np.zeros(uu.shape, bool)
        for ax in (0, 1):
            d = np.diff(uu.astype(np.int32), axis=ax) != 0
            both = (np.take(uu, range(uu.shape[ax] - 1), axis=ax) > 0) & (np.take(uu, range(1, uu.shape[ax]), axis=ax) > 0)
            e = d & both
            if ax == 0:
                c[:-1] |= e; c[1:] |= e
            else:
                c[:, :-1] |= e; c[:, 1:] |= e
        return ndimage.distance_transform_edt(~c)

    w = np.cos(np.radians(lat))[:, None] * np.ones((1, W))
    keep = valid & (u > 0) & (RNG.random((H, W)) < w)          # cos-latitude thinning
    brow = (((60.0 - lat) // 15).astype(int)).clip(0, 7)
    bcol = (((lon + 180.0) // 15).astype(int)).clip(0, 23)
    block = brow[:, None] * 24 + bcol[None, :]
    names = list(grads)
    edges = {}
    for k in names:
        v = grads[k][keep]
        v = v[np.isfinite(v)]
        edges[k] = np.unique(np.quantile(v, np.linspace(0, 1, 513)))
    def hists(dist):
        near = keep & (dist <= 3)
        far = keep & (dist >= 10) & (dist <= 25)
        out = {}
        for k in names:
            g = grads[k]
            b = np.clip(np.searchsorted(edges[k], g, side="right") - 1, 0, len(edges[k]) - 2)
            nb = len(edges[k]) - 1
            hn = np.zeros((192, nb)); hf = np.zeros((192, nb))
            for sel, h in ((near, hn), (far, hf)):
                s = sel & np.isfinite(g)
                np.add.at(h, (block[s], b[s]), 1)
            out[k] = (hn, hf)
        return out, int(near.sum()), int(far.sum())
    d0 = contact_dist(u)
    real, nn, nf = hists(d0)
    print("Q6: %d near-contact and %d far pixels (after cos-latitude thinning)" % (nn, nf))
    res = {"near_px": nn, "far_px": nf, "auc": {}, "null_max": {}, "null": {}}
    for k in names:
        hn, hf = real[k]
        res["auc"][k] = auc_from_hist(hn.sum(0), hf.sum(0))
    shifts = list(range(30, 360, 30))
    for s in shifts:
        k_px = int(round(s / 360.0 * u.shape[1]))
        ds = np.roll(contact_dist(np.roll(u, k_px, axis=1)), 0, axis=1)
        # rotated contacts, scored on the real pixels: unit membership kept, only the contact lines moved
        nul, _, _ = hists(ds)
        for k in names:
            hn, hf = nul[k]
            res["null"].setdefault(k, []).append(auc_from_hist(hn.sum(0), hf.sum(0)))
    for k in names:
        res["null_max"][k] = max(res["null"][k])
    # block bootstrap of composite minus the best single spectral band, and slope minus composite
    best = max(SPECTRAL, key=lambda k: res["auc"][k])
    boots = {"composite-best": [], "slope-composite": []}
    for _ in range(1000):
        idx = RNG.integers(0, 192, 192)
        a = {k: auc_from_hist(real[k][0][idx].sum(0), real[k][1][idx].sum(0)) for k in ("composite", best, "slope")}
        boots["composite-best"].append(a["composite"] - a[best])
        boots["slope-composite"].append(a["slope"] - a["composite"])
    res["best_single"] = best
    res["intervals"] = {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] for k, v in boots.items()}
    for k in names:
        print("  %-13s AUC %.3f   rotated contacts max %.3f (median %.3f)"
              % (k, res["auc"][k], res["null_max"][k], float(np.median(res["null"][k]))))
    print("  composite - %s: %+.3f, 95%% %s" % (best, res["auc"]["composite"] - res["auc"][best],
          ["%+.3f" % x for x in res["intervals"]["composite-best"]]))
    print("  slope - composite: %+.3f, 95%% %s" % (res["auc"]["slope"] - res["auc"]["composite"],
          ["%+.3f" % x for x in res["intervals"]["slope-composite"]]))
    res["verdicts"] = {
        "Q6-1": all(res["auc"]["composite"] > res["auc"][k] for k in SPECTRAL) and res["intervals"]["composite-best"][0] > 0,
        "Q6-2": {k: res["auc"][k] > res["null_max"][k] for k in SPECTRAL + ["composite"]},
        "Q6-3": all(res["auc"]["slope"] > res["auc"][k] for k in SPECTRAL + ["composite"])}
    return res


if __name__ == "__main__":
    arr, cell, lat, lon, gt = read_stack()
    print("stack read at %.0f m: %d x %d" % (cell, arr[1].shape[1], arr[1].shape[0]))
    grads, valid = gradients(arr, cell, lat)
    del arr
    out = {"cell_m": cell}
    out["H4"] = h4(grads, valid, lat, cell, gt)
    units, n_units = unit_raster()
    print("SIM 3292: %d units rasterised" % n_units)
    out["Q6"] = q6(grads, valid, lat, lon, units)
    out["Q6"]["n_units"] = n_units
    print("\nverdicts:", json.dumps({**out["H4"]["verdicts"], **out["Q6"]["verdicts"]}))
    json.dump(out, open(OUT, "w"), indent=1)
    print("wrote", OUT)
