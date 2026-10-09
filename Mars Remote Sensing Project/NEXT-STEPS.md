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

## Resume here — written at the end of the 2026-10-08 session (evening), updated 2026-10-09

> **Moving to the desktop? Read `HANDOFF-DESKTOP.md` first** (beside this file; KB §52): the first ten
> minutes there (`F:`, junctions, `desktop_check.py --gpu`), the working rules, and every open task
> audited on 2026-10-09 with its command, cost and "done when". The `.aprx` was verified to open whole
> on another drive letter.

**2026-10-09 (KB §50): every open decision is answered** (D2, D7, D9, D13; item 8 below). D9's deletions
are done; the deep-learning training export is redone from the training split for X5. The project:
23 maps, 12 layouts, 24 feature classes; `verify_all.py` 37 / 37 (two checks retired with the deleted data).
**Later 2026-10-09 (KB §51):** T4 stage 1 run (H2 not supported by window); the desktop day prepared
(`desktop_check.py --gpu` first; deep learning needs Esri's Deep Learning Libraries installed, absent on the
laptop); `make_dl_model.py` written with a tested scorer; layout 10's labels fixed; the interim rebuilt
(25 slides, 17 pages). **Nothing is left on the laptop that does not wait for the review, the desktop or an
install.** The next laptop work starts after a review session (item 2).

**Where it stopped.** All laptop work scheduled through 25 Oct (§8) is done, T5–T7 included (KB §47), and the interim deck and report are rebuilt with them (KB §48); the desktop jobs and the manual review are open.
**Latest (KB §49):** layout 13 (T8 against the geologic map) and layout 14 (the validation sheet) are in
the project; 24 maps, 12 layouts. Read before building them: **0 of 9,287 candidates reviewed**. Every
laptop item that does not wait for reviews, margins, the desktop or a decision is now done. Done:
T1, T2, T3 (local and planet-wide), T8, Athabasca (layout 09), the locator (layout 10), graticules,
the living interim deck and report, and the review fields for digitising (KB §40–§46). Checks green
on 2026-10-08: `audit_record.py`, `verify_all.py` 39 / 39, `neutral_voice.py`, the repo check;
pushed to GitHub, CI passed. **The three `Landform_*` digitising classes hold 0 rows.**
The same evening every plan was swept against KB §40–§46: this file, `INTERIM-PLAN.md` (§1–§5),
KB §11 (q14, q16–q19, q25) and the GitHub README's next steps now agree.

**Next, in this order:**

