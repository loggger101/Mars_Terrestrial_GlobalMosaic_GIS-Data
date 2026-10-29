# -*- coding: utf-8 -*-
r"""Exports what Mars Project.gdb holds that github_sync.py cannot copy (KB §35). ArcGIS Python.

    python github_export_gdb.py              vectors -> <repo>\exports\mars_project_vectors.gdb
                                             and     -> <dist>\mars_project_vectors.gpkg
    python github_export_gdb.py --rasters    also the two Pro-GUI SVM maps -> <dist>\*.tif
    python github_export_gdb.py --rasters-only   only the two SVM maps
    python github_export_gdb.py --catalog-only   only rewrite exports\README.md, no re-export.
                                             Re-exporting rewrites every gdb file even when the data
                                             is unchanged, so do it when the layers have changed.

The gdb is 200+ GB of rasters, but its feature classes are small and they hold the one thing
nothing can re-compute: the 512 hand-drawn training polygons. Every feature class goes, except the
third-party reference layers (Ref_*). The scratch classes "Line"/"Point", the _2/_3 duplicates of the
IAU nomenclature and the two ±60° smoke classes were deleted from the gdb on 2026-10-09 (KB §50); the
filter below still skips the first two kinds should they reappear. The empty Landform_* classes go too:
their schema is the work.
Row counts are checked against the source for each class.

The two SVM maps (29 and 30 Sep, §29-30) exist only inside the gdb, so they are written as
DEFLATE-compressed GeoTIFFs for the release. Superseded (§31), but they are original work. Pixel value =
class code 1-4 since 2026-10-07 (§36.4). The gdb keeps no-data as a mask, with 0 or 255 stored under
it, so the export writes 255 under the mask and declares NoData 255: a reader that ignores masks
can't take a masked pixel for a class.

Reads Z: only. --repo and --dist as in github_sync.py / github_release_bundle.py.
"""
import os, sys, shutil, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

DRIVE = Path(__file__).resolve().parents[2]
SRC = str(DRIVE / "Mars Project" / "Mars Project.gdb")
REPO = Path(sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else
            Path.home() / "OneDrive" / "Documents" / "GitHub" / "Mars_Terrestrial_GlobalMosaic_GIS-Data")
DIST = Path(sys.argv[sys.argv.index("--dist") + 1] if "--dist" in sys.argv else
            Path(os.environ["LOCALAPPDATA"]) / "Temp" / "mars_github_dist")
SVM_MAPS = ["Classified_202609292109007048151", "Classified_202609300147338582853"]

