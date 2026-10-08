# Backup, releases and restoring

The project's working copy is an external drive. This repository is its off-drive backup: the tree
holds everything small, and two GitHub releases hold the rasters. This page lists what is in the
releases, how the backup is kept current, and how to rebuild the drive from it. Each raster is
described in [rasters.md](rasters.md), each vector layer in [the layer catalog](../exports/README.md).

## What is in the releases

[`data-2026-10-06`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/data-2026-10-06), about 4.3 GB:

| Asset | What |
|---|---|
| `typearea-part*.zip` | the whole Ius Chasma type area: stack, terrain, thermal index, segmentations, classifications, models |
| `global60-classification.zip` | the ±60° SVM maps (raw and 3/5/7/9 majority), the model, smoke tests |
| `Classified_*.tif` | the two SVM maps made in the Pro GUI on 29 and 30 September (superseded, kept); pixel value = class code 1–4, NoData 255, since 2026-10-07 |
| `mars_project_vectors.gpkg.zip` | the same vector layers as `exports/`, as a GeoPackage |
| `npy-caches.zip` | decimated arrays of the globals that the figures are drawn from |
| `SHA256SUMS.txt` | checksums |

[`derivatives-2026-10-06`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/derivatives-2026-10-06), 74.4 GB in 46 assets: the products that take hours to rebuild.

| Asset | What |
|---|---|
| `global60_*.tif.partNNN` | the ±60° derivatives, original bytes cut into 1.9 GB pieces: the 7-band classification stack, the diurnal-contrast index (100 m and 200 m), DEM, slope in degrees, aspect, hillshade |
| `global60-sidecars.zip` | their statistics and lineage (`.aux.xml`, `.xml`) |
| `labeledobjects-part*.zip` | both deep-learning exports: the 1 October one from Pro and the ±60° re-export |
| `Segmented_202609290011302066080.tif*` | the ±60° mean-shift segmentation made in Pro on 29 September |
| `SHA256SUMS-derivatives-2026-10-06.txt` | checksums of every piece and of every reassembled file |

`restore.py` ([Restoring](#restoring)) rejoins and checks them. By hand: `cat global60_dem.tif.part* > global60_dem.tif` (or `copy /b a.part001+a.part002 a` in `cmd`), then check it against the sums.

Not backed up anywhere but the drive: the `.ovr` pyramids (Build Pyramids re-creates them) and the other geodatabase rasters, mostly legacy products the knowledge base finds defective and superseded (percent-rise slopes on a degree grid, a global composite mixing raw elevation with 8-bit bands).

## Keeping it current

Run from `Mars Remote Sensing Project\build\` on the drive; each script finds the drive from its own location, so `Z:` and `F:` both work.

```bash
python github_sync.py --commit
```

copies whatever changed into the clone, regenerates `docs/scripts.md`, commits and pushes. Files over 95 MB are reported and skipped.

```bash
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" github_export_gdb.py --rasters
```

re-exports the geodatabase's vector layers into `exports/` and rewrites the layer catalog (and stages the GeoPackage and the GUI SVM maps for the release). Run it after digitising: a re-export rewrites every geodatabase file even when nothing changed, so it isn't worth running otherwise. `--catalog-only` rewrites just the catalog.

```bash
python github_release_bundle.py --upload data-YYYY-MM-DD
```

zips the rasters and publishes them as a new release.

```bash
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" github_catalog_rasters.py
```

rewrites [rasters.md](rasters.md) from the rasters' own headers (a few seconds). Run it after adding or rebuilding a raster product; a raster nobody has described shows up there as "(not described)".

```bash
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" github_release_large.py derivatives-YYYY-MM-DD
```

does the same for the large products: about two hours at 10 MB/s, resumable, and it stages one 1.9 GB piece at a time.

## Restoring

From a clone of this repository, [`restore.py`](../restore.py) rebuilds the drive (Python 3.9+, nothing to install):

```bash
python restore.py --dest E:\ --dry-run
python restore.py --dest E:\
```

It copies the repository's folders into place, downloads both releases (about 79 GB), checks every download against GitHub's SHA-256, unzips each bundle where it belongs, rejoins the split rasters into `Mars Project/Global60/` and checks each against its whole-file hash. Downloads resume if interrupted, and it never overwrites an existing file unless given `--force`. `--only <text>` restores just the assets whose names contain that text. The two Pro-GUI SVM maps, the segmentation and the GeoPackage go to `Mars Project/restored_from_gdb/`.

Then, by hand:

1. Download the four source rasters ([links](../README.md#source-data)) to the drive root.
2. Create `Mars Project/Mars Project.gdb` in Pro and copy the feature classes from `exports/mars_project_vectors.gdb` into it.
3. Re-create the directory junctions `Z:\TypeArea` and `Z:\Global60`, which the legacy Spatial Analyst tools need (they reject the space in "Mars Project").
4. Build pyramids on the large rasters.

The `.aprx` stores relative paths, so it opens from any drive letter. Layers that pointed at rasters not restored will show as broken until the `build/` scripts rebuild them.
