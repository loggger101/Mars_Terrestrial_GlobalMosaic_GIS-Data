# -*- coding: utf-8 -*-
"""Presentation 1, second revision -- every template bullet, and the evidence.

What changed against build_pres1_le.py:

  * the three slides that were titled after a global raster and carried nothing
    now carry that raster, whole, read out of the project's own TIFF with a
    graticule and -- for the DEM -- a real elevation scale
  * four diagnostic figures were added, each one turning a claim the deck was
    making in prose into something the audience can see: the central-meridian
    mismatch, what WARNING 000869 does to a slope layer, the global relief and
    8-bit DN distributions, and a visible-against-thermal preview of H1
  * the slope slide's caption was a lone full stop; it says what the run was
  * a closing slide, so the talk ends on the blocker rather than on a list of
    problems

Slide order still follows '1 Project Statement.pdf'. Notes are attached per
slide as it is built rather than from a positional list at the foot, so
inserting a slide can no longer shift every note after it onto the wrong one.

    python build_pres1_v2.py <img_dir> <out.pptx>
"""

import os
import sys

import content as C
import deck_short as S
from le_theme import (deck, new, title_slide, bullets, labeled, table,
                      caption, note, picture, picture_box, png_size, textbox,
                      style, no_bullet, PT, W, MARGIN, CONTENT_W, BODY_Y, PALE)

IMG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "le_img")
OUT = sys.argv[2] if len(sys.argv) > 2 else "Presentation 1 v2.pptx"
prs = deck()


def sn(s, text):
    """Speaker notes for the slide just built."""
    s.notes_slide.notes_text_frame.text = text
    return s


BAND_TOP, BAND_H = BODY_Y, 358 * PT       # the space a figure may occupy


