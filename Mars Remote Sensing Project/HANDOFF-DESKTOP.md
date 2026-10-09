# Handoff: continuing the Mars Global Mosaic on the desktop

Written 2026-10-09 at the end of the laptop sessions, after a final audit of every open task. For the
next agent (or person) picking the project up when this drive moves to the desktop.
**Read this file first, then `NEXT-STEPS.md` "Resume here", then `PROJECT-KNOWLEDGE.md` as needed.**
The record (`PROJECT-KNOWLEDGE.md`, "KB" below, § numbers point into it) is the authority on what is
true; this file and `NEXT-STEPS.md` are plans. When the two disagree, the KB wins and the plan is fixed.

Deadlines: **interim ~13 November 2026** (the course says "mid-November"; the exact day is not known),
interim data cut **2 November**, digitising checkpoint **1 November**, data freeze **22 November**,
**final Tuesday 8 December 2026**. No rubric exists for either (D2, KB §50).

---

## 1. The first ten minutes on the desktop

1. **Which machine and drive letter?** The desktop is `DESKTOP-PJS73RO` (Windows user `Owner`; i7-8700K,
   64 GB, RTX 2080 Ti). There the drive is **`F:`**, not `Z:`. Every build script finds its drive from its
   own location (`build\paths.py`, KB §40.2); nothing needs editing for the letter.
2. **Is ArcGIS Pro closed?** Any script that writes the `.aprx` or the gdb asserts Pro is closed
   (`tasklist | findstr ArcGISPro`). Reading with Pro open is fine; writing is not.
