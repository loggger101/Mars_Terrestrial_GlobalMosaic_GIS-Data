# -*- coding: utf-8 -*-
r"""Scores beyond accuracy and kappa, and each class's share of the map (NEXT-STEPS §12.2 A4, A12; KB §69.18).

Reads the outputs of verify_global60_classification.py (logs\global60_classification_check_*.json) and, from the
held-out area-weighted confusion matrix of each (rows the labels, columns the map, cos-latitude weights), adds:

  balanced accuracy     the mean of the producer's accuracies (each class counts once, whatever its area)
  F1 per class, macro   2PU / (P + U) per class, and their mean
  quantity / allocation disagreement (Pontius and Millones 2011): 1 - accuracy = Q + A, where
                        Q = half the summed |label share - map share| over classes (the map has the wrong amount
                        of a class) and A the rest (the right amount in the wrong place)
  map shares            the share of +-60 deg that each class covers (share_area_weighted), for A12

No prediction is tested; these are descriptions of results already recorded. Pure Python; reads JSON only.
Uses confusion_unrounded where the output has it, else confusion_area_weighted (rounded to 4 places by the
scorer: every figure below is then good to about 0.001). The accuracy and kappa recomputed here are checked
against the scorer's own to 0.001, or the script stops.

  python score_metrics.py [log ...]      default: every map the papers quote (MAPS below)
Writes logs\score_metrics.json (--out to move it). Exit 2 if a log is missing or disagrees with itself.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(HERE, "logs")

MAPS = [  # (label, log): the published map, its filter sweep's ends, the U-Net maps, T1's band sets
    ("SVM 400 m raw", "global60_classification_check_400m.json"),
    ("SVM 200 m raw", "global60_classification_check_200m.json"),
    ("SVM 200 m 5x5", "global60_classification_check_200m_mode5.json"),
    ("SVM 200 m 11x11 (published)", "global60_classification_check_200m_mode11.json"),
    ("U-Net one pass", "global60_classification_check_global60_landforms_unet_200m.json"),
    ("U-Net two passes", "global60_classification_check_global60_landforms_unet_200m_seamfix.json"),
    ("SVM 200 m no thermal", "global60_classification_check_nothermal_200m.json"),
    ("SVM 400 m no thermal", "global60_classification_check_nothermal_400m.json"),
    ("SVM 400 m no visible", "global60_classification_check_novisible_400m.json"),
    ("SVM 400 m terrain only", "global60_classification_check_terrain_400m.json"),
]
TOL = 0.001


def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def kappa(cm):
    n = sum(map(sum, cm)); po = sum(cm[i][i] for i in range(len(cm))) / n
    pe = sum(sum(cm[i]) * sum(r[i] for r in cm) for i in range(len(cm))) / n ** 2
    return po, (po - pe) / (1 - pe)


def metrics(r):
    """The extra scores of one scorer output; raises ValueError if its own numbers disagree."""
    h = r["held_out"]
    cm = h.get("confusion_unrounded") or h["confusion_area_weighted"]
    names = list(h["producers"])
    n = sum(map(sum, cm)); cm = [[v / n for v in row] for row in cm]
    K = len(cm)
    lab = [sum(cm[i]) for i in range(K)]
    mp = [sum(row[i] for row in cm) for i in range(K)]
    oa, k = kappa(cm)
    if abs(oa - h["accuracy"]) > TOL or abs(k - h["kappa"]) > TOL:
        raise ValueError("recomputed accuracy %.4f, kappa %.4f against the log's %s, %s"
                         % (oa, k, h["accuracy"], h["kappa"]))
    out, f1 = {}, []
    present = [i for i in range(K) if lab[i] > 0]          # a class with no held-out area has no producer's
    for i in range(K):
        p = cm[i][i] / lab[i] if lab[i] else None
        u = cm[i][i] / mp[i] if mp[i] else None
        f = 2 * p * u / (p + u) if p and u else (0.0 if lab[i] else None)
        out[names[i]] = dict(producers=p, users=u, f1=f, label_share=lab[i], map_share_in_polygons=mp[i])
        if f is not None:
            f1.append(f)
    q = 0.5 * sum(abs(lab[i] - mp[i]) for i in range(K))
    rnd = lambda v: None if v is None else round(v, 4)
    return dict(
        polygons=h["polygons"], accuracy=rnd(oa), kappa=rnd(k),
        balanced_accuracy=rnd(sum(out[names[i]]["producers"] for i in present) / len(present)),
        macro_f1=rnd(sum(f1) / len(f1)),
        quantity_disagreement=rnd(q), allocation_disagreement=rnd(1 - oa - q),
        one_class_everywhere=h.get("one_class_everywhere"),
        source="confusion_unrounded" if h.get("confusion_unrounded") else "confusion_area_weighted (4 places)",
        per_class={c: {kk: rnd(vv) for kk, vv in d.items()} for c, d in out.items()},
        map_share=r.get("share_area_weighted"))


def main():
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] != "--out"]
    todo = [(os.path.basename(a), a) for a in args] or [(lb, os.path.join(LOGS, f)) for lb, f in MAPS]
    res, bad = {}, 0
    print("%-30s %6s %6s %6s %6s %6s %6s" % ("map", "acc", "kappa", "bal", "mF1", "Q", "A"))
    for lb, path in todo:
        if not os.path.exists(path):
            print("missing %s" % path); bad += 1; continue
        try:
            m = metrics(json.load(open(path, encoding="utf-8")))
        except (ValueError, KeyError) as e:
            print("%s: %s" % (lb, e)); bad += 1; continue
        m["log"] = os.path.basename(path); res[lb] = m
        print("%-30s %6.3f %6.3f %6.3f %6.3f %6.3f %6.3f" % (lb, m["accuracy"], m["kappa"], m["balanced_accuracy"],
              m["macro_f1"], m["quantity_disagreement"], m["allocation_disagreement"]))
        print("    F1 " + ", ".join("%s %s" % (c, "-" if d["f1"] is None else "%.3f" % d["f1"])
                                    for c, d in m["per_class"].items()))
        if m["map_share"]:
            print("    map share " + ", ".join("%s %.3f" % kv for kv in m["map_share"].items()))
    out = opt("--out", os.path.join(LOGS, "score_metrics.json"))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(script="score_metrics.py", note="held out; area-weighted (cos latitude); NEXT-STEPS §12.2 A4, A12",
                       maps=res), f, indent=1)
    print("wrote %s" % out)
    sys.exit(2 if bad else 0)


if __name__ == "__main__":
    main()
