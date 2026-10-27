# -*- coding: utf-8 -*-
"""The interim deck's design for the 10 November talk (KB §69.11-§69.14): navy throughout, over the project's mosaic.

le_theme.py, the author's Presentation 1 design, stays as it is for the decks that still use it (Presentation 1,
the final deck). This one, on 2026-10-27: basalt and rust first (§69.11), then navy and blues on white (§69.12),
then every slide dark (§69.13; the author: "I don't want to be blinded by white backgrounds"):

  960 x 540 pt  |  Cambria headings, Calibri body (both ship with every Office since 2007; Aptos does not)
  every slide on navy (#0E2841, le_theme.py's); the title and divider slides over Ius Chasma from the project's
    own 100 m mosaic; light text (INK #EAF0F7), a sky kicker above a white 28 pt title, a quiet footer
  sky (#8CC4EC): kickers, bullets, labels, numbered dots, headline numbers; blue (#4A90D9): bars and shading
  cards and alternate rows a lighter navy (TINT #163A61), table heads a deeper one (DEEP #081A2E)
  the charts and layouts come navy-ground from make_interim_dark.py (interim_img\\dark\\), the originals white
  then refined (§69.14): the backgrounds' graticule painted out (graticule, degraticule); a hypothesis slide's
    verdict in an outlined capsule on the kicker's line (pill)
"""

import io
import os

import numpy as np
from lxml import etree
from PIL import Image, ImageFont
from scipy import ndimage
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

PT = 12700
W, H = 960 * PT, 540 * PT
A = "http://schemas.openxmlformats.org/drawingml/2006/main"

HEAD = "Cambria"
BODY = "Calibri"

NAVY = RGBColor(0x0E, 0x28, 0x41)
INK = RGBColor(0xEA, 0xF0, 0xF7)            # text: light, on navy
MUTED = RGBColor(0xA9, 0xBA, 0xCD)
HAIR = RGBColor(0x2E, 0x50, 0x76)           # tracks and rules
TINT = RGBColor(0x16, 0x3A, 0x61)           # cards, alternate rows
DEEP = RGBColor(0x08, 0x1A, 0x2E)           # table heads
BLUE = RGBColor(0x4A, 0x90, 0xD9)
SKY = RGBColor(0x8C, 0xC4, 0xEC)
PALE = RGBColor(0xC5, 0xD3, 0xE3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

MARGIN = 56 * PT
CONTENT_W = W - 2 * MARGIN                  # 848 pt
KICKER_Y = 34 * PT
TITLE_Y = 50 * PT
BODY_Y = 112 * PT
BOTTOM = 506 * PT                            # content stops here; the footer sits below
FOOT_Y = 516 * PT
TITLE_SIZE = 28                              # the widest title, Cambria, measured at 790 of 848 pt


def deck():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(W), Emu(H)
    return prs


def _sub(parent, tag, **attrs):
    el = etree.SubElement(parent, "{%s}%s" % (A, tag))
    for k, v in attrs.items():
        el.set(k, v)
    return el


def hexof(rgb):
    return "%02X%02X%02X" % (rgb[0], rgb[1], rgb[2])


def bullet(p, level=0, color=SKY):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(200000 + 260000 * level))
    pPr.set("indent", "-200000")
    clr = _sub(pPr, "buClr")
    _sub(clr, "srgbClr", val=hexof(color))
    _sub(pPr, "buSzPct", val="110000")
    _sub(pPr, "buFont", typeface="Arial", pitchFamily="34", charset="0")
    _sub(pPr, "buChar", char="▪" if level == 0 else "–")


def no_bullet(p):
    _sub(p._p.get_or_add_pPr(), "buNone")


def style(run, size, bold=False, color=INK, font=BODY, italic=False, spacing=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font
    if spacing is not None:                  # letter spacing, in points
        run.font._rPr.set("spc", str(int(spacing * 100)))
    return run


def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP, wrap=True):
    tf = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h)).text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    return tf


def line(slide, x, y, w, h, text, size, align=PP_ALIGN.LEFT, **kw):
    """One paragraph of text in its own box; returns the text frame."""
    tf = textbox(slide, x, y, w, h)
    p = tf.paragraphs[0]
    p.alignment = align
    no_bullet(p)
    style(p.add_run(), size, **kw).text = text
    return tf


def blank(prs, dark=False):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = NAVY      # every slide dark (§69.13); `dark` kept for the callers
    return s


def shape(slide, kind, x, y, w, h, fill=None, round_=None):
    sh = slide.shapes.add_shape(kind, Emu(x), Emu(y), Emu(w), Emu(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    sh.shadow.inherit = False
    if round_ is not None:
        sh.adjustments[0] = round_
    return sh


def card(slide, x, y, w, h, fill=TINT):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, round_=0.05)


def dot(slide, x, y, d, label, fill=SKY, color=NAVY, size=13):
    """A numbered disc: the deck's one repeated mark."""
    sh = shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill)
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    style(p.add_run(), size, bold=True, color=color, font=HEAD).text = str(label)
    return sh


