# -*- coding: utf-8 -*-
r"""T1's three band sets mapped: how much of the four-class map each set of bands decides (KB §56.1, §69.149).

§56.1 classified ±60° at 400 m with the full stack's model and with three reduced band sets, each trained on the same
polygons, and scored them on held-out polygons only. This asks, for each set, how much of ±60° changes class against
the all-band map, and where:
  all        Global60\global60_landforms_svm_400m.tif             Viking R, G, B, night, day, slope, relief
  nothermal  Global60\global60_landforms_svm_nothermal_400m.tif   without the two THEMIS bands
  novisible  Global60\global60_landforms_svm_novisible_400m.tif   without the three Viking bands
  terrain    Global60\global60_landforms_svm_terrain_400m.tif     slope and relief alone
Pixels valid in both maps, cos(latitude) weighted, 1° either side of 180° left out (the all-band 400 m map predates the
§54 patch). Writes logs\bandset_change.json (per set: the share changed, the 4 x 4 table against the all-band map, the
class areas, by 10° band) and Global60\global60_bandset_change_<set>_0p5deg.tif (per 0.5° cell, the share changed;
geographic, nodata -1).

Predictions, written before the first run (2026-11-17, from §56.1's polygon scores and make_thermal_change.py's 200 m
result, 14.9 %, only):
  P1  Without the visible bands more of the map changes than without the thermal bands: three bands go, not two, and
      held-out accuracy moves 4.3 points against 2.0.
  P2  Terrain alone changes the most of the three: five of the seven bands go.
  P3  Without the thermal bands the 400 m map changes within 2 points of the 200 m result (12.9 to 16.9 %).
Each is reported as held or not held; none is adjusted after the run.

  "<ArcGIS Pro Python>" make_bandset_change.py      read-only on the four maps
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from osgeo import gdal

gdal.UseExceptions()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive
from make_thermal_change import lonlat, NAMES, CELL

G60 = on_drive(r"Mars Project\Global60")
ALL = os.path.join(G60, "global60_landforms_svm_400m.tif")
SETS = {"nothermal": "global60_landforms_svm_nothermal_400m.tif",
        "novisible": "global60_landforms_svm_novisible_400m.tif",
        "terrain": "global60_landforms_svm_terrain_400m.tif"}
LOG = os.path.join(HERE, "logs", "bandset_change.json")
STRIP = 512


def compare(a, b, out_grid):
    assert (a.RasterXSize, a.RasterYSize, a.GetGeoTransform()) == (b.RasterXSize, b.RasterYSize, b.GetGeoTransform())
    W, H, gt = a.RasterXSize, a.RasterYSize, a.GetGeoTransform()
    ba, bb = a.GetRasterBand(1), b.GetRasterBand(1)
    lon, _ = lonlat(gt, np.zeros(1), np.arange(W))
    keep_col = np.abs(((lon + 360.0) % 360.0) - 180.0) >= 1.0
    ci = np.floor((lon + 180.0) / CELL).astype(np.int64)
    NR, NC = int(round(120 / CELL)), int(round(360 / CELL))
    cell_all, cell_chg = np.zeros(NR * NC), np.zeros(NR * NC)
    tab = np.zeros((5, 5))
    band_all, band_chg = np.zeros(12), np.zeros(12)
    for r0 in range(0, H, STRIP):
        n = min(STRIP, H - r0)
        A, B = ba.ReadAsArray(0, r0, W, n), bb.ReadAsArray(0, r0, W, n)
        _, lat = lonlat(gt, np.arange(r0, r0 + n), np.zeros(1))
        ok = (A >= 1) & (A <= 4) & (B >= 1) & (B <= 4) & keep_col[None, :]
        w = np.cos(np.radians(lat))[:, None] * ok
        chg = ok & (A != B)
        np.add.at(tab, (A[ok], B[ok]), np.broadcast_to(w, A.shape)[ok])
        ri = np.clip(np.floor((60.0 - lat) / CELL).astype(np.int64), 0, NR - 1)
        idx = ri[:, None] * NC + ci[None, :]
        cell_all += np.bincount(idx[ok], weights=w[ok], minlength=NR * NC)
        cell_chg += np.bincount(idx[chg], weights=w[chg], minlength=NR * NC)
        bi = np.repeat(np.clip(np.floor((60.0 - lat) / 10.0).astype(int), 0, 11), W)
        band_all += np.bincount(bi[ok.ravel()], weights=w[ok], minlength=12)
        band_chg += np.bincount(bi[chg.ravel()], weights=w[chg], minlength=12)
    t = tab[1:, 1:] / tab.sum()
    g = np.where(cell_all > 0, cell_chg / np.maximum(cell_all, 1e-12), -1.0).reshape(NR, NC).astype(np.float32)
    o = gdal.GetDriverByName("GTiff").Create(out_grid, NC, NR, 1, gdal.GDT_Float32, ["COMPRESS=DEFLATE"])
    o.SetGeoTransform((-180.0, CELL, 0.0, 60.0, 0.0, -CELL))
    srs = gdal.osr.SpatialReference(); srs.ImportFromWkt(a.GetProjection())
    o.SetProjection(srs.CloneGeogCS().ExportToWkt())
    o.GetRasterBand(1).WriteArray(g); o.GetRasterBand(1).SetNoDataValue(-1.0); o = None
    return {"share_changed": round(float(1 - np.trace(t)), 5),
            "table_all_rows_set_cols": {NAMES[i + 1]: {NAMES[j + 1]: round(float(t[i, j]), 5) for j in range(4)}
                                        for i in range(4)},
            "class_area_all": {NAMES[i + 1]: round(float(t[i].sum()), 5) for i in range(4)},
            "class_area_set": {NAMES[j + 1]: round(float(t[:, j].sum()), 5) for j in range(4)},
            "changed_by_class_all": {NAMES[i + 1]: round(float(1 - t[i, i] / t[i].sum()), 5) for i in range(4)},
            "changed_by_lat_band": {"%+d..%+d" % (60 - 10 * k - 10, 60 - 10 * k): round(float(band_chg[k] / band_all[k]), 5)
                                    for k in range(12) if band_all[k] > 0},
            "cells_over_25pct": round(float((g >= 0.25).sum() / (g >= 0).sum()), 5),
            "grid": os.path.basename(out_grid)}


def main():
    t0 = time.time()
    a = gdal.Open(ALL)
    res = {"all": os.path.basename(ALL), "weight": "cos(latitude)", "excluded": "pixels within 1 degree of longitude 180",
           "sets": {}}
    for k, f in SETS.items():
        res["sets"][k] = dict(map=f, **compare(a, gdal.Open(os.path.join(G60, f)),
                                               os.path.join(G60, "global60_bandset_change_%s_0p5deg.tif" % k)))
        print("  %-10s %.4f changed  (%.0f s)" % (k, res["sets"][k]["share_changed"], time.time() - t0), flush=True)
    s = {k: v["share_changed"] for k, v in res["sets"].items()}
    res["predictions"] = {
        "P1 without visible changes more than without thermal": "held" if s["novisible"] > s["nothermal"] else "not held",
        "P2 terrain only changes the most": "held" if s["terrain"] == max(s.values()) else "not held",
        "P3 without thermal at 400 m within 2 points of 14.9 %": "held" if abs(s["nothermal"] - 0.14934) <= 0.02 else "not held"}
    json.dump(res, open(LOG, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v["share_changed"] for k, v in res["sets"].items()}), json.dumps(res["predictions"], indent=1))
    print("wrote %s  (%.0f s)" % (LOG, time.time() - t0))


if __name__ == "__main__":
    main()
