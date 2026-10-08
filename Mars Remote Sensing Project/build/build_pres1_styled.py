# -*- coding: utf-8 -*-
"""Presentation 1 -- dark redesign, same words.

Rebuilds 'ocean first pres LE (2).pdf' as a .pptx. Every sentence, table cell,
caption and figure is carried over verbatim from that PDF; the design is new.

  ground      #0E2841 on every slide, #060E16 on the title
  header      eyebrow (was the subtitle) in letterspaced cyan over an Aptos
              Display title, closed by a hairline across the content width with
              the slide number sitting on its right end -- no accent bars
  lists       bullet glyphs dropped. Each item is a row: a hairline, a cyan
              ordinal, then the text in a 700 pt column
  tables      no white header block; a cyan letterspaced head over a cyan rule,
              rows separated by hairlines and banded in #14314C
  figures     re-rendered on the slide ground by make_figs_dark.py, so they sit
              in the slide instead of floating as lit rectangles
  title       a whole-Mars orthographic disc from the project's own Viking mosaic,
              bleeding off the right edge (make_globe.py)

    python build_pres1_styled.py [img_dir] [out.pptx]
"""

import os
import sys

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ================================================================ SYSTEM =====

PT = 12700
W, H = 960 * PT, 540 * PT
A = "http://schemas.openxmlformats.org/drawingml/2006/main"

DISPLAY = "Aptos Display"
BODY = "Aptos"

GROUND = RGBColor(0x0E, 0x28, 0x41)      # the slide ground, the Presentation 1 navy
DEEP = RGBColor(0x06, 0x0E, 0x16)        # title slide only
BAND = RGBColor(0x14, 0x31, 0x4C)        # table banding, panel fills
RULE = RGBColor(0x2A, 0x4A, 0x66)        # hairlines
CYAN = RGBColor(0x0E, 0x9E, 0xD4)
PALE = RGBColor(0x9E, 0xD8, 0xED)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEXT = RGBColor(0xDD, 0xE8, 0xF0)        # body copy, off-white
MUTE = RGBColor(0x6F, 0x8C, 0xA6)        # notes, footers, ordinals

MARGIN = 65 * PT
CONTENT_W = 830 * PT

EYE_Y = 44 * PT
TITLE_Y = 62 * PT
HEAD_RULE_Y = 122 * PT
BODY_Y = 148 * PT
FOOT_Y = 506 * PT
DECK = "Mars Global Mosaic  ·  OCN 4704"

IMG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "pres1_img")
OUT = sys.argv[2] if len(sys.argv) > 2 else "Mars Global Mosaic - Presentation 1.pptx"


# =============================================================== HELPERS =====

def _sub(parent, tag, **attrs):
    el = etree.SubElement(parent, "{%s}%s" % (A, tag))
    for k, v in attrs.items():
        el.set(k, v)
    return el


def no_bullet(p):
    _sub(p._p.get_or_add_pPr(), "buNone")


def style(run, size, bold=False, color=TEXT, font=BODY, italic=False,
          spacing=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font
    if spacing:                            # letter-spacing, in 1/100 pt
        run.font._rPr.set("spc", str(int(spacing * 100)))
    return run


def line_spacing(p, mult):
    lnSpc = _sub(p._p.get_or_add_pPr(), "lnSpc")
    _sub(lnSpc, "spcPct", val=str(int(mult * 100000)))


def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP, wrap=True):
    tf = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h)).text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    return tf


def para(s, text, x, y, w, size, color=TEXT, font=BODY, bold=False,
         italic=False, lead=1.22, spacing=None, align=None, h=None):
    """One block of copy. Returns its estimated height in EMU."""
    height = h if h is not None else est_h(text, size, w, lead)
    tf = textbox(s, x, y, w, height)
    p = tf.paragraphs[0]
    no_bullet(p)
    line_spacing(p, lead)
    if align is not None:
        p.alignment = align
    style(p.add_run(), size, bold=bold, color=color, font=font, italic=italic,
          spacing=spacing).text = text
    return height


