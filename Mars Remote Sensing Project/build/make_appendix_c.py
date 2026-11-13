# -*- coding: utf-8 -*-
r"""The paper's Appendix C from the logs, nothing typed (KB §69.110): producer's accuracy by class and the overall
scores of each U-Net training on the windows, and accuracy on the 237 polygons in each held-out block.

Reads logs\v3_extras.json (make_v3_extras.py --report) and, once it exists, logs\v3_edf.json (make_v3_edf.py --report),
which adds a seventh column, "with squares" (run edf, the edifice retraining, D37), and logs3_edf2.json
(make_v3_edf.py --report --rerun), which adds an eighth, "rate fixed" (edf2, the same squares at the control's learning
rate, KB §69.126; its maps stand under the key edf in that file). Prints the rows of Tables
tab:perclass and tab:perblock as LaTeX, and the same as a Markdown table for the KB.

  py -3 make_appendix_c.py            prints the rows
  py -3 make_appendix_c.py --check    also checks that the paper's two tables hold exactly these rows
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "NEXT STUFF", "Final", "paper", "mars_global_mosaic.tex")
RUNS = [("unet_v2", "second set"), ("base", "third set"), ("rep", "trained again"), ("noth", "no thermal"),
        ("cut", "cut only"), ("add", "added only")]
CLASSES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground", "volcanic edifice", "apron", "fluvial channel"]
SETS = [("v2_polygons", "On the 237 polygons"), ("v3_polygons", "On the 1,652 polygons")]


def load():
    r = json.load(open(os.path.join(HERE, "logs", "v3_extras.json"), encoding="utf-8"))
    runs = list(RUNS)
    p = os.path.join(HERE, "logs", "v3_edf.json")
    if os.path.exists(p):
        e = json.load(open(p, encoding="utf-8"))
        for s, _ in SETS:
            r[s]["full"]["edf"] = e[s]["full"]["edf"]
            for b, row in e[s]["by_block"].items():
                r[s]["by_block"][b]["edf"] = row["edf"]
        runs.append(("edf", "with squares"))
    p = os.path.join(HERE, "logs", "v3_edf2.json")
    if os.path.exists(p):
        e = json.load(open(p, encoding="utf-8"))
        for s, _ in SETS:
            r[s]["full"]["edf2"] = e[s]["full"]["edf"]
            for b, row in e[s]["by_block"].items():
                r[s]["by_block"][b]["edf2"] = row["edf"]
        runs.append(("edf2", "rate fixed"))
    return r, runs


def perclass(r, runs):
    out = []
    for s, head in SETS:
        f = r[s]["full"]
        rows = [(c, ["%.1f" % (100 * f[k]["producers"][c]) for k, _ in runs]) for c in CLASSES]
        rows.append(("Accuracy", ["%.1f" % (100 * f[k]["accuracy"]) for k, _ in runs]))
        rows.append(("Balanced accuracy", ["%.1f" % (100 * f[k]["balanced"]) for k, _ in runs]))
        rows.append(("$\\kappa$", ["%.3f" % f[k]["kappa"] for k, _ in runs]))
        out.append((head, rows))
    return out


def perblock(r, runs):
    f = r["v2_polygons"]
    return [("$%s,\\,%s$" % tuple(b.split("_")), ["%.1f" % (100 * f["by_block"][b][k]) for k, _ in runs])
            for b in sorted(f["by_block"])]


def tex(label, cells):
    return "%s & %s \\\\" % (label, " & ".join(cells))


if __name__ == "__main__":
    r, runs = load()
    n = len(runs) + 1
    lines = [" & " + " & ".join(name for _, name in runs) + " \\\\"]
    for head, rows in perclass(r, runs):
        lines.append("\\multicolumn{%d}{l}{\\emph{%s}} \\\\" % (n, head))
        lines += [tex(c, v) for c, v in rows]
    blocks = [tex(b, v) for b, v in perblock(r, runs)]
    print("%% tab:perclass\n" + "\n".join(lines))
    print("%% tab:perblock\n" + "\n".join(blocks))
    print("\n| set | class or score | " + " | ".join(name for _, name in runs) + " |")
    print("|---|---|" + "---|" * len(runs))
    for head, rows in perclass(r, runs):
        for c, v in rows:
            print("| %s | %s | %s |" % (head[3:], c.replace("$\\kappa$", "κ"), " | ".join(v)))
    if "--check" in sys.argv:
        t = open(TEX, encoding="utf-8").read()
        norm = lambda x: re.sub(r"\s+", " ", x)
        body = norm(t)
        want = [x for x in lines[1:] if not x.startswith("\\multicolumn")] + blocks
        miss = [x for x in want if norm(x) not in body]
        print("\ncheck: %d of %d rows found in the paper" % (len(want) - len(miss), len(want)))
        for x in miss:
            print("  NOT in the paper:", x)
        sys.exit(1 if miss else 0)
