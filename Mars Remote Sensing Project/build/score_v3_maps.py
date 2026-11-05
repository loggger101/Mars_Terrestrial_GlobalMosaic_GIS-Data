# -*- coding: utf-8 -*-
r"""Do the v3 maps improve on the v2 ones? Block intervals, a recommendation rule and predictions (NEXT-STEPS row 3b).

run_v3.ps1 scores each map once, on each held-out set, with no interval and no verdict. This script reads the cached
400 m class arrays those steps write and scores every map polygon by polygon with the scorer's own routine
(make_block_bootstrap.py's, svmcheck.training_score), on both held-out sets, then resamples the 14 held-out blocks
(10,000 times, seed 60), every map paired on the same draw.

Maps: svm_v2, unet_v2 (KB §69.24, §69.25), svm_v3, unet_v3 (run_v3.ps1), near_v2 and near_v3, the nearest training
polygon of each label set (§69.35). Sets: Landform_TrainingSamples_v2_60_test (237, the like-for-like score, KB §69.49)
and Landform_TrainingSamples_v3_60_test (1,652, 85 % of it the same ground, §69.57).

Written 2026-11-05 ~14:00, with the U-Net on epoch 26 of 30: no v3 map exists and no held-out v3 score has been read.
Only the training run's validation table had been seen (chips from the training blocks, accuracy ~0.87, not a held-out
score). Nothing below is adjusted after the run.

**The recommendation** (the agent's, for the author, who picks: row 3b; D28 shows the pick is the author's whatever
this says). For each model, the v3 map is recommended over its v2 map only if:
  (a) on the v2 held-out polygons, its balanced accuracy and its kappa are each at least the v2 map's;
  (b) on the v3 held-out polygons, the same;
  (c) on the v2 held-out polygons no class loses 5 points or more of producer's accuracy;
  (d) U-Net only: volcanic edifice covers no more of ±60° than the v2 U-Net's 40.0 %, its known over-prediction
      (§69.25, §69.37).
Balanced accuracy leads because that is where the paper's gains and losses have been read since D25, D29 and D31.
Overall accuracy and the block intervals are reported beside the rule, not part of it: 14 blocks rarely resolve a
small difference (§69.44), so a recommendation may rest on a difference the intervals do not resolve, and the record
says which.

**Predictions** (each reported held or not held):
  P1  unet_v3's balanced accuracy on the v2 polygons is above unet_v2's 56.9 %: hills and lava tube train in far more
      blocks (150 and 11 against 2 and 3).
  P2  unet_v3's accuracy on the v2 polygons lies in 60-78 % (unet_v2 69.0 %).
  P3  svm_v3's accuracy on the v2 polygons lies in 37.5-50 % (svm_v2 42.5 %): the pixel classifier gains little from
      more polygons of the same stack.
  P4  Hills' producer's accuracy on the v2 polygons rises on both models (svm_v2 50.3 %, unet_v2 46.8 %).
  P5  unet_v3 maps edifice on under 40.0 % of ±60°: Normal Ground and hills now train in 178 and 150 blocks.
  P6  unet_v3 minus unet_v2 on the v2 polygons, block bootstrap: the accuracy and balanced intervals both include 0.
  P7  svm_v3 minus near_v3 on the v3 polygons, accuracy, block bootstrap: the interval includes 0, as on v2 (§69.57).
  P8  unet_v3 minus svm_v3, balanced accuracy, block bootstrap: above 0 on the v2 polygons, includes 0 on the v3 ones,
      the pattern of the v2 maps (§69.57).
  P9  On the 218 new polygons both v3 maps beat their v2 maps (svm_v2 30.3 %, unet_v2 36.1 %): such polygons are now
      in training.

**Limits, for whatever is reported:** the 14 blocks are used a third time (four classes, v2, v3), and v3's labels were
requested after the v2 scores were read (§69.49), so a gain here is not a fresh test. v3's held-out Crater discs come
from the Robbins catalogue, so that class partly measures agreement with it (§69.49).

Route check: every map must give the accuracy and kappa of its own scorer log within 0.001, or nothing is written
(exit 2). --rehearse stands the v2 arrays in for the v3 maps and checks the v2 maps on the v3 polygons against A16's
log instead, so the whole route can run before the v3 maps exist: every v3-minus-v2 difference must then be exactly 0,
and the rule's clauses must each fail on fabricated worse inputs. --plant (with --rehearse) rolls the stand-in unet_v3
half a planet, and the route check must refuse.

  "<ArcGIS Pro Python>" score_v3_maps.py [--rehearse [--plant]]
Writes logs\v3_maps.json (--rehearse: logs\v3_maps_rehearsal.json). Reads the drive only (Pro may be open); ~30 min.
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_block_bootstrap as B
import score_v2maps_on_v3 as V
from labelsets import SEVEN

REHEARSE, PLANT = "--rehearse" in sys.argv, "--plant" in sys.argv
OUT = os.path.join(HERE, "logs", "v3_maps_rehearsal.json" if REHEARSE else "v3_maps.json")
V2_TRAIN, V2_TEST = B.SETS["v2"]["train"], B.SETS["v2"]["test"]
V3_TRAIN = "Landform_TrainingSamples_v3_60_train"
HILLS, EDIFICE = "steep/windy hills", "volcanic edifice"
DROP = 0.05                                    # (c): a fall of 5 points or more fails, as D18's (c)
EDIFICE_V2 = 0.40                              # (d) and P5: unet_v2's share of ±60° (§69.25)
PAIRS = [("unet_v3", "unet_v2"), ("svm_v3", "svm_v2"), ("unet_v3", "svm_v3"), ("svm_v3", "near_v3"),
         ("unet_v3", "near_v3")]

# key: (kind, cached array, raster, training set, scorer log on the v2 polygons, on the v3 polygons)
SVM2 = ("npy", "global60_landforms_v2_200m_mode11_ov400.npy", "global60_landforms_svm_v2_200m_mode11", V2_TRAIN,
        "v2_200m_mode11", "v2_200m_mode11_on_v3_labels")
UNET2 = ("npy", "global60_landforms_global60_landforms_unet_v2_200m_seamfix_ov400.npy",
         "global60_landforms_unet_v2_200m_seamfix", V2_TRAIN, "global60_landforms_unet_v2_200m_seamfix",
         "global60_landforms_unet_v2_200m_seamfix_on_v3_labels")
SVM3 = ("npy", "global60_landforms_v3_200m_mode11_ov400.npy", "global60_landforms_svm_v3_200m_mode11", V3_TRAIN,
        "v3_200m_mode11_on_v2_labels", "v3_200m_mode11")
UNET3 = ("npy", "global60_landforms_global60_landforms_unet_v3_200m_seamfix_ov400.npy",
         "global60_landforms_unet_v3_200m_seamfix", V3_TRAIN, "global60_landforms_unet_v3_200m_seamfix_on_v2_labels",
         "global60_landforms_unet_v3_200m_seamfix")
MAPS = {"svm_v2": SVM2, "unet_v2": UNET2, "svm_v3": SVM2 if REHEARSE else SVM3, "unet_v3": UNET2 if REHEARSE else UNET3,
        "near_v2": ("near", None, None, V2_TRAIN, None, None), "near_v3": ("near", None, None, V3_TRAIN, None, None)}


def logged(name):
    return json.load(open(os.path.join(HERE, "logs", "global60_classification_check_%s.json" % name), encoding="utf-8"))


def route(key, label, oa, kp, want):
    """The map must give its own log's accuracy and kappa; want = (accuracy, kappa) or None where no log exists."""
    if want is None:
        print("%-8s on %s: accuracy %.4f kappa %.4f (no log to check)" % (key, label, oa, kp))
        return
    ok = abs(oa - want[0]) <= 0.001 and abs(kp - want[1]) <= 0.001
    print("%-8s on %s: accuracy %.4f kappa %.4f; its log %s -> %s" % (key, label, oa, kp, want, "ok" if ok else "MISMATCH"))
    if not ok:
        sys.exit(2)


