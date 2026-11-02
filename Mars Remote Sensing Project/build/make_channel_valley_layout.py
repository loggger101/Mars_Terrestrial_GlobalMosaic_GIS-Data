# -*- coding: utf-8 -*-
r"""A1 into the project: the routed channels against the mapped valleys (layout 19; NEXT-STEPS §14 row 5; KB §69.50).

  data   Ref_Valleys_Alemanno2018            Alemanno & Orofino's valley lines (Reference\Alemanno2017_valleys,
                                             SHA-256 checked as in A1), copied into the gdb as they are
         Landform_ChannelCandidates_auto_60_o3   the 44,704 routed segments of Strahler order >= 3, with
                                             ValleyKm5 (km of the segment within 5 km of a mapped valley) and
                                             ValleyShare5 (that share of its length), measured exactly as A1
                                             measures precision (make_channel_valley_check.py: pieces between
                                             vertices on the sphere, valley lines densified to 0.5 km). Check:
                                             the length-weighted share must equal A1's order >= 3 precision at
                                             5 km in logs\channel_valley_check.json, or nothing is drawn.
  map    "Mars ±60° — channels against the valley map"
         the valleys, the order >= 3 segments split at ValleyShare5 = 0.5, over the hillshade, the 30° graticule
  layout 19_channels_vs_valleys
         A the planet at ±60°; B the southern highlands (90°W–0°, 60–30°S), the band where the two maps meet most;
         precision by latitude band and by order and the rotated-map baseline, every number read from A1's log

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy; --fresh rebuilds the two feature
classes. Run polish_layouts.py afterwards, as after every layout builder.
"""
import os, sys, time, shutil, json, hashlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from scipy.spatial import cKDTree
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import make_channel_valley_check as A1
from layoutkit import text, rect, poly_geom
from make_global60_maps import (outline, add, get_map, order, page, add_text, extent_polygon, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table, hillshade

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
LOG = os.path.join(HERE, "logs", "channel_valley_check.json")
VFC = os.path.join(GDB, "Ref_Valleys_Alemanno2018")
O3 = os.path.join(GDB, "Landform_ChannelCandidates_auto_60_o3")
MAPN = "Mars ±60° — channels against the valley map"
L19 = "19_channels_vs_valleys"
ZOOM = (-90.0, -60.0, 0.0, -30.0)                   # lon/lat box of panel B, degrees: the band A1 scores best
VALLEY, ON, OFF = (31, 54, 112), (0, 158, 115), (230, 120, 40)

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def build_data():
    fresh = "--fresh" in sys.argv
    sha = hashlib.sha256(open(A1.VALLEYS, "rb").read()).hexdigest()
    assert sha == A1.VALLEY_SHA, "valley map SHA-256 %s" % sha
    if fresh or not arcpy.Exists(VFC):
        if arcpy.Exists(VFC):
            arcpy.management.Delete(VFC)
        arcpy.conversion.ExportFeatures(A1.VALLEYS, VFC)
    if fresh or not arcpy.Exists(O3):
        if arcpy.Exists(O3):
            arcpy.management.Delete(O3)
        arcpy.analysis.Select(A1.CHANNELS, O3, "StrahlerOrd >= 3")
        arcpy.management.AddField(O3, "ValleyKm5", "DOUBLE")
        arcpy.management.AddField(O3, "ValleyShare5", "DOUBLE")
    # pieces between consecutive vertices, as A1.read_channels, but kept by this class's own OID
    a = arcpy.da.FeatureClassToNumPyArray(O3, ["OID@", "SHAPE@X", "SHAPE@Y"], explode_to_points=True)
    oid, x, y = a["OID@"], a["SHAPE@X"], a["SHAPE@Y"]
    lon = (np.degrees(x / A1.G.R_MARS) + 180.0 + 180.0) % 360.0 - 180.0
    xyz = A1.unit(lon, np.degrees(y / A1.G.R_MARS))
    same = oid[1:] == oid[:-1]
    km = np.linalg.norm(xyz[1:] - xyz[:-1], axis=1) * A1.R_KM
    mid = (xyz[1:] + xyz[:-1]) / 2.0
    mid /= np.linalg.norm(mid, axis=1)[:, None]
    keep = same & (km < 5.0)
    piece_oid, km, mid = oid[1:][keep], km[keep], mid[keep]
    vlon, vlat, _ = A1.read_valleys()
    d = A1.within(cKDTree(A1.unit(vlon, vlat)), mid, 5.0)
    near = d <= 5.0
    ids, inv = np.unique(piece_oid, return_inverse=True)
    tot = np.bincount(inv, weights=km)
    on = np.bincount(inv, weights=km * near)
    R = json.load(open(LOG, encoding="utf-8"))
    share, want = on.sum() / tot.sum(), R["precision"]["order>=3"]["5.0"]
    print("   %d segments, %.0f km (A1: %s km); within 5 km of a valley %.6f (A1: %.6f)"
          % (ids.size, tot.sum(), R["channel_km_order3"], share, want))
    assert abs(share - want) < 1e-9 and abs(tot.sum() - R["channel_km_order3"]) < 1.0, "does not reproduce A1"
    look = dict(zip(ids.tolist(), zip(on.tolist(), (on / np.maximum(tot, 1e-12)).tolist())))
    n = 0
    with arcpy.da.UpdateCursor(O3, ["OID@", "ValleyKm5", "ValleyShare5"]) as cur:
        for r in cur:
            v = look.get(r[0], (0.0, 0.0))                 # a segment with no piece under 5 km has none near
            cur.updateRow([r[0], v[0], v[1]]); n += 1
    print("   ValleyKm5 / ValleyShare5 written to %d rows" % n)
    return R


def line(l, colour, width):
    sym = l.symbology
    sym.renderer.symbol.color = {"RGB": list(colour) + [100]}
    sym.renderer.symbol.size = width
    l.symbology = sym
    return l


def build_map(p):
    m = get_map(p, MAPN)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    on = line(add(m, O3, "Routed, order ≥ 3: mostly within 5 km of a mapped valley"), ON, 1.1)
    on.definitionQuery = "ValleyShare5 >= 0.5"
    va = line(add(m, VFC, "Mapped valleys (Alemanno & Orofino)"), VALLEY, 0.45)
    off = line(add(m, O3, "Routed, order ≥ 3: mostly farther"), OFF, 0.55)
    off.definitionQuery = "ValleyShare5 < 0.5"
    hs = hillshade(m)
    order(m, [ext.name, on.name, va.name, off.name, hs.name])
    add_graticule(p, MAPN, G30, 7)
    return m


def legend(x, y):
    dark = (40, 40, 40)
    els = [text(x, y, "Key", 9.5, "key_title", bold=True, colour=dark)]
    rows = [(ON, 0.06, "routed segment, order ≥ 3, at least half its\nlength within 5 km of a mapped valley"),
            (VALLEY, 0.03, "mapped valley (Alemanno & Orofino)"),
            (OFF, 0.04, "routed segment, order ≥ 3, mostly farther")]
    yy = y - 0.30
    for i, (col, h, lab) in enumerate(rows):
        els.append(rect(x, yy + 0.06, 0.34, h, "key_sw%d" % i, fill=col))
        els.append(text(x + 0.44, yy + 0.02, lab, 8.0, "key_lab%d" % i, colour=dark))
        yy -= 0.36 if "\n" in lab else 0.25
    return els


def sheet(p, m, R):
    lyt = page(p, L19)
    fw, fh = 6.90, 2.30
    mfa = lyt.createMapFrame(poly_geom(0.45, 4.70, fw, fh), m, "frame_a")
    mfa.camera.setExtent(extent_polygon().projectAs(m.spatialReference).extent)
    mfb = lyt.createMapFrame(poly_geom(0.45, 1.72, fw, fh), m, "frame_b")
    mfb.camera.setExtent(arcpy.Extent(*ZOOM, spatial_reference=m.spatialReference))
    pr, b5 = R["precision"]["order>=3"], R["baseline"]["5.0"]
    rec = R["recall"]["order>=3"]
    bands = R["precision_by_lat_band_order>=3_5km"]
    def band(k):                                        # "-60..-45" -> "60–45°S", "-15..+0" -> "15°S–0°"
        a, b = (int(float(s)) for s in k.split(".."))
        hemi = lambda v: "%d°%s" % (abs(v), "S" if v < 0 else "N") if v else "0°"
        return ("%d–%s" % (abs(a), hemi(b)) if a * b > 0 else "%s–%s" % (hemi(a), hemi(b)))

    rows = [["latitude", "order ≥ 3 km", "within 5 km"]]
    for k, v in bands.items():
        rows.append([band(k), "{:,}".format(int(round(v["km"]))), "%.1f %%" % (100 * v["share"])])
    po = R["precision_by_order"]
    orows = [["order", "within 5 km"]] + [[k.replace(">=", "≥ "), "%.1f %%" % (100 * v["5.0"])] for k, v in po.items()]
    dark, grey = (40, 40, 40), (70, 70, 70)
    n_on = sum(1 for _ in arcpy.da.SearchCursor(O3, ["OID@"], "ValleyShare5 >= 0.5"))
    n_all = int(arcpy.management.GetCount(O3)[0])
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: the routed channels against the mapped valleys (A1)", 18, "title", bold=True),
        text(0.45, 7.47, "Strahler order ≥ 3 of the 969,822 routed segments (%s km) against Alemanno & Orofino's "
             "valley lines (%s km inside ±60°)." % ("{:,}".format(R["channel_km_order3"]), "{:,}".format(R["valley_km"])),
             10, "subtitle", colour=grey),
        text(0.45, 4.70 + fh + 0.06, "A  ±60°: %.1f %% within 5 km of a valley; the valley map rotated in "
             "longitude, %.1f %% (%.1f to %.1f %%)"
             % (100 * pr["5.0"], 100 * b5["precision"]["median"], 100 * min(r["5.0"] for r in R["rotations_precision_order>=3"]),
                100 * b5["precision"]["max"]), 10, "label_a", bold=True),
        text(0.45, 1.72 + fh + 0.06, "B  The southern highlands, 90°W–0°, 60–30°S: %.1f %% within 5 km at 45–60°S"
             % (100 * bands["-60..-45"]["share"]), 10, "label_b", bold=True),
        text(7.65, 5.25, "Within 5 km of a valley, by latitude", 9.5, "table_title", bold=True, colour=dark),
        text(7.65, 3.05, "By Strahler order (all orders)", 9.5, "table2_title", bold=True, colour=dark),
        text(0.45, 1.25, ("%s of %s order ≥ 3 segments lie mostly within 5 km of a valley. Recall: %.1f %% of the "
                          "valley length lies\nwithin 5 km of an order ≥ 3 segment (rotated median %.1f %%).")
             % ("{:,}".format(n_on), "{:,}".format(n_all), 100 * rec["5.0"], 100 * b5["recall"]["median"]),
             7.9, "counts", colour=dark),
        text(0.45, 0.62, "The routed segments are the elevation model's drainage paths, not a valley map: most "
             "higher-order length\nruns across the low-latitude volcanic plains, where no valleys are mapped; only the "
             "largest trunks and the\nsouthern highlands meet the valleys well above the rotated baseline. Distances on "
             "the sphere (KB §69.50).", 7.9, "notes", colour=dark),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + legend(7.65, 6.80)
        + table(7.65, 5.17, rows, [0.95, 0.95, 0.90], size=7.8)
        + table(7.65, 2.97, orows, [0.95, 0.90], size=7.8))
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L19 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    print("1. data")
    R = build_data()
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("2. map:", MAPN)
    m = build_map(p)
    print("3. layout", L19)
    sheet(p, m, R)
    p.save()
    print("   %s: %s" % (MAPN, [l.name for l in m.listLayers()]))
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
