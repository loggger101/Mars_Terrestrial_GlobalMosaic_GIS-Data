# -*- coding: utf-8 -*-
r"""A5: block-bootstrap intervals for the held-out scores, and where the errors sit (NEXT-STEPS §12.2 A5).

Every interval in the record so far resamples whole held-out polygons (score_t1_bootstrap.py, KB §56; the paper's
Table 2). The held-out polygons are not independent: they lie in 14 whole 15° blocks, and polygons in one block share
its geology, its imagery and the classifier's errors there. This script scores each held-out polygon alone with the
scorer's own routine (svmcheck.training_score on the 400 m grid, as verify_global60_classification.py), so any
resample is a sum of polygon rows, then resamples the 14 blocks (10,000 times, seed 60) beside the polygons (the
same), every map paired on the same resample.

Maps, each checked first against its own log (accuracy and kappa within 0.001, or nothing is written):
  four classes, 183 held-out polygons (Landform_TrainingSamples_terrain_60_test):
    svm4    the published map, 200 m 11 x 11 (KB §57)            cached 400 m array
    unet4   the two-pass U-Net (§66.8)                          cached 400 m array
    all200  T1's all-band map, 200 m unfiltered (§56)           the raster's 400 m overview, as score_t1_bootstrap.py
    noth200 T1's map without the thermal bands (§56)            the same
    near4   the nearest training polygon (§69.35, nearest_polygon.py)
  seven classes, 237 held-out polygons (Landform_TrainingSamples_v2_60_test):
    svm7, unet7 (§69.24, §69.25), near7.
T1's polygon bootstrap is also rerun exactly as score_t1_bootstrap.py ran it (1,000 resamples, seed 60) and must
give its logged interval: the per-polygon rows are then the ones T1 was scored on.

Predictions, written before the first run (each reported as held or not held; none adjusted after):
  P1  The published SVM map's accuracy interval is at least 1.5 times as wide under the block bootstrap as under
      the polygon bootstrap.
  P2  The published SVM map minus the nearest-polygon baseline (-9.4 pt accuracy, +5.4 pt balanced accuracy,
      §69.35): both intervals include 0 under the block bootstrap.
  P3  The four-class U-Net minus the published SVM map, accuracy: the block interval lies above 0.
  P4  The seven-class U-Net minus the seven-class SVM, accuracy: the block interval lies above 0.
  P5  T1 at 200 m (all bands minus no thermal, +1.36 pt, polygon interval above 0, §56): the block interval
      includes 0.
  P6  Leaving out one block moves the published SVM map's accuracy by 5 points or more for at least one block.

Also written, descriptive: per block, the held-out polygons and area by class and each map's accuracy there; each
map's accuracy with each block left out; each class's producer's accuracy with its largest polygon left out.

  "<ArcGIS Pro Python>" make_block_bootstrap.py [--plant]
--plant rolls the published map's array half a planet before the check, which must then refuse (exit 2): the check
can fail. Writes logs\block_bootstrap.json; reads the drive only (Pro may be open).
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from scipy.spatial import cKDTree
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from svmcheck import KPD, kappa, training_score
from labelsets import FOUR, SEVEN
from nearest_polygon import unit, boundary_points, Nearest
import score_t1_bootstrap as T1

MARS = arcpy.SpatialReference(104905)
NBOOT, SEED = 10000, 60
OUT = os.path.join(HERE, "logs", "block_bootstrap.json")
PLANT = "--plant" in sys.argv
G60 = r"Mars Project\Global60\%s.tif"
SETS = {
    "four": dict(names=FOUR, train="Landform_TrainingSamples_terrain_60_train",
                 test="Landform_TrainingSamples_terrain_60_test", maps=[
        ("svm4", "npy", "global60_landforms_200m_mode11_on_v2_labels_ov400.npy", "global60_landforms_svm_200m_mode11",
         "global60_classification_check_200m_mode11.json"),
        ("unet4", "npy", "global60_landforms_global60_landforms_unet_200m_seamfix_ov400.npy",
         "global60_landforms_unet_200m_seamfix", "global60_classification_check_global60_landforms_unet_200m_seamfix.json"),
        ("all200", "tif", None, "global60_landforms_svm_200m", "global60_classification_check_200m.json"),
        ("noth200", "tif", None, "global60_landforms_svm_nothermal_200m",
         "global60_classification_check_nothermal_200m.json"),
        ("near4", "near", None, None, "spatial_baseline_nearest.json")]),
    "v2": dict(names=SEVEN, train="Landform_TrainingSamples_v2_60_train",
               test="Landform_TrainingSamples_v2_60_test", maps=[
        ("svm7", "npy", "global60_landforms_v2_200m_mode11_ov400.npy", "global60_landforms_svm_v2_200m_mode11",
         "global60_classification_check_v2_200m_mode11.json"),
        ("unet7", "npy", "global60_landforms_global60_landforms_unet_v2_200m_seamfix_ov400.npy",
         "global60_landforms_unet_v2_200m_seamfix", "global60_classification_check_global60_landforms_unet_v2_200m_seamfix.json"),
        ("near7", "near", None, None, "spatial_baseline_nearest_v2.json")]),
}
PAIRS = {"four": [("svm4", "near4"), ("unet4", "svm4"), ("unet4", "near4"), ("all200", "noth200")],
         "v2": [("svm7", "near7"), ("unet7", "svm7"), ("unet7", "near7")]}


def polys(fc):
    """(class code, [ring of (lon, lat)], block) in GCS_Mars_2000, as verify_global60_classification.polys plus
    the Block field make_global60_classification.py and apply_label_review.py wrote."""
    out = []
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue", "Block"], spatial_reference=MARS) as c:
        for g, v, b in c:
            out.append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g], b))
    return out


def grid(shape):
    H, W = shape
    return dict(dpx=360.0 / W, dpy=2 * G.G100.lat_of(G.G100.oy) / H,
                lat_top=G.G100.lat_of(G.G100.oy), lon_left=G.G100.lon_of(G.G100.ox))


def load(kind, npy, tif, train):
    """The map as class indices with its valid mask and grid; the nearest baseline as a stand-in array on the
    published map's mask (the baseline's own, §69.35)."""
    if kind == "npy":
        p = os.path.join(HERE, npy)
        if os.path.getmtime(p) < os.path.getmtime(on_drive(G60 % tif)):
            sys.exit("%s is older than %s.tif: rerun verify_global60_classification.py on it first" % (npy, tif))
        a = np.load(p, mmap_mode="r")
        return a, a != 255, grid(a.shape)
    if kind == "tif":
        return T1.read(on_drive(G60 % tif))
    a = np.load(os.path.join(HERE, SETS["four"]["maps"][0][2]), mmap_mode="r")
    g = grid(a.shape)
    x, y, k = boundary_points([(v, r) for v, r, _ in polys(train)])
    return Nearest(cKDTree(unit(x, y)), k, g, a.shape), a != 255, g


def rows(a, m, g, P, n):
    """One n x n confusion per polygon (one non-zero row): the scorer's own, polygon by polygon."""
    R = np.zeros((len(P), n, n))
    for i, (v, rings, _) in enumerate(P):
        R[i], _ = training_score(a, m, g, [(v, rings)], n)
    return R


