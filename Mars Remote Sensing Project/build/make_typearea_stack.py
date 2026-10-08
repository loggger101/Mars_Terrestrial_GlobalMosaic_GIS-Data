# -*- coding: utf-8 -*-
"""Task 3 + task 5 over a type area: Ius Chasma, or --area ath for Athabasca Valles (areas.py, KB §42).

Harmonises all four inputs onto ONE grid, then builds the band composite that
has failed four times at global scale. Bounded extent, per the prospectus's own fix.

Target grid = THEMIS native: eqc / lon_0=180 / R=3396190 / 100 m, snapped to the
day mosaic's own pixel edges. Chosen so the day-night pair is NOT resampled -
only Viking and the DEM are, and they must be regardless.
"""
import os, time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
import areas
A = areas.current()
from osgeo import gdal
gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "512")

OUT = A["out"]
os.makedirs(OUT, exist_ok=True)
TSRS = "+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=180 +x_0=0 +y_0=0 +R=3396190 +units=m +no_defs"
# snapped to the day grid (ULX -10669500, ULY 5334800, 100 m)
BOUNDS = A["bounds"]                                        # xmin ymin xmax ymax
RES = 100.0
W = int((BOUNDS[2]-BOUNDS[0])/RES); H = int((BOUNDS[3]-BOUNDS[1])/RES)
print("target grid %d x %d @ %g m  (%s)" % (W, H, RES, A["label"]))

SRC = [("viking", on_drive(r"Mars_Viking_MDIM21_ClrMosaic_global_232m.tif"), "cubic",    0),
       ("day",    on_drive(r"Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif"), "near",  0),
       ("night",  on_drive(r"Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif"),"near", 0),
       ("dem",    on_drive(r"Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif"), "cubic", -32768)]

made = {}
for name, src, alg, nod in SRC:
    dst = os.path.join(OUT, areas.name(A, "%s.tif" % name))
    t = time.time()
    gdal.Warp(dst, src, dstSRS=TSRS, outputBounds=BOUNDS, xRes=RES, yRes=RES,
              resampleAlg=alg, srcNodata=nod, dstNodata=nod,
              multithread=True, creationOptions=["TILED=YES","COMPRESS=DEFLATE","BIGTIFF=IF_SAFER"])
    d = gdal.Open(dst)
    print("  %-6s %-6s %5.1fs  %dx%d b=%d  %6.1f MB" % (name, alg, time.time()-t,
          d.RasterXSize, d.RasterYSize, d.RasterCount, os.path.getsize(dst)/1048576))
    assert (d.RasterXSize, d.RasterYSize) == (W, H), "grid mismatch for %s" % name
    made[name] = dst
print("all four on one grid - task 3 satisfied for this extent")

# gdal.Warp writes a PROJ-derived WKT that ArcGIS reads as name "unknown".
# Relabel with the equivalent NAMED Esri WKT - no coordinate is touched - so
# ArcGIS tools, layouts and the Landform_* feature classes all agree.
try:
    import arcpy
    WKT = ('PROJCS["Mars_Equidistant_Cylindrical_CM180",'
           'GEOGCS["GCS_Mars_2000_Sphere",DATUM["D_Mars_2000_Sphere",'
           'SPHEROID["Mars_2000_Sphere_IAU_IAG",3396190.0,0.0]],'
           'PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],'
           'PROJECTION["Equidistant_Cylindrical"],PARAMETER["False_Easting",0.0],'
           'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",180.0],'
           'PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]')
    _sr = arcpy.SpatialReference(); _sr.loadFromString(WKT)
    for _p in made.values():
        arcpy.management.DefineProjection(_p, _sr)
    print("CRS relabelled -> Mars_Equidistant_Cylindrical_CM180")
except ImportError:
    print("arcpy unavailable - CRS left as the PROJ WKT; ArcGIS will call it 'unknown'")


def composite(tag, parts):
    vrt = os.path.join(OUT, "_%s.vrt" % tag)
    out = os.path.join(OUT, areas.name(A, "composite_%s.tif" % tag))
    t = time.time()
    gdal.BuildVRT(vrt, parts, separate=True)
    gdal.Translate(out, vrt, creationOptions=["TILED=YES","COMPRESS=DEFLATE","BIGTIFF=IF_SAFER"])
    d = gdal.Open(out)
    print("  %-8s %5.1fs  %d bands  %6.1f MB  -> %s" % (tag, time.time()-t, d.RasterCount,
          os.path.getsize(out)/1048576, os.path.basename(out)))
    os.remove(vrt)
    return out

print("\nComposite Bands (bounded) - the run that failed 4x globally:")
c4 = composite("4band", [made["viking"], made["day"]])
c5 = composite("5band", [made["viking"], made["day"], made["night"]])
print("\nDONE")
