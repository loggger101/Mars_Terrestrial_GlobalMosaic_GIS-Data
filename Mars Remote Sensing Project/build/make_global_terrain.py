# -*- coding: utf-8 -*-
r"""Task 4 over the WHOLE +/-60 analysis extent, on the DEM's native grid.

make_typearea_terrain.py did this for Ius Chasma. This does it for G200 -
106694 x 35565 @ 200 m, the same footprint as the downloaded mosaics.

WHY 200 m AND NOT 100 m. HRSC/MOLA is natively 0.0033741208 deg, which is
199.999990 m on this sphere - 200 m to within 10 microns, drifting 0.005 px
across the full 106694-column width. So G200 is the DEM's own grid:

  * the warp is a column ROLL (CM 0 -> CM 180) plus a row crop, and nearest
    neighbour reproduces the original MOLA/HRSC values EXACTLY. No cubic, no
    interpolation, no invented elevations. ius_dem.tif could not do this - it
    targets 100 m, which has to interpolate.
  * it is 4x cheaper than G100 for no information whatsoever. Resampling a
    200 m DEM to 100 m and running Slope on it manufactures detail.

G200 nests exactly inside G100 (same origin, same footprint, 2x2), so these
products co-register with the thermal index and the imagery without a reproject.

Slope is DEGREES on a projected metric grid, so the z-factor is valid and
WARNING 000869 must not appear - KB 7, KB 20.
"""
import os
import sys
import time

from osgeo import gdal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grid60 as G

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "1024")

DEM = os.path.join(G.OUTDIR_NOSPACE, "global60_dem.tif")
CO = ["TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512", "COMPRESS=DEFLATE",
      "ZLEVEL=6", "BIGTIFF=YES", "NUM_THREADS=ALL_CPUS"]


def hms(s):
    return "%d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)


def build_dem():
    """Warp HRSC/MOLA onto G200. Nearest neighbour, because it is exact here."""
    if os.path.exists(DEM):
        d = gdal.Open(DEM)
        ok = (d.RasterXSize, d.RasterYSize) == (G.G200.nx, G.G200.ny)
        d = None
        if ok:
            print("  global60_dem.tif already on G200 - reusing")
            return DEM
        print("  existing DEM is the wrong grid, rebuilding")
    t = time.time()
    print("  warping HRSC/MOLA -> G200 (nearest: the grids coincide to 0.005 px)")
    gdal.Warp(DEM, G.SRC_DEM, creationOptions=CO,
              **G.G200.warp_kwargs("near", nodata=-32768))
    d = gdal.Open(DEM)
    assert (d.RasterXSize, d.RasterYSize) == (G.G200.nx, G.G200.ny), "grid mismatch"
    print("    %s  %d x %d  %.2f GB" % (hms(time.time() - t), d.RasterXSize,
                                        d.RasterYSize, os.path.getsize(DEM) / 1e9))
    d = None
    return DEM


def relabel(paths):
    """gdal.Warp writes a PROJ WKT that Pro reads as 'unknown' - KB 18."""
    try:
        import arcpy
        sr = arcpy.SpatialReference()
        sr.loadFromString(G.TARGET_WKT)
        for p in paths:
            arcpy.management.DefineProjection(p, sr)
        print("  CRS relabelled -> Mars_Equidistant_Cylindrical_CM180")
    except ImportError:
        print("  arcpy unavailable - CRS left as the PROJ WKT")


def derivatives():
    """Slope / aspect / hillshade via gdaldem, which streams and does not need
    the whole raster in RAM the way arcpy.sa does."""
    # only the kwargs each mode actually takes - passing an inapplicable one as
    # None is not the same as omitting it
    jobs = [
        ("global60_slope_deg.tif", "slope", dict(slopeFormat="degree")),
        ("global60_aspect.tif", "aspect", dict()),
        ("global60_hillshade.tif", "hillshade", dict(azimuth=225, altitude=45)),
    ]
    made = []
    for name, mode, extra in jobs:
        out = os.path.join(G.OUTDIR_NOSPACE, name)
        t = time.time()
        opts = gdal.DEMProcessingOptions(computeEdges=True, alg="Horn",
                                         creationOptions=CO, zFactor=1.0, **extra)
        gdal.DEMProcessing(out, DEM, mode, options=opts)
        d = gdal.Open(out)
        b = d.GetRasterBand(1)
        mn, mx, mean, sd = b.ComputeStatistics(True)
        print("  %-26s %s  %.2f GB   min %8.3f  max %8.3f  mean %8.3f  sd %7.3f"
              % (name, hms(time.time() - t), os.path.getsize(out) / 1e9, mn, mx, mean, sd))
        d = None
        made.append(out)
    return made


def main():
    os.makedirs(G.OUTDIR, exist_ok=True)
    G.check()
    print("=" * 78)
    print("TERRAIN DERIVATIVES OVER +/-60  (task 4 at analysis-extent scale)")
    print("=" * 78)
    print(" ", G.G200)
    t0 = time.time()
    print("\n1. the DEM on the target grid")
    build_dem()
    print("\n2. derivatives (gdaldem, Horn, z-factor 1 on a metric grid)")
    made = derivatives()
    print("\n3. label the CRS for ArcGIS")
    relabel([DEM] + made)
    print("\ndone in %s" % hms(time.time() - t0))
    print("outputs in %s" % G.OUTDIR)


if __name__ == "__main__":
    main()
