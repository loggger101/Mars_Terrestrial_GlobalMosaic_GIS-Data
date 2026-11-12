# -*- coding: utf-8 -*-
r"""The edifice retraining's report (logs\v3_edf.json, make_v3_edf.py --report; D37) as text: the tables for its KB
section and E1-E5 each with the numbers that decided it, read from the log and typed by no one. It judges nothing:
the verdicts printed are the log's own "predictions", and each line beside them only shows the numbers.

  py -3 summarise_v3_edf.py [--json <another v3_edf.json>]
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
P = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else os.path.join(HERE, "logs", "v3_edf.json")
CLASSES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground", "volcanic edifice", "apron", "fluvial channel"]
pc = lambda x: "—" if x is None else "%.1f" % (100 * x)
pt = lambda x: "%+.1f" % (100 * x)
ci = lambda d, k: "%s to %s" % (pt(d[k][0]), pt(d[k][1]))


def table(head, rows):
    print("\n| " + " | ".join(head) + " |\n|" + "---|" * len(head))
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")


if __name__ == "__main__":
    r = json.load(open(P, encoding="utf-8"))
    v2, v3, vp = r["v2_polygons"], r["v3_polygons"], r["validation_polygons"]
    sw, vw = r["standard_windows"], r["validation_windows"]
    runs = ["base", "rep", "freshw", "edf"]
    print("log %s, written %s; %d block resamples, seed %s" % (os.path.basename(P), r.get("when"), r.get("boot"), r.get("seed")))

    print("\n**Test: the 14 held-out blocks' windows** (%d and %d polygons with pixels)" % (v2["polygons"], v3["polygons"]))
    rows = []
    for name, f in (("237 v2", v2), ("1,652 v3", v3)):
        for m, lab in (("accuracy", "accuracy"), ("balanced", "balanced accuracy")):
            rows.append([name, lab] + [pc(f["full"][k][m]) for k in runs])
        rows.append([name, "κ"] + ["%.3f" % f["full"][k]["kappa"] for k in runs])
        for c in CLASSES:
            rows.append([name, "producer's, " + c] + [pc(f["full"][k]["producers"][c]) for k in runs])
    table(["polygons", "score", "base", "rep", "freshw", "edf"], rows)

    rows = []
    for name, f in (("237 v2", v2), ("1,652 v3", v3)):
        for pair in sorted(f["block_bootstrap"]):
            d = f["block_bootstrap"][pair]
            if "-" in pair and isinstance(d, dict) and "accuracy_ci95" in d:
                rows.append([name, pair.replace("-", " − "), ci(d, "accuracy_ci95"), ci(d, "balanced_ci95")])
    table(["polygons", "difference", "accuracy, 95 % by block (points)", "balanced accuracy"], rows)

    for title, w, names in (("the held-out blocks' windows", sw, runs), ("the validation blocks' windows", vw, ["fresh", "edfv"])):
        print("\n**Areas on %s** (share of the ground every map of the set holds; groups' shares of that ground: %s)"
              % (title, ", ".join("%s %s" % (k, pc(x)) for k, x in w["group_share_of_ground"].items())))
        table(["class, % of the ground"] + names, [[c] + [pc(w[k]["classes"][c]) for k in names] for c in CLASSES])
        table(["volcanic edifice, % of each unit group"] + names,
              [[g] + [pc(w[k]["edifice"][g]) for k in names] for g in w["group_share_of_ground"]])

    print("\n**Validation: fresh's 14 blocks** (%d polygons with pixels)" % vp["polygons"])
    table(["score", "fresh", "edfv"],
          [[lab] + [pc(vp["full"][k][m]) for k in ("fresh", "edfv")] for m, lab in (("accuracy", "accuracy"), ("balanced", "balanced accuracy"))]
          + [["κ"] + ["%.3f" % vp["full"][k]["kappa"] for k in ("fresh", "edfv")]]
          + [["producer's, " + c] + [pc(vp["full"][k]["producers"][c]) for k in ("fresh", "edfv")] for c in CLASSES])
    d = vp["block_bootstrap"].get("edfv-fresh")
    if d:
        print("edfv − fresh by block: accuracy %s, balanced accuracy %s points" % (ci(d, "accuracy_ci95"), ci(d, "balanced_ci95")))

    print("\n**The six Syrtis Major edifice polygons** (share of their ground each map calls each class; base 7.7 % edifice, §69.105)")
    table(["map"] + CLASSES, [[k] + [pc((r["syrtis_edifice"][k] or {}).get(c)) for c in CLASSES] for k in runs])

    off = lambda w, k: w[k]["edifice"]["off_edifice_units"]
    pe = lambda f, k: f["full"][k]["producers"]["volcanic edifice"]
    v = r["predictions"]
    print("\n**Predictions** (the log's verdicts; the numbers beside each)")
    print("- E1 %s: validation accuracy edfv %s against fresh %s, %s points apart (bound 3)."
          % (v["E1"], pc(vp["full"]["edfv"]["accuracy"]), pc(vp["full"]["fresh"]["accuracy"]),
             "%.2f" % (100 * abs(vp["full"]["edfv"]["accuracy"] - vp["full"]["fresh"]["accuracy"]))))
    print("- E2 %s: edifice off the edifice units on the validation windows, edfv %s against fresh %s."
          % (v["E2"], pc(off(vw, "edfv")), pc(off(vw, "fresh"))))
    print("- E3 %s: accuracy edf against base, %s against %s on the 237 polygons and %s against %s on the 1,652 (%s and %s points apart, bound 3)."
          % (v["E3"], pc(v2["full"]["edf"]["accuracy"]), pc(v2["full"]["base"]["accuracy"]), pc(v3["full"]["edf"]["accuracy"]),
             pc(v3["full"]["base"]["accuracy"]), "%.2f" % (100 * abs(v2["full"]["edf"]["accuracy"] - v2["full"]["base"]["accuracy"])),
             "%.2f" % (100 * abs(v3["full"]["edf"]["accuracy"] - v3["full"]["base"]["accuracy"]))))
    print("- E4 %s: edifice off the edifice units on the held-out windows, edf %s against base %s, rep %s, freshw %s."
          % (v["E4"], pc(off(sw, "edf")), pc(off(sw, "base")), pc(off(sw, "rep")), pc(off(sw, "freshw"))))
    print("- E5 %s: producer's accuracy of volcanic edifice on the 1,652 polygons, edf %s against base %s and rep %s (floor %s)."
          % (v["E5"], pc(pe(v3, "edf")), pc(pe(v3, "base")), pc(pe(v3, "rep")), pc(min(pe(v3, "base"), pe(v3, "rep")) - 0.10)))
    print("- The rule: %s." % v["rule"])
