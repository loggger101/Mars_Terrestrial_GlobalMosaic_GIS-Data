# -*- coding: utf-8 -*-
r"""D18's verdict: does the seven-class map replace the published four-class one? (KB §68.4, NEXT-STEPS §11.5)

Reads two outputs of verify_global60_classification.py --labels v2, both scored on the same v2 held-out polygons:

  --four  the published four-class map scored on the v2 labels
          (default logs\global60_classification_check_200m_mode11_on_v2_labels.json)
  --v2    the seven-class map (default logs\global60_classification_check_v2_200m_mode11.json)

The rule, written before any run (the author's word, 2026-10-22): the v2 map replaces the published one only if
  (a) its held-out accuracy and kappa are each at least the four-class map's;
  (b) each new class (5 volcanic edifice, 6 apron, 7 fluvial channel) in the v2 labels has a user's accuracy
      above its share of the held-out area (better than painting that class at random);
  (c) Crater, steep/windy hills and Normal Ground lose under 5 points of producer's accuracy each.
Otherwise the four-class map stays published and v2 is reported as a test. Beside the rule it reports accuracy and
kappa on the ground both maps can name (held-out v2 classes 1-4), since (a) is nearly automatic when classes 5-7
hold much of the held-out area (58 % in the 2026-10-23 rehearsal, KB §68.6). A new class left out of the v2 split
(short of NEXT-STEPS §11.3) is named as such and is not tested by (b). Pure Python; reads JSON only.
Writes logs\d18_verdict.json (--out to move it). Exit 0 whatever the verdict; 2 if the inputs do not match.
"""
import os, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from labelsets import SEVEN, FOUR

NEW = SEVEN[4:]
KEPT = ["Crater", "steep/windy hills", "Normal Ground"]
DROP = 0.05                                    # (c): a fall of 5 points or more fails


def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def load(path):
    if not os.path.exists(path):
        sys.exit("missing %s: run verify_global60_classification.py --labels v2 on that map first" % path)
    return json.load(open(path, encoding="utf-8"))


def verdict(four, v2):
    """(record, replaces?) from the two scorer outputs; refuses inputs not scored on the same v2 polygons."""
    for nm, r in (("four-class", four), ("v2", v2)):
        lab = r.get("labels", {})
        if lab.get("classes") != SEVEN or "v2" not in lab.get("held_out", ""):
            raise ValueError("the %s output was not scored on the v2 labels (--labels v2): %s" % (nm, lab))
    if four["labels"] != v2["labels"] or four["held_out"]["polygons"] != v2["held_out"]["polygons"]:
        raise ValueError("the two outputs were scored on different polygons: %s / %s"
                         % (four["held_out"]["polygons"], v2["held_out"]["polygons"]))
    if set(four["rat"].values()) - set(FOUR):
        raise ValueError("--four is not a four-class map: %s" % four["rat"])
    f, s = four["held_out"], v2["held_out"]
    a = dict(accuracy=(s["accuracy"], f["accuracy"]), kappa=(s["kappa"], f["kappa"]))
    a_ok = s["accuracy"] >= f["accuracy"] and s["kappa"] >= f["kappa"]
    b, left_out = {}, []
    for c in NEW:
        share = s["label_area_share"][c]
        if share == 0:
            left_out.append(c)
            continue
        b[c] = dict(users=s["users"][c], area_share=share, ok=s["users"][c] > share)
    b_ok = all(x["ok"] for x in b.values())
    # the scorer rounds to 3 places; rounding the fall too keeps 0.600 - 0.550 a fall of 5 points, not 4.99...
    cc = {c: dict(v2=s["producers"][c], four=f["producers"][c], fall=round(f["producers"][c] - s["producers"][c], 4))
          for c in KEPT}
    for x in cc.values():
        x["ok"] = x["fall"] < DROP
    c_ok = all(x["ok"] for x in cc.values())
    rec = dict(made=time.strftime("%Y-%m-%d %H:%M"), held_out_polygons=s["polygons"], labels=v2["labels"],
               a_accuracy_and_kappa=dict(a, ok=a_ok), b_new_classes=b, b_ok=b_ok, left_out_of_v2=left_out,
               c_kept_classes=cc, c_ok=c_ok, replaces=a_ok and b_ok and c_ok,
               kept_ground=dict(v2=kept_ground(s), four=kept_ground(f)),
               note="(v2, four-class) pairs; rule KB §68.4 / D18. kept_ground is reported, not part of the rule")
    return rec, rec["replaces"]


def kept_ground(h):
    """(accuracy, kappa) on the held-out polygons whose v2 class is 1-4, the ground both maps can name (KB §68.6):
    a four-class map loses all of classes 5-7 by construction, so rule (a) alone says little when they hold much
    of the held-out area. Needs the scorer's confusion_unrounded; None without it."""
    if "confusion_unrounded" not in h:
        return None
    cm = [row[:] for row in h["confusion_unrounded"]]
    for i in range(4, len(cm)):
        cm[i] = [0.0] * len(cm[i])
    tot = sum(map(sum, cm))
    po = sum(cm[i][i] for i in range(len(cm))) / tot
    pe = sum(sum(cm[i]) * sum(r[i] for r in cm) for i in range(len(cm))) / tot ** 2
    return round(po, 3), round((po - pe) / (1 - pe), 3)


def main():
    four = load(opt("--four", os.path.join(HERE, "logs", "global60_classification_check_200m_mode11_on_v2_labels.json")))
    v2 = load(opt("--v2", os.path.join(HERE, "logs", "global60_classification_check_v2_200m_mode11.json")))
    out = opt("--out", os.path.join(HERE, "logs", "d18_verdict.json"))
    try:
        rec, ok = verdict(four, v2)
    except ValueError as e:
        print("NOT JUDGED:", e)
        sys.exit(2)
    a = rec["a_accuracy_and_kappa"]
    print("held out, %d v2 polygons" % rec["held_out_polygons"])
    print("(a) accuracy %.3f vs %.3f, kappa %.3f vs %.3f: %s" % (a["accuracy"] + a["kappa"] + ("ok" if a["ok"] else "FAILS",)))
    for c, x in rec["b_new_classes"].items():
        print("(b) %-17s user's %.3f vs area share %.3f: %s" % (c, x["users"], x["area_share"], "ok" if x["ok"] else "FAILS"))
    for c in rec["left_out_of_v2"]:
        print("(b) %-17s not in the v2 split (short of NEXT-STEPS §11.3); not tested" % c)
    for c, x in rec["c_kept_classes"].items():
        print("(c) %-17s producer's %.3f vs %.3f, fall %+.3f: %s" % (c, x["v2"], x["four"], x["fall"], "ok" if x["ok"] else "FAILS"))
    kg = rec["kept_ground"]
    if kg["v2"] and kg["four"]:
        print("(not in the rule) on ground both maps can name, v2 classes 1-4: accuracy %.3f vs %.3f, kappa %.3f vs %.3f"
              % (kg["v2"][0], kg["four"][0], kg["v2"][1], kg["four"][1]))
    print("VERDICT: %s" % ("the seven-class map replaces the published one" if ok
                           else "the four-class map stays published; v2 is reported as a test"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(rec, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
