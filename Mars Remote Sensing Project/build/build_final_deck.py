# -*- coding: utf-8 -*-
"""The final presentation, in the interim's deck design (mars_theme.py, KB §69.11), from final.py (NEXT-STEPS.md §7).

D24 (the author's yes, 2026-11-03; KB §69.65): one look for both talks. Until then this drew the Presentation 1 design
(le_theme.py; git holds that version). The words are final.py's, unchanged; what changed is the look, as for the
interim on 2026-10-27: navy throughout, the figures in navy-ground copies, a dark divider over the Ius mosaic before
each part, and the KB sections behind each slide in its speaker notes rather than on it (KB §69.9).

No template or rubric exists for the final (KB §50, D2), so the deck follows the final report outline: the question,
the data and the grid, the thermal pair, the landforms, the classification, the verdicts, the limits, what next:

  <ArcGIS Pro Python> make_final_figs.py           the layouts, to final_img\\
  py -3.13 make_fig_final.py                       the charts the interim never drew, to final_img\\
  <ArcGIS Pro Python> make_final_dark.py           their navy-ground copies, to final_img\\dark\\
  py -3.13 build_final_deck.py "..\\NEXT STUFF\\Final\\Mars Global Mosaic - Final Presentation.pptx"

The figure placement, the layout tightening and the legend handling are the interim builder's, copied below by a
script so that build_interim_live.py stays untouched.
"""
import io
import os
import re
import sys

import numpy as np
from PIL import Image

import final as F
from mars_theme import (deck, new, blank, line, kicker, bullets, table, note, card, dot, shape, textbox, TINT, DEEP,
                        style, no_bullet, hero_image, graticule, veil, credit, footer, pill, PT, W, H, MARGIN,
                        CONTENT_W, BODY_Y, BOTTOM, HEAD, NAVY, INK, MUTED, HAIR, BLUE, SKY, PALE, WHITE)
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "final_img")
IIMG = os.path.join(HERE, "interim_img")     # the Ius backgrounds of the dark slides, the interim's own
OUT = sys.argv[1]

# ------------------------------------------------------------ copied from build_interim_live.py (lines 36-325),
# by a script, with the named substitutions of KB §69.65 only; that builder is left untouched
RIGHT = MARGIN + CONTENT_W                   # right edge of the content area
FIG_H = 380 * PT                             # tallest a figure may be under the title
SIDE_MAX_W = 520 * PT                        # wider than this at FIG_H, and the takeaways go below
WIDE_MAX_H = 290 * PT                        # a full-width map leaves room for four takeaways
LEGEND = PT // 2                             # a legend's size: 0.5 pt per exported pixel on every slide,
                                             # its text about 1.4 x its size in the layout (KB §69.14)
GAP_PX = 24                                  # blank bands inside a layout export close to this (pixels)
MINUS = "−"

# The backgrounds of the dark slides: Ius Chasma from layouts 01 and 02, the map frame only (pixels)
VISIBLE = os.path.join(IIMG, "01_visible.png")
NIGHT = os.path.join(IIMG, "02_night_ir.png")
CANYON = (300, 20, 1953, 950)                # the canyon and its tributaries
CREDIT_VIS = "Ius Chasma, 271–286°E: Viking MDIM 2.1 colour on this project's 100 m grid"
CREDIT_NIGHT = "Ius Chasma, 271–286°E: THEMIS night IR on this project's 100 m grid"
GRID = graticule(VISIBLE)                    # painted out of both backgrounds; the maps keep theirs


def dark(p):
    """The navy-ground copy from make_final_dark.py, if there is one (KB §69.13, §69.65)."""
    d = os.path.join(IMG, "dark", os.path.basename(p))
    return d if os.path.exists(d) else p


