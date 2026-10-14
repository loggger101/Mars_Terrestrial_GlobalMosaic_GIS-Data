# -*- coding: utf-8 -*-
r"""KB §11 q24: do the 29 Sep map's 4096-px blocks come from ClassifyRaster's processing tiles?

Read-only on the drive; scratch on C:\MarsScratch\q24 (internal disk). ArcGIS Python.

The 29 Sep map (Classified_202609292109007048151, SVM over Segmented_202609290011302066080 + Night IR,
KB §29.1, §30.2) has class edges on a 4096-px grid counted from the night grid's origin, while both of
its inputs are seamless. Test: reclassify a window with the SAME classifier definition
(ClassDefinitions_202609290010404137400.ecd), the window offset by half a tile (2048 px) in both
directions from the original tile grid, so the rerun's own processing tiles (counted from the window's
origin) fall 2048 px away from the original seams.

Metric, per boundary: the class-change rate between adjacent columns (rows) at that boundary, divided
by the median change rate across all other columns (rows) of the window ("jump ratio", as §30.2).

Prediction (written before the run): the seams are made by the processing tiles. Then
  - the ORIGINAL map's jump ratio at the original tile line (window offset 2048) is high (>= 1.5), and
  - the RERUN's jump ratio there is ~1 (< 1.3), while the rerun shows a jump (>= 1.5) at ITS own tile
    line (window offset 4096), if it tiles at 4096 too.
Verdict rule: "tiles" if both the first two hold; "not tiles" if the rerun also jumps (>= 1.5) at the
original line; otherwise "inconclusive". Reproduction check first: away from every tile line (> 64 px),
the rerun must agree with the original on >= 90 % of pixels, or the rerun does not reproduce the map
and the test says nothing.

    test_q24_tiles.py [--col-tile 40] [--row-tile 8]      the original tile corner to centre on
    test_q24_tiles.py --aligned                            the control below

Run 1 (2026-10-13, offset window): columns as predicted (original 43.0x at its line, rerun 1.17x there and
22.2x at its own), rows flat in both, but agreement away from the lines 0.876 < 0.90, so by the rule above:
no verdict. The 0.90 rule was mis-specified: if whole tiles change class with the processing extent, the
offset rerun must disagree inside tiles too. The rule is not changed; a control is added instead.

CONTROL, --aligned (prediction and rule written before it ran): the same window size, but its origin ON the
original tile grid (one tile up and left of the chosen corner), so the rerun's processing tiles coincide
with the original's. Prediction: if the processing tiles explain the map, the aligned rerun reproduces it,
agreement >= 0.98 over all valid pixels, and both jump at the shared line (window index 4096). Verdict:
"reproduces with aligned tiles" if agreement >= 0.98; "does not reproduce" if < 0.90 (then something
other than tiling, e.g. a different input, also differs); otherwise "partial".
"""
import os, sys, json, time, argparse
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, MARS_PROJECT, GDB
import numpy as np
import arcpy

ap = argparse.ArgumentParser()
ap.add_argument("--col-tile", type=int, default=40)
ap.add_argument("--row-tile", type=int, default=8)
ap.add_argument("--aligned", action="store_true")
a = ap.parse_args()

T, HALF, W = 4096, 2048, 8192
SEG = os.path.join(GDB, "Segmented_202609290011302066080")
ORIG = os.path.join(GDB, "Classified_202609292109007048151")
NIGHT = on_drive("Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif")
ECD = os.path.join(MARS_PROJECT, "ClassDefinitions_202609290010404137400.ecd")
SCR = r"C:\MarsScratch\q24" + ("_aligned" if "--aligned" in sys.argv else "")
LOG = os.path.join(HERE, "logs", "q24_tiles_aligned.json" if a.aligned else "q24_tiles.json")
OFF = T if a.aligned else HALF          # window origin = tile corner minus OFF
os.makedirs(SCR, exist_ok=True)

d = arcpy.Describe(SEG)
rs = arcpy.Raster(SEG)
ext, cs = rs.extent, rs.meanCellWidth
c0, r0 = a.col_tile * T - OFF, a.row_tile * T - OFF          # window origin, in night-grid pixels
xmin, ymax = ext.XMin + c0 * cs, ext.YMax - r0 * cs
xmax, ymin = xmin + W * cs, ymax - W * cs
win = arcpy.Extent(xmin, ymin, xmax, ymax)
print("window cols %d-%d rows %d-%d, cell %.3f m" % (c0, c0 + W, r0, r0 + W, cs), flush=True)