| # | what | who | where / how | done when |
|---|---|---|---|---|
| 1 | **Review the Ius candidates** in Pro, starting with "Channels: steep and rock-floored (188)", then the closed depressions; then Athabasca | manual (GUI) | §6 steps 1–4; `build\accept_reviewed.py` (dry run, then `--apply --by "<name>"`) | rows in `Landform_ChannelCenterlines` / `Landform_CraterRims`; tally printed |
| 2 | After each review session: run the copy, **refresh layout 14**, re-export the gdb to GitHub, push | Claude (laptop) | `accept_reviewed.py`; `make_validation_sheet.py` (Pro closed) then `polish_layouts.py`; `github_export_gdb.py`, then `github_sync.py` and the push (KB §35.2) | gdb export in the repo matches the drive; layout 14's table matches the tally |
| 3 | ~~**Validation sheet** (3.7)~~ **Done 2026-10-08 (KB §49):** layout 14, live in Pro, review precision and recall per class and window, the hand-drawn misses, the Robbins reference; tally tested on planted data (21 / 21, planted defect caught) | — | — | — |
| 4 | ~~**T6, T7, T5**~~ **Done 2026-10-08 (KB §47):** H1 inconclusive at the 1:20 M map's contacts (day IR leans its way, interval includes 0); H3 not supported (the composites are the least reproducible inputs); Q5 has no DEM-supported answer (no threshold keeps first-order streams on real slopes) | — | — | — |
| 4a | **T5 again on digitised margins:** rerun `make_flow_margin_test.py` against lava margins drawn at Athabasca (`Landform_LavaFlowMargins`), where the contact is known to a few pixels | Claude (laptop), after margins are drawn | the script needs a `--margins` source in place of the SIM 3292 contacts | H1 settled either way |
| 5 | ~~**T8 sheet** (§7 row 13)~~ **Done 2026-10-08 (KB §49):** layout 13, the cross-tabulation of all 12 unit groups from `logs\geomap_check.json` beside the map | — | — | — |
| 5a | ~~**At the next interim rebuild**~~ **Done 2026-10-09 (KB §51):** 25 slides, report 17 pages; 12 layouts, a T8 table and a T4 slide; every changed slide and page read, two faults fixed | — | — | — |
| 6 | ~~**Interim deck refresh**~~ **Done 2026-10-08 (KB §48):** 23 slides, report 15 pages; T5–T7 slides, review route, 10 layouts; a double-rounded κ and three report layout faults fixed. Next rebuild: after the next result (`INTERIM-PLAN.md` §0) | — | — | — |
| 6a | ~~**README results**~~ **Done 2026-10-08 (KB §48):** T1–T3, T5–T8 added to the GitHub README; the diurnal-contrast bullet qualified (§42.4) | — | — | — |
| 6b | **T4** (H2): ~~stage 1~~ **done 2026-10-09 (KB §51.1): not supported** by window (volcanic channels shallower; no thermal separation). Stage 2: on reviewed channels with `Origin` set | Claude (laptop) | `make_t4_channel_h2.py` reports stage 2 waiting until ≥ 10 fluvial and ≥ 10 volcanic exist | result in the record |
| 7 | **Desktop day** when available. **Start with `build\desktop_check.py --gpu`** (X0 + X1 + X5 preflight, KB §51.2). Deep learning (X5) first needs Esri's "Deep Learning Libraries" installed in Pro (absent on the laptop; a download, so asked first); then `make_dl_model.py --train`, `--detect`, `--score`. X0 junctions on `F:` → X1 GPU test → X2 fine pass (craters + channels ≥ 1 km at ±60°) → X4 pyramids alongside; X3 200 m classification next | desktop | §5 | X2 products verified (`verify_global60.py`); then 3.8 sheets |
| 8 | ~~**Decisions still open**~~ **All answered 2026-10-09 (KB §50):** D2 no rubric exists (§7 is the figure list); D7: q23 the labels' order, q25 deep learning yes on the corrected stack, q26 boxes, q27 keep 5 × 5; D9 deletions done; D13 keep the plateau candidates, reject in review | — | — | — |

**Dates that do not move:** digitising checkpoint **1 Nov** (still empty → the interim presents
candidates with recall, §6) · interim data cut **2 Nov** · interim ~**13 Nov** · data freeze
**22 Nov** · final **8 Dec**.

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
| **Lava flows** | none mapped; at Athabasca the geologic map's `lAv` unit is the reference (§42) | **reference layer**: SIM 3292 volcanic units on layout 10 (§44); the classifier cannot separate volcanic plains (§43.2–43.3) |
| **Manual digitising** | the three `Landform_*` classes are **empty** (0 rows, 2026-10-08); **review fields ready** (§46) | — |
| **Classification** | Iso Cluster + supervised on terrain labels (§19, §27) | SVM on the hand-drawn labels, held out 73.5 %, κ 0.58 (§32.2) |
| **Layouts** | 01, 02, 03, 06; 09 (Athabasca) | 04, 05, 07, 08; 10 (locator) |

**The two gaps that matter most:** lava flows are shown from the geologic map, not mapped from the
mosaic (no digitised margin yet), and nothing at ±60° yet resolves craters or channels below 20 km.
The third gap, the manual digitising, is the one only manual work can close, and it is still the
critical path (§11 q16). Since 2026-10-08 it starts as a review of the candidates (D10, §46).

**The central claim, now measured:** that thermal IR adds something visible light does not. Before
2026-10-08 it was measured for band independence (§18.3) and as a local index (§24) only; the
terrain labels of §27 gave +0.4 pt, which could not settle it (§27.3). **T1 used the 512 hand-drawn
polygons: +1.3 pt** (§40.1), and T3 checked the index against calibrated thermal inertia (§42.4, §43.1).

> **Status, end of 2026-10-08 (KB §40–§46).** Measured since this plan was written:
> - **T1:** the thermal bands add +1.3 pt [+0.6, +2.2] to the ±60° classification; slope + relief
>   alone match the full stack. The hand-drawn classes are landform classes.
> - **T3, local:** inside both type areas the diurnal-contrast index does **not** track calibrated TES
>   thermal inertia at 3 km (r −0.22 to ≈ 0); Viking albedo does at Athabasca (−0.55, −0.64).
> - **T2:** the Athabasca lava (`lAv`) is the least cratered large unit in its window (Robbins), about
>   half the older units' density.
> - **The crater detector:** only 11–13 % of its ≥ 1 km candidates are catalogued craters.
> - Reference data in the project (§41); Athabasca built (§42.1, layout 09); scripts run on any drive (§40.2).
> - Later the same day: T3 planet-wide and T8 (§43), graticules and layout 10 (§44), the living interim
>   report (§45), and **digitising by review ready** (D10, §46): the candidate tables carry a `Review`
>   drop-down, and `accept_reviewed.py` copies the accepts.
>
> **Consequence for both documents:** at every scale a calibrated product can check, visible albedo
> carries the material signal and the held THEMIS mosaics do not. The project's honest contribution
> is the co-registered mosaic, the scored products and these measured limits, not a thermal
> material map. Lava flows can now be mapped against the geologic map's volcanic units (T8).

