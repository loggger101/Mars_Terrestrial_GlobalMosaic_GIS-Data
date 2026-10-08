# -*- coding: utf-8 -*-
r"""Test T6 (H3): does the composite give more stable Iso Cluster classes than any single input? (NEXT-STEPS §4; KB §47)

H3, from the prospectus: the 4-band composite gives more stable Iso Cluster classes than any single input.

Prediction, written before the run (2026-10-08): H3 is not supported. At least one single input
(expected: Viking, resampled from 232 m and therefore smooth) is at least as stable between halves of
the window and more spatially coherent than the 5-band composite; a 1-band Iso Cluster is close to a
density slice, which reproduces easily.

Design (fixed before any classification was run):
- Inputs on the Ius grid (§18.1): Viking RGB (one input, 3 bands), day IR, night IR, the 4-band
  composite (Viking + day IR, the written plan) and the 5-band composite (+ night IR, §18.2).
- Iso Cluster as in §19: 10 classes, minimum class size 20, sample interval 10
  (IsoClusterUnsupervisedClassification, which already includes the maximum-likelihood step, §19.2).
- Three runs per input: trained on the whole window; trained on the west half; trained on the east
  half. Each half's signature is applied to the whole window with MLClassify (equal priors).
- Metrics:
  stability  = adjusted Rand index between the west- and east-trained maps over the whole window
               (1 = the same partition, about 0 = chance);
  coherence  = share of 4-neighbour pixel pairs in the same class, whole-window map;
  classes    = classes holding >= 1 % of the window, of 10 requested.
- Verdict rule: H3 supported only if the 4-band composite (the hypothesis' own input) has the
  highest stability of all five inputs and a coherence no lower than the median of the three single
  inputs. The 5-band composite is reported beside it.
- Metric check before use: ARI = 1 for a map against itself and against a relabelled copy, ~0
  against a shuffled copy.

Intermediate rasters go to %TEMP%\mars_t6 (internal disk, no spaces, §19.1). Read-only on the project.
Writes build\logs\t6_composite_stability.json.
"""
import os, sys, json, time, tempfile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
from arcpy.sa import IsoClusterUnsupervisedClassification, MLClassify

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import junction
import areas

A = dict(areas.AREAS["ius"], key="ius")
WS = junction(A["folder"])
TMP = os.path.join(tempfile.gettempdir(), "mars_t6")
OUT = os.path.join(HERE, "logs", "t6_composite_stability.json")
INPUTS = [("Viking RGB", "ius_viking.tif"), ("day IR", "ius_day.tif"), ("night IR", "ius_night.tif"),
          ("4-band composite", "ius_composite_4band.tif"), ("5-band composite", "ius_composite_5band.tif")]
SINGLE = ["Viking RGB", "day IR", "night IR"]
NCLASS, MINSIZE, INTERVAL = 10, 20, 10
t0 = time.time()


def log(msg):
    print("[%6.1fs] %s" % (time.time() - t0, msg), flush=True)


def ari(a, b):
    """Adjusted Rand index from the contingency table (Hubert & Arabie 1985)."""
    a = np.unique(a.ravel(), return_inverse=True)[1]
    b = np.unique(b.ravel(), return_inverse=True)[1]
    kb = b.max() + 1
    n = np.bincount(a * kb + b, minlength=(a.max() + 1) * kb).reshape(-1, kb).astype(float)
    c2 = lambda x: (x * (x - 1) / 2.0).sum()
    sij, sa, sb, tot = c2(n), c2(n.sum(1)), c2(n.sum(0)), c2(np.array([n.sum()]))
    expected = sa * sb / tot
    return (sij - expected) / ((sa + sb) / 2.0 - expected)


def coherence(m, ok):
    """Share of 4-neighbour pairs, both valid, that hold the same class."""
    h, v = ok[:, 1:] & ok[:, :-1], ok[1:, :] & ok[:-1, :]
    same = ((m[:, 1:] == m[:, :-1]) & h).sum() + ((m[1:, :] == m[:-1, :]) & v).sum()
    return same / float(h.sum() + v.sum())


