# -*- coding: utf-8 -*-
r"""Test T15: is the thermal bands' small gain on material labels location, not material? (KB §69.139)

T10-T12 (KB §69.133-§69.135) found the thermal pair adds about half a point to a point on calibrated material labels,
resolved within blocks. With 51 km windows, map coordinates made up most or all of the thermal share on the landform
labels (KB §69.100): a contrast stretch set region by region tells a classifier where it is. This asks the same of the
material labels: add the sample's map coordinates (latitude, sin and cos of longitude) to both band sets, and see
whether the thermal gain survives.

Labels: T10's inertia classes (150/350 tiu) and T11's thermophysical units (150 tiu, albedo 0.20), the published
settings. Everything else is T12's (make_t12_label_robustness.py, imported): the lattice, the two splits, the 400,000
training samples for gradient-boosted trees, maximum likelihood with equal priors, 1,000 block resamples, the rule.
Band sets: all 7 + coords, without thermal + coords, and coords alone; the thermal gain is all 7 + coords minus
without thermal + coords.

Predictions, written 2026-11-12 before the first run:
  C1  Within blocks, with gradient-boosted trees, the thermal gain is smaller with coordinates than without (T12's)
      for both label sets.
  C2  Within blocks, with trees and coordinates, thermal still HELPS by the rule for both label sets (the contrast is
      local, T14, and coordinates at 4 km cannot stand in for it).
  C3  At the block split, with trees, coordinates alone reach at least 43.3 % balanced accuracy on the units (the
      dust and rock provinces are large).
  C4  At the block split thermal does NOT HELP with coordinates, with either classifier, on either label set.

  "<ArcGIS Pro Python>" make_t15_coords_control.py   -> logs\t15_coords_control.json
"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_t9_material_labels as T9
import make_t10_ti_labels as T10
import make_t11_thermophysical_units as T11
import make_t12_label_robustness as T12

OUT = os.path.join(HERE, "logs", "t15_coords_control.json")
T12_JSON = os.path.join(HERE, "logs", "t12_label_robustness.json")
log = T9.log
VARIANTS = [("TI3", (150, 350)), ("UNITS", (150, 0.20))]
SETS = {"all 7 + coords": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "without thermal + coords": [0, 1, 2, 5, 6, 7, 8, 9],
        "coords only": [7, 8, 9]}


def main():
    T9.selftest()
    X7 = np.load(T9.CACHE)["X"]
    ny, nx = X7.shape[:2]
    rng = np.random.default_rng(T9.SEED)
    ii, jj = np.mgrid[0:ny, 0:nx]
    lon, lat = T9.lattice_lonlat(ii, jj)
    lon_g = np.where(lon >= 180.0, lon - 360.0, lon)
    X = np.concatenate([X7.astype(np.float32), np.stack([lat, np.sin(np.radians(lon_g)), np.cos(np.radians(lon_g))],
                                                        -1).astype(np.float32)], -1)
    ti_lab, tiv = T10.ti_labels(lon_g, lat)
    measured = ti_lab > 0
    alb = T11.albedo_at(lon_g, lat)
    # the same splits as T12: the same seed, drawn in the same order
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
    allok = (X7 > 0).all(-1)
    K = 3
    t12 = json.load(open(T12_JSON, encoding="utf-8"))
    res = {"variants": []}
    for kind, edges in VARIANTS:
        lab = T12.labels(kind, edges, tiv, measured, alb)
        valid = (lab > 0) & allok
        y = lab.astype(int) - 1
        V = {"kind": kind, "edges": list(edges), "runs": {}}
        prev = next(v for v in t12["variants"] if v["kind"] == kind and v["edges"] == list(edges))
        for sname, te_mask in (("block", test_block), ("within", test_within)):
            tr, te = valid & ~te_mask, valid & te_mask
            Xtr, ytr, wtr = X[tr], y[tr], w[tr]
            Xte, yte, wte, bte = X[te], y[te], w[te], bid[te]
            ub, binv = np.unique(bte, return_inverse=True)
            B = ub.size
            counts = np.stack([np.bincount(rng.integers(0, B, B), minlength=B) for _ in range(T9.NBOOT)])
            pick = rng.choice(len(ytr), T12.NTRAIN_GBT, replace=False, p=wtr / wtr.sum())
            for clf in ("ML", "GBT"):
                out, boot = {}, {}
                for name, cols in SETS.items():
                    if clf == "ML":
                        p = T9.predict(T9.fit(Xtr, ytr, cols, K), Xte, cols)
                    else:
                        m = T12.make_gbt(T9.SEED).fit(Xtr[pick][:, cols], ytr[pick])
                        p = np.concatenate([m.predict(Xte[i:i + 1000000][:, cols]) for i in range(0, len(yte), 1000000)])
                    cmb = np.zeros((B, K, K))
                    np.add.at(cmb, (binv, yte, p), wte)
                    po, kap, ba, prod = T9.stats(cmb.sum(0))
                    boot[name] = T9.stats(np.tensordot(counts, cmb, axes=1))
                    out[name] = {"accuracy": float(po), "balanced_accuracy": float(ba), "producers": [float(v) for v in prod]}
                ci = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
                f, n = out["all 7 + coords"], out["without thermal + coords"]
                fb, nb = boot["all 7 + coords"], boot["without thermal + coords"]
                g = {"accuracy": f["accuracy"] - n["accuracy"], "accuracy_ci95": ci(fb[0] - nb[0]),
                     "balanced_accuracy": f["balanced_accuracy"] - n["balanced_accuracy"],
                     "balanced_accuracy_ci95": ci(fb[2] - nb[2])}
                g["thermal_helps"] = bool(g["accuracy_ci95"][0] > 0 and g["balanced_accuracy_ci95"][0] > 0)
                g0 = prev["runs"]["%s %s" % (sname, clf)]["thermal_gain"]
                V["runs"]["%s %s" % (sname, clf)] = {"sets": out, "thermal_gain": g,
                                                    "thermal_gain_without_coords_t12": {k: g0[k] for k in
                                                        ("accuracy", "balanced_accuracy", "thermal_helps")}}
                log("%s %s %-6s %-3s all7+c acc %5.1f bal %5.1f | coords only bal %5.1f | thermal acc %+5.2f [%+.2f, %+.2f]"
                    " bal %+5.2f [%+.2f, %+.2f] %s | without coords (T12) acc %+5.2f bal %+5.2f" % (
                        kind, edges, sname, clf, 100 * f["accuracy"], 100 * f["balanced_accuracy"],
                        100 * out["coords only"]["balanced_accuracy"], 100 * g["accuracy"], 100 * g["accuracy_ci95"][0],
                        100 * g["accuracy_ci95"][1], 100 * g["balanced_accuracy"], 100 * g["balanced_accuracy_ci95"][0],
                        100 * g["balanced_accuracy_ci95"][1], "HELPS" if g["thermal_helps"] else "does not help",
                        100 * g0["accuracy"], 100 * g0["balanced_accuracy"]))
        res["variants"].append(V)
    r = lambda i, k: res["variants"][i]["runs"][k]
    res["predictions"] = {
        "C1 within GBT: thermal gain smaller with coords, both labels":
            all(r(i, "within GBT")["thermal_gain"]["accuracy"]
                < r(i, "within GBT")["thermal_gain_without_coords_t12"]["accuracy"] for i in (0, 1)),
        "C2 within GBT + coords: thermal HELPS, both labels":
            all(r(i, "within GBT")["thermal_gain"]["thermal_helps"] for i in (0, 1)),
        "C3 block GBT: coords only >= 43.3 % balanced on the units":
            r(1, "block GBT")["sets"]["coords only"]["balanced_accuracy"] >= 0.433,
        "C4 block + coords: thermal does not help, both classifiers, both labels":
            not any(r(i, "block %s" % c)["thermal_gain"]["thermal_helps"] for i in (0, 1) for c in ("ML", "GBT"))}
    for k, v in res["predictions"].items():
        log("prediction %-75s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
