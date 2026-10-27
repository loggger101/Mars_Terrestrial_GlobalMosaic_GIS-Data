# -*- coding: utf-8 -*-
"""The final presentation's content: the single source for build_final_deck.py (NEXT-STEPS.md §7).

Built on the interim's pattern (interim.py): every word and number on the slides is here, each with its KB §, and a
number changes here only after it changes in PROJECT-KNOWLEDGE.md. The slides follow the final report outline of
NEXT-STEPS.md §7: question and hook, data and the ±60° decision, co-registration, the thermal pair, craters,
channels, lava flows, classification and accuracy, limits, what next. The paper (NEXT STUFF\\Final\\paper) tells the
same story at length; the two must not disagree.

No rubric or template exists for the final (KB §50, D2): the deck uses the Presentation 1 design (le_theme.py), as the
interim does. Slide text is written in a neutral, impersonal voice.
"""
from content import DECK_TITLE, COURSE, TITLE                # unchanged since the prospectus
from interim import BANDS, CORRELATION                         # the data slides are the interim's, unchanged

AUTHOR = "Logan M Edwards"                                     # the public name, as the sheets' footers (KB §63)
STATUS_DATE = "22 October 2026"

QUESTION = (
    "Athabasca Valles was read as a water-carved outflow channel for decades, then reinterpreted as flood lava. "
    "Can a co-registered visible and thermal-infrared mosaic tell lava, water and impact landforms apart, "
    "and how far does the thermal infrared carry the answer?")                               # §14.4

GOALS = [
    "One co-registered stack: Viking visible colour, THEMIS day and night infrared and HRSC/MOLA topography "
    "on a single grid over ±60° (86.6% of the surface)",
    "Map the three landform families from it: lava flows, fluvial channels, impact craters",
    "Test whether thermal infrared separates surfaces that visible light cannot",
    "Score every product against something it never saw: held-out labels, the Robbins crater database, "
    "the USGS geologic map, calibrated TES thermal inertia",
]

HYPOTHESES = [   # (id, claim, verdict, KB)
    ("H1", "Day IR shows lava-flow margins that Viking misses",
     "Not supported at 1:20 M: day IR 21.0%, Viking red 12.3%, chance 10%; the difference's interval includes 0",
     "§47.2"),
    ("H2", "Fluvial and volcanic channels separate on gradient and thermal response",
     "Not supported at stage 1: the volcanic window's channels are shallower (1.4 against 10.2 m/km); thermal AUC 0.50",
     "§51.1"),
    ("H3", "The composite gives more stable classes than any single input",
     "Not supported: the composites are the least reproducible inputs (ARI 0.40 against 0.61–0.89)", "§47.3"),
    ("H4", "Crater rims from DN gradient recover the large IAU craters",
     "Answered by another method: fill depth recovers 68% of 117 craters ≥ 100 km", "§28.11"),
    ("T1", "Thermal IR improves the landform classification",
     "Yes, a little: +1.3 pt (numpy), +1.36 and +1.97 pt (Pro SVM), every interval above 0", "§40.1, §56"),
    ("T3", "The THEMIS pair tracks calibrated thermal inertia",
     "Weakly and only locally (|r| ≈ 0.1 within 15° blocks); Viking albedo carries the regional signal (r −0.36)",
     "§43.1"),
]

