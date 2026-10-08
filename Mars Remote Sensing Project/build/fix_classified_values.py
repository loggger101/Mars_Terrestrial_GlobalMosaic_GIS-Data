# -*- coding: utf-8 -*-
r"""Recode the remaining 0-based classified rasters so pixel value = class code (KB §36.4). ArcGIS Python.

    python fix_classified_values.py                  the rasters below
    python fix_classified_values.py --gdb <g> --tif-dir <d>   another gdb / folder (rehearsal)

  TypeArea\ius_sup_spectral / _thermal / _augmented.tif   pixels 0..5 -> codes 1..6 (KB §27)
      originals (with sidecars) MOVED to TypeArea\_0based_originals\
  Mars Project.gdb\Classified_202609292109007048151 / ..._202609300147338582853
      the two GUI SVM maps, pixels 0..3 -> codes 1..4 (KB §29-30). They had no NoData value,
      only a mask, and the 29 Sep map's masked pixels read as 0 (= Crater): they become NoData 255.
      Recoded to a GeoTIFF on internal disk, checked, then the original is RENAMED to <name>_0based
      in the gdb and the recode copied in under the original name, so the .aprx layers (symbology
      keyed on Class_name) keep working. Nothing is deleted.

Idempotent: a raster whose table already has Value == Classvalue is skipped. Pro must be closed.
The ±60° landform maps were done by fix_landform_values.py (§36.1).
"""
import os, sys, glob, shutil, time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
from osgeo import gdal
import landform_codes as LC

GDB = sys.argv[sys.argv.index("--gdb") + 1] if "--gdb" in sys.argv else on_drive(r"Mars Project\Mars Project.gdb")
TIFS = sys.argv[sys.argv.index("--tif-dir") + 1] if "--tif-dir" in sys.argv else on_drive(r"Mars Project\TypeArea")
TIF_NAMES = ["ius_sup_spectral.tif", "ius_sup_thermal.tif", "ius_sup_augmented.tif"]
GDB_NAMES = ["Classified_202609292109007048151", "Classified_202609300147338582853"]
SCRATCH = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mars_scratch", "recode")

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def already_coded(path):
    return all(v == cv for v, cv in arcpy.da.SearchCursor(path, ["Value", "Classvalue"]))


def same_pixels(a_path, b_path):
    """Pixels that differ in validity, or in value where both are valid. A file gdb keeps NoData as
    a mask, not a value: under it GDAL reads 0 where the GeoTIFF has 255, so raw values can't be
    compared there (and 0 is no class code any more, so a raw reader can't take it for Crater)."""
    da, db = gdal.Open(LC.gdal_path(a_path)), gdal.Open(LC.gdal_path(b_path))
    a, b = da.GetRasterBand(1), db.GetRasterBand(1)
    diff = 0
    for y in range(0, a.YSize, 2048):
        h = min(2048, a.YSize - y)
        ma = a.GetMaskBand().ReadAsArray(0, y, a.XSize, h) > 0
        mb = b.GetMaskBand().ReadAsArray(0, y, a.XSize, h) > 0
        va, vb = a.ReadAsArray(0, y, a.XSize, h), b.ReadAsArray(0, y, a.XSize, h)
        diff += int((ma != mb).sum()) + int(((va != vb) & ma & mb).sum())
    return diff


def report(name, problems, h_dst, table, t):
    counts = ", ".join(f"{n} {h_dst[cv]:,}" for cv, n, _ in sorted(table.values()))
    print(f"{'ok' if not problems else 'FAILED'}  {name}  ({time.time() - t:.0f} s): {counts}; NoData {h_dst[256]:,}", flush=True)
    for p in problems:
        print("          ", p)
    return bool(problems)


def fix_tif(name):
    path = os.path.join(TIFS, name)
    if already_coded(path):
        print(f"skip      {name} (already class codes)")
        return False
    t = time.time()
    keep = os.path.join(TIFS, "_0based_originals")
    os.makedirs(keep, exist_ok=True)
    for f in glob.glob(glob.escape(path) + "*"):
        shutil.move(f, os.path.join(keep, os.path.basename(f)))
    moved = os.path.join(keep, name)
    h_src, h_dst, table, nd = LC.recode(moved, path)
    return report(name, LC.check(moved, path, h_src, h_dst, table, nd), h_dst, table, t)


def readable_and_coded(path):
    try:
        return already_coded(path)
    except Exception:          # a raster half-written when the drive dropped can't be opened
        return False


def fix_gdb(name):
    path, oldp = os.path.join(GDB, name), os.path.join(GDB, name + "_0based")
    resumed = arcpy.Exists(oldp)            # an earlier run renamed the original, then stopped
    if arcpy.Exists(path) and readable_and_coded(path):
        print(f"skip      {name} (already class codes)")
        return False
    t = time.time()
    if resumed and arcpy.Exists(path):
        # the copy an interrupted run left behind (2026-10-07: Z: dropped off USB mid-copy);
        # the original is safe under _0based, so only this partial output goes
        print(f"removing  the partial {name} left by an interrupted run (unreadable or not recoded)")
        arcpy.management.Delete(path)
    src = oldp if resumed else path
    os.makedirs(SCRATCH, exist_ok=True)
    tmp = os.path.join(SCRATCH, name + ".tif")
    if arcpy.Exists(tmp):
        arcpy.management.Delete(tmp)
    h_src, h_dst, table, nd = LC.recode(src, tmp)
    problems = LC.check(src, tmp, h_src, h_dst, table, nd)
    if problems:
        return report(name, problems, h_dst, table, t)
    # Build the gdb raster on internal disk, where CopyRaster's small block writes are fast, then
    # copy the finished dataset to Z: in one go: CopyRaster straight onto the USB drive took 40+ min
    # and the drive dropped out under it.
    stage = os.path.join(SCRATCH, "stage.gdb")
    if not arcpy.Exists(stage):
        arcpy.management.CreateFileGDB(SCRATCH, "stage.gdb")
    staged = os.path.join(stage, name)
    if arcpy.Exists(staged):
        arcpy.management.Delete(staged)
    arcpy.management.CopyRaster(tmp, staged, nodata_value=str(nd), pixel_type="8_BIT_UNSIGNED")
    arcpy.management.BuildPyramids(staged, resample_technique="NEAREST")
    arcpy.management.CalculateStatistics(staged)
    if not resumed:
        arcpy.management.Rename(path, name + "_0based")
    arcpy.management.Copy(staged, path)
    # the copy in the gdb must be the recode exactly, and keep the table the layers key on
    diff = same_pixels(tmp, path)
    if diff:
        problems.append(f"{diff:,} pixels differ between the recode and its copy in the gdb")
    rows = lambda p: sorted(r[:3] for r in arcpy.da.SearchCursor(p, ["Value", "Classvalue", "Class_name"]))
    if rows(tmp) != rows(path):
        problems.append(f"attribute table lost in the copy: {rows(path)}")
    if not problems:
        arcpy.management.Delete(tmp)
        arcpy.management.Delete(staged)
    return report(name, problems, h_dst, table, t)


def main():
    bad = 0
    for n in TIF_NAMES:
        if os.path.exists(os.path.join(TIFS, n)):
            bad += fix_tif(n)
    for n in GDB_NAMES:
        if arcpy.Exists(os.path.join(GDB, n)):
            bad += fix_gdb(n)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
