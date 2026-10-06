# -*- coding: utf-8 -*-
"""Why does the THEMIS window land somewhere else? Compare the three grids."""
import math

from osgeo import gdal, osr

gdal.UseExceptions()
R = 3396190.0

for name, path in (
        ("Viking", r"Z:\Mars_Viking_MDIM21_ClrMosaic_global_232m.tif"),
        ("THEMIS", r"Z:\Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif"),
        ("DEM", r"Z:\Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")):
    ds = gdal.Open(path, gdal.GA_ReadOnly)
    gt = ds.GetGeoTransform()
    sr = osr.SpatialReference(wkt=ds.GetProjection())
    x0, x1 = gt[0], gt[0] + gt[1] * ds.RasterXSize
    y0, y1 = gt[3], gt[3] + gt[5] * ds.RasterYSize
    print("== %s" % name)
    print("   x %.1f .. %.1f   y %.1f .. %.1f" % (x0, x1, y0, y1))
    if abs(gt[1]) > 1.0:
        print("   as lon: %.3f .. %.3f    as lat: %.3f .. %.3f"
              % (math.degrees(x0 / R), math.degrees(x1 / R),
                 math.degrees(y0 / R), math.degrees(y1 / R)))
    for key in ("Central_Meridian", "False_Easting", "Standard_Parallel_1",
                "Longitude_Of_Center"):
        try:
            print("   %-22s %s" % (key, sr.GetProjParm(key)))
        except Exception:
            pass
    print("   semi-major: %s" % sr.GetSemiMajor())
    print("   AXIS/order: %s" % (sr.EPSGTreatsAsLatLong(),))
    print()
    ds = None