3. **Run the preflight**, with the ArcGIS Pro Python (path in §3):
   `python "F:\Mars Remote Sensing Project\build\desktop_check.py" --gpu`
   It checks, in under a minute, and writes `build\logs\desktop_check_<host>.json`:
   - **X0, the three junctions.** Spatial Analyst cannot take paths with spaces, so `<drive>\TypeArea`,
     `<drive>\Global60` and `<drive>\Athabasca` are no-space junctions to the same names under
     `<drive>\Mars Project\`. Junctions store absolute targets, so the ones made on `Z:` point at
     `Z:\...` and are broken on `F:`. The script prints the exact fix; in `cmd`:
     `rmdir "F:\TypeArea"` then `mklink /J "F:\TypeArea" "F:\Mars Project\TypeArea"` (same for `Global60`
     and `Athabasca`). `desktop_check.py` checks all three.
   - **X1, the GPU test (q10).** `Slope` on the Ius DEM, `CPU_ONLY` then `GPU_THEN_CPU`, timed. "GPU
     engaged" = the tool's messages exist and no longer say *"No compatible GPU device has been detected"*.
     (The map-algebra form `arcpy.sa.Slope` returns no messages at all; the script uses the tool form
     `arcpy.ddd.Slope`. On the laptop it correctly reports no GPU. The positive case has never been seen.)
   - **X5 preflight.** Deep learning needs Esri's separately installed **"Deep Learning Libraries"** for
     ArcGIS Pro (torch, torchvision, fastai, `arcgis.learn`). **Absent on the laptop.** If absent on the
     desktop too, installing them is a large download from Esri: **ask the author first.** Also checks CUDA
     and that the training-split export is intact (3,622 chips, labels from the training split only).
4. **Open the project in Pro once** (`F:\Mars Project\Mars Project.aprx`) and look at layout 10 and any
   map. Verified 2026-10-09 by opening it through another drive letter: **135 layers, 0 absolute `Z:\`
   paths, 0 broken, 9 web services** (KB §52). If anything is broken on `F:`, it is the junctions (step 3).
5. **What changed since this file was written?** Read `NEXT-STEPS.md` "Resume here" (rewritten at the end
   of each session), the `Review` tally (`python build\accept_reviewed.py`, dry run by default), and the
   GP history (KB §29 shows how). Plan from what is there, not from this file's snapshot.

## 2. Where everything is

| what | where (drive root = `F:` on the desktop) |
|---|---|
| the record | `Mars Remote Sensing Project\PROJECT-KNOWLEDGE.md` (sections 1–52; §11 open questions; tags `[V]` verified, `[E]` earlier, `[?]` open) |
| the plan | `Mars Remote Sensing Project\NEXT-STEPS.md` ("Resume here" at the top; decisions §2; tests §4; desktop jobs §5; manual work §6; figures §7; schedule §8; risks §9; ruled out §10) |
| the interim plan | `Mars Remote Sensing Project\INTERIM-PLAN.md` (living deck §0; hypotheses §5; timeline §6; wording traps §7) |
| scripts | `Mars Remote Sensing Project\build\` (139 `.py` / `.ps1`; 138 in the public repo, which leaves out `neutral_voice.py`; catalogue in its `docs/scripts.md`); logs and test results in `build\logs\*.json` |
| interim deck and report | `Mars Remote Sensing Project\NEXT STUFF\Mars Global Mosaic - Interim Presentation.pptx` (25 slides) and `Mars Mosaic - Interim Report.docx` (17 pages), built from `build\interim.py`; the course template is in the same folder |
| ArcGIS project | `Mars Project\Mars Project.aprx` (23 maps, 12 layouts), `Mars Project\Mars Project.gdb` (24 feature classes, ~138 GB of rasters); backups of the `.aprx` in `Mars Project\.backups\` (one per write) |
| layout PNGs | `Mars Project\Global60\layouts\` (04–10, 13, 14) and `Mars Project\TypeArea\layouts\` (01–03) |
| ±60° products | `Mars Project\Global60\` (`global60_svm_stack_200m.tif` is the 7-band stack; `build\grid60.py` defines the grid) |
| type areas | `Mars Project\TypeArea\` (`ius_*`, Ius Chasma) and `Mars Project\Athabasca\` (`ath_*`); windows in `build\areas.py` |
| reference data | `Mars Project\Reference\` (USGS SIM 3292, Robbins craters, TES thermal inertia; third-party, never mirrored to GitHub) |
| deep-learning exports | `Mars Project\LabeledObjects\global60_svm_stack_200m_train\` (**train on this one only**), `...\global60_svm_stack_200m\` (all 512 labels, held-out included: never train on it), `...\CompositeBand\` (the 1 Oct GUI export, superseded) |
| source mosaics | the drive root: Viking MDIM 2.1 colour, THEMIS day IR v12, THEMIS night IR v14 (60N–60S), HRSC/MOLA blend DEM |
| public backup and project page | GitHub `loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data`; clone at `~\OneDrive\Documents\GitHub\Mars_Terrestrial_GlobalMosaic_GIS-Data` (KB §35) |
| agent memories (private) | the laptop's Claude Code memories are mirrored one-way to the OneDrive knowledge vault: `~\OneDrive\Documents\Github Knowledge\memory\loggg\z-drive\` (refreshed 2026-10-09). Read them; do not edit them there. On the desktop, Claude Code starts with an empty memory for `F:` |

## 3. Working rules (each one learned the hard way; KB section in brackets)

**Tools and machines**
- **Two Pythons, neither does both jobs.** Rasters and `arcpy`: `C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe`
  (Pro 3.7 on the laptop; check the desktop's version in the preflight log). Decks, reports and charts:
  system Python with `python-pptx`, `python-docx`, `matplotlib`, `Pillow` (and `PyMuPDF` to read PDFs as
  images). Never `propy.bat`: it fails on its own unquoted path. `import arcpy` costs ~7 s: batch work.
- **No GUI automation.** `arcpy` headless is the channel; the Pro GUI is for the author. Work must end up
  **inside the `.aprx`** as a layer in a named map, and as a layout if it is a result; files in `build\`
  are not "done" (§31).
- **Safe-write pattern for the `.aprx`:** the builders back it up to `.backups\` first; rehearse with
  `--aprx <copy>` on a copy placed **beside** the real `.aprx` (it stores relative paths); then run for real.
- **After any layout builder, run `polish_layouts.py`** (Arial everywhere; Aptos and Tahoma are missing on
  the laptop and Pro substitutes a serif). Then export and **look at every sheet**: `isOverflowing` caught
  none of the defects found by reading (§33, §49). `polish_layouts.py --export` writes all sheets to
  `Global60\layouts`, including 01–03, whose real home is `TypeArea\layouts`: delete those three strays.
- **The builders wipe and rebuild their maps.** Order when several run: `make_global60_maps.py`,
  `make_candidate_maps.py`, `make_mosaic_layout.py`, then `make_reference_maps.py` (graticules and layout
  10 go on last), `make_geomap_sheet.py`, `make_validation_sheet.py`, then `polish_layouts.py`.
- **Big writes go to internal disk first**, then one copy to the drive; the USB drive dropped off
  mid-write twice (§36.4). Reads cap near 112 MB/s: the drive, not the CPU, is the ceiling (§2.2).
  **Never propose copying the project to internal disk** (ruled out by the author).
- **Classified rasters:** pixel value = class code since §36. `ClassifyRaster` output may need its VAT
  read (value vs `Classvalue`, §19). Build mixed stacks with one NoData sentinel by hand (§19).
- **Shell traps on Windows:** heredocs and `sed` eat backslashes (a `\t` became a tab in a path on
  2026-10-09): write scripts containing backslashes with a file editor, then run them. `python -` hangs.
  The cp1252 console crashes on `≥`/`—` in prints: `sys.stdout.reconfigure(encoding="utf-8")`.
  PowerShell scripts (`render_pdf.ps1`) are blocked by execution policy from `bash`; run them from
  PowerShell directly; do not change the policy.

**Content**
- **±60°, never "global"**: the analysis extent is the THEMIS night mosaic's, 86.6 % of the surface (§16).
- **"Diurnal-contrast index", never "thermal inertia"**: the held THEMIS mosaics are locally stretched
  8-bit DN; calibrated inertia is not derivable from them (§24, §28.10). The index does not track TES
  inertia at 3 km (§42.4, §43.1).
- **"Closed depressions ≥ 1 km", never a crater inventory**: only 11–13 % of the detector's ≥ 1 km
  candidates are catalogued craters; for craters use `Ref_Craters_Robbins2020` (§42.3).
- **Keep the four hand-drawn classes** (Crater, steep/windy hills, lava tube, Normal Ground; codes 1–4 in
  that order, the project's schema since q23). Never remove or replace them; a fifth only if a held-out
  test shows it helps (the "volcanic" fifth failed, §43.3).
- **Score on held-out data.** The 512 hand-drawn polygons are split by whole 15° blocks:
  `Landform_TrainingSamples_terrain_60_train` (329) and `_60_test` (183). Never train on the test set.
- **Every number from its source.** Derive from the rasters, logs and the KB, never from a previous
  document or a correction (§12). Every test writes its prediction and verdict rule into the script
  before it runs (§47, §51).
- **Prove a check can fail** on a planted defect before trusting that it passes (done for the review
  tally, the duplicate check, the DL scorer, the GPU test; §46, §49–§51).
- **Objective, impersonal voice** in the KB, plans, scripts, layer and layout text, slides and the
  public repo: "the hand-drawn labels", "on request", "the author". `build\neutral_voice.py --check <files>`
  exits 1 on a personal pronoun (§39.4).
- **Deletions only on explicit approval**, item by item, after an inventory and a backup (§37, §50).
  Machine output never enters the three `Landform_*` digitising classes except through an accept in
  review (§25, §46). Digitising is the author's judgement, not the agent's.

## 4. State at handoff (2026-10-09)

- **Checks green:** `audit_record.py`, `verify_all.py` 37 / 37, `verify_interim.py` (193 numbers),
  `neutral_voice.py`, the repo's `tools/check_repo.py`; pushed, CI passed (commit `64e9b7f` and the
  handoff commit after it).
- **Every open decision is answered** (KB §50): D2 no rubric; q23 the labels' class order; q25 deep
  learning yes, on the corrected stack; q26 boxes; q27 keep 5 × 5; D9 deletions done; D13 keep the plateau
  channel candidates and reject them in review.
- **Digitising has not started:** 0 of 9,287 candidates reviewed; `Landform_ChannelCenterlines`,
  `Landform_CraterRims`, `Landform_LavaFlowMargins` hold 0 rows. This is the critical path.
- **Hypotheses:** H1 not supported at the geologic map's 1:20 M (rerun on digitised margins); H2 not
  supported at stage 1 (by window; stage 2 on reviewed channels); H3 not supported; H4 answered by another
  method; Q1, Q2, Q4, Q5 answered; Q3 overtaken; Q6 unexamined (§47.5, §51.1).
- **Measured results to date:** the ±60° SVM 73.5 %, κ 0.58 held out (§32.2); thermal adds +1.3 pt (§40.1);
  TES checks (§42.4, §43.1); T8 (§43.2); T2 (§42.2); T5–T7 (§47); T4 stage 1 (§51.1).

## 5. Every open task, audited 2026-10-09

Who: **A** = the author, by hand in Pro; **C** = an agent, scripted; **D** = needs the desktop.
Ordered by what each unblocks. "Done when" is checkable.

### 5.1 Desktop day (D + C), in this order; the full list is `NEXT-STEPS.md` §5

| # | task | command (ArcGIS Python, from `F:\Mars Remote Sensing Project\build`) | cost | done when |
|---|---|---|---|---|
| X0 | junctions | `desktop_check.py`; fix with `mklink /J` as printed | minutes | preflight shows all three `ok` |
| X1 | GPU test (q10, settles q8) | `desktop_check.py --gpu` | ~1 min | `x1.gpu_engaged` recorded in the log and in KB §11 q10 |
| X2 | **fine pass**: craters and channels ≥ 1 km at ±60° | smoke first: `make_global_landforms.py --smoke` (recreates the two `_60_smoke` classes deleted in §50; leave or delete them only on approval); then `make_global_landforms.py --skip-coarse` (the coarse basin pass is done, layout 07). Resumable: checkpoints in `C:\MarsScratch\global60\` (internal disk; needs free space); a rerun skips finished tiles | ~7 h (laptop estimate; 70 tiles) | `verify_global60.py` passes; `Landform_CraterCandidates_auto_60` and `Landform_ChannelCandidates_auto_60` exist with row counts in the KB |
| X4 | pyramids on the four source mosaics (q6) | in the ArcGIS Python: `arcpy.management.BuildPyramids(r"F:\<file>.tif")` for each of the four root `.tif`s (one at a time; writes `.ovr` beside each) | hours, run alongside X2 | each source has an `.ovr`; panning in Pro is faster |
| X3 | 200 m classification | `make_global60_classification.py --cell 200`, then `verify_global60_classification.py`, then `make_global60_maps.py` + `make_reference_maps.py` + `polish_layouts.py` | ~15 h on the laptop's rate; desktop unmeasured | held-out score in the KB beside the 400 m one (§31.3, §32.2); layout 04 redone |
| X5 | deep learning (q25, approved) | after the libraries are installed (ask first) and the preflight says ready: `make_dl_model.py --train [--model RETINANET] [--epochs 20]`, then `--detect --emd <model.emd>`, then `--score <detections fc>`. **Never run before; parameter names checked against Pro 3.7; which detection models take 7-band input is unverified [?]** | hours | `logs\dl_heldout_score.json`; per-class recall and precision on the 183 held-out polygons in the KB, beside the SVM's numbers |
| X6 | q24: the 29 Sep `ClassifyRaster` settings | read the `.afr` / GP history on the desktop | minutes | KB §11 q24 answered |
| X7 | q12, optional: one source mosaic as a tiled, compressed copy, timed against the original | only if X4 leaves panning slow; needs drive space | ~1 h | timing in the KB |

Not to be run: segmentation at ±60° (~92 h; object-based work stays on the type areas); the 100 m
Composite Bands (`make_global_stack.py`, overtaken). See §5.9.

### 5.2 The review and digitising (A), the critical path

`NEXT-STEPS.md` §6 has the steps. In short: open "Ius Chasma — digitising", start with the layer
"Channels: steep and rock-floored (188)", then "Closed depressions ≥ 1 km (1685)"; set `Review`
(accept / reject / unsure) in the attribute table, and before accepting set `Origin` (channels:
fluvial / volcanic / indeterminate), `Preservation` (craters) and `Confidence`; save edits. Then draw
what the machine missed straight into the `Landform_*` classes: breached craters, and **lava-flow margins
at Athabasca** (the `lAv` unit of the geologic map shows where; these settle H1). Suggested minimum for
the validation to mean something: ~30 channel segments, ~50 crater rims, every defensible lava margin.
**Checkpoint 1 November:** if the classes are still empty, the interim presents the machine products as
candidates with their measured recall (`NEXT-STEPS.md` §6 contingency).

### 5.3 After each review session (C, minutes; Pro closed for the writes)

1. `accept_reviewed.py` (dry run: the tally and the precision), then `accept_reviewed.py --apply --by "<reviewer>"`.
2. `make_validation_sheet.py` (Pro closed; `--tally` alone is read-only and works with Pro open), then
   `polish_layouts.py`; read layout 14.
3. `make_t4_channel_h2.py`: reports stage 2 waiting until ≥ 10 fluvial and ≥ 10 volcanic reviewed channels
   exist. **Stage 2 is not written yet:** when the counts are reached, extend the script to compare by
   `Origin` (the reviewed channels carry no `ThermIdx`; sample the type-area index along them), with its
   prediction and rule written first.
4. When lava margins exist at Athabasca: give `make_flow_margin_test.py` a `--margins` source
   (`Landform_LavaFlowMargins` in place of the SIM 3292 contacts) and rerun T5 (H1) (`NEXT-STEPS.md` 4a).
5. `github_export_gdb.py` (the digitised features live only in the gdb), then the session-end sequence (§6).

### 5.4 After the fine pass (C)

- `verify_global60.py` first (it is the gate that the output co-registers, §28.4).
- Two ±60° sheets (`NEXT-STEPS.md` 3.8, layouts 11 and 12): closed depressions ≥ 1 km (density, scored
  against Robbins at every size with the §42.3 matching rule) and the channel network, each with its blind
  spots stated (closed depressions only; plateau channels are DEM noise, §25, §47.4).
- Add both to `interim.py` if ready by the 2 November cut; otherwise to the final.

### 5.5 The interim (C + A), due ~13 November

- **Ask the author:** the exact due date, and the percentages for the progress table (they are the
  author's to set; `interim.py` prints dashes).
- **Living build:** edit `build\interim.py` (one entry per result in `FIGURES`), then
  `make_interim_figs.py` (ArcGIS Python; Pro may be open), `build_interim_live.py "<deck.pptx>"` and
  `build_interim_report_live.py "<report.docx>"` (system Python; both take the output path; the live
  files are in `NEXT STUFF\`). Render: `render_pdf.ps1 -Deck <pptx> -Pdf <pdf>` from PowerShell; the report
  through Word COM (KB §51.5); rasterise PDFs with PyMuPDF; **read every changed slide and page**. Then
  `verify_interim.py` (it proves each number exists in the KB, not that it sits beside its claim: check
  new numbers against their section by hand, §48).
- Known fits: a log table of 14 rows overflows the slide; a whole tall layout makes its slide unreadable
  (draw the content as a chart instead, as for T8, §51.5); titles over ~60 characters wrap onto the rule.
- Timeline (`INTERIM-PLAN.md` §6): data work to 1 Nov; **cut 2 Nov**; finish text 2–6 Nov; rebuild and
  read 6–9 Nov; review 9–12 Nov; deliver. Wording traps: `INTERIM-PLAN.md` §7.

### 5.6 The final (C + A), due 8 December

- Data freeze **22 November**; final figure list = `NEXT-STEPS.md` §7 (no rubric exists); outline in §7
  (question and Athabasca hook · data and the ±60° decision · co-registration and the frames trap · the
  thermal pair's limits · craters · channels · lava flows · classification and accuracy · limits · next).
- **No final builder exists yet.** Write `build_final_live.py` / a report builder on the interim's pattern
  (one source module, charts from logs, layouts exported by script), early enough to rehearse.
- Before each deadline: refresh the GitHub release (`github_release_bundle.py --upload data-YYYY-MM-DD`),
  check it holds every figure the deadline needs (KB §35), and run `tools/check_remote.py` by hand
  (manual only, the author's decision).
- 23 Nov – 4 Dec documents; 26 Nov Thanksgiving, nothing planned; 5–8 Dec buffer.

### 5.7 Open questions still `[?]` in KB §11

| q | question | how it closes |
|---|---|---|
| 6 | pyramids on the four sources | X4 |
| 8 | which machine produced the §8 run times | follows from X1 |
| 10 | does `GPU_THEN_CPU` engage on the 2080 Ti | X1 |
| 12 | tiled, compressed copies of the sources | X7, optional |
| 15 | the ±60° segmentation run manually on the desktop (§29.5): does it de-speckle? | unmeasured; low priority; never start another without asking |
| 24 | what made the 29 Sep map blocky | X6 |
| Q6 | does DN gradient reveal unit boundaries beyond the source image | unexamined; low priority; say so in the final |
| — | which `arcgis.learn` detection models accept 7-band input | first X5 run |

### 5.8 Housekeeping left

- **`_removed_not_Mars` (711 MB) is in the drive's Recycle Bin**, sent from the laptop's Windows account
  (`$RECYCLE.BIN\S-1-5-21-...-1001`). It frees space only when emptied; restoring it is easiest on the
  laptop. Emptying it is the author's call.
- **Copies of the 13 deleted feature classes and the "mars" map** are on the laptop's internal disk only:
  `C:\Users\Loggg\Mars_deleted_2026-10-09\` (not on this drive, not on the desktop) (§50.1).
- `.aprx` backups accumulate in `Mars Project\.backups\` (53 by 2026-10-09); the README's count is checked
  by CI, so update it when backups are added.
- The release GeoPackage of 2026-10-06 still holds the two deleted smoke classes; refresh with the next
  release (§5.6).

### 5.9 Ruled out: do not propose again (`NEXT-STEPS.md` §10)

Segmentation at ±60° · calibrated thermal inertia from the held mosaics · copying the project to internal
disk · the 100 m Composite Bands (`make_global_stack.py`) · CRISM, SHARAD/MARSIS, a global CTX mosaic ·
correcting the delivered prospectus or Presentation 1 · crater ages from closed-depression counts ·
the agent digitising for the author.

## 6. End of every session (C)

1. Record what was done and measured in the KB (new section, tagged); strike done items in
   `NEXT-STEPS.md` and rewrite its "Resume here".
2. `audit_record.py` (on a machine without a Claude memory folder its memory checks print SKIP, not ok),
   `neutral_voice.py --check <edited files>`, `verify_all.py`, and `verify_interim.py` if `interim.py` moved.
3. `github_sync.py` (no `--commit`), then in the clone `python tools/check_repo.py`; update the README's
   counts it flags (build scripts, `.aprx` backups, layouts) and its "Where it stands" / results.
4. Commit by hand with a descriptive message and the attribution trailer, push (standing approval after
   the checks pass), and check CI (`gh run list --limit 1`).
5. **The clone sits in OneDrive, shared by both machines:** let OneDrive finish syncing before git work;
   never commit from both machines at once; `git status` can show phantom changes (confirm with
   `git diff`); never `git stash`; files named `*-DESKTOP-PJS73RO.*` are OneDrive conflict copies: check each
   against history, then delete it; never commit one. `gh` must be logged in on the desktop.
