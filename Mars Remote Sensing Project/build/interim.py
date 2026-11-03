# -*- coding: utf-8 -*-
"""The interim's content, as of STATUS_DATE: the living deck's single source (KB §39.3).

content.py still holds the September text that the delivered prospectus and Presentation 1
were built from; it is history and stays as it is. This module is the interim's current state,
and it is EXPECTED to change as the data moves (stated 2026-10-08: the interim "is dynamic
and will likely change largely as we gather and process the task data"). No fixed slide count.

Rules for editing it:
  * every number is quoted from PROJECT-KNOWLEDGE.md; the § is kept beside it so it can be
    rechecked, and a number changes here only after it changes there (KB §12.1);
  * a new result = one entry in FIGURES (a layout or a figure, 2-4 takeaways, its §);
  * the percentages in PROGRESS were set on 2026-10-26 (KB §69.5); None prints as a dash.
Style is the Presentation 1 design (le_theme.py), on request, 2026-10-08.
Slide text is written in a neutral, impersonal voice, edited for plain wording on 2026-10-26 (KB §69.6).
The § references stay in this file for checking and are not printed: the deck and report carry no KB
sections, decision codes, file names or build notes (2026-10-27, KB §69.9).
"""
from content import DECK_TITLE, COURSE, AUTHOR, TITLE        # unchanged since the prospectus

STATUS_DATE = "27 October 2026 (results to 26 October)"   # results cut 26 Oct (D20); status lines to 27 Oct (§69.21)

MISSION = (
    "Assemble one co-registered visible and thermal-infrared mosaic of Mars in ArcGIS Pro, over "
    "the ±60° band the THEMIS night mosaic covers (86.6% of the surface), and use it to map "
    "lava flows, fluvial channels and impact craters.")                                    # §16

GOALS = [
    "Put Viking visible colour, THEMIS day and night infrared and HRSC/MOLA topography on one "
    "grid over ±60°.",
    "Map the three landform families from that stack, first in a type area (Ius Chasma), "
    "then across ±60°.",
    "Test whether thermal infrared separates surfaces that visible light cannot.",
    "Score every product against something it never saw: held-out hand labels, the IAU crater "
    "gazetteer and the USGS geologic map.",
]

# ------------------------------------------------------------------ spectral bands
BANDS = [   # (band or product, wavelength, cell, what it contributes)
    ("Viking MDIM 2.1 R, G, B", "visible, ~0.4–0.7 µm", "232 m",
     "Colour and shading: bright dust, dark basalt. High-pass filtered at ~50 km; the colour, an uncalibrated "
     "blend, still carries regional differences."),  # §28.10 §43.1 §69.50
    ("THEMIS Day IR (v12)", "thermal IR, 12.57 µm", "100 m",
     "Daytime temperature. Ground that is bright in visible stays cooler by day (r −0.49 at Ius)."),  # §18.3
    ("THEMIS Night IR (v14, ±60°)", "thermal IR, 12.57 µm", "100 m",
     "Night temperature: rock holds heat. The band least like the others, |r| ≤ 0.12."),  # §18.3
    ("HRSC/MOLA blended DEM", "altimetry + stereo", "200 m",
     "Slope in degrees, local relief, hillshade, flow routing, closed-depression depth."),  # §20
    ("Diurnal contrast index", "day − night, relative", "100 m",
     "Separates materials inside one area; not thermal inertia, not comparable across the planet."),  # §24 §28.10
]

CORRELATION = {   # Ius type area, 100.00% co-valid, §18.3
    "bands": ["Viking R", "Viking G", "Viking B", "Day IR", "Night IR"],
    "r": [[1.000, 0.960, 0.925, -0.486, -0.121],
          [0.960, 1.000, 0.993, -0.496, -0.085],
          [0.925, 0.993, 1.000, -0.488, -0.068],
          [-0.486, -0.496, -0.488, 1.000, 0.105],
          [-0.121, -0.085, -0.068, 0.105, 1.000]],
    "takeaway": "The three Viking bands behave as one (r 0.93–0.99); day IR adds a second dimension and "
                "night IR a third. That is the measured case for fusing them.",
}

# ------------------------------------------------------------------ progress
# Percentages: toward the final deliverable, not the interim; set by the agent at the author's request,
# 2026-10-26 (D16, KB §69.5). 100 = nothing left for the final; a reduced scope that is settled counts as done.
PROGRESS = [   # (task, what is true now, percentage or None)                   KB
    ("Scope, targets and type area", "Two type areas, Ius Chasma and Athabasca Valles; the ±60° extent", 100),  # §14.3 §16 §42.1
    ("Raster acquisition", "Three global mosaics plus the THEMIS night IR mosaic", 100),               # §15
    ("Statistics, stretches, pyramids", "Done for every product; pyramids on the four source globals took 26 min", 100),  # §28 §29 §53
    ("Grouped mosaic viewer", "Done", 100),
    ("DEM terrain derivatives", "Slope rebuilt in degrees for the type area and ±60°", 100),  # §20 §28.8
    ("Image-gradient products", "Slope run on imagery, not the DEM; relabelled as gradient and not used", 100),                          # §7
    ("Jezero context", "Hosted services only; the dead HiRISE link removed", 100),                     # §3 §50
    ("Classification", "±60° SVM on hand-drawn labels, 200 m: 73.8%, κ 0.58 held out; 971 seven-class labels applied, maps running", 80),   # §55.3 §57 §69.8 §69.21
    ("CRS harmonisation", "Done: one 100 m / 200 m grid over ±60°", 100),                    # §18 §28.1
    ("Visible + IR composite", "Done: type area; 7-band ±60° stack", 100),                   # §18 §31.2
    ("Landform digitising", "Review begun at Ius: 94 channels and 26 crater rims accepted; Athabasca and lava margins to do", 20),  # §46 §69.7 §69.21
    ("Crater inventory", "Robbins catalogue in the project (385,049); 465,354 closed depressions ≥ 1 km at ±60°", 60),  # §41 §54.4
    ("Map layouts", "17 map layouts (none in September)", 85),          # §38 §44 §49 §53.6 §63 §66.4 §66.9
    ("Report and presentations", "Prospectus and Presentation 1 delivered; interim built to the 26 Oct cut; final paper and deck drafted", 60),  # §45 §69 §69.5
]
PROGRESS_SEPT = [90, 100, 70, 100, 80, 70, 20, 20, 15, 5, 0, 0, 0, 25]   # the 13 Sep deck, for comparison

