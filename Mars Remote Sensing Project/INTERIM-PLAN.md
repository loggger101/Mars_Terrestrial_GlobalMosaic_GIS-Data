# Interim report + presentation — plan

**Due mid-November 2026.** The exact day is **not known** (confirmed
2026-10-08), so plan against the early end of "mid-November" and don't wait for the date.
That makes the interim the **first** deadline, about three weeks before the final on 8 December,
and it changes the schedule in `NEXT-STEPS.md` §6. Written 2026-10-08 from `content.py`, the two
drafts in `NEXT STUFF\` and `PROJECT-KNOWLEDGE.md` (§ numbers point there).

> The standing directive still holds: data and layouts first, document prose only on request
> (KB §1). This file plans the interim. It does not draft it. Drafting starts on the date in §6
> below, or earlier on request.

---

## 0. The living deck — how it works now (decided 2026-10-08)

**Open decision: the Presentation 1 style with graphics, no fixed slide count; the interim "is dynamic and will
likely change largely as we gather and process the task data."** So the deck is a build, not a
file to edit:

```
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" make_interim_figs.py
python build_interim_live.py "..\NEXT STUFF\Mars Global Mosaic - Interim Presentation.pptx"
```

- **`build\interim.py`** holds every word and number on the slides, each with its KB §. A new
  result is one entry in `FIGURES` (a layout or a figure file, 2–4 takeaways, the §).
- **`build\make_interim_figs.py`** re-exports the layouts from the project at 200 dpi with the
  sheet's prose hidden (in memory, never saved) and trims them, so slides show the maps, not
  shrunken captions. A sheet with a legend also yields `__map` and `__legend`, so the map runs full
  width and the legend sits beside the takeaways.
- **`build\build_interim_live.py`** lays it out in `le_theme.py` (the Presentation 1 design):
  title, goals, spectral bands, the correlation table, tasks and percent complete, the processing
  log, a "Preliminary Results" divider, one slide per figure, issues, next steps with schedule.
  25 slides since the 2026-10-09 rebuild (T8 table and T4, KB §51; report 17 pages, 16 figures); 23 after
  the T5–T7 rebuild (KB §48); the count follows `FIGURES`. The
  report (`build_interim_report_live.py`) keeps each figure, its takeaways and its source on one page.
- The 13 Sep deck is kept in `NEXT STUFF\.backup_20261008\`. `build_interim_le.py` (the September
  builder, from `content.py`) is untouched.
- **After any rebuild:** render (`render_pdf.ps1`), rasterise (`pdf_pages.py`) and read every
  slide; it is how the shrunken-sheet and the "The hand-drawn labels" legend problems were caught.
- **Slide text is written in a neutral voice.** Layer names inside the project now read
  "Hand-drawn labels" (`build\fix_label_names.py`), because the legends show them.

**Still to do on the deck** (none blocks a rebuild):
1. **Percentages** in the progress table: the author's to set (`PROGRESS` in `interim.py`); the slide shows
   13 Sep's next to a dash.
2. **Legends are small** on the 05 and 07 slides; give them more room or a larger export.
3. **The province figure quotes 54.4 DN** (`pres1_img\global60_thermal.png`, five boxes), while
   KB §28.10 and layout 08 quote **47.67 DN** (seven provinces). Both are real; the slide quotes the
   figure's own number and says "these five boxes". Regenerate one consistent version before the
   final, light-background to match the deck.
4. ~~Done 2026-10-08 (KB §40.3).~~ **`pres1_img\ius_fusion.png` said "thermal-inertia proxy"** and "low/high inertia" on the
   image; fix `make_fig_fusion.py` wording before it goes on a slide.
5. ~~A locator slide; the T1 result.~~ **Done 2026-10-08:** layout 10 opens the results; T1, T3 and
   T5–T7 each have a chart slide (KB §44, §45, §48).
6. ~~Done 2026-10-08 (KB §45): `verify_interim.py`.~~ **`verify_all.py` checks `content.py`, not `interim.py`.** Add a check that every number in
   `interim.py` still matches the record before the interim is delivered.
7. ~~Done 2026-10-08 (KB §45): `build_interim_report_live.py`.~~ The **report** (`build_interim_docx.py`) read the September `content.py` and has no
   figures; switch it to `interim.py` and the same images when the deck settles.

## 1. What exists, and how old it is

Everything is in **`Z:\Mars Remote Sensing Project\NEXT STUFF\`**:

| file | dated | built by |
|---|---|---|
| `2 Interim Presentation Template.pptx` | put there 8 Oct | the course |
| `Mars Global Mosaic - Interim Presentation.pptx` | **8 Oct**, living (§0) | `build_interim_live.py` + `interim.py` |
| `.backup_20261008\` | 13 Sep | the September deck, from `build_interim_le.py` |
| `Mars Mosaic - Interim Report.docx` | **8 Oct**, living (KB §45) | `build_interim_report_live.py` + `interim.py`; 11 figures |
| `.backup_20260918\` | 18 Sep | copies of both, before the 18 Sep rebuild |
| `build\content.py` (the September prose) | 18 Sep | superseded by `interim.py` for both documents |

Both documents are generated, never hand-edited (KB §17, deck pipeline). **Every section of
`content.py` that the interim uses is stale**: it describes the project as it was before
CRS harmonisation, the night mosaic, the ±60° extent, any classification on Mars, the hand-drawn labels and
every layout. The interim must be rebuilt from the current record, not patched.

**What the course asks for is exactly the template's seven headings** (KB §39.2): Project Title,
Project Investigators, Project Goals; Relevant Spectral Bands, List of Project Tasks and Percent
Complete, Preliminary Results (if available), Project issues and Hurdles. The report mirrors the
same order.

**The deck is not blocked** (KB §21.4 was wrong, corrected in §39.2). Two builders, both test-built
2026-10-08 into scratch and rendered:

| builder | slides | look | needs |
|---|---|---|---|
| `build_interim_le.py <out>` | 12 | the Presentation 1 design (navy/cyan, `le_theme.py`) | nothing |
| `build_interim_deck.py <template> <out>` | 11 | the course template: its banner, lavender background, its headings kept | the template, now on `Z:` |

**Decided 2026-10-08: the Presentation 1 style** (D11), now as the living deck of §0.

**The biggest gap was: no maps.** Neither the September deck nor the report had a single figure,
while eight layouts existed. **Closed 2026-10-08:** the deck has 20 slides with the maps and the T1 and
T3 charts, and the report 11 figures, both from `interim.py` (KB §45); 12 layouts exist (§44, §49; the deck still says 10 until its next rebuild). *Preliminary Results* should be mostly sheets (§4 below). `le_theme.py` has the
picture helpers Presentation 1 used; `build_interim_deck.py` and `build_interim_docx.py` need one
added (python-pptx `add_picture`, python-docx `add_picture`). Export the sheets at 200 dpi for the
deck so text on them stays legible when projected.

## 2. What the template asks for, and how stale each part is

The interim follows the course template's section order (`build_interim_docx.py` docstring). Old
content → what is true now:

| section (`content.py`) | old claim (13–18 Sep) | now | KB |
|---|---|---|---|
| `GOALS_SHORT` | "one co-registered **global** mosaic" | ±60° by decision; say so | §16 |
| | accuracy "against the USGS global geologic map" | **on disk since 2026-10-08** and measured (T8): the classes are terrain classes, not geologic units | §41, §43.2 |
| `PROGRESS` (14 rows, %) | ~42 % overall | most rows moved; table in §3 below. **The percentages are the author's to set.** | — |
| `PRELIM` | 3 rasters loaded; z-factor broken; Mercury rehearsal; "not yet applied to Mars" | all superseded: see the results list in §4 | §18–§38 |
| `ISSUES` | 3 CRS frames; z-factor; composite fails; no GPU; no night IR; gazetteer; dead refs; duplicates | **solved**: CRS (§18, §28.1), z-factor (§20), composite (§18, §29, §31.2), night IR (§15), dead refs except HiRISE (§37). **Still open**: GPU (q10), duplicates (q4) | — |
| | — | **new issues to report** (lead with the measured limits, D12): the thermal bands add +1.3 pt (§40.1); the index does not track calibrated thermal inertia at 3 km (§42.4, §43.1); closed depressions are 11–13 % catalogued craters at ≥ 1 km (§42.3); THEMIS mosaics locally normalised (§28.10); lava tube class unusable, lava flows shown from the geologic map (§31.3, §43.3, §44); the 29/30 Sep GUI SVM maps (§30); the USB drive's dropouts and I/O ceiling (§2.2, §36.4); laptop sleep inflating timings (§28.9); class-schema clash (q23) | |
| `NEXT_STEPS` | "project to one frame", "retry Composite Bands", "download night IR"… | all done; replace with `NEXT-STEPS.md` §3–§5 | — |
| `WORKFLOW_LOG` | 8–13 Sep runs | add the 24 Sep – 1 Oct GUI runs (§29.1) and the scripted runs since | §29 |
| `SCHEDULE` | interim in weeks 7–8 (5–16 Oct) | interim mid-Nov; final 8 Dec. Re-cut from `NEXT-STEPS.md` §6 | — |

## 3. The progress table — facts per row, percentages left open

| # | row (as in the interim) | what is true on 2026-10-08 | KB |
|---|---|---|---|
| 1 | Scope, targets, type area | Ius Chasma set; ±60° extent decided; **Athabasca Valles built as the second type area** (layout 09) | §14.3, §16, §42.1 |
| 2 | Raster acquisition | three globals **plus THEMIS Night IR** (±60°) | §15 |
| 3 | Statistics and stretches; pyramids | statistics on all; overviews on every ±60° product and the GUI composites; **the four source globals still have none** | §28, §29 |
| 4 | Grouped mosaic viewer | done | — |
| 5 | DEM derivatives | rebuilt in degrees on a metric grid, WARNING 000869 gone, type area and ±60° | §20, §28.8 |
| 6 | Image-gradient products | renamed `Gradient_*` manually; not used further | §7 |
| 7 | Jezero context | unchanged: hosted services only, HiRISE link dead | §3 |
| 8 | Classification | Iso Cluster on Mars; supervised on terrain labels 62.7 %; the two GUI SVMs checked and found wanting; corrected ±60° SVM **73.5 %, κ 0.58 held out**; thermal ablation T1 (+1.3 pt); scored against the geologic map, T8 | §19, §27, §30–§32, §40.1, §43.2 |
| 9 | CRS harmonisation | **done**: type area at 100 m; ±60° on G100/G200 | §18, §28.1 |
| 10 | Visible + IR composite | **done**: type area 8.8 s; the two GUI global composites; the corrected 7-band ±60° stack | §18, §29, §31.2 |
| 11 | Landform digitising | classes exist and are **empty**; 512 training polygons drawn manually; candidates seeded at both type areas; **review fields and `accept_reviewed.py` ready** | §19.4, §25, §29.2, §46 |
| 12 | Crater inventory | 1,685 closed depressions ≥ 1 km at Ius (1,709 at Athabasca), 11–13 % of them catalogued craters; the Robbins catalogue in the project (385,049); 5,144 basins ≥ 20 km at ±60°, 68 % recall on IAU ≥ 100 km | §26, §28.11, §41, §42.3 |
| 13 | Map layouts | **12 layouts**, from 0, with graticules; 13 (T8) and 14 (validation) added after the deck was built | §22, §31–§33, §38, §42.1, §44, §49 |
| 14 | Report and presentations | Pres 1 and prospectus delivered; interim deck and report are living builds, rebuilt after each result | §1, §39.3, §45 |

## 4. The results the interim can show, each with its layout or figure

Ordered as a talk would run: data → method → result → limit.

1. **One grid for four datasets** — the co-registration that failed four times now works; layout 08
   shows the mosaic. (§18, §28.1, §38)
2. **Thermal IR carries information visible light does not** — three Viking bands are one
   dimension (r 0.93–0.99); night IR is the most independent band (|r| ≤ 0.12). (§18.3)
3. **…but only locally** — the province test: Syrtis Major and Arabia Terra are indistinguishable
   in the THEMIS mosaics, 47.7 DN apart in Viking. The most important limit of the project, and
   an honest result. (§28.10)
4. **Terrain done right** — slope in degrees; the z-factor defect gone. (§20)
5. **Craters from fill depth** — Perrotin within 7.1 %; Oudemans missed because it is breached;
   68 % of large IAU craters recovered at ±60°. Show the miss. (§26, §28.11, layout 07)
6. **Channels, and the Fill trap** — Fill raised Ius Chasma 2,077 m; 56 % of the first network was
   artefact; 188 steep, rock-floored candidates. (§25, layout 06)
7. **The hand-drawn labels → a scored classification** — 73.5 % / κ 0.58 on blocks the model never saw; the
   checks that caught the 29/30 Sep maps. (§30–§32, layouts 04, 05)
8. **What the references showed** — T1: the thermal bands add +1.3 pt and terrain alone matches the
   full stack; T3: the index does not track calibrated thermal inertia, Viking albedo does; T2:
   Athabasca's lava is the least cratered unit in its window; T8: the classes are terrain classes;
   T5: no band separates the 1:20 M contacts much better than chance (day IR leans H1's way);
   T6: the composite's Iso Cluster classes are the least reproducible of all inputs; T7: no channel
   threshold keeps first-order streams on real slopes. (§40.1, §42.2, §42.4, §43, §47)
9. **What is not done** — digitising (review ready, §46), lava flows mapped from the mosaic,
   craters and channels below 20 km at ±60° (the fine pass, desktop). (`NEXT-STEPS.md`)

Every number above is already in the record; requote from there, not from this list (KB §12.1).

## 5. Hypotheses and questions — where each stands

The interim (and prospectus) set four hypotheses and six questions. Nothing has tracked them
since. Status, for both the interim and the final:

| | claim | status | what would settle it |
|---|---|---|---|
| **H1** | Day IR delineates flow boundaries under dust that Viking misses | **tested, not supported at 1:20 M** (T5, §47.2): day IR separates 21 % of lAv contact profiles, Viking red 12 %, chance 10 %; the difference's interval includes 0 | T5 again on lava margins digitised at Athabasca |
| **H2** | Fluvial channels have shallower gradients than volcanic ones, and the two separate on gradient vs thermal | **stage 1 tested 2026-10-09 (KB §51.1), not supported:** by window, the volcanic channels are shallower (median 1.4 against 10.2 m/km) and thermal response separates nothing (AUC 0.50); stage 2 waits for reviewed channels with `Origin` (§46) | the digitised channels at Ius (fluvial) and Athabasca (volcanic), each with `SlopeDeg` and `ThermIdx` attributes the candidates already carry (§25) |
| **H3** | The 4-band composite gives more stable Iso Cluster classes than any single input | **answered, not supported** (T6, §47.3): halves-trained ARI 0.40 for the 4-band composite against 0.61–0.89 for single inputs; most coherent, only just ahead of Viking | — |
| **H4** | Crater rims from DN gradient recover most of the 141 IAU craters > 100 km | **answered with a different method**: fill depth, not DN gradient — 68 % of 117 inside ±58° (§28.11) | report the method change honestly; the gradient route was never run |
| Q1 | Does projecting the DEM change slope enough to matter? | **answered**: yes, percent rise on a degree grid was not a slope (§7, §20) | — |
| Q2 | Does Composite Bands complete globally once harmonised? | **answered**: bounded, 8.8 s; the GUI global runs 2 h 52 m and 3 h 10 m on the desktop (§18, §29.1) | — |
| Q3 | How much does 8-bit depth limit separation? | **overtaken**: local normalisation is the bigger limit (§28.10) | — |
| Q4 | Is day IR enough, or is night IR needed? | **answered**: night IR is the most independent band (§18.3) | — |
| Q5 | How many tributary orders are recoverable at 100 m? | **answered** (T7, §47.4): none that the DEM supports; max order follows the threshold (2 at 500 km², 3 at 50, 5 at 1) and ~two thirds of first-order streams lie under 2° at every threshold | — |
| Q6 | Does DN gradient reveal unit boundaries beyond the source image? | **unexamined** | low priority; say so |

## 6. Timeline to mid-November

The exact due date is not known; these assume **~13 November**, the early end of "mid-November".
If the date turns out later, the slack goes to data work, not to the documents.

| when | what |
|---|---|
| now → 1 Nov | data work per `NEXT-STEPS.md`; **rebuild the deck after every result** (§0) |
| **by 2 Nov** | **interim data cut**: whatever is measured by then goes in; everything after goes to the final |
| 2–6 Nov | finish `interim.py` (the deck's text) and point the report at it; previously: rewrite `content.py` from the record (`GOALS_SHORT`, `PROGRESS` facts, `PRELIM` → §4 results, `ISSUES`, `NEXT_STEPS`, `SCHEDULE`, `WORKFLOW_LOG`); the author sets the percentages |
| 6–9 Nov | rebuild both documents; export every slide and page and read them; `verify_all.py` updated for the new facts (it enforces the old ones) and green |
| 9–12 Nov | review and rehearsal |
| mid-Nov | deliver |

## 7. Wording traps, all hit before (KB §14.5, §12)

- **"Global"** → "±60°" or "the analysis extent" (§16.5).
- **"Thermal inertia"** → "diurnal contrast" or "relative thermal response". The held products
  cannot give inertia (§24). §19.3 and §18.4 of the record still use the old word in places.
- **"Crater inventory"** → "closed depressions ≥ 1 km"; quote **68 %**, not 75 % (§26, §28.11).
- **Composite Bands failed four times on 9–13 Sep** (five with the 24 Sep cancel), not three (§8).
- **The SegmentMeanShift of 9 Sep ran on the Mars DEM**, not Mercury (§14.5 #3).
- **The lava tube class is not a result** (§31.3). Don't show it as one.
- Elevation is not a classification band; the corrected stack has none (§31.2).
- **`verify_all.py` checks the interim against the record.** After `content.py` changes, update the
  checks, then make them pass, never the other way round (§17).
