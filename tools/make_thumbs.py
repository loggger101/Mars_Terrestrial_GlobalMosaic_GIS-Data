# -*- coding: utf-8 -*-
"""Writes the small previews the project page shows in place of the full-size figures.

    py -3 tools/make_thumbs.py          (needs Pillow; run after a layout or figure changes)

The layouts are 150 dpi PNGs of 1-4 MB each, and the README alone showed 25 MB of them. Every
image linked from docs/figures.md that is over 300 KB gets an 800 px wide JPEG in docs/thumbs/,
named after its source; the pages show the preview and link the full file. docs/thumbs/SOURCES.txt
records each source's SHA-256, so tools/check_repo.py fails when a source changes and its preview
was not rebuilt. Previews whose source is gone are deleted.
"""
import hashlib, re, sys, urllib.parse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "thumbs"
MANIFEST = OUT / "SOURCES.txt"
LIMIT = 300 * 1000                       # bytes: anything bigger is shown as a preview
WIDTH = 800


def sources():
    """The images docs/figures.md links, over LIMIT, in page order."""
    page = ROOT / "docs" / "figures.md"
    text = page.read_text(encoding="utf-8")
    seen = []
    for target in re.findall(r"""href=["']([^"']+)["']|\]\(<?([^)>\s]+)>?\)""", text):
        target = target[0] or target[1]
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        p = (page.parent / urllib.parse.unquote(target)).resolve()
        if p.suffix.lower() == ".png" and p.is_file() and p.stat().st_size > LIMIT and p not in seen:
            seen.append(p)
    return seen


def main():
    OUT.mkdir(exist_ok=True)
    rows, names = [], set()
    for src in sources():
        name = src.stem + ".jpg"
        if src.parent.name == "ModelCharacteristics":      # every model writes the same file names
            name = src.parents[1].name + "_" + name
        if name in names:
            sys.exit(f"two sources would share the preview name {name}")
        names.add(name)
        im = Image.open(src)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.getchannel("A"))
            im = bg
        im = im.convert("RGB")
        if im.width > WIDTH:
            im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
        im.save(OUT / name, "JPEG", quality=82, optimize=True, progressive=True)
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        rows.append(f"{digest}  {name}  {src.relative_to(ROOT).as_posix()}")
        print(f"{name:40s} {(OUT / name).stat().st_size / 1000:6.0f} KB  from {src.stat().st_size / 1e6:4.1f} MB")
    for old in OUT.glob("*.jpg"):
        if old.name not in names:
            old.unlink()
            print("removed", old.name)
    MANIFEST.write_text("".join(r + "\n" for r in rows), encoding="utf-8", newline="\n")
    print(f"{len(rows)} previews in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
