# -*- coding: utf-8 -*-
r"""Layout 25: where the lead maps score well — the 14 held-out blocks by accuracy (KB §69.81, §69.150).

The paper gives the lead maps' block scores only as intervals (block bootstrap, §69.44) and the U-Net trainings' block
scores as a table (Appendix C). This puts each held-out 15° block on the map, coloured by the accuracy of each lead map
on the third label set's held-out polygons inside it, as score_v3_maps.py measured it (logs\v3_maps.json, v3_polygons,
by_block: pixel accuracy over the block's held-out polygons), beside the nearest-training-polygon baseline.

  data   Ref_HeldOut_Blocks_v3   the 14 blocks as polygons in GCS_Mars_2000 (a block "a_b" is floor(lon / 15)_floor(lat
                                 / 15), longitude -180..180, make_block_split.py), with Block, Polygons (held-out v3
                                 polygons inside, from Landform_TrainingSamples_v3_60_test's Block field), AccUNet,
                                 AccSVM, AccNear; rebuilt on every run
  maps   "Mars ±60° — held-out blocks: U-Net v3", "... : SVM v3"
  layout 25_block_scores   A the U-Net, B the SVM; a table of every block

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy. Run polish_layouts.py afterwards.
"""
import os, sys, time, shutil, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
from layoutkit import text, poly_geom
from make_global60_maps import (outline, add, get_map, order, page, add_text, extent_polygon, CREDIT, BKDIR, OUTD, MARS)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table, hillshade
from make_thermal_change_layout import key

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
LOG = os.path.join(HERE, "logs", "v3_maps.json")
TEST = os.path.join(GDB, "Landform_TrainingSamples_v3_60_test")
FC = os.path.join(GDB, "Ref_HeldOut_Blocks_v3")
L25 = "25_block_scores"
ACC = [(0.40, "under 40 %", (215, 48, 39)), (0.60, "40–60 %", (252, 141, 89)), (0.80, "60–80 %", (254, 224, 139)),
       (0.90, "80–90 %", (145, 207, 96)), (1.01, "90 % and over", (26, 152, 80))]
FA = (0.45, 4.75, 6.50, 2.167)                 # 3:1, the ±60° extent
FB = (0.45, 1.90, 6.50, 2.167)

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def block_box(name):
    a, b = (int(s) for s in name.split("_"))
    x0, y0 = 15.0 * a, 15.0 * b
    pts = [(x0 + t, y0) for t in range(16)] + [(x0 + 15, y0 + t) for t in range(1, 16)] + \
          [(x0 + 15 - t, y0 + 15) for t in range(1, 16)] + [(x0, y0 + 15 - t) for t in range(1, 15)]
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x, y) for x, y in pts]), MARS)


def build_data(R):
    by = R["v3_polygons"]["by_block"]
    n = collections.Counter(r[0] for r in arcpy.da.SearchCursor(TEST, ["Block"]))
    assert sorted(n) == sorted(by) == sorted(R["v3_polygons"]["blocks"]), "blocks differ between the log and the gdb"
    assert sum(n.values()) == R["v3_polygons"]["polygons"], "held-out polygon count differs from the log"
    if arcpy.Exists(FC):
        arcpy.management.Delete(FC)
    arcpy.management.CreateFeatureclass(GDB, os.path.basename(FC), "POLYGON", spatial_reference=MARS)
    for f, t in [("Block", "TEXT"), ("Polygons", "LONG"), ("AccUNet", "DOUBLE"), ("AccSVM", "DOUBLE"), ("AccNear", "DOUBLE")]:
        arcpy.management.AddField(FC, f, t)
    with arcpy.da.InsertCursor(FC, ["SHAPE@", "Block", "Polygons", "AccUNet", "AccSVM", "AccNear"]) as c:
        for b in sorted(by):
            c.insertRow([block_box(b), b, n[b], by[b]["unet_v3"], by[b]["svm_v3"], by[b]["near_v3"]])
    print("   %d blocks, %d polygons" % (len(by), sum(n.values())))
    return by, n


