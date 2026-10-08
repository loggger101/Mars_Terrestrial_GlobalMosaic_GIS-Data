# -*- coding: utf-8 -*-
r"""Test T1: do the THEMIS bands improve the ±60° landform classification? (KB §40, NEXT-STEPS §4)

The project's central claim is that thermal infrared separates surfaces visible light cannot.
§18.3 measured band independence and §24 a local index, but no classification had been scored
with and without the thermal bands on the hand-drawn labels. This does it, on the §31 split.

Prediction, written before the run: little or no gain at ±60°, because both THEMIS mosaics are
locally contrast-normalised (§28.10). Reported whichever way it falls.

Method
  * Samples: every 400 m pixel of global60_svm_stack_200m.tif (its first overview, the cell of the
    published map) inside each polygon of Landform_TrainingSamples_terrain_60_train / _60_test,
    valid in all 7 bands. Area weight cos(latitude).
  * Classifier: Gaussian maximum likelihood (one mean and covariance per class, equal priors),
    in numpy. It is NOT the published SVM (scikit-learn is not installed in either Python here),
    so absolute scores differ from §31.3; the comparison BETWEEN band sets is the result.
  * Score: held-out, area-weighted overall accuracy and kappa, per-class producer's/user's.
  * Uncertainty: 1,000 bootstrap resamples of whole held-out polygons (pixels inside one polygon
    are not independent), the same resample for every band set, so differences are paired.

Read-only. Samples cached to %LOCALAPPDATA%\Temp\mars_scratch\ablation_samples.npz (rerun with
--fresh to re-extract). Writes build\logs\thermal_ablation.json.
"""
import os, sys, json, time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G

STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
GDB = on_drive(r"Mars Project\Mars Project.gdb")
SETS = {"train": "Landform_TrainingSamples_terrain_60_train", "test": "Landform_TrainingSamples_terrain_60_test"}
BANDS = ["Viking R", "Viking G", "Viking B", "Night IR", "Day IR", "slope", "relief"]
NAMES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]      # Classvalue 1..4
BANDSETS = {
    "all 7 bands":                     [0, 1, 2, 3, 4, 5, 6],
    "without thermal (no night, day)": [0, 1, 2, 5, 6],
    "without visible (no Viking)":     [3, 4, 5, 6],
    "visible + thermal (no terrain)":  [0, 1, 2, 3, 4],
    "visible only":                    [0, 1, 2],
    "thermal only":                    [3, 4],
    "terrain only":                    [5, 6],
}
CACHE = os.path.join(os.environ.get("LOCALAPPDATA", HERE), "Temp", "mars_scratch", "ablation_samples.npz")
OUT = os.path.join(HERE, "logs", "thermal_ablation.json")
CELL = 400.0
NBOOT = 1000
SEED = 60