def est_h(text, size, w, lead=1.22):
    """Rough wrapped height. Aptos averages ~0.52 em per character; erring
    wide costs a little slack rather than an overlap."""
    per_line = max(int((w / float(PT)) / (0.52 * size)), 1)
    lines = 0
    for chunk in text.split("\n"):
        lines += max(1, -(-len(chunk) // per_line))
    return int(lines * size * lead * PT)


def rect(s, x, y, w, h, color, alpha=None):
    sh = s.shapes.add_shape(1, Emu(x), Emu(y), Emu(w), Emu(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    if alpha is not None:
        srgb = sh.fill.fore_color._xFill.find("{%s}srgbClr" % A)
        _sub(srgb, "alpha", val=str(int(alpha * 100000)))
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def hairline(s, y, x=MARGIN, w=CONTENT_W, color=RULE):
    return rect(s, x, y, w, int(0.9 * PT), color)


def img_size(path):
    with Image.open(path) as im:
        return im.size


def picture(s, name, x, y, w, h):
    return s.shapes.add_picture(os.path.join(IMG, name), Emu(x), Emu(y),
                                Emu(w), Emu(h))


def picture_box(s, name, x, y, w, h, keep="mid"):
    """Fill an exact box, cropping the overflow -- never stretch a raster."""
    path = os.path.join(IMG, name)
    px_w, px_h = img_size(path)
    native, box = px_w / float(px_h), w / float(h)
    pic = s.shapes.add_picture(path, Emu(x), Emu(y), Emu(w), Emu(h))
    if box > native:
        excess = 1.0 - native / box
        if keep == "top":
            pic.crop_bottom = excess
        else:
            pic.crop_top = pic.crop_bottom = excess / 2.0
    elif native > box:
        excess = 1.0 - box / native
        pic.crop_left = pic.crop_right = excess / 2.0
    return pic


# ================================================================ FRAMES =====

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(W), Emu(H)
COUNT = [0]


def slide(title=None, eyebrow=None, chrome=True, ground=GROUND):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = ground
    COUNT[0] += 1
    if eyebrow:
        para(s, eyebrow.upper(), MARGIN, EYE_Y, CONTENT_W, 10.5, color=CYAN,
             spacing=1.8, h=16 * PT)
    if title:
        para(s, title, MARGIN, TITLE_Y, CONTENT_W, 34, color=WHITE,
             font=DISPLAY, h=46 * PT)
    if chrome:
        hairline(s, HEAD_RULE_Y)
        # the slide number rides the right end of that rule, not a corner
        para(s, "%02d" % COUNT[0], MARGIN, HEAD_RULE_Y - 22 * PT, CONTENT_W,
             13, color=MUTE, spacing=0.3, align=PP_ALIGN.RIGHT, h=18 * PT)
        para(s, DECK, MARGIN, FOOT_Y, CONTENT_W, 9, color=MUTE, spacing=0.4,
             h=14 * PT)
    return s


def rows(s, items, top=BODY_Y, size=16.5, width=700 * PT, gap=17 * PT,
         pad=13 * PT, ordinals=True):
    """A list as ruled rows: hairline, cyan ordinal, copy in one column.

    Replaces the bullet glyph entirely -- the rule does the separating and the
    ordinal does the counting, so nothing has to sit in the text column but
    text."""
    x_text = MARGIN + (58 * PT if ordinals else 0)
    w_text = width - (58 * PT if ordinals else 0)
    y = top
    for i, text in enumerate(items, 1):
        hairline(s, y)
        if ordinals:
            para(s, "%02d" % i, MARGIN, y + pad + 2 * PT, 48 * PT, 13.5,
                 color=CYAN, spacing=0.6, h=18 * PT)
        h = para(s, text, x_text, y + pad, w_text, size, color=TEXT)
        y += pad + h + gap
    return y


def note(s, text, y, size=10.5):
    return para(s, text, MARGIN, y, CONTENT_W, size, color=MUTE, italic=True,
                lead=1.18)


def caption(s, text, x, y, w, sub=None, size=15):
    tf = textbox(s, x, y, w, 40 * PT)
    p = tf.paragraphs[0]
    no_bullet(p)
    style(p.add_run(), size, color=WHITE).text = text
    if sub:
        p = tf.add_paragraph()
        p.space_before = Pt(5)
        no_bullet(p)
        style(p.add_run(), 10.5, color=MUTE).text = sub
    return tf


def table(s, headers, body, top, widths, size=11.5, row_h=30 * PT):
    """Dark table: a cyan letterspaced head over a cyan rule, hairline-split
    rows, banding in #14314C. No boxed header block."""
    tot = float(sum(widths))
    xs, x = [], MARGIN
    for wgt in widths:
        xs.append((x, int(CONTENT_W * wgt / tot)))
        x += int(CONTENT_W * wgt / tot)

    for (cx, cw), head in zip(xs, headers):
        para(s, head.upper(), cx + 10 * PT, top, cw - 20 * PT, 10, color=CYAN,
             spacing=1.4, h=16 * PT)
    y = top + 22 * PT
    rect(s, MARGIN, y, CONTENT_W, int(1.6 * PT), CYAN)
    y += int(1.6 * PT)

    for i, row in enumerate(body):
        heights = [est_h(str(v), size, cw - 20 * PT, 1.18)
                   for (cx, cw), v in zip(xs, row)]
        rh = max(max(heights) + 16 * PT, row_h)
        if i % 2:
            rect(s, MARGIN, y, CONTENT_W, rh, BAND)
        else:
            hairline(s, y + rh, color=RULE)
        for (cx, cw), v in zip(xs, row):
            th = est_h(str(v), size, cw - 20 * PT, 1.18)
            para(s, str(v), cx + 10 * PT, y + (rh - th) // 2, cw - 20 * PT,
                 size, color=WHITE if cx == MARGIN else TEXT,
                 bold=(cx == MARGIN), lead=1.18)
        y += rh
    return y


def figure(s, name, top, band_h, width=CONTENT_W):
    """Fit the content width, cap the height, centre the remainder."""
    pw, ph = img_size(os.path.join(IMG, name))
    w, h = width, int(width * ph / float(pw))
    if h > band_h:
        h, w = band_h, int(band_h * pw / float(ph))
    x = MARGIN + (CONTENT_W - w) // 2
    y = top + (band_h - h) // 2
    return picture(s, name, x, y, w, h)


# ================================================================== 01 =======

s = slide(chrome=False, ground=DEEP)
D = 560 * PT
picture(s, "globe_viking.png", 560 * PT, (H - D) // 2, D, D)
# a soft wash so the disc does not sit on the text column
rect(s, 0, 0, 470 * PT, H, DEEP, alpha=0.55)

para(s, "Mars Global Mosaic", MARGIN, 214 * PT, 440 * PT, 54, color=WHITE,
     font=DISPLAY, lead=1.06, h=140 * PT)
rect(s, MARGIN, 372 * PT, 44 * PT, int(2 * PT), CYAN)
para(s, "REMOTE SENSING 2026 OCN 4704", MARGIN, 392 * PT, 440 * PT, 12,
     color=CYAN, spacing=1.8, h=18 * PT)
para(s, "Logan Edwards", MARGIN, 414 * PT, 440 * PT, 15, color=TEXT, h=22 * PT)

# ================================================================== 02 =======

s = slide("Background", "Goals and Mission")

rect(s, MARGIN, BODY_Y, int(2.4 * PT), 104 * PT, CYAN)
para(s, "Assemble a co-registered global visible and thermal-infrared mosaic "
        "of Mars with altimetric data in ArcGIS Pro from three existing global "
        "products, and use it to map and classify three primary landform "
        "families (volcanic flow units, fluvial channels and valley networks, "
        "and impact craters) producing one internally consistent global "
        "landform inventory.",
     MARGIN + 24 * PT, BODY_Y, 700 * PT, 18, color=WHITE, lead=1.26,
     h=110 * PT)

rows(s, [
    "Three consumer-level(less then 1TB) global products cover Mars end to "
    "end, in three parts of the spectrum. No single product lets you "
    "interrogate morphology, thermal response, and slope at the same pixel; "
    "building that stack is the core technical task.",
    "Each target landform family records a different process (volcanic "
    "resurfacing, flowing water, impact) and each is expressed differently "
    "across the three datasets. That is what makes fusing them worth doing.",
], top=286 * PT, size=15.5, gap=15 * PT)

# ================================================================== 03 =======

s = slide("Significance of the Mission")
rows(s, [
    "Thermal infrared responds to particle size and surface coherence; "
    "visible albedo does not. Where Mars is dust-mantled, the THEMIS layer "
    "should recover flow boundaries the Viking mosaic cannot; a claim this "
    "project can measure.",
    "Discriminating volcanic from fluvial channels is a live problem: "
    "Athabasca Valles was mapped as a fluvial outflow channel for decades "
    "before being reinterpreted as flood lava. Morphology plus thermal "
    "response addresses it.",
    "Testable without privileged data: unit boundaries against the published "
    "USGS global geologic map, crater rims against the 141 IAU-named craters "
    "above 100 km already in the geodatabase.",
], top=BODY_Y + 8 * PT, size=16.5, gap=22 * PT)

# ================================================================== 04 =======

s = slide("Tasks Required")
table(s, ["#", "Task", "What it involves"], [
    ("1", "Acquire the global raster set",
     "Done. All three on disk with statistics built; pyramids still to build."),
    ("2", "Build a grouped mosaic viewer",
     "Done. One map, three groups, each source raster paired with its derived "
     "product."),
    ("3", "Rebuild the terrain derivatives",
     "Re-run Slope and Hillshade on the projected DEM for a valid z-factor."),
    ("4", "Build the visible + infrared composite",
     "Composite Bands over Viking colour and THEMIS day; four bands. Project "
     "first, then run over bounded extents."),
    ("5", "Derive image-gradient products",
     "Edge and texture from DN, labelled as gradient rather than as terrain "
     "slope."),
    ("6", "Classify surface units",
     "Iso Cluster, then Maximum Likelihood on training polygons. Already "
     "rehearsed on the Mercury MESSENGER basemap."),
    ("7", "Digitize landform vectors",
     "Flow margins, channel centerlines and crater rims as three feature "
     "classes."),
    ("8", "Build a real crater inventory",
     "The IAU layers are a gazetteer of 1,113 named craters. Digitize a "
     "sample area or import a catalogue."),
    ("9", "Produce the map layouts",
     "None exist yet. Global sheets at 60°N–60°S plus detail "
     "panels."),
], top=BODY_Y - 8 * PT, widths=[0.05, 0.29, 0.66], size=11.5, row_h=31 * PT)

# ================================================================== 05 =======

s = slide("Which Spectral Bands and Why")
table(s, ["Band or product", "Wavelength", "Why this band"], [
    ("THEMIS Day IR (v12 mosaic)", "6.8–14.9 µm",
     "The morphology and composition base, and the finest global layer held"),
    ("Viking MDIM 2.1 band 1 (red)", "≈ 0.59 µm",
     "Best contrast between ferric dust and darker basalt"),
    ("Viking MDIM 2.1 bands 1/2/3", "visible RGB",
     "Natural-colur context and unit boundary confirmation"),
    ("HRSC/MOLA elevation", "n/a (altimetry)",
     "The vertical reference for every channel gradient measured"),
], top=BODY_Y + 24 * PT, widths=[0.30, 0.16, 0.54], size=14, row_h=54 * PT)

# ================================================================== 06 =======

s = slide("Which Part of the Electromagnetic Spectrum")
figure(s, "em_spectrum_dark.png", BODY_Y - 6 * PT, 340 * PT)

# ================================================================== 07 =======

s = slide("Mapping Extent")
figure(s, "g_extent_dark.png", BODY_Y - 12 * PT, 348 * PT)

# ================================================================== 08 =======

s = slide("Data Sources")
PANEL_W, PANEL_H, GAP = 262 * PT, 226 * PT, 22 * PT
for i, (img, name, meta) in enumerate([
    ("s08_dem.jpg", "HRSC_MOLA_BlendDEM_200m",
     "Elevation · 200 m/px · 106,694 × 53,347"),
    ("s08_themis.jpg", "MO_THEMIS-IR-Day_100m",
     "Thermal IR · 100 m/px · 213,390 × 106,696"),
    ("s08_viking.jpg", "Viking_MDIM21_232m",
     "Visible color · 232 m/px · 92,160 × 46,080 · 3 bands"),
]):
    x = MARGIN + i * (PANEL_W + GAP)
    picture_box(s, img, x, BODY_Y + 10 * PT, PANEL_W, PANEL_H)
    rect(s, x, BODY_Y + 10 * PT + PANEL_H, PANEL_W, int(2.4 * PT), CYAN)
    caption(s, name, x, BODY_Y + 28 * PT + PANEL_H, PANEL_W, sub=meta)

# ================================================================== 09 =======

s = slide("HRSC/MOLA Blended DEM", "The Vertical Reference")
figure(s, "g_dem_dark.png", BODY_Y - 4 * PT, 306 * PT)
note(s, "200 m/px, 106,694 × 53,347, 16-bit. Measured relief "
        "−8,528 m to +21,226 m — 29,754 m from the Hellas floor to "
        "the Olympus Mons summit.", 470 * PT)

# ================================================================== 10 =======

s = slide("THEMIS Day IR", "The 100 m Thermal Base")
figure(s, "g_themis_dark.png", BODY_Y + 4 * PT, 292 * PT)
note(s, "100 m/px, 213,390 × 106,696 — 22.77 billion pixels, of "
        "which 22.14 billion are valid (97.3% coverage). Rolled from central "
        "meridian 180° onto 0° so it registers against the other "
        "two.", 464 * PT)

# ================================================================== 11 =======

s = slide("Viking MDIM 2.1", "The Visible Base")
figure(s, "g_viking_dark.png", BODY_Y + 4 * PT, 292 * PT)
note(s, "232 m/px, 92,160 × 46,080, three bands.", 464 * PT)

# ================================================================== 12 =======

s = slide("Resolution")
COL_W, COL_GAP = 262 * PT, 22 * PT
for i, (label, items) in enumerate([
    ("Spatial", [
        "Set by what is held: 100 m (THEMIS), 200 m (DEM), 232 m (Viking). "
        "The composite can be no finer than its coarsest input.",
        "Ten pixels across a feature to map its margin reliably; so features "
        "of about a kilometer and up. Sub-kilometer tributaries will not "
        "resolve."]),
    ("Spectral", [
        "Four bands held: one thermal, three visible. Enough to separate "
        "broad unit types, not enough to identify minerals."]),
    ("Radiometric", [
        "Both image mosaics are 8-bit as distributed, the practical limit on "
        "how finely units can be separated by DN alone.",
        "The DEM is the exception, carrying a real range of −8,528 m to "
        "+21,226 m. The quantitative measurements come from there."]),
]):
    x = MARGIN + i * (COL_W + COL_GAP)
    rect(s, x, BODY_Y + 6 * PT, COL_W, int(2.4 * PT), CYAN)
    para(s, label.upper(), x, BODY_Y + 20 * PT, COL_W, 13, color=CYAN,
         spacing=1.6, h=22 * PT)
    y = BODY_Y + 50 * PT
    for item in items:
        h = para(s, item, x, y, COL_W, 13.5, color=TEXT, lead=1.3)
        y += h + 18 * PT

# ================================================================== 13 =======

s = slide("Slope from Elevation")
PW, PH = 400 * PT, 274 * PT
for x, name in [(MARGIN, "s13_slope.png"),
                (MARGIN + PW + 30 * PT, "s13_dem.jpg")]:
    picture_box(s, name, x, BODY_Y + 4 * PT, PW, PH)
    rect(s, x, BODY_Y + 7 * PT + PH, PW, int(2.4 * PT), CYAN)
caption(s, "Slope Analysis", MARGIN, 442 * PT, PW)
caption(s, "Mars HRSC MOLA BlendDEM Global 200mp", MARGIN + PW + 30 * PT,
        442 * PT, PW)

# ================================================================== 14 =======

s = slide("Gradient Products")
PW, PH, VGAP = 400 * PT, 144 * PT, 10 * PT
COL2 = MARGIN + PW + 30 * PT
TOP = BODY_Y + 2 * PT
for x, top, name in [(MARGIN, TOP, "s14_vik_grad.jpg"),
                     (MARGIN, TOP + PH + VGAP, "s14_vik.jpg"),
                     (COL2, TOP, "s14_the_grad.jpg"),
                     (COL2, TOP + PH + VGAP, "s14_the.jpg")]:
    picture_box(s, name, x, top, PW, PH)
for x in (MARGIN, COL2):
    rect(s, x, TOP + 2 * PH + VGAP + 3 * PT, PW, int(2.4 * PT), CYAN)
caption(s, "Viking MDIM 2.1", MARGIN, 462 * PT, PW)
caption(s, "THEMIS Day IR", COL2, 462 * PT, PW)

# ================================================================== 15 =======

s = slide("Potential Problems")
y = BODY_Y + 20 * PT
for label, rest in [
    ("Processing time is the schedule:",
     " 1 h 27 min for surface parameters on Viking MDIM alone"),
    ("no sub-meter imagery:",
     " The finest imagery held is 100 m as research grade 5 m imagery is over "
     "10 TB of data. Even if it can be stored, processing time would be "
     "measured in days for simple tasks (Hence Consumer vs Researcher grade)"),
]:
    hairline(s, y)
    tf = textbox(s, MARGIN, y + 16 * PT, 760 * PT, 120 * PT)
    p = tf.paragraphs[0]
    no_bullet(p)
    line_spacing(p, 1.26)
    style(p.add_run(), 17, bold=True, color=CYAN).text = label
    style(p.add_run(), 17, color=TEXT).text = rest
    y += 16 * PT + est_h(label + rest, 17, 760 * PT, 1.26) + 26 * PT

# ================================================================== 16 =======

s = slide("Where This Stands")
rows(s, [
    "Three global rasters on disk, characterized from the files themselves; "
    "43.7 GB, 100–232 m/px, one of them 22.8 billion pixels.",
    "The mapped extent is settled: all 360° of longitude between "
    "60°N and 60°S, which is 86.6% of the surface and caps "
    "plate-carrée scale error at a factor of two.",
    "Next: project everything into one frame, rebuild slope and hillshade, "
    "then run Composite Bands to conjoin different data",
    "The whole plan is testable without privileged data; the USGS global "
    "geologic map and the IAU gazetteer are the references, and the 100 m "
    "floor is stated as a limit rather than worked around.",
], top=BODY_Y + 2 * PT, size=16, gap=16 * PT)

prs.save(OUT)
print("wrote %s -- %d slides" % (OUT, len(prs.slides._sldIdLst)))
