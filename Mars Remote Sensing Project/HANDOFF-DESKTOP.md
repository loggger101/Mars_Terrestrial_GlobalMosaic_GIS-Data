# Working on the Mars Global Mosaic: the operating guide

How to pick the project up on either machine: the first ten minutes, where everything is, the working rules, and the
end of a session. Current to 2026-10-26.

**Read this file first, then `NEXT-STEPS.md` "Resume here" (the state, the dates and every open task), then
`PROJECT-KNOWLEDGE.md` as needed.** The record (`PROJECT-KNOWLEDGE.md`, "KB" below; § numbers point into it, and its
"where to look" table maps topics to sections) is the authority on what is true; this file and `NEXT-STEPS.md` are
plans. When they disagree, the KB wins and the plan is fixed.

---

## 1. The first ten minutes

1. **Which machine and drive letter?** `hostname`: the desktop is `DESKTOP-PJS73RO` (Windows user `Owner`; i7-8700K,
   64 GB, RTX 2080 Ti) and the drive is **`F:`**; on the laptop it is **`Z:`**. Every build script finds its drive from
   its own location (`build\paths.py`, KB §40.2).
2. **Is ArcGIS Pro closed?** Every script that writes the `.aprx` or the gdb asserts it. Reading with Pro open is fine.
3. **Is anything running?** Long jobs run detached and log to `build\logs\*_<host>.log`; check for `python.exe`
   (`Get-CimInstance Win32_Process`) before starting another.
4. **The junctions.** `<drive>\TypeArea`, `Global60` and `Athabasca` (the no-space aliases Spatial Analyst needs, KB
   §19.1) store an absolute target, so they work on one drive letter at a time: since 2026-10-13 they point at `F:` and
   are broken on the laptop (KB §58). Before a Spatial Analyst run on the other machine, retarget them with
   `build\retarget_junction.py` (the scripts print the command); the first machine then needs them retargeted back. On
   a machine new to the drive, run the preflight with the ArcGIS Pro Python:
   `python "<drive>\Mars Remote Sensing Project\build\desktop_check.py" --gpu` (junctions, GPU, deep-learning libraries).
5. **What changed since last time?** `NEXT-STEPS.md` "Resume here", the review tally (`python build\accept_reviewed.py`,
   a dry run), new files on the drive, and the GP history (KB §9). Plan from that, not from a snapshot.

## 2. Where everything is

