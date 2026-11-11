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
STATUS_DATE = "10 November 2026"

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
     "Not supported on the map's contacts or on margins traced on CTX: day IR 19.7%, Viking red 14.8%, chance 10%; the difference's interval includes 0",
     "§47.2, §69.52"),
    ("H2", "Fluvial and volcanic channels separate on gradient and thermal response",
     "Not supported at stages 1 and 1b: volcanic channels are shallower (window 1.4 against 10.2 m/km; mapped units "
     "2.4 against 13.9); thermal |d| ≤ 0.31",
     "§51.1, §69.50"),
    ("H3", "The composite gives more stable classes than any single input",
     "Not supported: the composites are the least reproducible inputs (ARI 0.40 against 0.61–0.89)", "§47.3"),
    ("H4", "Crater rims from DN gradient recover the large IAU craters",
     "Answered by another method: fill depth recovers 68% of 117 craters ≥ 100 km", "§28.11"),
    ("T1", "Thermal IR improves the landform classification",
     "Yes, a little, in overall accuracy: +1.3 pt (numpy), +1.36 and +1.97 pt (Pro SVM), every interval above 0; "
     "none by balanced accuracy; the seven-class U-Net loses 6.4–7.6 pt without it, not resolved by block",
     "§40.1, §56, §69.18, §69.86"),
    ("T3", "The THEMIS pair tracks calibrated thermal inertia",
     "Weakly and only locally (|r| ≈ 0.1 within 15° blocks); Viking colour carries the regional signal (r −0.36)",
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
                 "Viking colour tracks calibrated inertia here (r −0.55); the diurnal-contrast index does not"],
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
         points=["Viking colour tracks TES inertia across the planet (r −0.31 dayside, −0.36 nightside)",
                 "Night IR and the index: a weak signal inside 15° blocks only (|r| ≈ 0.1); day IR none",
                 "The material signal at 3 km is in Viking colour, not calibrated albedo"],
         source="§41, §42.4, §43.1"),
    dict(title="Smaller blocks do not uncover a stronger thermal signal (T3)",
         images=[("layout", "18_t3_tes_blocks")],
         points=["Night IR against TES inertia peaks within 2–5° blocks at r ≈ 0.12; 0.15–0.2 was predicted",
                 "Below 2° the signal falls away: a block then holds too few TES cells to test it",
                 "Viking's correlation shrinks with the block: a regional signal, the dust provinces"],
         source="§69.29, §69.30"),
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
                 "Precision 15.3% at ≥ 1 km, 63.2% at ≥ 5 km, 87.4% at ≥ 20 km; chance under 14%",
                 "Recall 52.4% at ≥ 5 km, by rim state 83.1% (freshest) down to 38.4% (most degraded)",
                 "Below ~5 km the density follows the DEM's sharpness (r −0.11 with Robbins): prompts, not an inventory"],
         source="§53.4, §53.6, §54.4, §69.45"),
    dict(title="The same, as size-frequency distributions",
         images=[("file", r"final_img\crater_sfd.png")],
         points=["Depressions ÷ catalogued craters: 1.32 at 1 km, 0.81 at 4 km, 0.52–0.60 from 8 to 128 km",
                 "Above ~5 km the detector has the catalogue's shape at about half its height",
                 "In review, precision rises with size: 5.5% at 1–2 km to 38.9% at 5–10 km at Ius, 7.2% to 72.2% at Athabasca"],
         source="§69.35"),
    dict(title="Channels: the Fill trap at Ius Chasma",
         images=[("file", r"interim_img\ius_channel_candidates.png")],
         points=["Fill raised the canyon floor up to 2,077 m into a synthetic lake",
                 "56.1% of the first network routed across ground that does not exist",
                 "A fill mask (fill − DEM ≤ 1 m) removes it; 188 of 2,610 candidates are steep and rock-floored"],
         source="§25.1, §25.2"),
    dict(title="Channels across ±60°",
         images=[("layout", "12_global60_channels")],
         points=["969,822 routed segments; 60.5% of stream cells discarded as fill artefact",
                 "89.8% under 2°; order ≥ 3 meets mapped valleys no better than chance",
                 "Order follows the threshold (T7): a setting, not a measurement"],
         source="§47.4, §53.6, §54.4, §69.50"),
    dict(title="Lava flows: the classes against the geologic map (T8)",
         images=[("file", r"interim_img\t8_enrichment.png")],
         points=["'Lava tube' sits on volcano flanks and aprons (×3.30, ×4.29), not on volcanic plains (×0.84)",
                 "76% of the volcanic plains come out Normal Ground",
                 "Lava flows are therefore taken from the geologic map's volcanic units"],
         source="§43.2, §43.3, §57.1"),
    dict(title="Do the infrared mosaics show flow margins Viking misses? (H1)",
         images=[("file", r"final_img\t5_traced.png")],
         points=["633 profiles on 78 margins traced on CTX at Athabasca, 905 on 10 lAv contacts at 1:20 M, each against a random-line null (10%)",
                 "Traced margins: day IR 19.7%, Viking red 14.8%; the difference +4.9 pt, interval −2.7 to +13.1",
                 "Map contacts: 21.0% against 12.3%; +8.7 pt, interval −1.7 to +18.1: the lean persists, zero inside both",
                 "An automated process traced the 86 margins (1,476 km) and, reading them again blind, kept 56 of 85: +3.3 pt there, −7.2 to +13.8; no one else has checked them"],
         source="§47.2, §69.52, §69.105"),
    dict(section=("Classification", "Scored on labels the model never saw"),
         title="The four-class landform map at ±60°",
         images=[("layout", "04_global60_landforms")],
         points=["SVM on 512 hand-drawn polygons, split by whole 15° blocks: 329 train, 183 held out",
                 "200 m, 11 × 11 majority filter: balanced accuracy 66.7% held out; 73.8%, κ 0.58 overall",
                 "Geography alone, the nearest training polygon's class: 61.3% balanced, 83.2% overall",
                 "Normal Ground and cratered terrain solid; lava tube is not a result (user's 2%)"],
         source="§31.3, §55.3, §57, §69.35"),
    dict(title="Where each held-out class lands",
         images=[("file", r"interim_img\accuracy_200m.png")],
         points=["Smoothing raises every score because the labelled polygons are large; the window is set by "
                 "feature size (~2 km), not by score",
                 "Halving the cell to 200 m bought no held-out accuracy"],
         source="§32.2, §55.3, §57"),
    dict(title="What beats the SVM: position, not height",
         images=[("file", r"final_img\svm_baselines.png")],
         points=["The nearest training polygon's class scores 83.2%; elevation and latitude alone 62.5%, 3.9 points "
                 "over one class everywhere",
                 "A 51 km majority filter lifts the four-class map to 82.1%, still below the nearest polygon",
                 "Seven classes: elevation and latitude 31.8%, the SVM 42.5%, the nearest polygon 45.6%; "
                 "filtering leaves the SVM flat"],
         source="§69.35, §69.50"),
    dict(title="Does thermal infrared improve the classification? (T1)",
         images=[("file", r"interim_img\t1_pro.png")],
         points=["Thermal adds +1.36 pt at 200 m and +1.97 at 400 m, both intervals above 0 (numpy: +1.3)",
                 "By balanced accuracy the gain is gone: 63.1% with the thermal bands, 63.4% without (200 m)",
                 "It helps craters and hills and hurts lava tube",
                 "Terrain alone ties the score but makes a poor crater map: the classes are landform classes",
                 "The seven-class U-Net, retrained once without it: 81.2% against 87.5%, a drop not resolved by block; a second training with it moves under 1 point"],
         source="§40.1, §56, §56.1, §69.86, §69.106"),
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
                 "Of the four-class maps the SVM is the landform map; the U-Net stands beside it"],
         source="§57, §66.7, §66.8, §66.9"),
    dict(section=("Seven classes", "The labels revised"),
         title="Seven classes: the landform map revised",
         images=[("layout", "04b_global60_landforms_v2")],
         points=["Crater narrowed to impact craters; volcanic edifice, apron and fluvial channel added; "
                 "971 reviewed labels (734 train, 237 held out)",
                 "SVM 42.5%, κ 0.31 held out, against the four-class map's 35.7% on the same polygons",
                 "Edifice ×4.15 on edifice units, apron ×5.69 on apron units; fluvial channel over-predicted"],
         source="§69.8, §69.24, §69.26"),
    dict(title="Seven classes from a U-Net",
         images=[("layout", "17b_unet_v2_provinces")], map_left=True, points_h=262,
         points=["Held out 69.0%, κ 0.606, against the seven-class SVM's 42.5% and the four-class U-Net's 44.1%",
                 "Ahead by balanced accuracy (56.9% against 41.9%), resolved by block here but not on the 1,652 "
                 "v3 held-out polygons; by accuracy the lead sits on two Tharsis blocks",
                 "Every new class above its share of the labels: user's edifice 0.487, apron 0.798, fluvial 0.702",
                 "Volcanic edifice spreads over 40.0% of ±60°; on the four original classes 61.9% against 98.9%"],
         source="§69.25, §69.44, §69.57"),
    dict(title="Seven classes lead, at a measured cost",
         images=[("file", r"final_img\svm_vs_unet_v2.png")],
         points=["A rule set before the run would keep the four-class maps: on classes 1–4 the SVM scores 66.0% "
                 "against 79.9%, and Crater loses 25.7 points of producer's accuracy",
                 "Presented all the same, the four-class maps beside them: they name what four classes cannot",
                 "The gain is in overall accuracy and macro F1, not balanced accuracy (SVM 41.9% against 42.0%, "
                 "U-Net 56.9% against 56.7%)"],
         source="§68.4, §69.24–69.26, §69.34"),
    dict(title="A third label set: more and smaller polygons",
         images=[("file", r"final_img\svm_vs_unet_v3.png")],
         points=["10,269 training and 1,652 held-out polygons in the same 14 blocks: seven-class polygons cut at 0.5° and "
                 "screened, others added by rule",
                 "On the 237 polygons: U-Net 87.6%, κ 0.844 (before 69.0%, 0.606); SVM 39.1%, κ 0.288 (before 42.5%, 0.310)",
                 "Volcanic edifice covers 18.0% of ±60° on the new U-Net map, against 40.0%",
                 "Asked for after the seven-class scores were read, so a gain here is not a fresh test"],
         source="§69.49, §69.76, §69.77, §69.81"),
    dict(title="The lead maps: the U-Net",
         images=[("layout", "17c_unet_v3_provinces")], map_left=True, points_h=262,
         points=["Above its registered range (60–78%), so a leak was sought first: no held-out polygon shares area with "
                 "a training polygon",
                 "13 of 14 blocks rise; Crater gives 8.6 of the 18.6 points, Normal Ground 5.6",
                 "'Crater' 93.5% inside 469 named craters, 53.0% in the ring around them",
                 "Still wrong: edifice denser inside none of 10 small named edifices, 7.7% at Syrtis Major; lava tube's user's 8.0%",
                 "On two draws of 14 other blocks, held out from retrained models: 86.6% and 85.4%"],
         source="§69.80, §69.81, §69.82, §69.84, §69.96, §69.105"),
    dict(title="The lead maps: the SVM, against its rule",
         images=[("layout", "04c_global60_landforms_v3")],
         points=["The rule set before the run keeps the v2 map: κ falls, and Crater falls from 40.0% to 18.2% of producer's",
                 "Hills rise 38.3 points and fluvial channel 12.7, but fluvial channel covers 31.9% of ±60°",
                 "No better than the nearest training polygon (−24.9 to +24.3 points), nor on two draws of 14 other blocks (37.9%, 45.6%)",
                 "Presented beside the U-Net all the same, on one label set"],
         source="§69.81, §69.82, §69.84, §69.96"),
    dict(title="Where the two lead maps agree: 47.5% of ±60°",
         images=[("file", r"final_img\map_agreement_v3.png")],
         points=["Colour: both maps give that class; grey: they differ. 39.7% on the earlier labels, 61.4% for four classes",
                 "They share the plains: Normal Ground's overlap rises 0.42 to 0.64, Crater's falls 0.30 to 0.12",
                 "Largest disagreement, 10.7% of ±60°: the SVM draws fluvial channel where the U-Net draws Crater",
                 "A class boundary is one method's reading; where both agree it does not depend on the method"],
         source="§69.46, §69.81"),
    dict(title="Why the SVM stays flat: one pixel's bands",
         images=[("file", r"final_img\svm_windows.png")],
         points=["A stand-in SVM on the same stack repeats Pro's: 39.3% on the second label set, 38.8% on the third",
                 "Ten times the 1,000 pixels a class adds −0.6 to +1.0 points; the third label set helps at no window",
                 "Surroundings lift it: 39.2% to 57.1% with windows to 20 km, 62.0% to 51 km, 69.2% with map coordinates too",
                 "The U-Net still leads by 26.2 points, apron 14.85 and Crater 8.48: classes defined by where they lie"],
         source="§69.95, §69.97, §69.98, §69.100"),
    dict(title="What lifted the U-Net: retrainings set out first",
         images=[("file", r"final_img\extra_runs.png")],
         points=["Each retrained once with the published settings, its prediction written before it ran",
                 "Balanced: cut pieces alone 78.1%, added polygons alone 77.6%, both 84.7%, neither 56.9%; "
                 "each half gives part, together most",
                 "Added polygons alone score highest by accuracy (89.3%) but lose hills (−37.4 points) and lava tube "
                 "(−38.6): most of their hills are the rule's",
                 "Without the thermal bands 81.2% against 87.5%, not resolved by block; almost all of it apron in the "
                 "Tharsis block read as edifice",
                 "Trained a second time: 86.8% (score within a point), but edifice on 8.7% of the windows against "
                 "16.3%: the class areas are one training's"],
         source="§69.86, §69.88, §69.91, §69.93, §69.106"),
    dict(title="A probability sample, on automated labels",
         images=[("file", r"final_img\r2_vs_polygons.png")],
         points=["25 points per class of the seven-class SVM map, labelled blind on CTX and shaded relief; 142 of the 175 decided",
                 "U-Net 49.6% against 21.7% on the earlier labels, interval +17.5 to +38.4; SVM 40.2% against 39.9%",
                 "The labelling's check failed (66.7% on 27 hidden points, the bar 70%), and it read 79.8% of the ground as Normal Ground",
                 "Off Normal Ground the U-Net leads the SVM by 34.4 pt, interval +5.1 to +63.7"],
         source="§69.53, §69.55, §69.77, §69.81"),
]