def kicker(slide, text, x=MARGIN, y=KICKER_Y, dark=False, w=CONTENT_W):
    return line(slide, x, y, w, 14 * PT, text.upper(), 10.5, bold=True,
                color=SKY, spacing=1.6)


def text_width(text, size, bold=True, spacing=0.0):
    """Width in EMU of one line of Calibri, measured with the font file (an estimate without it)."""
    try:
        f = ImageFont.truetype(os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts",
                                            "calibrib.ttf" if bold else "calibri.ttf"), 100)
        w = f.getlength(text) * size / 100.0
    except OSError:
        w = 0.55 * size * len(text)
    return int((w + spacing * len(text)) * PT)


def pill(slide, text, right=MARGIN + CONTENT_W, y=KICKER_Y - 4 * PT, color=SKY):
    """A verdict on the kicker's line, right-aligned: capitals in an outlined capsule (KB §69.14)."""
    text = text.upper()
    pad, h = 10 * PT, 21 * PT
    w = text_width(text, 10, spacing=1.2) + 2 * pad
    sh = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, right - w, y, w, h, None, round_=0.5)
    sh.line.fill.solid()
    sh.line.fill.fore_color.rgb = color
    sh.line.width = Emu(int(1.25 * PT))
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    no_bullet(p)
    style(p.add_run(), 10, bold=True, color=color, spacing=1.2).text = text
    return sh


def new(prs, title, kicker_text=None):
    """A white content slide: kicker, title, nothing under it."""
    s = blank(prs)
    if kicker_text:
        kicker(s, kicker_text)
    line(s, MARGIN, TITLE_Y, CONTENT_W, 44 * PT, title, TITLE_SIZE, font=HEAD, color=WHITE)
    return s


# ------------------------------------------------------------------ the dark slides over the mosaic
def graticule(path):
    """Where a colour layout's graticule is (KB §69.14): its labels, white text haloed in exact grey
    (40, 40, 40), and its lines, rows and columns brighter than their neighbours the whole way across.
    A label is a cluster of that grey (the imagery's shadows are tinted, never exactly grey). The night
    IR layout shares the frame, so what is found in the colour one serves it too.
    Returns (rows, columns, label boxes): runs of line pixels and padded (top, bottom, left, right)."""
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    halo = np.all(np.abs(a - 40) <= 1, axis=2)
    lab, _ = ndimage.label(ndimage.binary_dilation(halo, iterations=2))
    boxes = [(sl[0].start - 3, sl[0].stop + 3, sl[1].start - 3, sl[1].stop + 3)
             for sl in ndimage.find_objects(lab) if halo[sl].sum() > 300 and halo[sl].mean() > 0.25]
    v = a.sum(axis=2)
    lines = []
    for m in (v, v.T):                                            # rows (parallels), then columns (meridians)
        excess = np.median(m[1:-1] - (m[:-2] + m[2:]) / 2.0, axis=1)
        hit = sorted(set((1 + np.flatnonzero(excess > 25)).tolist()))
        runs = []
        for i in hit:
            if runs and i <= runs[-1][1] + 2:
                runs[-1][1] = i
            else:
                runs.append([i, i])
        lines.append([(s - 2, e + 3) for s, e in runs])           # the antialiased edge too
    return lines[0], lines[1], boxes


def degraticule(im, g):
    """The graticule `g` (graticule()) painted out with the ground beside it: each line with the band of
    the same width beside it, then each label with the patch of its size to its left (or right), taken
    after the lines so no line is copied in. The ground keeps its grain, which a blur would not; this
    is a background, not a map."""
    a = np.asarray(im.convert("RGB")).copy()
    rows, cols, boxes = g
    for s, e in rows:
        w = e - s
        src = s - w if s - w >= 0 else e
        a[s:e, :] = a[src:src + w, :]
    for s, e in cols:
        w = e - s
        src = s - w if s - w >= 0 else e
        a[:, s:e] = a[:, src:src + w]
    for t, b, l, r in boxes:
        w = r - l
        src = l - w - 2 if l - w - 2 >= 0 else r + 2
        a[t:b, l:r] = a[t:b, src:src + w]
    return Image.fromarray(a)


def hero_image(slide, path, box, descr, grid=None):
    """A full-bleed crop of one of the project's own layouts: `box` (left, top, right, bottom) in
    pixels, widened or narrowed here to the slide's 16:9 about its centre. Never stretched. With
    `grid` (graticule()), the graticule is painted out first."""
    im = Image.open(path).convert("RGB")
    if grid is not None:
        im = degraticule(im, grid)
    l, t, r, b = box
    want = (b - t) * W / float(H)
    cx = (l + r) / 2.0
    l, r = int(round(cx - want / 2)), int(round(cx + want / 2))
    buf = io.BytesIO()
    im.crop((l, t, r, b)).save(buf, "PNG")
    buf.seek(0)
    pic = slide.shapes.add_picture(buf, 0, 0, Emu(W), Emu(H))
    pic._element.nvPicPr.cNvPr.set("descr", descr)
    return pic


