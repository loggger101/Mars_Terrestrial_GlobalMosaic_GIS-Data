# -*- coding: utf-8 -*-
r"""Mirrors the project's small, irreplaceable files into the GitHub repo clone (KB §35).

    python github_sync.py               copy what changed, report, touch nothing else
    python github_sync.py --dry-run     report only
    python github_sync.py --commit      also git add / commit / push the repo
    python github_sync.py --to-drive <commit> [--dry-run]
                                        the other way: files the clone changed since <commit>, onto the drive
    python github_sync.py --force       copy and remove even where the guard below refuses
    --drive <path>                      the drive's root, for running the clone's copy of this script

Repo: loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data, cloned by default at
~\OneDrive\Documents\GitHub\Mars_Terrestrial_GlobalMosaic_GIS-Data (--repo to override).

The drive is found from this script's own location, so it works as Z: on the laptop and F: on
the desktop alike. Z: is only ever READ.

What goes to the repo, mirrored under the same folder names as on the drive:
  Mars Remote Sensing Project\  everything except .npy caches and __pycache__
  Mars Project\                 the .aprx, models, logs, metadata sidecars, layouts: every file
                                except raster payloads (.tif/.ovr), the gdb and DL chips; not .backups
                                (the .aprx snapshots; git versions the .aprx itself, KB §57.6)
  <drive root>\  -> drive-root\ sidecars of the four globals (not "new training.*", KB §57.6)
Any single file over 95 MB is skipped and reported (GitHub refuses files over 100 MB).

What does not, and where it goes instead:
  Mars Project.gdb vectors      github_export_gdb.py writes them to exports\ in the repo
  rasters and .npy caches       github_release_bundle.py zips them for a GitHub release
  the four source globals       re-downloadable; the README gives the URLs
  Global60 derivatives, gdb rasters, DL chips: re-computable, and 300+ GB

Files that vanish from the drive are removed from the mirror too; git history keeps them.

The guard (NEXT-STEPS §13.1 P2, KB §69.19). Work done in the clone without the drive (the laptop) is newer than
the drive, and a plain sync would copy the drive's older files over it and delete the clone's new ones; it nearly
happened twice (KB §69.1, §69.19). So before copying anything the sync looks for a drive file whose bytes are an
older committed version of its path while the clone holds a later one. If there is any, the drive is behind the
clone: the sync copies and removes nothing, lists those files, the files the clone changed that the drive changed
too (merge them by hand), and the clone's files that are newer than the drive's state and would be deleted, and
names the commit the drive matches. Then:
  --to-drive <commit>  for every file the clone changed from <commit> to HEAD: copied onto the drive if the drive
                       still holds <commit>'s version (or nothing, for a file added since); left and listed if the
                       drive changed it too, or if the clone's copy is not committed; files deleted in the clone
                       are listed for deleting by hand, never deleted. Then sync as usual.
The guard cannot see a clone that only added files while the drive matches HEAD everywhere else; it needs one
changed file to know the drive is behind.
Stdlib only: runs on either Python.
"""
import filecmp, hashlib, os, re, sys, shutil, subprocess, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --drive: run the clone's copy of this script against the drive, e.g. when the drive's copy predates the guard
DRIVE = Path(sys.argv[sys.argv.index("--drive") + 1] if "--drive" in sys.argv else Path(__file__).resolve().parents[2])
assert (DRIVE / "Mars Project").is_dir(), f"not the project drive: {DRIVE}"
REPO = Path(sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else
            Path.home() / "OneDrive" / "Documents" / "GitHub" / "Mars_Terrestrial_GlobalMosaic_GIS-Data")
# The clone has a "Mars Project" folder too: its own copy of this script, run without --drive, would take the
# clone for the drive and mirror it into itself
assert DRIVE.resolve() != REPO.resolve(), f"the drive and the clone are one folder ({DRIVE}): pass --drive <drive>"
DRY = "--dry-run" in sys.argv
FORCE = "--force" in sys.argv
TO_DRIVE = sys.argv[sys.argv.index("--to-drive") + 1] if "--to-drive" in sys.argv else None
MAX = 95 * 1000 * 1000

SKIP_DIRS = {"__pycache__", ".git", "Mars Project.gdb", "Index", "images", "labels",
             "System Volume Information", "$RECYCLE.BIN",
             "Reference"}   # Mars Project\Reference: downloaded third-party data, not redistributed (KB §41)
