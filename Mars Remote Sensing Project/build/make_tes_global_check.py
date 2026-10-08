# -*- coding: utf-8 -*-
r"""Test T3, planet-wide half: which ±60° layer tracks calibrated thermal inertia? (KB §43, NEXT-STEPS §4)

The calibrated version of §28.10's province test. Each layer is read at the stack's coarse
overview, averaged into TES's 0.05° cells (~3 km), and correlated with log TES thermal inertia
(Putzig & Mellon 2007, §41) on MEASURED TES cells only:

  * globally, over all of ±60°;
  * within 15° x 15° blocks, the median of the per-block r: if the THEMIS mosaics are stretched
    region by region (§28.10), their signal could survive inside a block while vanishing globally.

Prediction, written before the run: Viking red clearly negative globally (dust is bright and has
low inertia); THEMIS day, night and the diurnal-contrast index near zero globally; the index
possibly negative within blocks. Read-only; writes build\logs\tes_global_check.json.
"""
import os, sys, json
import numpy as np
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive
import grid60 as G

gdal.UseExceptions()
TES = on_drive(r"Mars Project\Reference\TES_thermal_inertia_2007")
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
INDEX = os.path.join(G.OUTDIR, "global60_thermal_contrast.tif")
OUT = os.path.join(HERE, "logs", "tes_global_check.json")
STEP = 0.05
TARGET_M = 1600.0                 # read the overview nearest 1.6 km: finer than TES's ~3 km cells
BLOCK = 15.0


def overview(band, full_cell, target):
    """The overview of band whose cell is nearest (but not coarser than) target metres."""
    best, best_cell = band, full_cell
    for i in range(band.GetOverviewCount()):
        o = band.GetOverview(i)
        cell = full_cell * band.XSize / float(o.XSize)
        if cell <= target and cell > best_cell:
            best, best_cell = o, cell
    return best, best_cell


def to_tes_cells(arr, cell_m, ox, oy, nodata):
    """Mean of arr per TES 0.05° cell (east -180..180, north up); returns (sum, count) grids."""
    H, W = arr.shape
    xs = ox + (np.arange(W) + .5) * cell_m
    ys = oy - (np.arange(H) + .5) * cell_m
    lon = (180.0 + np.degrees(xs / G.R_MARS) + 180.0) % 360.0 - 180.0
    lat = np.degrees(ys / G.R_MARS)
    col = ((lon + 180.0) / STEP).astype(int).clip(0, 7199)
    row = ((90.0 - lat) / STEP).astype(int).clip(0, 3599)
    idx = row[:, None] * 7200 + col[None, :]
    v = (arr != nodata) & np.isfinite(arr)
    s = np.bincount(idx.ravel(), weights=np.where(v, arr, 0).ravel(), minlength=7200 * 3600)
    n = np.bincount(idx.ravel(), weights=v.ravel().astype(float), minlength=7200 * 3600)
    return s, n


def main():
    layers = {}
    ds = gdal.Open(STACK)
    for b, name in ((1, "Viking red"), (4, "THEMIS night DN"), (5, "THEMIS day DN"), (6, "slope"), (7, "local relief")):
        band = ds.GetRasterBand(b)
        o, cell = overview(band, G.G200.res, TARGET_M)
        arr = o.ReadAsArray().astype(float)
        layers[name] = to_tes_cells(arr, cell, G.G200.ox, G.G200.oy, 0)
        print("  %-16s read at %.0f m  %d x %d" % (name, cell, o.XSize, o.YSize))
    di = gdal.Open(INDEX)
    band = di.GetRasterBand(1)
    o, cell = overview(band, G.G100.res, TARGET_M)
    arr = o.ReadAsArray().astype(float)
    layers["diurnal-contrast index"] = to_tes_cells(arr, cell, G.G100.ox, G.G100.oy, -32768)
    print("  %-16s read at %.0f m  %d x %d" % ("index", cell, o.XSize, o.YSize))
    res = {}
    for side in ("dayside", "nightside"):
        tds = gdal.Open(os.path.join(TES, "TES_TI_2007_%s.tif" % side))
        ti = tds.ReadAsArray().astype(float).ravel()
        mds = gdal.Open(os.path.join(TES, "TES_TI_2007_%s_measured.tif" % side))
        meas = (mds.ReadAsArray() == 1).ravel()
        rows = np.repeat(np.arange(3600), 7200); cols = np.tile(np.arange(7200), 3600)
        lat = 90.0 - (rows + .5) * STEP; lon = -180.0 + (cols + .5) * STEP
        blk = (np.floor((lat + 90) / BLOCK) * 100 + np.floor((lon + 180) / BLOCK)).astype(int)
        out = {}
        for name, (s, n) in layers.items():
            m = np.where(n > 0, s / np.maximum(n, 1), np.nan)
            ok = meas & (ti > 0) & np.isfinite(m) & (np.abs(lat) < 60)
            x, y, b = m[ok], np.log(ti[ok]), blk[ok]
            r_all = float(np.corrcoef(x, y)[0, 1])
            rb = []
            for k in np.unique(b):
                sel = b == k
                if sel.sum() >= 2000 and x[sel].std() > 0:
                    rb.append(np.corrcoef(x[sel], y[sel])[0, 1])
            out[name] = {"r_global": r_all, "r_within_blocks_median": float(np.median(rb)),
                         "r_within_blocks_p25_p75": [float(np.percentile(rb, 25)), float(np.percentile(rb, 75))],
                         "blocks": len(rb), "cells": int(ok.sum())}
            print("%-9s %-24s r global %+.2f   within 15° blocks: median %+.2f [%+.2f, %+.2f] over %d blocks"
                  % (side, name, r_all, out[name]["r_within_blocks_median"], *out[name]["r_within_blocks_p25_p75"], len(rb)))
        res[side] = out
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
