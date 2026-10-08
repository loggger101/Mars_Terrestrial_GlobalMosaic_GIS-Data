# -*- coding: utf-8 -*-
r"""Candidate impact craters for a type area (Ius Chasma; --area ath for Athabasca, KB §42) - task 12 from zero.

The project's only crater data is the IAU gazetteer: 141 named craters >100 km
and 972 <100 km, planet-wide. That is a NAME LIST, not an inventory, and
size-frequency dating cannot be done from it (KB 14, 25).

The detector falls out of KB 25.1. Fill flooded every closed depression in the
scene - which is what a crater is, topographically. ius_filldepth.tif is
therefore already a crater-candidate raster; it only needs thresholding,
shape-filtering and measuring.

Validated against the gazetteer: recall and diameter agreement on named craters
inside the type area, which is an accuracy check this project has never had.

Run with the ArcGIS interpreter. Writes Landform_CraterCandidates_auto - a
SEPARATE class, like the channels. Landform_CraterRims stays manual.
"""
import os, time, datetime
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
import areas
A = areas.current()
PFX = A["prefix"] + "_"
import numpy as np
from osgeo import gdal
import arcpy
gdal.UseExceptions()

WS = A["ws"]()
GDB = on_drive(r"Mars Project\Mars Project.gdb")
TARGET = A["craters"]
DEPTH = os.path.join(WS, PFX + "filldepth.tif")
R = 3396190.0
DEG = R * np.pi / 180.0
CELL_KM2 = 0.01                 # 100 m cells
t0 = time.time()

# --- filters, each with a reason -------------------------------------------
MIN_DEPTH_M = 20.0     # below this is DEM noise in a 200 m blend
MIN_DIAM_KM = 1.0      # the project's own resolving limit (KB 23.5)
MAX_DIAM_KM = 300.0    # nothing larger is a crater in this window
# Tightened 2026-09-19 on the evidence of verify_crater_detection.py: at 2.0/0.55
# Perrotin is recovered as the LARGEST candidate in its window (rank 1 of 1,321)
# at -7.1% diameter error, ~20% of the candidate set is dropped, and the 140.9 km
# chasma fragment that 2.5/0.45 admitted (aspect 2.39) goes with it.
MAX_ASPECT = 2.0       # craters are round; the chasma is not
MIN_FILLRATIO = 0.55   # area / bbox area; a perfect circle gives pi/4 = 0.785


def step(m):
    print("  [%6.1fs] %s" % (time.time() - t0, m), flush=True)


def band(p):
    ds = gdal.Open(p)
    b = ds.GetRasterBand(1)
    a = b.ReadAsArray().astype(np.float32)
    gt = ds.GetGeoTransform()
    del b, ds
    return a, gt


print("=" * 76)
print("CANDIDATE IMPACT CRATERS - " + A["name"])
print("=" * 76)

depth, gt = band(DEPTH)
step("read fill depth  %dx%d" % (depth.shape[1], depth.shape[0]))

from scipy import ndimage
sink = depth > MIN_DEPTH_M
lab, n = ndimage.label(sink)
step("connected depressions > %.0f m: %s" % (MIN_DEPTH_M, format(n, ",")))

idx = np.arange(1, n + 1)
area_px = np.bincount(lab.ravel())[1:]
maxd = ndimage.maximum(depth, lab, idx)
meand = ndimage.mean(depth, lab, idx)
objs = ndimage.find_objects(lab)
com = ndimage.center_of_mass(sink, lab, idx)
cy = np.array([c[0] for c in com])
cx = np.array([c[1] for c in com])

area_km2 = area_px * CELL_KM2
diam_km = 2.0 * np.sqrt(area_km2 / np.pi)
hh = np.array([o[0].stop - o[0].start for o in objs], float)
ww = np.array([o[1].stop - o[1].start for o in objs], float)
aspect = np.maximum(hh, ww) / np.maximum(np.minimum(hh, ww), 1.0)
fillratio = area_px / np.maximum(hh * ww, 1.0)

