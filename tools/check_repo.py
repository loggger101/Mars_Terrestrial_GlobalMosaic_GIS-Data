# -*- coding: utf-8 -*-
"""Checks the repository the way a visitor or a restore would hit it. Runs in CI on every push.

    python tools/check_repo.py

1. Every relative link and image in the project-page Markdown (README.md, docs/, exports/)
   points at a file or folder that exists.
2. Every Python file parses (syntax only: most need arcpy or GDAL to run).
3. No file is over GitHub's 100 MB limit.
4. CITATION.cff names the same title and repository URL as the README.
5. The counts the project page states match the tree: build scripts (README and docs/scripts.md)
   and layouts. Numbers typed into a page go stale silently; this catches it.
6. Every image and PDF in the tree is linked from docs/figures.md, so the figure index stays
   complete. The interim deck's layout crops (build/interim_img/NN_*) are described there as a group.

Exit code 1 and a list of failures if anything is wrong. Stdlib only.
"""
import ast, re, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), ROOT / "exports" / "README.md"]
LINK = re.compile(r"!?\[[^\]]*\]\(<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\)")
HTML = re.compile(r"""\b(?:src|href)=["']([^"']+)["']""")
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"}
fails = []


def targets(page):
    """The relative link and image targets of one page, as (as written, resolved path)."""
    text = re.sub(r"```.*?```", "", page.read_text(encoding="utf-8"), flags=re.S)
    for target in LINK.findall(text) + HTML.findall(text):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        yield target, (page.parent / urllib.parse.unquote(target.split("#")[0])).resolve()


def links():
    n = 0
    for page in PAGES:
        for target, path in targets(page):
            n += 1
            if not path.exists():
                fails.append(f"broken link in {page.relative_to(ROOT)}: {target}")
    return n


def figures():
    page = ROOT / "docs" / "figures.md"
    linked = {path for _, path in targets(page)}
    crop = re.compile(r"\d\d_")                   # the interim deck's layout crops, one group
    files = [p for p in ROOT.rglob("*") if p.suffix.lower() in IMAGES and ".git" not in p.parts]
    for p in files:
        if p.parent.name == "interim_img" and crop.match(p.name):
            continue
        if p.resolve() not in linked:
            fails.append(f"not in docs/figures.md: {p.relative_to(ROOT)}")
    return len(files)


def python():
    files = [p for p in ROOT.rglob("*.py") if ".git" not in p.parts]
    for p in files:
        try:
            ast.parse(p.read_bytes(), filename=str(p))
        except SyntaxError as e:
            fails.append(f"syntax error: {p.relative_to(ROOT)}:{e.lineno}: {e.msg}")
    return len(files)


def sizes():
    files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    for p in files:
        if p.stat().st_size > 100 * 1000 * 1000:
            fails.append(f"over 100 MB: {p.relative_to(ROOT)}")
    return len(files)


def citation():
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    url = re.search(r"^repository-code:\s*\"?([^\"\n]+)", cff, re.M)
    if not url or url.group(1).strip() not in readme:
        fails.append("CITATION.cff repository-code is missing or not the README's URL")
    if "Mars Global Mosaic" not in cff:
        fails.append("CITATION.cff title does not name the Mars Global Mosaic")


def counts():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    index = (ROOT / "docs" / "scripts.md").read_text(encoding="utf-8")
    build = ROOT / "Mars Remote Sensing Project" / "build"
    mp = ROOT / "Mars Project"
    scripts = len(list(build.glob("*.py"))) + len(list(build.glob("*.ps1")))
    stated = [  # (what, page text, pattern, actual)
        ("build scripts", readme, r"build/\s+(\d+) scripts", scripts),
        ("build scripts", readme, r"\[build scripts\]\([^)]*\) \(all (\d+),", scripts),
        ("build scripts", index, r"All (\d+) scripts", scripts),
        ("rows in the script index", index, None, scripts),
        ("layouts", readme, r"Mars Project\.aprx\s+.*?(\d+) layouts", len(list(mp.glob("*/layouts/*.png")))),
    ]
    for what, text, pattern, actual in stated:
        if pattern is None:
            n = len(re.findall(r"^\| \[`", text, re.M))
        else:
            m = re.search(pattern, text)
            if not m:
                fails.append(f"count of {what} not found on its page (pattern {pattern})")
                continue
            n = int(m.group(1))
        if n != actual:
            fails.append(f"page says {n} {what}, the tree has {actual}")
    return len(stated)


if __name__ == "__main__":
    print(f"links checked:   {links()}")
    print(f"python files:    {python()}")
    print(f"files sized:     {sizes()}")
    print(f"counts checked:  {counts()}")
    print(f"figures indexed: {figures()}")
    citation()
    for f in fails:
        print("FAIL", f)
    print("ALL CHECKS PASS" if not fails else f"{len(fails)} FAILED")
    sys.exit(1 if fails else 0)
