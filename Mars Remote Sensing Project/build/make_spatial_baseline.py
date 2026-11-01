# -*- coding: utf-8 -*-
r"""A3(a): a spatial baseline for the held-out score: each pixel takes the class of the nearest training polygon
(NEXT-STEPS §12.2 A3, KB §69.35).

The held-out polygons lie in whole 15° blocks the classifiers never saw. If the classes are arranged in provinces,
geography alone predicts much of a held-out polygon's class: this baseline uses nothing but where the training
polygons are. It is scored by the scorer's own routine (svmcheck.training_score, as verify_global60_classification.py
calls it): the same 400 m grid (the published map's first overview), the same cos-latitude weights, the same mask
(the published map's valid pixels), the same polygons. Only the "map" differs: a stand-in that, for any pixel the
scorer asks about, returns the class of the training polygon whose boundary is nearest on the sphere. Boundaries
are densified to <= 0.005° (~300 m) and searched in 3-D (scipy cKDTree on unit vectors); a pixel inside a training
polygon is never asked about, as no held-out polygon lies in a training block (the one train/test overlap of the
four-class labels, 290/291, 51.5 km², KB §68.2, is the exception and takes the nearest boundary's class).

Both label sets: the four classes (Landform_TrainingSamples_terrain_60_train / _test) and the reviewed v2 seven
(Landform_TrainingSamples_v2_60_train / _test).

Predictions, written before the first run:
  P1  four classes: the baseline scores within 10 points of the published SVM map's 73.8 % (>= 63.8 %): much of
      the SVM's held-out accuracy is reproducible from where the labels are alone.
  P2  four classes: the baseline scores more than 10 points below the two-pass U-Net's 98.9 % (< 88.9 %): the
      U-Net's score is not location alone.
  P3  seven classes: the baseline scores within 10 points of the seven-class SVM's 42.5 % (32.5-52.5 %) and below
      the seven-class U-Net's 69.0 %.
Each is reported as held or not held; none is adjusted after the run.

  "<ArcGIS Pro Python>" make_spatial_baseline.py [--null 20]
--null N instead scores N shuffles of the four-class training polygons' classes (seeds 1..N, ~105 s each), the null
for the observed baseline, -> logs\spatial_baseline_null.json. Without it,
writes logs\spatial_baseline_nearest.json and logs\spatial_baseline_nearest_v2.json, each with a "held_out" block in
the scorer's own form, so score_metrics.py reads them as it reads a map's log. Reads the drive only.
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from scipy.spatial import cKDTree
import arcpy
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from svmcheck import kappa, training_score
from labelsets import FOUR, SEVEN
from score_metrics import metrics
from nearest_polygon import STEP, unit, boundary_points, Nearest

gdal.UseExceptions()
MAP = on_drive(r"Mars Project\Global60\global60_landforms_svm_200m_mode11.tif")      # the published map: grid, mask
MARS = arcpy.SpatialReference(104905)
SETS = [("four", FOUR, "Landform_TrainingSamples_terrain_60_train", "Landform_TrainingSamples_terrain_60_test",
         "spatial_baseline_nearest.json", dict(svm=0.738, unet=0.989)),
        ("v2", SEVEN, "Landform_TrainingSamples_v2_60_train", "Landform_TrainingSamples_v2_60_test",
         "spatial_baseline_nearest_v2.json", dict(svm=0.425, unet=0.690))]


def polys(fc):
    """As verify_global60_classification.polys: (class code, [ring of (lon, lat)]) in GCS_Mars_2000."""
    out = []
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue"], spatial_reference=MARS) as c:
        for g, v in c:
            out.append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g]))
    return out


class Mask:
    """Stands in for the mask: m[rows, cols] is the published map's validity at 400 m, read by row strips."""
    def __init__(self, band):
        self.band, self.cache, self.shape = band, {}, (band.YSize, band.XSize)

    def __getitem__(self, rc):
        r, c = (np.asarray(x) for x in rc)
        r0, r1 = int(r.min()), int(r.max()) + 1
        key = (r0, r1)
        if key not in self.cache:
            self.cache = {key: self.band.ReadAsArray(0, r0, self.band.XSize, r1 - r0) > 0}
        return self.cache[key][r - r0, c]