# ------------------------------------------------------------------ figures, in talk order
# images: ("layout", <layout name in the .aprx>, exported to final_img\ by make_final_figs.py)
#      or ("file", <path under build\>)
# section: a divider slide before this entry; special: a text or table slide of build_final_deck.py instead of a figure
# side_h (pt): a wide figure drawn left at this height, its takeaways right
FIGURES = [
    dict(section=("The question", "Lava or water at Athabasca Valles?"), special="question"),
    dict(title="Athabasca Valles: the hook",
         images=[("layout", "15_athabasca_type_area")], side_h=330,
         points=["150–162°E, 4–14°N: unit lAv, Late Amazonian volcanic (outlined)",
                 "Catalogued craters: 1,122 per million km² on lAv, 1,760 and 2,183 on the older units",
                 "Viking albedo tracks calibrated inertia here (r −0.55); the diurnal-contrast index does not"],
         source="§14.4, §42, §63"),
    dict(section=("Building the mosaic", "Four datasets, three coordinate frames, one grid"), special="bands"),
    dict(special="correlation"),
    dict(title="Where: the ±60° extent and the two type areas",
         images=[("layout", "10_global60_locator")],
         points=["±60° latitude: the THEMIS night mosaic's coverage, 86.6% of the surface",
                 "Ius Chasma (canyon and tributaries) and Athabasca Valles (flood lava)",
                 "Orange: the geologic map's volcanic units, the lava-flow reference"],
         source="§14.3, §16, §44"),
    dict(title="The mosaic at ±60°",
         images=[("layout", "08_global60_mosaic")],
         points=["THEMIS on a 180° meridian, Viking on 0°, the DEM in degrees: a window read at face value lands "
                 "half a planet away",
                 "One grid read off the night mosaic: day and night are never resampled; the DEM sits on it to 10 µm",
                 "Composite Bands failed four times globally by 13 Sep; on bounded extents it took 8.8 s"],
         source="§4, §8, §18, §28.1, §28.2"),
    dict(section=("The thermal pair", "What it can and cannot do"),
         title="Across ±60° the THEMIS mosaics carry local contrast",
         images=[("file", r"pres1_img\global60_thermal.png")],
         points=["Viking red separates dusty from rocky provinces by 47.67 DN; THEMIS day and night by −0.19 and +0.02",
                 "Every province repeats the mosaic-wide mean and spread: stretched region by region",
                 "So the diurnal-contrast index is not thermal inertia and is never compared across the planet"],
         source="§24.1, §28.10"),
    dict(title="Checked against calibrated thermal inertia (TES)",
         images=[("file", r"interim_img\tes_check.png")],
         points=["Viking albedo tracks TES inertia across the planet (r −0.31 dayside, −0.36 nightside)",
                 "Night IR and the index: a weak signal inside 15° blocks only (|r| ≈ 0.1); day IR none",
                 "The material signal at 3 km is in visible albedo"],
         source="§41, §42.4, §43.1"),
    dict(section=("Landforms", "Craters, channels, lava flows"),
         title="Basins ≥ 20 km: the large craters",
         images=[("layout", "07_global60_basins")], map_h=230,
         points=["5,144 closed basins ≥ 20 km from fill depth in 48 s at 1.6 km",
                 "68% of 117 IAU craters ≥ 100 km recovered; diameter error median +2.2%",
                 "Breached craters are invisible by construction (Oudemans is the type case)"],
         source="§26.3, §28.11"),
    dict(title="Closed depressions ≥ 1 km against the Robbins database",
         images=[("file", r"final_img\depressions_vs_robbins.png")],
         points=["465,354 closed depressions ≥ 1 km from an 11-hour pass at 200 m",
                 "Precision 15.3% at ≥ 1 km, 62.2% at ≥ 5 km, 83.1% at ≥ 20 km; chance under 11%",
                 "Recall levels off near half: degraded and breached craters stay hidden",
                 "Below ~5 km the density follows the DEM's sharpness (r −0.11 with Robbins): prompts, not an inventory"],
         source="§53.4, §53.6, §54.4"),
    dict(title="Channels: the Fill trap at Ius Chasma",
         images=[("file", r"interim_img\ius_channel_candidates.png")],
         points=["Fill raised the canyon floor up to 2,077 m into a synthetic lake",
                 "56.1% of the first network routed across ground that does not exist",
                 "A fill mask (fill − DEM ≤ 1 m) removes it; 188 of 2,610 candidates are steep and rock-floored"],
         source="§25.1, §25.2"),
    dict(title="Channels across ±60°",
         images=[("layout", "12_global60_channels")],
         points=["969,822 routed segments; 60.5% of stream cells discarded as fill artefact",
                 "89.8% lie on ground under 2°: plateau channels are DEM noise",
                 "Channel order follows the threshold, about one order per tenfold (T7): a setting, not a measurement"],
         source="§47.4, §53.6, §54.4"),
    dict(title="Lava flows: the classes against the geologic map (T8)",
         images=[("file", r"interim_img\t8_enrichment.png")],
         points=["'Lava tube' sits on volcano flanks and aprons (×3.30, ×4.29), not on volcanic plains (×0.84)",
                 "76% of the volcanic plains come out Normal Ground",
                 "Lava flows are therefore taken from the geologic map's volcanic units"],
         source="§43.2, §43.3, §57.1"),
    dict(title="Do the infrared mosaics show flow margins Viking misses? (H1)",
         images=[("file", r"interim_img\t5_margins.png")],
         points=["905 profiles across 10 lAv contacts at Athabasca, each against a random-line null (10%)",
                 "Day IR separates 21.0%, Viking red 12.3%: a lean toward H1, interval −1.7 to +18.1 pt",
                 "A 1:20 M map's contacts are kilometres wide: H1 needs margins digitised at 100 m"],
         source="§47.2"),
    dict(section=("Classification", "Scored on labels the model never saw"),
         title="The published landform map at ±60°",
         images=[("layout", "04_global60_landforms")],
         points=["SVM on 512 hand-drawn polygons, split by whole 15° blocks: 329 train, 183 held out",
                 "200 m, 11 × 11 majority filter: 73.8%, κ 0.58 held out (one class everywhere: 58.6%)",
                 "Normal Ground and cratered terrain solid; lava tube is not a result (user's 2%)"],
         source="§31.3, §55.3, §57"),
    dict(title="Where each held-out class lands",
         images=[("file", r"interim_img\accuracy_200m.png")],
         points=["Smoothing raises every score because the labelled polygons are large; the window is set by "
                 "feature size (~2 km), not by score",
                 "Halving the cell to 200 m bought no held-out accuracy"],
         source="§32.2, §55.3, §57"),
    dict(title="Does thermal infrared improve the classification? (T1)",
         images=[("file", r"interim_img\t1_pro.png")],
         points=["Thermal adds +1.36 pt at 200 m and +1.97 at 400 m, both intervals above 0 (numpy: +1.3)",
                 "It helps craters and hills and hurts lava tube",
                 "Terrain alone ties the score but makes a poor crater map: the classes are landform classes"],
         source="§40.1, §56, §56.1"),
    dict(title="Deep learning, 1: a box detector",
         images=[("layout", "16_x5_detections")], map_left=True,
         points=["RetinaNet on the 7-band stack, trained on the training blocks only",
                 "Crater: 41.9% of held-out polygons found, 87.6% of boxes right (always Crater: 71.1%)",
                 "Hills and lava tube never named; retrained unfrozen for 30 epochs, Normal Ground recall fell to 4.5%"],
         source="§66.1, §66.2, §66.5"),
    dict(title="Deep learning, 2: a U-Net maps terrain provinces",
         images=[("layout", "17_x5c_unet_provinces")], map_left=True,
         points=["Pixel classifier on the same stack and labels, over all of ±60°; a second pass 128 px offset "
                 "removes its tile seams (ratio 8.6–9.2 → 1.2)",
                 "Held out 98.9%, κ 0.980; lava tube user's 77.1% against 2.4%",
                 "Provinces, not features: 'Crater' covers 82.6% of the ring round named craters"],
         source="§66.6–66.9"),
    dict(title="The two maps under one scorer",
         images=[("file", r"final_img\svm_vs_unet.png")],
         points=["The U-Net agrees with the hand-drawn areas at province scale; the SVM separates craters from "
                 "their surroundings slightly better (57 / 46% against 91 / 83%)",
                 "Elevation alone reproduces 68% of the U-Net map, 55% of the SVM map",
                 "The SVM map stays the published landform map; the U-Net map stands beside it"],
         source="§57, §66.7, §66.8, §66.9"),
]

