# -*- coding: utf-8 -*-
"""Prospectus task 4: rebuild the terrain derivatives CORRECTLY.

Every existing DEM derivative carries WARNING 000869 - they were computed on a
degree grid with a default z-factor of 1, which is meaningless. ius_dem.tif is
a projected metric grid (eqc / 100 m), so the z-factor is finally valid and the
warning should not recur. Slope is produced in DEGREES, not PERCENT_RISE.
"""
import os, time, arcpy
from arcpy.sa import *

OUT = r"Z:\TypeArea"          # junction: legacy SA tools reject the space in "Mars Project"
DEM = os.path.join(OUT, "ius_dem.tif")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = OUT

d = arcpy.Raster(DEM)
print("DEM  %s  %s  cell %.3f %s" % (d.spatialReference.name,
      d.spatialReference.type, d.meanCellWidth,
      d.spatialReference.linearUnitName or "degrees"))

jobs = [("ius_slope_deg.tif",  lambda: Slope(DEM, "DEGREE", 1, "PLANAR", "METER")),
        ("ius_slope_pct.tif",  lambda: Slope(DEM, "PERCENT_RISE", 1, "PLANAR", "METER")),
        ("ius_aspect.tif",     lambda: Aspect(DEM, "PLANAR", "METER")),
        ("ius_hillshade.tif",  lambda: Hillshade(DEM, 225, 45, "SHADOWS", 1))]

seen = 0
for name, fn in jobs:
    t = time.time()
    fn().save(os.path.join(OUT, name))
    all_msgs = arcpy.GetMessages()
    msgs = all_msgs[seen:]           # only what THIS tool emitted
    seen = len(all_msgs)
    warn = "WARNING 000869" in msgs
    r = arcpy.Raster(os.path.join(OUT, name))
    print("%-20s %5.1fs  min %8.3f  max %8.3f  mean %8.3f   WARNING 000869: %s"
          % (name, time.time()-t, r.minimum, r.maximum, r.mean, "YES" if warn else "no"))
    if warn:
        print("     !! ", [l for l in msgs.splitlines() if "000869" in l])
arcpy.CheckInExtension("Spatial")
