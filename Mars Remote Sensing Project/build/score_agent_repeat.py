# -*- coding: utf-8 -*-
r"""Score a blind repeat of the agent's own review against its first pass (KB §69.52's gate).

    python score_agent_repeat.py <first decisions.json> <first index.json> <repeat decisions.json> <repeat index.json>
           [--out <result.json>]

Rows are matched by class and OBJECTID (the repeat uses new slots and a new order). Reports, on the rows decided
(not unsure) both times, the agreement and Cohen's kappa, with each pass's counts. The registered gate: agreement >= 0.80
and kappa >= 0.60; kappa is undefined when both passes give one value to every row, and the gate then FAILS (it cannot
show that the passes agree beyond what a constant answer would). Letters: a / r / u, or f / v / i for origin (where
"decided" means f or v). Plain Python.
"""
import sys, json

DECIDED = {"a", "r", "f", "v"}


def main():
    d1, i1, d2, i2 = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:5])
    key = lambda idx, s: (idx["slots"][s]["class"], idx["slots"][s]["oid"])
    first = {key(i1, s): v for s, v in d1.items() if s in i1["slots"]}
    pairs = [(first[key(i2, s)], v) for s, v in d2.items() if s in i2["slots"]]
    both = [(a, b) for a, b in pairs if a in DECIDED and b in DECIDED]
    n = len(both)
    po = sum(a == b for a, b in both) / n if n else float("nan")
    cats = sorted({x for p in both for x in p})
    pe = sum((sum(a == c for a, _ in both) / n) * (sum(b == c for _, b in both) / n) for c in cats) if n else 1.0
    kappa = (po - pe) / (1 - pe) if pe < 1 else None
    res = {"rows": len(pairs), "decided_both": n, "agreement": round(po, 3),
           "kappa": None if kappa is None else round(kappa, 3),
           "first": {c: sum(a == c for a, _ in pairs) for c in "arufvi" if any(a == c for a, _ in pairs)},
           "repeat": {c: sum(b == c for _, b in pairs) for c in "arufvi" if any(b == c for _, b in pairs)},
           "changed": [[a, b] for a, b in pairs if a != b]}
    res["gate"] = "PASS" if (kappa is not None and po >= 0.80 and kappa >= 0.60) else "FAIL"
    print(json.dumps(res, indent=1))
    if "--out" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
