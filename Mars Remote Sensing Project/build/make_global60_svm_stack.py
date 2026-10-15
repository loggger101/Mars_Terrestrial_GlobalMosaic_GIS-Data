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

`--patch-cols C0 C1` recomputes only G200 columns C0..C1 of the existing stack, with its stored
stretch (2026-10-14: 53342 53350, the 180 deg column's slope and 9 x 9 relief footprint; KB §54).
"""
import os, sys, time, ctypes, subprocess
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


def readers(vik=None, x0=0, nx=None):
    """`x0`, `nx`: a column window (default the whole width); `vik`: an open Viking G200 dataset
    whose column 0 is G200 column x0 (default VIK200, the full-width warp)."""
    dsets = [gdal.Open(G.SRC_DAY), gdal.Open(G.SRC_NIGHT), gdal.Open(SLOPE), gdal.Open(DEM)]   # kept alive: a band dies with its dataset
    day = dsets[0].GetRasterBand(1)
    night = dsets[1].GetRasterBand(1)
    off = G.check()
    vx = 0 if vik is not None else x0
    vik = vik if vik is not None else gdal.Open(VIK200)
    vb = [vik.GetRasterBand(i + 1) for i in range(3)]
    slope = dsets[2].GetRasterBand(1)
    dem = dsets[3].GetRasterBand(1)
    nx, ny = nx or G.G200.nx, G.G200.ny

    def strip(y0, h):
        """All seven raw bands for G200 rows y0..y0+h, plus a validity mask."""
        n = night.ReadAsArray(2 * x0, 2 * y0, 2 * nx, 2 * h)
        d = day.ReadAsArray(off["dx"] + 2 * x0, off["dy"] + 2 * y0, 2 * nx, 2 * h)
        v = [b.ReadAsArray(vx, y0, nx, h) for b in vb]
        s = slope.ReadAsArray(x0, y0, nx, h).astype(np.float32)
        a0, a1 = max(0, y0 - HALO), min(ny, y0 + h + HALO)
        z = dem.ReadAsArray(x0, a0, nx, a1 - a0).astype(np.float32)
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


# The 2 Oct stack's limits at full precision where STRETCH's 3 decimals are not enough. slope_deg
# p99 recomputed 2026-10-14 exactly as percentiles() did, from the pre-patch slope (2,926,448
# samples, as the run logged); the patched slope would give 17.7823, so a full rerun would restretch
# the whole band.
EXACT_LIM = {"slope_deg": (0.0, 17.7923641204834)}


def patch_columns(c0, c1, margin=8):
    """Recompute G200 columns c0..c1 of the existing stack in place (the 180 deg column, KB §54).

    The stretch limits are read back from the stack's STRETCH metadata, never recomputed, so the
    rest of the stack stays bit-identical. Gate before writing: every band in the margin columns
    (4..margin px outside c0..c1; the 9 x 9 relief wrap only spoils the outer 4) must equal the
    stack as it is, and inside c0..c1 bands 1-5 must equal it wherever it was valid."""
    import re
    ds = gdal.Open(OUT, gdal.GA_Update)
    lim = [tuple(float(v) for v in re.search(r"%s p1=([-\d.]+) p99=([-\d.]+)" % n,
                                            ds.GetMetadataItem("STRETCH")).groups()) for n in NAMES]
    for i, n in enumerate(NAMES):           # STRETCH is rounded to 3 decimals; use the exact value
        if n in EXACT_LIM:
            assert all(abs(a - b) < 5e-4 for a, b in zip(EXACT_LIM[n], lim[i])), n
            lim[i] = EXACT_LIM[n]
    x0, nx, ny = c0 - margin, c1 - c0 + 1 + 2 * margin, G.G200.ny
    t = time.time()
    vik = gdal.Warp("", G.SRC_VIKING, format="MEM", warpMemoryLimit=2048,
                    **G.G200.sub(x0, 0, nx, ny).warp_kwargs("bilinear", nodata=0))
    print("  Viking window warped, %s" % hms(time.time() - t))
    strip = readers(vik, x0, nx)
    new = np.zeros((7, ny, nx), np.uint8)
    for y0 in range(0, ny, STRIP):
        h = min(STRIP, ny - y0)
        raw, ok = strip(y0, h)
        allok = np.logical_and.reduce(ok)
        for i in range(7):
            o = scale(raw[i], *lim[i]); o[~allok] = 0
            new[i, y0:y0 + h] = o
    old = ds.ReadAsArray(x0, 0, nx, ny)
    m = np.r_[4:margin, nx - margin:nx - 4]
    inner = slice(margin, nx - margin)
    for i, n in enumerate(NAMES):
        same = np.array_equal(new[i][:, m], old[i][:, m])
        was = old[i][:, inner] > 0
        keep = np.array_equal(new[i][:, inner][was], old[i][:, inner][was])
        print("  %-12s margin identical %s | inside, where valid before, identical %s | pixels changed %d"
              % (n, same, keep, int((new[i][:, inner] != old[i][:, inner]).sum())))
        if not same or (i < 5 and not keep):
            raise SystemExit("window does not reproduce the stack - not writing")
    print("  nodata pixels in columns %d-%d: %d before, %d after"
          % (c0, c1, int((old[0][:, inner] == 0).sum()), int((new[0][:, inner] == 0).sum())))
    for i in range(7):
        ds.GetRasterBand(i + 1).WriteArray(new[i][:, inner], c0, 0)
    ds.SetMetadataItem("MERIDIAN_PATCH", "cols %d-%d recomputed after the DEM's col 53346 patch; "
                       "stretch from STRETCH; 2026-10-14" % (c0, c1))
    ds.FlushCache(); ds = None
    exe = os.path.join(os.path.dirname(sys.executable), "Library", "bin", "gdaladdo.exe")
    g = G.G200
    subprocess.check_call([exe, "-r", "average", "--quiet", "--partial-refresh-from-projwin",
                           repr(g.ox + c0 * g.res), repr(g.oy), repr(g.ox + (c1 + 1) * g.res),
                           repr(g.ymin), OUT])
    print("  written; overviews refreshed over columns %d-%d" % (c0, c1))


def main():
    if "--patch-cols" in sys.argv:
        k = sys.argv.index("--patch-cols")
        patch_columns(int(sys.argv[k + 1]), int(sys.argv[k + 2]))
        return
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
