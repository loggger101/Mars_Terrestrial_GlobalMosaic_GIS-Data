# -*- coding: utf-8 -*-
r"""Why the support vector machine did not rise on the third label set: the sample cap, the labels, or the pixels.

The U-Net rose from 69.0 % to 87.6 % on the 237 v2 held-out polygons when trained on the third label set; the support
vector machine went from 42.5 % to 39.1 % (KB §69.81). Pro's TrainSupportVectorMachineClassifier draws at most 1,000
pixels per class (max_samples_per_class=1000, make_global60_classification.py), so 14 times more polygons change which
pixels it trains on, not how many. Three readings are open: the cap holds it back; the third set's labels are no better
for a per-pixel classifier; or seven bands of one pixel cannot separate these classes whatever the labels and sample.

Pro's SVM cannot be rerun at another cap without a multi-hour global classification. This uses a stand-in instead: a
scikit-learn SVM (RBF kernel, features standardised) trained on random pixels of the same 200 m stack inside each label
set's training polygons, and scored at random points inside the held-out polygons, the same points for every model.
Pro's own raw maps are read at the same points, so the stand-in is checked against what it stands for.

  Training points: per label set, the training polygons dissolved by class, CreateRandomPoints, 10,000 per class
     (uniform in degrees, as the stack's pixels are), the draws below taken from them.
  Test points: per held-out set, points in each polygon in proportion to its area in degrees (as the scorer counts
     400 m cells), 30,000 in all, at least one per polygon. Scored pixel by pixel; intervals resample the 14 blocks.
  Points where any stack band is 0 (the stack's NoData) or Pro's map is 255 are dropped and counted.

Written 2026-11-10 while fresh2's SVM trains, before any of it ran. Nothing below is adjusted after the run.

**Predictions** (each reported held or not held):
  Q0  Sampling: Pro's raw svm_v2 map at the v2 test points and raw svm_v3 at the v3 test points score within 2.5 points
      of their logged raw accuracy at 400 m, 42.4 % and 37.4 % (logs\mode_curve.json, mode_curve_v3.json).
  Q1  Stand-in: at 1,000 per class the stand-in repeats Pro's direction on the 237 v2 polygons: its v3-label accuracy is
      no more than 2 points above its v2-label accuracy (Pro: 42.5 -> 39.1 % at 11 px; "42.4" here first, a typo
      corrected 11-10 while the run ran, no threshold changed), and each is within 8 points of
      Pro's raw map at the same points. Not held -> the rest is read as about a per-pixel SVM, not about Pro's.
  Q2  The cap: on the v3 labels, 10,000 per class scores within 3 points of 1,000 per class on the 237 v2 polygons.
  Q3  The labels: at 10,000 per class, the v3 labels score no more than 3 points above the v2 labels on the 237 polygons.
  Reading rule: Q2 and Q3 held -> neither the cap nor the labels hold the SVM back; the seven bands of one pixel do.
  Q2 not held, the larger sample higher -> the cap holds it back on the third label set.

Writes C:\MarsScratch\svm_cap\pts.gdb (points and samples; the project gdb is read only) and logs\svm_label_cap.json.

  "<ArcGIS Pro Python>" check_svm_label_cap.py            (about 30-60 min; --plant shuffles the test labels: Q0-Q3's
                                                           scores must fall to chance, proving the scorer can fail)

--pairs (added 2026-11-10 while the main run ran, a description, not a test): from the training samples the main run
wrote, how well each pair of classes is told apart by one pixel's seven bands under each label set: 2,000 pixels a
class, a k-nearest-neighbour classifier (k = 15, bands standardised), 5-fold cross-validated two-class accuracy, 0.5
being no separation. Writes logs\svm_label_cap_pairs.json.
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import arcpy
import grid60 as G
from paths import GDB as PROJECT_GDB
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

PLANT = "--plant" in sys.argv
GDB_DIR = r"C:\MarsScratch\svm_cap"
GDB = os.path.join(GDB_DIR, "pts.gdb")
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
PRO = {"v2": os.path.join(G.OUTDIR, "global60_landforms_svm_v2_200m.tif"),
       "v3": os.path.join(G.OUTDIR, "global60_landforms_svm_v3_200m.tif")}
PRO_MODE11_V2SET = {"v2": 0.425, "v3": 0.391}      # Pro's published maps on the 237 polygons (§69.81), for the record
LOGGED_RAW = {"v2": 0.424, "v3": 0.3737}           # Q0: raw svm_v2 on v2_test, raw svm_v3 on v3_test
PER_CLASS = 10000
N_TEST = 30000
SIZES = [(1000, 0), (1000, 1), (1000, 2), (3000, 0), (10000, 0)]
SEVEN = 7
FC = lambda ls, part: os.path.join(PROJECT_GDB, "Landform_TrainingSamples_%s_60_%s" % (ls, part))
arcpy.env.overwriteOutput = True
arcpy.env.randomGenerator = "61 ACM599"            # CreateRandomPoints repeatable from run to run


def setup():
    os.makedirs(GDB_DIR, exist_ok=True)
    if not arcpy.Exists(GDB):
        arcpy.management.CreateFileGDB(GDB_DIR, "pts.gdb")


def train_points(ls):
    d = os.path.join(GDB, "train_%s_dis" % ls)
    arcpy.management.Dissolve(FC(ls, "train"), d, "Classvalue")
    p = os.path.join(GDB, "train_%s_pts" % ls)
    arcpy.management.CreateRandomPoints(GDB, "train_%s_pts" % ls, d, number_of_points_or_field=PER_CLASS)
    cls = {o: v for o, v in arcpy.da.SearchCursor(d, ["OID@", "Classvalue"])}
    return p, cls


def test_points(ls):
    c = os.path.join(GDB, "test_%s" % ls)
    arcpy.management.CopyFeatures(FC(ls, "test"), c)
    rows = [(o, a) for o, a in arcpy.da.SearchCursor(c, ["OID@", "SHAPE@AREA"])]
    tot = sum(a for _, a in rows)
    arcpy.management.AddField(c, "NPTS", "LONG")
    with arcpy.da.UpdateCursor(c, ["SHAPE@AREA", "NPTS"]) as u:
        for a, _ in u:
            u.updateRow([a, max(1, int(round(N_TEST * a / tot)))])
    arcpy.management.CreateRandomPoints(GDB, "test_%s_pts" % ls, c, number_of_points_or_field="NPTS")
    meta = {o: (v, b) for o, v, b in arcpy.da.SearchCursor(c, ["OID@", "Classvalue", "Block"])}
    return os.path.join(GDB, "test_%s_pts" % ls), meta


def sample(points, rasters, name):
    """Values of every raster band at each point (nearest pixel), keyed by the point's CID."""
    t = os.path.join(GDB, name)
    arcpy.sa.Sample(rasters, points, t, "NEAREST", unique_id_field=arcpy.Describe(points).OIDFieldName)
    f = [x.name for x in arcpy.ListFields(t)]
    loc = f[1]                                   # the point's OBJECTID, as the tool names it
    vals = [x for x in f[2:] if x.upper() not in ("X", "Y")]
    cid = {o: c for o, c in arcpy.da.SearchCursor(points, ["OID@", "CID"])}
    out = [(cid[r[0]],) + tuple(r[1:]) for r in arcpy.da.SearchCursor(t, [loc] + vals)]
    return vals, np.array(out, dtype=np.float64)


