# -*- coding: utf-8 -*-
r"""Score the seven-class maps on the off-Tharsis edifice and apron labels (NEXT-STEPS §14 row 3; KB §69.63, §69.105;
rule and predictions in logs\agent_review\offtharsis_registration.md, written before any polygon was drawn).

    "<ArcGIS Pro Python>" score_offtharsis.py              writes logs\offtharsis_score.json
    "<ArcGIS Pro Python>" score_offtharsis.py --self-test  the v3 held-out polygons through this scorer must give the
                                                          producer's accuracies the maps' check logs hold (3 decimals)

Labels: Landform_TrainingSamples_offtharsis_draw (Classvalue 5 volcanic edifice, 6 apron). Maps, at the scorer's 400 m
(the cached arrays verify_global60_classification.py wrote; one older than its raster is refused): svm_v3, unet_v3
(the maps the final leads with, D36), svm_v2, unet_v2, and near_v3, each pixel the class of the nearest v3 training
polygon (make_block_bootstrap's baseline). A class with fewer than 3 polygons or under 300 km² is not scored (the
registration's floor). Per class and map: the area-weighted share of the polygons called that class (producer's
accuracy), a 95 % interval from resampling the polygons (2,000 draws, seed 105), each polygon's share, and the
class mix the maps give the rest. Predictions P1-P4 (the registration) are reported held or not held. Read-only.
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
from labelsets import SEVEN
import make_block_bootstrap as B

FC = "Landform_TrainingSamples_offtharsis_draw"
V3_TRAIN, V3_TEST = "Landform_TrainingSamples_v3_60_train", "Landform_TrainingSamples_v3_60_test"
MAPS = [("unet_v3", "npy", "global60_landforms_global60_landforms_unet_v3_200m_seamfix_ov400.npy",
         "global60_landforms_unet_v3_200m_seamfix", "global60_classification_check_global60_landforms_unet_v3_200m_seamfix.json"),
        ("svm_v3", "npy", "global60_landforms_v3_200m_mode11_ov400.npy", "global60_landforms_svm_v3_200m_mode11",
         "global60_classification_check_v3_200m_mode11.json"),
        ("unet_v2", "npy", "global60_landforms_global60_landforms_unet_v2_200m_seamfix_ov400.npy",
         "global60_landforms_unet_v2_200m_seamfix", None),
        ("svm_v2", "npy", "global60_landforms_v2_200m_mode11_ov400.npy", "global60_landforms_svm_v2_200m_mode11", None),
        ("near_v3", "near", None, None, None)]
CLASSES = {5: "volcanic edifice", 6: "apron"}
REF = {"unet_v3": {5: 0.795, 6: 0.819}, "svm_v3": {5: 0.401, 6: 0.038}}    # the registration's reference
NBOOT, SEED = 2000, 105
OUT = os.path.join(HERE, "logs", "offtharsis_score.json")
KM2_PX = 0.4 * 0.4


def polys(fc):
    out = []
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue"] + (["Notes"] if fc == FC else []),
                               spatial_reference=B.MARS) as c:
        for r in c:
            out.append((int(r[1]), [[(p.X, p.Y) for p in part if p is not None] for part in r[0]],
                        r[2].split()[0] if len(r) > 2 and r[2] else ""))
    return out


def self_test():
    P = [p for p in polys(V3_TEST) if p[0] in CLASSES]
    ok = True
    for key, kind, npy, tif, log in MAPS[:2]:
        a, m, g = B.load(kind, npy, tif, None)
        R = B.rows(a, m, g, P, 7)
        c = R.sum(0)
        want = json.load(open(os.path.join(HERE, "logs", log), encoding="utf-8"))["held_out"]["producers"]
        for v, name in CLASSES.items():
            got = round(float(c[v - 1, v - 1] / c[v - 1].sum()), 3)
            print("%s %-8s %-16s here %.3f, check log %.3f" % ("PASS" if got == want[name] else "FAIL", key, name, got, want[name]))
            ok &= got == want[name]
    return ok


def main():
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    P = polys(FC)
    res = {"labels": FC, "polygons": len(P), "maps": [m[0] for m in MAPS], "classes": {}, "skipped": {}}
    scored = {}
    for v, name in CLASSES.items():
        mine = [p for p in P if p[0] == v]
        if len(mine) < 3:
            res["skipped"][name] = "%d polygons, under the registration's 3" % len(mine)
            continue
        scored[v] = mine
    rng = np.random.default_rng(SEED)
    for key, kind, npy, tif, _ in MAPS:
        a, m, g = B.load(kind, npy, tif, V3_TRAIN)
        for v, mine in scored.items():
            R = B.rows(a, m, g, mine, 7)
            own = R[:, v - 1, :]                      # each polygon's row: area by map class
            tot = own.sum(1)
            share = float(own[:, v - 1].sum() / tot.sum())
            idx = rng.integers(0, len(mine), (NBOOT, len(mine)))
            boot = own[idx, v - 1].sum(1) / tot[idx].sum(1)
            mix = own.sum(0) / tot.sum()
            d = res["classes"].setdefault(CLASSES[v], {"polygons": len(mine), "pixels_400m": int(round(tot.sum())), "maps": {}})
            d["maps"][key] = {"share": round(share, 4), "ci95": [round(float(x), 4) for x in np.percentile(boot, [2.5, 97.5])],
                              "per_polygon": {p[2]: round(float(own[i, v - 1] / tot[i]), 3) if tot[i] else None
                                              for i, p in enumerate(mine)},
                              "called": {SEVEN[i]: round(float(mix[i]), 4) for i in np.argsort(-mix) if mix[i] >= 0.005}}
            if key in ("unet_v3", "svm_v3"):
                d.setdefault("_rows", {})[key] = own
                d["_v"] = v
    preds = {}
    ed = res["classes"].get("volcanic edifice")
    ap = res["classes"].get("apron")
    if ed:
        preds["P1 unet_v3 edifice share < 0.795"] = ed["maps"]["unet_v3"]["share"] < REF["unet_v3"][5]
    if ap:
        preds["P2 unet_v3 apron share < 0.819"] = ap["maps"]["unet_v3"]["share"] < REF["unet_v3"][6]
    p3 = [c["maps"]["unet_v3"]["share"] > c["maps"]["svm_v3"]["share"] for c in (ed, ap) if c]
    if p3:
        preds["P3 unet_v3 > svm_v3 on each scored class"] = all(p3)
    p4 = [c["maps"]["near_v3"]["share"] < 0.10 for c in (ed, ap) if c]
    if p4:
        preds["P4 near_v3 < 0.10 on each scored class"] = all(p4)
    for c in res["classes"].values():
        rows, v = c.pop("_rows", None), c.pop("_v", None)
        if rows:
            u, s = rows["unet_v3"], rows["svm_v3"]
            idx = rng.integers(0, u.shape[0], (NBOOT, u.shape[0]))      # the same polygons drawn for both maps
            diff = u[idx, v - 1].sum(1) / u.sum(1)[idx].sum(1) - s[idx, v - 1].sum(1) / s.sum(1)[idx].sum(1)
            c["unet_v3_minus_svm_v3_ci95"] = [round(float(x), 4) for x in np.percentile(diff, [2.5, 97.5])]
    res["predictions"] = preds
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    for name, c in res["classes"].items():
        print("%s: %d polygons, %d px at 400 m (%.0f km2)" % (name, c["polygons"], c["pixels_400m"], c["pixels_400m"] * KM2_PX))
        for k, mm in c["maps"].items():
            print("  %-8s %.3f [%.3f, %.3f]  called %s" % (k, mm["share"], mm["ci95"][0], mm["ci95"][1],
                                                         ", ".join("%s %.2f" % kv for kv in list(mm["called"].items())[:4])))
        if "unet_v3_minus_svm_v3_ci95" in c:
            print("  unet_v3 - svm_v3 interval", c["unet_v3_minus_svm_v3_ci95"])
    for k, v in res["skipped"].items():
        print("not scored:", k, "-", v)
    for k, v in preds.items():
        print("%-45s %s" % (k, "held" if v else "NOT held"))
    print("->", OUT)


if __name__ == "__main__":
    main()
