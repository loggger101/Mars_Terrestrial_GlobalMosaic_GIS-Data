# -*- coding: utf-8 -*-
r"""Candidate channel centrelines for the Ius Chasma type area.

Task 11 (digitising) is the critical path and it needs manual judgement - but it
should not start from a blank canvas. This derives CANDIDATE centrelines from
the DEM by flow routing and attributes each one with the diurnal-contrast index
(KB 24), so every candidate arrives pre-triaged on the one axis that bears on
the Athabasca question: is this thing rock-floored or dust-mantled?

These are candidates, not mapping. They are written to a SEPARATE feature class
- Landform_ChannelCandidates_auto - so Landform_ChannelCenterlines stays a clean
surface for manual digitising. Confidence is 'inferred' on every row.

Run with the ArcGIS interpreter. Scratch work happens under Z:\TypeArea because
legacy Spatial Analyst tools reject the space in "Mars Project".
"""
import os, time, arcpy
from arcpy.sa import *

WS = r"Z:\TypeArea"                       # junction - no spaces
GDB = r"Z:\Mars Project\Mars Project.gdb"  # the real project gdb
SCRATCH = os.path.join(WS, "chan_scratch.gdb")
DEM = os.path.join(WS, "ius_dem.tif")
IDX = os.path.join(WS, "ius_thermal_contrast.tif")
SLP = os.path.join(WS, "ius_slope_deg.tif")
TARGET = "Landform_ChannelCandidates_auto"

# a stream is a cell with at least this many upslope cells. 100 m cells, so
# 5000 = 50 km^2 of catchment - deliberately high, to return the trunk network
# rather than every plateau rill.
THRESH = 5000

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = WS
t0 = time.time()


def step(msg):
    print("  [%6.1fs] %s" % (time.time() - t0, msg), flush=True)


print("=" * 74)
print("CANDIDATE CHANNEL CENTRELINES - Ius Chasma")
print("=" * 74)

if arcpy.Exists(SCRATCH):
    arcpy.management.Delete(SCRATCH)
arcpy.management.CreateFileGDB(os.path.dirname(SCRATCH), os.path.basename(SCRATCH))
step("scratch gdb")

def cached(name, fn, label):
    """The routing rasters cost ~4.5 min and are deterministic - reuse them."""
    path = os.path.join(WS, name)
    if arcpy.Exists(path):
        step("%s  (reused)" % label)
        return path
    fn().save(path)
    step(label)
    return path


fill = cached("ius_fill.tif", lambda: Fill(DEM), "Fill")
fdr = cached("ius_fdr.tif", lambda: FlowDirection(fill, "NORMAL"), "FlowDirection")
fac = cached("ius_fac.tif", lambda: FlowAccumulation(fdr, None, "FLOAT"), "FlowAccumulation")
r = arcpy.Raster(fac)
step("   max upslope cells = %s" % f"{int(r.maximum):,}")
del r

# Ius Chasma is a CLOSED BASIN. Fill floods it - measured: 23% of the scene
# raised, max 2077 m - and routing across that synthetic lake surface produced
# 56% of the first network as pure artefact. Keep only real topography.
depth = os.path.join(WS, "ius_filldepth.tif")
if not arcpy.Exists(depth):
    (Raster(fill) - Raster(DEM)).save(depth)
nofill = Raster(depth) <= 1.0

def cellcount(ras):
    """Cells equal to 1, read off the attribute table."""
    t = os.path.join(WS, "_cc.tif")
    if arcpy.Exists(t):
        arcpy.management.Delete(t)
    ras.save(t)
    n = sum(r[0] for r in arcpy.da.SearchCursor(t, ["COUNT"], "VALUE = 1"))
    arcpy.management.Delete(t)
    return int(n)


streams = os.path.join(WS, "ius_streams.tif")
n_all = cellcount(Con(Raster(fac) > THRESH, 1))
Con((Raster(fac) > THRESH) & (nofill == 1), 1).save(streams)
n_keep = cellcount(Raster(streams) == 1)
step("Con > %s cells (%.0f km2), off filled ground: %s of %s cells kept "
     "(%.1f%% discarded as fill artefact)"
     % (f"{THRESH:,}", THRESH * 0.01, f"{n_keep:,}", f"{n_all:,}",
        100.0 * (1 - n_keep / max(n_all, 1))))

link = os.path.join(WS, "ius_strlink.tif")
StreamLink(streams, fdr).save(link)
step("StreamLink")

order = os.path.join(WS, "ius_strord.tif")
StreamOrder(streams, fdr, "STRAHLER").save(order)
step("StreamOrder (Strahler)")

lines = os.path.join(SCRATCH, "cand_raw")
StreamToFeature(link, fdr, lines, "NO_SIMPLIFY")
n = int(arcpy.management.GetCount(lines)[0])
step("StreamToFeature  -> %d segments" % n)

