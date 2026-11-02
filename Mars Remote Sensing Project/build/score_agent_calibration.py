# -*- coding: utf-8 -*-
r"""Score the agent's blind review against the author's (KB §69.51).

    python score_agent_calibration.py <decisions.json> <index.json> [--out <result.json>]

decisions.json maps each slot to a / r / u (the agent's call, written before this runs); index.json is the slot map
make_review_chips.py wrote. Reads the author's Review on each row and reports, on the rows both decided (unsure on
either side dropped), the agreement, Cohen's kappa and the 2 x 2 table, plus each side's unsure count. Read-only on
the gdb. ArcGIS Python.
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import GDB

CODE = {"a": "accept", "r": "reject", "u": "unsure"}


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a == "accept" for a, _ in pairs) / n
    pb = sum(b == "accept" for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main():
    dec = json.load(open(sys.argv[1], encoding="utf-8"))
    idx = json.load(open(sys.argv[2], encoding="utf-8"))["slots"]
    author = {}
    for slot, v in idx.items():
        with arcpy.da.SearchCursor(os.path.join(GDB, v["class"]), ["Review"], "OBJECTID = %d" % v["oid"]) as cur:
            author[slot] = next(cur)[0]
    rows = [(slot, CODE[dec[slot]], author[slot]) for slot in idx]
    both = [(a, b) for _, a, b in rows if a != "unsure" and b in ("accept", "reject")]
    table = {"%s/%s" % (a, b): sum(1 for x, y in both if (x, y) == (a, b))
             for a in ("accept", "reject") for b in ("accept", "reject")}
    po, k = kappa(both)
    res = {"n": len(rows), "both_decided": len(both), "agreement": round(po, 3), "kappa": round(k, 3),
           "table_agent/author": table,
           "agent_unsure": sum(1 for _, a, _ in rows if a == "unsure"),
           "author_unsure": sum(1 for _, _, b in rows if b == "unsure"),
           "author_accept_share": round(sum(1 for _, _, b in rows if b == "accept") / len(rows), 3),
           "agent_accept_share": round(sum(1 for _, a, _ in rows if a == "accept") / len(rows), 3),
           "rows": [{"slot": s, "agent": a, "author": b} for s, a, b in rows]}
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
    if "--out" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
