# -*- coding: utf-8 -*-
r"""D34's check (KB §69.56): the v3 labels before and after the fan amendment, row by row.

    python compare_v3_d34.py <before.json> <after.json>     e.g. logs\label_v3_pre_d34.json logs\label_v3_dryrun.json

Rows are matched by (class, action, source, area); the tallies are compared per class, action, split and
verdict. Prints every class whose tally changed, the apron rows whose verdict changed with their fan share, and the
registered prediction's verdict: only class 6 changes, by +20 to +150 accepted rows, all on lAa. Plain Python.
"""
import sys, json, collections


def load(p):
    return json.load(open(p, encoding="utf-8"))


def tally(rows):
    t = collections.Counter()
    for r in rows:
        t[(r["cls"], r["action"], r["split"], "accept" if r["ok"] else "reject")] += 1
    return t


def main():
    a, b = load(sys.argv[1]), load(sys.argv[2])
    ta, tb = tally(a["rows"]), tally(b["rows"])
    changed = sorted({k[0] for k in set(ta) | set(tb) if ta[k] != tb[k]})
    print("rows", len(a["rows"]), "->", len(b["rows"]))
    for c in range(1, 8):
        acc_a = sum(v for k, v in ta.items() if k[0] == c and k[3] == "accept")
        acc_b = sum(v for k, v in tb.items() if k[0] == c and k[3] == "accept")
        print("class %d accepted %5d -> %5d (%+d)%s" % (c, acc_a, acc_b, acc_b - acc_a, "  CHANGED" if c in changed else ""))
    for k in sorted(set(ta) | set(tb)):
        if ta[k] != tb[k]:
            print("   ", k, ta[k], "->", tb[k])
    key = lambda r: (r["cls"], r["action"], r["src"], r.get("km2"))      # a parent's pieces differ by area
    ia = collections.defaultdict(list)
    for r in a["rows"]:
        ia[key(r)].append(r)
    flips, off_fan = [], 0
    for r in b["rows"]:
        if r["cls"] != 6 or r["action"] == "new":
            continue
        for o in ia.get(key(r), []):
            if o["ok"] != r["ok"]:
                fan = (r.get("m") or {}).get("fan", 0) or 0
                flips.append((r["src"], o["ok"], r["ok"], fan, r["why"]))
                off_fan += fan < 0.5
                break
    print("apron pieces whose verdict changed: %d (%d not mostly on lAa)" % (len(flips), off_fan))
    for f in flips[:10]:
        print("   ", f)
    new_a = sum(v for k, v in ta.items() if k[0] == 6 and k[1] == "new" and k[3] == "accept")
    new_b = sum(v for k, v in tb.items() if k[0] == 6 and k[1] == "new" and k[3] == "accept")
    d6 = sum(v for k, v in tb.items() if k[0] == 6 and k[3] == "accept") - sum(v for k, v in ta.items() if k[0] == 6 and k[3] == "accept")
    print("new apron squares %d -> %d" % (new_a, new_b))
    fan_rows = [r for r in b["rows"] if r["action"] == "fan" and r["ok"]]
    fan_off = sum(1 for r in fan_rows if ((r.get("m") or {}).get("fan") or 0) < 0.5)
    print("D34b fan pieces accepted %d (train %d, held out %d; %d not mostly on lAa)" % (
        len(fan_rows), sum(r["split"] == "train" for r in fan_rows), sum(r["split"] == "test" for r in fan_rows), fan_off))
    lo, hi = (100, 400) if "--d34b" in sys.argv else (20, 150)     # the two registered predictions
    ok = changed == [6] and lo <= d6 <= hi and off_fan == 0 and fan_off == 0
    print("prediction (only class 6, %+d to %+d, all on lAa):" % (lo, hi), "HELD" if ok else "NOT HELD",
          "(classes changed %s, apron %+d, off-fan flips %d, off-fan D34b pieces %d)" % (changed, d6, off_fan, fan_off))


if __name__ == "__main__":
    main()
