# -*- coding: utf-8 -*-
r"""Exports what Mars Project.gdb holds that github_sync.py cannot copy (KB §35). ArcGIS Python.

    python github_export_gdb.py              vectors -> <repo>\exports\mars_project_vectors.gdb
                                             and     -> <dist>\mars_project_vectors.gpkg
    python github_export_gdb.py --rasters    also his two Pro-GUI SVM maps -> <dist>\*.tif

The gdb is 200+ GB of rasters, but its feature classes are small and they hold the one thing
nothing can re-compute: his 512 hand-drawn training polygons. Every feature class goes, except
the two empty scratch classes "Line"/"Point" and the _2/_3 duplicates of the IAU nomenclature
(identical copies, §11 q4). The empty Landform_* classes go too: their schema is the work.
Row counts are checked against the source for each class.

The two SVM maps (29 and 30 Sep, §29-30) exist only inside the gdb, so they are written as
DEFLATE-compressed GeoTIFFs for the release. Superseded (§31), but they are his.

Reads Z: only. --repo and --dist as in github_sync.py / github_release_bundle.py.
"""
import os, sys, shutil
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

arcpy.env.overwriteOutput = True


def vectors():
    arcpy.env.workspace = SRC
    fcs = [fc for fc in arcpy.ListFeatureClasses()
           if fc not in {"Line", "Point"} and not fc.endswith(("_March2019_2", "_March2019_3"))]
    out = REPO / "exports"
    out.mkdir(parents=True, exist_ok=True)
    DIST.mkdir(parents=True, exist_ok=True)
    fgdb, gpkg = out / "mars_project_vectors.gdb", DIST / "mars_project_vectors.gpkg"
    if fgdb.exists():
        shutil.rmtree(fgdb)
    if gpkg.exists():
        gpkg.unlink()
    arcpy.management.CreateFileGDB(str(out), fgdb.name)
    arcpy.management.CreateSQLiteDatabase(str(gpkg), "GEOPACKAGE_1.3")
    bad = 0
    for fc in fcs:
        n = int(arcpy.management.GetCount(fc)[0])
        arcpy.management.Copy(os.path.join(SRC, fc), str(fgdb / fc))
        arcpy.conversion.ExportFeatures(os.path.join(SRC, fc), str(gpkg / fc))
        counts = {int(arcpy.management.GetCount(str(d / fc))[0]) for d in (fgdb, gpkg)}
        ok = counts == {n}
        bad += not ok
        print(f"{'ok' if ok else 'MISMATCH'}\t{n:>6}\t{fc}", flush=True)
    print(f"{len(fcs)} feature classes -> {fgdb}\n{' ' * 23}and {gpkg}")
    return bad


def svm_maps():
    from osgeo import gdal
    gdal.UseExceptions()
    for name in SVM_MAPS:
        dst = DIST / f"{name}.tif"
        ds = gdal.Open(f"OpenFileGDB:{SRC}:{name}")
        gdal.Translate(str(dst), ds, creationOptions=[
            "COMPRESS=DEFLATE", "ZLEVEL=9", "TILED=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512",
            "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"])
        ds = None
        print(f"{name}.tif  {dst.stat().st_size / 1e6:.1f} MB", flush=True)


if __name__ == "__main__":
    bad = vectors()
    if "--rasters" in sys.argv:
        svm_maps()
    sys.exit(1 if bad else 0)