keep = ((diam_km >= MIN_DIAM_KM) & (diam_km <= MAX_DIAM_KM) &
        (aspect <= MAX_ASPECT) & (fillratio >= MIN_FILLRATIO))
step("after shape + size filters: %s candidates" % format(int(keep.sum()), ","))
print("     dropped: %6d too small  %5d too elongated  %5d too ragged  %4d too large"
      % (int((diam_km < MIN_DIAM_KM).sum()), int((aspect > MAX_ASPECT).sum()),
         int((fillratio < MIN_FILLRATIO).sum()), int((diam_km > MAX_DIAM_KM).sum())))

# map coords -> lon/lat (eqc, CM180)
X = gt[0] + (cx + 0.5) * gt[1]
Y = gt[3] + (cy + 0.5) * gt[5]
lon = 180.0 + X / DEG
lat = Y / DEG

# ------------------------------------------------- validate on the gazetteer
print("\n" + "=" * 76)
print("VALIDATION AGAINST THE IAU GAZETTEER")
print("=" * 76)
named = []
for fc in ("MARS_nomenclature_craters_gt100km_March2019_3",
           "MARS_nomenclature_craters_lt100km_March2019_3"):
    with arcpy.da.SearchCursor(os.path.join(GDB, fc),
                               ["name", "diameter", "center_lon", "center_lat"]) as c:
        for nm, dia, lo, la in c:
            if lo is None or la is None:
                continue
            lo = lo % 360.0
            if 271.0 <= lo <= 286.0 and -13.0 <= la <= -6.0:
                named.append((nm, dia, lo, la))
print("  named craters inside the type area: %d" % len(named))

kl, kla, kd = lon[keep], lat[keep], diam_km[keep]
hits = 0
for nm, dia, lo, la in sorted(named, key=lambda r: -r[1]):
    dkm = np.sqrt(((kl - lo) * DEG * np.cos(np.radians(la)) / 1000.0) ** 2 +
                  ((kla - la) * DEG / 1000.0) ** 2)
    j = int(np.argmin(dkm))
    ok = dkm[j] <= max(0.5 * dia, 2.0)
    hits += ok
    print("   %-14s IAU %7.1f km   nearest candidate %6.1f km away, %7.1f km across   %s"
          % (nm, dia, dkm[j], kd[j], "MATCH" if ok else "miss"))
if named:
    print("\n  recall on named craters: %d/%d = %.0f%%"
          % (hits, len(named), 100.0 * hits / len(named)))

# ------------------------------------------------------------ write the class
print("\n" + "=" * 76)
keep_ids = idx[keep]
mp = os.path.join(WS, PFX + "cratermask.tif")
drv = gdal.GetDriverByName("GTiff")
ref = gdal.Open(DEPTH)
ds = drv.Create(mp, ref.RasterXSize, ref.RasterYSize, 1, gdal.GDT_Int32,
                options=["TILED=YES", "COMPRESS=DEFLATE"])
ds.SetGeoTransform(ref.GetGeoTransform())
ds.SetProjection(ref.GetProjection())
b = ds.GetRasterBand(1)
b.WriteArray(np.where(np.isin(lab, keep_ids), lab, 0))
b.SetNoDataValue(0)
b.FlushCache()
del b, ds, ref
step("crater mask raster")

arcpy.env.overwriteOutput = True
SCRATCH = os.path.join(WS, "chan_scratch.gdb")
if not arcpy.Exists(SCRATCH):
    arcpy.management.CreateFileGDB(WS, "chan_scratch.gdb")
polys = os.path.join(SCRATCH, "crater_raw")
arcpy.conversion.RasterToPolygon(mp, polys, "SIMPLIFY", "Value")
step("RasterToPolygon -> %s parts" % arcpy.management.GetCount(polys)[0])

stat = {int(i): (float(d), float(mx), float(mn), float(a), float(fr), float(lo), float(la))
        for i, d, mx, mn, a, fr, lo, la in zip(idx[keep], diam_km[keep], maxd[keep],
                                               meand[keep], aspect[keep], fillratio[keep],
                                               lon[keep], lat[keep])}
