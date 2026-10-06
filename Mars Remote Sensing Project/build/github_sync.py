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
  <drive root>\  -> drive-root\ sidecars of the four globals and his "new training" shapefile
Any single file over 95 MB is skipped and reported (GitHub refuses files over 100 MB).

What does not, and where it goes instead:
  Mars Project.gdb vectors      github_export_gdb.py writes them to exports\ in the repo
  rasters and .npy caches       github_release_bundle.py zips them for a GitHub release
  the four source globals       re-downloadable; the README gives the URLs
  Global60 derivatives, gdb rasters, DL chips: re-computable, and 300+ GB

Files that vanish from the drive are removed from the mirror too; git history keeps them.
Stdlib only: runs on either Python.
"""
import os, sys, shutil, subprocess, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DRIVE = Path(__file__).resolve().parents[2]
assert (DRIVE / "Mars Project").is_dir(), f"not the project drive: {DRIVE}"
REPO = Path(sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else
            Path.home() / "OneDrive" / "Documents" / "GitHub" / "Mars_Terrestrial_GlobalMosaic_GIS-Data")
DRY = "--dry-run" in sys.argv
MAX = 95 * 1000 * 1000

SKIP_DIRS = {"__pycache__", ".git", "Mars Project.gdb", "Index", "images", "labels",
             "System Volume Information", "$RECYCLE.BIN"}
SKIP_DIR_SUFFIX = (".crf", ".gdb")
RASTER = {".tif", ".tiff", ".ovr", ".img", ".jp2"}


def keep_rsp(p):   # Mars Remote Sensing Project
    return p.suffix.lower() not in {".npy", ".pyc"}


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
                   and not os.path.islink(os.path.join(root, d))]
        for f in files:
            p = Path(root) / f
            if keep(p):
                yield p


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
