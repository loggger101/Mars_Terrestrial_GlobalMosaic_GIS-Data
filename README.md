# Mars Global Mosaic

[![check](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/actions/workflows/check.yml/badge.svg)](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/actions/workflows/check.yml)
[![paper](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/actions/workflows/paper.yml/badge.svg)](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/actions/workflows/paper.yml)

**Mapping Lava Flows, Fluvial Channels, and Impact Craters in Visible and Infrared.**
Logan M Edwards · OCN 4704 Remote Sensing · Fall 2026 · Florida Institute of Technology

An ArcGIS Pro project that co-registers Viking visible colour, THEMIS day and night thermal infrared and the HRSC/MOLA elevation model of Mars, then uses the stack to map three landform families: volcanic flow units, fluvial channels and valley networks, and impact craters. The scientific hook is Athabasca Valles, mapped for decades as a water-cut outflow channel before it was reinterpreted as flood lava. Morphology together with thermal response is this project's way of telling the two apart.

The analysis extent is **±60° latitude** (86.6% of the surface), set by the coverage of the THEMIS night mosaic. The detail work is done in two type areas: **Ius Chasma**, western Valles Marineris (271–286°E, 6–13°S), carved by water and collapse, and **Athabasca Valles** (150–162°E, 4–14°N), on flood lava. Layout 10 shows where they are; 01, 02 and 15 show each one in the inputs ([layouts](#layouts)).

This repository is the project page and an off-drive backup of the project. The working copy lives on an external drive (about 430 GB with all derived rasters, measured 2026-10-22). The tree holds everything small: the scripts, the knowledge base, the ArcGIS project file, the hand-drawn training labels and every vector layer, the layouts, the logs and the deliverables. The rasters go in three [releases](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases).

**Contents:** [knowledge base](Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md) (the full record, every number tagged verified or open) · [rasters](docs/rasters.md) and [vector layers](exports/README.md) (what each one is) · [figures](docs/figures.md) (every map sheet and chart, with the script that makes it) · [build scripts](docs/scripts.md) (all 250, by purpose) · [software environment](docs/environment.md) (each machine's versions, read from the machine) · [backup and restore](docs/backup.md)

[![Mars ±60° landform classification, seven classes, from a U-Net on the third label set](docs/thumbs/17c_unet_v3_provinces.jpg)](Mars%20Project/Global60/layouts/17c_unet_v3_provinces.png)
*The lead map: seven landform classes over ±60° from a U-Net trained on the third label set, scored on polygons it never saw (layout 17c; the SVM map on the same labels is layout 04c, the seven-class map on the reviewed labels 04b, the four-class map 04).*

## How it works

![Pipeline: four sources in three frames, one ±60° grid, the products, the SVM and U-Net classifiers and the candidates](docs/pipeline.svg)

The four sources sit in three coordinate frames. Everything is put on one grid read from the night mosaic, so the day–night pair is never resampled and the DEM lands on its native 200 m. Elevation is kept out of the classification stack on purpose: in raw metres it would swamp the 8-bit bands, and an earlier map that included it turned out to be mostly an elevation map. The machine candidates are prompts for a person to accept or reject, not results.

## What was asked and what was found

The prospectus asked whether a co-registered visible and thermal-infrared mosaic can separate lava, water and impact landforms on Mars, and how much of the answer comes from the thermal infrared. The short answers, each with its section below and its full account in the paper:

1. **The four sources do go on one grid.** Viking colour, THEMIS day and night infrared and the HRSC/MOLA elevation model, on three coordinate frames, are co-registered over ±60° without resampling the day–night pair ([How it works](#how-it-works)).
2. **The THEMIS mosaics are not a thermal-inertia map.** They are 8-bit products stretched region by region: dusty and rocky provinces differ by 47.67 DN in Viking red and by almost nothing in either infrared mosaic. Against TES thermal inertia, Viking red tracks it across the planet (r −0.36) and the THEMIS pair keeps only a weak local signal (|r| ≈ 0.1) ([Against calibrated thermal inertia](#against-calibrated-thermal-inertia-t3)).
3. **Craters are found from the elevation model, about half of them.** Of 465,354 closed depressions of 1 km and more, 63.2% of those ≥ 5 km are catalogued craters, and recall levels off near half; most of the craters missed are degraded or breached ([Craters](#craters)).
4. **The routed channel network is the elevation model's drainage, not a valley map.** Of 969,822 segments, 89.8% lie on ground under 2°, and only 2.8% of the larger ones' length lies within 5 km of a mapped valley ([Channels](#channels)).
5. **A classifier maps landforms from terrain more than from colour or heat.** A support vector machine scored on whole 15° blocks it never saw reaches a balanced accuracy of 66.7% (73.8% overall); the thermal bands add 1.4 to 2.0 points overall and nothing by balanced accuracy ([classification](#60-landform-classification), [T1](#does-thermal-infrared-help-test-t1)).
6. **Seven classes need a network that sees surroundings.** On a third, rule-made label set a U-Net scores 87.6% on 237 held-out polygons, 86.6% and 85.4% on two other draws of held-out blocks, and 49.6% on a probability sample; the support vector machine, held to one pixel's seven bands, scores 39.1% ([Deep learning](#deep-learning-x5)).
7. **Lava flows are not separable in these bands.** No band separates the geologic map's lava contacts or the traced margins at Athabasca Valles much better than chance, so lava flows are taken from the USGS geologic map. Three of the prospectus' four hypotheses are not supported; the fourth is answered by another method ([hypotheses](#the-prospectus-hypotheses-t4t7)).

## Where to start

| To read | Open |
|---|---|
| The final paper (AASTeX, PDF) | [`mars_global_mosaic.pdf`](Mars%20Remote%20Sensing%20Project/NEXT%20STUFF/Final/paper/mars_global_mosaic.pdf); its source and figures are beside it in [`NEXT STUFF/Final/paper/`](Mars%20Remote%20Sensing%20Project/NEXT%20STUFF/Final/paper) |
| The final presentation | [`Mars Global Mosaic - Final Presentation.pptx`](Mars%20Remote%20Sensing%20Project/NEXT%20STUFF/Final/Mars%20Global%20Mosaic%20-%20Final%20Presentation.pptx) |
| The lead maps | layouts [17c](Mars%20Project/Global60/layouts/17c_unet_v3_provinces.png) (U-Net) and [04c](Mars%20Project/Global60/layouts/04c_global60_landforms_v3.png) (SVM); all 26 sheets are under [Layouts](#layouts) |
| The results in brief, with their charts | [Results](#results), below |
| The maps and layers themselves | [Using the data](#using-the-data); ArcGIS Pro is not needed |
| How any number was reached | the [knowledge base](Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md), by section number (the paper's source cites one beside every number) |
| The earlier deliverables | the interim report and presentation in [`NEXT STUFF/`](Mars%20Remote%20Sensing%20Project/NEXT%20STUFF); the prospectus and Presentation 1 in [`OLD/`](Mars%20Remote%20Sensing%20Project/OLD) |

**Status, 11 November 2026: this page is a draft of the finished-work page.** The paper and deck are drafts until the data freeze on **22 November**; the final is due **8 December 2026**. One retraining of the lead U-Net is still running and its result will be added here, in the paper and in the deck.

| Part of the project | State |
|---|---|
| Sources and one ±60° grid | done: all four inputs match their published sizes; the grid is defined once in [`grid60.py`](Mars%20Remote%20Sensing%20Project/build/grid60.py) |
| Terrain derivatives and the 7-band stack | done at 200 m: slope in degrees on a metric grid, aspect, hillshade; a stack with no raw elevation band, 97.3% co-valid |
| Classification, four classes | done: the support vector machine map (layout 04), 73.8%, κ 0.58 held out; a U-Net beside it (layout 17) |
| Classification, seven classes | done: the maps on the third label set lead the final (layouts 04c, 17c); the maps on the reviewed labels (04b, 17b) are kept as history |
| Crater and channel candidates | done at ±60° and in both type areas, checked against the Robbins catalogue and the mapped valleys |
| Landform layers | 202 channels, 381 crater rims and 86 lava margins accepted into the three layers; the review of candidates stopped at 3,791 of 9,287 |
| Tests T1–T9 and the hypotheses | done, with every chart drawn from its test's log |
| Map layouts | twenty-six, below |
| Paper and deck | drafts, built from one record; frozen 22 November |

### The working record

Beside the results, the repository keeps the files the project was run from. They are not deliverables and are written as notes to the next working session, not to a reader:

- [`NEXT-STEPS.md`](Mars%20Remote%20Sensing%20Project/NEXT-STEPS.md): the working plan and the table of decisions, each with the date it was answered.
- [`HANDOFF-DESKTOP.md`](Mars%20Remote%20Sensing%20Project/HANDOFF-DESKTOP.md): how to work on the project on each machine.
- [`INTERIM-PLAN.md`](Mars%20Remote%20Sensing%20Project/INTERIM-PLAN.md): the plan the interim was built to.
- [`build/logs/`](Mars%20Remote%20Sensing%20Project/build/logs): every run's log and the scores as JSON, which the charts and the paper's numbers are read from.

The [knowledge base](Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md) is both: the record every number in the paper and deck is checked against, and a dated log of how each result was reached, including the ones that failed.

## Results

The method, the traps and every number behind these are in [`PROJECT-KNOWLEDGE.md`](Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md); every chart is drawn from a test's log, never retyped ([figures](docs/figures.md) lists each one with its script).

### ±60° landform classification

A support vector machine on the hand-drawn labels, scored on 183 polygons in 15° blocks it never saw. The published map (200 m, 11 × 11, the map at the top) scores a **balanced accuracy of 66.7%** and **73.8%, κ 0.58** overall, against 58.6% for one class everywhere; per pixel 69.9%, κ 0.53. Geography alone, giving each pixel the class of the nearest training polygon, scores 83.2% overall but 61.3% balanced: the map is ahead class by class, behind overall, and resampling the held-out blocks resolves neither gap (KB §69.35, §69.44). Elevation and latitude alone score 62.5% (one class everywhere 58.6%), so the score is not mostly height; a 51 km majority filter lifts the per-pixel map to 82.1%, still under the nearest-polygon line ([figure](Mars%20Remote%20Sensing%20Project/build/final_img/svm_baselines.png); A3, KB §69.50). Normal Ground is reliable (99% producer's) and Crater behaves as cratered terrain. The lava tube class isn't usable (2% user's accuracy).

[<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/accuracy_200m.png" width="760" alt="The published map's held-out confusion matrix, and held-out accuracy against the majority filter window at 200 m and 400 m">](Mars%20Remote%20Sensing%20Project/build/interim_img/accuracy_200m.png)

*A: where each hand-drawn class's held-out area lands on the map; each row sums to 100%, the diagonal is producer's accuracy and the row under it user's. Most lava-tube pixels fall on Crater polygons. B: each step of smoothing gains 0.4–1.8 points; the 400 m map (superseded) runs 0.6–1.7 points above the 200 m one at each window.*

### Does thermal infrared help? (test T1)

Yes, a little. With ArcGIS Pro's SVM over the whole ±60°, leaving the thermal bands out costs 1.36 points at 200 m (95% interval 0.46 to 2.47) and 1.97 at 400 m (1.08 to 3.35), from crater and hill terrain; lava tube scores better without them. A numpy classifier on the same split gives +1.3. The gain at 200 m holds when whole held-out blocks are resampled instead of polygons (0.46 to 2.67, KB §69.44); by balanced accuracy there is none. Leaving out the Viking bands, or both spectral groups, ties the full stack inside wide intervals, but terrain alone makes a poor crater map. The hand-drawn classes are landforms, and terrain decides them. On the seven reviewed classes the numpy classifier gains 1.1 points from thermal (0.6 to 1.7), 0.8 balanced, mostly on Crater; none of the three new classes gains 2 points (T1b, KB §69.50). The geologic map's unit groups (SIM 3292) were tried as material labels instead (T9): on a 4 km lattice the stack predicts them no better than their commonest group, with or without thermal, which adds at most a point, so they cannot price the thermal bands either (KB §69.50). On the third label set the seven-class U-Net, retrained without the thermal bands, scores 81.2 % against 87.5 %, a drop not resolved when the held-out blocks are resampled, most of it apron read as edifice in one Tharsis block (KB §69.86, §69.91). A stand-in SVM that sees 51 km around each point loses 8.0–9.9 points without them, all of it from the window statistics, and the point's map coordinates make up most or all of it, so there the thermal share is not shown to be material (KB §69.99–§69.101).

| What each band group adds (ArcGIS Pro SVM) | Held-out accuracy by band set (numpy classifier, 400 m) |
|---|---|
| [<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/t1_pro.png" alt="T1: accuracy the thermal bands add, with 95% intervals">](Mars%20Remote%20Sensing%20Project/build/interim_img/t1_pro.png) | [<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/thermal_ablation.png" alt="T1: held-out accuracy for seven band sets">](Mars%20Remote%20Sensing%20Project/build/interim_img/thermal_ablation.png) |
| Dot: accuracy with all bands minus accuracy without the group; line: paired-bootstrap 95% interval over the 183 held-out polygons. Right of 0, the group helps. | Cyan: band sets that include slope and relief. The dashed line is one class everywhere. |

### Deep learning (X5)

Two deep-learning models, trained on the desktop GPU on the same training blocks as the SVM and scored on the same held-out polygons. A RetinaNet detector on 7-band chips finds Crater polygons with 41.9% recall and 87.6% precision, against 71.1% for naming every polygon Crater, and never names the two rare classes (layout 16); retrained with its backbone unfrozen it names the hills but loses the plains (Normal Ground recall 4.5%). A U-Net pixel classifier over all of ±60° scores **98.9%, κ 0.980** held out, against the published map's 73.8%, κ 0.583 under the same scorer, and raises lava tube's user's accuracy from 2% to 77%. It paints terrain provinces rather than single landforms: its 'Crater' class covers 83% of the ring around named craters as well as the craters themselves. A second pass on a grid offset by 128 px removes the seams of the tool's 256 px tiles. The SVM map stays the published one; the U-Net map sits beside it as the province map (KB §66). On the reviewed seven-class labels a second U-Net scores 69.0%, κ 0.606 against the seven-class SVM's 42.5%, though volcanic edifice spreads over 40% of ±60° (layout 17b, KB §69.25). Against named features, its fluvial channel gathers on the named valleys (within 2 km of their valley lines more than 10–20 km away for 83% of 83 valles), but its edifice is less common inside each of the 10 smaller named Mons, Tholus and Patera scored than around them; the large volcanoes carry labels and can't be checked this way (KB §69.39). Resampling whole held-out blocks, the four-class U-Net's lead over the SVM map holds (+11 to +41 points), but the seven-class U-Net's 26.5-point lead in accuracy does not (−10 to +48; by balanced accuracy it does, +2 to +20): it rests on the two Tharsis blocks. The SVM and U-Net maps agree on 61.4% of ±60° with four classes and 39.7% with seven (KB §69.44, §69.46). On a third label set of 10,269 training polygons, seven classes, a U-Net scores 87.6 %, κ 0.844 on the 237 held-out polygons and 49.6 % on a probability sample; the SVM there scores 39.1 %, κ 0.288, and fails the rule set for it. Both lead the final, the author's choice ([KB §69.82](Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md)). Retrained with 14 other blocks held out, drawn at random twice, the U-Net scores 86.6 % and 85.4 %, so its score is not a property of the first held-out blocks; on the second draw its lead over the nearest training polygon is resolved only once weighted to the first blocks' class mix (KB §69.84, §69.96, §69.102). The support vector machine is held by one pixel's seven bands: a stand-in given each band's statistics over windows to 51 km rises from 39.2 % to 62.0 %, and the U-Net still leads it (KB §69.95–§69.98).

[<img src="docs/thumbs/17_x5c_unet_provinces.jpg" width="640" alt="Layout 17: the U-Net terrain-province map over ±60°, one held-out block, and its scores beside the SVM map's">](Mars%20Project/Global60/layouts/17_x5c_unet_provinces.png)

*Layout 17: the two-pass U-Net map over ±60° (A), one held-out block with its 31 hand-drawn polygons (B), and the U-Net and SVM maps under the same scorer.*

### Against calibrated thermal inertia (T3)

Across ±60°, TES thermal inertia tracks Viking red (r −0.36), while the THEMIS mosaics keep only a weak signal inside regions (|r| ≈ 0.1); in the two type areas the diurnal-contrast index does not track it. Where a calibrated product can check, the Viking colour (not a calibrated albedo, see Limits) carries the material signal. By block size the THEMIS signal is strongest inside 2–5° blocks (night IR r ≈ +0.12, against +0.09 in 15° blocks) and fades below 2°, where the ~3 km TES grid runs out ([chart](Mars%20Remote%20Sensing%20Project/build/final_img/tes_block_scale.png)). Mapped in 5° blocks (layout 18) it holds best on high-inertia southern ground, with Ius Chasma among the strongest blocks, and is weak on the dusty northern provinces and at Athabasca.

[<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/tes_check.png" width="640" alt="T3: correlation of each layer with TES thermal inertia">](Mars%20Remote%20Sensing%20Project/build/interim_img/tes_check.png)

*Correlation of each layer with log thermal inertia from TES (~3 km cells): blue across all of ±60°, orange the median inside 15° blocks.*

Inside a type area the day–night pair does carry a signal that topography doesn't: at Ius Chasma the diurnal-contrast index correlates with slope at only −0.25, and the two steepest object classes sit at opposite signs. Whether that is material is untestable below the ~3 km TES resolves.

[<img src="docs/thumbs/ius_thermal_contrast.jpg" width="640" alt="Ius Chasma diurnal-contrast index, its mean per class, and the class means against slope">](Mars%20Remote%20Sensing%20Project/build/interim_img/ius_thermal_contrast.png)

*A: the index over Ius Chasma (day and night IR each stretched on its own, then differenced; relative, not inertia). B: its mean per object-based class. C: the same means against slope (KB §24).*

The province test shows why. Over seven provinces with textbook thermal-inertia contrast, the diurnal-contrast index differs between dusty and rocky by −0.0009, against scatter of 0.13–0.23 inside each. Every province repeats the mosaic-wide mean and spread of both THEMIS mosaics, which are stretched region by region, while Viking red separates dusty from rocky by 47.67 DN.

[<img src="Mars%20Remote%20Sensing%20Project/build/pres1_img/global60_thermal.png" width="720" alt="Province test: the diurnal-contrast index over seven provinces, and day IR, night IR and Viking red DN over four">](Mars%20Remote%20Sensing%20Project/build/pres1_img/global60_thermal.png)

*A: index mean ± sd per province. B: DN mean ± sd in each source, the grey band the whole mosaic's; the numbers are dusty − rocky. KB §28.10.*

### Against the USGS geologic map (T8, T2)

The classes sit where terrain puts them, and volcanic plains can't be separated from other plains in these bands, so lava flows are shown from the map's volcanic units (layout 10). At Athabasca the flood lava (`lAv`) is the least cratered large unit: 1,122 catalogued craters per million km², against 1,760 and 2,183 on the older units (layout 15 outlines the unit on all four inputs).

[<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/t8_enrichment.png" width="720" alt="T8: enrichment of each class on each geologic unit group">](Mars%20Remote%20Sensing%20Project/build/interim_img/t8_enrichment.png)

*How strongly each class gathers on each unit group of SIM 3292: red over-represented, blue under-represented (layout 13 has the map).*

Relabelling the lava-tube polygons as the map's volcanic units doesn't rescue a lava class: as a third class it is found on 21% of its held-out area, and as a fifth class only 30% of what it calls volcanic is, below the 38% share of volcanic ground in the test blocks. The four hand-drawn classes stay.

[<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/lava_relabel.png" width="720" alt="The lava-tube relabel test: held-out accuracy of four class schemes">](Mars%20Remote%20Sensing%20Project/build/interim_img/lava_relabel.png)

*Held-out accuracy on the Crater, hills and Normal Ground polygons for each scheme, classifier at 1.6 km (KB §43.3).*

T2 counts craters per unit. The catalogue ranks the flood lava lowest at Athabasca; the closed-depression detector reverses it, counting pits on flat lava that are not craters, so it can't date surfaces.

[<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/t2_density.png" width="720" alt="T2: craters of 1 km and larger per million square kilometres on each geologic unit, catalogue against detector">](Mars%20Remote%20Sensing%20Project/build/interim_img/t2_density.png)

*Craters ≥ 1 km per 10⁶ km² on each unit of at least 20,000 km² in the two windows: blue the Robbins & Hynek catalogue, orange the detector. Relative density only, not an age (KB §42.2).*

### Craters

Across ±60°, 465,354 closed depressions ≥ 1 km; against the Robbins catalogue 15.3% of them are catalogued craters, 63.2% of those ≥ 5 km and 87.4% of those ≥ 20 km, each far above a chance baseline (each set cut at the minimum diameter only where it is scored); recall levels off near half (52.4% at ≥ 5 km), and Robbins' degradation states show why: the freshest rims are found at 83.1% and the most degraded at 38.4%, fresh rims ≥ 10 km at 90–100%, and partial rims at 41.3% against 63.9% for full ones (KB §69.45, §69.47). Below ~5 km the density follows the DEM's makeup more than the craters (layout 11). Large craters are measured well: Perrotin within 7.1% in diameter.

[<img src="docs/thumbs/ius_crater_candidates.jpg" width="640" alt="Ius Chasma closed depressions, their size-frequency, and the Oudemans miss and Perrotin hit">](Mars%20Remote%20Sensing%20Project/build/interim_img/ius_crater_candidates.png)

*Ius Chasma: the 1,685 closed depressions ≥ 1 km (A) and their size-frequency (B); C and D, the detector on two named craters: Oudemans is breached into the canyon (its lowest rim point 33 m below its floor), so it is not a closed depression and is missed; Perrotin is found within 7.1% (KB §26).*

### Channels

`Fill` flooded Ius Chasma 2,077 m deep (21.7% of the type area raised by more than 1 m), and 56% of the stream cells in the first network were an artefact of it; of the 2,610 candidates left, 188 steep, rock-floored ones are worth digitising (layout 06). Across ±60°, 969,822 routed segments (layout 12); 89.8% lie on ground under 2°, so plateau channels are DEM noise. Scored against the global valley map of Alemanno & Orofino (A1, layout 19), 2.8% of the order ≥ 3 length lies within 5 km of a mapped valley, no better than the same valley map rotated in longitude (median 3.3%); only the largest trunks (10.3%) and the southern highlands (18.0% at 45–60°S) meet the valleys well, and 46% of the order ≥ 3 length lies from the equator to 30°N, where 0.1% does. The routed network is the DEM's drainage, not a valley map (KB §69.50).

[<img src="docs/thumbs/ius_channel_candidates.jpg" width="640" alt="Ius Chasma channel candidates by diurnal-contrast index, and the depth Fill added">](Mars%20Remote%20Sensing%20Project/build/interim_img/ius_channel_candidates.png)

*Ius Chasma. A: the 2,610 channel candidates, coloured by the diurnal-contrast index. B: where `Fill` raised the DEM, which is what the channel network had been routed across before the mask (KB §25.1).*

### The prospectus' hypotheses (T4–T7)

No band separates the geologic map's lava contacts or the 86 traced margins at Athabasca much better than chance (H1, at 1:20 M and on CTX, KB §69.52, §69.105; day IR's small lead survives removing topography, A9); the volcanic channel candidates are shallower than the fluvial ones and thermal response doesn't tell them apart (H2, stage 1), and the same holds over the whole ±60° network with origin taken from the valley map and the geologic map: order ≥ 2 segments on volcanic units have a median gradient of 2.4 m/km against 13.9 m/km on mapped valleys, and thermal Cohen's d is −0.21 (stage 1b, KB §69.50); the composite's Iso Cluster classes are the least reproducible input (H3); no channel threshold keeps first-order streams on real slopes, so the tributary order count is a setting, not a measurement (Q5).

<details>
<summary>The four charts</summary>

| T4 (H2): volcanic against fluvial channels | T5 (H1): flow margins in each band |
|---|---|
| [<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/t4_channels.png" alt="T4: channel gradient and AUC">](Mars%20Remote%20Sensing%20Project/build/interim_img/t4_channels.png) | [<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/t5_margins.png" alt="T5: share of lava-contact profiles each band separates">](Mars%20Remote%20Sensing%20Project/build/interim_img/t5_margins.png) |
| Median gradient per window, and how well gradient and thermal response tell the windows apart (0.5 = chance). | Share of 905 profiles across 10 `lAv` contacts each band separates; chance is 10%. |
| **T6 (H3): stability of each input** | **T7 (Q5): stream orders against the threshold** |
| [<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/t6_stability.png" alt="T6: stability and coherence per input">](Mars%20Remote%20Sensing%20Project/build/interim_img/t6_stability.png) | [<img src="Mars%20Remote%20Sensing%20Project/build/interim_img/t7_orders.png" alt="T7: highest Strahler order and first-order share on slopes">](Mars%20Remote%20Sensing%20Project/build/interim_img/t7_orders.png) |
| Agreement of maps trained on the west and east halves (ARI), and spatial coherence. | Highest Strahler order, and the share of first-order cells on slopes ≥ 2°, as the channel threshold changes. |

</details>

### Two earlier SVM maps, checked and superseded

Made in the Pro GUI: one follows its 4096-pixel processing tiles and scores below chance on its own training data; the other is mostly an elevation map (layout 05).

## Layouts

The 26 map sheets in the ArcGIS Pro project, grouped by what they show. Click one for the full sheet; [figures](docs/figures.md) gives each one's builder script and knowledge-base sections. The ±60° sheets, 08 included, are centred on 0°E; the type-area sheets are drawn on the mosaics' own grid, central meridian 180°.

**The data at ±60°**

| | |
|---|---|
| [![Layout 10: Where everything is: the analysis extent, the two type areas and the geologic map's volcanic units](docs/thumbs/10_global60_locator.jpg)](Mars%20Project/Global60/layouts/10_global60_locator.png) **10** · Where everything is: the analysis extent, the two type areas and the geologic map's volcanic units | [![Layout 08: The four inputs at ±60°: visible, day IR, night IR, topography](docs/thumbs/08_global60_mosaic.jpg)](Mars%20Project/Global60/layouts/08_global60_mosaic.png) **08** · The four inputs at ±60°: visible, day IR, night IR, topography |
| [![Layout 18: Where the THEMIS mosaics track thermal inertia, in 5° blocks (T3)](docs/thumbs/18_t3_tes_blocks.jpg)](Mars%20Project/Global60/layouts/18_t3_tes_blocks.png) **18** · Where the THEMIS mosaics track thermal inertia, in 5° blocks (T3) | |

**The two type areas**

| | | |
|---|---|---|
| [![Layout 01: Ius Chasma, visible (Viking colour)](docs/thumbs/01_visible.jpg)](Mars%20Project/TypeArea/layouts/01_visible.png) **01** · Ius Chasma, visible (Viking colour) | [![Layout 02: Ius Chasma, night-time thermal infrared](docs/thumbs/02_night_ir.jpg)](Mars%20Project/TypeArea/layouts/02_night_ir.png) **02** · Ius Chasma, night-time thermal infrared | [![Layout 15: Athabasca Valles in its four inputs, with the flood-lava unit lAv outlined](docs/thumbs/15_athabasca_type_area.jpg)](Mars%20Project/Global60/layouts/15_athabasca_type_area.png) **15** · Athabasca Valles in its four inputs, with the flood-lava unit `lAv` outlined |

**Classification**

| | |
|---|---|
| [![Layout 04: The published ±60° landform map, scored](docs/thumbs/04_global60_landforms.jpg)](Mars%20Project/Global60/layouts/04_global60_landforms.png) **04** · The published ±60° landform map, scored | [![Layout 13: The classes against the USGS geologic map (T8)](docs/thumbs/13_geomap_check.jpg)](Mars%20Project/Global60/layouts/13_geomap_check.png) **13** · The classes against the USGS geologic map (T8) |
| [![Layout 04b: The landform map in seven classes, scored](docs/thumbs/04b_global60_landforms_v2.jpg)](Mars%20Project/Global60/layouts/04b_global60_landforms_v2.png) **04b** · The landform map in seven classes, scored | [![Layout 13b: The seven classes against the USGS geologic map (T8)](docs/thumbs/13b_geomap_check_v2.jpg)](Mars%20Project/Global60/layouts/13b_geomap_check_v2.png) **13b** · The seven classes against the USGS geologic map (T8) |
| [![Layout 04c: The seven-class SVM map on the third label set](docs/thumbs/04c_global60_landforms_v3.jpg)](Mars%20Project/Global60/layouts/04c_global60_landforms_v3.png) **04c** · The seven-class SVM map on the third label set, a lead map | [![Layout 13c: The v3 maps against the geologic map](docs/thumbs/13c_geomap_check_v3.jpg)](Mars%20Project/Global60/layouts/13c_geomap_check_v3.png) **13c** · The v3 maps against the USGS geologic map (T8) |
| [![Layout 03: Ius Chasma, unsupervised (Iso Cluster, 10 classes)](docs/thumbs/03_classification.jpg)](Mars%20Project/TypeArea/layouts/03_classification.png) **03** · Ius Chasma, unsupervised (Iso Cluster, 10 classes) | [![Layout 05: The first two SVM maps, checked and superseded](docs/thumbs/05_svm_checks.jpg)](Mars%20Project/Global60/layouts/05_svm_checks.png) **05** · The first two SVM maps, checked and superseded |
| [![Layout 16: A deep-learning detector (X5), scored per held-out polygon](docs/thumbs/16_x5_detections.jpg)](Mars%20Project/Global60/layouts/16_x5_detections.png) **16** · A deep-learning detector (X5), scored per held-out polygon | [![Layout 17: Terrain provinces from a U-Net (X5c), beside the published SVM map](docs/thumbs/17_x5c_unet_provinces.jpg)](Mars%20Project/Global60/layouts/17_x5c_unet_provinces.png) **17** · Terrain provinces from a U-Net (X5c), beside the published SVM map |
| [![Layout 17b: Seven classes from a U-Net, beside the seven-class SVM](docs/thumbs/17b_unet_v2_provinces.jpg)](Mars%20Project/Global60/layouts/17b_unet_v2_provinces.png) **17b** · Seven classes from a U-Net, beside the seven-class SVM | [![Layout 17c: Seven classes from a U-Net on the third label set](docs/thumbs/17c_unet_v3_provinces.jpg)](Mars%20Project/Global60/layouts/17c_unet_v3_provinces.png) **17c** · Seven classes from a U-Net on the third label set, the lead map |
| [![Layout 20: The v3 seven-class labels](docs/thumbs/20_labels_v3.jpg)](Mars%20Project/Global60/layouts/20_labels_v3.png) **20** · The v3 seven-class labels, before their runs | |

**Craters and channels**

| | | |
|---|---|---|
| [![Layout 11: Closed depressions ≥ 1 km against the Robbins catalogue](docs/thumbs/11_global60_depressions.jpg)](Mars%20Project/Global60/layouts/11_global60_depressions.png) **11** · Closed depressions ≥ 1 km against the Robbins catalogue | [![Layout 07: Basin and crater candidates ≥ 20 km](docs/thumbs/07_global60_basins.jpg)](Mars%20Project/Global60/layouts/07_global60_basins.png) **07** · Basin and crater candidates ≥ 20 km | [![Layout 12: The channel network routed on the DEM, order ≥ 3](docs/thumbs/12_global60_channels.jpg)](Mars%20Project/Global60/layouts/12_global60_channels.png) **12** · The channel network routed on the DEM, order ≥ 3 |
| [![Layout 19: The routed channels against the mapped valleys (A1)](docs/thumbs/19_channels_vs_valleys.jpg)](Mars%20Project/Global60/layouts/19_channels_vs_valleys.png) **19** · The routed channels against the mapped valleys (A1) | | |

**Digitising and validation**

| | | |
|---|---|---|
| [![Layout 06: Ius Chasma, candidates to digitise](docs/thumbs/06_ius_digitising.jpg)](Mars%20Project/Global60/layouts/06_ius_digitising.png) **06** · Ius Chasma, candidates to digitise | [![Layout 09: Athabasca Valles, candidates to digitise](docs/thumbs/09_athabasca_digitising.jpg)](Mars%20Project/Global60/layouts/09_athabasca_digitising.png) **09** · Athabasca Valles, candidates to digitise | [![Layout 14: Validation: the candidates against review and the Robbins catalogue](docs/thumbs/14_validation.jpg)](Mars%20Project/Global60/layouts/14_validation.png) **14** · Validation: the candidates against review and the Robbins catalogue |

## Source data

Not in this repository: 62 GB, public. [`tools/check_remote.py`](tools/check_remote.py), run by hand, checks that each is still served at its address at the exact size the project drive holds. Put them at the root of the project drive.

| File | Size | Grid |
|---|---|---|
| [`Mars_Viking_MDIM21_ClrMosaic_global_232m.tif`](https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars_Viking_MDIM21_ClrMosaic_global_232m.tif) | 12.7 GB | 231.5 m, central meridian 0° |
| [`Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif`](https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif) | 22.8 GB | 100 m, central meridian 180° |
| [`Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif`](https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif) | 15.2 GB | 100 m, central meridian 180°, ±60° |
| [`Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif`](https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif) | 11.4 GB | 0.00337° geographic |

Neither imagery source is calibrated: the THEMIS mosaics are contrast-stretched region by region (KB §28.10), and the Viking mosaic's brightness, MDIM 2.1, was high-pass filtered at ~50 km to remove regional albedo and normalised so equal slopes show equal contrast, with an older colour mosaic blended over it "artistically" (USGS product pages; KB §69.50). The Viking bands therefore carry topographic shading as well as albedo.

The four files use three coordinate frames, so check `Central_Meridian` per file before reading a window, or THEMIS lands half a planet away. Their statistics sidecars (`.aux.xml`), the night mosaic's PDS label and MD5 are in [`drive-root/`](drive-root).

## Using the data

ArcGIS Pro is not required. The rasters are GeoTIFFs and the vectors come as a file geodatabase and a GeoPackage; QGIS and GDAL read all of them.

**Quick start.** Download the landform maps (1.9 GB; the published one unzips to `Global60/global60_landforms_svm_200m_mode11.tif`) and unzip them:

```bash
curl -LO https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/download/data-2026-11-10/global60-classification-part1.zip
unzip global60-classification-part1.zip
```

Then, with GDAL's Python bindings (`osgeo`, from conda-forge or the Python that ships with QGIS), read the map and turn a pixel into longitude and latitude:

```python
from osgeo import gdal
import numpy as np, math
gdal.UseExceptions()

ds = gdal.Open("Global60/global60_landforms_svm_200m_mode11.tif")  # 200 m, 106,694 x 35,565
band = ds.GetRasterBand(1)
# A tenth of the full resolution is plenty for an overview.
a = band.ReadAsArray(buf_xsize=ds.RasterXSize // 10, buf_ysize=ds.RasterYSize // 10)
names = {1: "Crater", 2: "steep/windy hills", 3: "lava tube", 4: "Normal Ground"}
valid = a != band.GetNoDataValue()                                  # 255: no class
for code, name in names.items():
    print(f"{name:18} {np.mean(a[valid] == code):6.1%}")

# Map coordinates are metres on the Mars sphere, central meridian 180°E.
R = 3396190.0
x0, dx, _, y0, _, dy = ds.GetGeoTransform()
def lonlat(col, row):
    x, y = x0 + (col + 0.5) * dx, y0 + (row + 0.5) * dy
    return 180 + math.degrees(x / R), math.degrees(y / R)           # longitude 0–360°E, latitude
```

It prints Crater 32.8%, steep/windy hills 1.8%, lava tube 9.3%, Normal Ground 56.1%, the same shares as a full-resolution count. `lonlat` agrees with PROJ's own transform to 10⁻¹³ degrees.

- **Coordinate system.** Almost everything is in `Mars_Equidistant_Cylindrical_CM180`: metres on the Mars sphere (R = 3,396,190 m) with the **central meridian at 180°**, so x runs 0–360°E. The CRS is embedded in each file; keep it. Reprojecting to an Earth CRS, or assuming a 0° meridian, puts features half a planet away. The exception is the 30 Sep SVM map, `Classified_202609300147338582853`: same projection, but **central meridian 0°**, on Viking's grid. The hand-drawn labels and the IAU nomenclature are in geographic `Mars_2000_(Sphere)`.
- **The four-class landform map** is `global60_landforms_svm_200m_mode11.tif` (the 400 m maps are its superseded predecessors). Its pixel values are the class codes: **1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground, 255 no class**, the same codes as the training labels; the attribute table adds names and colours. Read the lava tube class as unreliable (above). Every classified raster in the project follows the same rule: pixel value = class code.
- **The seven-class maps**, which the project leads with (D28), are `global60_landforms_svm_v2_200m_mode11.tif` (the SVM, layout 04b) and `global60_landforms_unet_v2_200m_seamfix.tif` (the U-Net, layout 17b), in [`global60-classification-part2.zip`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/download/data-2026-11-10/global60-classification-part2.zip) and [`-part3.zip`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/download/data-2026-11-10/global60-classification-part3.zip). Codes 1–4 as above, plus **5 volcanic edifice, 6 apron, 7 fluvial channel**. The `_v2p_` files beside them are a rehearsal of the pipeline, never a result.
- **The maps on the third label set**, which lead the final (D36), are `global60_landforms_unet_v3_200m_seamfix.tif` (the U-Net, layout 17c) and `global60_landforms_svm_v3_200m_mode11.tif` (the SVM, layout 04c), with the same codes 1–7, in [`global60-classification-part3.zip`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/download/data-2026-11-10/global60-classification-part3.zip) of [`data-2026-11-10`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/data-2026-11-10) (KB §69.105).
- **The training labels** are `Landform_TrainingSamples_terrain` in [`exports/`](exports/README.md), with the same class codes 1–4. One class schema in the project swaps 2 and 3; the layer catalogue says which.
- **What each raster is**, with its grid, data type, NoData and the release that holds it: [docs/rasters.md](docs/rasters.md).

## What is in this repository

The folders mirror the drive, so a path in the knowledge base (`<drive>\Mars Project\…`) maps directly onto one here.

```
Mars Remote Sensing Project/
  PROJECT-KNOWLEDGE.md     the authoritative record: data, traps, every result, open questions
  build/                   250 scripts: every raster product, figure, layout, audit and deliverable
    logs/                  run logs and the classification scores as JSON
  NEXT STUFF/              interim report and presentation; Final/: the AASTeX paper and the final deck (drafts)
  OLD/                     prospectus and Presentation 1 (delivered; the deck as PDF)
Mars Project/
  Mars Project.aprx        the ArcGIS Pro project: 45 maps, all Mars, and 26 layouts
  Global60/, TypeArea/,    metadata sidecars, models (.ecd), raster attribute tables, layouts;
  Athabasca/               Global60/checks/ holds the DEM step chips
  DLModels/                the twelve deep-learning models' metadata and training plots (the
                           weight files, 137-165 MB, are in the release's
                           dl-models-part*.zip and dl-models-rep.zip, data-2026-11-10)
  LabeledObjects/          deep-learning export metadata (the chips are in the release)
  GpMessages/, ImportLog/  Pro's own geoprocessing logs
  review_sheets/           the guides to the candidate review on contact sheets and to the off-Tharsis
                           labels, and the author's answer files (the sheets stay on the drive)
exports/
  mars_project_vectors.gdb every feature class in Mars Project.gdb, including the 512 hand-drawn
                           training polygons, the candidate layers and the digitised landforms
  README.md                the layer catalogue: rows, CRS, fields and what each layer is
docs/
  rasters.md               every backed-up raster: grid, type, NoData, what it is, which release
  backup.md                the release assets, keeping the backup current, restoring the drive
  scripts.md               every build script by purpose, with the Python it needs
  figures.md               every image in the tree: what it shows, its script, its KB section
  pipeline.svg             the diagram above
  thumbs/                  the 800 px previews these pages show; the full files are one click away
drive-root/                the source rasters' sidecars and the night mosaic's PDS label and MD5
restore.py                 rebuilds the drive from this repository and its releases
tools/check_repo.py        the checks CI runs on every push: page links, Python syntax, file sizes,
                           that the counts this page states match the tree, the figure index,
                           alt text, previews current with their sources, every number in the
                           interim, final deck and paper in the record, the stored scores
                           reproduced, every vector layer described, and the tests below
tools/test_score_metrics.py  hand-worked confusion matrices through the scoring arithmetic
                           (balanced accuracy, F1, quantity and allocation disagreement)
tools/make_thumbs.py       rebuilds docs/thumbs/ after a layout or figure changes (needs Pillow)
tools/check_remote.py      run by hand: release assets against their checksums, linked releases,
                           the source mosaics' addresses and sizes
.github/workflows/paper.yml  compiles the paper in TeX Live on every push that touches it; fails on
                           an undefined citation or reference; the PDF is the run's artifact
CITATION.cff               how to cite the project ("Cite this repository" on GitHub)
```

## Backup and restore

The rasters are in three releases: [`data-2026-11-10`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/data-2026-11-10) (13.3 GB: both type areas, Ius Chasma and Athabasca Valles, the ±60° landform maps with the U-Net maps, the seven-class maps and the two v3 maps that lead the final, the extra runs' window maps, the twelve trained deep-learning models, the GUI SVM maps, caches, the GeoPackage with the ±60° candidates and the seven-class and v3 labels; it replaces `data-2026-10-29`), [`derivatives-2026-10-06`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/derivatives-2026-10-06) (74.4 GB: the ±60° derivatives, split into 1.9 GB pieces, and the deep-learning exports) and [`derivatives-2026-11-11`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/derivatives-2026-11-11) (35.3 GB: the DEM, slope, aspect, hillshade and classification stack as patched at the 180° column, which replace their copies in the older release). [`restore.py`](restore.py) rebuilds the drive from a clone and those three releases, checking every file against its SHA-256:

```bash
python restore.py --dest E:\ --dry-run
```

[docs/backup.md](docs/backup.md) lists every release asset, how the backup is kept current from the drive, and what is not backed up; since rep's model and window maps were added on 11 November, nothing a restore needs is missing.

## License

- **Code** (the `.py` and `.ps1` scripts): [MIT](LICENSE).
- **Everything else made for this project**: the knowledge base, documents, figures, map layouts, the ArcGIS project file, the vector layers in `exports/` and the rasters in the releases are under [Creative Commons Attribution 4.0 International](LICENSE-CC-BY-4.0.txt) (CC BY 4.0). Use and adapt them freely, with credit:

  > Logan M Edwards (2026), *Mars Global Mosaic: Mapping Lava Flows, Fluvial Channels, and Impact Craters in Visible and Infrared*, https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data

- **Third-party data is not covered by either license** and keeps its producers' terms: the Viking MDIM 2.1 and HRSC/MOLA blended DEM distributed by USGS Astrogeology (the DEM blends HRSC data from DLR/ESA/FU Berlin with MOLA), the THEMIS mosaics from NASA's Mars Odyssey mission and Arizona State University, and the IAU/USGS Gazetteer of Planetary Nomenclature layers in `exports/`. The derived products carry CC BY 4.0 for this project's own contribution; credit the source missions too.
