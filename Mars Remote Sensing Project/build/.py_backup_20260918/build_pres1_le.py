# -*- coding: utf-8 -*-
"""Presentation 1, in Logan Edwards' deck design -- trimmed for a short slot.

Slide order still follows '1 Project Statement.pdf' and covers all eleven of
its bullets, but the talk is cut to 16 slides from 22:

  - the three section dividers carried no content and are gone; the slide
    titles do the signposting
  - the spectrum table is folded into the spectrum figure
  - the two resolution slides become one
  - the two problems slides become one

The five figure slides are all kept -- they are the point of the talk. Nothing
is removed from content.py, so the written prospectus stays complete; the deck
just shows fewer of the same items. To restore any of it, widen the slices.

Second pass: the slide count was already right for an eleven-bullet template,
but the words on them were not -- 2,491 body words is a document, not a talk.
The long blocks now come from deck_short.py instead of content.py, one fact
stated in full on the slide that owns it and referenced in a clause elsewhere.
Slide count is unchanged; body words drop to about 1,810, and the space that
 frees is given back to the type rather than to margins -- most body text is
 two to four points larger than it was. To go back to the
long prose, swap the S.* blocks below for their C.* originals.
"""

import sys
import content as C
import deck_short as S
from le_theme import (deck, new, title_slide, bullets, labeled, table,
                      caption, note, picture, picture_box, textbox, style,
                      no_bullet, PT, MARGIN, CONTENT_W, BODY_Y, PALE)

IMG = sys.argv[1]
OUT = sys.argv[2]
prs = deck()

# ================================================================== TITLE ====
title_slide(prs, C.DECK_TITLE, (C.COURSE, C.AUTHOR))

# =========================================================== INTRODUCTION ====
s = new(prs, "Background — Goals and Mission")
tf = textbox(s, MARGIN, BODY_Y, CONTENT_W, 70 * PT)
p = tf.paragraphs[0]
no_bullet(p)
style(p.add_run(), 19).text = C.MISSION
bullets(s, S.BACKGROUND_DECK, size=18, top=228 * PT, height=270 * PT, space=24)

# one clause per task; the paragraphs behind them are in the written prospectus
s = new(prs, "Tasks Required to Meet the Mission")
table(s, ["#", "Task", "What it involves"],
      [[i, t, d] for i, (t, d) in enumerate(S.TASKS_DECK, 1)],
      widths=[0.4, 3.0, 6.6], size=11.5, row_h=30 * PT)

s = new(prs, "Significance of the Mission")
bullets(s, S.SIGNIFICANCE_DECK, size=19, space=26)

# ================================================================= METHODS ===
# the figure replaces the spectrum table; the note carries what each region gives
s = new(prs, "Which Part of the Electromagnetic Spectrum")
picture(s, IMG, "em_spectrum.png", MARGIN, 136 * PT, 830 * PT, 308 * PT)
note(s, "Visible gives morphology and the ferric absorption edge; thermal IR gives "
        "composition through the Si–O reststrahlen bands and, paired with a night "
        "mosaic, thermal inertia; altimetry gives slope and drainage context. Radar "
        "is excluded — it probes the subsurface, not surface landforms.", 452 * PT)

# -- where on the planet the work is being done ---------------------------
# the locator labels its own box, coordinates and Jezero caveat, so a caption
# under it would only repeat the figure; it is spoken instead, and the picture
# gets the space back
s = new(prs, "Type Area and Context Map")
picture(s, IMG, "locator_global.jpg", MARGIN, 150 * PT, 830 * PT, 295 * PT)
note(s, "Viking MDIM 2.1, read from the project’s own copy. The box is the "
        "mosaic viewer’s own saved extent.", 470 * PT)

# -- potential data sources: acquired, rebuilt from the project's own rasters
s = new(prs, "Data Sources — Acquired", dark=True)
specs = [("lz_dem.jpg", "HRSC_MOLA_BlendDEM_200m",
          "Elevation · 200 m/px · 106,694 × 53,347"),
         ("lz_themis.jpg", "MO_THEMIS-IR-Day_100m",
          "Thermal IR · 100 m/px · 213,390 × 106,696"),
         ("lz_viking.jpg", "Viking_MDIM21_232m",
          "Visible colour · 232 m/px · 92,160 × 46,080 · "
          "3 bands")]
for i, (img, cap, spec) in enumerate(specs):
    x = MARGIN + i * 284 * PT          # 3 x 262 + 2 x 22 = 830, the column
    picture_box(s, IMG, img, x, 140 * PT, 262 * PT, 232 * PT, keep="centre")
    caption(s, cap, x, 382 * PT, 262 * PT, dark=True, size=16)
    tf = textbox(s, x, 406 * PT, 262 * PT, 40 * PT)
    p = tf.paragraphs[0]
    no_bullet(p)
    style(p.add_run(), 11, color=PALE).text = spec