def graduated(layer, field):
    sym = layer.symbology
    sym.updateRenderer("GraduatedColorsRenderer")
    r = sym.renderer
    r.classificationField = field
    r.breakCount = len(ACC)
    for brk, (ub, lab, col) in zip(r.classBreaks, ACC):
        brk.upperBound = ub; brk.label = lab
        brk.symbol.color = {"RGB": list(col) + [100]}
        brk.symbol.outlineColor = {"RGB": [30, 30, 30, 100]}
        brk.symbol.outlineWidth = 0.8
    layer.symbology = sym


def build_map(p, name, field):
    m = get_map(p, name)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.2)
    bl = add(m, FC, "Held-out block, accuracy on its v3 polygons", transparency=10)
    graduated(bl, field)
    hs = hillshade(m)
    order(m, [ext.name, bl.name, hs.name])
    add_graticule(p, name, G30, 7)
    return m


def place(b):
    a, c = (int(s) for s in b.split("_"))
    ew = lambda v: "%d°%s" % (abs(v), "W" if v < 0 else "E") if v else "0°"
    ns = lambda v: "%d°%s" % (abs(v), "S" if v < 0 else "N") if v else "0°"
    return "%s–%s, %s–%s" % (ew(15 * a), ew(15 * a + 15), ns(15 * c), ns(15 * c + 15))


def sheet(p, ma, mb, R, by, n):
    lyt = page(p, L25)
    for (x, y, w, h), m, nm in [(FA, ma, "frame_a"), (FB, mb, "frame_b")]:
        mf = lyt.createMapFrame(poly_geom(x, y, w, h), m, nm)
        mf.camera.setExtent(extent_polygon().projectAs(m.spatialReference).extent)
    full = R["v3_polygons"]["full"]
    pc = lambda v: "%.1f %%" % (100 * v)
    rows = [["block", "where", "polys", "U-Net", "SVM", "nearest"]]
    for b in sorted(by, key=lambda k: -n[k]):
        rows.append([b, place(b), str(n[b]), pc(by[b]["unet_v3"]), pc(by[b]["svm_v3"]), pc(by[b]["near_v3"])])
    lo_u = min(by, key=lambda k: by[k]["unet_v3"])
    svm60 = sorted((k for k in by if by[k]["svm_v3"] >= 0.60), key=lambda k: -by[k]["svm_v3"])
    dark, grey = (40, 40, 40), (70, 70, 70)
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: where the lead maps score well", 18, "title", bold=True),
        text(0.45, 7.47, "The 14 held-out 15° blocks, each coloured by the map's accuracy on the third label set's "
             "held-out polygons inside it ({:,} polygons; KB §69.81).".format(R["v3_polygons"]["polygons"]), 10, "subtitle",
             colour=grey),
        text(0.45, FA[1] + FA[3] + 0.06, "A  The U-Net on the third label set: %s over all blocks"
             % pc(full["unet_v3"]["accuracy"]), 10, "label_a", bold=True),
        text(0.45, FB[1] + FB[3] + 0.06, "B  The support vector machine on the same labels: %s over all blocks"
             % pc(full["svm_v3"]["accuracy"]), 10, "label_b", bold=True),
        text(7.15, 4.95, "Every held-out block, by its polygons", 9.5, "table_title", bold=True, colour=dark),
        text(0.45, 1.20, ("Pixel accuracy over each block's held-out polygons, as the scorer reads them; \"nearest\": "
                          "each pixel given the class of the nearest training polygon.\nThe U-Net's lowest block is %s "
                          "(%s, %s); the support vector machine reaches 60 %% in %d of the 14 (%s).\nBlocks with "
                          "few polygons are the least certain.")
             % (lo_u, place(lo_u), pc(by[lo_u]["unet_v3"]), len(svm60), ", ".join(svm60)), 7.9, "notes", colour=dark),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + key(7.15, 6.95, "Accuracy in the block (A, B)", [(l, c) for _, l, c in ACC], "keya")
        + table(7.15, 4.88, rows, [0.45, 1.15, 0.38, 0.47, 0.45, 0.50], size=6.8))
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L25 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    R = json.load(open(LOG, encoding="utf-8"))
    print("1. data")
    by, n = build_data(R)
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("2. maps")
    ma = build_map(p, "Mars ±60° — held-out blocks: U-Net v3", "AccUNet")
    mb = build_map(p, "Mars ±60° — held-out blocks: SVM v3", "AccSVM")
    print("3. layout", L25)
    sheet(p, ma, mb, R, by, n)
    p.save()
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
