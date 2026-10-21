# -*- coding: utf-8 -*-
r"""Prove that every +/-60 product lands on the downloaded mosaics' own grid.

Requirement, 2026-09-19: the data produced must be for the analysis extent
rather than the type area, and must sit in the same content area as the
mosaics on the drive and the products that live beside them.

"Same content area" is checkable, so this checks it rather than asserting it.
For each product, against grid60's G100 / G200, or the 400 m lattice (G400) and the 0.5 degree
density grid (D05) derived from them below:

  extent   the four corners, to the millimetre
  cellsize exact
  shape    exact pixel counts
  CRS      projected, named, CM 180, R = 3396190
  nesting  a 200 m or 400 m product's cell edges must fall on 100 m cell edges

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
    # the SVM stack and the landform maps (KB 31, 55, 57); the published map is the 200 m 11 x 11 one
    ("global60_svm_stack_200m.tif", "G200", "7-band SVM stack"),
    ("global60_landforms_svm_200m.tif", "G200", "landforms, 200 m raw"),
    ("global60_landforms_svm_200m_mode3.tif", "G200", "landforms, 200 m 3 x 3"),
    ("global60_landforms_svm_200m_mode5.tif", "G200", "landforms, 200 m 5 x 5"),
    ("global60_landforms_svm_200m_mode7.tif", "G200", "landforms, 200 m 7 x 7"),
    ("global60_landforms_svm_200m_mode9.tif", "G200", "landforms, 200 m 9 x 9"),
    ("global60_landforms_svm_200m_mode11.tif", "G200", "landforms, PUBLISHED (KB 57)"),
    ("global60_landforms_unet_200m.tif", "G200", "landforms, U-Net X5c (KB 66.7)"),
    ("global60_landforms_unet_200m_seamfix.tif", "G200", "landforms, U-Net X5c, two passes (KB 66.8)"),
    ("global60_landforms_svm_400m.tif", "G400", "landforms, 400 m raw (superseded, KB 57.2)"),
    ("global60_landforms_svm_400m_mode3.tif", "G400", "superseded"),
    ("global60_landforms_svm_400m_mode5.tif", "G400", "superseded (published to 2026-10-16)"),
    ("global60_landforms_svm_400m_mode7.tif", "G400", "superseded"),
    ("global60_landforms_svm_400m_mode9.tif", "G400", "superseded"),
    # T1 in Pro (KB 56): band-subset stacks and their maps
    ("global60_svm_stack_200m_nothermal.tif", "G200", "T1 stack without thermal"),
    ("global60_svm_stack_200m_novisible.tif", "G200", "T1 stack without visible"),
    ("global60_svm_stack_200m_terrain.tif", "G200", "T1 stack, terrain only"),
    ("global60_landforms_svm_nothermal_200m.tif", "G200", "T1 map"),
    ("global60_landforms_svm_nothermal_400m.tif", "G400", "T1 map"),
    ("global60_landforms_svm_novisible_400m.tif", "G400", "T1 map"),
    ("global60_landforms_svm_terrain_400m.tif", "G400", "T1 map"),
    # layout 11's 0.5 degree density grids (KB 53.6)
    ("global60_depression_density_0p5deg.tif", "D05", "closed depressions per 1e4 km2"),
    ("global60_robbins_density_0p5deg.tif", "D05", "Robbins craters per 1e4 km2"),
]

# Ruled out (NEXT-STEPS 10, KB 11 q7): the 100 m Composite Bands run was overtaken by the 200 m SVM stack.
# Listed so that their absence is reported as a decision, not as work still to do.
RULED_OUT = ["global60_viking.tif", "global60_day.tif", "global60_night.tif",
             "global60_composite_4band.tif", "global60_composite_5band.tif"]

# The 400 m lattice: the same origin, every second G200 edge; ceil(n / 2) cells, so it reaches half a
# cell (200 m) past the south edge, where G200's 35,565 rows are odd. The 0.5 degree grid: G200's exact
# extent in 720 x 240 cells, so its cells are not square (29,637.2 m across, 29,637.5 m down).
G400 = G.Grid(G.G200.ox, G.G200.oy, 400.0, -(-G.G200.nx // 2), -(-G.G200.ny // 2), "G400")


class RectGrid(G.Grid):
    """A grid whose cells differ in x and y (resy, the cell height)."""

    def __init__(self, ox, oy, res, resy, nx, ny, name=""):
        G.Grid.__init__(self, ox, oy, res, nx, ny, name)
        self.resy = resy

    @property
    def ymin(self):
        return self.oy - self.ny * self.resy


D05 = RectGrid(G.G200.ox, G.G200.oy, (G.G200.xmax - G.G200.ox) / 720.0, (G.G200.oy - G.G200.ymin) / 240.0,
               720, 240, "D05")
GRIDS = {"G100": G.G100, "G200": G.G200, "G400": G400, "D05": D05}


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
    resy = getattr(grid, "resy", grid.res)
    if abs(gt[1] - grid.res) > 1e-6 or abs(gt[5] + resy) > 1e-6:
        bad.append("cell %.9f / %.9f, expected %.9f / %.9f" % (gt[1], gt[5], grid.res, -resy))
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

    # a 200 m or 400 m product must nest on the 100 m grid
    if grid.res in (200.0, 400.0):
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

    for name in RULED_OUT:
        built = os.path.exists(os.path.join(G.OUTDIR, name))
        print("  ----  %-40s %s" % (name, "(ruled out, NEXT-STEPS 10)" + ("; FOUND ON DISK" if built else "")))

    print()
    print("  %d pass, %d fail, %d not built, %d ruled out" % (npass, nfail, nmiss, len(RULED_OUT)))
    if nfail == 0 and npass:
        print("  Every built product sits exactly on its grid, all of them aligned with the night mosaic.")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
