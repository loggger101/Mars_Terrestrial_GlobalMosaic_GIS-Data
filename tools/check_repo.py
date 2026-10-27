# -*- coding: utf-8 -*-
"""Checks the repository the way a visitor or a restore would hit it. Runs in CI on every push.

    python tools/check_repo.py

1. Every relative link and image in the project-page Markdown (README.md, docs/, exports/)
   points at a file or folder that exists, and a "#section" link at a heading of its page
   (GitHub's slug: lower case, punctuation dropped, spaces to hyphens).
2. Every Python file parses (syntax only: most need arcpy or GDAL to run).
3. No file is over GitHub's 100 MB limit.
4. CITATION.cff names the same title and repository URL as the README.
5. The counts the project page states match the tree: build scripts (README and docs/scripts.md)
   and layouts. Numbers typed into a page go stale silently; this catches it.
6. Every image and PDF in the tree is linked from docs/figures.md, so the figure index stays
   complete. The interim and final decks' layout crops (build/interim_img/NN_*, build/final_img/NN_*) are
   described there as a group each; the final paper's figures/ folder holds copies of figures listed there;
   build/interim_img/dark/ holds the deck's navy copies, rebuilt by make_interim_dark.py and git-ignored.
7. Every image a page shows inline has alt text and is at most 300 KB: bigger figures are shown as
   their docs/thumbs/ preview and linked in full. Each preview's source still has the SHA-256 that
   docs/thumbs/SOURCES.txt recorded, so a changed layout with a stale preview fails
   (rebuild with tools/make_thumbs.py).
8. Every number in the interim's text (interim.py), the final deck's (final.py) and the paper's .tex is in
   PROJECT-KNOWLEDGE.md (build/verify_interim.py on each), and build/score_metrics.py, rerun on the committed
   logs, gives what build/logs/score_metrics.json holds (NEXT-STEPS §13.1 P1, KB §69.19).
9. Every layer in exports/README.md has a description, and none with rows calls itself empty (§13.1 P3): the
   text comes from github_export_gdb.py's ABOUT, the counts from the export, and the two drift apart.

Exit code 1 and a list of failures if anything is wrong. Stdlib only.
"""
import ast, hashlib, json, os, re, subprocess, sys, tempfile, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "Mars Remote Sensing Project" / "build"
# The documents whose every number must be in the record (verify_interim.py takes each as its argument).
DOCUMENTS = [BUILD / "interim.py", BUILD / "final.py",
             ROOT / "Mars Remote Sensing Project" / "NEXT STUFF" / "Final" / "paper" / "mars_global_mosaic.tex"]
PAGES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), ROOT / "exports" / "README.md"]
LINK = re.compile(r"!?\[[^\]]*\]\(<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\)")
HTML = re.compile(r"""\b(?:src|href)=["']([^"']+)["']""")
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"}
SHOWN_MD = re.compile(r"!\[([^\]]*)\]\(<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\)")
SHOWN_HTML = re.compile(r"<img\b[^>]*>")
INLINE_MAX = 300 * 1000                       # bytes; tools/make_thumbs.py uses the same limit
THUMBS = ROOT / "docs" / "thumbs"
fails = []


def targets(page):
    """The relative link and image targets of one page, as (as written, resolved path)."""
    text = re.sub(r"```.*?```", "", page.read_text(encoding="utf-8"), flags=re.S)
    for target in LINK.findall(text) + HTML.findall(text):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        yield target, (page.parent / urllib.parse.unquote(target.split("#")[0])).resolve()


def anchors(md):
    """The "#section" names GitHub gives a page's headings."""
    text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
    seen, out = {}, set()
    for h in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)
        s = re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-")
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    return out


def links():
    n = 0
    for page in PAGES:
        for target, path in targets(page):
            n += 1
            if not path.exists():
                fails.append(f"broken link in {page.relative_to(ROOT)}: {target}")
        text = re.sub(r"```.*?```", "", page.read_text(encoding="utf-8"), flags=re.S)
        for target in LINK.findall(text) + HTML.findall(text):   # "#section" links, on this page or another
            if "#" not in target or re.match(r"[a-z]+:", target):
                continue
            path, frag = target.split("#", 1)
            md = page if not path else (page.parent / urllib.parse.unquote(path)).resolve()
            if md.suffix == ".md" and md.exists() and urllib.parse.unquote(frag).lower() not in anchors(md):
                fails.append(f"no heading for #{frag} in {page.relative_to(ROOT)}: {target}")
    return n


def figures():
    page = ROOT / "docs" / "figures.md"
    linked = {path for _, path in targets(page)}
    crop = re.compile(r"\d\d_")                   # the interim and final decks' layout crops, one group each
    files = [p for p in ROOT.rglob("*") if p.suffix.lower() in IMAGES and ".git" not in p.parts]
    for p in files:
        if p.parent.name in ("interim_img", "final_img") and crop.match(p.name):
            continue
        if p.parent.name == "figures" and p.parent.parent.name == "paper":
            continue                              # the final paper's copies of figures listed elsewhere
        if p.parent.name == "dark" and p.parent.parent.name == "interim_img":
            continue                              # navy copies for the deck: rebuilt by make_interim_dark.py, not tracked
        if p.resolve() not in linked:
            fails.append(f"not in docs/figures.md: {p.relative_to(ROOT)}")
    return len(files)


