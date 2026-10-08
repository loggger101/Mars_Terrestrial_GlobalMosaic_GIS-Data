# -*- coding: utf-8 -*-
r"""Take everything that isn't Mars out of the project (KB §37). ArcGIS Python. Pro must be closed.

    python remove_non_mars.py --aprx <copy beside the real .aprx>    rehearse the map removal
    python remove_non_mars.py                                         the real project

Instruction, 2026-10-07: anything that isn't part of Mars is not relevant; remove it.
Nothing is deleted outright. Every item goes to Z:\_removed_not_Mars\, which can be deleted manually:

  .aprx maps whose coordinate system is not Mars, and which no layout uses:
      "Map" (Earth: World Topographic + World Hillshade, WGS 84),
      "Map1" and "Enceladus" (the Enceladus Cassini DEM, a broken link; Earth basemaps),
      "Mercury" (the MESSENGER basemap, a broken link)
      -> removed from the project after a backup to Mars Project\.backups\; each removed map is
         first exported to _removed_not_Mars\<name>.mapx so it can be imported again
  Mars Project.gdb\Mercury_MESSEN_IsoClusterUns (the Mercury Iso Cluster rehearsal, KB §7)
      -> copied to _removed_not_Mars\removed_not_Mars.gdb, checked, then removed from the project gdb
  build\aprx_live\: the Enceladus and Mercury layer files of the 2026-09-18 .aprx snapshot -> moved
"""
import os, sys, glob, shutil, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

APRX = sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv else r"Z:\Mars Project\Mars Project.aprx"
REHEARSAL = "--aprx" in sys.argv
GDB = r"Z:\Mars Project\Mars Project.gdb"
OUT = r"Z:\_removed_not_Mars"
MAPS = {"Map", "Map1", "Enceladus", "Mercury"}
RASTERS = ["Mercury_MESSEN_IsoClusterUns"]
SNAPSHOT = r"Z:\Mars Remote Sensing Project\build\aprx_live"

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def is_mars(sr):
    return "mars" in ((sr.GCS.datumName if sr.GCS else "") + sr.name).lower()


def maps():
    if not REHEARSAL:
        bk = os.path.join(os.path.dirname(APRX), ".backups",
                          f"Mars Project {time.strftime('%Y%m%d-%H%M%S')}.aprx")
        shutil.copy2(APRX, bk)
        print("backup  ", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    in_layouts = {e.map.name for l in p.listLayouts() for e in l.listElements("MAPFRAME_ELEMENT") if e.map}
    gone = []
    for m in p.listMaps():
        if m.name not in MAPS:
            continue
        assert not is_mars(m.spatialReference), f"{m.name} is in a Mars coordinate system: not removing"
        assert m.name not in in_layouts, f"{m.name} is used by a layout: not removing"
        if not REHEARSAL:
            m.exportToMAPX(os.path.join(OUT, f"{m.name}.mapx"))
        gone.append(f"{m.name} ({m.spatialReference.name})")   # read before deleteItem: m is dead after
        p.deleteItem(m)
    p.save()
    p = arcpy.mp.ArcGISProject(APRX)
    left = [m.name for m in p.listMaps()]
    print(f"maps removed: {gone}")
    print(f"maps left ({len(left)}), all Mars: {all(is_mars(m.spatialReference) for m in p.listMaps())}; "
          f"layouts {len(p.listLayouts())}")
    assert not MAPS & set(left)


def rasters():
    hold = os.path.join(OUT, "removed_not_Mars.gdb")
    if not arcpy.Exists(hold):
        arcpy.management.CreateFileGDB(OUT, "removed_not_Mars.gdb")
    for r in RASTERS:
        src, dst = os.path.join(GDB, r), os.path.join(hold, r)
        if not arcpy.Exists(src):
            print(f"already gone: {r}")
            continue
        if not arcpy.Exists(dst):
            arcpy.management.Copy(src, dst)
        a, b = arcpy.Raster(src), arcpy.Raster(dst)
        assert (a.width, a.height, a.bandCount, a.pixelType) == (b.width, b.height, b.bandCount, b.pixelType), "copy differs"
        del a, b
        arcpy.management.Delete(src)
        print(f"moved   {r} -> {dst}")


def snapshot():
    dst = os.path.join(OUT, "aprx_live_snapshot_2026-09-18")
    for f in glob.glob(os.path.join(SNAPSHOT, "*", "*.json")):
        if any(k in os.path.basename(f).lower() for k in ("enceladus", "mercury", "ercury_messenger")):
            to = os.path.join(dst, os.path.basename(os.path.dirname(f)))
            os.makedirs(to, exist_ok=True)
            shutil.move(f, os.path.join(to, os.path.basename(f)))
            print(f"moved   {os.path.relpath(f, SNAPSHOT)}")


if __name__ == "__main__":
    if REHEARSAL:
        maps()
        sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write("Removed from the Mars project on %s because they are not Mars (remove_non_mars.py, KB section 37).\n"
                "Nothing here is used by the project. Safe to delete this whole folder.\n"
                "*.mapx: the removed maps (Map, Map1, Enceladus, Mercury); import one into Pro to get it back.\n"
                "removed_not_Mars.gdb: the Mercury Iso Cluster raster.\n"
                "aprx_live_snapshot_2026-09-18: the Enceladus/Mercury layer files of an old .aprx snapshot.\n"
                % time.strftime("%Y-%m-%d"))
    maps()
    rasters()
    snapshot()
