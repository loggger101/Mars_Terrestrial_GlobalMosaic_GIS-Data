# -*- coding: utf-8 -*-
r"""Finish one fix_classified_values.py gdb recode whose last step, the copy onto Z:, failed (KB §36.4).
ArcGIS Python. Pro must be closed.

    python fix_classified_finish.py Classified_202609292109007048151

Needs what that run left: <name>_0based in the gdb, no <name>, and on internal disk the checked
recode (<name>.tif) and its staged gdb copy. Copies the staged raster in under <name>, then runs the
same checks as fix_gdb. 2026-10-07: Copy failed with ERROR 000260 (file read/write) onto the USB drive.
"""
import os, sys, time
import arcpy
import fix_classified_values as F

name = sys.argv[1]
path, oldp = os.path.join(F.GDB, name), os.path.join(F.GDB, name + "_0based")
tmp = os.path.join(F.SCRATCH, name + ".tif")
staged = os.path.join(F.SCRATCH, "stage.gdb", name)
assert arcpy.Exists(oldp) and not arcpy.Exists(path), "not the state an interrupted copy leaves"
assert arcpy.Exists(tmp) and arcpy.Exists(staged), "the recode or its staged copy is missing: rerun fix_classified_values.py"

problems = []
if F.same_pixels(tmp, staged):
    problems.append("the staged copy differs from the recode")
t = time.time()
if not problems:
    for attempt in (1, 2, 3):
        try:
            arcpy.management.Copy(staged, path)
            break
        except arcpy.ExecuteError as e:
            print(f"copy attempt {attempt} failed: {str(e).strip().splitlines()[0]}", flush=True)
            if arcpy.Exists(path):
                arcpy.management.Delete(path)
            if attempt == 3:
                raise
            time.sleep(30)
    diff = F.same_pixels(tmp, path)
    if diff:
        problems.append(f"{diff:,} pixels differ between the recode and its copy in the gdb")
    rows = lambda p: sorted(r[:3] for r in arcpy.da.SearchCursor(p, ["Value", "Classvalue", "Class_name"]))
    if rows(tmp) != rows(path):
        problems.append(f"attribute table lost in the copy: {rows(path)}")
print(f"{'ok' if not problems else 'FAILED'}  {name}  ({time.time() - t:.0f} s)")
for p in problems:
    print("          ", p)
if not problems:
    arcpy.management.Delete(tmp)
    arcpy.management.Delete(staged)
sys.exit(1 if problems else 0)