def _keep(used, gap):
    """Indices to keep along one axis: every used one; of each blank run inside, `gap`; of the blank
    margins, none."""
    idx = np.flatnonzero(used)
    if not len(idx):
        return np.arange(len(used))
    keep = []
    for i, j in zip(idx[:-1], idx[1:]):
        keep.append(i)
        if j - i - 1 > gap:                  # a blank run longer than gap: its two ends only
            keep.extend(range(i + 1, i + 1 + gap // 2))
            keep.extend(range(j - (gap - gap // 2), j))
        else:
            keep.extend(range(i + 1, j))
    keep.append(idx[-1])
    return np.array(keep)


_TIGHT = {}


def tight(path):
    """A layout export with its blank page margins cut and its blank bands closed to GAP_PX (KB §69.14):
    Pro places the frames on a page, and the page's empty rows (between the ±60° mosaic's two rows of
    panels, above and below the scale bars) took slide room from the maps. In memory, for the deck only.
    Returns PNG bytes and the size."""
    if path not in _TIGHT:
        a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
        ink = np.abs(a - a[0, 0]).max(axis=2) > 24
        a = a[_keep(ink.any(axis=1), GAP_PX)][:, _keep(ink.any(axis=0), GAP_PX)]
        buf = io.BytesIO()
        Image.fromarray(a.astype(np.uint8)).save(buf, "PNG")
        _TIGHT[path] = (buf.getvalue(), (a.shape[1], a.shape[0]))
    return _TIGHT[path]


CHIP = (190, 190, 190)                       # the hillshade's grey: a swatch the navy ground would hide sits on it
ITEM_GAP = 40                                # blank columns this wide separate a legend's columns of items (px)


def _ink(a, ground):
    return np.abs(a.astype(np.int16) - ground).max(axis=2) > 24


def _runs(used, gap):
    """(start, stop) of each run of used indices, runs joined across blanks shorter than gap."""
    idx = np.flatnonzero(used)
    if not len(idx):
        return []
    cuts = np.flatnonzero(np.diff(idx) > gap)
    starts = np.r_[idx[0], idx[cuts + 1]]
    stops = np.r_[idx[cuts], idx[-1]] + 1
    return list(zip(starts, stops))


def _contrast(c1, c2):
    def lum(c):
        c = np.asarray(c, float) / 255
        c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    l1, l2 = sorted((lum(c1), lum(c2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def _chip(seg, ground):
    """A swatch too dark for the navy ground (a contrast under 2:1) gets the map's grey behind it, so it reads as
    it does on the map; the text beside it is left alone."""
    ink = _ink(seg, ground)
    runs = _runs(ink.any(axis=0), 12)
    if len(runs) < 2:
        return seg
    c0, c1 = runs[0]                         # the swatch: the leftmost run of ink, before the label
    sw = ink[:, c0:c1]
    if _contrast(seg[:, c0:c1][sw].mean(axis=0), ground) >= 2:
        return seg
    r0, r1 = _runs(sw.any(axis=1), 2)[0]
    seg = seg.copy()
    box = (slice(max(r0 - 6, 0), r1 + 6), slice(max(c0 - 6, 0), c1 + 6))
    patch = seg[box]
    patch[~_ink(patch, ground)] = CHIP
    return seg


def restack(path, room_h, max_w):
    """A wide one-row legend (Pro lays the items out in columns across) regrouped into the columns that fit the
    room under the map at the largest scale, reframed; dark swatches on a grey chip (KB §69.16). In memory, like
    tight(); returns the key add_pic and png_size take."""
    a = np.asarray(Image.open(io.BytesIO(tight(path)[0])).convert("RGB"))
    cols, counts = np.unique(a.reshape(-1, 3), axis=0, return_counts=True)
    ground = cols[counts.argmax()].astype(np.int16)
    ink = _ink(a, ground)
    edge = np.flatnonzero(ink.mean(axis=1) > 0.9)       # the frame: rows and columns inked almost the whole way
    frame = a[edge[0], a.shape[1] // 2] if len(edge) else None
    t, b = (edge[edge < 12].max() + 1, edge[edge > a.shape[0] - 12].min()) if len(edge) else (0, a.shape[0])
    edge = np.flatnonzero(ink.mean(axis=0) > 0.9)
    l, r = (edge[edge < 12].max() + 1, edge[edge > a.shape[1] - 12].min()) if len(edge) else (0, a.shape[1])
    inner, iink = a[t:b, l:r], ink[t:b, l:r]
    segs = []
    for c0, c1 in _runs(iink.any(axis=0), ITEM_GAP):
        rr = _runs(iink[:, c0:c1].any(axis=1), 10 ** 6)[0]
        seg = np.empty((rr[1] - rr[0] + 16, c1 - c0 + 16, 3), np.uint8)   # 8 px of ground round each item,
        seg[:] = ground                                                    # so a chip clears the item's edge
        seg[8:-8, 8:-8] = inner[rr[0]:rr[1], c0:c1]
        segs.append(_chip(seg, ground))
    pad, vgap, hgap = 18, 2, ITEM_GAP - 16

    def size(groups):
        ws = [max(s.shape[1] for s in g) for g in groups]
        hs = [sum(s.shape[0] for s in g) + vgap * (len(g) - 1) for g in groups]
        return sum(ws) + hgap * (len(groups) - 1) + 2 * pad, max(hs) + 2 * pad

    best = None
    n = len(segs)
    for mask in range(2 ** max(n - 1, 0)):   # every split of the items, in order, into columns
        groups, g = [], [segs[0]]
        for j in range(1, n):
            if mask >> (j - 1) & 1:
                groups.append(g)
                g = []
            g.append(segs[j])
        groups.append(g)
        w, h = size(groups)
        scale = min(room_h / h, max_w / w, LEGEND / float(PT))
        if best is None or scale > best[0]:
            best = (scale, groups, w, h)
    _, groups, w, h = best
    out = np.empty((h, w, 3), np.uint8)
    out[:] = ground
    x = pad
    for g in groups:
        y = pad
        for sgm in g:
            out[y:y + sgm.shape[0], x:x + sgm.shape[1]] = sgm
            y += sgm.shape[0] + vgap
        x += max(sgm.shape[1] for sgm in g) + hgap
    if frame is not None:
        out[:2], out[-2:], out[:, :2], out[:, -2:] = frame, frame, frame, frame
    buf = io.BytesIO()
    Image.fromarray(out).save(buf, "PNG")
    key = path + "|stacked"
    _TIGHT[key] = (buf.getvalue(), (w, h))
    return key


def is_layout(path):
    """A navy-ground layout export: interim_img\\dark\\<two digits>_<name>[__map|__legend].png."""
    return os.path.basename(os.path.dirname(path)) == "dark" and os.path.basename(path)[:2].isdigit()


def png_size(path):
    if is_layout(path):
        return tight(path)[1]
    with Image.open(path) as im:
        return im.size


def image_path(kind, ref):
    p = os.path.join(IMG, ref + ".png") if kind == "layout" else os.path.join(HERE, ref)
    if not os.path.exists(p):
        sys.exit("missing image %s: run make_final_figs.py / make_fig_final.py first" % p)
    return dark(p)


def add_pic(s, path, x, y, w=None, h=None):
    """A picture at its own aspect; a layout export goes in tightened (tight())."""
    px_w, px_h = png_size(path)
    if w is None:
        w = int(h * px_w / px_h)
    if h is None:
        h = int(w * px_h / px_w)
    src = io.BytesIO(tight(path)[0]) if is_layout(path) else path
    s.shapes.add_picture(src, Emu(x), Emu(y), Emu(w), Emu(h))
    return w, h


def below(s, f, y):
    """Takeaways under a picture. The KB § in f["source"] is not printed (KB §69.9)."""
    bullets(s, f["points"], size=14, top=y, height=BOTTOM - y, space=4)


def split_legend(s, f, path):
    """If make_interim_figs.py wrote <layout>__map.png and __legend.png, use them: the map
    across the full width, the takeaways under it on the left, the legend on the right."""
    base = os.path.join(IMG, os.path.basename(path)[:-4])
    m, lg = base + "__map.png", base + "__legend.png"
    if not (os.path.exists(m) and os.path.exists(lg)):
        return False
    m, lg = dark(m), dark(lg)
    px_w, px_h = png_size(m)
    if f.get("map_left"):                    # a tall map (16, 17: frame A over frame B): map left at full
        w, h = add_pic(s, m, MARGIN, BODY_Y, h=FIG_H)   # height; takeaways, then the legend, on the right
        x = MARGIN + w + 24 * PT
        tw = RIGHT - x
        ph = f.get("points_h", 176) * PT     # points_h (pt): more room when the takeaways run long
        bullets(s, f["points"], size=14, top=BODY_Y, height=ph, space=6, left=x, width=tw)
        y = BODY_Y + ph + 8 * PT
        lw_px, lh_px = png_size(lg)
        lh = BODY_Y + FIG_H - y
        lw = min(int(lh * lw_px / lh_px), tw, lw_px * LEGEND)
        add_pic(s, lg, x, y, w=lw, h=int(lw * lh_px / lw_px))
        return True
    w = CONTENT_W
    h = int(w * px_h / px_w)
    cap = f.get("map_h", 0) * PT or WIDE_MAX_H   # map_h (pt): a lower cap, when the legend is tall
    if h > cap:
        h = cap
        w = int(h * px_w / px_h)
    if f.get("legend_beside"):               # a squarish map (09): map left, the legend in the room to its right,
        add_pic(s, m, MARGIN, BODY_Y, w=w, h=h)   # the takeaways full width beneath (KB §69.16)
        x = MARGIN + w + 24 * PT
        lw_px, lh_px = png_size(lg)
        lw = min(RIGHT - x, lw_px * LEGEND, int(h * lw_px / lh_px))
        add_pic(s, lg, x, BODY_Y, w=lw, h=int(lw * lh_px / lw_px))
        below(s, f, BODY_Y + h + 12 * PT)
        return True
    add_pic(s, m, MARGIN + (CONTENT_W - w) // 2, BODY_Y, w=w, h=h)
    y = BODY_Y + h + 12 * PT
    room = BOTTOM - y                        # height left above the footer
    lw_px, lh_px = png_size(lg)
    max_w = 300 * PT
    if lw_px > 3 * lh_px:                    # one wide row of items: regrouped to fit the room (KB §69.16)
        lg = restack(lg, room / float(PT), max_w / float(PT))
        lw_px, lh_px = png_size(lg)
    lw = min(int(room * lw_px / lh_px), max_w, lw_px * LEGEND)
    lh = int(lw * lh_px / lw_px)
    add_pic(s, lg, RIGHT - lw, y, w=lw, h=lh)
    bullets(s, f["points"], size=14, top=y, height=room, space=4, width=CONTENT_W - lw - 18 * PT)
    return True


def figure_slide(prs, f):
    s = new(prs, f["title"], f.get("group"))
    if f.get("verdict"):                     # the hypothesis slides: the answer on the kicker's line
        pill(s, f["verdict"])
    paths = [image_path(k, r) for k, r in f["images"]]
    if len(paths) == 1:
        px_w, px_h = png_size(paths[0])
        aspect = px_w / float(px_h)
        side_h = f.get("side_h", 0) * PT or FIG_H   # side_h (pt): a wide figure drawn left at this height
        if side_h * aspect <= SIDE_MAX_W or f.get("side_h"):   # a tall figure: figure left, takeaways right
            w, _ = add_pic(s, paths[0], MARGIN, BODY_Y, h=side_h)
            x = MARGIN + w + 24 * PT
            tw = RIGHT - x
            bullets(s, f["points"], size=15 if tw > 300 * PT else 14, top=BODY_Y + 8 * PT,
                    height=320 * PT, space=12, left=x, width=tw)
        elif split_legend(s, f, paths[0]):   # map full width; takeaways and legend beneath
            pass
        else:                                # a wide figure: full width, takeaways beneath
            w = CONTENT_W
            h = int(w / aspect)
            cap = f.get("map_h", 0) * PT or WIDE_MAX_H   # map_h (pt): taller, when the takeaways are few
            if h > cap:
                h = cap
                w = int(h * aspect)
            add_pic(s, paths[0], MARGIN + (CONTENT_W - w) // 2, BODY_Y, w=w, h=h)
            below(s, f, BODY_Y + h + 12 * PT)
    else:                                    # figures side by side, takeaways beneath
        gap = 16 * PT
        w = int((CONTENT_W - gap * (len(paths) - 1)) / len(paths))
        h = 0
        for i, p in enumerate(paths):
            _, h = add_pic(s, p, MARGIN + i * (w + gap), BODY_Y, w=w)
        below(s, f, BODY_Y + h + 12 * PT)
    for sh in s.shapes:                      # alt text: the slide's title, not the image's file name (KB §69.9)
        if sh.shape_type == 13:
            sh._element.nvPicPr.cNvPr.set("descr", f["title"])
    return s


def mix(a, b, t):
    return RGBColor(*[int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)])


def issue_cards(s, items, cols, top, h, size):
    gap = 14 * PT
    cw = int((CONTENT_W - (cols - 1) * gap) / cols)
    for k, (label, body) in enumerate(items):
        x = MARGIN + (k % cols) * (cw + gap)
        y = top + (k // cols) * (h + gap)
        card(s, x, y, cw, h)
        tf = textbox(s, x + 16 * PT, y + 12 * PT, cw - 32 * PT, h - 20 * PT)
        p = tf.paragraphs[0]
        no_bullet(p)
        style(p.add_run(), size + 1, bold=True, color=SKY).text = label
        p = tf.add_paragraph()
        no_bullet(p)
        p.space_before = Emu(3 * PT)
        style(p.add_run(), size, color=INK).text = body


def data_slides(prs, group):
    """The bands table and the correlation slide, as the interim draws them (build_interim_live.py lines 426-452)."""
    s = new(prs, "Relevant Spectral Bands", group)
    table(s, ["Band or product", "Wavelength", "Cell", "What it contributes"],
          [[c.replace("r −", "r −").replace("| ≤ ", "| ≤ ") for c in r]
           for r in F.BANDS],                                             # "r −0.49" and "|r| ≤ 0.12" unbroken
          widths=[2.4, 2.25, 0.75, 5.6], size=14, row_h=60 * PT, bold_first=True)

    s = new(prs, "Why Fuse Them: Three Independent Dimensions", group)
    c = F.CORRELATION
    rows = [[b] + [("%+.3f" % v).replace("-", MINUS) if v != 1 else "1" for v in r]
            for b, r in zip(c["bands"], c["r"])]
    t = table(s, ["Ius Chasma, r"] + c["bands"], rows, widths=[1.6] + [1.0] * 5, size=14, row_h=40 * PT,
              bold_first=True)
    for i, r in enumerate(c["r"], 1):            # each cell shaded by |r|, one hue: the pale cells are independent
        for j, v in enumerate(r, 1):
            cell, run = t.cell(i, j), t.cell(i, j).text_frame.paragraphs[0].runs[0]
            cell.fill.solid()
            if i == j:
                cell.fill.fore_color.rgb, run.font.color.rgb = HAIR, MUTED
            else:
                k = abs(v) ** 1.2
                cell.fill.fore_color.rgb = mix(TINT, BLUE, k)
                run.font.color.rgb = WHITE if k > 0.55 else (SKY if abs(v) < 0.2 else INK)
                run.font.bold = abs(v) < 0.2
    note(s, c["takeaway"], 372 * PT, size=14)
    note(s, "Each cell is shaded by the strength of the correlation: the brighter, the more the two bands repeat "
            "each other.", 412 * PT, size=11)


def title_slide(prs):
    """The title slide, as the interim's (build_interim_live.py lines 401-412)."""
    s = blank(prs, dark=True)
    hero_image(s, VISIBLE, CANYON, CREDIT_VIS, GRID)
    veil(s, [(0, 97), (45, 93), (100, 38)])
    kicker(s, "Final presentation  ·  " + F.COURSE, y=152 * PT, dark=True)
    line(s, MARGIN, 170 * PT, 700 * PT, 70 * PT, F.DECK_TITLE, 54, font=HEAD, color=WHITE)
    subtitle = F.TITLE[len(F.DECK_TITLE) + 2:] if F.TITLE.startswith(F.DECK_TITLE + ": ") else F.TITLE   # not twice
    line(s, MARGIN, 246 * PT, 500 * PT, 56 * PT, subtitle, 20, color=PALE)
    line(s, MARGIN, 322 * PT, 500 * PT, 22 * PT, F.AUTHOR, 16, bold=True, color=WHITE)
    line(s, MARGIN, 344 * PT, 500 * PT, 18 * PT, "Status as of " + F.STATUS_DATE, 12, color=PALE)
    credit(s, CREDIT_VIS)
    notes(s, "The final presentation, " + F.STATUS_DATE + ".")
    no_footer.append(len(prs.slides._sldIdLst))


# ------------------------------------------------------------ the final deck's own slides
KB_REF = re.compile(r"\s*\((§[^)]*)\)")      # "(§40.1, §43.2)" at the end of a limit: to the notes, off the slide


def notes(s, text):
    """Speaker notes: here, the KB sections behind the slide (KB §69.9: no KB reference on a slide)."""
    s.notes_slide.notes_text_frame.text = text
    return s


def divider(prs, number, head, blurb, night):
    """A part's opening: the Ius mosaic, a veil, the part's number, name and one line (the interim's results slide)."""
    s = blank(prs, dark=True)
    bg, cr = (NIGHT, CREDIT_NIGHT) if night else (VISIBLE, CREDIT_VIS)
    hero_image(s, bg, CANYON, cr, GRID)
    veil(s, [(0, 94), (60, 86), (100, 60)])
    kicker(s, "Part " + number, y=112 * PT, dark=True)
    line(s, MARGIN, 130 * PT, CONTENT_W, 56 * PT, head, 44, font=HEAD, color=WHITE)
    line(s, MARGIN, 192 * PT, 620 * PT, 40 * PT, blurb, 16, color=PALE)
    credit(s, cr)
    no_footer.append(len(prs.slides._sldIdLst))
    return notes(s, "Part %s: %s." % (number, head))


def question_slide(prs, group):
    """The question and the four goals, as the interim's goals slide."""
    s = notes(new(prs, "The Question", group), "Sources: PROJECT-KNOWLEDGE.md §14.4.")
    line(s, MARGIN, BODY_Y, CONTENT_W, 90 * PT, F.QUESTION, 19, font=HEAD, italic=True, color=INK)
    gap = 16 * PT
    cw = int((CONTENT_W - 3 * gap) / 4)
    for i, g in enumerate(F.GOALS):
        x = MARGIN + i * (cw + gap)
        card(s, x, 216 * PT, cw, 236 * PT)
        dot(s, x + 18 * PT, 236 * PT, 32 * PT, i + 1, size=14)
        line(s, x + 18 * PT, 286 * PT, cw - 36 * PT, 160 * PT, g, 16, color=INK)


prs = deck()
no_footer = []                               # slide numbers that carry no footer
title_slide(prs)
part, group = 0, None
for f in F.FIGURES:
    if "section" in f:
        part += 1
        group = f["section"][0]
        divider(prs, "%02d" % part, f["section"][0], f["section"][1], night=part % 2 == 0)
    if f.get("special") == "question":
        question_slide(prs, group)
    elif f.get("special") == "bands":
        data_slides(prs, group)
        for sl in list(prs.slides)[-2:]:
            notes(sl, "Sources: PROJECT-KNOWLEDGE.md §3, §18.3, §28.10.")
    elif f.get("special") == "correlation":
        pass                                 # drawn with the bands table by data_slides
    else:
        notes(figure_slide(prs, dict(f, group=group)), "Sources: PROJECT-KNOWLEDGE.md " + f["source"] + ".")

# ------------------------------------------------------------ verdicts, limits, conclusions, next
part += 1
divider(prs, "%02d" % part, "What It Adds Up To", "The hypotheses, the limits, the answer", night=part % 2 == 0)
group = "What it adds up to"

s = new(prs, "The Hypotheses and Tests", group)
table(s, ["", "Claim", "Verdict"], [list(r[:3]) for r in F.HYPOTHESES],
      widths=[0.5, 3.8, 6.8], size=13, row_h=52 * PT, bold_first=True)
notes(s, "Sources: PROJECT-KNOWLEDGE.md " + "; ".join("%s %s" % (r[0], r[3]) for r in F.HYPOTHESES) + ".")

s = new(prs, "Limits", group)
items = [(head, KB_REF.sub("", body).rstrip(".") + ".") for head, body in F.LIMITS]
issue_cards(s, items, 2, BODY_Y, int((BOTTOM - BODY_Y - 3 * 14 * PT) / 4), 11)
notes(s, "Sources: PROJECT-KNOWLEDGE.md " + "; ".join(
    "%s %s" % (head.split(":")[0], ", ".join(KB_REF.findall(body))) for head, body in F.LIMITS) + ".")

s = notes(new(prs, "Conclusions", group), "The conclusions of the paper, item for item.")
bullets(s, F.CONCLUSIONS, size=17, top=BODY_Y, height=BOTTOM - BODY_Y, space=14)

s = notes(new(prs, "What Next", group), "NEXT-STEPS.md §12.4 W6 and §14.")
gap = 14 * PT
n = len(F.NEXT_STEPS)
cw = int((CONTENT_W - (n - 1) * gap) / n)
for i, text in enumerate(F.NEXT_STEPS):
    x = MARGIN + i * (cw + gap)
    card(s, x, BODY_Y, cw, 220 * PT)
    dot(s, x + 14 * PT, BODY_Y + 14 * PT, 26 * PT, i + 1, size=12)
    line(s, x + 14 * PT, BODY_Y + 50 * PT, cw - 28 * PT, 164 * PT, text, 13, color=INK)
note(s, F.DATA, BODY_Y + 244 * PT, size=13)

s = blank(prs, dark=True)
hero_image(s, VISIBLE, CANYON, CREDIT_VIS, GRID)
veil(s, [(0, 97), (45, 93), (100, 38)])
line(s, MARGIN, 170 * PT, 700 * PT, 70 * PT, "Questions?", 54, font=HEAD, color=WHITE)
line(s, MARGIN, 246 * PT, 560 * PT, 56 * PT, F.TITLE, 18, color=PALE)
line(s, MARGIN, 322 * PT, 560 * PT, 22 * PT, F.AUTHOR + "  ·  " + F.COURSE, 14, color=WHITE)
credit(s, CREDIT_VIS)
notes(s, "Questions.")
no_footer.append(len(prs.slides._sldIdLst))

footer(prs, F.DECK_TITLE + "  ·  Final presentation", set(no_footer))
silent = [i for i, sl in enumerate(prs.slides, 1) if not sl.notes_slide.notes_text_frame.text.strip()]
assert not silent, "slides without a speaker note: %s" % silent

cp = prs.core_properties                      # python-pptx's defaults name its own author (KB §69.9)
cp.author = cp.last_modified_by = F.AUTHOR
cp.title, cp.subject, cp.comments, cp.keywords = F.TITLE, "Final presentation", "", ""
cp.revision = 1
prs.save(OUT)
print("wrote", OUT, "-", len(prs.slides._sldIdLst), "slides")
