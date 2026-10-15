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

THE 180 DEG COLUMN (2026-10-14). The source is 106694 px of 0.003374120830641 deg = 359.99845 deg:
it ends 0.46 px short of +180, and its LAST column (src 106693, lon 179.9951-179.9984) is defective -
nodata in 24,335 of the 35,565 +/-60 rows, wrong by tens of metres elsewhere. The roll puts it at
G200 column 53346 (x -200..0). The warp is exact (the DEM equals the rolled source everywhere); the
source simply has no good pixel there. patch_meridian() replaces that one column with the mean of
columns 53345 and 53347 (src 106692 and src 0, both real pixels, 400 m apart) and stamps the DEM's
metadata MERIDIAN_PATCH. On request of the author: option A of three (mean / copy / nodata).
`--meridian-only` patches an existing DEM and its derivatives in a column window (Horn is 3 x 3, so
only columns 53345-53347 change), after proving the window reproduces the full-raster run bit for bit.
"""
import os
import subprocess
import sys
import time

import numpy as np
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


# only the kwargs each mode actually takes - passing an inapplicable one as
# None is not the same as omitting it
JOBS = [
    ("global60_slope_deg.tif", "slope", dict(slopeFormat="degree")),
    ("global60_aspect.tif", "aspect", dict()),
    ("global60_hillshade.tif", "hillshade", dict(azimuth=225, altitude=45)),
]

MERIDIAN_COL = 53346         # G200 column holding the source's defective last column
PATCH_KEY = "MERIDIAN_PATCH"
PATCH_NOTE = ("col 53346 (x -200..0 m, source col 106693, its defective last column) = "
              "round-half-up mean of cols 53345 and 53347; 2026-10-14")
WIN = 16                      # columns of context either side for the windowed derivative patch


def patch_meridian(dem=DEM):
    """Replace G200 column 53346 by the mean of its two neighbours, in place. Idempotent."""
    d = gdal.Open(dem, gdal.GA_Update)
    if d.GetMetadataItem(PATCH_KEY):
        print("  %s already patched: %s" % (os.path.basename(dem), d.GetMetadataItem(PATCH_KEY)))
        d = None
        return False
    b = d.GetRasterBand(1)
    nd = b.GetNoDataValue()
    a = b.ReadAsArray(MERIDIAN_COL - 1, 0, 3, d.RasterYSize).astype(np.int32)
    w, c, e = a[:, 0], a[:, 1], a[:, 2]
    both = (w != nd) & (e != nd)
    new = np.where(both, np.floor((w + e) / 2.0 + 0.5), nd).astype(np.int16)
    print("  column %d: %d nodata -> %d; changed %d of %d rows; neighbours both valid in %d"
          % (MERIDIAN_COL, int((c == nd).sum()), int((new == nd).sum()),
             int((new != c).sum()), c.size, int(both.sum())))
    assert not ((new == nd) & both).any()
    b.WriteArray(new.reshape(-1, 1), MERIDIAN_COL, 0)
    d.SetMetadataItem(PATCH_KEY, PATCH_NOTE)
    d.FlushCache()
    d = None
    return True


def _window_derivative(dem, mode, extra, x0, w):
    """gdaldem on a full-height column window, in memory."""
    src = gdal.Translate("", dem, format="MEM", srcWin=[x0, 0, w, G.G200.ny])
    opts = gdal.DEMProcessingOptions(computeEdges=True, alg="Horn", format="MEM",
                                     zFactor=1.0, **extra)
    out = gdal.DEMProcessing("", src, mode, options=opts)
    a = out.GetRasterBand(1).ReadAsArray()
    out = src = None
    return a


def refresh_overviews(path, x0, x1):
    """Recompute the external .ovr over G200 columns x0..x1 only (gdaladdo partial refresh)."""
    if not os.path.exists(path + ".ovr"):
        return
    exe = os.path.join(os.path.dirname(sys.executable), "Library", "bin", "gdaladdo.exe")
    g = G.G200
    ulx, lrx = g.ox + x0 * g.res, g.ox + (x1 + 1) * g.res
    subprocess.check_call([exe, "-r", "average", "--quiet",
                           "--partial-refresh-from-projwin", repr(ulx), repr(g.oy), repr(lrx), repr(g.ymin),
                           path])
    print("    overviews refreshed over columns %d-%d" % (x0, x1))


def meridian_only():
    """Patch the existing DEM and its derivatives at the 180 deg column only."""
    x0, w = MERIDIAN_COL - WIN, 2 * WIN + 1
    inner = slice(WIN - 1, WIN + 2)                 # window columns 53345..53347
    keep = np.r_[4:WIN - 1, WIN + 2:w - 4]          # columns that must not change
    olds = {}
    print("  proof: the window reproduces each full-raster derivative before the patch")
    for name, mode, extra in JOBS:
        out = os.path.join(G.OUTDIR_NOSPACE, name)
        d = gdal.Open(out)               # a band dies with its dataset
        old = d.GetRasterBand(1).ReadAsArray(x0, 0, w, G.G200.ny)
        d = None
        got = _window_derivative(DEM, mode, extra, x0, w)
        same = np.array_equal(got[:, 2:-2], old[:, 2:-2])
        print("    %-24s window == file on columns %d-%d: %s"
              % (name, x0 + 2, x0 + w - 3, same))
        if not same and not gdal.Open(DEM).GetMetadataItem(PATCH_KEY):
            raise SystemExit("window does not reproduce %s - not patching" % name)
        olds[name] = old
    patch_meridian()
    refresh_overviews(DEM, MERIDIAN_COL, MERIDIAN_COL)
    for name, mode, extra in JOBS:
        out = os.path.join(G.OUTDIR_NOSPACE, name)
        got = _window_derivative(DEM, mode, extra, x0, w)
        old = olds[name]
        assert np.array_equal(got[:, keep], old[:, keep]), name + ": columns outside 53345-53347 changed"
        ndiff = int((got[:, inner] != old[:, inner]).sum())
        d = gdal.Open(out, gdal.GA_Update)
        d.GetRasterBand(1).WriteArray(got[:, inner], MERIDIAN_COL - 1, 0)
        d.SetMetadataItem(PATCH_KEY, "cols 53345-53347 recomputed from the patched DEM; 2026-10-14")
        d.FlushCache()
        d = None
        print("    %-24s columns 53345-53347 rewritten, %d pixels changed" % (name, ndiff))
        refresh_overviews(out, MERIDIAN_COL - 1, MERIDIAN_COL + 1)


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
    made = []
    for name, mode, extra in JOBS:
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
    if "--meridian-only" in sys.argv:
        print("\nthe 180 deg column only (patch in place, windowed derivatives)")
        meridian_only()
        print("\ndone in %s" % hms(time.time() - t0))
        return
    print("\n1. the DEM on the target grid")
    build_dem()
    patch_meridian()
    print("\n2. derivatives (gdaldem, Horn, z-factor 1 on a metric grid)")
    made = derivatives()
    print("\n3. label the CRS for ArcGIS")
    relabel([DEM] + made)
    print("\ndone in %s" % hms(time.time() - t0))
    print("outputs in %s" % G.OUTDIR)


if __name__ == "__main__":
    main()
