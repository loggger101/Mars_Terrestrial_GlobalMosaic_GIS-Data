# -*- coding: utf-8 -*-
r"""Test T14: is the duricrust/dust contrast in the night mosaic locally, where the classifiers cannot use it? (KB §69.138)

T11-T12 (KB §69.134-§69.135) found the thermal bands add nothing to duricrust (unit C: high inertia, bright) against
dust (unit A: low inertia, bright), the pair only inertia tells apart. Two readings fit: the night mosaic does not hold
the contrast, or it holds it locally and the region-by-region stretch (KB §28.10) removes it between regions, so a
classifier trained across regions cannot use it. This tests the second directly.

For every 0.05 deg TES cell within 59.9 deg in unit A or C (T11's units: inertia 150 tiu, albedo 0.20, measured cells),
the stack's bands at the cell centre, read from the 7-band stack's 1.6 km overview (`global60_svm_stack_200m.tif`
overview 2). Per square window (1, 2 and 5 deg; 2 deg primary, where T3's night-IR signal peaked, KB §69.29) holding at
least 20 cells of each unit: the AUC of each band for C against A (P(band on a C cell > on an A cell), ties half).
Summaries: the median window AUC (cos-latitude weight of the window's cells) and the share of windows above 0.5, with
intervals from 1,000 resamples of whole 15 deg blocks of windows; and the pooled AUC over all cells, no windows.
Physics: duricrust's higher inertia keeps it warmer at night (night IR AUC > 0.5) and cooler by day (day IR < 0.5).

Predictions, written 2026-11-12 before the first run (2 deg windows):
  P1  Night IR is higher on duricrust within windows: median AUC above 0.55, and the share of windows above 0.5 has
      its interval above 0.5.
  P2  Pooled over all of +-60 deg, night IR's AUC is below 0.55 (the stretch removes the contrast between regions).
  P3  Within windows night IR separates the units better than Viking red: its median |AUC - 0.5| is larger.
  P4  Day IR is lower on duricrust within windows: median AUC below 0.5.

  "<ArcGIS Pro Python>" make_t14_crust_dust_local.py   -> logs\t14_crust_dust_local.json
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
import make_t13_maps_on_units as T13
from osgeo import gdal

gdal.UseExceptions()
OUT = os.path.join(HERE, "logs", "t14_crust_dust_local.json")
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
BANDS = ["Viking red", "Viking green", "Viking blue", "night IR", "day IR", "slope", "relief"]
OVR, OVPX = 2, 1600.0
WINDOWS, MINN, NBOOT, SEED = (1.0, 2.0, 5.0), 20, 1000, 20261112


def log(m):
    print(m, flush=True)


def auc_ranked(pos, neg):
    allv = np.r_[pos, neg].astype(float)
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt)
    r = (csum - (cnt - 1) / 2.0)[inv]
    return (r[:pos.size].sum() - pos.size * (pos.size + 1) / 2) / (pos.size * neg.size)


def main():
    lat, lon, tv, av, unit = T13.tes_cells()
    keep = (unit == 0) | (unit == 1)
    lat, lon, unit = lat[keep], lon[keep], unit[keep]
    ds = gdal.Open(STACK)
    ov = [ds.GetRasterBand(k + 1).GetOverview(OVR) for k in range(7)]
    W, H = ov[0].XSize, ov[0].YSize
    sc = ds.RasterXSize / W                                   # overview pixel in base pixels
    col = np.floor((G.R_MARS * np.radians(np.mod(lon, 360.0) - 180.0) - G.G200.ox) / (200.0 * sc)).astype(int)
    row = np.floor((G.G200.oy - G.R_MARS * np.radians(lat)) / (200.0 * sc)).astype(int)
    ok = (col >= 0) & (col < W) & (row >= 0) & (row < H)
    X = np.zeros((lat.size, 7), np.uint8)
    for k in range(7):
        A = ov[k].ReadAsArray()
        X[ok, k] = A[row[ok], col[ok]]
        if k == 3:   # check: 30 cells against single-pixel reads of the overview
            rng0 = np.random.default_rng(SEED)
            for i in rng0.choice(np.flatnonzero(ok), 30, replace=False):
                assert int(ov[k].ReadAsArray(int(col[i]), int(row[i]), 1, 1)[0, 0]) == int(X[i, k])
    valid = ok & (X > 0).all(1)
    lat, lon, unit, X = lat[valid], lon[valid], unit[valid], X[valid]
    w = np.cos(np.radians(lat))
    log("check: 30 of 30 night-IR values equal single-pixel reads of overview %d (%.0f m)" % (OVR, 200 * sc))
    log("%d cells in units A or C with all 7 bands (A %d, C %d)" % (lat.size, (unit == 0).sum(), (unit == 1).sum()))
    res = {"overview_m": 200 * sc, "min_cells_per_unit": MINN, "bands": BANDS, "pooled_auc": {}, "windows": {}}
    for k, b in enumerate(BANDS):
        res["pooled_auc"][b] = float(auc_ranked(X[unit == 1, k], X[unit == 0, k]))
    log("pooled AUC (C against A, all cells): " + ", ".join("%s %.3f" % (b, v) for b, v in res["pooled_auc"].items()))
    rng = np.random.default_rng(SEED)
    for ws in WINDOWS:
        wid = (np.floor((lon + 180) / ws).astype(int)) * 1000 + np.floor((lat + 90) / ws).astype(int)
        order = np.argsort(wid, kind="stable")
        uw, start = np.unique(wid[order], return_index=True)
        ends = np.r_[start[1:], order.size]
        aucs, wts, blks = [], [], []
        for s, e in zip(start, ends):
            idx = order[s:e]
            u = unit[idx]
            if (u == 0).sum() < MINN or (u == 1).sum() < MINN:
                continue
            aucs.append([auc_ranked(X[idx][u == 1, k], X[idx][u == 0, k]) for k in range(7)])
            wts.append(w[idx].sum())
            cl, ct = lon[idx].mean(), lat[idx].mean()
            blks.append(int(np.floor((cl + 180) / 15)) * 100 + int(np.floor((ct + 90) / 15)))
        aucs, wts, blks = np.array(aucs), np.array(wts), np.array(blks)
        ub, binv = np.unique(blks, return_inverse=True)
        def wmed(a, ww):
            o = np.argsort(a); c = np.cumsum(ww[o]); return a[o][np.searchsorted(c, c[-1] / 2)]
        out = {"n_windows": int(len(wts)), "n_blocks": int(ub.size), "bands": {}}
        draws = [np.concatenate([np.flatnonzero(binv == j) for j in rng.integers(0, ub.size, ub.size)])
                 for _ in range(NBOOT)]
        for k, b in enumerate(BANDS):
            a = aucs[:, k]
            med, share = wmed(a, wts), float((wts * (a > 0.5)).sum() / wts.sum())
            bm = [wmed(a[d], wts[d]) for d in draws]
            bs = [(wts[d] * (a[d] > 0.5)).sum() / wts[d].sum() for d in draws]
            bd = [wmed(np.abs(a[d] - 0.5), wts[d]) for d in draws]
            out["bands"][b] = {"median_auc": float(med), "median_auc_ci95": np.percentile(bm, [2.5, 97.5]).tolist(),
                               "share_above_half": share, "share_ci95": np.percentile(bs, [2.5, 97.5]).tolist(),
                               "median_abs_dev": float(wmed(np.abs(a - 0.5), wts)),
                               "median_abs_dev_ci95": np.percentile(bd, [2.5, 97.5]).tolist()}
            o = out["bands"][b]
            log("%.0f deg  %-12s windows %4d  median AUC %.3f [%.3f, %.3f]  share > 0.5 %.2f [%.2f, %.2f]  |AUC-0.5| %.3f" % (
                ws, b, len(wts), med, *o["median_auc_ci95"], share, *o["share_ci95"], o["median_abs_dev"]))
        # paired: night |AUC-0.5| minus Viking red's, same draws
        dn = [wmed(np.abs(aucs[d, 3] - 0.5), wts[d]) - wmed(np.abs(aucs[d, 0] - 0.5), wts[d]) for d in draws]
        out["night_minus_vikingred_abs_dev_ci95"] = np.percentile(dn, [2.5, 97.5]).tolist()
        log("%.0f deg  night minus Viking red, median |AUC-0.5|: %+.3f [%+.3f, %+.3f]" % (
            ws, out["bands"]["night IR"]["median_abs_dev"] - out["bands"]["Viking red"]["median_abs_dev"],
            *out["night_minus_vikingred_abs_dev_ci95"]))
        res["windows"]["%g deg" % ws] = out
    p = res["windows"]["2 deg"]["bands"]
    res["predictions"] = {
        "P1 2 deg: night IR median AUC > 0.55 and share > 0.5 interval above 0.5":
            p["night IR"]["median_auc"] > 0.55 and p["night IR"]["share_ci95"][0] > 0.5,
        "P2 pooled night IR AUC < 0.55": res["pooled_auc"]["night IR"] < 0.55,
        "P3 2 deg: night IR median |AUC-0.5| > Viking red's":
            p["night IR"]["median_abs_dev"] > p["Viking red"]["median_abs_dev"],
        "P4 2 deg: day IR median AUC < 0.5": p["day IR"]["median_auc"] < 0.5}
    for k, v in res["predictions"].items():
        log("prediction %-75s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