# ---------------------------------------------------------------- attribute
# Strahler order, then the thermal index and slope along each segment.
step("attributing...")
zs_idx = os.path.join(SCRATCH, "zs_idx")
zs_slp = os.path.join(SCRATCH, "zs_slp")
zs_ord = os.path.join(SCRATCH, "zs_ord")
zs_fil = os.path.join(SCRATCH, "zs_fil")
arcpy.sa.ZonalStatisticsAsTable(lines, "arcid", IDX, zs_idx, "DATA", "MEAN_STD")
arcpy.sa.ZonalStatisticsAsTable(lines, "arcid", SLP, zs_slp, "DATA", "MEAN")
arcpy.sa.ZonalStatisticsAsTable(lines, "arcid", order, zs_ord, "DATA", "MAXIMUM")
arcpy.sa.ZonalStatisticsAsTable(lines, "arcid", depth, zs_fil, "DATA", "MEAN")
step("zonal statistics x4")

idx_by = {r[0]: (r[1], r[2]) for r in arcpy.da.SearchCursor(zs_idx, ["arcid", "MEAN", "STD"])}
slp_by = {r[0]: r[1] for r in arcpy.da.SearchCursor(zs_slp, ["arcid", "MEAN"])}
ord_by = {r[0]: r[1] for r in arcpy.da.SearchCursor(zs_ord, ["arcid", "MAX"])}
fil_by = {r[0]: r[1] for r in arcpy.da.SearchCursor(zs_fil, ["arcid", "MEAN"])}

# ------------------------------------------------- build the output in the gdb
if arcpy.Exists(os.path.join(GDB, TARGET)):
    arcpy.management.Delete(os.path.join(GDB, TARGET))
sr = arcpy.Describe(lines).spatialReference
arcpy.management.CreateFeatureclass(GDB, TARGET, "POLYLINE", spatial_reference=sr)
out = os.path.join(GDB, TARGET)
FIELDS = [("UnitName", "TEXT", 60), ("Origin", "TEXT", 20), ("Confidence", "TEXT", 12),
          ("Evidence", "TEXT", 90), ("StrahlerOrd", "SHORT", None),
          ("LengthKm", "DOUBLE", None), ("ThermIdx", "DOUBLE", None),
          ("ThermSd", "DOUBLE", None), ("SlopeDeg", "DOUBLE", None), ("FillDepthM", "DOUBLE", None),
          ("Notes", "TEXT", 200), ("MappedBy", "TEXT", 40), ("MappedOn", "DATE", None)]
for nm, ty, ln in FIELDS:
    if ln:
        arcpy.management.AddField(out, nm, ty, field_length=ln)
    else:
        arcpy.management.AddField(out, nm, ty)
step("schema on %s" % TARGET)

import datetime
today = datetime.datetime(2026, 9, 19)
cols = ["SHAPE@", "UnitName", "Origin", "Confidence", "Evidence", "StrahlerOrd",
        "LengthKm", "ThermIdx", "ThermSd", "SlopeDeg", "FillDepthM", "Notes",
        "MappedBy", "MappedOn"]
kept = 0
MINKM = 2.0          # below the project's ~1 km resolving limit x2, drop it
with arcpy.da.InsertCursor(out, cols) as ic:
    for shp, aid in arcpy.da.SearchCursor(lines, ["SHAPE@", "arcid"]):
        km = shp.length / 1000.0
        if km < MINKM:
            continue
        ti, ts = idx_by.get(aid, (None, None))
        note = ""
        if ti is not None:
            note = ("damped - rock-floored, consistent with lava" if ti < -0.15
                    else "swings hard - mantled floor, fines"    if ti > 0.15
                    else "intermediate - no thermal call")
        ic.insertRow((shp, None, "indeterminate", "inferred",
                      "DEM flow acc >%d cells, off filled ground; thermal idx KB24" % THRESH,
                      int(ord_by.get(aid, 0) or 0), round(km, 3),
                      None if ti is None else round(ti, 4),
                      None if ts is None else round(ts, 4),
                      round(slp_by.get(aid, 0.0) or 0.0, 3),
                      round(fil_by.get(aid, 0.0) or 0.0, 3), note, "auto-candidate (flow accumulation)", today))
        kept += 1
step("wrote %d candidates (>= %.0f km) of %d segments" % (kept, MINKM, n))

# ---------------------------------------------------------------------- report
print("\n" + "=" * 74)
print("WHAT CAME OUT")
print("=" * 74)
tot = 0.0
buckets = {"damped (rock / lava?)": 0, "intermediate": 0, "mantled (fines)": 0}
orders = {}
with arcpy.da.SearchCursor(out, ["LengthKm", "ThermIdx", "StrahlerOrd", "Notes"]) as c:
    for km, ti, so, note in c:
        tot += km
        orders[so] = orders.get(so, 0) + 1
        if ti is None:
            continue
        buckets["damped (rock / lava?)" if ti < -0.15 else
                "mantled (fines)" if ti > 0.15 else "intermediate"] += 1
print("  %d candidate centrelines, %.0f km total" % (kept, tot))
print("  by Strahler order: " + "  ".join("%s:%d" % (k, v) for k, v in sorted(orders.items())))
print("  thermal triage:")
for k, v in buckets.items():
    print("     %-24s %4d  (%4.1f%%)" % (k, v, 100.0 * v / max(kept, 1)))
print("""
  Every row is Confidence='inferred', Origin='indeterminate', MappedBy='auto-candidate'.
  Nothing was written to Landform_ChannelCenterlines - that stays manual.""")
arcpy.CheckInExtension("Spatial")
print("done in %.1f s" % (time.time() - t0))
