# -*- coding: utf-8 -*-
r"""Renames layers and layout text that were worded in the third person (KB §39.3, §39.4).

make_global60_maps.py and make_candidate_maps.py named them as notes about one person; they show
in the project and in the legends of the interim deck. This applies neutral_voice.py's rules to
every layer name and every layout text element in the .aprx, so the project and the builders
(which now write the neutral names too) agree. Idempotent. Pro must be closed; the .aprx is
backed up first. --dry-run reports without saving.
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neutral_voice import rewrite

APRX = r"Z:\Mars Project\Mars Project.aprx"
BKDIR = r"Z:\Mars Project\.backups"
DRY = "--dry-run" in sys.argv

assert DRY or not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"

p = arcpy.mp.ArcGISProject(APRX)
todo = []
for m in p.listMaps():
    for l in m.listLayers():
        new = rewrite(l.name)
        if new != l.name:
            todo.append(("layer", "%s / %s" % (m.name, l.name), l, "name", new))
for lyt in p.listLayouts():
    for e in lyt.listElements("TEXT_ELEMENT"):
        new = rewrite(e.text)
        if new != e.text:
            todo.append(("text", "%s / %s" % (lyt.name, e.name), e, "text", new))
for kind, where, obj, attr, new in todo:
    print("  %-5s %s\n        %r\n     -> %r" % (kind, where, getattr(obj, attr)[:90], new[:90]))
if not todo:
    sys.exit("nothing to rename")
if DRY:
    sys.exit("dry run: %d changes, nothing saved" % len(todo))
bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
shutil.copy2(APRX, bk); print("backup", bk)
for kind, where, obj, attr, new in todo:
    setattr(obj, attr, new)
p.save()
print("saved: %d changes" % len(todo))