# ------------------------------------------------------------------ processing log
LOG = [   # (date, what, outcome, §)
    ("18 Sep", "Night IR acquired; type-area stack; slope on a metric grid",     # 14 rows overflow: 18 Sep in one
     "Four inputs on one 100 m grid, 100% co-valid; slope in degrees", "§15–20"),
    ("19 Sep", "±60° grids and diurnal contrast index", "15.2 bn px in 36.3 min", "§28"),
    ("19 Sep", "Channel and crater candidates, Ius; basins at ±60°",      # merged: 14 rows overflow
     "2,610 channels; 1,685 closed depressions; 5,144 basins ≥ 20 km", "§25–28"),
    ("24–30 Sep", "Global composites built in ArcGIS Pro", "Two runs finished: 2 h 52 m and 3 h 10 m", "§29"),
    ("29 Sep", "Hand-drawn training polygons; SVMs", "Four classes; two ±60° maps", "§29"),
    ("2–3 Oct", "First SVM maps checked; corrected stack scored held out",   # merged: 14 rows overflow
     "Tile artefact, mostly elevation; then 73.5%, κ 0.58", "§30–32"),
    ("6–7 Oct", "Backup to GitHub; class codes", "Public repository; pixel = class code", "§35–36"),
    ("8 Oct", "Reference data, Athabasca, tests T1–T3 and T8", "Thermal adds +1.3 points; ten layouts", "§38–44"),
    ("8–9 Oct", "Digitising by review; tests T4–T7; validation sheet",          # 14 rows overflow the slide
     "No support for H1–H3 or a tributary count; 12 layouts", "§46–51"),
    ("13–15 Oct", "Pyramids; ±60° craters and channels ≥ 1 km; 180° DEM fix",
     "465,354 closed depressions, 969,822 channel segments", "§53–54"),
    ("14–16 Oct", "200 m classification; T1 with Pro's SVM; the published map",
     "73.8%, κ 0.58; thermal adds +1.36 and +1.97 points", "§55–57"),
    ("19–21 Oct", "Deep learning: a box detector, then a U-Net over ±60°",
     "U-Net 98.9%, κ 0.98 held out, as terrain provinces", "§66"),
    ("22–27 Oct", "The 512 labels audited; seven classes proposed and reviewed",
     "Five Crater labels are volcanoes; 971 seven-class labels applied", "§68–69.8"),
]

# ------------------------------------------------------------------ headline numbers (the results divider)
# Four numbers the results slides then explain, each already on its own slide below (2026-10-27, KB §69.11).
HEADLINES = [   # (number, what it measures)
    ("86.6%", "of the planet inside the ±60° analysis extent"),                        # §16
    ("73.8%", "held-out accuracy of the published landform map, κ 0.58"),              # §57
    ("+1.36", "points of overall accuracy the thermal bands add, Pro's SVM at 200 m; none by balanced accuracy"),  # §56 §69.18
    ("465,354", "closed depressions ≥ 1 km mapped across ±60°"),                       # §54.4
]

