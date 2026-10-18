# Working on the Mars Global Mosaic: the operating guide

How to pick the project up on either machine: the first ten minutes, where everything is, the working rules,
every open task with its command, and the end of a session. Current to 2026-10-18.
**Read this file first, then `NEXT-STEPS.md` "Resume here", then `PROJECT-KNOWLEDGE.md` as needed.** The
record (`PROJECT-KNOWLEDGE.md`, "KB" below, § numbers point into it) is the authority on what is true; this
file and `NEXT-STEPS.md` are plans. When they disagree, the KB wins and the plan is fixed.

Deadlines: digitising checkpoint **1 November**, interim data cut **2 November**, interim **mid-November**
(exact day not known; plan against ~13 November), data freeze **22 November**, **final Tuesday 8 December
2026**. No rubric exists for either (D2, KB §50).

---

## 1. The first ten minutes

1. **Which machine and drive letter?** The desktop is `DESKTOP-PJS73RO` (Windows user `Owner`; i7-8700K, 64 GB,
   RTX 2080 Ti): the drive is **`F:`**. On the laptop it is **`Z:`**. Every build script finds its drive from
   its own location (`build\paths.py`, KB §40.2); nothing needs editing for the letter.
2. **Is ArcGIS Pro closed?** Every script that writes the `.aprx` or the gdb asserts it. Reading with Pro open
   is fine.
3. **Is anything running?** Long jobs run detached and log to `build\logs\*_<host>.log`; check for
   `python.exe` processes before starting another.
4. **On a machine new to the drive, run the preflight** with the ArcGIS Pro Python (§3):
   `python "<drive>\Mars Remote Sensing Project\build\desktop_check.py" --gpu`. It checks the three no-space
   junctions (`<drive>\TypeArea`, `Global60`, `Athabasca`, which Spatial Analyst needs; on `F:` they were
   retargeted in place with `build\retarget_junction.py`, KB §53.3), the GPU (it engages on the 2080 Ti, q10)
   and the deep-learning preflight (the libraries need an administrator install, KB §53.5). **A junction
   stores an absolute target, so it works on one drive letter at a time:** since 2026-10-13 all three
   point at `F:\Mars Project\...` and are empty on the laptop (KB §58). Before any Spatial Analyst run on
   `Z:`, retarget them; the desktop then needs them retargeted back.
5. **What changed since last time?** `NEXT-STEPS.md` "Resume here", the review tally (`python
   build\accept_reviewed.py`, a dry run), and the GP history (KB §29 shows how).

## 2. Where everything is

