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

STATUS_DATE = "9 October 2026"

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
    ("Statistics, stretches, pyramids", "All products overviewed; the four source globals still not", None),  # §28 §29
    ("Grouped mosaic viewer", "Done", None),
    ("DEM terrain derivatives", "Rebuilt in degrees, type area and ±60°; WARNING 000869 gone", None),  # §20 §28.8
    ("Image-gradient products", "Renamed Gradient_*; not used further", None),                          # §7
    ("Jezero context", "Hosted services only; the dead HiRISE link removed", None),                     # §3 §50
    ("Classification", "±60° SVM on hand-drawn labels: 73.5%, κ 0.58 held out", None),          # §32.2
    ("CRS harmonisation", "Done: one 100 m / 200 m grid over ±60°", None),                    # §18 §28.1
    ("Visible + IR composite", "Done: type area; 7-band ±60° stack", None),                   # §18 §31.2
    ("Landform digitising", "Classes ready and empty; candidates reviewable; validation sheet ready; 512 training polygons drawn", None),  # §19.4 §29.2 §46 §49
    ("Crater inventory", "Robbins catalogue in the project (385,049); 5,144 basins ≥ 20 km at ±60°", None),  # §41 §28.11
    ("Map layouts", "12 layouts, from none, with graticules", None),                                    # §38 §42.1 §44 §49
    ("Report and presentations", "Interim deck and report are living builds from one source", None),  # §45
]
PROGRESS_SEPT = [90, 100, 70, 100, 80, 70, 20, 20, 15, 5, 0, 0, 0, 25]   # the 13 Sep deck, for comparison

# ------------------------------------------------------------------ processing log
LOG = [   # (date, what, outcome, §)
    ("18 Sep", "Type-area stack: four inputs on one 100 m grid", "Composite in 8.8 s, 100% co-valid", "§18"),
    ("18 Sep", "THEMIS Night IR acquired", "14.14 GB, pixel-aligned with day IR", "§15"),
    ("18 Sep", "Slope and hillshade rebuilt on a metric grid", "Slope in degrees; z-factor warning gone", "§20"),
    ("19 Sep", "±60° grids and diurnal contrast index", "15.2 bn px in 36.3 min", "§28"),
    ("19 Sep", "Channel and crater candidates, Ius", "2,610 channels; 1,685 closed depressions in 49 s", "§25–26"),
    ("19 Sep", "Basins at ±60°", "5,144 ≥ 20 km in 48 s", "§28.11"),
    ("24–30 Sep", "Global composites in the Pro GUI (desktop)", "First successes: 2 h 52 m, 3 h 10 m", "§29"),
    ("29 Sep", "Hand-drawn training polygons; SVMs", "Four classes; two ±60° maps", "§29"),
    ("2 Oct", "The first two SVM maps checked", "Tile artefact; mostly elevation", "§30"),
    ("3 Oct", "Corrected stack; SVM scored held out", "73.5%, κ 0.58 (5 × 5)", "§31–32"),
    ("6–7 Oct", "Backup to GitHub; class codes", "Public repository; pixel = class code", "§35–36"),
    ("8 Oct", "Reference data, Athabasca, tests T1–T3 and T8", "Thermal adds +1.3 points; ten layouts", "§38–44"),
    ("8–9 Oct", "Digitising by review; tests T4–T7; validation sheet",          # 14 rows overflow the slide
     "No support for H1–H3 or a tributary count; 12 layouts", "§46–51"),
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
         points=["Viking separates dusty from rocky provinces by 54.4 DN (these five boxes)",
                 "Both THEMIS mosaics separate them by under 0.3 DN",
                 "They are contrast-stretched region by region: thermal contrast is local",
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
                 "73.5%, κ 0.58 held out (one class everywhere: 58.6%)",
                 "Normal Ground and cratered terrain are solid; lava tube is not (2% user's)"],
         source="§31.3, §32.2"),
    dict(title="The landform classes against the USGS geologic map",
         images=[("file", r"interim_img\t8_enrichment.png")],          # layout 13 is the Pro sheet; its table, legible
         points=["Each cell: how much more often a class occurs in a unit group than across ±60° (×1 = no link)",
                 "\"Lava tube\" is not enriched on volcanic plains (×0.87) but on volcano flanks and aprons (×3.34, ×4.12)",
                 "75% of the volcanic plains come out Normal Ground",
                 "A coherent terrain map, not a lava-flow map: lava flows come from the geologic map"],
         source="§43.2, §49"),
    dict(title="Does thermal infrared improve the classification?",
         images=[("file", r"interim_img\thermal_ablation.png")],
         points=["Slope and relief alone: 68.6%, κ 0.51 held out; all seven bands: 67.0%, κ 0.50",
                 "The thermal bands add +1.3 points (95% interval +0.6 to +2.2): real, but small",
                 "Without terrain, visible and thermal score below one class everywhere (58.6%)",
                 "The labelled classes are landforms, so terrain decides them; the thermal claim needs material labels"],
         source="§40"),
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
     "classification the thermal bands add 1.3 points (§40.1, §42.4, §43.1)."),
    ("The landform classes are terrain classes",
     "Slope and relief alone match all seven bands; against the geologic map the classes sit where terrain "
     "puts them, and \"lava tube\" marks volcano flanks, not lava plains (§40.1, §43.2)."),
    ("Lava flows come from the geologic map",
     "Volcanic plains are not separable from other plains in these bands; a fifth \"volcanic\" class tested "
     "below chance. The USGS map's volcanic units are the lava-flow reference (§43.3, §44)."),
    ("Closed depressions are not a crater count",
     "Only 11–13% of the detector's ≥ 1 km candidates are catalogued craters; the Robbins catalogue "
     "(385,049 craters) is the crater reference (§42.3)."),
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
     "Three coordinate frames, the z-factor defect, four failed global composites, the missing night mosaic (§15, §18, §20)."),
]

NEXT_STEPS = [
    "Digitise Ius Chasma and Athabasca Valles: accept or reject the machine candidates, then draw what they miss",
    "Craters and channels ≥ 1 km across ±60° on the desktop (a 7-hour resumable run), scored against Robbins",
    "Hypothesis H2 again, on reviewed channels with their origin set",
    "A deep-learning model on the desktop GPU, trained on the training split and scored on the held-out polygons",
    "Flow margins in visible against infrared at Athabasca, retested on digitised margins: hypothesis H1",
    "Pyramids on the four source mosaics, for faster work in ArcGIS Pro",
]

SCHEDULE = [   # (when, what)
    ("8–25 Oct", "Digitising by review starts; desktop runs: junctions, pyramids, ±60° crater and channel pass"),
    ("26 Oct – 1 Nov", "±60° crater and channel sheets; H1 and H2 on digitised features"),
    ("mid-Nov", "Interim presentation and report"),
    ("14–22 Nov", "Validation against the digitised landforms; data freeze"),
    ("23 Nov – 4 Dec", "Final report and presentation"),
    ("8 Dec", "Final due"),
]