def wanted(key, name, set_key, a16):
    """What a map's log says it scored on one set. near_v2's log is the baseline's own; the rehearsal has no scorer log
    of a v2 map on the v3 polygons yet, so A16's stands in."""
    if key == "near_v2" and set_key == "v2":
        h = json.load(open(os.path.join(HERE, "logs", "spatial_baseline_nearest_v2.json"), encoding="utf-8"))["held_out"]
        return h["accuracy"], h["kappa"]
    if name is None:
        return None
    if REHEARSE and set_key == "v3":
        h = a16[{"svm": "svm7", "unet": "unet7"}[key.split("_")[0]]]
        return h["accuracy"], h["kappa"]
    h = logged(name)["held_out"]
    return h["accuracy"], h["kappa"]


def rule(model, on_v2, on_v3, prod_v3, prod_v2, edifice_share):
    """The recommendation above for one model. on_v2, on_v3: {"v3": full, "v2": full}; prod_*: producer's on the v2
    polygons by class; edifice_share: the v3 map's, or None for the SVM, which (d) does not test."""
    def at_least(s):
        return bool(s["v3"]["balanced"] >= s["v2"]["balanced"] and s["v3"]["kappa"] >= s["v2"]["kappa"])   # numpy's bool is no JSON
    falls = {c: round(prod_v2[c] - prod_v3[c], 4) for c in SEVEN if prod_v2[c] is not None and prod_v3[c] is not None}
    rec = dict(a_on_v2_polygons=at_least(on_v2), b_on_v3_polygons=at_least(on_v3), c_falls=falls,
               c_no_class_falls_5pt=all(f < DROP for f in falls.values()))
    rec["d_edifice_share"] = edifice_share
    rec["d_ok"] = True if edifice_share is None else edifice_share <= EDIFICE_V2
    rec["recommended"] = all((rec["a_on_v2_polygons"], rec["b_on_v3_polygons"], rec["c_no_class_falls_5pt"], rec["d_ok"]))
    return rec


