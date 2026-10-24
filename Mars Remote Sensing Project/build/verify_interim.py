# -*- coding: utf-8 -*-
r"""Every number on the interim deck and report must be in the record (KB §45, INTERIM-PLAN §0).

interim.py holds all the interim's text. This pulls every number out of its strings (73.5%, 1,685,
−0.36, 2 h 52 m, 15.2 bn ...) and checks each appears in PROJECT-KNOWLEDGE.md, normalised for the
minus sign, thousands separators and a space before %. Structural numbers (section numbers, dates,
years, small integers 0-20) are ignored. Exits 1 and lists any number the record does not hold.

    python verify_interim.py            (either Python)
    python verify_interim.py final.py   the final's text (KB §69), the same way
    python verify_interim.py "..\NEXT STUFF\Final\paper\mars_global_mosaic.tex"   the paper's prose (KB §69.3)
"""
import os, re, sys, ast
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(os.path.dirname(HERE), "PROJECT-KNOWLEDGE.md")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "interim.py")   # a path: for planted-defect tests
NUM = re.compile(r"(?<![\w§.])[−\-+]?\d[\d,]*(?:\.\d+)?")


def norm(x):
    return x.replace("−", "-").replace(",", "").lstrip("+")


def rounds_from(n, kb_vals):
    """True if a more precise number in the record rounds to n (the slide says κ 0.52, the record 0.515).
    Round half up, as a reader would."""
    if "." not in n:
        return False
    d = len(n.split(".")[1])
    target = abs(float(n))
    step = 10 ** -d
    return any(abs(v - target) <= step / 2 + 1e-9 and v != target and len(repr(v).split(".")[-1]) > d
               for v in kb_vals)


def tex_strings(path):
    """The paper's prose, one paragraph at a time: the body without comments (the KB § notes), citations, labels,
    lengths or the address block, with LaTeX's spacing and percent signs made plain."""
    t = open(path, encoding="utf-8").read()
    t = t.split(r"\begin{document}", 1)[-1].split(r"\end{document}", 1)[0]
    t = re.sub(r"(?<!\\)%.*", "", t)
    t = re.sub(r"\\(?:cite[pt]?|citealt|label|ref|eqref|autoref|email|affiliation|includegraphics|input|url)"
               r"(?:\[[^\]]*\])*\{[^}]*\}", " ", t)
    t = re.sub(r"\\begin\{(?:tabular|table|figure)\*?\}(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", t)
    t = re.sub(r"[\d.]+\s*(?:\\(?:text|line|column)width|pt|em|ex|mm|cm|in)\b", " ", t)
    t = t.replace(r"\%", "%").replace("{,}", ",").replace(r"\times", "×").replace(r"\,", " ").replace("~", " ").replace("$", " ")
    for para in re.split(r"\n\s*\n", t):
        if para.strip():
            yield re.sub(r"\s+", " ", para)


def strings(path):
    if path.endswith(".tex"):
        yield from tex_strings(path)
        return
    tree = ast.parse(open(path, encoding="utf-8").read())
    doc = ast.get_docstring(tree) or ""
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value != doc:
            yield n.value


def numbers_in(text):
    text = re.sub(r"§\s*[\d.]+(?:[–-][\d.]+)?", " ", text)                  # section references
    text = re.sub(r"\b\d{1,2}\s+(?:Sep|Oct|Nov|Dec)\b|\b(?:19|20)\d\d\b", " ", text)   # dates, years
    text = re.sub(r"\bv\d+\b|MDIM \d\.\d|\d+-band|\d+ [x×] \d+", " ", text)   # versions, band counts, window sizes
    return {norm(m.group()) for m in NUM.finditer(text)}


def main():
    kb = open(KB, encoding="utf-8").read()
    kb_nums = {norm(m.group()) for m in NUM.finditer(kb.replace(" %", "%"))}
    kb_nums |= {n.lstrip("-") for n in kb_nums}
    kb_vals = set()
    for n in kb_nums:
        try:
            kb_vals.add(abs(float(n)))
        except ValueError:
            pass
    missing = {}
    for s in strings(SRC):
        for n in numbers_in(s):
            try:
                v = float(n)
            except ValueError:
                continue
            if v.is_integer() and 0 <= abs(v) <= 20:
                continue
            if n not in kb_nums and n.lstrip("-") not in kb_nums and not rounds_from(n, kb_vals):
                missing.setdefault(n, s[:90])
    checked = sum(len(numbers_in(s)) for s in strings(SRC))
    if missing:
        print("NOT IN THE RECORD (%d):" % len(missing))
        for n, s in sorted(missing.items()):
            print("  %-10s in: %s" % (n, s))
        sys.exit(1)
    print("all %d numbers in %s appear in PROJECT-KNOWLEDGE.md" % (checked, os.path.basename(SRC)))


if __name__ == "__main__":
    main()
