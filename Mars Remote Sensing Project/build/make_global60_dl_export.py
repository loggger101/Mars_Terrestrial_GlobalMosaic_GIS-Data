# -*- coding: utf-8 -*-
r"""Re-export the hand-labelled deep-learning training data from the corrected ±60° stack (KB §29.6, §31).

The 1 Oct export came from the 7-band CompositeBand: a raw DEM band in metres, percent-rise slope,
and empty thermal bands past ±60° (§29.4, §30.3). This one uses the same settings as the GUI export
(256 x 256 chips, PASCAL VOC rectangles, the class values; the GUI stride is not recorded in the
export, so stride is 128, half a chip) on
global60_svm_stack_200m.tif, so every chip is inside ±60° and every band is 8-bit 1-255.

The GUI export is left as it is. This writes a NEW folder:
  <drive>\Mars Project\LabeledObjects\global60_svm_stack_200m\
Labels: the hand-drawn Landform_TrainingSamples_terrain, read only. Chips exist only where the stack does,
so the parts of the labelled polygons north of 60°N fall away by themselves.

--train-only (added 2026-10-09, KB §50, q25 answered yes): the same export from
Landform_TrainingSamples_terrain_60_train alone (329 polygons) into ...\global60_svm_stack_200m_train\,
so a model trained on it can be scored on the 183 held-out polygons in their 15° blocks, as the SVM was
(§31.3). The default export above holds all 512, held-out ones included: train on it and the held-out
score means nothing. Boxes, as exported (q26).

--rare [--out <folder>] (added 2026-10-20, KB §66.5): extra chips around the two rare classes for X5b. Labels are
still the whole training split (so a crater beside a lava tube is labelled, not taught as background); the chips
are limited by a mask, each training steep/windy hills or lava tube polygon buffered by 55 km (a chip is 51.2 km
and must lie wholly inside the mask), and taken at stride 64 instead of 128. Written to internal disk first
(default C:\MarsScratch\x5b\export_rare; KB §36.4).
"""
import os, sys, time, shutil
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G

STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
RARE = "--rare" in sys.argv
TRAIN_ONLY = "--train-only" in sys.argv or RARE
LABELS = on_drive(r"Mars Project\Mars Project.gdb\Landform_TrainingSamples_terrain"
                  + ("_60_train" if TRAIN_ONLY else ""))
OUT = on_drive(r"Mars Project\LabeledObjects\global60_svm_stack_200m" + ("_train" if TRAIN_ONLY else ""))
if RARE:
    OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else r"C:\MarsScratch\x5b\export_rare"

if os.path.exists(OUT):
    # only ever replace a folder this script made: it carries our marker file
    if not os.path.exists(os.path.join(OUT, "MADE_BY_make_global60_dl_export.txt")):
        sys.exit("REFUSING: %s exists and was not made by this script" % OUT)
    shutil.rmtree(OUT)
t = time.time()
arcpy.CheckOutExtension("ImageAnalyst")
mask, stride, note = "", 128, ""
if RARE:
    # the mask: rare training polygons buffered 55 km in the stack's metric SR (domain widened as in §66.3)
    sr = arcpy.Describe(STACK).spatialReference
    sr.setDomain(-11.1e6, 11.1e6, -4.0e6, 4.0e6)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    mask = os.path.join(arcpy.env.scratchGDB, "x5b_rare_mask")
    arcpy.management.CreateFeatureclass(os.path.dirname(mask), os.path.basename(mask), "POLYGON",
                                        spatial_reference=sr)
    n = 0
    with arcpy.da.SearchCursor(LABELS, ["SHAPE@", "Classvalue"], "Classvalue IN (2, 3)") as c, \
            arcpy.da.InsertCursor(mask, ["SHAPE@"]) as ins:
        for g, v in c:
            ins.insertRow([g.projectAs(sr).buffer(55000)]); n += 1
    stride = 64
    note = "rare mode: mask = %d training steep/windy hills + lava tube polygons buffered 55 km; stride 64\n" % n
    print(note.strip())
arcpy.ia.ExportTrainingDataForDeepLearning(
    STACK, OUT, LABELS, image_chip_format="TIFF",
    tile_size_x=256, tile_size_y=256, stride_x=stride, stride_y=stride,
    output_nofeature_tiles="ONLY_TILES_WITH_FEATURES",
    metadata_format="PASCAL_VOC_rectangles", class_value_field="Classvalue",
    **({"in_mask_polygons": mask} if mask else {}))
open(os.path.join(OUT, "MADE_BY_make_global60_dl_export.txt"), "w").write(
    "Written by build\\make_global60_dl_export.py from %s\nlabels: %s\n%s" % (STACK, LABELS, note))
print("exported in %.0f s -> %s" % (time.time() - t, OUT))
print(open(os.path.join(OUT, "stats.txt")).read()[:1500])
