# -*- coding: utf-8 -*-
r"""A13: how much the rule-screened v2 rows depend on the rule's two thresholds (NEXT-STEPS §12.2 A13, KB §69.50).

review_v2_by_rule.py (KB §69.8) accepted the new fluvial strips whose floor sits >= 20 m below a 4.8 km flank ring
(and ShareVolc < 0.5), and the new apron pieces whose median slope is >= 1° (and CraterCover < 0.5). This re-applies
the same rule at other thresholds to the measures that script logged for every row (logs\label_review_by_rule.json),
so nothing is re-measured: floor 10 and 30 m, slope 0.5° and 1.5°, each with the other condition unchanged. It
counts the rows whose verdict changes, by class and split, and the held-out blocks each class would still reach.

Prediction, written before the first run: at each alternative threshold fewer than 20 % of the class's rows change
verdict, and every class still meets the minimum of NEXT-STEPS §11.3 in held-out blocks (>= 10 polygons in >= 2
blocks). Reported as held or not held, whichever way it falls.

  python make_review_rule_sensitivity.py       -> logs\review_rule_sensitivity.json  (plain Python; no arcpy)
"""
import os, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "logs", "label_review_by_rule.json")
OUT = os.path.join(HERE, "logs", "review_rule_sensitivity.json")
FLOORS, SLOPES = (10.0, 20.0, 30.0), (0.5, 1.0, 1.5)
CHANGE_MAX, MIN_TEST, MIN_TEST_BLOCKS = 0.20, 10, 2


def verdict(r, floor, slope, rule):
    if r["cls"] == 7:
        return r.get("floor_m") is not None and r["floor_m"] >= floor and (r["volc"] or 0) < rule["VOLC_MAX"]
    return r["slope"] is not None and r["slope"] >= slope and (r["crater"] or 0) < rule["APRON_CRATER"]


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    rule, rows = d["rule"], d["rows"]
    base = {r["oid"]: verdict(r, rule["FLOOR_M"], rule["APRON_SLOPE"], rule) for r in rows}
    bad = [r["oid"] for r in rows if base[r["oid"]] != (r["review"] == "accept")]
    assert not bad, "the logged verdicts are not reproduced: %s" % bad[:10]
    out = dict(source=os.path.basename(SRC), rule=rule, settings=[])
    held = True
    for cls, name, key, values, base_v in ((7, "fluvial channel", "floor_m", FLOORS, rule["FLOOR_M"]),
                                           (6, "apron", "slope", SLOPES, rule["APRON_SLOPE"])):
        rs = [r for r in rows if r["cls"] == cls]
        for v in values:
            f, s = (v, rule["APRON_SLOPE"]) if cls == 7 else (rule["FLOOR_M"], v)
            now = {r["oid"]: verdict(r, f, s, rule) for r in rs}
            changed = [r for r in rs if now[r["oid"]] != base[r["oid"]]]
            acc = collections.Counter(r["split"] for r in rs if now[r["oid"]])
            blocks = sorted(set(r["block"] for r in rs if now[r["oid"]] and r["split"] == "test"))
            share = len(changed) / len(rs)
            ok = v == base_v or (share < CHANGE_MAX and acc["test"] >= MIN_TEST and len(blocks) >= MIN_TEST_BLOCKS)
            held &= ok
            row = dict(cls=name, threshold=key, value=v, rows=len(rs), changed=len(changed), share=round(share, 4),
                       to_accept=sum(1 for r in changed if now[r["oid"]]), to_reject=sum(1 for r in changed if not now[r["oid"]]),
                       accepted_train=acc["train"], accepted_test=acc["test"], test_blocks=blocks,
                       prediction="held" if ok else "NOT held")
            out["settings"].append(row)
            print("%-16s %-7s %5.1f  accepted train %3d test %3d in %d blocks; changed %3d of %d (%.1f %%: +%d -%d)  %s" % (
                name, key, v, acc["train"], acc["test"], len(blocks), len(changed), len(rs), 100 * share,
                row["to_accept"], row["to_reject"], row["prediction"] if v != base_v else "(the rule)"))
    out["prediction_held"] = held
    print("prediction:", "held" if held else "NOT held")
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", OUT)


if __name__ == "__main__":
    main()