def shown():
    """Images displayed inline: alt text, and small enough that the page stays light."""
    n = 0
    for page in PAGES:
        text = re.sub(r"```.*?```", "", page.read_text(encoding="utf-8"), flags=re.S)
        found = [(alt, src) for alt, src in SHOWN_MD.findall(text)]
        for tag in SHOWN_HTML.findall(text):
            src = re.search(r"""\bsrc=["']([^"']+)["']""", tag)
            alt = re.search(r"""\balt=["']([^"']*)["']""", tag)
            found.append((alt.group(1) if alt else "", src.group(1) if src else ""))
        for alt, src in found:
            if re.match(r"[a-z]+:", src):
                continue                             # the CI badge and other remote images
            n += 1
            where = f"{page.relative_to(ROOT)}: {src}"
            if len(alt.strip()) < 8 or alt.strip().isdigit():
                fails.append(f"image without descriptive alt text in {where}")
            path = (page.parent / urllib.parse.unquote(src)).resolve()
            if path.is_file() and path.suffix.lower() != ".svg" and path.stat().st_size > INLINE_MAX:
                fails.append(f"image over {INLINE_MAX // 1000} KB shown inline in {where}: show its docs/thumbs preview")
    return n


def thumbs():
    """Each preview's source unchanged since tools/make_thumbs.py drew it."""
    manifest = THUMBS / "SOURCES.txt"
    listed = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, name, src = line.split("  ", 2)
        listed.add(name)
        source = ROOT / src
        if not (THUMBS / name).is_file():
            fails.append(f"preview missing: docs/thumbs/{name}")
        if not source.is_file():
            fails.append(f"preview's source gone: {src} (rerun tools/make_thumbs.py)")
        elif hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            fails.append(f"stale preview docs/thumbs/{name}: {src} changed (rerun tools/make_thumbs.py)")
    for p in THUMBS.glob("*.jpg"):
        if p.name not in listed:
            fails.append(f"preview not in docs/thumbs/SOURCES.txt: {p.name}")
    return len(listed)


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


def run(*args):
    """One of the build's stdlib scripts, as CI's Python runs it; (exit code, its output)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, *map(str, args)], cwd=BUILD, env=env, capture_output=True,
                       text=True, encoding="utf-8", stdin=subprocess.DEVNULL, timeout=300)
    return p.returncode, (p.stdout + p.stderr).strip()


def numbers(documents=DOCUMENTS, scores=BUILD / "logs" / "score_metrics.json"):
    for doc in documents:
        code, out = run(BUILD / "verify_interim.py", doc)
        if code:
            fails.append(f"numbers not in the record: {doc.relative_to(ROOT)}\n    " + out.replace("\n", "\n    "))
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "score_metrics.json"
        code, out = run(BUILD / "score_metrics.py", "--out", fresh)
        if code or not fresh.exists():
            fails.append(f"score_metrics.py failed on the committed logs (exit {code}): {out[-300:]}")
        elif json.loads(fresh.read_text(encoding="utf-8")) != json.loads(scores.read_text(encoding="utf-8")):
            fails.append(f"build/logs/{scores.name} is not what score_metrics.py gives on the committed logs: rerun it")
    return len(documents) + 1


def layers(page=ROOT / "exports" / "README.md"):
    rows = 0
    for line in page.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `([^`]+)` \| [^|]+ \| ([\d,]+) \| [^|]+ \|(.*?)\|", line)
        if not m:
            continue
        rows += 1
        name, n, about = m.group(1), int(m.group(2).replace(",", "")), m.group(3).strip()
        if not about:
            fails.append(f"exports/README.md: {name} has no description (github_export_gdb.py's ABOUT)")
        elif n and re.search(r"\bempty\b", about, re.I):
            fails.append(f"exports/README.md: {name} has {n:,} rows but its description says it is empty")
    if not rows:
        fails.append("exports/README.md: no layer rows found")
    return rows


if __name__ == "__main__":
    print(f"links checked:   {links()}")
    print(f"python files:    {python()}")
    print(f"files sized:     {sizes()}")
    print(f"counts checked:  {counts()}")
    print(f"figures indexed: {figures()}")
    print(f"images shown:    {shown()}")
    print(f"previews:        {thumbs()}")
    print(f"number checks:   {numbers()}")
    print(f"layers described: {layers()}")
    citation()
    for f in fails:
        print("FAIL", f)
    print("ALL CHECKS PASS" if not fails else f"{len(fails)} FAILED")
    sys.exit(1 if fails else 0)
