# -*- coding: utf-8 -*-
r"""Rebuild the Mars Global Mosaic project drive from this repository and its releases.

    python restore.py --dest E:\                    everything: the tree, both releases
    python restore.py --dest E:\ --dry-run          say what would happen, download nothing
    python restore.py --dest E:\ --only typearea    only assets whose name contains "typearea"
    python restore.py --dest E:\ --no-tree          releases only

Run it from a clone of the repo. It lays the drive out as the knowledge base expects:

    <dest>\Mars Remote Sensing Project\     the repo folder, plus npy-caches.zip
    <dest>\Mars Project\                    the repo folder, plus TypeArea\, Global60\ rasters
                                            (split files rejoined), LabeledObjects\
    <dest>\Mars Project\restored_from_gdb\  the GUI SVM maps and the ±60° segmentation, which
                                            lived inside Mars Project.gdb; the vector layers are
                                            in <repo>\exports\ and its GeoPackage
    <dest>\                                 the drive-root sidecars and "new training" shapefile

Every download is checked against the release's SHA-256 (GitHub records one per asset), and every
rejoined file against the whole-file hash in SHA256SUMS. Downloads resume if interrupted and
are kept in <dest>\_downloads until --clean. Existing files are never overwritten unless --force.
The four source mosaics are not in the releases; the README links them.

Not restored: Mars Project.gdb itself (create it in Pro and copy in exports\mars_project_vectors.gdb),
the .ovr pyramids (Build Pyramids), and the Z:\TypeArea / Z:\Global60 junctions (README, Restoring).
Stdlib only, Python 3.9+.
"""
import argparse, hashlib, json, os, shutil, sys, urllib.request, zipfile
from pathlib import Path

REPO = "loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data"
HERE = Path(__file__).resolve().parent
API = f"https://api.github.com/repos/{REPO}/releases"


def releases():
    with urllib.request.urlopen(urllib.request.Request(API, headers={"Accept": "application/vnd.github+json"})) as r:
        return json.load(r)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 24), b""):
            h.update(c)
    return h.hexdigest()


def download(asset, folder):
    """Fetch one asset, resuming a partial file, and verify it against GitHub's SHA-256."""
    out = folder / asset["name"]
    want = (asset.get("digest") or "").removeprefix("sha256:")
    if out.exists() and out.stat().st_size == asset["size"] and (not want or sha256(out) == want):
        return out
    part = out.with_name(out.name + ".partial")
    have = part.stat().st_size if part.exists() else 0
    req = urllib.request.Request(asset["browser_download_url"], headers={"Range": f"bytes={have}-"} if have else {})
    with urllib.request.urlopen(req) as r, open(part, "ab" if have and r.status == 206 else "wb") as f:
        shutil.copyfileobj(r, f, 1 << 24)
    if want and sha256(part) != want:
        part.unlink()
        sys.exit(f"checksum mismatch, deleted: {asset['name']}")
    part.replace(out)
    return out


def place(src, dst, force):
    if dst.exists() and not force:
        print(f"  exists, kept: {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def unzip(zp, into, force):
    with zipfile.ZipFile(zp) as z:
        for m in z.infolist():
            target = into / m.filename
            if m.is_dir():
                continue
            if target.exists() and not force:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(m) as s, open(target, "wb") as d:
                shutil.copyfileobj(s, d, 1 << 24)


def join(parts, target, want, force):
    """Concatenate .partNNN pieces in order into target and check the whole-file hash."""
    if target.exists() and not force:
        print(f"  exists, kept: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".joining")
    h = hashlib.sha256()
    with open(tmp, "wb") as out:
        for p in sorted(parts, key=lambda p: p.name):
            with open(p, "rb") as f:
                for c in iter(lambda: f.read(1 << 24), b""):
                    out.write(c)
                    h.update(c)
    if want and h.hexdigest() != want:
        tmp.unlink()
        sys.exit(f"rejoined file does not match its SHA256SUMS entry, deleted: {target.name}")
    tmp.replace(target)


def whole_hashes(sums_file):
    """{file name: sha256} for the '(reassembled from N parts)' lines of a SHA256SUMS file."""
    out = {}
    for line in sums_file.read_text(encoding="utf-8").splitlines():
        if "(reassembled" in line:
            h, name = line.split()[:2]
            out[name] = h
    return out


def destination(name, dest):
    """Where an asset's contents go, by its name."""
    mp, rsp = dest / "Mars Project", dest / "Mars Remote Sensing Project"
    if name.startswith(("typearea", "global60-classification", "global60-sidecars", "labeledobjects")):
        return "unzip", mp
    if name.startswith("npy-caches"):
        return "unzip", rsp
    if name.startswith("mars_project_vectors.gpkg"):
        return "unzip", mp / "restored_from_gdb"
    if ".tif.part" in name:
        return "join", mp / "Global60"
    if name.startswith(("Classified_", "Segmented_")):
        return "copy", mp / "restored_from_gdb"
    return "skip", None   # the SHA256SUMS files


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dest", required=True, type=Path, help="root of the drive to rebuild")
    ap.add_argument("--only", default="", help="only assets whose name contains this text")
    ap.add_argument("--no-tree", action="store_true", help="skip copying the repo's folders")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--clean", action="store_true", help="delete <dest>\\_downloads when done")
    a = ap.parse_args()
    dest = a.dest.resolve()
    dl = dest / "_downloads"

    if not a.no_tree and not a.only:
        for folder, to in (("Mars Remote Sensing Project", dest / "Mars Remote Sensing Project"),
                           ("Mars Project", dest / "Mars Project"), ("drive-root", dest)):
            files = [p for p in (HERE / folder).rglob("*") if p.is_file()]
            print(f"tree  {folder}/  ({len(files)} files) -> {to}")
            if not a.dry_run:
                for p in files:
                    place(p, to / p.relative_to(HERE / folder), a.force)

    total = 0
    for rel in releases():
        assets = [x for x in rel["assets"] if a.only in x["name"] or x["name"].startswith("SHA256SUMS")]
        if not any(destination(x["name"], dest)[0] != "skip" for x in assets):
            continue
        print(f"\nrelease {rel['tag_name']}")
        folder = dl / rel["tag_name"]
        folder.mkdir(parents=True, exist_ok=True) if not a.dry_run else None
        whole, parts = {}, {}
        for x in sorted(assets, key=lambda x: (not x["name"].startswith("SHA256SUMS"), x["name"])):
            how, where = destination(x["name"], dest)
            if how == "skip" and not x["name"].startswith("SHA256SUMS"):
                continue
            total += x["size"]
            print(f"  {x['size'] / 1e9:7.2f} GB  {x['name']}  -> {how} {where or ''}")
            if a.dry_run:
                continue
            f = download(x, folder)
            if x["name"].startswith("SHA256SUMS"):
                whole.update(whole_hashes(f))
            elif how == "unzip":
                unzip(f, where, a.force)
            elif how == "copy":
                place(f, where / f.name, a.force)
            elif how == "join":
                parts.setdefault(x["name"].rsplit(".part", 1)[0], []).append(f)
        for name, ps in parts.items():
            print(f"  join  {name} from {len(ps)} pieces")
            join(ps, dest / "Mars Project" / "Global60" / name, whole.get(name), a.force)
    print(f"\n{'would download' if a.dry_run else 'done:'} {total / 1e9:.1f} GB")
    if a.clean and not a.dry_run:
        shutil.rmtree(dl, ignore_errors=True)


if __name__ == "__main__":
    main()
