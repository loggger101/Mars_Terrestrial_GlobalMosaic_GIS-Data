# -*- coding: utf-8 -*-
"""Object-based pass over the Ius Chasma stack: segment, then classify segments.

The per-pixel Iso Cluster result (19.3) is geologically coherent but speckled.
Segment Mean Shift groups spectrally similar neighbours into objects first, so
the classification labels regions instead of pixels.

Bands 1, 4, 5 = Viking red, THEMIS day, THEMIS night. Those are the three
near-independent dimensions found in 18.3 - Viking G and B are 0.96-0.99
correlated with R and would add nothing but weight.

Parameters are the ones he rehearsed on Mercury: spectral 20, spatial 20,
min segment 5 px.
"""
import os, time, arcpy
from arcpy.sa import *

OUT = r"Z:\TypeArea"          # junction: legacy SA tools reject spaces in paths
SRC = os.path.join(OUT, "ius_composite_5band.tif")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = OUT

seg  = os.path.join(OUT, "ius_segmented.tif")
sig  = os.path.join(OUT, "ius_seg_10.gsg")
cls  = os.path.join(OUT, "ius_seg_isocluster_10.tif")

t = time.time()
SegmentMeanShift(SRC, "20", "20", "5", "1 4 5").save(seg)
print("SegmentMeanShift   %6.1fs -> %s" % (time.time()-t, os.path.basename(seg)))
r = arcpy.Raster(seg)
print("   %d x %d  bands=%d  %s" % (r.width, r.height, r.bandCount, r.spatialReference.name))

t = time.time()
IsoClusterUnsupervisedClassification(seg, 10, 20, 10, sig).save(cls)
print("IsoCluster on segs %6.1fs -> %s" % (time.time()-t, os.path.basename(cls)))

rows = []
with arcpy.da.SearchCursor(cls, ["Value", "Count"]) as cur:
    rows = [(v, c) for v, c in cur]
tot = sum(c for _, c in rows)
print("\n%d classes, %s px" % (len(rows), format(tot, ",")))
for v, c in sorted(rows, key=lambda x: -x[1]):
    print("   class %2d  %6.2f%%" % (v, 100.0*c/tot))
arcpy.CheckInExtension("Spatial")
