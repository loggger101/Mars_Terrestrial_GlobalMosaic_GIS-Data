# -*- coding: utf-8 -*-
r"""T1 confirmed with Pro's SVM: the ±60° classification at 200 m WITHOUT the thermal bands (NEXT-STEPS §4, T1).

KB §40.1 measured T1 with a numpy Gaussian maximum-likelihood classifier: the thermal bands add
+1.3 pt [+0.6, +2.2]. NEXT-STEPS scheduled the confirmation with Pro's own SVM. This runs it on the
same split, the same settings and the same tiling as the published 200 m map (X3), changing one thing:
the night and day IR bands are left out.

  1. global60_svm_stack_200m_nothermal.tif   bands 1, 2, 3, 6, 7 of the 7-band stack (Viking RGB,
                                             slope, relief), copied exactly, no resampling
  2. global60_landforms_svm_nothermal.ecd    TrainSupportVectorMachineClassifier on the _60_train
                                             polygons, max 1000 samples per class (as X3)
  3. global60_landforms_svm_nothermal_200m.tif   tiled ClassifyRaster at 200 m, tiles in their own
                                             scratch folder (never the X3 tiles), then mosaic + recode

Then score both maps the same way:
  python verify_global60_classification.py --cell 200
  python verify_global60_classification.py --cell 200 --raster <...nothermal_200m.tif>

Writes only the three files above and its scratch tiles. The 7-band stack, its .ecd and the
published maps are read, never written. Resumes: a finished tile is skipped on re-run.

  python make_t1_pro_confirm.py --cell 200            all three steps (band set nothermal)
  python make_t1_pro_confirm.py --cell 200 --classify-only
  python make_t1_pro_confirm.py --cell 400 --set terrain [--reuse-ecd]
      --set nothermal | novisible | terrain: the band set; every file name carries it.
      --reuse-ecd: skip the stack and training when that set's .ecd exists.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osgeo import gdal
import arcpy
import grid60 as G
import make_global60_classification as M

gdal.UseExceptions()
FULL = M.STACK
# --set picks the band set; the names match make_thermal_ablation.py's BANDSETS (KB §40.1)
SETS = {
    "nothermal": [1, 2, 3, 6, 7],            # without thermal (no night, day)
    "novisible": [4, 5, 6, 7],               # without visible (no Viking)
    "terrain":   [6, 7],                     # terrain only
}
SET = sys.argv[sys.argv.index("--set") + 1] if "--set" in sys.argv else "nothermal"
KEEP = SETS[SET]
ALL = ["viking_red", "viking_green", "viking_blue", "night_ir", "day_ir", "slope_deg", "relief_m"]
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m_%s.tif" % SET)
ECD = os.path.join(G.OUTDIR, "global60_landforms_svm_%s.ecd" % SET)
OUT = os.path.join(G.OUTDIR, "global60_landforms_svm_%s_%dm.tif" % (SET, M.CELL))
CO = ["TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512", "COMPRESS=DEFLATE", "ZLEVEL=6",
      "BIGTIFF=YES", "NUM_THREADS=ALL_CPUS"]


def make_stack():
    if os.path.exists(STACK):
        print("  %s exists - reusing" % os.path.basename(STACK))
        return
    t = time.time()
    src = gdal.Open(FULL)
    names = [src.GetRasterBand(k).GetDescription() for k in KEEP]
    assert names == [ALL[k - 1] for k in KEEP], names
    tmp = STACK.replace(".tif", "_tmp.tif")
    gdal.Translate(tmp, src, bandList=KEEP, creationOptions=CO)
    d = gdal.Open(tmp, gdal.GA_Update)
    for i, n in enumerate(names, 1):
        b = d.GetRasterBand(i); b.SetNoDataValue(0); b.SetDescription(n)
    d.SetMetadataItem("T1", "bands %s of %s, copied exactly" % (KEEP, os.path.basename(FULL)))
    d = None
    os.replace(tmp, STACK)
    print("  %s  in %.0f s" % (os.path.basename(STACK), time.time() - t))


def main():
    assert "--cell" in sys.argv, "pass --cell 200 (it names the output, as in make_global60_classification.py)"
    M.keep_awake(True)
    M.STACK, M.ECD = STACK, ECD                               # the module's functions read these globals
    M.SCRATCH = os.path.join(M.SCRATCH, "t1_" + SET)          # its own tiles, never X3's
    if "--classify-only" not in sys.argv and not ("--reuse-ecd" in sys.argv and os.path.exists(ECD)):
        print("1. %d-band stack (%s)" % (len(KEEP), SET)); make_stack()
        print("2. train SVM on the same _60_train polygons"); M.train()
    assert os.path.exists(ECD), "no %s - run without --classify-only first" % ECD
    print("3. classify ±60° at %d m, band set %s %s" % (M.CELL, SET, KEEP))
    M.classify_tiled(OUT, M.CELL)
    M.keep_awake(False)


if __name__ == "__main__":
    main()