| what | where |
|---|---|
| the record | `Mars Remote Sensing Project\PROJECT-KNOWLEDGE.md` (§1–§16 reference, §17 on the dated log; §11 open questions; tags `[V]` verified, `[E]` earlier, `[?]` open) |
| the plan | `Mars Remote Sensing Project\NEXT-STEPS.md` ("Resume here"; standing §1; decisions §2; after-review steps §3; tests §4; desktop jobs §5; the review §6; figures and the final §7; schedule §8; risks §9; ruled out §10) |
| the interim plan | `Mars Remote Sensing Project\INTERIM-PLAN.md` (the living build and its commands §0; progress facts §3; hypotheses §5; timeline §6; wording traps §7) |
| scripts | `Mars Remote Sensing Project\build\` (163 `.py` / `.ps1`; catalogue in the repo's `docs/scripts.md`); logs and test results in `build\logs\` |
| interim deck and report | `Mars Remote Sensing Project\NEXT STUFF\Mars Global Mosaic - Interim Presentation.pptx` (30 slides) and `Mars Mosaic - Interim Report.docx` (23 pages), built from `build\interim.py` |
| ArcGIS project | `Mars Project\Mars Project.aprx` (33 maps, 17 layouts, KB §5); `Mars Project\Mars Project.gdb` (KB §6); `.aprx` backups in `Mars Project\.backups\` (one per write; drive only) |
| layout PNGs | `Mars Project\Global60\layouts\` (04–17) and `Mars Project\TypeArea\layouts\` (01–03) |
| ±60° products | `Mars Project\Global60\` (its `README.md` lists them): `global60_svm_stack_200m.tif` (the 7-band stack), **`global60_landforms_svm_200m_mode11.tif` (the published map)**; `build\grid60.py` defines the grid |
| type areas | `Mars Project\TypeArea\` (`ius_*`) and `Mars Project\Athabasca\` (`ath_*`); windows in `build\areas.py` |
| reference data | `Mars Project\Reference\` (USGS SIM 3292, Robbins craters, TES thermal inertia; third-party, never mirrored) |
| deep-learning exports | `Mars Project\LabeledObjects\global60_svm_stack_200m_train\` (**train on this one only**); `...\global60_svm_stack_200m\` holds the held-out labels too: never train on it |
| source mosaics | the drive root: Viking MDIM 2.1 colour, THEMIS day IR v12, THEMIS night IR v14 (±60°), HRSC/MOLA blend DEM; pyramids built |
| public backup and project page | GitHub `loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data`; clone at `~\OneDrive\Documents\GitHub\Mars_Terrestrial_GlobalMosaic_GIS-Data`; releases `data-2026-10-21` (both type areas, the U-Net maps, the deep-learning models) and `derivatives-2026-10-06` (KB §35, §57.4, §63.2, §66.10) |
| agent memories (private) | the laptop's, mirrored read-only to `~\OneDrive\Documents\Github Knowledge\memory\loggg\z-drive\`; the desktop has its own for `F:` |

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
  `--aprx <copy>` on a copy placed **beside** the real `.aprx` (it stores relative paths, §13.3).
- **The builders wipe and rebuild their maps.** Order when several run: `make_global60_maps.py --cell 200`
  (the published map; the default cell is 400), `make_candidate_maps.py`, `make_mosaic_layout.py`,
  `make_reference_maps.py` (graticules back on the maps the first one wipes), `make_geomap_sheet.py --cell 200`,
  `make_validation_sheet.py`, `make_global60_candidate_sheets.py`, `make_athabasca_layout.py` (layout 15; adds
  its own graticule), `make_dl_map.py` and `make_unet_map.py` (layouts 16, 17), then `polish_layouts.py`
  (§57, §63, §66.4, §66.9). A text-only change can go into the builder and the `.aprx` element directly, without
  a rebuild (§67.2).
- **After any layout builder, run `polish_layouts.py`** (Arial everywhere), export with `--export <scratch>`,
  **read every changed sheet** (`isOverflowing` catches none of the defects found by reading, §33, §49), and
  copy the polished sheets into `Global60\layouts\`: the builders' own PNGs there are written before polishing.
- **Long jobs:** run detached with Python's output redirected by `cmd /c ... > log 2>&1`. Never stop a
  PowerShell queue that runs `& $py ... *> log`: it pipes the job's output, and killing it breaks the job.
  Two Pro runs at once are safe when each has its own inputs, model, scratch folder and logs (§56.1).
- **Queues** (`build\run_rehearsal_v2p.ps1` is the one to copy, `-From <step>` to resume) write their own log with a
  retrying `[IO.File]::AppendAllText`: `Add-Content` under `$ErrorActionPreference = "Stop"` ended a queue when a
  watcher held the file. A watcher counts "queue done" lines; the log keeps earlier runs' lines. A PowerShell
  `-replace` whose replacement holds `$_` inserts the whole input: use `.Replace()` (§69.4).
- **`ClassifyPixelsUsingDeepLearning` leaks ~0.28 GB a tile in one process** (40 GB by tile 144; the pagefile ate C:):
  run a ±60° pass in `--tiles` chunks of at most 60, one process each; stop a pass only just after a tile line
  prints, so no tile is left partial (§69.4).
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
- **The class codes are fixed:** 1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground, and from the
  revision D17 (§68) 5 volcanic edifice, 6 apron, 7 fluvial channel. Never renumber or delete a class;
  `Landform_TrainingSamples_terrain` is never written (the revision goes through `_v2_proposals` and the
  author's accept); the seven-class map is published only by D18's held-out rule, its (a) judged on v2 classes
  1–4 (D19, §68.4, §69.4). **`--labels v2p` is a rehearsal** (every proposal taken as proposed), never a result:
  not published, not in the interim, not used for D18; `labelsets.py` keeps its outputs apart by name.
- **Score on held-out data**: `Landform_TrainingSamples_terrain_60_train` (329) and `_60_test` (183), split by
  whole 15° blocks. Never train on the test set.
- **Every number from its source**: the rasters, logs and the KB, never a previous document; round from the log's
  full precision (§48). Every test writes its prediction and verdict rule into the script before it runs (§47, §51).
- **Prove a check can fail** on a planted defect before trusting that it passes (§46, §49–§51).
- **Objective, impersonal voice** everywhere, the public repo included; `build\neutral_voice.py --check <files>`
  exits 1 on a personal pronoun (§39.4).
- **Deletions only on explicit approval**, after an inventory; send to the Recycle Bin, never hard-delete; emptying
  it is the author's call (§37, §50, §57.5). Machine output enters the `Landform_*` digitising classes only
  through an accept in review (§25, §46).
- **Never start a ±60° segmentation, a multi-hour job not in `NEXT-STEPS.md`, or a software install without asking.**

## 4. End of every session

1. Record what was done and measured in the KB (a new dated section, tagged; edit any §1–§16 fact it changes);
   remove done items from `NEXT-STEPS.md` and rewrite its "Resume here".
2. `audit_record.py` (under the ArcGIS Python, so it also counts the gdb), `neutral_voice.py --check <edited files>`,
   `verify_all.py`, and `verify_interim.py` if `interim.py` or the KB moved (with `final.py` and the paper's `.tex`
   as its argument for the final, KB §69.3).
3. `github_sync.py` (no `--commit`), then in the clone `python tools/check_repo.py`; update the README's counts
   it flags and its "Where it stands", next steps and results, **current state only**. When a layout or figure
   changed, first `py -3 tools/make_thumbs.py` in the clone: the pages show its 800 px previews, and
   `check_repo.py` fails on a preview older than its source (KB §67.1).
4. Commit by hand with a descriptive message and the attribution trailer, push (standing approval after the
   checks pass), and check CI (`gh run list --limit 1`).
5. **The clone sits in OneDrive, shared by both machines:** fetch and compare with `origin/main` first (the clone
   can lag, KB §58); let OneDrive finish syncing before git work; never commit from both machines at once;
   `git status` can show phantom changes (confirm with `git diff`); never `git stash`; files named
   `*-DESKTOP-PJS73RO.*` (a hyphen) are OneDrive conflict copies: check each against history, then delete it; never
   commit one. The project's own logs end `_DESKTOP-PJS73RO.log` (an underscore).
