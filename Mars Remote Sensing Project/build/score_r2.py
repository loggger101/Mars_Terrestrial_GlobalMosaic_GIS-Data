# -*- coding: utf-8 -*-
r"""Score R2: the labelled probability sample against the four maps (KB §69.53; registration logs\r2\r2_registration.md).

    python score_r2.py <labels.json> [--out <result.json>]
    python score_r2.py --rehearse        planted labels, nothing written; every check must PASS

<labels.json>: {"A1": "n", ...}, or <answers.txt> with one "A1 n" per line; one letter per slot: c Crater, h steep/windy hills, t lava tube, n Normal Ground,
e volcanic edifice, a apron, f fluvial channel, u unsure. Reads logs\r2\r2_key.json (make_r2_points.py).

1. The gate, on the calibration rows (points inside the author's held-out polygons): at least 25 decided, agreement
   with the polygon's class >= 0.70 and Cohen's kappa >= 0.60. Reported first; if it fails, nothing else is estimated.
   --author: the author's own answers; the gate (registered for the agent's labelling) is reported, not enforced.
   --waive-gate: the agent's answers estimated though the gate failed, at the author's word (KB §69.55); labelled so.
2. On the sample rows, by the stratified estimator (Olofsson et al. 2014), unsure rows dropped: each map's overall
   accuracy with a 95 % interval (an unbiased estimator for any map: the strata are the seven-class SVM's classes and
   their area weights W_h); the four-class maps also on the rows whose reference is one of their four classes (a
   ratio estimator). For the seven-class SVM: user's and producer's accuracy per class, and each class's reference
   area share with its interval beside its mapped share. Plain Python.
"""
import os, sys, json, math, random

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(HERE, "logs", "r2", "r2_key.json")
LETTERS = "chtneaf"                                          # index = class code - 1 (labelsets.SEVEN)
MAPS = ("svm4", "unet4", "svm7", "unet7")


def kappa(pairs, k=7):
    n = len(pairs)
    if not n:
        return float("nan"), None
    po = sum(a == b for a, b in pairs) / n
    pe = sum((sum(a == c for a, _ in pairs) / n) * (sum(b == c for _, b in pairs) / n) for c in range(k))
    return po, ((po - pe) / (1 - pe) if pe < 1 else None)


def gate(key, lab):
    cal = [(key[s]["polygon"], LETTERS.index(lab[s])) for s in key if key[s]["kind"] == "cal" and lab.get(s, "u") != "u"]
    po, k = kappa(cal)
    ok = len(cal) >= 25 and k is not None and po >= 0.70 and k >= 0.60
    return {"decided": len(cal), "of": sum(1 for s in key if key[s]["kind"] == "cal"), "agreement": round(po, 3),
            "kappa": None if k is None else round(k, 3), "gate": "PASS" if ok else "FAIL"}


def strat(rows, Wh, ind, den=None):
    """Stratified estimate of sum_h W_h mean(ind) (or a ratio to den), with a 95 % interval."""
    est = var = dsum = 0.0
    for h, W in enumerate(Wh):
        r = [x for x in rows if x["stratum"] == h]
        n = len(r)
        if not n:
            continue
        y = [ind(x) for x in r]
        d = [den(x) for x in r] if den else [1.0] * n
        est += W * sum(y) / n; dsum += W * sum(d) / n
        if n > 1:
            var += W * W * (sum(v * v for v in y) / n - (sum(y) / n) ** 2) * n / (n - 1) / n
    if den:                                                    # ratio: the linearised variance, approximately
        rr = est / dsum if dsum else float("nan")
        var = 0.0
        for h, W in enumerate(Wh):
            r = [x for x in rows if x["stratum"] == h]
            n = len(r)
            if n > 1:
                z = [ind(x) - rr * den(x) for x in r]
                m = sum(z) / n
                var += W * W * sum((v - m) ** 2 for v in z) / (n - 1) / n
        var /= dsum * dsum if dsum else 1
        est = rr
    se = math.sqrt(max(var, 0.0))
    return {"est": round(est, 4), "lo": round(est - 1.96 * se, 4), "hi": round(est + 1.96 * se, 4)}


