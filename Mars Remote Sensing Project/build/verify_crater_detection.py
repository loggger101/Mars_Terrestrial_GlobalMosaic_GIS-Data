# -*- coding: utf-8 -*-
r"""Does the fill-depth crater detector actually work? Measure it.

The Ius Chasma type area contains ZERO named craters - the nearest are
Oudemans (124.2 km, 268.23E 9.84S) and Perrotin (82.8 km, 282.06E 2.82S), both
just outside the box. So the detector cannot be validated in place.

This runs the identical detector over two small windows built around those two
craters and compares the recovered diameter and position against the IAU
gazetteer. Each window is ~25 Mpx - smaller than the type area, so this is a
laptop job.

It also sweeps the shape filters, because the type-area run returned a 140.9 km
"crater" that is almost certainly part of the chasma.
"""
import os, time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
import numpy as np
from osgeo import gdal
import arcpy
from arcpy.sa import Fill
from scipy import ndimage
gdal.UseExceptions()

WS = junction("TypeArea")
VAL = os.path.join(WS, "val")
GDB = on_drive(r"Mars Project\Mars Project.gdb")
DEM_SRC = on_drive(r"Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")
TSRS = ("+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=180 +x_0=0 +y_0=0 +R=3396190 "
        "+units=m +no_defs")
R = 3396190.0
DEG = R * np.pi / 180.0
RES = 100.0
MIN_DEPTH_M = 20.0
os.makedirs(VAL, exist_ok=True)
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
t0 = time.time()

# name, lon0, lon1, lat0, lat1  - windows chosen to hold the crater with room
WINDOWS = [("oudemans", 263.5, 273.0, -14.5, -5.5),
           ("perrotin", 277.5, 286.5, -7.5, 1.5)]


def bounds(lon0, lon1, lat0, lat1):
    return ((lon0 - 180.0) * DEG, lat0 * DEG, (lon1 - 180.0) * DEG, lat1 * DEG)


def band(p):
    ds = gdal.Open(p)
    b = ds.GetRasterBand(1)
    a = b.ReadAsArray().astype(np.float32)
    gt = ds.GetGeoTransform()
    del b, ds
    return a, gt


def detect(depth, gt, min_diam=1.0, max_diam=300.0, max_aspect=2.5, min_fill=0.45):
    """The identical detector from make_crater_candidates.py."""
    lab, n = ndimage.label(depth > MIN_DEPTH_M)
    if n == 0:
        return np.empty(0), np.empty(0), np.empty(0), np.empty(0), np.empty(0), 0
    idx = np.arange(1, n + 1)
    area_px = np.bincount(lab.ravel())[1:]
    maxd = ndimage.maximum(depth, lab, idx)
    objs = ndimage.find_objects(lab)
    com = ndimage.center_of_mass(depth > MIN_DEPTH_M, lab, idx)
    cy = np.array([c[0] for c in com]); cx = np.array([c[1] for c in com])
    diam = 2.0 * np.sqrt(area_px * 0.01 / np.pi)
    hh = np.array([o[0].stop - o[0].start for o in objs], float)
    ww = np.array([o[1].stop - o[1].start for o in objs], float)
    asp = np.maximum(hh, ww) / np.maximum(np.minimum(hh, ww), 1.0)
    fr = area_px / np.maximum(hh * ww, 1.0)
    k = ((diam >= min_diam) & (diam <= max_diam) & (asp <= max_aspect) & (fr >= min_fill))
    X = gt[0] + (cx + 0.5) * gt[1]
    Y = gt[3] + (cy + 0.5) * gt[5]
    return (180.0 + X / DEG)[k], (Y / DEG)[k], diam[k], asp[k], fr[k], n


# the two truth craters
truth = {}
for fc in ("MARS_nomenclature_craters_gt100km_March2019_3",
           "MARS_nomenclature_craters_lt100km_March2019_3"):
    with arcpy.da.SearchCursor(os.path.join(GDB, fc),
                               ["name", "diameter", "center_lon", "center_lat"]) as c:
        for nm, d, lo, la in c:
            if nm and nm.lower() in ("oudemans", "perrotin"):
                truth[nm.lower()] = (nm, d, lo % 360.0, la)

print("=" * 78)
print("VALIDATING THE FILL-DEPTH CRATER DETECTOR ON TWO NAMED CRATERS")
print("=" * 78)