def scores(c):
    """Accuracy, kappa and balanced accuracy (the mean producer's over the classes present, as score_metrics.py)."""
    oa, kp = kappa(c)
    rs = c.sum(1); ok = rs > 0
    return oa, kp, float((np.diag(c)[ok] / rs[ok]).mean())


def ci(x):
    return [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]


def boot(units, R, keys, pairs, nboot, seed):
    """Resample the units (blocks or polygons) with replacement; every map on the same draw. R[key] holds the
    per-unit confusion sums."""
    rng = np.random.default_rng(seed)
    U = len(units)
    S = {k: np.empty((nboot, 3)) for k in keys}
    for b in range(nboot):
        w = np.bincount(rng.integers(0, U, U), minlength=U).astype(float)
        for k in keys:
            S[k][b] = scores(np.tensordot(w, R[k], 1))
    out = {k: dict(accuracy_ci95=ci(S[k][:, 0]), kappa_ci95=ci(S[k][:, 1]), balanced_ci95=ci(S[k][:, 2]),
                   accuracy_width=round(float(np.subtract(*np.percentile(S[k][:, 0], [97.5, 2.5]))), 4)) for k in keys}
    for a, b in pairs:
        d = S[a] - S[b]
        out["%s-%s" % (a, b)] = dict(accuracy_ci95=ci(d[:, 0]), balanced_ci95=ci(d[:, 2]), kappa_ci95=ci(d[:, 1]),
                                     share_above_0_accuracy=round(float((d[:, 0] > 0).mean()), 4),
                                     share_above_0_balanced=round(float((d[:, 2] > 0).mean()), 4))
    return out


