# -*- coding: utf-8 -*-
"""True object-based classification, and a segmentation-parameter sweep.

Two corrections to the first attempt:

1. The legacy IsoClusterUnsupervisedClassification still classifies PER PIXEL
   even when fed a segmented raster - it just sees a smoother image, which is
   why it cut speckle only 11%. TrainIsoClusterClassifier + ClassifyRaster
   (Image Analyst) read the segment attributes and label whole objects.

2. In SegmentMeanShift, spectral_detail and spatial_detail run 1-20 where
   HIGHER MEANS MORE DETAIL. The parameters rehearsed on Mercury (20/20, min 5)
   are the maximum-detail setting - the smallest possible segments, the
   opposite of what de-speckling wants. Hence the sweep below.
"""
import os, time, arcpy
from arcpy.ia import *

OUT = r"Z:\TypeArea"
SRC = os.path.join(OUT, "ius_composite_5band.tif")
BANDS = "1 4 5"            # Viking red, THEMIS day, THEMIS night - the three
                           # near-independent dimensions (18.3)
arcpy.CheckOutExtension("ImageAnalyst")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = OUT

# (tag, spectral, spatial, min segment px)
SWEEP = [("fine",   "20", "20",  "5"),      # his Mercury parameters
         ("medium", "14", "14", "30"),
         ("coarse", "9",  "9",  "80")]

for tag, spec, spat, minsz in SWEEP:
    seg = os.path.join(OUT, "ius_seg_%s.tif" % tag)
    ecd = os.path.join(OUT, "ius_obj_%s.ecd" % tag)
    cls = os.path.join(OUT, "ius_obj_%s.tif" % tag)
    t = time.time()
    SegmentMeanShift(SRC, spec, spat, minsz, BANDS).save(seg)
    ts = time.time() - t
    t = time.time()
    TrainIsoClusterClassifier(seg, 10, ecd, "", 20, 10)
    r = ClassifyRaster(seg, ecd)
    r.save(cls)
    del r
    print("%-7s spec=%-2s spat=%-2s min=%-2s   segment %5.1fs   classify %5.1fs"
          % (tag, spec, spat, minsz, ts, time.time() - t))

arcpy.CheckInExtension("ImageAnalyst")
arcpy.CheckInExtension("Spatial")
