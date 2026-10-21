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
  * the percentages in PROGRESS are the author's to set; None prints as a dash.
Style is the Presentation 1 design (le_theme.py), on request, 2026-10-08.
Slide text is written in a neutral, impersonal voice.
"""
from content import DECK_TITLE, COURSE, AUTHOR, TITLE        # unchanged since the prospectus

STATUS_DATE = "21 October 2026"

MISSION = (
    "Assemble one co-registered visible and thermal-infrared mosaic of Mars in ArcGIS Pro, over "
    "the ±60° band the THEMIS night mosaic covers (86.6% of the surface), and use it to map "
    "lava flows, fluvial channels and impact craters.")                                    # §16

GOALS = [
    "One co-registered stack: Viking visible colour, THEMIS day and night infrared, HRSC/MOLA "
    "topography, on a single grid over ±60°.",
    "Map and classify the three landform families from it, in a type area first (Ius Chasma) "
    "and then across ±60°.",
    "Test whether thermal infrared separates surfaces that visible light cannot.",
    "Score every product against something it never saw: held-out hand labels, the IAU crater "
    "gazetteer, and the USGS geologic map.",
]

# ------------------------------------------------------------------ spectral bands
BANDS = [   # (band or product, wavelength, cell, what it contributes)
    ("Viking MDIM 2.1 R, G, B", "visible, ~0.4–0.7 µm", "232 m",
     "Albedo: bright dust against dark basalt. Keeps real regional differences (§28.10)."),
    ("THEMIS Day IR (v12)", "thermal IR, 6.8–14.9 µm", "100 m",
     "Daytime temperature: bright in visible = cool by day (r −0.49 at Ius, §18.3)."),
    ("THEMIS Night IR (v14, ±60°)", "thermal IR, 6.8–14.9 µm", "100 m",
     "Night temperature: rock holds heat. The most independent band, |r| ≤ 0.12 (§18.3)."),
    ("HRSC/MOLA blended DEM", "altimetry + stereo", "200 m",
     "Slope in degrees, local relief, hillshade, flow routing, closed-depression depth (§20)."),
    ("Diurnal contrast index", "day − night, relative", "100 m",
     "A local material discriminator inside one area; not thermal inertia, not planet-wide (§24, §28.10)."),
]

CORRELATION = {   # Ius type area, 100.00% co-valid, §18.3
    "bands": ["Viking R", "Viking G", "Viking B", "Day IR", "Night IR"],
    "r": [[1.000, 0.960, 0.925, -0.486, -0.121],
          [0.960, 1.000, 0.993, -0.496, -0.085],
          [0.925, 0.993, 1.000, -0.488, -0.068],
          [-0.486, -0.496, -0.488, 1.000, 0.105],
          [-0.121, -0.085, -0.068, 0.105, 1.000]],
    "takeaway": "Three visible bands are one dimension (r 0.93–0.99); day IR adds a second, "
                "night IR a third. Effective dimensionality ≈ 3: the measured case for fusing them.",
}

# ------------------------------------------------------------------ progress
PROGRESS = [   # (task, what is true now, percentage or None)                   KB
    ("Scope, targets and type area", "Ius Chasma and Athabasca Valles type areas; ±60° extent decided", None),  # §14.3 §16 §42.1
    ("Raster acquisition", "Three globals + THEMIS Night IR", None),                                     # §15
    ("Statistics, stretches, pyramids", "Done: all products overviewed, the four source globals in 26 min", None),  # §28 §29 §53
    ("Grouped mosaic viewer", "Done", None),
    ("DEM terrain derivatives", "Rebuilt in degrees, type area and ±60°; WARNING 000869 gone", None),  # §20 §28.8
    ("Image-gradient products", "Renamed Gradient_*; not used further", None),                          # §7
    ("Jezero context", "Hosted services only; the dead HiRISE link removed", None),                     # §3 §50
    ("Classification", "±60° SVM on hand-drawn labels, 200 m: 73.8%, κ 0.58 held out", None),   # §55.3 §57
    ("CRS harmonisation", "Done: one 100 m / 200 m grid over ±60°", None),                    # §18 §28.1
    ("Visible + IR composite", "Done: type area; 7-band ±60° stack", None),                   # §18 §31.2
    ("Landform digitising", "Classes ready and empty; candidates reviewable; validation sheet ready; 512 training polygons drawn", None),  # §19.4 §29.2 §46 §49
    ("Crater inventory", "Robbins catalogue in the project (385,049); 465,354 closed depressions ≥ 1 km at ±60°", None),  # §41 §54.4
    ("Map layouts", "17 layouts, from none, with graticules", None),                     # §38 §44 §49 §53.6 §63 §66.4 §66.9
    ("Report and presentations", "Interim deck and report are living builds from one source", None),  # §45
]
PROGRESS_SEPT = [90, 100, 70, 100, 80, 70, 20, 20, 15, 5, 0, 0, 0, 25]   # the 13 Sep deck, for comparison

# ------------------------------------------------------------------ processing log
LOG = [   # (date, what, outcome, §)
    ("18 Sep", "Night IR acquired; type-area stack; slope on a metric grid",     # 14 rows overflow: 18 Sep in one
     "Four inputs on one 100 m grid, 100% co-valid; slope in degrees", "§15–20"),
    ("19 Sep", "±60° grids and diurnal contrast index", "15.2 bn px in 36.3 min", "§28"),
    ("19 Sep", "Channel and crater candidates, Ius", "2,610 channels; 1,685 closed depressions in 49 s", "§25–26"),
    ("19 Sep", "Basins at ±60°", "5,144 ≥ 20 km in 48 s", "§28.11"),
    ("24–30 Sep", "Global composites in the Pro GUI (desktop)", "First successes: 2 h 52 m, 3 h 10 m", "§29"),
    ("29 Sep", "Hand-drawn training polygons; SVMs", "Four classes; two ±60° maps", "§29"),
    ("2–3 Oct", "First SVM maps checked; corrected stack scored held out",   # merged: 14 rows overflow
     "Tile artefact, mostly elevation; then 73.5%, κ 0.58", "§30–32"),
    ("6–7 Oct", "Backup to GitHub; class codes", "Public repository; pixel = class code", "§35–36"),
    ("8 Oct", "Reference data, Athabasca, tests T1–T3 and T8", "Thermal adds +1.3 points; ten layouts", "§38–44"),
    ("8–9 Oct", "Digitising by review; tests T4–T7; validation sheet",          # 14 rows overflow the slide
     "No support for H1–H3 or a tributary count; 12 layouts", "§46–51"),
    ("13–15 Oct", "Desktop: pyramids; ±60° craters and channels ≥ 1 km; 180° DEM fix",
     "465,354 closed depressions, 969,822 channel segments", "§53–54"),
    ("14–16 Oct", "200 m classification; T1 with Pro's SVM; the published map",
     "73.8%, κ 0.58; thermal adds +1.36 and +1.97 points", "§55–57"),
    ("19–21 Oct", "Deep learning: a box detector, then a U-Net over ±60°",
     "U-Net 98.9%, κ 0.98 held out: terrain provinces", "§66"),
]

# ------------------------------------------------------------------ figures (preliminary results)
# images: ("layout", <layout name in the .aprx>) or ("file", <path under build\>)
FIGURES = [
    dict(title="Where: the analysis extent and the two type areas",
         images=[("layout", "10_global60_locator")],
         points=["±60° latitude, 86.6% of the planet: the THEMIS night mosaic's coverage",
                 "Ius Chasma, canyon and tributaries; Athabasca Valles, flood lava",
                 "Orange: volcanic units of the USGS geologic map, the lava-flow reference"],
         source="§16, §41, §42, §43"),
    dict(title="The mosaic at ±60°",
         images=[("layout", "08_global60_mosaic")],
         points=["Four datasets on one 200 m grid for the first time",
                 "The failed global Composite Bands is solved: project first, then bound the extent",
                 "Night-IR coverage sets the extent: 86.6% of the planet"],
         source="§16, §18, §28.1, §38"),
    dict(title="Ius Chasma type area: visible and night IR",
         images=[("layout", "01_visible"), ("layout", "02_night_ir")],
         points=["271–286°E, 6–13°S: canyon walls, plateau, Louros Valles",
                 "Same 100 m grid, every pixel valid in all five bands",
                 "Night IR correlates |r| ≤ 0.12 with every other band: information no other layer holds"],
         source="§14.3, §18"),
    dict(title="Can the thermal pair map material across ±60°?",
         images=[("file", r"pres1_img\global60_thermal.png")],
         points=["Viking red separates the dusty provinces from the rocky ones by 47.67 DN",
                 "THEMIS day and night IR: −0.19 and +0.02 DN; the index over seven provinces: −0.0009",
                 "Each province repeats the mosaic-wide mean and spread: contrast-stretched region by region",
                 "Planet-wide, visible albedo carries the material signal"],
         source="§28.10"),
    dict(title="Checked against calibrated thermal inertia (TES)",
         images=[("file", r"interim_img\tes_check.png")],
         points=["Viking albedo tracks real thermal inertia across the planet (r −0.36)",
                 "Night IR and the diurnal-contrast index: a weak signal inside regions only (|r| ≈ 0.1)",
                 "Day IR carries none; across the planet the THEMIS pair says nothing",
                 "So the material signal is in visible albedo; thermal IR adds little at 3 km"],
         source="§41, §42.4, §43.1"),
    dict(title="Craters at ±60°: closed depressions ≥ 20 km",
         images=[("layout", "07_global60_basins")],
         points=["5,144 basins found by fill depth in 48 s",
                 "68% of 117 IAU craters ≥ 100 km recovered, diameter within ±50%",
                 "Diameter error median +2.2%",
                 "Misses breached craters by construction: they are not closed"],
         source="§28.11"),
    dict(title="Closed depressions ≥ 1 km across ±60°",
         images=[("layout", "11_global60_depressions")],
         points=["465,354 closed depressions ≥ 1 km, from an 11-hour run on the desktop",
                 "Against Robbins: 15.3% are catalogued craters at ≥ 1 km, 62.2% at ≥ 5 km, 83.1% at ≥ 20 km",
                 "Below ~5 km their density follows the DEM's sharpness, not the craters (r −0.11)",
                 "A map of large craters and a list of prompts, not a crater inventory"],
         source="§53.4, §53.6, §54.4, §55.4"),
    dict(title="Channels across ±60°",
         images=[("layout", "12_global60_channels")],
         points=["969,822 routed channel segments; orders 3–5 drawn",
                 "60.5% of stream cells discarded as fill artefact (Ius alone: 56%)",
                 "89.8% lie on ground under 2°: plateau channels are DEM noise",
                 "No channel reference exists at ±60°, so the network is not scored"],
         source="§53.4, §53.6, §54.4, §55.4"),
    dict(title="Ius Chasma: candidates to digitise",
         images=[("layout", "06_ius_digitising")],
         points=["Fill raised the canyon floor 2,077 m; 56% of the first channel network was artefact",
                 "188 channel candidates are steep and rock-floored: the place to start",
                 "1,685 closed depressions ≥ 1 km: only 11% match a catalogued (Robbins) crater, "
                 "so they are prompts, not a crater count"],
         source="§25, §26, §42.3"),
    dict(title="Athabasca Valles: the second type area",
         images=[("layout", "09_athabasca_digitising")],
         points=["Flood lava once mapped as a water channel; the USGS map calls it Late Amazonian volcanic (lAv)",
                 "Same 100 m stack, terrain and candidates as Ius: 3,283 channels, 409 rock-floored",
                 "Catalogued craters: 1,122 per million km² on lAv, against 1,760 and 2,183 on the older units",
                 "Calibrated TES inertia: the diurnal-contrast index does not track it (r ≈ 0); Viking albedo does (−0.55)"],
         source="§41, §42"),
    dict(title="Landforms at ±60°, scored on labels the model never saw",
         images=[("layout", "04_global60_landforms")],
         points=["SVM on 512 hand-drawn polygons, split by whole 15° blocks",
                 "200 m, smoothed 11 × 11 (2.2 km): 73.8%, κ 0.58 held out (one class everywhere: 58.6%)",
                 "Halving the cell bought no accuracy: 69.9% raw at 200 m, 70.5% at 400 m",
                 "Normal Ground and cratered terrain are solid; lava tube is not (2% user's)"],
         source="§31.3, §55.3, §57"),
    dict(title="The landform classes against the USGS geologic map",
         images=[("file", r"interim_img\t8_enrichment.png")],          # layout 13 is the Pro sheet; its table, legible
         points=["Each cell: how much more often a class occurs in a unit group than across ±60° (×1 = no link)",
                 "\"Lava tube\" is not enriched on volcanic plains (×0.84) but on volcano flanks and aprons (×3.30, ×4.29)",
                 "76% of the volcanic plains come out Normal Ground",
                 "A coherent terrain map, not a lava-flow map: lava flows come from the geologic map"],
         source="§43.2, §49, §57.1"),
    dict(title="Does thermal infrared improve the classification?",
         images=[("file", r"interim_img\thermal_ablation.png")],
         points=["Slope and relief alone: 68.6%, κ 0.51 held out; all seven bands: 67.0%, κ 0.50",
                 "The thermal bands add +1.3 points (95% interval +0.6 to +2.2): real, but small",
                 "Without terrain, visible and thermal score below one class everywhere (58.6%)",
                 "The labelled classes are landforms, so terrain decides them; the thermal claim needs material labels"],
         source="§40"),
    dict(title="The thermal gain, confirmed with ArcGIS Pro's own SVM",
         images=[("file", r"interim_img\t1_pro.png")],
         points=["Retrained with the published model's settings, without each band group, over the whole ±60°",
                 "Thermal adds +1.36 points at 200 m (+0.46 to +2.47) and +1.97 at 400 m (+1.08 to +3.35)",
                 "It helps craters and hills and hurts lava tube; dropping visible or both groups leaves the score tied",
                 "Terrain alone ties the score but makes a poor crater map: 34 of 124 crater polygons"],
         source="§56, §56.1"),
    dict(title="Deep learning, 1: a detector that draws boxes",
         images=[("layout", "16_x5_detections")], map_left=True,      # frame A over B: map left, legend right
         points=["RetinaNet on the 7-band stack, trained on the training blocks only, scored on the 183 held-out polygons",
                 "Crater: 41.9% of polygons found, 87.6% of boxes right, against 71.1% for always naming Crater",
                 "Normal Ground: 22.7% found, 56.9% right; hills and lava tube never named",
                 "Retrained with the backbone unfrozen for 30 epochs: hills named, but Normal Ground found "
                 "falls to 4.5%, so not improved"],
         source="§66.1, §66.2, §66.5"),
    dict(title="Deep learning, 2: a U-Net maps terrain provinces",
         images=[("layout", "17_x5c_unet_provinces")], map_left=True,
         points=["A pixel classifier on the same stack and labels, over all of ±60°; a second pass offset "
                 "128 px removes its tile seams",
                 "Held out: 98.9%, κ 0.980, against the published SVM map's 73.8%, κ 0.583, under the same scorer",
                 "Lava tube becomes usable: 77.1% user's accuracy against 2.4%",
                 "Provinces, not features: 'Crater' covers 82.6% of the ring round named craters; "
                 "the SVM map stays the published one"],
         source="§66.6–66.9"),
    dict(title="Do the infrared mosaics show lava-flow edges Viking misses? (H1)",
         images=[("file", r"interim_img\t5_margins.png")],
         points=["Profiles across the geologic map's lava contacts at Athabasca: does each band tell the units apart?",
                 "Every band does so only slightly more often than chance (10%): Viking red 12.3%, day IR 21.0%",
                 "Day IR leans toward H1, but the intervals overlap (difference +8.7 points, −1.7 to +18.1)",
                 "A 1:20 M map's contacts are kilometres wide: H1 is retested on margins digitised at 100 m"],
         source="§47.2"),
    dict(title="Is the composite more stable than a single band? (H3)",
         images=[("file", r"interim_img\t6_stability.png")],
         points=["Iso Cluster trained on the west and the east half of Ius, compared over the whole window",
                 "The composites are the least reproducible inputs: 0.40 and 0.38, against 0.61–0.89 for single bands",
                 "They give the smoothest maps, only just ahead of Viking (0.85 against 0.84)",
                 "H3 is not supported"],
         source="§47.3"),
    dict(title="How many tributary orders does 100 m resolve? (Q5)",
         images=[("file", r"interim_img\t7_orders.png")],
         points=["Channel thresholds from 1 to 500 km² of catchment at Ius Chasma",
                 "The highest stream order follows the threshold: 5 at 1 km², 3 at 50 km², 2 at 500 km²",
                 "Only 30.8–36.7% of first-order streams lie on slopes ≥ 2°, at every threshold",
                 "The order count is a setting, not a property of the terrain: no answer the DEM supports"],
         source="§47.4"),
    dict(title="Do volcanic channels differ from fluvial ones? (H2)",
         images=[("file", r"interim_img\t4_channels.png")],
         points=["Channel candidates, Ius Chasma (fluvial) against Athabasca Valles (volcanic): 2,588 and 3,272",
                 "The volcanic channels are shallower, not steeper: median 1.4 against 10.2 m per km",
                 "Thermal response tells the two apart no better than chance (AUC 0.50)",
                 "H2 is not supported at this stage; the window, not the origin, sets the gradient; retested on reviewed channels"],
         source="§51.1"),
    dict(title="Checking the first two classifications",
         images=[("layout", "05_svm_checks")],
         points=["29 Sep map follows its 4096-px processing tiles, not the terrain",
                 "30 Sep map is mostly elevation: elevation alone reproduces 62% of it",
                 "Both led to the corrected stack: no elevation band, slope in degrees"],
         source="§30"),
]

# ------------------------------------------------------------------ issues
ISSUES = [   # led by the measured limits (decision D12, 2026-10-08)
    ("The thermal signal is weak where it can be checked",
     "Against calibrated TES thermal inertia, the THEMIS mosaics keep only a weak local signal (|r| ≈ 0.1 "
     "within 15° blocks) and none across the planet; Viking albedo tracks it (r −0.31 to −0.36). In the "
     "classification the thermal bands add 1.3–2.0 points, with two classifiers (§40.1, §42.4, §43.1, §56)."),
    ("The landform classes are terrain classes",
     "Slope and relief alone match all seven bands; against the geologic map the classes sit where terrain "
     "puts them, and \"lava tube\" marks volcano flanks, not lava plains (§40.1, §43.2)."),
    ("Lava flows come from the geologic map",
     "Volcanic plains are not separable from other plains in these bands; a fifth \"volcanic\" class tested "
     "below chance. The USGS map's volcanic units are the lava-flow reference (§43.3, §44)."),
    ("Closed depressions are not a crater count",
     "Of the candidates ≥ 1 km, 11–13% in the type areas and 15.3% across ±60° are catalogued craters; "
     "from 5 km up most are (62.2%). Robbins (385,049 craters) is the crater reference (§42.3, §54.4)."),
    ("Four hypotheses tested, none supported",
     "No band separates the geologic map's lava contacts much better than chance (the map is too coarse to "
     "settle H1); the composite's classes are the least reproducible input (H3); no channel threshold keeps "
     "first-order streams on real slopes (Q5); the volcanic window's channels are shallower, and thermal "
     "response separates nothing (H2, stage 1) (§47, §51)."),
    ("Digitising has not started",
     "The three landform classes are ready and empty in both type areas; candidates can now be accepted or "
     "rejected in the attribute table (§46). It is the critical path, and only judgement can do it."),
    ("250 GB on one USB drive",
     "Reads cap near 112 MB/s, and the drive has dropped off mid-write; big outputs are built on internal disk first (§2.2, §36.4)."),
    ("Solved since September",
     "Three coordinate frames, the z-factor defect, four failed global composites, the missing night mosaic, "
     "a defective DEM column at 180° (§15–20, §54)."),
]

NEXT_STEPS = [
    "Digitise Ius Chasma and Athabasca Valles: accept or reject the machine candidates, then draw what they miss",
    "Score the machine candidates against the reviewed features: the validation sheet (layout 14)",
    "Hypothesis H2 again, on reviewed channels with their origin set",
    "Deep learning: the U-Net's province map stands beside the published SVM map; any further tuning first "
    "needs validation blocks of its own, so the held-out score stays a test (§66.5, §66.9)",
    "Flow margins in visible against infrared at Athabasca, retested on digitised margins: hypothesis H1",
]

SCHEDULE = [   # (when, what)
    ("8–25 Oct", "Digitising by review starts; desktop runs done: pyramids, ±60° crater and channel pass, 200 m map, T1 in Pro, the deep-learning detector and U-Net"),
    ("26 Oct – 1 Nov", "H1 and H2 on digitised features"),
    ("mid-Nov", "Interim presentation and report"),
    ("14–22 Nov", "Validation against the digitised landforms; data freeze"),
    ("23 Nov – 4 Dec", "Final report and presentation"),
    ("8 Dec", "Final due"),
]
