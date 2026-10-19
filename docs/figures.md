# Figures

Every image in this repository: what it shows, the script that makes it and the knowledge-base section behind it.
Click a thumbnail for the full-size file. "KB §N" is a section of
[`PROJECT-KNOWLEDGE.md`](../Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md); scripts are in
[`build/`](../Mars%20Remote%20Sensing%20Project/build) and described in [scripts.md](scripts.md).

- [Map layouts](#map-layouts): the 15 sheets in the ArcGIS Pro project, exported at 150 dpi
- [Result charts](#result-charts): the tests, drawn from their logs
- [Check images](#check-images): the DEM steps found by the stack's line sweep
- [Interim crops](#interim-crops): the layouts as the interim deck uses them
- [Other](#other)

The ±60° sheets (04, 05, 07, 10–13) are drawn in geographic Mars 2000 coordinates with 0°E at the centre; 08 and the
type-area sheets (01–03, 06, 09, 14, 15) are equidistant cylindrical on the Mars sphere, central meridian 180°, the
mosaics' own grid. The analysis extent is ±60° latitude, the coverage of the THEMIS night mosaic.

## Map layouts

The layouts live in `Mars Project.aprx`. Each builder wipes and rebuilds its own maps, then
[`polish_layouts.py`](../Mars%20Remote%20Sensing%20Project/build/polish_layouts.py) applies the presentation fixes and
exports every sheet; the PNGs here are the polished exports.

### The data

| | Sheet | Built by |
|---|---|---|
| <a href="../Mars%20Project/Global60/layouts/10_global60_locator.png"><img src="../Mars%20Project/Global60/layouts/10_global60_locator.png" width="300"></a> | **10 · The analysis extent and the two type areas.** Ius Chasma and Athabasca Valles on the Viking colour mosaic, with the volcanic units of the USGS geologic map (SIM 3292), the project's lava-flow reference. KB §44. | `make_reference_maps.py` |
| <a href="../Mars%20Project/Global60/layouts/08_global60_mosaic.png"><img src="../Mars%20Project/Global60/layouts/08_global60_mosaic.png" width="300"></a> | **08 · The four inputs at ±60°.** Viking colour, THEMIS day IR, THEMIS night IR and the HRSC/MOLA topography, each on the same grid. Black streaks in the south: no THEMIS coverage. KB §38. | `make_mosaic_layout.py` |
| <a href="../Mars%20Project/TypeArea/layouts/01_visible.png"><img src="../Mars%20Project/TypeArea/layouts/01_visible.png" width="300"></a> | **01 · Ius Chasma, visible.** Viking MDIM 2.1 resampled to the type area's 100 m grid. KB §18, §22. | `make_typearea_layouts.py` |
| <a href="../Mars%20Project/TypeArea/layouts/02_night_ir.png"><img src="../Mars%20Project/TypeArea/layouts/02_night_ir.png" width="300"></a> | **02 · Ius Chasma, night-time thermal infrared.** THEMIS Night IR v14. Bright is warmer at night than the surroundings: local contrast, not calibrated thermal inertia. KB §22, §28.10. | `make_typearea_layouts.py` |
| <a href="../Mars%20Project/Global60/layouts/15_athabasca_type_area.png"><img src="../Mars%20Project/Global60/layouts/15_athabasca_type_area.png" width="300"></a> | **15 · Athabasca Valles, the four inputs.** Viking colour, THEMIS night and day IR, and the DEM over its hillshade at 100 m, with the geologic map's flood-lava unit `lAv` outlined on each; captions give each band's correlations and the T2 and T5 results there. KB §42, §47.2, §63. | `make_athabasca_layout.py` |

### Classification

| | Sheet | Built by |
|---|---|---|
| <a href="../Mars%20Project/Global60/layouts/04_global60_landforms.png"><img src="../Mars%20Project/Global60/layouts/04_global60_landforms.png" width="300"></a> | **04 · The published ±60° landform map.** A support vector machine on the 512 hand-drawn labels, 200 m, 11 × 11 majority filter; scored on 183 held-out polygons: 73.8 %, κ 0.58. KB §31, §55.3, §57. | `make_global60_maps.py --cell 200` |
| <a href="../Mars%20Project/Global60/layouts/13_geomap_check.png"><img src="../Mars%20Project/Global60/layouts/13_geomap_check.png" width="300"></a> | **13 · The classes against the USGS geologic map (test T8).** How strongly each class gathers on each unit group: an association, not an accuracy. KB §43.2, §57.1. | `make_geomap_sheet.py --cell 200` |
| <a href="../Mars%20Project/TypeArea/layouts/03_classification.png"><img src="../Mars%20Project/TypeArea/layouts/03_classification.png" width="300"></a> | **03 · Ius Chasma, unsupervised classification.** Iso Cluster, 10 classes, on the five-band stack. KB §19, §22. | `make_typearea_layouts.py` |
| <a href="../Mars%20Project/Global60/layouts/05_svm_checks.png"><img src="../Mars%20Project/Global60/layouts/05_svm_checks.png" width="300"></a> | **05 · The first two SVM maps, checked and superseded.** The 29 Sep map follows its 4096-pixel tiles; the 30 Sep map is mostly elevation. KB §30, §31.1. | `make_global60_maps.py` |

### Craters and channels

| | Sheet | Built by |
|---|---|---|
| <a href="../Mars%20Project/Global60/layouts/11_global60_depressions.png"><img src="../Mars%20Project/Global60/layouts/11_global60_depressions.png" width="300"></a> | **11 · Closed depressions ≥ 1 km against the Robbins catalogue.** 465,354 depressions per 0.5° cell beside the catalogue's density, and the match rate by diameter. Below ~5 km the density follows the DEM's makeup. KB §53.4, §53.6, §54.4. | `make_global60_candidate_sheets.py` |
| <a href="../Mars%20Project/Global60/layouts/07_global60_basins.png"><img src="../Mars%20Project/Global60/layouts/07_global60_basins.png" width="300"></a> | **07 · Basin and crater candidates ≥ 20 km.** 5,144 closed depressions, sized by diameter, with the IAU named craters over 100 km. KB §28.11, §32.1. | `make_candidate_maps.py` |
| <a href="../Mars%20Project/Global60/layouts/12_global60_channels.png"><img src="../Mars%20Project/Global60/layouts/12_global60_channels.png" width="300"></a> | **12 · The channel network routed on the DEM, Strahler order ≥ 3.** 969,822 segments in all; routed flow paths, not mapped valleys. KB §53.4, §53.6, §55.4. | `make_global60_candidate_sheets.py` |

### Digitising and validation

| | Sheet | Built by |
|---|---|---|
| <a href="../Mars%20Project/Global60/layouts/06_ius_digitising.png"><img src="../Mars%20Project/Global60/layouts/06_ius_digitising.png" width="300"></a> | **06 · Ius Chasma, candidates to digitise.** The 188 steep, rock-floored channel candidates and 1,685 closed depressions, over the hillshade. KB §25, §32.1. | `make_candidate_maps.py` |
| <a href="../Mars%20Project/Global60/layouts/09_athabasca_digitising.png"><img src="../Mars%20Project/Global60/layouts/09_athabasca_digitising.png" width="300"></a> | **09 · Athabasca Valles, candidates to digitise.** 409 rock-floored channel candidates and 1,709 closed depressions on the flood lava. KB §42.1. | `make_candidate_maps.py` |
| <a href="../Mars%20Project/Global60/layouts/14_validation.png"><img src="../Mars%20Project/Global60/layouts/14_validation.png" width="300"></a> | **14 · Validation.** The candidates against the review (accept, reject, unsure) and the Robbins catalogue; the table fills in as the review proceeds. KB §46, §49. | `make_validation_sheet.py` |

## Result charts

Drawn from the tests' JSON logs in [`build/logs/`](../Mars%20Remote%20Sensing%20Project/build/logs) (the province chart
from the KB's own §28.10 tables), never retyped. They are the interim deck's figures, in
[`build/interim_img/`](../Mars%20Remote%20Sensing%20Project/build/interim_img) (the province chart in
[`build/pres1_img/`](../Mars%20Remote%20Sensing%20Project/build/pres1_img)).

| | What it shows | Made by · log |
|---|---|---|
| <a href="../Mars%20Remote%20Sensing%20Project/build/interim_img/t1_pro.png"><img src="../Mars%20Remote%20Sensing%20Project/build/interim_img/t1_pro.png" width="300"></a> | **T1 in ArcGIS Pro: what each band group adds.** Held-out accuracy of the full stack minus the stack without the group, with a paired-bootstrap 95 % interval. The thermal bands add 1.36 points at 200 m and 1.97 at 400 m, both resolved. KB §56, §56.1. | `make_fig_t1_pro.py` · `t1_bootstrap_*.json` |
| <a href="../Mars%20Remote%20Sensing%20Project/build/interim_img/thermal_ablation.png"><img src="../Mars%20Remote%20Sensing%20Project/build/interim_img/thermal_ablation.png" width="300"></a> | **T1 with a numpy classifier: held-out accuracy by band set**, against the 58.6 % of one class everywhere. Every set that includes slope and relief clears it; the spectral bands alone do not. KB §40.1. | `make_fig_ablation.py` · `thermal_ablation.json` |
| <a href="../Mars%20Remote%20Sensing%20Project/build/interim_img/tes_check.png"><img src="../Mars%20Remote%20Sensing%20Project/build/interim_img/tes_check.png" width="300"></a> | **T3: which layer tracks calibrated thermal inertia (TES)?** Correlation across ±60° and within 15° blocks. Viking red does (r −0.36); the THEMIS pair keeps only a weak local signal. KB §42.4, §43.1. | `make_fig_tes.py` · `tes_global_check.json` |
| <a href="../Mars%20Remote%20Sensing%20Project/build/pres1_img/global60_thermal.png"><img src="../Mars%20Remote%20Sensing%20Project/build/pres1_img/global60_thermal.png" width="300"></a> | **Can the day–night pair tell material apart across ±60°?** A: the diurnal-contrast index over seven provinces, dusty against rocky −0.0009 with scatter of 0.13–0.23 inside each. B: day IR, night IR and Viking red over the four provinces with tabulated DN; every province repeats the THEMIS mosaic-wide mean and spread, and Viking separates dusty from rocky by 47.67 DN, the THEMIS pair by −0.19 and +0.02. KB §28.10, §62. | `make_fig_global60.py` · KB §28.10's tables, parsed at run time |
| <a href="../Mars%20Remote%20Sensing%20Project/build/interim_img/t8_enrichment.png"><img src="../Mars%20Remote%20Sensing%20Project/build/interim_img/t8_enrichment.png" width="300"></a> | **T8: each class's enrichment on each geologic unit group**, P(class \| group) ÷ P(class). Layout 13's table, legible at slide size. KB §43.2, §57.1. | `make_fig_t8.py` · `geomap_check.json` |
| <a href="../Mars%20Remote%20Sensing%20Project/build/interim_img/t4_channels.png"><img src="../Mars%20Remote%20Sensing%20Project/build/interim_img/t4_channels.png" width="300"></a> | **T4 (H2, stage 1): volcanic against fluvial channels.** The Athabasca candidates are shallower than Ius's, and thermal response does not tell the two windows apart (AUC 0.50). KB §51.1. | `make_fig_t4.py` · `t4_channel_h2.json` |
| <a href="../Mars%20Remote%20Sensing%20Project/build/interim_img/t5_margins.png"><img src="../Mars%20Remote%20Sensing%20Project/build/interim_img/t5_margins.png" width="300"></a> | **T5 (H1): does IR show lava-flow margins?** The share of 905 profiles across the geologic map's `lAv` contacts that each band separates; every interval reaches chance. KB §47.2. | `make_fig_tests567.py` · `t5_flow_margins.json` |
| <a href="../Mars%20Remote%20Sensing%20Project/build/interim_img/t6_stability.png"><img src="../Mars%20Remote%20Sensing%20Project/build/interim_img/t6_stability.png" width="300"></a> | **T6 (H3): is the composite more stable than one input?** Agreement of west- and east-trained maps (ARI) and spatial coherence; the composites are the least reproducible. KB §47.3. | `make_fig_tests567.py` · `t6_composite_stability.json` |
| <a href="../Mars%20Remote%20Sensing%20Project/build/interim_img/t7_orders.png"><img src="../Mars%20Remote%20Sensing%20Project/build/interim_img/t7_orders.png" width="300"></a> | **T7 (Q5): how many stream orders does the DEM resolve?** The highest order falls with the channel threshold, and no threshold puts half the first-order cells on real slopes: the count is a setting. KB §47.4. | `make_fig_tests567.py` · `t7_order_sweep.json` |

## Check images

[`Mars Project/Global60/checks/dem_step_chips_20261015/`](../Mars%20Project/Global60/checks/dem_step_chips_20261015):
image chips at each line in the DEM that the sweep of the 7-band stack flagged (steps 2.2–4× the local roughness, ~500 km
long). 297.5°E is a real escarpment; the others are seams and smoothed gap-fill strips in the HRSC/MOLA blend, not fixable
in this project. `180E_col53346_after_fix` shows the 180° column after its patch. KB §54, §55.2.

| | | |
|---|---|---|
| <a href="../Mars%20Project/Global60/checks/dem_step_chips_20261015/180E_col53346_after_fix.png"><img src="../Mars%20Project/Global60/checks/dem_step_chips_20261015/180E_col53346_after_fix.png" width="250"></a><br>180°E, after the fix | <a href="../Mars%20Project/Global60/checks/dem_step_chips_20261015/297.5E_col88163.png"><img src="../Mars%20Project/Global60/checks/dem_step_chips_20261015/297.5E_col88163.png" width="250"></a><br>297.5°E, a real escarpment | <a href="../Mars%20Project/Global60/checks/dem_step_chips_20261015/304.4E_col90211.png"><img src="../Mars%20Project/Global60/checks/dem_step_chips_20261015/304.4E_col90211.png" width="250"></a><br>304.4°E, a seam |
| <a href="../Mars%20Project/Global60/checks/dem_step_chips_20261015/345.8E_col102499_a.png"><img src="../Mars%20Project/Global60/checks/dem_step_chips_20261015/345.8E_col102499_a.png" width="250"></a><br>345.8°E (a), a seam | <a href="../Mars%20Project/Global60/checks/dem_step_chips_20261015/345.8E_col102499_b.png"><img src="../Mars%20Project/Global60/checks/dem_step_chips_20261015/345.8E_col102499_b.png" width="250"></a><br>345.8°E (b), a seam | <a href="../Mars%20Project/Global60/checks/dem_step_chips_20261015/61.9E_col18333.png"><img src="../Mars%20Project/Global60/checks/dem_step_chips_20261015/61.9E_col18333.png" width="250"></a><br>61.9°E, a seam |
| <a href="../Mars%20Project/Global60/checks/dem_step_chips_20261015/15.0S_row22230.png"><img src="../Mars%20Project/Global60/checks/dem_step_chips_20261015/15.0S_row22230.png" width="250"></a><br>15.0°S (a row), a seam | | |

## Interim crops

[`build/interim_img/`](../Mars%20Remote%20Sensing%20Project/build/interim_img) also holds each layout the interim deck
shows, exported at 200 dpi with the sheet's own prose hidden by
[`make_interim_figs.py`](../Mars%20Remote%20Sensing%20Project/build/make_interim_figs.py). A sheet with a legend yields
three files: the whole sheet, `__map` (the map alone, full width on the slide) and `__legend`. They are the same maps as
the layouts above.

## Other

| | What it shows | Made by |
|---|---|---|
| [`pipeline.svg`](pipeline.svg) | The pipeline diagram on the front page. | by hand |
| [`OLD/ocean first pres LE.pdf`](../Mars%20Remote%20Sensing%20Project/OLD/ocean%20first%20pres%20LE.pdf) | Presentation 1 as delivered (history, not corrected). KB §14.5. | — |