def scores(y, p, w=None):
    c = np.zeros((SEVEN, SEVEN))
    np.add.at(c, (y - 1, p - 1), 1)
    rs = c.sum(1); ok = rs > 0
    return float(np.trace(c) / c.sum()), float((np.diag(c)[ok] / rs[ok]).mean())


def block_ci(y, preds, blocks, pairs, nboot=2000, seed=1):
    """95 % intervals of a - b accuracy and balanced accuracy, resampling the 14 blocks, every model on one draw."""
    ub = sorted(set(blocks)); idx = {b: np.where(blocks == b)[0] for b in ub}
    rng = np.random.default_rng(seed); D = {p: [] for p in pairs}
    for _ in range(nboot):
        pick = np.concatenate([idx[ub[i]] for i in rng.integers(0, len(ub), len(ub))])
        for a, b in pairs:
            sa, sb = scores(y[pick], preds[a][pick]), scores(y[pick], preds[b][pick])
            D[(a, b)].append((sa[0] - sb[0], sa[1] - sb[1]))
    return {"%s - %s" % p: dict(accuracy_ci95=[round(float(v), 4) for v in np.percentile(np.array(d)[:, 0], [2.5, 97.5])],
                                balanced_ci95=[round(float(v), 4) for v in np.percentile(np.array(d)[:, 1], [2.5, 97.5])])
            for p, d in D.items()}


