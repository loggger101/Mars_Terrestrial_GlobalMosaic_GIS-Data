# -*- coding: utf-8 -*-
r"""Test T17: the display mosaics against calibrated THEMIS thermal inertia at 100 m, in both type areas. (KB §69.144)

The paper's future work asked for THEMIS-derived inertia (Fergason et al. 2006) where it exists, to check the display
mosaics' local contrast at their own resolution; TES (~3 km) was the only calibrated product held. The USGS quantitative
THEMIS thermal-inertia mosaic (32-bit, 100 m, 30 x 60 deg tiles, ISIS3 cubes of 2.5 GB, internally tiled) was read
remotely through GDAL's /vsicurl/ for the two type-area windows only (2026-11-13, at the author's yes): tile 30S240E
for Ius Chasma and 00N120E for Athabasca Valles, warped bilinearly onto each window's 100 m grid (its equidistant
cylindrical, CM 180 frame) and kept in `Mars Project\Reference\THEMIS_TI_quantitative_windows\`.

Per window, every 5th pixel each way with all inputs valid: Spearman's rho of log THEMIS inertia with night IR, day IR,
the diurnal-contrast index, Viking red and slope, over the whole window and within 10 km tiles (100 x 100 px, at least
200 samples); intervals for the whole-window rho from 1,000 resamples of 50 km tiles.

Predictions, written 2026-11-13 before the first run:
  Q1  Night IR rises with inertia over each whole window: rho above 0.3 in both.
  Q2  Within 10 km tiles the median rho of night IR is higher than over the whole window, in both (the mosaics are
      stretched region by region, KB §28.10).
  Q3  Night IR tracks inertia better than the diurnal-contrast index does (whole window), in both.
  Q4  Viking red's |rho| is below night IR's (whole window), in both.

  "<ArcGIS Pro Python>" make_t17_themis_ti_windows.py   -> logs\t17_themis_ti_windows.json
"""
import os, sys, json
import numpy as np
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G

gdal.UseExceptions()
ROOT = os.path.dirname(G.OUTDIR)
OUT = os.path.join(HERE, "logs", "t17_themis_ti_windows.json")
AREAS = {"Ius Chasma": ("TypeArea", "ius"), "Athabasca Valles": ("Athabasca", "ath")}
INPUTS = ["night IR", "day IR", "diurnal contrast", "Viking red", "slope"]
STEP, TILE, BOOTTILE, MINN, NBOOT, SEED = 5, 100, 500, 200, 1000, 20261113


def rank(a):
    o = np.argsort(a, kind="mergesort")
    r = np.empty(a.size); r[o] = np.arange(a.size)
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    rng = np.random.default_rng(SEED)
    res = {"step_px": STEP, "tile_px": TILE, "areas": {}}
    for area, (folder, p) in AREAS.items():
        def rd(n, band=1):
            ds = gdal.Open(os.path.join(ROOT, folder, "%s_%s.tif" % (p, n)))
            return ds.GetRasterBand(band).ReadAsArray()[::STEP, ::STEP]
        ti = gdal.Open(os.path.join(ROOT, "Reference", "THEMIS_TI_quantitative_windows", "%s_themis_ti_quant.tif" % p)
                       ).ReadAsArray()[::STEP, ::STEP]
        L = {"night IR": rd("night").astype(float), "day IR": rd("day").astype(float),
             "diurnal contrast": rd("thermal_contrast").astype(float), "Viking red": rd("viking", 1).astype(float),
             "slope": rd("slope_deg").astype(float)}
        ok = (ti > 0) & (L["night IR"] > 0) & (L["day IR"] > 0) & (L["Viking red"] > 0) & (L["diurnal contrast"] > -9999) \
             & (L["slope"] > -1e30) & (L["slope"] < 1e30)
        H, W = ti.shape
        rr, cc = np.mgrid[0:H, 0:W]
        tile = (rr // (TILE // STEP)) * 10000 + cc // (TILE // STEP)
        btile = (rr // (BOOTTILE // STEP)) * 10000 + cc // (BOOTTILE // STEP)
        lt = np.log10(ti[ok]); tl, bt = tile[ok], btile[ok]
        A = {"n": int(ok.sum()), "ti_median": float(np.median(ti[ok])), "inputs": {}}
        ub, binv = np.unique(bt, return_inverse=True)
        groups = [np.flatnonzero(binv == j) for j in range(ub.size)]
        draws = [np.concatenate([groups[j] for j in rng.integers(0, ub.size, ub.size)]) for _ in range(NBOOT)]
        ut, tinv = np.unique(tl, return_inverse=True)
        tgroups = [np.flatnonzero(tinv == j) for j in range(ut.size)]
        for name in INPUTS:
            v = L[name][ok]
            whole = spearman(lt, v)
            boot = [spearman(lt[d], v[d]) for d in draws[:300]]          # 300 draws: rank correlations are slow
            tiles = np.array([spearman(lt[g], v[g]) for g in tgroups if g.size >= MINN and np.ptp(v[g]) > 0
                              and np.ptp(lt[g]) > 0])
            A["inputs"][name] = {"rho_whole": whole, "rho_whole_ci95": np.percentile(boot, [2.5, 97.5]).tolist(),
                                 "tiles": int(tiles.size), "rho_tile_median": float(np.median(tiles)),
                                 "rho_tile_iqr": np.percentile(tiles, [25, 75]).tolist(),
                                 "share_tiles_positive": float((tiles > 0).mean())}
            o = A["inputs"][name]
            print("%-16s %-16s whole rho %+.3f [%+.3f, %+.3f]  10 km tiles %d: median %+.3f (IQR %+.3f to %+.3f), %.0f %% positive" % (
                area, name, whole, *o["rho_whole_ci95"], tiles.size, o["rho_tile_median"], *o["rho_tile_iqr"],
                100 * o["share_tiles_positive"]), flush=True)
        res["areas"][area] = A
        print("%-16s %d samples, median THEMIS inertia %.0f tiu" % (area, A["n"], A["ti_median"]), flush=True)
    As = list(res["areas"].values())
    res["note_bootstrap"] = "whole-window intervals from 300 of the 1,000 drawn resamples of 50 km tiles"
    res["predictions"] = {
        "Q1 night IR whole-window rho > 0.3, both": all(a["inputs"]["night IR"]["rho_whole"] > 0.3 for a in As),
        "Q2 night IR median 10 km tile rho > whole-window rho, both":
            all(a["inputs"]["night IR"]["rho_tile_median"] > a["inputs"]["night IR"]["rho_whole"] for a in As),
        "Q3 night IR rho > diurnal contrast rho (whole), both":
            all(a["inputs"]["night IR"]["rho_whole"] > a["inputs"]["diurnal contrast"]["rho_whole"] for a in As),
        "Q4 |Viking red rho| < night IR rho (whole), both":
            all(abs(a["inputs"]["Viking red"]["rho_whole"]) < a["inputs"]["night IR"]["rho_whole"] for a in As)}
    for k, v in res["predictions"].items():
        print("prediction %-60s %s" % (k, "held" if v else "NOT HELD"), flush=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
