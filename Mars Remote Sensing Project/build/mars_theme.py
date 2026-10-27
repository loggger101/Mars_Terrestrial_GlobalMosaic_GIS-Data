# -*- coding: utf-8 -*-
"""The interim deck's design for the 10 November talk (KB §69.11): basalt and rust over the project's own mosaic.

le_theme.py, the author's Presentation 1 design, stays as it is for the decks that still use it (Presentation 1,
the final deck). This one:

  960 x 540 pt  |  Cambria headings, Calibri body (both ship with every Office since 2007; Aptos does not)
  white content slides: a rust kicker above a 28 pt title, no rule under it, a quiet footer with the number
  basalt (#17181C) title, divider and closing slides over Ius Chasma from the project's own 100 m mosaic
  rust (#B4472A) marks what is ours to read: kickers, bullets, numbered dots, the bars of progress
  dust (#E8A46A) carries figures on dark ground
"""

import io
import os

from lxml import etree
from PIL import Image
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

BASALT = RGBColor(0x17, 0x18, 0x1C)
INK = RGBColor(0x1E, 0x1F, 0x23)
MUTED = RGBColor(0x62, 0x65, 0x6C)
HAIR = RGBColor(0xDC, 0xDC, 0xE0)
TINT = RGBColor(0xF3, 0xF3, 0xF5)
RUST = RGBColor(0xB4, 0x47, 0x2A)
DUST = RGBColor(0xE8, 0xA4, 0x6A)
PALE = RGBColor(0xC9, 0xCB, 0xD1)
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


def bullet(p, level=0, color=RUST):
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
    s.background.fill.fore_color.rgb = BASALT if dark else WHITE
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


def dot(slide, x, y, d, label, fill=RUST, color=WHITE, size=13):
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
                color=DUST if dark else RUST, spacing=1.6)


def new(prs, title, kicker_text=None):
    """A white content slide: kicker, title, nothing under it."""
    s = blank(prs)
    if kicker_text:
        kicker(s, kicker_text)
    line(s, MARGIN, TITLE_Y, CONTENT_W, 44 * PT, title, TITLE_SIZE, font=HEAD)
    return s


# ------------------------------------------------------------------ the dark slides over the mosaic
def hero_image(slide, path, box, descr):
    """A full-bleed crop of one of the project's own layouts: `box` (left, top, right, bottom) in
    pixels, widened or narrowed here to the slide's 16:9 about its centre. Never stretched."""
    im = Image.open(path).convert("RGB")
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
    """A basalt gradient over the picture: stops are (position 0-100, alpha 0-100)."""
    sh = shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, W, H, BASALT)
    spPr = sh._element.spPr
    for el in spPr.findall("{%s}solidFill" % A):
        spPr.remove(el)
    gs = "".join('<a:gs pos="%d"><a:srgbClr val="%s"><a:alpha val="%d"/></a:srgbClr></a:gs>'
                 % (p * 1000, hexof(BASALT), a * 1000) for p, a in stops)
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
        bullet(p, lvl, DUST if dark else RUST)
        style(p.add_run(), size if lvl == 0 else size - 2,
              color=WHITE if dark else (INK if lvl == 0 else MUTED)).text = text
    return tf


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
            c.fill.fore_color.rgb = BASALT if i == 0 else (TINT if i % 2 == 0 else WHITE)
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