# What each class is, for exports\README.md. A class missing here is listed without a description.
ABOUT = {
    "Landform_TrainingSamples_terrain": "**The 512 hand-drawn training polygons**, four classes, planet-wide (KB §29.2). "
        "The labels everything supervised is trained on.",
    "Landform_TrainingSamples_terrain_60_train": "The hand-drawn polygons clipped to ±60° and split by whole 15° blocks, seed 60: "
        "the 329 used for training (KB §31.3).",
    "Landform_TrainingSamples_terrain_60_test": "The 183 held out: never trained on, used only for scoring (KB §31.3).",
    "Landform_TrainingSamples_v2_proposals": "The seven-class revision (D17), proposed, not decided: the 512 with an "
        "`Action` and its evidence each, plus 574 new polygons for classes 5-7. Only rows the author sets `Review` "
        "accept on enter the v2 labels, through `apply_label_review.py` (KB §68.5, §69.2).",
    "Landform_TrainingSamples_v2p": "A rehearsal, not the author's labels: every v2 proposal taken as proposed "
        "(`apply_label_review.py --rehearsal`), to test the v2 runs before the review (KB §69.4). Never a result.",
    "Landform_TrainingSamples_v2p_60_train": "The rehearsal labels clipped to ±60°, training half (827; KB §69.4).",
    "Landform_TrainingSamples_v2p_60_test": "The rehearsal labels clipped to ±60°, held-out half (258; KB §69.4).",
    "Landform_TrainingSamples_v2": "**The seven-class labels**, from the author's review of the proposals (D17): "
        "classes 1-4 as before, 5-7 new. The author's own rows by eye; the apron and fluvial strips by a written rule, "
        "at the author's word (KB §69.8). The labels the final's seven-class maps are trained and scored on.",
    "Landform_TrainingSamples_v2_60_train": "The seven-class labels clipped to ±60°, training half: the same whole 15° "
        "blocks as the four-class split (KB §69.8).",
    "Landform_TrainingSamples_v2_60_test": "The seven-class labels clipped to ±60°, held out in the same 14 blocks: "
        "never trained on, used only for scoring (KB §69.8).",
    "TrainingSamples_202609290009589587982": "The first hand-drawn training set, saved from Pro on 29 Sep (455 polygons, KB §29.2).",
    "Landform_ChannelCenterlines": "Digitising target, task 11: channel centrelines accepted in review from the "
        "machine candidates (`accept_reviewed.py`), and any drawn by hand (KB §69.7).",
    "Landform_CraterRims": "Digitising target, task 11: crater rims accepted in review from the machine candidates "
        "(`accept_reviewed.py`), and any drawn by hand (KB §69.7).",
    "Landform_LavaFlowMargins": "Digitising target, task 11. Empty until digitised by hand.",
    "Landform_ChannelCandidates_auto": "Machine channel centrelines over Ius Chasma, from flow routing with filled ground masked out "
        "(KB §25). `SlopeDeg >= 5 AND ThermIdx < -0.15` selects the 188 steep, rock-floored ones worth digitising.",
    "Landform_CraterCandidates_auto": "Machine crater candidates over Ius Chasma: closed depressions ≥ 1 km from fill "
        "depth (KB §26). Blind to breached craters.",
    "Landform_BasinCandidates_auto_60": "Closed basins ≥ 20 km over ±60°, the coarse planet-scale pass (KB §28.11, §32.1).",
    "Analysis_Extent_60": "The analysis extent: ±60.0003° latitude, the THEMIS night mosaic's own edge (KB §16, §31.3).",
    "Check_Tiles_4096px_60": "The 4096-pixel processing tiles that the 29 Sep SVM map follows (KB §30.2).",
    "MARS_nomenclature_albedo_March2019": "IAU/USGS Gazetteer of Planetary Nomenclature, March 2019: albedo features.",
    "MARS_nomenclature_classicalbedo_March2019": "IAU/USGS Gazetteer, March 2019: classical albedo features.",
    "MARS_nomenclature_craters_gt100km_March2019": "IAU/USGS Gazetteer, March 2019: named craters over 100 km.",
    "MARS_nomenclature_craters_lt100km_March2019": "IAU/USGS Gazetteer, March 2019: named craters under 100 km.",
    "MARS_nomenclature_misc_March2019": "IAU/USGS Gazetteer, March 2019: other named features.",
    "Landform_CraterCandidates_auto_60": "Closed depressions ≥ 1 km over ±60°, the X2 fine pass (KB §53.4; the tiles "
        "over 180° rerun, §54).",
    "Landform_ChannelCandidates_auto_60": "Channel segments over ±60°, the X2 fine pass (KB §53.4, §54).",
    "Landform_CraterCandidates_auto_ath": "Crater candidates over the Athabasca Valles type area (KB §42.1).",
    "Landform_ChannelCandidates_auto_ath": "Channel candidates over the Athabasca Valles type area (KB §42.1).",
    "Landform_CraterCandidates_auto_60_smoke": "X2's smoke-test window (KB §53.3), recreated by the smoke run.",
    "Landform_ChannelCandidates_auto_60_smoke": "X2's smoke-test window (KB §53.3), recreated by the smoke run.",
    "Graticule_30deg": "Latitude / longitude lines every 30° over ±60°, labelled (KB §44).",
    "Graticule_2deg": "Lines every 2° over the two type-area windows (KB §44).",
    "Type_Areas": "The Ius Chasma and Athabasca Valles windows as polygons (KB §44).",
    "DL_Detections_heldout_20261019": "X5's RetinaNet detections over the held-out blocks: boxes with class and "
        "confidence (KB §66.2, §66.3).",
    "DL_UNet_Heldout_Scores_20261020": "The 183 held-out labels, each with its own-class share and majority class "
        "under the U-Net and under the published SVM map, at 400 m (KB §66.9).",
}
# Too big for git (their .gdbtable files reach 246 and 113 MB; GitHub refuses files over 100 MB):
# exported to the release GeoPackage only, and listed in exports\README.md as such (KB §57).
RELEASE_ONLY = {"Landform_CraterCandidates_auto_60", "Landform_ChannelCandidates_auto_60"}
RELEASE = "data-2026-10-29"            # the release whose GeoPackage holds them (KB §57.4, §63.2, §66.10, §69.28)
MAX_FILE = 95 * 1000 * 1000
SYSTEM_FIELDS = {"OBJECTID", "FID", "Shape", "SHAPE", "Shape_Length", "Shape_Area"}