results = {}
for name, lo0, lo1, la0, la1 in WINDOWS:
    dem = os.path.join(VAL, "%s_dem.tif" % name)
    fil = os.path.join(VAL, "%s_fill.tif" % name)
    dep = os.path.join(VAL, "%s_depth.tif" % name)
    if not os.path.exists(dem):
        gdal.Warp(dem, DEM_SRC, dstSRS=TSRS, outputBounds=bounds(lo0, lo1, la0, la1),
                  xRes=RES, yRes=RES, resampleAlg="cubic", srcNodata=-32768,
                  dstNodata=-32768, multithread=True,
                  creationOptions=["TILED=YES", "COMPRESS=DEFLATE"])
    d0 = gdal.Open(dem)
    px = d0.RasterXSize * d0.RasterYSize
    del d0
    if not arcpy.Exists(fil):
        Fill(dem).save(fil)
    if not os.path.exists(dep):
        a, gt = band(dem)
        f, _ = band(fil)
        m = (a > -32000) & (f > -32000)
        out = np.where(m, f - a, 0.0).astype(np.float32)
        drv = gdal.GetDriverByName("GTiff")
        ref = gdal.Open(dem)
        ds = drv.Create(dep, ref.RasterXSize, ref.RasterYSize, 1, gdal.GDT_Float32,
                        options=["TILED=YES", "COMPRESS=DEFLATE"])
        ds.SetGeoTransform(ref.GetGeoTransform())
        ds.SetProjection(ref.GetProjection())
        b = ds.GetRasterBand(1); b.WriteArray(out); b.FlushCache()
        del b, ds, ref, a, f, out
    depth, gt = band(dep)
    print("\n%s window  %.1f-%.1fE  %.1f-%.1f   %s px   [%.0fs]"
          % (name, lo0, lo1, la0, la1, format(px, ","), time.time() - t0))

    tn, td, tlo, tla = truth[name]
    results[name] = (depth, gt, (tn, td, tlo, tla))

    lon, lat, diam, asp, fr, nsink = detect(depth, gt)
    dkm = np.sqrt(((lon - tlo) * DEG * np.cos(np.radians(tla)) / 1000.0) ** 2 +
                  ((lat - tla) * DEG / 1000.0) ** 2)
    j = int(np.argmin(dkm))
    print("   IAU %-10s %7.1f km at %.2fE %.2f" % (tn, td, tlo, tla))
    print("   detector: %s sinks -> %d candidates" % (format(nsink, ","), len(diam)))
    print("   nearest candidate: %6.2f km away   diameter %7.1f km  (IAU %7.1f)  "
          "error %+.1f%%   aspect %.2f fill %.2f"
          % (dkm[j], diam[j], td, 100.0 * (diam[j] - td) / td, asp[j], fr[j]))
    big = np.argsort(-diam)[:3]
    print("   3 largest in window: " +
          "  ".join("%.1f km @%.2fE %.2f" % (diam[i], lon[i], lat[i]) for i in big))

# ------------------------------------------------------------ filter sweep
print("\n" + "=" * 78)
print("SHAPE-FILTER SWEEP - does a tighter filter still recover the truth craters?")
print("=" * 78)
print("  aspect  fill    %-22s %-22s" % ("Oudemans err / rank", "Perrotin err / rank"))
for max_asp, min_fr in [(2.5, 0.45), (2.2, 0.50), (2.0, 0.55), (1.8, 0.60), (1.5, 0.65)]:
    cells = []
    for name in ("oudemans", "perrotin"):
        depth, gt, (tn, td, tlo, tla) = results[name]
        lon, lat, diam, asp, fr, _ = detect(depth, gt, max_aspect=max_asp, min_fill=min_fr)
        if len(diam) == 0:
            cells.append("%-22s" % "none")
            continue
        dkm = np.sqrt(((lon - tlo) * DEG * np.cos(np.radians(tla)) / 1000.0) ** 2 +
                      ((lat - tla) * DEG / 1000.0) ** 2)
        j = int(np.argmin(dkm))
        found = dkm[j] <= max(0.5 * td, 2.0)
        rank = int((diam > diam[j]).sum()) + 1
        cells.append("%-22s" % ("%+6.1f%%  rank %d/%d%s" %
                     (100.0 * (diam[j] - td) / td, rank, len(diam), "" if found else "  MISS")))
    print("   %.1f    %.2f   %s %s" % (max_asp, min_fr, cells[0], cells[1]))

arcpy.CheckInExtension("Spatial")
print("\ndone in %.1f s" % (time.time() - t0))