t0 = time.time()
DS = gdal.Open(MAP)                                     # kept open: an overview band dies with its dataset
ov = DS.GetRasterBand(1).GetOverview(0)
H, W = ov.YSize, ov.XSize
g = dict(dpx=360.0 / W, dpy=2 * G.G100.lat_of(G.G100.oy) / H,
         lat_top=G.G100.lat_of(G.G100.oy), lon_left=G.G100.lon_of(G.G100.ox))            # as the scorer sets it
mask = Mask(ov.GetMaskBand())
print("grid %d x %d (400 m), lat_top %.4f, lon_left %.4f" % (W, H, g["lat_top"], g["lon_left"]))


class MapPixels(Mask):
    """The published map itself through the same stand-in route: pixel value = class code (KB §36), index code - 1."""
    def __getitem__(self, rc):
        r, c = (np.asarray(x) for x in rc)
        r0, r1 = int(r.min()), int(r.max()) + 1
        if (r0, r1) not in self.cache:
            self.cache = {(r0, r1): self.band.ReadAsArray(0, r0, self.band.XSize, r1 - r0)}
        return (self.cache[(r0, r1)][r - r0, c].astype(np.int16) - 1).clip(0, 3)


# The route checked first: the published map read through it must score what its own log says, or nothing is written.
log = json.load(open(os.path.join(HERE, "logs", "global60_classification_check_200m_mode11.json"), encoding="utf-8"))
cmx, _ = training_score(MapPixels(ov), mask, g, polys(SETS[0][3]), 4)
oa, kp = kappa(cmx)
ok = abs(oa - log["held_out"]["accuracy"]) <= 0.001 and abs(kp - log["held_out"]["kappa"]) <= 0.001
print("self-check, the published map through this route: accuracy %.4f, kappa %.4f; its log %s, %s -> %s"
      % (oa, kp, log["held_out"]["accuracy"], log["held_out"]["kappa"], "ok" if ok else "MISMATCH"))
if not ok:
    sys.exit(2)

if "--null" in sys.argv:
    # The null: the four-class training polygons' classes shuffled among them (random.Random(seed), seeds 1..N), so
    # location carries no class information; the observed baseline is read from its own log, written by a plain run.
    import random
    N = int(sys.argv[sys.argv.index("--null") + 1])
    key, names, train, test, out, ref = SETS[0]
    P0, P = polys(train), polys(test)
    obs = json.load(open(os.path.join(HERE, "logs", out), encoding="utf-8"))
    runs = []
    for seed in range(1, N + 1):
        cl = [v for v, _ in P0]
        random.Random(seed).shuffle(cl)
        x, y, k = boundary_points([(c, r) for c, (_, r) in zip(cl, P0)])
        cmx, _ = training_score(Nearest(cKDTree(unit(x, y)), k, g, (H, W)), mask, g, P, len(names))
        oa, kp = kappa(cmx)
        m = metrics({"held_out": dict(confusion_unrounded=(cmx / cmx.sum()).tolist(), producers=dict.fromkeys(names),
                                      accuracy=oa, kappa=kp, polygons=len(P))})
        runs.append(dict(seed=seed, accuracy=round(float(oa), 4), kappa=round(float(kp), 4),
                         balanced_accuracy=float(m["balanced_accuracy"])))
        print("seed %2d: accuracy %.4f, kappa %.4f, balanced %.4f (%.0f s)" % (seed, oa, kp, m["balanced_accuracy"],
                                                                            time.time() - t0))
    o = dict(accuracy=obs["held_out"]["accuracy"], balanced_accuracy=obs["beyond_accuracy"]["balanced_accuracy"])
    summary = {s: dict(median=float(np.median([r[s] for r in runs])), min=min(r[s] for r in runs),
                       max=max(r[s] for r in runs), at_or_above_observed=int(sum(r[s] >= o[s] for r in runs)))
               for s in ("accuracy", "balanced_accuracy")}
    summary["accuracy"]["at_or_above_published_svm_0.738"] = int(sum(r["accuracy"] >= 0.738 for r in runs))
    with open(os.path.join(HERE, "logs", "spatial_baseline_null.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(script="make_spatial_baseline.py --null %d" % N, when=time.strftime("%Y-%m-%d %H:%M"),
                       null="the four-class training polygons' classes shuffled among them", observed=o,
                       summary=summary, runs=runs), fh, indent=1, ensure_ascii=False)
    print("observed", o, "\nnull", summary, "\nwrote logs\\spatial_baseline_null.json")
    sys.exit(0)

