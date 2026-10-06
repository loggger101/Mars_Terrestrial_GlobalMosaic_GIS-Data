# -*- coding: utf-8 -*-
r"""The diurnal-contrast index (KB 24) over the WHOLE +/-60 analysis extent.

make_typearea_thermal.py built this for Ius Chasma only, 8891 x 4150. This
builds the same index on G100 - 213388 x 71130, the night mosaic's own grid -
so it lands pixel-for-pixel on the downloaded mosaics.

Two things make this tractable on the laptop despite being 15.2 Gpx:

1. NEITHER INPUT IS RESAMPLED. The day mosaic sits at an exact integer pixel
   offset from the night grid (+1, +17783 - verified by grid60.check()), so
   the +/-60 band of the day mosaic is a plain window read. No warp, no
   interpolation, no temporary copy.

2. THE INDEX IS A BYTE LOOKUP. Both inputs are uint8, and the index is
       clip01((day - dlo)/(dhi - dlo)) - clip01((night - nlo)/(nhi - nlo))
   which depends only on the two byte VALUES. Two 256-entry tables therefore
   compute it exactly, with no float array of any kind. Peak RAM is one strip.

Output  global60_thermal_contrast.tif   Int16, index * 10000, nodata -32768
        HIGH = large diurnal swing = low thermal inertia = dust / fines
        LOW  = damped swing        = high thermal inertia = bedrock / coarse

This is a RELATIVE index. It is not thermal inertia and must never be called
that - KB 24.1. The 2/98 stretch is now computed over +/-60, not over Ius, so
the numbers are NOT comparable to ius_thermal_contrast.tif; that is the point.
"""
import os
import sys
import time

import numpy as np
from osgeo import gdal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grid60 as G

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "512")

SCALE = 10000.0
NODATA = -32768
STRIP = 512           # rows per pass; inputs are one-scanline-per-block
SAMPLE_ROWS = 400     # evenly spaced full scanlines used for the percentiles
SAMPLE_XSTEP = 8

OUT = os.path.join(G.OUTDIR, "global60_thermal_contrast.tif")


def open_pair():
    """Return (day_ds, day_xoff, day_yoff, night_ds). The offsets put the day
    mosaic's pixels in exact correspondence with the night grid."""
    off = G.check()
    day = gdal.Open(G.SRC_DAY)
    night = gdal.Open(G.SRC_NIGHT)
    # G100.ox = day.ox + dx*100  ->  the G100 origin is day pixel (dx, dy)
    dx, dy = off["dx"], off["dy"]
    assert dx + G.G100.nx <= day.RasterXSize, "day window overruns in x"
    assert dy + G.G100.ny <= day.RasterYSize, "day window overruns in y"
    assert (night.RasterXSize, night.RasterYSize) == (G.G100.nx, G.G100.ny)
    return day, dx, dy, night


def percentiles(day, dx, dy, night):
    """2nd/98th percentile of each input over +/-60, from evenly spaced rows.

    A full decimated read would touch all 30 GB - the blocks are whole
    scanlines, so GDAL cannot skip columns. Reading a few hundred complete rows
    costs ~85 MB per raster and gives millions of samples.
    """
    t = time.time()
    rows = np.linspace(0, G.G100.ny - 1, SAMPLE_ROWS).astype(int)
    db, nb = day.GetRasterBand(1), night.GetRasterBand(1)
    dacc, nacc = [], []
    for r in rows:
        dacc.append(db.ReadAsArray(dx, dy + int(r), G.G100.nx, 1)[0, ::SAMPLE_XSTEP])
        nacc.append(nb.ReadAsArray(0, int(r), G.G100.nx, 1)[0, ::SAMPLE_XSTEP])
    d = np.concatenate(dacc)
    n = np.concatenate(nacc)
    co = (d > 0) & (n > 0)
    dv, nv = d[co], n[co]
    dlo, dhi = np.percentile(dv, [2, 98])
    nlo, nhi = np.percentile(nv, [2, 98])
    print("  sampled %d rows x %d px  -> %s samples, %s co-valid (%.2f%%)  %.1fs"
          % (SAMPLE_ROWS, d.size // SAMPLE_ROWS, f"{d.size:,}", f"{int(co.sum()):,}",
             100.0 * co.mean(), time.time() - t))
    print("  day    mean %6.2f sd %5.2f   p2=%.0f p98=%.0f" % (dv.mean(), dv.std(), dlo, dhi))
    print("  night  mean %6.2f sd %5.2f   p2=%.0f p98=%.0f" % (nv.mean(), nv.std(), nlo, nhi))
    return float(dlo), float(dhi), float(nlo), float(nhi)


def make_lut(lo, hi):
    """256-entry table of clip01((v - lo)/(hi - lo)) * SCALE, as int32."""
    v = np.arange(256, dtype=np.float64)
    t = np.clip((v - lo) / (hi - lo), 0.0, 1.0)
    return np.rint(t * SCALE).astype(np.int32)


