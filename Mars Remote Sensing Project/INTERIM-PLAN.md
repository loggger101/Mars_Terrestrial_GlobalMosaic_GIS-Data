# Interim report + presentation — plan

**Due mid-November 2026**; the exact day is **not known**, so plan against ~13 November and don't wait for
the date. The interim is the first deadline, about three weeks before the final on 8 December
(`NEXT-STEPS.md` §8). § numbers point into `PROJECT-KNOWLEDGE.md` ("KB"), the authority on every number.

> The standing directive holds: data and layouts first, document prose only on request (KB §1). This file
> plans the interim; the text lives in `build\interim.py`.

---

## 0. The living deck — how it works

The Presentation 1 style with graphics, no fixed slide count, rebuilt as the data moves (decision D11). The
deck and the report are builds, never hand-edited:

```
<ArcGIS Pro Python> make_interim_figs.py          (desktop: D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe)
python build_interim_live.py "..\NEXT STUFF\Mars Global Mosaic - Interim Presentation.pptx"
python build_interim_report_live.py "..\NEXT STUFF\Mars Mosaic - Interim Report.docx"
python verify_interim.py
```

- **`build\interim.py`** holds every word and number on the slides and in the report, each with its KB §. A new
  result is one entry in `FIGURES` (a layout or a figure file, 2–4 takeaways, the §); every number in it must be
  in the KB (`verify_interim.py` checks; it cannot check that a number sits beside the right claim, so check new
  numbers by hand, KB §48).
- **`build\make_interim_figs.py`** re-exports the layouts named in `FIGURES` at 200 dpi with the sheet's prose
  hidden (in memory, never saved) and trims them; a sheet with a legend also yields `__map` and `__legend`, so the
  map runs full width and the legend sits beside the takeaways. Charts come from their own scripts, drawn from
  the logs: `make_fig_ablation.py`, `make_fig_t1_pro.py`, `make_fig_t8.py`, `make_fig_t4.py`, `make_fig_tes.py`,
  `make_fig_tests567.py`.
- **`build\build_interim_live.py`** lays it out in `le_theme.py`: title, goals, spectral bands, the correlation
  table, tasks and percent complete, the processing log, a "Preliminary Results" divider, one slide per figure,
  issues, next steps with schedule. **28 slides; the report 20 pages, 19 figures** (2026-10-16, KB §57.3).
- **After every rebuild:** back up the live files, render (`render_pdf.ps1` for the deck, Word COM for the
  report), rasterise and **read every changed slide and page** (HANDOFF §5.5 has the commands and the known fits).

**Still to do on the deck** (none blocks a rebuild):
1. **Percentages** in the progress table: the author's to set (`PROGRESS` in `interim.py`); the slide shows
   13 Sep's next to a dash.
2. **The province figure quotes 54.4 DN** (`pres1_img\global60_thermal.png`, five boxes), while KB §28.10 and
   layout 08 quote **47.67 DN** (seven provinces). Both are real; the slide says "these five boxes". Regenerate
   one consistent, light-background version before the final.
3. **Legends are small** on the 05 and 07 slides; give them more room or a larger export.

## 1. What exists

