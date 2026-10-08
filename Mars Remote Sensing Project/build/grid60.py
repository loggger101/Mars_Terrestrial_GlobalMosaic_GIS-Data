# -*- coding: utf-8 -*-
r"""The canonical +/-60 deg target grid, and the only place it is defined.

KB 16.4: "Clip or snap everything to the night raster's extent, since it is the
binding one and the day grid aligns to it exactly." This module is that rule as
code. Nothing here is hardcoded from a table - the grid is READ from the night
mosaic on Z:\ every time, so a product built through this module is by
construction on the same content area as the downloaded mosaics.

Two nested grids, both with the night mosaic's origin and footprint:

    G100   213388 x 71130  @ 100 m   - the imagery grid. Day and night are
                                       native here and are NEVER resampled.
    G200   106694 x 35565  @ 200 m   - the DEM grid. Exactly 2x2 aggregation
                                       of G100: same origin, same footprint,
                                       every 200 m cell edge falls on a 100 m
                                       cell edge. HRSC/MOLA is native 200 m, so
                                       terrain and hydrology belong here and
                                       running them at 100 m costs 4x for no
                                       information.

Use TARGET_WKT (not the PROJ string) when labelling outputs for ArcGIS - see
make_typearea_stack.py, gdal.Warp writes a WKT that Pro reads as "unknown".
"""
import os
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
import math

from osgeo import gdal

gdal.UseExceptions()

# ---------------------------------------------------------------- the sources
ROOT = on_drive()
SRC_VIKING = os.path.join(ROOT, "Mars_Viking_MDIM21_ClrMosaic_global_232m.tif")
SRC_DAY = os.path.join(ROOT, "Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif")
SRC_NIGHT = os.path.join(ROOT, "Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif")
SRC_DEM = os.path.join(ROOT, "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")

# the binding raster - the +/-60 extent IS this file's extent
TEMPLATE = SRC_NIGHT

R_MARS = 3396190.0

TARGET_PROJ4 = ("+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=180 +x_0=0 +y_0=0 "
                "+R=3396190 +units=m +no_defs")

# The named Esri WKT equivalent. Same coordinates, a name ArcGIS recognises.
TARGET_WKT = ('PROJCS["Mars_Equidistant_Cylindrical_CM180",'
              'GEOGCS["GCS_Mars_2000_Sphere",DATUM["D_Mars_2000_Sphere",'
              'SPHEROID["Mars_2000_Sphere_IAU_IAG",3396190.0,0.0]],'
              'PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],'
              'PROJECTION["Equidistant_Cylindrical"],PARAMETER["False_Easting",0.0],'
              'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",180.0],'
              'PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]')

# where +/-60 products go - beside the type-area products, not mixed into them
OUTDIR = on_drive(r"Mars Project\Global60")
# junction form, for the legacy Spatial Analyst tools that reject spaces (KB 19.1)
OUTDIR_NOSPACE = on_drive(r"Global60")


