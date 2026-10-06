# -*- coding: utf-8 -*-
"""Shared helpers: read a lon/lat window out of any of the three global rasters.

SimpleCylindrical Mars has standard_parallel_1 = 0, so it is plate carree:
x = R*lambda, y = R*phi with R = 3396190 m. The DEM's GCS_Mars_2000_Sphere grid
is the same plate carree lattice expressed in degrees, so a lon/lat window maps
cleanly onto all three rasters and they co-register exactly.
"""
import math

import numpy as np
from osgeo import gdal, osr

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "1024")

R = 3396190.0
VIKING = r"Z:\Mars_Viking_MDIM21_ClrMosaic_global_232m.tif"
THEMIS = r"Z:\Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif"
DEM = r"Z:\Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif"

# The saved extent of the project's "Mars High-Resolution Mosaic Viewer" map.
WINDOW = dict(lon0=-88.7446, lon1=-74.4783, lat0=-13.0527, lat1=-5.7390)


def central_meridian(ds):
    """Central meridian of a projected grid, 0 for a geographic one.

    THEMIS Day IR v12 ships on CM 180 while Viking MDIM and the HRSC/MOLA DEM
    ship on CM 0 -- assuming a common CM puts the THEMIS window half a planet
    away from the other two.
    """
    wkt = ds.GetProjection()
    if not wkt:
        return 0.0
    sr = osr.SpatialReference(wkt=wkt)
    if not sr.IsProjected():
        return 0.0
    return float(sr.GetProjParm("Central_Meridian", 0.0) or 0.0)


def _to_grid(ds, lon, lat):
    """lon/lat -> (col, row) for either a metric or a degree plate-carree grid."""
    gt = ds.GetGeoTransform()
    if abs(gt[1]) > 1.0:                       # metres (SimpleCylindrical)
        dlon = (lon - central_meridian(ds) + 180.0) % 360.0 - 180.0
        x, y = R * math.radians(dlon), R * math.radians(lat)
    else:                                      # degrees (GCS)
        x, y = lon, lat
    return (x - gt[0]) / gt[1], (y - gt[3]) / gt[5]


def read_window(path, win=None, max_px=4096):
    """Read a lon/lat window; returns (array, extent) with array as (h, w[, b])."""
    win = win or WINDOW
    ds = gdal.Open(path, gdal.GA_ReadOnly)
    c0, r0 = _to_grid(ds, win["lon0"], win["lat1"])     # lat1 = north edge
    c1, r1 = _to_grid(ds, win["lon1"], win["lat0"])
    c0, c1 = int(round(min(c0, c1))), int(round(max(c0, c1)))
    r0, r1 = int(round(min(r0, r1))), int(round(max(r0, r1)))
    c0, r0 = max(c0, 0), max(r0, 0)
    c1, r1 = min(c1, ds.RasterXSize), min(r1, ds.RasterYSize)
    w, h = c1 - c0, r1 - r0
    scale = min(1.0, max_px / float(max(w, h)))
    bw, bh = max(1, int(w * scale)), max(1, int(h * scale))
    arr = ds.ReadAsArray(c0, r0, w, h, buf_xsize=bw, buf_ysize=bh)
    ds = None
    if arr.ndim == 3:
        arr = np.transpose(arr, (1, 2, 0))
    ext = (win["lon0"], win["lon1"], win["lat0"], win["lat1"])
    return arr, ext


def stretch(a, lo=2.0, hi=98.0, mask=None):
    """Percentile stretch to 0-255 uint8, ignoring nodata."""
    a = a.astype(np.float32)
    valid = a if mask is None else a[mask]
    p_lo, p_hi = np.percentile(valid, [lo, hi])
    if p_hi <= p_lo:
        p_hi = p_lo + 1.0
    out = np.clip((a - p_lo) / (p_hi - p_lo), 0, 1)
    return (out * 255).astype(np.uint8)


def stretch_rgb(a, lo=0.5, hi=99.5):
    """Per-band percentile stretch, matching the 0.5% min-max used in the project."""
    out = np.empty(a.shape, dtype=np.uint8)
    for b in range(a.shape[2]):
        out[..., b] = stretch(a[..., b], lo, hi)
    return out


def gradient(a):
    """Sobel magnitude -- the same edge/texture measure Slope-on-imagery produces."""
    a = a.astype(np.float32)
    if a.ndim == 3:
        a = a.mean(axis=2)
    gx = np.zeros_like(a)
    gy = np.zeros_like(a)
    gx[:, 1:-1] = a[:, 2:] - a[:, :-2]
    gy[1:-1, :] = a[2:, :] - a[:-2, :]
    return np.hypot(gx, gy)


def hillshade(dem, lat_deg, cell_deg, az=225.0, alt=45.0):
    """Hillshade with a latitude-correct z-factor -- the WARNING 000869 fix.

    One degree of latitude is R*pi/180 m everywhere; one degree of longitude is
    that times cos(lat). Converting the cell size to metres before the gradient
    is exactly what a valid z-factor does.
    """
    m_per_deg_lat = R * math.pi / 180.0
    m_per_deg_lon = m_per_deg_lat * math.cos(math.radians(lat_deg))
    dy = cell_deg * m_per_deg_lat
    dx = cell_deg * m_per_deg_lon
    z = dem.astype(np.float32)
    gy, gx = np.gradient(z, dy, dx)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    az_r, alt_r = math.radians(360.0 - az + 90.0), math.radians(alt)
    shade = (np.sin(alt_r) * np.cos(slope)
             + np.cos(alt_r) * np.sin(slope) * np.cos(az_r - aspect))
    return np.clip(shade, 0, 1)
