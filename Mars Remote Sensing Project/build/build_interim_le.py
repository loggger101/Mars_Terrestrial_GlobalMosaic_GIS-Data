# -*- coding: utf-8 -*-
"""Interim presentation, in Logan Edwards' deck design.

Covers every heading the supplied '2 Interim Presentation Template.pptx'
asks for, in its order:
  slide 1 -> Project Title, Project Investigators, Project Goals
  slide 2 -> List of Project Tasks and Percent Complete
             Relevant Spectral Bands
             Preliminary Results (if available)
             Project issues and Hurdles
"""

import sys
import content as C
from le_theme import (deck, new, title_slide, section, bullets, labeled, table,
                      note, textbox, style, no_bullet, PT, MARGIN, CONTENT_W,
                      BODY_Y, CYAN, GREY, NAVY)

OUT = sys.argv[1]
prs = deck()
overall = round(sum(v for _, v in C.PROGRESS) / len(C.PROGRESS))

# ============================ slide 1 of the template: title / who / goals ===
title_slide(prs, C.DECK_TITLE,
            (C.COURSE, C.AUTHOR, "Interim Presentation · "
             "%d%% complete" % overall))

s = new(prs, "Project Goals")
tf = textbox(s, MARGIN, BODY_Y, CONTENT_W, 76 * PT)
p = tf.paragraphs[0]
no_bullet(p)
style(p.add_run(), 17).text = C.MISSION
bullets(s, C.GOALS_SHORT, size=16, top=226 * PT, height=250 * PT, space=13)

# ================================ tasks and percent complete ================
s = new(prs, "Project Tasks and Percent Complete")
rows = [[i, t, "%d%%" % v, "■" * max(1, round(v / 10)) if v else "–"]
        for i, (t, v) in enumerate(C.PROGRESS, 1)]
t = table(s, ["#", "Task", "Complete", "Progress"], rows,
          widths=[0.4, 5.6, 1.0, 3.0], size=10, row_h=21 * PT)
for i, (_, v) in enumerate(C.PROGRESS, start=1):
    t.cell(i, 3).text_frame.paragraphs[0].runs[0].font.color.rgb = CYAN if v else GREY
note(s, "Overall completion is approximately %d%%. The base mosaic and its derived "
        "rasters are the gating tasks — classification, digitizing, and crater "
        "counting all wait on them." % overall, 482 * PT)

s = new(prs, "Processing Completed to Date")
table(s, ["When", "Tool", "Parameters", "Outcome"],
      [list(r) for r in C.WORKFLOW_LOG],
      widths=[1.0, 2.0, 3.4, 4.2], size=10, row_h=25 * PT)
note(s, "Recovered from the geoprocessing lineage and tool logs in the project "
        "geodatabase — the actual run history, failures included.", 440 * PT)

# ========================================= relevant spectral bands ==========
s = new(prs, "Relevant Spectral Bands")
table(s, ["Band or product", "Wavelength", "Why this band"],
      [list(r) for r in C.BANDS],
      widths=[2.4, 1.7, 7.0], size=10, row_h=25 * PT)

s = new(prs, "Relevant Spectral Bands — by Region")
table(s, ["Region", "Wavelength", "What it contributes"],
      [[a, b, c] for a, b, c in C.SPECTRUM],
      widths=[1.4, 1.7, 7.4], size=12, row_h=42 * PT)
note(s, "Held today: THEMIS Day IR as the 100 m morphology base, Viking MDIM 2.1 "
        "colour for visible context, and the HRSC/MOLA DEM for slope and drainage. "
        "THEMIS Night IR is the one missing band.", 360 * PT)

# ============================================== preliminary results =========
s = new(prs, "Preliminary Results — Data and Measurements")
labeled(s, C.PRELIM[:3], size=15, space=16)

s = new(prs, "Preliminary Results — Derived Products")
labeled(s, C.PRELIM[3:], size=15, space=16)
note(s, C.PRELIM_NOTE, 470 * PT)

# ============================================== issues and hurdles ==========
s = new(prs, "Project Issues and Hurdles (1 of 2)")
labeled(s, C.ISSUES[:4], size=15, space=16)

s = new(prs, "Project Issues and Hurdles (2 of 2)")
labeled(s, C.ISSUES[4:], size=15, space=16)

# ============================================== remaining work ==============
s = new(prs, "Remaining Work — Immediate Next Steps")
bullets(s, C.NEXT_STEPS, size=16, space=12)

s = new(prs, "Remaining Schedule")
table(s, ["Week", "Dates (2026)", "Activity", "Deliverable"],
      [list(r) for r in C.SCHEDULE[3:]],
      widths=[0.7, 1.6, 6.4, 2.3], size=10.5, row_h=28 * PT)
note(s, "The critical path runs through weeks 5–8: nothing can be classified "
        "until the composite exists, and nothing can be digitized until it is "
        "classified.", 440 * PT)

prs.save(OUT)
print("wrote", OUT, "-", len(prs.slides._sldIdLst), "slides")
