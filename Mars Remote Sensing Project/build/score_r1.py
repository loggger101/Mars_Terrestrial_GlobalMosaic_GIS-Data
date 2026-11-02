# -*- coding: utf-8 -*-
r"""Score R1: the author's blind answers on the rule-screened apron and fluvial rows (NEXT-STEPS §12.3; registration
logs\r1\r1_registration.md; sheets from make_r1_sheets.py).

    python score_r1.py <answers.txt | labels.json> [--agent] [--out <result.json>]     --agent: the agent's answers (KB §69.55)
    python score_r1.py --rehearse        planted answers, nothing written; every check must PASS

<answers.txt>: one "A1 a" per line (a accept, r reject, u unsure), # comments; or {"A1": "a", ...}. Every slot must be
answered (u is an answer). Reads logs\r1\r1_key.json (the rule's verdict per slot). Reported, no gate: the author's eye
is the reference. Per class (fluvial channel 7, apron 6), unsure rows dropped and counted:
  - precision: the share of the rule's accepts the author accepts, Wilson 95 % interval; and that share applied to all
    of the class's rule accepts (192 fluvial, 155 apron: logs\label_review_by_rule.json)
  - the share of the rule's rejects the author rejects, Wilson 95 % interval
  - agreement and Cohen's kappa between rule and author on the decided rows
Plain Python.
"""
import os, sys, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(HERE, "logs", "r1", "r1_key.json")
RULE = os.path.join(HERE, "logs", "label_review_by_rule.json")
NAMES = {7: "fluvial channel", 6: "apron"}


def wilson(k, n):
    if not n:
        return None
    p, z = k / n, 1.96
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return {"share": round(p, 3), "k": k, "n": n, "lo": round(c - h, 3), "hi": round(c + h, 3)}


def kappa(pairs):
    n = len(pairs)
    if not n:
        return None, None
    po = sum(a == b for a, b in pairs) / n
    pe = sum((sum(a == c for a, _ in pairs) / n) * (sum(b == c for _, b in pairs) / n) for c in ("a", "r"))
    return round(po, 3), (round((po - pe) / (1 - pe), 3) if pe < 1 else None)


def score(key, lab, totals):
    out = {}
    for cls, name in NAMES.items():
        rows = [(v["rule"][0], lab[s]) for s, v in key.items() if v["cls"] == cls]
        dec = [(r, a) for r, a in rows if a != "u"]
        acc = [a for r, a in dec if r == "a"]
        rej = [a for r, a in dec if r == "r"]
        prec = wilson(sum(a == "a" for a in acc), len(acc))
        po, k = kappa(dec)
        out[name] = {"rows": len(rows), "unsure": len(rows) - len(dec),
                     "precision_of_rule_accepts": prec,
                     "rule_rejects_rejected": wilson(sum(a == "r" for a in rej), len(rej)),
                     "agreement": po, "kappa": k,
                     "rule_accepts_in_class": totals[cls],
                     "fair_labels_among_them": None if prec is None else
                     [round(prec["lo"] * totals[cls]), round(prec["share"] * totals[cls]), round(prec["hi"] * totals[cls])]}
    return out


def totals():
    rows = json.load(open(RULE, encoding="utf-8"))["rows"]
    return {c: sum(1 for r in rows if r["cls"] == c and r["review"] == "accept") for c in NAMES}


def read(path, slots):
    if path.lower().endswith(".txt"):
        lab = {}
        for line in open(path, encoding="utf-8"):
            parts = line.split("#")[0].replace(",", " ").split()
            for i in range(0, len(parts) - 1, 2):
                lab[parts[i].upper()] = parts[i + 1].lower()
    else:
        lab = json.load(open(path, encoding="utf-8"))
    bad = {s: v for s, v in lab.items() if s not in slots or v not in ("a", "r", "u")}
    missing = sorted(set(slots) - set(lab))
    if bad or missing:
        sys.exit("refused: bad %s; slots missing %s" % (bad, missing[:10]))
    return lab


def rehearse():
    key = json.load(open(KEY, encoding="utf-8"))["slots"]
    T = totals()
    same = {s: v["rule"][0] for s, v in key.items()}
    flip = {s: "r" if v == "a" else "a" for s, v in same.items()}
    allu = {s: "u" for s in key}
    all_a = {s: "a" for s in key}
    sc, sf, su, sa = (score(key, x, T) for x in (same, flip, allu, all_a))
    half = dict(same)                                         # planted: the author rejects 15 of each class's 30 accepts
    for cls in NAMES:
        for s in sorted(s for s, v in key.items() if v["cls"] == cls and v["rule"] == "accept")[:15]:
            half[s] = "r"
    sh = score(key, half, T)
    checks = [("30 accepts and 10 rejects per class", all(sum(1 for v in key.values() if v["cls"] == c and v["rule"] == r) == n
                                                          for c in NAMES for r, n in (("accept", 30), ("reject", 10)))),
              ("answers = the rule: precision 1, kappa 1", all(v["precision_of_rule_accepts"]["share"] == 1 and v["kappa"] == 1
                                                              for v in sc.values())),
              ("answers = the rule's opposite: precision 0, kappa -0.6 (30:10 margins)", all(v["precision_of_rule_accepts"]["share"] == 0
                                                                          and v["kappa"] == -0.6 for v in sf.values())),
              ("all unsure: nothing estimated", all(v["precision_of_rule_accepts"] is None and v["kappa"] is None for v in su.values())),
              ("all accept: kappa 0, rejects-rejected 0", all(v["kappa"] == 0 and v["rule_rejects_rejected"]["share"] == 0
                                                              for v in sa.values())),
              ("half the accepts rejected: precision 0.5", all(v["precision_of_rule_accepts"]["share"] == 0.5 for v in sh.values())),
              ("the totals are the KB's 192 and 155", T == {7: 192, 6: 155}),
              ("Wilson 15 of 30 is 0.332-0.668", wilson(15, 30)["lo"] == 0.332 and wilson(15, 30)["hi"] == 0.668)]
    for name, ok in checks:
        print("PASS" if ok else "FAIL", name)
    return all(ok for _, ok in checks)


def main():
    if "--rehearse" in sys.argv:
        sys.exit(0 if rehearse() else 1)
    key = json.load(open(KEY, encoding="utf-8"))["slots"]
    lab = read(sys.argv[1], key)
    res = {"labeller": "agent (KB 69.55)" if "--agent" in sys.argv else "author", **score(key, lab, totals())}
    print(json.dumps(res, indent=1, ensure_ascii=False))
    if "--out" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
