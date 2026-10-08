# -*- coding: utf-8 -*-
r"""Mirrors the project's small, irreplaceable files into the GitHub repo clone (KB §35).

    python github_sync.py               copy what changed, report, touch nothing else
    python github_sync.py --dry-run     report only
    python github_sync.py --commit      also git add / commit / push the repo

Repo: loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data, cloned by default at
~\OneDrive\Documents\GitHub\Mars_Terrestrial_GlobalMosaic_GIS-Data (--repo to override).

The drive is found from this script's own location, so it works as Z: on the laptop and F: on
the desktop alike. Z: is only ever READ.

What goes to the repo, mirrored under the same folder names as on the drive:
  Mars Remote Sensing Project\  everything except .npy caches and __pycache__
  Mars Project\                 the .aprx, models, logs, metadata sidecars, layouts: every file
                                except raster payloads (.tif/.ovr), the gdb and DL chips; .backups (the
                                .aprx snapshots from before git) included
  <drive root>\  -> drive-root\ sidecars of the four globals and the "new training" shapefile
Any single file over 95 MB is skipped and reported (GitHub refuses files over 100 MB).

What does not, and where it goes instead:
  Mars Project.gdb vectors      github_export_gdb.py writes them to exports\ in the repo
  rasters and .npy caches       github_release_bundle.py zips them for a GitHub release
  the four source globals       re-downloadable; the README gives the URLs
  Global60 derivatives, gdb rasters, DL chips: re-computable, and 300+ GB

Files that vanish from the drive are removed from the mirror too; git history keeps them.
Stdlib only: runs on either Python.
"""
import os, re, sys, shutil, subprocess, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DRIVE = Path(__file__).resolve().parents[2]
assert (DRIVE / "Mars Project").is_dir(), f"not the project drive: {DRIVE}"
REPO = Path(sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else
            Path.home() / "OneDrive" / "Documents" / "GitHub" / "Mars_Terrestrial_GlobalMosaic_GIS-Data")
DRY = "--dry-run" in sys.argv
MAX = 95 * 1000 * 1000

SKIP_DIRS = {"__pycache__", ".git", "Mars Project.gdb", "Index", "images", "labels",
             "System Volume Information", "$RECYCLE.BIN",
             "Reference"}   # Mars Project\Reference: downloaded third-party data, not redistributed (KB §41)
SKIP_DIR_SUFFIX = (".crf", ".gdb")
# Dated snapshots of the record and scripts (.backup_YYYYMMDD, .py_backup_YYYYMMDD): history, kept on
# the drive and in git history, not on the project page (KB §39.4).
SKIP_DIR_PREFIX = (".backup_", ".py_backup_")
SKIP_FILES = {"neutral_voice.py"}
RASTER = {".tif", ".tiff", ".ovr", ".img", ".jp2"}


def keep_rsp(p):   # Mars Remote Sensing Project
    # neutral_voice.py lists the personal phrasings it removes, so it stays off the public page (KB §39.4)
    return p.suffix.lower() not in {".npy", ".pyc"} and p.name not in SKIP_FILES


def keep_mp(p):    # Mars Project
    return p.suffix.lower() not in RASTER


def keep_root(p):  # drive root, files only
    return p.suffix.lower() not in RASTER


TREES = [  # (source, destination in repo, recurse, filter)
    (DRIVE / "Mars Remote Sensing Project", "Mars Remote Sensing Project", True, keep_rsp),
    (DRIVE / "Mars Project", "Mars Project", True, keep_mp),
    (DRIVE, "drive-root", False, keep_root),
]


def walk(src, recurse, keep):
    if not recurse:
        yield from (p for p in src.iterdir() if p.is_file() and keep(p))
        return
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.endswith(SKIP_DIR_SUFFIX)
                   and not d.startswith(SKIP_DIR_PREFIX)
                   and not os.path.islink(os.path.join(root, d))]
        for f in files:
            p = Path(root) / f
            if keep(p):
                yield p


GROUPS = [  # (heading, predicate on the script name); first match wins
    ("Record and backup", lambda n: n.startswith(("audit_record", "github_"))),
    ("Ius Chasma type area", lambda n: n.startswith(("make_typearea_", "verify_typearea", "make_channel_",
                                                     "make_crater_", "make_landform_", "verify_crater_",
                                                     "verify_segmentation")) and "layouts" not in n),
    ("±60° analysis extent", lambda n: n.startswith(("grid60", "make_extent", "make_global_", "make_global60_",
                                                     "verify_global60", "svmcheck", "verify_svm_"))
                                       and n != "make_global60_maps.py"),
    ("ArcGIS project: maps and layouts", lambda n: n in {"layoutkit.py", "polish_layouts.py", "make_global60_maps.py",
                                                         "make_candidate_maps.py", "make_typearea_layouts.py",
                                                         "repoint_junction_layers.py", "audit_aprx.py",
                                                         "audit_layers.py", "fix_night_stretch.py"}),
    ("Figures", lambda n: n.startswith(("make_fig", "make_glob", "make_locator", "make_panels", "make_spectrum",
                                        "make_zoom", "make_extra", "marsfig", "optimise_", "img_contrast"))),
    ("Deliverables and their checks", lambda n: n.startswith(("build_", "content", "deck_", "le_theme", "pdf_pages",
                                                              "audit_", "verify_all", "verify2", "render"))),
    ("Reading the geodatabase and rasters", lambda n: True),
]


