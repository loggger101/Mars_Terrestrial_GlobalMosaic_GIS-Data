# -*- coding: utf-8 -*-
"""Audit the PROJECT RECORD itself: PROJECT-KNOWLEDGE.md and the memory files.

Not a data check - a bookkeeping check. It exists because an audit on
2026-09-18 found four stale claims and six dead script references that had
accumulated by adding new sections without reconciling older ones, plus three
Windows-path escape bugs that made find-and-replace silently miss.

Run it after editing the knowledge base:
  <ArcGIS python.exe> audit_record.py
(plain system Python works too - nothing here needs arcpy.)
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import io, os, re, glob

BS   = chr(92)
ROOT = r"Z:\Mars Remote Sensing Project"
KB   = os.path.join(ROOT, "PROJECT-KNOWLEDGE.md")
BUILD= os.path.join(ROOT, "build")
MEM  = r"C:\Users\Loggg\.claude\projects\Z--\memory"
fails = []

def check(label, ok, detail=""):
    print("  %-4s %-46s %s" % ("ok" if ok else "FAIL", label, detail))
    if not ok:
        fails.append(label)

print("=== PROJECT-KNOWLEDGE.md ===")
s = io.open(KB, encoding="utf-8").read()
L = s.split("\n")
nums = [int(l.split(".")[0][3:]) for l in L if l.startswith("## ") and l[3:4].isdigit()]
check("sections sequential, no duplicates", nums == list(range(1, len(nums)+1)), "1-%d" % max(nums))
srefs = sorted({int(x) for x in re.findall(r"\u00a7(\d+)", s)})
dead = [r for r in srefs if r not in nums]
check("every \u00a7N cross-reference resolves", not dead, "dead: %s" % dead if dead else "")

refs = set()
for part in s.split("build" + BS)[1:]:
    tok = ""
    for ch in part:
        if ch.isalnum() or ch in "_.": tok += ch
        else: break
    if tok.endswith(".py"): refs.add(tok)
miss = [r for r in sorted(refs) if not os.path.isfile(os.path.join(BUILD, r))]
check("every named build script exists", not miss, "missing: %s" % miss if miss else "%d refs" % len(refs))

ctrl = sum(s.count(c) for c in map(chr, list(range(0, 9)) + [11, 12] + list(range(14, 32))))
check("no stray control characters", ctrl == 0, "%d found (\f \t \v from non-raw paths)" % ctrl)
check("no mojibake", s.count("\ufffd") == 0)

i = 0; badtbl = 0
while i < len(L)-1:
    if L[i].strip().startswith("|") and set(L[i+1].strip()) <= set("|-: "):
        n = L[i].count("|"); j = i+2
        while j < len(L) and L[j].strip().startswith("|"):
            if L[j].count("|") != n: badtbl += 1
            j += 1
        i = j
    else:
        i += 1
check("tables well formed", badtbl == 0, "%d bad rows" % badtbl)

print("  --   tags: [V] %d   [E] %d   [?] %d   (%d lines)"
      % (s.count("[V]"), s.count("[E]"), s.count("[?]"), len(L)))

print("\n=== ground truth vs what the record claims ===")
nroot = len(glob.glob(r"Z:\*.tif"))
check("Z: root raster count matches \u00a73", ("**%s** global GeoTIFFs" %
      {3: "Three", 4: "**Four**"}.get(nroot, nroot)).replace("****", "**") in s or
      ("**Four** global GeoTIFFs" in s and nroot == 4), "%d on disk" % nroot)
try:
    import arcpy
    arcpy.env.workspace = r"Z:\Mars Project\Mars Project.gdb"
    nfc = len(arcpy.ListFeatureClasses()); nr = len(arcpy.ListRasters())
    check("gdb feature-class count matches \u00a76", "%d present" % nfc in s, "%d in gdb" % nfc)
    check("gdb raster count matches \u00a713.2", "%d rasters" % nr in s, "%d in gdb" % nr)
except ImportError:
    print("  --   arcpy unavailable; gdb counts not checked")

print("\n=== figures have scripts ===")
imgdir = os.path.join(BUILD, "pres1_img")
scripts = glob.glob(os.path.join(BUILD, "make_*.py"))
orphan = []
for f in sorted(os.listdir(imgdir)):
    if not f.startswith("ius_"): continue
    if not any(f in io.open(m, encoding="utf-8").read() for m in scripts):
        orphan.append(f)
check("every type-area figure is reproducible", not orphan, "orphans: %s" % orphan if orphan else "")

print("\n=== memory ===")
mf = [f for f in glob.glob(os.path.join(MEM, "*.md")) if os.path.basename(f) != "MEMORY.md"]
names, badfm = set(), []
for f in mf:
    t = io.open(f, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        badfm.append(os.path.basename(f)); continue
    nm = re.search(r"^name:\s*(\S+)", m.group(1), re.M)
    ty = re.search(r"^\s*type:\s*(\S+)", m.group(1), re.M)
    if not nm or nm.group(1) != os.path.splitext(os.path.basename(f))[0]: badfm.append(os.path.basename(f))
    elif not ty or ty.group(1) not in ("user", "feedback", "project", "reference"): badfm.append(os.path.basename(f))
    if nm: names.add(nm.group(1))
check("frontmatter valid on every memory", not badfm, "bad: %s" % badfm if badfm else "%d files" % len(mf))
broken = sorted({l for f in mf for l in re.findall(r"\[\[([^\]]+)\]\]",
                 io.open(f, encoding="utf-8").read()) if l not in names})
check("every [[wikilink]] resolves", not broken, "broken: %s" % broken if broken else "")
idx = io.open(os.path.join(MEM, "MEMORY.md"), encoding="utf-8").read()
linked = set(re.findall(r"\]\(([^)]+\.md)\)", idx))
actual = {os.path.basename(f) for f in mf}
check("index lists every memory", not (actual - linked), "unindexed: %s" % sorted(actual - linked))
check("index has no dangling rows", not (linked - actual), "dangling: %s" % sorted(linked - actual))

print("\n%s  (%d check%s failed)" % ("ALL CHECKS PASS" if not fails else "FAILURES: " + ", ".join(fails),
      len(fails), "" if len(fails) == 1 else "s"))
sys.exit(1 if fails else 0)
