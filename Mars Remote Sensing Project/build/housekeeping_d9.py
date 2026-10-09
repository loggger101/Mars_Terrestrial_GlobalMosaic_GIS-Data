# -*- coding: utf-8 -*-
r"""Housekeeping deletions approved 2026-10-09 (NEXT-STEPS D9, KB §11 q4, §50). ArcGIS Python. Pro must be closed.

    python housekeeping_d9.py --dry-run      list what would go, check every precondition, write nothing
    python housekeeping_d9.py                do it

Approved items, each checked before it goes:
  the 9 _2/_3 copies of the IAU nomenclature classes   each must be row-for-row identical (fields, CRS,
                                                       attributes, coordinates) to its original, which stays
  Line, Point                                          must hold 0 rows
  Landform_ChannelCandidates_auto_60_smoke,            the one-tile smoke test of the ±60° pass (§28.11);
  Landform_CraterCandidates_auto_60_smoke              make_global_landforms.py --smoke rebuilds them
  map "mars"                                           must hold only the broken Jezero HiRISE layer and
                                                       sit in no layout

Before anything is deleted: the .aprx is copied to Mars Project\.backups\, every class is copied to a
file gdb OUTSIDE the drive (BACKUP below, internal disk) and its row count checked, and the map is
exported to .mapx there. Z:\_removed_not_Mars\ is not handled here: it goes to the Recycle Bin from
PowerShell, so it can still be restored until the bin is emptied.
"""
import os, re, sys, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

DRY = "--dry-run" in sys.argv
APRX = on_drive(r"Mars Project\Mars Project.aprx")
GDB = on_drive(r"Mars Project\Mars Project.gdb")
BKDIR = on_drive(r"Mars Project\.backups")
BACKUP = r"C:\Users\Loggg\Mars_deleted_2026-10-09"
EMPTY = ["Line", "Point"]
SMOKE = ["Landform_ChannelCandidates_auto_60_smoke", "Landform_CraterCandidates_auto_60_smoke"]
MAPNAME, HIRISE = "mars", "JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first.tif"

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"
arcpy.env.workspace = GDB


def rows(fc):
    flds = [f.name for f in arcpy.ListFields(fc) if f.type not in ("OID", "Geometry", "GlobalID")
            and f.name.lower() not in ("shape_length", "shape_area")]
    sr = arcpy.Describe(fc).spatialReference.name
    with arcpy.da.SearchCursor(fc, ["SHAPE@XY"] + flds) as c:
        return flds, sr, sorted((round(r[0][0], 9), round(r[0][1], 9)) + tuple(r[1:]) for r in c)


def count(fc):
    return int(arcpy.management.GetCount(fc)[0])


fcs = arcpy.ListFeatureClasses()
dups = sorted(f for f in fcs if re.search(r"_March2019_\d$", f))
problems = []
for d in dups:
    orig = re.sub(r"_\d$", "", d)
    if orig not in fcs:
        problems.append("%s: original %s missing" % (d, orig))
    elif rows(d) != rows(orig):
        problems.append("%s differs from %s" % (d, orig))
for e in EMPTY:
    if e in fcs and count(e):
        problems.append("%s holds %d rows" % (e, count(e)))
for s in SMOKE:
    if s not in fcs:
        problems.append("%s missing" % s)
p = arcpy.mp.ArcGISProject(APRX)
in_layouts = {mf.map.name for l in p.listLayouts() for mf in l.listElements("MAPFRAME_ELEMENT") if mf.map}
mp = [m for m in p.listMaps() if m.name == MAPNAME]
if len(mp) != 1:
    problems.append("expected one map %r, found %d" % (MAPNAME, len(mp)))
else:
    lyrs = mp[0].listLayers()
    if [l.name for l in lyrs] != [HIRISE] or not lyrs[0].isBroken:
        problems.append("map %r holds %s, not only the broken HiRISE layer" % (MAPNAME, [l.name for l in lyrs]))
    if MAPNAME in in_layouts:
        problems.append("map %r is in a layout" % MAPNAME)
targets = dups + [e for e in EMPTY if e in fcs] + SMOKE
print("to delete (%d classes): %s" % (len(targets), ", ".join("%s (%d)" % (t, count(t)) for t in targets if t in fcs)))
print("and the map %r" % MAPNAME)
if problems:
    sys.exit("REFUSING:\n  " + "\n  ".join(problems))
print("all preconditions hold")
if DRY:
    sys.exit("dry run: nothing written")

os.makedirs(BKDIR, exist_ok=True)
bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
shutil.copy2(APRX, bk); print("backup", bk)
os.makedirs(BACKUP, exist_ok=True)
bgdb = os.path.join(BACKUP, "deleted_classes.gdb")
if not arcpy.Exists(bgdb):
    arcpy.management.CreateFileGDB(BACKUP, "deleted_classes.gdb")
for t in targets:
    dst = os.path.join(bgdb, t)
    if not arcpy.Exists(dst):
        arcpy.management.Copy(os.path.join(GDB, t), dst)
    assert count(dst) == count(os.path.join(GDB, t)), "backup of %s incomplete" % t
print("backed up %d classes to %s" % (len(targets), bgdb))
mp[0].exportToMAPX(os.path.join(BACKUP, "mars.mapx"))
for t in targets:
    arcpy.management.Delete(os.path.join(GDB, t))
    print("  deleted", t)
p.deleteItem(mp[0])
p.save()
left = arcpy.ListFeatureClasses()
print("project now: %d maps, %d layouts, %d feature classes" % (len(p.listMaps()), len(p.listLayouts()), len(left)))