zi = os.path.join(SCRATCH, "zs_cidx")
arcpy.sa.ZonalStatisticsAsTable(mp, "Value", os.path.join(WS, PFX + "thermal_contrast.tif"),
                                zi, "DATA", "MEAN")
idx_by = {r[0]: r[1] for r in arcpy.da.SearchCursor(zi, ["Value", "MEAN"])}
step("thermal index per candidate")

out = os.path.join(GDB, TARGET)
if arcpy.Exists(out):
    arcpy.management.Delete(out)
sr = arcpy.Describe(polys).spatialReference
arcpy.management.CreateFeatureclass(GDB, TARGET, "POLYGON", spatial_reference=sr)
for nm, ty, ln in [("UnitName", "TEXT", 60), ("Confidence", "TEXT", 12),
                   ("Evidence", "TEXT", 90), ("DiameterKm", "DOUBLE", None),
                   ("DepthMaxM", "DOUBLE", None), ("DepthMeanM", "DOUBLE", None),
                   ("Aspect", "DOUBLE", None), ("FillRatio", "DOUBLE", None),
                   ("ThermIdx", "DOUBLE", None), ("CenterLon", "DOUBLE", None),
                   ("CenterLat", "DOUBLE", None), ("IAUName", "TEXT", 40),
                   ("Preservation", "TEXT", 20), ("Notes", "TEXT", 200),
                   ("MappedBy", "TEXT", 38), ("MappedOn", "DATE", None)]:
    if ln:
        arcpy.management.AddField(out, nm, ty, field_length=ln)
    else:
        arcpy.management.AddField(out, nm, ty)

today = datetime.datetime(2026, 9, 19)
cols = ["SHAPE@", "UnitName", "Confidence", "Evidence", "DiameterKm", "DepthMaxM",
        "DepthMeanM", "Aspect", "FillRatio", "ThermIdx", "CenterLon", "CenterLat",
        "IAUName", "Preservation", "Notes", "MappedBy", "MappedOn"]
written = 0
with arcpy.da.InsertCursor(out, cols) as ic:
    for shp, gv in arcpy.da.SearchCursor(polys, ["SHAPE@", "gridcode"]):
        st = stat.get(int(gv))
        if st is None:
            continue
        d, mx, mn, asp, fr, lo, la = st
        iau = None
        for nm2, dia2, lo2, la2 in named:
            dd = np.sqrt(((lo - lo2) * DEG * np.cos(np.radians(la)) / 1000.0) ** 2 +
                         ((la - la2) * DEG / 1000.0) ** 2)
            if dd <= max(0.5 * dia2, 2.0):
                iau = nm2
                break
        ti = idx_by.get(int(gv))
        ic.insertRow((shp, None, "inferred",
                      "closed depression in HRSC/MOLA DEM (fill depth >%.0f m)" % MIN_DEPTH_M,
                      round(d, 3), round(mx, 1), round(mn, 1), round(asp, 3), round(fr, 3),
                      None if ti is None else round(ti, 4), round(lo, 4), round(la, 4),
                      iau, None,
                      "depth/diameter = %.4f" % (mx / (d * 1000.0)),
                      "auto-candidate (fill-depth detection)", today))
        written += 1
step("wrote %d candidates to %s" % (written, TARGET))

# ------------------------------------------------------------------- summary
print("\n" + "=" * 76)
print("WHAT CAME OUT")
print("=" * 76)
dk = diam_km[keep]
print("  %d candidates   diameter: min %.2f  median %.2f  max %.1f km"
      % (len(dk), dk.min(), np.median(dk), dk.max()))
for lo_, hi_ in [(1, 2), (2, 5), (5, 10), (10, 20), (20, 50), (50, 1000)]:
    m = (dk >= lo_) & (dk < hi_)
    if m.sum():
        print("     %5.0f - %-6.0f km  %5d" % (lo_, hi_, int(m.sum())))
print("\n  %d candidates >= 1 km in the %d x %d deg %s window, against %d named craters."
      % (len(dk), A["lon"][1] - A["lon"][0], A["lat"][1] - A["lat"][0], A["name"], len(named)))
print("done in %.1f s" % (time.time() - t0))
