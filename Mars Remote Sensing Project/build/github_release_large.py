# -*- coding: utf-8 -*-
r"""Backs up the large, slow-to-recompute products as a second GitHub release (KB §35.3).

    <ArcGIS python.exe> github_release_large.py derivatives-YYYY-MM-DD [--no-gdb]

What goes, as release assets (GitHub caps one asset at 2 GiB, so big files are byte-split):
  Global60 derivatives: global60_svm_stack_200m, _thermal_contrast, _thermal_contrast_200m, _dem,
      _slope_deg, _aspect, _hillshade (.tif). Original bytes, cut into <file>.partNNN of 1.9 GB.
      The .ovr pyramids are left out: Build Pyramids re-creates them.
  global60-sidecars.zip      their .aux.xml / .xml (statistics, lineage)
  labeledobjects-partN.zip   both deep-learning exports, the GUI one (1 Oct) and the §31.4 one
  Segmented_202609290011302066080.tif   the GUI ±60° segmentation (§29.5), out of the gdb as a
      DEFLATE GeoTIFF, split the same way if it needs to be. Skipped with --no-gdb.
  SHA256SUMS-<tag>.txt       a hash of every asset AND of every reassembled whole file

Reassemble a split file:   cat global60_dem.tif.part* > global60_dem.tif        (bash)
                           copy /b global60_dem.tif.part001+global60_dem.tif.part002 global60_dem.tif
Then check it against SHA256SUMS.

Not backed up: the other gdb rasters. They are the legacy products §7 and §29-30 find defective
(percent-rise slopes on a degree grid, the misregistered global composite) and are superseded.

Resumable: an asset already on the release is skipped and its SHA-256 taken from GitHub, so re-run after a
dropped connection or a sleep. Each part is staged on internal disk, uploaded, then deleted, so
staging never needs more than one part. Reads Z: only. Keeps the machine awake while it runs.
"""
import os, sys, json, time, hashlib, zipfile, subprocess, ctypes
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DRIVE = Path(__file__).resolve().parents[2]
MP = DRIVE / "Mars Project"
G60 = MP / "Global60"
REPO = "loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data"
STAGE = Path(os.environ["LOCALAPPDATA"]) / "Temp" / "mars_github_large"
PART = 1_900_000_000
BIG = ["global60_dem.tif", "global60_hillshade.tif", "global60_thermal_contrast_200m.tif",
       "global60_slope_deg.tif", "global60_aspect.tif", "global60_svm_stack_200m.tif",
       "global60_thermal_contrast.tif"]
SEGMENTED = "Segmented_202609290011302066080"

TAG = sys.argv[1]
ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)  # ES_CONTINUOUS | SYSTEM_REQUIRED
STAGE.mkdir(parents=True, exist_ok=True)
# name -> sha256, kept on disk so a resumed run has the hashes of what an earlier run uploaded
SUMS = STAGE / f"sums-{TAG}.json"
sums = json.loads(SUMS.read_text()) if SUMS.exists() else {}


def add_sum(name, hexdigest):
    sums[name] = hexdigest
    SUMS.write_text(json.dumps(sums, indent=1))


def gh(*a, **kw):
    return subprocess.run(["gh", *a, "-R", REPO], check=True, **kw)


def existing():
    """{name: sha256 hex} of every asset fully uploaded. GitHub records each asset's SHA-256, so
    a resumed run takes the checksum from there instead of rebuilding the file to hash it."""
    out = subprocess.run(["gh", "api", f"repos/{REPO}/releases/tags/{TAG}", "--jq",
                          '[.assets[] | select(.state == "uploaded") | {(.name): .digest}] | add // {}'],
                         capture_output=True, text=True, check=True).stdout
    return {k: (v or "").removeprefix("sha256:") for k, v in json.loads(out or "{}").items()}


def already_up(name, have):
    if name in have and have[name]:
        add_sum(name, have[name])
        print(f"skip (already up)  {name}", flush=True)
        return True
    return False


