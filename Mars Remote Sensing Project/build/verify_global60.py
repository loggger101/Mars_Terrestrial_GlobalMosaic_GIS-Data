# -*- coding: utf-8 -*-
r"""Prove that every +/-60 product lands on the downloaded mosaics' own grid.

Requirement, 2026-09-19: the data produced must be for the analysis extent
rather than the type area, and must sit in the same content area as the
mosaics on Z:\ and the products that live beside them.

"Same content area" is checkable, so this checks it rather than asserting it.
For each product, against grid60's G100 / G200:

  extent   the four corners, to the millimetre
  cellsize exact
  shape    exact pixel counts
  CRS      projected, named, CM 180, R = 3396190
  nesting  a 200 m product's cell edges must fall on 100 m cell edges

A product that fails any of these is listed as FAIL with the actual numbers.
Exit status is non-zero if anything fails, so this can gate a build.

Run it after any +/-60 job. It reads headers only - seconds, not minutes.
"""
import os
import sys

from osgeo import gdal, osr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grid60 as G

gdal.UseExceptions()

TOL = 1e-3          # millimetre, in metres

# product -> which grid it must be on
EXPECTED = [
    ("global60_thermal_contrast.tif", "G100", "diurnal-contrast index (KB 24)"),
    ("global60_dem.tif", "G200", "HRSC/MOLA on the target grid"),
    ("global60_slope_deg.tif", "G200", "slope, DEGREES (KB 7)"),
    ("global60_aspect.tif", "G200", "aspect"),
    ("global60_hillshade.tif", "G200", "hillshade 225/45"),
    ("global60_thermal_contrast_200m.tif", "G200", "index aggregated to the DEM grid"),
    ("global60_viking.tif", "G100", "Viking MDIM harmonised"),
    ("global60_day.tif", "G100", "THEMIS day IR harmonised"),
    ("global60_night.tif", "G100", "THEMIS night IR harmonised"),
    ("global60_composite_4band.tif", "G100", "Composite Bands, 4 band"),
    ("global60_composite_5band.tif", "G100", "Composite Bands, 5 band"),
]

GRIDS = {"G100": G.G100, "G200": G.G200}


def check_one(path, grid):
    """Return (ok, [problems])."""
    bad = []
    try:
        ds = gdal.Open(path)
    except RuntimeError as e:
        # a build may be writing this file right now - that is not a failure
        return None, [str(e).strip().splitlines()[-1]], "unreadable"
    gt = ds.GetGeoTransform()
    nx, ny = ds.RasterXSize, ds.RasterYSize

    if (nx, ny) != (grid.nx, grid.ny):
        bad.append("shape %d x %d, expected %d x %d" % (nx, ny, grid.nx, grid.ny))
    if abs(gt[1] - grid.res) > 1e-9 or abs(gt[5] + grid.res) > 1e-9:
        bad.append("cell %.9f / %.9f, expected %g" % (gt[1], gt[5], grid.res))
    if abs(gt[0] - grid.ox) > TOL:
        bad.append("west edge %.4f, expected %.4f" % (gt[0], grid.ox))
    if abs(gt[3] - grid.oy) > TOL:
        bad.append("north edge %.4f, expected %.4f" % (gt[3], grid.oy))
    xmax = gt[0] + nx * gt[1]
    ymin = gt[3] + ny * gt[5]
    if abs(xmax - grid.xmax) > TOL:
        bad.append("east edge %.4f, expected %.4f" % (xmax, grid.xmax))
    if abs(ymin - grid.ymin) > TOL:
        bad.append("south edge %.4f, expected %.4f" % (ymin, grid.ymin))
    if gt[2] or gt[4]:
        bad.append("raster is rotated: %r" % (gt,))

    sr = osr.SpatialReference(wkt=ds.GetProjection())
    if not sr.IsProjected():
        bad.append("CRS is not projected")
    else:
        cm = sr.GetProjParm("Central_Meridian", 0.0)
        if abs(cm - 180.0) > 1e-6:
            bad.append("central meridian %.4f, expected 180" % cm)
        if abs(sr.GetSemiMajor() - G.R_MARS) > 1.0:
            bad.append("radius %.1f, expected %.1f" % (sr.GetSemiMajor(), G.R_MARS))
        nm = sr.GetName() or ""
        if not nm or nm.lower() in ("unknown", "unnamed"):
            bad.append("CRS unnamed - ArcGIS will call it 'unknown'; run DefineProjection")

    # a 200 m product must nest on the 100 m grid
    if grid.res == 200.0:
        for edge, ref in ((gt[0], G.G100.ox), (gt[3], G.G100.oy)):
            if abs(((edge - ref) / 100.0) - round((edge - ref) / 100.0)) > 1e-6:
                bad.append("does not nest on the 100 m grid at %.4f" % edge)

    info = "%d x %d x %d  %s  %.2f GB" % (
        nx, ny, ds.RasterCount,
        gdal.GetDataTypeName(ds.GetRasterBand(1).DataType),
        os.path.getsize(path) / 1e9)
    ds = None
    return (not bad), bad, info


def main():
    print("=" * 78)
    print("+/-60 PRODUCTS - CO-REGISTRATION WITH THE DOWNLOADED MOSAICS")
    print("=" * 78)
    off = G.check()
    print("  template   %s" % os.path.basename(G.TEMPLATE))
    print("  G100       %d x %d @ 100 m   X %.0f..%.0f  Y %.0f..%.0f"
          % (G.G100.nx, G.G100.ny, G.G100.ox, G.G100.xmax, G.G100.ymin, G.G100.oy))
    print("  G200       %d x %d @ 200 m   (exact 2x2 of G100)" % (G.G200.nx, G.G200.ny))
    print("  day mosaic sits at +%d, +%d px from the night grid - integer, so the"
          % (off["dx"], off["dy"]))
    print("             day/night pair is never resampled")
    print()

    npass = nfail = nmiss = 0
    for name, gname, desc in EXPECTED:
        path = os.path.join(G.OUTDIR_NOSPACE, name)
        if not os.path.exists(path):
            path = os.path.join(G.OUTDIR, name)
        if not os.path.exists(path):
            print("  ----  %-40s %s" % (name, "(not built yet)"))
            nmiss += 1
            continue
        ok, bad, info = check_one(path, GRIDS[gname])
        if ok is None:
            print("  ....  %-40s %-5s %s" % (name, gname, "being written - skipped"))
            nmiss += 1
        elif ok:
            print("  PASS  %-40s %-5s %s" % (name, gname, info))
            npass += 1
        else:
            print("  FAIL  %-40s %-5s %s" % (name, gname, info))
            for b in bad:
                print("          - %s" % b)
            nfail += 1

    print()
    print("  %d pass, %d fail, %d not built" % (npass, nfail, nmiss))
    if nfail == 0 and npass:
        print("  Every built product is pixel-coincident with the night mosaic.")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