LIMITS = [   # (head, text)
    ("The thermal signal is weak where it can be checked",
     "The held THEMIS mosaics are 8-bit products stretched region by region: no calibrated thermal inertia, and "
     "against TES only |r| ≈ 0.1 inside 15° blocks. In the classification thermal adds 1.3–2.0 points (§24, §28.10, §43.1, §56)."),
    ("The landform classes are terrain classes",
     "Slope and relief alone match all seven bands; 'lava tube' marks volcano flanks, not lava plains (§40.1, §43.2)."),
    ("Five 'Crater' labels are volcanoes",
     "Arsia Mons alone is 31% of the held-out Crater area; one held-out label overlaps a training one by "
     "51.5 km² (§68.2)."),
    ("Closed depressions are not a crater count",
     "Below ~5 km most are not catalogued craters, and breached craters are invisible; Robbins is the crater "
     "reference (§26.3, §53.4)."),
    ("Channels and orders are DEM-limited",
     "Fill floods closed basins; 89.8% of ±60° channels lie under 2°; the stream order is a setting (§25.1, §47.4, §54.4)."),
    ("The review has only begun",
     "549 of 9,287 candidates reviewed, all at Ius Chasma (precision 54% on steep channels, 7% on depressions); "
     "the digitising classes hold 94 channels, 26 crater rims and no lava margins, so H1 and H2 wait (§69.7)."),
    ("A held-out test spent once",
     "Any further tuning of the deep-learning models needs validation blocks of its own (§66.5)."),
]

CONCLUSIONS = [
    "Four global products now share one co-registered grid over ±60°; the co-registration that failed four times works",
    "Visible albedo, day IR and night IR are three nearly independent dimensions, but the THEMIS mosaics carry "
    "local contrast only, and calibrated inertia follows Viking",
    "Craters ≥ 5 km are mostly recovered as closed depressions (62.2% precision); smaller ones and breached craters are not",
    "The published landform map scores 73.8%, κ 0.58 on blocks it never saw; thermal adds a resolved 1.4–2.0 points",
    "A U-Net reaches 98.9% as a terrain-province map; lava flows still come from the geologic map",
]

NEXT_STEPS = [
    "Review the 9,287 machine candidates at Ius Chasma and Athabasca Valles; draw breached craters and lava margins",
    "Retest H1 on margins digitised at 100 m and H2 on reviewed channels with their origin set",
    "Seven classes (D17): impact craters only, plus volcanic edifice, apron and fluvial channel; both maps scored "
    "on the same held-out polygons",
    "Material labels, not landform labels, to price the thermal bands; calibrated THEMIS products where they exist",
    "Validation blocks of their own before any further deep-learning tuning",
]

DATA = ("Every map, script and model: github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data, "
        "release data-2026-10-21 (CC BY 4.0 data, MIT scripts)")
