# -*- coding: utf-8 -*-
r"""A corrected classification stack at the analysis extent (KB §30, §31).

Fixes, one by one, what §29.4 and §30.3 found in the 7-band `CompositeBand`:

  CompositeBand (30 Sep)                       this stack
  ---------------------------------------      ------------------------------------------
  global, bands 6-7 empty past ±60°            G200, ±60° exactly (grid60.py, §16, §28.1)
  THEMIS rolled 180° and resampled to 231 m    THEMIS 2x2-averaged on its own grid, no warp
  raw DEM in metres beside 8-bit bands         no elevation band (it carried 62% of the map)
  Slope_Mars_H1: percent rise on a degree grid slope in degrees, global60_slope_deg.tif (§28.8)
  F32, one band 0-255, another -5611..18305    every band U8, stretched 1-255 over ±60°
                                               with the same p1/p99 rule; 0 = nodata

Bands:  1-3 Viking MDIM 2.1 R, G, B     (bilinear warp 231.5 m -> 200 m)
        4   THEMIS Night IR              (2x2 mean of the native 100 m grid)
        5   THEMIS Day IR                (2x2 mean, the day window at its integer offset)
        6   slope, degrees
        7   local relief, m              (max - min elevation in a 9 x 9 = 1.8 km window)

Relief stands in for the DEM: it says "rough or smooth here", which is what the four landform
classes differ in, without saying "high or low", which is what made the old map an elevation map.

Writes  Z:\Mars Project\Global60\global60_svm_stack_200m.tif   (+ .ovr, statistics)
Run on the laptop: ~35 GB of strip reads over USB. Holds the machine awake while it runs.
"""
import os, sys, time, ctypes
import numpy as np
from osgeo import gdal
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "1024")

OUT = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
SCRATCH = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mars_scratch")   # internal SSD (§2.2)
VIK200 = os.path.join(SCRATCH, "viking_g200.tif")
SLOPE = os.path.join(G.OUTDIR, "global60_slope_deg.tif")
DEM = os.path.join(G.OUTDIR, "global60_dem.tif")
STRIP = 512                       # G200 rows per pass
HALO = 4                          # rows of DEM context for the 9 x 9 relief window
NAMES = ["viking_red", "viking_green", "viking_blue", "night_ir", "day_ir", "slope_deg", "relief_m"]
CO = ["TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512", "COMPRESS=DEFLATE", "ZLEVEL=6",
      "PREDICTOR=2", "BIGTIFF=YES", "NUM_THREADS=ALL_CPUS", "INTERLEAVE=BAND"]


def keep_awake(on=True):
    """Ask Windows not to sleep while this process runs (KB §28.9). Not a settings change."""
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on else 0))


def hms(s):
    return "%d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)


def warp_viking():
    if os.path.exists(VIK200):
        d = gdal.Open(VIK200)
        if (d.RasterXSize, d.RasterYSize, d.RasterCount) == (G.G200.nx, G.G200.ny, 3):
            print("  reusing", VIK200)
            return
    os.makedirs(SCRATCH, exist_ok=True)
    t = time.time()
    gdal.Warp(VIK200, G.SRC_VIKING, creationOptions=CO, warpMemoryLimit=2048,
              **G.G200.warp_kwargs("bilinear", nodata=0))
    print("  Viking -> G200 bilinear, %s" % hms(time.time() - t))


