# -*- coding: utf-8 -*-
r"""Test T3, local half: inside each type area, does the diurnal-contrast index track calibrated
thermal inertia? (KB §42, NEXT-STEPS §4)

§24.3 says the index is a material discriminator within one area, and §28.10 that it fails across
the planet. TES thermal inertia (Putzig & Mellon 2007, §41) is calibrated, so it can test the first
claim directly. Prediction, written before the run: r(index, log TI) clearly negative in both
windows (large day-night swing = dust = low inertia).

Each 100 m pixel of the area's rasters is assigned to its TES 0.05° cell (~3 km) and averaged
there; only cells the area fills completely and TES MEASURED (the _measured mask) are used. Read-only;
writes build\logs\tes_local_check.json.
"""
import os, sys, json
import numpy as np
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive
import areas

gdal.UseExceptions()
TES = on_drive(r"Mars Project\Reference\TES_thermal_inertia_2007")
R = 3396190.0
STEP = 0.05
LAYERS = [("thermal_contrast.tif", "diurnal-contrast index", -9999.0), ("viking.tif", "Viking red", 0),
          ("day.tif", "THEMIS day DN", 0), ("night.tif", "THEMIS night DN", 0)]
OUT = os.path.join(HERE, "logs", "tes_local_check.json")


def main():
    res = {}
    for side in ("dayside", "nightside"):
        ti_ds = gdal.Open(os.path.join(TES, "TES_TI_2007_%s.tif" % side))
        ti = ti_ds.ReadAsArray().astype(float)
        meas = gdal.Open(os.path.join(TES, "TES_TI_2007_%s_measured.tif" % side)).ReadAsArray() == 1
        for key in ("ius", "ath"):
            sys.argv = [sys.argv[0], "--area", key]
            a = areas.current()
            xmin, ymin, xmax, ymax = a["bounds"]
            W, H = a["W"], a["H"]
            xs = xmin + (np.arange(W) + .5) * 100.0
            ys = ymax - (np.arange(H) + .5) * 100.0
            lon = (180.0 + np.degrees(xs / R) + 180.0) % 360.0 - 180.0
            lat = np.degrees(ys / R)
            col = ((lon + 180.0) / STEP).astype(int)
            row = ((90.0 - lat) / STEP).astype(int)
            c0, r0 = col.min(), row.min()
            nc, nr = col.max() - c0 + 1, row.max() - r0 + 1
            cell = (row[:, None] - r0) * nc + (col[None, :] - c0)          # H x W cell index
            full = np.bincount(cell.ravel(), minlength=nr * nc)
            means = {}
            for fn, label, nod in LAYERS:
                ds = gdal.Open(os.path.join(a["out"], areas.name(a, fn)))    # keep a reference: a chained
                arr = ds.GetRasterBand(1).ReadAsArray().astype(float)       # Open().GetRasterBand() frees it
                ds = None
                v = arr != nod
                s = np.bincount(cell.ravel(), weights=np.where(v, arr, 0).ravel(), minlength=nr * nc)
                n = np.bincount(cell.ravel(), weights=v.ravel().astype(float), minlength=nr * nc)
                means[label] = np.where(n >= 0.95 * full.max(), s / np.maximum(n, 1), np.nan)
            tsub = ti[r0:r0 + nr, c0:c0 + nc].ravel()
            msub = meas[r0:r0 + nr, c0:c0 + nc].ravel()
            ok = msub & (tsub > 0) & (full >= 0.95 * full.max())
            out = {"cells": int(ok.sum()), "median_TI": float(np.median(tsub[ok])),
                   "p10_p90_TI": [float(np.percentile(tsub[ok], 10)), float(np.percentile(tsub[ok], 90))], "r_log_TI": {}}
            for label, m in means.items():
                good = ok & np.isfinite(m)
                out["r_log_TI"][label] = float(np.corrcoef(m[good], np.log(tsub[good]))[0, 1])
            res.setdefault(side, {})[key] = out
            print("%-9s %-17s %5d cells  TI median %4.0f (p10 %3.0f, p90 %4.0f)   r(log TI): %s" % (
                side, a["name"], out["cells"], out["median_TI"], out["p10_p90_TI"][0], out["p10_p90_TI"][1],
                ", ".join("%s %+.2f" % kv for kv in out["r_log_TI"].items())))
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