**The project's own hypotheses (H1–H4) and questions (Q1–Q6), tracked again since 2026-10-08**
(status table in `INTERIM-PLAN.md` §5, KB §47.5): H1 tested and not supported at the geologic map's
1:20 M scale (rerun on digitised margins); H2 not supported at stage 1 (T4 by window, KB §51.1; stage 2
needs reviewed channels); H3 tested, not
supported; H4 answered by a different method. Q1, Q2, Q4 and Q5 answered, Q3 overtaken, Q6 unexamined.

---

## 2. Open decisions, each with a recommendation

These block or shape everything below. Ask them together, once.

| # | Decision | Recommendation |
|---|---|---|
| D1 | ~~Is the interim still owed?~~ **Answered 2026-10-08: owed, due mid-November; the exact day is not known.** ~~The template~~ **on `Z:` since 2026-10-08** (`NEXT STUFF\`). | Plan against ~13 November. Nothing left to ask. |
| D2 | ~~What do the **interim and final** require?~~ **Answered 2026-10-09: no rubric exists.** | Plan to the draft lists: §7 is the figure list for both deadlines; interim = the living deck and report (D11), final = the §7 outline. |
| D3 | ~~Where to run the ±60° crater + channel fine pass?~~ **Answered 2026-10-08: on the desktop** (X2), after the junctions there are recreated (X0, KB §40.2). | — |
| D4 | ~~A second type area at Athabasca Valles?~~ **Answered 2026-10-08: yes, build it** (3.5). | — |
| D5 | ~~Acquire reference data?~~ **Answered 2026-10-08: yes to (a) the USGS geologic map, (b) the Robbins crater database and (d) TES thermal inertia**; (c) has no public source. Stored under `Z:\Mars Project\Reference\`, not mirrored to GitHub (third-party data). | — |
| D6 | ~~The lava tube class?~~ **Settled 2026-10-08 (KB §43.3): the four hand-drawn classes stay** (the author's rule: never remove them; a fifth may be added if it helps). Relabel, drop and a fifth "volcanic (map)" class were tested at 1.6 km; the fifth class scored below chance and cost the others 5.6 pt, so **no fifth class and no rerun**. Lava flows come from the geologic map's volcanic units, as a reference layer. | — |
| D7 | ~~§11 **q23**, **q25**, **q26**, **q27**~~ **Answered 2026-10-09 (KB §50):** q23 the labels' order (1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground; the `.ecs` is superseded); q25 **yes**, deep learning on the corrected stack (X5); q26 **boxes**, as exported; q27 **keep 5 × 5**. | q23 before any new samples. q25 and q26 only matter if deep learning goes ahead (X5); the corrected stack is already what every scored product uses. q27: keep 5 × 5, it was fixed by feature size (§32.2). |
| D8 | ~~Push to GitHub?~~ **Answered 2026-10-08: push after each working session**, once the record audit, the voice check and the repo's own check pass. | — |
| D9 | ~~**Housekeeping deletions**~~ **Answered and done 2026-10-09 (KB §50):** the two `*_60_smoke` classes, the 9 (not 10) identical nomenclature copies, `Line`/`Point`, the map holding only the dead Jezero HiRISE layer; `Z:\_removed_not_Mars\` to the Recycle Bin. Backups on the laptop's internal disk. | The interim may list them as cleared. |
| D10 | ~~Digitising as review instead of drawing?~~ **Answered 2026-10-08: yes.** Review fields and `accept_reviewed.py` built the same day (3.6, KB §46); workflow in §6. | — |
| D11 | ~~Interim deck format~~ **Answered 2026-10-08: the Presentation 1 style with graphics, no fixed slide count, rebuilt as the data moves.** Built the same day as a living deck (`INTERIM-PLAN.md` §0). | Rebuild after every new result; read every slide. |
| D13 | **Answered 2026-10-09: keep, reject in review.** §11 **q17**: prune the 2,422 channel candidates outside the steep, rock-floored subset (64 % on ground under 2°)? | **No:** with the review (§46) they cost one "reject" each and the rejections become the detector's precision. Review the 188 first; leave the rest as prompts. |
| D12 | ~~How to present the thermal claim, after T1 and T3?~~ **Answered 2026-10-08: lead with the measured limits.** The results are the co-registered mosaic, the scored products and the limits: visible albedo carries the material signal at every scale a calibrated product can check; the held THEMIS mosaics do not. | — |

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

1. ~~**Make the build scripts drive-independent.**~~ **Done 2026-10-08 (KB §40.2).** Left: the junctions on `F:` (X0). 58 of the 100 scripts in `build\` hard-code `Z:`;
   on the desktop the drive is `F:` (§11 q22). Every desktop job below is blocked until this is
   fixed. One `paths.py` that finds the drive from the script's own location (the `github_*`
   scripts already do this), then grep for any `Z:` left, then smoke-test the two big scripts.
   *Done when: a grep finds no hard-coded drive outside `paths.py`, and `--smoke` runs with the
   drive letter changed (a `subst` alias proves it on the laptop).*
2. ~~**Test T1, the thermal ablation** (§4).~~ **Done 2026-10-08 (KB §40.1): thermal +1.3 pt [+0.6, +2.2]; terrain alone matches the full stack; the labels are landform classes.** Optional: confirm with Pro's SVM. *Done when: held-out scores for every band set are
   in the record, whichever way they fall.*
3. ~~**A graticule that renders.**~~ **Done 2026-10-08 (KB §44).** `CIMGraticule` failed three times (§22.3). One can be added in
   the Pro GUI in seconds, but the builders wipe and rebuild each sheet, so a GUI graticule would
   be lost on the next rerun. A feature class of latitude/longitude lines every 30° (15° on type
   areas), labelled and added by the builders, survives reruns and is plain data. Every layout
   lacks coordinates now, and a remote-sensing grade looks for them.
   *Done when: every sheet's PNG shows labelled lines, and `polish_layouts.py` still finds
   nothing to change.*
4. ~~**A locator/index sheet:**~~ **Done 2026-10-08 as layout 10 (KB §44).** ±60° Viking, the extent outline, boxes for Ius and
   (if D4) Athabasca, with the IAU names. `make_locator.py` makes this as a matplotlib figure; it
   should be a real layout. It is the interim's natural first map.
5. ~~**Athabasca type area (if D4).**~~ **Done 2026-10-08 (KB §42.1, layout 09).** Window ~150–162°E, 4–14°N: about 7,100 × 5,900 px at 100 m,
   42 Mpx, the same order as Ius (37 Mpx), so every type-area step costs about what it did there
   (seconds to minutes). Chain: stack (§18), terrain (§20), diurnal-contrast index (§24), channel
   and crater candidates (§25, §26), a digitising map and layout like 06. Check the THEMIS night
   coverage and seams in the window first (§28.10 left the unit of normalisation unmeasured).
6. ~~**Review fields for digitising (if D10, §6).**~~ **Done 2026-10-08 (KB §46):** `Review` (domain
   accept / reject / unsure) and `ReviewNote` on the four candidate classes, `SourceID` on the
   channel and crater digitising classes, `build\accept_reviewed.py` (dry run by default; `--apply
   --by "<name>"` copies accepts only, `MappedBy` = the reviewer). Rehearsed on a scratch gdb,
   15 / 15 checks including two planted defects.
7. ~~**Validation layout for the manual digitising**~~ **Done 2026-10-08 as layout 14 (KB §49);** rerun `make_validation_sheet.py` after each review session (ready before digitising starts, filled in as it proceeds):
   candidates against the accepted features, recall per class, the breached craters the detector
   misses (§26.3). Scripted so it reruns in seconds after each session.
8. **After the fine pass:** two ±60° sheets, crater density ≥ 1 km and the channel network, each
   with the IAU check and the stated blind spots (closed depressions only; plateau channels are
   DEM noise, §25). Run `verify_global60.py` first (§28.4).
9. ~~**After D5(a):** the lava-flow reference sheet and test T8.~~ **Done 2026-10-08:** T8 measured
   (KB §43.2); the volcanic units are the lava-flow reference on layout 10 (§44). T8's sheet is
   layout 13 (§49).
10. ~~**The figure lists for the interim and the final**~~ **Settled 2026-10-09:** no rubric exists (D2),
    so §7 is the list; layouts are built to it rather than by drift.

---

## 4. Tests that would turn work into results

Each is a measurement with a prediction written down **before** it runs, so the answer can
surprise. Cheapest first. All on the laptop unless marked.

| # | Question | Design | Cost | Needs |
|---|---|---|---|---|
| **T1** ✓ | **Does thermal IR improve classification, with the hand-drawn labels?** (the central claim) | The §31 split, unchanged. Band sets: all 7; without night + day IR; without Viking; thermal + terrain only. Fast pass: sample the stack under the labelled polygons, scikit-learn SVM per band set, held-out κ (minutes). Then confirm the best and the no-thermal set with Pro's SVM at 400 m. **Prediction:** at ±60° the thermal bands add little (§28.10); report it either way. | minutes; ~3.5 h per Pro run | nothing |
| **T2** ✓ | **Is Athabasca younger than Ius's plateau?** | Closed depressions ≥ 1 km per 10⁶ km² in each window, same detector, same filters. **Prediction [E]:** Athabasca's flood lavas are among the youngest surfaces on Mars, so far fewer craters. A size-frequency plot per window, **labelled "closed depressions", never used for an age** (the detector misses breached craters, §26.3). With D5b, use Robbins counts instead and compare. | minutes | D4 |
| **T3** ✓ (local §42.4, planet-wide §43.1) | **Which of our layers tracks calibrated thermal inertia?** | Aggregate Viking red, the THEMIS day and night DN, and the contrast index to TES's 3 km grid over ±60°; correlate each with TES inertia on measured pixels only. **Prediction:** Viking correlates (dust = bright = low inertia), the THEMIS pair does not (local normalisation). This would turn §28.10 from an argument into a calibrated measurement. | ~1 h | D5d |
| **T4** | **H2: do volcanic and fluvial channels separate on gradient and thermal response?** | Channel slope and `ThermIdx` per segment: Ius candidates (fluvial/collapse) vs Athabasca candidates (volcanic), then the digitised `Origin` labels once they exist. The index is compared **within** each window only (§28.10), so test the separation inside each window against its own background. | minutes | ~~D4~~ ready (Athabasca built, §42.1); **better after review**: accepted channels with `Origin` set (§46) |
| **T5** ✓ at 1:20 M (§47.2; inconclusive, rerun on digitised margins) | **H1: does IR show flow margins Viking misses?** | Across the geologic map's volcanic contacts at Athabasca (or the digitised margins): edge contrast in Viking vs day IR vs night IR, sampled on perpendicular profiles. | ~1 h | ~~D4 + D5a~~ **ready now**: Athabasca (§42.1) and SIM 3292 (§41) are in the project |
| **T6** ✓ (§47.3; H3 not supported) | **H3: is the composite more stable than any single input?** | Iso Cluster 10 classes on Ius per input and on the composite; count surviving classes and their spatial coherence. | minutes | nothing |
| **T7** ✓ (§47.4; no DEM-supported order count) | **Q5: how many tributary orders does 100 m resolve?** | Sweep the flow-accumulation threshold on the cached routing rasters (§25: ~2 min each); Strahler order and network length per threshold; where does it saturate? | ~20 min | nothing |
| **T8** ✓ | **Accuracy against the geologic map** (the original schedule's week 13) | The SVM classes against SIM 3292 unit groups, confusion matrix; and the volcanic units as the lava-flow reference (D6). | ~1 h | D5a |

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
| X5 | Deep-learning training on the 2080 Ti | hours | **Approved 2026-10-09 (q25, KB §50)**, only if X1 says the GPU works. Train on `LabeledObjects\global60_svm_stack_200m_train\` (the training split only, boxes), never on the all-labels export; score on the 183 held-out polygons as the SVM was (§31.3). After X2–X4. |
| X6 | q24: read the 29 Sep `ClassifyRaster` settings | minutes | Closes a question; nothing depends on it. |
| X7 | q12, optional: one source global rewritten as an internally tiled, compressed copy, timed against the original | ~1 h | Tests the I/O ceiling fix (§2.2); only if X4's pyramids leave panning slow. Needs space on the drive. |

**A desktop day, when one is available:** X0 → X1 (alongside) → X2 or X3 started → X4 while it runs.

---

## 6. Manual GUI work, the critical path

- **Digitise in Ius Chasma** into the three empty classes, starting from layout 06's prompts:
  the 188 steep, rock-floored channel candidates; crater rims, **including the breached ones the
  detector cannot see**; lava flow margins wherever they are visible. Suggested minimum so the
  validation means something: ~30 channel segments, ~50 crater rims, every lava margin that can
  be defended. Re-export the gdb to GitHub after each session (§35.2).
- **Faster route (D10, ready since 2026-10-08, KB §46): review, then draw only what is missing.**
  1. Open the map "Ius Chasma — digitising" (or "Athabasca Valles — digitising"); start with the
     layer "Channels: steep and rock-floored (188)", then "Closed depressions ≥ 1 km".
  2. In the layer's attribute table, set `Review` from the drop-down (accept / reject / unsure); add
     a `ReviewNote` if useful. Before accepting, set `Origin` (channels: fluvial / volcanic /
     indeterminate), `Preservation` (craters: fresh / degraded / ghost) and `Confidence`
     (certain / probable / inferred) on the candidate row; they are copied as they stand.
  3. Save edits. Run, with the ArcGIS Pro Python, `build\accept_reviewed.py` (dry run: the tally and
     the precision so far), then `accept_reviewed.py --apply --by "<name>"`. Reruns copy only new accepts.
     Then refresh layout 14 (Pro closed): `make_validation_sheet.py`, then `polish_layouts.py` (KB §49).
  4. Draw what the machine missed directly in the digitising classes: breached craters, lava margins.
  Rejections are data too: they give the detector a precision figure (3.7).
- **The same at Athabasca** (built, layout 09, map "Athabasca Valles — digitising"), where lava flow
  margins are the point; the `lAv` unit of the geologic map shows where to look (§42).
- ~~Answer the open decisions: D2, D7, D9.~~ All answered 2026-10-09.
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

## 7. Figures — what exists and what each deadline needs (the list: no rubric exists, D2)

| # | sheet | exists | interim | final |
|---|---|---|---|---|
| 10 | locator: ±60° with both type areas and the volcanic units (lava-flow reference) | ✓ (§44) | ✓ first slide | ✓ |
| 08 | the mosaic at ±60°: visible, day, night, topography | ✓ (§38) | ✓ | ✓ |
| 01–02 | Ius visible; Ius night IR | ✓ | ✓ | ✓ |
| — | the province test: Viking separates, THEMIS doesn't | figure only (§28.10) | ✓ | ✓ |
| — | T3: the layers against calibrated TES thermal inertia | chart `tes_check.png` (§43.1, §45) | ✓ | ✓ |
| 03 | Ius Iso Cluster | ✓ | ✓ | maybe superseded |
| 06 | Ius digitising candidates | ✓ | ✓ | replaced by the validation sheet (3.7) |
| 09 | Athabasca type area, digitising candidates | ✓ (§42.1) | ✓ | ✓ |
| 07 | ±60° basins ≥ 20 km | ✓ | ✓ | ✓ |
| 04 | ±60° SVM landforms, scored | ✓ | ✓ | redone after X3 (D6 settled, §43.3) |
| 05 | the 29–30 Sep GUI SVMs checked | ✓ | ✓ (a lesson worth showing) | appendix |
| — | T1 ablation result | chart `thermal_ablation.png` (§40.1) | ✓ | ✓ |
| 11–12 | ±60° craters ≥ 1 km; ±60° channels | — (after X2) | if ready by the cut | ✓ |
| 13 | accuracy against the geologic map (T8) | ✓ layout 13 (§49) | optional | ✓ |
| 14 | validation of the manual digitising (3.7) | ✓ layout 14 (§49); fills as reviews arrive | if reviewing has started | ✓ |

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
| **8–14 Oct** | ~~D1–D13 answered~~ (all by 2026-10-09). ~~Scripts repathed (3.1). T1 fast pass. Graticule (3.3).~~ Done 2026-10-08. Digitising or reviewing starts (§6; fields ready, §46). The interim deck is rebuilt after each result (`INTERIM-PLAN.md` §0). Fine pass overnight if D3 = laptop. |
| **15–25 Oct** | Desktop: X0, X1, X2 if still needed, X4. ~~Athabasca type area (3.5); T2~~, T6, T7. ~~Reference data in (D5); T3. Locator sheet (3.4).~~ (struck items done 2026-10-08) Validation sheet (3.7) once reviews exist. |
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
- ~~The interim report is still figure-free and September-dated.~~ **Fixed 2026-10-08 (§45):** deck
  and report are both living builds from `interim.py`; the risk now is drift between rebuilds, so
  run `verify_interim.py` after each one.
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