Everything is in `<drive>\Mars Remote Sensing Project\NEXT STUFF\`:

| file | built by |
|---|---|
| `Mars Global Mosaic - Interim Presentation.pptx` (28 slides) | `build_interim_live.py` + `interim.py` |
| `Mars Mosaic - Interim Report.docx` (20 pages) | `build_interim_report_live.py` + `interim.py` |
| `2 Interim Presentation Template.pptx` | the course |

Earlier versions are kept on the drive in `NEXT STUFF\.backup_*` (not mirrored to GitHub).

## 2. What the template asks for

**The course asks for exactly the template's seven headings** (KB §39.2), and the report follows the same order:
Project Title · Project Investigators · Project Goals · Relevant Spectral Bands · List of Project Tasks and
Percent Complete · Preliminary Results (if available) · Project Issues and Hurdles. In `interim.py`: `TITLE`,
`AUTHOR`, `MISSION` / `GOALS`, `BANDS` / `CORRELATION`, `PROGRESS` / `LOG`, `FIGURES`, `ISSUES`, then
`NEXT_STEPS` / `SCHEDULE`.

## 3. The progress table — facts per row, percentages left open

| # | row | what is true on 2026-10-16 | KB |
|---|---|---|---|
| 1 | Scope, targets, type area | Ius Chasma and Athabasca Valles; the ±60° extent | §14.3, §16, §42.1 |
| 2 | Raster acquisition | three globals plus THEMIS Night IR (±60°) | §15 |
| 3 | Statistics, stretches, pyramids | done, the four source globals included (26 min) | §28, §29, §53.1 |
| 4 | Grouped mosaic viewer | done | — |
| 5 | DEM derivatives | degrees on a metric grid, type area and ±60°; the 180° column patched | §20, §28.8, §54 |
| 6 | Image-gradient products | renamed `Gradient_*`; not used further | §7 |
| 7 | Jezero context | hosted services only; the dead HiRISE link removed | §3, §50 |
| 8 | Classification | ±60° SVM on the hand-drawn labels, published at 200 m, 11 × 11: 73.8 %, κ 0.58 held out; T1 thermal +1.3 to +2.0 pt; T8 against the geologic map | §55.3, §56, §57 |
| 9 | CRS harmonisation | done: one 100 m / 200 m grid over ±60° | §18, §28.1 |
| 10 | Visible + IR composite | done: type areas; the 7-band ±60° stack | §18, §31.2 |
| 11 | Landform digitising | classes ready and **empty**; candidates reviewable; validation sheet ready; 512 training polygons drawn | §29.2, §46, §49 |
| 12 | Crater inventory | 465,354 closed depressions ≥ 1 km at ±60°, 15.3 % catalogued at ≥ 1 km, 62.2 % at ≥ 5 km; the Robbins catalogue (385,049) | §41, §53.4, §54.4 |
| 13 | Map layouts | 14 layouts, from none, with graticules | §44, §49, §53.6 |
| 14 | Report and presentations | Presentation 1 and the prospectus delivered; the interim deck and report are living builds | §1, §45, §57.3 |

## 4. The results the interim shows, each with its layout or figure

Ordered as a talk would run: data → method → result → limit. Every number is requoted from the KB, not from
this list (KB §12.1).

1. **One grid for four datasets**: the co-registration that failed four times works; layout 08. (§18, §28.1, §38)
2. **Thermal IR carries information visible light does not**: three Viking bands are one dimension, night IR the
   most independent band. (§18.3)
3. **…but only locally**: the province test, and TES thermal inertia tracks Viking, not the THEMIS pair.
   (§28.10, §42.4, §43.1)
4. **Craters**: basins ≥ 20 km (layout 07) and closed depressions ≥ 1 km across ±60° against Robbins (layout 11):
   prompts and a large-crater map, not a crater inventory. (§28.11, §53.4, §53.6)
5. **Channels**: the Fill trap at Ius (layout 06), the ±60° network and its blind spots (layout 12). (§25, §53.6)
6. **A scored classification**: the published 200 m map on blocks the model never saw (layout 04); the checks that
   caught the 29/30 Sep maps (layout 05). (§30–§32, §57)
7. **What the tests showed**: T1 thermal +1.3 to +2.0 pt with two classifiers, the classes are terrain classes;
   T8 against the geologic map; T2–T7. (§40.1, §42–§43, §47, §51, §56)
8. **What is not done**: the review and digitising, lava flows mapped from the mosaic, deep learning.
   (`NEXT-STEPS.md`)

## 5. Hypotheses and questions — where each stands

| | claim | status | what would settle it |
|---|---|---|---|
| **H1** | Day IR delineates flow boundaries under dust that Viking misses | **tested, not supported at 1:20 M** (T5, §47.2): day IR separates 21 % of lAv contact profiles, Viking red 12 %, chance 10 %; the difference's interval includes 0 | T5 again on lava margins digitised at Athabasca |
| **H2** | Fluvial channels have shallower gradients than volcanic ones, and the two separate on gradient vs thermal | **stage 1 not supported** (§51.1): by window the volcanic channels are shallower (median 1.4 against 10.2 m/km) and thermal response separates nothing (AUC 0.50); stage 2 waits for reviewed channels with `Origin` (§46) | the reviewed channels at Ius (fluvial) and Athabasca (volcanic) |
| **H3** | The 4-band composite gives more stable Iso Cluster classes than any single input | **not supported** (T6, §47.3): halves-trained ARI 0.40 against 0.61–0.89 for single inputs | — |
| **H4** | Crater rims from DN gradient recover most of the 141 IAU craters > 100 km | **answered with a different method**: fill depth, 68 % of 117 inside ±58° (§28.11) | report the method change honestly |
| Q1 | Does projecting the DEM change slope enough to matter? | **answered**: yes (§7, §20) | — |
| Q2 | Does Composite Bands complete globally once harmonised? | **answered**: bounded, 8.8 s; the GUI global runs 2 h 52 m and 3 h 10 m (§18, §29.1) | — |
| Q3 | How much does 8-bit depth limit separation? | **overtaken**: local normalisation is the bigger limit (§28.10) | — |
| Q4 | Is day IR enough, or is night IR needed? | **answered**: night IR is the most independent band (§18.3) | — |
| Q5 | How many tributary orders are recoverable at 100 m? | **answered** (T7, §47.4): none the DEM supports | — |
| Q6 | Does DN gradient reveal unit boundaries beyond the source image? | **unexamined** | low priority; say so |

## 6. Timeline to mid-November

Assumes **~13 November**; if the date is later, the slack goes to data work, not to the documents.

| when | what |
|---|---|
| now → 1 Nov | data work per `NEXT-STEPS.md`; **rebuild after every result** (§0) |
| **by 2 Nov** | **interim data cut**: what is measured goes in; everything after goes to the final |
| 2–6 Nov | finish `interim.py`; the author sets the percentages |
| 6–9 Nov | rebuild both documents; render and read every slide and page; `verify_interim.py` green |
| 9–12 Nov | review and rehearsal |
| mid-Nov | deliver |

## 7. Wording traps, all hit before (KB §14.5, §12)

- **"Global"** → "±60°" or "the analysis extent" (§16.5).
- **"Thermal inertia"** → "diurnal contrast" or "relative thermal response"; the held products cannot give
  inertia (§24). §19.3 and §18.4 of the record still use the old word in places.
- **"Crater inventory"** → "closed depressions ≥ 1 km"; quote **68 %** for the large IAU craters, not 75 %
  (§26, §28.11).
- **Composite Bands failed four times on 9–13 Sep** (five with the 24 Sep cancel), not three (§8).
- **The SegmentMeanShift of 9 Sep ran on the Mars DEM**, not Mercury (§14.5 #3).
- **The lava tube class is not a result** (§31.3). Don't show it as one.
- **The published map is the 200 m 11 × 11 one**; the 400 m 5 × 5 figures (73.5 %) are its predecessor (§57).
- Elevation is not a classification band; the corrected stack has none (§31.2).