def write_script_index():
    """docs\\scripts.md in the repo: every build script, grouped, with its own docstring's first line."""
    import ast
    build = DRIVE / "Mars Remote Sensing Project" / "build"
    rows = {g: [] for g, _ in GROUPS}
    srcs = {p.stem: p.read_text(encoding="utf-8", errors="replace") for p in sorted(build.glob("*.py"))
            if p.name not in SKIP_FILES}
    # Which interpreter: arcpy/osgeo need ArcGIS's, pptx the system one, inherited through local imports.
    imported = {k: set(re.findall(r"^\s*(?:import|from) (\w+)", s, re.M)) for k, s in srcs.items()}
    needs = {k: {m for m, mods in (("ArcGIS", {"arcpy", "osgeo"}), ("system", {"pptx"})) if imported[k] & mods}
             for k in srcs}
    changed = True
    while changed:
        changed = False
        for k in srcs:
            inherited = set().union(*(needs[m] for m in imported[k] if m in needs and m != k))
            if not inherited <= needs[k]:
                needs[k] |= inherited
                changed = True
    for stem, src in srcs.items():
        p = build / f"{stem}.py"
        try:
            doc = (ast.get_docstring(ast.parse(src)) or "").strip()
        except SyntaxError:
            doc = ""
        first = " ".join(doc.split("\n\n")[0].split())
        py = " + ".join(sorted(needs[stem])) or "either"
        link = "../Mars%20Remote%20Sensing%20Project/build/" + p.name
        group = next(g for g, test in GROUPS if test(p.name))
        rows[group].append(f"| [`{p.name}`]({link}) | {py} | {first.replace('|', '/') or '(no docstring)'} |")
    for p in sorted(build.glob("*.ps1")):   # the Office renderers: their opening comment is the description
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        first = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("#") else ""
        link = "../Mars%20Remote%20Sensing%20Project/build/" + p.name
        group = next(g for g, test in GROUPS if test(p.name))
        rows[group].append(f"| [`{p.name}`]({link}) | PowerShell + Office | {first.replace('|', '/') or '(no header)'} |")
    out = ["# The build scripts", "",
           f"All {sum(map(len, rows.values()))} scripts in `Mars Remote Sensing Project/build/`, grouped by what they "
           "make. The description is each script's own docstring. **Python** says which interpreter it needs: "
           "*ArcGIS* (arcpy or GDAL: `C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe`), "
           "*system* (python-pptx), or *either*; the three `.ps1` renderers need PowerShell and Microsoft Office. "
           "Generated by `github_sync.py`; don't edit it here.", ""]
    for g, _ in GROUPS:
        if rows[g]:
            out += [f"## {g}", "", "| Script | Python | What it does |", "|---|---|---|", *rows[g], ""]
    path = REPO / "docs" / "scripts.md"
    text = "\n".join(out)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def same(a, b):
    if not b.exists():
        return False
    sa, sb = a.stat(), b.stat()
    return sa.st_size == sb.st_size and int(sa.st_mtime) == int(sb.st_mtime)


def main():
    assert REPO.is_dir() and (REPO / ".git").exists(), f"clone the repo first: {REPO}"
    copied, unchanged, too_big, removed = [], 0, [], []
    for src, dst, recurse, keep in TREES:
        wanted = set()
        for p in walk(src, recurse, keep):
            rel = p.relative_to(src)
            if p.stat().st_size > MAX:
                too_big.append((p, p.stat().st_size))
                continue
            out = REPO / dst / rel
            wanted.add(out)
            if same(p, out):
                unchanged += 1
                continue
            copied.append(out.relative_to(REPO))
            if not DRY:
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, out)
        top = REPO / dst
        if top.is_dir():
            for p in list(top.rglob("*")):
                if p.is_file() and p not in wanted:
                    removed.append(p.relative_to(REPO))
                    if not DRY:
                        p.unlink()

    tag = "would copy" if DRY else "copied"
    print(f"drive {DRIVE}  ->  repo {REPO}")
    print(f"{tag} {len(copied)}, unchanged {unchanged}, removed {len(removed)}, too big {len(too_big)}")
    for c in copied[:40]:
        print("  +", c)
    if len(copied) > 40:
        print(f"  ... and {len(copied) - 40} more")
    for r in removed:
        print("  -", r)
    for p, s in too_big:
        print(f"  SKIPPED (> 95 MB, {s / 1e6:.0f} MB): {p}")
    if not DRY and write_script_index():
        print("  docs\\scripts.md regenerated")

    if "--commit" in sys.argv and not DRY:
        git = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], check=True)
        git("add", "-A")
        if subprocess.run(["git", "-C", str(REPO), "diff", "--cached", "--quiet"]).returncode:
            git("commit", "-m", f"Sync from the project drive, {time.strftime('%Y-%m-%d')}")
            git("push")
        else:
            print("nothing to commit")


if __name__ == "__main__":
    main()
