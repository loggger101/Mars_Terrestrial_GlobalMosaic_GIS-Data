# -*- coding: utf-8 -*-
r"""Zips the rasters and caches too big for the repo into GitHub release assets (KB §35).

    python github_release_bundle.py                    build the zips in <dist>
    python github_release_bundle.py --upload data-YYYY-MM-DD
                                                       ...and publish them as that release

Run github_export_gdb.py (ArcGIS Python, with --rasters) first: it leaves the GeoPackage and
the two GUI SVM maps in <dist>, and this picks them up.

Assets, each part under 1.9 GB (GitHub's limit is 2 GiB per file); files are the originals,
byte for byte, so a restore is an unzip:
  typearea-partN.zip         <drive>\Mars Project\TypeArea\, whole: the Ius Chasma stack and every
                             derivative, classification and model (§18-27)
  athabasca.zip              <drive>\Mars Project\Athabasca\, whole: the second type area's stack,
                             terrain, thermal index and channel rasters (§42.1; layout 15). Added
                             2026-10-19 (§63): data-2026-10-16 and earlier do not hold it
  global60-classification[-partN].zip  the ±60° SVM maps (400 m raw + mode 3/5/7/9; since 2026-10-16
                             also 200 m raw + mode 3-11 and the four T1 maps), the models, the two
                             0.5° density grids, smoke tests; since 2026-10-21 the two U-Net maps
                             (one pass and two passes, §66.7-66.8); since 2026-10-29 the seven-class
                             SVM and U-Net maps, v2 and the v2p rehearsal (§69.4, §69.24-69.25)
  dl-models.zip              <drive>\Mars Project\DLModels\, whole: every trained deep-learning
                             model (X5, X5b, X5c, and since 2026-10-29 the two seven-class U-Nets:
                             .pth, .emd, .dlpk), their loss graphs and the detections (§66, §69).
                             Added 2026-10-21: hours of GPU to retrain
  npy-caches.zip             decimated arrays of the globals behind the figures (§9); the five
                             ~950 MB *_ov400.npy are left out, they are views of the tifs above
  mars_project_vectors.gpkg.zip, Classified_*.tif   from github_export_gdb.py
  SHA256SUMS.txt

Not bundled: the four source globals (re-downloadable), Global60's 85 GB of derivatives and the
gdb rasters (re-computable from build\), the deep-learning chips (re-exportable, §31.4).
Stdlib only, plus the gh CLI for --upload. Reads Z: only.
"""
import os, sys, hashlib, zipfile, subprocess
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DRIVE = Path(__file__).resolve().parents[2]
MP, RSP = DRIVE / "Mars Project", DRIVE / "Mars Remote Sensing Project"
DIST = Path(sys.argv[sys.argv.index("--dist") + 1] if "--dist" in sys.argv else
            Path(os.environ["LOCALAPPDATA"]) / "Temp" / "mars_github_dist")
REPO = "loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data"
PART = 1_900_000_000


def files_under(d):
    return sorted(p for p in d.rglob("*") if p.is_file())


def groups():
    g60 = MP / "Global60"
    yield "typearea", MP, files_under(MP / "TypeArea")
    yield "athabasca", MP, files_under(MP / "Athabasca")
    yield "global60-classification", MP, sorted(
        [p for p in g60.glob("global60_landforms_svm*") if p.is_file() and p.suffix != ".ovr"]
        + [p for p in g60.glob("global60_landforms_unet*") if p.is_file() and p.suffix != ".ovr"]  # §66.7-66.8
        + [p for p in g60.glob("global60_*_density_0p5deg.tif*") if p.is_file() and p.suffix != ".ovr"]  # §53.6
        + [p for p in g60.glob("smoke60_*") if p.is_file()]
        + [p for d in g60.glob("*.crf") for p in files_under(d)] + [g60 / "README.md"])
    yield "dl-models", MP, files_under(MP / "DLModels")                                        # §66
    yield "npy-caches", RSP, sorted(p for p in (RSP / "build").rglob("*.npy")
                                    if not p.name.endswith("_ov400.npy"))
    gpkg = DIST / "mars_project_vectors.gpkg"
    if gpkg.exists():
        yield "mars_project_vectors.gpkg", DIST, [gpkg]


def write_zips():
    DIST.mkdir(parents=True, exist_ok=True)
    made = []
    for name, base, files in groups():
        parts, cur, size = [], [], 0
        for p in files:
            s = p.stat().st_size
            if cur and size + s > PART:
                parts.append(cur)
                cur, size = [], 0
            cur.append(p)
            size += s
        parts.append(cur)
        for i, part in enumerate(parts, 1):
            zname = f"{name}-part{i}.zip" if len(parts) > 1 else f"{name}.zip"
            zp = DIST / zname
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as z:
                for p in part:
                    z.write(p, p.relative_to(base).as_posix())
            print(f"{zname}\t{len(part)} files\t{zp.stat().st_size / 1e6:,.0f} MB", flush=True)
            made.append(zp)
    made += sorted(DIST.glob("Classified_*.tif"))
    for p in made:
        assert p.stat().st_size < 2 * 1024**3, f"over GitHub's 2 GiB asset limit: {p}"
    with open(DIST / "SHA256SUMS.txt", "w", newline="\n") as f:
        for p in made:
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 24), b""):
                    h.update(chunk)
            f.write(f"{h.hexdigest()}  {p.name}\n")
    return made + [DIST / "SHA256SUMS.txt"]


if __name__ == "__main__":
    assets = write_zips()
    if "--upload" in sys.argv:
        tag = sys.argv[sys.argv.index("--upload") + 1]
        exists = subprocess.run(["gh", "release", "view", tag, "-R", REPO],
                                capture_output=True).returncode == 0
        if not exists:
            subprocess.run(["gh", "release", "create", tag, "-R", REPO, "--title", tag,
                            "--notes", "Rasters, caches and vector exports from the project drive. "
                                       "See the README section 'Restoring'."], check=True)
        for a in assets:   # one at a time, so a dropped connection costs one file
            subprocess.run(["gh", "release", "upload", tag, str(a), "-R", REPO, "--clobber"], check=True)
            print("uploaded", a.name, flush=True)
