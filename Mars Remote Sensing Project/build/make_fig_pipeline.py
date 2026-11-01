# -*- coding: utf-8 -*-
r"""Renders the pipeline diagram (docs/pipeline.svg in the clone) to a PDF and a PNG for the paper (NEXT-STEPS W10, KB §69.38).

The diagram is drawn by hand as SVG and lives only in the repository's docs\ (the project page shows it). LaTeX
cannot include SVG and no converter is installed, so Microsoft Edge's headless mode renders it: a PDF page the
SVG's own size (vector, for \includegraphics) and a PNG at twice that size. Nothing is installed. The paper's caption
carries the footnote, so its text (class "note") is dropped and the page cut to the SVG's data-paper-height.
At \textwidth (~504 pt) a 1,100 px wide SVG sets 15 px text at ~6.9 pt.

  python make_fig_pipeline.py [--repo <clone>]

Writes build\final_img\pipeline.pdf and pipeline.png. System Python. Fails if the SVG, Edge or either output is
missing, or if an output is older than the SVG.
"""
import os, re, sys, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else
            Path.home() / "OneDrive" / "Documents" / "GitHub" / "Mars_Terrestrial_GlobalMosaic_GIS-Data")
SVG = REPO / "docs" / "pipeline.svg"
OUT = HERE / "final_img"
EDGE = next((Path(p) for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                               r"C:\Program Files\Microsoft\Edge\Application\msedge.exe") if Path(p).exists()), None)


def edge(*args):
    subprocess.run([str(EDGE), "--headless", "--disable-gpu", "--hide-scrollbars", *args],
                   capture_output=True, timeout=120)


def main():
    if not SVG.exists():
        sys.exit("no %s" % SVG)
    if EDGE is None:
        sys.exit("Microsoft Edge not found")
    src = SVG.read_text(encoding="utf-8")
    w, h = (int(v) for v in re.search(r'viewBox="0 0 (\d+) (\d+)"', src).groups())
    ph = int(re.search(r'data-paper-height="(\d+)"', src).group(1))
    notes = len(re.findall(r'<text[^>]*class="note"', src))
    paper = re.sub(r'\s*<text[^>]*class="note"[^>]*>.*?</text>', "", src)
    if notes == 0 or 'class="note"' in paper:
        sys.exit("footnote not found or not removed (%d note lines)" % notes)
    paper = paper.replace('viewBox="0 0 %d %d"' % (w, h), 'viewBox="0 0 %d %d"' % (w, ph), 1)
    paper = re.sub(r'(<svg[^>]*?) height="%d"' % h, r'\1 height="%d"' % ph, paper, count=1)
    OUT.mkdir(exist_ok=True)
    pdf, png = OUT / "pipeline.pdf", OUT / "pipeline.png"
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "pipeline.html"
        page.write_text("<!doctype html><meta charset='utf-8'><style>@page{size:%dpx %dpx;margin:0}"
                        "html,body{margin:0;padding:0}svg{display:block}</style>%s" % (w, ph, paper), encoding="utf-8")
        edge("--no-pdf-header-footer", "--print-to-pdf=%s" % pdf, page.as_uri())
        edge("--force-device-scale-factor=2", "--window-size=%d,%d" % (w, ph), "--screenshot=%s" % png, page.as_uri())
    print("paper version: %d footnote lines dropped, %d x %d px" % (notes, w, ph))
    for p in (pdf, png):
        if not p.exists() or p.stat().st_mtime < SVG.stat().st_mtime:
            sys.exit("not written: %s" % p)
        print("wrote %s (%d bytes)" % (p, p.stat().st_size))


if __name__ == "__main__":
    main()