def main():
    os.makedirs(G.OUTDIR, exist_ok=True)
    print("=" * 78)
    print("DIURNAL-CONTRAST INDEX OVER +/-60  (KB 24 at analysis-extent scale)")
    print("=" * 78)
    print(" ", G.G100)
    t0 = time.time()

    day, dx, dy, night = open_pair()
    print("  day window  xoff=%d yoff=%d  (integer - no resampling)" % (dx, dy))

    print("\n1. stretch, computed over +/-60 rather than over the type area")
    dlo, dhi, nlo, nhi = percentiles(day, dx, dy, night)
    lut_d, lut_n = make_lut(dlo, dhi), make_lut(nlo, nhi)

    print("\n2. streaming %d-row strips" % STRIP)
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(OUT, G.G100.nx, G.G100.ny, 1, gdal.GDT_Int16,
                    options=["TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512",
                             "COMPRESS=DEFLATE", "ZLEVEL=6", "PREDICTOR=2",
                             "BIGTIFF=YES", "NUM_THREADS=ALL_CPUS"])
    ds.SetGeoTransform(G.G100.geotransform)
    ds.SetProjection(G.TARGET_WKT)
    ob = ds.GetRasterBand(1)
    ob.SetNoDataValue(float(NODATA))

    db, nb = day.GetRasterBand(1), night.GetRasterBand(1)
    nvalid = 0
    ssum = 0.0
    ssq = 0.0
    hist = np.zeros(2001, dtype=np.int64)     # index binned to 0.001
    nstrip = (G.G100.ny + STRIP - 1) // STRIP
    tlast = time.time()
    for i, y in enumerate(range(0, G.G100.ny, STRIP)):
        h = min(STRIP, G.G100.ny - y)
        d = db.ReadAsArray(dx, dy + y, G.G100.nx, h)
        n = nb.ReadAsArray(0, y, G.G100.nx, h)
        co = (d != 0) & (n != 0)
        out = np.full((h, G.G100.nx), NODATA, dtype=np.int16)
        if co.any():
            vals = (lut_d[d[co]] - lut_n[n[co]]).astype(np.int16)
            out[co] = vals
            v = vals.astype(np.float64)
            nvalid += v.size
            ssum += v.sum()
            ssq += (v * v).sum()
            hist += np.bincount(((vals.astype(np.int32) + 10000) // 10),
                                minlength=2001)
        ob.WriteArray(out, 0, y)
        del d, n, co, out
        if i % 10 == 0 or i == nstrip - 1:
            el = time.time() - t0
            frac = (y + h) / float(G.G100.ny)
            print("    strip %3d/%d  row %6d  %5.1f%%  %6.1f min elapsed, "
                  "%6.1f min projected  (%.1fs/strip)"
                  % (i + 1, nstrip, y, 100 * frac, el / 60, el / 60 / max(frac, 1e-9),
                     time.time() - tlast))
            tlast = time.time()

    ob.FlushCache()
    ob.SetStatistics(float(hist.nonzero()[0].min() * 10 - 10000),
                     float(hist.nonzero()[0].max() * 10 - 10000),
                     ssum / nvalid, (ssq / nvalid - (ssum / nvalid) ** 2) ** 0.5)
    del ob, ds, db, nb, day, night

    # ---- report ---------------------------------------------------------
    mean = ssum / nvalid / SCALE
    sd = (ssq / nvalid - (ssum / nvalid) ** 2) ** 0.5 / SCALE
    cum = np.cumsum(hist) / float(nvalid)
    def pct(p):
        return (np.searchsorted(cum, p / 100.0) * 10 - 10000) / SCALE
    print("\n3. result")
    print("  %s" % OUT)
    print("  %.2f GB on disk  (%.1f GB uncompressed -> %.2fx)"
          % (os.path.getsize(OUT) / 1e9, G.G100.npix * 2 / 1e9,
             G.G100.npix * 2.0 / os.path.getsize(OUT)))
    print("  co-valid %s / %s = %.2f%%"
          % (f"{nvalid:,}", f"{G.G100.npix:,}", 100.0 * nvalid / G.G100.npix))
    print("  index  mean %+.4f  sd %.4f" % (mean, sd))
    print("         p2 %+.3f  p25 %+.3f  p50 %+.3f  p75 %+.3f  p98 %+.3f"
          % (pct(2), pct(25), pct(50), pct(75), pct(98)))
    print("\n  Ius type area for comparison (KB 24.2): mean +0.0757")
    print("  The two are on DIFFERENT stretches and are not comparable - this")
    print("  one is scaled over +/-60, that one over the type area.")
    print("\ndone in %.1f min" % ((time.time() - t0) / 60))


if __name__ == "__main__":
    main()