def figure(s, name, cap=None, max_h=BAND_H):
    """Fill the content width, cap the height, centre what is left over.

    Wide figures were being placed at a fixed height and left a dead band at
    the foot of the slide; sizing from the width and centring the remainder
    puts that space back into the picture or splits it evenly.
    """
    pw, ph = png_size(os.path.join(IMG, name))
    w, h = CONTENT_W, int(CONTENT_W * ph / float(pw))
    if h > max_h:
        h, w = max_h, int(max_h * pw / float(ph))
    top = BAND_TOP + (max_h - h) // 2
    picture(s, IMG, name, (W - w) // 2, top, w, h)
    if cap:
        note(s, cap, top + h + 12 * PT)
    return h


# ================================================================== TITLE ====
sn(title_slide(prs, C.DECK_TITLE, (C.COURSE, C.AUTHOR)),
   "Mars Global Mosaic. Three global rasters are already on disk; the project "
   "is to fuse them into one co-registered stack and map three landform "
   "families from it.")

# =========================================================== INTRODUCTION ====
s = new(prs, "Background — Goals and Mission")
tf = textbox(s, MARGIN, BODY_Y, CONTENT_W, 70 * PT)
p = tf.paragraphs[0]
no_bullet(p)
style(p.add_run(), 19).text = C.MISSION
bullets(s, S.BACKGROUND_DECK, size=18, top=228 * PT, height=270 * PT, space=24)
sn(s, "The mission in one sentence, then why it is not already solved. The "
      "three products, if you need to name them: Viking MDIM 2.1 colour at "
      "232 m, THEMIS Day IR at 100 m, and the HRSC/MOLA blended DEM at 200 m "
      "— all downloaded and loaded, all better than 250 m per pixel. They "
      "exist; they are just distributed separately and in three different "
      "coordinate frames. Building the co-registered stack is the actual work.")

s = new(prs, "Tasks Required to Meet the Mission")
table(s, ["#", "Task", "What it involves"],
      [[i, t, d] for i, (t, d) in enumerate(S.TASKS_DECK, 1)],
      widths=[0.4, 3.0, 6.6], size=11.5, row_h=30 * PT)
sn(s, "Ten tasks, ordered by dependency rather than by effort. Tasks 1 and 2 "
      "are complete. Task 3 — one coordinate frame, one meridian — is "
      "the gate: task 5 has been attempted three times without it and has "
      "never finished. On task 5, if asked why elevation is not in the "
      "composite: Iso Cluster measures distance in raw band values, so a band "
      "running −8,528 to +21,226 m would swamp four running 1–255.")

s = new(prs, "Significance of the Mission")
bullets(s, S.SIGNIFICANCE_DECK, size=19, space=26)
sn(s, "Open by naming the contribution: the three source products are "
      "individually standard, and stacking them into one analysis raster in a "
      "common projection is the new thing — it lets a unit be described by "
      "morphology, thermal response and slope at once. Then lead with "
      "Athabasca Valles: mapped as a fluvial outflow channel for decades "
      "before being reinterpreted as flood lava. That is exactly the "
      "discrimination problem morphology plus thermal response is for. Close "
      "on testability — nothing here needs privileged data.")

# ================================================================= METHODS ===
s = new(prs, "Which Part of the Electromagnetic Spectrum")
picture(s, IMG, "em_spectrum.png", MARGIN, 136 * PT, 830 * PT, 308 * PT)
note(s, "Visible gives morphology and the ferric absorption edge; thermal IR "
        "gives composition through the Si–O reststrahlen bands and, paired "
        "with a night mosaic, thermal inertia; altimetry gives slope and "
        "drainage context. Radar is excluded — it probes the subsurface, "
        "not surface landforms.", 452 * PT)
sn(s, "Four bands of real measurement and one active instrument. If asked "
      "about atmospheric correction: ~6 mbar of CO₂, effectively "
      "transparent across the visible and near-infrared, and the THEMIS window "
      "stops short of the 15 µm CO₂ band — the atmosphere is "
      "designed around, not ignored.")

s = new(prs, "Mapping Extent")
figure(s, "g_extent.jpg",
       "All 360° of longitude, 60°N to 60°S — 86.6% of the "
       "surface. Every product here is plate carrée, where the east-west "
       "scale error is 1/cos(lat): 1.15× at 30°, 2.00× at "
       "60°, 5.76× at 80° and unbounded at the pole. Cutting at "
       "60° caps the distortion at a factor of two.")
sn(s, "State the extent plainly: the whole mosaic between 60 north and 60 "
      "south, all the way round. The poles are excluded on purpose, and the "
      "reason is the projection rather than the data — these are all plate "
      "carrée products, so east-west scale error is one over cosine "
      "latitude. Two times at 60 degrees, nearly six at 80. Cutting there still "
      "leaves 86.6% of the surface. If asked about the close-ups later in the "
      "deck: those are there to show what 100 m and 232 m data resolve on the "
      "ground, not to narrow the area being mapped.")

# -- potential data sources: acquired ---------------------------------------
s = new(prs, "Data Sources — Acquired", dark=True)
specs = [("lz_dem.jpg", "HRSC_MOLA_BlendDEM_200m",
          "Elevation · 200 m/px · 106,694 × 53,347"),
         ("lz_themis.jpg", "MO_THEMIS-IR-Day_100m",
          "Thermal IR · 100 m/px · 213,390 × 106,696"),
         ("lz_viking.jpg", "Viking_MDIM21_232m",
          "Visible colour · 232 m/px · 92,160 × 46,080 "
          "· 3 bands")]
for i, (img, cap, spec) in enumerate(specs):
    x = MARGIN + i * 284 * PT
    picture_box(s, IMG, img, x, 140 * PT, 262 * PT, 232 * PT, keep="centre")
    caption(s, cap, x, 382 * PT, 262 * PT, dark=True, size=16)
    tf = textbox(s, x, 406 * PT, 262 * PT, 40 * PT)
    p = tf.paragraphs[0]
    no_bullet(p)
    style(p.add_run(), 11, color=PALE).text = spec
note(s, "All three global, public, and already loaded — 44 GB on disk, "
        "22.8 billion pixels in the thermal layer alone. The three panels are a "
        "close-up on one 4° × 3.5° window over Louros Valles, "
        "to show the same landform read three ways at once.", 470 * PT,
     dark=True)
sn(s, "All three downloaded, statistics built, 44 GB on disk. Pyramids are not "
      "built on any of them. The three panels are the same ground, which is "
      "the whole argument for fusing them: one landform, read three ways at "
      "once.")

# -- each source raster, whole ----------------------------------------------
s = new(prs, "Viking MDIM 2.1 — the Visible Base")
figure(s, "g_viking.jpg",
       "232 m/px, 92,160 × 46,080, three bands. Decimated from the "
       "project’s own GeoTIFF — the whole 12.7 GB file read and "
       "averaged, because no pyramids exist to read instead.")
sn(s, "This is the colour mosaic, whole. It is the visible reference the rest "
      "of the talk compares against: bright ferric dust, darker basaltic "
      "surfaces, and the Tharsis rise running away to the west. Worth "
      "saying out loud that this is not a screenshot — it is the file on "
      "the drive, read end to end and averaged down, which is also why it took "
      "a minute to make.")

s = new(prs, "THEMIS Day IR — the 100 m Thermal Base")
figure(s, "g_themis.jpg",
       "100 m/px, 213,390 × 106,696 — 22.77 billion pixels, of which "
       "22.14 billion are valid (97.3% coverage). Rolled from central meridian "
       "180° onto 0° so it registers against the other two.")
sn(s, "The finest global layer held, and the one the project is really built "
      "on. Two numbers worth quoting: 22.77 billion pixels, 97.3% of them "
      "valid. And note what had to happen to put it on this page at all "
      "— it ships on central meridian 180°, so the array is rolled "
      "half its width before it will line up with the other two. That is the "
      "coordinate problem, in one operation.")

s = new(prs, "HRSC/MOLA Blended DEM — the Vertical Reference")
figure(s, "g_dem.jpg",
       "200 m/px, 106,694 × 53,347, 16-bit. Measured relief −8,528 m "
       "to +21,226 m — 29,754 m from the Hellas floor to the Olympus Mons "
       "summit, and the only layer in the project carrying a physical unit.")
sn(s, "Elevation is where every quantitative measurement in this project comes "
      "from, because it is the only layer with a real physical unit on it "
      "— the other two are 8-bit brightness. Relief of 29,754 m, and the "
      "extremes land exactly where they should, at Hellas and Olympus Mons, "
      "which is the first confirmation that the DEM is correctly "
      "georeferenced. It stays out of the band composite: Iso Cluster measures "
      "distance in raw values, so a band running to 21,226 would swamp four "
      "running 1 to 255.")

# -- potential data sources: still required ---------------------------------
s = new(prs, "Data Sources — Still Required")
table(s, ["Dataset", "Resolution", "Why it is needed"],
      [list(r) for r in S.DATA_NEEDED_DECK],
      widths=[2.6, 1.3, 7.1], size=14, row_h=62 * PT)
sn(s, "THEMIS Night IR is the one that matters — same source and format as "
      "the day mosaic, so it is a download rather than a redesign. A global "
      "CTX mosaic is multi-terabyte and is out of scope on purpose, not by "
      "omission.")

s = new(prs, "Which Spectral Bands, and Why")
table(s, ["Band or product", "Wavelength", "Why this band"],
      [list(r) for r in S.BANDS_DECK],
      widths=[2.4, 1.7, 7.0], size=14, row_h=50 * PT)
note(s, "Four real bands — three visible, one thermal — plus elevation "
        "as a separate analysis layer. The derived products — slope, "
        "hillshade and the two DN gradients — have their own slides later "
        "in the methods section.", 392 * PT)
sn(s, "Four real bands — three visible plus one thermal — and "
      "elevation kept separate. Iso Cluster measures distance in raw band "
      "values, so a band running −8,528 to +21,226 m would swamp four "
      "running 1–255.")

s = new(prs, "Resolution Required")
items = []
for kind, lines in S.RESOLUTION_DECK:
    items.append((0, kind))
    for ln in lines:
        items.append((1, ln))
bullets(s, items, size=15.5, space=12)
sn(s, "Ten pixels across a feature is the working rule. At 100 m that means "
      "features of about a kilometre and up. 8-bit depth is the real "
      "constraint on how finely units separate, and temporal resolution "
      "matters diurnally, not as change detection. Two out-of-scope answers to "
      "have ready: mineral identification would need CRISM, which ArcGIS Pro "
      "cannot process as hyperspectral cubes; and true thermal inertia needs "
      "calibrated radiance, so the day–night difference is a proxy and "
      "will be described as one.")

s = new(prs, "Radiometric Resolution, Measured")
figure(s, "f_hypsometry.jpg",
       "Left and centre: every valid DEM pixel inside the mapped band. Right: "
       "the 8-bit DN distributions over one close-up window — both mosaics use "
       "a few tens of levels where a unit boundary has to live, which is the "
       "argument for not over-interpreting a single-DN difference.")
sn(s, "This is the resolution slide with numbers on it. The DEM histogram is "
      "bimodal because Mars is — that is the crustal dichotomy, northern "
      "lowlands against southern highlands, and it falls straight out of the "
      "data without being looked for. The right-hand panel is the honest "
      "limit: 8-bit sources, most of the surface packed into a narrow DN "
      "range, so classification boundaries are coarse by construction.")

# -- work already done with these data ---------------------------------------
s = new(prs, "Derived Product — Slope from Elevation")
picture(s, IMG, "s3_img1.png", MARGIN, 132 * PT, 404 * PT, 276 * PT)
picture(s, IMG, "s3_img2.png", MARGIN + 422 * PT, 132 * PT, 404 * PT, 276 * PT)
caption(s, "Slope, percent rise", MARGIN, 416 * PT, 404 * PT)
caption(s, "HRSC/MOLA blended DEM, 200 m", MARGIN + 422 * PT, 416 * PT, 404 * PT)
note(s, "Slope, percent rise, built in 7 min 15 s on the 200 m DEM. The run "
        "returned WARNING 000869 — elevation in metres against horizontal "
        "units in degrees — so it will be rebuilt on a projected DEM "
        "before any slope value is quoted. The next slide shows what that "
        "warning costs.", 452 * PT)
sn(s, "Seven minutes fifteen seconds on the 200 m DEM. It returned WARNING "
      "000869 — elevation in metres against horizontal units in degrees "
      "— so it is display-only until it is rebuilt on the projected DEM. "
      "Do not quote a slope value off this run. Hand straight on to the next "
      "slide, which measures the damage.")

s = new(prs, "What WARNING 000869 Actually Costs")
figure(s, "f_zfactor.jpg",
       "Same DEM window, same tool, one difference: horizontal units. On a "
       "degree grid with the default z-factor of 1 the slope is 89.7° on "
       "average and saturated almost everywhere; in metres it runs 0–52.3"
       "° with a mean of 5.9°. The warning is not cosmetic — the "
       "layer carries no usable information until it is rebuilt.")
sn(s, "This is the slide that justifies task 4 on the task list. A degree of "
      "longitude is about 59,000 times a metre, so with the default z-factor "
      "of 1 every gradient is multiplied by that and the arctangent pins to "
      "90°. Mean slope 89.7° against a real 5.9°. The point to "
      "land: this is not a scale error you can divide out afterwards — "
      "the layer is saturated, so the information is gone and the run has to "
      "be repeated on a projected DEM.")

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
note(s, "Slope run on imagery returns DN gradient, not terrain slope — an "
        "edge and texture measure that picks out flow margins and crater rims. "
        "Note the straight lines across the Viking panel: they are mosaic "
        "seams, not landforms, which is exactly how this product can generate "
        "artifacts.", 474 * PT)
sn(s, "Slope run on imagery is a DN gradient, not terrain slope. It is a "
      "legitimate edge and texture measure, and the straight lines in the "
      "Viking panel are mosaic seams — proof that it manufactures edges as "
      "well as finding them.")

s = new(prs, "Why Everything Waits on One Coordinate Frame")
figure(s, "f_meridian.jpg",
       "The same window number for number, read three ways. THEMIS ships on "
       "central meridian 180° while Viking and the DEM ship on 0°, so "
       "a stack built without checking the meridian lands half a planet from "
       "the ground it claims — and misregisters silently rather than "
       "failing.")
sn(s, "This is the single most important slide in the talk. The middle panel "
      "is Terra Sabaea, 91 to 106°E; the outer two are Ius Chasma, 271 to "
      "286°E. Same numbers requested, same tool, and nothing errors. That "
      "is the whole danger: no warning, no failure, just the wrong ground. It "
      "is why task 3 is the gate, and it is the most likely reason Composite "
      "Bands has never completed.")

s = new(prs, "Project Schedule")
table(s, ["Week", "Dates (2026)", "Activity", "Deliverable"],
      [list(r) for r in C.SCHEDULE],
      widths=[0.7, 1.6, 6.4, 2.3], size=10.5, row_h=26 * PT)
note(s, "Weeks 1–3 are complete. The critical path runs through weeks "
        "4–8: one coordinate system unblocks the composite, and the "
        "composite unblocks everything after it.", 468 * PT)
sn(s, "Weeks 1 to 3 are complete. Weeks 4 to 8 are the critical path: one "
      "coordinate frame unblocks the composite, and the composite unblocks "
      "everything after it. Week 14 falls on Thanksgiving, so the layouts get "
      "front-loaded into week 13.")

# ======================================================== EXPECTED RESULTS ===
s = new(prs, "Hypotheses to be Tested")
labeled(s, S.HYPOTHESES_DECK, size=18, space=26)
sn(s, "Four hypotheses, each with a stated measurement rather than a hope. H1 "
      "is the core claim, and the mechanism behind it is the one from the "
      "significance slide: thermal response depends on particle size and "
      "surface coherence, while visible albedo is dominated by the dust "
      "veneer. H4 is the self-check: the 141 IAU-named craters above 100 km "
      "are a built-in test set for the gradient method before it is trusted on "
      "unnamed craters.")

s = new(prs, "H1, Previewed — Daedalia Planum")
figure(s, "f_daedalia.jpg",
       "16° × 11° over the Daedalia Planum flow field, same "
       "window in both. The visible mosaic is flattened by the dust veneer; "
       "the thermal layer separates individual flow lobes and their margins. "
       "This is the effect H1 proposes to measure — not yet the "
       "measurement.")
sn(s, "Be careful to frame this as a preview, not a result: it is the "
      "qualitative effect H1 predicts, over a flow field nobody would call "
      "ambiguous. The measurement H1 actually requires is mapped flow area "
      "from the IR layer against the visible layer over the same extent, and "
      "that needs the classification step, which needs the composite, which "
      "needs the coordinate frame.")

s = new(prs, "Questions to be Answered")
bullets(s, [C.QUESTIONS[i] for i in (0, 1, 3, 5)], size=18, space=28)
sn(s, "These are genuinely open, not rhetorical. The first two decide whether "
      "the schedule holds.")

s = new(prs, "Potential Problems")
labeled(s, S.PROBLEMS_DECK, size=16, space=20)
sn(s, "Five problems that would change the result rather than merely "
      "constrain it. The three-frame mismatch is the root cause of most of the "
      "rest. The honest limit: the finest imagery held is 100 m, so nothing "
      "below about a kilometre can be confirmed.")

# ================================================================= CLOSE =====
s = new(prs, "Where This Stands", dark=True)
bullets(s, [
    "Three global rasters on disk, characterized from the files themselves "
    "— 43.7 GB, 100–232 m/px, one of them 22.8 billion pixels.",
    "The mapped extent is settled: all 360° of longitude between "
    "60°N and 60°S, which is 86.6% of the surface and caps "
    "plate-carrée scale error at a factor of two.",
    "The blocker is named and measured: three coordinate frames on two central "
    "meridians, which is why the band composite has never completed and why "
    "the terrain derivatives are display-only.",
    "Next: project everything into one frame, rebuild slope and hillshade, "
    "then run Composite Bands over a bounded extent rather than the globe.",
    "The whole plan is testable without privileged data — the USGS global "
    "geologic map and the IAU gazetteer are the references, and the 100 m "
    "floor is stated as a limit rather than worked around.",
], size=18, space=24, dark=True)
sn(s, "Close on the blocker, not on the data. The honest summary is that the "
      "acquisition and characterization are done, the fusion is not, and the "
      "reason is a coordinate-frame problem that is now identified and "
      "measurable rather than mysterious.")

prs.save(OUT)
print("wrote %s — %d slides" % (OUT, len(prs.slides._sldIdLst)))