def main():
    global BIG, SMALL
    SMALL, BIG = "sk_%%s_%d_s0" % SIZES[0][0], "sk_%%s_%d_s0" % SIZES[-1][0]   # Q2/Q3's two sample sizes
    t0 = time.time()
    setup()
    arcpy.CheckOutExtension("Spatial")
    res = dict(script="check_svm_label_cap.py", plant=PLANT, per_class_drawn=PER_CLASS, n_test=N_TEST, sizes=SIZES)
    X, Y = {}, {}
    for ls in ("v2", "v3"):
        p, cls = train_points(ls)
        bands, a = sample(p, [STACK], "train_%s_s" % ls)
        keep = (a[:, 1:] > 0).all(1)
        res["train_%s_dropped" % ls] = int((~keep).sum())
        X[ls], Y[ls] = a[keep, 1:], np.array([cls[int(c)] for c in a[keep, 0]])
        res["train_%s_per_class" % ls] = {int(k): int(n) for k, n in zip(*np.unique(Y[ls], return_counts=True))}
        print(ls, "train", res["train_%s_per_class" % ls], "dropped", res["train_%s_dropped" % ls], flush=True)
    res["test"], T = {}, {}
    for ts in ("v2", "v3"):
        p, meta = test_points(ts)
        bands, a = sample(p, [STACK, PRO["v2"], PRO["v3"]], "test_%s_s" % ts)
        stack = a[:, 1:8]                                         # NoData comes back as NaN: NaN > 0 is False
        pro2, pro3 = (np.nan_to_num(a[:, j], nan=255).astype(int) for j in (8, 9))
        assert set(np.unique(pro2)) | set(np.unique(pro3)) <= set(range(1, SEVEN + 1)) | {255}
        keep = (stack > 0).all(1) & (pro2 != 255) & (pro3 != 255)
        y = np.array([meta[int(c)][0] for c in a[:, 0]])[keep]
        blocks = np.array([meta[int(c)][1] for c in a[:, 0]])[keep]
        if PLANT:
            y = np.random.default_rng(7).permutation(y)
        T[ts] = dict(x=stack[keep], y=y, blocks=blocks, dropped=int((~keep).sum()),
                     preds={"pro_svm_v2": pro2[keep], "pro_svm_v3": pro3[keep]})
    for ls in ("v2", "v3"):                                       # each stand-in fitted once, both sets predicted
        for n, seed in SIZES:
            rng = np.random.default_rng(100 + seed)
            pick = np.concatenate([rng.choice(np.where(Y[ls] == k)[0], min(n, (Y[ls] == k).sum()), replace=False)
                                   for k in range(1, SEVEN + 1)])
            m = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1.0, gamma="scale", cache_size=2000))
            t1 = time.time(); m.fit(X[ls][pick], Y[ls][pick])
            for ts in T:
                T[ts]["preds"]["sk_%s_%d_s%d" % (ls, n, seed)] = m.predict(T[ts]["x"]).astype(int)
            print("  %s labels, %d per class, seed %d: %d support vectors, %.0f s" % (
                ls, n, seed, m[-1].n_support_.sum(), time.time() - t1), flush=True)
    for ts, t in T.items():
        y, preds = t["y"], t["preds"]
        r = dict(points=int(len(y)), dropped=t["dropped"], blocks=len(set(t["blocks"])),
                 scores={k: dict(zip(("accuracy", "balanced"), [round(v, 4) for v in scores(y, p_)])) for k, p_ in preds.items()})
        pairs = [(BIG % "v3", SMALL % "v3"), (BIG % "v3", BIG % "v2"), (SMALL % "v3", SMALL % "v2"), ("pro_svm_v3", "pro_svm_v2")]
        r["block_bootstrap"] = block_ci(y, preds, t["blocks"], pairs)
        res["test"][ts] = r
        for k, s_ in r["scores"].items():
            print("  %s %-18s %s" % (ts, k, s_), flush=True)
    s2 = {k: v["accuracy"] for k, v in res["test"]["v2"]["scores"].items()}
    s3 = {k: v["accuracy"] for k, v in res["test"]["v3"]["scores"].items()}
    small = SIZES[0][0]
    sk1 = lambda ls: np.mean([s2["sk_%s_%d_s%d" % (ls, n, i)] for n, i in SIZES if n == small])
    v = {}
    v["Q0"] = abs(s2["pro_svm_v2"] - LOGGED_RAW["v2"]) <= 0.025 and abs(s3["pro_svm_v3"] - LOGGED_RAW["v3"]) <= 0.025
    v["Q1"] = (sk1("v3") - sk1("v2") <= 0.02 and abs(sk1("v2") - s2["pro_svm_v2"]) <= 0.08
               and abs(sk1("v3") - s2["pro_svm_v3"]) <= 0.08)
    v["Q2"] = abs(s2[BIG % "v3"] - s2[SMALL % "v3"]) <= 0.03
    v["Q3"] = s2[BIG % "v3"] - s2[BIG % "v2"] <= 0.03
    res["predictions"] = {k: "held" if x else "NOT held" for k, x in v.items()}
    res["stand_in_1000_mean_of_3"] = {ls: round(float(sk1(ls)), 4) for ls in ("v2", "v3")}
    res["seconds"] = round(time.time() - t0)
    print(res["predictions"], res["stand_in_1000_mean_of_3"])
    out = os.path.join(HERE, "logs", "svm_label_cap%s.json" % ("_plant" if PLANT else ""))
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print("->", out)


