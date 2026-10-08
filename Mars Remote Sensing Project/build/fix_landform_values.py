# -*- coding: utf-8 -*-
r"""Recode the five ±60° landform maps so pixel value = class code (KB §36). ArcGIS Python.

    python fix_landform_values.py              the five maps in Z:\Mars Project\Global60
    python fix_landform_values.py --dir <d>    the same names in another folder (rehearsal)

Before: pixel 0 Crater, 1 steep/windy hills, 2 lava tube, 3 Normal Ground (ClassifyRaster's
0-based values; the codes 1-4 lived only in the attribute table). After: pixel 1..4 = the codes,
255 still no class. Each original (with its .ovr, .aux.xml, .vat.dbf, .xml) is MOVED to
Global60\_0based_originals\, not deleted, and the release data-2026-10-06 also holds them.
Idempotent: a map whose attribute table already has Value == Classvalue is skipped.
Pro must be closed: the .aprx layers point at these files (their symbology keys on Class_name,
so it survives the recode unchanged).
"""
import os, sys, glob, shutil, time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy
import landform_codes as LC

DIR = sys.argv[sys.argv.index("--dir") + 1] if "--dir" in sys.argv else on_drive(r"Mars Project\Global60")
NAMES = ["global60_landforms_svm_400m.tif"] + [f"global60_landforms_svm_400m_mode{n}.tif" for n in (3, 5, 7, 9)]
KEEP = os.path.join(DIR, "_0based_originals")

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def already_coded(path):
    return all(v == cv for v, cv in arcpy.da.SearchCursor(path, ["Value", "Classvalue"]))


def main():
    os.makedirs(KEEP, exist_ok=True)
    bad = 0
    for name in NAMES:
        path = os.path.join(DIR, name)
        if not os.path.exists(path):
            print(f"missing   {name}")
            continue
        if already_coded(path):
            print(f"skip      {name} (pixel values are already the class codes)")
            continue
        t = time.time()
        moved = os.path.join(KEEP, name)
        for f in glob.glob(glob.escape(path) + "*"):          # the .tif and its sidecars
            shutil.move(f, os.path.join(KEEP, os.path.basename(f)))
        h_src, h_dst, table, nd = LC.recode(moved, path)
        problems = LC.check(moved, path, h_src, h_dst, table, nd)
        bad += bool(problems)
        counts = ", ".join(f"{n} {h_dst[cv]:,}" for cv, n, _ in sorted(table.values()))
        print(f"{'ok' if not problems else 'FAILED'}  {name}  ({time.time() - t:.0f} s): {counts}")
        for p in problems:
            print("          ", p)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