def score(key, lab, Wh, classes):
    rows = [dict(key[s], ref=LETTERS.index(lab[s])) for s in key if key[s]["kind"] == "r2" and lab.get(s, "u") != "u"]
    out = {"rows": len(rows), "unsure": sum(1 for s in key if key[s]["kind"] == "r2" and lab.get(s, "u") == "u"),
           "per_stratum": [sum(1 for r in rows if r["stratum"] == h) for h in range(len(Wh))], "overall": {}}
    for m in MAPS:
        out["overall"][m] = strat(rows, Wh, lambda r, m=m: float(r["maps"][m] == r["ref"]))
        if m.endswith("4"):
            out["overall"][m + "_on_four_class_reference"] = strat(rows, Wh, lambda r, m=m: float(r["maps"][m] == r["ref"]),
                                                                   den=lambda r: float(r["ref"] < 4))
    cls = {}
    for k, name in enumerate(classes):
        area = strat(rows, Wh, lambda r, k=k: float(r["ref"] == k))
        nk = [r for r in rows if r["stratum"] == k]
        ua = sum(r["ref"] == k for r in nk) / len(nk) if nk else None
        pa = Wh[k] * ua / area["est"] if ua is not None and area["est"] > 0 else None
        cls[name] = {"mapped_share": round(Wh[k], 4), "reference_share": area,
                     "users": None if ua is None else round(ua, 3), "producers": None if pa is None else round(pa, 3)}
    out["svm7_classes"] = cls
    return out


def rehearse():
    key = json.load(open(KEY, encoding="utf-8"))
    K, Wh = key["slots"], key["Wh"]
    rnd = random.Random(1)
    perfect = {s: LETTERS[v["polygon"]] if v["kind"] == "cal" else LETTERS[v["maps"]["svm7"]] for s, v in K.items()}
    noise = {s: rnd.choice(LETTERS) for s in K}
    allu = {s: "u" for s in K}
    sc = score(K, perfect, Wh, key["classes"])
    checks = [("perfect calibration passes", gate(K, perfect)["gate"] == "PASS"),
              ("random letters fail the gate", gate(K, noise)["gate"] == "FAIL"),
              ("all unsure fails the gate", gate(K, allu)["gate"] == "FAIL"),
              ("labels = the seven-class SVM give it accuracy 1", sc["overall"]["svm7"]["est"] == 1.0),
              ("then every stratum's user's accuracy is 1", all(c["users"] == 1.0 for c in sc["svm7_classes"].values())),
              ("then reference shares equal mapped shares", all(abs(c["reference_share"]["est"] - c["mapped_share"]) < 1e-3
                                                                for c in sc["svm7_classes"].values())),
              ("the weights sum to 1", abs(sum(Wh) - 1) < 1e-6)]
    flip = dict(perfect)                                       # one stratum wrong: accuracy drops by its weight
    for s, v in K.items():
        if v["kind"] == "r2" and v["stratum"] == 3:
            flip[s] = "c" if perfect[s] != "c" else "h"
    checks.append(("one stratum wrong costs exactly its weight",
                   abs(score(K, flip, Wh, key["classes"])["overall"]["svm7"]["est"] - (1 - Wh[3])) < 1e-3))
    for name, ok in checks:
        print("PASS" if ok else "FAIL", name)
    return all(ok for _, ok in checks)


def read_labels(path):
    if path.lower().endswith(".txt"):                         # answers.txt: "A1 n" per line, # comments
        lab = {}
        for line in open(path, encoding="utf-8"):
            parts = line.split("#")[0].split()
            if len(parts) == 2:
                lab[parts[0].upper()] = parts[1].lower()
        return lab
    return json.load(open(path, encoding="utf-8"))


def main():
    if "--rehearse" in sys.argv:
        sys.exit(0 if rehearse() else 1)
    key = json.load(open(KEY, encoding="utf-8"))
    lab = read_labels(sys.argv[1])
    lab = {s: v for s, v in lab.items() if s in key["slots"]}
    bad = {s: v for s, v in lab.items() if v not in LETTERS + "u"}
    if bad or set(lab) != set(key["slots"]):
        sys.exit("refused: letters %s; slots missing %s" % (bad, sorted(set(key["slots"]) - set(lab))[:10]))
    waived = "--waive-gate" in sys.argv                         # the author's word, 2026-11-02 (KB §69.55)
    res = {"gate": gate(key["slots"], lab), "labeller": "author" if "--author" in sys.argv else
           "agent, gate waived by the author (KB 69.55)" if waived else "agent"}
    if res["gate"]["gate"] == "PASS" or "--author" in sys.argv or waived:
        res.update(score(key["slots"], lab, key["Wh"], key["classes"]))
    print(json.dumps(res, indent=1, ensure_ascii=False))
    if "--out" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