SKIP_DIR_SUFFIX = (".crf", ".gdb")
# Dated snapshots of the record and scripts (.backup_YYYYMMDD, .py_backup_YYYYMMDD): history, kept on
# the drive and in git history, not on the project page (KB §39.4).
SKIP_DIR_PREFIX = (".backup_", ".py_backup_")
# History, not current work, kept on the drive and in git history only (KB §57.6): the .aprx snapshots (git
# versions Mars Project.aprx itself), a stale unpacked copy of the .aprx, Presentation 1's figure folders.
SKIP_DIRS |= {".backups", "aprx_live", "le_img"}
SKIP_FILES = {"neutral_voice.py",
              "ocean first pres LE.pptx"}     # Presentation 1, delivered; its PDF stays in OLD\
RASTER = {".tif", ".tiff", ".ovr", ".img", ".jp2"}
# pres1_img\ holds Presentation 1's figures; only those the interim or the final deck still shows are mirrored
PRES1_USED = {n for m in ("interim.py", "final.py")
              for n in re.findall(r"pres1_img\\([\w.-]+)", (DRIVE / "Mars Remote Sensing Project" / "build" /
                                                            m).read_text(encoding="utf-8"))}
# LaTeX's working files beside the final paper; the .bbl stays so the .tex compiles without BibTeX (KB §69.1)
LATEX_WORK = {".aux", ".log", ".out", ".blg", ".synctex", ".fls", ".fdb_latexmk"}


def keep_rsp(p):   # Mars Remote Sensing Project
    # neutral_voice.py lists the personal phrasings it removes, so it stays off the public page (KB §39.4)
    if p.parent.name == "pres1_img" and p.name not in PRES1_USED:
        return False
    if p.parent.name == "paper" and p.suffix.lower() in LATEX_WORK:
        return False
    return p.suffix.lower() not in {".npy", ".pyc"} and p.name not in SKIP_FILES


def keep_mp(p):    # Mars Project
    return p.suffix.lower() not in RASTER


