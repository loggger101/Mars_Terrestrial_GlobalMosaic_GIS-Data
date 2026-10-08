# -*- coding: utf-8 -*-
r"""Points every layer that reads through a junction at the real folder instead (KB §34).

Z:\Global60 and Z:\TypeArea are junctions for the legacy Spatial Analyst tools that reject the space
in "Mars Project" (§19.1). A junction stores an ABSOLUTE target, \??\Z:\Mars Project\..., so on the
desktop, where the drive mounts as F: (§2.4), F:\Global60 resolves to a Z: that isn't there. Any
layer that reads through it breaks. The .aprx stores relative paths, so a layer reading
"Mars Project\Global60" directly survives the letter change. Same files, so only the path changes.

Scripts keep using the junctions for geoprocessing. Layers in the project must not.

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must
sit BESIDE the real .aprx (§31.5). Idempotent.
"""
import os, sys, time, shutil
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
BKDIR = on_drive(r"Mars Project\.backups")
JUNCTIONS = {on_drive(r"Global60"): on_drive(r"Mars Project\Global60"),
             on_drive(r"TypeArea"): on_drive(r"Mars Project\TypeArea")}

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def through_junction(p):
    out = []
    for m in p.listMaps():
        for l in m.listLayers():
            if l.isGroupLayer or not l.supports("DATASOURCE"):
                continue
            src = l.dataSource
            for j in JUNCTIONS:
                if src.lower().startswith(j.lower() + "\\"):
                    out.append((m, l, j))
    return out


def main():
    p = arcpy.mp.ArcGISProject(APRX)
    todo = through_junction(p)
    print("layers reading through a junction:", len(todo))
    if not todo:
        return
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    for m, l, j in todo:
        old = l.dataSource
        l.updateConnectionProperties(j, JUNCTIONS[j])
        print("  %s | %s\n      %s -> %s%s" % (m.name, l.longName, old, l.dataSource,
                                             "   BROKEN" if l.isBroken else ""))
    p.save()
    left = through_junction(arcpy.mp.ArcGISProject(APRX))
    print("saved; still through a junction after reopening:", len(left))
    assert not left


if __name__ == "__main__":
    main()
