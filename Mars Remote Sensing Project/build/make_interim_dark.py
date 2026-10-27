# -*- coding: utf-8 -*-
r"""Navy-ground copies of the interim deck's charts and layouts, for the deck only (KB §69.13) -> interim_img\dark\.

The deck is navy throughout since 2026-10-27 (the author: "I don't want to be blinded by white backgrounds"); a
figure saved on white would sit in it as a lit rectangle. The report, the final paper and the README keep the
white originals: nothing here overwrites one.

Charts: each chart script runs unchanged, with matplotlib's Figure.savefig wrapped so the finished figure is
recoloured for navy ground and written to dark\ under the same name. The recolouring is chosen for dark ground,
not a flip: neutral greys swap ends (white paper -> navy, near-black ink -> light text); a strong colour keeps its
value; a light tint keeps its hue and its distance from the ground, so it stays as quiet as it was on white; white
text on a strong fill stays white.

Layouts (PNGs from make_interim_figs.py, which needs Pro): the white page connected to the image's edge becomes
navy, and the small marks standing on that page (panel titles, scale bars, north arrows) are lightened; the map
frames and their imagery are left exactly as they are. In legend PNGs every white pixel is the page; text and
outlines are lightened; filled swatches keep their colour, so they still match the map.

    python make_interim_dark.py            (system Python: matplotlib, numpy, scipy, Pillow)
"""
import colorsys
import os
import runpy
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.figure                                          # noqa: E402
import numpy as np                                                # noqa: E402
from matplotlib.collections import Collection                     # noqa: E402
from matplotlib.colors import to_hex, to_rgba                     # noqa: E402
from matplotlib.lines import Line2D                               # noqa: E402
from matplotlib.patches import Patch                              # noqa: E402
from matplotlib.text import Text                                  # noqa: E402
from PIL import Image                                             # noqa: E402
from scipy import ndimage                                         # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "interim_img", "dark")
GROUND = (0x0E / 255.0, 0x28 / 255.0, 0x41 / 255.0)             # mars_theme.GROUND
TEXT = (0xEA / 255.0, 0xF0 / 255.0, 0xF7 / 255.0)               # mars_theme.TEXT

CHARTS = ["make_fig_tes.py", "make_fig_t8.py", "make_fig_ablation.py", "make_fig_t1_pro.py", "make_fig_t4.py",
          "make_fig_tests567.py", "make_fig_global60.py"]


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def remap(c, text=False):
    r, g, b, a = to_rgba(c)
    if a == 0:
        return (r, g, b, a)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if max(r, g, b) - min(r, g, b) < 0.12:                       # a neutral grey (the charts' #5A6570 is 0.09)
        if text and l > 0.9:
            return (r, g, b, a)                                  # white text on a strong fill
        if text:                                                 # muted grey text stays readable on navy
            return mix(GROUND, TEXT, 0.55 + 0.45 * (1.0 - l)) + (a,)
        return mix(GROUND, TEXT, 1.0 - l) + (a,)
    if l > 0.6:                                                  # a light tint: as quiet on navy as on white
        return colorsys.hls_to_rgb(h, 0.15 + (1.0 - l) * 0.8, s) + (a,)
    return (r, g, b, a)


def recolour(fig):
    fig.canvas.draw()                                            # tick labels exist only once drawn
    ticks = []
    for ax in fig.axes:                                          # ticks made afresh at save take these colours
        for name, axis in (("x", ax.xaxis), ("y", ax.yaxis)):
            labels = [t for t in axis.get_ticklabels() if t.get_text()]
            if labels:
                ticks.append((ax, name, remap(labels[0].get_color(), text=True)))
    for ax, name, colour in ticks:
        ax.tick_params(axis=name, labelcolor=colour)
    for art in fig.findobj():
        if isinstance(art, Text):
            art.set_color(remap(art.get_color(), text=True))
            box = art.get_bbox_patch()
            if box is not None:
                box.set_facecolor(remap(box.get_facecolor()))
                box.set_edgecolor(remap(box.get_edgecolor()))
        elif isinstance(art, Line2D):
            art.set_color(remap(art.get_color()))
            art.set_markerfacecolor(remap(art.get_markerfacecolor()))
            art.set_markeredgecolor(remap(art.get_markeredgecolor()))
        elif isinstance(art, Patch):
            art.set_facecolor(remap(art.get_facecolor()))
            art.set_edgecolor(remap(art.get_edgecolor()))
        elif isinstance(art, Collection):
            fc, ec = art.get_facecolor(), art.get_edgecolor()
            if len(fc):
                art.set_facecolor([remap(c) for c in fc])
            if len(ec):
                art.set_edgecolor([remap(c) for c in ec])


_savefig = matplotlib.figure.Figure.savefig


def dark_savefig(self, fname, *args, **kw):
    recolour(self)
    kw["facecolor"] = to_hex(GROUND)
    kw.pop("transparent", None)
    out = os.path.join(OUT, os.path.basename(str(fname)))
    _savefig(self, out, *args, **kw)
    print("  dark", os.path.relpath(out, HERE))


def charts():
    matplotlib.figure.Figure.savefig = dark_savefig
    try:
        for script in CHARTS:
            print(script)
            try:
                runpy.run_path(os.path.join(HERE, script), run_name="__main__")
            except SystemExit as e:                              # make_fig_global60.py ends in sys.exit(main())
                if e.code not in (None, 0):
                    raise
    finally:
        matplotlib.figure.Figure.savefig = _savefig


def lighten(px, mask):
    """Neutral pixels under `mask` swap ends onto the navy-to-light scale; coloured pixels stay."""
    rgb = px[mask]
    neutral = (rgb.max(1) - rgb.min(1)) < 0.12
    t = 1.0 - rgb.max(1)
    new = np.array(GROUND)[None, :] + (np.array(TEXT) - np.array(GROUND))[None, :] * t[:, None]
    rgb[neutral] = new[neutral]
    px[mask] = rgb


def layout(path, legend):
    px = np.asarray(Image.open(path).convert("RGB")).astype(float) / 255.0
    white = px.min(2) > 0.93
    if legend:
        page = white
    else:                                                        # the page is the white touching the edge
        lab, _ = ndimage.label(white)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        page = np.isin(lab, list(edge))
    marks, n = ndimage.label(~page)
    area = px.shape[0] * px.shape[1]
    keep = np.zeros_like(page)
    for k, sl in enumerate(ndimage.find_objects(marks), 1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        fill = (marks[sl] == k).sum() / float(h * w)
        swatch = w >= 18 and h >= 8 and fill > 0.75              # wider than any glyph: "l", "I", "a" are not
        if (not legend and h * w > 0.06 * area) or (legend and swatch):
            keep[sl] |= marks[sl] == k                           # a map frame, or a filled swatch
    lighten(px, ~page & ~keep)
    px[page] = GROUND
    out = os.path.join(OUT, os.path.basename(path))
    Image.fromarray((px * 255).round().astype(np.uint8)).save(out, optimize=True)
    print("  dark", os.path.relpath(out, HERE))


def layouts():
    sys.path.insert(0, HERE)
    import interim
    names = [r for f in interim.FIGURES for k, r in f["images"] if k == "layout"]
    for name in names:
        for suffix, legend in (("", False), ("__map", False), ("__legend", True)):
            p = os.path.join(HERE, "interim_img", name + suffix + ".png")
            if os.path.exists(p):
                layout(p, legend)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    charts()
    layouts()