# ------------------------------------------------------------------ figures (preliminary results)
# images: ("layout", <layout name in the .aprx>) or ("file", <path under build\>)
# group: the kicker printed above the slide's title (2026-10-27, KB §69.11).
# verdict: a hypothesis slide's answer, on the kicker's line; each is a bullet on its slide or the issue card
# "Four hypotheses tested, none supported", shortened (2026-10-27, KB §69.14).
# Order (2026-10-26): data, thermal signal, craters and channels, type areas, classification (the two failed
# maps first, then the published one), deep learning, then the hypotheses in order H1, H2, H3, Q5.
FIGURES = [
    dict(group="The data", title="The analysis extent and the two type areas",
         images=[("layout", "10_global60_locator")],
         points=["The analysis covers ±60° latitude, 86.6% of the planet: the THEMIS night mosaic's coverage",
                 "Two type areas: Ius Chasma (canyon and tributaries) and Athabasca Valles (flood lava)",
                 "Orange: the USGS geologic map's volcanic units, used as the lava-flow reference"],
         source="§16, §41, §42, §43"),
    dict(group="The data", title="The mosaic at ±60°",
         images=[("layout", "08_global60_mosaic")], map_h=328,  # two takeaways: the four panels taller
         points=["All four datasets on one 200 m grid",
                 "Composite Bands failed four times on the global rasters; projecting first and bounding the "
                 "extent fixed it"],
         source="§16, §18, §28.1, §38"),
    dict(group="The data", title="Ius Chasma type area: visible and night IR",
         images=[("layout", "01_visible"), ("layout", "02_night_ir")],
         points=["Left, Viking visible colour; right, THEMIS night IR. 271–286°E, 6–13°S: canyon walls, "
                 "plateau, Louros Valles",
                 "Same 100 m grid, every pixel valid in all five bands",
                 "Night IR barely correlates with any other band (|r| ≤ 0.12), so it adds information the others lack"],
         source="§14.3, §18"),
    dict(group="Thermal signal", title="Can the thermal pair map material across ±60°?",
         images=[("file", r"pres1_img\global60_thermal.png")],
         points=["Viking red separates the dusty provinces from the rocky ones by 47.67 DN",
                 "THEMIS day and night IR separate them by −0.19 and +0.02 DN; the index, over seven provinces, by −0.0009",
                 "Every province repeats the whole mosaic's mean and spread, because both THEMIS mosaics were "
                 "stretched region by region",
                 "Across the planet, the material signal is in Viking colour"],
         source="§28.10"),
    dict(group="Thermal signal", title="Checked against calibrated thermal inertia (TES)",
         images=[("file", r"interim_img\tes_check.png")],
         points=["Viking colour follows calibrated thermal inertia across the planet (r −0.36)",
                 "Night IR and the diurnal-contrast index follow it weakly, and only inside regions (|r| ≈ 0.1)",
                 "Day IR does not follow it, and across the planet neither THEMIS mosaic does",
                 "At TES's ~3 km cells the material signal is in Viking colour; thermal IR adds little"],
         source="§41, §42.4, §43.1"),
    dict(group="Craters", title="Craters at ±60°: closed depressions ≥ 20 km",
         images=[("layout", "07_global60_basins")], map_h=230,  # a lower map leaves the tall legend room
         points=["5,144 basins found by fill depth in 48 s",
                 "68% of 117 IAU craters ≥ 100 km recovered, diameter within ±50%",
                 "Median diameter error +2.2%",
                 "Breached craters are missed by design: they do not close"],
         source="§28.11"),
    dict(group="Craters", title="Closed depressions ≥ 1 km across ±60°",
         images=[("layout", "11_global60_depressions")], map_left=True, points_h=214,  # two maps stacked
         points=["465,354 closed depressions ≥ 1 km, from an 11-hour run",
                 "Against Robbins: 15.3% are catalogued craters at ≥ 1 km, 62.2% at ≥ 5 km, 83.1% at ≥ 20 km",
                 "Their density per 10⁴ km² barely follows the catalogued craters (r −0.11); below ~5 km it follows the DEM's sharpness",
                 "Good for large craters and as prompts for review; for crater counts, Robbins is the reference"],
         source="§53.4, §53.6, §54.4, §55.4"),
    dict(group="Channels", title="Channels across ±60°",
         images=[("layout", "12_global60_channels")], map_h=262,  # a lower map: the legend room to be read
         points=["969,822 routed channel segments; orders 3–5 drawn",
                 "60.5% of stream cells discarded as fill artefact (Ius alone: 56%)",
                 "89.8% lie on ground under 2°, so the plateau channels are DEM noise",
                 "No channel reference exists at ±60°, so the network is not scored"],
         source="§53.4, §53.6, §54.4, §55.4"),
    dict(group="Type areas", title="Ius Chasma: candidates to digitise",
         images=[("layout", "06_ius_digitising")],
         points=["Fill raised the canyon floor by up to 2,077 m; 56% of the first channel network was artefact",
                 "188 channel candidates are steep and rock-floored; reviewed first, 94 accepted",
                 "Only 11% of the 1,685 closed depressions ≥ 1 km match a Robbins crater, so they are prompts "
                 "for review"],
         source="§25, §26, §42.3"),
    dict(group="Type areas", title="Athabasca Valles: the second type area",
         images=[("layout", "09_athabasca_digitising")], legend_beside=True,  # map left, legend in the room beside it
         points=["Flood lava once mapped as a water channel; the USGS map calls it Late Amazonian volcanic (lAv)",
                 "Built the same way as Ius: 3,283 channel candidates, 409 of them rock-floored",
                 "Catalogued craters: 1,122 per million km² on lAv, against 1,760 and 2,183 on the older units",
                 "The diurnal-contrast index does not track calibrated TES inertia here (r ≈ 0); Viking colour does (−0.55)"],
         source="§41, §42"),
    dict(group="Classification", title="Checking the first two classifications",
         images=[("layout", "05_svm_checks")], map_left=True,         # two maps stacked: map left, legend right
         points=["The 29 Sep map follows its 4096-px processing tiles instead of the terrain",
                 "The 30 Sep map is mostly elevation: elevation alone reproduces 62% of it",
                 "Both problems led to the corrected stack, with no elevation band and slope in degrees"],
         source="§30"),
    dict(group="Classification", title="Landforms at ±60°, scored on labels the model never saw",
         images=[("layout", "04_global60_landforms")],
         points=["512 hand-drawn polygons in whole 15° blocks: 329 train the SVM, 183 are held out",
                 "Published map, 200 m, 11 × 11 majority (2.2 km): 73.8%, κ 0.58 held out; one class everywhere: 58.6%",
                 "Halving the cell bought no accuracy: 69.9% raw at 200 m, 70.5% at 400 m",
                 "Normal Ground and cratered terrain hold up; lava tube does not (2% user's accuracy)"],
         source="§31.3, §55.3, §57"),
    dict(group="Classification", title="The landform classes against the USGS geologic map",
         images=[("file", r"interim_img\t8_enrichment.png")],          # layout 13 is the Pro sheet; its table, legible
         points=["Each cell: how much more often a class occurs in a unit group than across ±60° (×1 = no link)",
                 "\"Lava tube\" gathers on volcano flanks and aprons (×3.30, ×4.29), not on volcanic plains (×0.84)",
                 "76% of the volcanic plains come out Normal Ground",
                 "The classes follow terrain, so lava flows are taken from the geologic map"],
         source="§43.2, §49, §57.1"),
    dict(group="Classification", title="Does thermal infrared improve the classification?",
         images=[("file", r"interim_img\thermal_ablation.png")],
         points=["Slope and relief alone: 68.6%, κ 0.51 held out; all seven bands: 67.0%, κ 0.50",
                 "The thermal bands add +1.3 points of overall accuracy (95% interval +0.6 to +2.2), small but clear of zero",
                 "Without terrain, visible and thermal score below one class everywhere (58.6%)",
                 "The labels are landforms, so terrain decides them; testing thermal IR properly needs material labels"],
         source="§40"),
    dict(group="Classification", title="The thermal gain, checked with ArcGIS Pro's own SVM",
         images=[("file", r"interim_img\t1_pro.png")],
         points=["Pro's SVM retrained over all of ±60° with the published settings, leaving out one band group at a time",
                 "Thermal adds +1.36 points of overall accuracy at 200 m (+0.46 to +2.47) and +1.97 at 400 m (+1.08 to +3.35)",
                 "It helps craters and hills and hurts lava tube, so with every class weighted equally (balanced accuracy) "
                 "the gain disappears: −0.31 points at 200 m, +0.07 at 400 m",
                 "Leaving out visible, or both groups, ties the score; terrain alone ties it too but gets only 34 of 124 "
                 "crater polygons right"],
         source="§56, §56.1, §69.18"),
    dict(group="Deep learning", title="Deep learning, 1: a detector that draws boxes",
         images=[("layout", "16_x5_detections")], map_left=True,      # frame A over B: map left, legend right
         points=["RetinaNet on the 7-band stack, trained on the training blocks only, scored on the 183 held-out polygons",
                 "Crater: 41.9% of polygons found, 87.6% of boxes right, against 71.1% for always naming Crater",
                 "Normal Ground: 22.7% found, 56.9% right; hills and lava tube never named",
                 "Retrained with the backbone unfrozen for 30 epochs, it names hills but finds only 4.5% of "
                 "Normal Ground, so it is no better"],
         source="§66.1, §66.2, §66.5"),
    dict(group="Deep learning", title="Deep learning, 2: a U-Net maps terrain provinces",
         images=[("layout", "17_x5c_unet_provinces")], map_left=True, points_h=204,  # 4 long points: the legend lower
         points=["A U-Net pixel classifier on the same stack and labels, over all of ±60°; a second pass, offset "
                 "128 px, removes its tile seams",
                 "Held out: 98.9%, κ 0.980, against the published SVM map's 73.8%, κ 0.583, under the same scorer",
                 "Lava tube becomes usable: 77.1% user's accuracy, against 2.4% for the SVM",
                 "It maps provinces rather than single landforms: its 'Crater' covers 82.6% of the ring around named "
                 "craters. The SVM map stays the published one"],
         source="§66.6–66.9"),
    dict(group="Hypotheses", title="Do the infrared mosaics show lava-flow edges Viking misses? (H1)",
         images=[("file", r"interim_img\t5_margins.png")], verdict="Not supported at the map's 1:20 M scale",
         points=["905 profiles across 10 of the geologic map's lava contacts at Athabasca: does each band tell the units apart?",
                 "Every band does only slightly better than chance (10%): Viking red 12.3%, day IR 21.0%",
                 "Day IR leans toward H1, but the intervals overlap (difference +8.7 points, −1.7 to +18.1)",
                 "Contacts on a 1:20 M map are kilometres wide; H1 is retested on margins digitised at 100 m"],
         source="§47.2"),
    dict(group="Hypotheses", title="Do volcanic channels differ from fluvial ones? (H2)",
         images=[("file", r"interim_img\t4_channels.png")], verdict="Not supported at stage 1",
         points=["Channel candidates, Ius Chasma (fluvial) against Athabasca Valles (volcanic): 2,588 and 3,272",
                 "H2 expected the volcanic channels to be steeper; they are shallower (median 1.4 against 10.2 m per km)",
                 "Thermal response tells the two apart no better than chance (AUC 0.50)",
                 "Not supported at stage 1: the window sets the gradient, not the origin. Reviewed channels retest it"],
         source="§51.1"),
    dict(group="Hypotheses", title="Is the composite more stable than a single band? (H3)",
         images=[("file", r"interim_img\t6_stability.png")], verdict="Not supported",
         points=["Iso Cluster trained on the west and the east half of Ius, compared over the whole window",
                 "The composites are the least reproducible inputs: 0.40 and 0.38, against 0.61–0.89 for single bands",
                 "They give the smoothest maps, only just ahead of Viking (0.85 against 0.84)",
                 "H3 is not supported"],
         source="§47.3"),
    dict(group="Hypotheses", title="How many tributary orders does 100 m resolve? (Q5)",
         images=[("file", r"interim_img\t7_orders.png")], verdict="The DEM cannot answer it",
         points=["Channel thresholds from 1 to 500 km² of catchment at Ius Chasma",
                 "The highest stream order follows the threshold: 5 at 1 km², 3 at 50 km², 2 at 500 km²",
                 "Only 30.8–36.7% of first-order streams lie on slopes ≥ 2°, at every threshold",
                 "The order count reflects the threshold chosen, so the DEM cannot answer Q5"],
         source="§47.4"),
]

