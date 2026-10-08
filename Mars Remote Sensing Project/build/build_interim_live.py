# -*- coding: utf-8 -*-
"""The living interim presentation, in the Presentation 1 design (KB §39.3).

Decided 2026-10-08: the Presentation 1 style with graphics, no fixed slide count, rebuilt as the data
moves. Content comes from interim.py only; the layouts come from interim_img\\, which
make_interim_figs.py refreshes from the project. So the build is two commands:

  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" make_interim_figs.py
  python build_interim_live.py <out.pptx>

It covers every heading of the course template ('NEXT STUFF\\2 Interim Presentation
Template.pptx'): title, investigators, goals; relevant spectral bands; tasks and percent
complete; preliminary results; issues and hurdles. build_interim_le.py, which made the
13 Sep deck from content.py, is left as it was.
"""
import os
import sys

import interim as I
from le_theme import (deck, new, title_slide, section, bullets, labeled, table, note,
                      textbox, style, no_bullet, png_size, PT, MARGIN, CONTENT_W, BODY_Y,
                      CYAN, GREY, NAVY)
from pptx.util import Emu

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "interim_img")
OUT = sys.argv[1]
RIGHT = MARGIN + CONTENT_W                   # right edge of the content area
FIG_H = 368 * PT                             # tallest a figure may be under the title bar
SIDE_MAX_W = 520 * PT                        # wider than this at FIG_H, and the takeaways go below
WIDE_MAX_H = 290 * PT                        # a full-width map leaves room for three takeaways
MINUS = "−"


def image_path(kind, ref):
    p = os.path.join(IMG, ref + ".png") if kind == "layout" else os.path.join(HERE, ref)
    if not os.path.exists(p):
        sys.exit("missing image %s: run make_interim_figs.py first" % p)
    return p


def add_pic(s, path, x, y, w=None, h=None):
    px_w, px_h = png_size(path)
    if w is None:
        w = int(h * px_w / px_h)
    if h is None:
        h = int(w * px_h / px_w)
    s.shapes.add_picture(path, Emu(x), Emu(y), Emu(w), Emu(h))
    return w, h


def source(s, text, x, y, w):
    tf = textbox(s, x, y, w, 18 * PT)
    p = tf.paragraphs[0]
    no_bullet(p)
    style(p.add_run(), 10, italic=True, color=GREY).text = "PROJECT-KNOWLEDGE.md " + text


def below(s, f, y):
    """Takeaways under a picture, the source line pinned to the foot of the slide."""
    bullets(s, f["points"], size=14, top=y, height=510 * PT - y, space=4)
    source(s, f["source"], MARGIN, 516 * PT, CONTENT_W)


