# Interim report + presentation — plan

**The presentation is 10 November 2026** (D16, the author, 2026-10-27); the report's date is not given, so plan
it against the same day. The interim is the first deadline, about three weeks before the final on 8 December
(`NEXT-STEPS.md` §8). **Its data cut is 26 October (D20):** the content is set; what remains is the author's. § numbers point into `PROJECT-KNOWLEDGE.md` ("KB"), the authority on every number.

> The standing directive holds: data and layouts first, document prose only on request (KB §1). This file
> plans the interim; the text lives in `build\interim.py`.

---

## 0. The living deck — how it works

The Presentation 1 style with graphics, no fixed slide count, rebuilt as the data moves (decision D11). The
deck and the report are builds, never hand-edited:

```
<ArcGIS Pro Python> make_interim_figs.py          (desktop: D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe)
python make_interim_dark.py                       (the deck's navy copies of the charts and layouts)
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
- **`build\build_interim_live.py`** lays it out in `mars_theme.py` (since 2026-10-27, KB §69.11–§69.13: every slide navy,
  the charts and maps in navy-ground copies from `make_interim_dark.py`, over the Ius mosaic, Cambria and Calibri; `le_theme.py`, the Presentation 1 design, before): title, goals,
  spectral bands, the correlation matrix, tasks with progress bars, the processing log, a results divider with
  four headline numbers, one slide per figure, issues on two slides, next steps over a timeline. **31 slides; the report 21 pages, 21 figures** (2026-10-27, KB §69.9: nothing that reads as machine-made; 2026-10-26, KB §69.6: the text
  edited for plain wording, the failed first maps moved before the published one, the hypotheses in order H1, H2,
  H3, Q5). Earlier, 2026-10-21 (KB §66.10): the two
  deep-learning slides, layouts 16 and 17, each map left with takeaways and legend beside it, `map_left=True`).
- **After every rebuild:** back up the live files; render the deck with `render_pdf.ps1 -Deck <pptx> -Pdf <pdf>`
  from PowerShell and the report through Word COM (KB §51.5); rasterise with PyMuPDF and **read every changed slide
  and page**; then `verify_interim.py`, and check each new number by hand against its own section.
- **Known fits:** the log table holds 13 rows (a 14th overflows); a whole tall layout is unreadable on a slide, so draw
  a chart from its log (as for T8 and T1); titles over ~60 characters wrap onto the accent rule.

**Still to do on the deck** (none blocks a rebuild):
1. ~~Percentages~~ **set 2026-10-26** by the agent at the author's request, each row's progress toward the final
   (`PROGRESS` in `interim.py`; the reasoning in KB §69.5).
(The small legends on the 05 and 07 slides were enlarged on 2026-10-22, KB §67.5: 05 takes `map_left=True`,
07 a lower map cap, `map_h=230`.)

## 1. What exists

Everything is in `<drive>\Mars Remote Sensing Project\NEXT STUFF\`:

| file | built by |
|---|---|
| `Mars Global Mosaic - Interim Presentation.pptx` (30 slides) | `build_interim_live.py` + `interim.py` |
| `Mars Mosaic - Interim Report.docx` (21 pages) | `build_interim_report_live.py` + `interim.py` |
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
| 13 | Map layouts | 17 layouts, from none, with graticules (the deck shows 13 of them: not 03, 14, 15, and 13 as its table, §63, §66.10) | §44, §49, §53.6, §63, §66.4, §66.9, §66.10 |
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
8. **Deep learning**: the detector scored per held-out polygon (layout 16) and the U-Net's terrain provinces beside
   the published map (layout 17), one slide each. (§66.2, §66.9, §66.10)
9. **What is not done**: the review and digitising, lava flows mapped from the mosaic; the label audit (five
   Crater labels on volcanoes) and the seven-class scheme proposed for the final. (§68.2, §69.2, `NEXT-STEPS.md`)

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

## 6. Timeline to 10 November

The presentation is **10 November**. **The data cut is 26 October (D20, KB §69.5):** the interim covers what was measured by
then, and `interim.py` was brought to it and both documents rebuilt and read the same day. Results after the cut
go to the final, not here; slack goes to the final's data work.

| when | what |
|---|---|
| **26 Oct** | **interim data cut**; `interim.py` brought to it; 30 slides, 21 pages, `verify_interim.py` green (KB §69.5) |
| 26 Oct | the percentages (`PROGRESS`) set toward the final (KB §69.5); rebuilt, slide 5 and report page 2 read |
| 27 Oct | refined for the talk, the cut kept (the author's choice): T4 and T8 charts at 200 dpi, the U-Net slide's legend clear of its text, the title slide's subtitle, the schedule's 10 Nov; both rebuilt and the changed slides and pages read (KB §69.10) |
| before 10 Nov | any last change; rebuild both documents; render and read every changed slide and page; `verify_interim.py`; rehearsal |
| **10 Nov** | the presentation; the report as the course asks |

## 7. Wording traps, all hit before (KB §14.5, §12)

- **"Global"** → "±60°" or "the analysis extent" (§16.5).
- **"Thermal inertia"** → "diurnal contrast" or "relative thermal response"; the held products cannot give
  inertia (§24).
- **"Crater inventory"** → "closed depressions ≥ 1 km"; quote **68 %** for the large IAU craters, not 75 %
  (§26, §28.11).
- **Composite Bands failed four times on 9–13 Sep** (five with the 24 Sep cancel), not three (§8).
- **The SegmentMeanShift of 8 Sep (logged as 9 Sep) ran on the Mars DEM**, not Mercury (§14.5, defect 2).
- **The lava tube class is not a result** (§31.3). Don't show it as one.
- **The published map is the 200 m 11 × 11 one**; the 400 m 5 × 5 figures (73.5 %) are its predecessor (§57).
- Elevation is not a classification band; the corrected stack has none (§31.2).