LIMITS = [   # (head, text)
    ("The thermal signal is weak where it can be checked",
     "The held THEMIS mosaics are 8-bit products stretched region by region: no calibrated thermal inertia; against "
     "TES |r| ≈ 0.1 inside 15° blocks. Per pixel thermal adds 1.3–2.0 points, none by balanced accuracy; without it "
     "the U-Net loses 6.4–7.6 (not resolved by block), an SVM seeing 51 km 8.0–9.9, mostly made up by map coordinates (§24, §56, §69.86, §69.99–§69.101, §69.106)."),
    ("The landform classes are terrain classes",
     "Slope and relief alone match all seven bands; 'lava tube' marks volcano flanks, not lava plains; the geologic "
     "map's unit groups cannot stand in for material labels either (§40.1, §43.2, §69.50)."),
    ("The seven classes cost the old ones",
     "Five four-class 'Crater' labels were volcanoes (Arsia Mons alone 31% of the held-out Crater area); the "
     "revision fixes that, but both seven-class maps fall below the four-class ones on the original classes. On the "
     "third label set the U-Net's edifice falls to 18.0% of ±60°; the SVM keeps fluvial channel over 31.9% (§68.2, §69.24, §69.25, §69.81)."),
    ("Closed depressions are not a crater count",
     "Below ~5 km most are not catalogued craters, and breached craters are invisible; Robbins is the crater "
     "reference (§26.3, §53.4)."),
    ("Channels and orders are DEM-limited",
     "Fill floods closed basins; 89.8% of ±60° channels lie under 2° and meet the mapped valleys no more often than "
     "a rotated valley map; the stream order is a setting (§25.1, §47.4, §54.4, §69.50)."),
    ("The review is partial",
     "3,791 of 9,287 candidates reviewed (precision 54% on steep Ius channels, 50% on rock-floored Athabasca channels, 10% and 13% on depressions); the digitising classes hold 202 channels, 381 crater rims and 86 traced lava margins; H2 needs both channel origins in one area, which neither type area has (§69.33, §69.52, §69.55, §69.63)."),
    ("The held-out blocks used three times",
     "By the four-class models, the seven-class ones and those on a third label set, asked for after the seven-class scores were read, "
     "so a gain there is not a fresh test; two draws of 14 other blocks give a retrained U-Net 86.6% and 85.4%, the second ahead of the nearest polygon once weighted to the first 14 blocks' class mix (§66.5, §69.49, §69.84, §69.96, §69.102)."),
    ("The polygons flatter five of six maps",
     "Polygon scores sit where a class is clear; the sample shows by how much, but on automated labels, which failed their "
     "check, and only the SVM on the third label set scores level, so unbiased accuracies need an analyst who passes it (§69.53, §69.55, §69.82)."),
]

