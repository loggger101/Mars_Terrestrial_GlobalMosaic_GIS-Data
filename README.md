# Mars Global Mosaic

**Mapping Lava Flows, Fluvial Channels, and Impact Craters in Visible and Infrared.**
Logan Edwards · OCN 4704 Remote Sensing · Fall 2026 · Florida Institute of Technology

An ArcGIS Pro project that co-registers Viking visible color, THEMIS day and night thermal infrared and the HRSC/MOLA elevation model of Mars, then uses the stack to map three landform families: volcanic flow units, fluvial channels and valley networks, and impact craters. The scientific hook is Athabasca Valles, mapped for decades as a water-cut outflow channel before it was reinterpreted as flood lava. Morphology together with thermal response is this project's way of telling the two apart.

The analysis extent is **±60° latitude** (86.6% of the surface), set by the coverage of the THEMIS night mosaic. The detail work is done in a type area at **Ius Chasma**, western Valles Marineris (~271–286°E, 6–13°S).

This repository is the project page and an off-drive backup of the project. The working copy lives on an external drive (about 370 GB with all derived rasters). Everything here is the small part that can't be re-downloaded or cheaply re-computed: the scripts, the knowledge base, the ArcGIS project file, the hand-drawn training labels and every vector layer, the layouts, the logs and the deliverables. The rasters that matter go in a [GitHub release](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases).

![Mars ±60° landform classification](Mars%20Project/Global60/layouts/04_global60_landforms.png)

## Where it stands (2026-10-06)

The final deliverable is due **8 December 2026**. Presentation 1 and the prospectus are delivered. The interim report and presentation are drafted in [`NEXT STUFF/`](Mars%20Remote%20Sensing%20Project/NEXT%20STUFF).

| Task | State |
|---|---|
| Raster acquisition, including THEMIS Night IR | done; all four inputs match their published sizes; the night mosaic its MD5 too |
| CRS harmonisation (the gate) | done at ±60°: one grid, defined once in [`grid60.py`](Mars%20Remote%20Sensing%20Project/build/grid60.py) and read from the night mosaic |
| Terrain derivatives | done at ±60°: slope in degrees on a metric grid, aspect, hillshade, no z-factor defect |
| Band composite | done: a 7-band, 8-bit ±60° stack at 200 m with no raw elevation band, 97.3% co-valid |
| Unsupervised classification | done for the type area (Iso Cluster, object-based segmentation, parameter sweep) |
| Supervised classification | done at ±60° on the 512 hand-drawn labels, scored on held-out 15° blocks |
| Channel and crater candidates | seeded: 2,610 channel candidates, 1,685 crater candidates in Ius Chasma, 5,144 basin candidates at ±60° |
| Landform digitising | **open, the critical path**: the target classes exist and are empty |
| Map layouts | seven layouts in the project (below) |

## Results so far

- **±60° landform classification**: a support vector machine on the hand-drawn labels, scored on 183 polygons in 15° blocks it never saw. **70.5%, κ 0.54** per pixel; **73.5%, κ 0.58** after a 5 × 5 majority filter, against 58.6% for one class everywhere. Normal Ground is reliable (99% producer's, 78% user's) and Crater behaves as cratered terrain. **The lava tube class isn't usable** (2% user's accuracy): 44 polygons are too few for a planet-scale class.
- **Two earlier SVM maps checked and superseded**: one follows its 4096-pixel processing tiles and scores below chance on its own training data. The other is mostly an elevation map.
- **Diurnal-contrast index**: calibrated thermal inertia can't be derived from the 8-bit, locally stretched THEMIS mosaics. A relative day–night contrast index can, and within the type area it is nearly independent of terrain (r = +0.11 against elevation, −0.25 against slope). It is a material signal, not a restatement of topography. It does not compare across the planet.
- **Type-area supervised accuracy**: 62.7%, κ 0.41 on terrain-defined classes. The thermal index adds +0.4 points there, as it should on terrain classes.
- **Channels**: `Fill` flooded Ius Chasma 2,077 m deep, and 56% of the stream cells in the first channel network were an artefact of it. Of the 2,610 candidates that remain, the 188 steep, rock-floored ones (1,037 km) are the ones worth digitising.
- **Craters**: 1,685 closed-depression candidates ≥ 1 km, validated on Perrotin (−7.1% in diameter). The detector can't see breached craters such as Oudemans. At ±60°, 68% of the 117 IAU craters ≥ 100 km are recovered within ±50% in diameter.

All of it, with every number tagged verified or open, is in [`PROJECT-KNOWLEDGE.md`](Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md).

## Layouts

| | |
|---|---|
| ![01](Mars%20Project/TypeArea/layouts/01_visible.png) Ius Chasma, visible | ![02](Mars%20Project/TypeArea/layouts/02_night_ir.png) Ius Chasma, night IR |
| ![03](Mars%20Project/TypeArea/layouts/03_classification.png) Ius Chasma, classification | ![05](Mars%20Project/Global60/layouts/05_svm_checks.png) Checks on the earlier SVM maps |
| ![06](Mars%20Project/Global60/layouts/06_ius_digitising.png) Ius Chasma, digitising candidates | ![07](Mars%20Project/Global60/layouts/07_global60_basins.png) ±60° basin candidates |

## Source data

Not in this repository: 58 GB, public, and still at these addresses at byte-identical sizes (checked 2026-10-06). Put them at the root of the project drive.