def keep_root(p):  # drive root, files only
    # "new training.*": the 30 Sep export of the hand-drawn labels, a near copy of the gdb class in exports\
    # (KB §29.2); the screenshot: a 3D view from 15 Sep
    return p.suffix.lower() not in RASTER and not p.name.startswith(("new training.", "Screenshot "))


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
    ("Tests T1–T8 and the class checks", lambda n: n.startswith(("make_thermal_ablation", "make_t1_", "score_t1_",
                                                                  "make_tes_global", "make_tes_local", "make_t4_",
                                                                  "make_flow_margin", "make_composite_stability",
                                                                  "make_order_sweep", "make_geomap_check",
                                                                  "make_lava_relabel", "make_crater_density",
                                                                  "test_q24"))),
    ("Deep learning (X5)", lambda n: n.startswith(("make_dl_", "make_unet_map", "make_global60_dl_export"))),
    ("Digitising by review", lambda n: n.startswith(("accept_reviewed", "add_review_fields", "make_landform_fcs",
                                                     "propose_label_changes", "apply_label_review", "labelsets",
                                                     "score_d18_verdict", "run_rehearsal_v2p"))),
    ("Ius Chasma type area", lambda n: n.startswith(("make_typearea_", "verify_typearea", "make_channel_",
                                                     "make_crater_", "make_landform_", "verify_crater_",
                                                     "verify_segmentation")) and "layouts" not in n),
    ("±60° analysis extent", lambda n: n.startswith(("grid60", "make_extent", "make_global_", "make_global60_",
                                                     "verify_global60", "svmcheck", "verify_svm_", "score_metrics"))
                                       and n != "make_global60_maps.py"),
    ("ArcGIS project: maps and layouts", lambda n: n in {"layoutkit.py", "polish_layouts.py", "make_global60_maps.py",
                                                         "make_candidate_maps.py", "make_typearea_layouts.py",
                                                         "repoint_junction_layers.py", "audit_aprx.py",
                                                         "audit_layers.py", "fix_night_stretch.py",
                                                         "make_athabasca_layout.py", "make_geomap_sheet.py",
                                                         "make_mosaic_layout.py", "make_reference_maps.py",
                                                         "make_validation_sheet.py", "fix_label_names.py",
                                                         "rebuild_groups.py", "remove_non_mars.py"}),
    ("Figures", lambda n: n.startswith(("make_fig", "make_glob", "make_locator", "make_panels", "make_spectrum",
                                        "make_zoom", "make_extra", "marsfig", "optimise_", "img_contrast"))),
    ("Deliverables and their checks", lambda n: n.startswith(("build_", "content", "deck_", "le_theme", "mars_theme", "pdf_pages",
                                                              "audit_", "verify_all", "verify2", "render", "interim",
                                                              "make_interim_figs", "make_interim_dark", "docx_kit", "verify_interim",
                                                              "final", "make_final_figs"))),
    ("Drive, paths and one-off fixes", lambda n: n.startswith(("paths", "areas", "desktop_check", "retarget_junction",
                                                               "osgeo_shim", "fix_", "landform_codes",
                                                               "housekeeping_"))),
    ("Reference data, readers and diagnostics", lambda n: True),
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
    for p in sorted(build.glob("*.ps1")):   # the Office renderers and the run queues: the opening comment describes
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        first = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("#") else ""
        link = "../Mars%20Remote%20Sensing%20Project/build/" + p.name
        group = next(g for g, test in GROUPS if test(p.name))
        runs = "PowerShell + ArcGIS" if "arcgispro-py3" in text else "PowerShell + Office"
        rows[group].append(f"| [`{p.name}`]({link}) | {runs} | {first.replace('|', '/') or '(no header)'} |")
    out = ["# The build scripts", "",
           f"All {sum(map(len, rows.values()))} scripts in `Mars Remote Sensing Project/build/`, grouped by what they "
           "make. The description is each script's own docstring. **Python** says which interpreter it needs: "
           "*ArcGIS* (arcpy or GDAL: `<Pro install folder>\\bin\\Python\\envs\\arcgispro-py3\\python.exe`, by default "
           "`C:\\Program Files\\ArcGIS\\Pro`; `paths.arcgis_python()` finds it), "
           "*system* (python-pptx), or *either*; the three `.ps1` renderers need PowerShell and Microsoft Office, "
           "`run_rehearsal_v2p.ps1` PowerShell and the ArcGIS Python. "
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
    if sa.st_size != sb.st_size:
        return False
    # A git checkout or pull stamps files with the time of the checkout, so equal size with a different
    # mtime is compared byte for byte; otherwise every pull on the other machine reports phantom copies.
    return int(sa.st_mtime) == int(sb.st_mtime) or filecmp.cmp(a, b, shallow=False)


def blob(path):
    """A file's git blob id. The repo stores every file byte for byte (.gitattributes `* -text`), so this is the
    id git gives it, without a subprocess per file. None if it cannot be read (a deck open in PowerPoint is locked)."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def git_out(*args):
    p = subprocess.run(["git", "--literal-pathspecs", "-C", str(REPO), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    return p.returncode, p.stdout


def history(rel):
    """[(commit, blob)] for one path, newest first; a deletion's blob is all zeros."""
    out, commit = [], None
    for line in git_out("log", "--raw", "--no-abbrev", "--no-renames", "--format=@%H", "--", rel)[1].splitlines():
        if line.startswith("@"):
            commit = line[1:]
        elif line.startswith(":") and commit:
            out.append((commit, line.split()[3]))
    return out


def blob_at(commit, rel):
    code, out = git_out("rev-parse", "--verify", "--quiet", f"{commit}:{rel}")
    return out.strip() if code == 0 else None


def guard(copies, removals):
    """Whether the drive is behind the clone (the module docstring); returns the report's lines, empty if not."""
    tracked = set(git_out("ls-files")[1].splitlines())
    order = {c: i for i, c in enumerate(git_out("log", "--format=%H")[1].split())}   # 0 is HEAD
    stale = []   # (repo path, the commit whose version the drive holds)
    for p, out in copies:
        rel = out.relative_to(REPO).as_posix()
        if rel not in tracked:
            continue
        h = history(rel)
        older = {b: c for c, b in h[1:]}
        b = blob(p)
        if b and h and b != h[0][1] and b in older:
            stale.append((rel, older[b]))
    if not stale:
        return []
    base = min((c for _, c in stale), key=lambda c: order.get(c, 1 << 30))   # the newest of the drive's versions
    stale_rels = {r for r, _ in stale}
    both, newer = [], []
    for p, out in copies:
        rel = out.relative_to(REPO).as_posix()
        if rel in tracked and rel not in stale_rels and blob_at(base, rel) != blob_at("HEAD", rel):
            both.append(rel)
    for out in removals:
        rel = out.relative_to(REPO).as_posix()
        if rel in tracked and blob_at(base, rel) is None:
            newer.append(rel)
    lines = [f"REFUSED: the drive is behind the clone. It holds older committed versions of {len(stale)} file(s); "
             f"the newest it matches is {base[:7]}. Nothing was copied or removed.",
             f"  First: python github_sync.py --to-drive {base[:7]} --dry-run, then without --dry-run; then sync.",
             "  (--force copies and removes anyway, reverting the clone.)",
             f"  The drive holds an older version ({len(stale)}):"]
    lines += [f"    {r}  (as of {c[:7]})" for r, c in stale]
    if both:
        lines += [f"  Changed in the clone since {base[:7]} and different on the drive: merge by hand ({len(both)}):"]
        lines += [f"    {r}" for r in both]
    if newer:
        lines += [f"  Added in the clone since {base[:7]}, not on the drive; a sync would delete them ({len(newer)}):"]
        lines += [f"    {r}" for r in newer]
    return lines


def drive_path(rel):
    """The drive file a repo path mirrors, or None if the path is not a mirrored one."""
    top, _, rest = rel.partition("/")
    for src, dst, recurse, _ in TREES:
        if top == dst and rest and (recurse or "/" not in rest):
            return src / rest
    return None


def to_drive(base):
    """Copies the clone's changes since <base> onto the drive (the module docstring)."""
    code, out = git_out("diff", "--name-status", "--no-renames", "-z", base, "HEAD", "--",
                        *[dst for _, dst, _, _ in TREES])
    if code:
        sys.exit(f"git diff {base} HEAD failed: is {base} a commit of {REPO}?")
    f = out.split("\0")
    changes = [(f[i], f[i + 1]) for i in range(0, len(f) - 1, 2)]
    done, there, conflict, uncommitted, deleted, unmapped, locked = [], [], [], [], [], [], []
    for status, rel in changes:
        d = drive_path(rel)
        if d is None:
            unmapped.append(rel)
            continue
        old, new = blob_at(base, rel), blob_at("HEAD", rel)
        if status == "D":
            if d.exists() and blob(d) == old:
                deleted.append(rel)
            continue
        c = REPO / rel
        if (c.exists() and blob(c) is None) or (d.exists() and blob(d) is None):
            locked.append(rel)
        elif not c.exists() or blob(c) != new:
            uncommitted.append(rel)
        elif d.exists() and blob(d) == new:
            there.append(rel)
        elif (not d.exists() and old is None) or (d.exists() and blob(d) == old):
            done.append(rel)
            if not DRY:
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(c, d)
        else:
            conflict.append(rel)
    print(f"clone {REPO}  ->  drive {DRIVE}, the changes {base[:7]}..HEAD")
    print(f"{'would copy' if DRY else 'copied'} {len(done)}, already on the drive {len(there)}, "
          f"changed on both sides {len(conflict)}, not committed in the clone {len(uncommitted)}, "
          f"deleted in the clone {len(deleted)}, could not be read {len(locked)}")
    for title, rows in (("copied" if not DRY else "would copy", done),
                        ("CHANGED ON BOTH SIDES, merge by hand", conflict),
                        ("NOT COMMITTED in the clone, left alone", uncommitted),
                        ("COULD NOT BE READ (open in another program?): close it and rerun", locked),
                        ("deleted in the clone; delete on the drive by hand", deleted),
                        ("not a mirrored path, skipped", unmapped)):
        if rows:
            print(f"  {title}:")
            for r in rows:
                print("    " + r)
    return 1 if conflict or uncommitted or locked else 0


def main():
    assert REPO.is_dir() and (REPO / ".git").exists(), f"clone the repo first: {REPO}"
    if TO_DRIVE:
        sys.exit(to_drive(TO_DRIVE))
    copies, unchanged, too_big, removals = [], 0, [], []
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
            copies.append((p, out))
        top = REPO / dst
        if top.is_dir():
            removals += [p for p in top.rglob("*") if p.is_file() and p not in wanted]

    refused = [] if FORCE else guard(copies, removals)
    if refused:
        print("\n".join(refused))
        sys.exit(3)
    if not DRY:
        for p, out in copies:
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)
        for p in removals:
            p.unlink()
    copied = [out.relative_to(REPO) for _, out in copies]
    removed = [p.relative_to(REPO) for p in removals]

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
