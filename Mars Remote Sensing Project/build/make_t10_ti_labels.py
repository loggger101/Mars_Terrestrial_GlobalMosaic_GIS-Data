# -*- coding: utf-8 -*-
r"""Test T10: do the thermal bands help predict a calibrated material property? (KB §69.133)

The paper's limit (and NEXT-STEPS's last card) says the thermal bands' share needs material labels, and T9 (KB §69.50)
tried the geologic map's unit groups, which are partly age and stratigraphy. Here the label is a measured material
property from a different instrument: TES nightside apparent thermal inertia (Putzig & Mellon 2007, held since
2026-10-08, `Mars Project\Reference\TES_thermal_inertia_2007\`), on cells TES measured (the `_measured` mask; gap-filled
cells are dropped). Three classes, by the conventional reading of inertia (Mellon et al. 2000; Putzig & Mellon 2007):
  1 low       < 150 tiu    fine dust mantles
  2 moderate  150-349 tiu  sand, duricrust, mixed surfaces
  3 high      >= 350 tiu   coarse sand, rocks, bedrock
Chosen before the first run, not tuned to the data.

Everything else is T9's (make_t9_material_labels.py, imported): the 4 km lattice of the stack's 400 m overview, the
label sets' 14 held-out 15 deg blocks and the within-block split (3 deg cells, a random half held out), Gaussian maximum
likelihood, area weights cos(latitude), 1,000 bootstrap resamples of whole 15 deg blocks, the band sets (all 7, without
thermal, thermal only, without Viking) and the answer rule: thermal HELPS at a split if all 7 bands beat "without
thermal" with both the accuracy and the balanced-accuracy intervals above 0.

Two priors, both registered: equal priors (T9's registered choice; balanced accuracy is the score that matters) and
training-share priors (T9's post-hoc fix, here registered in advance).

Predictions, written 2026-11-12 before the first run:
  P1  At the block split, thermal adds under 3 points of accuracy (T3: THEMIS tracks TES inertia only weakly within
      regions, |r| ~ 0.1; the mosaics are stretched region by region, KB §28.10).
  P2  Thermal adds more within blocks than at the block split (the local contrast survives the stretch).
  P3  At the block split, leaving out Viking costs more balanced accuracy than leaving out thermal (Viking red tracks
      inertia planet-wide, r -0.36, T3).
  P4  At the block split, all 7 bands beat one class everywhere in balanced accuracy (33.3 % for three classes) by at
      least 10 points: the stack predicts this material property at all.
  The answer to "do the thermal bands carry material information?" is the answer rule, per split.

  "<ArcGIS Pro Python>" make_t10_ti_labels.py [--priors train]   -> logs\t10_ti_labels[_trainpriors].json
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_t9_material_labels as T9
import grid60 as G

TES = os.path.join(os.path.dirname(G.OUTDIR), "Reference", "TES_thermal_inertia_2007")
EDGES = (150, 350)
CLASSES = ["low inertia (< 150)", "moderate (150-349)", "high (>= 350)"]
PRIORS = T9.PRIORS
OUT = os.path.join(HERE, "logs", "t10_ti_labels%s.json" % ("" if PRIORS == "equal" else "_trainpriors"))
log = T9.log


def ti_labels(lon_g, lat):
    from osgeo import gdal
    gdal.UseExceptions()
    ti = gdal.Open(os.path.join(TES, "TES_TI_2007_nightside.tif")).ReadAsArray()
    meas = gdal.Open(os.path.join(TES, "TES_TI_2007_nightside_measured.tif")).ReadAsArray()
    c = np.clip(((lon_g + 180.0) / 0.05).astype(int), 0, ti.shape[1] - 1)
    r = np.clip(((90.0 - lat) / 0.05).astype(int), 0, ti.shape[0] - 1)
    v, m = ti[r, c], meas[r, c]
    lab = np.where(v < EDGES[0], 1, np.where(v < EDGES[1], 2, 3)).astype(np.int16)
    lab[(v <= 0) | (m != 1)] = 0
    return lab, v


def main():
    T9.selftest()
    ny, nx = (G.G200.ny // 2 + 1 - T9.OFF + T9.STEP - 1) // T9.STEP, (G.G200.nx // 2 - T9.OFF + T9.STEP - 1) // T9.STEP
    rng = np.random.default_rng(T9.SEED)
    if os.path.exists(T9.CACHE) and "--fresh" not in sys.argv:
        X = np.load(T9.CACHE)["X"]
        log("lattice from cache %s" % T9.CACHE)
    else:
        X = T9.read_lattice(ny, nx)
        os.makedirs(os.path.dirname(T9.CACHE), exist_ok=True)
        np.savez_compressed(T9.CACHE, X=X)
    ii, jj = np.mgrid[0:ny, 0:nx]
    lon, lat = T9.lattice_lonlat(ii, jj)
    lon_g = np.where(lon >= 180.0, lon - 360.0, lon)
    lab, tiv = ti_labels(lon_g, lat)
    # check: 200 labels against a direct read of the TES raster through GDAL's own geotransform
    from osgeo import gdal
    ds = gdal.Open(os.path.join(TES, "TES_TI_2007_nightside.tif"))
    gt = ds.GetGeoTransform()
    pi, pj = rng.integers(0, ny, 200), rng.integers(0, nx, 200)
    same = sum(int(ds.ReadAsArray(int((lon_g[i, j] - gt[0]) / gt[1]), int((lat[i, j] - gt[3]) / gt[5]), 1, 1)[0, 0])
               == int(tiv[i, j]) for i, j in zip(pi, pj))
    log("check: %d of 200 lattice inertia values equal a direct GDAL read" % same)
    assert same == 200
    valid = (lab > 0) & (X > 0).all(-1)
    y = lab.astype(int) - 1
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
    K = 3
    log("lattice %d x %d; %d valid labelled samples; class shares %s" % (ny, nx, valid.sum(), [
        round(float(w[valid & (y == k)].sum() / w[valid].sum()), 3) for k in range(K)]))
    res = {"method": "T9's design (make_t9_material_labels.py) with TES nightside thermal inertia classes as the label",
           "classes": CLASSES, "edges_tiu": EDGES, "priors": PRIORS, "bands": T9.BANDS,
           "label_check_direct_reads": same, "held_out_blocks": sorted(held), "splits": {}}
    for sname, te_mask in (("block", test_block), ("within", test_within)):
        tr, te = valid & ~te_mask, valid & te_mask
        Xtr, ytr = X[tr], y[tr]
        Xte, yte, wte, bte = X[te], y[te], w[te], bid[te]
        ub, binv = np.unique(bte, return_inverse=True)
        B = ub.size
        counts = np.stack([np.bincount(rng.integers(0, B, B), minlength=B) for _ in range(T9.NBOOT)])
        area = np.bincount(yte, weights=wte, minlength=K)
        out = {"n_train": int(tr.sum()), "n_test": int(te.sum()), "test_blocks": int(B),
               "one_class_everywhere": float(area.max() / area.sum()),
               "test_share_by_class": dict(zip(CLASSES, (area / area.sum()).round(4).tolist())), "sets": {}}
        boot = {}
        for name, cols in T9.BANDSETS.items():
            p = T9.predict(T9.fit(Xtr, ytr, cols, K), Xte, cols)
            cmb = np.zeros((B, K, K))
            np.add.at(cmb, (binv, yte, p), wte)
            po, kap, ba, prod = T9.stats(cmb.sum(0))
            boot[name] = T9.stats(np.tensordot(counts, cmb, axes=1))
            out["sets"][name] = {"accuracy": float(po), "kappa": float(kap), "balanced_accuracy": float(ba),
                                 "producers": dict(zip(CLASSES, np.round(prod, 4).tolist())),
                                 "balanced_ci95": [float(np.nanpercentile(boot[name][2], 2.5)),
                                                   float(np.nanpercentile(boot[name][2], 97.5))]}
            log("%-6s %-32s acc %5.1f %%  kappa %.3f  balanced %5.1f %%" % (sname, name, 100 * po, kap, 100 * ba))
        ci = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
        full = out["sets"]["all 7 bands"]
        for name in T9.BANDSETS:
            if name == "all 7 bands":
                continue
            s = out["sets"][name]
            s["gain_from_full_stack"] = {
                "accuracy": full["accuracy"] - s["accuracy"], "accuracy_ci95": ci(boot["all 7 bands"][0] - boot[name][0]),
                "balanced_accuracy": full["balanced_accuracy"] - s["balanced_accuracy"],
                "balanced_accuracy_ci95": ci(boot["all 7 bands"][2] - boot[name][2])}
            g = s["gain_from_full_stack"]
            log("%-6s   all 7 minus %-30s acc %+5.1f pt [%+.1f, %+.1f]  balanced %+5.1f pt [%+.1f, %+.1f]" % (
                sname, name, 100 * g["accuracy"], 100 * g["accuracy_ci95"][0], 100 * g["accuracy_ci95"][1],
                100 * g["balanced_accuracy"], 100 * g["balanced_accuracy_ci95"][0], 100 * g["balanced_accuracy_ci95"][1]))
        g = out["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
        out["thermal_helps"] = bool(g["accuracy_ci95"][0] > 0 and g["balanced_accuracy_ci95"][0] > 0)
        log("%-6s thermal %s on inertia labels (one class everywhere %.1f %%)"
            % (sname, "HELPS" if out["thermal_helps"] else "does NOT HELP", 100 * out["one_class_everywhere"]))
        res["splits"][sname] = out
    S = res["splits"]
    gb = S["block"]["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
    gw = S["within"]["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
    gv = S["block"]["sets"]["without visible (no Viking)"]["gain_from_full_stack"]
    res["predictions"] = {
        "P1 block: thermal adds < 3 pt of accuracy": bool(gb["accuracy"] < 0.03),
        "P2 thermal adds more within blocks than at the block split": bool(gw["accuracy"] > gb["accuracy"]),
        "P3 block: leaving out Viking costs more balanced accuracy than leaving out thermal":
            bool(gv["balanced_accuracy"] > gb["balanced_accuracy"]),
        "P4 block: all 7 bands >= 43.3 % balanced": bool(S["block"]["sets"]["all 7 bands"]["balanced_accuracy"] >= 0.433)}
    for k, v in res["predictions"].items():
        log("prediction %-80s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