def rule_can_fail(s, p):
    """Each clause must fail on fabricated worse inputs (HANDOFF §3: prove a check can fail)."""
    worse = dict(s, balanced=s["balanced"] - 0.001)
    on = dict(v3=s, v2=s)
    bad = dict(v3=worse, v2=s)
    fall = dict(p, **{HILLS: p[HILLS] - DROP})
    tests = {"(a)": rule("t", bad, on, p, p, None), "(b)": rule("t", on, bad, p, p, None),
             "(c)": rule("t", on, on, fall, p, None), "(d)": rule("t", on, on, p, p, EDIFICE_V2 + 0.001)}
    assert rule("t", on, on, p, p, EDIFICE_V2)["recommended"], "the rule refuses equal inputs"
    assert not any(t["recommended"] for t in tests.values()), "a clause of the rule cannot fail"
    print("the rule: equal inputs pass; (a), (b), (c), (d) each fail on a fabricated worse input")


def judge(res):
    f2, f3 = res["v2_polygons"]["full"], res["v3_polygons"]["full"]
    b2, b3 = res["v2_polygons"]["block_bootstrap"], res["v3_polygons"]["block_bootstrap"]
    new = res["v3_polygons"].get("by_origin", {}).get("new")
    has0 = lambda ci: ci[0] <= 0 <= ci[1]
    d = b2["unet_v3-unet_v2"]
    u = (b2["unet_v3-svm_v3"]["balanced_ci95"], b3["unet_v3-svm_v3"]["balanced_ci95"])
    v = {"P1": f2["unet_v3"]["balanced"] > f2["unet_v2"]["balanced"],
         "P2": 0.60 <= f2["unet_v3"]["accuracy"] <= 0.78,
         "P3": 0.375 <= f2["svm_v3"]["accuracy"] <= 0.50,
         "P4": all(f2[m + "_v3"]["producers"][HILLS] > f2[m + "_v2"]["producers"][HILLS] for m in ("svm", "unet")),
         "P5": res["edifice_share"]["unet_v3"] < EDIFICE_V2,
         "P6": has0(d["accuracy_ci95"]) and has0(d["balanced_ci95"]),
         "P7": has0(b3["svm_v3-near_v3"]["accuracy_ci95"]),
         "P8": u[0][0] > 0 and has0(u[1]),
         "P9": bool(new) and all(new[m + "_v3"]["accuracy"] > new[m + "_v2"]["accuracy"] for m in ("svm", "unet"))}
    return {p: "held" if x else "NOT held" for p, x in v.items()}