# ------------------------------------------------------------------ the size of a 15° block
# The held-out split's 15° blocks against the US state nearest each in area (interim_block_scale.py, KB §69.15),
# requested by the author 2026-10-27. A slide of its own, drawn from shapes rather than a picture, so it stays out of
# FIGURES (the report and the figure scripts read those); the deck puts it just before the slide named in `before`,
# where the blocks are first used. One block per band of latitude, the same in the south.
BLOCK_SLIDE = dict(
    group="For scale", title="How big is a 15° block? About the size of Texas",
    before="Landforms at ±60°, scored on labels the model never saw",
    note="Above each block, its two rows on the ±60° grid of 192 blocks; blocks and squares below drawn to one "
         "scale, equator side down. Every block is 889 km north to south; east to west it narrows from 889 km at the "
         "equator to 445 km at 60°. The hand-drawn labels fall in 39 blocks, 14 held out. State areas: 2010 US "
         "Census, land and water.",
    source="§31.3, §69.15")
BLOCK_SCALE = [   # (band, km², sq mi, E-W side at the band's low and high edge in km, state, ratio)   §69.15
    ("0–15° N and S", "782,000 km²", "302,000 sq mi", 889.1, 858.8, "Texas", "1.12"),
    ("15–30° N and S", "728,000 km²", "281,000 sq mi", 858.8, 770.0, "Texas", "1.05"),
    ("30–45° N and S", "625,000 km²", "241,000 sq mi", 770.0, 628.7, "Texas", "0.90"),
    ("45–60° N and S", "480,000 km²", "185,000 sq mi", 628.7, 444.6, "California", "1.13"),
]
BLOCK_NS_KM = 889.1                                       # every block's north-south side
STATE_AREA = {"Texas": (695662, "695,662 km²"), "California": (423967, "423,967 km²")}   # 2010 census, total

