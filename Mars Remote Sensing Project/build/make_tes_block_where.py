# -*- coding: utf-8 -*-
r"""Where the 5° THEMIS signal holds: each block's r against its own inertia level and range (KB §69.29).

Reads the three 5° r rasters written by make_tes_block_scale.py and nightside TES; per 5° block, the mean and the
standard deviation of log inertia over measured cells, placed on the same frame lattice (columns from 0°E). Reports
the Spearman correlation of each layer's r (signed so that positive is the physical direction) with the block's
mean and sd of log inertia, and the median signed r north and south of the equator and in three latitude bands.
Read-only; writes build\logs\tes_block_where.json.
"""
import os, sys, json
import numpy as np
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
from make_tes_global_check import TES

gdal.UseExceptions()
OUT = os.path.join(HERE, "logs", "tes_block_where.json")
LAYERS = (("nightIR", "night IR", +1), ("index", "diurnal-contrast index", -1), ("viking", "Viking red", -1))


def rank(a):
    return np.argsort(np.argsort(a)).astype(float)


def spearman(a, b):
    return float(np.corrcoef(rank(a), rank(b))[0, 1])


def main():
    ti = gdal.Open(os.path.join(TES, "TES_TI_2007_nightside.tif")).ReadAsArray()[600:3000].astype(float)
    meas = gdal.Open(os.path.join(TES, "TES_TI_2007_nightside_measured.tif")).ReadAsArray()[600:3000] == 1
    ok = meas & (ti > 0)
    y = np.where(ok, np.log(np.where(ti > 0, ti, 1)), 0)
    k = 100                                                   # 5° in 0.05° cells
    S = lambda a: a.reshape(24, k, 72, k).sum(axis=(1, 3))
    n, s1, s2 = S(ok.astype(float)), S(y), S(y * y)
    mean = np.roll(s1 / np.maximum(n, 1), -36, axis=1)       # columns from 180°W -> from 0°E, as the rasters
    sd = np.roll(np.sqrt(np.maximum(s2 / np.maximum(n, 1) - (s1 / np.maximum(n, 1)) ** 2, 0)), -36, axis=1)
    lat = 60 - 5 * (np.arange(24) + .5)
    LAT = np.repeat(lat[:, None], 72, axis=1)
    res = {}
    for tag, name, sign in LAYERS:
        ds = gdal.Open(os.path.join(G.OUTDIR, "global60_tes_r5deg_%s.tif" % tag))   # held: see make_tes_block_scale
        b = ds.GetRasterBand(1)
        r = b.ReadAsArray().astype(float); r[r == b.GetNoDataValue()] = np.nan
        v = np.isfinite(r)
        rp = sign * r
        d = {"blocks": int(v.sum()),
             "spearman_r_vs_mean_logTI": spearman(rp[v], mean[v]),
             "spearman_r_vs_sd_logTI": spearman(rp[v], sd[v]),
             "median_signed_r_north": float(np.median(rp[v & (LAT > 0)])),
             "median_signed_r_south": float(np.median(rp[v & (LAT < 0)])),
             "median_signed_r_by_band": {}}
        for lo, hi in ((30, 60), (0, 30), (-30, 0), (-60, -30)):
            sel = v & (LAT > lo) & (LAT < hi)
            d["median_signed_r_by_band"]["%d..%d" % (lo, hi)] = float(np.median(rp[sel]))
        tq = np.nanpercentile(sd[v], [33.3, 66.7])
        d["median_signed_r_by_sd_tercile"] = [float(np.median(rp[v & (sd <= tq[0])])),
                                              float(np.median(rp[v & (sd > tq[0]) & (sd <= tq[1])])),
                                              float(np.median(rp[v & (sd > tq[1])]))]
        d["sd_logTI_tercile_edges"] = [float(t) for t in tq]
        res[name] = d
        print("%-24s rho(r, mean logTI) %+.2f  rho(r, sd logTI) %+.2f  | median signed r N %+.3f S %+.3f  "
              "bands 30-60N %+.3f 0-30N %+.3f 0-30S %+.3f 30-60S %+.3f  | by sd tercile %+.3f %+.3f %+.3f" % (
                  name, d["spearman_r_vs_mean_logTI"], d["spearman_r_vs_sd_logTI"], d["median_signed_r_north"],
                  d["median_signed_r_south"], *d["median_signed_r_by_band"].values(),
                  *d["median_signed_r_by_sd_tercile"]))
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