def main():
    t0 = time.time()
    sets = {"v2": B.polys(V2_TEST)}
    P3, A3 = V.v3_polys()
    sets["v3"] = P3
    a16 = json.load(open(os.path.join(HERE, "logs", "v2maps_on_v3.json"), encoding="utf-8"))["full"]
    n = len(SEVEN)
    R = {"v2": {}, "v3": {}}
    for key, (kind, npy, tif, train, log2, log3) in MAPS.items():
        a, m, g = B.load(kind, npy, tif, train)
        if PLANT and key == "unet_v3":
            a = np.roll(np.asarray(a), a.shape[1] // 2, axis=1); m = a != 255
        for sk, log in (("v2", log2), ("v3", log3)):
            R[sk][key] = B.rows(a, m, g, sets[sk], n)
            oa, kp, _ = B.scores(R[sk][key].sum(0))
            route(key, sk + " held out", oa, kp, wanted(key, log, sk, a16))
        del a, m
        print("  (%.0f s)" % (time.time() - t0))

    res = dict(script="score_v3_maps.py", when=time.strftime("%Y-%m-%d %H:%M"), rehearsal=REHEARSE, boot=B.NBOOT,
               seed=B.SEED, classes=SEVEN,
               edifice_share={k: logged(MAPS[k][5] if not REHEARSE else MAPS[k][4])["share_area_weighted"][EDIFICE]
                              for k in ("svm_v3", "unet_v3", "svm_v2", "unet_v2")})
    keys = list(MAPS)
    for sk, P in sets.items():
        hit = np.all([R[sk][k].sum((1, 2)) > 0 for k in keys], axis=0)    # polygons every map has pixels on
        Pk = [p for p, h in zip(P, hit) if h]
        Rk = {k: R[sk][k][hit] for k in keys}
        blocks = sorted({b for _, _, b in Pk})
        bi = np.array([blocks.index(b) for _, _, b in Pk])
        RB = {k: np.array([Rk[k][bi == j].sum(0) for j in range(len(blocks))]) for k in keys}
        full = {}
        for k in keys:
            c = Rk[k].sum(0)
            oa, kp, ba = B.scores(c)
            full[k] = dict(accuracy=round(oa, 4), kappa=round(kp, 4), balanced=round(ba, 4),
                           producers=dict(zip(SEVEN, V.producers(c))))
        d = dict(polygons=len(Pk), polygons_without_pixels=int((~hit).sum()), blocks=blocks, full=full,
                 block_bootstrap=B.boot(blocks, RB, keys, PAIRS, B.NBOOT, B.SEED),
                 by_block={b: {k: round(B.scores(RB[k][j])[0], 4) for k in keys} for j, b in enumerate(blocks)})
        if sk == "v3":
            d["by_origin"] = {}
            acts = [x for x, h in zip(A3, hit) if h]
            for gname, want in (("v2 pieces", ("piece", "keep")), ("new", ("new",)), ("fan", ("fan",))):
                sel = np.array([x in want for x in acts])
                if sel.any():
                    d["by_origin"][gname] = dict(polygons=int(sel.sum()), **{k: dict(zip(
                        ("accuracy", "kappa", "balanced"), [round(v, 4) for v in B.scores(Rk[k][sel].sum(0))])) for k in keys})
        res[sk + "_polygons"] = d
        print("%s held out, %d polygons (%d without pixels on some map), %d blocks  (%.0f s)"
              % (sk, len(Pk), d["polygons_without_pixels"], len(blocks), time.time() - t0))
        for k in keys:
            print("  %-8s accuracy %.4f kappa %.4f balanced %.4f" % (k, full[k]["accuracy"], full[k]["kappa"], full[k]["balanced"]))
        for a, b in PAIRS:
            x = d["block_bootstrap"]["%s-%s" % (a, b)]
            print("  %s - %s block 95 %%: accuracy %s, balanced %s" % (a, b, x["accuracy_ci95"], x["balanced_ci95"]))

    f2, f3 = res["v2_polygons"]["full"], res["v3_polygons"]["full"]
    res["recommendation"] = {}
    for m in ("svm", "unet"):
        hi, lo = m + "_v3", m + "_v2"
        res["recommendation"][m] = rule(m, dict(v3=f2[hi], v2=f2[lo]), dict(v3=f3[hi], v2=f3[lo]), f2[hi]["producers"],
                                        f2[lo]["producers"], res["edifice_share"]["unet_v3"] if m == "unet" else None)
    rule_can_fail(f2["unet_v2"], f2["unet_v2"]["producers"])
    res["predictions"] = judge(res)
    if REHEARSE:   # stand-ins: the same maps, so every difference is exactly nothing
        for sk in ("v2", "v3"):
            for a, b in PAIRS[:2]:
                x = res[sk + "_polygons"]["block_bootstrap"]["%s-%s" % (a, b)]
                assert x["accuracy_ci95"] == [0.0, 0.0] and x["balanced_ci95"] == [0.0, 0.0], (sk, a, b, x)
        print("rehearsal: every v3-minus-v2 difference is 0, as stand-ins must be; verdicts below mean nothing")
    print("recommendation:", {m: r["recommended"] for m, r in res["recommendation"].items()})
    print("predictions:", res["predictions"])
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s  (%.0f s)" % (OUT, time.time() - t0))


if __name__ == "__main__":
    main()
