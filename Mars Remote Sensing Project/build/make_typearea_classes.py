# -*- coding: utf-8 -*-
"""Task 7: Iso Cluster + ML Classify on the Ius Chasma 5-band stack.

Same parameters he rehearsed on the Mercury MESSENGER basemap - 10 classes,
min class size 20, sample interval 10 - now applied to Mars for the first time.
"""
import os, time, arcpy
from arcpy.sa import *

OUT = r"Z:\TypeArea"        # junction to Z:\Mars Project\TypeArea -- legacy Spatial
                             # Analyst grid-expression parser rejects spaces in paths
SRC = os.path.join(OUT, "ius_composite_5band.tif")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = OUT
arcpy.env.scratchWorkspace = os.environ.get("TMP_SCRATCH", OUT)

sig = os.path.join(OUT, "ius_5band.gsg")
cls = os.path.join(OUT, "ius_isocluster_10.tif")
mlc = os.path.join(OUT, "ius_mlclassify_10.tif")

t = time.time()
IsoClusterUnsupervisedClassification(SRC, 10, 20, 10, sig).save(cls)
print("IsoCluster        %6.1fs -> %s" % (time.time()-t, os.path.basename(cls)))

t = time.time()
MLClassify(SRC, sig, "0.0", "EQUAL", "", "").save(mlc)
print("MLClassify        %6.1fs -> %s" % (time.time()-t, os.path.basename(mlc)))

for name, path in (("IsoCluster", cls), ("MLClassify", mlc)):
    r = arcpy.Raster(path)
    tot = 0; rows = []
    with arcpy.da.SearchCursor(path, ["Value", "Count"]) as cur:
        for v, c in cur:
            rows.append((v, c)); tot += c
    print("\n%s: %d classes, %s px" % (name, len(rows), format(tot, ",")))
    for v, c in sorted(rows, key=lambda x: -x[1]):
        print("   class %2d  %7.2f%%  %s" % (v, 100.0*c/tot, format(c, ",")))
arcpy.CheckInExtension("Spatial")