| what | where |
|---|---|
| the record | `Mars Remote Sensing Project\PROJECT-KNOWLEDGE.md` (sections 1–57; §11 open questions; tags `[V]` verified, `[E]` earlier, `[?]` open) |
| the plan | `Mars Remote Sensing Project\NEXT-STEPS.md` ("Resume here"; decisions §2; after-review steps §3; tests §4; desktop jobs §5; the review §6; figures §7; schedule §8; risks §9; ruled out §10) |
| the interim plan | `Mars Remote Sensing Project\INTERIM-PLAN.md` (living deck §0; hypotheses §5; timeline §6; wording traps §7) |
| scripts | `Mars Remote Sensing Project\build\` (148 `.py` / `.ps1` / `.bat`; catalogue in the repo's `docs/scripts.md`); logs and test results in `build\logs\` |
| interim deck and report | `Mars Remote Sensing Project\NEXT STUFF\Mars Global Mosaic - Interim Presentation.pptx` (28 slides) and `Mars Mosaic - Interim Report.docx` (20 pages), built from `build\interim.py` |
| ArcGIS project | `Mars Project\Mars Project.aprx` (26 maps, 14 layouts); `Mars Project\Mars Project.gdb`; `.aprx` backups in `Mars Project\.backups\` (one per write; drive only) |
| layout PNGs | `Mars Project\Global60\layouts\` (04–14) and `Mars Project\TypeArea\layouts\` (01–03) |
| ±60° products | `Mars Project\Global60\`: `global60_svm_stack_200m.tif` (the 7-band stack), **`global60_landforms_svm_200m_mode11.tif` (the published map)**; `build\grid60.py` defines the grid |
| type areas | `Mars Project\TypeArea\` (`ius_*`) and `Mars Project\Athabasca\` (`ath_*`); windows in `build\areas.py` |
| reference data | `Mars Project\Reference\` (USGS SIM 3292, Robbins craters, TES thermal inertia; third-party, never mirrored) |
| deep-learning exports | `Mars Project\LabeledObjects\global60_svm_stack_200m_train\` (**train on this one only**); `...\global60_svm_stack_200m\` holds the held-out labels too: never train on it |
| source mosaics | the drive root: Viking MDIM 2.1 colour, THEMIS day IR v12, THEMIS night IR v14 (±60°), HRSC/MOLA blend DEM; pyramids built (KB §53.1) |
| public backup and project page | GitHub `loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data`; clone at `~\OneDrive\Documents\GitHub\Mars_Terrestrial_GlobalMosaic_GIS-Data`; releases `data-2026-10-16` and `derivatives-2026-10-06` (KB §35, §57.4) |
| agent memories (private) | the laptop's: `~\OneDrive\Documents\Github Knowledge\memory\loggg\z-drive\` (read-only mirror); the desktop has its own for `F:` |

## 3. Working rules (each one learned the hard way; KB section in brackets)

**Tools and machines**
- **Two Pythons, neither does both jobs.** Rasters and `arcpy`: the ArcGIS Pro Python,
  `C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe` on the laptop,
  **`D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe` on the desktop** (§53.0; `paths.arcgis_python()`
  finds it). Decks, reports and charts: system Python (`py -3.13` on the desktop) with `python-pptx`,
  `python-docx`, `matplotlib`, `Pillow`, `PyMuPDF`; run the project's own scripts without `-I`, which hides
  both the script's folder and the user packages. Never `propy.bat`. `import arcpy` costs ~7 s: batch work.
- **No GUI automation.** `arcpy` headless is the channel; the Pro GUI is the author's. Work must end up
  **inside the `.aprx`**, as a layer in a named map, and as a layout if it is a result (§31).
- **Safe-write pattern for the `.aprx`:** the builders back it up to `.backups\` first; rehearse with
  `--aprx <copy>` on a copy placed **beside** the real `.aprx` (it stores relative paths).
- **The builders wipe and rebuild their maps.** Order when several run: `make_global60_maps.py --cell 200`
  (the published map; the default cell is 400), `make_candidate_maps.py`, `make_mosaic_layout.py`,
  `make_reference_maps.py` (graticules back on the maps the first one wipes), `make_geomap_sheet.py --cell 200`,
  `make_validation_sheet.py`, `make_global60_candidate_sheets.py`, then `polish_layouts.py`.
- **After any layout builder, run `polish_layouts.py`** (Arial everywhere), export with `--export <scratch>`,
  **read every changed sheet** (`isOverflowing` catches none of the defects found by reading, §33, §49), and
  copy the polished sheets into `Global60\layouts\`: the builders' own PNGs there are written before polishing.
- **Long jobs:** run detached with Python's output redirected by `cmd /c ... > log 2>&1`. Never stop a
  PowerShell queue that runs `& $py ... *> log`: it pipes the job's output, and killing it breaks the job.
  Two Pro runs at once are safe when each has its own inputs, model, scratch folder and logs (§56.1).
- **Big writes go to internal disk first**, then one copy to the drive; the USB drive dropped off mid-write
  twice (§36.4). Reads cap near 112 MB/s (§2.2). **Never propose copying the project to internal disk.**
- **`tasklist` can hang** for minutes inside a builder's "Pro is closed" check (0 % CPU, a child
  `tasklist.exe`): confirm Pro is closed another way, then stop that `tasklist.exe` (§53.6).
- **Shell traps on Windows:** heredocs and `sed` eat backslashes and line endings: edit with a file editor.
  The KB, the plans and `interim.py` are LF; most `build\*.py` are CRLF; keep each file's own. The cp1252
  console crashes on `≥` / `—` in prints: `sys.stdout.reconfigure(encoding="utf-8")`. Run `.ps1` scripts from
  PowerShell; do not change the execution policy.

**Content**
- **±60°, never "global"**: the analysis extent is the THEMIS night mosaic's, 86.6 % of the surface (§16).
- **"Diurnal-contrast index", never "thermal inertia"** (§24, §28.10, §42.4, §43.1).
- **"Closed depressions ≥ 1 km", never a crater inventory**: for craters use `Ref_Craters_Robbins2020` (§42.3, §53.4).
- **The published landform map is the 200 m 11 × 11 one** (§57); the 400 m maps are superseded (§57.2).
- **Keep the four hand-drawn classes** (1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground, q23).
  Never remove or replace them; a fifth only if a held-out test shows it helps (§43.3).
- **Score on held-out data**: `Landform_TrainingSamples_terrain_60_train` (329) and `_60_test` (183), split by
  whole 15° blocks. Never train on the test set.
- **Every number from its source**: the rasters, logs and the KB, never a previous document (§12). Every test
  writes its prediction and verdict rule into the script before it runs (§47, §51).
- **Prove a check can fail** on a planted defect before trusting that it passes (§46, §49–§51).
- **Objective, impersonal voice** everywhere, the public repo included; `build\neutral_voice.py --check <files>`
  exits 1 on a personal pronoun (§39.4).
- **Deletions only on explicit approval**, after an inventory; send to the Recycle Bin, never hard-delete; emptying
  it is the author's call (§37, §50, §57.5). Machine output enters the `Landform_*` digitising classes only
  through an accept in review (§25, §46).

## 4. State, 2026-10-16

- **Checks green:** `audit_record.py`, `verify_all.py` 37 / 37, `verify_interim.py` (249 numbers),
  `neutral_voice.py`, the repo's `tools/check_repo.py`; pushed, CI passed.
- **Digitising has not started:** 0 of 9,287 candidates reviewed; the three `Landform_*` classes hold 0 rows.
- **Results:** the published map 73.8 %, κ 0.58 held out (§57); thermal +1.36 / +1.97 pt with Pro's SVM (§56);
  465,354 closed depressions and 969,822 channel segments at ±60° (§54.4); T2–T8 as in `NEXT-STEPS.md` §4.

## 5. Every open task

Who: **A** = the author, by hand; **C** = an agent, scripted; **D** = needs the desktop.

### 5.1 Desktop (D + C)

| # | task | command (ArcGIS Python, from `<drive>\Mars Remote Sensing Project\build`) | done when |
|---|---|---|---|
| — | the Deep Learning Libraries (A at the screen for UAC) | `D:\MarsDownloads\dl_libs_37\extracted\ProDeepLearning.msi`, elevated; then `desktop_check.py` | the X5 preflight says ready |
| X5 | deep learning (q25, approved) | `make_dl_model.py --train [--model RETINANET] [--epochs 20]`, then `--detect --emd <model.emd>`, then `--score <detections fc>` | `logs\dl_heldout_score.json`; per-class recall and precision on the 183 held-out polygons in the KB |
| X7 | optional (q12): a tiled, compressed copy of one source, timed | only if panning stays slow | timing in the KB |

### 5.2 The review and digitising (A), the critical path

`NEXT-STEPS.md` §6 has the steps: set `Review` on the candidates in "Ius Chasma — digitising", starting with
"Channels: steep and rock-floored (188)", then the closed depressions; then Athabasca, where the lava margins
settle H1. **Checkpoint 1 November:** if the classes are still empty, the interim presents the machine products
as candidates with their measured recall.

### 5.3 After each review session (C, minutes; Pro closed for the writes)

`NEXT-STEPS.md` §3: `accept_reviewed.py` (dry run, then `--apply --by "<reviewer>"`); layout 14
(`make_validation_sheet.py`, `polish_layouts.py`, read it); `make_t4_channel_h2.py` (stage 2 to write once ≥ 10
fluvial and ≥ 10 volcanic reviewed channels exist); `make_flow_margin_test.py --margins` once margins exist;
`github_export_gdb.py`; then §6.

### 5.4 After the fine pass (C)

Done (KB §53.4–§55.4): verified, layouts 11 and 12 built, in the interim.

### 5.5 The interim (C + A), due ~13 November

- **Ask the author:** the exact due date, and the percentages for the progress table (`interim.py` prints dashes).
- **Living build:** edit `build\interim.py` (one entry per result in `FIGURES`; every number from the KB), then
  `make_interim_figs.py` (ArcGIS Python; Pro may be open), `build_interim_live.py "<deck.pptx>"` and
  `build_interim_report_live.py "<report.docx>"` (system Python; the live files are in `NEXT STUFF\`; back them
  up first). Render: `render_pdf.ps1 -Deck <pptx> -Pdf <pdf>` from PowerShell, the report through Word COM
  (KB §51.5); rasterise with PyMuPDF; **read every changed slide and page**; then `verify_interim.py` (it proves
  each number exists in the KB, not that it sits beside its claim: check new numbers by hand, §48).
- Known fits: the log table holds 13 rows (14 overflow); a whole tall layout is unreadable on a slide (draw a
  chart, as for T8 and T1, §51.5, §57.3); titles over ~60 characters wrap onto the rule.

### 5.6 The final (C + A), due 8 December

- Data freeze **22 November**; figure list and outline in `NEXT-STEPS.md` §7.
- **No final builder exists yet:** write one on the interim's pattern, early enough to rehearse.
- Before each deadline: refresh the GitHub data release (`github_release_bundle.py --upload data-YYYY-MM-DD`,
  then point `github_catalog_rasters.py`'s `DATA` and `github_export_gdb.py`'s `RELEASE` at it, KB §57.4), and
  run `tools/check_remote.py` by hand.

### 5.7 Open questions still `[?]` in KB §11

| q | question | how it closes |
|---|---|---|
| 12 | tiled, compressed copies of the sources | X7, optional |
| 15 | the ±60° segmentation made in the GUI (§29.5): does it de-speckle? | unmeasured; low priority; never start another without asking |
| Q6 | does DN gradient reveal unit boundaries beyond the source image? | unexamined; low priority; say so in the final |
| — | which `arcgis.learn` detection models accept 7-band input | the first X5 run |

### 5.8 Housekeeping left (each the author's call)

- **Recycle Bins:** `_removed_not_Mars` (711 MB, sent from the laptop's account, in the drive's bin) and ~21 GB
  of finished scratch and caches in the desktop's bins (KB §57.5).
- **The two `_60_smoke` classes** recreated by X2's smoke run (KB §57.1).
- **Copies of the 13 classes deleted in §50** are on the laptop's internal disk only:
  `C:\Users\Loggg\Mars_deleted_2026-10-09\`.

### 5.9 Ruled out: do not propose again (`NEXT-STEPS.md` §10)

Segmentation at ±60° · calibrated thermal inertia from the held mosaics · copying the project to internal
disk · the 100 m Composite Bands (`make_global_stack.py`) · CRISM, SHARAD/MARSIS, a global CTX mosaic ·
correcting the delivered prospectus or Presentation 1 · crater ages from closed-depression counts · rerunning
the 400 m map's 180° column · the agent digitising for the author.

## 6. End of every session (C)

1. Record what was done and measured in the KB (new section, tagged); remove done items from `NEXT-STEPS.md`
   and rewrite its "Resume here"; keep this file's §4 and §5 current.
2. `audit_record.py`, `neutral_voice.py --check <edited files>`, `verify_all.py`, and `verify_interim.py` if
   `interim.py` moved.
3. `github_sync.py` (no `--commit`), then in the clone `python tools/check_repo.py`; update the README's counts
   it flags and its "Where it stands", next steps and results, **current state only**.
4. Commit by hand with a descriptive message and the attribution trailer, push (standing approval after the
   checks pass), and check CI (`gh run list --limit 1`).
5. **The clone sits in OneDrive, shared by both machines:** let OneDrive finish syncing before git work; never
   commit from both machines at once; `git status` can show phantom changes (confirm with `git diff`); never
   `git stash`; files named `*-DESKTOP-PJS73RO.*` (a hyphen) are OneDrive conflict copies: check each against
   history, then delete it; never commit one. The project's own logs end `_DESKTOP-PJS73RO.log` (an underscore).
