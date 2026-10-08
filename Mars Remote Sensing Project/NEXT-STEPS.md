# Mars Global Mosaic — next steps

Brainstormed 2026-10-08 and expanded the same day. **Two deadlines now, not one:**

| | due | days from 8 Oct |
|---|---|---|
| **Interim** report + presentation | **mid-November** (exact day not known) | ~36 |
| **Final** | **Tuesday 8 December 2026** | 61 |

Every status claim below was read from `PROJECT-KNOWLEDGE.md` (the record; § numbers point into
it) or from the project itself on 2026-10-08. This file is the plan; the record stays the
authority on what is true. When a step is done, record it there and strike it here.
**The interim has its own plan: `INTERIM-PLAN.md`** (staleness map, progress facts, hypothesis
status, deck formats, timeline). The drafts and the course template are in `NEXT STUFF\`.

---

## 0. Start of every session (two minutes, saves hours)

1. Which machine? (`hostname`; laptop = metadata and light raster work, desktop = heavy runs, §2.1)
2. Is `Z:` (or `F:` on the desktop) mounted? Is ArcGIS Pro closed before any write? (§13.3)
3. On the laptop: on AC? Lid open? (§28.9; battery check in the heavy-runs memory)
4. **What changed since last time?** Files changed on the drive, new rows in the gdb classes,
   new GP history (§29 shows how). Plan from that, not from this file's snapshot.
5. Which decisions in §2 have been answered? Strike them here, record them in the record.

---

## 1. Where the project stands against its own goal

The prospectus promises **one internally consistent landform inventory of three families —
lava flows, fluvial channels, impact craters — from a co-registered visible + thermal-IR mosaic.**

| | type area (Ius Chasma) | ±60° analysis extent |
|---|---|---|
| **Co-registered mosaic** | done, 100 m (§18) | done: G100/G200 grids, 7-band stack, layout 08 (§28, §31.2, §38) |
| **Craters** | 1,685 closed depressions ≥ 1 km, validated (§26) | only basins ≥ 20 km: 5,144, 68 % recall on IAU ≥ 100 km (§28.11) |
| **Channels** | 2,610 candidates, 188 worth the time (§25) | **nothing** |
| **Lava flows** | **nothing** | **nothing reliable**: the "lava tube" class is 39 % / 2 % (§31.3) |
| **Manual digitising** | the three `Landform_*` classes are **empty** | — |
| **Classification** | Iso Cluster + supervised on terrain labels (§19, §27) | SVM on the hand-drawn labels, held out 73.5 %, κ 0.58 (§32.2) |
| **Layouts** | 01, 02, 03, 06 | 04, 05, 07, 08 |

**The two gaps that matter most:** lava flows have no product at any scale, and nothing at ±60°
yet resolves craters or channels below 20 km. Both are fixable in the time left. The third gap,
the manual digitising, is the one only manual work can close, and it is still the critical path (§11 q16).

**The unproven central claim:** that thermal IR adds something visible light does not. It is
measured for band independence (§18.3) and as a local index (§24), but **never with the hand-drawn labels**.
The terrain labels of §27 gave +0.4 pt, which cannot settle it (§27.3). The 512 labelled polygons can.

**The project's own hypotheses (H1–H4) and questions (Q1–Q6) have not been tracked since
September.** Status table in `INTERIM-PLAN.md` §5: two hypotheses untested, one partly answered,
one answered by a different method; four of six questions answered. The tests in §4 below are
designed to close the rest.

---

## 2. Open decisions, each with a recommendation

These block or shape everything below. Ask them together, once.

| # | Decision | Recommendation |
|---|---|---|
| D1 | ~~Is the interim still owed?~~ **Answered 2026-10-08: owed, due mid-November; the exact day is not known.** ~~The template~~ **on `Z:` since 2026-10-08** (`NEXT STUFF\`). | Plan against ~13 November. Nothing left to ask. |
| D2 | What do the **interim and final** require: length, deck, poster, rubric? Is the final deck on the same template? | Get both rubrics now; they decide which layouts matter. |
| D3 | Run the **±60° crater + channel fine pass** (`make_global_landforms.py`, ~7 h, resumable) on the laptop overnight on AC, or wait for the desktop? | Laptop, lid open, on AC, if the desktop is days away. It was approved at 200 m on 2026-09-19; but §11 q18 says "ask before any hydrology at ±60°", so **confirm both in one answer**. |
| D4 | A **second type area at Athabasca Valles** (IAU: 153.2–156.8°E, 7.2–10.0°N, beside Cerberus Fossae)? | **Yes.** It is the project's own hook (§14.4): a channel mapped as fluvial for decades, now flood lava. The thermal index is valid locally (§28.10), so a type area is exactly where it can do work. Ius is fluvial/collapse; Athabasca is volcanic. Together they are the volcanic-versus-fluvial test, and tests T2, T4 and T5 below need it. |
| D5 | **Acquire reference data?** Each is a download, so each needs approval. Sources checked 2026-10-08, table below. | (a) and (d) first; (b) next; (c) only if a public file turns up. |
| D6 | The **lava tube class**: 10.7 % of the ±60° map, 2 % right where it says so. Keep, merge into steep/windy hills, or relabel? | Retrain without it, or with new polygons drawn from the geologic map's volcanic units (needs D5a). A class that is wrong 98 % of the time is worse than no class. |
| D7 | §11 **q23** (which class schema), **q26** (boxes or pixel labels for deep learning), **q27** (how much smoothing to publish). | q23 before any new samples. q26 only matters if deep learning goes ahead (X5). q27: keep 5 × 5, it was fixed by feature size (§32.2). |
| D8 | **Push to GitHub**: layout 08, §38–§39 and the two plan files are not mirrored yet (`build\github_sync.py --commit`). | Yes, after each working session. It is the only off-drive copy (§35). |
| D9 | **Housekeeping deletions** (all an open decision): the `*_60_smoke` feature classes, the 10 duplicate nomenclature classes (q4), the empty `Line`/`Point` classes, the dead Jezero HiRISE layer, `Z:\_removed_not_Mars\`. | Leave until after the final unless space runs out. The interim may list them as "cleared" only if they are. |
| D10 | **Digitising as review instead of drawing** (§6)? | Yes: it turns hours of drawing into minutes of accepting and rejecting, and keeps every decision manual. |
| D11 | ~~Interim deck format~~ **Answered 2026-10-08: the Presentation 1 style with graphics, no fixed slide count, rebuilt as the data moves.** Built the same day as a living deck (`INTERIM-PLAN.md` §0). | Rebuild after every new result; read every slide. |

### D5 in detail — what each download is, checked on the web 2026-10-08

| | dataset | source | size / form | what it unlocks | caveat |
|---|---|---|---|---|---|
| **a** | USGS **Geologic Map of Mars**, Tanaka et al. 2014, SIM 3292, 1:20 M | USGS, doi 10.3133/sim3292; public domain | ArcGIS file geodatabase (`SIM3292_geodatabase.gdb`), one feature dataset | the **only reference for lava flows** (volcanic units); the accuracy assessment the prospectus promised (§10) and the original schedule had in week 13 | stored in a **Robinson projection** on Mars 2000: project it before any overlay; check `Central_Meridian` (the three-frames trap, §4) |
| **b** | **Robbins & Hynek 2012** crater database (JGR 117, doi 10.1029/2011JE003966) | research-data repositories (GAVO / B2FIND records found); USGS Astrogeology hosting not confirmed **[?]** | a table: centres, diameters; morphometry only ≥ 3 km; statistically complete to ~1 km | scores the fine pass at **every size**, not only ≥ 100 km; turns 68 % recall into a size-resolved recall curve | the ≥ 1 km count is quoted inconsistently online (~384 k vs ~635 k in press) **[?]**: read it from the file; Prometheus basin excluded |
| **c** | **Hynek et al. 2010** valley networks (JGR 115, doi 10.1029/2009JE003548) | **no public download found**; possibly the paper's supplement, possibly the authors | lines, if obtainable | recall of the channel candidates against a published map | may need an email; skip if not public. A newer published network map may exist **[?]** |
| **d** | **TES thermal inertia**, Putzig & Mellon 2007 (Icarus 191) | PSI (`se.psi.edu/inertia/2007`), ASU Mars Global Data Sets, PDS Geosciences | 20 px/° (~3 km), 7200 × 3600, ~50 MB, dayside + nightside, **with interpolation masks** | the **calibrated** check of §28.10: does Viking albedo, or anything in the THEMIS pair, track real thermal inertia at ±60°? (test T3) | 3 km, not 100 m: a regional reference, not a layer to classify on. Use measured pixels only (the mask) |

---

## 3. What Claude can do on the laptop now (no decision needed unless marked)

Ranked by what they unblock. Each has a **done when** so "done" is checkable.

1. **Make the build scripts drive-independent.** 58 of the 100 scripts in `build\` hard-code `Z:`;
   on the desktop the drive is `F:` (§11 q22). Every desktop job below is blocked until this is
   fixed. One `paths.py` that finds the drive from the script's own location (the `github_*`
   scripts already do this), then grep for any `Z:` left, then smoke-test the two big scripts.
   *Done when: a grep finds no hard-coded drive outside `paths.py`, and `--smoke` runs with the
   drive letter changed (a `subst` alias proves it on the laptop).*
2. **Test T1, the thermal ablation** (§4). *Done when: held-out scores for every band set are
   in the record, whichever way they fall.*
3. **A graticule that renders.** `CIMGraticule` failed three times (§22.3). One can be added in
   the Pro GUI in seconds, but the builders wipe and rebuild each sheet, so a GUI graticule would
   be lost on the next rerun. A feature class of latitude/longitude lines every 30° (15° on type
   areas), labelled and added by the builders, survives reruns and is plain data. Every layout
   lacks coordinates now, and a remote-sensing grade looks for them.
   *Done when: every sheet's PNG shows labelled lines, and `polish_layouts.py` still finds
   nothing to change.*
4. **A locator/index sheet (layout 09):** ±60° Viking, the extent outline, boxes for Ius and
   (if D4) Athabasca, with the IAU names. `make_locator.py` makes this as a matplotlib figure; it
   should be a real layout. It is the interim's natural first map.
5. **Athabasca type area (if D4).** Window ~150–162°E, 4–14°N: about 7,100 × 5,900 px at 100 m,
   42 Mpx, the same order as Ius (37 Mpx), so every type-area step costs about what it did there
   (seconds to minutes). Chain: stack (§18), terrain (§20), diurnal-contrast index (§24), channel
   and crater candidates (§25, §26), a digitising map and layout like 06. Check the THEMIS night
   coverage and seams in the window first (§28.10 left the unit of normalisation unmeasured).
6. **Review fields for digitising (if D10, §6).** Add `Review` (accept / reject / unsure) to the
   candidate classes and a script that copies accepted rows into the `Landform_*` classes with
   `MappedBy` set to the reviewer. Never write into the digitising classes without an explicit accept.
7. **Validation layout for the manual digitising** (ready before digitising starts, filled in as it proceeds):
   candidates against the accepted features, recall per class, the breached craters the detector
   misses (§26.3). Scripted so it reruns in seconds after each session.
8. **After the fine pass:** two ±60° sheets, crater density ≥ 1 km and the channel network, each
   with the IAU check and the stated blind spots (closed depressions only; plateau channels are
   DEM noise, §25). Run `verify_global60.py` first (§28.4).
9. **After D5(a):** the lava-flow reference sheet and test T8 — the only route to a lava-flow
   result at ±60°.
10. **The figure lists for the interim and the final** (draft in §7), closed against D2's rubrics,
    so layouts are built to a list rather than by drift.

---

## 4. Tests that would turn work into results

Each is a measurement with a prediction written down **before** it runs, so the answer can
surprise. Cheapest first. All on the laptop unless marked.

| # | Question | Design | Cost | Needs |
|---|---|---|---|---|
| **T1** | **Does thermal IR improve classification, with the hand-drawn labels?** (the central claim) | The §31 split, unchanged. Band sets: all 7; without night + day IR; without Viking; thermal + terrain only. Fast pass: sample the stack under the labelled polygons, scikit-learn SVM per band set, held-out κ (minutes). Then confirm the best and the no-thermal set with Pro's SVM at 400 m. **Prediction:** at ±60° the thermal bands add little (§28.10); report it either way. | minutes; ~3.5 h per Pro run | nothing |
| **T2** | **Is Athabasca younger than Ius's plateau?** | Closed depressions ≥ 1 km per 10⁶ km² in each window, same detector, same filters. **Prediction [E]:** Athabasca's flood lavas are among the youngest surfaces on Mars, so far fewer craters. A size-frequency plot per window, **labelled "closed depressions", never used for an age** (the detector misses breached craters, §26.3). With D5b, use Robbins counts instead and compare. | minutes | D4 |
| **T3** | **Which of our layers tracks calibrated thermal inertia?** | Aggregate Viking red, the THEMIS day and night DN, and the contrast index to TES's 3 km grid over ±60°; correlate each with TES inertia on measured pixels only. **Prediction:** Viking correlates (dust = bright = low inertia), the THEMIS pair does not (local normalisation). This would turn §28.10 from an argument into a calibrated measurement. | ~1 h | D5d |
| **T4** | **H2: do volcanic and fluvial channels separate on gradient and thermal response?** | Channel slope and `ThermIdx` per segment: Ius candidates (fluvial/collapse) vs Athabasca candidates (volcanic), then the digitised `Origin` labels once they exist. The index is compared **within** each window only (§28.10), so test the separation inside each window against its own background. | minutes | D4; better with the hand-drawn labels |
| **T5** | **H1: does IR show flow margins Viking misses?** | Across the geologic map's volcanic contacts at Athabasca (or the digitised margins): edge contrast in Viking vs day IR vs night IR, sampled on perpendicular profiles. | ~1 h | D4 + D5a, or the digitised margins |
| **T6** | **H3: is the composite more stable than any single input?** | Iso Cluster 10 classes on Ius per input and on the composite; count surviving classes and their spatial coherence. | minutes | nothing |
| **T7** | **Q5: how many tributary orders does 100 m resolve?** | Sweep the flow-accumulation threshold on the cached routing rasters (§25: ~2 min each); Strahler order and network length per threshold; where does it saturate? | ~20 min | nothing |
| **T8** | **Accuracy against the geologic map** (the original schedule's week 13) | The SVM classes against SIM 3292 unit groups, confusion matrix; and the volcanic units as the lava-flow reference (D6). | ~1 h | D5a |

---

## 5. Desktop jobs (after step 3.1)

Order matters: the cheap tests first, so a failure costs minutes.

| # | Job | Cost | Why |
|---|---|---|---|
| X0 | Smoke-test the repathed scripts on `F:` | minutes | Nothing else is safe until this passes. |
| X1 | `GPU_THEN_CPU` test on the 2080 Ti (q10) | 5 min | Settles whether GPU is worth planning around, and q8. |
| X2 | Fine landforms pass, if not run on the laptop (D3) | ≤ 7 h | Craters and channels ≥ 1 km at ±60°. |
| X3 | 200 m classification (`--cell 200`) after D6 and T1 | ~15 h on the laptop; desktop unmeasured | The 400 m map resolves ~4 km features only (§32.2). Run it with T1's winning band set. |
| X4 | Pyramids on the four source globals (q6) | hours | Speeds up every pan and zoom in the GUI work, including digitising. |
| X5 | Deep-learning training on the 2080 Ti | hours | **Only after D6/D7**, and only if X1 says the GPU works. Lowest priority: the SVM is already scored, and a model trained on a broken class inherits it. |
| X6 | q24: read the 29 Sep `ClassifyRaster` settings | minutes | Closes a question; nothing depends on it. |

**A desktop day, when one is available:** X0 → X1 (alongside) → X2 or X3 started → X4 while it runs.

---

## 6. Manual GUI work, the critical path

- **Digitise in Ius Chasma** into the three empty classes, starting from layout 06's prompts:
  the 188 steep, rock-floored channel candidates; crater rims, **including the breached ones the
  detector cannot see**; lava flow margins wherever they are visible. Suggested minimum so the
  validation means something: ~30 channel segments, ~50 crater rims, every lava margin that can
  be defended. Re-export the gdb to GitHub after each session (§35.2).
- **Faster route (D10): review, then draw only what is missing.** `Review` is set on candidates
  (accept / reject / unsure) in the attribute table; a script copies the accepted ones into the
  digitising classes. Only what the machine missed is then drawn: breached craters, lava margins. Rejections
  are data too: they give the detector a precision figure.
- **If D4: the same at Athabasca**, where lava flow margins are the point.
- Answer D1–D10.
- **The original schedule** (interim `SCHEDULE`, September) had digitising on 19–30 Oct, the crater
  inventory on 2–13 Nov, accuracy against the geologic map on 16–20 Nov and layouts on 23–27 Nov.
  §8 keeps that order and moves the interim into it.

**If digitising slips** (the contingency, decided now so it isn't improvised in December):
the final still stands on the machine products, the 512 training polygons, the held-out scores
and the tests in §4. Every machine product is then presented as **candidates**, with its measured
recall, never as a landform map. Lava flows would rest on T8 and the geologic map alone.
**Trigger:** if the three `Landform_*` classes are still empty on **1 November**, write the interim
on this footing and say so in it.

---

## 7. Figures — what exists and what each deadline needs (draft; close against D2)

| # | sheet | exists | interim | final |
|---|---|---|---|---|
| 09 | locator: ±60° with the type areas | — (3.4) | ✓ first slide | ✓ |
| 08 | the mosaic at ±60°: visible, day, night, topography | ✓ (§38) | ✓ | ✓ |
| 01–02 | Ius visible; Ius night IR | ✓ | ✓ | ✓ |
| — | the province test: Viking separates, THEMIS doesn't | figure only (§28.10) | ✓ | ✓, with T3 if done |
| 03 | Ius Iso Cluster | ✓ | ✓ | maybe superseded |
| 06 | Ius digitising candidates | ✓ | ✓ | replaced by the validation sheet (3.7) |
| 07 | ±60° basins ≥ 20 km | ✓ | ✓ | ✓ |
| 04 | ±60° SVM landforms, scored | ✓ | ✓ | redone after D6 / X3 |
| 05 | the 29–30 Sep GUI SVMs checked | ✓ | ✓ (a lesson worth showing) | appendix |
| 10–11 | ±60° craters ≥ 1 km; ±60° channels | — (after X2) | if ready by the cut | ✓ |
| 12 | Athabasca type area | — (D4) | if ready | ✓ |
| 13 | lava-flow reference / accuracy vs geologic map | — (D5a) | — | ✓ |
| 14 | T1 ablation result | chart | if done | ✓ |

**Final report, an outline built on these** (to fill after the freeze, not before): 1 question
and hook (Athabasca) · 2 data and the ±60° decision · 3 co-registration and the trap · 4 the
thermal pair: what it can and cannot do (§18.3, §28.10, T1, T3) · 5 craters · 6 channels ·
7 lava flows · 8 classification and accuracy · 9 limits · 10 what next. Each section closes on
a measured number and a sheet.

---

## 8. Schedule to the two deadlines

**Assumes the interim is due ~13 November.** Redo the interim rows once the date is known.

| Window | Focus |
|---|---|
| **8–14 Oct** | D1–D10 answered. Scripts repathed (3.1). T1 fast pass. Graticule (3.3). Digitising or reviewing starts (§6). The interim deck is rebuilt after each result (`INTERIM-PLAN.md` §0). Fine pass overnight if D3 = laptop. |
| **15–25 Oct** | Desktop: X0, X1, X2 if still needed, X4. Athabasca type area (3.5); T2, T6, T7. Reference data in (D5); T3. Locator sheet (3.4). |
| **26 Oct – 1 Nov** | T1 confirmed in Pro; X3 with the winning band set. ±60° crater and channel sheets (3.8). **1 Nov: digitising checkpoint** (§6 contingency). |
| **2 Nov** | **Interim data cut.** Whatever is measured goes in; the rest goes to the final. |
| **2–12 Nov** | **Interim** per `INTERIM-PLAN.md` §6: rewrite `content.py`, rebuild, read every page, `verify_all.py` updated and green, review. Data work pauses except overnight runs. |
| **~13 Nov** | **Interim due.** |
| **14–22 Nov** | T4, T5, T8; validation sheet from the manual digitising (3.7); lava-flow sheet (3.9). **Data freeze 22 Nov.** Final figure list closed. GitHub release refreshed. |
| **23 Nov – 4 Dec** | The final report and deck, built from the layouts by the `build\` pipeline. Thanksgiving is 26 Nov: plan nothing that day. |
| **5–8 Dec** | Buffer and rehearsal. Nothing new. |

The freeze moved from 20 to 22 Nov because the interim takes ~10 days out of data work.

---

## 9. Risks to plan around

- **`Z:` is the only full copy** of a 250 GB project; GitHub holds the scripts, the vectors and
  the derived products, not the gdb's 138 GB. It has dropped off USB mid-write twice (§36.4). Big
  writes are built on internal disk and copied once; keep doing that. **Before each deadline,
  check the GitHub releases hold everything that deadline's figures need.**
- **Two deadlines three weeks apart** compete for the same days. The interim must not eat the
  final's data work: hence a hard cut on 2 Nov and documents built by script, not by hand.
- **The laptop sleeps** when the lid closes and runs down on battery. Long runs must checkpoint,
  and every elapsed time needs a rate check (§28.9).
- **The thermal argument is weaker at ±60° than the prospectus says** (§28.10). Write both
  documents around what is measured: local discrimination at the type areas, Viking albedo for
  planet-wide material, and T1/T3 whichever way they fall.
- **The interim report is still figure-free and September-dated**; the deck is fixed (living, seven
  map slides). Point the report at `interim.py` before the cut (`INTERIM-PLAN.md` §0 item 7).
- **The record still says "thermal inertia" in old sections** (§18.4, §19.3). Requoting them into
  a document would reintroduce the error (`INTERIM-PLAN.md` §7).
- **Projection of new data:** every download in D5 arrives in its own frame (SIM 3292 in
  Robinson). Misregistration is silent; check `Central_Meridian` per file (§4).
- **Scope creep:** every test in §4 is optional except T1. If time runs short, drop from the
  bottom of §4, never the digitising checkpoint or the cut dates.

---

## 10. Considered and ruled out, so they aren't proposed again

- **Segmentation at ±60°:** ~92 h at 14/14/30 (§23.6). Object-based work stays on type areas.
- **Calibrated thermal inertia from the held mosaics:** impossible, they are stretched 8-bit DN (§24).
  Calibrated inertia can only come from outside data (D5d), and then only at ~3 km.
- **Copying the project to internal disk:** ruled out manually (§2.2).
- **The 100 m Composite Bands run** (`make_global_stack.py`): overtaken by the 200 m stack; nothing waits on it (q7).
- **CRISM, SHARAD/MARSIS, a global CTX mosaic:** out of scope (§14, science goals).
- **Correcting the delivered prospectus or Presentation 1:** they are history (§1).
- **Crater ages from the closed-depression counts:** the detector misses breached craters by
  construction (§26.3); relative density between windows (T2) is the most it supports.
- **Claude digitising for the author:** the judgement is the point of task 11. Machine output stays in
  separate classes; only an explicit accept moves a row into them (§25, D10).
