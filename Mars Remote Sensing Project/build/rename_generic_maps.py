# -*- coding: utf-8 -*-
r"""Gives the five maps of the author's September GUI work names that say what they hold (KB §69.71).

At the author's request (2026-11-03, "Rename them"). Two of the five were both called "Mars", so each map is found
by its name AND a layer it holds, and the script refuses unless exactly one map matches each rule. Only names change:
no layer, extent or symbology. Idempotent: a map already renamed is reported, not touched.

  "Mars" (one layer, the OnMars MDIM service)        -> "Mars — Viking MDIM web basemap"
  "Mars" (one layer, the HRSC/MOLA DEM)              -> "Mars — HRSC/MOLA DEM"
  "Map2" (the hosted CTX mosaic, KB §3)              -> "Mars — CTX web mosaic"
  "Map3" (Viking, THEMIS, DEM with gradients)        -> "Mars — sources with gradients (Sep GUI work)"
  "Mars High-Resolution Mosaic Viewer"               -> "Mars — sources and composite (Sep GUI work)"

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy beside the real .aprx (§31.5).
"""
import os, sys, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
BKDIR = on_drive(r"Mars Project\.backups")
RULES = [  # (old name, a layer name it must hold, new name)
    ("Mars", "MDIM", "Mars — Viking MDIM web basemap"),
    ("Mars", "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif", "Mars — HRSC/MOLA DEM"),
    ("Map2", "Global CTX Mosaic of Mars (V01)", "Mars — CTX web mosaic"),
    ("Map3", "Gradient_Mars_M1", "Mars — sources with gradients (Sep GUI work)"),
    ("Mars High-Resolution Mosaic Viewer", "CompositeBand", "Mars — sources and composite (Sep GUI work)"),
]

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def main():
    p = arcpy.mp.ArcGISProject(APRX)
    maps = p.listMaps()
    plan = []
    for old, layer, new in RULES:
        if any(m.name == new for m in maps):
            print("already   %s" % new)
            continue
        hits = [m for m in maps if m.name == old and any(l.name == layer for l in m.listLayers())]
        if len(hits) != 1:
            sys.exit("refused: %d maps named %r hold %r (want 1); nothing renamed" % (len(hits), old, layer))
        plan.append((hits[0], old, new))
    if not plan:
        print("nothing to rename"); return
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    for m, old, new in plan:
        m.name = new
        print("renamed   %-36s -> %s" % (old, new))
    p.save()
    print("saved %s; %d maps" % (APRX, len(arcpy.mp.ArcGISProject(APRX).listMaps())))


if __name__ == "__main__":
    main()