arcpy.env.overwriteOutput = True
arcpy.env.extent = win
arcpy.env.snapRaster = SEG
arcpy.env.outputCoordinateSystem = d.spatialReference
arcpy.env.workspace = SCR
arcpy.env.scratchWorkspace = SCR
arcpy.CheckOutExtension("Spatial")

t = time.time()
seg_w, night_w = os.path.join(SCR, "seg_w.tif"), os.path.join(SCR, "night_w.tif")
arcpy.management.CopyRaster(SEG, seg_w)
arcpy.management.CopyRaster(NIGHT, night_w)
print("copied windows %.0f s" % (time.time() - t), flush=True)

t = time.time()
out = arcpy.sa.ClassifyRaster(seg_w, ECD, night_w)
rerun_p = os.path.join(SCR, "rerun.tif")
out.save(rerun_p)
t_cls = time.time() - t
print("ClassifyRaster %.0f s" % t_cls, flush=True)

ll = arcpy.Point(xmin, ymin)
orig = arcpy.RasterToNumPyArray(ORIG, ll, W, W).astype(np.int16)
rerun = arcpy.RasterToNumPyArray(rerun_p, ll, W, W).astype(np.int16)
nd_o = arcpy.Describe(ORIG).noDataValue
print("orig values", np.unique(orig)[:10], "rerun values", np.unique(rerun)[:10], flush=True)

# the 29 Sep map was recoded 0-3 -> 1-4 (KB §36); align the rerun's coding to the original's
best = max(range(-1, 2), key=lambda k: np.mean((rerun + k) == orig))
rerun = rerun + best
valid = (orig >= 1) & (orig <= 4) & (rerun >= 1) & (rerun <= 4)


def jump(arr, axis):
    """change rate across each boundary between adjacent columns (axis=1) or rows (axis=0)"""
    ch = (np.diff(arr, axis=axis) != 0)
    v = np.logical_and(np.take(valid, range(arr.shape[axis] - 1), axis=axis),
                       np.take(valid, range(1, arr.shape[axis]), axis=axis))
    num = (ch & v).sum(axis=1 - axis); den = v.sum(axis=1 - axis)
    return np.where(den > 0, num / np.maximum(den, 1), np.nan)


res = {"window": {"col0": c0, "row0": r0, "size": W, "col_tile": a.col_tile, "row_tile": a.row_tile},
       "classify_seconds": round(t_cls), "rerun_offset_applied": best}
far = np.ones((W, W), bool)
for k in (HALF, T):
    far[:, max(0, k - 64):k + 64] = False; far[max(0, k - 64):k + 64, :] = False
res["agreement_away_from_tile_lines"] = float(np.mean(orig[far & valid] == rerun[far & valid]))
for name, arr in (("original", orig), ("rerun", rerun)):
    for axis, lab in ((1, "cols"), (0, "rows")):
        j = jump(arr, axis)
        base = np.nanmedian(j)
        # boundary between index k-1 and k sits at diff index k-1
        res["%s_%s" % (name, lab)] = {"median_rate": float(base),
                                      "at_original_line_2048": float(j[HALF - 1] / base),
                                      "at_rerun_line_4096": float(j[T - 1] / base)}
if a.aligned:
    agree = float(np.mean(orig[valid] == rerun[valid]))
    res["agreement_all"] = agree
    res["verdict"] = ("reproduces with aligned tiles" if agree >= 0.98 else
                      "does not reproduce" if agree < 0.90 else "partial")
    res["when"] = time.strftime("%Y-%m-%d %H:%M")
    json.dump(res, open(LOG, "w"), indent=1)
    print(json.dumps(res, indent=1))
    sys.exit(0)
o, r = res["original_cols"], res["rerun_cols"]
o2, r2 = res["original_rows"], res["rerun_rows"]
reproduces = res["agreement_away_from_tile_lines"] >= 0.90
orig_jumps = o["at_original_line_2048"] >= 1.5 and o2["at_original_line_2048"] >= 1.5
rerun_flat = r["at_original_line_2048"] < 1.3 and r2["at_original_line_2048"] < 1.3
rerun_jumps_orig = r["at_original_line_2048"] >= 1.5 or r2["at_original_line_2048"] >= 1.5
if not reproduces:
    v = "no verdict: the rerun does not reproduce the map"
elif orig_jumps and rerun_flat:
    v = "tiles: the seams move with the processing extent"
elif rerun_jumps_orig:
    v = "not tiles: the rerun keeps the original seams"
else:
    v = "inconclusive"
res["verdict"] = v
res["when"] = time.strftime("%Y-%m-%d %H:%M")
json.dump(res, open(LOG, "w"), indent=1)
print(json.dumps(res, indent=1))
