# -*- coding: utf-8 -*-
r"""A16: the two seven-class v2 maps scored on the v3 held-out labels, with block-bootstrap intervals (KB §69.57).

The seven-class results rest on 237 held-out polygons (Landform_TrainingSamples_v2_60_test), and the U-Net's accuracy
lead over the SVM is not resolved by block (−9.7 to +47.8 pt; A5, KB §69.44; NEXT-STEPS §14 row 3). The v3 labels
(KB §69.49, §69.56) hold 1,652 held-out polygons in the same 14 blocks: the v2 held-out polygons cut into screened
0.5° pieces, plus new polygons placed by rule from reference data (Robbins craters, steep and smooth terrain, catena
troughs, valley strips, the Tharsis fan pieces). Neither map saw any of them in training (same blocks), so they are
a second, larger held-out set for the maps already published. run_v3.ps1 steps 08 and 13 would make the same score
at 400 m on the desktop; the full verifier needs ~8 GB for its weight array, so this scores the cached 400 m arrays
polygon by polygon with the scorer's own routine instead (make_block_bootstrap.py's, svmcheck.training_score).

Maps (make_block_bootstrap.SETS["v2"]): svm7 (the seven-class SVM, 200 m 11 x 11), unet7 (the seven-class U-Net),
near7 (the nearest v2 training polygon, KB §69.35). Route check first: each map scored on the v2 held-out polygons
must give its logged accuracy and kappa within 0.001, or nothing is written (exit 2); --plant rolls svm7's array
half a planet, and the check must then refuse.

Also descriptive: the v3 held-out polygons by where they came from (Action of their row in
Landform_TrainingSamples_v3_proposals: "piece" or "keep", the v2 held-out polygons cut or kept; "new"; "fan", D34b),
each map's accuracy on each group; producer's accuracy per class; per block.

Predictions, written 2026-11-02 before any v3 score was read (each reported held or not held, none adjusted after):
  P1  unet7's accuracy on the v3 held-out polygons lies in 61-77 % (69.0 % on v2's): the held-out area is mostly
      the same ground, screened.
  P2  svm7's accuracy lies in 34.5-50.5 % (42.5 % on v2's).
  P3  unet7 minus svm7 under the block bootstrap: the accuracy interval includes 0 (as on v2), the balanced-accuracy
      interval lies above 0 (as on v2, D31).
  P4  svm7 minus near7, accuracy, block bootstrap: the interval includes 0 (as on v2).
  P5  Every map scores lower on the "new" polygons than on the "piece"/"keep" ones: the new ones are small (craters,
      strips) and the maps learned from the large v2 polygons.

  "<ArcGIS Pro Python>" score_v2maps_on_v3.py [--plant]
Writes logs\v2maps_on_v3.json; reads the drive only (Pro may be open). One such job at a time on the laptop.
"""
import os, sys, json, time, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import make_block_bootstrap as B

V3_TEST = "Landform_TrainingSamples_v3_60_test"
V3_PROP = "Landform_TrainingSamples_v3_proposals"
OUT = os.path.join(HERE, "logs", "v2maps_on_v3.json")
PLANT = "--plant" in sys.argv
PAIRS = [("unet7", "svm7"), ("svm7", "near7"), ("unet7", "near7")]


def v3_polys():
    """(class code, rings, block) as make_block_bootstrap.polys, and each polygon's Action from its proposal row."""
    act = {oid: a for oid, a in arcpy.da.SearchCursor(os.path.join(GDB, V3_PROP), ["OID@", "Action"])}
    P, A = [], []
    with arcpy.da.SearchCursor(os.path.join(GDB, V3_TEST), ["SHAPE@", "Classvalue", "Block", "ProposalOID"],
                               spatial_reference=B.MARS) as c:
        for g, v, b, po in c:
            P.append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g], b))
            A.append(act[po])
    return P, A


def producers(c):
    rs = c.sum(1)
    return [round(float(c[i, i] / rs[i]), 4) if rs[i] else None for i in range(len(c))]


