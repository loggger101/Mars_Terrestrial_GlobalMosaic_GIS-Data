# Mars Global Mosaic — next steps

The plan. `PROJECT-KNOWLEDGE.md` ("KB", § numbers point into it) is the record and the authority on what
is true; when the two disagree, the KB wins and this file is fixed. Done work is recorded there and
**removed** from here, not struck through; sections 1–10 keep their numbers (scripts and the KB cite them). The
interim has its own plan, `INTERIM-PLAN.md`; how to work on either machine, including the start-of-session
checklist, is `HANDOFF-DESKTOP.md`.

| deadline | date |
|---|---|
| interim data cut | **26 October** (D20; was 2 November): the interim covers what is measured by then |
| interim presentation | **10 November** (D16, the author, 2026-10-27); the report's date not given, plan against the same day |
| label review, v2 runs, digitising: for the final | **27 October – 22 November** (the v2 runs need ~2 days after the label review) |
| data freeze | **22 November** |
| final | **Tuesday 8 December 2026** |

---

## Resume here — 2026-10-31

Only the state, what waits on whom and the next step; the history behind each line is the KB section it cites
(condensed 2026-10-31, §13.1 P10: the dated paragraphs since 10-18 are in git history and KB §58–§69.34).

**Where it stands.**
- **The ±60° products** (KB §53–§57, §66): 465,354 closed depressions ≥ 1 km and 969,822 routed channel segments
  (layouts 11, 12); the four-class SVM map at 200 m with an 11 × 11 majority filter, 73.8 %, κ 0.58 held out (§57,
  layout 04); the two-pass U-Net province map, 98.9 %, κ 0.980 held out (§66.8, layout 17). **A geography-only
  baseline**, each pixel the nearest training polygon's class, scores 83.2 % on the same polygons, above the SVM
  map, which leads it only by balanced accuracy (§69.35, D30). Crater size-frequency curves: §69.35.
- **Seven classes** (D17, D28): 971 reviewed v2 labels, 734 training and 237 held out (§69.8). On the v2 held-out
  polygons the seven-class SVM scores 42.5 %, κ 0.310 and the seven-class U-Net 69.0 %, κ 0.606; both fail D18's
  rule, and **they lead all the same** (layouts 04b, 13b, 17b; §69.24–§69.27). The U-Net maps edifice on 39.5 % of
  ±60°, 70 % of it off the volcanic units, most on SIM 3292's highland group, 46.8 % of which it calls edifice
  (T8, A14, §69.37).
- **Thermal:** T1, +1.36 pt at 200 m in overall accuracy and none by balanced accuracy (§56, §69.18, D25); T3, the
  THEMIS pair against TES inertia peaks in 2–5° blocks at r ≈ 0.12 (§69.29; layout 18, §69.30).
- **The review, the critical path** (§69.33): **3,791 of 9,287 candidates**: every closed depression at both type
  areas, the 188 steep Ius channels, 209 of the 409 rock-floored Athabasca channels. The digitising classes hold 199
  channels, 381 crater rims and 0 lava margins, none drawn by hand; `Origin` is set on no channel, so H2's stage 2
  waits.
- **The project and the deliverables:** 38 maps and 21 layouts, no broken source (§5). The interim at its 26 October
  cut (D20): 32 slides and a 21-page report, rebuilt 10-31 for layout 11's corrected citation (§69.34). The final
  paper (16 pages) and deck lead with the seven-class maps (§69.27); their review figures stay at §69.7's until the
  freeze (§12.1). Backup: release `data-2026-10-29` (§69.28).
- **The machines:** the drive-root junctions point at `F:` and are broken on the laptop (§58); the drive and the
  clone agree, and `github_sync.py` refuses if the clone ever holds work the drive lacks (§69.20). Nothing is
  running.

**Next, in this order:**

| # | what | who | how | done when |
|---|---|---|---|---|
| 1 | **Review:** `Origin` on the 199 channel copies (H2 stage 2 needs ≥ 10 fluvial and ≥ 10 volcanic); the other 200 rock-floored Athabasca channels, then the rest; the Athabasca lava margins (H1) and breached craters, by hand | author, in Pro | §6 | rows in `Landform_ChannelCenterlines` / `Landform_CraterRims` / `Landform_LavaFlowMargins`; the tally printed |
| 2 | After each review session: copy the accepts, refresh layout 14, re-export the gdb, push | agent | §3 | the repo's gdb export matches the drive; layout 14's table matches the tally |
| 3 | Retests that wait for the review: H2 stage 2, H1 on digitised margins | agent | §4 | results in the KB, either way |
| 4 | The paper's analyses that need no author time, in §12.6's order (desktop: A1, A2, A3 (b) and (c), A5, A6; A4b, A3 (a), A10, A14 and W10 done 10-31, KB §69.34–§69.38) | agent | §12.2, §12.4 | results in the KB, by the **22 Nov** freeze |
| 5 | The interim: deliver on **10 Nov**; the report's date from the author | author + agent | `INTERIM-PLAN.md` §0, §6 | delivered |
| 6 | The freeze: §12.1's lines and every result into the KB, then `final.py` and the `.tex`; rebuild, read, `verify_interim.py` on both | agent | §12.6 step 4 | by **22 Nov** |