| File | Size | Grid |
|---|---|---|
| [`Mars_Viking_MDIM21_ClrMosaic_global_232m.tif`](https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars_Viking_MDIM21_ClrMosaic_global_232m.tif) | 12.7 GB | 231.5 m, central meridian 0° |
| [`Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif`](https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif) | 22.8 GB | 100 m, central meridian 180° |
| [`Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif`](https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif) | 15.2 GB | 100 m, central meridian 180°, ±60° |
| [`Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif`](https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif) | 11.4 GB | 0.00337° geographic |

Three coordinate frames, not two: check `Central_Meridian` per file before reading a window, or THEMIS lands half a planet away. Their statistics sidecars (`.aux.xml`), the night mosaic's PDS label and MD5 are in [`drive-root/`](drive-root).

## What is in this repository

The folders mirror the drive, so a path in the knowledge base (`Z:\Mars Project\…`) maps directly onto one here.

```
Mars Remote Sensing Project/
  PROJECT-KNOWLEDGE.md     the authoritative record: data, traps, every result, open questions
  build/                   93 scripts: every raster product, figure, layout, audit and deliverable
    logs/                  run logs and the classification scores as JSON
    pres1_img/, le_img/    figures
  NEXT STUFF/              interim report and presentation (in progress)
  OLD/                     prospectus and Presentation 1 (delivered)
Mars Project/
  Mars Project.aprx        the ArcGIS Pro project: 19 maps, 7 layouts
  .backups/                31 earlier copies of the .aprx, 2026-09-18 to 10-03
  Global60/, TypeArea/     metadata sidecars, models (.ecd), raster attribute tables, layouts
  LabeledObjects/          deep-learning export metadata (the chips are in the release)
  GpMessages/, ImportLog/  Pro's own geoprocessing logs
exports/
  mars_project_vectors.gdb every feature class in Mars Project.gdb, including the 512 hand-drawn
                           training polygons, the candidate layers and the empty digitising classes
drive-root/                source-raster sidecars; the "new training" shapefile
```

### In the releases, not the tree

[`data-2026-10-06`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/data-2026-10-06), about 4.3 GB:

| Asset | What |
|---|---|
| `typearea-part*.zip` | the whole Ius Chasma type area: stack, terrain, thermal index, segmentations, classifications, models |
| `global60-classification.zip` | the ±60° SVM maps (raw and 3/5/7/9 majority), the model, smoke tests |
| `Classified_*.tif` | the two SVM maps made in the Pro GUI on 29 and 30 September (superseded, kept) |
| `mars_project_vectors.gpkg.zip` | the same vector layers as `exports/`, as a GeoPackage |
| `npy-caches.zip` | decimated arrays of the globals that the figures are drawn from |
| `SHA256SUMS.txt` | checksums |

[`derivatives-2026-10-06`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/derivatives-2026-10-06), about 75 GB: the products that take hours to rebuild.

| Asset | What |
|---|---|
| `global60_*.tif.partNNN` | the ±60° derivatives, original bytes cut into 1.9 GB pieces: the 7-band classification stack, the diurnal-contrast index (100 m and 200 m), DEM, slope in degrees, aspect, hillshade |
| `global60-sidecars.zip` | their statistics and lineage (`.aux.xml`, `.xml`) |
| `labeledobjects-part*.zip` | both deep-learning exports: the 1 October one from Pro and the ±60° re-export |
| `Segmented_202609290011302066080.tif*` | the ±60° mean-shift segmentation made in Pro on 29 September |
| `SHA256SUMS-derivatives-2026-10-06.txt` | checksums of every piece and of every reassembled file |

Rejoin a split file before use: `cat global60_dem.tif.part* > global60_dem.tif` (or `copy /b a.part001+a.part002 a` in `cmd`), then check it against the sums.

Not backed up anywhere but the drive: the `.ovr` pyramids (Build Pyramids re-creates them) and the other geodatabase rasters, mostly legacy products the knowledge base finds defective and superseded (percent-rise slopes on a degree grid, a global composite mixing raw elevation with 8-bit bands).

## Keeping it current

Run from `Mars Remote Sensing Project\build\` on the drive; each script finds the drive from its own location, so `Z:` and `F:` both work.

```bash
python github_sync.py --commit
```

copies whatever changed into the clone, commits and pushes. Files over 95 MB are reported and skipped.

```bash
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" github_export_gdb.py --rasters
```

re-exports the geodatabase's vector layers into `exports/` (and the GeoPackage and the GUI SVM maps for the release). Run it after digitising.

```bash
python github_release_bundle.py --upload data-YYYY-MM-DD
```

zips the rasters and publishes them as a new release.

```bash
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" github_release_large.py derivatives-YYYY-MM-DD
```

does the same for the large products: about two hours at 10 MB/s, resumable, and it stages one 1.9 GB piece at a time.

## Restoring

1. Download the four source rasters to the drive root.
2. Copy `Mars Remote Sensing Project/`, `Mars Project/` and the contents of `drive-root/` onto the drive.
3. Unzip `typearea-part*.zip`, `global60-classification.zip`, `global60-sidecars.zip` and `labeledobjects-part*.zip` into `Mars Project/`, and `npy-caches.zip` into `Mars Remote Sensing Project/`. Rejoin the `global60_*.tif.part*` pieces into `Mars Project/Global60/`.
4. Create `Mars Project/Mars Project.gdb` in Pro and copy the feature classes from `exports/mars_project_vectors.gdb` into it.
5. Re-create the directory junctions `Z:\TypeArea` and `Z:\Global60`, which the legacy Spatial Analyst tools need (they reject the space in "Mars Project").

The `.aprx` stores relative paths, so it opens from any drive letter. Layers that pointed at rasters not restored will show as broken until the `build/` scripts rebuild them.
