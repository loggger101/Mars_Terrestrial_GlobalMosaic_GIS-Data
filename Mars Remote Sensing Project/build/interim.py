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

STATUS_DATE = "8 October 2026"

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
    ("Scope, targets and type area", "Ius Chasma type area; ±60° extent decided", None),       # §14.3 §16
    ("Raster acquisition", "Three globals + THEMIS Night IR", None),                                     # §15
    ("Statistics, stretches, pyramids", "All products overviewed; the four source globals still not", None),  # §28 §29
    ("Grouped mosaic viewer", "Done", None),
    ("DEM terrain derivatives", "Rebuilt in degrees, type area and ±60°; WARNING 000869 gone", None),  # §20 §28.8
    ("Image-gradient products", "Renamed Gradient_*; not used further", None),                          # §7
    ("Jezero context", "Hosted services only; HiRISE link dead", None),                                 # §3
    ("Classification", "±60° SVM on hand-drawn labels: 73.5%, κ 0.58 held out", None),          # §32.2
    ("CRS harmonisation", "Done: one 100 m / 200 m grid over ±60°", None),                    # §18 §28.1
    ("Visible + IR composite", "Done: type area; 7-band ±60° stack", None),                   # §18 §31.2
    ("Landform digitising", "Classes ready and empty; 512 training polygons drawn", None),              # §19.4 §29.2
    ("Crater inventory", "1,685 at Ius ≥ 1 km; 5,144 basins ≥ 20 km at ±60°", None),  # §26 §28.11
    ("Map layouts", "8 layouts, from none", None),                                                       # §38
    ("Report and presentations", "Interim being rebuilt", None),
]
PROGRESS_SEPT = [90, 100, 70, 100, 80, 70, 20, 20, 15, 5, 0, 0, 0, 25]   # the 13 Sep deck, for comparison

# ------------------------------------------------------------------ processing log
LOG = [   # (date, what, outcome, §)
    ("18 Sep", "Type-area stack: four inputs on one 100 m grid", "Composite in 8.8 s, 100% co-valid", "§18"),
    ("18 Sep", "THEMIS Night IR acquired", "14.14 GB, pixel-aligned with day IR", "§15"),
    ("18 Sep", "Slope and hillshade rebuilt on a metric grid", "Slope in degrees; z-factor warning gone", "§20"),
    ("19 Sep", "±60° grids and diurnal contrast index", "15.2 bn px in 36.3 min", "§28"),
    ("19 Sep", "Channel and crater candidates, Ius", "2,610 channels; 1,685 craters in 49 s", "§25–26"),
    ("19 Sep", "Basins at ±60°", "5,144 ≥ 20 km in 48 s", "§28.11"),
    ("24–30 Sep", "Global composites in the Pro GUI (desktop)", "First successes: 2 h 52 m, 3 h 10 m", "§29"),
    ("29 Sep", "Hand-drawn training polygons; SVMs", "Four classes; two ±60° maps", "§29"),
    ("2 Oct", "The first two SVM maps checked", "Tile artefact; mostly elevation", "§30"),
    ("3 Oct", "Corrected stack; SVM scored held out", "73.5%, κ 0.58 (5 × 5)", "§31–32"),
    ("6–8 Oct", "Backup to GitHub; class codes; layout 08", "Eight layouts", "§35–38"),
]

# ------------------------------------------------------------------ figures (preliminary results)
# images: ("layout", <layout name in the .aprx>) or ("file", <path under build\>)
FIGURES = [
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
                 "1,685 closed depressions ≥ 1 km, checked on two named craters just outside: "
                 "Perrotin within 7.1%, Oudemans missed because it is breached"],
         source="§25, §26"),
    dict(title="Landforms at ±60°, scored on labels the model never saw",
         images=[("layout", "04_global60_landforms")],
         points=["SVM on 512 hand-drawn polygons, split by whole 15° blocks",
                 "73.5%, κ 0.58 held out (one class everywhere: 58.6%)",
                 "Normal Ground and cratered terrain are solid; lava tube is not (2% user's)"],
         source="§31.3, §32.2"),
    dict(title="Checking the first two classifications",
         images=[("layout", "05_svm_checks")],
         points=["29 Sep map follows its 4096-px processing tiles, not the terrain",
                 "30 Sep map is mostly elevation: elevation alone reproduces 62% of it",
                 "Both led to the corrected stack: no elevation band, slope in degrees"],
         source="§30"),
]

# ------------------------------------------------------------------ issues
ISSUES = [
    ("Thermal contrast is local",
     "Both THEMIS mosaics were stretched region by region, so day–night contrast works inside one "
     "area and fails across the planet. Calibrated thermal inertia is not derivable from them (§24, §28.10)."),
    ("Lava flows have no reliable product yet",
     "The lava tube class is right 2% of the times it is mapped. Needs new labels or the USGS geologic map."),
    ("Digitising has not started",
     "The three landform classes are ready and empty; it is the critical path, and only judgement can do it."),
    ("Closed-depression craters only",
     "Fill depth finds closed basins; breached craters, the fluvially modified ones, need hand mapping (§26.3)."),
    ("250 GB on one USB drive",
     "Reads cap near 112 MB/s, and the drive has dropped off mid-write; big outputs are built on internal disk first (§2.2, §36.4)."),
    ("Solved since September",
     "Three coordinate frames, the z-factor defect, four failed global composites, the missing night mosaic (§15, §18, §20)."),
]

NEXT_STEPS = [
    "Digitise Ius Chasma: accept or reject the machine candidates, then draw what they miss",
    "Measure whether the thermal bands improve the classification, with the hand-drawn labels",
    "Craters and channels ≥ 1 km across ±60° (a 7-hour resumable run)",
    "A second type area at Athabasca Valles: flood lava once mapped as a water channel",
    "Score against the USGS geologic map: the reference for lava flows",
]

SCHEDULE = [   # (when, what)
    ("8–25 Oct", "Digitising starts; thermal test; ±60° crater and channel run; Athabasca"),
    ("26 Oct – 1 Nov", "±60° crater and channel sheets; reference data scored"),
    ("mid-Nov", "Interim presentation and report"),
    ("14–22 Nov", "Validation against the digitised landforms; lava-flow sheet; data freeze"),
    ("23 Nov – 4 Dec", "Final report and presentation"),
    ("8 Dec", "Final due"),
]