def upload(path, have):
    if already_up(path.name, have):
        return
    for attempt in range(1, 7):   # a dropped connection or a failed DNS lookup is retried, not fatal
        try:
            gh("release", "upload", TAG, str(path), "--clobber")
            break
        except subprocess.CalledProcessError:
            if attempt == 6:
                raise
            print(f"upload failed, retry {attempt} in {60 * attempt} s  {path.name}", flush=True)
            time.sleep(60 * attempt)
    print(f"uploaded  {path.name}  {path.stat().st_size / 1e6:,.0f} MB", flush=True)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 24), b""):
            h.update(c)
    return h.hexdigest()


def split_upload(src, have):
    """Cut src into .partNNN chunks; stage, hash, upload and delete each in turn."""
    size, whole = src.stat().st_size, hashlib.sha256()
    n = (size + PART - 1) // PART
    with open(src, "rb") as f:
        for i in range(1, n + 1):
            name = f"{src.name}.part{i:03d}"
            chunk = STAGE / name
            ph = hashlib.sha256()
            done = name in have   # still read it: the whole file's hash needs every byte
            with open(os.devnull if done else chunk, "wb") as out:
                left = min(PART, size - (i - 1) * PART)
                while left:
                    b = f.read(min(1 << 24, left))
                    out.write(b); ph.update(b); whole.update(b); left -= len(b)
            if done:
                assert have[name] in ("", ph.hexdigest()), f"{name} on GitHub differs from the drive"
                already_up(name, have)
                continue
            add_sum(name, ph.hexdigest())
            upload(chunk, have)
            chunk.unlink()
    add_sum(f"{src.name}  (reassembled from {n} parts)", whole.hexdigest())


def zip_parts(name, base, files, have):
    parts, cur, size = [], [], 0
    for p in files:
        if cur and size + p.stat().st_size > PART:
            parts.append(cur); cur, size = [], 0
        cur.append(p); size += p.stat().st_size
    parts.append(cur)
    for i, part in enumerate(parts, 1):
        zp = STAGE / (f"{name}-part{i}.zip" if len(parts) > 1 else f"{name}.zip")
        if already_up(zp.name, have):
            continue
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
            for p in part:
                z.write(p, p.relative_to(base).as_posix())
        add_sum(zp.name, sha(zp))
        upload(zp, have)
        zp.unlink()


def main():
    if subprocess.run(["gh", "release", "view", TAG, "-R", REPO], capture_output=True).returncode:
        gh("release", "create", TAG, "--title", TAG, "--notes",
           "Large derived products from the project drive: the ±60° derivatives (byte-split, "
           "reassemble with `cat name.part* > name`), the deep-learning exports and the GUI ±60° "
           "segmentation. See SHA256SUMS and the README section 'Restoring'.")
    have = existing()
    zip_parts("global60-sidecars", MP, sorted(p for b in BIG for p in G60.glob(b + ".*xml")), have)
    lo = MP / "LabeledObjects"
    zip_parts("labeledobjects", MP, sorted(p for p in lo.rglob("*") if p.is_file()), have)
    seg = STAGE / f"{SEGMENTED}.tif"
    if "--no-gdb" in sys.argv or already_up(seg.name, have) or already_up(seg.name + ".part001", have):
        pass
    else:
        if not seg.exists():
            from osgeo import gdal
            gdal.UseExceptions()
            ds = gdal.Open(f"OpenFileGDB:{MP / 'Mars Project.gdb'}:{SEGMENTED}")
            gdal.Translate(str(seg) + ".tmp.tif", ds, creationOptions=[
                "COMPRESS=DEFLATE", "ZLEVEL=6", "PREDICTOR=2", "TILED=YES", "BLOCKXSIZE=512",
                "BLOCKYSIZE=512", "BIGTIFF=YES", "NUM_THREADS=ALL_CPUS"])
            ds = None
            os.replace(str(seg) + ".tmp.tif", seg)
        if seg.stat().st_size > PART:
            split_upload(seg, have)
        else:
            add_sum(seg.name, sha(seg)); upload(seg, have)
        seg.unlink()
    for b in BIG:
        split_upload(G60 / b, have)
    s = STAGE / f"SHA256SUMS-{TAG}.txt"
    s.write_text("".join(f"{h}  {n}\n" for n, h in sums.items()), encoding="utf-8", newline="\n")
    upload(s, existing())
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