CONCLUSIONS = [
    "Four global products now share one co-registered grid over ±60°; the co-registration that failed four times works",
    "Viking colour, day IR and night IR span about three dimensions, night IR nearly independent of the others, but the THEMIS mosaics carry "
    "local contrast only, and calibrated inertia follows Viking",
    "Craters ≥ 5 km are mostly recovered as closed depressions (63.2% precision); those missed are mostly degraded or breached",
    "Routed channels follow the elevation model (89.8% under 2°) and meet the mapped valleys no more often than chance",
    "The four-class landform map scores 66.7% balanced (73.8%, κ 0.58 overall) on blocks it never saw, above geography alone by class (61.3%); thermal adds a resolved 1.4–2.0 points overall, none by balanced accuracy",
    "A U-Net reaches 98.9% as a four-class province map and, with seven classes on a third label set, 87.6% on polygons and "
    "49.6% on a probability sample; the SVM there fails its rule (39.1%); both lead; lava flows still come from the geologic map",
    "H1 is not supported on 1,476 km of margins traced on CTX either, and H2 awaits a window that holds both channel origins",
]

NEXT_STEPS = [
    "Finish the review at both type areas; draw breached craters by hand",
    "An analyst to check the traced margins for H1; H2 needs one area with both channel origins",
    "Seven classes: curb the SVM's fluvial channel and win back its Crater; correct the U-Net's small edifices and lava tube",
    "Have the probability sample labelled by an analyst who passes its check: unbiased accuracies and class areas",
    "Material labels to price the thermal bands; validation blocks of their own before any further deep-learning tuning",
]

DATA = ("Every map, script and model: github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data, "
        "release data-2026-11-10 (CC BY 4.0 data, MIT scripts)")
