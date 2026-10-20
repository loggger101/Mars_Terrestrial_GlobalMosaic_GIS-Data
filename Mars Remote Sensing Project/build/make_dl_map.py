# -*- coding: utf-8 -*-
r"""X5's held-out detections into the gdb and the .aprx (KB §66.2, §66.3).

  DL_Detections_heldout_20261019   the 1,838 RetinaNet boxes kept by make_dl_model.py --detect (one
                                   window per held-out 15° block), copied from the shapefile beside the
                                   model; fields Class, Classvalue, Confidence, Model, MappedBy
  map "X5 — deep-learning detections (held out)"
                                   the boxes outlined in the class colours over the held-out hand-drawn
                                   labels (filled faintly in the same colours), the 30° graticule, the
                                   ±60° hillshade; the training labels off, for context
  layout 16_x5_detections          the map twice: ±60° (where the 14 held-out blocks are) and the block with
                                   the most held-out polygons; the per-polygon score of logs\dl_heldout_score.json
                                   beside each class's one-class rate, computed here (KB §66.4); the limits.
                                   Its numbers go to logs\dl_sheet.json.

The feature class is written in the stack's own SR with its XY domain widened by 400 km: a default-domain
class refuses a box past the 0°E edge of the CM 180 grid (KB §66.2). One holding rows another script
wrote is never replaced. Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a
copy beside the real .aprx (§31.5).
"""
import os, sys, time, shutil, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from layoutkit import text, poly_geom
from make_global60_maps import (outline, by_class, add, get_map, order, page, add_text, legend_classes,
                                extent_polygon, CLASS_COLOURS, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
MARKER = "make_dl_map.py"
STAMP = "20261019"
MODEL = "global60_retinanet_%s" % STAMP
SRC = on_drive(r"Mars Project\DLModels\%s\detections_heldout_%s\dl_detections_heldout_%s.shp" % (MODEL, STAMP, STAMP))
FC = os.path.join(GDB, "DL_Detections_heldout_%s" % STAMP)
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
MAP = "X5 — deep-learning detections (held out)"
VALUES = {"Crater": 1, "steep/windy hills": 2, "lava tube": 3, "Normal Ground": 4}
TEST = os.path.join(GDB, "Landform_TrainingSamples_terrain_60_test")
SCORE = os.path.join(HERE, "logs", "dl_heldout_score.json")
EMD = on_drive(r"Mars Project\DLModels\%s\%s.emd" % (MODEL, MODEL))
SHEET_LOG = os.path.join(HERE, "logs", "dl_sheet.json")
L16 = "16_x5_detections"
TABLE_W16 = [1.30, 0.78, 0.86, 0.95, 0.96, 1.10]    # 5.95 in: x 4.60 to the 10.55 in margin

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def copy_detections():
    if arcpy.Exists(FC):
        with arcpy.da.SearchCursor(FC, ["MappedBy"]) as c:
            if not all(r[0] == MARKER for r in c):
                sys.exit("REFUSING: %s holds rows this script did not write" % FC)
        arcpy.management.Delete(FC)
    sr = arcpy.Describe(STACK).spatialReference
    e = arcpy.Describe(STACK).extent
    sr.setDomain(e.XMin - 4e5, e.XMax + 4e5, e.YMin - 4e5, e.YMax + 4e5)
    arcpy.management.CreateFeatureclass(GDB, os.path.basename(FC), "POLYGON", spatial_reference=sr)
    for name, typ, n in (("Class", "TEXT", 32), ("Classvalue", "SHORT", None), ("Confidence", "DOUBLE", None),
                         ("Model", "TEXT", 64), ("MappedBy", "TEXT", 40)):
        arcpy.management.AddField(FC, name, typ, field_length=n)
    rows = 0
    with arcpy.da.SearchCursor(SRC, ["SHAPE@", "Class", "Confidence"]) as src, \
            arcpy.da.InsertCursor(FC, ["SHAPE@", "Class", "Classvalue", "Confidence", "Model", "MappedBy"]) as dst:
        for g, k, p in src:
            dst.insertRow([g, k, VALUES[k], p, MODEL, MARKER]); rows += 1
    n_src = int(arcpy.management.GetCount(SRC)[0])
    assert rows == n_src == int(arcpy.management.GetCount(FC)[0]), "row count differs from the shapefile"
    a, b = arcpy.Describe(SRC).extent, arcpy.Describe(FC).extent
    assert max(abs(a.XMin - b.XMin), abs(a.YMin - b.YMin), abs(a.XMax - b.XMax), abs(a.YMax - b.YMax)) < 1.0, \
        "extent differs from the shapefile"
    print("   %s: %d boxes, extent matches the shapefile" % (os.path.basename(FC), rows))


def by_class_field(layer, field, width, fill=0):
    """Polygons outlined in the class colours, filled at `fill` % opacity."""
    sym = layer.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = [field]
    for grp in sym.renderer.groups:
        for it in grp.items:
            col = list(CLASS_COLOURS.get(it.values[0][0], (255, 255, 255)))
            it.symbol.color = {"RGB": col + [fill]}
            it.symbol.outlineColor = {"RGB": col + [100]}
            it.symbol.outlineWidth = width
    layer.symbology = sym


def sheet_numbers():
    """Everything layout 16 prints: the score log as it stands, the one-class rates and the busiest block,
    both computed from the gdb class and the held-out labels, and the model's validation AP from its .emd."""
    s = json.load(open(SCORE))
    assert s["layer"].endswith(os.path.basename(FC)) and s["detections"] == int(arcpy.management.GetCount(FC)[0]), \
        "dl_heldout_score.json does not describe %s: run make_dl_model.py --score on it" % FC
    sr = arcpy.Describe(FC).spatialReference
    with arcpy.da.SearchCursor(TEST, ["SHAPE@", "Classname"], spatial_reference=sr) as c:
        polys = [(g, k) for g, k in c]
    inside = collections.Counter()                   # polygon class of every box centred in a held-out polygon
    by_class = collections.Counter()
    with arcpy.da.SearchCursor(FC, ["SHAPE@", "Class"]) as c:
        for d, k in c:
            by_class[k] += 1
            pt = arcpy.PointGeometry(d.centroid, sr)
            hit = next((v for g, v in polys if g.contains(pt)), None)
            if hit:
                inside[hit] += 1
    n_in = sum(inside.values())
    one_class = {k: inside[k] / n_in for k in VALUES}
    # the block with the most held-out polygons, in the map's geographic coordinates
    blocks = collections.defaultdict(list)
    with arcpy.da.SearchCursor(TEST, ["SHAPE@"]) as c:          # native geographic
        for (g,) in c:
            blocks[(int(g.centroid.X // 15) * 15, int(g.centroid.Y // 15) * 15)].append(g.extent)
    k, ex = max(blocks.items(), key=lambda kv: len(kv[1]))
    zoom = [min(e.XMin for e in ex), min(e.YMin for e in ex), max(e.XMax for e in ex), max(e.YMax for e in ex)]
    ap = json.load(open(EMD))["average_precision_score"]
    out = {"when": time.strftime("%Y-%m-%d %H:%M"), "score": s, "boxes_by_class": dict(by_class),
           "boxes_in_heldout_polygons": n_in, "in_polygons_by_polygon_class": dict(inside),
           "one_class_precision": one_class, "zoom_block": {"lon": k[0], "lat": k[1], "polygons": len(ex),
           "extent_deg": zoom}, "validation_ap": ap, "blocks": len(blocks)}
    json.dump(out, open(SHEET_LOG, "w"), indent=1)
    return out


def sheet(p, m, det, tst):
    n = sheet_numbers()
    s, oc, z = n["score"], n["one_class_precision"], n["zoom_block"]
    lyt = page(p, L16)
    fw = 7.35; fh = fw / 3.0
    mfa = lyt.createMapFrame(poly_geom(0.45, 4.62, fw, fh), m, "frame_all")
    mfa.camera.setExtent(extent_polygon().projectAs(m.spatialReference).extent)
    zw, zh = 3.90, 3.05
    mfb = lyt.createMapFrame(poly_geom(0.45, 1.15, zw, zh), m, "frame_block")
    pad = 0.3
    mfb.camera.setExtent(arcpy.Extent(z["extent_deg"][0] - pad, z["extent_deg"][1] - pad,
                                      z["extent_deg"][2] + pad, z["extent_deg"][3] + pad))
    pc = lambda v: "—" if v is None else "%.1f %%" % (100 * v)
    rows = [["class", "held out", "recall", "boxes inside", "precision", "one-class rate"]]
    for k in ("Crater", "Normal Ground", "steep/windy hills", "lava tube"):
        r, pr = s["recall"][k], s["precision"][k]
        rows.append([k, "%d" % s["recall_n"][k], pc(r), "%d" % s["precision_n"][k], pc(pr),
                     pc(oc[k]) if pr is not None else "—"])
    lon = lambda v: "%d°E" % (v % 360)
    lat = lambda v: "%d°%s" % (abs(v), "N" if v > 0 else "S") if v else "0°"
    dark, grey = (40, 40, 40), (70, 70, 70)
    ap = n["validation_ap"]
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60° — a deep-learning detector, scored on held-out ground (X5)", 19, "title",
             bold=True),
        text(0.45, 7.47, "RetinaNet on the 7-band 200 m stack, trained only on chips of the %d training polygons; "
             "%s boxes in %d windows round the %d held-out polygons." % (
                 int(arcpy.management.GetCount(TEST.replace("_60_test", "_60_train"))[0]),
                 format(s["detections"], ","), n["blocks"], sum(s["recall_n"].values())),
             10, "subtitle", colour=grey),
        text(0.45, 4.62 + fh + 0.06, "A  Where it ran: the %d held-out 15° blocks" % n["blocks"], 10, "label_a",
             bold=True),
        text(0.45, 1.15 + zh + 0.06, "B  The block with the most held-out polygons (%d), %s–%s, %s–%s" % (
            z["polygons"], lon(z["lon"]), lon(z["lon"] + 15), lat(z["lat"]), lat(z["lat"] + 15)),
             10, "label_b", bold=True),
        text(4.60, 4.06, "Held-out score, per polygon (KB §66.2)", 10, "table_title", bold=True),
        text(4.60, 2.62, "Recall: the polygon's own-class boxes cover ≥ 50 %% of it. Precision: of the boxes centred "
             "in a\nheld-out polygon, the share whose class matches it. One-class rate: the precision of a "
             "detector\nthat always names this class. %d of the %s boxes are centred in a held-out polygon." % (
                 n["boxes_in_heldout_polygons"], format(s["detections"], ",")), 7.6, "table_note", colour=(60, 60, 60)),
        text(4.60, 1.92, "It finds under half the crater polygons and a fifth of the plains, and never names "
             "steep/windy\nhills or lava tube (%d and %d held-out polygons). Where it does name a class it beats "
             "the\none-class rate: Crater by %.1f points, Normal Ground by %.1f. Validation average precision\n"
             "while training stayed ≤ %.3f for every class (KB §66.1)." % (
                 s["recall_n"]["steep/windy hills"], s["recall_n"]["lava tube"],
                 100 * (s["precision"]["Crater"] - oc["Crater"]),
                 100 * (s["precision"]["Normal Ground"] - oc["Normal Ground"]), max(ap.values())),
             7.9, "findings", colour=dark),
        text(0.45, 0.64, "Boxes on area classes are a limit of the method (KB §50): the hand-drawn labels are areas, "
             "not objects, so a box can only approximate one. The score is per polygon and NOT comparable with\n"
             "the SVM's per-pixel 73.8 %, κ 0.58 (layout 04). No prediction or verdict rule was written before the "
             "run: a measurement, not a test of a hypothesis. Windows, not a mask: the held-out buffer as a mask\n"
             "made the tool fail (KB §66.2). Boxes are drawn in their class colour; the held-out labels are filled "
             "faintly in theirs.", 7.9, "notes", colour=dark),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + table(4.60, 3.98, rows, TABLE_W16, size=7.6))
    legend_classes(p, lyt, mfa, 7.98, 7.12, 2.42, 2.40, [det.name, tst.name], names=True, cols=1)
    items = p.listStyleItems("ArcGIS 2D", "SCALE_BAR")
    # beside B, not on it: over the hillshade its labels could not be read
    add_text(lyt, [text(4.60, 1.62, "Scale of B", 8.2, "sbar_label", bold=True, colour=(40, 40, 40))])
    sb = lyt.createMapSurroundElement(arcpy.Point(4.60, 1.20), "SCALE_BAR", mfb,
                                      next((i for i in items if i.name == "Double Alternating Scale Bar 1 Metric"),
                                           items[0]), "sbar")
    d = sb.getDefinition("V3")
    d.divisions, d.subdivisions, d.division = 2, 0, 100.0
    d.labelFrequency = "Divisions"
    d.fittingStrategy = "AdjustFrame"
    sb.setDefinition(d)
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L16 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    print("1. feature class")
    copy_detections()
    print("2. map:", MAP)
    p = arcpy.mp.ArcGISProject(APRX)
    m = get_map(p, MAP)
    det = add(m, FC, "X5 detections, RetinaNet (%s boxes; KB §66.2)" % format(
        int(arcpy.management.GetCount(FC)[0]), ","))
    by_class_field(det, "Class", 1.2)
    tst = add(m, os.path.join(GDB, "Landform_TrainingSamples_terrain_60_test"),
              "Held-out labels (never trained on)")
    by_class_field(tst, "Classname", 0.6, fill=35)
    trn = add(m, os.path.join(GDB, "Landform_TrainingSamples_terrain_60_train"),
              "Hand-drawn labels — used to train", visible=False)
    by_class(trn, 0.7)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    hs = add(m, os.path.join(G.OUTDIR, "global60_hillshade.tif"), "Hillshade (±60°, 200 m)")
    order(m, [det.name, tst.name, trn.name, ext.name, hs.name])
    add_graticule(p, MAP, G30, 7)                    # on top, as on the other ±60° maps
    print("3. layout", L16)
    sheet(p, m, det, tst)
    p.save()
    m = next(x for x in p.listMaps() if x.name == MAP)
    print("   drawing order:", [l.name for l in m.listLayers()])
    print("saved. maps:", len(p.listMaps()))


if __name__ == "__main__":
    main()
