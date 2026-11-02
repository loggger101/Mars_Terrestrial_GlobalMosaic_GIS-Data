# -*- coding: utf-8 -*-
r"""A3 (b): a classifier on elevation and latitude alone, as a baseline for the held-out score (NEXT-STEPS §12.2 A3,
KB §69.50).

Mars's crustal dichotomy puts the cratered highlands high and in the south and the plains low and in the north, so
elevation and latitude alone may predict much of a landform class. This fits T1's classifier (make_thermal_ablation.py:
Gaussian maximum likelihood, one mean and covariance per class, equal priors, numpy) to two features, the HRSC/MOLA
height (global60_dem.tif, its 400 m overview) and the latitude, on every 400 m pixel inside the training polygons,
and scores it on the held-out polygons, area-weighted by cos(latitude), as T1 does. Four classes (terrain_60) and
seven (v2_60), the same splits as every published score. Interval: 1,000 bootstrap resamples of whole held-out
polygons (seed 60).

Predictions, written before the first run (each reported as held or not held):
  P1  four classes: within 10 points of the published SVM map's 73.8 % (>= 63.8 %);
  P2  seven classes: within 10 points of the seven-class SVM's 42.5 % (32.5-52.5 %).

  "<ArcGIS Pro Python>" make_elevation_baseline.py     -> logs\elevation_baseline.json  (reads the drive only)
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import numpy as np
from matplotlib.path import Path
import arcpy
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import grid60 as G

gdal.UseExceptions()
DEM = os.path.join(G.OUTDIR, "global60_dem.tif")
OUT = os.path.join(HERE, "logs", "elevation_baseline.json")
CELL, NBOOT, SEED = 400.0, 1000, 60
SETS = {"four": ("Landform_TrainingSamples_terrain_60_train", "Landform_TrainingSamples_terrain_60_test", 4, 0.738),
        "seven": ("Landform_TrainingSamples_v2_60_train", "Landform_TrainingSamples_v2_60_test", 7, 0.425)}


def extract(fcs):
    ds = gdal.Open(DEM)                                        # held: a band outlives no dataset
    b = ds.GetRasterBand(1)
    k = [i for i in range(b.GetOverviewCount()) if b.GetOverview(i).XSize == G.G200.nx // 2]
    assert k, "no 400 m overview on the DEM"
    ov = b.GetOverview(k[0])
    W, H, nod = ov.XSize, ov.YSize, b.GetNoDataValue()
    sr = arcpy.SpatialReference(); sr.loadFromString(G.TARGET_WKT)
    X, y, w, pid, test = [], [], [], [], []
    n = 0
    for is_test, fc in enumerate(fcs):
        with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue"], spatial_reference=sr) as cur:
            for g, v in cur:
                n += 1
                for part in g:
                    pts = np.array([(p.X, p.Y) for p in part if p is not None])
                    col = (pts[:, 0] - G.G200.ox) / CELL
                    row = (G.G200.oy - pts[:, 1]) / CELL
                    c0, c1 = max(int(col.min()), 0), min(int(np.ceil(col.max())) + 1, W)
                    r0, r1 = max(int(row.min()), 0), min(int(np.ceil(row.max())) + 1, H)
                    if c1 <= c0 or r1 <= r0:
                        continue
                    rr, cc = np.mgrid[r0:r1, c0:c1]
                    ins = Path(np.c_[col, row]).contains_points(np.c_[cc.ravel() + .5, rr.ravel() + .5]).reshape(rr.shape)
                    if not ins.any():
                        continue
                    z = ov.ReadAsArray(c0, r0, c1 - c0, r1 - r0)
                    sel = ins & (z != nod)
                    if not sel.any():
                        continue
                    lat = np.degrees((G.G200.oy - (rr[sel] + .5) * CELL) / G.R_MARS)
                    X.append(np.c_[z[sel].astype(np.float64), lat]); y.append(np.full(sel.sum(), int(v) - 1))
                    w.append(np.cos(np.radians(lat))); pid.append(np.full(sel.sum(), n)); test.append(np.full(sel.sum(), bool(is_test)))
    return np.concatenate(X), np.concatenate(y), np.concatenate(w), np.concatenate(pid), np.concatenate(test)


def fit(X, y, K):
    m = []
    for k in range(K):
        Z = X[y == k]
        cov = np.cov(Z, rowvar=False) + np.eye(2) * 1e-3
        m.append((Z.mean(0), np.linalg.inv(cov), np.linalg.slogdet(cov)[1]))
    return m


def predict(m, X):
    ll = np.stack([-0.5 * (np.einsum("ij,jk,ik->i", X - mu, ic, X - mu) + ld) for mu, ic, ld in m], 1)
    return ll.argmax(1)


def metrics(cm):
    tot = cm.sum(axis=(-2, -1))
    po = np.trace(cm, axis1=-2, axis2=-1) / tot
    pe = (cm.sum(-2) * cm.sum(-1)).sum(-1) / tot ** 2
    rows = cm.sum(-1)
    prod = np.where(rows > 0, np.diagonal(cm, axis1=-2, axis2=-1) / np.where(rows > 0, rows, 1), np.nan)
    return po, (po - pe) / (1 - pe), np.nanmean(prod, -1), prod


def main():
    t0 = time.time()
    res = {"method": "Gaussian maximum likelihood on (elevation, latitude), equal priors; 400 m; held-out, "
                     "area-weighted; polygon bootstrap 1,000, seed 60", "sets": {}}
    for name, (tr_fc, te_fc, K, svm) in SETS.items():
        X, y, w, pid, te = extract((tr_fc, te_fc))
        m = fit(X[~te], y[~te], K)
        p = predict(m, X[te])
        polys, inv = np.unique(pid[te], return_inverse=True)
        pc = np.zeros((len(polys), K, K))
        np.add.at(pc, (inv, y[te], p), w[te])
        acc, kp, bal, prod = metrics(pc.sum(0))
        rng = np.random.default_rng(SEED)
        cnt = np.stack([np.bincount(rng.integers(0, len(polys), len(polys)), minlength=len(polys)) for _ in range(NBOOT)])
        ba, bk, bb, _ = metrics(np.tensordot(cnt, pc, axes=1))
        ci = lambda a: [round(float(np.percentile(a, 2.5)), 4), round(float(np.percentile(a, 97.5)), 4)]
        res["sets"][name] = dict(train_px=int((~te).sum()), test_px=int(te.sum()), test_polygons=len(polys),
                                 accuracy=round(float(acc), 4), accuracy_ci95=ci(ba), kappa=round(float(kp), 4),
                                 kappa_ci95=ci(bk), balanced=round(float(bal), 4), balanced_ci95=ci(bb),
                                 producers=np.round(prod, 3).tolist(), svm_accuracy=svm,
                                 class_means=[[round(float(v), 2) for v in mu] for mu, _, _ in m])
        print("%s: accuracy %.1f %% [%.1f, %.1f], kappa %.3f, balanced %.1f %%; the SVM %.1f %%  (%d test px, %.0f s)" % (
            name, 100 * acc, 100 * ci(ba)[0], 100 * ci(ba)[1], kp, 100 * bal, 100 * svm, te.sum(), time.time() - t0))
    f, s = res["sets"]["four"], res["sets"]["seven"]
    res["predictions"] = {"P1 four-class >= 63.8 %": f["accuracy"] >= 0.638,
                          "P2 seven-class 32.5-52.5 %": 0.325 <= s["accuracy"] <= 0.525}
    print("predictions:", res["predictions"])
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print("->", OUT)


if __name__ == "__main__":
    main()