note(s, "All three global, public, and already loaded — 44 GB on disk, 22.8 billion "
        "pixels in the thermal layer alone. All three panels are the same 4° × 3.5° "
        "window over Louros Valles: one landform, read three ways at once.",
     470 * PT, dark=True)

# -- potential data sources: still required
s = new(prs, "Data Sources — Still Required")
table(s, ["Dataset", "Resolution", "Why it is needed"],
      [list(r) for r in S.DATA_NEEDED_DECK],
      widths=[2.6, 1.3, 7.1], size=14, row_h=62 * PT)

# -- which spectral bands: the four real bands plus the planned one.
#    The derived products get their own two figure slides below.
s = new(prs, "Which Spectral Bands, and Why")
table(s, ["Band or product", "Wavelength", "Why this band"],
      [list(r) for r in S.BANDS_DECK],
      widths=[2.4, 1.7, 7.0], size=14, row_h=50 * PT)
note(s, "Four real bands — three visible, one thermal — plus elevation as a "
        "separate analysis layer. The derived products are on the next two slides.",
     392 * PT)

# -- resolution required, all four kinds on one slide
s = new(prs, "Resolution Required")     # the four kinds are the bullet labels
items = []
for kind, lines in S.RESOLUTION_DECK:
    items.append((0, kind))
    for ln in lines:
        items.append((1, ln))
bullets(s, items, size=15.5, space=12)

# -- work already done with these data
s = new(prs, "Derived Product — Slope from Elevation")
picture(s, IMG, "s3_img1.png", MARGIN, 132 * PT, 404 * PT, 276 * PT)
picture(s, IMG, "s3_img2.png", MARGIN + 422 * PT, 132 * PT, 404 * PT, 276 * PT)
caption(s, "Slope Analysis", MARGIN, 416 * PT, 404 * PT)
caption(s, "Mars HRSC MOLA BlendDEM Global 200mp", MARGIN + 422 * PT, 416 * PT,
        404 * PT)
note(s, "Slope, percent rise, built in 7 min 15 s. This run returned WARNING 000869 "
        "— elevation in metres against horizontal units in degrees — so it "
        "will be rebuilt on a projected DEM before any slope value is quoted.",
     452 * PT)

s = new(prs, "Gradient Products Against Their Source Imagery")
COL_W, PANEL_H = 400 * PT, 145 * PT
RIGHT = MARGIN + 430 * PT
for x, top_img, bot_img in ((MARGIN, "lv_grad_viking.png", "lv_viking.jpg"),
                            (RIGHT, "lv_grad_themis.png", "lv_themis.jpg")):
    picture_box(s, IMG, top_img, x, 136 * PT, COL_W, PANEL_H)
    picture_box(s, IMG, bot_img, x, 291 * PT, COL_W, PANEL_H)
caption(s, "Viking MDIM 2.1 — gradient over source", MARGIN, 446 * PT,
        COL_W, size=15)
caption(s, "THEMIS Day IR — gradient over source", RIGHT, 446 * PT,
        COL_W, size=15)
note(s, "Slope run on imagery returns DN gradient, not terrain slope — an edge "
        "and texture measure that picks out flow margins and crater rims. Note the "
        "straight lines across the Viking panel: they are mosaic seams, not "
        "landforms, which is exactly how this product can generate artifacts.",
     474 * PT)

# -- project schedule
s = new(prs, "Project Schedule")
table(s, ["Week", "Dates (2026)", "Activity", "Deliverable"],
      [list(r) for r in C.SCHEDULE],
      widths=[0.7, 1.6, 6.4, 2.3], size=10.5, row_h=26 * PT)
note(s, "Weeks 1–3 are complete. The critical path runs through weeks 4–8: "
        "one coordinate system unblocks the composite, and the composite unblocks "
        "everything after it.", 468 * PT)

# ======================================================== EXPECTED RESULTS ===
s = new(prs, "Hypotheses to be Tested")
labeled(s, S.HYPOTHESES_DECK, size=18, space=26)

# the four that are still genuinely open
s = new(prs, "Questions to be Answered")
bullets(s, [C.QUESTIONS[i] for i in (0, 1, 3, 5)], size=18, space=28)

# the five that would change the result, not merely constrain it; this slide
# owns the coordinate-frame and Composite Bands facts, so it states them in full
s = new(prs, "Potential Problems")
labeled(s, S.PROBLEMS_DECK, size=16, space=20)

