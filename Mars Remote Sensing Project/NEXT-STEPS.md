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

## Resume here — 2026-10-26

**2026-10-27, laptop, without the drive (KB §69.10): copy to the drive before the next `github_sync.py`.** The
interim refined for the 10 November presentation, the 26 Oct cut kept (the author's choice): the T4 and T8 charts
redrawn at 200 dpi, the U-Net slide's legend moved clear of its takeaways, the title slide's subtitle no longer
repeats the title, the schedule gives 10 Nov; both documents rebuilt (30 slides, 21 pages, 285 numbers). Then
the deck redesigned at the author's request (KB §69.11), repainted navy (§69.12), then dark throughout with navy-ground figures (§69.13,
`make_interim_dark.py`; its `interim_img\dark\` is git-ignored: rerun it on the drive): `mars_theme.py`, 31 slides, words and numbers unchanged
(294 numbers with the four on the results divider), then refined (§69.14: tighter maps, one legend scale, verdicts on the hypothesis slides, the backgrounds' graticule painted out; 295 numbers), then given a "For scale" slide (§69.15: each band's 15° block against the nearest US state, Texas or California; new `build/interim_block_scale.py`; 32 slides, 325 numbers), and its graphics refined (§69.16: a ±60° grid strip on each block card, wide legends restacked to be read, a hidden dark swatch on a grey chip, Athabasca's legend beside its map); `le_theme.py` and the report untouched. These
files were written in the clone only: `git diff --name-only e6ec284 HEAD -- "Mars Remote Sensing Project"` (the
desktop's v2 run writes only `build\logs\run_v2\` and `Global60\`).
**On the desktop, first** (KB §69.20): the drive's `github_sync.py` predates the guard, so run the clone's
copy against the drive: `python "<clone>\Mars Remote Sensing Project\build\github_sync.py" --drive F:\
--to-drive e6ec284 --dry-run`, read it, then again without `--dry-run`. It copies each file the clone changed
since `e6ec284` whose drive copy is still `e6ec284`'s, and lists any the drive changed too (merge those by
hand) and any the clone has not committed. Close the deck in PowerPoint first (a locked file is listed, not
copied). Only then `github_sync.py` as usual; if it ever refuses (exit 3), it names the commit to pass.
**Done 10-28, desktop (KB §69.23):** all 25 copied (none changed on both sides; the `--to-drive` dry run now
reports 0 to copy), `interim_img\dark\` with them. A restart on 10-27 at 21:18 stopped `run_v2.ps1` after 12 of
step 01's 21 tiles; resumed 10-28 02:29 with `-ClassifyOnly` on the trained model (SVM results ~17:00 10-28,
U-Net ~14:00 10-29).
**Later 10-27, laptop (KB §69.17):** a brainstorm of what would strengthen the final paper, now **§12** of this
plan: the paper's lines the freeze must change (§12.1), thirteen analyses that need no author time (A1–A13; first,
after the v2 scoring: the channels scored against the valley map, T1 on v2, spatial baselines for the held-out score,
block-bootstrap intervals), two small blind checks for the author (R1, R2), the text and figures (W1–W8), the two
talks, and an order of work (§12.6). Four new decisions for the author, D21–D24 (§2).
**Later 10-27, laptop (KB §69.18):** §12.6 step 1 mostly done. New `build\score_metrics.py`: balanced accuracy,
F1 and quantity / allocation disagreement from the logs. The published map's error is mostly quantity (20.5 of
26.2 points), and **by balanced accuracy the thermal gain vanishes** (D25). The paper: abstract at 250 words,
Table 3 widened, its limits brought current, two references checked by DOI, the v2 text drafted for both outcomes
(`v2_drafts.tex`); `final.py`'s review limit fixed. **Not compiled** (no AASTeX on the laptop): rebuild the PDF on
the desktop and read it. Copy to the drive with the rest (the list is under the first paragraph above).
**Later 10-27, laptop (KB §69.19):** a second brainstorm, on the repository and the project rather than the paper,
now **§13**: the number checks into CI (P1), a guard so `github_sync.py` cannot revert clone-only edits (P2), the
vector-layer guide brought true (P3), the built documents committed at milestones only (P4: they are nearly all of the
860 MB history), the paper compiled in CI (P6), a real restore (P7), and closing the project
after 8 Dec (P12). Two new decisions, D26 and D27; D25 widened to the README and an interim backup slide.
**Later 10-27, laptop (KB §69.20):** P1–P3 done. `tools/check_repo.py` (CI) now runs the number checks on the
interim, the final deck and the paper, reruns `score_metrics.py` against its stored file, and checks every layer
in `exports/README.md` is described. `github_sync.py` refuses to copy over or delete clone-only work, and
`--to-drive <commit>` does the clone → drive copy (the paragraph on the desktop above); tested on a scratch
drive and clone, and against this clone's history with a drive as of `e6ec284` (20 files to copy). The vector-
layer guide describes the v2 labels and the reviewed layers. Nothing new on the drive: copy with the rest.
**Later 10-27, laptop (KB §69.21):** the interim reviewed for truth at the author's request: five corrections (THEMIS
is band 9, 12.57 µm; layout 05 has no graticule; 2,077 m is the maximum fill raise; one Arsia label, not Arsia
alone; H1 "not supported" as the rule says), the status brought to 27 October with the 26 October results cut kept
(the review begun, the v2 labels applied), and the thermal gain qualified by balanced accuracy (D25 for the
interim, the author's yes). Rebuilt: 32 slides, 21 pages, 334 numbers; read. Clone-only: copy with the rest.
Then every graphic checked against its log or record (KB §69.22): all agree but one. **On the desktop:** layout 11's
lower panel says "Robbins & Hynek (2020)" (the citation is 2012, the 2020 release); the script is fixed, so
rerun `make_global60_candidate_sheets.py` and `polish_layouts.py`, re-export layout 11, `make_interim_figs.py`,
`make_interim_dark.py`, rebuild both interim documents, `tools/make_thumbs.py`; and `make_fig_checks.py` for
`t2_density.png`.

**Where it stands.** Every scripted job up to the review is done and recorded (KB §53–§57): the ±60°
fine pass (465,354 closed depressions ≥ 1 km, 969,822 channel segments, layouts 11–12); the 180° DEM
column fixed at its source (§54); the 200 m classification, **published as the 200 m map with an 11 × 11
(2.2 km) majority filter, 73.8 %, κ 0.58 held out** (§55.3, §57), the 400 m map superseded (§57.2);
T1 confirmed with Pro's SVM (thermal +1.36 pt at 200 m, +1.97 at 400 m, §56); T8 rerun on the published map
(§57.1); the interim rebuilt, 28 slides and 20 pages (§57.3); GitHub release `data-2026-10-16` (§57.4).
The project: 32 maps, 17 layouts (§63, §66.4, §66.9); nothing is running on the desktop.
**2026-10-18, laptop (§58–§61):** no new data since; the drive-root junctions point at `F:` and are broken on
the laptop (retarget before any Spatial Analyst run there); the record and the plans condensed, two scripts freed
from a hard-coded `F:`, every sheet re-polished and the interim rebuilt from them, nothing measured changed.
**2026-10-19, laptop (§62):** the province figure redrawn light from §28.10's tables (47.67 DN covers four
provinces, −0.0009 seven); slide 11 updated; the interim rebuilt, 28 slides and 19 pages.
**2026-10-19, laptop (§63):** layout 15 added, the Athabasca Valles type area in visible, night IR, day IR and
topography with unit `lAv`; every footer now gives "Logan M Edwards"; 08's caption no longer names Tharsis.
The interim deck still says 14 layouts and does not show 15 (the author's call: leave it for now).
Release `data-2026-10-19` (§63.2) adds `athabasca.zip`: both type areas are now backed up; `check_remote.py` passes.
**2026-10-19, laptop (§64):** all 15 sheets read again for quality and accuracy: 08 now centred on 0°E like the
other ±60° sheets, with a graticule; 09's map enlarged; type-area footers name their CRS; scale bars, legends,
11's table and 13's footer kept inside the page margin. Three results drawn as charts for the first time
(`make_fig_checks.py`: the published map's confusion and filter sweep, T2, the lava-tube relabel). The interim
deck's crop of 08 predates the recentring (deck left as it is).
**2026-10-19, laptop (§65):** four type-area results (segmentation sweep, diurnal-contrast index, `Fill` trap,
closed depressions with Oudemans / Perrotin) drawn light for the repo with `--light`, wording brought to the
record; §25.1's flooded share corrected to 21.7 %; layout 07's size classes rounded; 03's legend titled, and
`polish_layouts.py` now idempotent on every sheet.
**2026-10-19, desktop (§66):** the Deep Learning Libraries 3.7.1901 installed (the author answered the UAC prompt);
`desktop_check.py --gpu` says X5 is ready to train on the 2080 Ti. **X5 trained (§66.1):** RetinaNet takes the 7 bands,
25 min, early-stopped, epoch 3 kept; validation AP ≤ 0.010 per class. **Detected and scored (§66.2)**, one window per
held-out block (a mask broke the tool): Crater recall 41.9 %, precision 87.6 % (all-Crater baseline 71.1 %); Normal
Ground 22.7 % and 56.9 % (baseline 20.9 %); hills and lava tube never predicted. **In the gdb and the `.aprx` (§66.3)**:
`DL_Detections_heldout_20261019` and the map "X5 — deep-learning detections (held out)"; **layout 16** (§66.4).
**2026-10-20, desktop (§66.4):** layout 16 built and read; the interim's deep-learning next step and schedule line
brought current (no X5 slide added: the author's call); rebuilt, only slide 28 and report page 19 changed.
**2026-10-20, desktop (§66.5–66.6), at the author's request to improve the detector:** **X5b**, RetinaNet retrained
with the backbone unfrozen, no early stopping (30 epochs, epoch 16 kept), rare-class chips (`make_global60_dl_export.py
--rare`) and edge slivers dropped (`make_dl_model.py --prepare`): names hills (25 % recall, 100 % precision) and
Crater at 100 % precision, but Normal Ground recall fell to 4.5 % and lava tube is over-predicted on craters, so
**not improved** by its rule. **X5c**, a U-Net pixel classifier (the author's yes, reversing q26 for this model,
`make_dl_pixels.py`): **98.75 %, κ 0.977 held out** against the published SVM map's 73.8 %, κ 0.583 under the same
scorer; lava tube user's 70.7 % (SVM 2.4 %); a map of terrain provinces with tile seams, only in the 14 windows.
**2026-10-20, desktop (§66.7), the author's yes:** X5c over all of ±60° in 5 h 46 min,
`Global60\global60_landforms_unet_200m.tif`: held out 98.8 %, κ 0.979; IAU craters 'Crater' inside 91 % against ring
82 % (SVM 57 / 46 %); elevation bins reproduce 68 % (SVM 55 %); **seams at the tool's 256 px tiles** (ratio 8.6–9.2,
SVM ~1.0), not removed by padding 112 or test-time augmentation.
**2026-10-21, desktop (§66.8), the author's yes:** a second pass offset by 128 px, each pixel from the pass farther
from a tile edge: `Global60\global60_landforms_unet_200m_seamfix.tif`, seams 8.6–9.2 → **1.2**, held out **98.9 %,
κ 0.980**, crater test and elevation unchanged. Nothing is running on the desktop.
**2026-10-21, desktop (§66.9), the author's decision:** the SVM map stays the published one; the two-pass U-Net
map joins the project beside it as the province map: map "X5c — U-Net terrain provinces (±60°)", layout
**17_x5c_unet_provinces**, and `DL_UNet_Heldout_Scores_20261020` (each held-out polygon under both maps).
**2026-10-21, desktop (§66.10), the author's request:** the interim gains two deep-learning slides (layouts 16 and
17; 30 slides, report 21 pages, every changed page read). Release **`data-2026-10-21`**, 12 assets, 7.71 GB: the
GeoPackage with all 28 classes, both U-Net maps and, new, `dl-models.zip` (the three trained models);
`check_remote.py` passes, the quick start reproduces, the catalogues point at it.
**2026-10-22, desktop (§67), the author's request:** the layouts and images audited. All 17 sheets re-export
pixel-identical to their PNGs on the drive and in the repo, and the drive and the clone are in sync. The interim's
crops of 01, 02 and 04–11 predated §63–§65 (08 not recentred, 07's old size classes, 09's smaller map): at the
author's word all 13 were re-exported and the deck and report rebuilt (30 slides, 21 pages, text unchanged), every
changed page read. Stale counts fixed in the README, `docs/figures.md`, the handoff and the interim plan.
The repo's pages now show 800 px previews (`tools/make_thumbs.py`, §67.1): the README's images fell from
25.5 MB to 3.2 MB; CI checks alt text, inline size and that each preview matches its source. The README gains
a deep-learning results section; its next steps hold only what is open. A writing pass (§67.2) removed named
AI-prose patterns from the pages and the sheets: em dashes in the 17 sheets' titles, "What it is / is not", colon
reveals, capitals for emphasis; the builders carry the same text. Numbers untouched; the deck's 05 crop rebuilt.
Then (§67.3–67.5): the script catalogue regrouped, stale docstrings fixed, the U-Net in the pipeline diagram; every
number on the pages checked against the record; the drive measured at 429 GB; "#section" links checked in CI; the
clone's two orphan pack files removed (author's yes); the 05 and 07 slides' legends enlarged.
**2026-10-22, laptop, without the drive (§68), the author's decision D17:** the class scheme is revised
**before the interim**: codes 1–4 kept and narrowed (Crater means impact only; volcanic plains are Normal Ground),
5 volcanic edifice, 6 apron, 7 fluvial channel; the agent proposes, the author accepts (§11). The 512 labels,
audited from the repo's gdb export: no overlap between classes, one train/test leak (labels 290/291, 51.5 km²),
five volcanoes labelled Crater (Arsia Mons, held out, 31 % of the held-out Crater area; Ulysses Tholus, held
out; Ascraeus and Pavonis Mons and Tharsis Tholus, training), lava-tube polygons on fluvial valleys. The author
approved downloads and a seven-class map beside the four-class one in the interim (D18). The same day, without
the drive, `propose_label_changes.py` and `apply_label_review.py` were written and tested on downloaded copies
of the references (KB §68.5): ready for the desktop run (item 2a, §11.2).
**2026-10-23, laptop, without the drive (KB §68.6):** the v2 runs after the review scripted (`--labels v2`,
`labelsets.py`; `score_d18_verdict.py`; §11.5 lists the commands), the scorer made fast on long outlines with the
same results, and everything rehearsed on the released maps: unchanged without `--labels`; the four-class maps
score 33.6 % (SVM) and 41.6 % (U-Net) on stand-in v2 held-out labels, 58 % of whose area is classes 5–7. A
question for the author (§2, D19). **Every file under `Mars Remote Sensing Project\` that the clone changed
since commit `449cc9a` was written in the clone only:** list them with
`git diff --name-only 449cc9a HEAD -- "Mars Remote Sensing Project"` and copy each to the drive before the next
`github_sync.py`, which copies drive → clone and would overwrite or remove them. A drive file that existed before
should still equal `449cc9a` (check with `git hash-object` against `git rev-parse 449cc9a:<path>`); if one
differs, merge by hand.
**2026-10-22, desktop (§69), the author's request:** the final started early, as builds: an AASTeX 7 paper (14
pages, 16 figures, compiled with MiKTeX, installed per-user at the author's choice) and a 32-slide final deck, both in
`NEXT STUFF\Final\`, both on the machine products as candidates (the review not started); every page and slide read.
**2026-10-23, desktop (KB §69.1):** the clone's §68 work copied to the drive as the note above asks (nine scripts
replaced, four added, the record and this plan merged by hand); the final paper and deck now carry §68's audit
as a limit and the seven-class revision as a next step; everything pushed. The drive and the clone agree again.
**2026-10-23, desktop (KB §69.2): item 2a done.** The valley map downloaded and checked; `propose_label_changes.py`
run on the drive gives the laptop's result exactly (1,086 rows: 12 relabel, 23 check, 1 clip, 1 delete, 1 fix,
574 new); `Landform_TrainingSamples_v2_proposals` and the map "Labels v2: proposals" are in the project, sampled
and read. **Next is the author's review (2b, §11.4)**; flagged for it: new fluvial strip 778 on the Arsia flank,
Crater 47; hills and lava tube need more training polygons (§11.3).
**2026-10-24, desktop (KB §69.3):** no change on the drive since 10-23 (the review not started). An audit pass:
the KB's gdb inventory (§6) gains the proposals class (31 feature classes, which `audit_record.py` under the ArcGIS
Python had flagged); four audits that looked for Presentation 1 and the prospectus at the root now read `OLD\`.
`verify_all.py` 37 / 37, `check_repo.py` passes. `verify_interim.py` now checks the paper's `.tex` as well: all 508
numbers in the record.
**2026-10-24, desktop (KB §69.4), the author's request:** while the review waits, the v2 runs are **rehearsed** on
the proposals taken as proposed (`--labels v2p`, never a result): `apply_label_review.py --rehearsal`, then
`build\run_rehearsal_v2p.ps1` (SVM, then U-Net, ~21 h unattended). D19 answered: rule (a) on v2 classes 1–4.
**2026-10-25 (KB §69.4): the SVM rehearsal ran end to end** (21 h 47 min to the map, 7-class ~3 × the 4-class
time); on the proposals as proposed the seven-class map scores 41.3 %, κ 0.297 and D18 keeps the four-class
map ((a) on classes 1–4, apron in (b), Crater in (c) fail); fluvial channel paints 32.9 % of ±60°. **For the
review:** trimming the valley strips to their floors is where the seven-class map stands to gain most.
**2026-10-26 (KB §69.4): the rehearsal is done**, all 13 steps. The seven-class U-Net scores 88.8 %, κ 0.856 on
the rehearsal polygons (four-class U-Net 41.6 %); by D18's rule as a report it too keeps the four-class map ((a)
on classes 1–4, 90.4 against 98.9 %; Crater and hills in (c)). Times for the real run: SVM ~22 h, U-Net ~21 h.
The label review (2b) has not started: 0 of 1,086 rows have a `Review` (read 2026-10-26 evening).
**2026-10-26 evening (KB §69.5), D20, the author's decision: the interim's data cut is today.** What is
measured now is the interim; the label review, the v2 runs, the candidate review and digitising, and the H1 / H2
retests go to the final (by the 22 Nov freeze). `interim.py` brought to the cut and both documents rebuilt and
read: 30 slides, 21 pages, `verify_interim.py` 282 numbers. The percent-complete column set by the agent at the
author's request (D16, toward the final; KB §69.5). Left on the interim: the due date and delivery.
**Same evening (KB §69.6), the author's request:** the interim's text edited for plain wording (no numbers
changed), the slides reordered (first maps before the published one; H1, H2, H3, Q5), two stale facts fixed
(the drive's size, "finds" for 34 of 124 crater polygons right). 30 slides, 23 pages; every slide and page read.
**Late 10-26 (KB §69.7): the first review session.** At Ius, all 188 steep channels (94 accept, 80 reject, 14
unsure: precision 54 %) and 361 closed depressions (26 / 331 / 4: 7 %) reviewed; the 120 accepts copied **as they
stand** at the author's word (Origin indeterminate, Confidence inferred, Preservation empty), so H2's stage 2
still waits for ≥ 10 fluvial and ≥ 10 volcanic channels: set `Origin` on the copies in
`Landform_ChannelCenterlines` (a rerun skips copied rows). Layout 14 rebuilt and read.
**10-27 (KB §69.8): the label review (2b) is all but done.** The author reviewed 162 of the 164 rows that are
not new apron or fluvial strips (512 and edifice 870 left); the 172 apron and 276 fluvial rows were left to the
agent and reviewed by a written rule (`build\review_v2_by_rule.py`: fluvial strips accepted only on a floor ≥ 20 m
below their flanks and off volcanic plains, 192 / 276; aprons only if not flat and not in craters, 155 / 172).
`apply_label_review.py --dry-run`: no overlaps; **every class meets §11.3 but hills (training in 2 blocks)**.
The author's answers: the six rejected Crater checks (21, 38, 42, 47, 48, 54) are dropped; hills stays in with
`--keep-short`. **Applied:** `Landform_TrainingSamples_v2` 971 labels (734 training, 237 held out). **2c is
running:** `build\run_v2.ps1` started 10-27 01:32, SVM then U-Net, ~2 days (stopped by a restart at 21:18 after 12 of
21 SVM tiles, resumed 10-28 02:29 with `-ClassifyOnly`, KB §69.23); **keep Pro closed** until
`build\logs\run_v2\queue.log` says "queue done". Then the agent reads the scores and D18's verdict, and makes
the layouts (§11.5 step 4).

**The digitising classes hold 94 channels and 26 crater rims (0 lava margins); 549 of 9,287 candidates are
reviewed, none at Athabasca.** The review is the critical path, and only the author can do it (§6). The class revision (§11) runs beside it and must not
delay it.

**Next, in this order:**

| # | what | who | how | done when |
|---|---|---|---|---|
| 1 | **Review the Ius candidates** (the 188 steep channels done; 1,324 depressions open), then Athabasca; draw breached craters and the Athabasca lava margins | author, in Pro | §6 | rows in `Landform_ChannelCenterlines` / `Landform_CraterRims`; the tally printed |
| 2 | After each review session: copy the accepts, refresh layout 14, re-export the gdb, push | agent | §3 | the repo's gdb export matches the drive; layout 14's table matches the tally |
| 2a | ~~**Class revision, proposals**~~ **done 2026-10-23 (KB §69.2):** the 512 with evidence and an `Action` each, plus new polygons for classes 5–7, in `Landform_TrainingSamples_v2_proposals` and a map in the `.aprx` | agent, drive | §11.2 | every label has an `Action`; each new class meets §11.3's minimum in proposals |
| 2b | ~~**Review the label proposals**~~ **done 2026-10-27 (KB §69.8):** the author's rows, the apron and fluvial rows by the agent's rule at the author's word; applied with hills kept short (`--keep-short`) | author, in Pro | §11.4 | every non-`keep` row reviewed |
| 2c | v2 labels and split (done 10-27); SVM and U-Net on v2 (**running since 10-27 01:32**, resumed 10-28 02:29 after a restart, `run_v2.ps1`); both maps scored on v2; D18's verdict; layouts and the final | agent, desktop | §11.5 | results in the KB beside the four-class scores, by the **22 Nov** freeze |
| 3 | **X5, deep learning**: X5 done to layout 16 (§66.1–66.4); X5b and the U-Net X5c trained and scored (§66.5–66.6). ±60° U-Net map made (§66.7), seams removed (§66.8), in the project beside the published SVM map with layout 17 (§66.9), in the interim and the release `data-2026-10-21` (§66.10). For the author: any further tuning needs its own validation blocks first (§66.5) | author | §5 | held-out recall and precision in the KB beside the SVM's |
| 4 | Retests that wait for the review: H2 stage 2, H1 on digitised margins | agent | §4 | results in the KB, either way |
| 5 | The interim: content cut on 26 Oct (D20) and rebuilt, percentages set (D16); refined for the **10 Nov** presentation (KB §69.10); the report's date from the author, then deliver | author + agent | `INTERIM-PLAN.md` §0, §6 | delivered |

**Waiting on the author:** items 1, 3 and 5 (and Pro kept closed while `run_v2.ps1` runs); D21–D27 (§2, from
§12 and §13); the interim talk's slot length (§12.5); whether to delete the two recreated `_60_smoke` classes
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
| D16 | the interim's due date: **the presentation is 10 November** (the author, 2026-10-27, KB §69.10); the report's date is still open (the percentages were set 2026-10-26, KB §69.5) | plan the report against 10 November too |
| D21 | the paper's title, which promises "Mapping Lava Flows" though they come from the geologic map (§12.4 W2) | retitle around the stack and what it can and cannot map |
| D22 | the two blind checks: the rule-screened v2 rows (§12.3 R1, ~45 min) and a probability-sample accuracy check (R2, ~2–3 h) | R1 yes, after the candidate review; R2 if time is free |
| D23 | a DOI for the data release through Zenodo, and a data statement (§12.4 W7); publishing | yes, with the pre-final release (§7) |
| D24 | the final deck in the interim's dark `mars_theme` (§12.5) | yes: one look for both talks |
| D25 | the abstract's and conclusions' thermal gain: qualify it with the balanced-accuracy result (§12.4 W9); also the README (the interim: done, the author's yes, KB §69.21) | yes: one clause, "in overall accuracy; none by balanced accuracy" |
| D26 | the built deck, report and paper PDF committed only once per deadline (§13.1 P4); rewriting history to drop the 35 earlier copies needs a force push and a re-clone on both machines | yes to committing at milestones; no rewrite |
| D27 | closing the project after 8 Dec: final tag and release, `CITATION.cff` completed, the README rewritten as finished work (§13.1 P12); an ORCID for the citation if the author has one | yes |
D19 was answered 2026-10-24, before any v2 score existed: D18's rule (a) is judged on the held-out polygons whose
v2 class is 1–4, the ground both maps can name (KB §68.4 amended, §69.4); `score_d18_verdict.py` does so.
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
4. Layouts: a new sheet for the seven-class SVM map beside 04 (the four-class map, kept), 13 on both, 17 for
   the U-Net on v2; legends name seven classes. The X5 detector and layout 16 stay four-class, as history.
   `polish_layouts.py`, export, read.
5. The final rebuilt **with both maps** (D18, moved from the interim by D20): the four-class map and its scores,
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
author's review (§6).

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
| A3 | **Spatial baselines for the held-out score**: (a) each pixel given the class of the nearest training polygon; (b) a classifier on elevation and latitude only (the crustal dichotomy); (c) the SVM map under a ~51 km mode filter, the U-Net's context | turns "the U-Net's 98.9 % measures agreement at province scale" into a measured statement | desktop | A |
| A5 | **Block bootstrap**: intervals that resample the 14 held-out blocks, not the 183 polygons (polygons in one block are not independent); beside the polygon intervals, for the maps and for T1. Needs per-polygon scores: `DL_UNet_Heldout_Scores_20261020` holds them for the four-class maps; the scorer does not write them yet | honest intervals for a spatial test | desktop | A |
| A6 | **Agreement map**: where the SVM and U-Net maps agree, per class, as a share of ±60° and as a figure; four-class now, v2 after | shows where the two methods disagree, not only how each scores | desktop, minutes | B |
| A7 | **H2 with references for origin** (§4, T4 stage 1b): routed segments on Alemanno valleys as fluvial against segments on SIM 3292 volcanic units off them as volcanic; gradient and thermal z-score as in stage 1 | H2 tested by origin rather than by window, without waiting for 10 + 10 reviewed channels; still a stand-in, and stage 2 stays the authority if the review reaches it | desktop | B |
| A8 | **T9: thermal value on material labels** (§4): SIM 3292 unit groups as the labels at 400 m, the same block split, thermal ablated; also within blocks | answers the paper's own limit, "a test of thermal value needs material labels", with the only material map held | desktop, numpy | B |
| A9 | **Day IR at the contacts checked against topography**: T5 rerun with day IR residualised on hillshade and slope (day temperature follows slope facing the sun) | if the +8.7 pt lean vanishes, H1's hint is illumination; if it holds, it is stronger | desktop, minutes | B |
| A10 | **Crater size-frequency distribution**: cumulative counts, log-log, closed depressions against Robbins, at ±60° and per type area; the completeness diameter where the curves part | the standard planetary figure for a crater catalogue | desktop | B |
| A11 | **The breached-crater explanation tested**: recall by Robbins' morphology or degradation fields, if the 2020 release carries them **[?]** (columns not read), else by rim-height deficit on the DEM | the paper asserts why recall stops near one half; this measures it | desktop | B |
| A4b | `score_metrics.py` on the v2 logs (the list is at the top of `v2_drafts.tex`), for Table 3's v2 rows | balanced accuracy, F1, Q and A beside v2's accuracy and κ | either Python, minutes | A |
| A13 | **The review rule's sensitivity**: how many fluvial and apron rows change at floor depths of 10 and 30 m and median slopes of 0.5° and 1.5° | bounds how much the v2 labels depend on two thresholds | desktop, minutes | C |

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
- **W4, figures** (page budget: 14 pages now): the pipeline (`docs/pipeline.svg`) in Methods; **the block split**,
  39 blocks with the 14 held out and the polygons by class, so a reader can judge the spatial test; a type-area
  zoom of the published map against the imagery at full resolution; Perrotin found and Oudemans breached, the
  detector's limit in one panel; after v2, the seven-class map and its confusion; A6 and A10 if run.
- **W5, limits to add**: one labeller; the rule-screened v2 rows; hills short; THEMIS strips differ in local time,
  season and dust, a physical cause beside the stretch (to check in Edwards et al. 2011); Viking MDIM 2.1 colour is
  itself a balanced mosaic, so part of its albedo signal may be processing **[?]** (to check in the MDIM 2.1
  documentation).
- **W6, future work**: the outline's item 10 (§7) has no section in the paper: calibrated THEMIS inertia where it
  exists, CTX for margins, validation blocks for the deep-learning models, R2 if not done.
- **W7, data availability** (D23): a DOI for the data release through Zenodo's GitHub link, cited as
  `Edwards2026data`, and a data statement as AAS asks. Publishing: the author's yes.
- **W8, the deck's half**: the paper's v2 text is drafted for both outcomes (`v2_drafts.tex`, KB §69.18) and the
  colours are `labelsets.COLOURS`, checked; `final.py`'s v2 slide (the seven-class map, its scores beside the
  four-class map's, D18's verdict) is still to draft, the same way. Laptop.
- **W9, the thermal claim** (D25): by balanced accuracy the thermal gain vanishes (−0.3 and +0.1 points, KB
  §69.18); the paper says so in Results, but the abstract and conclusions still give "a resolved 1.4 to 2.0
  points" alone. Whether they should carry the qualifier is the author's call.

### 12.5 The two talks

- **The interim, 10 Nov:** speaker notes on every slide; one timed run-through (the slot's length from the author);
  backup slides for the likely questions: why no calibrated thermal inertia, why the U-Net's 98.9 % is not the
  headline, what a held-out block is, what has changed since the cut (the v2 labels).
- **The final deck** (D24): rebuild it in the interim's dark `mars_theme` so the two talks look alike; `final.py`
  keeps the words.

### 12.6 Order of work

1. **Laptop, now:** W8's deck half; W3's candidates checked (A4, A12, W1 and the paper's half of W8 done 10-27,
   KB §69.18).
2. **Desktop, after "queue done":** the v2 scoring and D18 (§11.5) first; then A4b, A1, A2, A3, A5, A6, then
   A7–A11 as time allows; A13 if cheap.
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
| P9 | **Tests of the scoring arithmetic**: hand-worked confusion matrices through `score_metrics.metrics()` (accuracy, κ, balanced accuracy, F1, Q and A, a class absent from the labels), run in CI with P1 | the paper's new Table 3 columns rest on 60 lines no test has exercised beyond the agreement check | laptop | B |
| P10 | **"Resume here" condensed**: it has grown to ~180 lines of dated paragraphs since 10-18; cut it to where things stand, what waits on whom and the clone → drive list, with the history left to the KB (as §58–§61 did once) | the most-read part of the plan readable in a minute | laptop | B |
| P11 | **Which runs repeat exactly**: a table in the KB of each published number's run and whether a rerun reproduces it (a fixed seed, Pro's SVM, the U-Net's training); five build scripts name a seed | the paper's methods can say what is deterministic, and the freeze knows which reruns can move a number | laptop to read the scripts; the desktop for any rerun | C |
| P12 | **Closing the project, after 8 Dec** (D27): a tag `final-2026-12-08` and a final release (the deck, the paper's PDF, the maps); `CITATION.cff` given `version`, the DOI (D23), a `preferred-citation` for the paper and its date; the README's "Where it stands" turned into what was found; this plan closed with a header saying so; the memory and "Resume here" retired; D14's smoke classes settled | the repository reads as finished work, not a project paused mid-term | laptop, ~1 h, 9–12 Dec | after |

**The thermal wording beyond the paper** (D25, widened): the README's T1 section ("Yes, a little") and the interim
talk give the overall-accuracy gain alone. The interim's content is cut at 26 October (D20), but this result is a
reanalysis of logs that existed at the cut; one backup slide for "does thermal really help?" would answer the
question without changing the cut. The README follows whatever the paper says.

### 13.2 Order of work

1. **Laptop, now:** P4 (code only; its behaviour waits on D26), then P9 and P10 (P1–P3 done 10-27, KB §69.20).
2. **Either machine:** P6.
3. **Desktop, when it is free of `run_v2.ps1`:** P2's first real use, the clone → drive copy ("Resume here");
   the next `github_export_gdb.py` writes `exports/README.md` from the same descriptions (P3); P7, P8.
4. **After 8 Dec:** P12.