def veil(slide, stops, angle=0):
    """A navy gradient over the picture: stops are (position 0-100, alpha 0-100)."""
    sh = shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, W, H, NAVY)
    spPr = sh._element.spPr
    for el in spPr.findall("{%s}solidFill" % A):
        spPr.remove(el)
    gs = "".join('<a:gs pos="%d"><a:srgbClr val="%s"><a:alpha val="%d"/></a:srgbClr></a:gs>'
                 % (p * 1000, hexof(NAVY), a * 1000) for p, a in stops)
    grad = etree.fromstring('<a:gradFill xmlns:a="%s" rotWithShape="1"><a:gsLst>%s</a:gsLst>'
                            '<a:lin ang="%d" scaled="0"/></a:gradFill>' % (A, gs, angle * 60000))
    spPr.find("{%s}prstGeom" % A).addnext(grad)
    return sh


def credit(slide, text):
    line(slide, W - MARGIN - 420 * PT, H - 26 * PT, 420 * PT, 12 * PT, text, 9, align=PP_ALIGN.RIGHT,
         color=PALE, italic=True)


# ------------------------------------------------------------------ text, tables
def bullets(s, items, size=16, top=BODY_Y, height=None, space=10, left=MARGIN, width=CONTENT_W,
            dark=False):
    tf = textbox(s, left, top, width, height or (BOTTOM - top))
    for i, it in enumerate(items):
        lvl, text = it if isinstance(it, tuple) else (0, it)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space)
        bullet(p, lvl, SKY)
        for op in ("≥ ", "≤ ", "≈ "):   # "≥ 1 km" never broken after the sign (KB §69.14)
            text = text.replace(op, op[0] + " ")
        style(p.add_run(), size if lvl == 0 else size - 2,
              color=INK if lvl == 0 else MUTED).text = text
    return tf


def borders(cell, color, width=1.5):
    """Cell rules in `color` (pt): PowerPoint's default table style draws them white, which glares on navy."""
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("lnB", "lnT", "lnR", "lnL"):                 # inserted first-to-last: lnL, lnR, lnT, lnB
        for old in tcPr.findall("{%s}%s" % (A, tag)):
            tcPr.remove(old)
        ln = etree.Element("{%s}%s" % (A, tag), w=str(int(width * PT)))
        _sub(_sub(ln, "solidFill"), "srgbClr", val=hexof(color))
        tcPr.insert(0, ln)


def table(s, headers, rows, top=BODY_Y, widths=None, size=11, row_h=26 * PT, left=MARGIN,
          width=CONTENT_W, bold_first=False):
    sh = s.shapes.add_table(len(rows) + 1, len(headers), Emu(left), Emu(top), Emu(width),
                            Emu(row_h * (len(rows) + 1)))
    t = sh.table
    t.first_row = True
    t.horz_banding = False
    if widths:
        tot = float(sum(widths))
        for i, w in enumerate(widths):
            t.columns[i].width = Emu(int(width * w / tot))
    for i in range(len(rows) + 1):
        t.rows[i].height = Emu(row_h)
        for j in range(len(headers)):
            c = t.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = DEEP if i == 0 else (TINT if i % 2 == 0 else NAVY)
            borders(c, NAVY)
            c.margin_left = c.margin_right = Emu(7 * PT)
            c.margin_top = c.margin_bottom = Emu(2 * PT)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = c.text_frame.paragraphs[0]
            no_bullet(p)
            v = headers[j] if i == 0 else rows[i - 1][j]
            style(p.add_run(), size, bold=(i == 0 or (bold_first and j == 0)),
                  color=WHITE if i == 0 else INK).text = str(v)
    return t


def note(s, text, y, size=12, x=MARGIN, w=CONTENT_W):
    return line(s, x, y, w, 40 * PT, text, size, italic=True, color=MUTED)


def footer(prs, label, skip):
    """The slide number and the deck's name on every slide but those in `skip` (1-based)."""
    for n, s in enumerate(prs.slides, 1):
        if n in skip:
            continue
        line(s, MARGIN, FOOT_Y, 500 * PT, 12 * PT, label, 9, color=MUTED, spacing=0.4)
        line(s, W - MARGIN - 60 * PT, FOOT_Y, 60 * PT, 12 * PT, str(n), 9, bold=True,
             align=PP_ALIGN.RIGHT, color=MUTED)


def png_size(path):
    with Image.open(path) as im:
        return im.size