# ================================================================== NOTES ====
# One line of delivery per slide: the point to make, and the number to quote.
NOTES = [
    "Mars Global Mosaic. Three global rasters are already on disk; the project is to "
    "fuse them into one co-registered stack and map three landform families from it.",

    "The mission in one sentence, then why it is not already solved. The three products, "
    "if you need to name them: Viking MDIM 2.1 colour at 232 m, THEMIS Day IR at 100 m, "
    "and the HRSC/MOLA blended DEM at 200 m — all downloaded and loaded, all better "
    "than 250 m per pixel. They exist; they are just distributed separately and in three "
    "different coordinate frames. Building the co-registered stack is the actual work.",

    "Ten tasks, ordered by dependency rather than by effort. Tasks 1 and 2 are complete. "
    "Task 3 — one coordinate frame, one meridian — is the gate: task 5 has been "
    "attempted three times without it and has never finished. On task 5, if asked why "
    "elevation is not in the composite: Iso Cluster measures distance in raw band "
    "values, so a band running −8,528 to +21,226 m would swamp four running 1–255.",

    "Open by naming the contribution: the three source products are individually "
    "standard, and stacking them into one analysis raster in a common projection is the "
    "new thing — it lets a unit be described by morphology, thermal response and slope "
    "at once. Then lead with Athabasca Valles: mapped as a fluvial outflow channel for "
    "decades before being reinterpreted as flood lava. That is exactly the "
    "discrimination problem morphology plus thermal response is for. Close on "
    "testability — nothing here needs privileged data.",

    "Four bands of real measurement and one active instrument. If asked about "
    "atmospheric correction: ~6 mbar of CO₂, effectively transparent across the "
    "visible and near-infrared, and the THEMIS window stops short of the 15 µm "
    "CO₂ band — the atmosphere is designed around, not ignored.",

    "Both areas on one sheet, and the figure labels itself — read the box, do not "
    "read the labels aloud. The box is the map’s own saved extent, not a region picked "
    "for the slide: Ius Chasma and its Louros Valles tributaries, 271–286°E, 6–13°S. "
    "Jezero, at 77.6°E 18.4°N, is a context map carrying hosted Perseverance services "
    "only — no imagery of it is held locally, which is why nothing else in the talk "
    "comes from there.",

    "All three downloaded, statistics built, 44 GB on disk. Pyramids are not built on "
    "any of them. The three panels are the same ground, which is the whole argument for "
    "fusing them: one landform, read three ways at once.",

    "THEMIS Night IR is the one that matters — same source and format as the day "
    "mosaic, so it is a download rather than a redesign. A global CTX mosaic is "
    "multi-terabyte and is out of scope on purpose, not by omission.",

    "Four real bands — three visible plus one thermal — and elevation kept "
    "separate. Iso Cluster measures distance in raw band values, so a band running "
    "−8,528 to +21,226 m would swamp four running 1–255.",

    "Ten pixels across a feature is the working rule. At 100 m that means features of "
    "about a kilometre and up. 8-bit depth is the real constraint on how finely units "
    "separate, and temporal resolution matters diurnally, not as change detection. "
    "Two out-of-scope answers to have ready: mineral identification would need CRISM, "
    "which ArcGIS Pro cannot process as hyperspectral cubes; and true thermal inertia "
    "needs calibrated radiance, so the day–night difference is a proxy and will be "
    "described as one.",

    "Seven minutes fifteen seconds on the 200 m DEM. It returned WARNING 000869 "
    "— elevation in metres against horizontal units in degrees — so it is "
    "display-only until it is rebuilt on the projected DEM. Do not quote a slope value "
    "off this run.",

    "Slope run on imagery is a DN gradient, not terrain slope. It is a legitimate edge "
    "and texture measure, and the straight lines in the Viking panel are mosaic seams "
    "— proof that it manufactures edges as well as finding them.",

    "Weeks 1 to 3 are complete. Weeks 4 to 8 are the critical path: one coordinate "
    "frame unblocks the composite, and the composite unblocks everything after it. "
    "Week 14 falls on Thanksgiving, so the layouts get front-loaded into week 13.",

    "Four hypotheses, each with a stated measurement rather than a hope. H1 is the core "
    "claim, and the mechanism behind it is the one from the significance slide: thermal "
    "response depends on particle size and surface coherence, while visible albedo is "
    "dominated by the dust veneer. H4 is the self-check: the 141 IAU-named craters above "
    "100 km are a built-in test set for the gradient method before it is trusted on "
    "unnamed craters.",

    "These are genuinely open, not rhetorical. The first two decide whether the "
    "schedule holds.",

    "Five problems that would change the result rather than merely constrain it. The "
    "three-frame mismatch is the root cause of most of the rest. The honest limit: the "
    "finest imagery held is 100 m, so nothing below about a kilometre can be confirmed.",
]

for slide, text in zip(prs.slides, NOTES):
    slide.notes_slide.notes_text_frame.text = text

prs.save(OUT)
print("wrote", OUT, "-", len(prs.slides._sldIdLst), "slides,",
      len(NOTES), "notes")