results = {}
for key, names, train, test, out, ref in SETS:
    K = len(names)
    x, y, k = boundary_points(polys(train))
    tree = cKDTree(unit(x, y))
    P = polys(test)
    cmx, own = training_score(Nearest(tree, k, g, (H, W)), mask, g, P, K)
    oa, kp = kappa(cmx)
    prod = (np.diag(cmx) / np.maximum(cmx.sum(1), 1e-12)).round(3).tolist()
    user = (np.diag(cmx) / np.maximum(cmx.sum(0), 1e-12)).round(3).tolist()
    maj = ["%d/%d" % (sum(1 for c, f in own if c == i and f > .5), sum(1 for c, f in own if c == i)) for i in range(K)]
    held_out = dict(polygons=len(P), accuracy=round(oa, 3), kappa=round(kp, 3),
                    one_class_everywhere=round(cmx.sum(1).max() / cmx.sum(), 3),
                    label_area_share=dict(zip(names, (cmx.sum(1) / cmx.sum()).round(4).tolist())),
                    confusion_unrounded=(cmx / cmx.sum()).tolist(),
                    producers=dict(zip(names, prod)), users=dict(zip(names, user)),
                    polygons_majority_own_class=dict(zip(names, maj)),
                    confusion_area_weighted=(cmx / cmx.sum()).round(4).tolist())
    m = metrics({"held_out": held_out})
    res = dict(script="make_spatial_baseline.py", when=time.strftime("%Y-%m-%d %H:%M"),
               baseline="nearest training polygon (boundary, on the sphere)", labels=dict(training_set=train, held_out=test),
               boundary_points=int(len(x)), step_deg=STEP, held_out=held_out,
               beyond_accuracy={kk: m[kk] for kk in ("balanced_accuracy", "macro_f1", "quantity_disagreement",
                                                     "allocation_disagreement")},
               compared_with=ref)
    results[key] = res
    print("%-5s %d training polygons -> %d boundary points; %d held out: accuracy %.4f, kappa %.4f, balanced %.4f, "
          "macro F1 %.4f (%.0f s)" % (key, len(polys(train)), len(x), len(P), oa, kp, m["balanced_accuracy"],
                                      m["macro_f1"], time.time() - t0))
    print("      producer's", dict(zip(names, prod)))

f, s = results["four"]["held_out"]["accuracy"], results["v2"]["held_out"]["accuracy"]
pred = {
    "P1": dict(rule="four classes: >= 0.638 (within 10 pt of the SVM's 0.738)", accuracy=f, held=bool(f >= 0.638)),
    "P2": dict(rule="four classes: < 0.889 (more than 10 pt below the U-Net's 0.989)", accuracy=f, held=bool(f < 0.889)),
    "P3": dict(rule="seven classes: 0.325-0.525 (within 10 pt of the SVM's 0.425) and below the U-Net's 0.690",
               accuracy=s, held=bool(0.325 <= s <= 0.525 and s < 0.690)),
}
for key, *_, out, ref in SETS:
    results[key]["predictions"] = pred
    with open(os.path.join(HERE, "logs", out), "w", encoding="utf-8") as fh:
        json.dump(results[key], fh, indent=1, ensure_ascii=False)
for k_, v in pred.items():
    print("%s %-9s %s: %.3f" % (k_, "HELD" if v["held"] else "NOT HELD", v["rule"], v["accuracy"]))
print("wrote logs\\spatial_baseline_nearest.json, logs\\spatial_baseline_nearest_v2.json (%.0f s)" % (time.time() - t0))
