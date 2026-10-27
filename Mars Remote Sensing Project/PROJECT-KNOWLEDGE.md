# Mars Global Mosaic — Project Knowledge Base

**Owner:** Logan M Edwards · OCN 4704 Remote Sensing · Fall 2026 · Florida Tech
**File:** `<drive>\Mars Remote Sensing Project\PROJECT-KNOWLEDGE.md` (`Z:` on the laptop, `F:` on the desktop)
**Started:** 2026-09-18 · **Last updated:** 2026-10-27 (§69.17).

The record of what is true about this project, and the authority for every number in the plans, the
layouts and the deliverables. How to work is `HANDOFF-DESKTOP.md`; what to do next is `NEXT-STEPS.md`.

**How it is laid out.** §1–§16 are reference and are kept current: when a later section changes one of
their facts, the older text is edited, not left to be contradicted. §17 onward is the dated log, one
section per session, newest last; a log section that a later one supersedes says so at its top. §11 is
the open-questions list. Condensed on 2026-10-18 (§59): the full wording to that date is in git history
and in `.backup_20261018\`.

| Tag | Means |
|---|---|
| **[V]** | Verified by reading the project with `arcpy` / GDAL, on the date of its section. |
| **[E]** | Established earlier, or an inference from verified facts; not re-checked, nothing contradicts it. |
| **[?]** | Open, conflicting or assumed. Never put it in a deliverable before resolving it. |

Additions must be tagged. An untagged claim is worth nothing six weeks later.

**Where to look**

| topic | sections |
|---|---|
| sources, the three frames, the ±60° grid | §3, §4, §15, §16, §28.1–§28.2 |
| the ArcGIS project and the gdb | §5, §6 |
| the map layouts: builders, polish, defects found by reading | §5, §22, §33, §61, §63, §64, §65, §67 |
| how scripted work is done, and its traps | §2, §9, §12, §13 |
| what the THEMIS pair can and cannot do | §24, §28.10, §40.1, §42.4, §43.1, §56, §62 |
| classification: type area | §19, §23, §27 |
| classification: ±60°, the published map | §31, §32.2, §55.3, §57 |
| the class scheme and the labels' audit | §29.2, §43.3, §68, §69.2 |
| the final builds: the AASTeX paper and the deck | §69; what would strengthen them, §69.17 (`NEXT-STEPS.md` §12) |
| craters and closed depressions | §26, §28.11, §42.3, §53.4, §53.6 |
| channels | §25, §47.4, §53.4, §53.6, §54.4 |
| lava flows and the geologic map | §41, §43.2, §43.3, §44, §47.2 |
| tests T1–T8 and the hypotheses | §40.1, §42.2–§42.4, §43, §47, §51.1, §56 (status: `NEXT-STEPS.md` §4) |
| the GUI work of 24 Sep–1 Oct and its checks | §29, §30, §53.2 |
| digitising by review | §46, §49 |
| the 180° column | §54, §55.1 |
| GitHub backup and releases | §35, §57.4, §63.2 (`data-2026-10-19`, the first with Athabasca), §66.10 (`data-2026-10-21`, the first with the deep-learning models) |
| the interim builds | §39.3, §45, §48, §51.5, §57.3, §66.10, §67 |

---

## 1. What the project is

**"Mars Global Mosaic"** is the project's own title (in full: *"Mars Global Mosaic: Mapping Lava Flows,
Fluvial Channels, and Impact Craters in Visible and Infrared"*, §14.1); use it, don't invent one. A
co-registered visible + thermal-infrared mosaic of Mars, used to map lava flows, fluvial channels and
impact craters. **[E]**

**The analysis extent is ±60° latitude, not the globe** (§16): built from global products, the
co-registered stack spans ±60°, 86.6 % of the surface, set by THEMIS night coverage.

**Deliverables.** Presentation 1 and the prospectus are **delivered and presented**: history, not to be
corrected (§14.5). Left: the **interim** report + presentation, due **mid-November 2026** (exact day not
given **[?]**), and the **final**, due **Tuesday 8 December 2026** **[V]**. No rubric exists for either
(§50). The working dates are in `NEXT-STEPS.md`.

> **The standing directive, 2026-09-19: "just worry about getting data worked and laid out."** Work the
> data and the layouts, not document prose; spend no time repairing delivered documents.

---

## 2. How to work on this project

### 2.1 The two machines **[V]**

| | **Laptop** | **Desktop** `DESKTOP-PJS73RO` (Windows user `Owner`) |
|---|---|---|
| Model / CPU | HP OmniBook 3 16-bu0xxx; Intel Core Ultra 5 225U, ~15 W, 12 cores / 14 threads | Intel i7-8700K, 95 W, 6 cores / 12 threads |
| RAM | **15.4 GB** | **64 GB DDR4** |
| GPU | Intel integrated, none usable | **NVIDIA RTX 2080 Ti**, 11 GB; engages (§2.3) |
| Internal disk | 477 GB NVMe | ~32 GB free on `C:` (scratch `C:\MarsScratch\`); ArcGIS Pro on `D:` (§53.0) |
| The drive | `Z:` | `F:` |

**Heavy runs go to the desktop**, and RAM is the reason, not the CPU: a job over a 15–23-billion-pixel
raster has room in 64 GB and not in the laptop's ~5.5 GB free. The GPU and the absence of a thermal
ceiling on multi-hour runs come second. The laptop is for metadata, small windows, figures from cached
arrays and editing. **The laptop sleeps:** a script's printed elapsed time includes suspend (§28.9).

### 2.2 The drive is the bottleneck, permanently **[V]**

The drive is a **Seagate Backup Plus Slim, a 2.5-inch HDD on USB**, 1863 GB. Full-resolution reads on
the laptop ran at **~112 MB/s**, USB-3 HDD speed: those runs were I/O-bound, and a faster CPU changes
nothing about them.

**Decided 2026-09-18: the project stays on the external drive and is never copied to internal disk**;
it will outgrow both computers (250 GB on that date, `Mars Project.gdb` alone 138 GB). Never propose the
copy. The levers that remain:

- **Pyramids** on the four sources: built 2026-10-13, ~34× faster overview reads (§53.1).
- **Scratch on internal SSD**, not on the drive; **big outputs are built on internal disk and copied to
  the drive once** (the drive dropped off USB mid-write twice, §36.4).
- **Cache decimated reads to `.npy`** (§9) and never re-read a global when a cached array will do.
- **Tiled, compressed copies** of the sources might read faster (fewer bytes, no whole-row reads, §9):
  untested, a decision, not a tweak (§11 q12). **[?]**

### 2.3 The GPU **[V]**

`GPU_THEN_CPU` engages on the 2080 Ti: `arcpy.ddd.Slope` on the Ius DEM took 2.77 s against 7.63 s with
`CPU_ONLY`, and the tool says so (*WARNING 010453*: the GPU also drives the display, so very long GPU jobs
risk a driver reset) (§53.3). On the laptop the same tool logs *"No compatible GPU device has been
detected."* Not GPU tools: `IsoCluster`, `MLClassify`, `SegmentMeanShift`, `CompositeBands`.
`arcpy.sa.Slope` (map algebra) returns no GP messages, so it cannot show whether the GPU ran (§51.2).

### 2.4 Tooling **[V]**

- **No GUI automation.** Everything runs through `arcpy`, headless; the Pro GUI is the author's.
- **ArcGIS Pro 3.7**, Python 3.13.13; `CheckExtension` gives **Available** for 3D, Spatial and
  ImageAnalyst. Its Python: `C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe` on the
  laptop, `D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe` on the desktop; `paths.arcgis_python()`
  finds it from the registry. **Never `propy.bat`** (it does not quote its own path).
- **Deep Learning Libraries 3.7.1901: on the desktop only** (installed 2026-10-19, §66; `torch`, `torchvision`,
  `fastai`, `arcgis.learn`, CUDA on the 2080 Ti). The laptop has none, so X5 runs on the desktop.
- **Two Pythons, neither does both jobs:**

| | ArcGIS Python | System Python (3.14.6 laptop; `py -3.13` desktop) |
|---|---|---|
| `osgeo.gdal`, `arcpy` | **yes** | **no** |
| `pptx`, `docx`, PyMuPDF | **no** | **yes** (on the desktop since §53.3) |
| numpy, matplotlib, PIL | yes | yes |

  Rasters run on the ArcGIS one, decks and reports on the system one.
- **Close ArcGIS Pro before any write to the `.aprx` or the gdb**; reading with Pro open is fine.
- **The drive is not always mounted**; check before planning a run. **[E]**
- **Every build script finds its drive** from its own location (`build\paths.py`, §40.2). The exception
  is the three no-space junctions at the drive root (`TypeArea`, `Global60`, `Athabasca`, needed by legacy
  Spatial Analyst, §19.1): a junction stores an absolute target, so it serves one drive letter at a time.
  Since 2026-10-13 they point at `F:` and are broken on `Z:`; `retarget_junction.py` moves them (§53.3, §58).

### 2.5 The drive is the project's home; GitHub is the backup

**Stated 2026-09-18:** `<drive>\Mars Project\` (the ArcGIS project) and `<drive>\Mars Remote Sensing
Project\` (this file, `build\`, the deliverables) hold just about everything, and scripted sessions
have a standing go-ahead to create and edit files there. The old
`C:\Users\Loggg\OneDrive\Documents\ArcGIS\Projects\Mars Project` folder is gone, and with it three files
the maps referenced (§3); one home is what prevents a repeat.

**Since 2026-10-06 the irreplaceable part is backed up to GitHub** (§35): the tree (this file, the scripts,
the `.aprx`, the vectors, the hand-drawn labels) and two releases of rasters. What is at stake if the drive
dies:

| | Size | If the drive dies |
|---|---|---|
| `Mars Remote Sensing Project\`: this file, `build\`, the decks and reports | **2.5 GB** (1.98 GB of it `build\`'s `.npy` caches, which are in a release; the rest in git) | irreplaceable, in git |
| The source GeoTIFFs at the drive root | 62.1 GB (57.8 GiB) | re-downloadable (README links them) |
| `Mars Project\`: `Mars Project.gdb` 225 GB, `Global60\` 124 GB, `LabeledObjects\` 7.7 GB, the rest 7.6 GB | 364 GB | re-computable, hours of desktop time; most of `Global60\` is in a release |
| Measured 2026-10-22 (§67.4), decimal GB | **429 GB** | |

Care rules that stand: **prefer additive writes**; **never delete from the drive without asking**, and
then to the Recycle Bin, never a hard delete (emptying it is the author's call); **close Pro before
writing the `.aprx`**; destructive changes and overwriting a hand-edited deliverable are asked about.

---

## 3. The data actually held

**Four** global GeoTIFFs at the drive root, **~58 GB** together (this table's "GB" are GiB, 2³⁰ bytes, as
Windows reports them: 62.1 decimal GB, the unit the README uses); THEMIS Night IR was added on 2026-09-18
(§15). A recursive search finds no other source imagery. **[V]** Derived rasters live in
`Mars Project\TypeArea\`, `Athabasca\` and `Global60\`, and are not counted here.

| File | Size | Dimensions | Bands | Type | Cell | CRS | Central meridian | NoData |
|---|---|---|---|---|---|---|---|---|
| `Mars_Viking_MDIM21_ClrMosaic_global_232m.tif` | 11.87 GB | 92,160 × 46,080 | 3 | U8 | 231.542 m | `SimpleCylindrical_Mars` | **0°** | **0.0** |
| `Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif` | 21.21 GB | 213,390 × 106,696 | 1 | U8 | 100 m | `SimpleCylindrical_Mars` | **180°** | **0.0** |
| `Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif` | 10.60 GB | 106,694 × 53,347 | 1 | S16 | 0.00337412° | `GCS_Mars_2000_Sphere` | geographic | **−32768** |
| `Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif` | 14.14 GB | 213,388 × 71,130 | 1 | U8 | 100 m | `SimpleCylindrical_Mars` | **180°** | **0.0** |

All of the above **[V]**. All four are uncompressed, band-interleaved, and stored **one scanline per
block** (`block = width × 1`), so a windowed read pulls whole rows (§9). **Pyramids are built** on all four
since 2026-10-13: 15.0 GB of external `.ovr` (§53.1). The DEM's **last column is defective** (nodata in
24,335 rows, wrong values elsewhere), and the file ends 0.46 px short of +180°; the ±60° derivatives patch
it (§54).

**Statistics** (from the `.aux.xml` sidecars and GDAL, every pixel) **[V]**:

| | min | max | mean | stddev | median | valid px |
|---|---|---|---|---|---|---|
| DEM | −8528 m | +21226 m | −720.54254 | 2976.46528 | −360.235 | 5,691,764,861 (99.9993 %) |
| THEMIS Day IR | **1** | 255 | 125.74638 | 34.36466 | 125 | 22,143,880,259 of 22,767,859,440 (97.26 %) |
| THEMIS Night IR | 1 | 255 | 124.60 | 32.79 | — | — |

THEMIS DN 0 is NoData, so valid data run 1–255. **Viking MDIM**, every one of its 4,246,732,800 pixels valid
(no fill at all, minimum 18, although NoData is declared 0):

| Band | min | max | mean | stddev |
|---|---|---|---|---|
| 1 | 18 | **207** | 122.83502 | 31.58019 |
| 2 | 18 | 231 | 97.26186 | 32.86124 |
| 3 | 18 | 255 | 95.77282 | 35.51307 |

Band 1's maximum of **207** is a real clip (a histogram spike).

**Reference data**, third-party, in `Mars Project\Reference\` (§41): the USGS geologic map SIM 3292, the
Robbins & Hynek crater database (2020 release), TES thermal inertia (Putzig & Mellon 2007). **Not held
locally:** CTX and CRISM. CTX is reachable as the hosted Esri service `Global CTX Mosaic of Mars (V01)`
in `Map2`. **[V]**

**Gone for good, do not re-acquire:** the Jezero HiRISE orthomosaic, the Mercury MESSENGER basemap and the
Enceladus DEM did not survive the move off `C:`. The maps that referenced them are out of the project
(§37, §50); 0 broken layers remain (§58.1). **[V]**

---

## 4. The trap that has cost the most time

**The project spans three coordinate frames, not two.** **[V]**

1. THEMIS Day and Night IR: **central meridian 180°**, grid 0–360°E.
2. Viking MDIM: **central meridian 0°**, grid −180–180°E.
3. The DEM: **`GCS_Mars_2000_Sphere`**, degrees, not metres.

- **A THEMIS window read at face value lands half a planet away.** Read `GetProjParm('Central_Meridian')`
  per file before windowing; a misregistration is silent. **[E]** To reproduce it for a figure, shift the
  window's longitudes by 180°.
- The metre / degree split is why every early DEM derivative logged **WARNING 000869** (*"The Z units of the
  output geographical spatial reference are undefined. A default Z factor of 1 was used."*). Projecting
  first removes it (§20). **[V]**
- It is the likely reason the early global Composite Bands runs never completed; the logs record only
  user cancellations, never a CRS error, so this stays an inference. **[?]**

The cure is one grid read from the night mosaic, `build\grid60.py` (§28.1), and for the type areas the
stack script's 100 m grid snapped to the day mosaic (§18.1).

---

## 5. Project structure

`Mars Project\Mars Project.aprx`, read with `arcpy.mp` on 2026-10-23 (§63, §66.9, §69.2) **[V]**: **33 maps, all in
Mars coordinate systems, and 17 layouts** (17 since §66.9); 0 broken data sources, none reading through a junction (145
non-group layers on 2026-10-18, §58.1; layout 15 added four maps and 13 layers; X5's map one map and 6 layers,
§66.3; X5c's one map and 9 layers, §66.9; "Labels v2: proposals" one map and 9 layers on a basemap, §69.2); 7 hosted services (Esri OnMars MDIM, CTX, MOLA/HRSC, the Perseverance / Jezero feeds).
`defaultGeodatabase` = `<drive>\Mars Project\Mars Project.gdb`; `homeFolder` = `<drive>\Mars Project`. The
`.aprx` stores relative paths, so it opens from either drive letter.

| Layout | Shows | Built by |
|---|---|---|
| `01_visible`, `02_night_ir`, `03_classification` | Ius Chasma: Viking, night IR, Iso Cluster | `make_typearea_layouts.py` (§22) |
| `04_global60_landforms` | the published ±60° landform map, scored | `make_global60_maps.py --cell 200` (§57) |
| `05_svm_checks` | the 29–30 Sep GUI SVM maps, checked | `make_global60_maps.py` (§30, §31.1) |
| `06_ius_digitising`, `09_athabasca_digitising` | the digitising candidates per type area | `make_candidate_maps.py` (§32.1, §42.1) |
| `07_global60_basins` | basins ≥ 20 km | `make_candidate_maps.py` (§32.1) |
| `08_global60_mosaic` | the mosaic at ±60°: visible, day, night, topography | `make_mosaic_layout.py` (§38) |
| `10_global60_locator` | type areas and the geologic map's volcanic units | `make_reference_maps.py` (§44) |
| `11_global60_depressions`, `12_global60_channels` | the ±60° fine pass | `make_global60_candidate_sheets.py` (§53.6, §55.4) |
| `13_geomap_check` | T8, the classes against the geologic map | `make_geomap_sheet.py --cell 200` (§49, §57.1) |
| `14_validation` | the review's precision and recall | `make_validation_sheet.py` (§49) |
| `15_athabasca_type_area` | Athabasca Valles: visible, night IR, day IR, topography, with unit `lAv` | `make_athabasca_layout.py` (§63) |
| `16_x5_detections` | X5, the deep-learning detector, scored per held-out polygon | `make_dl_map.py` (§66.4) |
| `17_x5c_unet_provinces` | X5c, the U-Net terrain-province map, beside the published SVM map | `make_unet_map.py` (§66.9) |

The ±60° sheets (04, 05, 07, 08, 10–13, 16) draw in geographic `GCS_Mars_2000`, so 0°E is at the centre (08 since §64);
the type-area sheets (01–03, 06, 09, 14, 15) draw in `Mars_Equidistant_Cylindrical_CM180`, and their footers name it. **[V]**

Polished exports are in `Mars Project\TypeArea\layouts\` (01–03) and `Mars Project\Global60\layouts\` (04–17);
the builders' own PNGs are written before `polish_layouts.py` runs, so copy the polished export over them.

- **Map names are not unique**: two maps are named `Mars` (one `Mars_2000_(Sphere)`, one
  `GCS_Mars_2000_Sphere`). Never select a map by name alone in a script; index it, or match the spatial
  reference too. **[V]**
- `Jezero_CTX_BlockAdj_dd_Clip` is a hosted tile service (`CIMTiledServiceLayer`) and a duplicate of the
  `Jezero Crater Clipped` layer beside it; its `dataSource` raises rather than returning empty. **[V]**

---

## 6. Geodatabase inventory

`Mars Project.gdb`, read with `arcpy` on 2026-10-18 (§58.2); X5's detections added 2026-10-19 (§66.3), the label
proposals 2026-10-23 (§69.2), read again 2026-10-24 (§69.3), the rehearsal labels the same day (§69.4), the v2 labels 2026-10-27 (§69.8). All of
§6 is **[V]**.

### Feature classes — 37 present

| Dataset | Geometry | Rows | Made by |
|---|---|---|---|
| `MARS_nomenclature_craters_lt100km_March2019` | Point | **972** | IAU gazetteer |
| `MARS_nomenclature_misc_March2019` | Point | 337 | IAU gazetteer |
| `MARS_nomenclature_classicalbedo_March2019` | Point | 303 | IAU gazetteer |
| `MARS_nomenclature_craters_gt100km_March2019` | Point | **141** | IAU gazetteer |
| `MARS_nomenclature_albedo_March2019` | Point | 126 | IAU gazetteer |
| `Landform_LavaFlowMargins`, `Landform_ChannelCenterlines`, `Landform_CraterRims` | Polyline, Polyline, Polygon | **0, 94, 26** | the digitising classes (§19.4, §46); the 120 copied from the Ius review (§69.7) |
| `Landform_ChannelCandidates_auto` | Polyline | 2,610 | Ius channel candidates (§25) |
| `Landform_CraterCandidates_auto` | Polygon | 1,685 | Ius closed depressions ≥ 1 km (§26) |
| `Landform_ChannelCandidates_auto_ath` | Polyline | 3,283 | Athabasca channel candidates (§42.1) |
| `Landform_CraterCandidates_auto_ath` | Polygon | 1,709 | Athabasca closed depressions ≥ 1 km (§42.1) |
| `Landform_BasinCandidates_auto_60` | Point | 5,144 | ±60° basins ≥ 20 km, coarse pass (§28.11) |
| `Landform_CraterCandidates_auto_60` | Point | 465,354 | ±60° closed depressions ≥ 1 km (§54.4) |
| `Landform_ChannelCandidates_auto_60` | Polyline | 969,822 | ±60° routed channels (§54.4) |
| `Landform_CraterCandidates_auto_60_smoke`, `Landform_ChannelCandidates_auto_60_smoke` | Point, Polyline | 8,098, 5,305 | X2's smoke run (§53.3); deleting them is open decision D14 |
| `Landform_TrainingSamples_terrain` | Polygon | 512 | **the hand-drawn labels** (§29.2); never overwrite |
| `Landform_TrainingSamples_terrain_60_train`, `_60_test` | Polygon | 329, 183 | the labels clipped to ±60° and split by 15° blocks (§31.3) |
| `Landform_TrainingSamples_v2_proposals` | Polygon | 1,086 | the seven-class proposals (§69.2): the 512 copied with an `Action` (474 keep, 12 relabel, 23 check, 1 clip, 1 delete, 1 fix) and 574 new; for the author's review (2b), never a training set until applied |
| `Landform_TrainingSamples_v2p`, `_v2p_60_train`, `_v2p_60_test` | Polygon | 1,085, 827, 258 | the rehearsal labels (§69.4): every proposal taken as proposed, **not the author's review**; for `--labels v2p` only |
| `Landform_TrainingSamples_v2`, `_v2_60_train`, `_v2_60_test` | Polygon | 971, 734, 237 | the seven-class labels from the review (§69.8; apron and fluvial rows by the agent's rule at the author's word); for `--labels v2` |
| `DL_Detections_heldout_20261019` | Polygon | 1,838 | X5's RetinaNet boxes around the held-out labels (§66.2); stack SR, XY domain widened 400 km (§66.3) |
| `DL_UNet_Heldout_Scores_20261020` | Polygon | 183 | the held-out labels with each one's own-class share and majority class under the U-Net (two passes) and the published SVM map, at 400 m (§66.9) |
| `TrainingSamples_202609290009589587982` | Polygon | 455 | manual (GUI), 29 Sep (§29.2) |
| `Analysis_Extent_60` | Polygon | 1 | the ±60° clip shape (§31) |
| `Check_Tiles_4096px_60` | Polygon | 954 | the §30.2 tile grid (§31.1) |
| `Ref_SIM3292_GeologicUnits` | Polygon | 1,311 | USGS geologic map units (§41, §47.1) |
| `Ref_Craters_Robbins2020` | Point | 385,049 | the Robbins crater database (§41) |
| `Graticule_30deg`, `Graticule_2deg` | Polyline | 17, 25 | graticules as data (§44) |
| `Type_Areas` | Polygon | 2 | the two windows of `areas.py` (§44) |

**No tables.** The candidate classes are deliberately separate from the `Landform_*` digitising classes:
machine output enters those only through an accept in review (`accept_reviewed.py`, §46). Every candidate
row carries `Confidence='inferred'`. The IAU layers are a **gazetteer**, named features, not a crater
population: 141 craters > 100 km and 972 < 100 km planet-wide; never present them as a crater count. The
`_2` / `_3` duplicates, `Line`, `Point` and the first smoke classes were deleted on approval (§50).

### Rasters — 15 rasters

| Raster | Dimensions | Type | Grid | Note |
|---|---|---|---|---|
| `Slope_Mars_H1` | 106,694 × 53,347 | F32 | DEM, degrees | percent rise on a degree grid (§7) |
| `Slope_Mars_M1` | 213,390 × 106,696 | F32 | THEMIS, CM 180 | DN gradient, not slope (§7) |
| `Slope_Mars_V1` | 92,160 × 46,080 | F32 | Viking, CM 0 | DN gradient, not slope (§7) |
| `Surface_Mars1` | 92,160 × 46,080 | F32 | Viking, CM 0 | `SurfaceParameters` on imagery (§7) |
| `HillSha_Mars1` | 106,694 × 53,347 | U8 | DEM, degrees | z-factor 1 on a degree grid (§7) |
| `Segmented_202609081925347487376` + `_interIndex` | 106,694 × 53,347 | U8 ×3, S32 | DEM, degrees | 8 Sep segmentation of the DEM (§7) |
| `Mars_MO_THEMIS_CompositeBand` | 213,388 × 71,130 | ×2 | night grid | GUI, 24 Sep (§29.1) |
| `Segmented_202609290011302066080` + `_interIndex` | 213,388 × 71,130 | ×3, ×1 | night grid | GUI ±60° segmentation, 29 Sep (§29.5) |
| `Classified_202609292109007048151` | 213,388 × 71,130 | ×1 | night grid | GUI SVM, 29 Sep; tile artefact, unusable (§30.2) |
| `CompositeBand` | 92,160 × 46,080 | ×7 | Viking, CM 0 | GUI, 30 Sep (§29.4) |
| `Classified_202609300147338582853` | 92,160 × 46,080 | ×1 | Viking, CM 0 | GUI SVM, 30 Sep; mostly elevation (§30.3) |
| `Classified_…_0based` ×2 | as above | ×1 | as above | the two GUI maps before their recode (§36.4) |

Every classified raster's pixel value is its class code (§36). The valid derivatives are the type-area
`ius_*` / `ath_*` products and `Global60\` (§20, §28.8, §31.2).

---

## 7. Derived products and what is wrong with each

The legacy global derivatives in the gdb predate the project's own pipeline; none is used by a result.

- **Every `Slope_*` layer is PERCENT_RISE, not degrees** **[V]**: the lineage reads
  `Slope <dem> -> Slope_Mars_H1 PERCENT_RISE 1 PLANAR METER CPU_ONLY` (likewise M1, and V1 with
  `GPU_THEN_CPU`). `Slope_Mars_H1` reaches 400.13, M1 141.99, impossible in degrees. **Never describe them
  as degrees**; an old "0–90°, mean 89.74° (saturated)" figure attached to them came from elsewhere.
- **`Slope_Mars_M1` and `Slope_Mars_V1` are DN gradient**, `Slope` run on imagery; the maps call them
  `Gradient_Mars_M1` / `Gradient_Mars_V1`, the gdb names still say `Slope_*`. `Surface_Mars1` is
  `SurfaceParameters SLOPE` on the Viking imagery (max 4223). **[V]**
- **`HillSha_Mars1`** (`225 45 SHADOWS 1`) carries the same z-factor-1-on-degrees defect. **[V]**
- **The 8 Sep segmentation** (`SegmentMeanShift` 20 / 20 / 5) ran on the **Mars DEM**, not on Mercury as the
  interim of September said: **65,474 segments**, the maximum-detail setting (§23.3). **[V]**
- **The Mercury Iso Cluster rehearsal** (10 classes, minimum size 20, interval 10) is out of the project
  (§37); its settings are where the early segmentation parameters came from. Re-running `MLClassify` on
  `IsoClusterUnsupervisedClassification`'s own signature file reproduces its output exactly: the tool
  already runs both steps (§19.2). **[V]**

The valid terrain derivatives are `ius_*` at 100 m (§20) and `global60_*` at 200 m (§28.8, patched §54).
Do not carry the "2 classes per 3 requested" collapse rule over from other coursework: check fill fraction
and class dominance first.

---

## 8. Processing history

The `GpMessages\` XML records, read 2026-09-18 and 2026-10-01 **[V]**:

| # | Started | Ended | Elapsed | Result | Notes |
|---|---|---|---|---|---|
| 1 | 09 Sep 11:52:35 | 12:40:32 | **47 m 57 s** | FAILED | CompositeBands, `Operation cancelled by user` |
| 2 | 09 Sep 12:43:02 | 12:44:44 | **1 m 41 s** | FAILED | CompositeBands, cancelled |
| 3 | 09 Sep 12:44:51 | 13:59:43 | **1 h 14 m 51 s** | FAILED | CompositeBands, cancelled |
| 4 | 10 Sep 19:44:24 | 19:51:39 | **7 m 15 s** | ok | **WARNING 000869**, Slope on the DEM |
| 5 | 11 Sep 12:24:33 | 13:51:19 | **1 h 26 m 45 s** | ok | SurfaceParameters on Viking |
| 6 | 11 Sep 20:34:10 | 21:39:12 | **1 h 05 m 01 s** | ok | *"No compatible GPU device has been detected."* (so the laptop, §53.3) |
| 7 | 13 Sep 03:03:23 | 03:15:06 | **11 m 42 s** | ok | **WARNING 000869**, DEM derivative, likely HillShade |
| 8 | **13 Sep 14:30:59** | **14:48:27** | **17 m 28 s** | FAILED | **CompositeBands, cancelled: the fourth attempt** |
| 9 | 24 Sep 15:57:04 | 16:07:05 | 10 m 01 s | FAILED | CompositeBands, cancelled: a fifth attempt (§29) |
| 10 | 24 Sep 16:07:30 | 18:59:55 | 2 h 52 m 25 s | ok | CompositeBands night + day IR: the first global composite to succeed (§29) |
| 11 | 29 Sep 22:08:58 | 30 Sep 01:19:39 | 3 h 10 m 40 s | ok | CompositeBands, 7 bands on the Viking grid (§29.4) |

- **Composite Bands was cancelled four times by 13 Sep, about 2 h 22 m discarded, and a fifth time on
  24 Sep.** Each logs `A raster error has occurred` → `Operation cancelled by user` → `Failed to execute
  (CompositeBands)`: cancelled, not errored. The delivered prospectus says three (§14.5).
- **A trap worth naming.** A session once invented a phantom fourth run by regex-scraping deleted rows out
  of a `.gdbtable` (§9); the retraction then hardened "three" into the record and into `verify_all.py`
  (§17.2). The logs, an independent source, show four. **A retracted claim being wrong for the right
  reason does not make its opposite true: re-derive from the authoritative source.**
- **The lineage dates the drive move:** the Mercury, 8 Sep segmentation, `Slope_Mars_H1`, `Slope_Mars_M1` and
  `SurfaceParameters` runs wrote to the old `C:\…\ArcGIS\Projects\Mars Project\`; `Slope_Mars_V1` and
  `HillSha_Mars1` wrote to the drive. **[V]**
- Only run 6 is attributable to a machine (the laptop). Full-resolution `GRIORA_Average` decimation took
  Viking 355 s, THEMIS 204 s, DEM 96 s **[E]**. Never quote a script's elapsed time as a cost without a
  rate check (§28.9).

---

## 9. Reading the data without opening Pro

**Prefer `arcpy`.** `arcpy.mp.ArcGISProject(<aprx>)` opens in 0.1 s with Pro closed and gives
`listMaps()`, `listLayers()`, `listBrokenDataSources()`, `listLayouts()` and per-layer `dataSource` /
`isBroken`. **[V]**

**The byte-level route is the fallback**, and the only one that sees what was deleted:

- The `.aprx` is a **zip of CIM JSON**.
- GP lineage with parameters and timestamps: `Mars Project.gdb\a00000004.gdbtable`, decoded latin-1, regex
  for `<Process ...>`. Fine for **lineage** (a stale record is still something that ran). **[V]**
- Elapsed times and warnings: `GpMessages\`. Raster statistics: the `.tif.aux.xml` sidecars. Row counts:
  byte offset 4 of each `.gdbtable`.

> **Never scrape `.gdbtable` bytes with a plain regex for inventory.** Free space holds deleted rows, and
> dead datasets read as live: that is how a phantom Composite Bands run was once invented. Walk the
> `.gdbtablx` instead: 16-byte header, then one 5-byte little-endian entry per ObjectID, 0 = deleted. **[E]**

**Windowed reads.** The sources are one scanline per block, so a window still pulls whole rows and
narrowing it horizontally buys nothing; cache to `.npy`. **`ReadAsArray` decimates by nearest neighbour
unless told otherwise**: at 1:71 THEMIS becomes aliased speckle. Pass `resample_alg=gdal.GRIORA_Average`.
Hold a dataset in a name: `gdal.Open(p).GetRasterBand(1)` in one expression frees the dataset and crashes
the next read. **[E]**

---

## 10. Validation

There is **no ground truth and no sub-metre imagery.** Validation rests on:

- the **USGS geologic map** SIM 3292, held since 2026-10-08 (§41): the lava-flow reference (§43.2, §44) and T5's contacts (§47.2);
- the **Robbins crater database**, 385,049 craters ≥ 1 km (§41): the closed-depression detector's recall
  and precision (§42.3, §53.4);
- **TES thermal inertia** (§41): the only calibrated thermal product, at ~3 km (§42.4, §43.1);
- the **IAU gazetteer** in the gdb (§6) and the hosted **CTX mosaic** (§3), network permitting;
- the **held-out half of the hand-drawn labels**, 183 polygons in whole 15° blocks (§31.3).

---

## 11. Open questions

**Open** **[?]**:

| q | question | where it stands |
|---|---|---|
| 12 | Rewrite the sources as internally tiled, compressed copies? | untested; desktop job X7, only if panning stays slow after the pyramids (§2.2, §53.1) |
| 14 | The 8 Sep segmentation's time: the September interim logs "Sep 9, 03:35", the output name encodes 2026-09-08 19:25:34 | unresolved; plausibly UTC against local time (§14.5) |
| 15 | Does the GUI ±60° segmentation of 29 Sep de-speckle? | unmeasured; low priority; never start another ±60° segmentation without asking (§23.6, §29.5) |
| 24 | Which step inside `ClassifyRaster` makes neighbouring processing tiles differ? | the tiles themselves are proven the cause (§53.2); the inner step is not known, and the `.afr` is gone |

**Answered** **[V]** (the question as asked, and its answer):

| q | question | answer |
|---|---|---|
| 1 | final deliverable date | Tuesday 8 December 2026 (§1) |
| 2 | `Jezero_CTX_BlockAdj_dd_Clip` with an empty data source | a hosted tile service, duplicate of `Jezero Crater Clipped` (§5) |
| 3 | does the 8 Sep segmentation belong in the record | yes; it ran on the Mars DEM, not Mercury (§7, §14.5) |
| 4 | delete the duplicate nomenclature classes | yes, the 9 copies, each verified identical first (§50) |
| 5 | clear the broken references | the non-Mars maps left the project (§37); the HiRISE map was deleted (§50); 0 broken (§58.1) |
| 6 | build pyramids on the four sources | built 2026-10-13, 26 min on the desktop (§53.1) |
| 7 | Composite Bands / CRS harmonisation at ±60° | overtaken: the classification uses the 7-band 200 m stack (§31.2); the 100 m Composite Bands is ruled out (`NEXT-STEPS.md` §10) |
| 8 | which machine produced the §8 run times | run 6 was the laptop (no GPU detected, and the 2080 Ti is, q10); the others are unattributed |
| 9 | copy the rasters to internal disk | no, permanently (§2.2) |
| 10 | does `GPU_THEN_CPU` engage on the 2080 Ti | yes (§2.3, §53.3) |
| 11 | the desktop's internal disk | ~32 GB free on `C:`, enough for scratch with per-tile clean-up (§53.0) |
| 13 | acquire THEMIS Night IR | done 2026-09-18; no global night mosaic exists, coverage is ±60° (§15) |
| 16 | digitising: seeded, and how it starts | candidates in separate classes (§25, §26); 512 hand-drawn training labels (§29.2); digitising starts as a review (§46). The classes hold 0 lava margins, 94 channels and 26 crater rims, all accepted Ius candidates (§69.7) |
| 17 | keep the plateau channel candidates | keep; reject in review: the rejections become layout 14's precision (§50) |
| 18 | hydrology at ±60° | yes; the fine pass ran (§53.4); the fill mask is not optional (§28.11) |
| 19 | rebuild the 7-band composite on the night grid with valid slope | done as the corrected stack (§31.2); the GUI `CompositeBand` stays as it is |
| 20 | retarget `make_typearea_supervised.py` | done: it writes `_auto` and refuses to delete what it did not write (§29.8) |
| 21 | `verify_all.py` failing 1 of 38 | fixed; 37 / 37 since two checks were retired (§50.1) |
| 22 | the drive is `F:` on the desktop | every script finds its drive (§40.2); the `.aprx` opens on either letter; the junctions serve one letter at a time (§2.4) |
| 23 | which class schema | the labels' order: 1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground; `Composite Object Classes.ecs` superseded (§29.2, §50). Revised 2026-10-22: seven classes, codes 1–4 kept, 5 volcanic edifice, 6 apron, 7 fluvial channel (D17, §68.1) |
| 25 | fix the 7-band stack before deep learning | yes: train on the corrected stack's training-split export (§31, §50.2) |
| 26 | boxes or pixel labels for deep learning | boxes (PASCAL VOC), as exported; whole-chip boxes on area classes are a limit to report (§50) |
| 27 | how much smoothing to publish | the 200 m map with an 11 × 11 (2.2 km) majority filter (§57); the 400 m 5 × 5 map is superseded (§57.2) |

---

## 12. Working conventions

- **Read the project before writing anything about it.** Deliverables written from assumption were
  rejected, correctly; that is the origin of this file.
- **"Restyle" means a visible redesign**, not consistency fixes: a conservative tidy-up was rejected in
  those terms.
- **The school SharePoint is not synced** to either machine; ask for an export.
- **ArcGIS Pro only**, as the GIS.
- **Objective, impersonal voice** everywhere, the public repo included; `build\neutral_voice.py --check`
  exits 1 on a personal pronoun (§39.4).

### 12.1 File and record conventions

**The failure mode is writing a new section without reconciling the old one** (an audit on 2026-09-18
found four stale claims and six dead script references). So: sections are numbered and sequential; every
claim carries a tag; cross-references use `§N`; **when a new section supersedes an older claim, edit the
older one**. A false claim wearing a `[V]` is worse than none.

**Scripts in `build\`**, verb first:

| Prefix | Purpose |
|---|---|
| `make_*` | produces data, rasters or figures (`make_fig_*` for figures) |
| `build_*` | produces a deliverable (`.pptx` / `.docx`) |
| `audit_*` | inspects the deliverables or the project |
| `verify*`, `check_*`, `test_*` | checks claims against the project files |
| bare noun | a module: `paths.py`, `grid60.py`, `areas.py`, `interim.py`, `le_theme.py`, `layoutkit.py` |

**Counted 2026-10-27 (§69.8):** 166 build scripts on the drive (161 `.py`, 5 `.ps1`); 165 in the public repo, which leaves out
`neutral_voice.py`. The repo's `docs/scripts.md` catalogues them; `tools/check_repo.py` fails if the README's count drifts.

**Every figure has a script that regenerates it.** Type-area products are `ius_*` in `Mars Project\TypeArea\`
and `ath_*` in `Mars Project\Athabasca\`; ±60° products are `global60_*` in `Mars Project\Global60\`. Every
warped raster gets the **named** Esri WKT `Mars_Equidistant_Cylindrical_CM180` (§20.2).

**Windows paths in non-raw Python strings corrupt silently**: `\f`, `\t`, `\v`, `\(`. All four have bitten
this project (two find-and-replace passes matched nothing; one wrote a vertical tab into this file). Use raw
strings or `os.path.join`, even in one-liners.

**`build\audit_record.py` checks this file**: section numbering, every `§N` reference, script names, control
characters, table shape, the counts in §3 and §6 against the disk and the gdb, every type-area figure having a
script, and the memory files. **Run it after every edit.** `build\verify_interim.py` checks that every number
in `interim.py` appears here, so a number the interim quotes must stay in this file.

---

## 13. What scripted sessions can do — verified 2026-09-18

### 13.1 The channel

**Headless `arcpy` is the only channel, and it is enough.** `import arcpy` costs **7.3 s**: pay it once per
script, not per question. **[V]**

### 13.2 Verified capability matrix

| Operation | Cost | Notes |
|---|---|---|
| `arcpy.mp.ArcGISProject(...)` | 0.1 s | opens with Pro closed |
| `listMaps` / `listLayers` / `listBrokenDataSources` | instant | |
| `ListRasters` / `ListFeatureClasses` on the gdb | instant | 28 feature classes and 15 rasters on 2026-10-18 (§6) |
| **`p.saveACopy(tmp)`** | 0.7 s | the safety primitive (§13.3) |
| `p.createLayout(w, h, "INCH")`, `lyt.createMapFrame(geom, map)`, `mf.camera.scale` | instant | |
| **`lyt.exportToPNG(out, resolution=72)`** | 11.7 s | a global extent, real raster render |

### 13.3 The safe-edit pattern

Back up the `.aprx` before any write (the builders do: `Mars Project\.backups\`), and **rehearse on a copy
placed beside the real `.aprx`**, never elsewhere: it stores relative paths, so a copy in another folder
breaks every layer (§31.5). Check that an edit landed before relying on it.

### 13.4 Two figure routes

`matplotlib` figures from `build\make_fig_*.py` (full control, cached `.npy`, no Pro) and `arcpy.mp` layout
exports (the GIS itself: renderers, legends, scale bars, ~12 s a frame). Neither is obsolete; layouts are how
results reach the project (§31) and the decks take both (§39.3).

### 13.5 What this makes possible

Read and report anything (inventories, statistics, lineage, extents, CRS), build figures and layouts, rebuild
the deliverables from `build\`, audit them against the project's numbers, and stage geoprocessing for the
desktop.

### 13.6 Limits

No GUI; anything that exists only as a Pro dialog is out of reach. Global runs wait for the desktop (§2.1):
`arcpy` will start a job the laptop cannot finish. Writes need Pro closed. Raster work and deck work use
different interpreters (§2.4). Deletions need the author's approval (§2.5).

---

## 14. The deliverables — what they claim, and the defects found in them

Read out of the delivered `.docx` files on 2026-09-18 **[V]**. They are history (§1); this section exists so
their claims are not repeated where they are wrong.

### 14.1 The plan, in the prospectus's own words

**Full title:** *"Mars Global Mosaic: Mapping Lava Flows, Fluvial Channels, and Impact Craters in Visible and
Infrared."* **Goal:** a **co-registered** visible + thermal-IR mosaic from the held products, used to map
volcanic flow units, fluvial channels and valley networks, and impact craters into **one internally consistent
landform inventory**. The prospectus has 10 tasks; the September interim re-cut them as **14 tasks with percent
complete**, ~42 % overall. **Task 3, harmonising the coordinate systems, is "the gate"** in the prospectus's
own words: §4's trap as project structure.

### 14.2 Two design decisions that are easy to get wrong

- **The composite excludes elevation on purpose.** Iso Cluster and similar classifiers measure distance in
  raw band values, so a DEM band running −8,528 to +21,226 would swamp 8-bit bands. **Do not add the DEM to
  a classification stack**: the 30 Sep GUI map that did became mostly an elevation map (§30.3).
- **The fix for the failed composite: project first, then run over bounded extents.** It worked: 8.8 s over
  the type area (§18).

### 14.3 The type areas

**Ius Chasma**, western Valles Marineris, ~271–286°E, 6–13°S, with the Louros Valles tributaries on its south
wall: where the mosaic viewer is parked and where the detail work is done. **Athabasca Valles** (150–162°E,
4–14°N) is the second, volcanic one since 2026-10-08 (§42.1). Both windows are in `build\areas.py`. The Jezero
map is context only: hosted Perseverance services, no local imagery.

### 14.4 The scientific hook

**Athabasca Valles was mapped as a fluvial outflow channel for decades before being reinterpreted as flood
lava.** Discriminating volcanic from fluvial channels is a live problem, and morphology + thermal response is
the project's answer. The documents name THEMIS Night IR as the highest-value missing dataset, for
day–night thermal inertia.

> **What the data allow (§24, §28.10, §42.4):** the held THEMIS mosaics are 8-bit, independently stretched
> display products, so **calibrated thermal inertia is not derivable**. What carries the hook is a **relative
> diurnal-contrast index**, valid only within one area. **Write the hook, not the word "inertia".**

### 14.5 Defects in the delivered documents **[V]**

Not to be repaired (§1); listed so they are not repeated:

1. **The Composite Bands count.** Both say three attempts ("the tool logs record all three"); the logs record
   four by 13 Sep (§8). The September interim's own table lists four rows while its prose says three.
2. **Segment Mean Shift attributed to Mercury.** The output is on the Mars DEM grid, in Mars degrees
   (`Segmented_2026090819253…`, 106,694 × 53,347, `GCS_Mars_2000_Sphere`); only Iso Cluster and ML Classify
   were rehearsed on Mercury.
3. **The segmentation's date** disagrees with itself: logged "Sep 9, 03:35", while the output name encodes
   2026-09-08 19:25:34 (§11 q14). **[?]**
4. **Scope.** Both call for a *global* night mosaic and a global analysis stack; neither exists. The analysis
   extent is ±60° (§16.5 has the wording).

All four were found by reading the project rather than the prose, each checkable in seconds against a raster
header or a log.

---

## 15. THEMIS Night IR — sourced and verified 2026-09-18

### 15.1 The file **[V]**

`https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif`,
**14.14 GB**, MD5 `39a50397e05e078258083be88cee0714` (verified: match), ProductId `thm_night_ir_v14`, ASU Mars
Space Flight Facility. Its `.lbl` and `.md5` sit beside it. The same bucket (where `planetarymaps.usgs.gov/mosaic/`
redirects) serves the day and Viking mosaics at byte-identical sizes, so the whole holding's provenance is settled.

### 15.2 Why this file and not the controlled mosaic

| | **`…Night_mosaic_60N60S_100m_v14`** ✅ | `THEMIS_NightIR_ControlledMosaics_100m_v2_oct2018` |
|---|---|---|
| Size | 14.14 GB | 15.32 GB (+ 5.13 GB `.ovr`) |
| Dimensions | 213,388 × 71,130 | 213,389 × 77,058 |
| **Central meridian** | **180, as the day mosaic** | **0, mismatched** |
| Latitude | ±60° | ±65° |
| ULX | −10,669,400.0 | −10,669,445.554 |
| **Aligns with the day grid?** | **yes, exact integer offset** | **no, 0.544 px** |

The controlled mosaic buys 5° of latitude at the price of a reprojection and a resample, on exactly the axis of §4.

### 15.3 The grids are pixel-aligned **[V]**

| | Day v12 | Night v14 |
|---|---|---|
| Size | 213,390 × 106,696 | 213,388 × 71,130 |
| ULX / ULY | −10,669,500.0 / 5,334,800.0 | −10,669,400.0 / 3,556,500.0 |

**X offset exactly 1.00 px, Y offset exactly 17,783.00 px**, both at 100 m, `SimpleCylindrical`, CM 180. The
night raster is an exact integer-pixel sub-window of the day grid: day − night needs no resampling and no
reprojection. **Never reproject this file "to be safe".** A windowed read over Ius re-derives the offsets
from each file's own geotransform every run (`make_fig_daynight.py`): dcol −1.000, drow −17783.000, 100.00 %
valid overlap.

### 15.4 Coverage

**There is no global THEMIS night mosaic.** Night IR stops at **±60°**: about 87 % of Mars by area, the polar
deposits and ice caps out, both type areas well inside. This set the analysis extent (§16).

### 15.5 The first result **[V]**

**Pearson r between day and night over the Ius type area is 0.098: nearly uncorrelated.** Registration is
proven (§15.3), so this is the case for the night mosaic, measured: daytime IR reads as shaded relief (solar
heating and slope orientation), night IR as material (rock stays warm, dust cools). Figure:
`build\pres1_img\ius_day_night_diff.png` (`make_fig_daynight.py`, its third panel labelled "raw DN difference,
not thermal inertia").

**Read it with §24:** the two mosaics are independently stretched 8-bit DN (day p2/p98 = 35/205, night =
58/203; the night label says `Base=0.0, Multiplier=1.0`), so a raw difference subtracts two unrelated scales.
The correlation is unaffected; for a dust-versus-bedrock reading use the index of §24.2, within one area only.

---

## 16. The project's analysis extent is ±60° latitude — decided 2026-09-18

**The decision: the basis for the project, while built from global products, covers only ±60° of
latitude.** This supersedes "global" wherever that word describes the analysis stack. **[V]**

### 16.1 Why it is the right call

The night mosaic forces it (§15.4), and it is the first time all four inputs share one latitude range: a
stack whose bands stop at different latitudes would give every product a ragged edge and a different denominator.

### 16.2 What it costs **[V]**

| Dataset | Full grid | At ±60° | Rows kept |
|---|---|---|---|
| Viking MDIM (232 m) | 92,160 × 46,080 | 92,160 × **30,720** | 66.7 % |
| THEMIS Day IR (100 m) | 213,390 × 106,696 | 213,390 × **71,130** | 66.7 % |
| HRSC/MOLA DEM (200 m) | 106,694 × 53,347 | 106,694 × **35,565** | 66.7 % |
| THEMIS Night IR (100 m) | 213,388 × 71,130 | unchanged | 100 % |

Band-pixels fall from 56.38 bn to 42.64 bn (−24.4 %). **Clipping to ±60° removes a third of the rows but only
13.4 % of the surface: 86.6 % of Mars lies within ±60°**, because simple cylindrical oversamples high latitudes.

### 16.3 The science survives it **[V]**

DEM minimum −8,263 m at Hellas Planitia (32.8°S, 62.1°E) and maximum +21,080 m at Olympus Mons (17.3°N, 227°E),
both inside ±60° (from the cached decimated DEM): relief within ±60° equals global relief, 29,343 m. Lost: the
polar layered deposits, both ice caps and the north polar erg, none of them a target landform family.

### 16.4 Consequences

Every ±60° product is built on the night raster's grid (`grid60.py`, §28.1): imagery at 100 m, DEM products at
200 m (§28.2).

### 16.5 How to say it in the deliverables

Keep the title: the source products and the visible mosaic are global; the **co-registered analysis stack** is
±60°. State it once in scope and again in limitations, with the number:

> built from global products; the co-registered analysis stack spans ±60° latitude, set by THEMIS night-time
> coverage, and covers 86.6% of the surface.

---
## 17. The audit suite — was dead, now works. Run it. 2026-09-18 **[V]**

### 17.1 It had been broken since the move off `C:`

Twelve `build\` scripts pointed at a folder that no longer existed, so the audit and several figure
generators had been silently dead since the move; nothing reported it because nothing ran them. Repathed,
the deliverable filenames remapped (the interim in `NEXT STUFF\`; Presentation 1 is `ocean first pres LE.pptx`,
`ocean` being the course code), and a UTF-8 stdout shim added (the cp1252 console crashed on `→` and `−`).
Since §40.2 every script finds its drive. Run with the ArcGIS Python from `build\`: `verify_all.py`.

### 17.2 `verify_all.py` was enforcing the retracted error

It asserted exactly **three** cancelled Composite Bands runs and flagged "four" as an error: the §8
retraction frozen into the verifier. Counted from the logs: **8 GpMessages files, 4 `Failed to execute
(CompositeBands)`, 2 `WARNING 000869`.** Corrected; it now dates each log (four by 13 Sep, the fourth at
17 min 28 s, the fifth on 24 Sep, §29.8). Since §50.1: **37 / 37**.

> **A check that encodes a belief is not evidence for it.** Re-derive from `GpMessages\` or the raster
> headers, never from what the verifier expects.

### 17.3 What the working suite found

`audit_consistency.py` pulls every sentence carrying a key number across the documents; its first run
confirmed §14.5 defect 1 in all three live documents (the prospectus even says "the tool logs record all
three").

### 17.4 `verify2.py` checks the pre-restyle Presentation 1

It reports 16 failures against the delivered deck by design: that deck no longer exists in the form it
checks. Not defects to fix. The restyled Presentation 1 has 20 slides and 0 speaker notes.

---

## 18. Tasks 3 and 5 are DONE for the type area — 2026-09-18 **[V]**

**The Composite Bands run that failed four times globally completed in 8.8 seconds over the type area**;
the whole harmonise-plus-composite pipeline, ~44 s on the laptop. The prospectus's fix (project first,
bounded extents) was right. `build\make_typearea_stack.py` → `Mars Project\TypeArea\`.

### 18.1 The target grid

**`eqc / lon_0=180 / R=3396190 / 100 m`, snapped to the day mosaic's pixel edges**; 271–286°E, 13–6°S →
**8891 × 4150 px**. Chosen so **the day–night pair is never resampled** (§15.3); only Viking (cubic) and the
DEM (cubic) are. Reprojecting onto CM 0 instead would resample the two finest, natively aligned layers.

| Output | Source | Resample | Time |
|---|---|---|---|
| `ius_viking.tif` (3 band) | Viking 232 m, CM 0 | cubic | 9.7 s |
| `ius_day.tif` / `ius_night.tif` | THEMIS 100 m, CM 180 | **none** | 2.3 / 2.5 s |
| `ius_dem.tif` | HRSC/MOLA, degrees | cubic | 6.4 s |
| `ius_composite_4band.tif` / `_5band.tif` | Viking RGB + day (+ night) | — | 8.8 / 13.8 s |

DEM over the type area: −4,592 m to +5,805 m, relief 10,397 m.

### 18.2 Two composites

The written plan is **4 bands** (Viking RGB + day IR). Night IR is 8-bit like the others, so a **5-band**
composite was built as well; it is the better classification input.

### 18.3 The band statistics **[V]**

**100.00 % of pixels valid in all five bands.** Correlation over the type area:

| | Vik R | Vik G | Vik B | Day IR | Night IR |
|---|---|---|---|---|---|
| **Viking R** | 1.000 | 0.960 | 0.925 | −0.486 | −0.121 |
| **Viking G** | 0.960 | 1.000 | 0.993 | −0.496 | −0.085 |
| **Viking B** | 0.925 | 0.993 | 1.000 | −0.488 | −0.068 |
| **Day IR** | −0.486 | −0.496 | −0.488 | 1.000 | 0.105 |
| **Night IR** | −0.121 | −0.085 | −0.068 | 0.105 | 1.000 |

1. **The three Viking bands are one dimension** (r = 0.925–0.993).
2. **Day IR is anti-correlated with visible (−0.49)**: bright in visible, cool by day, the dust signature.
3. **Night IR is the most independent band** (|r| ≤ 0.12 against everything).

> **Effective dimensionality is about three: visible albedo, day IR, night IR.** The case for the fusion,
> measured. `build\verify_typearea.py` reprints this matrix.

### 18.4 Figure

`build\pres1_img\ius_fusion.png` (`make_fig_fusion.py`): natural colour / HSV fusion / relative diurnal
contrast. Use the HSV form (hue from the false colour at half saturation, value from day IR) for any fusion
figure; per-band percentile stretches of decorrelated bands come out as unreadable neon. Its third panel is
labelled "relative diurnal contrast", not thermal inertia (§40.3).

### 18.5 What this unblocked

Iso Cluster on the composite (§19), terrain from the projected DEM (§20), and the same recipe at ±60° (§28).

---

## 19. Task 7 run on Mars for the first time — and a method correction 2026-09-18 **[V]**

`build\make_typearea_classes.py` on `ius_composite_5band.tif`: **10 classes, minimum size 20, sample
interval 10**; IsoCluster 12.5 s, MLClassify 7.2 s; ten delivered, every one populated (25.25 / 15.21 /
12.39 / 10.21 / 9.34 / 6.31 / 6.29 / 5.95 / 5.64 / 3.41 %).

### 19.1 Legacy Spatial Analyst rejects spaces in paths **[V]**

`ERROR 010328: Syntax error at or near symbol SPACE` on `…\Mars Project\TypeArea\…`; 8.3 short names are
disabled on the volume. **The fix is a directory junction** at the drive root (`mklink /J <drive>\TypeArea
"<drive>\Mars Project\TypeArea"`; likewise `Global60`, `Athabasca`): the same folder, not a copy. Scripts
may use the junctions for geoprocessing; **layers in the project must not** (§34.1). A junction serves one
drive letter at a time (§2.4).

### 19.2 The Iso Cluster → ML Classify two-step is a no-op as run **[V]**

The two outputs are the same raster: 0 differing pixels in a 1,023,371-px sample, GDAL checksum 62066 = 62066.
`IsoClusterUnsupervisedClassification` already runs IsoCluster then MLClassify internally. **What makes a
supervised step real is training polygons** (§27, §31).

### 19.3 The classification is geologically coherent

`build\pres1_img\ius_classification.png`: classes 1–3 (24.0 % together) track the canyon walls, wall-rock
spurs and the Louros Valles tributary fans, rock and coarse debris that stays warm at night; classes 4–6
(50.7 %) blanket the dust-mantled plateau; 7, 8 and 10 pick out crater ejecta and intermediate texture. The
dust-versus-bedrock split falls out without training data. It is per pixel and speckled (§23).

### 19.4 The three landform feature classes

`build\make_landform_fcs.py`: `Landform_LavaFlowMargins` (polyline, 10 fields), `Landform_ChannelCenterlines`
(polyline, 11), `Landform_CraterRims` (polygon, 11), in **`Mars_Equidistant_Cylindrical_CM180`**. Common
schema: `UnitName`, `Confidence` (certain / probable / inferred), `Evidence`, `Notes`, `MappedBy`, `MappedOn`;
channels carry **`Origin` (fluvial / volcanic / indeterminate)**, the Athabasca question as an attribute;
craters carry `DiameterKm` and `Preservation`. Review fields were added in §46. Since 2026-10-26 they hold 0, 94 and 26 rows, accepted Ius candidates (§69.7).

---

## 20. Task 4 done for the type area — the z-factor defect is FIXED 2026-09-18 **[V]**

`build\make_typearea_terrain.py` on `ius_dem.tif`, a projected metric grid:

| Output | Time | min | max | mean | WARNING 000869 |
|---|---|---|---|---|---|
| `ius_slope_deg.tif` | 21.9 s | 0.000 | **71.792°** | 6.539° | **no** |
| `ius_slope_pct.tif` | 21.7 s | 0.000 | 304.001 % | 12.028 % | **no** |
| `ius_aspect.tif` | 19.4 s | −1.000 | 359.931 | 159.387 | **no** |
| `ius_hillshade.tif` | 7.0 s | 0.000 | 254.000 | 175.482 | **no** |

**The first terrain derivatives in the project with a valid z-factor**; the warning was the degree grid,
as §4 diagnosed.

### 20.1 The numbers cross-check

71.792° = atan(3.04001): the two independent runs agree to three decimals. Mean slope 6.54° (gentle plateau,
steep walls). These may be quoted in degrees; the global `Slope_*` layers may not (§7). `ius_dem.tif` had to
be cubic-resampled to 100 m, so for quantitative terrain claims prefer the ±60° products (§28.2).

### 20.2 Name the CRS

`gdal.Warp` wrote a PROJ WKT that ArcGIS reads as `"unknown"`. `make_typearea_stack.py` relabels every
output with the **named Esri WKT `Mars_Equidistant_Cylindrical_CM180`** right after the warp: a label only,
no pixel touched. GDAL and ArcGIS agree on the maths and disagree on the name, and ArcGIS keys on the name.

---

## 21. Audit round 2 — 2026-09-18 **[V]**

### 21.1 Two open questions closed

q2 (§5) and, in part, q8 (§8); both now answered in §11.

### 21.2 A layer added by script inherits defaults, not its neighbour's symbology

`addDataFromPath` gave the night mosaic `PercentMinimumMaximum 0.5/0.5` beside the day mosaic's
`StandardDeviations n=5`, so flipping between them would compare stretches as much as data.
`build\fix_night_stretch.py` matched them in both working maps. **Check the stretch whenever a raster
joins a comparison group.**

### 21.3 Defect 1 fixed at the source

`content.py` (the September documents' source) carried "three attempts" in three places; corrected to four,
~2 h 22 m. Rebuilding the interim report also showed the shipped document was already stale against its own
source: built documents are not automatically in step with what feeds them.

### 21.4 The interim deck was never blocked

The September deck was built by `build_interim_le.py`, which needs no template (§39.2). The template-filling
`build_interim_deck.py` needs `2 Interim Presentation Template.pptx`, in `NEXT STUFF\` since 2026-10-08. Both
are superseded by the living build (§39.3).

---

## 22. Task 13 started — the project has layouts now 2026-09-18 **[V]**

`build\make_typearea_layouts.py`: layouts `01_visible`, `02_night_ir`, `03_classification` (11 × 8.5 in,
150 dpi, ~1.3 s each), each with title, subtitle, metric scale bar, north arrow and a credit block (projection,
sphere radius, cell size, extent). Since §31.1 each has its own map.

### 22.1 Four `arcpy.mp` traps

- **No `createTextElement` in Pro 3.x.** Text goes through the CIM: a `CIMTextGraphic` (shape = an
  `arcpy.Point`; `CIMPointGeometry` is not creatable) in a `CIMGraphicElement`, appended to
  `layout.getDefinition("V3").elements`, then `setDefinition`.
- **`createMapSurroundElement` wants a StyleItem object**, from `p.listStyleItems("ArcGIS 2D", "NORTH_ARROW")`,
  not its name.
- **Match the frame to the data's aspect** (8891 × 4150 = 2.14 : 1) or get white bands.
- **`el.isOverflowing` reports legend overflow truthfully**; a 10-class legend needs `columnCount = 4`. It
  does not catch the defects found by reading a sheet (§33).

### 22.2 Default symbology can be wrong

Iso Cluster's default colours gave classes 2 and 10 the same red. `recolour_classes()` applies a qualitative
set, cool for wall rock and debris, warm for plateau dust.

### 22.3 No graticule through the CIM

`CIMGraticule` built through the CIM renders nothing, and `CIMGraticuleLine` / `CIMSimpleMapGridEdge` raise
`LookupError`. Graticules are drawn as data instead (§44).

### 22.4 What this changed

Results reach the project as layouts; figure routes in §13.4.

---

## 23. Object-based classification — two method corrections 2026-09-19 **[V]**

### 23.1 Measure the speckle

`build\verify_segmentation.py` over one 3200 × 2200 px window across wall and plateau: **boundary pixels**
(share with a 4-neighbour of another class) and **mean run length** (horizontal distance to a class change).

### 23.2 The legacy tool classifies per pixel even when fed segments

`IsoClusterUnsupervisedClassification` on a `SegmentMeanShift` output cut speckle only 11.1 %. The Image
Analyst chain `SegmentMeanShift → TrainIsoClusterClassifier → ClassifyRaster` respects the segments.

### 23.3 The Mercury segmentation parameters are the worst case for de-speckling

**In `SegmentMeanShift`, `spectral_detail` and `spatial_detail` run 1–20 and higher means more detail.** The
inherited 20 / 20 / 5 px is the **maximum-detail** setting, the smallest segments the tool makes: the reason
the 8 Sep run made 65,474 segments. Never treat 20 / 20 / 5 as the project's settings.

### 23.4 Three traps

`TrainIsoClusterClassifier` returns the `.ecd` path, not a Raster. `ClassifyRaster(...).save(out)` holds a
lock: `del` the Raster before reading the output. And `gdal.Open(p).GetRasterBand(1)` in one expression
frees the dataset (§9).

### 23.5 The parameter sweep **[V]**

| method | params | cost | boundary px | mean run | vs per-pixel |
|---|---|---|---|---|---|
| per-pixel | — | — | 43.13 % | 5.0 px | baseline |
| legacy classifier on segments | 20/20/5 | — | 38.35 % | 6.3 px | −11.1 % |
| object-based | **20/20/5** | 103 + 52 s | 35.22 % | 6.9 px | −18.3 % |
| object-based | **14/14/30** | 712 + 93 s | **12.99 %** | 18.6 px | **−69.9 %** |
| object-based | **9/9/80** | 817 + 87 s | **6.36 %** | 37.3 px | **−85.3 %** |

**The parameters matter far more than the classifier.** **Recommended: 14 / 14 / minimum 30 px**, by the
project's resolution rule: **~10 pixels across a feature are needed to map its margin, so at 100 m the limit
is ~1 km** (§14). 14/14/30's mean run, 18.6 px ≈ 1.9 km, sits just above it; 9/9/80's 3.7 km is below the
stated resolving power and flattens the plateau into one unit (`build\pres1_img\ius_segmentation_sweep.png`; the repo's light copy in `interim_img\`, §65).
Lower detail is slower, not cheaper: 9/9/80 took 8× longer than 20/20/5.

### 23.6 Segmentation does not scale to ±60° **[V]**

The type area is 36.9 M px; the ±60° stack **15.18 bn px, 411×**. At 14/14/30: **92 h (3.8 days)** on the
laptop's rate, ~37 h even at an assumed 2.5× on the desktop. **Object-based classification is a type-area
technique in this project**; say so rather than imply a global segmented map. Never start a ±60°
segmentation without asking (`NEXT-STEPS.md` §10). One was run in the GUI anyway (§29.5).

---

## 24. The day–night pair, worked properly — 2026-09-19 **[V]**

`build\make_typearea_thermal.py` and `make_fig_thermal.py` → `build\pres1_img\ius_thermal_contrast.png` (`--light`: `interim_img\`, §65).

### 24.1 Calibrated thermal inertia is NOT derivable from the held products **[V]**

The night mosaic's ISIS label: `Type = UnsignedByte`, `Base = 0.0`, `Multiplier = 1.0`: no scaling to radiance
or Kelvin. The day mosaic is the same. Both are 8-bit display products, **independently stretched by ASU**:

| | mean | sd | p2 | p98 |
|---|---|---|---|---|
| day DN | 125.56 | 34.86 | **35** | 205 |
| night DN | 124.26 | 33.97 | **58** | 203 |

So raw `day − night` is not a temperature difference and not thermal inertia; it is kept as
`ius_dn_diff.tif` (mean 1.30, sd 46.06), labelled for what it is.

### 24.2 What IS derivable: a relative diurnal-contrast index **[V]**

Scale each band by its own 2–98 percentile to [0, 1] first, then difference: dimensionless, [−1, 1], relative
to the area it was stretched over. `ius_thermal_contrast.tif`: mean **+0.0757**, sd **0.2790**, p2 / p50 / p98
= −0.62 / +0.11 / +0.57. **High** = large diurnal swing, dust-like; **low** = damped, rock and coarse debris.

### 24.3 It is independent of topography **[V]**

| against | r |
|---|---|
| day IR / night IR | +0.605 / −0.719 (arithmetic: the index is built from them) |
| Viking red | −0.237 |
| **elevation** | **+0.108** |
| **slope** | **−0.248** |

Per object-based class (`ius_obj_medium`, 14/14/30):

| class | % area | contrast | slope° | elev m | read as |
|---|---|---|---|---|---|
| 3 | 2.6 | **−0.467** | 13.3 | +2785 | wall outcrop, rocky |
| 5 | 3.8 | **−0.443** | 9.2 | +1105 | lower wall / floor bedrock |
| 2 | 5.2 | −0.268 | **21.5** | +1983 | the steep wall itself |
| 6 | 16.9 | −0.030 | 3.1 | +2987 | mixed plateau |
| 7 | 11.6 | +0.096 | 5.1 | +3291 | plateau |
| 1 | 3.7 | +0.134 | 11.3 | +951 | |
| 8 | 9.4 | +0.197 | **17.0** | **+43** | chasma floor, mantled |
| 9 | 43.4 | +0.202 | 2.1 | +3381 | dust-mantled plateau |
| 4 | 3.4 | **+0.261** | 5.3 | +3883 | highest, dustiest |

**Classes 2 and 8 are the two steepest units, 4.4° apart in mean slope, and 0.46 apart in the index at
opposite signs**: same steepness, opposite response. Fresh crater ejecta rings come out damped against the
plateau. **[V]**

> **Limit (§42.4):** against calibrated TES inertia at the ~3 km TES resolves, the index does not track
> inertia here (r −0.08 dayside, −0.22 nightside) or at Athabasca (≈ 0). It is independent of topography;
> that it separates *materials* is untestable below 3 km, where nothing calibrated exists. At ±60° it is a
> local contrast field only (§28.10).

### 24.4 Why it matters to the Athabasca hook

It is a second axis beside morphology, an evidence value for the channels' `Origin` field (§19.4). Tested as
H2 in §51.1: it separates nothing at stage 1.

### 24.5 A figure's overclaim fixed

`make_fig_daynight.py` had titled the raw difference "thermal-inertia proxy"; relabelled "raw DN difference,
not thermal inertia".

### 24.6 Two stale lines in `content.py`

Its risk register still says thermal inertia is blocked on a missing dataset; `content.py` only feeds the
delivered September documents, so it is flagged, not edited. **[?]**

---

## 25. Candidate channel centrelines — task 11 seeded, with one large trap 2026-09-19 **[V]**

`build\make_channel_candidates.py`: centrelines from DEM flow routing, each with the diurnal-contrast index,
into the separate class **`Landform_ChannelCandidates_auto`** (`Confidence='inferred'`,
`Origin='indeterminate'`); the digitising class is never written by it.

### 25.1 The trap: `Fill` floods Ius Chasma, and half the network was artefact **[V]**

Ius Chasma is a **closed basin**, and `Fill` floods it into a flat synthetic lake that `FlowAccumulation`
then routes across. On `fill − dem`:

| | |
|---|---|
| scene raised at all (> 1 m) | **21.7 %** (21.746 %; read "21.8 %" to §65), 80,238 km² |
| raised > 100 m | 9.1 % |
| **maximum raise** | **2,077 m** |
| **stream cells on filled ground** | **56.1 %** |

> **Over half of the first network was routing across a surface that does not exist**, and it looked
> plausible: long, smooth, dendritic trunk lines down the chasma.

**The fix is a mask:** keep only cells with `fill − dem ≤ 1 m`. The script prints the discard every run and
stores `FillDepthM` per segment (mean 0.073 m, max 0.889 m over the kept set). **It generalises** to every
closed basin and crater interior (§28.6). Figure: `build\pres1_img\ius_channel_candidates.png` (`--light`: `interim_img\`, §65).

### 25.2 What came out **[V]**

2,610 candidates, **15,428 km**, median 4.2 km, longest 58.2 km; threshold 5,000 upslope cells (50 km²),
segments < 2 km dropped.

| mean slope | n | km | mean thermal index |
|---|---|---|---|
| **< 2° (plateau)** | **1,661** | 10,072 | +0.122 |
| 2–5° | 253 | 1,180 | +0.128 |
| 5–10° | 308 | 1,725 | +0.026 |
| **> 10° (wall)** | **388** | 2,451 | −0.033 |

**64 % sit on plateau under 2°**, where routing finds paths in the noise of a 200 m DEM resampled to 100 m:
prompts, not results. **The subset worth review: 188 candidates, 1,037 km, slope ≥ 5° and index < −0.15**,
steep and rock-floored. Removing the fill artefacts doubled the rock-floored share, 7.0 % → 11.0 %.

### 25.3 Schema and cost

Fields `UnitName`, `Origin`, `Confidence`, `Evidence`, `StrahlerOrd`, `LengthKm`, `ThermIdx`, `ThermSd`,
`SlopeDeg`, `FillDepthM`, `Notes`, `MappedBy`, `MappedOn`: a superset of the digitising schema. 4.5 min cold,
2.2 min warm (routing rasters cached as `ius_fill/fdr/fac.tif`). Strahler order tops out at 3 because the
network ends at the chasma rim; the order is a parameter of the threshold (§47.4).

### 25.4 Not a landform map

`Confidence='inferred'` on every row is the guard; candidates enter `Landform_ChannelCenterlines` only through
a review accept (§46).

---

## 26. Task 12 from zero — a crater inventory, and an honest detection limit 2026-09-19 **[V]**

> **Read with §42.3:** against the Robbins database, at D ≥ 1 km only **11 %** of the 1,685 candidates are
> catalogued craters (they find 21 % of the catalogued ones). The layer is **closed depressions ≥ 1 km**,
> never a crater count; for craters use `Ref_Craters_Robbins2020`.

`Fill` floods every closed depression, which is what a fresh crater is topographically, so `ius_filldepth.tif`
was already a detector input. `build\make_crater_candidates.py`, 49 s.

### 26.1 The gazetteer is empty over the type area

**Zero named craters in 271–286°E, 6–13°S**; the nearest, Oudemans (124.2 km, 268.23°E 9.84°S) and Perrotin
(82.8 km, 282.06°E 2.82°S), are just outside.

### 26.2 What came out **[V]**

10,164 closed depressions deeper than 20 m; **1,685 survive**:

| filter | value | why | dropped |
|---|---|---|---|
| min depth | 20 m | noise below this in a 200 m blend | — |
| min diameter | 1.0 km | the resolving limit (§23.5) | 7,551 |
| max aspect | 2.0 | craters are round; the chasma is not | 529 |
| min fill ratio | 0.55 | area / bbox (a circle gives π/4 = 0.785) | 1,116 |

Diameters median **1.46** km, max 31.4 km (1–2 km: 1,233 · 2–5: 364 · 5–10: 61 · 10–20: 22 · 20–50: 5); median
depth / diameter **0.0453**, low because the detector measures depth below the lowest rim pass. Candidates
average index +0.124 against the scene's +0.0757: interiors mantled relative to their surroundings.

### 26.3 Validated on two named craters: one hit, one instructive failure **[V]**

`build\verify_crater_detection.py`, the identical detector on windows around both:

| | IAU | detected | centre error | verdict |
|---|---|---|---|---|
| **Perrotin** | 82.8 km | **77.0 km** | 1.95 km | **hit, −7.1 %**, rank 1 of 1,321 |
| **Oudemans** | 124.2 km | — | — | **miss** |

**Oudemans is breached into the canyon system**: its lowest rim point sits 33 m below its floor, so `Fill` has
nothing to fill. **The method finds closed depressions; a breached crater is invisible to it**, and in a canyon
type area breached craters are the population of most interest. They must be digitised by hand.

### 26.4 The filters were tuned on the evidence

| aspect ≤ | fill ≥ | Perrotin error / rank | Oudemans |
|---|---|---|---|
| 2.5 | 0.45 | −7.1 %, rank 2 / 1,779 | miss |
| **2.0** | **0.55** | **−7.1 %, rank 1 / 1,321** | miss |
| 1.5 | 0.65 | −7.1 %, rank 1 / 693 | miss |

2.0 / 0.55 is the loosest setting at which the true crater ranks first; it also drops a 140.9 km "crater"
that is a fragment of the chasma.

### 26.5 Where it lives

`Landform_CraterCandidates_auto` (polygon, 1,685): `DiameterKm`, `DepthMaxM`, `DepthMeanM`, `Aspect`,
`FillRatio`, `ThermIdx`, `CenterLon`, `CenterLat`, `IAUName`, `Preservation` and the common schema; separate
from `Landform_CraterRims`. Figure `build\pres1_img\ius_crater_candidates.png` shows both validation windows,
the miss included.

---

## 27. Task 7 supervised — the project's first accuracy assessment 2026-09-19 **[V]**

> **Since 2026-10-01 the 1,604 terrain polygons of this section are no longer in the gdb**:
> `Landform_TrainingSamples_terrain` holds the 512 hand-drawn labels (§29.3). The script now writes
> `Landform_TrainingSamples_terrain_auto` and refuses to delete what it did not write (§29.8). The scores
> below stand as measured.

`build\make_typearea_supervised.py`, ~17 min for three runs.

### 27.1 Two design choices

**Labels from terrain alone** (slope, elevation, §26's crater mask), so no spectral band touches a label. **Train
and test in spatial blocks** (a 10 × 6 checkerboard), never random pixels, which would put a test pixel next
to its own training pixel; class cores eroded 2 px. 1,604 training polygons; 13,901,945 held-out pixels.

### 27.2 The result **[V]**

| stack | overall accuracy | kappa | |
|---|---|---|---|
| **the 5-band composite** | **62.7 %** | **0.406** | the clean number |
| + diurnal-contrast index | 63.1 % | 0.409 | +0.4 pt |
| + index **and** slope | 82.6 % | 0.682 | **circular**, never quote |

Against a 16.7 % baseline for six classes, 62.7 % / κ 0.41 is a real result.

### 27.3 The thermal index adds +0.4 points

Consistent with §24.3: an index nearly orthogonal to terrain cannot help predict terrain classes. **Terrain
labels cannot price the thermal index by construction**; that needs material labels, which only
photo-interpretation can give. The same conclusion held with the hand-drawn labels at ±60° (§40.1, §56).

### 27.4 Per class

| class | producer | user | n test |
|---|---|---|---|
| wall_steep | **74.2 %** | 74.2 % | 1,601,902 |
| chasma_floor | **72.3 %** | 39.2 % | 2,021,560 |
| plateau | 62.8 % | **92.2 %** | 9,462,727 |
| crater_interior | 16.1 % | 8.2 % | 567,459 |
| plateau_flank | 19.7 % | 3.5 % | 169,192 |
| wall_moderate | 2.4 % | 3.4 % | 79,105 |

**Craters are a topographic class, not a spectral one**: never present the crater candidates as spectrally
derived. The two thin transitional classes are too narrow to learn.

### 27.5 Two silent traps behind a 2.1 % first result

Below-random accuracy with an unpredicted majority class is a bug signature:

- **`ClassifyRaster` writes VALUE 0…n−1, not the class codes**; the class is in the VAT's `Classvalue`. Map
  VALUE → Classvalue from the VAT (since §36 every map is recoded to the codes).
- **`BuildVRT(..., separate=True)` keeps a different NoData per source**; a mixed stack (0, −9999, −3.4e38)
  collapsed to one class on 98.6 % of pixels. Build mixed stacks with one sentinel no band can take.

Figure: `build\pres1_img\ius_supervised.png`.

---

## 28. The products move to the analysis extent — `Global60` 2026-09-19 **[V]**

**Instruction:** the data produced must be for the global mosaic, not only a type area, in the same content
area as the downloaded mosaics. The type area is where a method is proven, not where it is left; a
type-area result is a prototype until it runs at ±60°. **Read §28.10 before using anything here for thermal
discrimination.**

### 28.1 One grid, read from the night mosaic **[V]**

**`build\grid60.py`** reads the grid off the night mosaic every time, so a product built through it is
co-registered by construction:

| | **G100** | **G200** |
|---|---|---|
| size | 213,388 × 71,130 | 106,694 × 35,565 |
| cell | 100 m | 200 m |
| pixels | **15.178 bn** | 3.795 bn |
| origin | −10,669,400 , +3,556,500 | identical |
| footprint | ±60.0003° lat, 359.9985° lon | identical |
| CRS | `Mars_Equidistant_Cylindrical_CM180`, R = 3,396,190 m | identical |
| vs type area | **411×** | 103× |

G200 is an exact 2 × 2 aggregation of G100. Outputs go to **`Mars Project\Global60\`** (junction
`<drive>\Global60`); its `README.md` states the grid, the 400 m and 0.5° lattices (§58.1) and the caveats.

### 28.2 Two measurements that made it tractable **[V]**

- **The THEMIS pair is a window read**: the day mosaic sits exactly +1 px, +17,783 px from the night grid.
- **The DEM is already on G200, to 10 microns**: 0.0033741208° is **199.999990 m** on this sphere, drifting
  0.005 px across the width. A nearest-neighbour warp to G200 reproduces **262,144 / 262,144** source pixels
  exactly; cubic alters 36 % by up to 28 m. So the ±60° terrain is computed on the real elevations, and
  `ius_dem.tif` (cubic to 100 m) is not.

**The rule: imagery products at 100 m, DEM products at 200 m.** Terrain at 100 m costs 4× and invents detail.

### 28.3 The diurnal-contrast index at ±60° **[V]**

`build\make_global_thermal.py`, 36.3 min: **`global60_thermal_contrast.tif`**, Int16 × 10000, nodata −32768,
25.57 GB. A byte lookup: both inputs are uint8, so two 256-entry tables compute it exactly, one 512-row strip
in memory.

| | ±60° (G100) | Ius type area (§24.2) |
|---|---|---|
| co-valid pixels | **14,776,942,885 / 15,178,288,440 = 97.36 %** | 100.00 % |
| mean | +0.0597 | +0.0757 |
| sd | 0.2905 | — |
| p2 / p50 / p98 | −0.613 / +0.075 / +0.626 | — |

**The two are not comparable**: one is stretched over ±60°, the other over Ius. No latitude gradient (band
means against |latitude| r = −0.237; spread of band means 0.1455 against a within-band sd of 0.286), but that
rules out one artefact and is no evidence of signal: §28.10 tested the signal, and it fails.

### 28.4 What was built where

| script | product | grid | state |
|---|---|---|---|
| `make_global_thermal.py` | diurnal-contrast index | G100 | done, 36.3 min |
| `make_global_terrain.py` | DEM, slope°, aspect, hillshade | G200 | done, ~27 min (§28.8); 180° patched (§54) |
| `make_global_landforms.py` | crater + channel candidates | G200 | basins 2026-09-19 (§28.11); fine pass 2026-10-14 (§53.4, §54.4) |
| `make_global_stack.py` | harmonised bands + Composite Bands at 100 m | G100 | smoke-tested only; ruled out (`NEXT-STEPS.md` §10), overtaken by the §31.2 stack |
| `verify_global60.py` | co-registration gate | — | seconds; covers every `global60_*.tif` since §58.1 |

**`verify_global60.py` makes "same content area" checkable**: every product's corners to the millimetre, cell
size, shape, CRS name and central meridian, nesting on G100. Run it after every ±60° job.

### 28.5 No segmentation at ±60°

`make_global_landforms.py` holds no segmentation step: flow routing and fill depth tile, segmentation does not (§23.6).

### 28.6 Two limits that grow with the extent

- **`Fill` floods closed basins**: at ±60° that is Valles Marineris, Hellas, Argyre, Isidis and every crater
  interior. The fill mask is applied and its discard printed per tile.
- **Breached craters stay invisible** (§26.3): the output is closed depressions ≥ 1 km, never a crater inventory.

`make_global_landforms.py` runs **two scales**: the whole extent decimated 8× to 1600 m and filled in one
piece (basins ≥ 20 km, no seams), and 8192 px tiles with a **1024 px (205 km) halo**, keeping only candidates
whose centroid falls in a tile core. It checkpoints per tile and skips finished ones on a rerun.

### 28.7 Test the call on a window first

Three call sites passed `resampleAlg` twice (`TypeError` at the first warp). A 512 × 512 test window found
them before any run. **On jobs measured in hours, test the call on a window first.**

### 28.8 Terrain at ±60° **[V]**

`build\make_global_terrain.py`, G200 (`gdaldem`, so no WARNING 000869):

| product | type | size | min | max | mean | sd |
|---|---|---|---|---|---|---|
| `global60_dem.tif` | Int16 | 3.21 GB | — | — | — | — |
| `global60_slope_deg.tif` | Float32 | 7.04 GB | 0.000° | **52.698°** | **2.186°** | 3.457 |
| `global60_aspect.tif` | Float32 | 8.03 GB | 0.000° | 359.944° | 177.157° | 106.896 |
| `global60_hillshade.tif` | Byte | 1.30 GB | 1 | 255 | 180.055 | 9.099 |

Slope is in degrees on a metric grid and may be quoted. Mean 2.19° against 6.54° at Ius (a canyon); maximum
52.7° at 200 m against 71.8° at 100 m: slope depends on support, so never compare the maxima. Statistics after
the §54 patch: §55.1.

### 28.9 A timing trap: scripts report wall clock, and the laptop sleeps **[V]**

`make_global_terrain.py` printed `done in 9:15:10`; a timed full-width slice put the real cost at ~27 min (DEM
warp ~5.5 min, the CM 0 → CM 180 roll 1.8× a same-CRS warp). **The other 8.7 hours were the laptop asleep.**
Never quote a script's elapsed figure as a cost without a rate check. A first reading blamed the
scanline-blocked source; the slice test disproved it within the hour. **Disable sleep before a multi-hour run
on the laptop**; `SetThreadExecutionState` keeps an idle machine awake but cannot stop a lid close or Modern
Standby on battery (§31.2, §35.3).

### 28.10 The THEMIS mosaics are LOCALLY NORMALISED — the thermal index does not scale **[V]**

**The finding that constrains the project's central claim.** Seven provinces whose thermal-inertia contrast is
textbook:

| province | index mean | sd |
|---|---|---|
| Arabia Terra — bright, **dusty**, low TI | +0.0597 | 0.193 |
| Amazonis — **dustiest** on the planet | +0.0574 | 0.131 |
| Tharsis dust | +0.0578 | 0.146 |
| Syrtis Major — dark, **rocky**, high TI | +0.0633 | 0.204 |
| Acidalia — dark, rocky | +0.0607 | 0.231 |
| Hellas floor | +0.0539 | 0.228 |
| Valles Marineris — bedrock walls | +0.0590 | 0.234 |

**Dusty against rocky: −0.0009**, against within-province scatter of 0.13–0.23. The cause is in the sources,
with Viking as the control:

| | day IR | night IR | **Viking red** |
|---|---|---|---|
| dusty provinces | 125.61 | 124.50 | 123.50 |
| rocky provinces | 125.80 | 124.49 | 75.82 |
| **difference** | **−0.19** | **+0.02** | **+47.67** |

| | day DN | night DN | Viking R |
|---|---|---|---|
| Arabia Terra | 125.6 ± 34.1 | 124.4 ± 30.9 | 122.1 ± 20.3 |
| Amazonis | 125.5 ± 31.1 | 124.5 ± 29.2 | 124.9 ± 14.0 |
| Syrtis Major | 125.6 ± 32.6 | 124.2 ± 32.6 | **67.3** ± 23.3 |
| Acidalia | 126.0 ± 34.1 | 124.7 ± 32.8 | **84.3** ± 25.9 |
| *whole mosaic (§3)* | *125.75 ± 34.36* | — | *122.84 ± 31.58* |

**Every province reproduces the mosaic-wide mean and spread in both THEMIS products: both are locally
contrast-normalised, their DN is local contrast, not radiance.** Viking keeps its real albedo differences
(47.67 DN). The spatial unit of the normalisation is not measured **[?]**.

- **§24.3 stands within one area**, where the stretch is roughly constant.
- **The index must not be compared across the planet** or between the type area and ±60°.
  `global60_thermal_contrast.tif` is local texture for per-object attribution, **never a material map**.
- **For regional material discrimination lead with Viking albedo**; thermally, only calibrated products (TES,
  §41) can do it. Calibrated inertia then tracks Viking, not the THEMIS pair (§43.1).
- **Absence of a suspected artefact is not evidence of signal.**

**Which provinces each number covers (§62):** the index difference (−0.0009) is three dusty (Arabia Terra,
Amazonis, Tharsis) against four rocky (Syrtis Major, Acidalia, Hellas floor, Valles Marineris); the DN rows
(47.67 DN for Viking) equal, within the per-province table's rounding, the means of its two dusty and two rocky
provinces (Arabia Terra and Amazonis; Syrtis Major and Acidalia). The box coordinates of 2026-09-19 are not
recorded **[?]**. `pres1_img\global60_thermal.png` charts these tables since 2026-10-19 (§62); its earlier
version quoted 54.4 DN from five boxes of its own (`logs\global_fig2.log`).

### 28.11 The staged scripts smoke-tested; the basin pass done **[V]**

Both carry `--smoke` (a small window over Ius, separately named outputs):
`make_global_landforms.py --smoke --skip-coarse --max-tiles 1`, `make_global_stack.py --smoke`. The stack smoke
(20 s) lands every output on the grid, and band 4 of its composite is bit-identical to the standalone day raster.
The landform smoke: fill-artefact discard **46.2 %** of stream cells (Ius 56.1 %); crater density 4.85 × 10⁻³
/ km² against 4.56 × 10⁻³ at Ius at 100 m.

**The coarse basin pass:** 48 s for the whole extent at 1600 m, **217,622 closed depressions, 5,144 ≥ 20 km**,
in `Landform_BasinCandidates_auto_60`. It recovers Hellas (2,697 km at 71.9°E −41.0°, **7,857 m deep**), Utopia
(2,093 km at 113.5°E +44.5°) and Isidis (1,026 km at 87.6°E +12.5°).

**Against all 117 named IAU craters ≥ 100 km inside ±58°:**

| | | |
|---|---|---|
| a closed depression near the centre | 88 / 117 | 75 % (positional) |
| …**and** diameter within ±50 % | 79 / 117 | **68 %** (usable) |
| diameter error on those | median **+2.2 %** | p10 −12.6 %, p90 +20.8 % |

**Quote 68 %, not 75 %**: a degraded crater's closed part can be a small pocket in the right place. **Match to
the largest candidate near the centre, not the nearest** (Greeley, 457 km, otherwise "matches" a 24.6 km pocket).
Median +2.2 % here and −7.1 % on Perrotin (§26.3) agree: good to ~10 % in diameter when the crater is seen at
all; the third it misses is the breached population, not a random sample. Every Robbins crater ≥ 100 km is a
different measurement (39 % recall, §53.4).

---

## 29. Manual work in the Pro GUI — 2026-09-24 to 10-01, read 2026-10-01 **[V]**

Not scripted; read from `GpMessages\`, the gdb lineage and `arcpy`, nothing changed.

### 29.1 What was run **[V]**

| End (local) | Tool | Output |
|---|---|---|
| 24 Sep 16:07 | Composite Bands, cancelled after 10 m 01 s (the fifth) | none |
| 24 Sep 18:59 | Composite Bands, Night + Day IR, 2 h 52 m 25 s | `Mars_MO_THEMIS_CompositeBand`, 2 bands, exactly the night grid |
| 29 Sep 00:09 | Training samples saved | `TrainingSamples_202609290009589587982`, 455 polygons |
| 29 Sep 19:22 | `SegmentMeanShift` 15.5 / 15 / min 20 px on a raster-function input (`.afr`, since gone) | `Segmented_202609290011302066080`, night grid |
| 29 Sep 21:53 | `ClassifyRaster`, SVM, over the segments + Night IR | `Classified_202609292109007048151`, 4 classes |
| 30 Sep 01:19 | Composite Bands, 7 bands, 3 h 10 m 40 s | `CompositeBand`, 92,160 × 46,080, 231.54 m, CM 0 |
| 30 Sep 04:28 | `ClassifyRaster`, SVM, on `CompositeBand` | `Classified_202609300147338582853`, 4 classes |
| 30 Sep 08:03 | Training samples exported | `<drive>\new training.shp`, 511 polygons |
| 1 Oct 19:56 | Export Training Data For Deep Learning, from `CompositeBand` | `Mars Project\LabeledObjects\CompositeBand\202610011907318762216\` |

The segmentation ran about **19 h 11 m** (00:11:30 to 19:22:17, from the name stamp and the lineage) **[E]**. The
29–30 Sep runs carry `C:\Users\Owner\…` and `F:\…`: the desktop. The 24 Sep composite wrote to `Z:`, probably
the laptop **[?]**.

### 29.2 The labels: four classes, hand-drawn, planet-wide **[V]**

| Set | Crater | steep/windy hills | lava tube | Normal Ground | Total |
|---|---|---|---|---|---|
| `TrainingSamples_202609290009589587982` (29 Sep) | 275 | 39 | 44 | 97 | 455 |
| `new training.shp` (30 Sep) | 301 | 44 | 44 | 122 | 511 |
| **`Landform_TrainingSamples_terrain` (the labels)** | 302 | 44 | 44 | 122 | **512** |

**The project's class schema is the labels' order: 1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal
Ground** (§50). Every file holding labels or a model uses it (`THERMAL NIGHT.ecs`, both `.ecd`, the deep-learning
export's `.emd`); only `Composite Object Classes.ecs` (1 Oct, superseded) swaps 2 and 3, so a model or new
samples read through it would swap those classes without error. The polygons span 166.2°W to 94.9°E and 43.8°S
to 62.1°N: planet-wide, a few north of ±60°. They are **landform and terrain** classes, not material classes
(§40.1).

### 29.3 The labels replaced the §27 terrain polygons

`Landform_TrainingSamples_terrain` now holds the 512 hand-drawn polygons. As found,
`make_typearea_supervised.py` would have deleted and rewritten that class: fixed the same day (§29.8).
`new training.shp` is a near copy (one Crater fewer), not a backup.

### 29.4 The GUI 7-band composite departs from the project's grid **[V]**

Bands 1–3 Viking RGB, 4 DEM (−5,611 to 18,305 m), 5 `Slope_Mars_H1` (percent rise on a degree grid), 6 Night IR,
7 Day IR, on **Viking's grid** (CM 0, 231.54 m, global): the THEMIS bands rolled 180° and resampled, bands 6–7
empty outside ±60°, and the raw DEM beside 8-bit bands. At 231.54 m the resolving limit is ~2.3 km.
Corrected in §31.2.

### 29.5 The ±60° segmentation

15.5 / 15 / 20 in about 19 h: more detail and smaller segments than §23.5 recommends. Not measured for speckle
(q15) **[?]**; the 29 Sep SVM over it is a tile artefact (§30.2), the segmentation itself seamless.

### 29.6 The GUI deep-learning export **[V]**

4,507 tiles of 256 × 256 × 7 bands from `CompositeBand`, PASCAL VOC rectangles, 6,808 objects (Crater 3,152,
Normal Ground 2,691, hills 539, lava tube 426). The largest box is a whole tile (3.51 × 10⁹ m²). Built on a
stack that is mostly elevation (§30.3); redone from the corrected stack (§31.4, §50.2).

### 29.7 What this section changed

The inventory (§6) and the processing history (§8) carry these items.

### 29.8 Two scripts fixed, 2026-10-01 **[V]**

- **`make_typearea_supervised.py`** writes `Landform_TrainingSamples_terrain_auto`, and `safe_to_replace()`
  allows a delete only when the class is absent or every row's `MappedBy` is the script's own marker;
  otherwise `REFUSING: … Nothing deleted`.
- **`verify_all.py`** dates each cancelled run: four by 13 Sep, the fourth at 17 min 28 s, the fifth on
  24 Sep at 10 min 01 s.

Both proved on planted defects in scratch (a missing 13 Sep log, a missing 24 Sep log, a later run; the
hand-drawn class, script-only rows, one manual row, no `MappedBy` field): every case behaved as predicted.

---

## 30. The two GUI SVM classifications, checked — 2026-10-02 **[V]**

Read-only. `build\verify_svm_classifications.py` reproduces every number in about a minute
(`logs\svm_check.json`); `make_fig_svm_check.py` draws `pres1_img\svm_check.png`. **The 29 Sep map** (SVM over the
±60° segments + Night IR) and **the 30 Sep map** (SVM over `CompositeBand`). Layout 05 shows the checks.

### 30.1 Four independent checks **[V]**

| Check | 29 Sep map | 30 Sep map |
|---|---|---|
| Area shares at ±60° (Crater / hills / lava tube / Normal) | 51 / 45 / 1.4 / 2.7 % | 40 / 3.5 / 24 / 33 % |
| The 512 labels scored on the map (training set, an **upper** bound) | **19.5 %, κ −0.01** | **65.1 %, κ 0.47** |
| — polygons won by their own class: Crater / hills / lava tube / Normal | 224/301, 26/44, **0/44, 0/122** | 204/301, 38/44, 35/44, 45/122 |
| IAU craters ≥ 5 km away from the labels: 'Crater' inside 0.7 R vs a 1.5–2.5 R ring | 0.59 vs **0.67** (n 817) | 0.62 vs 0.53 (n 898) |

The two maps agree on 24.0 % of the band against 21.6 % by chance (κ 0.03). Normal Ground everywhere would score
55 % on the labels: the 29 Sep map scores below that, on its own training data.

### 30.2 The 29 Sep map follows its processing tiles, not the terrain **[V]**

Its class edges fall on **4096-pixel tiles** (6.91°) counted from 0°E and 60°N. Jump ratios across tile lines
against elsewhere (pyramid level 4): the composite 1.00 and the segmentation 1.01, but the classified map
**2.77** (columns) and **3.14** (rows). Not a misregistration: no longitude shift lifts its training κ above
0.14, while the 30 Sep map peaks at 0° (κ 0.47). **The cause is `ClassifyRaster`'s processing tiles** (§53.2).
**The map cannot be used as a result.**

### 30.3 The 30 Sep map is mostly an elevation map **[V]**

**Elevation alone reproduces 62.1 % of it** (each 500 m DEM bin given its majority class; the largest class alone
36.7 %): below −2 km 60–68 % Normal Ground, 0 to +4 km 60–62 % lava tube, above +4 km 84 % Crater. Rolled 180° it
still scores κ 0.35 on the labels. Outside ±60° the empty thermal bands make 91 % of the south polar region
Crater. The raw DEM band dominated, as §14.2 warned.

### 30.4 The metrics were proved on planted maps first

Crater disks painted Crater scored inside 0.998 / ring 0.046, rolled 180° 0.029 / 0.030; the labels painted with
their own class scored 1.000, κ 1.000; Normal Ground everywhere 0.555, κ 0.000.

### 30.5 What this led to

A defensible classification needed: no DEM band, valid slope, ±60° only, scored on held-out labels. Done in §31.

---
## 31. The fix: a corrected ±60° stack, a reclassification scored on held-out labels, and the work put into the project — 2026-10-02/03 **[V]**

**Request: put the work where it shows when the project is opened in Pro, clip everything to ±60°, and fix
what is wrong.** Every number below comes from a script in `build\` and its log in `build\logs\`. **The
400 m map of this section is superseded by the 200 m 11 × 11 map (§57, §57.2)**; its scores stand as the
baseline of §32.2, §55.3 and T1.

### 31.1 What shows in Pro **[V]**

`build\make_global60_maps.py`: **every Mars map clipped to ±60°** with `Map.clipLayers` on `Analysis_Extent_60`
(display only; `clipLayers(None)` undoes it); the map **"Mars ±60° Analysis"** (the classification over hillshade,
the training and held-out labels, the stack's inputs, the superseded GUI SVMs in a group); one map per check
frame ("Check — 29 Sep SVM", "Check — 30 Sep SVM"), so each frame shows its own layer live; layouts **04** and
**05**. **One map per layout frame**: layouts 01 and 02 had shown whichever layer of a shared map was on last.

### 31.2 The corrected stack **[V]**

`build\make_global60_svm_stack.py` → **`Global60\global60_svm_stack_200m.tif`**: G200, 106,694 × 35,565, 7 bands,
U8, nodata 0, **97.33 % co-valid**, overviews, statistics, the named CM 180 WKT.

| `CompositeBand` (30 Sep) | this stack |
|---|---|
| global; bands 6–7 empty past ±60° | ±60° exactly, the night mosaic's extent |
| THEMIS rolled 180° and resampled to 231.5 m | THEMIS 2 × 2-averaged on its own grid, never warped |
| raw DEM in metres beside 8-bit bands | **no elevation band**; 9 × 9 local relief (1.8 km) instead |
| `Slope_Mars_H1`, percent rise on a degree grid | slope in degrees, `global60_slope_deg.tif` |
| F32, ranges 0–255 beside −5,611–18,305 | every band U8, p1/p99 → 1–255 over ±60° |

**Bands: 1–3 Viking R, G, B (bilinear 231.5 → 200 m); 4 Night IR; 5 Day IR; 6 slope; 7 relief.** The p1/p99
limits are in the file's `STRETCH` metadata. Registration: Viking red against Day IR at the 1.6 km overview,
**r −0.147 at zero shift**, the strongest within ±19 km, +0.001 rolled 180° (bright dust is cool by day). Slope
against relief r 0.989. Cost ~1 h of compute (the Viking warp 24.6 min); the script printed 5 h 26 min because
the laptop slept (§28.9). Patched at 180° in §54.2.

### 31.3 The classification, scored on labels it never saw **[V]**

`build\make_global60_classification.py`:

- **The 512 labels clipped to ±60° and split by whole 15° × 15° blocks** (39 blocks, 14 held out; seed 60):
  **329 training, 183 held out** (held out: Crater 124/302, hills 16/44, lava tube 21/44, Normal Ground 22/122).
  No held-out polygon shares a block with a training polygon. `Landform_TrainingSamples_terrain_60_train` /
  `_60_test`; the original class was only read.
- Train Support Vector Machine, 1,000 samples per class, on the 200 m stack, 25.4 min →
  `Global60\global60_landforms_svm.ecd`. Classified at 400 m on the laptop (200 m would be ~15 h; run on the
  desktop in §55.3): `global60_landforms_svm_400m.tif`.

`build\verify_global60_classification.py`:

| | this map (400 m) | 30 Sep map | 29 Sep map |
|---|---|---|---|
| **Held-out polygons** | **70.5 %, κ 0.54** | — | — |
| Training polygons | 82.8 %, κ 0.67 | 65.1 %, κ 0.47 | 19.5 %, κ −0.01 |
| One class everywhere, held out | 58.6 % | | |
| Elevation bins alone reproduce | **54.6 %** | 62.1 % | |
| Tile-seam ratio (1.00 = none) | 1.00 | | 2.77 |
| 'Crater' inside IAU craters vs ring | 52 vs 44 %, n 817 | 62 vs 53 % | 59 vs 67 % |

Held-out producer's: Crater 55 %, hills 61 %, lava tube 39 %, Normal Ground 99 %; polygons won 103/124, 14/16,
4/21, 20/22. Area shares: Crater 33.0 %, hills 2.3 %, lava tube 10.7 %, Normal Ground 54.0 %.

**Verdict:** the first map scored on labels it never saw, better than both GUI maps on accuracy, seams and
elevation (54.6 % against 53.9 % for a constant: no longer an elevation map). **What it is not:** a map of what
the names suggest. Normal Ground is solid (99 / 78 %); 'Crater' behaves as **cratered terrain** (user's 92 %,
finds 55 %); hills middling (61 / 47 %); **lava tube is not usable** (10.7 % of the map, 1.8 % correct inside
held-out polygons; over Tharsis, Elysium and Hellas): 44 polygons are too few for a planet-scale class. THEMIS
coverage gaps show as nodata stripes poleward of ~40°.

### 31.4 The deep-learning export, redone **[V]**

`build\make_global60_dl_export.py` → `Mars Project\LabeledObjects\global60_svm_stack_200m\`: 256 × 256 chips,
stride 128, PASCAL VOC rectangles; **5,480 chips × 7 bands, 7,884 objects** (Crater 3,575, Normal Ground 3,241,
hills 610, lava tube 458). It holds the held-out labels too: **never train on it**; the training-split export
is §50.2. Boxes around area classes can be a whole chip (2.62 × 10⁹ m²); `Classified_Tiles` would suit those
classes, a change of method declined (§50).

### 31.5 Traps hit on the way

- **A full-extent `ClassifyRaster` from a script hands off to `LocalWorker.exe`** about 90 s in; until then the
  Python process sits at 0 % CPU and looks hung. It was stopped as hung, wrongly. The script classifies in 21
  tiles of 16,384 px, each checkpointed with a `.done` marker on internal disk, then mosaics them.
- **`Map.moveLayer` inside a group layer deletes layers.** Place group members with `addLayerToGroup(...,
  "BOTTOM")` in order; use `moveLayer` only at the top level. Pro auto-arranges added layers (new groups on top):
  order explicitly, and check the export.
- **A "dry run" that wrote the real project:** a `sed` edit meant to add `--aprx` matched nothing. Check that
  an edit landed; rehearse on a copy **beside** the `.aprx` (§13.3).
- cp1252 console crashes on `≥` (reconfigure stdout to UTF-8); `gdal.Open(p).GetRasterBand(1)` (§9).

### 31.6 Open items it left

q24 (the 29 Sep blocks) was answered in §53.2; q25–q26 in §50.

---

## 32. The digitising map, the basin layout, and a smoothed classification — 2026-10-03 **[V]**

### 32.1 What digitising needs, in the project

`build\make_candidate_maps.py`:

- **Map "Ius Chasma — digitising", layout `06_ius_digitising`**: the three empty digitising classes on top
  (channels blue, crater rims yellow, lava margins orange), then **"Channels: steep and rock-floored (188)"**, a
  definition query `SlopeDeg >= 5 AND ThermIdx < -0.15` (reproduces §25's 188 and 1,037 km), "Channels: other
  (2,422)" off, "Closed depressions ≥ 1 km (1,685)", over the Ius rasters. The notes say what the candidates
  cannot do (64 % on plateau under 2°; breached craters missing).
- **Map "Mars ±60° — basins", layout `07_global60_basins`**: the 5,144 basins as graduated symbols on
  `DiameterKm` (20–41 km to 1,027–2,697 km), IAU craters > 100 km in red; the notes quote §28.11 (68 % of 117,
  median +2.2 %).

Two traps: labels set on a graduated renderer's `classBreaks` through `arcpy.mp` do not stick (set the CIM's
`renderer.breaks`); single-symbol legends need `names=False` or the layer name repeats.

### 32.2 Majority filters, chosen by feature size, not by score **[V]**

`build\make_global60_landforms_clean.py --size n` (nodata never votes; ties keep the original class), each
scored by `verify_global60_classification.py --raster …`:

| window | pixels changed | held out | training | 'Crater' inside / ring |
|---|---|---|---|---|
| none (raw) | — | 70.5 %, κ 0.54 | 82.8 %, κ 0.67 | 52 / 44 % |
| 3 × 3 (1.2 km) | 7.3 % | 72.3 %, κ 0.56 | 84.7 %, κ 0.70 | 55 / 46 % |
| **5 × 5 (2 km)** | **11.2 %** | **73.5 %, κ 0.58** | **85.9 %, κ 0.73** | **57 / 47 %** |
| 7 × 7 (2.8 km) | 13.5 % | 74.3 %, κ 0.59 | 86.8 %, κ 0.74 | 58 / 47 % |
| 9 × 9 (3.6 km) | 15.1 % | 75.1 %, κ 0.60 | 87.5 %, κ 0.75 | 60 / 48 % |

**Every score rises with every window, on both label sets**, because the labelled polygons are large (median
107–652 km² outside lava tube): a polygon score rewards smoothing past the point where small landforms vanish,
and choosing on the held-out set would spend it. **The rule: about half the ~4 km resolving limit of a 400 m map
(the ~10 px rule, §23.5), so 5 × 5 at 400 m**; the same ~2 km rule gives 11 × 11 at 200 m (§57). The 400 m 5 × 5
map (73.5 %) was the published one until 2026-10-16.

### 32.3 Caveats

The stack's night and day bands are locally contrast-normalised (§28.10): in the classifier they carry local
contrast and texture, suitable for landform classes, never a material map. **[E]** The ±60° index sits in the
analysis map, off, labelled "compare within one area only (KB §28.10)".

---

## 33. Every layout exported and read; five presentation defects fixed — 2026-10-03 **[V]**

All seven sheets of that date were exported and read; `build\polish_layouts.py` fixes what reading found, in
the `.aprx`, idempotently (a second run reports "no change"). **The rules it left:**

- **Arial everywhere.** The builders asked for Aptos and the legend style for Tahoma; neither is installed, so
  Pro substituted different fallbacks (serif legends). `polish_layouts.py` sets every font to Arial and caps
  legend headings at 11 pt. **Run it after any layout builder**, export, and read every changed sheet.
- **Captions must match the record.** Sheet 02 said "bright = high thermal inertia"; now "warmer at night
  than its surroundings … local contrast, not calibrated thermal inertia (KB §28.10)", fixed in the builder too.
- **Explain what a sheet shows.** Sheet 04's grey streaks are no-data: 2.6 % of the band, 19 % of the rows south
  of 48°S, gaps between THEMIS orbits.
- Legends: no duplicated headings; manual columns where automatic ones split a group.

`isOverflowing` catches none of these; only reading the exported sheet does.

---

## 34. Twelve layers would have broken on the desktop; two more layout nudges — 2026-10-03 **[V]**

### 34.1 No layer reads through a junction

The junctions store absolute targets (`\??\Z:\Mars Project\Global60`), so a layer reading through one breaks
on the other drive letter. **12 layers read through `Z:\Global60`**; `build\repoint_junction_layers.py` pointed
them at the real folder (renders pixel-identical; a second run finds 0). The builders add layers from
`grid60.OUTDIR`, not `OUTDIR_NOSPACE`. **Rule: scripts may use the junctions for geoprocessing; layers in the
project must not.** Absolute band paths broke two more layers in §52.

### 34.2 Two nudges

Sheet 04's subtitle rewrapped inside the frame; sheet 06's north arrow moved clear of the legend. Both in
`polish_layouts.py` and the builders.

---

## 35. Backed up to GitHub, which is also the project page — 2026-10-06 **[V]**

**Request: a public repo, `Mars_Terrestrial_GlobalMosaic_GIS-Data`, that backs up as much as it can and is the
project page.** `https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data`. The drive stays the
working copy and the only home of most large derivatives. Clone:
`<home>\OneDrive\Documents\GitHub\Mars_Terrestrial_GlobalMosaic_GIS-Data` on either machine.

**Licensing, 2026-10-06:** code (`.py`, `.ps1`) **MIT** (`LICENSE`); everything else made for the project (this
file, documents, figures, layouts, the `.aprx`, vectors, release rasters) **CC BY 4.0** (`LICENSE-CC-BY-4.0.txt`).
Source mosaics and IAU nomenclature keep their producers' terms. The public name is **Logan M Edwards**
(`CITATION.cff`; the author's own commit, 2026-10-07).

### 35.1 What goes where **[V]**

| | where |
|---|---|
| `Mars Remote Sensing Project\` (this file, `build\`, logs, deliverables) | repo, same folder name |
| `Mars Project\`: the `.aprx`, `.atbx`, `.ecd` / `.ecs`, `GpMessages`, sidecars, RATs, models, layout PNGs, `LabeledObjects\` metadata | repo, same folder name |
| the drive root: the sources' `.aux.xml`, the night mosaic's `.lbl` / `.md5` | repo, `drive-root\` |
| the gdb's feature classes, the 512 labels included | repo, `exports\mars_project_vectors.gdb`; the two X2 classes release-only (§57.1); all in the GeoPackage |
| both type areas, ±60° classification maps (SVM and U-Net) and models, the deep-learning models, `.npy` caches, the GUI SVM maps, the GeoPackage | the data release (`data-2026-10-21`, §57.4, §66.10) |
| the seven ±60° derivatives, both deep-learning exports, the GUI ±60° segmentation | release `derivatives-2026-10-06` (§35.3) |
| the four source mosaics | **not copied**; linked by URL, sizes checked |

Not mirrored since §57.6: `.backups\`, `build\aprx_live\`, Presentation 1's figure folders and `.pptx`, the drive
root's `new training.*`, the `.backup_*` / `.py_backup_*` folders, `neutral_voice.py`, `Mars Project\Reference\`
(third-party). The repo stores files byte-exact (`.gitattributes`: `* -text`).

### 35.2 Keeping it current

Each script finds its drive (§40.2):

- **`build\github_sync.py`** (stdlib, either Python): mirrors what changed into the clone (bytes compared when
  sizes match and mtimes differ, §58), skips files over 95 MB, removes files deleted on the drive, regenerates
  `docs\scripts.md`; `--commit` commits and pushes. Only reads the drive.
- **`build\github_export_gdb.py --rasters`** (ArcGIS Python): re-exports the gdb vectors into `exports\`, writes the
  layer catalogue `exports\README.md`, stages the GeoPackage and the two GUI SVM maps. **Run after digitising**:
  manual edits live only in the gdb. A re-export rewrites every gdb file (new UUIDs, ~60 MB of history) even with
  no change, so only after real edits; `--catalog-only` rewrites the catalogue; `--rasters-only` the two maps.
- **`build\github_catalog_rasters.py`** (ArcGIS Python, seconds): writes `docs\rasters.md` from GDAL headers, with
  a description and the release asset for each raster; an undescribed one prints "(not described)". Re-run after
  any new raster product. It found the 0-based pixel values (§36).
- **`build\github_release_bundle.py --upload data-YYYY-MM-DD`**: zips the release groups (parts under 1.9 GB) and
  publishes them; then point `github_catalog_rasters.py`'s `DATA` and `github_export_gdb.py`'s `RELEASE` at it.
- **Repo-only:** `restore.py` (rebuilds the drive from a clone and the releases; never overwrites without
  `--force`; tested byte-identical on the 2-piece `global60_dem.tif`, 3.2 GB in 352 s), `tools\check_repo.py`
  (CI on every push: links, Python syntax, sizes, `CITATION.cff`, the README's stated counts), `tools\check_remote.py`
  (by hand only: release assets against their sums, linked tags, the sources' sizes), `CITATION.cff`.

The clone is in OneDrive: check for `*-DESKTOP-PJS73RO.*` conflict copies before committing (`.gitignore`
excludes them).

### 35.3 The large products, as a second release

`build\github_release_large.py derivatives-YYYY-MM-DD` (ArcGIS Python) published **`derivatives-2026-10-06`**: the
seven ±60° derivatives (`global60_svm_stack_200m`, `_thermal_contrast`, `_thermal_contrast_200m`, `_dem`,
`_slope_deg`, `_aspect`, `_hillshade`; 67.6 GB) as their original bytes in 1.9 GB `.partNNN` pieces, their
sidecars, both `LabeledObjects` exports and `Segmented_202609290011302066080`; one `SHA256SUMS` over every piece
and every reassembled file. **Finished 2026-10-07: 46 assets, 74.4 GB, every SHA-256 matching (45/45).** It took
~16 h, not 2: a DNS failure (now retried), Modern Standby twice on battery (which `SetThreadExecutionState` does not
prevent), and the uplink falling from ~10 MB/s to 0.7–1.4 MB/s. **Big uploads: on AC, lid open, wired if possible.**
Its DEM, slope, aspect, hillshade and stack predate the §54 patch; `docs/backup.md` gives the two patch commands.

**Not backed up:** the `.ovr` pyramids (Build Pyramids recreates them) and the legacy gdb rasters that §7 and
§29–§30 find defective.

---

## 36. The landform maps' pixel values are now the class codes — 2026-10-07 **[V]**

`ClassifyRaster` writes pixels 0..n−1 and keeps the codes only in the attribute table's `Classvalue`, so a raw
reader (GDAL, numpy, QGIS without the RAT) got every class off by one against labels coded 1–4.

### 36.1 What changed

- The ±60° landform maps hold **1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground, 255 no class**; the
  RAT has Value = Classvalue; grid, NoData, colours, overviews unchanged.
- The originals were **moved, not deleted**, to `Global60\_0based_originals\`.
- `build\landform_codes.py` does the recode from the raster's own table (`fix_landform_values.py` applied it,
  idempotently). The sources cannot bring 0–3 back: the classifier recodes after its mosaic, and
  `make_global60_landforms_clean.py` reads the class values from the table.
- The `.aprx` needed no change: the layers key their symbology on `Class_name`.

### 36.2 Proved, not assumed

Every pixel of every map equals the old value + 1 (old ≠ 255), counted independently (the same check on an
un-recoded file reports 923,742,337 mismatches, so it can fail); the updated filter reproduces the recoded
`_mode5` exactly; rescored identically (raw **70.5 %, κ 0.540**; 5 × 5 **73.5 %, κ 0.578**).

### 36.3 The same convention elsewhere

Recoded too (§36.4).

### 36.4 The rest recoded: the type-area maps and the two GUI maps **[V]**

`build\fix_classified_values.py`: `TypeArea\ius_sup_spectral.tif` / `_thermal` / `_augmented` (0–5 → 1 crater
interior, 2 steep wall, 3 moderate wall, 4 chasma floor, 5 plateau flank, 6 plateau) and the two gdb
`Classified_*` maps (0–3 → 1–4; originals renamed `<name>_0based`). **Every classified raster in the project now
has pixel value = class code.** The GUI maps had only a mask, under which the 29 Sep map stored 0 (Crater): its
401,286,036 masked pixels are now NoData 255.

- **The drive dropped off USB mid-write** ("Delayed Write Failed") while `CopyRaster` wrote into the gdb on the
  drive, 40 minutes in; a second copy failed with ERROR 000260. The script now **builds on internal disk and
  copies the finished dataset to the drive once**, and resumes from `<name>_0based`. **Big writes to internal disk
  first.**
- **numpy 2 keeps `np.where(mask, 256, uint8_array)` as uint8**: 256 wraps to 0. Cast to int16 first.
- **Full-width 2048-row strips thrash GDAL's cache** on gdb rasters (58 GB read for a ~600 MB raster); read one
  block (128 rows) high with a 2 GB cache.
- The release copies are GeoTIFF with 255 written under the mask (`github_export_gdb.py --rasters-only`).

## 37. Everything that isn't Mars is out of the project — 2026-10-07 **[V]**

**Instruction:** "anything that isnt part of MARS is not relevent tho so please remove it." `build\remove_non_mars.py`
moved, never deleted: the maps "Map" (Earth basemaps), "Map1" and "Enceladus" (the Enceladus DEM), "Mercury"
(the MESSENGER basemap), each exported to `.mapx` first, and the gdb raster `Mercury_MESSEN_IsoClusterUns`, all to
`<drive>\_removed_not_Mars\` (with a README). That folder went to the Recycle Bin in §50.1, where it still is;
emptying the bin is the author's call. The `.aprx`'s geoprocessing history still records the Mercury run; the
record keeps the Mercury settings because the inherited segmentation parameters came from them (§23.3).

## 38. The mosaic itself, as a layout — 2026-10-08 **[V]**

`build\make_mosaic_layout.py`: **layout `08_global60_mosaic`**, four one-layer maps (one per panel):

| panel | map | layer |
|---|---|---|
| A | "Mosaic ±60° — visible" | Viking colour, stack bands 1–3 |
| B | "Mosaic ±60° — day IR" | THEMIS Day IR, stack band 5 |
| C | "Mosaic ±60° — night IR" | THEMIS Night IR, stack band 4 |
| D | "Mosaic ±60° — topography" | `global60_dem.tif`, 35 % transparent over `global60_hillshade.tif` |

- Drawn from the stack (G200, already stretched, overviews built): about a second per export.
- **The diurnal index is deliberately not a panel** (§28.10); the captions say the THEMIS panels are locally
  normalised (why B and C look near-uniform grey at this scale) and that Viking albedo carries the regional signal.
- ~~The maps draw in the stack's own CRS, centred on 180°E~~ (to 2026-10-19): reprojected, the raster's 0°/360° edge
  had left a white seam down each small frame. **Since §64 they draw in `GCS_Mars_2000`, centred on 0°E like every other
  ±60° sheet**, with the 30° graticule; no seam shows (the 0°E meridian line would cover a one-pixel one).
- **`Map.moveLayer(reference, moved, …)`: the reference layer comes first.**
- Band layers are added as the whole stack with the band chosen in the colorizer, not by a band path, which Pro
  stores absolute (§52).

## 39. Next steps, brainstormed — 2026-10-08

The plan moved into **`NEXT-STEPS.md`** and the interim's into **`INTERIM-PLAN.md`**; this file stays the
authority on what is true. Facts found while writing them:

- **Athabasca Valles is inside the analysis extent**: IAU 153.2–156.8°E, 7.2–10.0°N, beside Cerberus Fossae
  (154.4–174.7°E, 6.2–16.2°N), from `MARS_nomenclature_misc_March2019`; it became the second type area (§42.1). **[V]**
- Lava flows had no product at any scale; the geologic map was then not held (§41). **[V]**

### 39.1 The interim date, and two plan files

**The interim is due mid-November** (§1). The plan gained a session-start checklist, the decisions D1–D13
(answered in §50), the reference downloads, eight tests T1–T8 each with its prediction written before it runs,
a figure list for both deadlines, and dates: **digitising checkpoint 1 November** (if the digitising classes are
still empty, both documents present the machine products as candidates with measured recall), **interim data
cut 2 November**, interim ~13 November, **data freeze 22 November**. The interim's four hypotheses and six
questions are tracked in `INTERIM-PLAN.md` §5.

### 39.2 The interim folder, read 2026-10-08

`NEXT STUFF\` holds `2 Interim Presentation Template.pptx`: two slides of headings, *Project Title*, *Project
Investigators*, *Project Goals*, *Relevant Spectral Bands*, *List of Project Tasks and Percent Complete*,
*Preliminary Results (if available)*, *Project issues and Hurdles*, under "Remote Sensing Project – Interim
Presentation". **Those seven headings are what the course asks of the interim.** The September deck and report
held no map or figure at all.

### 39.3 The interim as a living build in the Presentation 1 style **[V]**

**Decided:** the Presentation 1 style with graphics, no fixed slide count, rebuilt as the data move. `build\interim.py`
(every word and number, each with its §), `build\make_interim_figs.py` (layouts at 200 dpi with the sheet prose
hidden in memory, never saved; trimmed; legends split out) and `build\build_interim_live.py` (`le_theme.py`).
How it runs is section 0 of `INTERIM-PLAN.md`. Lessons:

- **A whole layout sheet on a slide fails**: captions shrink to fine print and the map to a third of the slide.
  Hide the prose for the export; a tall sheet becomes a chart instead (§51.5).
- **A legend exports blank once its map frame is hidden**: cut legends out as the difference between the sheet
  exported with and without them.
- Province figures: quote a number with its province set. Since 2026-10-19 `pres1_img\global60_thermal.png` and
  the deck quote §28.10 only: −0.0009 (index, seven provinces) and 47.67 DN (Viking, four provinces) (§62); the
  54.4 DN of its Presentation 1 version came from five boxes of its own.

### 39.4 The project's text in an objective, impersonal voice **[V]**

**Request:** everything written from an objective, impersonal point of view, the public repo included.
**`build\neutral_voice.py`**: ordered phrase rules, anchored at word starts; `--check` exits 1 on any
third-person pronoun. Applied to this file, the plans, `Global60\README.md`, every build script, the `.aprx`'s
layer names and layout text (`build\fix_label_names.py`; a renamed layer keeps its internal file name, so
`build\rebuild_groups.py` recreated the two renamed groups), and the figures. Verbatim quotations of instructions
keep their wording; delivered documents and the CC BY legal text are left as they are. The tool lists the phrases
it removes, so it is kept off the project page. **Run `neutral_voice.py --check` on any edited text before it is
mirrored.**

## 40. Test T1, and scripts that run on either drive — 2026-10-08 **[V]**

### 40.1 T1: the thermal bands add 1.3 points; slope and relief alone match the full stack

`build\make_thermal_ablation.py`, `logs\thermal_ablation.json`, figure `make_fig_ablation.py` →
`interim_img\thermal_ablation.png`. Prediction written first: little or no gain at ±60° (§28.10).

- **Samples:** every 400 m pixel of the stack inside the §31 split, valid in all 7 bands: **38.3 M training pixels in
  328 polygons, 2.69 M held-out pixels in 183 polygons**, area-weighted by cos(latitude).
- **Classifier:** Gaussian maximum likelihood, equal priors, numpy (scikit-learn is in neither Python). Absolute
  scores differ from the SVM's; the comparison between band sets is the result. Cross-check: one class everywhere
  gives **58.6 %**, exactly §31.3's.
- **Uncertainty:** 1,000 paired bootstrap resamples of whole held-out polygons.

| bands | held-out accuracy | κ |
|---|---|---|
| terrain only (slope, relief) | **68.6 %** | 0.515 |
| without visible (no Viking) | 68.1 % | 0.509 |
| all 7 bands | 67.0 % | 0.502 |
| without thermal (no night, day) | 65.7 % | 0.489 |
| visible + thermal (no terrain) | 42.4 % | 0.205 |
| visible only | 40.3 % | 0.174 |
| thermal only | 38.7 % | 0.151 |
| one class everywhere | 58.6 % | — |

- **The thermal bands add +1.3 pt, 95 % interval +0.6 to +2.2 (κ +0.013, +0.006 to +0.017)**: detectable and small.
  Confirmed with Pro's SVM in §56.
- **Terrain alone matches or beats the full stack** (inside the intervals); without terrain, visible and thermal
  score below the one-class baseline.
- **The four hand-drawn classes are landform classes**, a terrain property; they cannot price a material signal.
  That needs material labels or a local test (§42.4).
- The unrounded terrain-only κ is **0.5148** (so the slide says 0.51: round from the log, §48). Summing per-polygon
  confusion matrices instead of holding 1,000 index arrays: same result, 26 s.

### 40.2 Every build script finds its drive **[V]**

`build\paths.py`: `DRIVE` is two levels above `build\` (`abspath`, not `resolve`), `on_drive(rel)` joins under it,
`junction(name)` checks a no-space alias and, if it is missing or broken, stops with the command to fix it (since
§58, `retarget_junction.py` for a broken one). 114 path literals in 58 scripts were rewritten by a token-level pass
(originals in `build\.py_backup_20261008\`). A latent bug it exposed: `grid60.py` joined `ROOT, "\\", file`, which
resets to the drive root. Proved from a stand-in root through junctions.

### 40.3 Two figures corrected

`ius_fusion.png`'s third panel is "relative diurnal contrast" (red large swing, dust-like; blue small swing, bedrock
and coarse debris), marked 8-bit DN; `svm_check.png` regenerated for §39.4.

## 41. The reference data: geologic map, crater database, calibrated thermal inertia — 2026-10-08 **[V]**

Approved 2026-10-08. In **`Mars Project\Reference\`**, one folder each, SHA-256 of every file in
`Reference\README.md`; third-party, never mirrored. Zips listed before extraction.

| dataset | source | in the project |
|---|---|---|
| USGS **Geologic Map of Mars**, SIM 3292 (Tanaka et al. 2014), public domain | `pubs.usgs.gov/sim/3292/downloads/sim3292_database.zip` (808.9 MB) | `Ref_SIM3292_GeologicUnits`: 1,311 unit polygons; `UnitGroup` = the type code without its age (`lAv` → `v`); frame label §47.1 |
| **Robbins & Hynek crater database**, 2020 release (cite Robbins & Hynek 2012, JGR 117, E05004) | `craters.sjrdesign.net` (39.4 MB zip; comma-separated, not tab as stated) | `Ref_Craters_Robbins2020`: **385,049** craters ≥ 1 km, circle-fit centre, `DiamKm` |
| **TES thermal inertia**, Putzig & Mellon 2007 (Icarus 191), dayside and nightside, 20 px/° | `se.psi.edu/inertia/2007` | `TES_TI_2007_dayside/_nightside.tif` (Int16 tiu, nodata 0) and `_measured.tif` (`make_tes_reference.py`) |

- **Craters registered:** every IAU crater > 100 km matches a Robbins crater; centre offset median **1.0 %** of the
  diameter (p90 2.9 %), size ratio median **1.000**.
- **Units registered:** Olympus Mons summit in `Ave`, Hellas floor in `lHb`, Arabia Terra in `mNh`, the Ius floor in
  `Aa`; **Athabasca Valles in `lAv`, Late Amazonian volcanic**, the flood-lava reading behind §14.4.
- **TES orientation proved:** columns are west longitude and the first row −90°; only that reading correlates
  negatively with Viking red over ±60° (dayside r −0.279, nightside −0.320). **A byte-order bug caught by reading the
  output back**: GDAL wrote the big-endian integers unswapped (Tharsis 9,728 tiu); the script now reads each file
  back and asserts range and province order.
- **The calibrated contrast the THEMIS mosaics lose:** dayside median **45 tiu** over the dusty provinces (Tharsis 41,
  Arabia 50, Amazonis 43) against **246 tiu** over the rocky ones (Syrtis Major 228, Acidalia 264): fivefold, at 3 km,
  where THEMIS DN separated the same boxes by under 0.3 DN.
- The masks mean "measured": 90.0 % (dayside) and 88.3 % (nightside) of pixels.

## 42. Athabasca Valles, the second type area, and three tests against the references — 2026-10-08 **[V]**

### 42.1 The area, built by the same scripts as Ius

`build\areas.py` holds both windows; the type-area chain takes `--area ath`.

- **Window** 150–162°E, 4–14°N, snapped to the day mosaic: **7,114 × 5,929 px**, 42 Mpx. Products `ath_*` in
  `Mars Project\Athabasca\`, junction `<drive>\Athabasca`.
- Band correlations follow Ius: visible 0.81–0.95 with each other, day IR −0.35 to −0.42 against visible, night IR
  |r| ≤ 0.15 against everything. Slope mean 1.8° (smooth lava plains). The index: r +0.015 with elevation, −0.12
  with slope; the THEMIS DN statistics again equal the mosaic-wide ones (§28.10).
- **Candidates:** `Landform_ChannelCandidates_auto_ath`, 3,283 centrelines (23,677 km; 38.8 % of stream cells
  discarded as fill artefact; 409 "damped", i.e. rock-floored); `Landform_CraterCandidates_auto_ath`, 1,709 closed
  depressions ≥ 1 km. No IAU-named crater in the window.
- **Layout `09_athabasca_digitising`** (`make_candidate_maps.py`, both digitising sheets from one function): at
  Athabasca 97 % of candidates lie under 2°, so the prompt is rock-floored alone (409).

### 42.2 T2: crater density per unit, Robbins against the detector

`build\make_crater_density.py`, `logs\crater_density.json`: craters ≥ 1 km per 10⁶ km² per SIM 3292 unit (units ≥
20,000 km² in the window). Prediction: the Athabasca lava far below the older units.

| window | unit | km² | Robbins | per 10⁶ km² | detector | per 10⁶ km² |
|---|---|---|---|---|---|---|
| Athabasca Valles | `lAv` Late Amazonian volcanic unit | 184,458 | 207 | 1122 | 916 | 4966 |
| Athabasca Valles | `AHv` Amazonian and Hesperian volcanic | 166,437 | 293 | 1760 | 490 | 2944 |
| Athabasca Valles | `HNt` Hesperian and Noachian transition unit | 40,762 | 89 | 2183 | 253 | 6207 |
| Ius Chasma | `lHv` Late Hesperian volcanic unit | 48,490 | 358 | 7383 | 281 | 5795 |
| Ius Chasma | `eHv` Early Hesperian volcanic unit | 106,627 | 287 | 2692 | 553 | 5186 |
| Ius Chasma | `lNh` Late Noachian highland unit | 25,653 | 77 | 3002 | 180 | 7017 |
| Ius Chasma | `eHh` Early Hesperian highland unit | 23,004 | 61 | 2652 | 167 | 7260 |
| Ius Chasma | `Nhu` Noachian highland undivided unit | 83,005 | 23 | 277 | 182 | 2193 |
| Ius Chasma | `Htu` Hesperian transition undivided unit | 26,299 | 5 | 190 | 53 | 2015 |

- **Robbins: lAv is the least cratered large unit in its window, 1,122 against 1,760 (AHv) and 2,183 (HNt) per 10⁶
  km²**: the predicted direction, about half, not "far fewer" (at 1 : 20 M the polygon spans more than the young flood
  lava). Relative density only, never an age.
- **The detector reverses it** (4,966 on `lAv`): on flat lava it counts closed depressions that are not craters.
  Unusable for T2.

### 42.3 The crater detector against Robbins: precision is low below a few km

A candidate matches a Robbins crater if its centre is within half the Robbins diameter and its diameter within a
factor of 2.

| window | D ≥ | Robbins craters | found (recall) | candidates | that match (precision) |
|---|---|---|---|---|---|
| Ius | 1 km | 935 | **21 %** | 1685 | **11 %** |
| Ius | 2 km | 198 | 49 % | 452 | 21 % |
| Athabasca | 1 km | 592 | **36 %** | 1709 | **13 %** |
| Athabasca | 2 km | 191 | 56 % | 352 | 30 % |

At the sizes that make up the type-area candidates, about nine in ten are not catalogued craters. **The layers are
closed depressions; for craters use `Ref_Craters_Robbins2020`.** The ±60° version is §53.4.

### 42.4 T3, local: the index against calibrated thermal inertia

`build\make_tes_local_check.py`, `logs\tes_local_check.json`: each window's 100 m rasters averaged into TES's 0.05°
(~3 km) cells, measured TES pixels only. Prediction: the index clearly negative against log inertia in both windows.

| | index | Viking red | THEMIS day DN | THEMIS night DN |
|---|---|---|---|---|
| Ius, dayside TES | -0.08 | -0.10 | +0.02 | +0.11 |
| Ius, nightside TES | -0.22 | -0.26 | +0.11 | +0.36 |
| Athabasca, dayside TES | -0.02 | -0.55 | +0.04 | +0.05 |
| Athabasca, nightside TES | -0.01 | -0.64 | +0.05 | +0.05 |

- **The prediction fails at 3 km**: the index barely tracks calibrated inertia at Ius and not at all at Athabasca;
  **Viking albedo does at Athabasca (−0.55, −0.64)**. Night IR at Ius tracks nightside inertia the physical way (+0.36).
- **What is left of the thermal claim:** the index is independent of topography (§24.3, §42.1); whether it separates
  materials below 3 km is untestable with calibrated data. At every scale a calibrated product can check, visible
  albedo carries the material signal and the held THEMIS mosaics do not; T1 (§40.1) agrees.

## 43. T3 planet-wide, T8 against the geologic map, and the lava-tube relabel tested — 2026-10-08 **[V]**

Decisions taken first: **D12, lead both documents with the measured limits**; **D6, test a relabel of "lava tube"
from the geologic map before any SVM rerun.**

### 43.1 T3, planet-wide: the THEMIS pair keeps a weak local signal; Viking carries the regional one

`build\make_tes_global_check.py`, `logs\tes_global_check.json`: each ±60° layer at the 1.6 km overview, averaged into
TES cells, against log TES inertia; globally and as the median r within 192 blocks of 15° × 15° (interquartile range).

| layer | dayside r, global | dayside r, within blocks | nightside r, global | nightside r, within blocks |
|---|---|---|---|---|
| Viking red | -0.31 | -0.06 [-0.17, +0.01] | -0.36 | -0.10 [-0.23, -0.00] |
| THEMIS night DN | +0.04 | +0.06 [+0.04, +0.09] | +0.05 | +0.11 [+0.07, +0.15] |
| THEMIS day DN | +0.00 | -0.01 [-0.03, +0.01] | +0.01 | -0.01 [-0.04, +0.02] |
| diurnal-contrast index | -0.03 | -0.05 [-0.08, -0.03] | -0.03 | -0.08 [-0.14, -0.05] |
| slope | +0.03 | -0.05 [-0.11, +0.04] | +0.06 | +0.00 [-0.08, +0.09] |

- **Viking tracks calibrated inertia across the planet** (r −0.31 / −0.36), much less within a block: a regional
  signal, the dust provinces.
- **Night IR and the index carry a weak, consistent local signal in the physical direction** (quartiles all of one
  sign within blocks), which vanishes globally: what region-by-region stretching predicts. Weak: |r| ≈ 0.1 at 3 km.
- Day IR carries nothing.

### 43.2 T8: the ±60° classes against the geologic map

`build\make_geomap_check.py`, `logs\geomap_check.json`: the classification at 1.6 km against SIM 3292 unit groups,
as enrichment P(class | group) / P(class); not an accuracy. Measured on the 400 m 5 × 5 map; rerun on the published
map in §57.1 with no finding changed.

| group (area) | Crater | steep/windy hills | lava tube | Normal Ground |
|---|---|---|---|---|
| `v` volcanic plains (22.8 %) | ×0.47 | ×0.34 | ×0.87 | ×1.38 |
| `ve` volcanic edifices (1.1 %) | ×1.20 | ×1.19 | ×3.34 | ×0.45 |
| `a` aprons (1.3 %) | ×1.05 | ×4.05 | ×4.12 | ×0.30 |
| `h` highlands (41.2 %) | ×1.34 | ×0.95 | ×1.02 | ×0.78 |
| `i` impact (5.5 %) | ×1.39 | ×1.55 | ×1.15 | ×0.71 |
| `hu` highland undivided (2.1 %) | ×1.18 | ×6.51 | ×1.19 | ×0.66 |
| `l` lowlands (9.2 %) | ×0.25 | ×0.05 | ×0.05 | ×1.67 |

- **"Lava tube" is not enriched on the volcanic plains (×0.87)**, as predicted; it sits on edifices (×3.3) and aprons
  (×4.1): steep volcano flanks. Topography again.
- The other three sit where the map says they should. **A coherent terrain map, not a lava-flow map.**

### 43.3 The lava-tube relabel, tested before the SVM rerun

`build\make_lava_relabel_test.py`, `logs\lava_relabel_test.json`; the T1 classifier at 1.6 km on the §31 held-out
blocks; volcanic samples from SIM 3292 `v` / `ve` / `vf` outside every hand polygon.

| variant | held-out accuracy, Crater / hills / Normal Ground polygons | the third class |
|---|---|---|
| A: four hand-drawn classes | 70.2 % | lava tube found on 36 % of its held-out area |
| B: lava tube → "volcanic (map)" | 70.2 % | volcanic: producer's 21 %, user's 30 % |
| C: three classes, lava tube dropped | **79.0 %** | — |

- Volcanic plains are not separable from other plains in these bands (75 % come out Normal Ground).
- **The author's answer: keep all four hand-drawn classes; a fifth only if it helps.** Variant **D** (four + "volcanic
  (map)"): Crater / hills / Normal Ground fall to **64.6 %**, and of what the fifth class calls volcanic only **30 %
  is, below the 38 % base rate**: worse than chance. **Decision: no fifth class, no rerun.** Lava flows are shown from
  the geologic map's volcanic units (§44).

## 44. Graticules, and layout 10: the locator with the lava-flow reference — 2026-10-08 **[V]**

`build\make_reference_maps.py`. **Run it after the other map builders** (they wipe their maps), then `polish_layouts.py`.

- **Graticules as data** (§22.3): `Graticule_30deg` (17 lines, labelled "30°N", "270°E": east longitude 0–360) on the
  ±60° maps, `Graticule_2deg` (25 lines) on the type-area maps; densified so they bend correctly in CM 180.
- **Layout `10_global60_locator`**: Viking colour, the analysis extent, `Type_Areas` labelled, and **SIM 3292's
  volcanic units (`v`, `ve`, `vf`) in orange: the project's lava-flow reference**. It opens the interim's results.
- Every class it writes carries `MappedBy = make_reference_maps.py`; a class holding other rows is never replaced.

## 45. The interim report rebuilt, and every interim number checked against this record — 2026-10-08 **[V]**

- **The report is a living build too:** `build\build_interim_report_live.py` writes the `.docx` from `interim.py` and
  the figures of `make_interim_figs.py`, so the report and the deck cannot disagree; typography from `build\docx_kit.py`.
- **The interim leads with the measured limits (D12):** the weak thermal signal, the terrain nature of the classes,
  lava flows from the geologic map, closed depressions not being a crater count. The T3 chart: `make_fig_tes.py` →
  `interim_img\tes_check.png`, colours from the dataviz reference palette (validated: CVD ΔE 24.7, contrast ≥ 3 : 1).
- **`build\verify_interim.py`:** every number in `interim.py`'s strings must appear in this file (section references,
  dates, years and integers 0–20 ignored; a slide may round a more precise value here). **Run it before delivering.**
  It proves a number exists here, not that it sits beside its claim (§48).
- **THEMIS infrared**, as the bands slide quotes: the instrument's ten IR bands span **6.8–14.9 µm**; the held mosaics
  are single-band 8-bit products from it (§3, §24). **[E]**
- **`verify_all.py`'s Mercury lineage check** read evidence that survived only in gdb free space; retired with the
  `_removed_not_Mars` folder (§50.1), not made to pass.

## 46. Digitising by review: the review fields and the accept script — 2026-10-08 **[V]**

D10: digitising starts by judging the machine candidates in the attribute table, then drawing only what they miss
(breached craters, lava margins). The judgement stays manual; **only an explicit accept moves a candidate into a
`Landform_*` class**.

- **`build\add_review_fields.py`** (once, idempotent) added to the four type-area candidate classes `Review` (TEXT 6,
  coded-value domain **`ReviewDecision`** = accept / reject / unsure, a drop-down in Pro; empty = not reviewed) and
  `ReviewNote` (TEXT 60); `Landform_ChannelCenterlines` and `Landform_CraterRims` gained `SourceID` (TEXT 48,
  `<candidate class>:<OBJECTID>`).
- **`build\accept_reviewed.py`**: a dry run by default prints, per class, accept / reject / unsure / not reviewed and
  the detector's precision, accept ÷ (accept + reject). `--apply --by "<name>"` copies new accepts (`MappedBy` = the
  reviewer); geometry unchanged; `UnitName`, `Confidence`, `Origin`, `Preservation` copied **as they stand on the
  candidate** (set them before accepting); `Evidence` gains "; accepted in review"; `GradientPct` stays empty
  (`SlopeDeg` is terrain slope along the line, not channel gradient). Reruns skip anything copied (`SourceID`). It
  never deletes: a copied row whose candidate is no longer "accept" is listed for removal by hand. Every value is
  checked against its target field before any write.
- Rehearsed on a scratch gdb: 15 / 15 checks, including two planted defects refused with nothing written.
- **Workflow:** open "Ius Chasma — digitising" (or Athabasca), the candidate layer's attribute table, set `Review`
  (and `Origin` / `Preservation` / `Confidence` when accepting), save edits, run `accept_reviewed.py` (dry run, then
  `--apply --by`), re-export the gdb (§35.2). Steps in `NEXT-STEPS.md` §3 and §6.

## 47. Tests T5, T6, T7: flow margins, composite stability, tributary orders — 2026-10-08 **[V]**

Each with its prediction and verdict rule written into the script first; logs `t5_flow_margins.json`,
`t6_composite_stability.json`, `t7_order_sweep.json`; each reran to identical numbers. **None supports the
prospectus' claim.**

### 47.1 The geologic map's frame label, corrected

`Ref_SIM3292_GeologicUnits` is labelled **GCS_Mars_2000 (WKID 104905, the ellipsoid)**, but its vertices are the
sphere's coordinates unshifted (the import had no datum transformation): max difference 5 × 10⁻¹⁰° on 40 features
against the source inverted on its own sphere. Earlier uses (T2, T8, layout 10) are unaffected; a transformation
added later would move latitudes by up to ~0.2°, so T5 converts lon/lat to the grid directly. **[V]**

### 47.2 T5 (H1): do the IR mosaics show lava-flow contacts that Viking misses?

`build\make_flow_margin_test.py`, Athabasca window: five SIM 3292 units, **14 internal contacts, 2,764 km**; profiles
every 2 km, perpendicular, ±20 km; separation d = |mean difference| / pooled sd; a profile "separates" above the
band's null 90th percentile (2,000 random profiles ≥ 25 km from any contact, so 10 % of null by construction);
intervals by bootstrap over contacts. Registration check: units at ±10 km differ on **97.2 %** of contact profiles,
**0 %** of null ones.

| band | lAv contacts (905 profiles, 10 contacts) | all contacts (1,234 profiles, 13 contacts) |
|---|---|---|
| Viking red | 12.3 % [2.6, 21.6] | 13.2 % [4.1, 20.0] |
| Viking green / blue | 11.3 % / 11.5 % | 11.9 % / 11.9 % |
| **day IR** | **21.0 % [3.3, 38.4]** | **18.2 % [5.1, 32.8]** |
| night IR | 11.7 % [3.3, 20.2] | 12.7 % [5.7, 20.1] |
| diurnal-contrast index | 13.0 % [3.0, 24.9] | 11.8 % [4.4, 21.0] |
| day − Viking red | +8.7 pt [−1.7, +18.1]; day-only 137, Viking-only 58 | +4.9 pt [−3.6, +14.6]; 152 vs 91 |
| night − Viking red | −0.6 pt [−4.9, +12.3] | −0.5 pt [−4.5, +8.9] |

- **Verdict by the rule fixed in advance: H1 not supported** (the day − Viking interval includes 0). Day IR leans in
  H1's direction: a hint, not a result.
- Every band separates the 1:20 M contacts only slightly more often than random lines (11–21 % against 10 %): at this
  map scale contacts are generalised by kilometres, and 10 independent contacts cannot settle H1.
- **What would settle it:** the same script on lava margins digitised at 100 m at Athabasca (`--margins`,
  `NEXT-STEPS.md` §3). It needs the `<drive>\Athabasca` junction (§58.2). **[V]**

### 47.3 T6 (H3): is the composite more stable than any single input?

`build\make_composite_stability.py`, Ius, Iso Cluster as §19; stability = adjusted Rand index (ARI) between maps
trained on the west and on the east half; coherence = share of 4-neighbour pairs in one class.

| input | stability (ARI) | coherence | classes ≥ 1 % |
|---|---|---|---|
| Viking RGB | 0.611 | 0.841 | 10 |
| day IR | **0.891** | 0.697 | 10 |
| night IR | 0.866 | 0.543 | 10 |
| 4-band composite (the hypothesis' input) | 0.396 | **0.846** | 10 |
| 5-band composite | 0.378 | 0.798 | 10 |

**H3 not supported**: the composites give the least reproducible partitions, while being the most coherent. A
one-band Iso Cluster is close to a density slice, so it reproduces easily but speckles. Stability is not meaning:
§19.3's geological coherence stands. **[V]**

### 47.4 T7 (Q5): how many tributary orders does the 100 m stack resolve?

`build\make_order_sweep.py`, Ius, the cached routing and the fill mask; per order, the share of stream cells on
slopes ≥ 2° (53.3 % of the window is ≥ 2°).

| threshold (cells / km²) | 100 / 1 | 250 / 2.5 | 500 / 5 | 1,000 / 10 | 2,000 / 20 | 5,000 / 50 | 10,000 / 100 | 20,000 / 200 | 50,000 / 500 |
|---|---|---|---|---|---|---|---|---|---|
| max Strahler order | 5 | 5 | 4 | 4 | 4 | 3 | 3 | 3 | 2 |
| order-1 cells on ≥ 2° | 36.7 % | 35.0 % | 35.0 % | 36.0 % | 36.1 % | 35.5 % | 34.3 % | 32.9 % | 30.8 % |
| highest order on ≥ 2° | 7 % | 4 % | 3 % | 2 % | 0 % | 2 % | 0 % | 0 % | 3 % |

**Q5 by the rule fixed in advance: no threshold passes** (order-1 streams ≥ 50 % on ≥ 2°): about two thirds of the
first-order network lies on ground under 2°. The maximum order rises about **one per tenfold** fall in the threshold:
**the channel order is a parameter, not a measurement.** The higher orders lie on flat ground (trunk routing across
the plateau, §25.2). **[V]**

### 47.5 Where the hypotheses stand

H1 not supported at 1:20 M (retest on digitised margins); H2 not supported at stage 1 (§51.1; stage 2 on reviewed
channels); H3 not supported; H4 answered by a different method (§28.11); Q5: no DEM-supported order count. The table
is `INTERIM-PLAN.md` §5.

## 48. The interim rebuilt with T5–T7, and four presentation faults fixed — 2026-10-08 **[V]**

Result slides per test from `build\make_fig_tests567.py` (`interim_img\t5_margins.png`, `t6_stability.png`,
`t7_orders.png`, from the tests' own logs; the validated colour pair, CVD ΔE 24.7, contrast ≥ 3 : 1). Faults found by
reading the rendered pages:

1. **A double rounding:** the T1 slide said κ 0.52 for terrain alone, its own chart 0.51; the log holds **0.5148**.
   **Round from the log's full precision, never from a rounded value here.**
2. Narrow table columns wrapped numbers; 3. takeaway lists broke across pages (now kept with their figure);
   4. tall images pushed their source line off the page (capped at 6 in).

**A limit of `verify_interim.py`, measured:** a planted 27.93 % fails it, a planted 23.4 % passes because 23.4 occurs
elsewhere here. **Check every new slide number by hand against its own section.**

## 49. Two sheets: T8 against the geologic map (layout 13) and the validation sheet (layout 14) — 2026-10-08 **[V]**

- **Layout `13_geomap_check`** (`build\make_geomap_sheet.py`): the classification over hillshade with the SIM 3292
  contacts and volcanic groups outlined; below, T8's enrichment table for all 12 unit groups as native layout
  elements (editable in Pro), every number from `logs\geomap_check.json` (the groups shown cover 96.9 % of the area).
  On the published map since §57.1.
- **Layout `14_validation`** (`build\make_validation_sheet.py`), maps "Ius Chasma — validation" and "Athabasca Valles
  — validation": every candidate by review state, the accepted copies (`SourceID`), the hand-drawn misses (no
  `SourceID`), lava margins, `Ref_Craters_Robbins2020`; definition queries, so the maps follow the review live. The
  table, per window and class: candidates, accept / reject / unsure / not reviewed, **precision = accept ÷ (accept +
  reject)**, drawn by hand, **recall = accepted copies ÷ (accepted copies + drawn by hand)**, and the Robbins recall /
  precision at ≥ 1 km (§42.3). Writes `logs\validation.json`.
- **After each review session:** `make_validation_sheet.py --tally` only reads (Pro may be open) and prints the table;
  without it (Pro closed) it rebuilds the maps and the sheet; then `polish_layouts.py`.
- The tally was tested on planted data: **21 / 21** expected counts; with the window test disabled, **5 checks failed**.
- `build\layoutkit.py` gained `rect()` and `cell_text()` for table cells.

## 50. Every open decision answered; housekeeping deletions; a training-split deep-learning export — 2026-10-09 **[V]**

| decision | answer | consequence |
|---|---|---|
| D2 rubrics | **no rubric exists** for the interim or the final | `NEXT-STEPS.md` §7 is the figure list; the interim stays a living build (D11) |
| D7 / q23 class schema | **the labels' order**: 1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground | `Composite Object Classes.ecs` superseded; nothing recoded |
| D7 / q25 deep learning | **yes, on the corrected stack** | desktop job X5, scored on the §31.3 held-out polygons |
| D7 / q26 label format | **boxes**, as exported (PASCAL VOC) | whole-chip boxes on area classes are a limit to report |
| D7 / q27 smoothing | **keep 5 × 5** | superseded by §57 |
| D9 housekeeping | **delete**, item by item after an inventory | §50.1 |
| D13 / q17 plateau candidates | **keep; reject in review** | the rejections become layout 14's precision |

### 50.1 The deletions (D9)

`build\housekeeping_d9.py` (dry run first; refuses unless every precondition holds): **the 9 `_2` / `_3`
nomenclature copies** (each compared with its original on fields, CRS, attributes and coordinates and found
identical; the comparison was shown to fail on a 10⁻⁶° move), **`Line`, `Point`** (0 rows), **the two first
`_60_smoke` classes**, and **the map "mars"** (only the broken HiRISE layer; `.mapx` exported first). Copies of all 13
classes: `C:\Users\Loggg\Mars_deleted_2026-10-09\` (laptop internal disk). **`<drive>\_removed_not_Mars\`** (711 MB)
went to the Recycle Bin. Two `verify_all.py` checks whose evidence was deleted were **retired, not made to pass**:
**37 / 37**.

### 50.2 The deep-learning export, redone from the training split (q25)

The §31.4 export holds the held-out polygons too. `make_global60_dl_export.py --train-only` makes the same export
from `_60_train` (329 polygons) into **`Mars Project\LabeledObjects\global60_svm_stack_200m_train\`**, 488 s:

| class | chips | boxes |
|---|---|---|
| Crater | 1,404 | 1,968 |
| steep/windy hills | 171 | 329 |
| lava tube | 159 | 292 |
| Normal Ground | 1,983 | 2,704 |
| **all** | **3,622** | **5,293** |

**X5 trains on the `_train` folder only.** Chips near a block edge may show held-out ground as unlabelled context,
never as a label.

## 51. T4 stage 1 (H2), the desktop-day preflight, the deep-learning script, a locator fix — 2026-10-09 **[V]**

### 51.1 T4, stage 1: do the two windows' channels separate on gradient and thermal response? (H2)

`build\make_t4_channel_h2.py`, `logs\t4_channel_h2.json`; chart `make_fig_t4.py` → `interim_img\t4_channels.png`.
H2: fluvial channels have shallower gradients than volcanic ones, and the two separate on gradient against thermal
response. Stage 1 uses the window as a stand-in for origin (Ius fluvial / collapse, Athabasca volcanic). Gradient =
straight-line drop over the routed length on the 100 m DEM; thermal = `ThermIdx` as a z-score against 200,000
background pixels of the window's own index; intervals by bootstrap over 50 km cells; AUC 5-fold cross-validated.

| | Ius Chasma | Athabasca Valles | difference, 95 % interval | AUC: gradient / thermal / both |
|---|---|---|---|---|
| all candidates ≥ 1 km (2,588 / 3,272) | median 10.2 m/km | 1.4 m/km | −8.85 [−15.69, −5.76] m/km; thermal d −0.02 [−0.12, +0.08] | 0.81 / 0.50 / 0.81 |
| Strahler order ≥ 2 (1,009 / 1,803) | 3.8 m/km | 0.9 m/km | −2.87 [−4.87, −1.91] m/km; thermal d −0.08 [−0.20, +0.04] | 0.76 / 0.53 / 0.77 |

- **H2 not supported at stage 1**: the volcanic window's channels are **shallower**, and neither window's candidates
  differ from their background on the index (mean z +0.04 and +0.03). What separates the windows is the window
  itself (chasma walls against lava plains), so stage 1 cannot settle H2.
- **Stage 2** runs on reviewed channels with `Origin` set, once ≥ 10 fluvial and ≥ 10 volcanic exist; the script
  reports it waiting, and the comparison by `Origin` is still to be written (`NEXT-STEPS.md` §3).

### 51.2 `desktop_check.py`: the desktop preflight

One command: the three junctions, with `--gpu` the q10 test (`arcpy.ddd.Slope` with `CPU_ONLY` then `GPU_THEN_CPU`;
`arcpy.sa.Slope` returns no messages and once called the laptop's integrated graphics "engaged": a false positive
caught on a known negative), and X5's preconditions (the Deep Learning Libraries: `torch`, `torchvision`, `fastai`,
`arcgis.learn`).

### 51.3 `make_dl_model.py`: X5 written, its scorer tested

`--train` (training-split chips only; refuses unless the preflight says ready), `--detect` (around the 183 held-out
polygons, 25 km mask), `--score <layer>`. Parameter names checked against Pro 3.7's signatures; **train and detect
have never run**, and which detection models accept 7-band input is not verified **[?]**. **The score is per
polygon**: recall = share of held-out polygons whose own class's boxes cover ≥ 50 % of them; precision = of the
boxes centred in a held-out polygon, the share with its class. Tested: true envelopes score 1 and 1, rotated classes 0.

### 51.4 Layout 10's type-area labels

Placed around the polygon (Maplex `HorizontalAroundPolygon`) with a dark halo.

### 51.5 The interim rebuilt

A T8 slide drawn as a chart (`make_fig_t8.py` → `interim_img\t8_enrichment.png`) because the whole of layout 13 is
unreadable on a slide; a T4 slide. Faults found by reading: a whole tall layout on a slide, a title over ~60
characters wrapping onto the accent rule, a 14th log row running off the slide (the log table holds 13 rows).
Rendering: the deck through PowerPoint (`render_pdf.ps1`), the report through Word COM; rasterise with PyMuPDF.

## 52. Ready for the move to the desktop: a final audit, two transfer defects fixed, the handoff — 2026-10-09 **[V]**

- **The `.aprx` opened through another drive letter** (`subst W: Z:\`): **2 layers held an absolute `Z:\` path**, the
  THEMIS panels of layout 08, added from a band path (`global60_svm_stack_200m.tif\day_ir`), which Pro stores
  absolute. `make_mosaic_layout.py` now adds the whole stack and selects the band in the stretch colorizer; layout 08
  renders pixel-identical.
- **`audit_record.py`** looks for the memory folder of the current drive letter (`<home>\.claude\projects\<letter>--\memory`,
  or `MARS_MEMORY_DIR`) and prints SKIP, not pass, where a machine has none.
- **`HANDOFF-DESKTOP.md`** (beside this file) is the operating guide; **`<drive>\CLAUDE.md`** points an agent at the
  drive root to it. The laptop's agent memories are mirrored read-only to the knowledge vault
  (`memory\loggg\z-drive\`); the desktop keeps its own.

## 53. The first desktop session: pyramids, q24 answered, what the desktop lacks — 2026-10-13 **[V]**

### 53.0 The desktop as found

- **ArcGIS Pro 3.7 is on `D:\ArcGISPro\`**: its Python is `D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe`.
- **The Deep Learning Libraries are absent on both machines** (X5 preflight, `logs\desktop_check_DESKTOP-PJS73RO.json`).
  The training-split export is intact (3,622 chips).
- **The system Python** is 3.13 (`py`; `python` is the Microsoft Store stub). `python-pptx`, `python-docx` and PyMuPDF
  were installed in §53.3.
- **Free space:** ~32 GB on `C:`, ~1.4 TB on `F:`. **The agent's shell refuses `rmdir` on the junction paths**, so
  junctions are retargeted in place (§53.3).

### 53.1 X4: pyramids on the four sources (§11 q6)

`arcpy.management.BuildPyramids`, defaults, one at a time (`logs\x4_pyramids_DESKTOP-PJS73RO.json`):

| source | time | `.ovr` |
|---|---|---|
| THEMIS night IR v14 | 6 m 56 s | 4.27 GB |
| HRSC/MOLA DEM | 4 m 09 s | 1.87 GB |
| Viking MDIM 2.1 | 5 m 03 s | 2.79 GB |
| THEMIS day IR v12 | 9 m 58 s | 6.09 GB |
| **all four** | **26 m** | **15.0 GB** |

**Measured benefit** (`logs\x4_pyramid_timing.json`): a 1/32-resolution read of a full-width 4,096-row strip of the
night mosaic takes 0.03 s with the overviews and 1.01 s without, ~34×. Panning in Pro is the author's to judge.
`verify_all.py` now asserts the external `.ovr` (37 / 37); `paths.arcgis_python()` reads Pro's install folder from the
registry.

### 53.2 X6: what made the 29 Sep map blocky (§11 q24)

The classifier definitions:

| | 29 Sep (`ClassDefinitions_202609290010404137400.ecd`) | 30 Sep (`…300147338582547.ecd`) |
|---|---|---|
| input | `Segmented_202609290011302066080` (3 bands) + Night IR | `CompositeBand`, 7 bands, pixel-based |
| training | `new training.shp`, ≤ 500 samples per class | same |
| RBF γ / cost C | **11.31** / 32,768 | 0.5 / 11,585 |
| support vectors | **1,845** (of ≤ 2,000 samples) | 542 |
| `CrossValidationRate` | **0.391** | 0.881 |

The 29 Sep model memorised its samples (a narrow kernel, nearly every sample a support vector), so it is sensitive to
small input changes **[E]**. **The test** (`build\test_q24_tiles.py`, prediction and rule first; logs
`q24_tiles.json`, `q24_tiles_aligned.json`): the same `.ecd` and inputs rerun over an 8,192 px window.

| run | agreement with the original | jump at the original tile column | jump at the rerun's own tile column |
|---|---|---|---|
| window offset half a tile (2,048 px) | 87.6 % away from tile lines | original **43.0×**, rerun **1.17×** | original 1.83×, rerun **22.2×** |
| control: window aligned with the original tiles | **99.9995 %** | — (the lines coincide) | — |

**q24: the 4,096-px blocks are `ClassifyRaster`'s processing tiles over the segmented input**: the seam moves with the
window. Which step inside the tool makes neighbouring tiles differ is not known **[?]**. Run 1's own rule was
mis-specified and gave no verdict; it was not changed afterwards, and a control with its own rule was run instead.
**For any GUI `ClassifyRaster` over a segmented raster larger than one tile, check for 4,096-px seams first** (§30.2's
jump ratio). The 29 Sep map stays unusable.

### 53.3 X0, X1 and the fine-pass smoke test

- **X0:** `build\retarget_junction.py` rewrites a junction's reparse point in place (`FSCTL_SET_REPARSE_POINT`),
  removing nothing; it refuses unless the path is a junction and the target exists. All three now point at `F:`.
- **X1: the GPU engages** (§2.3): `CPU_ONLY` 7.63 s, `GPU_THEN_CPU` **2.77 s**, *"WARNING 010453: The GPU being used is
  connected to your display ..."*; NVIDIA GeForce RTX 2080 Ti, 11 GB, driver 596.36. **[V]**
- **X2 smoke** (6 m 50 s): **5,144 basins ≥ 20 km** as in §28.11; tile 1 gives **816** crater and **1,425** channel
  candidates, identical to the laptop's run. Four tiles, 8,098 craters and 5,305 channel segments, recreated the
  `_60_smoke` classes (D14).
- **A scratch leak fixed:** each tile's clean-up ran while arcpy still held its rasters (~15 GB over 70 tiles against
  ~30 GB free); `make_global_landforms.py` now empties every checkpointed tile's folder when the next tile starts.
- **The full fine pass runs without `--skip-coarse`**, which would drop the coarse-only basins (wider than the halo)
  from the merged crater class.
- **X5 install prepared:** `ArcGIS_Pro_37_Deep_Learning_Libraries_200060.zip` (6,398,596,251 bytes) from
  `gisupdates.esri.com`, in `D:\MarsDownloads\dl_libs_37\`; every CRC ok; `ProDeepLearning.msi` Authenticode-signed by
  Environmental Systems Research Institute, Inc. (DigiCert), Valid. Install only when no job runs from `arcgispro-py3`.
- `python-pptx` 1.0.2, `python-docx` 1.2.0, `PyMuPDF` 1.28.2 installed for the system Python (`pip --user`).

### 53.4 X2 done: closed depressions and channels at ±60° — 2026-10-14 **[V]**

`make_global_landforms.py`, coarse pass then 70 fine tiles, **11 h 07 min** on the desktop (tiles 45.7–884.9 s;
`logs\landform_fine_DESKTOP-PJS73RO.log`). **Superseded at 180° by the rerun of §54.4: the current counts are 465,354 and
969,822.** Run 2's figures, as measured:

| class | rows | what |
|---|---|---|
| `Landform_CraterCandidates_auto_60` | 467,547 points | closed depressions ≥ 1 km: 467,224 fine-pass + 323 coarse-only (≥ 20 km) |
| `Landform_ChannelCandidates_auto_60` | 973,879 polylines | median 4.2 km; orders 1–5: 567,384 / 361,681 / 41,547 / 3,170 / 97 |

Fill-artefact discard **60.1 %** of stream cells. `MappedOn` had been a hard-coded 2026-09-19; set to each run's date,
and the script now uses the run's date.

**Checked** (`build\verify_global60_candidates.py`, predictions and rules first; `logs\global60_candidates_check.json`):
counts, CRS, geometry and filters hold (D ≥ 1.009 km, aspect ≤ 2.000, fill ratio ≥ 0.550); **tile seams clean**
(density across core seams 0.985 / 0.961 of half a core away; near-duplicates 0.0000 at seams, 0.0002 elsewhere); the
type-area windows reproduce §42.3 (Ius **1,709** at 200 m, Robbins recall **20.5 %**, precision **11.1 %**; Athabasca
**1,819**, recall **37.2 %**, precision **12.1 %**). **Against Robbins over ±60°** (the §42.3 rule; the chance baseline
shifts each candidate east by 3 of its own diameters, after a 2° shift proved too small for large craters):

| D ≥ | Robbins | recall (baseline) | candidates | precision (baseline) |
|---|---|---|---|---|
| 1 km | 352,796 | 20.5 % (1.1 %) | 467,547 | **15.3 %** (0.8 %) |
| 2 km | 118,124 | 36.0 % (1.7 %) | 142,902 | 29.3 % (1.4 %) |
| 5 km | 43,049 | 46.0 % (2.9 %) | 31,043 | **62.2 %** (4.0 %) |
| 10 km | 21,990 | 48.0 % (4.2 %) | 12,838 | 79.2 % (7.1 %) |
| 20 km | 9,784 | 48.3 % (5.7 %) | 5,400 | **83.0 %** (10.2 %) |
| 50 km | 1,857 | 46.1 % (5.5 %) | 1,025 | 78.5 % (9.9 %) |
| 100 km | 269 | 39.0 % (4.5 %) | 145 | 69.0 % (8.3 %) |

**Below ~2 km most candidates are not catalogued craters; from ~5 km up most are. Recall levels off near half**: breached
and degraded craters stay invisible (§26.3). The ≥ 100 km recall (39 %) and §28.11's 68 % measure different things (every
Robbins crater against named IAU craters, with different match rules). Run 3's precisions (§54.4) differ by ≤ 0.1 pt.
**The class remains "closed depressions ≥ 1 km", not a crater inventory.** The channel class has no reference at ±60°
and is not scored.

### 53.5 X5: the install needs an administrator

Run elevated, the UAC prompt went unanswered; unelevated it ends with **Error 1925** (a per-machine install), before any
file was written. Open: one approved UAC prompt for `D:\MarsDownloads\dl_libs_37\extracted\ProDeepLearning.msi`, or
Esri's conda route into a cloned environment (no admin; Esri calls that package set uncertified).
**Closed 2026-10-19:** installed elevated with the author at the screen (§66).

### 53.6 Layouts 11 and 12, and what reading them found — 2026-10-14 **[V]**

`build\make_global60_candidate_sheets.py` (`logs\global60_candidate_sheets.json`): **layout `11_global60_depressions`**,
closed depressions and Robbins craters ≥ 1 km per 0.5° cell of true spherical area (`Global60\global60_depression_density_0p5deg.tif`,
`global60_robbins_density_0p5deg.tif`, 720 × 240, Int16 per 10⁴ km²) with the §53.4 table and the blind spots;
**layout `12_global60_channels`**, Strahler orders 3–5 over the ±60° hillshade (orders 1–2 not drawn). Rebuilt from run 3
in §55.4.

**Found by reading the first export, not by any check:**

1. **The detector's density does not follow the craters**: log-density r **−0.11** over cells with any count. By 30°
   band it is nearly flat (33, 35, 40, 38 per 10⁴ km² from 60°N to 60°S) while Robbins' doubles (18, 25, 37, 29).
2. **North–south stripes and blocks** fill the detector's map, strongest in small candidates: detector against Robbins
   in the same size class by 1° cell, r **0.34** (1–2 km), **0.31** (2–5 km), **0.56** (≥ 5 km). **Small closed
   depressions gather where the HRSC/MOLA blend is sharp** (HRSC strips run north–south; an inference **[E]**, no source
   mask is held). **Below ~5 km the detector's density maps the DEM's resolution as much as the craters; never compare
   regions with it.**
3. **The channel network follows the DEM's makeup inversely**: order ≥ 3 length per 1° cell against 1–2 km depressions
   r **−0.36**; where the DEM holds many pits the fill mask breaks the network, and long high-order paths gather on
   smooth ground. Real terrain and DEM sharpness are not separated **[E]**.

**`tasklist` can hang** for minutes inside a builder's "Pro is closed" check (0 % CPU, a stuck `tasklist.exe` child):
confirm Pro is closed another way, then stop that child.

## 54. The 180° stripe: the DEM's edge column, patched; the 200 m map and X2 redone there — 2026-10-14/15 **[V]**

**Found** in the 200 m and 400 m maps: a 10 px (2 km) stripe of excess Crater / hills / lava tube along 180° (G200 x ≈ 0),
column change rate 0.26–0.28 against ~0.10. Traced to G200 column **53346** of `global60_dem.tif`: nodata in 24,335 of
35,565 rows, wrong values elsewhere; slope 13–16× rougher at 53345–53348, relief 2–9× at 53342–53351, and the stack's 7
bands nodata at 53342–53350.

### 54.1 Cause: the source, not the warp

The source DEM is 106,694 px of 0.003374120830641° = **359.99845°**, 0.46 px (≈ 92 m) short of +180°, and its **last
column** (src 106693) is the bad one: nodata in the same 24,335 rows, elsewhere off its neighbours by median −4.5 m, p95
92.5 m. `global60_dem.tif` is exactly the rolled source (0 mismatches over 8 full rows), and the roll puts src 106693 at
G200 53346. No other DEM is held.

### 54.2 The fix (option A of three, the author's choice: mean / copy nearest / nodata)

- **`make_global_terrain.py`:** `patch_meridian()` sets col 53346 to the round-half-up mean of cols 53345 and 53347 (src
  106692 and src 0, both real), metadata `MERIDIAN_PATCH`; a full build runs it after the warp. **`--meridian-only`**
  patches an existing DEM and recomputes slope / aspect / hillshade in a 33-column window, **after proving the window
  reproduces each full-raster file bit for bit**; only cols 53345–53347 change; the `.ovr` refreshed over them
  (`gdaladdo --partial-refresh`). Log `logs\global_terrain_meridian.log`.
- **`make_global60_svm_stack.py --patch-cols 53342 53350`:** those columns recomputed with the stack's own code and the
  **stored** stretch: `STRETCH` holds 3 decimals, so the slope p99 was recomputed exactly as before, **17.7923641204834**
  (`EXACT_LIM`); a full rerun would have restretched the whole band and changed the map everywhere. Gated: margin columns
  identical, bands 1–5 identical inside wherever valid. Nodata there 219,384 → 3,093 px.
- **Residual, from the source:** slope at col 53346 averages 2.07° against ~1.45° (+40 %); the two real pixels either side
  of 180° are 2.46 px apart, not 2. `check_meridian_columns.py` (≤ 2× local roughness) fails before (48×) and still after
  (7.4×): no fill of one column removes it.
- Rollback copies of every touched pixel: `%LOCALAPPDATA%\Temp\mars_scratch\meridian_backup_20261014\`.

### 54.3 The 200 m map: tile column c03 reclassified

The three classify tiles holding col 53346 reclassified and re-mosaicked (`--classify-only --cell 200`, 1 h 19 min).
`check_landform_columns.py` reproduces the checks that found the stripe:

| | before | after |
|---|---|---|
| change rate, cols 53340–53355 (reference 0.0999 ± 0.0060) | 0.078–0.279, max z **+29.8** | 0.078–0.117, max abs z **3.6**: **pass** |
| tile seams every 16384 px, abs z | ≤ 1.27 | ≤ 1.27: **pass** |
| no-class pixels there | 221,767 | 5,476 |

The maps before and after differ **only** in cols 53342–53350. **The 400 m map still carries the stripe** (superseded, §57.2).

### 54.4 X2 over x = 0: rerun on the five tiles **[V]**

**Before** (`check_x2_meridian.py`, within 60 km of x = 0): a ~16 km deficit of closed depressions, channel end points ~4.8×
normal, 28 polylines straddling x = 0 against 176–215 at control offsets: the column cut the network. **Rerun** of the five
fine tiles whose core + halo holds col 53346 (006, 020, 034, 048, 062), the other 65 and the coarse pass reused; 1 h 01 min;
both classes backed up first to `C:\MarsScratch\global60\pre_meridian_20261014\x2_pre.gdb`.

- **Counts now: 465,354 closed depressions (465,030 fine + 324 coarse-only) and 969,822 channel segments**; fill-artefact
  discard 60.5 %.
- **x = 0 after:** crossings **150** against 133–167, fixed; channel ends ~1.8× normal; the depression dip half filled
  (0.48 of the reference) and **still abnormal** against 208 control meridians (median 0.99, min 0.70). **Why it is left:
  the source blend is smoother there** (north–south roughness 0.80–0.84 of its surroundings), and the small depressions
  follow DEM sharpness (§53.6). **[E]**
- **Far from x = 0, a real change of drainage:** tiles 048 and 062 lost 2,156 and 239 small depressions at 166–193°E,
  30–45°S (Eridania, a known closed basin) and 176–189°E, 51–57°S. The nodata column had been an outlet; now closed, those
  regions fill as basins and swallow their pits, as every closed basin does under the fill-depth rule.
- `verify_global60_candidates.py` run 3: **12 checks, 0 failed**; seams **0.990** / **0.979**; Robbins precision 15.3 / 29.2 /
  62.2 / 79.2 / 83.1 % at ≥ 1 / 2 / 5 / 10 / 20 km; the type-area windows unchanged (1,709, 1,819).
- **Run 3 by Strahler order** (from `logs\global60_candidate_sheets.json`, §58.2): **564,882 / 360,236 / 41,442 / 3,165 /
  97** (orders 1–2 together 925,118), 6.17 million km in all; of 40,410 sampled midpoints **89.8 %** lie on ground under 2°,
  **96.7 % of order 3 and up**. **Plateau channels are DEM noise**; say so on any sheet built from them.

### 54.5 Left stale near 180°, and since resolved

The 400 m map stays stale (superseded, §57.2); layouts 11–12, the density rasters and the DEM statistics were brought
current in §55.1 and §55.4.

## 55. X3 scored, the stack swept for line artefacts, layouts 11 and 12 rebuilt, T1 in Pro started — 2026-10-15 **[V]**

### 55.1 Checks after the 180° fix

- `verify_global60.py`: 6 pass, 0 fail (27 / 27 since §58.1 extended it).
- The 200 m map, whole raster: every seam |z| ≤ 1.3; values 1–4 and 255 only; nodata 2.659 %; shares Crater 31.52 / hills
  2.53 / lava tube 10.44 / Normal 55.51 %; col 53347 change rate 0.117 (z 3.9, within the map's own top ten): the §54.2
  residual, not a stripe. Agreement with the 400 m map: **92.10 %**.
- **No hand-drawn polygon lies within 1° of 180°** (nearest −166.2°): the SVM was never trained or scored on the bad
  column; the model and held-out scores stand.
- Feature density at 180° against other meridians, every gdb class ≥ 500 rows: only the two X2 classes deviate, and after
  the rerun they sit inside the control meridians' range.
- `.aux.xml` statistics recalculated on the DEM (−8528..21226 m, mean −541.47), slope (0..82.40°, mean 2.191), aspect and
  hillshade.

### 55.2 The 7-band stack swept for line artefacts

Every row and column of all 7 bands, adjacent-column (row) differences against a ±64 running median (robust z > 8): **no
second defect like §54.**

| where | bands | what | size |
|---|---|---|---|
| col 53347 (180°) | Viking R, G, B | brightness step: the Viking source's own edge | 1 px |
| cols 17782 (60.0°E), 88912 (300.0°E) | night, day IR | one unusually smooth column pair: THEMIS tile joins | 1 px |
| first / last 4 rows (±60°) | relief | the 9 × 9 window truncated at the grid edge | 0.8 km each edge |
| cols 0–7, last col | Viking | smoothed / duplicated at the 0°/360° edge | ~5 px |
| cols 18333, 88163, 90211, 102499; row 22230 | slope, relief | DEM steps 2.2–4× local roughness, ~500 km long | — |

Image chips at each DEM step: `Mars Project\Global60\checks\dem_step_chips_20261015\`. **297.5°E is a real escarpment**; the
others are seams and smoothed gap-fill strips of the HRSC/MOLA blend (345.8°E at 39°N, 304.4°E at 5°N, 61.9°E, −15.0°).
None is fixable here.

### 55.3 X3 scored: the 200 m map and its majority filters

`verify_global60_classification.py --cell 200` (it reads the 400 m overview level), then `--raster` per filter;
`make_global60_landforms_clean.py --cell 200 --size 3 5 7 9 11`. Held-out, 183 polygons (one class everywhere 0.586):

| map | 200 m acc / κ | 400 m acc / κ (§32.2) |
|---|---|---|
| raw | **0.699 / 0.532** | 0.705 / 0.540 |
| 3 × 3 | 0.710 / 0.546 | 0.723 / 0.562 |
| 5 × 5 | 0.720 / 0.560 | 0.735 / 0.578 |
| 7 × 7 | 0.728 / 0.569 | 0.743 / 0.589 |
| 9 × 9 | 0.734 / 0.577 | 0.751 / 0.599 |
| 11 × 11 | **0.738 / 0.583** | — |

Raw 200 m: producer's Crater 0.543, hills 0.608, lava tube 0.376, Normal 0.991; polygons won 102/124, 14/16, 5/21, 20/22;
training set 0.820 / 0.654; IAU 'Crater' inside 0.513 against ring 0.432 (62.8 %); seam ratios 0.998 / 0.990; elevation
alone 54.9 %. **Halving the cell bought no held-out accuracy**; the same window covers half the ground, so the 200 m maps
trail filter for filter by ~1.5 pt. By §32.2's rule the 2 km window at 200 m is 9 × 9 or 11 × 11: **11 × 11 was chosen
(§57)**. Logs `logs\global60_classification_check_200m*.json`.

### 55.4 Layouts 11 and 12 rebuilt from the post-fix X2

465,354 candidates; r −0.11 unchanged; plateau share 89.8 %; order ≥ 3 against 1–2 km depressions r −0.35. Both density
rasters rewritten; both sheets read. Left as found: on 12 the legend box starts left of the map frame, and "0°E" and "0°"
overlap at the centre.

### 55.5 T1 confirmed in Pro: the runs

`make_t1_pro_confirm.py`: copies band subsets of the stack exactly (`gdal.Translate`), trains Pro's SVM on the same
`_60_train` polygons (max 1000 per class), classifies ±60° with X3's tiling in its own scratch; `--set nothermal |
novisible | terrain`. It writes only `global60_svm_stack_200m_<set>.tif`, `global60_landforms_svm_<set>.ecd` and
`global60_landforms_svm_<set>_<cell>m.tif`. **Training took 2861 s** (Pro computes the new stack's statistics first)
and the ±60° classification at 200 m 6 h 28 min (§56). The queue (`t1_queue.ps1`) scored each with
`verify_global60_classification.py --cell 400 --raster`. Results: §56.

## 56. T1 confirmed with Pro's SVM at 200 m: the thermal bands add +1.4 pt — 2026-10-15 **[V]**

Run 1 (200 m without thermal) classified in 6 h 28 min, scored like the all-band map (§55.3), and bootstrapped by
`score_t1_bootstrap.py` (paired, whole held-out polygons, 1,000 resamples, seed 60, as §40.1; it reproduces verify's
0.699 / 0.532 and 0.720 / 0.560 exactly).

| 200 m, raw, held-out (183 polygons) | all 7 bands | without thermal | difference, 95 % CI |
|---|---|---|---|
| accuracy | 0.699 | 0.685 | **+1.36 pt** [+0.46, +2.47] |
| kappa | 0.532 | 0.516 | **+0.016** [+0.005, +0.026] |
| producer's: Crater / hills / lava tube / Normal | 0.543 / 0.608 / 0.376 / 0.991 | 0.524 / 0.553 / 0.461 / 0.993 | |
| polygons won: Crater / hills / lava tube / Normal | 102 / 14 / 5 / 20 | 93 / 11 / 13 / 20 | of 124 / 16 / 21 / 22 |
| training set accuracy / kappa | 0.820 / 0.654 | 0.818 / 0.650 | |
| IAU craters: 'Crater' inside vs ring | 0.513 vs 0.432 (62.8 %) | 0.468 vs 0.425 (55.8 %) | |
| seam ratios; elevation alone reproduces | 0.998, 0.990; 54.9 % | 0.997, 0.996; 54.4 % | |

- **T1 holds with Pro's SVM**: the same size and sign as §40.1's +1.3 pt [+0.6, +2.2]; both intervals exclude zero.
- **Not uniformly:** thermal helps Crater (+1.9 pt producer's, 9 more polygons won, IAU craters read as Crater more often)
  and hills (+5.5 pt), and **hurts lava tube** (−8.5 pt; 5 of 21 polygons won with it, 13 without). Read the gain as
  coming from crater and hill terrain, not from lava. Logs `global60_classification_check_nothermal_200m.json`,
  `t1_bootstrap_200m_vs_nothermal_200m.json`.

### 56.1 The 400 m band sets — 2026-10-15/16 **[V]**

Each set's `.ecd` (trained on the 200 m stack) classified on the 400 m lattice, against `global60_landforms_svm_400m.tif`.
That map predates §54, but no training or held-out polygon lies within 1° of ±180°, so the stripe cannot enter these
scores. **Two Pro runs at once are safe** when each has its own inputs, model, scratch folder and logs (`*_lane2_*`).

| 400 m, raw, held-out (183 polygons) | all 7 bands | without thermal | difference, 95 % CI |
|---|---|---|---|
| accuracy | 0.705 | 0.685 | **+1.97 pt** [+1.08, +3.35] |
| kappa | 0.540 | 0.516 | **+0.024** [+0.013, +0.037] |
| producer's: Crater / hills / lava tube / Normal | 0.553 / 0.606 / 0.394 / 0.991 | 0.524 / 0.554 / 0.464 / 0.993 | |
| polygons won: Crater / hills / lava tube / Normal | 103 / 14 / 4 / 20 | 93 / 11 / 12 / 20 | of 124 / 16 / 21 / 22 |
| training set accuracy / kappa | 0.828 / 0.670 | 0.817 / 0.649 | |
| IAU craters: 'Crater' inside vs ring | 0.525 vs 0.443 (61.8 %) | 0.467 vs 0.424 (55.7 %) | |
| seam ratios; elevation alone reproduces | 1.002, 0.995; 54.6 % | 0.991, 0.988; 54.4 % | |

| 400 m, raw, held-out (183 polygons) | all 7 bands | without visible | difference, 95 % CI |
|---|---|---|---|
| accuracy | 0.705 | 0.747 | **−4.26 pt** [−10.96, +2.18] (83 % of resamples favour no visible) |
| kappa | 0.540 | 0.600 | −0.060 [−0.138, +0.016] |
| producer's: Crater / hills / lava tube / Normal | 0.553 / 0.606 / 0.394 / 0.991 | 0.596 / 0.864 / 0.241 / 0.993 | |
| polygons won: Crater / hills / lava tube / Normal | 103 / 14 / 4 / 20 | 84 / 16 / 1 / 18 | of 124 / 16 / 21 / 22 |
| training set accuracy / kappa | 0.828 / 0.670 | 0.815 / 0.636 | |
| IAU craters: 'Crater' inside vs ring | 0.525 vs 0.443 (61.8 %) | 0.509 vs 0.481 (53.0 %) | |
| seam ratios; elevation alone reproduces | 1.002, 0.995; 54.6 % | 1.018, 1.021; 56.4 % | |

| 400 m, raw, held-out (183 polygons) | all 7 bands | terrain only | difference, 95 % CI |
|---|---|---|---|
| accuracy | 0.705 | 0.708 | −0.30 pt [−6.54, +7.73] (47 % of resamples favour terrain only) |
| kappa | 0.540 | 0.551 | −0.012 [−0.092, +0.071] |
| producer's: Crater / hills / lava tube / Normal | 0.553 / 0.606 / 0.394 / 0.991 | 0.528 / 0.857 / 0.292 / 0.995 | |
| polygons won: Crater / hills / lava tube / Normal | 103 / 14 / 4 / 20 | **34** / 16 / 3 / 19 | of 124 / 16 / 21 / 22 |
| training set accuracy / kappa | 0.828 / 0.670 | 0.803 / 0.612 | |
| IAU craters: 'Crater' inside vs ring | 0.525 vs 0.443 (61.8 %) | 0.445 vs 0.441 (**47.1 %**) | |
| seam ratios; elevation alone reproduces | 1.002, 0.995; 54.6 % | 1.020, 1.024; 57.7 % | |

**T1 in Pro, all four comparisons** (the difference is "all 7 bands minus the set"):

| cell | band set | accuracy / κ | all bands minus set, accuracy [95 % CI] | resolved? |
|---|---|---|---|---|
| 200 m | without thermal | 0.685 / 0.516 | +1.36 pt [+0.46, +2.47] | yes |
| 400 m | without thermal | 0.685 / 0.516 | +1.97 pt [+1.08, +3.35] | yes |
| 400 m | without visible | 0.747 / 0.600 | −4.26 pt [−10.96, +2.18] | no |
| 400 m | terrain only | 0.708 / 0.551 | −0.30 pt [−6.54, +7.73] | no |

- **The thermal gain is the one difference resolved at both cells.** It is a little larger at 400 m because the all-band
  map scores higher there; the map without thermal scores the same at both.
- **Dropping the visible bands, or both spectral groups, leaves the area-weighted score unchanged within wide intervals**,
  as §40.1 found: the hand-drawn classes are landform classes, and the score is carried by a few large hill and crater
  polygons.
- **Per class the sets differ a lot even where the score ties**: the full stack makes the best crater map (103 Crater
  polygons, 61.8 % on the IAU test); terrain only is the best hills map and a poor crater map (34 Crater polygons, 47.1 %).
  **The published maps stay on all 7 bands. T1 is closed.** Logs `t1_bootstrap_*.json`.

## 57. The 200 m map published with an 11 × 11 majority filter; layout 04 rebuilt — 2026-10-16 **[V]**

**The author's decision, 2026-10-16: the published ±60° landform map is the 200 m map smoothed 11 × 11 (2.2 km)**,
`Global60\global60_landforms_svm_200m_mode11.tif`: held-out **73.8 %, κ 0.58** (0.738 / 0.583, §55.3). `make_global60_maps.py`
takes the window from the cell, `CLEAN = {200: 11, 400: 5}[CELL]`; **run it with `--cell 200`** (the default 400 m still
gives the 5 × 5 map). Layout 04 shows it: raw 70 %, κ 0.53; producer's Crater 61 %, hills 63 %, lava tube 45 %, Normal 99 %;
**user's lava tube 2 %**; training 86 %, κ 0.74; elevation alone 55 %; seam ratio 1.00; IAU 'Crater' inside 57 % against
ring 46 %.

**The builder order** when several run (each wipes and rebuilds its maps): `make_global60_maps.py --cell 200`,
`make_candidate_maps.py`, `make_mosaic_layout.py`, `make_reference_maps.py` (graticules back on the maps the first one
wipes), `make_geomap_sheet.py --cell 200`, `make_validation_sheet.py`, `make_global60_candidate_sheets.py`, then
`polish_layouts.py --export`, read, and copy the polished sheets into `Global60\layouts\`.

### 57.1 T8 and layout 13 on the 200 m map; the catalogues — 2026-10-16

**T8 rerun** (`make_geomap_check.py` on the published map at its 1.6 km overview; the JSON names its map, and
`make_geomap_sheet.py` refuses a JSON for another; the 400 m result kept as `logs\geomap_check_400m_mode5.json`). **No finding
changes:** every enrichment moves by ≤ 0.07 except lava tube on aprons, ×4.12 → ×4.29 (lava tube on tu ×1.35 → ×1.28, v
×0.87 → ×0.84, ve ×3.34 → ×3.30; Crater on h ×1.34, i ×1.39; Normal Ground on l ×1.67 → ×1.66, v ×1.38); 76 % of the volcanic
plains come out Normal Ground; class shares 34 / 2 / 9 / 55 %. Layout 13 rebuilt.

- **`github_catalog_rasters.py`** names the published map and the superseded ones, describes every raster (32 in Global60, 0
  undescribed), says "not yet (next release)" for files newer than a release, and flags the five §54-patched files whose
  release copy predates the patch.
- **`github_export_gdb.py`:** the two X2 classes make `.gdbtable` files of 246 and 113 MB, which GitHub refuses (> 100 MB):
  they are **release-only** (`RELEASE_ONLY`), in the GeoPackage (all 26 classes) but not in the repo's `.gdb`; an assert
  stops any file over 95 MB reaching the clone. The hand-drawn labels stay in git.

### 57.2 The 400 m map superseded — 2026-10-16

**The author's decision:** the 400 m map (`global60_landforms_svm_400m.tif` and its filters 3–9) is **superseded by the 200 m
11 × 11 map**, not rerun at 180°, nothing deleted. It stays the 400 m baseline of T1 (§56.1) and of the filter tables (§32.2,
§55.3). In Pro it sits in the group "Superseded: the 400 m map, published to 2026-10-16 (KB §57.2)", off, in "Mars ±60°
Analysis"; no layout shows it.

### 57.3 The interim rebuilt — 2026-10-16 **[V]**

`interim.py` brought to the record (status 16 October; the published map at 73.8 %; 465,354 closed depressions; 14 layouts;
the log at 13 rows; new figures: layouts 11 and 12 and T1 in Pro). `make_fig_t1_pro.py`: the four T1 comparisons from the
`t1_bootstrap_*.json` logs, each a dot with its 95 % interval, resolved in blue, not resolved open grey (validated:
normal-vision ΔE 25, CVD ΔE 21). `make_interim_figs.py` hides layout 11's table and note for the slide. **Deck 28 slides,
report 20 pages, 19 figures**; every changed slide and page read; `verify_interim.py`: all 249 numbers in the record. The
percent-complete column (the author's) and the due date (unknown) are still open. Previous files in `NEXT STUFF\.backup_20261016\`.

### 57.4 GitHub release `data-2026-10-16` — 2026-10-16 **[V]**

`github_export_gdb.py --rasters-only`, then `github_release_bundle.py --upload data-2026-10-16`: **10 assets, 5.9 GB**:
`typearea-part1..3.zip`, `global60-classification-part1.zip` and `-part2.zip` (every landform map and model, 200 m, 400 m and
T1, the two density grids, the smoke tests), `npy-caches.zip`, `mars_project_vectors.gpkg.zip` (the two X2 classes
included), the two `Classified_*.tif`, `SHA256SUMS.txt`; every asset's GitHub SHA-256 matches. `data-2026-10-06` is kept, not
deleted.

- **Not in it:** the three T1 stacks (rebuilt by `make_t1_pro_confirm.py`) and a new derivatives release:
  `derivatives-2026-10-06` stays, and `docs/backup.md` gives the two §54.2 commands that patch its DEM, slope, aspect,
  hillshade and stack after a restore (open decision D15).
- **`restore.py`** takes the newest release of each kind (`--all-releases` for every one): `data-2026-10-16` +
  `derivatives-2026-10-06`, 80.3 GB.
- **Before each deadline:** a new data release, then point `github_catalog_rasters.py`'s `DATA` and `github_export_gdb.py`'s
  `RELEASE` at it, then `tools/check_remote.py` by hand.

### 57.5 Housekeeping: finished scratch to the Recycle Bin — 2026-10-16

Sent to the Recycle Bin on the author's choice (space returns when the bin is emptied, the author's call): the release
staging folder (6.2 GB), the T1 classify tiles, X2's checkpoints, and 15 `build\*_ov400.npy` written by
`verify_global60_classification.py` and read by no script (13.2 GB; a rescore writes one again). **Kept:** the §54 rollback
copies, the two `_60_smoke` classes, the T1 stacks, the interim backup.

### 57.6 The plans and the project page brought to the current state — 2026-10-16

The repo stopped mirroring the parts that only record the past (§35.1). `NEXT-STEPS.md`, `HANDOFF-DESKTOP.md`,
`INTERIM-PLAN.md` and the README were rewritten to the current state, done items removed rather than struck. The README's
usage example reads the published map: shares 32.8 / 1.8 / 9.3 / 56.1 %, the same at a tenth and at full resolution.

### 57.7 Audit of the repository against the project — 2026-10-16

Every tracked text file searched for superseded figures, map names and counts, and every layout export compared pixel by
pixel with its mirrored PNG. Fixed: `Global60\README.md` (the 200 m maps, `_mode11` the published one) and its copy in the
release (`global60-classification-part2.zip` replaced with its `SHA256SUMS.txt` line); layouts 11 and 12's PNGs (the
builder's, from before polishing); `docs/pipeline.svg` ("200 m · 73.8 %"); `CITATION.cff`. ~20 docstrings still give paths
as `Z:\...` while the code finds its drive at run time (§40.2).

## 58. A laptop check-in after the desktop sessions: junctions, the clone, the sync comparison — 2026-10-18 **[V]**

On the laptop; nothing written to the `.aprx`, the gdb or any raster. Nothing on the drive was newer than §57.

- **The drive-root junctions are broken on the laptop**: they target `F:\Mars Project\...` since §53.3. Scripts that call
  `paths.junction()` stop with a message, which now names `retarget_junction.py` with this machine's paths for a broken
  junction (`mklink /J` for a missing one). Not retargeted: each retarget breaks the other machine. A relative directory
  symlink would serve both letters; replacing a junction is the author's call.
- **The laptop's clone was 7 commits behind `origin/main`** (the tree clean); fast-forwarded with `git pull --ff-only`.
  **Fetch and compare before any git work on either machine.**
- **`github_sync.py` reported 94 phantom copies after the pull**: it compared only size and whole-second mtime, and a
  checkout stamps files with the checkout time. It now compares bytes when sizes match and mtimes differ (proved on
  planted files).

### 58.1 The audit continued: the project on the laptop, every ±60° raster, the open questions

- **The `.aprx` opens whole on `Z:`**: 26 maps, 14 layouts, 145 non-group layers (137 on the drive, 7 hosted services, 1
  without a data source), **0 broken**, none through a junction. The broken junctions affect only Spatial Analyst scripts.
- **`verify_global60.py` checks every ±60° raster**: the stack, the six 200 m maps, the five 400 m maps, the three T1 stacks
  and four T1 maps, the two density grids; the five never-built Composite Bands products are reported "ruled out". Two
  lattices are derived from G200: **G400**, the same origin with ceil(n / 2) cells, 53,347 × 17,783 (G200's 35,565 rows are
  odd, so it reaches 200 m past the south edge), and **D05**, G200's exact extent in 720 × 240 cells, not square (29,637.2 m
  across, 29,637.5 m down). **27 pass, 0 fail**; planted mismatches fail.
- §11 brought up to date with what §53–§57 settled.

### 58.2 The audit, third pass: the review tally, X2's run-3 figures, the READMEs, the scripts

- **The review has not started:** `accept_reviewed.py` (dry run) counts 0 accept / 0 reject / 0 unsure in every candidate
  class (Ius channels 2,610, Athabasca channels 3,283, Ius closed depressions 1,685, Athabasca 1,709: **9,287**), and the
  digitising classes hold 0 rows. `audit_record.py` under the ArcGIS Python: **28 feature classes, 15 rasters** (§6).
- No run-2 figure (467,547, 973,879, 60.1 %, 89.9 %) is quoted as current anywhere; layout 12 prints run 3's (now in §54.4).
- **`make_flow_margin_test.py` (T5) is the only after-review script that needs a junction** (`WS = junction(...)` at
  import, though it reads only through `arcpy.Raster` and `RasterToNumPyArray`, which accept spaces). Changing it belongs
  with the T5 rerun.
- The knowledge vault's Mars pages (`Github Knowledge`, a separate repository) still describe the project at §34.

## 59. The record condensed — 2026-10-18 **[V]**

**On request:** remove or trim what is redundant or no longer relevant, and lay the record out so an agent can use it
efficiently. 5,197 lines / 340 KB became a smaller file; the full wording to this date is in git history (commit
`0cf77a6`) and in `.backup_20261018\PROJECT-KNOWLEDGE.md` on the drive.

- **§1–§16 rewritten to the current state** instead of carrying 2026-09-18 claims with "superseded" notes: the machines
  and the GPU (§2), pyramids built and the DEM's bad column (§3), the project's 26 maps and 14 layouts with their builders
  (§5), the gdb as it stands (§6), §11 as two tables, open and answered.
- **§17–§58 kept as the dated log, every `##` and `###` number kept** (scripts and the plans cite them), each section cut to
  its results, numbers, decisions and lessons. Cut: session narration, rehearsal and backup bookkeeping, project counts of
  the day, cosmetic layout faults already fixed, and reasoning that a later section overturned.
- **A "where to look" table** at the top maps each topic to its sections.
- Checked: every number in the condensed file was in the original; every number the plans, READMEs and `interim.py` quote
  is still here (`verify_interim.py`); every `§` reference in the record, the plans, the scripts and the repo's pages
  resolves; `audit_record.py` passes.

## 60. The audit, fourth pass: two scripts tied to `F:`, the docstring paths — 2026-10-18 **[V]**

On the laptop; nothing written to the `.aprx`, the gdb or any raster. The repo and the drive matched before the
pass (`github_sync.py`: 0 copied, 687 unchanged).

- **`check_landform_columns.py` and `check_meridian_columns.py` (§54) hard-coded `F:\Mars Project\Global60`** in
  code, so neither ran on the laptop. Both now build the path with `paths.on_drive()`; imported under the ArcGIS
  Python, each resolves to an existing `Z:\Mars Project\...` path. No other live script hard-codes a drive letter
  (searched for `[A-Z]:\` and `[A-Z]:/` in quoted strings; the `.py_backup_*` folders are snapshots and left as
  they are).
- **The docstrings §57.7 counted:** 12 that gave a location as `Z:\...` now say `<drive>\...` or "the drive".
  Left as written, because they describe what happened on `Z:`: `content.py`, `housekeeping_d9.py`,
  `remove_non_mars.py`, `repoint_junction_layers.py`, the comments in `verify_all.py`, and the example
  command in `retarget_junction.py`.
- The README's "what is in this repository" line now gives the knowledge base's paths as `<drive>\...`.
- Checked current, no change: `HANDOFF-DESKTOP.md`, `NEXT-STEPS.md`, `drive-root/CLAUDE.md`, `Global60\README.md`,
  `docs/backup.md`, `CITATION.cff`, and the generated `exports/README.md`, `docs/rasters.md` and
  `docs/scripts.md` (149 scripts on the drive, 148 in the repo, as §12 says).

## 61. Every sheet read again; layout fixes; the interim rebuilt; the repo's figures indexed — 2026-10-18 **[V]**

On the laptop, ArcGIS Pro closed. Nothing measured changed.

- **All 14 layout exports and the 8 result charts read.** Defects found: on 11 the graticule labels (white, no halo)
  vanished on the light density maps, and were faint on the chasma walls of 01–02; a legend's border is drawn ~0.15 in
  outside its position, so on 12 and 14 it stood left of the map frame and on 03 and 06 it cut into the frame's bottom
  edge; 03's "Graticule 2°" and the "Analysis extent ±60°" entries of 04, 10 and 13 had no visible symbol (the extent
  outline is the frame edge); 07's IAU entry printed its name twice; 14 said "Read 2026-10-08".
- **Fixed in `polish_layouts.py`**, so a rebuild keeps them: a dark halo (RGB 40, 1.2 pt) on every graticule label
  class (14 layers), the four legends moved, the symbol-less entries dropped from the legends (the layers kept), 07's
  IAU entry named once. Rehearsed on a copy first (kept in `.backups\` as `Mars Project rehearse-polish 20261018.aprx`),
  then `make_validation_sheet.py` (tally unchanged: 0 of 9,287 reviewed) and the polish on the real `.aprx`; every sheet
  exported and read, and the polished PNGs copied into `TypeArea\layouts\` and `Global60\layouts\`.
- **The interim rebuilt from the new sheets**: `make_interim_figs.py` (11 layouts at 200 dpi), the deck (28 slides) and
  the report (20 pages, 19 figures), live files backed up to `NEXT STUFF\.backup_20261018\`; both rendered and read;
  `verify_interim.py`: 249 numbers, all in the KB.
- **The repo**: a new `docs/figures.md` lists every image with its builder script and sections, thumbnails linked to
  the full files; the README shows the result charts beside the results they back and groups the layouts by theme with
  captions. `tools/check_repo.py` now also reads HTML `src`/`href` links and fails when an image or PDF in the tree is
  missing from `docs/figures.md` (the interim's layout crops count as one group); proved on a planted unindexed file
  and a planted broken image.
- Not changed: the layouts' footer gives "Logan Edwards" (the public name in the repo is "Logan M Edwards"); the
  province figure (`pres1_img\global60_thermal.png`) is still the dark Presentation 1 version (`INTERIM-PLAN.md`, section 0).

## 62. The province figure redrawn from §28.10, light style; the interim rebuilt — 2026-10-19 **[V]**

On the laptop; nothing measured, no raster read, nothing written to the `.aprx` or the gdb.

- **`build\make_fig_global60.py` rewritten** (old version in `build\.py_backup_20261019\`, with the dark PNG). It
  parses §28.10's three tables from this file at run time and draws two panels in the palette and type of
  `make_fig_tes.py`: **A**, the diurnal-contrast index over the seven provinces (mean ± sd); **B**, day IR, night IR
  and Viking red DN ± sd for the four provinces with tabulated DN, the whole-mosaic mean ± sd as a band, and the
  dusty − rocky differences −0.19, +0.02 and +47.67 DN. System Python, matplotlib only; the Viking cache and the
  source mosaics are no longer read. Output `pres1_img\global60_thermal.png`, 2300 × 980 px.
- **What the tables cover, found by recomputing them:** the −0.0009 reproduces only as three dusty against four
  rocky (−0.000925; with Syrtis and Acidalia alone as rocky it would be −0.0037). The dusty and rocky DN rows are the
  means of the two dusty and two rocky provinces of the per-province table: Viking 123.50 and 75.80 against 123.50
  and 75.82; day 125.55 and 125.80 against 125.61 and 125.80; night 124.45 and 124.45 against 124.50 and 124.49.
  So **47.67 DN is four provinces, not seven**; INTERIM-PLAN and §39.3 said seven. §28.10 now says which set each
  number covers.
- **The script checks this before drawing** and stops otherwise: the recomputed index difference must round to the
  recorded one, and each DN row must lie within 0.07 DN of its two-province mean. Proved on two planted defects
  (Hellas floor counted dusty; the Viking rocky row moved 6 DN): both stop it.
- **The deck's slide 11** (`interim.py`) now says 47.67 DN, −0.19 and +0.02 DN, and −0.0009 over seven provinces,
  instead of "54.4 DN (these five boxes)". Rebuilt: 28 slides; the report **19 pages** (the wide figure is shorter
  than the tall dark one), 19 figures; live files backed up to `NEXT STUFF\.backup_20261019\`. `make_interim_figs.py`
  not rerun (no layout changed). Both rendered; slide 11 and report page 5 read. `verify_interim.py`: 251 numbers,
  all in the record.
- Repo: the figure's row in `docs/figures.md` moved from "Other" to "Result charts" and rewritten; the README shows
  the chart under T3 with the province result.
- Not changed: layout 08's caption A says "Bright dust (Arabia, Tharsis, Amazonis) against dark, rocky Syrtis Major
  and Acidalia: 47.7 DN apart", which names Tharsis among the dusty provinces of a number that does not include it
  (`make_mosaic_layout.py`; fixing it means a layout rebuild and polish).

## 63. Layout 15, the Athabasca type area; footers and 08's caption fixed; the repo's layouts reviewed — 2026-10-19 **[V]**

On the laptop, ArcGIS Pro closed. Nothing measured; no raster written.

- **Why a new sheet:** Athabasca Valles is the scientific hook, but its only layout was 09 (candidates over a
  hillshade); Ius Chasma has its visible and night-IR sheets (01, 02). **`build\make_athabasca_layout.py`** builds
  four maps (`Athabasca Valles — visible / night IR / day IR / topography`, from the existing `ath_*` rasters) and
  layout **`15_athabasca_type_area`** in the four-panel form of 08: unit `lAv` of SIM 3292 outlined on every panel,
  the 2° graticule, a scale bar; captions from §42.1, §42.2, §42.4 and §47.2 only. The DEM's range in caption D is
  read from `ath_dem.tif` at run time: **−4,495 to 1,945 m**. The diurnal-contrast index is not a panel (§42.4).
  Rehearsed on a copy beside the `.aprx` (kept in `.backups\` as `Mars Project rehearse-ath 20261019.aprx`), then run
  on the real one; exported and read twice (a legend element replaced by a drawn swatch; the scale bar's label
  frequency set to divisions only, the default added a "25").
- **`polish_layouts.py`**: every footer "Logan Edwards" → "Logan M Edwards", the public name (also the builders'
  `CREDIT` in `make_global60_maps.py` and `make_typearea_layouts.py`); 08's caption A no longer names Tharsis
  (§62; also fixed in `make_mosaic_layout.py`). All 15 sheets polished, exported, copied into `TypeArea\layouts\`
  and `Global60\layouts\`. The project: **30 maps, 15 layouts, 0 broken data sources**.
- **Map frames, checked:** the ±60° sheets draw in geographic `GCS_Mars_2000` (0°E at the centre); 08 and the
  type-area sheets in `Mars_Equidistant_Cylindrical_CM180`. The repo's `docs/figures.md` said every map was
  CM 180: corrected. §5 records it.
- Not changed: the interim deck and report still say 14 layouts and do not show 15 (`interim.py` line 75); the crops
  in `build\interim_img\` were not re-exported (`make_interim_figs.py` hides each sheet's prose, footer included).
  The author's decision the same day: leave the deck as it is for now.

### 63.1 The repo audited for stale parts: Athabasca is in no release

- **`Mars Project\Athabasca\` (20 rasters, 1.18 GB, the source of layouts 09 and 15) is in no GitHub release**,
  and the raster catalogue and `restore.py` did not know it: `github_release_bundle.py` bundled `TypeArea\` only.
  Now `github_release_bundle.py` adds an `athabasca` group (one zip, under the 1.9 GB part size); `restore.py`
  (repo-only) unzips `athabasca*` into `Mars Project\`; `github_catalog_rasters.py` writes an Athabasca section to
  `docs/rasters.md` from the rasters' headers (20 described, none missing, the CRS assertion holds), marked
  "none yet" until `ATH_RELEASE` is set to the first data release that carries it. `docs/backup.md` and the
  README say so. **Until the next `github_release_bundle.py --upload data-YYYY-MM-DD`, the drive is its only
  copy**; it is re-computable with the type-area chain's `--area ath` (§42.1).
- Smaller: this file's header (last updated, owner's public name), a "where to look" row for the layouts;
  `Global60\README.md`'s `layouts\` row (04–15); `restore.py`'s docstring (no "new training" shapefile since §57.6,
  the Athabasca junction); the README's status heading re-dated 2026-10-19. `verify_interim.py` 251 numbers, all
  in the record; `verify_all.py` 37 / 37.

### 63.2 Release `data-2026-10-19`: the Athabasca type area backed up

At the author's request the same day. Laptop, Wi-Fi.

- **Staged:** `github_export_gdb.py --rasters --repo <scratch>`, so the repo's `exports/` was not rewritten (the gdb
  has not changed since 2026-10-16 12:45, before that export): 26 feature classes, every row count matched, the
  catalogue identical to the repo's but for row order; the two GUI SVM maps re-exported at exactly the 10-16 asset
  sizes (249,261,023 and 238,247,660 bytes).
- **Published** with `github_release_bundle.py --upload data-2026-10-19`: 11 assets, **7.3 GB**: `typearea-part1..3`,
  **`athabasca.zip`** (145 files, 918 MB), `global60-classification-part1/2` (part 1 still holds the published
  `_mode11` map; 1.9 GB now), `npy-caches.zip`, the GeoPackage, the two `Classified_*.tif`, `SHA256SUMS.txt`. It
  replaces `data-2026-10-16` (kept); `restore.py` takes the newest data release, so it now restores Athabasca too.
- **Pointed at it:** `github_catalog_rasters.py` (`DATA`, `ATH_RELEASE`; `docs/rasters.md` regenerated, 0 rows on
  the old tag), `github_export_gdb.py` (`RELEASE`; `--catalog-only` rewrote `exports/README.md`), the README's
  quick start and backup section, `docs/backup.md`, `CITATION.cff` (`date-released`).
- **`github_export_gdb.py --catalog-only` no longer restamps the export date** with the day it runs: it keeps the
  date of the export it describes (2026-10-16 here). File times can't give it: a `git pull` restamped the clone's
  gdb files 2026-10-18.
- `GITHUB_TOKEN=$(gh auth token) python tools/check_remote.py`: **72 release assets, 4 source mosaics, all pass.**
- **The README quick start rerun verbatim** on the new release: download, unzip, the Python block: Crater 32.8 %,
  steep/windy hills 1.8 %, lava tube 9.3 %, Normal Ground 56.1 %, as the README says; the downloaded
  `global60_landforms_svm_200m_mode11.tif` has the drive copy's SHA-256.

## 64. All fifteen sheets read for quality and accuracy; 08 recentred; three results given charts — 2026-10-19 **[V]**

On the laptop, ArcGIS Pro closed. Nothing measured; no raster written. At the author's request: every analysed
result that matters should have a proper depiction, and the layouts should be of proper quality and accuracy.

**Every sheet exported and read.** Defects found, and the fix:

| sheet | defect | fix |
|---|---|---|
| 08 | the only ±60° sheet centred on 180°E (§38): beside 04 or 10 the planet sat half a turn round; no graticule | `make_mosaic_layout.py` draws the four maps in `GCS_Mars_2000` centred on 0°E; `make_reference_maps.py` adds the 30° graticule at 5.5 pt (`MAPS_30_SMALL`); the note says so |
| 06, 09, 14 | footer named the ±60° extent and "Mars 2000 sphere" on sheets drawn on the type-area grid | `areas.credit()` gives the CRS line of 01–03 and 15 with each window; used by `make_candidate_maps.py` and `make_validation_sheet.py` |
| 09 | the map filled 4.7 in of an 8.5 in page; a third of the page empty | the frame runs down to the notes (5.68 in high); legend, scale bar and north arrow beside it |
| 01–03, 06, 09 | scale bar's first division split in two: "0 20 40" crowded into the start | `polish_layouts.py`: no subdivisions, a label at every division (0 40 80 120 160; 0 50 … 200) |
| 04, 07, 13 | legend border ran to 10.68–10.70 in, past the 10.55 in margin the map frames keep (a legend's border is drawn 0.15 in outside its element) | builders place them so x + width = 10.40; `polish_layouts.py` moves any that do not |
| 11 | the Robbins table ran to 10.76 in | columns narrowed (`TABLE_W` in the builder; `polish_layouts.py` moves the 80 cells in place, since rerunning the builder recomputes 1.4 million features) |
| 13 | footer ran to 10.8 in; the enrichment key to 10.61 | the footer's second clause on its own line; key swatches 0.768 in |

Nothing else wrong was found: every number printed on a sheet was checked against its JSON log or this record
(04 against `global60_classification_check_200m_mode11.json`; 10's type-area boxes against `areas.py` to the
pixel; 12's order counts sum to 969,822). Rehearsed on a copy beside the `.aprx` (kept in the scratch folder), then
`make_candidate_maps.py`, `make_mosaic_layout.py`, `make_reference_maps.py`, `make_geomap_sheet.py --cell 200`,
`make_validation_sheet.py` and `polish_layouts.py` on the real one; a second polish run changes nothing but 03's
legend (dropped again each run, as before; harmless). All 15 sheets exported, read, and copied into
`TypeArea\layouts\` and `Global60\layouts\`. Layout 14 now reads "Read 2026-10-19 03:30"; its counts are unchanged
(0 of 9,287 reviewed).

**Three results had a log and a table here but no figure.** `build\make_fig_checks.py` draws them from the logs
into `build\interim_img\`:

- `accuracy_200m.png`: the published map's held-out confusion, area-weighted, rows summing to 100 % (§57): of the area
  the map calls lava tube inside held-out polygons, 94 % lies on Crater polygons, hence its 2 % user's accuracy;
  and held-out accuracy against the majority window at 200 m and 400 m (§55.3).
- `t2_density.png`: T2, craters ≥ 1 km per 10⁶ km² per unit, Robbins against the detector (§42.2).
- `lava_relabel.png`: the lava-tube relabel, variants A–D (§43.3).

The README shows all three under its results, `docs/figures.md` lists them. Not changed: the interim deck (the
author's call, §63); its crop of 08 in `build\interim_img\` predates the recentring.

## 65. The type-area results drawn for the repo; 07's size classes and 03's legend; a rounding slip — 2026-10-19 **[V]**

On the laptop, ArcGIS Pro closed. Nothing measured; no raster written. The same request as §64, continued.

- **Four type-area results had no depiction in the repo.** Their only figures were Presentation 1's navy slides
  in `build\pres1_img\`, which the repo no longer mirrors (§57.6): the segmentation sweep (§23.5), the
  diurnal-contrast index (§24), the channel candidates with the `Fill` trap (§25.1), and the closed depressions
  with the Oudemans / Perrotin check (§26). `make_fig_segmentation.py`, `make_fig_thermal.py`,
  `make_fig_channels.py` and `make_fig_craters.py` take **`--light`**, which writes the repo's light style to
  `build\interim_img\`; without it they still write Presentation 1's originals. All four now read the real
  `Mars Project\TypeArea\` folder, not the junction, which is broken on whichever machine it does not point at
  (§58). The README shows each beside its result; `docs/figures.md` has a "Type-area figures" section.
- **Wording brought to the record**, in both modes: the index panels say "mean index per object-based class" and
  "same steepness, opposite sign" (they said "every class separates" and "not a topography proxy"), and the
  suptitle cites §24; the crater figure says "closed depressions, not a crater count" (it said "candidate craters",
  against §42.3) and calls the overlay what it is, depression depth (fill − DEM), not "depth Fill removed"; the
  sweep's 9 / 9 / 80 caption says "far coarser than the 1 km the grid can map" (it said "below the 1 km limit").
- **A rounding slip fixed:** the `Fill` figure's title said **23 %** of the scene flooded, and §25.1 said **21.8 %**.
  `ius_filldepth.tif` read whole: 8,023,834 of 36,897,650 cells raised > 1 m = **21.746 %**, 80,238 km²; so
  **21.7 %**. The title is now computed from the raster; §25.1 corrected.
- **Layout 07:** the five basin size classes were natural breaks (20–41, 41–81, 81–220, 220–1,027, 1,027–2,697 km);
  now **20–40, 40–80, 80–200, 200–1,000, 1,000–2,697 km** (3,541, 1,295, 282, 22 and 4 basins), `BASIN_BREAKS` in
  `make_candidate_maps.py`. The IAU layer's smallest crater is 100.8 km, so its legend's "> 100 km" stands.
- **Layout 03:** the legend auto-added every layer of its map, so the graticule entry that `polish_layouts.py`
  dropped came back on each open, and polish was not idempotent there. Auto-add is now off; the legend has a title,
  "Iso Cluster class (spectral clusters, not named landforms)". **A second polish run now changes nothing on any sheet.**
- Smaller: the public name in three deck scripts' docstrings (`le_theme.py`, `build_interim_le.py`,
  `build_pres1_le.py`); `make_fig_craters.py`'s first line, which `docs/scripts.md` quotes; `INTERIM-PLAN.md`'s
  layout count. Rebuilt with `make_candidate_maps.py`, `make_reference_maps.py` and `polish_layouts.py` (rehearsed
  on a copy first); all 15 sheets exported, 03 and 07 read, the polished sheets copied into the layout folders.

## 66. The Deep Learning Libraries installed on the desktop; the X5 preflight ready — 2026-10-19 **[V]**

On the desktop, ArcGIS Pro closed, no job running from `arcgispro-py3`. Closes §53.5.

- **Checked first:** `ProDeepLearning.msi` (18,209,792 bytes) still Authenticode **Valid**, signed by Environmental
  Systems Research Institute, Inc. (§53.3).
- **Installed** with `msiexec /i ProDeepLearning.msi /passive /norestart /l*v`, elevated; the author answered the
  UAC prompt. 21:39:08 → 21:45:11, **6 min 6 s**, exit code **0**. The log
  (`D:\MarsDownloads\dl_libs_37\install_admin.log`, drive D: only): *"Deep Learning Libraries for ArcGIS Pro",
  version 3.7.1901, "Installation success or error status: 0"*.
- **`desktop_check.py --gpu`** (`logs\desktop_check_DESKTOP-PJS73RO.json`): the three junctions ok; `torch`,
  `torchvision`, `fastai`, `arcgis.learn` import; CUDA sees the **RTX 2080 Ti**; the training-split export holds
  **3,622 chips**, labels from the training split; Slope 23.6 s CPU-only against 12.1 s GPU_THEN_CPU, GPU engaged.
  **"X5 ready to train: True."** One warning: `fastai` imports the deprecated `pkg_resources` (harmless today;
  setuptools ≥ 81 drops it).

### 66.1 X5 trained: RetinaNet on the training-split chips — 2026-10-19 **[V]**

`make_dl_model.py --train --model RETINANET --epochs 20` (batch 8, chip 256, 10 % validation, backbone frozen,
early stopping), detached, `logs\dl_train_DESKTOP-PJS73RO.log`; the script now prints the tool's messages.
**RetinaNet takes the 7-band input**: the `.emd` reads `IsMultispectral` true, `ExtractBands` 0–6, ResNet-50
backbone (ImageNet weights fetched from `download.pytorch.org` into `~\.cache\torch`), arcgis.learn 2.4.3. The tool
ran 21:55:58 → 22:21:20, **25 min 22 s** (epoch 1 4 min 51 s with the learning-rate finder, then ~2 min 05 s each;
GPU ~27 %, 4.2 GB). Learning rate 3.6e-5 to 3.6e-4.

| epoch | train loss | valid loss | AP |
|---|---|---|---|
| 1 | 1.587 | 484.501 | 0.055 |
| 2 | 1.247 | 17.150 | 0.016 |
| 3 | 1.156 | **1.567** | 0.005 |
| 4 | 1.117 | 1.937 | 0.003 |
| 5 | 1.138 | 1.859 | 0.002 |
| 6 | 1.050 | 3.185 | 0.006 |
| 7 | 1.079 | 2.458 | 0.075 |
| 8 | 1.015 | 3.787 | 0.003 |
| 9 | 0.988 | 2.502 | 0.036 |

**Early stopping after epoch 9; the saved model is epoch 3's** (`monitored_valid_loss` 1.567).
`Mars Project\DLModels\global60_retinanet_20261019\` (`.emd`, `.pth` 146 MB, `.dlpk` 137 MB,
`model_metrics.html`, `ModelCharacteristics\`). **Validation average precision per class: Crater 0.010, Normal
Ground 0.009, lava tube 0, steep/windy hills 0.** The sample sheet (`show_results.png`) puts the right class on
crater and plains chips with boxes that do not match the labels' extents: the whole-chip boxes on area classes
that §50 named a limit. These are validation numbers on chips drawn from the training split, **not the held-out
score**: that needs `--detect --emd <model>` and then `--score`. Which other detection models take 7-band input
remains unverified **[?]**.

### 66.2 X5 detected and scored on the held-out polygons — 2026-10-19 **[V]**

**Three failed runs first, the cause found by probe.** `--detect` as written (the 25 km buffer of the test class as
`arcpy.env.mask`) failed three times with *ERROR 000599: Falls outside of output geometry domains* (logs
`dl_detect_score_run1/2/3_failed_*.log`), writing to the gdb, to the gdb with a widened XY domain on the output SR,
and to a shapefile. A guess that boxes past the 0°E edge broke the domain was wrong (the nearest held-out polygon
is 451 km from the edge; a planted box 12.8 km past the edge does fail a default-domain class, but neither the
`XYDomain` nor the `outputCoordinateSystem` environment reached the tool's own table). **Probes on one 300 km
window settled it:** no mask, 33 boxes in 147 s; the same window with the geographic buffer as the mask, ERROR 000599
in 74 s; the buffer projected to the stack's SR, still running after 17 min at ~0 % CPU and I/O (stopped).
**`detect()` now runs one window per held-out 15° block** (its polygons' extent + 25 km, no mask; 14 blocks,
~5.0 M km²), keeps each window's boxes that touch its own polygons' extent, and merges them into
`C:\MarsScratch\x5\dl_detections_heldout_20261019.shp`, copied to
`Mars Project\DLModels\global60_retinanet_20261019\detections_heldout_20261019\`. 23:10:09 → 23:33:35, **23 min 26 s**
(66–166 s a block); **2,032 boxes, 1,838 kept** (968 Crater, 870 Normal Ground; confidence 30.0–74.4 against the
0.3 threshold). **The model never predicts steep/windy hills or lava tube.** `--score` (7 s; its extent prefilters
leave `--score-selftest` 4/4), `logs\dl_heldout_score.json`:

| class | held-out polygons | recall (≥ 50 % covered by own-class boxes) | in-polygon detections | precision | all-one-class labeller |
|---|---|---|---|---|---|
| Crater | 124 | **41.9 %** (52) | 129 | **87.6 %** (113) | 71.1 % |
| Normal Ground | 22 | **22.7 %** (5) | 72 | **56.9 %** (41) | 20.9 % |
| steep/windy hills | 16 | 0 | 0 | — | — |
| lava tube | 21 | 0 | 0 | — | — |

Of the 201 detections centred in a held-out polygon, 143 fall in Crater polygons (71.1 %; Crater is 57.6 % of the
held-out area, Normal Ground 35.2 %, hills 6.6 %, lava tube 0.6 %). The wrong ones: 30 Normal Ground boxes on Crater
polygons, 13 Crater boxes on hills, 2 on lava tube, 1 on Normal Ground; 1 Normal Ground box on hills. **Reading:** the
detector separates the two common classes well above the one-class baselines (Crater +16.5 pt, Normal Ground
+36.0 pt in precision) but finds under half the crater polygons and a fifth of the plains, and nothing of the two
rare classes. **No prediction or verdict rule was written into the script before it ran** (§51.3 defines the
metric only, against the §47 practice), so this is a measurement, not a test of a hypothesis; it is polygon-level
and **not comparable** with the SVM's per-pixel 73.8 %, κ 0.58 (§57). The detections are not yet in
the gdb or the `.aprx` (§66.3 puts them there).

### 66.3 X5's detections in the gdb and a map in the `.aprx` — 2026-10-19 **[V]**

`build\make_dl_map.py` (Pro closed; `.aprx` backed up to `.backups\Mars Project 20261019-234048.aprx`; rehearsed
first on a copy beside the `.aprx`, the copy then moved off the drive):

- **`DL_Detections_heldout_20261019`**, 1,838 polygons copied from the shapefile beside the model; fields `Class`,
  `Classvalue`, `Confidence`, `Model`, `MappedBy`. Written in the stack's SR with the XY domain widened by 400 km
  (an explicit SR carries its own domain; §66.2). The script asserts the row count and the extent (< 1 m) against
  the shapefile, and refuses a class holding rows it did not write.
- **Map "X5 — deep-learning detections (held out)"**, top to bottom: the 30° graticule, the detections outlined in
  the class colours, the held-out labels outlined and filled at 35 %, the training labels (off), the ±60° extent,
  the ±60° hillshade. A trial export of one block (lon −45…−30°, lat −15…0°) and of ±60° was read: both draw.
  **No layout yet**: a result should also get one (§31); made in §66.4.
- **Checked:** `--score` on the gdb class reproduces §66.2's recall, precision and counts exactly (1,838 boxes);
  `logs\dl_heldout_score.json` now names the gdb class. The project: **31 maps, 15 layouts**.
- **Two empty leftovers deleted, on the author's approval:** `DL_Detections_heldout_20261019_56` and `_7050`
  (0 rows each, the tool's schema `Class`, `Confidence`), written by the failed detect runs 1 and 2 (§66.2) and
  found by the vector export. Each asserted empty before `Delete`; the gdb is back to 29 feature classes.
- **`github_export_gdb.py`:** 25 classes to the repo's `exports\mars_project_vectors.gdb`, 27 to the GeoPackage,
  every row count checked. A first attempt stopped on *WinError 1224* (OneDrive still held a file of the
  previous copy) with the clone's gdb half-written; the rerun completed, and its 180 files match the fresh
  export byte for byte. The copy overwrites but never removes files, so compare after any interrupted export.

### 66.4 Layout 16, X5's sheet; the interim's deep-learning lines brought current — 2026-10-20 **[V]**

On the desktop, Pro closed. Nothing new measured: the sheet prints §66.1–66.2 and two figures computed from the gdb
class at run time, logged to `logs\dl_sheet.json`.

- **`16_x5_detections`** (`make_dl_map.py` now also builds it): frame A, the X5 map over ±60° (the 14 windows);
  frame B, the block with the most held-out polygons, **57, at 75–90°E, 30–15°S**; the per-polygon table from
  `logs\dl_heldout_score.json` with each class's one-class rate; the limits (boxes on area classes, §50; not
  comparable with the SVM's per-pixel score; no verdict rule before the run). Rehearsed on a copy beside the
  `.aprx`, polished and read; **reading found** the scale bar's labels unreadable over B's hillshade (moved beside B,
  titled "Scale of B") and the held-out layer's legend heading wrapping to three lines (layer renamed "Held-out
  labels (never trained on)"). Then built on the real `.aprx` (backups `20261020-001308`, `-001516`);
  `polish_layouts.py` changed nothing on 01–15 and gave 16 Arial and 11 pt legend headings; the polished export,
  pixel-identical to the rehearsal's that was read, copied into `Global60\layouts\`. The project: **31 maps, 16
  layouts**.
- **The interim:** `interim.py`'s next step said the model would come "once Esri's Deep Learning Libraries are
  installed", and the schedule put it in 26 Oct – 1 Nov. Now the next step names the result (Crater precision
  87.6 % against 71.1 % for always naming Crater; the two rare classes never named, §66.2) and the schedule lists
  the detector among the desktop runs done. **No X5 slide was added** (what the deck shows is the author's call;
  it still shows 14 layouts, §63). Rebuilt with the live files backed up to `NEXT STUFF\.backup_20261020\`: 28
  slides, 19 pages; rendered through PowerPoint and Word, compared page by page with the previous build: **only
  slide 28 and report page 19 changed**, both read. `verify_interim.py`: all **253** numbers found in this record.

### 66.5 X5b: the detector retrained with the backbone unfrozen, no early stopping, rare-class chips and cleaned boxes — 2026-10-20

The author's request, 2026-10-20: improve the detector and the deep-learning process, and turn off the early
stopping that ended X5 after 9 of 20 epochs. **Written before the run** (the §47 practice §66.2 missed).

**What X5 got wrong, from its record and its export:**

- **The backbone was frozen** (`FREEZE_MODEL`, the tool's default). Four of the seven bands (night IR, day IR,
  slope, relief) are not RGB; the ImageNet layers behind the re-initialised first layer could not adapt to them.
- **Early stopping** (patience 5 epochs on a validation loss that swung from 484.5 to 1.6 to 3.8) ended the run at
  epoch 9; the one-cycle learning-rate schedule never reached its low-rate end.
- **The rare classes had 329 and 292 boxes** against 1,968 and 2,704 (§50.2), and the model never named them.
- **Edge slivers:** a polygon that only clips a chip's edge still gives a box. In the training export, boxes
  under 16 px (3.2 km) thin that touch the chip edge on that side: Crater 287 of 1,968, hills 49 of 329, lava tube
  29 of 292, Normal Ground 254 of 2,704; 284 of the 3,622 chips hold nothing else.
- **Process:** a second `--detect` would have reused X5's finished windows in `C:\MarsScratch\x5`; `--score`
  overwrote the one score file that layout 16 reads; the model folder was named by date only; the run's settings
  were not saved beside the model.

**What changes (`make_dl_model.py`, `make_global60_dl_export.py --rare`):**

- `make_global60_dl_export.py --rare`: chips around the 51 training hills and lava tube polygons (each buffered
  55 km in the stack's SR; a chip must lie wholly inside the mask) at **stride 64**, labelled from the whole
  training split, to `C:\MarsScratch\x5b\export_rare`.
- `--prepare`: cleaned copies of the training export and of the rare chips in `C:\MarsScratch\x5b\main_clean`,
  `rare_clean`, without the edge slivers or the chips they leave empty; counts in `logs\dl_prepare_x5b.json`.
- `--train` defaults: backbone **unfrozen**, early stopping **off**, **30 epochs**, the model on internal disk then
  copied to `DLModels\global60_retinanet_x5b_20261020\` with `run_config.json` and `training_messages.txt`.
  arcgis.learn still keeps the epoch with the lowest validation loss whether or not it stops early
  (`fit(checkpoint=True)`, which the tool always passes). Validation is still the tool's random 10 % of chips,
  which overlap their neighbours by half: optimistic, used only to pick the epoch.
- `--detect` at threshold **0.1**, into the model's own folder; `--score` at cutoffs 0.1–0.5 from that one layer,
  into `logs\dl_heldout_score_x5b.json`, refusing to overwrite another layer's file. The rescored X5 matches §66.2
  exactly (cutoff 0.3); at 0.4 its Crater recall falls to 29.0 % and its Normal Ground recall to 0.

Unchanged from X5, so the two compare: RetinaNet, ResNet-50, chip 256, batch 8, the tool's default augmentation,
the same held-out polygons and windows, the same scorer.

**Verdict rule, at the primary cutoff 0.3** (also in the script's docstring): X5b improves on X5 if (a) Crater
recall > 41.9 % with Crater precision ≥ 71.1 %, (b) Normal Ground recall > 22.7 % with its precision ≥ 20.9 %, and
(c) at least one rare class is named in a held-out polygon of its own class at least once. All three: improved;
(a) and (b) without (c): better on the common classes only; otherwise not improved. The other cutoffs are
reported, never used to pick a winner. **Prediction:** (a) and (b) hold; (c) holds for hills, not for lava tube
(its 23 training polygons are narrow and its SVM user's accuracy was 2 %, §57).

**The run** (`logs\run_x5b.cmd` → `logs\dl_x5b_DESKTOP-PJS73RO.log`; 00:51 → 02:58):

- **The rare export**, 855 s: **1,430 chips**, 4,872 boxes (hills 2,597, lava tube 1,702, Crater 338, Normal
  Ground 235). **`--prepare`** (`logs\dl_prepare_x5b.json`): main 3,622 → **3,338 chips**, 5,293 → 4,674 boxes
  (slivers dropped: Crater 287, hills 49, lava tube 29, Normal Ground 254); rare 1,430 → **1,419 chips** (slivers
  62, 283, 108, 38). Training boxes after both: Crater 1,957, hills 2,594, lava tube 1,857, Normal Ground 2,647.
- **Training**, 6,014 s (**1 h 40 min**; epoch 1 4 min 43 s with the learning-rate finder, then ~3 min 07 s;
  GPU ~4.7 GB): all **30 epochs** ran. Validation loss 428.1 at epoch 1 (as X5's 484.5), 1.96 at epoch 4, then
  swinging between 1.20 and 4.37 while the training loss fell steadily to 0.460; validation AP rose to 0.35–0.44
  from epoch 9 on (X5: ≤ 0.075). **The kept model is epoch 16** (valid loss **1.203**, AP 0.350); by epoch 30 the
  validation loss stood at 1.70 against a training loss of 0.46, the start of overfitting. Validation AP per class:
  Crater 0.343, hills 0.538, lava tube 0.519, **Normal Ground 0.000**; the rare classes' figures are inflated, their
  chips overlapping by three quarters at stride 64. `DLModels\global60_retinanet_x5b_20261020\`.
- **Detection** at threshold 0.1, ~25 min (1,517 s in the 14 windows, 65–229 s each): **5,810 boxes** kept; 1,024 at ≥ 0.3 (Crater
  508, lava tube 298, Normal Ground 173, hills 45), against X5's 1,838 (968 Crater, 870 Normal Ground).

**The held-out score at the primary cutoff 0.3** (`logs\dl_heldout_score_x5b.json`):

| class | polygons | recall X5 → **X5b** | in-polygon detections X5 → X5b | precision X5 → **X5b** |
|---|---|---|---|---|
| Crater | 124 | 41.9 % → **43.5 %** (54) | 129 → 88 | 87.6 % → **100 %** (88) |
| steep/windy hills | 16 | 0 → **25.0 %** (4) | 0 → 11 | — → **100 %** (11) |
| lava tube | 21 | 0 → **4.8 %** (1) | 0 → 37 | — → **5.4 %** (2) |
| Normal Ground | 22 | 22.7 % → **4.5 %** (1) | 72 → 48 | 56.9 % → **100 %** (48) |

All of X5b's 35 wrong in-polygon detections are lava tube boxes: 31 on Crater polygons, 3 on hills, 1 on Normal
Ground. X5's 47 were Normal Ground boxes on craters (30) and hills (1) and Crater boxes on hills (13), lava tube
(2) and Normal Ground (1). Normal Ground boxes are fewer and smaller (median 655 km² against X5's 1,372 km²), and the recall
needs a polygon ≥ 50 % covered, which large plains polygons rarely are. Other cutoffs, descriptive only: at 0.1,
Crater 55.6 % / 93.6 %, hills 50.0 % / 92.3 %, lava tube 4.8 % / 3.1 %, Normal Ground 13.6 % / 91.0 %
(recall / precision); at 0.5, Crater 22.6 % / 100 %, hills 18.8 % / 100 %.

**Verdict by the rule: not improved.** (a) holds (43.5 % > 41.9 %, by two polygons; precision 100 %), (c) holds
(hills named 11 times in hills polygons, lava tube twice), **(b) fails** (Normal Ground recall 4.5 % against
22.7 %). The prediction was wrong twice: (b) failed, and lava tube was named. **Reading:** X5b names three classes
with no class confusion among them and finds a quarter of the hills polygons that X5 never named; its one
systematic error is lava tube, over-predicted on cratered ground after the rare chips raised its boxes six-fold,
and it gave up Normal Ground coverage. A tuned X5d (fewer lava tube chips, Normal Ground restored) would be chosen
by looking at these held-out numbers, which would make them a validation set; any next round needs a validation
split of its own first (training blocks held back), not another look at the 14 held-out blocks.

### 66.6 X5c: a pixel classifier (U-Net) beside the box detector, scored per pixel like the SVM — 2026-10-20

**The author's decision, 2026-10-20:** after X5b, train a pixel classifier on the same training split and score it
per pixel on the held-out polygons. This reverses, for this one model, the "boxes only" of q26 (§50; §31.4 had
named `Classified_Tiles` the better fit for area classes). **Written before the run.**

- `build\make_dl_pixels.py --export`: `Classified_Tiles` from `Landform_TrainingSamples_terrain_60_train`, 256 px
  chips, stride 128, chips with features only, to `C:\MarsScratch\x5c\export_tiles`. Unlabelled ground is 0.
- `--train`: U-Net, ResNet-34, `class_balancing True`, `ignore_classes [0]` (the loss never teaches that
  unlabelled ground is a class), backbone unfrozen, early stopping off, 30 epochs, batch 8, 10 % validation;
  the model to `DLModels\global60_unet_x5c_20261020\` with its settings and messages.
- `--classify`: one raster per X5 window (the held-out polygons' extent + 25 km, snapped to the stack), GPU.
- `--score`: `svmcheck.training_score`, the code behind §31.3 and §57, area-weighted, each window on its own
  polygons, at 400 m (the 400 m lattice of the 200 m grid, as §57 scored) and at 200 m.
  `logs\dl_pixels_score_x5c.json`.
- **The scorer checked first:** `--score-svm` runs it on the SVM maps' windows and gives the published numbers,
  the 11 × 11 map **0.7383, κ 0.5827** at 400 m (§57: 73.8 %, κ 0.583) and the unfiltered 200 m map **0.6985,
  κ 0.532** (§57: 70 %, κ 0.53); at 200 m the same to 0.0001. `logs\dl_pixels_score_svm_baseline.json`.

**Verdict rule, at 400 m:** X5c beats the published SVM map if its held-out accuracy and κ both exceed 0.7383 and
0.5827; within 2 points of accuracy either way is a match; below that the SVM stays the better map. Producer's and
user's accuracy per class are reported, the rare classes' above all. **Prediction:** a match, with lava tube's user's
accuracy still under 10 % (§57: 2 %).

**The run** (`logs\run_x5c.cmd` → `logs\dl_x5c_DESKTOP-PJS73RO.log`; export `logs\dl_x5c_export_DESKTOP-PJS73RO.log`):

- **Export**, 358 s, during X5b's training: **3,622 chips**, the same chips and 5,293 features as §50.2.
- **Training**, 02:58 → 04:11, 4,376 s (**1 h 13 min**; ~2 min 19 s an epoch, 30 epochs). Validation loss 0.466 →
  0.029, falling almost throughout (one spike, 1.40 at epoch 6); **the kept model is epoch 29** (valid loss
  **0.0291**), pixel accuracy 0.992 on the labelled pixels of the validation chips. Per class on those chips:
  recall 0.985–0.995, **precision 0.10–0.53** (Crater 0.354, hills 0.235, lava tube 0.101, Normal Ground 0.530):
  the model assigns a class to every pixel, unlabelled ground included, and those pixels count against it.
  `DLModels\global60_unet_x5c_20261020\` (`.pth` 165 MB, `.dlpk` 156 MB, drive only).
- **Classification**, 04:11 → 04:30, **19 min** (61–168 s a window), 14 rasters at 200 m, values 1–4 named in
  the attribute table, 99.98 % of window pixels classified; copied to the model's `classified_heldout\`.

**The held-out score** (`logs\dl_pixels_score_x5c.json`; the SVM columns from `logs\dl_pixels_score_svm_baseline.json`,
same code, same windows):

| at 400 m | X5c U-Net | SVM, 11 × 11 (published) | SVM, unfiltered 200 m |
|---|---|---|---|
| **accuracy, κ** | **98.75 %, 0.977** | 73.83 %, 0.583 | 69.85 %, 0.532 |
| producer's: Crater, hills, lava tube, Normal Ground | 99.0, 99.8, 82.6, 98.3 % | 60.7, 62.8, 44.8, 99.2 % | |
| user's: Crater, hills, lava tube, Normal Ground | 99.1, 93.4, **70.7**, 99.8 % | 93.3, 50.7, **2.4**, 80.3 % | |
| polygons won (own class > 50 %) | 119/124, 16/16, 20/21, 15/22 | 107/124, 14/16, 8/21, 20/22 | |

At 200 m: 98.74 %, κ 0.977. **Verdict by the rule: X5c beats the published SVM map** (both figures above it); the
prediction (a match, lava tube's user's accuracy < 10 %) was wrong on both counts.

**What the number does and does not show, read from the windows** (three mixed blocks and the busiest one drawn
beside the Viking colour and the SVM map):

- **It paints terrain provinces, not features.** In the 57-crater block at 75–90°E it calls 93 % of the window
  Crater, the plains between the craters included, so every crater polygon is right; the validation sheet shows
  the same, a whole chip called Crater around one labelled crater. In mixed blocks it does separate classes: at
  −90…−75°E, 15–30°N (8 Crater, 15 lava tube, 8 Normal Ground polygons) lava tube lies along the lava tube
  polygons, Normal Ground round the plains polygons, Crater on the crater cluster; at −60…−45°E, 15–0°S hills
  follow the chasma walls and scarps beyond the labelled hills polygons. The held-out labels mark areas that are
  mostly single-class at 50 km, and a model that sees 51 km of context gets those areas right; the SVM, pixel by
  pixel, did not. Whether the provinces it draws outside the labels are right is not measured.
- **Tile seams:** straight-edged rectangular patches at 60–75°E, 30–45°N and in the lava tube block, where
  neighbouring 256 px tiles were classified from different context. The SVM map shows none (§31.3).
- **The crater test (§31.3) is inconclusive:** only **4** named IAU craters ≥ 5 km lie wholly in the windows clear
  of every labelled polygon (U-Net 'Crater' inside 1.00 against ring 0.59; SVM 0.40 against 0.25). A ±60°
  classification would give hundreds (§31.3: 817).
- Neighbouring blocks share provinces: a held-out block next to a training block of the same terrain is easier
  than new terrain. The SVM had the same advantage under the same split.

**So:** under the project's own held-out test the U-Net is the best landform map made so far, by 25 points, and
the first to make lava tube usable (user's 70.7 % against 2.4 %); it is a map of terrain provinces with tile seams,
not of individual features, and it exists only in the 14 windows. Not yet in the gdb, the `.aprx` or a layout.
**Open for the author:** a ±60° U-Net classification (~8 h on the GPU at the windows' rate, ~25 × their area; it
would also give the crater test its hundreds of craters and a seam count), and whether the U-Net map replaces the
SVM map as the published one.

### 66.7 X5c over all of ±60° — 2026-10-20

**The author's yes, 2026-10-20:** classify all of ±60° with the U-Net and score it as the SVM maps were. **Written
before the results.**

- `make_dl_pixels.py --classify-global`: **243 tile cores** of 4,096 × 4,096 px on the G200 grid, each classified
  with a 256 px (51.2 km) margin that `--mosaic` cuts away, so no core edge is a window edge; tiles in
  `C:\MarsScratch\x5c\global\tiles\`. Two test tiles took 136 s and 83 s; launched 11:50 (`logs\run_x5c_global.cmd`
  → `logs\dl_x5c_global_DESKTOP-PJS73RO.log`).
- `--mosaic` → **`Global60\global60_landforms_unet_200m.tif`**: G200, U8, class values 1–4 (0 none), LZW,
  nearest-neighbour overviews, an attribute table with `Class_name`; class shares in
  `logs\dl_unet_global_mosaic.json`.
- **Scored by `verify_global60_classification.py --cell 200 --raster`**, the script behind every SVM figure in §31.3
  and §57 (held-out and training accuracy, the IAU crater test, elevation bins, its 4,096 px seam ratio), and by
  `make_dl_pixels.py --seams`, which folds class changes by column and row phase at periods 128, 256 and 4,096 px,
  run on the U-Net map and on the two SVM maps for comparison (`logs\dl_seams.json`).

**Predictions:** held out, the same as in the windows to within 0.5 points (the windows hold every held-out
polygon); the crater test's 'Crater' inside minus ring smaller than the published SVM map's (57 − 46 = 11 points,
§57), since the windows show cratered provinces painted whole; a seam ratio above 1.5 at 128 or 256 px for the
U-Net and near 1.0 for both SVM maps; elevation bins reproduce more of the U-Net map than of the SVM map's 55 %
(provinces follow elevation more than pixels do).

**The run:** 11:50 → 17:36, **5 h 46 min** for 243 tiles (63–136 s each, ~85 s typical; GPU), mosaic 17:36, scored
and seam-checked by 17:43. `Global60\global60_landforms_unet_200m.tif`, **61 MB** (LZW; overviews 31 MB): Crater
**52.2 %**, Normal Ground **42.1 %**, lava tube **4.85 %**, hills **0.86 %** of the classified pixels; 100.9 M pixels
(2.7 %) none, where the stack has no data. `verify_global60.py`: **28 pass**, the new product exactly on G200.

**Scored by `verify_global60_classification.py`** (`logs\global60_classification_check_global60_landforms_unet_200m.json`),
beside the published SVM map's file of §57 (`..._200m_mode11.json`):

| | U-Net ±60° | SVM 200 m, 11 × 11 (published) |
|---|---|---|
| **held out** | **98.8 %, κ 0.979** (producer's 99.2, 99.3, 79.9, 98.5 %) | 73.8 %, κ 0.583 |
| user's: Crater, hills, lava tube, Normal Ground | 99.1, 94.5, **75.5**, 99.9 % | 93.3, 50.7, **2.4**, 80.3 % |
| training polygons | 99.3 %, κ 0.986 | 86 %, κ 0.74 |
| area shares (cos-weighted) | Crater 55.0, hills 1.0, lava tube 4.8, Normal Ground 39.2 % | 33.9, 1.9, 9.4, 54.7 % |
| IAU craters ≥ 5 km, n 817: 'Crater' inside / ring | **91.2 / 82.4 %**, inside > ring 56.8 % | 56.8 / 46.2 %, 62.9 % |
| elevation bins alone reproduce | **67.9 %** | 55.4 % |
| seam ratio, 4,096 px tiles | **5.53** (100 m), **5.75** (200 m) | 1.00 |

**`--seams`** (`logs\dl_seams.json`; ratio of the highest phase's class-change rate to the median phase's): U-Net
**8.58 / 9.20** (columns / rows) at **256 px**, both at phase 255, 4.94 / 5.19 at 128 px; SVM 11 × 11 1.01 / 1.03 and
unfiltered 1.00 / 1.03. The U-Net's seams are the classification tool's own 256 px tiles (phase 255 = the boundary
between pixels 255 and 256 of every tile; the 4,096 px ratios inherit them, 4,096 being a multiple of 256). Class
changes per neighbouring pixel pair: U-Net 0.011, SVM 11 × 11 0.023, unfiltered SVM 0.123.

**Every prediction held:** held out within 0.5 points of the windows' 98.75 %; the crater test's gap 8.8 points
against the SVM's 10.6; seams 8.6–9.2 at 256 px against ~1.0; elevation bins 67.9 % against 55.4 %.

**A seam probe on one tile** (rows 16,384–20,479, columns 57,344–61,439): padding 64 as run, 256 px ratio **6.97**;
padding 112, **4.47** in 344 s (4 × the time: ~23 h for ±60°); padding 64 with test-time augmentation, **7.98** in
147 s. Each changes 6–8 % of the tile's pixels. Larger padding reduces the seams, never removes them.

**Reading:** drawn whole, the map is a coherent province map: the southern highlands Crater, the northern lowlands
Normal Ground, lava tube on Tharsis and Elysium, hills along Valles Marineris; it is far smoother than the SVM's
(half its class changes) and gives lava tube half the SVM's area at 31 times its user's accuracy. It is also what
the windows suggested: 'Crater' covers 82 % of the ground round named craters and 91 % inside, so it marks cratered
terrain, not craters (the SVM's 57 / 46 % separates them slightly better), and elevation alone reproduces 68 % of
it. The held-out score measures agreement with hand-drawn areas, which the U-Net matches at province scale. **The
256 px seams make it unfit to publish as it stands.** Not in the gdb, the `.aprx` or a layout.

**Open for the author:** whether the U-Net map replaces the SVM map as the published one, or stands beside it as
the province map; a seam remedy first (classify twice on tile grids offset by 128 px and keep, per pixel, the pass
whose pixel lies farther from its tile edge: ~12 h; or larger padding, ~23 h and seams remaining); a layout. The
243 tiles (`C:\MarsScratch\x5c\global\tiles\`) are scratch, to the Recycle Bin on the author's word.

### 66.8 The U-Net map's seams removed by a second, offset pass — 2026-10-20

**The author's yes, 2026-10-20:** a second pass with the tile grid offset by 128 px, each pixel kept from the pass
that puts it farther from a tile edge, then rescored. **Written before the results.**

- **Pass B** (`make_dl_pixels.py --classify-global --pass B`): every window starts 128 px later than pass A's
  (at the map's left and top edges, 128 px into the map, which keeps the phase where an earlier start would be
  clipped), into `C:\MarsScratch\x5c\global\tiles_b\`. Only B is new: pass A is §66.7's 243 tiles.
- **`--mosaic --two-pass`** → **`Global60\global60_landforms_unet_200m_seamfix.tif`**: per pixel, the distance to the
  nearest edge of the tool's 256 px tiles, the smaller of the row and column distances, in each pass (A's edges
  between pixels 255 and 256 of every 256, B's between 127 and 128); the pass with the larger distance wins; A where
  B gives no class. The share taken from B and the share where A and B differ go to
  `logs\dl_unet_global_mosaic_seamfix.json`.
- **Tested on one tile first** (rows 16,384–20,479, columns 57,344–61,439; pass B 143 s): B's seams at phase **127**
  as designed (A's at 255); the 256 px seam ratio, columns / rows, A **6.97 / 8.32**, B 6.66 / 9.41, two passes
  **1.30 / 1.38**; 49.6 % of the pixels from B; A and B differ on 3.2 %.
- Then scored by `verify_global60_classification.py --cell 200 --raster` and `--seams` beside §66.7's map and both
  SVM maps (`logs\run_x5c_seamfix.cmd` → `logs\dl_x5c_seamfix_DESKTOP-PJS73RO.log`; launched 20:57).

**Predictions:** the 256 px seam ratio under 1.5 in both directions and the 4,096 px ratio of the verify script under
1.5; held out within 0.5 points of §66.7's 98.8 %; the crater test and the elevation bins within 1 point of
§66.7's; A and B differing on 2–5 % of pixels, as on the test tile.

**The run:** pass B 20:57 → 03:17, **6 h 20 min** for the 242 remaining tiles; the two-pass mosaic 03:17 → 03:22;
scored and seam-checked by 03:31. **`Global60\global60_landforms_unet_200m_seamfix.tif`**: **49.4 %** of the
classified pixels from pass B, A and B **differing on 2.7 %**; Crater 52.2 %, Normal Ground 42.2 %, lava tube 4.74 %,
hills 0.84 % (`logs\dl_unet_global_mosaic_seamfix.json`).

| | one pass (§66.7) | **two passes** | SVM 11 × 11 (published) |
|---|---|---|---|
| held out | 98.8 %, κ 0.979 | **98.9 %, κ 0.980** | 73.8 %, κ 0.583 |
| held-out user's: Crater, hills, lava tube, Normal Ground | 99.1, 94.5, 75.5, 99.9 % | 99.1, 95.1, **77.1**, 99.9 % | 93.3, 50.7, 2.4, 80.3 % |
| polygons won: Crater, hills, lava tube, Normal Ground | 119, 16, 20, 16 | 120/124, 16/16, 20/21, 17/22 | 107, 14, 8, 20 |
| training polygons | 99.3 %, κ 0.986 | 99.3 %, κ 0.987 | 86 %, κ 0.74 |
| IAU craters, n 817: inside / ring | 91.2 / 82.4 % | 91.3 / 82.6 % | 56.8 / 46.2 % |
| elevation bins alone reproduce | 67.9 % | 68.0 % | 55.4 % |
| verify seam ratio, 4,096 px (100 m / 200 m) | 5.53 / 5.75 | **1.14 / 1.18** | 1.00 / 1.01 |
| `--seams` 256 px, columns / rows | 8.58 / 9.20 | **1.22 / 1.20** | 1.01 / 1.03 |
| class changes per pixel pair | 0.0114 | 0.0114 | 0.0229 |

(`logs\global60_classification_check_global60_landforms_unet_200m_seamfix.json`, `logs\dl_seams.json`.) The
residual 256 px ratio, 1.2, still peaks at phase 255: where pass B gives no class, pass A's pixel stays. The
`--seams` 4,096 px row ratio, 2.06 at phase 2,795, sits one row from the SVM maps' own peak (1.43 at 2,794 and 2,795
is not a tile edge of either map: a feature of the stack, not of the classifier). Drawn at full resolution, the
2,048 px window of §66.7 has lost its straight class boundaries.

**Every prediction held:** seams 1.22 / 1.20 and 1.14 / 1.18, both under 1.5; held out +0.1 point; crater test and
elevation within 0.2 point; A and B differ on 2.7 %. **Reading:** the second pass removes the tile seams and changes
nothing else that the record measures: the map remains a terrain-province map (§66.7), now without the defect that
made it unfit to publish. **Open for the author:** whether it replaces the SVM map as the published one or stands
beside it; a layout, and its place in the gdb and the `.aprx`; the scratch tiles (`C:\MarsScratch\x5c\global\tiles\`,
`tiles_b\`) to the Recycle Bin on the author's word.

### 66.9 The U-Net map in the project beside the published SVM map; layout 17 — 2026-10-21 **[V]**

**The author's decision, 2026-10-21:** the SVM map (11 × 11, §57) stays the published landform map; the two-pass
U-Net map (§66.8) goes into the project beside it as the terrain-province map, with a layout of its own.
`build\make_unet_map.py` (Pro closed; `.aprx` backed up to `.backups\Mars Project 20261021-170556.aprx`; rehearsed
twice on a copy beside the `.aprx`, the copy then moved off the drive):

- **The two U-Net rasters' attribute tables** gained `Classvalue`, `Red`, `Green`, `Blue`, as the SVM maps carry
  them, so Pro draws them in the class colours; `make_dl_pixels.py --mosaic` now writes them itself.
- **`DL_UNet_Heldout_Scores_20261020`**, 183 polygons: the held-out labels, each with its own-class share and majority
  class under the U-Net and under the published SVM map, scored at 400 m with `svmcheck.training_score` on each 15°
  block's window. **Checked:** summed area-weighted, they give **0.9893** and **0.7383**, the two maps' held-out
  accuracies (§66.8, §57), and the script stops if they differ by 0.002; polygons whose own class holds more than
  half: **U-Net 173, SVM 149**, the per-class counts of §66.8 (120 + 16 + 20 + 17) and of §66.7's SVM column
  (107 + 14 + 8 + 20); no polygon lacks a score under either map. The raster itself stays in `Global60\`, as every
  ±60° product does; the gdb holds the records.
- **Map "X5c — U-Net terrain provinces (±60°)"**, 9 layers, top to bottom: the 30° graticule, the held-out labels
  outlined in their class colours over a white halo, the training labels (off), the ±60° extent, the two-pass map at
  30 % transparency, the one-pass map (off), the published SVM map (off), the hillshade.
- **Layout `17_x5c_unet_provinces`**: frame A, the map over ±60° with the area shares (Crater 55 %, Normal Ground
  39 %, lava tube 4.7 %, hills 1.0 %); frame B, the held-out block with the most classes (3; 31 polygons;
  270–285°E, 15–30°N); the two maps under the same scorer (held out, polygons won, user's accuracy per class, the
  IAU crater test, elevation bins, seams), every figure read from the logs at run time and kept in
  `logs\dl_unet_sheet.json`; what it is (terrain provinces; lava tube usable) and is not (single features); the
  SVM map named as the published one. **Reading the rehearsal found** the subtitle running past the margin
  (shortened), the held-out outlines invisible where the map agrees with them, a class colour on the same colour
  (a white halo layer added under them), and the grey no-data streaks unexplained (a note added). Thin polygons
  still show only their outline at the frame's scale; at full resolution (rendered separately) the 15 lava tube
  polygons of frame B's block lie inside or along a lava tube province covering 38 % of their window, all 15 own
  class 1.00 in the records.
- **Built on the real `.aprx`**: `polish_layouts.py` changed nothing on 01–16 and gave 17 Arial and 11 pt legend
  headings; the polished export is pixel-identical to the rehearsal's that was read, copied into
  `Global60\layouts\`. `arcpy.mp`: **32 maps, 17 layouts**, 0 broken data sources. 30 feature classes.

### 66.10 The interim gains two deep-learning slides; release `data-2026-10-21` — 2026-10-21 **[V]**

At the author's request ("do both": a deep-learning slide in the interim, and the GeoPackage republished as a new
release). On the desktop; nothing measured, no raster or gdb class written.

**The interim** (live files backed up to `NEXT STUFF\.backup_20261021\`):

- `interim.py`: two figure entries after the T1 slide, "Deep learning, 1: a detector that draws boxes" (layout 16;
  X5's held-out recall and precision against the one-class baseline, §66.2; X5b not improved, §66.5) and "Deep
  learning, 2: a U-Net maps terrain provinces" (layout 17; 98.9 %, κ 0.980 against the SVM's 73.8 %, κ 0.583; lava
  tube user's 77.1 % against 2.4 %; 'Crater' on 82.6 % of the ring round named craters, so provinces, not features;
  the SVM map stays the published one, §66.8–66.9). The status date is 21 October; the progress row says 17 layouts;
  the log gains "19–21 Oct" (the 2 and 3 Oct rows merged, so the slide keeps 13 rows); the deep-learning next step
  now names the validation-block split (§66.5); the schedule lists the U-Net. `verify_interim.py`: all **277**
  numbers in this record.
- `make_interim_figs.py --only <layouts>` exports just the named sheets (the others' exports kept, so 08's crop
  still predates its recentring, §64); `findings` (16, 17) joins the hidden prose. Its legend crop now adds the
  white margin instead of cropping it: on 16 and 17 frame A ends 0.03 in from the legend, and the 12 px margin
  showed a strip of the map.
- `build_interim_live.py`: a figure with `map_left=True` puts the map (frames A over B, aspect 1.20) at full height
  on the left and the takeaways, then the legend, on the right. The first build ran the map across the full width:
  half the picture was the white space where the sheet's table had been, the legend was a thumbnail and slide 22's
  last takeaway ran into the source line. 05 and 11 also have tall maps; they keep their layout (opt-in flag).
- **Rebuilt: 30 slides, the report 21 pages, 21 figures**; rendered through PowerPoint and Word and compared page
  by page with the previous build. Changed: the title (date), slides 3–4 (no content change: PowerPoint moved table
  text by a pixel), 5 (17 layouts), 6 (the log), the two new slides 22–23, 29 (next steps), 30 (schedule); every
  other slide only in its footer. Report: pages 1–3, the two new figures (15, 16), figure numbers after them, the
  last page. All changed pages read; the log's new row first wrapped to the slide's edge and was shortened.
- The deck now shows 13 of the 17 layouts (not 03, 14, 15; 13 as its table, figure `t8_enrichment.png`).

**Release `data-2026-10-21`** (`github_export_gdb.py --rasters-only`, then `github_release_bundle.py --upload
data-2026-10-21`, log `logs\release_data-2026-10-21_DESKTOP-PJS73RO.log`; 18:38–19:03, the upload ~18 min):

- **12 assets, 7.71 GB**: `typearea-part1..3`, `athabasca.zip`, `global60-classification-part1/2`, **`dl-models.zip`**
  (new: `Mars Project\DLModels\` whole, 218 files, 864 MB: the X5, X5b and X5c models with `.pth`, `.emd`, `.dlpk`,
  loss graphs, sample results and X5's held-out detections), `npy-caches.zip`, the GeoPackage (28 classes, with
  `DL_UNet_Heldout_Scores_20261020` and `DL_Detections_heldout_20261019`; staged 17:13 after §66.9), the two
  `Classified_*.tif` (exactly the 10-19 sizes), `SHA256SUMS.txt`. The classification group now takes
  `global60_landforms_unet*` too: both U-Net maps are in part 2; part 1 still holds the published `_mode11` map.
- **The zips are 8–10 % smaller than 10-19's** with the same file counts (`typearea-part1` 920 MB against 1,020 MB,
  `athabasca.zip` 819 against 918): the compression differs on this machine's Python, the content does not. The
  old releases' central directories, read by HTTP range requests, give every entry's name, size and CRC: the
  type-area, Athabasca, caches and classification part 1 entries are identical but for three re-exported type-area
  layout PNGs (01–03); part 2 adds the ten U-Net files and the updated `Global60\README.md`.
- `restore.py` unzips `dl-models*` into `Mars Project\` (dry run: the newest data release, 82.1 GB with the
  derivatives). `tools/check_remote.py`: **83 release assets, 4 source mosaics, all pass**. The README quick start
  rerun on the new release: part 1 downloaded, its `_mode11` map has the drive copy's SHA-256.
- **Pointed at it:** `github_catalog_rasters.py` (`DATA`; the two U-Net maps described; `docs/rasters.md`
  regenerated, 0 rows on the old tag), `github_export_gdb.py` (`RELEASE`; `--catalog-only` rewrote
  `exports/README.md`, the two release-only rows in a new order), the README's quick start and backup section,
  `docs/backup.md` (the `dl-models.zip` row), `CITATION.cff`. `data-2026-10-19` and the older releases are kept.

## 67. The layouts and images audited; the interim's layout crops re-exported — 2026-10-22 **[V]**

On the desktop, at the author's request to audit that the layouts and images are all in place.

- **The 17 sheets match their PNGs.** `arcpy.mp` on `Mars Project.aprx`: 32 maps, 17 layouts, each 11 × 8.5 in.
  Every layout exported at 150 dpi to scratch is pixel-identical to its PNG in `TypeArea\layouts\` (01–03) and
  `Global60\layouts\` (04–17), and those are byte-identical to the repo's. `github_sync.py --dry-run`: 0 to copy,
  961 unchanged; the six model weights over 95 MB are the release's `dl-models.zip` (§66.10). `tools/check_repo.py`:
  347 links, 81 images indexed, all pass. Layouts 16 and 17 are drawn in GCS_Mars_2000 centred on 0°E like the other
  ±60° sheets; 01–03, 06, 09, 14 and 15 on the CM 180° equidistant cylindrical grid.
- **The interim's crops were stale.** `make_interim_figs.py` run with its output in scratch, compared with
  `build\interim_img\`: 12, 16 and 17 identical; 01, 02 and 04–11 not. 08's crop predated its recentring (§64), 07's
  legend still gave the size classes before §65's rounding (20–41 … 1027–2697 km), 09's map was the smaller frame
  before §64; the others differed in 0.3–7.5 % of their pixels. The author's decision the same day: refresh them
  (reversing "leave the deck as it is", §63).
- **Re-exported and rebuilt:** `make_interim_figs.py` (all 13 layouts), the deck (30 slides) and the report
  (21 pages, 21 figures); the live files backed up first to `NEXT STUFF\.backup_20261022\`. `verify_interim.py`: all
  277 numbers in this record. Rendered through PowerPoint and Word and compared page by page with the previous build:
  the text is unchanged but for the report's date line; the pictures changed on slides 9 (08, now centred on 0°E),
  10 (01–02), 13 (07's legend), 16 (06) and 17 (09, the larger map of §64), and on report
  pages 4, 6, 10 and 11; every other slide by under 2 % of its pixels, with the same text. Every changed slide and page
  read. The crops now show the sheets as they are.
- **Stale statements corrected:** the README's "16 map sheets" (17); `docs/figures.md`'s "15 sheets", its list of the
  ±60° sheets (16 and 17 added) and its note that 08's crop predates the recentring; `HANDOFF-DESKTOP.md`'s layout
  range (04–17); `INTERIM-PLAN.md`'s open item on 08's caption naming Tharsis (fixed in §63; no text element of any
  layout names Tharsis, read with `arcpy.mp`) and its line that deep learning has no slide (two since §66.10).
- **The review:** `accept_reviewed.py`, dry run: 0 of 9,287 candidates reviewed (2,610 and 1,685 at Ius, 3,283 and
  1,709 at Athabasca); nothing for `NEXT-STEPS.md` §3.

### 67.1 The repo's pages: previews, alt text, a deep-learning section — 2026-10-22 **[V]**

At the author's request to refine the repository itself. `tools/check_remote.py` first: 83 release assets and the
four source mosaics, all pass.

- **Page weight.** The README showed 34 images, 25.5 MB, the layouts as full 150 dpi PNGs; `docs/figures.md` 46,
  36.1 MB. New `tools/make_thumbs.py` (repo only, Pillow) writes an 800 px JPEG for every image `docs/figures.md`
  links that is over 300 KB, 31 previews, 2.7 MB in all, into `docs/thumbs/`, and records each source's SHA-256 in
  `docs/thumbs/SOURCES.txt`; the three models' `show_results.png` take their model folder's name. The pages show
  the preview and link the full file: **3.2 MB and 4.1 MB**. Previews read: legible as previews, colours kept.
- **Alt text.** The README's 17 layout images had the sheet number as alt text; 46 images in `docs/figures.md` had
  none. Each now carries its row's own caption ("Layout 07: Basin and crater candidates ≥ 20 km").
- **`tools/check_repo.py`** (CI) gains two checks: every image a page shows inline has alt text of 8 or more
  characters and is at most 300 KB; every preview's source still has its recorded SHA-256, and every preview is in
  the manifest. Each proved on a planted defect in a scratch copy (alt text "07", a full layout shown inline, a
  byte appended to layout 04, a stray preview): all four failed as they should.
- **README:** "Where it stands" dated 2026-10-22; the deep-learning paragraph moved from the next steps (done work)
  to a results section "Deep learning (X5)" with layout 17's preview; the next steps name the 1 November
  contingency (`NEXT-STEPS.md` §6); the folder tree adds `Athabasca/`, `DLModels/`, `docs/figures.md`,
  `docs/thumbs/` and `tools/make_thumbs.py`. `CITATION.cff`'s abstract names the deep-learning models.

### 67.2 A writing pass over the pages and the sheets: named patterns only — 2026-10-22 **[V]**

At the author's request to remove AI-sounding prose ("slop") from the repo and the layouts. Method: the
`no-ai-slop` checklist (named patterns, minimum edit) with its fact-binding rule (every number, unit and name kept
byte-identical; a "X, not Y" that states a method limit is kept, e.g. "routed flow paths, not mapped valleys",
"local contrast, not calibrated thermal inertia", "not a crater count": those are the record's wording rules, §12).
A word scan of the README, `docs/`, `exports/README.md`, `CITATION.cff`, `Global60\README.md` and every visible
text element of the 17 layouts (dumped with `arcpy.mp`) found no banned vocabulary, puffery or "-ing" commentary;
what was there was structural.

- **Layouts** (the builders edited too, so a rebuild reproduces the text; applied to the `.aprx` by element after
  a backup to `.backups\`, each old string asserted to occur once, saved and re-read; `polish_layouts.py`; all 17
  exported and compared; every changed sheet read; copied into the layout folders):
  - 16 titles and 05's two panel headings: the em dash separator became a colon ("Mars ±60°: landform
    classification"). Map and layer names keep theirs: scripts look them up by name.
  - 08: the rhetorical opener "Why all three:" cut.
  - 11 and 16: "do NOT agree", "NOT comparable" in lower case (capitals as emphasis).
  - 13: "a coherent terrain map, not a lava-flow map" (colon reveal, evaluative adjective) became "The classes map
    terrain; lava flows come from the geologic map".
  - 16: two colon reveals ("…before the run: a measurement, not a test of a hypothesis. Windows, not a mask: …")
    became plain sentences; the tool ran in one window per block because a mask made it fail.
  - 17: "What it is: … What it is not: …" (negative listing) became "The U-Net maps terrain provinces. … but it does
    not map single features: …".
  - Builders edited: `make_typearea_layouts.py`, `make_global60_maps.py`, `make_candidate_maps.py`,
    `make_mosaic_layout.py`, `make_reference_maps.py`, `make_global60_candidate_sheets.py`, `make_geomap_sheet.py`,
    `make_validation_sheet.py`, `make_athabasca_layout.py`, `make_dl_map.py`, `make_unet_map.py`.
- **The deck:** its crops hide titles and notes, so only 05's (its panel headings show) changed: re-exported with
  `--only 05_svm_checks`, the deck and report rebuilt (live files to `NEXT STUFF\.backup_20261022b\`), slide 28 and
  report page 20 changed and read; the text of both documents unchanged; `verify_interim.py`: 277 numbers.
- **Pages:** the README ("Three coordinate frames, not two:" a binary-contrast opener; "not just the craters"; four
  emphasis bolds mid-sentence), `Global60\README.md` (the verdict "That is the whole point of the folder", six em
  dashes, five emphasis bolds, "This is a *relative* index"), `docs/backup.md` (a sentence with two colons).
  Previews rebuilt (`tools/make_thumbs.py`).
- **Not edited:** this record and the plans (an internal log), the scripts' docstrings (`docs/scripts.md` is
  generated from them), the interim deck's text (`interim.py`, the author's). Kept as voice: "Yes, a little.",
  lower case after a colon, "just" where it means "only".

### 67.3 The script catalogue regrouped; stale docstrings; the pipeline diagram — 2026-10-22 **[V]**

A further review of the repository at the author's request.

- **`docs/scripts.md`'s groups.** Its last group, "Reading the geodatabase and rasters", was `github_sync.py`'s
  catch-all and held 59 of the 153 scripts: seven layout builders, eleven tests, the deep-learning scripts, the
  review, the interim's own builders and the drive plumbing. `GROUPS` gains "Tests T1–T8 and the class checks" (13),
  "Deep learning (X5)" (5), "Digitising by review" (3) and "Drive, paths and one-off fixes" (10); the layout
  builders join "ArcGIS project: maps and layouts" (17) and the interim's scripts "Deliverables and their checks"
  (30); the remainder (13: reference layers, file readers, column checks) is "Reference data, readers and
  diagnostics". 153 listed, as before.
- **Stale first lines** (the catalogue shows each docstring's first paragraph): `polish_layouts.py` said "the seven
  layouts" and "the three layout builders" (it runs over all 17 after any builder); `make_validation_sheet.py`,
  `add_review_fields.py`, `accept_reviewed.py`, `housekeeping_d9.py` and `make_lava_relabel_test.py` cited
  `NEXT-STEPS.md` items (3.6, 3.7, D6, D9, D10) that moved to this record's §50 when the plan was condensed;
  `verify_interim.py` cited item 6 of `INTERIM-PLAN.md`'s first section, which no longer has numbered items. `HANDOFF-DESKTOP.md`'s builder order adds
  `make_dl_map.py` and `make_unet_map.py`.
- **`docs/pipeline.svg`** gains a result box, "U-Net provinces (X5c), 98.9%, κ 0.98, held out", fed by the
  hand-drawn labels beside the SVM; rendered with headless Edge and read.
- **Checked, no change needed:** `restore.py --dry-run` into scratch lists the newest data release and the
  derivatives, 82.1 GB (`docs/backup.md` says about 80 GB); the repository's description and topics; the licence.

### 67.4 The pages' numbers against this record; anchors; the drive's size; spelling — 2026-10-22 **[V]**

- **Every number on the public pages** (README, `docs/figures.md`, `docs/backup.md`, `Global60\README.md`,
  `CITATION.cff`) run through `verify_interim.py`'s own matcher against this record: all held except three. The
  X5b loss "428" rounds this record's 428.1 (§66.5); the DEM's "11.4 GB" is decimal where §3 gives 10.60 GiB, the
  same file (§3 now says its "GB" are GiB); the drive's "about 390 GB" was nowhere in the record and is stale.
- **The drive, measured** (`Get-ChildItem -Recurse`, decimal GB): `Mars Project\` 364.1 (`Mars Project.gdb`
  225.0, `Global60\` 123.6, `LabeledObjects\` 7.7, `TypeArea\` 3.4, `Reference\` 2.4, `Athabasca\` 1.2,
  `DLModels\` 0.9), the source GeoTIFFs 62.1, `Mars Remote Sensing Project\` 2.5 (`.npy` caches 1.98): **428.7 GB,
  399.3 GiB**. §2's table said 112 MB, ~58 GB and ~300 GB and is updated; the README says about 430 GB.
- **"#section" links:** all 12 on the pages resolve to a heading. `tools/check_repo.py` now checks them against
  GitHub's heading slugs (proved on three planted defects, on the same page and in this record).
- **Spelling:** the pages write British English ("colour" 5 times, "catalogue" 14, "metres", "centred"); the
  README's opening, `CITATION.cff` and `docs/pipeline.svg` said "color", and "layer catalog" appeared five times.
  Made consistent; the `--catalog-only` option keeps its name.
- **The clone's `.git`** holds two pack files with no index, `pack-c444774…` (50 MB) and `pack-d8f33e5…`
  (126 MB), dated 2026-10-16 and stored by OneDrive as placeholders; git skips them with a warning. Neither was in
  the multi-pack index; `git count-objects -v` counted them as garbage (2 files, 172,591 KiB). At the author's yes
  they were deleted with `SendToRecycleBin`: being online-only OneDrive files, they did not appear in the local
  Recycle Bin (3 items, none of them), so any copy is in OneDrive's online recycle bin, not checked. After:
  garbage 0, `git multi-pack-index verify` and `git fsck --full` exit 0 (dangling blobs only), HEAD = origin/main.

### 67.5 The interim deck's two small legends enlarged — 2026-10-22 **[V]**

`INTERIM-PLAN.md`'s open deck item: the legends on the 05 and 07 slides were too small to read. Measured in the
built deck (points of slide per pixel of the 200 dpi crop): 05's at 0.29, beside a map 322 pt wide; 07's at 0.20,
about 4–5 pt text, smaller than before §67 because 07's rounded legend (§65) is one tall column (399 × 409 px,
earlier 744 × 346). Two layout flags in `interim.py`, no wording changed:

- 05 (two maps stacked, aspect 1.11) takes `map_left=True`, the layout of 16 and 17 (§66.10): the maps at full
  height on the left, 408 pt wide, the takeaways and legend on the right; legend 0.62 pt/px.
- 07 (aspect 2.92) gets `map_h=230`, a new per-figure cap in `build_interim_live.split_legend` on a full-width
  map's height (290 pt otherwise): the map 230 pt high, the legend 0.33 pt/px.
- The deck rebuilt (live file backed up to `NEXT STUFF\.backup_20261022c\`), rendered through PowerPoint and
  compared with the previous build: only slides 13 and 28 changed; both read. The report places whole crops and
  was not rebuilt. `verify_interim.py`: 277 numbers.

## 68. The class scheme revised (D17); the 512 labels audited — 2026-10-22 **[V]**

On the laptop, without the drive (only `C:` mounted), at the author's request. Read from a scratch copy of the
repo's `exports\mars_project_vectors.gdb` with the laptop's ArcGIS Pro Python; nothing on the drive or in the
gdb was written. **The object IDs below are the export's**; match them on the drive by geometry before acting.

### 68.1 The author's revision, and the decision (D17)

The author's notes: "lava tube" ≠ volcanic edifices ≠ craters; Crater means impact only; steep/windy hills
could be an apron, and aprons (water and water ice) must be told apart from lava tubes; a fluvial class
("fluvial tubes": water-cut sinuous channels, inverted channels, eskers and fluvial pit chains, all of them);
volcanic plains count as Normal Ground. Answers the same day: aprons cover both the mid-latitude lobate debris
aprons and the Tharsis fan-shaped deposits; the revision lands **before the interim**; **the agent proposes, the
author accepts**, and the existing 512 are audited so that no mistake or overlap gets through.

This reverses §43.3's "no fifth class" for a scheme the author defines, not for the geologic-map relabel that
failed there; the held-out rule stays (§68.4). Codes 1–4 keep their numbers (the swap trap, §29.2):

| code | class | what it holds |
|---|---|---|
| 1 | Crater | impact craters only, any state of preservation; no calderas, no volcano summits |
| 2 | steep/windy hills | high relief that is no impact crater, volcano or apron: massifs, chasma walls, knobs, mesas |
| 3 | lava tube | volcanic conduits and collapses at km scale: pit chains (catenae), sinuous rilles, lava channels; a tube itself, tens to hundreds of metres wide, is below the 200 m grid |
| 4 | Normal Ground | plains, **volcanic plains included** |
| 5 | volcanic edifice | montes, tholi, paterae: shields, flanks, calderas, cones |
| 6 | apron | lobate debris aprons (ice-rich, mid-latitude) and the Tharsis fan-shaped deposits; the Olympus Mons aureole (Lycus, Gigas, Sulci Gordii) is included with its origin open **[?]** |
| 7 | fluvial channel | water-cut sinuous channels and valleys; `Subtype` records inverted channel, esker or fluvial pit chain, so a subtype can become its own class once it has the polygons |

The record already pointed this way: "lava tube" sits on the geologic map's apron units (×4.12) and volcanic
edifices (×3.34), not on volcanic plains (×0.87, §43.2); 75 % of volcanic plains already come out Normal Ground
(§43.3).

### 68.2 The audit of the 512 labels

`label_audit.py` and `label_audit2.py` (agent scratch, read only):

- **No two polygons of different classes share ground.** 136 pairs overlap, all within one class: 9 polygons
  lie ≥ 95 % inside another (Crater 51 in 50, 53 in 52, 167 in 166, 182 and 183 in 181, 214 in 213; lava tube 336
  in 334; Normal Ground 350 in both 347 and 348); 127 overlap in part, 117,819 km² shared, most of it three
  large Normal Ground polygons (468, 469, 471, ~80,000 km² between them). A crater inside a basin is a real second
  crater; 350 inside 347 and 348 adds nothing but a second count. The polygon scores ("polygons won") count
  every overlapping polygon separately.
- **One train/test leak:** label 290 (hills, training, block −6_−1) and 291 (hills, held out, block −5_−1) share
  51.5 km² across the −75° block edge (−75.5°E, −2°). The split assigns whole polygons to blocks (329 + 183 =
  512, none cut), so a polygon can cross into the next block. No other held-out polygon touches a training one.
- **Crater polygons that are volcanoes** (five in all, §68.5: also 464 Pavonis Mons, 19 Tharsis Tholus and 20
  Ulysses Tholus): label **22** (held out, block −9_−1), 73,939 km², holds Arsia Mons and
  Arsia Chasmata and no named crater: **31 % of all held-out Crater area** (240,581 km²). Label **465**
  (training, block −7_0), 52,953 km², holds Ascraeus Mons: 18 % of training Crater area (289,146 km²). The SVM
  learned part of Crater from a volcano, which fits Crater ×1.20 on the volcanic edifices (§43.2). Hills 507 holds
  Nectaris Montes, a Valles Marineris massif, rightly hills.
- **The 44 lava-tube polygons:** 38 in Tharsis, chains of 3–109 km² beside Labeatis Catenae, Labeatis and
  Uranius Fossae and Tractus Catena, a group east of Olympus Mons by Gordii Fossae, and two large ones in north
  Tharsis (4,018 and 13,251 km², label 334, around 252.8°E 23.3°N) that look like flow fields or edifice
  ground **[?]**. **Six sit by fluvial valleys:** three in Xanthe Terra by Hypanis and Tyras Valles (training,
  block −4_0) and three in NE Arabia by Auqakuh and Huo Hsing Valles (held out, block 4_2).
- **Attributes:** 511 labels carry Classcode " " and their class colour; label **512** (Crater, 1,061 km²,
  241.96°E 19.83°N, 97 km from Jovis Tholus) has Classcode "" and colour (168, 0, 0): added by hand after
  `new training.shp` (§29.2). Its class is unchecked against the crater catalogue **[?]**.
- **Geometry:** `CheckGeometry` finds nothing; 29 polygons are multipart (lava tube 11, Normal Ground 14,
  hills 4), chains drawn as parts; 82 are under 25 km² (625 cells of 200 m), 33 Crater polygons under 5 km across.
- **Balance across blocks:** hills train in 2 blocks (27 of 28 in −6_−1) and are held out in 3; lava tube in 4
  and 3, its held-out area 2,495 km², 15 of 21 polygons in block −6_1.

### 68.3 Where each new class can be held out

The 14 held-out blocks stay as drawn in §31.3. Named IAU features (all five nomenclature layers; the
"classical albedo" one holds most volcanoes and mensae) by the block their centre lies in:

| class | held-out blocks | training blocks, or no labels yet (training) |
|---|---|---|
| volcanic edifice | Arsia Mons (−9_−1); Biblis Tholus and Patera, Ulysses Tholus (−9_0); Nili Tholus (4_0) | Olympus, Ascraeus, Pavonis Mons, Jovis, Uranius, Ceraunius, Tharsis Tholus; Elysium |
| apron | Arsia Sulci, the Arsia fan (−9_−1); Gigas Sulci, the aureole (−9_0); Nilosyrtis Mensae (4_2) | Pavonis Sulci, the Ascraeus fan; Sulci Gordii, Lycus Sulci; Deuteronilus and Protonilus Mensae |
| fluvial channel | 17 valleys: Auqakuh, Huo Hsing (4_2); Ravi, Tigre, Columbia, Daga (−3_−1); Napo, Huallaga, Vichada (5_−2); Allegheny, Elaver, Walla Walla (−4_−1); Dittaino, Sepik (−5_−1); Arnus (4_0); Her Desher (−4_−2) | 30 named valleys, e.g. Nanedi, Hypanis, Shalbatana, Nirgal, Uzboi, Ladon, Mawrth |
| lava tube | Labeatis Catenae and the existing 15 (−6_1) | Tractus and Ceraunius Catenae; Elysium catenae |

Valles Marineris labes are landslides and its mensae interior layered deposits: neither is an apron.

### 68.4 How the revision is carried out (planned; `NEXT-STEPS.md` §11)

- **Proposals, never edits:** a new class `Landform_TrainingSamples_v2_proposals` holds the 512 as copies
  (`OldOID`, `OldClass`) and the agent's new polygons, each with `Action` (keep / relabel / clip / delete / new /
  fix), `ProposedClass`, `Subtype`, `Reason`, `Evidence`, and the author's `Review` (accept / reject / unsure) and
  `ReviewNote`. `Landform_TrainingSamples_terrain` is never written. An apply script builds `_v2`, `_v2_60_train`
  and `_v2_60_test` from accepted rows only.
- **Evidence per polygon, from the drive:** SIM 3292 unit-group shares; the largest Robbins crater inside against
  the polygon's size (a Crater polygon with none near its size is flagged); relief and slope from the stack; shape
  (elongation, for classes 3 and 7); the IAU names (§68.2).
- **The split:** the same 14 held-out blocks; a polygon goes to the block holding its centroid; blocks with no
  label so far are training; no polygon may share ground with one in the other split (290/291 clipped).
- **Minimum per new class:** ≥ 10 held-out polygons in ≥ 2 held-out blocks and ≥ 20 training polygons in ≥ 3
  training blocks. Hills meets it only in part today (2 training blocks).
- **Verdict rule, written before any run (D18, the author's word 2026-10-22: both maps go in the interim; the
  seven-class map is expected to supersede for the final if it scores well):** both the four-class map and the v2
  map are scored on the v2 held-out polygons by the §55.3 scorer. The v2 map replaces the published one only if (a)
  its overall accuracy and κ are at least the four-class map's (**amended by D19, the author's answer 2026-10-24,
  before any v2 score existed: on the held-out polygons whose v2 class is 1–4**, the ground both maps can name,
  §68.6, §69.4), (b) each new class's user's accuracy exceeds its
  share of held-out area, and (c) Crater, hills and Normal Ground producer's accuracy each fall by under 5 pt.
  Otherwise the four-class map stays published and v2 is reported as a test. 73.8 %, κ 0.58 stays the record of
  the four-class labels.

### 68.5 The proposals script, run and tested on the laptop — 2026-10-22 **[V]**

The author approved the downloads. On the laptop, into scratch: the repo's gdb export, with `Ref_SIM3292_GeologicUnits`
and `Ref_Craters_Robbins2020` rebuilt by `make_reference_layers.py`'s own functions from fresh downloads
(`sim3292_database.zip` 808.9 MB, 1,311 units; the Robbins 2020 zip 39.4 MB, 385,049 craters: both as §41
records the drive's); the DEM downloaded whole (11,384,463,908 bytes, the drive's size in `tools/check_remote.py`).
**New source:** Alemanno & Orofino (2017), "Global map of Martian fluvial systems", Zenodo
10.5281/zenodo.1051038, CC BY-SA 4.0: 3,772 valley polylines, 714,434 km, typed Single Valley / Valley
Network, with ages; `Giulia Valleys.shp` SHA-256 bf853acd…6e306715 (the script checks it). Levy et al. (2014)'s
debris-glacier outlines are behind a bot check on Wiley's site and were not fetched.

- **The apron units of SIM 3292:** `ANa` is the mid-latitude debris-apron terrain (Deuteronilus and Protonilus
  Mensae, the Hellas east rim, Tempe); `lAa` the Tharsis fan-shaped deposits (Arsia, Pavonis, Ascraeus);
  `Aa` the Olympus aureole **and the Valles Marineris landslides** (Ius, Coprates, Ophir Labes, Candor Chaos),
  which the script keeps out of class 6. No apron unit lies in a held-out block except the Tharsis ones: held-out
  aprons are the Arsia fan and Gigas Sulci; lobate debris aprons are training only unless drawn in block 4_2.
- **`propose_label_changes.py`** (third run, 701 s; 1,086 rows, the map "Labels v2: proposals" built in a copy
  of the `.aprx`): the split's centroid rule reproduces all 183 / 329 assignments. On the 512:
  - **relabel 12:** five Crater polygons are volcanoes, to 5: **22 Arsia Mons** (held out), **20 Ulysses
    Tholus** (held out), **464 Pavonis Mons**, **465 Ascraeus Mons**, **19 Tharsis Tholus**: each a circle round
    the volcano, under 8 % inside catalogued craters; five lava-tube polygons to 7 (304–306 Xanthe, 436–437 NE
    Arabia, 26–82 km of mapped valley each); 334 and 335 (13,251 and 4,018 km², all on volcanic plains, no
    catena) to 4, each with the lava-tube chain inside it (336, 337) cut out and kept.
  - **check 23:** 15 Crater polygons under a quarter inside catalogued crater rims (mostly small craters drawn
    with a wide margin; two under 1 km, below the catalogue's floor; 21, 16,013 km², no named feature near);
    seven lava-tube chains 318–324 on `eHh` near Uranius Fossae (tectonic pit chains?); 435 on `mNh` (fluvial?).
  - **clip 1** (290 by 291), **delete 1** (350), **fix 1** (512: a real crater, 75 % inside a 32 km one).
  - **new 574:** 276 valley strips (2.4 km wide, ≤ 6 per held-out and 2 per training block), 172 apron and 126
    edifice pieces (3° pieces of SIM 3292 units, inset 5 km).
  - If every proposal were accepted: no overlap between classes or across the split; classes 5–7 meet §68.4's
    minimum (edifice 12 held out in 3 blocks, apron 22 in 3, fluvial 46 in 10); **hills (2 training blocks) and
    lava tube (18 training polygons) do not**: both need polygons drawn in more training blocks.
- **Read by eye** (16 sampled proposals over hillshade): the relabels and valley strips sit where their reasons
  say; the unit pieces are coarse (a Protonilus `ANa` piece holds mesas and plains, an Alba Mons edifice piece
  is nearly flat): their reason asks the author to trim them to the landform before accepting.
- **Tests** (scratch copies): a proposals class holding one review is not replaced; a full accept applies
  (`apply_label_review.py`: 1,085 labels, 827 training + 258 held out); planted defects refused: the clip of 290
  rejected (51.5 km² across the split) and 334 accepted with its uncut outline (138.5 km² over lava tube 336).
- The first run found the two rule errors the third fixes: a broad relabel overlapping a chain that keeps its
  class, and a nested polygon deleted although its container changes class.

### 68.6 The v2 runs scripted, and rehearsed on the published maps — 2026-10-22/23, laptop **[V]**

At the author's request ("general work without the drive"): every run of `NEXT-STEPS.md` §11.5 steps 2–3 is
now one command (the list is there).

- **`labelsets.py`** holds the two label sets. Default: the four classes and the `terrain_60` split, every name
  as before. `--labels v2`: the seven classes (codes 1–7, colours as `apply_label_review.py`'s), the `v2_60`
  split, `_v2` in every output name. Taken by `make_global60_classification.py` (skips the four-class split;
  refuses to train unless both v2 halves exist, every row is `apply_label_review.py`'s and every code is 1–7;
  its own tile folder, so finished four-class tiles are never reused), `make_global60_landforms_clean.py`,
  `verify_global60_classification.py` (a map without "v2" in its name is written up `…_on_v2_labels`; new keys
  `labels`, `label_area_share`, `confusion_unrounded`), `make_geomap_check.py` (T8), `make_dl_pixels.py` /
  `make_dl_model.py` (work in `C:\MarsScratch\x5c_v2`; `--train` refuses an export from the other label set).
  `svmcheck.training_score` takes the number of classes. Layout code (`make_global60_maps.py`,
  `make_unet_map.py`, the sheets) stays four-class: step 4's work, on the desktop.
- **`score_d18_verdict.py`** applies §68.4's rule (a)–(c) to two scorer outputs and refuses a pair not scored
  on the same v2 polygons. Twelve planted cases pass; the first nine, on their first run, caught a float error: a producer's
  fall from 0.600 to 0.550 computed as 4.99… points and passed (c). Fixed by rounding the fall to the scorer's
  precision.
- **A scratch drive from the release** (`data-2026-10-21`'s classification zips, checksums matched): the 11 × 11
  SVM map and the two-pass U-Net map; the zips hold no overviews, so they were rebuilt NEAREST as the
  originals were; a header-only stand-in for the THEMIS night mosaic (grid60 reads only its grid: 213,388 ×
  71,130 at 100 m, as §3 records); the full-accept test gdb of §68.5 as stand-in v2 labels (258 held out, 827
  training). **Without `--labels`, the edited scorer reproduces both recorded outputs in every value**
  (73.8 %, κ 0.583; 98.9 %, κ 0.980; the crater test, seams, elevation). Output names in both modes printed and
  checked; the v2 split guard refuses a foreign row, a code 8 and a missing class.
- **The scorer's cost.** The v2 valley strips are long and many-vertexed (one spans 23.7° with 148,360
  vertices); the scorer tested every pixel of a polygon's box against every vertex, so the v2 training set cost
  ~127 × the four-class one (3.75 × 10¹² against 3.0 × 10¹⁰ vertex-pixel tests), hours per map. `svmcheck.inside`
  now skips any block no edge touches (one centre decides it), splitting the rest down to 8 × 8 px tested
  centre by centre: meant to give the same pixels, so the same sums. **The first version did not**: matplotlib
  closes an open outline with an unseen last-to-first edge, which the edge test missed; the exactness test
  (fast against every pixel) found 4 of 3,000 random polygons and four-class training polygon 162 (389 px)
  wrong, although both maps' held-out results had come out identical. Fixed by testing edges on an explicitly
  closed copy; then 0 of 3,000 random polygons and 0 of 2,685 real parts (both label sets, both splits) differ,
  and a planted defect (edge test off) is caught (296 of 400). One part, the 148,360-vertex strip, was too costly
  to test pixel by pixel; it is covered end to end: `verify_global60_classification.py --labels v2` on the 11 ×
  11 map gives every value identical, training set included, through the old path (**29,610 s**) and the fixed
  one (**1,305 s**). On the existing labels a whole scoring falls from ~440 s to ~95 s. The
  scorer rebuilt on GDAL alone reproduces both maps' recorded held-out results, confusion included, through the
  fixed path. (For some hours on 2026-10-23 new arcpy processes failed with "The Product License has not been
  initialized", then started again with nothing changed here; a process already running kept working.)
- **Curved outlines:** one hand-drawn label is stored with true curves (512, a training Crater), and 21 v2
  training pieces (the inset unit pieces); no held-out polygon in either set, so no held-out score depends on
  them. Checked with arcpy once the licence came back: label 512 is one circular arc, and `polys()`'s point
  iteration returns its 2 end points, enclosing nothing, so **every recorded training-set score has left
  label 512 out** (in effect 328 training polygons, not 329). Pro's SVM tool reads the true curve, so the
  classifiers did train on it, and no held-out score is touched. The 20 curved v2 pieces iterate to within 1 % of
  their area. Densifying curves in `polys()` would add 512 to the training-set figures (a side diagnostic, §31.3)
  and change recorded numbers, so it is left for the author (`NEXT-STEPS.md` §11.5 step 0).
- **The rehearsal (stand-in labels, not the author's review):** the four-class maps on the v2 held-out polygons,
  same scorer: **SVM 33.6 %, κ 0.227; U-Net 41.6 %, κ 0.280.** Classes 5–7 hold **58 %** of the held-out area
  (edifice 18.3 %, apron 32.8 %, fluvial 6.9 %), mostly the 3° unit pieces, and a four-class map loses all of it
  by construction. **So rule (a) is nearly automatic on such labels**; (c) still guards Crater, hills and Normal
  Ground. `score_d18_verdict.py` reports beside the rule, not in it, accuracy and κ on the ground both maps can
  name (v2 classes 1–4): there the four-class maps score **SVM 79.9 %, κ 0.668; U-Net 98.9 %, κ 0.980**, the
  bar a seven-class map would have to meet. Whether (a) should use that instead is the author's decision
  (`NEXT-STEPS.md` D19). The pieces' share falls as the author trims them to the landforms (§68.5).
- **What the four-class maps call the new ground:** the U-Net paints 98.7 % of the edifice area and 89.5 % of the
  apron area Crater; the SVM splits them among Crater, lava tube and Normal Ground. The four-class "Crater" is a
  province that takes in the Tharsis volcanoes, as §68.2's five volcano labels led it to.

## 69. The final started: an AASTeX paper and the final deck, both builds — 2026-10-22 **[V]**

On the desktop, at the author's request: "start working on the proposed final stuff", a paper in LaTeX with
AASTeX formatting, and the presentation (no further instructions for it; no rubric exists, §50). Built on the
interim's pattern (`NEXT-STEPS.md` §7: one source, figures exported by script) and on the final report outline of
§7. **Nothing new was measured**; every number is quoted from this record or the log it cites. The review is still
at 0 of 9,287, so both documents present the machine products as candidates with their measured scores (§6 of the
plan, the contingency).

- **LaTeX:** MiKTeX 25.12 installed per-user with `winget` (the author chose it over Overleaf), automatic package
  installs on; AASTeX **7.0.1** (`aastex701.cls`, `aasjournalv7.bst`). AASTeX 7 refuses to compile without an
  `\email` for each author: the paper carries the author's school address (§69.1); AASTeX 7 does not print it.
- **The paper:** `NEXT STUFF\Final\paper\mars_global_mosaic.tex` (two-column, 14 pages, 16 figures, 5 tables,
  40 references in `references.bib`), each number with its § in a `%%` comment. Sections: introduction (the
  Athabasca hook, H1–H4), data, methods (the grid, the stack, the index, fill depth and routing, the SVM and its
  block split, deep learning, bootstrap), results, discussion (the hypotheses table, limits), conclusions.
  `build\build_final_paper.py` copies the figures into `figures\` (cropping two deck charts' title strip and KB
  footnote) and runs pdflatex, bibtex, pdflatex ×2: no undefined reference, no overfull box; one wide table floats
  to the page after the references begin. Every page rendered and read; faults found by reading and fixed:
  `deluxetable` turned every table sideways in two-column mode (now `table` + `tabular`), Table 1 ran 57 pt wide,
  the H1 chart unreadable at column width, the AAS style printing ",," and dropping `note` on `@misc` entries
  (now `version`, `publisher`, `url`), "Jr." names inverted.
- **Numbers checked:** `verify_interim.py`'s matcher run over the paper's prose (comments, citations and labels
  removed) against this record plus the three logs it quotes: 302 numbers, all found or rounding from one, the
  only misses being comma-split pixel sizes, 4.25 bn (4,246,732,800, §3), 199.99999 m (§28.2) and a ZIP code.
- **Two charts not drawn before** (`build\make_fig_final.py`, from the logs): `final_img\depressions_vs_robbins.png`,
  precision and recall by minimum diameter beside the 3-diameter chance baseline from
  `logs\global60_candidates_check.json` (run 3: recall 20.4 / 35.8 / 45.8 / 47.8 / 48.1 / 45.8 / 38.3 % at ≥ 1 to
  ≥ 100 km; the §53.4 table's recalls are run 2's); `final_img\svm_vs_unet.png`, producer's and user's accuracy per
  class for the published SVM map and the two-pass U-Net map (§57, §66.8).
- **Layouts:** `build\make_final_figs.py` runs `make_interim_figs.py`'s export (prose hidden in memory, `.aprx` never
  saved) over `final.py`'s figures into `build\final_img\`: 04, 07, 08, 10, 12, 15, 16, 17 (layout 15 shown in a
  deck for the first time). Layout 13 is left out: its T8 table cells are not named like the other sheets' and
  would stay; the T8 chart is used instead.
- **The deck:** `build\final.py` (content, every number with its §) and `build\build_final_deck.py` (the interim's
  slide placement, copied so `build_interim_live.py` is untouched; special slides for the question, the bands and
  the correlation table; `side_h` for a wide figure drawn left) → `NEXT STUFF\Final\Mars Global Mosaic - Final
  Presentation.pptx`, **32 slides**: the question, the mosaic, the thermal pair, landforms, classification (deep
  learning included), the hypotheses, limits, conclusions, what next. Rendered through PowerPoint and every slide
  read; `verify_interim.py final.py`: all 172 numbers in this record; `neutral_voice.py --check` clean on the new
  files. Its labelled lists use ": ", not " — " (§67.2).
- **Build scripts:** five new (`final.py`, `make_final_figs.py`, `make_fig_final.py`, `build_final_paper.py`,
  `build_final_deck.py`): 159 on the drive then (156 `.py`, 3 `.ps1`); in the repo from §69.1.
- **Open for the author:** whether the final should be refreshed after the review and the data freeze (22
  November), as the plan intends.

### 69.1 The laptop's §68 brought to the drive; the final made to agree with it — 2026-10-23, desktop **[V]**

At the author's request: the repo had moved on without the drive (PRs #1 and #2, `cc848db`, `05c697e`: §68, D17
and the v2 scripts), and the desktop's §69 work was not yet committed. This section was first written as "§68" on
the desktop and renumbered when the two met.

- **Repo → drive**, as `NEXT-STEPS.md`'s 2026-10-23 note asks: every file under `Mars Remote Sensing Project\` the
  clone changed since `449cc9a` was checked by `git hash-object`. Nine drive copies (`HANDOFF-DESKTOP.md`,
  `github_sync.py`, `make_dl_model.py`, `make_dl_pixels.py`, `make_geomap_check.py`,
  `make_global60_classification.py`, `make_global60_landforms_clean.py`, `svmcheck.py`,
  `verify_global60_classification.py`) still equalled `449cc9a` and were replaced by the repo's; the four new
  scripts (`apply_label_review.py`, `labelsets.py`, `propose_label_changes.py`, `score_d18_verdict.py`) copied.
  Each copy's hash matches `HEAD`. The record and the plan had changed on both sides: merged by hand (the repo's
  text, this section and the plan's two §69 passages re-applied). The drive's earlier copies are in
  `.backup_20261023\` and `build\.py_backup_20261023\`. Nothing under `Mars Project\` or the drive root differed.
- **The final made to agree with §68** (the author: "facts now, v2 later"): the paper's split sentence said no
  held-out polygon shares a block with a training one; it now gives the centroid rule and the 290/291 overlap
  (51.5 km²). Its limits gain a paragraph on the audit (five Crater polygons on volcanoes, Arsia Mons 31 % of
  held-out Crater area; six lava-tube polygons by valleys; the seven-class scheme and D18's rule, not yet run); the
  deck gains the same limit and a "Seven classes (D17)" next step. The classification results stay four-class until
  the v2 scores exist. The paper's `\email` is the author's school address (the author's choice). Rebuilt: the
  paper 14 pages, no overfull box or undefined reference, 304 numbers checked (the only ones not matched literally:
  comma-split pixel sizes, a ZIP code, and 72.0 % = §57's 0.720); the deck 32 slides, `verify_interim.py final.py`
  174 numbers. The changed pages and slides were read.
- **Repo:** `github_sync.py` groups the final builders under "Deliverables and their checks" and leaves out
  LaTeX's working files (`.aux`, `.log`, `.out`, `.blg`; the `.bbl` stays so the `.tex` compiles without BibTeX).

### 69.2 The label proposals built on the drive (D17, `NEXT-STEPS.md` item 2a) — 2026-10-23, desktop **[V]**

At the author's request ("yes run the proposals"), after a recheck that the drive, the clone and `origin/main`
agree (`github_sync.py --dry-run`: 0 to copy; `e11642d`, CI passed; every build script parses).

- **The valley map** downloaded from Zenodo record 1051038 into `Mars Project\Reference\Alemanno2017_valleys\`
  (`.shp`, `.shx`, `.dbf`, `.prj`; Zenodo's MD5s matched, the `.shp`'s SHA-256 is the script's `VALLEY_SHA`), and
  added to `Reference\README.md` with each file's SHA-256. `Reference\` is not mirrored to GitHub (§41).
- **`propose_label_changes.py --dry-run`** (1,166 s), then **`--map`** (924 s), Pro closed, logs
  `logs\propose_dryrun_DESKTOP-PJS73RO.log` and `propose_run_…log`, `logs\label_proposals.json` (the dry run's
  kept as `label_proposals_dryrun_DESKTOP-PJS73RO.json`; tally and minimum identical). **The drive gives the
  laptop's result (§68.5) exactly:** the centroid rule reproduces 183 / 329 with 0 mismatches; 1,086 rows: keep
  474, relabel 12 (5 to edifice, 5 to fluvial, 2 to Normal Ground), check 23 (15 Crater, 7 lava tube, 1 fluvial),
  clip 1, delete 1, fix 1, new 574 (126 edifice, 172 apron, 276 fluvial); no overlap between classes or across the
  split. If all were accepted: edifice 12 held out in 3 blocks, apron 22 in 3, fluvial 46 in 10, all meet §11.3;
  **hills (28 training polygons in 2 blocks) and lava tube (18 training) stay short.**
- **Written:** `Landform_TrainingSamples_v2_proposals` (1,086 rows; the gdb now holds 31 feature classes) and the
  map "Labels v2: proposals" (one layer per `Action`, "Kept" hidden; 33 maps). `.aprx` backed up first to
  `Mars Project\.backups\Mars Project 20261023-153029.aprx`. `Landform_TrainingSamples_terrain` untouched.
- **Read by eye** (33 rows over DEM hillshade: every relabel, clip, delete and fix, 6 checks, 4 new per class,
  agent scratch): the five volcano circles sit on Tharsis Tholus, Ulysses Tholus, Arsia, Pavonis and Ascraeus
  Mons; the five lava-tube relabels on valleys; 334 and 335 with chains 336 and 337 cut out; 350 inside 347/348;
  512 a real crater; the checks are small craters drawn with a wide margin. The unit pieces are coarse, as their
  reasons say (edifice pieces 969 and 1031 nearly flat plains; apron pieces hold mesas and plains). Two to flag
  for the review: **new fluvial strip 778** (held out, ~121.6°W 9–10°S, "Late Amazonian single valley") lies on
  the Arsia Mons flank and may be a lava channel **[?]**; **Crater 47** (1 km²) surrounds a feature of about one
  DEM cell and no catalogued crater.
- **Next:** the author's review (item 2b, by 26 Oct, `NEXT-STEPS.md` §11.4), including more hills and lava-tube
  polygons in other training blocks.

### 69.3 Check-in and audit pass — 2026-10-24, desktop **[V]**

At the author's request to keep the repo and the drive current. **Nothing changed on the drive since §69.2's push**
(no file under `Mars Project\` or this folder newer than 10-23 15:36 but a log), so the review (2b) has not started;
the clone equals `origin/main` (`cdac6d7`, CI passed), no other branch or open PR; `github_sync.py --dry-run`:
0 to copy, 1,019 unchanged (the six > 95 MB model files are skipped as always; they are in `dl-models.zip`, §66.10).

- **`audit_record.py` under the ArcGIS Python failed one check:** §6 said 30 feature classes, the gdb holds 31.
  §69.2 had written the 31st (`Landform_TrainingSamples_v2_proposals`) without adding it to §6's table; added
  (Polygon, 1,086 rows, `Action` counts read with `arcpy`: 474 keep, 574 new, 23 check, 12 relabel, 1 clip,
  1 delete, 1 fix, as §69.2). The `py -3` run cannot see this (no `arcpy`): run it under the ArcGIS Python after any gdb change.
- **Four audits pointed at the root for the delivered Presentation 1 and the prospectus,** which live in `OLD\`, and
  crashed: `audit_consistency.py`, `audit_structure.py`, `audit_images.py` and `verify2.py` now read `OLD\`. The
  first three run clean; `verify2.py` gives 57 checks, 26 failed, stale by design as §17.4 says (its gdb checks
  describe September: the nomenclature triplicates deleted in §50, no pyramids before X4).
  `audit_headroom.py` takes a deck as its argument, as before.
- **Passed:** `verify_all.py` 37 / 37; `audit_record.py` (ArcGIS Python) after the §6 fix; `tools/check_repo.py`
  in the clone; `audit_text.py`, no schedule issues; `tools/check_remote.py`, 83 release assets and 4 source
  mosaics; `audit_headroom.py` on the interim and the final deck, no slide under 40 pt of slack.
- **The paper's numbers now have a scripted check.** §69's count of 302 was a one-off run of the matcher;
  `verify_interim.py` now reads a `.tex` too (the body without comments, citations, labels, lengths or the address
  block; `\%`, `~`, `\,`, `{,}` and `\times` made plain). On `mars_global_mosaic.tex`: **all 508 numbers in this
  record** (counted per paragraph, so repeats count again); two planted changes (465,357 for 465,354 and 73.4 %
  for 73.8 %) both fail it. Its report now names the file it checked (it said "interim.py" for `final.py` too):
  interim 277, final 174, both in the record. `HANDOFF-DESKTOP.md` §4 and `NEXT-STEPS.md` name the paper run.
- **Next:** unchanged, the author's review (2b, by 26 Oct), then the v2 runs (§11.5).

### 69.4 The v2 runs rehearsed on the proposals as proposed (`--labels v2p`) — 2026-10-24/26, desktop **[V]**

The author's request, 2026-10-24, before leaving the machine to the agent: start the long runs that can go
unattended. The review (2b) has not started (0 of 1,086 rows have a `Review`), so the real v2 runs (§11.5) cannot.
The author chose a **rehearsal**: every proposal taken as proposed, run through the whole of §11.5 steps 2–3, so
that the real run after the review meets no new failure and its timings are known. **A rehearsal, never a
result:** these labels are the agent's proposals, not the author's judgement (§68.4, "the agent proposes, the
author accepts"); nothing here is published, put in the interim, or used for D18.

- **D19 answered by the author, the same day, before any v2 score existed:** rule (a) is judged on held-out v2
  classes 1–4, the ground both maps can name (§68.4 amended). `score_d18_verdict.py` now does that and reports
  overall accuracy and κ beside the rule; it refuses an output without `confusion_unrounded`. Planted case: a
  seven-class map that wins overall (71.7 % against 55.4 %) only through classes 5–7, and loses on 1–4 (67.7 %
  against 82.3 %), now fails (a) and does not replace the published map.
- **A third label set, `--labels v2p`** (`labelsets.py`): seven classes, `Landform_TrainingSamples_v2p_60_train` /
  `_test`, `_v2p` in every output name, so neither a four-class nor a v2 file is touched.
  `apply_label_review.py --rehearsal` writes `Landform_TrainingSamples_v2p[_60_train/_test]` taking every
  non-keep row as accepted (its log `logs\label_review_rehearsal.json`); `verify_global60_classification.py`
  names a v2p score `…v2p…` and a four-class map's `…_on_v2p_labels`. The v2 names are unchanged (all three sets
  printed and checked).
- **The rehearsal labels:** 1,085 labels (the delete drops one), 827 training and 258 held out, as the laptop's
  full-accept test of §68.5; no overlap between classes or across the split. Training / held out (blocks):
  Crater 175 (15) / 122 (8), hills 28 (2) / 16 (3), lava tube 18 (3) / 18 (2), Normal Ground 101 (13) / 22 (4),
  edifice 119 (23) / 12 (3), apron 150 (21) / 22 (3), fluvial 236 (121) / 46 (10). Classes 5–7 meet §11.3; hills
  and lava tube fall short of it in training, as §11.3 says (the script leaves out only a short new class).
- **The runs:** `build\run_rehearsal_v2p.ps1` runs §11.5's commands with `--labels v2p` one after another,
  the SVM chain (train, classify at 200 m, 11 × 11, both maps scored on the v2p polygons, the verdict, T8) and
  then the U-Net chain (export, train, two passes, mosaic, both maps scored); each step's log in
  `build\logs\rehearsal_v2p\`, one line per step in `queue.log`. Started 15:08.
- **Seven classes cost ~3 × the four-class SVM time** (measured; §11.5 had assumed the four-class times): training
  **6,441 s** (1.8 h, against 2,861 s for a T1 retrain on this stack, §55.5); classifying, tile 1 **4,926 s** and
  tile 2 **5,139 s** against 1,656 s and 1,735 s for the same tiles in the four-class 200 m run, a steady
  **2.97 ×**, so ±60° at 200 m projects to **~20 h** (the four-class run: 6.8 h). The workers keep 10.3 of 12
  cores busy. So the real v2 SVM needs **~22 h from the review's end to its map**, not ~7 h.
- **The SVM chain ran end to end** (`queue.log`): train and classify 21 h 47 min in all (the 21 tiles 3.2 × the
  four-class run's on average; the last row's short tiles ~22 min each); 11 × 11 filter 10.1 min; each scoring
  29.0 min; the verdict and T8 under a minute. Steps 2–6 exit 0; step 1's code went unrecorded (below), its output
  complete through "mosaic done". **One failure of the queue, not of a step:** after
  the mosaic, writing `queue.log` failed because another process (the agent's watcher) held it open, and
  `$ErrorActionPreference = "Stop"` ended the queue; the map was complete. The queue now writes its log through a
  retrying `Log`, and was restarted `-From 02`.
- **The scores, on the 258 rehearsal held-out polygons** (an agent's labels, so a test of the pipeline, not of the
  scheme): the seven-class SVM map **41.3 %, κ 0.297** (one class everywhere 32.8 %); the published four-class map
  **33.6 %, κ 0.227**, the laptop's figures of §68.6 exactly. Producer's, seven-class: Crater 0.301, hills 0.582,
  lava tube 0.270, Normal Ground 0.984, edifice 0.508, apron 0.054, fluvial 0.604. On its own 827 training
  polygons the seven-class map scores only **51.7 %, κ 0.386** (the four-class map 16.4 %, κ 0.106): a weak fit.
- **D18's verdict on these labels: the four-class map stays.** (a), on v2 classes 1–4 (D19): **62.0 % against
  79.9 %, κ 0.465 against 0.668, fails**; overall it would have passed (41.3 % against 33.6 %), so D19 decides
  this case. (b): edifice user's 0.280 against its share 0.183, ok; **apron 0.180 against 0.328, fails**; fluvial
  0.379 against 0.069, ok. (c): **Crater producer's falls 35.6 points, fails**; hills −4.5, Normal Ground −0.8, ok.
- **What the rehearsal map does with the new classes:** fluvial channel takes **32.9 % of ±60°** (45.6 % of the
  highland units `h`), against 6.9 % of the held-out label area: the 236 machine-drawn valley strips, the
  largest training class, pull the classifier towards it **[E]**; Crater falls to 9.2 % of the map (33.9 % in the
  four-class map). Against SIM 3292 (T8, `logs\geomap_check_v2p.json`), edifice is 4.2 × its share on `ve` units and 2.6 ×
  on `a`, apron 4.9 × on `a`: the new classes find their units. **For the review:** trimming the valley strips to
  the valley floors (§68.5's "the pieces' share falls as the author trims them") is where the seven-class map
  stands to gain most; the Crater fall is the other half of (c).
- **The U-Net chain ran end to end** (queue done 2026-10-26 13:50; 13 steps, every one but 1 and the stopped
  09 exit 0). Times: export **22.7 min** (21,711 chips, 47,072 features, against ~3,600 chips from the four-class
  labels); training **28,050 s = 7.8 h** (30 epochs at ~14 min, some to ~22 min while other desktop programs
  shared the GPU; the four-class model 4,376 s, §66.6), so **6.4 ×**; pass A **6.6 h** and pass B **6.0 h**
  (243 tiles each, ~90 s a tile); the two-pass mosaic 4.8 min (passes disagree on 5.4 % of pixels); each scoring
  ~31 min. **So the real v2 U-Net needs ~21 h after its export**, not ~13 h, if the reviewed labels give as many
  chips.
- **A leak in the pass's process:** `ClassifyPixelsUsingDeepLearning` in one process grew ~0.28 GB a tile (40 GB
  of private memory by pass A's tile 144, ~13 GB an hour); Windows grew `pagefile.sys` to 17.3 GB and C: fell from
  63 to 42 GB free. The agent stopped the process just after tile 148 was saved (no partial tile), and the queue
  now runs each pass in chunks of at most 60 new tiles (`--tiles 180`, `243` for A; `60`, `120`, `180`, `243` for
  B), one process each, finished tiles kept: the largest reading was 14.8 GB (pass A's last chunk, 48 tiles in),
  and C: stayed ~50 GB free. The
  four-class passes (§66.7–66.8) ran 243 tiles in one process each; whether they leaked as much was not measured.
- **The U-Net scores, the same 258 rehearsal held-out polygons:** seven-class **88.8 %, κ 0.856**; producer's
  Crater 0.836, hills 0.887, lava tube 0.226, Normal Ground 0.988, edifice 0.949, apron 0.862, fluvial 0.750. The
  published four-class U-Net **41.6 %, κ 0.280** (§68.6's figures exactly). On the 827 training polygons:
  seven-class 85.4 %, κ 0.809; four-class 18.2 %, κ 0.129. The map: edifice 27.8 % of ±60°, Normal Ground 25.3 %,
  fluvial 19.5 %, Crater 13.6 %, apron 12.9 %. Pro's own validation figures for the model (pixels of the 10 %
  validation chips) give high recall and low precision for every class (Crater 0.86 / 0.08, edifice 0.93 / 0.27,
  apron 0.99 / 0.48, fluvial 0.61 / 0.13).
- **D18's rule applied to the U-Net pair, as a report** (`logs\d18_verdict_unet_v2p.json`; D18 itself is about the
  SVM map): (a) on v2 classes 1–4 **90.4 % against 98.9 %, κ 0.844 against 0.980, fails**; (b) all three new
  classes pass (user's 0.766 / 0.913 / 0.752 against shares 0.183 / 0.328 / 0.069); (c) **Crater −15.5 and hills
  −10.7 points fail**, Normal Ground +0.3 ok. Overall it would have won by 47 points (88.8 % against 41.6 %):
  D19 decides this case too.
- **What the rehearsal says for the real run:** the pipeline works end to end on seven classes with every guard
  in place; the times are ~22 h for the SVM map and ~21 h for the U-Net map after the review, run one after the
  other ~2 days. The U-Net learns the new classes well where the SVM does not (edifice user's 0.766 against
  0.280, apron 0.913 against 0.180), at a cost to Crater and hills on the old ground. These are an agent's labels,
  so none of this is the scheme's result.

### 69.5 The interim's data cut moved to 26 October (D20); the interim rebuilt to it — 2026-10-26, desktop **[V]**

- **D20, the author's decision, 2026-10-26 evening:** the interim data cut is **26 October**, not 2 November
  (§39.1): what is measured by then is what the interim covers, and the interim is wrapped up now rather than
  pushed. Everything after goes to the final: the label review (2b) and the v2 runs (§11.5 of the plan), the review
  and digitising of the candidates, layout 14 from the review, and the H1 and H2 retests. **D18's "both maps in the
  interim" moves to the final**; its verdict rule (§68.4, D19) is unchanged. The interim falls under the 1 November
  contingency now: the digitising classes hold 0 rows and 0 of 9,287 candidates are reviewed, so it presents the
  machine products as candidates. The label review had not started (0 of 1,086 rows with a `Review`, read the
  same evening). The final's dates are unchanged: data freeze 22 November, due 8 December.
- **The interim brought to the cut** (`interim.py`, nothing else): `STATUS_DATE` 26 October; the processing log
  gains "22–23 Oct: the 512 labels audited; seven classes proposed (D17)" (§68–§69.2), the two 19 Sep candidate rows
  merged so the table keeps 13 rows; the issues gain "Five 'Crater' labels are volcanoes" (Arsia Mons 31 % of
  the held-out Crater area, §68.2), and "Digitising has not started" becomes "The review has not started" (0 of
  9,287 candidates); the next steps name the work for the final, the seven-class labels among them; the schedule
  gives the 26 October cut. The rehearsal (§69.4) stays out: never a result. The figures are unchanged.
- **Rebuilt and read:** deck 30 slides, report 21 pages, 21 figures; `verify_interim.py` 282 numbers, all in the
  record. The first build ran the issues slide off its foot (nine items); two items cut to one line each fit it.
  Slides 1, 6, 29 and 30 and report pages 1–3, 20 and 21 were read. Backups in `NEXT STUFF\.backup_20261026\` and
  `build\.py_backup_20261026\`.
- **The percent-complete column (D16), set by the agent at the author's request the same evening:** each row's
  progress toward the final deliverable, not the interim; 100 means nothing is left for the final, and a scope that
  was reduced and settled counts as done. 100 for rows 1–7, 9 and 10 (done, or closed: the gradient products are not
  used further, §7; Jezero stays hosted services, §50). **Classification 75**: the four-class map published and
  scored, T1 and the deep-learning models done; the seven-class labels and maps remain (§57, §66, §69.2).
  **Landform digitising 10**: the classes, review fields, candidates and validation sheet are ready and the 512
  training polygons drawn, but no landform is digitised (§46). **Crater inventory 60**: the Robbins catalogue
  and 465,354 closed depressions with their measured precision; no reviewed crater rims (§53.4, §54.4).
  **Map layouts 85**: 17 sheets; the final adds a seven-class sheet and layout 14 from the review (§11.5).
  **Report and presentations 60**: the prospectus and Presentation 1 delivered, the interim built to the cut,
  the final paper and deck drafted (§69). Rebuilt: 30 slides, 21 pages, `verify_interim.py` 283 numbers; slide 5
  and report page 2 read.
- **Left for the interim, the author's:** the due date and the delivery.

### 69.6 The interim edited for plain wording and reordered — 2026-10-26, desktop **[V]**

At the author's request ("improve and refine the interim; humanize it and remove AI slop"):

- **The wording** (`interim.py` only; every number byte-identical, each sentence holding a number re-read against
  its own section): colon reveals and stacked "X, not Y" contrasts rewritten as plain sentences; subjects added
  where a bullet had none ("Day IR carries none" → "Day IR does not follow it"); repeated facts cut (86.6 % was on
  three slides). The wording traps (§7 of `INTERIM-PLAN.md`) still hold: "±60°", "diurnal-contrast index", no
  crater inventory.
- **Two facts corrected in passing:** the issue "250 GB on one USB drive" was the size at §2.2's date; the drive is
  **428.7 GB** (§67.4). "Terrain alone … 34 of 124 crater polygons" now says *right* (polygons won, §56.1), and the
  landform slide gives the split as 329 training and 183 held out.
- **The order:** the two failed first maps (layout 05) now come before the published map, and the hypotheses run
  H1, H2, H3, Q5 (they ran H1, H3, Q5, H2). The Ius slide says which map is visible and which night IR.
- **The report's tables:** a header row keeps with its first row, and a table of up to 8 rows never breaks across
  a page (`docx_kit.table`); the bands table's columns widened so "232 m" and the wavelengths sit on one line.
  Both breaks were seen in the rendered report (the schedule's header alone on page 22; the correlation table's
  last row on page 2).
- **Rebuilt and read:** deck 30 slides, report 23 pages (21 before: the new figure order breaks pages
  differently), `verify_interim.py` 286 numbers; `neutral_voice.py` clean. Every slide and every page read after
  the last build of each.

### 69.7 The first review session: Ius channels and depressions — 2026-10-26, desktop **[V]**

The author's first review session (§46; `NEXT-STEPS.md` item 1), the gdb saved 23:16; the interim's data cut was
earlier the same day (D20), so this is for the final.

| Ius class | reviewed | accept | reject | unsure | precision, accept ÷ (accept + reject) |
|---|---|---|---|---|---|
| channels (`Landform_ChannelCandidates_auto`) | 188 of 2,610 | 94 | 80 | 14 | **54 %** of 174 |
| closed depressions ≥ 1 km (`Landform_CraterCandidates_auto`) | 361 of 1,685 | 26 | 331 | 4 | **7 %** of 357 |

- **The 188 reviewed channels are exactly the layer "Channels: steep and rock-floored (188)"** (§32.1's query
  `SlopeDeg >= 5 AND ThermIdx < -0.15`), so 54 % is that layer's precision, not the 2,610's. Athabasca: 0 reviewed.
- **Copied** with `accept_reviewed.py --apply --by "Logan M Edwards"`: 94 rows into `Landform_ChannelCenterlines`,
  26 into `Landform_CraterRims`. **The accepts carry the candidates' defaults**, at the author's word ("copy the
  accepts as they stand, defaults and all"): every channel `Origin` indeterminate, every row `Confidence` inferred,
  crater `Preservation` empty. A rerun skips copied rows (`SourceID`), so attributes set later on a candidate do
  not reach its copy; they must be set on the copy itself.
- **Layout 14** rebuilt (`make_validation_sheet.py`, `polish_layouts.py`, then re-exported; read). Its recall column
  reads 100 % because nothing is drawn by hand yet: recall means something only once the missed features are drawn.
- **T4 (H2)**, `make_t4_channel_h2.py`: stage 1 reproduces §51.1 (median gradient diff −8.85 [−15.69, −5.76] m/km,
  AUC 0.81 / 0.50 / 0.81); **stage 2 still waits**, `{indeterminate: 94}` against ≥ 10 fluvial and ≥ 10 volcanic.
- The label proposals (2b): 0 of 1,086 rows reviewed. Lava margins: 0 drawn.

### 69.8 The label review (2b): the author's rows, and the apron and fluvial rows by a written rule — 2026-10-27, desktop **[V]**

Read after the author saved and closed Pro (no locks). The candidate classes and digitising classes are as §69.7
left them; the change is in `Landform_TrainingSamples_v2_proposals`.

- **The author's review, in Pro: 162 of the 164 non-`keep` rows that are not new apron or fluvial strips.**
  Checks 23 (17 accept, 6 reject): of the 15 Crater checks 9 accepted (2, 3, 4, 6, 16, 17, 18, 46, 434) and 6
  rejected (21, 38, 42, 47, 48, 54); the 7 lava-tube chains near Uranius Fossae (318–324) accepted as lava tube;
  435 accepted as fluvial. **A rejected check of the 512 enters as it was** (§11.4), so the six rejected Crater
  checks still enter as Crater unless the author meant them dropped (asked 10-27). Relabels 12 (10 accept: the five
  volcanoes to 5 and the five lava tubes to 7; **334 and 335 rejected**, so they stay lava tube); the clip of 290
  and the delete of 350 accepted;
  new edifice pieces 125 of 126 (119 accept, 6 reject). **Not reviewed:** 512 (`fix`, so it enters as it was) and
  edifice piece 870 (left out). No outline was edited (every geometry within 1 % of the proposed `KM2`), so the
  accepted edifice pieces are the untrimmed 3° pieces.
- **The new apron (172) and fluvial (276) rows were left to the agent**, at the author's word ("the classification
  of aprons and fluvial channels i will leave to you to accept them as i will not be able to do it myself").
  `build\review_v2_by_rule.py` sets their `Review` by a rule fixed before it ran; `ReviewNote` begins "agent rule
  §69.8"; `logs\label_review_by_rule.json` holds every row's measures. **These are screens, not anyone's eye; the
  final must say so:**
  - fluvial: accept if the strip's median DEM height is ≥ 20 m below that of a 4.8 km geodesic flank ring
    around it, and `ShareVolc` < 0.5 (on volcanic plains a channel's origin, water or lava, is H2's open
    question). Floor depth deciles −11, 12, 25, 37, 48, 62, 83, 113, 172 m. **192 accept, 84 reject** (61 no
    floor, 15 volcanic, 8 both). Strip 778 on the Arsia flank, flagged in §69.2, sits 178 m above its flanks:
    rejected.
  - apron: accept if `SlopeMed` ≥ 1° and `CraterCover` < 0.5. **155 accept, 17 reject** (11 flat, 6 in craters).
    Accepted pieces keep their coarse outlines (§68.5: mesas and plains inside), untrimmed.
  - The proposals class was copied first to `.backups\proposals_20261027-002809.gdb` (an earlier copy, `-002234`,
    is from a first run that stopped at the first row: `ReviewNote` holds 60 characters).
- **`apply_label_review.py --dry-run`** (nothing written): 0 overlaps between classes or across the split. Per
  class, training / held out: Crater 175 in 15 blocks / 122 in 8; **hills 28 in 2 / 16 in 3, short** (§11.3:
  training needs 3 blocks); lava tube 20 in 3 / 18 in 2; Normal Ground 99 / 22; edifice 112 in 23 / 12 in 3;
  apron 139 in 21 / 16 in 3; fluvial 166 in 96 / 32 in 8. Every class but hills meets the minimum.
- **The author's answers, the same night:** the six rejected Crater checks are **not craters, drop them**
  (set to an accepted `delete`, `ReviewNote` "author 10-27: not a crater, drop"); hills **stays in, with
  `--keep-short`** (training in 2 blocks against §11.3's 3: a limit the final must state).
- **Applied** (`apply_label_review.py --keep-short`, 81 s; `logs\label_review_applied.json`):
  `Landform_TrainingSamples_v2` 971 labels, `_v2_60_train` 734, `_v2_60_test` 237; no overlaps. Crater now 170
  training in 14 blocks / 121 held out in 8; the other classes as above.
- **The v2 runs started 2026-10-27 01:32** (2c, NEXT-STEPS §11.5 steps 2–3): `build\run_v2.ps1`, the rehearsal's
  queue with `--labels v2` (SVM, then U-Net; logs in `build\logs\run_v2\`), detached; ~2 days by the rehearsal's
  times, Pro closed throughout. 58 GB free on `C:` at the start (the rehearsal had ~50).

### 69.9 The interim cleared of anything that reads as machine-made — 2026-10-27, desktop **[V]**

At the author's request ("remove anything that would look machine-made"). The content is the 26 Oct cut's (D20);
no number changed (`verify_interim.py`).

- **Taken off the page:** the report's closing "Generated … by build_interim_report_live.py from interim.py"; the
  "PROJECT-KNOWLEDGE.md §…" source line under every slide and figure; the "KB" column of the processing log; the
  § references inside the band, issue and next-step text and on the correlation note; the decision code "(D17)";
  "WARNING 000869", "Gradient_*", "(desktop)", "Desktop:", "on the desktop" and "(layout 14)" (now "the
  validation sheet"); the locator slide's "Where:" title. The § stay in `interim.py` as comments and in each
  figure's `source` field, which is no longer printed.
- **Inside the pictures:** the thermal-provinces figure's footnote ended "PROJECT-KNOWLEDGE.md §28.10"
  (`make_fig_global60.py`, redrawn; the final paper's copy crops that strip); layout 16's legend read
  "X5 detections, RetinaNet (1,838 boxes; KB §66.2)": `make_interim_figs.py` now renames such layers in memory
  for the export ("RetinaNet detections (1,838 boxes)"), so the .aprx and the sheet are unchanged. No other
  interim legend item carries an internal label (checked with arcpy).
- **File properties:** python-docx wrote author "python-docx" and comment "generated by python-docx";
  python-pptx wrote last-modified-by "Steve Canny" (its own author) and "generated using python-pptx". Both
  builders now set author and last-modified-by to the author, the title to the project title, and clear the
  comment. Picture alt text was the image file name (`10_global60_locator__map.png`); it is now the figure title.
- **Rebuilt and read:** deck 30 slides, report 21 pages (23 before: no source lines); every page and the changed
  slides read; a text search of both PDFs finds no "PROJECT-KNOWLEDGE", "KB", "§", ".py", "D1x/D2x", "X5",
  "desktop" or "Generated".

### 69.10 The interim refined for the 10 November presentation, the cut kept — 2026-10-27, laptop **[V]**

The author's request ("refine the interim presentation before my presentation on the 10th; update any figures you
come across"), on the laptop without the drive. **D16's date, from the author: the presentation is 10 November**;
the report's date was not given. Asked whether to move the status past the 26 Oct cut (the first review session,
§69.7, and the applied v2 labels, §69.8, make "the review has not started" and "landform classes empty" out of date
by the talk), the author chose to **keep the 26 Oct cut** (D20 stands), and to keep the seven-class maps for the
final. So nothing measured or stated changed: `verify_interim.py` 285 numbers, the same count as the committed
`interim.py`.

- **Every slide read** (rendered through PowerPoint on the laptop). Changed: **T4 and T8 charts** (`make_fig_t4.py`,
  `make_fig_t8.py`) were saved at 100 dpi (1,100 px wide) where the other charts use 200; rerun unchanged first, T4
  is pixel-identical and T8 one pixel row taller (matplotlib version), then at 200 dpi (2,200 px). `final.py`, the
  paper and the README use the same files. **The U-Net slide**: its four takeaways ran into the legend; `map_left`
  slides take a `points_h` (pt) and the U-Net slide 204, the legend placed below it. **The title slide** printed
  "Mars Global Mosaic" and then "Mars Global Mosaic: Mapping …"; the subtitle drops the repeated title
  (`build_interim_live.py`; `content.py` untouched). **The schedule** gives "10 Nov, Interim presentation" for
  "mid-Nov, Interim presentation and report".
- **Seen and left, they need Pro and the drive:** the legend titles of layouts 04 and 17 keep their em dashes
  ("Landforms — SVM …", "Landforms — U-Net …"; `make_interim_figs.py`'s in-memory renames could take them); the
  ±60° mosaic slide's day and night IR panels read as flat grey at slide size.
- **Rebuilt and read:** deck 30 slides (slides 1, 20, 24, 26 and 30 read after the build), report 21 pages (pages
  13, 19 and 21 read). Backups of both in the session's scratch folder; git holds the previous build (`862dbf8`).
  Written in the clone only: copy to the drive before the next `github_sync.py` (`NEXT-STEPS.md`, "Resume here").

### 69.11 The interim deck redesigned for the talk: basalt and rust over the project's own mosaic — 2026-10-27, laptop **[V]**

The author's request ("utilise the skills available to you to improve and artistically update the presentation"),
the 26 Oct cut kept (§69.10): every word and number on the slides is `interim.py`'s, unchanged; only the design
and the layout of the slides changed. The deck design guidance (the pptx skill) and the chart method (the dataviz
skill) were followed; the report is not touched.

- **A new theme, `build\mars_theme.py`; `le_theme.py` untouched** (the author's Presentation 1 design, still used
  by the Presentation 1 builders and `build_final_deck.py`). Cambria headings and Calibri body, both shipped with
  every Office since 2007 (Aptos is missing from older installs, so the room's PC could substitute it). White
  content slides with a rust (#B4472A) kicker naming the slide's group above a 28 pt title (the widest title,
  measured with the font file, takes 790 of 848 pt), **no rule under the title** (the cyan accent bar is gone), a
  footer with the slide number. Dark slides in basalt (#17181C) over **Ius Chasma from layouts 01 and 02**, cropped
  in memory to 16:9 under a basalt gradient, each with its credit.
- **The slides** (`build_interim_live.py`, 30 → 31): a full-bleed title slide (Viking colour); the goals as four
  numbered cards under the mission in italics; the bands table restyled; the correlation table **shaded by |r|** in
  one hue, the independent pairs pale and bold; **the progress table drawn as rows with bars**, percent complete now
  in rust with a tick at 13 September (drawn from shapes: PowerPoint sized the table's rows itself and the bars
  drifted off them); the processing log restyled (26 pt rows, clear of the footer); the results divider over the
  night IR of the same canyon with **four headline numbers** (`HEADLINES` in `interim.py`, each already on its own
  slide: 86.6 %, 73.8 %, +1.36, 465,354); every figure slide with its group as a kicker (`group=` in each `FIGURES`
  entry); the issues as cards on **two slides**, the six measured limits, then the three hurdles of the work; next
  steps as four numbered cards over **the schedule as a timeline**, 10 Nov marked. A closing "Questions" slide over the mosaic was built and read, then removed at the author's word: the deck ends on the next steps.
- **The charts are unchanged.** Their blue and orange pass the dataviz palette validator (CVD ΔE 24.7, normal-vision
  33.6, contrast ≥ 3:1), they carry direct labels and recessive grids, and they are shared with the report, the
  final paper and the README; restyling them was not needed and would reach beyond the deck.
- **Checked:** `verify_interim.py` 294 numbers, all in the record (285 + the headline numbers); the pptx skill's
  `validate.py` passes; its text dump of all 31 slides holds no "§", "KB", ".py", decision code or "Generated";
  rendered through PowerPoint and every slide read, the figure slides on contact sheets. Fixed in the reading: the
  progress bars (above), the "#" column wrapping 10–14, half-empty cards, map labels showing through the title
  slide's text. `tools/check_repo.py` passes with the new script catalogued (166).
- **Clone only**, like §69.10: copy to the drive before the next `github_sync.py`.

### 69.12 The interim deck repainted navy, one family of blues throughout — 2026-10-27, laptop **[V]**

The author's request ("the main color should be navy or other dark blue; try to keep a mostly consistent design
throughout"), the same day as §69.11, words, numbers and layout unchanged. `mars_theme.py`'s palette is now one
hue family: **navy #0E2841** (`le_theme.py`'s own, so the interim matches the author's Presentation 1 navy) for
the title and divider slides, their veil over the mosaic, every table head and the numbered dots; **blue
#1D5C9E** (7:1 on white) for kickers, bullets, issue labels and the correlation shading; **sky #8CC4EC** (7.9:1 on
navy) for the headline numbers and kickers on dark slides; the card and row tint `le_theme.py`'s #EEF3F8. Rust,
basalt and dust are gone. The progress bars became **two shades of one hue**: navy for what was done by 13
September, light blue for what was added since, grey for what is left (the navy tick of the first repaint was lost
against the blue bar). The charts keep their own blue and orange (§69.11). Checked: 31 slides, `verify_interim.py`
294, the pptx skill's `validate.py` passes, every slide rendered through PowerPoint and read on contact sheets.
Clone only, like §69.10.

### 69.13 The interim deck dark throughout: navy slides, navy-ground charts and maps — 2026-10-27, laptop **[V]**

The author's request ("I would like the main themes to be darker colors, I don't want to be blinded by white
backgrounds"), the same day as §69.12; words, numbers and slide layouts unchanged.

- **Every slide on navy** (`mars_theme.py`): the ground `NAVY` #0E2841; text light (`INK` #EAF0F7, `MUTED`
  #A9BACD), titles white, kickers, bullets, issue labels and the numbered dots sky #8CC4EC; cards and alternate
  rows a lighter navy (`TINT` #163A61), table heads a deeper one (`DEEP` #081A2E), table rules navy (PowerPoint's
  default table style draws them white). The correlation shading runs from the card navy to blue #4A90D9, the
  independent pairs in bold sky; the progress bars light blue for 13 September, blue for what was added since,
  dark for what is left; the timeline's 10 Nov in sky.
- **The figures, navy-ground, for the deck only: `build\make_interim_dark.py`** -> `interim_img\dark\` (42 files,
  37 MB, git-ignored and rebuilt by the script; the builder takes a dark copy where one exists). The report, the
  final paper and the README keep the white originals; `git status` showed none of them changed.
  - **Charts:** each of the seven chart scripts runs unchanged with `Figure.savefig` wrapped: the finished figure is
    recoloured for navy and written to `dark\`. Neutral greys swap ends (paper -> navy, ink -> light), grey text is
    lifted to stay readable, strong colours keep their value, light tints keep their hue and their distance from
    the ground (so T8's weak bins stay quiet and its strong bins brightest), white text on a strong fill stays white.
    Found in the reading: tick labels are made at draw time (the figure is now drawn first and the new colour passed
    to `tick_params`), and the charts' blue-grey #5A6570 sat just over the grey threshold (0.08 -> 0.12).
  - **Layouts:** the white page touching the edge of each export becomes navy; the small marks on it (panel titles,
    scale bars, north arrows) are lightened; the map frames and imagery are untouched. In legends every white pixel
    is page, text and outlines are lightened, filled swatches keep their colour so they still match the map. Found in
    the reading: solid glyphs ("l", "I", "a") had passed as swatches and stayed black; a swatch must now be at least
    18 x 8 px and 75 % filled.
- **Checked:** 31 slides; `verify_interim.py` 294; the pptx skill's `validate.py` passes; every slide rendered
  through PowerPoint and read on contact sheets, the chart and legend slides again after each fix.
  `tools/check_repo.py` passes: the new script catalogued (167), and the check skips the git-ignored
  `interim_img/dark/` as it skips the layout crops. Clone only, like §69.10.

### 69.14 The interim deck refined: tighter maps, one legend scale, verdicts, clean backgrounds — 2026-10-27, laptop **[V]**

The author's request ("looking at the interim presentation again, continue to improve and refine it wherever you
can"), the same day as §69.13, the 26 Oct cut kept. Every slide of the §69.13 build was rendered through PowerPoint
and read; what was found, and done:

- **The title and divider backgrounds without their graticule** (`mars_theme.graticule`, `degraticule`): the crops
  of layouts 01 and 02 showed the layout's grid lines and labels ("282°E", "8°S") through the veil, beside the title.
  The labels are found in the colour layout as clusters of their exact halo grey (40, 40, 40), the lines as rows and
  columns brighter than their neighbours the whole way across; the night IR layout shares the frame, so the same
  places serve it. Each line is painted over with the band beside it, then each label with the patch beside it, so
  the ground keeps its grain (a Gaussian fill, tried first, left smooth stripes). Backgrounds only; the maps keep
  their graticules.
- **Layout exports tightened** (`build_interim_live.tight`, in memory, for the deck only): the page margins cut and
  any blank band inside closed to 24 px. The ±60° mosaic (layout 08) lost the 163 px gap between its two rows of
  panels and, with `map_h=328` (two takeaways), its panels are about twice the size; the SVM checks, the Ius pair
  and the deep-learning maps gain a little.
- **One legend scale**: 0.5 pt per exported pixel on every slide, smaller only where the room is (`LEGEND`). Before,
  each legend was fitted to its space, so the SVM checks' four-class legend filled a third of the slide while the
  depressions legend was too small to read.
- **Closed depressions ≥ 1 km** (layout 11, two maps stacked) now `map_left`, the takeaways beside it: the maps a
  third larger.
- **A verdict on each hypothesis slide**, an outlined capsule on the kicker's line (`pill`, `verdict=` in `FIGURES`):
  H1 "Not settled: the map is too coarse", H2 "Not supported at stage 1", H3 "Not supported", Q5 "The DEM cannot
  answer it". Each shortens a takeaway on its slide or the issue card "Four hypotheses tested, none supported";
  nothing new is claimed.
- **Goals**: the cards closer under the mission and taller, text 15 -> 16 pt. **Bands table**: 12 -> 14 pt, rows
  50 -> 60 pt, the wavelength column wide enough for "thermal IR, 6.8–14.9 µm". **"What slows the work"**: the three
  issues as full-width bands, label left at 20 pt and text right at 17 pt, filling the slide where three cards had
  floated mid-slide. A sky edge stripe on each band was tried and removed (the pptx skill's guidance: no edge stripes).
- **No breaks inside an expression**: no-break spaces after ≥, ≤ and ≈ in every bullet (`mars_theme.bullets`), and in
  the bands table "r −0.49" and "|r| ≤ 0.12".
- **Seen and left:** Athabasca (layout 09) is square with its scale bar beside it, so map-left gains nothing; the Ius
  candidates' north arrow sits below the scale bar and keeps that map at the 290 pt cap; both need Pro.
- **Checked:** 31 slides; `verify_interim.py` 295 (the "1" of "stage 1"); the pptx skill's `validate.py` passes; its
  text dump holds no "§", "KB", ".py" or "Generated"; every slide rendered through PowerPoint and read, the changed
  ones after each fix. The report is untouched. Clone only, like §69.10.

### 69.15 The size of a 15° block: a slide comparing each band's block with the nearest US state — 2026-10-27, laptop **[V]**

The author's request ("a section which compares the size of a 15 degree square cell to the state its most close to
area with"). The cells are the held-out split's whole 15° × 15° blocks (§31.3), edges on multiples of 15°, so over
±60° there are 24 × 8 = **192 blocks** in four bands of latitude, mirrored about the equator.
`build\interim_block_scale.py` computes them on the project's sphere (R = 3,396,190 m, §18):
A = R² · Δλ · (sin φ2 − sin φ1). State areas: US Census Bureau, 2010 census, total area (land and water).
Nearest by ratio.

| Band (N and S) | Block area | sq mi | E-W side, low → high edge | Nearest state | Ratio |
|---|---|---|---|---|---|
| 0–15° | 781,536 km² (782,000) | 301,753 (302,000) | 889.1 → 858.8 km | Texas, 695,662 km² | 1.12 |
| 15–30° | 728,275 km² (728,000) | 281,189 (281,000) | 858.8 → 770.0 km | Texas | 1.05 |
| 30–45° | 625,384 km² (625,000) | 241,462 (241,000) | 770.0 → 628.7 km | Texas | 0.90 |
| 45–60° | 479,874 km² (480,000) | 185,280 (185,000) | 628.7 → 444.6 km | California, 423,967 km² | 1.13 |

Every block is 889.1 km (889 km) north to south; the E-W side runs from 889 km at the equator to 445 km at 60°.
The ±60° band is 125,523,330 km², a mean block of 653,767 km². Texas is 268,596 sq mi and California 163,695.
Alaska (1,723,337 km²) is 2.2× the largest block, and no block is as small as Montana (380,831 km²).

The deck (`interim.py` `BLOCK_SLIDE`, `BLOCK_SCALE`; `build_interim_live.block_scale_slide`): one slide, kicker
"For scale", "How big is a 15° block? About the size of Texas", just before "Landforms at ±60°, scored on labels
the model never saw", where the blocks are first used. One card per band: the block drawn to scale as its
trapezoid (equator side down, 0.18 pt per km), the state's area as a dashed square of the same area behind it,
the area in km² and sq mi, the ratio. Kept out of `FIGURES`, which the report and the figure scripts read, so the
report is untouched.

### 69.16 The graphics refined: the block slide's grid, legends that can be read — 2026-10-27, laptop **[V]**

The author's request ("continue to refine and improve the graphics further"), the same day as §69.15, the 26 Oct
cut kept. All 32 slides rendered through PowerPoint and read; what was found, and done (`build_interim_live.py`,
`interim.py`; no Pro, so the layout exports themselves are unchanged):

- **The block slide** (§69.15): above each block, a tile strip of the ±60° grid, 24 × 8 blocks, the band's two rows
  (north and south) lit and the equator a light rule (`band_grid`), so each card says where its band is. Blocks and
  squares at 0.16 pt per km (was 0.18) to make the room; the note says what the strip is.
- **Wide legends restacked** (`restack`, in memory, for the deck only): a legend laid out by Pro as one wide row of
  item columns (wider than 3 × its height: layouts 06 and 12) is cut at its blank columns, the items regrouped into
  whichever columns fit the room under the map at the largest scale, and reframed. The channels legend went from
  about 0.23 to 0.5 pt per exported pixel (the cap), the Ius candidates' from 0.26 to about 0.4.
- **A swatch the navy ground hid**: "Order 5" in the channels legend is a dark blue line, contrast under 2:1 on navy;
  any such swatch now sits on a chip of the hillshade's grey (190, 190, 190), so it reads as it does on the map.
  The text and the other swatches are untouched.
- **Channels** (layout 12): the map capped at 262 pt (`map_h`) so the restacked legend has the room to be read.
- **Athabasca Valles** (layout 09): map-left was tried and dropped (the scale bar beside the map pushed the takeaways
  into a narrow column and the fourth under the legend). Instead `legend_beside`: the map at the left margin, the
  legend in the room to its right at 0.5 pt per pixel (was about 0.25), the takeaways full width beneath.
- **Checked:** 32 slides; `verify_interim.py` 325; every slide rendered through PowerPoint, and against the first
  render only slides 15, 16, 17 and 19 differ; those read after each fix. The pptx skill's `validate.py` was not
  on this machine; PowerPoint opened and rendered the deck. The report is untouched. Clone only, like §69.10.

### 69.17 What would strengthen the final paper, brainstormed — 2026-10-27, laptop **[V]**

The author's request, while `run_v2.ps1` runs on the desktop: think of the topics and goals still open and of what
would improve the paper, and log them, the next steps above all. The plan is `NEXT-STEPS.md` §12 (A1–A13 analyses,
R1–R2 blind checks for the author, W1–W8 text and figures, the talks, an order of work) and D21–D24 in its §2.
Nothing measured, no file but the two plans changed. Facts found while reading, each against the clone:

- **The paper's abstract is 306 words** (counted between `\begin{abstract}` and `\end{abstract}`); AAS journals
  allow 250 **[E]** (the AAS author guide, not re-read today).
- **`references.bib` has no entry for the Alemanno valley map**, which seeded class 7 (§68.5); and the paper's
  channel section still says the project holds no channel reference at ±60°, untrue since the map reached the drive
  (§69.2).
- **The paper's Limits predate §69.7–§69.8**: "Its labels await review" and "the manual review ... has not
  started"; `final.py` line 185 says the same.
- **The score logs carry area-weighted confusion matrices** (`build\logs\global60_classification_check_*.json`,
  `held_out.confusion_area_weighted`), so balanced accuracy, F1 and quantity / allocation disagreement can be
  computed on the laptop without the drive. They carry no per-polygon scores: a block bootstrap needs the scorer
  extended, or `DL_UNet_Heldout_Scores_20261020` (four-class maps only).
- The clone's copy of `build\logs\run_v2\queue.log` (untracked) shows the SVM training started 10-27 01:32; it is a
  copy, not the desktop's live log, and says nothing of the run's progress since.
- The literature candidates in §12.4 W3 are **[?]**: named from memory, none looked up.