def mean2x2(a):
    """2x2 mean of a U8 strip, nodata 0 wherever any of the four is 0."""
    h, w = a.shape[0] // 2 * 2, a.shape[1] // 2 * 2
    a = a[:h, :w]
    q = a.reshape(h // 2, 2, w // 2, 2)
    s = q.astype(np.uint16).sum(axis=(1, 3))
    out = ((s + 2) // 4).astype(np.uint8)
    out[(q == 0).any(axis=(1, 3))] = 0
    return out


def readers():
    dsets = [gdal.Open(G.SRC_DAY), gdal.Open(G.SRC_NIGHT), gdal.Open(SLOPE), gdal.Open(DEM)]   # kept alive: a band dies with its dataset
    day = dsets[0].GetRasterBand(1)
    night = dsets[1].GetRasterBand(1)
    off = G.check()
    vik = gdal.Open(VIK200)
    vb = [vik.GetRasterBand(i + 1) for i in range(3)]
    slope = dsets[2].GetRasterBand(1)
    dem = dsets[3].GetRasterBand(1)
    nx, ny = G.G200.nx, G.G200.ny

    def strip(y0, h):
        """All seven raw bands for G200 rows y0..y0+h, plus a validity mask."""
        n = night.ReadAsArray(0, 2 * y0, 2 * nx, 2 * h)
        d = day.ReadAsArray(off["dx"], off["dy"] + 2 * y0, 2 * nx, 2 * h)
        v = [b.ReadAsArray(0, y0, nx, h) for b in vb]
        s = slope.ReadAsArray(0, y0, nx, h).astype(np.float32)
        a0, a1 = max(0, y0 - HALO), min(ny, y0 + h + HALO)
        z = dem.ReadAsArray(0, a0, nx, a1 - a0).astype(np.float32)
        zv = z > -32000

        hi = ndimage.maximum_filter(np.where(zv, z, -1e9), size=9, mode="wrap")
        lo = ndimage.minimum_filter(np.where(zv, z, 1e9), size=9, mode="wrap")
        rel = (hi - lo)[y0 - a0:y0 - a0 + h]
        relok = (ndimage.minimum_filter(zv.astype(np.uint8), size=9, mode="wrap") > 0)[y0 - a0:y0 - a0 + h]
        raw = [v[0], v[1], v[2], mean2x2(n), mean2x2(d), s, rel]
        ok = [v[0] > 0, v[1] > 0, v[2] > 0, raw[3] > 0, raw[4] > 0, s >= 0, relok]
        return raw, ok
    strip.keep = (dsets, vik)          # the closure only captures the bands; pin their datasets too
    return strip


def percentiles(strip):
    """p1/p99 of each band over ±60°, from 24 strips of 8 rows spread over the extent."""
    t = time.time()
    acc = [[] for _ in NAMES]
    for y0 in np.linspace(HALO, G.G200.ny - 8 - HALO, 24).astype(int):
        raw, ok = strip(int(y0), 8)
        for i in range(7):
            acc[i].append(raw[i][ok[i]][::7])
    lim = []
    for i, n in enumerate(NAMES):
        x = np.concatenate(acc[i])
        lo, hi = np.percentile(x, [1, 99])
        lim.append((float(lo), float(hi)))
        print("  %-12s p1 %8.2f  p99 %8.2f   (%d samples)" % (n, lo, hi, x.size))
    print("  %.0f s" % (time.time() - t))
    return lim


def scale(x, lo, hi):
    return (np.clip((x.astype(np.float32) - lo) / (hi - lo), 0, 1) * 254 + 1).astype(np.uint8)


def main():
    keep_awake(True)
    t0 = time.time()
    print("1. Viking onto G200"); warp_viking()
    strip = readers()
    print("2. stretch limits over ±60°"); lim = percentiles(strip)

    print("3. streaming %d-row strips -> %s" % (STRIP, OUT))
    ds = gdal.GetDriverByName("GTiff").Create(OUT, G.G200.nx, G.G200.ny, 7, gdal.GDT_Byte, options=CO)
    ds.SetGeoTransform(G.G200.geotransform); ds.SetProjection(G.TARGET_WKT)
    bands = [ds.GetRasterBand(i + 1) for i in range(7)]
    for b, n in zip(bands, NAMES):
        b.SetNoDataValue(0); b.SetDescription(n)
    nvalid = 0
    nstrip = (G.G200.ny + STRIP - 1) // STRIP
    for k, y0 in enumerate(range(0, G.G200.ny, STRIP)):
        h = min(STRIP, G.G200.ny - y0)
        raw, ok = strip(y0, h)
        allok = np.logical_and.reduce(ok)
        nvalid += int(allok.sum())
        for i in range(7):
            o = scale(raw[i], *lim[i]); o[~allok] = 0
            bands[i].WriteArray(o, 0, y0)
        if k % 5 == 0 or k == nstrip - 1:
            el = time.time() - t0
            print("   strip %2d/%d  valid %.1f%%  %s" % (k + 1, nstrip, 100 * allok.mean(), hms(el)), flush=True)
    ds.SetMetadataItem("STRETCH", "; ".join("%s p1=%.3f p99=%.3f -> 1..255" % (n, a, b)
                                             for n, (a, b) in zip(NAMES, lim)))
    ds.FlushCache(); ds = None
    print("   co-valid %.2f%% of G200" % (100.0 * nvalid / G.G200.npix))

    print("4. overviews"); t = time.time()
    d = gdal.Open(OUT, gdal.GA_ReadOnly)
    gdal.SetConfigOption("COMPRESS_OVERVIEW", "DEFLATE")
    d.BuildOverviews("AVERAGE", [2, 4, 8, 16, 32, 64, 128]); d = None
    print("   %s" % hms(time.time() - t))

    print("5. ArcGIS label + statistics")
    import arcpy
    sr = arcpy.SpatialReference(); sr.loadFromString(G.TARGET_WKT)
    arcpy.management.DefineProjection(OUT, sr)
    arcpy.management.CalculateStatistics(OUT, x_skip_factor=8, y_skip_factor=8)
    print("done in %s" % hms(time.time() - t0))
    keep_awake(False)


if __name__ == "__main__":
    main()
