# -*- coding: utf-8 -*-
r"""Score the author's check of the 86 lava-flow margins the agent traced on CTX (D33; KB §69.52, §69.104; sheets from
make_margin_check_sheets.py, the rule in <drive>\Mars Project\review_sheets\margins_check\README.md, written before
any answer).

    python score_margin_check.py <answers.txt> [--out <result.json>]     default logs\margin_check.json
    python score_margin_check.py --rehearse                                planted answers, nothing written

<answers.txt>: "M01 k" pairs in any layout, # comments; k keep, p partly, n no margin, u unsure. Part of the folder
may be answered (the result says how much); make_flow_margin_test.py --check refuses a partial one. Any unknown slot
or letter refuses the whole file. Reported, no gate (the author's eye is the reference):
  - the share of the decided margins (k, p, n) kept as k, and as k or p, Wilson 95 % intervals, and the km each keeps
  - the same shares by the agent's own confidence (certain, probable, inferred): does its confidence track the check?
  - answers_by_oid, for make_flow_margin_test.py --margins --check <result.json> --keep k|kp
Plain Python.
"""
import os, sys, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive

INDEX = on_drive(r"Mars Project\review_sheets\margins_check\index.json")
LETTERS = ("k", "p", "n", "u")


def wilson(k, n):
    if not n:
        return None
    p, z = k / n, 1.96
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return {"share": round(p, 3), "k": k, "n": n, "lo": round(c - h, 3), "hi": round(c + h, 3)}


def read(path, slots):
    lab, bad = {}, []
    for line in open(path, encoding="utf-8"):
        parts = line.split("#")[0].replace(",", " ").replace(":", " ").split()
        if len(parts) % 2:
            bad.append("odd line: %r" % line.strip())
            continue
        for i in range(0, len(parts), 2):
            s, v = parts[i].upper(), parts[i + 1].lower()
            if s not in slots or v not in LETTERS:
                bad.append("%s %s" % (s, v))
            elif s in lab and lab[s] != v:
                bad.append("%s given %s and %s" % (s, lab[s], v))
            else:
                lab[s] = v
    if bad:
        sys.exit("refused, nothing written: %s" % "; ".join(bad[:10]))
    return lab


def score(slots, lab):
    dec = {s: v for s, v in lab.items() if v != "u"}
    res = {"margins": len(slots), "answered": len(lab), "counts": {c: sum(1 for v in lab.values() if v == c) for c in LETTERS},
           "total_km": round(sum(m["km"] for m in slots.values()), 1)}
    for form, keep in (("k", "k"), ("kp", "kp")):
        res["kept_" + form] = wilson(sum(1 for v in dec.values() if v in keep), len(dec))
        res["kept_km_" + form] = round(sum(slots[s]["km"] for s, v in lab.items() if v in keep), 1)
    res["by_agent_confidence"] = {}
    for conf in ("certain", "probable", "inferred"):
        d = {s: v for s, v in dec.items() if slots[s]["confidence"] == conf}
        res["by_agent_confidence"][conf] = {"k": wilson(sum(1 for v in d.values() if v == "k"), len(d)),
                                            "kp": wilson(sum(1 for v in d.values() if v in "kp"), len(d))}
    res["answers_by_oid"] = {str(slots[s]["oid"]): v for s, v in sorted(lab.items())}
    return res


def rehearse():
    slots = json.load(open(INDEX, encoding="utf-8"))["slots"]
    S = sorted(slots)
    allk, alln, allu = ({s: c for s in S} for c in "knu")
    half = {s: ("k" if i % 2 else "n") for i, s in enumerate(S)}
    part = {s: "p" for s in S[:10]}
    a, b, u, h, p = (score(slots, x) for x in (allk, alln, allu, half, part))
    checks = [("86 slots, 1,476 km in all (KB §69.52)", len(S) == 86 and int(a["total_km"]) == 1476),
              ("all keep: share 1, every km kept", a["kept_k"]["share"] == 1 and a["kept_km_k"] == a["total_km"]),
              ("all no margin: share 0, nothing kept", b["kept_k"]["share"] == 0 and b["kept_km_kp"] == 0),
              ("all unsure: nothing estimated", u["kept_k"] is None and u["kept_kp"] is None),
              ("half keep: share 0.5", h["kept_k"]["share"] == 0.5),
              ("ten partly: k 0, kp 1, answered 10", p["kept_k"]["share"] == 0 and p["kept_kp"]["share"] == 1 and p["answered"] == 10),
              ("every oid once", len(set(a["answers_by_oid"])) == 86),
              ("Wilson 15 of 30 is 0.332-0.668", wilson(15, 30)["lo"] == 0.332 and wilson(15, 30)["hi"] == 0.668)]
    for name, ok in checks:
        print("PASS" if ok else "FAIL", name)
    return all(ok for _, ok in checks)


def main():
    if "--rehearse" in sys.argv:
        sys.exit(0 if rehearse() else 1)
    slots = json.load(open(INDEX, encoding="utf-8"))["slots"]
    lab = read(sys.argv[1], slots)
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "logs", "margin_check.json")
    res = score(slots, lab)
    res["answers_file"] = os.path.abspath(sys.argv[1])
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print("answered %d of %d: %s" % (res["answered"], res["margins"], res["counts"]))
    for form in ("k", "kp"):
        w = res["kept_" + form]
        if w:
            print("kept (%s): %.1f %% [%.1f, %.1f] of %d decided, %.1f of %.1f km"
                  % (form, 100 * w["share"], 100 * w["lo"], 100 * w["hi"], w["n"], res["kept_km_" + form], res["total_km"]))
    print("->", out)


if __name__ == "__main__":
    main()