def pairs():
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import cross_val_score
    names = ["Crater", "Hills", "Lava tube", "Normal Ground", "Volcanic edifice", "Apron", "Fluvial channel"]  # values 1-7
    res = dict(script="check_svm_label_cap.py --pairs", per_class=2000, k=15, folds=5, classes=names, sets={})
    for ls in ("v2", "v3"):
        t = os.path.join(GDB, "train_%s_s" % ls)
        p = os.path.join(GDB, "train_%s_pts" % ls)
        cls = {o: v for o, v in arcpy.da.SearchCursor(os.path.join(GDB, "train_%s_dis" % ls), ["OID@", "Classvalue"])}
        cid = {o: c for o, c in arcpy.da.SearchCursor(p, ["OID@", "CID"])}
        f = [x.name for x in arcpy.ListFields(t)]
        vals = [x for x in f[2:] if x.upper() not in ("X", "Y")]
        a = np.array([(cls[cid[r[0]]],) + tuple(r[1:]) for r in arcpy.da.SearchCursor(t, [f[1]] + vals)], dtype=np.float64)
        a = a[(a[:, 1:] > 0).all(1)]
        rng = np.random.default_rng(5)
        S = {k: a[rng.choice(np.where(a[:, 0] == k)[0], 2000, replace=False), 1:] for k in range(1, SEVEN + 1)}
        M = np.full((SEVEN, SEVEN), np.nan)
        for i in range(1, SEVEN + 1):
            for j in range(i + 1, SEVEN + 1):
                x = np.vstack([S[i], S[j]]); y = np.r_[np.zeros(2000), np.ones(2000)]
                m = make_pipeline(StandardScaler(), KNeighborsClassifier(15))
                M[i - 1, j - 1] = M[j - 1, i - 1] = cross_val_score(m, x, y, cv=5).mean()
        res["sets"][ls] = dict(pair_accuracy=[[None if np.isnan(v) else round(float(v), 3) for v in r] for r in M],
                               median_band={names[k - 1]: [float(v) for v in np.median(S[k], 0)] for k in S},
                               bands=[v.replace("global60_svm_stack_200m_", "") for v in vals])
        print(ls, "\n" + "\n".join("%-17s " % names[i] + " ".join("  -  " if np.isnan(v) else "%.3f" % v for v in M[i])
                                   for i in range(SEVEN)), flush=True)
    d = np.array(res["sets"]["v3"]["pair_accuracy"], dtype=float) - np.array(res["sets"]["v2"]["pair_accuracy"], dtype=float)
    res["v3_minus_v2"] = [[None if np.isnan(v) else round(float(v), 3) for v in r] for r in d]
    out = os.path.join(HERE, "logs", "svm_label_cap_pairs.json")
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("v3 - v2:\n" + "\n".join("%-17s " % names[i] + " ".join("  -   " if np.isnan(v) else "%+.3f" % v for v in d[i])
                                  for i in range(SEVEN)))
    print("->", out)


if __name__ == "__main__":
    pairs() if "--pairs" in sys.argv else main()
