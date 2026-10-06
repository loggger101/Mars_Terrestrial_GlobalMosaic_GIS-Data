# -*- coding: utf-8 -*-
"""Presentation 1 - Project Prospectus, following '1 Project Statement.pdf'."""

import copy, sys
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.text import PP_ALIGN

import content as C
from deck_helpers import (new_slide, add_banner, add_bullets, add_labeled,
                          add_table, add_note, textbox, style, no_bullet,
                          bullet, MARGIN_L, CONTENT_W, BODY_TOP, RUST, INK,
                          GREY)

TEMPLATE = sys.argv[1]
OUT = sys.argv[2]
BANNER = "Remote Sensing Project – Project Prospectus"

prs = Presentation(TEMPLATE)
# strip the two template skeleton slides; the master/theme are what we keep
xml_slides = prs.slides._sldIdLst
for sld in list(xml_slides):
    rid = sld.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    prs.part.drop_rel(rid)
    xml_slides.remove(sld)

# ------------------------------------------------------------------- 1. TITLE
s = prs.slides.add_slide(prs.slide_layouts[6])
add_banner(s, BANNER)

tf = textbox(s, MARGIN_L, 1900000, CONTENT_W, 1500000)
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
no_bullet(p)
style(p.add_run(), 30, bold=True, color=RUST).text = C.TITLE

tf = textbox(s, MARGIN_L, 3550000, CONTENT_W, 1800000)
first = True
for line in C.INVESTIGATORS:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    p.alignment = PP_ALIGN.CENTER
    no_bullet(p)
    p.space_after = Pt(6)
    style(p.add_run(), 16, color=GREY).text = line

# ------------------------------------------------------- 2. INTRO: BACKGROUND
s = new_slide(prs, BANNER, "Introduction — Background and Mission")
tf = textbox(s, MARGIN_L, BODY_TOP, CONTENT_W, 900000)
p = tf.paragraphs[0]
no_bullet(p)
style(p.add_run(), 15, bold=True, color=RUST).text = "Mission:  "
style(p.add_run(), 15, color=INK).text = C.MISSION
add_bullets(s, C.BACKGROUND, top=2800000, height=3500000, size=15)

# ------------------------------------------------------------ 3. INTRO: TASKS
s = new_slide(prs, BANNER, "Introduction — Tasks Required to Meet the Mission")
add_table(s,
          ["#", "Task", "What it involves"],
          [[i, t, d] for i, (t, d) in enumerate(C.TASKS, 1)],
          top=1620000, widths=[0.5, 3.0, 8.0], size=10.5, row_h=250000)

# ----------------------------------------------------- 4. INTRO: SIGNIFICANCE
s = new_slide(prs, BANNER, "Introduction — Significance of the Mission")
add_bullets(s, C.SIGNIFICANCE, size=16, space=14)

# ------------------------------------------------------- 5. METHODS: SPECTRUM
s = new_slide(prs, BANNER, "Methods — Applicable Regions of the EM Spectrum")
add_table(s,
          ["Region", "Wavelength", "What it contributes to the mission"],
          [[a, b, c] for a, b, c in C.SPECTRUM],
          top=1620000, widths=[1.2, 1.6, 8.2], size=12, row_h=450000)
add_note(s, C.SPECTRUM_NOTES[0], top=4150000, size=11)
add_note(s, C.SPECTRUM_NOTES[1], top=4750000, size=11)

# ----------------------------------------------------------- 6. METHODS: DATA
s = new_slide(prs, BANNER, "Methods — Data Sources Already Acquired")
add_table(s,
          ["Dataset", "Mission", "Type", "Resolution", "Measured properties"],
          [list(r) for r in C.DATA_HELD],
          top=1600000, widths=[2.6, 1.5, 2.0, 1.2, 4.2], size=10, row_h=290000)
add_note(s, "Roughly 32 GB of global imagery on disk, all public: USGS Astrogeology "
            "Annex, PDS nodes, ASU Mars Space Flight Facility. Properties above were "
            "measured from the files themselves.", top=4050000, size=11)

s = new_slide(prs, BANNER, "Methods — Data Still Required")
add_table(s,
          ["Dataset", "Resolution", "Why it is needed"],
          [list(r) for r in C.DATA_NEEDED],
          top=1620000, widths=[2.6, 1.3, 7.6], size=11, row_h=560000)
add_note(s, "A global CTX mosaic is deliberately excluded: multi-terabyte, and not "
            "tractable on this hardware. CTX is scoped to bounded windows only.",
         top=4250000, size=11)

# ---------------------------------------------------------- 7. METHODS: BANDS
s = new_slide(prs, BANNER, "Methods — Which Spectral Bands, and Why")
add_table(s,
          ["Band or product", "Wavelength", "Why this band"],
          [list(r) for r in C.BANDS],
          top=1600000, widths=[2.4, 1.8, 7.3], size=10.5, row_h=300000)

# ----------------------------------------------------- 8. METHODS: RESOLUTION
# Split across two slides: all four resolution types on one slide overflows.
def resolution_slide(title, pairs):
    sl = new_slide(prs, BANNER, title)
    items = []
    for kind, lines in pairs:
        items.append((0, kind))
        for ln in lines:
            items.append((1, ln))
    add_bullets(sl, items, top=1620000, height=4900000, size=15, space=8)
    return sl


resolution_slide("Methods — Resolution Required (1 of 2): Spatial and Spectral",
                 C.RESOLUTION[:2])
resolution_slide("Methods — Resolution Required (2 of 2): Radiometric and Temporal",
                 C.RESOLUTION[2:])

# ------------------------------------------------------- 9. METHODS: SCHEDULE
s = new_slide(prs, BANNER, "Methods — Project Schedule")
add_table(s,
          ["Week", "Dates (2026)", "Activity", "Deliverable"],
          [list(r) for r in C.SCHEDULE],
          top=1620000, widths=[0.8, 1.8, 6.6, 2.3], size=11, row_h=330000)
add_note(s, "Semester dates are assumed — adjust to your syllabus. Weeks 1–3 are "
            "complete. The critical path runs through weeks 4–8: projecting to one "
            "CRS unblocks the composite, and the composite unblocks everything after "
            "it.", top=5850000, size=11)

# -------------------------------------------------------- 10. HYPOTHESES
s = new_slide(prs, BANNER, "Expected Results — Hypotheses to be Tested")
add_labeled(s, C.HYPOTHESES, top=1650000, size=15, space=16)

# --------------------------------------------------------- 11. QUESTIONS
s = new_slide(prs, BANNER, "Expected Results — Questions to be Answered")
add_bullets(s, C.QUESTIONS, size=15, space=14)

# ---------------------------------------------------------- 12-13. PROBLEMS
s = new_slide(prs, BANNER, "Expected Results — Potential Problems (1 of 2)")
add_labeled(s, C.PROBLEMS[:5], top=1650000, size=14, space=14)

s = new_slide(prs, BANNER, "Expected Results — Potential Problems (2 of 2)")
add_labeled(s, C.PROBLEMS[5:], top=1650000, size=14, space=12)

prs.save(OUT)
print("wrote", OUT, "-", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