# ------------------------------------------------------------------ issues
ISSUES = [   # led by the measured limits (decision D12, 2026-10-08)
    ("The thermal signal is weak where it can be checked",
     "The THEMIS mosaics follow calibrated TES thermal inertia only weakly inside 15° blocks (|r| ≈ 0.1) and "
     "not at all across the planet; Viking colour follows it (r −0.31 to −0.36). In the classification the "
     "thermal bands add 1.3–2.0 points of overall accuracy, with two classifiers, but none by balanced accuracy."),   # §40.1 §42.4 §43.1 §56 §69.18
    ("The landform classes are terrain classes",
     "Slope and relief alone score as well as all seven bands. On the geologic map the classes sit where terrain "
     "puts them, and \"lava tube\" lands on volcano flanks rather than lava plains."),   # §40.1 §43.2
    ("Five \"Crater\" labels are volcanoes",
     "One label, on Arsia Mons, is 31% of the held-out Crater area; the seven-class labels make them volcanic edifices."),   # §68.2 §69.8
    ("Lava flows come from the geologic map",
     "These bands cannot tell volcanic plains from other plains, and a fifth \"volcanic\" class scored below "
     "chance. Lava flows are taken from the USGS map's volcanic units."),   # §43.3 §44
    ("Closed depressions are not a crater count",
     "Of the candidates ≥ 1 km, 11–13% in the type areas and 15.3% across ±60° are catalogued craters; "
     "from 5 km up most are (62.2%). The Robbins catalogue (385,049 craters) is the crater reference."),   # §42.3 §54.4
    ("Four hypotheses tested, none supported",
     "No band separates the geologic map's lava contacts much better than chance, though the map is too coarse to "
     "settle H1; the volcanic channels are shallower, and thermal response separates nothing (H2, stage 1); the "
     "composite's classes are the least reproducible input (H3); no channel threshold keeps first-order streams "
     "on real slopes (Q5)."),   # §47 §51
    ("The review has only begun",
     "549 of 9,287 candidates reviewed, all at Ius (precision 54% on steep channels, 7% on depressions); H1 and H2 wait."),   # §69.7 §69.21
    ("428.7 GB on one USB drive",
     "Reads cap near 112 MB/s, and the drive has dropped off mid-write, so big outputs are built on internal disk first."),   # §2.2 §36.4 §67.4
    ("Solved since September",
     "Three coordinate frames, the z-factor defect, four failed global composites, the missing night mosaic, "
     "a defective DEM column at 180°."),   # §15–20 §54
]

NEXT_STEPS = [   # all for the final: the interim's data cut is 26 Oct (D20)
    "Continue the review: the rest of Ius Chasma, then Athabasca Valles; draw breached craters and lava margins",
    "Score the candidates against the reviewed features on the validation sheet; retest H1 on digitised margins and H2 on "
    "reviewed channels with their origin set",
    "Seven classes: the 971 reviewed labels are applied and the SVM and U-Net are rerunning; score both maps "
    "on the same held-out blocks",
    "Deep learning: set aside validation blocks before any further tuning, so the held-out blocks stay a clean test",  # §66.5
]

SCHEDULE = [   # (when, what)
    ("8–26 Oct", "Pyramids, ±60° crater and channel pass, 200 m map, T1 in Pro, the deep-learning detector and U-Net; seven classes proposed"),
    ("26 Oct", "Interim data cut; later results go to the final report"),
    ("27 Oct – 22 Nov", "Review and digitising (begun 26 Oct); the seven-class maps; H1 and H2 on digitised features; data freeze"),
    ("10 Nov", "Interim presentation"),   # the date from the author, 2026-10-27 (D16)
    ("23 Nov – 4 Dec", "Final report and presentation"),
    ("8 Dec", "Final due"),
]

