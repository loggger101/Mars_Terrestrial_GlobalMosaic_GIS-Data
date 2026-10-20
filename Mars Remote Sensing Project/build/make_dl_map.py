# -*- coding: utf-8 -*-
r"""X5's held-out detections into the gdb and the .aprx (KB §66.2, §66.3).

  DL_Detections_heldout_20261019   the 1,838 RetinaNet boxes kept by make_dl_model.py --detect (one
                                   window per held-out 15° block), copied from the shapefile beside the
                                   model; fields Class, Classvalue, Confidence, Model, MappedBy
  map "X5 — deep-learning detections (held out)"
                                   the boxes outlined in the class colours over the held-out hand-drawn
                                   labels (filled faintly in the same colours), the 30° graticule, the
                                   ±60° hillshade; the training labels off, for context

The feature class is written in the stack's own SR with its XY domain widened by 400 km: a default-domain
class refuses a box past the 0°E edge of the CM 180 grid (KB §66.2). One holding rows another script
wrote is never replaced. Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a
copy beside the real .aprx (§31.5).
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from make_global60_maps import outline, by_class, add, get_map, order, CLASS_COLOURS, BKDIR
from make_reference_maps import add_graticule, G30

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
              "Hand-drawn labels — held out (scored, never trained on)")
    by_class_field(tst, "Classname", 0.6, fill=35)
    trn = add(m, os.path.join(GDB, "Landform_TrainingSamples_terrain_60_train"),
              "Hand-drawn labels — used to train", visible=False)
    by_class(trn, 0.7)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    hs = add(m, os.path.join(G.OUTDIR, "global60_hillshade.tif"), "Hillshade (±60°, 200 m)")
    order(m, [det.name, tst.name, trn.name, ext.name, hs.name])
    add_graticule(p, MAP, G30, 7)                    # on top, as on the other ±60° maps
    p.save()
    m = next(x for x in p.listMaps() if x.name == MAP)
    print("   drawing order:", [l.name for l in m.listLayers()])
    print("saved. maps:", len(p.listMaps()))


if __name__ == "__main__":
    main()