def extract():
    import arcpy
    from osgeo import gdal
    gdal.UseExceptions()
    ds = gdal.Open(STACK)
    b1 = ds.GetRasterBand(1)
    k = [i for i in range(b1.GetOverviewCount()) if b1.GetOverview(i).XSize == G.G200.nx // 2]
    assert k, "no 400 m overview on the stack"
    ovs = [ds.GetRasterBand(b + 1).GetOverview(k[0]) for b in range(7)]
    W, H = ovs[0].XSize, ovs[0].YSize
    sr = arcpy.SpatialReference(); sr.loadFromString(G.TARGET_WKT)
    X, y, w, pid, split = [], [], [], [], []
    n_poly = 0
    for s, fc in SETS.items():
        with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue"], spatial_reference=sr) as cur:
            for g, v in cur:
                n_poly += 1
                for part in g:
                    pts = np.array([(p.X, p.Y) for p in part if p is not None])
                    col = (pts[:, 0] - G.G200.ox) / CELL
                    row = (G.G200.oy - pts[:, 1]) / CELL
                    c0, c1 = max(int(col.min()), 0), min(int(np.ceil(col.max())) + 1, W)
                    r0, r1 = max(int(row.min()), 0), min(int(np.ceil(row.max())) + 1, H)
                    if c1 <= c0 or r1 <= r0:
                        continue
                    rr, cc = np.mgrid[r0:r1, c0:c1]
                    ins = Path(np.c_[col, row]).contains_points(
                        np.c_[cc.ravel() + .5, rr.ravel() + .5]).reshape(rr.shape)
                    if not ins.any():
                        continue
                    cube = np.stack([o.ReadAsArray(c0, r0, c1 - c0, r1 - r0) for o in ovs], axis=-1)
                    sel = ins & (cube > 0).all(axis=-1)
                    if not sel.any():
                        continue
                    lat = np.degrees((G.G200.oy - (rr[sel] + .5) * CELL) / G.R_MARS)
                    X.append(cube[sel]); y.append(np.full(sel.sum(), int(v) - 1, np.int8))
                    w.append(np.cos(np.radians(lat)).astype(np.float32))
                    pid.append(np.full(sel.sum(), n_poly, np.int32)); split.append(np.full(sel.sum(), s == "test"))
    out = dict(X=np.concatenate(X), y=np.concatenate(y), w=np.concatenate(w),
               pid=np.concatenate(pid), test=np.concatenate(split))
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    np.savez_compressed(CACHE, **out)
    return out


def fit(X, y, cols):
    """Per-class mean and covariance, equal priors."""
    models = []
    for k in range(4):
        Z = X[y == k][:, cols].astype(np.float64)
        mu = Z.mean(0)
        cov = np.cov(Z, rowvar=False) + np.eye(len(cols)) * 1e-3
        models.append((mu, np.linalg.inv(cov), np.linalg.slogdet(cov)[1]))
    return models


def predict(models, X, cols, chunk=500000):
    out = np.empty(len(X), np.int8)
    for i in range(0, len(X), chunk):
        Z = X[i:i + chunk][:, cols].astype(np.float64)
        ll = np.stack([-0.5 * (np.einsum("ij,jk,ik->i", Z - mu, icov, Z - mu) + logdet)
                       for mu, icov, logdet in models], axis=1)
        out[i:i + chunk] = ll.argmax(1)
    return out


def scores(t, p, w):
    cm = np.zeros((4, 4))
    np.add.at(cm, (t, p), w)
    tot = cm.sum()
    po = np.trace(cm) / tot
    pe = (cm.sum(0) * cm.sum(1)).sum() / tot ** 2
    prod = np.diag(cm) / np.maximum(cm.sum(1), 1e-12)
    user = np.diag(cm) / np.maximum(cm.sum(0), 1e-12)
    return po, (po - pe) / (1 - pe), prod, user, cm


def main():
    t0 = time.time()
    if os.path.exists(CACHE) and "--fresh" not in sys.argv:
        d = dict(np.load(CACHE))
        print("samples from cache", CACHE)
    else:
        d = extract()
        print("extracted in %.0f s" % (time.time() - t0))
    X, y, w, pid, test = d["X"], d["y"].astype(int), d["w"], d["pid"], d["test"]
    tr, te = ~test, test
    print("train %d px in %d polygons; test %d px in %d polygons"
          % (tr.sum(), len(np.unique(pid[tr])), te.sum(), len(np.unique(pid[te]))))
    res = {"method": "Gaussian maximum likelihood, equal priors, numpy; 400 m; held-out area-weighted",
           "n_train_px": int(tr.sum()), "n_test_px": int(te.sum()),
           "n_test_polygons": int(len(np.unique(pid[te]))), "bands": BANDS, "sets": {}}
    # the baseline the record quotes: one class everywhere (the commonest held-out class by area)
    area = np.bincount(y[te], weights=w[te], minlength=4)
    res["one_class_everywhere"] = float(area.max() / area.sum())
    # paired bootstrap over whole held-out polygons: each polygon's weighted confusion matrix is
    # computed once per band set, and a resample is a count-weighted sum of them. (Re-indexing the
    # pixels for every resample needed > 4 GB at this sample size.)
    rng = np.random.default_rng(SEED)
    test_polys, inv = np.unique(pid[te], return_inverse=True)
    P = len(test_polys)
    counts = np.stack([np.bincount(rng.integers(0, P, P), minlength=P) for _ in range(NBOOT)])   # NBOOT x P
    preds, poly_cm = {}, {}
    for name, cols in BANDSETS.items():
        models = fit(X[tr], y[tr], cols)
        p = predict(models, X[te], cols)
        preds[name] = p
        cmp_ = np.zeros((P, 4, 4))
        np.add.at(cmp_, (inv, y[te], p), w[te])
        poly_cm[name] = cmp_
        po, k, prod, user, cm = scores(y[te], p, w[te])
        res["sets"][name] = {"bands": [BANDS[c] for c in cols], "accuracy": po, "kappa": k,
                             "producers": dict(zip(NAMES, prod.tolist())), "users": dict(zip(NAMES, user.tolist()))}
        print("  %-34s acc %5.1f%%  kappa %.3f" % (name, 100 * po, k))
    # paired differences against the full stack, with 95% bootstrap intervals
    def acc_kappa(cms):                       # cms: NBOOT x 4 x 4
        tot = cms.sum(axis=(1, 2))
        po = np.trace(cms, axis1=1, axis2=2) / tot
        pe = (cms.sum(1) * cms.sum(2)).sum(1) / tot ** 2
        return po, (po - pe) / (1 - pe)
    a_full, k_full = acc_kappa(np.tensordot(counts, poly_cm["all 7 bands"], axes=1))
    for name in BANDSETS:
        if name == "all 7 bands":
            continue
        a_sub, k_sub = acc_kappa(np.tensordot(counts, poly_cm[name], axes=1))
        da, dk = a_full - a_sub, k_full - k_sub
        res["sets"][name]["gain_from_full_stack"] = {
            "accuracy": float(res["sets"]["all 7 bands"]["accuracy"] - res["sets"][name]["accuracy"]),
            "accuracy_ci95": [float(np.percentile(da, 2.5)), float(np.percentile(da, 97.5))],
            "kappa": float(res["sets"]["all 7 bands"]["kappa"] - res["sets"][name]["kappa"]),
            "kappa_ci95": [float(np.percentile(dk, 2.5)), float(np.percentile(dk, 97.5))]}
        g = res["sets"][name]["gain_from_full_stack"]
        print("    full stack minus %-30s acc %+5.1f pt [%+.1f, %+.1f]   kappa %+.3f [%+.3f, %+.3f]"
              % (name, 100 * g["accuracy"], 100 * g["accuracy_ci95"][0], 100 * g["accuracy_ci95"][1],
                 g["kappa"], g["kappa_ci95"][0], g["kappa_ci95"][1]))
    res["one_class_everywhere_note"] = "area share of the commonest held-out class"
    print("  one class everywhere: %.1f%%" % (100 * res["one_class_everywhere"]))
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT, "in %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