def main():
    t0 = time.time()
    S = B.SETS["v2"]
    names, n = S["names"], len(S["names"])
    P2 = B.polys(S["test"])
    P3, A3 = v3_polys()
    blocks = sorted({b for _, _, b in P3})
    print("v3 held out: %d polygons in %d blocks; %s" % (len(P3), len(blocks), dict(collections.Counter(A3))))
    res = dict(script="score_v2maps_on_v3.py", when=time.strftime("%Y-%m-%d %H:%M"), boot=B.NBOOT, seed=B.SEED,
               labels=V3_TEST, classes=names, route_check={}, full={})
    R = {}
    for key, kind, npy, tif, logname in S["maps"]:
        a, m, g = B.load(kind, npy, tif, S["train"])
        if PLANT and key == "svm7":
            a = np.roll(np.asarray(a), a.shape[1] // 2, axis=1); m = a != 255
        oa, kp, ba = B.scores(B.rows(a, m, g, P2, n).sum(0))
        log = json.load(open(os.path.join(HERE, "logs", logname), encoding="utf-8"))["held_out"]
        ok = abs(oa - log["accuracy"]) <= 0.001 and abs(kp - log["kappa"]) <= 0.001
        print("%-6s on v2 held out: accuracy %.4f kappa %.4f; its log %s, %s -> %s  (%.0f s)"
              % (key, oa, kp, log["accuracy"], log["kappa"], "ok" if ok else "MISMATCH", time.time() - t0))
        if not ok:
            sys.exit(2)
        res["route_check"][key] = dict(accuracy=round(oa, 4), kappa=round(kp, 4), balanced=round(ba, 4))
        R[key] = B.rows(a, m, g, P3, n)
        del a, m
        oa, kp, ba = B.scores(R[key].sum(0))
        res["full"][key] = dict(accuracy=round(oa, 4), kappa=round(kp, 4), balanced=round(ba, 4),
                                producers=dict(zip(names, producers(R[key].sum(0)))))
        print("%-6s on v3 held out: accuracy %.4f kappa %.4f balanced %.4f  (%.0f s)" % (key, oa, kp, ba, time.time() - t0))
    keys = list(R)
    hit = R[keys[0]].sum((1, 2)) > 0
    assert all(((R[k].sum((1, 2)) > 0) == hit).all() for k in keys), "maps disagree on which polygons have pixels"
    Pk = [p for p, h in zip(P3, hit) if h]
    Ak = [x for x, h in zip(A3, hit) if h]
    for k in keys:
        R[k] = R[k][hit]
    res.update(polygons=len(Pk), polygons_without_pixels=int((~hit).sum()), blocks=blocks)
    bi = np.array([blocks.index(b) for _, _, b in Pk])
    RB = {k: np.array([R[k][bi == j].sum(0) for j in range(len(blocks))]) for k in keys}
    res["block_bootstrap"] = B.boot(blocks, RB, keys, PAIRS, B.NBOOT, B.SEED)
    res["polygon_bootstrap"] = B.boot(Pk, R, keys, PAIRS, B.NBOOT, B.SEED)

    grp = {"v2 pieces": ("piece", "keep"), "new": ("new",), "fan": ("fan",)}
    res["by_origin"] = {}
    for gname, acts in grp.items():
        sel = np.array([x in acts for x in Ak])
        if not sel.any():
            continue
        d = dict(polygons=int(sel.sum()), area_share=round(float(R[keys[0]][sel].sum() / R[keys[0]].sum()), 4))
        for k in keys:
            oa, kp, ba = B.scores(R[k][sel].sum(0))
            d[k] = dict(accuracy=round(oa, 4), balanced=round(ba, 4))
        res["by_origin"][gname] = d
        print("%-10s %4d polygons, %5.1f %% of the area: %s" % (gname, d["polygons"], 100 * d["area_share"],
              "  ".join("%s %.3f" % (k, d[k]["accuracy"]) for k in keys)))
    res["by_block"] = {b: {k: round(B.scores(RB[k][j])[0], 4) for k in keys} for j, b in enumerate(blocks)}

    full, bb = res["full"], res["block_bootstrap"]
    lo0 = lambda ci: ci[0] <= 0 <= ci[1]
    new, old = res["by_origin"].get("new"), res["by_origin"]["v2 pieces"]
    verdict = {
        "P1": 0.61 <= full["unet7"]["accuracy"] <= 0.77,
        "P2": 0.345 <= full["svm7"]["accuracy"] <= 0.505,
        "P3": lo0(bb["unet7-svm7"]["accuracy_ci95"]) and bb["unet7-svm7"]["balanced_ci95"][0] > 0,
        "P4": lo0(bb["svm7-near7"]["accuracy_ci95"]),
        "P5": bool(new) and all(new[k]["accuracy"] < old[k]["accuracy"] for k in keys),
    }
    res["predictions"] = {p: "held" if v else "NOT held" for p, v in verdict.items()}
    for k in keys:
        print("%-6s block 95 %%: accuracy %s, balanced %s" % (k, bb[k]["accuracy_ci95"], bb[k]["balanced_ci95"]))
    for a, b in PAIRS:
        d = bb["%s-%s" % (a, b)]
        print("%s - %s block 95 %%: accuracy %s, balanced %s" % (a, b, d["accuracy_ci95"], d["balanced_ci95"]))
    print("predictions:", res["predictions"])
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print("wrote %s  (%.0f s)" % (OUT, time.time() - t0))


if __name__ == "__main__":
    main()