The class revision (§11) is done to the final's text (2a–2c, KB §69.2–§69.27). Deep learning (X5, X5b, X5c) is done
and scored (§66); further tuning first needs validation blocks of its own (§66.5), the author's call.

**Waiting on the author:** items 1 and 5; D14–D16, D21–D27, D29 and D30 (§2); the interim talk's slot length (§12.5); whether
layout 18 or `final_img\tes_block_scale.png` goes into a deliverable (§69.30); whether the interim shows layouts 15–18
(it shows 13 of the 17 that existed at the cut, `INTERIM-PLAN.md` §3); emptying the Recycle Bins (~21 GB of finished
scratch, §57.5).

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
| D16 | the interim's due date: **the presentation is 10 November** (the author, 2026-10-27, KB §69.10); the report's date is still open (the percentages were set 2026-10-26, KB §69.5) | plan the report against 10 November too |
| D21 | the paper's title, which promises "Mapping Lava Flows" though they come from the geologic map (§12.4 W2) | retitle around the stack and what it can and cannot map |
| D22 | the two blind checks: the rule-screened v2 rows (§12.3 R1, ~45 min) and a probability-sample accuracy check (R2, ~2–3 h) | R1 yes, after the candidate review; R2 if time is free |
| D23 | a DOI for the data release through Zenodo, and a data statement (§12.4 W7); publishing | yes, with the pre-final release (§7) |
| D24 | the final deck in the interim's dark `mars_theme` (§12.5) | yes: one look for both talks |
| D25 | the abstract's and conclusions' thermal gain: qualify it with the balanced-accuracy result (§12.4 W9); also the README (the interim: done, the author's yes, KB §69.21) | yes: one clause, "in overall accuracy; none by balanced accuracy" |
| D26 | the built deck, report and paper PDF committed only once per deadline (§13.1 P4); rewriting history to drop the 35 earlier copies needs a force push and a re-clone on both machines | yes to committing at milestones; no rewrite |
| D27 | closing the project after 8 Dec: final tag and release, `CITATION.cff` completed, the README rewritten as finished work (§13.1 P12); an ORCID for the citation if the author has one | yes |
| D29 | the seven-class maps' gain (D28) by balanced accuracy: none (SVM −0.15 pt, U-Net +0.20 pt on the v2 held-out polygons); the gain is in macro F1 and in quantity disagreement (KB §69.34). Say so in the paper's Table 3 and text, the deck and the README? | yes, as for D25: one clause, "in overall accuracy and macro F1; not in balanced accuracy"; D28's lead stands |
| D30 | the geography-only baseline (KB §69.35): the nearest training polygon's class scores 83.2 % held out, above the published SVM map's 73.8 %; the SVM map leads only by balanced accuracy (0.667 against 0.613); the U-Net clears it on every measure. Report it beside every held-out score (the paper's Table 3, the final deck), and lead the SVM map's score with balanced accuracy? The interim is cut (D20) | yes: one Table 3 row and one sentence; the interim untouched |
D19 was answered 2026-10-24, before any v2 score existed: D18's rule (a) is judged on the held-out polygons whose
v2 class is 1–4, the ground both maps can name (KB §68.4 amended, §69.4); `score_d18_verdict.py` does so.
D28 was answered 2026-10-29, after both seven-class maps had failed D18's rule (KB §69.24–69.25): **the
seven-class maps lead** all the same, as the most up-to-date and detailed maps; the four-class maps stay as
history, and D18's result stays on the record and on the sheets (KB §69.26).
D20 was answered 2026-10-26: **the interim's data cut is 26 October** (KB §69.5); the class revision, the
review and the retests go to the final, and D17 / D18's "before the interim" and "in the interim" below now read
"for the final".
D17, the class revision, was answered 2026-10-22: seven classes, before the interim, the agent proposes and the
author accepts (KB §68.1; §11 here). D18 the same day: **the interim shows both maps**, four-class and
seven-class, each scored on its own held-out polygons and both on v2's; the seven-class map is expected to
supersede the four-class one for the final, by KB §68.4's rule (v2's accuracy and κ at least the four-class
map's on the v2 held-out polygons, each new class above its base rate, the old three within 5 pt); failing it,
v2 is a reported test. The author makes time for both reviews: no cap.

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
| T1b | T1 on the seven v2 classes | **proposed** (§12.2 A2), after the v2 scoring |
| T4, stage 1b | H2 with the valley map and SIM 3292 standing in for origin | **proposed** (§12.2 A7); stage 2 stays the authority |
| T9 | does thermal IR help predict geologic-unit groups, material labels? | **proposed** (§12.2 A8) |

**Scope:** every open test is optional; if time runs short, drop tests, never the digitising checkpoint or
the cut dates.

---

## 5. Desktop jobs

| # | job | cost | notes |
|---|---|---|---|
| X5 | deep learning on the 2080 Ti (approved, q25) | hours | trained, detected and scored 2026-10-19, RetinaNet, model and detections in `DLModels\global60_retinanet_20261019\` (KB §66.1–66.2); the detections in the gdb, a map and layout 16, `make_dl_map.py` (§66.3–66.4). X5b and X5c 2026-10-20 (§66.5–66.6): `DLModels\global60_retinanet_x5b_20261020\`, `global60_unet_x5c_20261020\`; queues `build\logs\run_x5b.cmd`, `run_x5c.cmd`. Commands: `make_dl_model.py --prepare`, `--train [--tag] [--data a;b] [--epochs 30] [--freeze] [--early-stop]`, `--detect --emd <model.emd> [--threshold]`, `--score <detections> --out <json>`; `make_dl_pixels.py --export`, `--train`, `--classify --emd`, `--score <folder>`, `--score-svm`. Train on `LabeledObjects\global60_svm_stack_200m_train\` only; score on the 183 held-out polygons. Which other detection models take 7-band input is unverified **[?]** |
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

**Contingency, decided now, applied to the interim at its 26 Oct cut (D20):** if the three `Landform_*` classes
are still empty on **1 November**, the interim presents every machine product as **candidates with its measured recall**, never as a landform map, and says
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
closes on a measured number and a sheet. **The final builders exist since 2026-10-22 (KB §69):** the AASTeX paper
`NEXT STUFF\Final\paper\mars_global_mosaic.tex` (`build_final_paper.py` copies its figures and compiles it with
MiKTeX) and the deck from `final.py` (`build_final_deck.py`), figures from `make_final_figs.py` (ArcGIS Python) and
`make_fig_final.py`. After the review and the freeze: bring the numbers in `final.py` and the `.tex` to the record,
re-export, rebuild both, read every page and slide, run `verify_interim.py final.py` and `verify_interim.py` on
the `.tex` (KB §69.3).

**Before each deadline:** a new GitHub data release (`github_release_bundle.py --upload data-YYYY-MM-DD`), then
point `github_catalog_rasters.py`'s `DATA` and `github_export_gdb.py`'s `RELEASE` at it, then run
`tools/check_remote.py` by hand (KB §57.4). Check that the releases hold every figure the documents need.

---

## 8. Schedule

| window | focus |
|---|---|
| **16–26 Oct** | Done: X5 on the desktop (KB §66); the class revision's proposals (22–23 Oct) and its rehearsal (KB §69.4). |
| **26 Oct** | **Interim data cut** (D20, KB §69.5). What is measured is in the interim; the rest goes to the final. |
| **27 Oct – 22 Nov** | For the final: review and digitising (§6), after each session §3; the label review (§11.4), then the v2 runs (~2 days, §11.5); H1 and H2 retests, layout 14 from the review. **Data freeze 22 Nov.** GitHub release refreshed. |
| **by 10 Nov** | The interim per `INTERIM-PLAN.md` §6: any last change, rebuild, read every page, `verify_interim.py`. **Interim presentation 10 Nov** (the report's date not given). |
| **23 Nov – 4 Dec** | The final report and deck, built by script from the layouts. Thanksgiving 26 Nov: nothing planned. |
| **5–8 Dec** | Buffer and rehearsal. Nothing new. |

---

## 9. Risks to plan around

- **The drive is the only full copy** of the project; GitHub holds the tree and the releases, not the gdb's
  rasters. The USB drive has dropped off mid-write twice (§36.4): big writes go to internal disk first, then one
  copy (§7 has the release step).
- **Two deadlines three weeks apart** compete for the same days: hence the hard cut on 26 Oct (D20) and documents
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
- **The decks' and paper's images as JPEG** (was §13.1 P5): ruled out by the author, 2026-10-27; the figures stay
  PNG (KB §69.19).
- **The agent digitising for the author:** the judgement is the point of task 11. Machine output enters the
  digitising classes only through an accept in review (§25, D10).

---

## 11. The class revision (D17), for the final

The author's scheme, the audit and the plan are KB §68; this section is the work.

### 11.1 The classes

| code | class | changes from today |
|---|---|---|
| 1 | Crater | impact only: volcano summits and calderas leave it (labels 22 Arsia, 465 Ascraeus) |
| 2 | steep/windy hills | aprons leave it |
| 3 | lava tube | narrowed to volcanic pit chains, sinuous rilles and lava channels; fluvial ones leave it (six labels), flow fields go to Normal Ground or edifice |
| 4 | Normal Ground | volcanic plains are drawn as Normal Ground |
| 5 | volcanic edifice | new |
| 6 | apron | new: lobate debris aprons and the Tharsis fan-shaped deposits; the Olympus aureole with its origin open |
| 7 | fluvial channel | new, the author's "fluvial tubes"; `Subtype`: valley / inverted channel / esker / fluvial pit chain |

### 11.2 The proposals (agent, needs the drive)

`propose_label_changes.py` (written and tested on the laptop 2026-10-22, KB §68.5; ArcGIS Python, Pro
closed) writes `Landform_TrainingSamples_v2_proposals` and, with `--map`, the map "Labels v2: proposals" (one
layer per `Action`). **Before the first run on the desktop:** download the valley map to
`<drive>\Mars Project\Reference\Alemanno2017_valleys\` (Zenodo 10.5281/zenodo.1051038, CC BY-SA 4.0: the
`Giulia Valleys` `.shp`, `.shx`, `.dbf`, `.prj`; the script checks the `.shp`'s SHA-256) and add it to
`Reference\README.md`; then `--dry-run`, read the tally, then the real run with `--map`. At the session's end,
`github_sync.py` lists the two new scripts: give them a group in its `GROUPS` ("Digitising by review" fits) and
bring the README's script count to 155 (`tools/check_repo.py` fails until then). The geologic map, the crater
database and the DEM are already on the drive. The outlines of Levy et al. 2014's lobate-apron catalogue sit
behind a bot check on Wiley's site: only the author can download them (the article's "GIS data set").

1. **Every one of the 512**, with evidence: SIM 3292 unit-group shares, the largest Robbins crater inside against
   the polygon's size, relief and slope from the stack, elongation, the IAU names inside and within 100 km.
2. **Rules, each giving an `Action` and a `Reason`:** Crater with no Robbins crater near its size, or mostly on
   `ve` units → relabel 5 or check; lava tube by a named vallis off volcanic units → 7; lava tube mostly on volcanic
   plains without a catena → 4; lava tube or hills mostly on apron units → 6; nested same-class duplicates (350)
   → delete; 290/291 → clip at the block edge; label 512 → fix attributes, check its class; everything else keep.
3. **New polygons for 5–7**, inside the held-out blocks first (KB §68.3), then training: edifices and the Tharsis
   fans from the SIM 3292 units and the IAU names; valley floors for 7 from the DEM inside each named vallis's
   extent; lobate debris aprons around the Nilosyrtis, Deuteronilus and Protonilus mensae from the DEM. Any
   outside catalogue (e.g. a published lobate-apron map) only with the author's yes to download it.
4. Read back: counts per `Action` and class and split; every proposed polygon drawn on a chip and checked by eye.

**What the laptop run proposes** (KB §68.5; the desktop run will differ only if the drive's data do): 12
relabels (five Crater polygons that are volcanoes, five lava-tube polygons on valleys, two lava-tube flow fields
to Normal Ground), 23 checks, 1 clip, 1 delete, 1 fix, 574 new (276 valley strips, 172 apron and 126 edifice
pieces); ~8–12 min.

### 11.3 The minimum

Per new class, accepted: ≥ 10 held-out polygons in ≥ 2 held-out blocks, ≥ 20 training in ≥ 3 training blocks.
A class short of it stays out of v2 and is reported as such; its polygons stay in the proposals. **Hills and
lava tube fall short of the training half today** (hills in 2 training blocks; lava tube 18 training polygons
after the relabels): the author draws a few more of each in other training blocks (lava tube: Tractus,
Ceraunius and the Elysium catenae; hills: massifs outside Valles Marineris).

### 11.4 The author's review

The map "Labels v2: proposals", like §6: set `Review` on every row whose `Action` is not `keep`; edit an outline
before accepting it; set `Subtype` on class 7; draw missing polygons straight into the proposals class with
`Action` new, `ProposedClass` set and `Review` accept. **Only `accept` counts:** an accepted row enters with its
outline and `ProposedClass`; any other row of the 512 enters as it was, and any other new row is left out. To
change the class of a `keep` row, set its `ProposedClass` and accept it. The clip of label 290 must be
accepted (or the two outlines otherwise separated): `apply_label_review.py` refuses labels that share ground
across the split.

### 11.5 After the review (agent, desktop)

0. If `import arcpy` says "The Product License has not been initialized" (it did for some hours on 2026-10-23,
   then cleared by itself, KB §68.6), open Pro and sign in. Optional, the author's call: `verify_global60_classification.polys()`
   reads curved label 512 as 2 points and so leaves it out of every training-set score (KB §68.6); densifying
   curves there adds it, changing recorded training-set figures only. Held-out polygons have no curves.
1. `apply_label_review.py --dry-run`, then without it → `Landform_TrainingSamples_v2`, `_v2_60_train`,
   `_v2_60_test` (same 14 held-out blocks; centroid rule; no ground shared across classes or the split,
   checked; a new class short of §11.3 left out of the split unless `--keep-short`). The originals untouched.
2. SVM on v2: train (~1.8 h with seven classes), classify at 200 m (**~20 h** with seven classes, ~3 × the
   four-class run: measured in the rehearsal, KB §69.4), 11 × 11 filter; score v2 and the published
   map on the v2 held-out polygons; D18's verdict. T8 on v2. Every script takes `--labels v2` (`labelsets.py`,
   KB §68.6): it reads `_v2_60_train` / `_v2_60_test`, writes names with `_v2`, and never replaces a four-class
   file. In `build\`, ArcGIS Python, with `<G60>` = `F:\Mars Project\Global60`:
   ```
   python make_global60_classification.py --cell 200 --labels v2
   python make_global60_landforms_clean.py --cell 200 --size 11 --labels v2
   python verify_global60_classification.py --cell 200 --labels v2 --raster <G60>\global60_landforms_svm_v2_200m_mode11.tif
   python verify_global60_classification.py --cell 200 --labels v2 --raster <G60>\global60_landforms_svm_200m_mode11.tif
   python score_d18_verdict.py
   python make_geomap_check.py --labels v2
   ```
   The first refuses to start unless both v2 halves exist and every row is `apply_label_review.py`'s with a
   code 1–7; it skips the four-class split. The fourth scores the published map on the v2 polygons; the fifth
   prints (a)–(c) and the verdict into `logs\d18_verdict.json`.
3. U-Net on v2: export the v2 training split, train (**~7.8 h** in the rehearsal: 21,711 chips, 6.4 × the
   four-class time), two passes over ±60° (**~12.6 h**, run in chunks of ≤ 60 tiles: one process leaks ~0.28 GB a
   tile, KB §69.4); scored the same way. `run_rehearsal_v2p.ps1` is the queue to copy for v2.
   Dropped first if the dates slip.
   ```
   python make_dl_pixels.py --export --labels v2
   python make_dl_pixels.py --train --labels v2
   python make_dl_pixels.py --classify-global --labels v2 --emd <the new model's .emd>
   python make_dl_pixels.py --classify-global --labels v2 --pass B --emd <the same .emd>
   python make_dl_pixels.py --mosaic --two-pass --labels v2
   python verify_global60_classification.py --cell 200 --labels v2 --raster <G60>\global60_landforms_unet_v2_200m_seamfix.tif
   python verify_global60_classification.py --cell 200 --labels v2 --raster <G60>\global60_landforms_unet_200m_seamfix.tif
   ```
   Work goes to `C:\MarsScratch\x5c_v2`; `--train` refuses an export made from the four-class labels.
   `make_unet_map.py` (the per-polygon table and layout 17's layers) is still four-class: step 4's work.
4. **Done 2026-10-29 (KB §69.26):** `make_v2_sheets.py` → 04b, 13b, 17b. Layouts: a new sheet for the seven-class SVM map beside 04 (the four-class map, kept), 13 on both, 17 for
   the U-Net on v2; legends name seven classes. The X5 detector and layout 16 stay four-class, as history.
   `polish_layouts.py`, export, read.
5. **Text done 2026-10-29 (KB §69.27):** paper and deck rewritten, the seven-class maps leading. The final rebuilt **with both maps**, the seven-class maps leading (D28; D18, moved from the interim by D20): the four-class map and its scores,
   the seven-class map and its scores, and both scored on the v2 held-out polygons; the class wording in
   `final.py` and the paper updated; `verify_interim.py final.py` and on the `.tex`.

### 11.6 Dates, and what gives first

| by | what |
|---|---|
| 23 Oct | proposals built on the drive and read (the script is tested, KB §68.5): **done** (KB §69.2) |
| 26 Oct | the interim's data cut (D20, KB §69.5): the interim shows the four-class maps and describes the seven-class scheme as proposed, with §68's audit as its evidence |
| ~18 Nov | the author's label review done |
| review + ~1 day | v2 SVM map scored; D18 verdict (~22 h after the review, KB §69.4) |
| review + ~2 days | v2 U-Net scored (~21 h after its export) |
| 22 Nov | data freeze: layouts and the final rebuilt with both maps |

**What gives first** if the label review runs late: the U-Net rerun, then the SVM rerun; the final then shows the
four-class maps and reports the seven-class scheme as a proposal. The author makes time for both reviews
(no cap, D18).

---

## 12. Strengthening the final paper (brainstormed 2026-10-27, laptop, while `run_v2.ps1` runs)

Read against the paper as built (`NEXT STUFF\Final\paper\mars_global_mosaic.tex`, KB §69) and this plan; nothing
was measured (KB §69.17). Each item says what it adds, where it runs and what it waits on. **Priority:** A, before
the 22 Nov freeze if at all possible; B, if time allows; C, only if cheap. Every new test writes its prediction and
verdict rule into its script before it runs (§4). Drive items wait for "queue done" in
`build\logs\run_v2\queue.log` and for the v2 scoring (§11.5), which comes first. Nothing here goes ahead of the
author's review (§6). A14 and W10 (done 10-31, KB §69.37–§69.38), A15, W11, the additions to A3 (c), A5 and
W6, and P13 (§13) come from an outside brainstorm audited on 2026-10-31 against the record (KB §69.36); the rest of that
brainstorm was dropped.

### 12.1 Lines in the paper and `final.py` that the freeze must change

The abstract, the limits on the labels and the candidates, the channel reference and the two citations were brought
current on 2026-10-27 (KB §69.18). Left for the freeze, each drafted in `NEXT STUFF\Final\paper\v2_drafts.tex`:

| where | today | true since |
|---|---|---|
| Methods, labels | four classes, 512 polygons | v2: seven classes, 734 training / 237 held out; **347 apron and fluvial rows accepted by a written rule, not by eye**, and hills short of §11.3 (`--keep-short`): both stated (KB §69.8) |
| Limits, held-out use | "used once for each model" | the v2 maps are a second use of the 14 blocks; say so |
| the PDF and the final deck | built 2026-10-22/23 | rebuild on the desktop (`build_final_paper.py`, MiKTeX; `build_final_deck.py`) and read every page: Table 3 is wider now |

### 12.2 Analyses that need no author time

| # | what | adds | where | pri |
|---|---|---|---|---|
| A1 | **The routed channels scored against the valley map**: share of order ≥ 3 length within 2 / 5 / 10 km of a mapped valley, and of valley length within the same of a routed channel, beside a shifted-network chance baseline (as for craters); by latitude band and SIM 3292 unit group | the network gets a precision and recall, the test the paper names as missing | desktop, ArcGIS Python | A |
| A2 | **T1 on the v2 labels** (§4, T1b): §40.1's Gaussian ablation on the v2 split; does thermal help edifice, apron or fluvial channel, as it helped Crater and hills? | the central claim retested on the classes most likely to carry material | desktop, numpy | A |
| A3 | **Spatial baselines for the held-out score**: ~~(a) each pixel given the class of the nearest training polygon~~ (done 10-31, KB §69.35: 83.2 %, κ 0.658, above the published SVM map); (b) a classifier on elevation and latitude only (the crustal dichotomy); (c) the SVM map under mode filters up to ~51 km, the U-Net's context (256-pixel chips at 200 m): a curve, not one point, at 25, 75 and 255 px (5, 15 and 51 km) beside §55.3's 3–11 px, **for the four-class and the seven-class SVM maps**, each beside its U-Net; the raw seven-class map has never been scored, so its curve starts there. `make_global60_landforms_clean.py --cell 200 --size N [--labels v2]`, then `verify_global60_classification.py --cell 200 [--labels v2] --raster <output>`; ~10 min a filter (uniform-filter votes, so the window's size barely matters) and ~29 min a score (§69.24), ~4.5 h unattended for all seven. The paper sets its window from the resolving rule because every score rises with the window (Methods): the curve is read as how much of each U-Net's lead a plain smoothing reproduces, never as a choice of window | turns "the U-Net's 98.9 % measures agreement at province scale" into a measured statement, and asks the same of the seven-class U-Net's 26.5-point lead | desktop | A |
| A5 | **Block bootstrap**: intervals that resample the 14 held-out blocks, not the 183 polygons (polygons in one block are not independent); beside the polygon intervals, for the maps and for T1. Needs per-polygon scores: `DL_UNet_Heldout_Scores_20261020` holds them for the four-class maps; the scorer does not write them yet. **From the same scores, where the errors sit:** a table of the 14 blocks against the classes (held-out area, polygons, the area each map gets right) for the four-class and both seven-class maps, and each class's score with its largest polygon left out. One polygon moves a class's area-weighted score by tens of points (Arsia Mons was 31 % of the four-class held-out Crater area, §68.2; one shuffle in A3 (a)'s null reached the published map's 0.738, §69.35) | honest intervals for a spatial test; the reader sees which blocks and polygons carry each score | desktop | A |
| A6 | **Agreement map**: where the SVM and U-Net maps agree, per class, as a share of ±60° and as a figure; four-class now, v2 after | shows where the two methods disagree, not only how each scores | desktop, minutes | B |
| A7 | **H2 with references for origin** (§4, T4 stage 1b): routed segments on Alemanno valleys as fluvial against segments on SIM 3292 volcanic units off them as volcanic; gradient and thermal z-score as in stage 1 | H2 tested by origin rather than by window, without waiting for 10 + 10 reviewed channels; still a stand-in, and stage 2 stays the authority if the review reaches it | desktop | B |
| A8 | **T9: thermal value on material labels** (§4): SIM 3292 unit groups as the labels at 400 m, the same block split, thermal ablated; also within blocks | answers the paper's own limit, "a test of thermal value needs material labels", with the only material map held | desktop, numpy | B |
| A9 | **Day IR at the contacts checked against topography**: T5 rerun with day IR residualised on hillshade and slope (day temperature follows slope facing the sun) | if the +8.7 pt lean vanishes, H1's hint is illumination; if it holds, it is stronger | desktop, minutes | B |
| A11 | **The breached-crater explanation tested**: recall by Robbins' morphology or degradation fields, if the 2020 release carries them **[?]** (columns not read), else by rim-height deficit on the DEM | the paper asserts why recall stops near one half; this measures it | desktop | B |
| A13 | **The review rule's sensitivity**: how many fluvial and apron rows change at floor depths of 10 and 30 m and median slopes of 0.5° and 1.5° | bounds how much the v2 labels depend on two thresholds | desktop, minutes | C |
| A15 | **Named features for the new classes**, the IAU-crater check (inside 0.7 R against a 1.5–2.5 R ring) extended: edifice on IAU Mons, Tholus and Patera (R from the gazetteer's `diameter`); fluvial channel on named valles, inside a buffer of the Alemanno valley lines within each vallis's extent against an outer buffer; lava tube on named catenae, listed one by one. In `MARS_nomenclature_misc_March2019` within ±60° (counted 10-31, by the first word of `type`): 32 edifice names (Mons 21, Patera 8, Tholus 3), 146 valles, 8 catenae; **19, 112 and 8 of them have no v2 label polygon at their centre**, and only those are scored. Even so the check is not independent: the edifice and fluvial labels were drawn from these names and the SIM 3292 units (§11.2 step 3), so it shows consistency, not accuracy | the three new classes get the named-feature baseline that Crater has in every score (Methods) | laptop, ArcGIS Python, ~1 h | C |

### 12.3 Small asks of the author (each after the candidate review, never ahead of it)

| # | what | adds | cost | pri |
|---|---|---|---|---|
| R1 | **A blind spot-check of the rule-screened rows**: 30 accepted and 10 rejected of each of fluvial and apron, shown without the rule's verdict; agreement gives the rule a measured precision | the paper can say how good the screen is, not only that it is one | ~45 min in Pro | A |
| R2 | **A probability-sample accuracy check** (Olofsson et al. 2014): stratified random points on the published map (and the U-Net and v2 maps), 25–50 per mapped class, labelled blind from the imagery with the maps hidden; a script writes the points class and scores it | unbiased map accuracy and area-adjusted class areas with intervals; hand-drawn polygons sit where a class is clear, so the polygon score flatters every map | ~2–3 h for ~200 points | A if any time is free |
| R3 | Lava margins at Athabasca, for H1 (already §6 step 4) | H1 tested at the stack's own scale | | |
| R4 | A few hills polygons in a third training block (§11.3) | only if v2 is rerun; otherwise the limit is stated | ~20 min | C |

### 12.4 The paper's text and figures

- **W2, the title** (D21): it promises "Mapping Lava Flows" though the lava flows come from the geologic map; a
  title that names the stack and what it can and cannot map would match the results.
- **W3, prior work**: the introduction cites the data but no earlier automated mapping, and the discussion compares
  with none. Candidates, **from memory and unchecked: each needs its DOI read before it enters `references.bib`**:
  automated crater detection (the DeLatte et al. 2019 review; Silburt et al. 2019); automated landform and valley
  mapping on Mars (Bue and Stepinski 2006; Luo and Stepinski 2009); deep learning on Mars landforms (Wilhelm et al.
  2020, DoMars16k); accuracy assessment (Olofsson et al. 2014). Alemanno et al. 2018 and Pontius and Millones 2011
  are in, checked by DOI (KB §69.18).
- **W4, figures** (page budget: 14 pages now): the pipeline in Methods (redrawn for seven classes,
  `final_img\pipeline.pdf` from `make_fig_pipeline.py`, KB §69.38; not yet in `build_final_paper.py`'s list);
  **the block split**, 39 blocks with the 14 held out and the polygons by class, so a reader can judge the
  spatial test; a type-area zoom of the published map against the imagery at full resolution; Perrotin found and Oudemans breached, the
  detector's limit in one panel; after v2, the seven-class map and its confusion; A6 if run, and A10's `final_img\crater_sfd.png` (KB §69.35).
- **W5, limits to add**: one labeller; the rule-screened v2 rows; hills short; THEMIS strips differ in local time,
  season and dust, a physical cause beside the stretch (to check in Edwards et al. 2011); Viking MDIM 2.1 colour is
  itself a balanced mosaic, so part of its albedo signal may be processing **[?]** (to check in the MDIM 2.1
  documentation).
- **W6, future work**: the outline's item 10 (§7) has no section in the paper: calibrated THEMIS inertia where it
  exists, CTX for margins, validation blocks for the deep-learning models, R2 if not done. Once the models have
  validation blocks, the seven-class U-Net's over-predicted edifice (§69.25; by A14 mostly on the highland group,
  §69.37) is the first target of any retraining.
- **W7, data availability** (D23): a DOI for the data release through Zenodo's GitHub link, cited as
  `Edwards2026data`, and a data statement as AAS asks. Publishing: the author's yes.
- **W8, the deck's half**: the paper's v2 text is drafted for both outcomes (`v2_drafts.tex`, KB §69.18) and the
  colours are `labelsets.COLOURS`, checked; `final.py`'s v2 slide (the seven-class map, its scores beside the
  four-class map's, D18's verdict) is still to draft, the same way. Laptop.
- **W9, the thermal claim** (D25): by balanced accuracy the thermal gain vanishes (−0.3 and +0.1 points, KB
  §69.18); the paper says so in Results, but the abstract and conclusions still give "a resolved 1.4 to 2.0
  points" alone. Whether they should carry the qualifier is the author's call.
- **W11, the values Methods leaves out**: the detector's, the router's and the SVM's thresholds are already in the
  prose (read 10-31), so a parameter table would repeat them on a tight page budget. Missing: the review rule's
  thresholds (fluvial, floor ≥ 20 m below a 4.8 km flank ring and `ShareVolc` < 0.5; apron, `SlopeMed` ≥ 1° and
  `CraterCover` < 0.5; KB §69.8), which §12.1's line and A13 need stated; the U-Net's batch of 8, 10 % of chips for
  validation, backbone unfrozen, 64-pixel padding at inference (`make_dl_pixels.py`). One sentence each, every
  value read from its script at the freeze. **B**, with §12.1.

### 12.5 The two talks

- **The interim, 10 Nov:** speaker notes on every slide; one timed run-through (the slot's length from the author);
  backup slides for the likely questions: why no calibrated thermal inertia, why the U-Net's 98.9 % is not the
  headline, what a held-out block is, what has changed since the cut (the v2 labels).
- **The final deck** (D24): rebuild it in the interim's dark `mars_theme` so the two talks look alike; `final.py`
  keeps the words.

### 12.6 Order of work

1. **Laptop, now:** W8's deck half; W3's candidates checked; A15 if cheap (A4, A12, W1 and the paper's half of W8
   done 10-27, KB §69.18; A14 and W10 done 10-31, §69.37–§69.38).
2. **Desktop:** the v2 scoring and D18 done (§11.5; A4b done 10-31, KB §69.34); next A1, A2, A3 (b) and (c) (its
   seven filter-and-score runs queue overnight), A5 with its block table, A6, then A7–A9 and A11 as time allows; A13
   if cheap.
3. **The author:** the candidate review (§6) first; then R1; R2 if any time is free.
4. **By 22 Nov:** the freeze; §12.1's lines and every result above that ran, into the KB, then `final.py` and the
   `.tex`; rebuild and read; `verify_interim.py` on both.

---

## 13. The repository and the project, beyond the paper (brainstormed 2026-10-27, laptop)

Read against the repository as it stands at `d3f79a5`; what was measured is KB §69.19. Same priorities as §12 (A,
before the freeze if at all possible; B, if time allows; C, only if cheap). None of it goes ahead of the author's
review (§6) or the v2 scoring (§11.5); most of it is laptop work that fills the wait for `run_v2.ps1`.

### 13.1 The work

| # | what | adds | where | pri |
|---|---|---|---|---|
| P4 | **The built documents committed at milestones only** (D26): the interim deck has been committed 22 times (498 MB of history) and the report 15 times (331 MB): nearly all of the 860 MB `.git` (KB §69.19). GitHub reports 720 MB and asks for under 1 GB. `github_sync.py` would skip the `.pptx`, `.docx` and paper `.pdf` unless given `--deliverables`, used once per deadline; between deadlines they are rebuilt from source on the drive and are not needed in the tree | stops ~25 MB per rebuild; the final's rebuilds alone would pass 1 GB at the interim's rate | laptop, minutes | A |
| P6 | **The paper compiled in CI**: a job that builds the `.tex` with TeX Live (a TeX Live container image is the likely source of `aastex701.cls` **[?]**, unchecked) and fails on an undefined reference or citation; the PDF kept as the run's artifact. The laptop then sees a compile without the desktop | catches what the laptop cannot (this session's edits are uncompiled); one more check before the freeze | laptop to write, CI to run | B |
| P7 | **A real restore**: `restore.py` has only ever been dry-run (KB §67.4). Restore one small release group into scratch on the desktop and compare every file with the drive by hash | the drive is the only full copy (§9); a backup is proven only by a restore | desktop, ~1 h | B |
| P8 | **The environment on the project page**: the versions are in KB §2.4 only (Pro 3.7, its Python 3.13.13, Deep Learning Libraries 3.7.1901, `arcgis.learn` 2.4.3). A short `docs/environment.md`: both Pythons, the system Python's packages (`python-pptx`, `python-docx`, matplotlib, Pillow) as a `requirements.txt`, MiKTeX and the AASTeX class version, the GPU and driver; written by a script on the desktop so it is read, not typed | a reader can tell what reproduces their run; the paper's data statement (W7) can point at it | desktop, minutes | B |
| P11 | **Which runs repeat exactly**: a table in the KB of each published number's run and whether a rerun reproduces it (a fixed seed, Pro's SVM, the U-Net's training); five build scripts name a seed | the paper's methods can say what is deterministic, and the freeze knows which reruns can move a number | laptop to read the scripts; the desktop for any rerun | C |
| P12 | **Closing the project, after 8 Dec** (D27): a tag `final-2026-12-08` and a final release (the deck, the paper's PDF, the maps); `CITATION.cff` given `version`, the DOI (D23), a `preferred-citation` for the paper and its date; the README's "Where it stands" turned into what was found; this plan closed with a header saying so; the memory and "Resume here" retired; D14's smoke classes settled | the repository reads as finished work, not a project paused mid-term | laptop, ~1 h, 9–12 Dec | after |
| P13 | **The maps viewable without ArcGIS, after 8 Dec and only if the project continues**: the two seven-class maps as cloud-optimised GeoTIFFs (`gdal_translate -of COG` under the ArcGIS Python, which has GDAL) in a release, and a simple web map of them on the project page | a reader can pan the maps in a browser instead of downloading 106,694 × 35,565-pixel rasters | laptop, ~2 h | after |

**The thermal wording beyond the paper** (D25, widened): the README's T1 section ("Yes, a little") and the interim
talk give the overall-accuracy gain alone. The interim's content is cut at 26 October (D20), but this result is a
reanalysis of logs that existed at the cut; one backup slide for "does thermal really help?" would answer the
question without changing the cut. The README follows whatever the paper says.

### 13.2 Order of work

1. **Laptop, now:** P4 (code only; its behaviour waits on D26). P1–P3 done 10-27 (KB §69.20), P2's first real use
   10-28 (§69.23); P9 and P10 done 10-31 (§69.34).
2. **Either machine:** P6.
3. **Desktop:** P7, P8.
4. **After 8 Dec:** P12; P13 if the project goes on.
