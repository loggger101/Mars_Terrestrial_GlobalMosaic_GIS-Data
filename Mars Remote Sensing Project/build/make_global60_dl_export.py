# -*- coding: utf-8 -*-
r"""Re-export the hand-labelled deep-learning training data from the corrected ±60° stack (KB §29.6, §31).

The 1 Oct export came from the 7-band CompositeBand: a raw DEM band in metres, percent-rise slope,
and empty thermal bands past ±60° (§29.4, §30.3). This one uses the same settings as the GUI export
(256 x 256 chips, PASCAL VOC rectangles, the class values; the GUI stride is not recorded in the
export, so stride is 128, half a chip) on
global60_svm_stack_200m.tif, so every chip is inside ±60° and every band is 8-bit 1-255.

The GUI export is left as it is. This writes a NEW folder:
  Z:\Mars Project\LabeledObjects\global60_svm_stack_200m\
Labels: the hand-drawn Landform_TrainingSamples_terrain, read only. Chips exist only where the stack does,
so the parts of the labelled polygons north of 60°N fall away by themselves.
"""
import os, sys, time, shutil
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G

STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
LABELS = r"Z:\Mars Project\Mars Project.gdb\Landform_TrainingSamples_terrain"
OUT = r"Z:\Mars Project\LabeledObjects\global60_svm_stack_200m"

if os.path.exists(OUT):
    # only ever replace a folder this script made: it carries our marker file
    if not os.path.exists(os.path.join(OUT, "MADE_BY_make_global60_dl_export.txt")):
        sys.exit("REFUSING: %s exists and was not made by this script" % OUT)
    shutil.rmtree(OUT)
t = time.time()
arcpy.CheckOutExtension("ImageAnalyst")
arcpy.ia.ExportTrainingDataForDeepLearning(
    STACK, OUT, LABELS, image_chip_format="TIFF",
    tile_size_x=256, tile_size_y=256, stride_x=128, stride_y=128,
    output_nofeature_tiles="ONLY_TILES_WITH_FEATURES",
    metadata_format="PASCAL_VOC_rectangles", class_value_field="Classvalue")
open(os.path.join(OUT, "MADE_BY_make_global60_dl_export.txt"), "w").write(
    "Written by build\\make_global60_dl_export.py from %s\n" % STACK)
print("exported in %.0f s -> %s" % (time.time() - t, OUT))
print(open(os.path.join(OUT, "stats.txt")).read()[:1500])