def main():
    t0 = time.time()
    res = dict(script="make_block_bootstrap.py", when=time.strftime("%Y-%m-%d %H:%M"), boot=NBOOT, seed=SEED)
    for sk, S in SETS.items():
        names, n = S["names"], len(S["names"])
        P = polys(S["test"])
        blocks = sorted({b for _, _, b in P})
        R, full = {}, {}
        for key, kind, npy, tif, logname in S["maps"]:
            a, m, g = load(kind, npy, tif, S["train"])
            if PLANT and key == "svm4":
                a = np.roll(np.asarray(a), a.shape[1] // 2, axis=1); m = a != 255
            R[key] = rows(a, m, g, P, n)
            del a, m
            oa, kp, ba = scores(R[key].sum(0))
            log = json.load(open(os.path.join(HERE, "logs", logname), encoding="utf-8"))["held_out"]
            ok = abs(oa - log["accuracy"]) <= 0.001 and abs(kp - log["kappa"]) <= 0.001
            print("%-8s accuracy %.4f kappa %.4f balanced %.4f; its log %s, %s -> %s  (%.0f s)"
                  % (key, oa, kp, ba, log["accuracy"], log["kappa"], "ok" if ok else "MISMATCH", time.time() - t0))
            if not ok:
                sys.exit(2)
            full[key] = dict(accuracy=round(oa, 4), kappa=round(kp, 4), balanced=round(ba, 4))
        keys = list(R)
        hit = R[keys[0]].sum((1, 2)) > 0
        assert all(((R[k].sum((1, 2)) > 0) == hit).all() for k in keys), "maps disagree on which polygons have pixels"
        Pk = [p for p, h in zip(P, hit) if h]
        for k in keys:
            R[k] = R[k][hit]
        bi = np.array([blocks.index(b) for _, _, b in Pk])
        RB = {k: np.array([R[k][bi == j].sum(0) for j in range(len(blocks))]) for k in keys}
        out = dict(polygons=len(Pk), polygons_without_pixels=int((~hit).sum()), blocks=blocks, full=full,
                   block_bootstrap=boot(blocks, RB, keys, PAIRS[sk], NBOOT, SEED),
                   polygon_bootstrap=boot(Pk, R, keys, PAIRS[sk], NBOOT, SEED))
        # the route check: T1's own polygon bootstrap, as score_t1_bootstrap.py drew it
        if sk == "four":
            t1 = json.load(open(os.path.join(HERE, "logs", "t1_bootstrap_200m_vs_nothermal_200m.json"), encoding="utf-8"))
            rng = np.random.default_rng(T1.SEED); N = len(Pk); d = np.empty(T1.NBOOT)
            for b in range(T1.NBOOT):
                s = rng.integers(0, N, N)
                d[b] = kappa(R["noth200"][s].sum(0))[0] - kappa(R["all200"][s].sum(0))[0]   # B - A, as logged
            same = bool(np.allclose(ci(d), t1["diff_acc_ci95"], atol=1e-4))
            out["t1_route_check"] = dict(rerun_ci95=ci(d), logged_ci95=t1["diff_acc_ci95"], same=same)
            print("T1 route check, no thermal minus all bands: rerun %s, its log %s -> %s"
                  % (ci(d), t1["diff_acc_ci95"], "ok" if same else "MISMATCH"))
            if not same:
                sys.exit(3)
        # where the errors sit: per block, the area by class and each map's accuracy there
        g = grid(np.load(os.path.join(HERE, SETS["four"]["maps"][0][2]), mmap_mode="r").shape)
        px_km2 = (KPD * g["dpx"]) * (KPD * g["dpy"])                     # cos-latitude weight 1 = this many km²
        tab = []
        for j, b in enumerate(blocks):
            sel = bi == j
            ref = RB[keys[0]][j].sum(1)
            tab.append(dict(block=b, polygons=int(sel.sum()),
                            km2_by_class={nm: round(float(ref[i] * px_km2)) for i, nm in enumerate(names) if ref[i]},
                            accuracy={k: round(float(np.trace(RB[k][j]) / RB[k][j].sum()), 3) for k in keys},
                            share_of_held_out_area=round(float(ref.sum() / RB[keys[0]].sum((1, 2)).sum()), 4)))
        out["by_block"] = tab
        loo = {}
        for k in keys:
            tot = RB[k].sum(0)
            acc = [float(np.trace(tot - RB[k][j]) / (tot - RB[k][j]).sum()) for j in range(len(blocks))]
            loo[k] = dict(zip(blocks, [round(x, 4) for x in acc]))
            loo[k]["largest_move_pt"] = round(100 * max(abs(x - full[k]["accuracy"]) for x in acc), 2)
        out["leave_one_block_out_accuracy"] = loo
        cls = np.array([v - 1 for v, _, _ in Pk])
        area = R[keys[0]].sum((1, 2))
        lp = {}
        for i, nm in enumerate(names):
            idx = np.where(cls == i)[0]
            if len(idx) < 2:
                continue
            big = idx[np.argmax(area[idx])]
            d = dict(polygons=int(len(idx)), largest_share_of_class_area=round(float(area[big] / area[idx].sum()), 3),
                     largest_block=Pk[big][2])
            for k in keys:
                c, c2 = R[k][idx].sum(0), R[k][idx].sum(0) - R[k][big]
                tot = R[k].sum(0) - R[k][big]
                d[k] = dict(producers=round(float(c[i, i] / c[i].sum()), 3),
                            producers_without_largest=round(float(c2[i, i] / c2[i].sum()), 3),
                            accuracy_without_largest=round(float(np.trace(tot) / tot.sum()), 4))
            lp[nm] = d
        out["largest_polygon_left_out"] = lp
        res[sk] = out
        print("%s: %d polygons in %d blocks scored (%.0f s)" % (sk, len(Pk), len(blocks), time.time() - t0))

    f, v = res["four"], res["v2"]
    w_blk = f["block_bootstrap"]["svm4"]["accuracy_width"]; w_pol = f["polygon_bootstrap"]["svm4"]["accuracy_width"]
    inc0 = lambda x: x[0] <= 0 <= x[1]
    fb, vb = f["block_bootstrap"], v["block_bootstrap"]
    res["predictions"] = {
        "P1": dict(block_width=w_blk, polygon_width=w_pol, ratio=round(w_blk / w_pol, 2), held=bool(w_blk >= 1.5 * w_pol)),
        "P2": dict(accuracy=fb["svm4-near4"]["accuracy_ci95"], balanced=fb["svm4-near4"]["balanced_ci95"],
                   held=bool(inc0(fb["svm4-near4"]["accuracy_ci95"]) and inc0(fb["svm4-near4"]["balanced_ci95"]))),
        "P3": dict(accuracy=fb["unet4-svm4"]["accuracy_ci95"], held=bool(fb["unet4-svm4"]["accuracy_ci95"][0] > 0)),
        "P4": dict(accuracy=vb["unet7-svm7"]["accuracy_ci95"], held=bool(vb["unet7-svm7"]["accuracy_ci95"][0] > 0)),
        "P5": dict(accuracy=fb["all200-noth200"]["accuracy_ci95"], held=bool(inc0(fb["all200-noth200"]["accuracy_ci95"]))),
        "P6": dict(largest_move_pt=f["leave_one_block_out_accuracy"]["svm4"]["largest_move_pt"],
                   held=bool(f["leave_one_block_out_accuracy"]["svm4"]["largest_move_pt"] >= 5))}
    for p, d in res["predictions"].items():
        print(p, "held" if d["held"] else "NOT held", {k: x for k, x in d.items() if k != "held"})
    for sk in ("four", "v2"):
        print("\n%s, block bootstrap (polygon bootstrap):" % sk)
        for k, d in res[sk]["block_bootstrap"].items():
            pd = res[sk]["polygon_bootstrap"][k]
            print("  %-15s accuracy %s (%s)  balanced %s (%s)" % (k, d["accuracy_ci95"], pd["accuracy_ci95"],
                                                                  d["balanced_ci95"], pd["balanced_ci95"]))
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s  (%.0f s)" % (OUT, time.time() - t0))


if __name__ == "__main__":
    main()
