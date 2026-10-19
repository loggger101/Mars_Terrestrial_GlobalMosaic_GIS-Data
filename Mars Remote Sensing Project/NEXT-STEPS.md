# Mars Global Mosaic — next steps

The plan. `PROJECT-KNOWLEDGE.md` ("KB", § numbers point into it) is the record and the authority on what
is true; when the two disagree, the KB wins and this file is fixed. Done work is recorded there and
**removed** from here, not struck through; sections 1–10 keep their numbers (scripts and the KB cite them). The
interim has its own plan, `INTERIM-PLAN.md`; how to work on either machine, including the start-of-session
checklist, is `HANDOFF-DESKTOP.md`.

| deadline | date |
|---|---|
| digitising checkpoint | **1 November** (§6 contingency) |
| interim data cut | **2 November** |
| interim report + presentation | **mid-November** (exact day not known; plan against ~13 November) |
| data freeze | **22 November** |
| final | **Tuesday 8 December 2026** |

---

## Resume here — 2026-10-16

**Where it stands.** Every scripted job up to the review is done and recorded (KB §53–§57): the ±60°
fine pass (465,354 closed depressions ≥ 1 km, 969,822 channel segments, layouts 11–12); the 180° DEM
column fixed at its source (§54); the 200 m classification, **published as the 200 m map with an 11 × 11
(2.2 km) majority filter, 73.8 %, κ 0.58 held out** (§55.3, §57), the 400 m map superseded (§57.2);
T1 confirmed with Pro's SVM (thermal +1.36 pt at 200 m, +1.97 at 400 m, §56); T8 rerun on the published map
(§57.1); the interim rebuilt, 28 slides and 20 pages (§57.3); GitHub release `data-2026-10-16` (§57.4).
The project: 30 maps, 15 layouts (§63); nothing is running on the desktop.
**2026-10-18, laptop (§58–§61):** no new data since; the drive-root junctions point at `F:` and are broken on
the laptop (retarget before any Spatial Analyst run there); the record and the plans condensed, two scripts freed
from a hard-coded `F:`, every sheet re-polished and the interim rebuilt from them, nothing measured changed.
**2026-10-19, laptop (§62):** the province figure redrawn light from §28.10's tables (47.67 DN covers four
provinces, −0.0009 seven); slide 11 updated; the interim rebuilt, 28 slides and 19 pages.
**2026-10-19, laptop (§63):** layout 15 added, the Athabasca Valles type area in visible, night IR, day IR and
topography with unit `lAv`; every footer now gives "Logan M Edwards"; 08's caption no longer names Tharsis.
The interim deck still says 14 layouts and does not show 15 (the author's call: leave it for now).
`Mars Project\Athabasca\` is in no release yet (§63.1): the next `github_release_bundle.py --upload` carries it as
`athabasca.zip`; then set `ATH_RELEASE` in `github_catalog_rasters.py` and rerun it.

**The three `Landform_*` digitising classes hold 0 rows; 0 of 9,287 candidates are reviewed.** The review
is the critical path, and only the author can do it (§6).

**Next, in this order:**

| # | what | who | how | done when |
|---|---|---|---|---|
| 1 | **Review the Ius candidates**, then Athabasca | author, in Pro | §6 | rows in `Landform_ChannelCenterlines` / `Landform_CraterRims`; the tally printed |
| 2 | After each review session: copy the accepts, refresh layout 14, re-export the gdb, push | agent | §3 | the repo's gdb export matches the drive; layout 14's table matches the tally |
| 3 | **Deep Learning Libraries**: one install as administrator (the author at the screen, for the UAC prompt) | author + agent | `D:\MarsDownloads\dl_libs_37\extracted\ProDeepLearning.msi` (downloaded, CRC and Esri signature checked, KB §53.5); then `desktop_check.py` | the X5 preflight says ready |
| 4 | **X5, deep learning** | agent, desktop | §5 | held-out recall and precision in the KB beside the SVM's |
| 5 | Retests that wait for the review: H2 stage 2, H1 on digitised margins | agent | §4 | results in the KB, either way |
| 6 | The interim: due date and the percent-complete column from the author; rebuild after each result | author + agent | `INTERIM-PLAN.md` §0, §6 | delivered |

**Waiting on the author:** items 1, 3 and 6; whether to delete the two recreated `_60_smoke` classes
(KB §57.1); whether to publish a derivatives release carrying the §54 patch (33 GB; the catalogue says how
to patch a restore instead, §57.4); emptying the Recycle Bins (~21 GB of finished scratch, §57.5).

---

## 1. Where the project stands against its own goal

The prospectus promises **one internally consistent landform inventory of three families — lava flows,
fluvial channels, impact craters — from a co-registered visible + thermal-IR mosaic.**

| | type areas (Ius Chasma, Athabasca Valles) | ±60° analysis extent |
|---|---|---|
| **Co-registered mosaic** | done, 100 m (§18, §42.1) | done: one 100 m / 200 m grid, 7-band stack, layout 08 (§28, §31.2, §38) |
| **Craters** | closed depressions ≥ 1 km in both windows, 11–13 % catalogued craters (§26, §42.3) | 465,354 closed depressions ≥ 1 km: 15.3 % catalogued at ≥ 1 km, 62.2 % at ≥ 5 km (§53.4, §54.4); layout 11 |
| **Channels** | 2,610 candidates at Ius, 188 steep and rock-floored (§25); 3,283 at Athabasca | 969,822 routed segments, not scored (no reference), layout 12 (§53.6) |
| **Lava flows** | the geologic map's `lAv` unit at Athabasca is the reference (§42) | SIM 3292 volcanic units, layout 10 (§44); the classifier cannot separate volcanic plains (§43.2–43.3) |
| **Manual digitising** | **empty**; review fields ready (§46) | — |
| **Classification** | Iso Cluster and supervised on terrain labels (§19, §27) | SVM on the 512 hand-drawn labels, 200 m 11 × 11: 73.8 %, κ 0.58 held out (§57) |

**The central claim, measured:** the thermal bands add a small, resolved amount to the classification
(+1.3 to +2.0 pt with two classifiers, §40.1, §56), from crater and hill terrain; against calibrated TES
thermal inertia the THEMIS mosaics keep only a weak local signal and visible albedo carries the material
signal (§42.4, §43.1). The hand-drawn classes are landform classes (§40.1, §56.1).

**Hypotheses** (status table in `INTERIM-PLAN.md` §5): H1 not supported at the geologic map's 1:20 M
(rerun on digitised margins); H2 not supported at stage 1 (stage 2 on reviewed channels); H3 not supported;
H4 answered by another method. Q1, Q2, Q4, Q5 answered; Q3 overtaken; Q6 unexamined.

---

## 2. Open decisions

D1–D13 were all answered on 2026-10-08/09 (KB §50); the published filter on 2026-10-16 (§57) and the
400 m map on 2026-10-16 (§57.2). Open, each the author's:

| # | decision | recommendation |
|---|---|---|
| D14 | the two `_60_smoke` classes, recreated by X2's smoke run (§57.1) | delete (they were deleted once, D9); they are in the release GeoPackage |
| D15 | a derivatives release with the §54 patch (33 GB upload) | not needed: the catalogue gives the two commands that patch a restore (§57.4) |
| D16 | the interim's percent-complete column and its due date | the author's numbers; `interim.py` prints dashes until then |

---

## 3. What the agent does after each review session

1. `accept_reviewed.py` (ArcGIS Python; a dry run prints the tally and the precision so far), then
   `accept_reviewed.py --apply --by "<reviewer>"`. Reruns copy only new accepts.
2. Layout 14: `make_validation_sheet.py` (Pro closed), then `polish_layouts.py`; export and read it.
3. `make_t4_channel_h2.py`: it reports stage 2 waiting until ≥ 10 fluvial and ≥ 10 volcanic reviewed
   channels exist. **Stage 2 is not written yet:** when the counts are reached, extend the script to compare
   by `Origin` (sample the type-area index along the reviewed channels), prediction and rule written first.
4. When lava margins exist at Athabasca: give `make_flow_margin_test.py` a `--margins` source
   (`Landform_LavaFlowMargins` in place of the SIM 3292 contacts) and rerun T5 (H1). The script needs the
   `<drive>\Athabasca` junction (retarget it first on the laptop, KB §58.2).
5. `github_export_gdb.py`, then the end-of-session sequence (`HANDOFF-DESKTOP.md` §4).

---

## 4. Tests

Each writes its prediction and verdict rule into the script before it runs.

| # | question | status |
|---|---|---|
| T1 | does thermal IR improve the classification? | **done**: +1.3 pt numpy (§40.1); Pro's SVM +1.36 (200 m), +1.97 (400 m); without visible and terrain only tie (§56, §56.1) |
| T2 | is Athabasca younger than Ius's plateau? | **done** (§42.2) |
| T3 | which layer tracks calibrated thermal inertia? | **done**: Viking does, the THEMIS pair barely (§42.4, §43.1) |
| T4 | H2: do volcanic and fluvial channels separate on gradient and thermal response? | stage 1 done, not supported (§51.1); **stage 2 open**, on reviewed channels (§3 step 3) |
| T5 | H1: does IR show flow margins Viking misses? | inconclusive at 1:20 M (§47.2); **open**, on digitised margins (§3 step 4) |
| T6 | H3: is the composite more stable than any single input? | **done**, not supported (§47.3) |
| T7 | Q5: how many tributary orders does 100 m resolve? | **done**: no DEM-supported answer (§47.4) |
| T8 | the classes against the geologic map | **done** (§43.2), rerun on the published map (§57.1) |

**Scope:** every open test is optional; if time runs short, drop tests, never the digitising checkpoint or
the cut dates.

---

## 5. Desktop jobs

| # | job | cost | notes |
|---|---|---|---|
| X5 | deep learning on the 2080 Ti (approved, q25) | hours | after the install (Resume here, item 3): `make_dl_model.py --train [--model RETINANET] [--epochs 20]`, `--detect --emd <model.emd>`, `--score <detections fc>`. Train on `LabeledObjects\global60_svm_stack_200m_train\` only; score on the 183 held-out polygons. Never run before; which detection models take 7-band input is unverified **[?]** |
| X7 | optional, q12: one source mosaic as a tiled, compressed copy, timed against the original | ~1 h | only if panning stays slow after the pyramids (§53.1) |

Done on the desktop and recorded: X0 junctions, X1 GPU, X2 fine pass, X3 200 m classification, X4
pyramids, X6 q24 (§53–§55); T1 in Pro (§56).

---

## 6. Manual GUI work, the critical path

**Review, then draw only what is missing** (decision D10, KB §46):

1. Open the map "Ius Chasma — digitising" (later "Athabasca Valles — digitising"); start with the layer
   "Channels: steep and rock-floored (188)", then "Closed depressions ≥ 1 km".
2. In the layer's attribute table, set `Review` (accept / reject / unsure), and a `ReviewNote` if useful.
   Before accepting, set `Origin` (channels: fluvial / volcanic / indeterminate), `Preservation` (craters:
   fresh / degraded / ghost) and `Confidence` (certain / probable / inferred); they are copied as they stand.
3. Save edits; the agent then runs §3.
4. Draw what the machine missed straight into the digitising classes: breached craters, and **lava-flow
   margins at Athabasca** (the `lAv` unit of the geologic map shows where; these settle H1).

Rejections are data too: they become the detector's precision. Suggested minimum for the validation to mean
something: ~30 channel segments, ~50 crater rims, every defensible lava margin.

**Contingency, decided now:** if the three `Landform_*` classes are still empty on **1 November**, the interim
presents every machine product as **candidates with its measured recall**, never as a landform map, and says
so; lava flows rest on T8 and the geologic map alone. The final stands on the machine products, the 512
training polygons, the held-out scores and the tests.

---

## 7. Figures for the two deadlines (no rubric exists, D2)

| # | sheet | interim | final |
|---|---|---|---|
| 10 | locator: ±60°, both type areas, the volcanic units | ✓ | ✓ |
| 08 | the mosaic at ±60°: visible, day, night, topography | ✓ | ✓ |
| 01–02 | Ius visible; Ius night IR | ✓ | ✓ |
| — | the province test (Viking separates, THEMIS does not) and T3 against TES | ✓ | ✓ |
| 03 | Ius Iso Cluster | ✓ | maybe superseded |
| 06, 09 | Ius and Athabasca digitising candidates | ✓ | replaced by layout 14 |
| 07 | ±60° basins ≥ 20 km | ✓ | ✓ |
| 11–12 | ±60° closed depressions ≥ 1 km; ±60° channels | ✓ | ✓ |
| 04 | ±60° landforms, the published 200 m 11 × 11 map, scored | ✓ | ✓ |
| — | T1: the numpy ablation and the Pro confirmation | ✓ | ✓ |
| 13 | the classes against the geologic map (T8) | ✓ (as a chart) | ✓ |
| 05 | the 29–30 Sep GUI SVMs checked | ✓ | appendix |
| 14 | validation of the review | if reviewing has started | ✓ |

**Final report outline** (to fill after the freeze, not before): 1 question and hook (Athabasca) · 2 data and
the ±60° decision · 3 co-registration and the frames trap · 4 the thermal pair: what it can and cannot do ·
5 craters · 6 channels · 7 lava flows · 8 classification and accuracy · 9 limits · 10 what next. Each section
closes on a measured number and a sheet. **No final builder exists yet:** write one on the interim's pattern
(one source module, charts from logs, layouts exported by script), early enough to rehearse.

**Before each deadline:** a new GitHub data release (`github_release_bundle.py --upload data-YYYY-MM-DD`), then
point `github_catalog_rasters.py`'s `DATA` and `github_export_gdb.py`'s `RELEASE` at it, then run
`tools/check_remote.py` by hand (KB §57.4). Check that the releases hold every figure the documents need.

---

## 8. Schedule

| window | focus |
|---|---|
| **16 Oct – 1 Nov** | Review and digitising (§6); after each session §3. The install and X5 when the author is at the screen. **1 Nov: digitising checkpoint.** |
| **2 Nov** | **Interim data cut.** What is measured goes in; the rest goes to the final. |
| **2–12 Nov** | The interim per `INTERIM-PLAN.md` §6: rebuild, read every page, `verify_interim.py`, review. Data work pauses except overnight runs. |
| **~13 Nov** | **Interim due.** |
| **14–22 Nov** | H1 and H2 retests, layout 14 from the review. **Data freeze 22 Nov.** GitHub release refreshed. |
| **23 Nov – 4 Dec** | The final report and deck, built by script from the layouts. Thanksgiving 26 Nov: nothing planned. |
| **5–8 Dec** | Buffer and rehearsal. Nothing new. |

---

## 9. Risks to plan around

- **The drive is the only full copy** of the project; GitHub holds the tree and the releases, not the gdb's
  rasters. The USB drive has dropped off mid-write twice (§36.4): big writes go to internal disk first, then one
  copy (§7 has the release step).
- **Two deadlines three weeks apart** compete for the same days: hence the hard cut on 2 Nov and documents
  built by script, not by hand.
- **The thermal argument is weaker than the prospectus says** (§28.10, §43.1): write both documents around what
  is measured; the wording traps are `INTERIM-PLAN.md` §7.
- **The review may not start in time:** the §6 contingency is the plan for that case.

---

## 10. Considered and ruled out, so they aren't proposed again

- **Segmentation at ±60°:** ~92 h at 14/14/30 (§23.6). Object-based work stays on the type areas.
- **Calibrated thermal inertia from the held mosaics:** impossible, they are stretched 8-bit DN (§24);
  calibrated inertia only from outside data (TES), and then at ~3 km.
- **Copying the project to internal disk:** ruled out by the author (§2.2).
- **The 100 m Composite Bands run** (`make_global_stack.py`): overtaken by the 200 m stack (q7).
- **CRISM, SHARAD/MARSIS, a global CTX mosaic:** out of scope (§14).
- **Correcting the delivered prospectus or Presentation 1:** they are history (§1).
- **Crater ages from the closed-depression counts:** the detector misses breached craters (§26.3); relative
  density between windows (T2) is the most it supports.
- **Rerunning the 400 m map's 180° column:** superseded by the 200 m map (§57.2).
- **The agent digitising for the author:** the judgement is the point of task 11. Machine output enters the
  digitising classes only through an accept in review (§25, D10).
