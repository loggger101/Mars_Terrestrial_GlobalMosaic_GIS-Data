# -*- coding: utf-8 -*-
r"""Test T7 (Q5): how many tributary orders does the 100 m stack resolve at Ius Chasma? (NEXT-STEPS §4; KB §47)

Q5, from the prospectus: how many tributary orders are recoverable at 100 m?

Prediction, written before the run (2026-10-08): the maximum Strahler order rises by about one for
every 4-5x fall in the threshold (Horton's law), so the order count is set by the threshold rather
than by the DEM; the share of first-order streams on slopes >= 2 deg falls as the threshold falls;
the finest threshold that keeps >= 50 % of first-order cells on slopes >= 2 deg is >= 1,000 cells
(10 km2), and it gives 4 orders.

Design (fixed before the sweep was run):
- The cached routing rasters of §25, unchanged: ius_fdr, ius_fac, ius_filldepth. A stream cell is
  fac > T and fill depth <= 1 m, exactly the candidate recipe (§25.1's fill-artefact mask) at other
  thresholds.
- T in 100 m cells: 100, 250, 500, 1,000, 2,000, 5,000 (the candidates, §25), 10,000, 20,000, 50,000.
- Per threshold: StreamOrder (Strahler) on that network; per order, stream cells, approximate
  length (cells x 100 m; a diagonal step is undercounted by up to 41 %) and the share of its cells
  on slopes >= 2 deg (ius_slope_deg).
- Q5's answer, by a rule fixed in advance: the maximum Strahler order at the finest threshold whose
  first-order streams keep >= 50 % of their cells on slopes >= 2 deg. Below 2 deg the routing follows
  DEM noise (§25.2: 64 % of the candidates lie there). If no threshold passes, Q5 has no answer the
  DEM supports at Ius, and that is the result.
- The DEM is the HRSC/MOLA 200 m blend resampled to 100 m (§3, §18.1): 1 km2 is 25 source cells.

Intermediate rasters go to %TEMP%\mars_t7 (internal disk, no spaces, §19.1). Read-only on the
project. Writes build\logs\t7_order_sweep.json.
"""
import os, sys, json, time, tempfile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
from arcpy.sa import Con, Raster, StreamOrder

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import junction
import areas

A = dict(areas.AREAS["ius"], key="ius")
WS = junction(A["folder"])
TMP = os.path.join(tempfile.gettempdir(), "mars_t7")
OUT = os.path.join(HERE, "logs", "t7_order_sweep.json")
THRESHOLDS = [100, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000]
STEEP_DEG, PASS_SHARE = 2.0, 0.5
t0 = time.time()


def log(msg):
    print("[%6.1fs] %s" % (time.time() - t0, msg), flush=True)


os.makedirs(TMP, exist_ok=True)
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = TMP
arcpy.env.scratchWorkspace = TMP
fdr, fac, depth, slope = (os.path.join(WS, "ius_%s.tif" % k) for k in ("fdr", "fac", "filldepth", "slope_deg"))
for p in (fdr, fac, depth, slope):
    assert arcpy.Exists(p), p
slp = arcpy.RasterToNumPyArray(slope).astype("float32")
nd = arcpy.Raster(slope).noDataValue
valid = np.isfinite(slp) if nd is None else (slp != np.float32(nd)) & np.isfinite(slp)
slp[~valid] = np.nan                       # the edge cells slope cannot be computed on; excluded from every share
steep = slp >= STEEP_DEG
log("slope read: %d x %d; %d no-data cells excluded; %.1f %% of the valid window on >= %.0f deg"
    % (slp.shape[1], slp.shape[0], int((~valid).sum()), 100 * steep[valid].mean(), STEEP_DEG))

res = {"test": "T7", "question": "Q5",
       "prediction": "max order +1 per 4-5x fall in threshold; finest passing threshold >= 1,000 cells, 4 orders",
       "rule": "max Strahler order at the finest threshold whose order-1 cells are >= 50 % on slopes >= 2 deg",
       "thresholds": {}}
for T in THRESHOLDS:
    t = time.time()
    streams = Con((Raster(fac) > T) & (Raster(depth) <= 1.0), 1)
    out = os.path.join(TMP, "ord_%d.tif" % T)
    StreamOrder(streams, fdr, "STRAHLER").save(out)
    o = arcpy.RasterToNumPyArray(out, nodata_to_value=0)
    assert o.shape == slp.shape
    orders = {}
    for k in range(1, int(o.max()) + 1):
        m = (o == k) & valid
        n = int(m.sum())
        if n == 0:
            continue
        orders[k] = {"cells": n, "km_approx": round(n * 0.1, 1),
                     "steep_share": round(float(steep[m].mean()), 3),
                     "mean_slope_deg": round(float(slp[m].mean()), 2)}
    r = {"km2": T * 0.01, "max_order": max(orders) if orders else 0, "orders": orders,
         "total_km_approx": round(sum(v["km_approx"] for v in orders.values()), 1),
         "order1_steep_share": orders.get(1, {}).get("steep_share"),
         "passes": bool(orders and orders[1]["steep_share"] >= PASS_SHARE),
         "seconds": round(time.time() - t, 1)}
    res["thresholds"][str(T)] = r
    log("T %6d cells (%6.1f km2): max order %d, %8.0f km; order-1 on >= 2 deg %.1f %%  %s  (%.0f s)" % (
        T, T * 0.01, r["max_order"], r["total_km_approx"], 100 * (r["order1_steep_share"] or 0),
        "PASS" if r["passes"] else "fail", r["seconds"]))
    arcpy.management.Delete(out)

passing = [int(T) for T, r in res["thresholds"].items() if r["passes"]]
if passing:
    finest = min(passing)
    res["answer"] = {"finest_passing_threshold_cells": finest,
                     "orders_resolved": res["thresholds"][str(finest)]["max_order"]}
else:
    res["answer"] = {"finest_passing_threshold_cells": None, "orders_resolved": None}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fo:
    json.dump(res, fo, indent=1, ensure_ascii=False)

print("\nper threshold, steep share by order (order: share of cells on >= 2 deg):")
for T, r in res["thresholds"].items():
    print("  %6s cells: %s" % (T, "  ".join("%d: %.0f%%" % (k, 100 * v["steep_share"]) for k, v in r["orders"].items())))
print("\nQ5 answer by the rule fixed in advance:", res["answer"])
log("wrote %s" % OUT)
