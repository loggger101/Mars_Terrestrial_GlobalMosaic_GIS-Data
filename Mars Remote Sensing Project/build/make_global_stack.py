# -*- coding: utf-8 -*-
r"""Tasks 3 + 5 over the whole +/-60 extent - the harmonised stack and the
Composite Bands run that failed four times globally (KB 8).

make_typearea_stack.py did this for Ius Chasma in 44 seconds. This is the same
script at G100 - 213388 x 71130, 411x the area, the night mosaic's own grid.

DESKTOP JOB. 61 GB for the 4-band, 76 GB for the 5-band, plus 45 GB of
harmonised single-band inputs. Budget ~150 GB of writes over the USB bus.

------------------------------------------------ why this one should now finish

The four cancelled global attempts (KB 8) were fighting three things at once.
All three are now removed:

  1. THEY WERE GLOBAL. +/-60 is a third smaller - 15.2 Gpx per band instead of
     22.8 (KB 16.4).
  2. THEY REPROJECTED THE FINEST LAYERS. Presentation 1 proposed CM 0, which
     resamples both THEMIS mosaics. On G100 the day and night mosaics are
     NATIVE - a window read, no interpolation (grid60.check). Only Viking and
     the DEM resample, and they must at any target.
  3. THEY BUILT THE COMPOSITE IN ONE STEP from unharmonised sources. Here the
     harmonise and the stack are separate: each band lands on G100 alone and is
     checked, then the composite is a VRT plus a copy, which streams.

--------------------------------------------------------------------- the bands

  1-3  Viking MDIM red/green/blue   232 m -> 100 m, cubic
  4    THEMIS day IR                native, not resampled
  5    THEMIS night IR              native, not resampled

The DEM is deliberately NOT a band. Iso Cluster measures distance in raw
values, and -8528..+21226 would swamp 1..255 (KB 14.2, 18.2). Elevation lives
beside the stack in global60_dem.tif, not inside it.

The 4-band exists because the written plan says four; the 5-band is the better
classification input because night IR is the most independent layer in the
stack (r <= 0.12 against everything else, KB 18.3).
"""
import os
import sys
import time

from osgeo import gdal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grid60 as G

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "1024")

GRID = G.G100
PREFIX = "global60"
CO = ["TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512", "COMPRESS=DEFLATE",
      "ZLEVEL=6", "BIGTIFF=YES", "NUM_THREADS=ALL_CPUS"]

BANDS = [
    ("viking", G.SRC_VIKING, "cubic", 0),
    ("day", G.SRC_DAY, "near", 0),
    ("night", G.SRC_NIGHT, "near", 0),
]


def hms(s):
    return "%d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)


def harmonise():
    made = {}
    for name, src, alg, nod in BANDS:
        dst = os.path.join(G.OUTDIR_NOSPACE, "%s_%s.tif" % (PREFIX, name))
        if os.path.exists(dst):
            d = gdal.Open(dst)
            ok = (d.RasterXSize, d.RasterYSize) == (GRID.nx, GRID.ny)
            nb = d.RasterCount
            d = None
            if ok:
                print("  %-7s reused   %d band(s)  %6.2f GB"
                      % (name, nb, os.path.getsize(dst) / 1e9))
                made[name] = dst
                continue
        t = time.time()
        gdal.Warp(dst, src, creationOptions=CO, **GRID.warp_kwargs(alg, nod))
        d = gdal.Open(dst)
        assert (d.RasterXSize, d.RasterYSize) == (GRID.nx, GRID.ny), \
            "%s landed on the wrong grid" % name
        print("  %-7s %-6s %s  %d band(s)  %6.2f GB"
              % (name, alg, hms(time.time() - t), d.RasterCount,
                 os.path.getsize(dst) / 1e9))
        d = None
        made[name] = dst
    return made


def composite(tag, parts):
    out = os.path.join(G.OUTDIR_NOSPACE, "%s_composite_%s.tif" % (PREFIX, tag))
    vrt = os.path.join(G.OUTDIR_NOSPACE, "_%s_%s.vrt" % (PREFIX, tag))
    t = time.time()
    gdal.BuildVRT(vrt, parts, separate=True)
    gdal.Translate(out, vrt, creationOptions=CO)
    d = gdal.Open(out)
    print("  %-8s %s  %d bands  %6.2f GB"
          % (tag, hms(time.time() - t), d.RasterCount, os.path.getsize(out) / 1e9))
    d = None
    os.remove(vrt)
    return out


def relabel(paths):
    try:
        import arcpy
        sr = arcpy.SpatialReference()
        sr.loadFromString(G.TARGET_WKT)
        for p in paths:
            arcpy.management.DefineProjection(p, sr)
        print("  CRS relabelled -> Mars_Equidistant_Cylindrical_CM180")
    except ImportError:
        print("  arcpy unavailable - CRS left as the PROJ WKT")


def apply_smoke():
    """A cheap window over Ius Chasma, separately named.

    KB 28.7: test the call on a window before launching an hours-long job.
    This script writes ~150 GB in the real run, so proving the warp, the VRT,
    the composite and the CRS relabel on ~0.1 GB first is the difference
    between finding a mistake in a minute and finding it in hour three.
    """
    global GRID, PREFIX
    GRID = G.Grid(5394000.0, -355600.0, 100.0, 4096, 2048, "SMOKE")
    PREFIX = "smoke60"


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--smoke", action="store_true",
                    help="4096 x 2048 window over Ius Chasma, outputs named "
                         "smoke60_* - exercises every step in seconds")
    args = ap.parse_args(argv if argv is not None else sys.argv[1:])
    if args.smoke:
        apply_smoke()
    os.makedirs(G.OUTDIR, exist_ok=True)
    G.check()
    print("=" * 78)
    print("HARMONISED STACK + COMPOSITE BANDS OVER +/-60  (tasks 3 + 5)")
    if args.smoke:
        print("*** SMOKE TEST - window over Ius Chasma, smoke60_* outputs ***")
    print("=" * 78)
    print(" ", GRID)
    print("  expect ~150 GB of writes; free space now %.0f GB"
          % (__import__("shutil").disk_usage(G.OUTDIR).free / 1e9))
    t0 = time.time()

    print("\n1. harmonise each source onto G100")
    made = harmonise()

    print("\n2. Composite Bands")
    c4 = composite("4band", [made["viking"], made["day"]])
    c5 = composite("5band", [made["viking"], made["day"], made["night"]])

    print("\n3. label the CRS for ArcGIS")
    relabel(list(made.values()) + [c4, c5])

    print("\ndone in %s" % hms(time.time() - t0))
    print("  the DEM is NOT in these composites, by design - KB 14.2.")
    print("  Use global60_composite_5band.tif for classification; night IR is")
    print("  the most independent band in the stack (KB 18.3).")


if __name__ == "__main__":
    sys.exit(main() or 0)