def split_legend(s, f, path):
    """If make_interim_figs.py wrote <layout>__map.png and __legend.png, use them: the map
    across the full width, the takeaways under it on the left, the legend on the right."""
    base = path[:-4]
    m, lg = base + "__map.png", base + "__legend.png"
    if not (os.path.exists(m) and os.path.exists(lg)):
        return False
    px_w, px_h = png_size(m)
    w = CONTENT_W
    h = int(w * px_h / px_w)
    if h > WIDE_MAX_H:
        h = WIDE_MAX_H
        w = int(h * px_w / px_h)
    add_pic(s, m, MARGIN + (CONTENT_W - w) // 2, BODY_Y, w=w, h=h)
    y = BODY_Y + h + 10 * PT
    room = 508 * PT - y                      # height left above the source line
    lw_px, lh_px = png_size(lg)
    lw = min(int(room * lw_px / lh_px), 300 * PT)
    lh = int(lw * lh_px / lw_px)
    add_pic(s, lg, RIGHT - lw, y, w=lw, h=lh)
    bullets(s, f["points"], size=14, top=y, height=room, space=4, width=CONTENT_W - lw - 16 * PT)
    source(s, f["source"], MARGIN, 516 * PT, CONTENT_W)
    return True


def figure_slide(prs, f):
    s = new(prs, f["title"], size=30)
    paths = [image_path(k, r) for k, r in f["images"]]
    if len(paths) == 1:
        px_w, px_h = png_size(paths[0])
        aspect = px_w / float(px_h)
        if FIG_H * aspect <= SIDE_MAX_W:     # a tall figure: figure left, takeaways right
            w, _ = add_pic(s, paths[0], MARGIN, BODY_Y, h=FIG_H)
            x = MARGIN + w + 22 * PT
            tw = RIGHT - x
            bullets(s, f["points"], size=15 if tw > 300 * PT else 14, top=BODY_Y + 8 * PT,
                    height=320 * PT, space=12, left=x, width=tw)
            source(s, f["source"], x, BODY_Y + FIG_H - 18 * PT, tw)
        elif split_legend(s, f, paths[0]):   # map full width; takeaways and legend beneath
            pass
        else:                                # a wide map: full width, takeaways beneath
            w = CONTENT_W
            h = int(w / aspect)
            if h > WIDE_MAX_H:
                h = WIDE_MAX_H
                w = int(h * aspect)
            add_pic(s, paths[0], MARGIN + (CONTENT_W - w) // 2, BODY_Y, w=w, h=h)
            below(s, f, BODY_Y + h + 10 * PT)
    else:                                    # figures side by side, takeaways beneath
        gap = 16 * PT
        w = int((CONTENT_W - gap * (len(paths) - 1)) / len(paths))
        h = 0
        for i, p in enumerate(paths):
            _, h = add_pic(s, p, MARGIN + i * (w + gap), BODY_Y, w=w)
        below(s, f, BODY_Y + h + 10 * PT)
    return s


prs = deck()

# ------------------------------------------------------------ title, investigators, goals
title_slide(prs, I.DECK_TITLE, (I.TITLE, I.COURSE + " \u00b7 " + I.AUTHOR,
                                "Interim Presentation \u00b7 status as of " + I.STATUS_DATE))

s = new(prs, "Project Goals")
tf = textbox(s, MARGIN, BODY_Y, CONTENT_W, 80 * PT)
p = tf.paragraphs[0]
no_bullet(p)
style(p.add_run(), 17).text = I.MISSION
bullets(s, I.GOALS, size=16, top=232 * PT, height=270 * PT, space=12)

# ------------------------------------------------------------ relevant spectral bands
s = new(prs, "Relevant Spectral Bands")
table(s, ["Band or product", "Wavelength", "Cell", "What it contributes"],
      [list(r) for r in I.BANDS], widths=[2.3, 1.9, 0.7, 6.2], size=11, row_h=40 * PT)

s = new(prs, "Why Fuse Them: Three Independent Dimensions")
c = I.CORRELATION
rows = [[b] + [("%+.3f" % v).replace("-", MINUS) if v != 1 else "1" for v in r]
        for b, r in zip(c["bands"], c["r"])]
t = table(s, ["Ius Chasma, r"] + c["bands"], rows, widths=[1.6] + [1.0] * 5, size=13,
          row_h=34 * PT)
for i, r in enumerate(c["r"], 1):            # the independent pairs in cyan, so the eye finds them
    for j, v in enumerate(r, 1):
        if abs(v) < 0.2:
            t.cell(i, j).text_frame.paragraphs[0].runs[0].font.color.rgb = CYAN
note(s, c["takeaway"] + "   PROJECT-KNOWLEDGE.md \u00a718.3", 360 * PT, size=13)

# ------------------------------------------------------------ tasks and percent complete
s = new(prs, "Project Tasks and Percent Complete")
rows = [[i, task, now, "%d%%" % sep, "%d%%" % pct if pct is not None else "\u2013"]
        for i, ((task, now, pct), sep) in enumerate(zip(I.PROGRESS, I.PROGRESS_SEPT), 1)]
table(s, ["#", "Task", "Where it stands", "13 Sep", "Now"], rows,
      widths=[0.4, 3.0, 6.0, 0.8, 0.8], size=10, row_h=24 * PT)

s = new(prs, "Processing Completed Since the Last Report")
table(s, ["When", "What", "Outcome", "KB"], [list(r) for r in I.LOG],
      widths=[1.0, 4.4, 4.0, 0.9], size=11, row_h=28 * PT)

# ------------------------------------------------------------ preliminary results
section(prs, "Preliminary Results", "What the data show so far",
        "Every map is a layout in the ArcGIS project, exported fresh for this deck.")
for f in I.FIGURES:
    figure_slide(prs, f)

# ------------------------------------------------------------ issues and hurdles
s = new(prs, "Project Issues and Hurdles")
labeled(s, I.ISSUES, size=14, space=9)

s = new(prs, "Next Steps")
bullets(s, I.NEXT_STEPS, size=16, top=BODY_Y, height=200 * PT, space=10)
table(s, ["When", "What"], [list(r) for r in I.SCHEDULE], top=340 * PT, widths=[1.6, 9.0],
      size=11, row_h=24 * PT)

prs.save(OUT)
print("wrote", OUT, "-", len(prs.slides._sldIdLst), "slides")
