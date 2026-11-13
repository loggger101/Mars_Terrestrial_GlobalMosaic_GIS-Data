# -*- coding: utf-8 -*-
r"""Are 15 deg blocks wide enough for the intervals? Error correlation by distance, and intervals by block size.
(KB §69.141)

Every interval in the paper resamples whole 15 deg blocks (about 890 km at the equator), which is right only if the
errors of samples in different blocks are close to independent. Two checks on the material-label tests T10 and T11
(KB §69.133-§69.134; their lattice, held-out blocks, labels and maximum-likelihood fits, imported):
  1. Correlogram: on the held-out blocks, the error indicator of the all-7-band classifier (1 = wrong), its Pearson
     correlation between pairs of samples by great-circle distance (2,000,000 random pairs, 100 km bins to 3,000 km).
  2. Intervals by block size: the same predictions resampled by blocks of 5, 7.5, 15 and 30 deg (1,000 draws each);
     the width of the all-7 accuracy interval and the thermal gain's verdict by the rule at each.

Predictions, written 2026-11-13 before the first run:
  B1  For both label sets the error correlation falls below 0.1 by 890 km.
  B2  30 deg blocks widen the all-7 accuracy interval by less than 50 % over 15 deg blocks, for both label sets.
  B3  The thermal verdict by the rule is the same with 15 and with 30 deg blocks for both label sets.

  "<ArcGIS Pro Python>" make_block_size_check.py   -> logs\block_size_check.json
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_t9_material_labels as T9
import make_t10_ti_labels as T10
import make_t11_thermophysical_units as T11
import make_t12_label_robustness as T12
import grid60 as G

OUT = os.path.join(HERE, "logs", "block_size_check.json")
SIZES, NPAIRS, BINKM, MAXKM, SEED = (5.0, 7.5, 15.0, 30.0), 2000000, 100, 3000, 20261113


def main():
    X = np.load(T9.CACHE)["X"]
    ny, nx = X.shape[:2]
    ii, jj = np.mgrid[0:ny, 0:nx]
    lon, lat = T9.lattice_lonlat(ii, jj)
    lon_g = np.where(lon >= 180.0, lon - 360.0, lon)
    ti_lab, tiv = T10.ti_labels(lon_g, lat)
    alb = T11.albedo_at(lon_g, lat)
    split = json.load(open(T9.SPLIT, encoding="utf-8"))
    held = set(split["v2"]["test_blocks"])
    code = lambda bx, by: (bx + 100) * 100 + (by + 10)
    bid = code(np.floor(lon_g / T9.BLOCK).astype(np.int32), np.floor(lat / T9.BLOCK).astype(np.int32))
    test_block = np.isin(bid, [code(*map(int, b.split("_"))) for b in held])
    w = np.cos(np.radians(lat))
    rng = np.random.default_rng(SEED)
    res = {"sizes_deg": SIZES, "labels": {}}
    K = 3
    for name, (kind, edges) in (("T10 inertia classes", ("TI3", (150, 350))), ("T11 units", ("UNITS", (150, 0.20)))):
        lab = T12.labels(kind, edges, tiv, ti_lab > 0, alb)
        valid = (lab > 0) & (X > 0).all(-1)
        y = lab.astype(int) - 1
        tr, te = valid & ~test_block, valid & test_block
        preds = {s: T9.predict(T9.fit(X[tr], y[tr], T9.BANDSETS[s], K), X[te], T9.BANDSETS[s])
                 for s in ("all 7 bands", "without thermal (no night, day)")}
        yte, wte, la, lo = y[te], w[te], lat[te], lon_g[te]
        err = (preds["all 7 bands"] != yte).astype(float)
        # check: the all-7 accuracy equals the published block-split score
        acc = 1 - (wte * err).sum() / wte.sum()
        print("%s: %d test samples, all-7 accuracy %.4f" % (name, yte.size, acc), flush=True)
        # 1. correlogram
        a, b = rng.integers(0, yte.size, NPAIRS), rng.integers(0, yte.size, NPAIRS)
        d = G.R_MARS / 1000 * np.arccos(np.clip(np.sin(np.radians(la[a])) * np.sin(np.radians(la[b])) + np.cos(np.radians(la[a]))
                                                * np.cos(np.radians(la[b])) * np.cos(np.radians(lo[b] - lo[a])), -1, 1))
        m, v = err.mean(), err.var()
        bins = (d // BINKM).astype(int)
        corr = []
        for k in range(MAXKM // BINKM):
            s = bins == k
            corr.append(float(((err[a[s]] - m) * (err[b[s]] - m)).mean() / v) if s.sum() > 500 else None)
        first_below = next((BINKM * (k + 1) for k, c in enumerate(corr) if c is not None and c < 0.1), None)
        print("  error correlation by 100 km: " + " ".join("%.2f" % c if c is not None else "-" for c in corr[:20]), flush=True)
        print("  first bin below 0.1 ends at %s km" % first_below, flush=True)
        # 2. intervals by block size
        L = {"n_test": int(yte.size), "all7_accuracy": float(acc), "correlogram_km": BINKM, "correlogram": corr,
             "first_below_0p1_km": first_below, "by_size": {}}
        for sz in SIZES:
            g = (np.floor((lo + 180) / sz).astype(int)) * 1000 + np.floor((la + 90) / sz).astype(int)
            ub, binv = np.unique(g, return_inverse=True)
            cms = {}
            for s, p in preds.items():
                cm = np.zeros((ub.size, K, K))
                np.add.at(cm, (binv, yte, p), wte)
                cms[s] = cm
            counts = np.stack([np.bincount(rng.integers(0, ub.size, ub.size), minlength=ub.size) for _ in range(T9.NBOOT)])
            f = T9.stats(np.tensordot(counts, cms["all 7 bands"], axes=1))
            n = T9.stats(np.tensordot(counts, cms["without thermal (no night, day)"], axes=1))
            ci = lambda x: [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]
            acc_ci, ga, gb = ci(f[0]), ci(f[0] - n[0]), ci(f[2] - n[2])
            helps = ga[0] > 0 and gb[0] > 0
            L["by_size"]["%g" % sz] = {"groups": int(ub.size), "all7_accuracy_ci95": acc_ci,
                                       "width": acc_ci[1] - acc_ci[0], "thermal_acc_ci95": ga, "thermal_bal_ci95": gb,
                                       "thermal_helps": bool(helps)}
            print("  %4g deg blocks: %3d groups; all-7 accuracy [%.3f, %.3f] width %.3f; thermal acc [%+.4f, %+.4f] "
                  "bal [%+.4f, %+.4f] %s" % (sz, ub.size, *acc_ci, acc_ci[1] - acc_ci[0], *ga, *gb,
                                             "HELPS" if helps else "does not help"), flush=True)
        res["labels"][name] = L
    Ls = res["labels"].values()
    res["predictions"] = {
        "B1 error correlation below 0.1 by 890 km, both":
            all(l["first_below_0p1_km"] is not None and l["first_below_0p1_km"] <= 890 for l in Ls),
        "B2 30 deg widens the accuracy interval by < 50 % over 15 deg, both":
            all(l["by_size"]["30"]["width"] < 1.5 * l["by_size"]["15"]["width"] for l in Ls),
        "B3 same thermal verdict at 15 and 30 deg, both":
            all(l["by_size"]["30"]["thermal_helps"] == l["by_size"]["15"]["thermal_helps"] for l in Ls)}
    for k, v in res["predictions"].items():
        print("prediction %-65s %s" % (k, "held" if v else "NOT HELD"), flush=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