arcpy.env.overwriteOutput = True


def vectors():
    arcpy.env.workspace = SRC
    fcs = [fc for fc in arcpy.ListFeatureClasses()
           if fc not in {"Line", "Point"} and not fc.endswith(("_March2019_2", "_March2019_3"))
           and not fc.startswith("Ref_")]       # third-party reference data (KB §41): not redistributed
    out = REPO / "exports"
    out.mkdir(parents=True, exist_ok=True)
    DIST.mkdir(parents=True, exist_ok=True)
    # Built in staging, then copied file by file: the clone is in OneDrive, which can hold a lock
    # on the folder itself, so the repo's .gdb folder is refilled, never deleted.
    fgdb, gpkg = DIST / "mars_project_vectors.gdb", DIST / "mars_project_vectors.gpkg"
    if fgdb.exists():
        shutil.rmtree(fgdb)
    if gpkg.exists():
        gpkg.unlink()
    arcpy.management.CreateFileGDB(str(DIST), fgdb.name)
    arcpy.management.CreateSQLiteDatabase(str(gpkg), "GEOPACKAGE_1.3")
    bad = 0
    for fc in fcs:
        n = int(arcpy.management.GetCount(fc)[0])
        dests = (gpkg,) if fc in RELEASE_ONLY else (fgdb, gpkg)
        if fc not in RELEASE_ONLY:
            arcpy.management.Copy(os.path.join(SRC, fc), str(fgdb / fc))
        arcpy.conversion.ExportFeatures(os.path.join(SRC, fc), str(gpkg / fc))
        counts = {int(arcpy.management.GetCount(str(d / fc))[0]) for d in dests}
        ok = counts == {n}
        bad += not ok
        print(f"{'ok' if ok else 'MISMATCH'}\t{n:>6}\t{fc}", flush=True)
    arcpy.management.ClearWorkspaceCache()
    big = [(f.name, f.stat().st_size) for f in fgdb.iterdir() if f.stat().st_size > MAX_FILE]
    assert not big, "files over %d MB would be refused by GitHub; add their class to RELEASE_ONLY: %s" % (
        MAX_FILE // 10**6, big)
    dst = out / fgdb.name
    dst.mkdir(exist_ok=True)
    for old in dst.iterdir():
        if not (fgdb / old.name).exists():
            old.unlink()
    for f in fgdb.iterdir():
        if f.suffix != ".lock":
            shutil.copy2(f, dst / f.name)
    kept = [fc for fc in fcs if fc not in RELEASE_ONLY]
    print(f"{len(kept)} feature classes -> {dst}\n{len(fcs):>2} feature classes -> {gpkg}")
    catalog(dst, kept, {fc: int(arcpy.management.GetCount(str(gpkg / fc))[0]) for fc in fcs if fc in RELEASE_ONLY})
    return bad


def catalog(fgdb, fcs, release_only=None, when=None):
    """exports\\README.md: one row per class, read back from the export itself; release_only = {class: rows}
    for the classes in the GeoPackage only; when = the export's date (default today)."""
    release_only = release_only or {}
    when = when or time.strftime('%Y-%m-%d')
    rows = []
    for fc in fcs:
        p = str(fgdb / fc)
        d = arcpy.Describe(p)
        fields = [f.name for f in arcpy.ListFields(p) if f.name not in SYSTEM_FIELDS and f.type not in ("OID", "Geometry")]
        rows.append(f"| `{fc}` | {d.shapeType} | {int(arcpy.management.GetCount(p)[0]):,} | "
                    f"{d.spatialReference.name} | {ABOUT.get(fc, '')} | {', '.join(f'`{x}`' for x in fields)} |")
    text = f"""# Vector layers from `Mars Project.gdb`

Exported by [`github_export_gdb.py`](../Mars%20Remote%20Sensing%20Project/build/github_export_gdb.py) on {when}.
Every feature class in the project geodatabase except the third-party reference layers (`Ref_*`:
the USGS geologic map and the Robbins crater database, available from their publishers). Row counts
were checked against the source.
"KB §N" is a section of the project knowledge base,
[`PROJECT-KNOWLEDGE.md`](../Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md).
The same layers are in the release as a GeoPackage (`mars_project_vectors.gpkg.zip`).

**Class codes in the training layers:** 1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground; the
seven-class labels (`*_v2*`) add 5 volcanic edifice, 6 apron, 7 fluvial channel. Every labelled file and model
uses these, and they are the project's schema (decided 2026-10-09, KB §11 q23; the seven classes 2026-10-22,
KB §68.1); a code is never renumbered. The class schema file `Composite Object Classes.ecs` swaps 2 and 3 and is superseded: don't draw
new samples under it (KB §29.2).

The Landform classes are in `Mars_Equidistant_Cylindrical_CM180` (metres, central meridian 180°);
the labels and nomenclature are in geographic `Mars_2000_(Sphere)`.

| Layer | Geometry | Rows | CRS | What it is | Fields |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"
    if release_only:
        text += ("\n**In the release GeoPackage only** (too big for git: GitHub refuses files over 100 MB): "
                 f"`mars_project_vectors.gpkg.zip` in [`{RELEASE}`](https://github.com/loggger101/"
                 f"Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/{RELEASE}):\n\n"
                 + "\n".join(f"- `{fc}`: {n:,} rows. {ABOUT.get(fc, '')}" for fc, n in release_only.items()) + "\n")
    (fgdb.parent / "README.md").write_text(text, encoding="utf-8", newline="\n")
    arcpy.management.ClearWorkspaceCache()
    print("catalog ->", fgdb.parent / "README.md")


def svm_maps():
    from osgeo import gdal
    import numpy as np
    gdal.UseExceptions()
    # Strips one block high, and a cache that holds them plus the output tiles being filled: full-width
    # 1024-row strips overflowed GDAL's default cache and re-read the drive (8 GB, output stalled).
    gdal.SetCacheMax(2 * 1024**3)
    DIST.mkdir(parents=True, exist_ok=True)
    for name in SVM_MAPS:
        dst = DIST / f"{name}.tif"
        src = gdal.Open(f"OpenFileGDB:{SRC}:{name}")
        b = src.GetRasterBand(1)
        assert b.DataType == gdal.GDT_Byte, f"{name}: not 8-bit"
        out = gdal.GetDriverByName("GTiff").Create(str(dst), src.RasterXSize, src.RasterYSize, 1, gdal.GDT_Byte, [
            "COMPRESS=DEFLATE", "ZLEVEL=9", "TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512",
            "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"])
        out.SetGeoTransform(src.GetGeoTransform())
        out.SetProjection(src.GetProjection())
        ob = out.GetRasterBand(1)
        ob.SetNoDataValue(255)
        valid, step, mb = 0, b.GetBlockSize()[1], b.GetMaskBand()
        for y in range(0, src.RasterYSize, step):
            h = min(step, src.RasterYSize - y)
            v = b.ReadAsArray(0, y, src.RasterXSize, h)
            m = mb.ReadAsArray(0, y, src.RasterXSize, h) > 0
            assert not (v[m] == 255).any(), f"{name}: a valid pixel holds the NoData value 255"
            v[~m] = 255
            ob.WriteArray(v, 0, y)
            valid += int(m.sum())
        ob.ComputeStatistics(False)
        out = ob = src = b = mb = None
        print(f"{name}.tif  {dst.stat().st_size / 1e6:.1f} MB, {valid:,} valid pixels", flush=True)


if __name__ == "__main__":
    if "--catalog-only" in sys.argv:   # rewrite exports\README.md from the export already in the repo
        fgdb = REPO / "exports" / "mars_project_vectors.gdb"
        arcpy.env.workspace = str(fgdb)
        # the export's own date, kept from the catalog it rewrites, not today's: --catalog-only re-exports
        # nothing. File times can't tell: a git pull restamps the clone's files (KB §63.2).
        import re
        old = (fgdb.parent / "README.md").read_text(encoding="utf-8")
        when = re.search(r"\) on (\d{4}-\d\d-\d\d)\.", old).group(1)
        catalog(fgdb, arcpy.ListFeatureClasses(),
                {fc: int(arcpy.management.GetCount(os.path.join(SRC, fc))[0]) for fc in sorted(RELEASE_ONLY)}, when)
        sys.exit(0)
    if "--rasters-only" in sys.argv:
        svm_maps()
        sys.exit(0)
    bad = vectors()
    if "--rasters" in sys.argv:
        svm_maps()
    sys.exit(1 if bad else 0)