# ------------------------------------------------------------------ speaker notes
# One note per slide of the deck, keyed by the slide's title ("title", "results", "issues: limits" and
# "issues: work" for the slides without one of their own); build_interim_live.py fails if a slide has none or a
# note is left unused (NEXT-STEPS §12.5, 2026-11-01). The notes stay at the 26 October cut, like the slides; only
# the last answers the likely question of what has changed since. Numbers checked by verify_interim.py as above.
NOTES = {
    "title":
        "The Mars Global Mosaic: one co-registered visible and thermal-infrared mosaic over ±60°, and what it can "
        "and cannot map. Results are to the 26 October data cut, status lines to 27 October. The background is Ius "
        "Chasma in Viking colour on the project's 100 m grid.",   # §16 §69.5 §69.21
    "Project Goals":
        "The question in one line: can a co-registered visible and thermal-infrared mosaic map lava flows, fluvial "
        "channels and impact craters across ±60°? Four goals follow: one grid for four datasets; the three families, "
        "first in a type area, then across ±60°; a test of whether thermal IR separates what visible light cannot; "
        "and a score for every product against something it never saw. The last goal shapes the talk: every number "
        "shown is a held-out or reference score, not agreement with the training data.",
    "Relevant Spectral Bands":
        "Five layers. Viking MDIM 2.1 gives visible colour at 232 m, not calibrated albedo; THEMIS day and night IR at 100 m give day "
        "and night temperature as display brightness; the HRSC/MOLA DEM at 200 m gives slope, relief and flow routing. "
        "The diurnal-contrast index is day minus night, each first stretched to its own range: it separates "
        "materials inside one area and is not thermal inertia. If asked why not thermal inertia: both THEMIS "
        "mosaics are 8-bit display products, stretched independently, with no scaling to temperature, so calibrated "
        "inertia cannot be derived from them; it comes only from TES, at about 3 km.",   # §20 §24.1 §24.2 §41
    "Why Fuse Them: Three Independent Dimensions":
        "The case for fusion, measured at Ius Chasma with every pixel valid in all five bands. The three Viking "
        "bands repeat each other (r 0.93 to 0.99): visible colour is one dimension. Day IR runs against visible at "
        "about −0.49, because bright ground stays cooler by day. Night IR correlates with nothing above 0.12, a third "
        "dimension. Independence is needed for fusion to help but does not prove it helps: the classification "
        "slides measure how much it adds.",   # §18.3
    "Project Tasks and Percent Complete":
        "Percent complete toward the final, not the interim. Light blue: done by the 13 September deck; blue: added "
        "since. The data, the grids, the composite and the coordinate work are complete. The open rows are landform "
        "digitising at 20%, the crater inventory at 60% and classification at 80%; what remains in them is mostly "
        "the review of machine candidates, which runs to the 22 November data freeze.",   # §69.5
    "Processing Completed Since the Last Report":
        "Each step since the last report, with its measured outcome. Three to point at: the ±60° crater and channel "
        "pass in mid-October, 465,354 closed depressions and 969,822 channel segments; the 200 m published map, "
        "73.8%, κ 0.58 held out; and the deep-learning runs from 19 October. The last row, the audit of the 512 "
        "labels, found five Crater labels drawn on volcanoes; that led to the seven-class scheme.",   # §54.4 §57 §66 §68
    "results":
        "Four headline numbers, each explained on its own slide: the ±60° extent is 86.6% of the planet; the "
        "published landform map scores 73.8% on held-out labels; the thermal bands add 1.36 points of overall "
        "accuracy and none by balanced accuracy; and 465,354 closed depressions of 1 km and more. Every map that "
        "follows is a layout in the ArcGIS Pro project, exported for this deck. The background is the same canyon "
        "in THEMIS night IR.",   # §16 §54.4 §56 §57 §69.18
    "The analysis extent and the two type areas":
        "The extent is set by the THEMIS night mosaic, which stops at 60° north and south: 86.6% of the surface, "
        "so the work is ±60°, never global. Two type areas: Ius Chasma, a canyon with tributary valleys, for "
        "channels and craters; Athabasca Valles, a young flood-lava channel, for lava flows. Orange marks the "
        "volcanic units of the USGS geologic map, SIM 3292, the lava-flow reference throughout.",   # §16 §42 §44
    "The mosaic at ±60°":
        "Four panels on one 200 m grid: Viking visible, THEMIS day IR, THEMIS night IR and topography. The hurdle "
        "was the Composite Bands tool, which failed four times on the global rasters; projecting each input first "
        "and bounding the extent to ±60° fixed it. The source files also came in different coordinate frames, a "
        "misregistration that stays silent unless each file is checked.",   # §15–20 §28.1 §38
    "Ius Chasma type area: visible and night IR":
        "The type area at full resolution, 271 to 286°E and 6 to 13°S: canyon walls, plateau and the Louros Valles "
        "tributaries. Left, Viking colour; right, THEMIS night IR on the same 100 m grid. Night IR is brightest "
        "where the ground holds heat, and it barely correlates with any other band (|r| ≤ 0.12), so it carries "
        "information the others lack. The next two slides ask whether that information is material.",   # §14.3 §18
    "Can the thermal pair map material across ±60°?":
        "A province test: seven provinces with a textbook contrast in thermal inertia, dusty ones such as Arabia "
        "Terra and Amazonis against rocky ones such as Syrtis Major and Acidalia. Viking red separates dusty from "
        "rocky by 47.67 DN; day and night IR by −0.19 and +0.02 DN, effectively nothing. The cause is processing, "
        "not physics: both THEMIS mosaics were stretched region by region, so every province repeats the whole "
        "mosaic's mean and spread. Across the planet the material signal is in Viking colour.",   # §28.10
    "Checked against calibrated thermal inertia (TES)":
        "The check against an independent measure, calibrated TES thermal inertia at about 3 km. Viking colour "
        "follows it across the planet, r −0.36. Night IR and the diurnal-contrast index follow it weakly and only "
        "inside regions, |r| near 0.1; day IR not at all. This is the project's main measured limit, and it is why "
        "the thermal layer is called a relative diurnal-contrast index and never thermal inertia.",   # §42.4 §43.1
    "Craters at ±60°: closed depressions ≥ 20 km":
        "The first crater product: depressions found by how deep they fill, run over ±60° in 48 seconds, 5,144 "
        "basins of 20 km and more. Of 117 IAU-named craters of 100 km and more, 68% are recovered with a diameter "
        "within ±50%, and the median diameter error is +2.2%. A breached crater, its rim cut by a channel, does not "
        "close, so it is missed by design: the method's main limit.",   # §28.11
    "Closed depressions ≥ 1 km across ±60°":
        "The same method from 1 km up, an 11-hour run: 465,354 closed depressions. Against the Robbins catalogue, "
        "15.3% are catalogued craters at 1 km and more, 62.2% at 5 km and 83.1% at 20 km. Below about 5 km their "
        "density follows the DEM's sharpness rather than the craters, so the small ones are mostly DEM texture. "
        "They are prompts for review; for crater counts the Robbins catalogue, 385,049 craters, is the reference.",   # §41 §53.4 §54.4 §55.4
    "Channels across ±60°":
        "Flow routing on the DEM over ±60°: 969,822 channel segments, orders 3 to 5 drawn. Filling closed basins "
        "before routing makes false channels, so 60.5% of stream cells were discarded as fill artefact (56% at Ius "
        "alone). 89.8% of the segments lie on ground under 2°: the plateau channels are DEM noise. No channel "
        "reference exists at ±60°, so the network is a candidate layer, not scored.",   # §53.6 §54.4 §55.4
    "Ius Chasma: candidates to digitise":
        "Filling raised the canyon floor by up to 2,077 m, which is why 56% of the first channel network was "
        "artefact. 188 channel candidates are steep and rock-floored; they were reviewed first and 94 accepted. "
        "Only 11% of the 1,685 closed depressions match a Robbins crater, so they too are prompts. Accepted "
        "candidates are copied into the digitising classes; nothing enters them without a review.",   # §25 §26 §42.3 §46 §69.7
    "Athabasca Valles: the second type area":
        "Athabasca Valles was once read as a water-carved channel; the USGS map calls it Late Amazonian volcanic, "
        "lAv. Built the same way as Ius: 3,283 channel candidates, 409 of them rock-floored. Catalogued craters "
        "number 1,122 per million km² on lAv against 1,760 and 2,183 on the older units, so the lava is the "
        "youngest of the three surfaces (test T2). Here the diurnal-contrast index does not track TES inertia (r about 0); "
        "Viking colour does (−0.55).",   # §41 §42
    "Checking the first two classifications":
        "Two SVM maps made in the Pro interface on 29 and 30 September, checked before anything was built on them. "
        "The 29 September map follows its 4096-pixel processing tiles rather than the terrain. The 30 September "
        "map is mostly elevation: elevation alone reproduces 62% of it. Both led to the corrected stack, with no "
        "elevation band and slope in degrees.",   # §30
    "How big is a 15° block? About the size of Texas":
        "The unit of the test that follows. The hand-drawn labels were split by whole 15° blocks, not by polygon, "
        "so no held-out polygon shares a block with a training polygon: the score measures the map on ground it "
        "has not seen nearby. A block is 889 km north to south, about Texas near the equator and California from "
        "45° to 60°. The labels fall in 39 blocks; 14 are held out.",   # §31.3 §69.15
    "Landforms at ±60°, scored on labels the model never saw":
        "The published map. 512 hand-drawn polygons in four classes, split by whole blocks: 329 train the SVM and "
        "183 are held out. At 200 m with an 11 × 11 majority filter, 2.2 km, it scores 73.8%, κ 0.58 on the "
        "held-out polygons, where naming one class everywhere scores 58.6%. Halving the cell bought no accuracy. "
        "Normal Ground and cratered terrain hold up; lava tube does not, at 2% user's accuracy.",   # §31.3 §55.3 §57
    "The landform classes against the USGS geologic map":
        "Each cell is an enrichment: how much more often a class occurs on a unit group than across ±60°, where ×1 "
        "means no link. Lava tube gathers on volcano flanks and aprons, ×3.30 and ×4.29, not on volcanic plains, "
        "×0.84, and 76% of the volcanic plains come out Normal Ground. The classes follow terrain rather than "
        "material, so the lava flows come from the geologic map, not the classifier.",   # §43.2 §57.1
    "Does thermal infrared improve the classification?":
        "Test T1: the same classifier trained with and without each band group, scored held out. Slope and relief "
        "alone reach 68.6%, κ 0.51; all seven bands 67.0%, κ 0.50. The thermal bands add 1.3 points of overall "
        "accuracy, 95% interval +0.6 to +2.2: small but clear of zero. Without terrain, visible and thermal score "
        "below naming one class everywhere. The labels are landforms, so terrain decides them; a fair test of "
        "thermal value would need material labels.",   # §40 §40.1
    "The thermal gain, checked with ArcGIS Pro's own SVM":
        "The same question asked of ArcGIS Pro's own SVM, retrained over all of ±60° with one band group left out "
        "at a time. Thermal adds 1.36 points at 200 m (+0.46 to +2.47) and 1.97 at 400 m. It helps craters and "
        "hills and hurts lava tube, so with every class weighted equally, balanced accuracy, the gain disappears: "
        "−0.31 points at 200 m, +0.07 at 400 m. In short: a small gain in overall accuracy, none by balanced "
        "accuracy.",   # §56 §56.1 §69.18
    "Deep learning, 1: a detector that draws boxes":
        "A RetinaNet box detector on the 7-band stack, trained on the training blocks only and scored on the same "
        "183 held-out polygons. Crater: 41.9% of polygons found and 87.6% of boxes right, but always naming Crater "
        "would be right 71.1% of the time. Hills and lava tube are never named, and retraining with the backbone "
        "unfrozen names hills but loses Normal Ground. Boxes do not suit classes that cover areas.",   # §66.1 §66.2 §66.5
    "Deep learning, 2: a U-Net maps terrain provinces":
        "A U-Net labels every pixel, run over all of ±60° in two passes offset by 128 pixels to remove its tile "
        "seams. Held out: 98.9%, κ 0.980, against the SVM map's 73.8% under the same scorer; lava tube becomes "
        "usable at 77.1% user's accuracy. Why it is not the headline: it maps terrain provinces, not single "
        "landforms. Its Crater class covers 82.6% of the ring around named craters, so it is right about regions "
        "rather than about each crater. The SVM map stays the published one.",   # §66.6–66.9
    "Do the infrared mosaics show lava-flow edges Viking misses? (H1)":
        "H1: 905 profiles across 10 of the geologic map's lava contacts at Athabasca, asking whether each band "
        "tells the two sides apart. Chance is 10%; Viking red scores 12.3% and day IR 21.0%. Day IR leans toward "
        "H1, but the difference, +8.7 points, has an interval from −1.7 to +18.1 that includes zero. Contacts on a "
        "1:20 M map are kilometres wide, so H1 is retested on margins digitised at 100 m.",   # §47.2
    "Do volcanic channels differ from fluvial ones? (H2)":
        "H2, stage 1, with the window standing in for origin: the Ius candidates as fluvial, 2,588, against the "
        "Athabasca ones as volcanic, 3,272. H2 expected the volcanic channels to be steeper; they are shallower, a "
        "median 1.4 against 10.2 m per km. Thermal response separates them no better than chance, AUC 0.50. The "
        "window sets the gradient, not the origin, so stage 2 waits for channels reviewed with their origin set.",   # §51.1
    "Is the composite more stable than a single band? (H3)":
        "H3: Iso Cluster trained on the west half of Ius and on the east half, the two maps compared over the "
        "whole window. The composites are the least reproducible inputs, 0.40 and 0.38, against 0.61 to 0.89 for "
        "single bands. They give the smoothest maps, just ahead of Viking, 0.85 against 0.84. Not supported.",   # §47.3
    "How many tributary orders does 100 m resolve? (Q5)":
        "Q5: channel thresholds from 1 to 500 km² of catchment at Ius. The highest order follows the threshold: 5 "
        "at 1 km², 3 at 50 km², 2 at 500 km². At every threshold only 30.8% to 36.7% of first-order streams lie on "
        "slopes of 2° or more. The count reflects the threshold chosen, so the DEM cannot answer Q5.",   # §47.4
    "issues: limits":
        "The six limits the measurements set. The thermal signal is weak wherever it can be checked against TES. "
        "The landform classes are terrain classes. Five Crater labels are volcanoes, and one, on Arsia Mons, is 31% "
        "of the held-out Crater area. Lava flows come from the geologic map. Closed depressions are prompts, not a "
        "crater count. Four hypotheses were tested and none is supported. Each is a result: it says what this "
        "stack can and cannot map.",   # §40.1 §43 §47 §51 §54.4 §68.2
    "issues: work":
        "Three practical hurdles. The review had only begun at the cut: 549 of 9,287 candidates, all at Ius, with "
        "precision 54% on the steep channels and 7% on the depressions; H1 and H2 wait for it. The project is "
        "428.7 GB on one USB drive that reads near 112 MB/s and has dropped off mid-write, so big outputs are "
        "built on internal disk first. And what was solved since September: three coordinate frames, the z-factor "
        "defect, four failed global composites, the missing night mosaic and a defective DEM column at 180°.",   # §2.2 §36.4 §54 §69.7
    "Next Steps":
        "Four steps for the final, due 8 December after a data freeze on 22 November: finish the review at both "
        "type areas and draw breached craters and lava margins by hand; score the candidates against the reviewed "
        "features and retest H1 and H2 on them; score the seven-class SVM and U-Net on the same held-out blocks; "
        "and set aside validation blocks before any further deep-learning tuning. If asked what has changed since "
        "the cut: both seven-class maps are scored on the 237 held-out seven-class polygons, the SVM at 42.5%, "
        "κ 0.310 and the U-Net at 69.0%, κ 0.606, and they lead the final; the review reached 3,791 of 9,287 "
        "candidates by 31 October (read the current tally before the talk).",   # §66.5 §69.24–69.26 §69.33
}