# ------------------------------------------------------------------ the metric, checked first
rng = np.random.default_rng(20261008)
x = rng.integers(0, 10, (300, 300))
assert abs(ari(x, x) - 1) < 1e-12 and abs(ari(x, (x * 7 + 3) % 10) - 1) < 1e-12
assert abs(ari(x, rng.permutation(x.ravel()).reshape(x.shape))) < 0.01
log("ARI check: 1 against itself and a relabelled copy, ~0 against a shuffled copy")

os.makedirs(TMP, exist_ok=True)
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = TMP
arcpy.env.scratchWorkspace = TMP
xmin, ymin, xmax, ymax = A["bounds"]
W = int(round((xmax - xmin) / 100.0))
xmid = xmin + (W // 2) * 100.0
FULL = arcpy.Extent(xmin, ymin, xmax, ymax)
HALVES = {"west": arcpy.Extent(xmin, ymin, xmid, ymax), "east": arcpy.Extent(xmid, ymin, xmax, ymax)}


def arr(path):
    """The class map and its valid mask (a few edge pixels of the Viking-based inputs are no data)."""
    r = arcpy.Raster(path)
    a = arcpy.RasterToNumPyArray(path)
    assert a.shape == (int(round((ymax - ymin) / 100.0)), W), (path, a.shape)
    ok = np.ones(a.shape, bool) if r.noDataValue is None else a != r.noDataValue
    return a, ok


res = {"test": "T6", "hypothesis": "H3",
       "prediction": "H3 not supported: a single input (expected Viking) at least as stable and more coherent than the 5-band composite",
       "parameters": {"classes": NCLASS, "min_class_size": MINSIZE, "sample_interval": INTERVAL,
                      "split": "west/east halves at x = %.0f m" % xmid}, "inputs": {}}
for label, f in INPUTS:
    src = os.path.join(WS, f)
    key = os.path.splitext(f)[0]
    t = time.time()
    arcpy.env.extent = FULL
    full = os.path.join(TMP, key + "_full.tif")
    IsoClusterUnsupervisedClassification(src, NCLASS, MINSIZE, INTERVAL, os.path.join(TMP, key + "_full.gsg")).save(full)
    maps = {}
    for side, ext in HALVES.items():
        sig = os.path.join(TMP, "%s_%s.gsg" % (key, side))
        arcpy.env.extent = ext
        half = os.path.join(TMP, "%s_%s_half.tif" % (key, side))
        IsoClusterUnsupervisedClassification(src, NCLASS, MINSIZE, INTERVAL, sig).save(half)
        hw = arcpy.Raster(half).width
        assert abs(hw - W // 2) <= 1 or abs(hw - (W - W // 2)) <= 1, "extent not honoured: %d px" % hw
        arcpy.env.extent = FULL
        out = os.path.join(TMP, "%s_%s_applied.tif" % (key, side))
        MLClassify(src, sig, "0.0", "EQUAL").save(out)
        maps[side] = arr(out)
    m, mok = arr(full)
    both = maps["west"][1] & maps["east"][1]
    shares = np.bincount(np.unique(m[mok], return_inverse=True)[1]) / float(mok.sum())
    r = {"stability_ari": round(float(ari(maps["west"][0][both], maps["east"][0][both])), 4),
         "coherence": round(float(coherence(m, mok)), 4),
         "nodata_px": int((~mok).sum()),
         "classes_ge_1pct": int((shares >= 0.01).sum()),
         "classes_delivered": int(len(shares)),
         "seconds": round(time.time() - t, 1)}
    res["inputs"][label] = r
    log("%-17s stability ARI %.3f  coherence %.3f  classes >= 1 %%: %d of %d  (%.0f s)" % (
        label, r["stability_ari"], r["coherence"], r["classes_ge_1pct"], r["classes_delivered"], r["seconds"]))
arcpy.env.extent = None

I = res["inputs"]
best = max(I, key=lambda k: I[k]["stability_ari"])
med_single_coh = float(np.median([I[k]["coherence"] for k in SINGLE]))
res["most_stable"] = best
res["median_single_coherence"] = round(med_single_coh, 4)
res["h3_supported"] = bool(best == "4-band composite" and I["4-band composite"]["coherence"] >= med_single_coh)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fo:
    json.dump(res, fo, indent=1, ensure_ascii=False)
print("\nmost stable: %s; median single-input coherence %.3f; H3 supported by the rule fixed in advance: %s"
      % (best, med_single_coh, res["h3_supported"]))
log("wrote %s" % OUT)
