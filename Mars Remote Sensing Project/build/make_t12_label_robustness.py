# -*- coding: utf-8 -*-
r"""Test T12: do T10's and T11's answers survive other class edges and a nonlinear classifier? (KB §69.135)

T10 (TES inertia classes, KB §69.133) and T11 (thermophysical units, inertia x TES albedo, KB §69.134) found the thermal
bands add about a point and do not help across held-out blocks. Two choices could be behind that: the class edges
(fixed by convention, one setting each) and the classifier (Gaussian maximum likelihood, which can only draw quadric
boundaries and may miss a thermal signal that lives in an interaction). This reruns both tests over a grid of edges and
with gradient-boosted trees beside maximum likelihood, everything else as T9/T10/T11 (imported): the 4 km lattice, the
14 held-out 15 deg blocks and the within-block split, cos-latitude weights, 1,000 block resamples, the answer rule
(thermal HELPS at a split only if all 7 bands beat "without thermal" with both the accuracy and the balanced-accuracy
intervals above 0).

Label variants, fixed before the first run (the first of each is the published test):
  TI3 inertia edges (tiu)    150/350 (T10), 100/300, 200/400
  UNITS inertia / albedo     150/0.20 (T11), 150/0.18, 150/0.22, 200/0.20   (low-inertia dark corner dropped, as T11)
Classifiers:
  ML   T9's Gaussian maximum likelihood, equal priors
  GBT  scikit-learn HistGradientBoostingClassifier (max_iter 200, learning_rate 0.1, max_leaf_nodes 31, no early
       stopping), trained on 400,000 training samples drawn with probability proportional to cos(latitude), class
       weights 'balanced' (the counterpart of equal priors), random_state fixed
Band sets: all 7, and without thermal (T9's); only the thermal gain is scored here.

Predictions, written 2026-11-12 before the first run:
  P1  ML: at the block split thermal does NOT HELP by the rule for every one of the five new label variants.
  P2  At the block split thermal adds under 3 points of accuracy in all 14 runs (7 variants x 2 classifiers).
  P3  GBT's all-7 balanced accuracy at the block split is at least ML's in at least 5 of the 7 variants.
  P4  GBT: thermal HELPS at the block split by the rule in at most 2 of the 7 variants.
  P5  Unit C (duricrust): its producer's accuracy gains under 2 points from thermal at the block split in all 8 unit
      runs (4 variants x 2 classifiers).

  "<ArcGIS Pro Python>" make_t12_label_robustness.py   -> logs\t12_label_robustness.json
"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_t9_material_labels as T9
import make_t10_ti_labels as T10
import make_t11_thermophysical_units as T11
import grid60 as G

OUT = os.path.join(HERE, "logs", "t12_label_robustness.json")
log = T9.log
VARIANTS = [("TI3", (150, 350)), ("TI3", (100, 300)), ("TI3", (200, 400)),
            ("UNITS", (150, 0.20)), ("UNITS", (150, 0.18)), ("UNITS", (150, 0.22)), ("UNITS", (200, 0.20))]
NTRAIN_GBT = 400000
SETS = {k: T9.BANDSETS[k] for k in ("all 7 bands", "without thermal (no night, day)")}


def labels(kind, edges, tiv, measured, alb):
    lab = np.zeros(tiv.shape, np.int16)
    ok = measured & (tiv > 0)
    if kind == "TI3":
        lab[ok] = np.where(tiv[ok] < edges[0], 1, np.where(tiv[ok] < edges[1], 2, 3))
    else:
        ok &= alb > 0
        hi, bright = tiv >= edges[0], alb >= edges[1]
        lab[ok & ~hi & bright] = 1
        lab[ok & hi & bright] = 2
        lab[ok & hi & ~bright] = 3
    return lab


def make_gbt(seed):
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, max_leaf_nodes=31, early_stopping=False,
                                          class_weight="balanced", random_state=seed)


def main():
    T9.selftest()
    X = np.load(T9.CACHE)["X"]
    log("lattice from cache %s" % T9.CACHE)
    ny, nx = X.shape[:2]
    rng = np.random.default_rng(T9.SEED)
    ii, jj = np.mgrid[0:ny, 0:nx]
    lon, lat = T9.lattice_lonlat(ii, jj)
    lon_g = np.where(lon >= 180.0, lon - 360.0, lon)
    ti_lab, tiv = T10.ti_labels(lon_g, lat)
    measured = ti_lab > 0
    alb = T11.albedo_at(lon_g, lat)
    # check: the base variants reproduce T10's and T11's labels exactly
    assert np.array_equal(labels("TI3", (150, 350), tiv, measured, alb), ti_lab)
    assert np.array_equal(labels("UNITS", (150, 0.20), tiv, measured, alb), T11.unit_labels(lon_g, lat)[0])
    log("check: the base variants equal T10's and T11's labels")
    split = json.load(open(T9.SPLIT, encoding="utf-8"))
    held = set(split["v2"]["test_blocks"])
    code = lambda bx, by: (bx + 100) * 100 + (by + 10)
    bid = code(np.floor(lon_g / T9.BLOCK).astype(np.int32), np.floor(lat / T9.BLOCK).astype(np.int32))
    test_block = np.isin(bid, [code(*map(int, b.split("_"))) for b in held])
    cx, cy = np.floor(lon_g / T9.WCELL).astype(int), np.floor(lat / T9.WCELL).astype(int)
    cell = (cx + 1000) * 1000 + (cy + 100)
    uc = np.unique(cell)
    test_within = np.isin(cell, rng.choice(uc, uc.size // 2, replace=False))
    w = np.cos(np.radians(lat)).astype(np.float64)
    allok = (X > 0).all(-1)
    K = 3
    res = {"variants": [], "ntrain_gbt": NTRAIN_GBT}
    for kind, edges in VARIANTS:
        lab = labels(kind, edges, tiv, measured, alb)
        valid = (lab > 0) & allok
        y = lab.astype(int) - 1
        shares = [float(w[valid & (y == k)].sum() / w[valid].sum()) for k in range(K)]
        log("%s %s: %d samples, shares %s" % (kind, edges, valid.sum(), [round(s, 3) for s in shares]))
        V = {"kind": kind, "edges": list(edges), "n": int(valid.sum()), "shares": shares, "runs": {}}
        for sname, te_mask in (("block", test_block), ("within", test_within)):
            tr, te = valid & ~te_mask, valid & te_mask
            Xtr, ytr, wtr = X[tr], y[tr], w[tr]
            Xte, yte, wte, bte = X[te], y[te], w[te], bid[te]
            ub, binv = np.unique(bte, return_inverse=True)
            B = ub.size
            counts = np.stack([np.bincount(rng.integers(0, B, B), minlength=B) for _ in range(T9.NBOOT)])
            pick = rng.choice(len(ytr), NTRAIN_GBT, replace=False, p=wtr / wtr.sum())
            for clf in ("ML", "GBT"):
                out, boot = {}, {}
                for name, cols in SETS.items():
                    t0 = time.time()
                    if clf == "ML":
                        p = T9.predict(T9.fit(Xtr, ytr, cols, K), Xte, cols)
                    else:
                        m = make_gbt(T9.SEED).fit(Xtr[pick][:, cols].astype(np.float32), ytr[pick])
                        p = np.concatenate([m.predict(Xte[i:i + 1000000][:, cols].astype(np.float32))
                                            for i in range(0, len(yte), 1000000)])
                    cmb = np.zeros((B, K, K))
                    np.add.at(cmb, (binv, yte, p), wte)
                    po, kap, ba, prod = T9.stats(cmb.sum(0))
                    boot[name] = T9.stats(np.tensordot(counts, cmb, axes=1))
                    out[name] = {"accuracy": float(po), "kappa": float(kap), "balanced_accuracy": float(ba),
                                 "producers": [float(v) for v in prod], "seconds": round(time.time() - t0, 1)}
                ci = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
                f, n = out["all 7 bands"], out["without thermal (no night, day)"]
                fb, nb = boot["all 7 bands"], boot["without thermal (no night, day)"]
                g = {"accuracy": f["accuracy"] - n["accuracy"], "accuracy_ci95": ci(fb[0] - nb[0]),
                     "balanced_accuracy": f["balanced_accuracy"] - n["balanced_accuracy"],
                     "balanced_accuracy_ci95": ci(fb[2] - nb[2]),
                     "producers": [a - b for a, b in zip(f["producers"], n["producers"])],
                     "producers_ci95": [ci(fb[3][:, k] - nb[3][:, k]) for k in range(K)]}
                g["thermal_helps"] = bool(g["accuracy_ci95"][0] > 0 and g["balanced_accuracy_ci95"][0] > 0)
                V["runs"]["%s %s" % (sname, clf)] = {"sets": out, "thermal_gain": g}
                log("  %-6s %-3s all7 acc %5.1f bal %5.1f | thermal acc %+5.2f [%+.2f, %+.2f] bal %+5.2f [%+.2f, %+.2f]"
                    " | prod gain %s | %s" % (
                        sname, clf, 100 * f["accuracy"], 100 * f["balanced_accuracy"], 100 * g["accuracy"],
                        100 * g["accuracy_ci95"][0], 100 * g["accuracy_ci95"][1], 100 * g["balanced_accuracy"],
                        100 * g["balanced_accuracy_ci95"][0], 100 * g["balanced_accuracy_ci95"][1],
                        " ".join("%+.1f" % (100 * v) for v in g["producers"]),
                        "HELPS" if g["thermal_helps"] else "does not help"))
        res["variants"].append(V)
    vs = res["variants"]
    blk = lambda v, c: v["runs"]["block " + c]
    res["predictions"] = {
        "P1 ML block: thermal does not help for the five new variants":
            all(not blk(v, "ML")["thermal_gain"]["thermal_helps"] for i, v in enumerate(vs) if i not in (0, 3)),
        "P2 block: thermal adds < 3 pt accuracy in all 14 runs":
            all(blk(v, c)["thermal_gain"]["accuracy"] < 0.03 for v in vs for c in ("ML", "GBT")),
        "P3 block: GBT all-7 balanced >= ML's in at least 5 of 7":
            sum(blk(v, "GBT")["sets"]["all 7 bands"]["balanced_accuracy"]
                >= blk(v, "ML")["sets"]["all 7 bands"]["balanced_accuracy"] for v in vs) >= 5,
        "P4 GBT block: thermal helps in at most 2 of 7":
            sum(blk(v, "GBT")["thermal_gain"]["thermal_helps"] for v in vs) <= 2,
        "P5 block: duricrust producer's gain from thermal < 2 pt in all 8 unit runs":
            all(blk(v, c)["thermal_gain"]["producers"][1] < 0.02 for v in vs if v["kind"] == "UNITS"
                for c in ("ML", "GBT"))}
    for k, v in res["predictions"].items():
        log("prediction %-70s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
