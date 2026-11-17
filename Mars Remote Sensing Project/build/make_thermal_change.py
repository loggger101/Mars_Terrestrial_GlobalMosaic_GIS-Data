# -*- coding: utf-8 -*-
r"""T1 mapped: where the thermal bands change the four-class map (KB §56, §69.148).

T1 (§40.1, §56) scored the published four-class SVM with and without the two THEMIS bands on held-out polygons only:
+1.36 points of accuracy with them, gained on Crater and hills and lost on lava tube. This asks where, over all of
±60°, the two classifications differ. The same training polygons and settings, the same 200 m grid; the only
difference is the two thermal bands.

  with      Global60\global60_landforms_svm_200m.tif            all seven bands (raw, no majority filter)
  without   Global60\global60_landforms_svm_nothermal_200m.tif  Viking R, G, B, slope, relief

Read in strips of 512 rows with GDAL; every pixel valid in both maps counts, weighted by cos(latitude) (the grid is
equidistant cylindrical, so a pixel's area falls with latitude). Pixels within 1° of longitude 180° are left out: the
with-thermal map had that column reclassified after the 2026-10-14 patch (§54.3) and the without map may not hold the
same correction there.

Writes logs\thermal_change.json (the share of ±60° that changes; the 4 x 4 table of classes with and without, as area
shares; per class the area each map gives it; the share changed by 10° latitude band and by class with thermal), and
Global60\global60_thermal_change_0p5deg.tif (per 0.5° cell, the share of its valid area whose class changes; geographic,
-180..180°E, nodata -1), and with --window lon0 lat0 lon1 lat1 the full-resolution change code of that box,
Global60\global60_thermal_change_window.tif, the change grouped for the layout's close-up (GROUPS: 0 the same
class, 1 Crater with thermal and Normal Ground without, 2 the reverse, 3 Crater to lava tube, 4 lava tube to Crater,
5 between lava tube and Normal Ground, 6 any change to or from hills; 255 nodata), and the window's own table.

Predictions, written before the first run (2026-11-17, from §56's polygon scores only):
  P1  The two maps differ on less than 15 % of ±60°: the thermal bands move accuracy by 1.4 points.
  P2  The largest single change is between Crater and Normal Ground (either direction): those two classes hold most
      of the map and Crater is where §56 found the gain.
  P3  Without the thermal bands lava tube covers more of ±60° than with them: its producer's accuracy rose from 37.6 to
      46.1 % when they were removed (§56), which a larger class would explain.
Each is reported as held or not held; none is adjusted after the run.

  "<ArcGIS Pro Python>" make_thermal_change.py [--window lon0 lat0 lon1 lat1]   (layout 21: --window 25 -55 115 -25)      read-only on the two maps
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from osgeo import gdal

gdal.UseExceptions()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive

G60 = on_drive(r"Mars Project\Global60")
WITH = os.path.join(G60, "global60_landforms_svm_200m.tif")
WITHOUT = os.path.join(G60, "global60_landforms_svm_nothermal_200m.tif")
GRID = os.path.join(G60, "global60_thermal_change_0p5deg.tif")
WIN = os.path.join(G60, "global60_thermal_change_window.tif")
LOG = os.path.join(HERE, "logs", "thermal_change.json")
NAMES = {1: "Crater", 2: "steep/windy hills", 3: "lava tube", 4: "Normal Ground"}
R = 3396190.0
STRIP = 512
CELL = 0.5
GROUPS = np.full(256, 255, np.uint8)               # 10 * with + without -> the close-up's change group
GROUPS[0] = 0
for _c, _g in {14: 1, 41: 2, 13: 3, 31: 4, 34: 5, 43: 5, 12: 6, 21: 6, 23: 6, 32: 6, 24: 6, 42: 6}.items():
    GROUPS[_c] = _g
GROUP_NAMES = {1: "Crater with, Normal Ground without", 2: "Normal Ground with, Crater without",
               3: "Crater with, lava tube without", 4: "lava tube with, Crater without",
               5: "between lava tube and Normal Ground", 6: "to or from steep/windy hills"}


def lonlat(gt, rows, cols):
    """East longitude in [-180, 180) and latitude of pixel centres; x = 0 is longitude 180° (CM 180)."""
    x = gt[0] + (cols + 0.5) * gt[1]
    y = gt[3] + (rows + 0.5) * gt[5]
    lon = (np.degrees(x / R) + 180.0 + 180.0) % 360.0 - 180.0
    return lon, np.degrees(y / R)


def main():
    t0 = time.time()
    a, b = gdal.Open(WITH), gdal.Open(WITHOUT)
    assert (a.RasterXSize, a.RasterYSize, a.GetGeoTransform()) == (b.RasterXSize, b.RasterYSize, b.GetGeoTransform())
    W, H, gt = a.RasterXSize, a.RasterYSize, a.GetGeoTransform()
    ba, bb = a.GetRasterBand(1), b.GetRasterBand(1)
    cols = np.arange(W)
    lon, _ = lonlat(gt, np.zeros(1), cols)
    keep_col = np.abs(((lon + 360.0) % 360.0) - 180.0) >= 1.0          # off the 180° stripe
    ci = np.floor((lon + 180.0) / CELL).astype(np.int64)               # 0.5° column, 0..719
    NR, NC = int(round(120 / CELL)), int(round(360 / CELL))
    cell_all, cell_chg = np.zeros(NR * NC), np.zeros(NR * NC)
    tab = np.zeros((5, 5))                                               # [with][without], codes 1..4
    band_all, band_chg = np.zeros(12), np.zeros(12)
    win = None
    if "--window" in sys.argv:
        k = sys.argv.index("--window")
        win = [float(v) for v in sys.argv[k + 1:k + 5]]                  # lon0 lat0 lon1 lat1, east longitude
        inbox_col = (lon >= win[0]) & (lon < win[2])
        wc = np.where(inbox_col)[0]
        assert wc.size and np.all(np.diff(wc) == 1), "the window must not cross 180°"
        wrows, wtab = [], np.zeros((5, 5))
    for r0 in range(0, H, STRIP):
        n = min(STRIP, H - r0)
        A = ba.ReadAsArray(0, r0, W, n)
        B = bb.ReadAsArray(0, r0, W, n)
        _, lat = lonlat(gt, np.arange(r0, r0 + n), np.zeros(1))
        ok = (A >= 1) & (A <= 4) & (B >= 1) & (B <= 4) & keep_col[None, :]
        w = np.cos(np.radians(lat))[:, None] * ok
        chg = ok & (A != B)
        np.add.at(tab, (A[ok], B[ok]), np.broadcast_to(w, A.shape)[ok])
        ri = np.clip(np.floor((60.0 - lat) / CELL).astype(np.int64), 0, NR - 1)
        idx = (ri[:, None] * NC + ci[None, :])
        cell_all += np.bincount(idx[ok], weights=w[ok], minlength=NR * NC)
        cell_chg += np.bincount(idx[chg], weights=w[chg], minlength=NR * NC)
        bi = np.clip(np.floor((60.0 - lat) / 10.0).astype(int), 0, 11)
        band_all += np.bincount(np.repeat(bi, W)[ok.ravel()], weights=w[ok], minlength=12)
        band_chg += np.bincount(np.repeat(bi, W)[chg.ravel()], weights=w[chg], minlength=12)
        if win is not None:
            rr = (lat <= win[3]) & (lat > win[1])
            if rr.any():
                code = np.where(ok, np.where(A != B, 10 * A + B, 0), 255).astype(np.uint8)
                code = GROUPS[code]
                np.add.at(wtab, (A[rr][:, wc][ok[rr][:, wc]], B[rr][:, wc][ok[rr][:, wc]]),
                          np.broadcast_to(w[rr][:, wc], (int(rr.sum()), wc.size))[ok[rr][:, wc]])
                wrows.append(code[rr][:, wc])
        if r0 // STRIP % 10 == 0:
            print("  row %d of %d  (%.0f s)" % (r0, H, time.time() - t0), flush=True)
    tot = tab.sum()
    share = 1.0 - np.trace(tab) / tot
    t = tab[1:, 1:] / tot
    res = {"with": os.path.basename(WITH), "without": os.path.basename(WITHOUT), "weight": "cos(latitude)",
           "excluded": "pixels within 1 degree of longitude 180", "share_changed": round(float(share), 5),
           "table_with_rows_without_cols": {NAMES[i + 1]: {NAMES[j + 1]: round(float(t[i, j]), 5) for j in range(4)}
                                            for i in range(4)},
           "class_area_with": {NAMES[i + 1]: round(float(t[i].sum()), 5) for i in range(4)},
           "class_area_without": {NAMES[j + 1]: round(float(t[:, j].sum()), 5) for j in range(4)},
           "changed_by_class_with": {NAMES[i + 1]: round(float(1 - t[i, i] / t[i].sum()), 5) for i in range(4)},
           "changed_by_lat_band": {"%+d..%+d" % (60 - 10 * k - 10, 60 - 10 * k): round(float(band_chg[k] / band_all[k]), 5)
                                   for k in range(12) if band_all[k] > 0}}
    off = [(t[i, j], NAMES[i + 1], NAMES[j + 1]) for i in range(4) for j in range(4) if i != j]
    big = max(off)
    res["largest_change"] = {"with": big[1], "without": big[2], "share": round(float(big[0]), 5)}
    res["predictions"] = {
        "P1 share changed < 15 %": "held" if share < 0.15 else "not held",
        "P2 largest change Crater <-> Normal Ground": "held" if {big[1], big[2]} == {"Crater", "Normal Ground"} else "not held",
        "P3 lava tube larger without thermal": "held" if t[:, 2].sum() > t[2].sum() else "not held"}
    # the 0.5° grid, geographic, -180..180°E, 60..-60°
    g = np.where(cell_all > 0, cell_chg / np.maximum(cell_all, 1e-12), -1.0).reshape(NR, NC).astype(np.float32)
    res["cells_half_degree"] = {"n": int((g >= 0).sum()), "median_share_changed": round(float(np.median(g[g >= 0])), 5),
                                "p90": round(float(np.percentile(g[g >= 0], 90)), 5),
                                "over_25pct": round(float((g >= 0.25).sum() / (g >= 0).sum()), 5)}
    drv = gdal.GetDriverByName("GTiff")
    o = drv.Create(GRID, NC, NR, 1, gdal.GDT_Float32, ["COMPRESS=DEFLATE"])
    o.SetGeoTransform((-180.0, CELL, 0.0, 60.0, 0.0, -CELL))
    srs = gdal.osr.SpatialReference(); srs.ImportFromWkt(a.GetProjection())
    o.SetProjection(srs.CloneGeogCS().ExportToWkt())
    o.GetRasterBand(1).WriteArray(g); o.GetRasterBand(1).SetNoDataValue(-1.0); o = None
    if win is not None:
        arr = np.vstack(wrows)
        x0 = gt[0] + wc[0] * gt[1]
        rows_in = [r for r in range(H) if win[1] < np.degrees((gt[3] + (r + 0.5) * gt[5]) / R) <= win[3]]
        y0 = gt[3] + rows_in[0] * gt[5]
        o = drv.Create(WIN, arr.shape[1], arr.shape[0], 1, gdal.GDT_Byte, ["COMPRESS=DEFLATE", "TILED=YES"])
        o.SetGeoTransform((x0, gt[1], 0.0, y0, 0.0, gt[5])); o.SetProjection(a.GetProjection())
        o.GetRasterBand(1).WriteArray(arr); o.GetRasterBand(1).SetNoDataValue(255); o = None
        sub = arr[arr != 255]
        wt = wtab[1:, 1:] / wtab.sum()
        res["window"] = {"lon0": win[0], "lat0": win[1], "lon1": win[2], "lat1": win[3],
                         "share_changed": round(float(1 - np.trace(wt)), 5),
                         "table_with_rows_without_cols": {NAMES[i + 1]: {NAMES[j + 1]: round(float(wt[i, j]), 5)
                                                                  for j in range(4)} for i in range(4)},
                         "groups": {GROUP_NAMES[k]: round(float((sub == k).mean()), 5) for k in GROUP_NAMES}}
    json.dump(res, open(LOG, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))
    print("wrote %s, %s  (%.0f s)" % (LOG, GRID, time.time() - t0))


if __name__ == "__main__":
    main()