class Grid(object):
    """An axis-aligned raster grid: origin, cell size, size in cells."""

    __slots__ = ("ox", "oy", "res", "nx", "ny", "name")

    def __init__(self, ox, oy, res, nx, ny, name=""):
        self.ox, self.oy, self.res, self.nx, self.ny, self.name = ox, oy, res, nx, ny, name

    # ---- geometry -------------------------------------------------------
    @property
    def geotransform(self):
        return (self.ox, self.res, 0.0, self.oy, 0.0, -self.res)

    @property
    def xmax(self):
        return self.ox + self.nx * self.res

    @property
    def ymin(self):
        return self.oy - self.ny * self.res

    @property
    def bounds(self):
        """(xmin, ymin, xmax, ymax) - the order gdal.Warp(outputBounds=) wants."""
        return (self.ox, self.ymin, self.xmax, self.oy)

    @property
    def npix(self):
        return self.nx * self.ny

    def lat_of(self, y):
        return math.degrees(y / R_MARS)

    def lon_of(self, x):
        return (math.degrees(x / R_MARS) + 180.0) % 360.0

    # ---- warp ------------------------------------------------------------
    def warp_kwargs(self, resample="near", nodata=None):
        """Everything gdal.Warp needs to land a source exactly on this grid."""
        kw = dict(dstSRS=TARGET_PROJ4, outputBounds=self.bounds,
                  xRes=self.res, yRes=self.res, resampleAlg=resample,
                  targetAlignedPixels=False, multithread=True)
        if nodata is not None:
            kw.update(srcNodata=nodata, dstNodata=nodata)
        return kw

    # ---- tiling ----------------------------------------------------------
    def tiles(self, tile=8192, overlap=0):
        """Yield (col, row, xoff, yoff, xsize, ysize) covering the grid.

        `overlap` pads each window outward, clipped to the grid - use it for
        neighbourhood operations (Fill, FlowDirection, Slope) where a tile edge
        would otherwise be a false boundary, then trim the pad on write.
        """
        for row, yoff in enumerate(range(0, self.ny, tile)):
            for col, xoff in enumerate(range(0, self.nx, tile)):
                x0 = max(0, xoff - overlap)
                y0 = max(0, yoff - overlap)
                x1 = min(self.nx, xoff + tile + overlap)
                y1 = min(self.ny, yoff + tile + overlap)
                yield (col, row, x0, y0, x1 - x0, y1 - y0)

    def n_tiles(self, tile=8192):
        return (((self.nx + tile - 1) // tile) * ((self.ny + tile - 1) // tile))

    def sub(self, xoff, yoff, xsize, ysize, name=""):
        """The Grid describing a window of this one - so a tile is a Grid too."""
        return Grid(self.ox + xoff * self.res, self.oy - yoff * self.res,
                    self.res, xsize, ysize, name or (self.name + "/sub"))

    def __repr__(self):
        return ("<Grid %s %d x %d @ %g m  X %.0f..%.0f  Y %.0f..%.0f  "
                "lat %+.3f..%+.3f  %.3f Gpx>"
                % (self.name, self.nx, self.ny, self.res, self.ox, self.xmax,
                   self.ymin, self.oy, self.lat_of(self.ymin),
                   self.lat_of(self.oy), self.npix / 1e9))


def _read_template():
    """Read the +/-60 grid off the night mosaic rather than trusting a table."""
    ds = gdal.Open(TEMPLATE)
    gt = ds.GetGeoTransform()
    nx, ny = ds.RasterXSize, ds.RasterYSize
    ds = None
    if abs(gt[1] - 100.0) > 1e-6 or abs(gt[5] + 100.0) > 1e-6:
        raise RuntimeError("night mosaic is not 100 m: %r" % (gt,))
    return Grid(gt[0], gt[3], gt[1], nx, ny, "G100")


G100 = _read_template()
# 2x2 aggregation: same origin, same footprint, nested cell edges
G200 = Grid(G100.ox, G100.oy, 200.0, G100.nx // 2, G100.ny // 2, "G200")

# the type area, for products that stay local (KB 18.1)
IUS = Grid(5394000.0, -355600.0, 100.0, 8891, 4150, "IUS")


def check():
    """Assert the two grids really do co-register, and report. Run on import
    in scripts that matter - a silent grid mismatch is KB 4's whole lesson."""
    assert G200.ox == G100.ox and G200.oy == G100.oy, "origins differ"
    assert abs(G200.xmax - G100.xmax) < 1e-6, "east edges differ"
    assert abs(G200.ymin - G100.ymin) < 1e-6, "south edges differ"
    assert G100.nx % 2 == 0 and G100.ny % 2 == 0, "G100 not evenly halvable"
    # day mosaic must be an exact integer pixel offset from the night grid
    ds = gdal.Open(SRC_DAY)
    dgt = ds.GetGeoTransform()
    ds = None
    dx = (G100.ox - dgt[0]) / 100.0
    dy = (dgt[3] - G100.oy) / 100.0
    assert abs(dx - round(dx)) < 1e-9 and abs(dy - round(dy)) < 1e-9, \
        "day mosaic is NOT pixel-aligned to night: dx=%r dy=%r" % (dx, dy)
    return dict(dx=int(round(dx)), dy=int(round(dy)))


if __name__ == "__main__":
    off = check()
    print("target CRS      Mars_Equidistant_Cylindrical_CM180 (eqc, CM 180, R=%.0f)" % R_MARS)
    print("template        %s" % TEMPLATE)
    print("day offset      %+d px in x, %+d px in y  (exact - no resampling)"
          % (off["dx"], off["dy"]))
    for g in (G100, G200, IUS):
        print(g)
    print()
    print("%-6s %-22s %10s %10s %10s" % ("grid", "product type", "U8", "I16", "F32"))
    for g in (G100, G200):
        print("%-6s %-22s %9.1fG %9.1fG %9.1fG"
              % (g.name, "one band, uncompressed", g.npix / 1e9, g.npix * 2 / 1e9,
                 g.npix * 4 / 1e9))
    print()
    print("scale vs the Ius type area: G100 = %.0fx,  G200 = %.0fx"
          % (G100.npix / IUS.npix, G200.npix / IUS.npix))
    for t in (4096, 8192, 16384):
        print("tiles @ %5d px: G100 %4d   G200 %4d" % (t, G100.n_tiles(t), G200.n_tiles(t)))
