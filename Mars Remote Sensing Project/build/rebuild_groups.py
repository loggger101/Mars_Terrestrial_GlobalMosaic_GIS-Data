# -*- coding: utf-8 -*-
r"""Recreates two group layers so their internal CIM files carry the neutral names (KB §39.4).

Renaming a layer (fix_label_names.py) changes what Pro shows but not the file the .aprx stores it
in, which keeps the name it was created with, so the old wording still appeared in
build\aprx_live\ and so on the project page. A group created under the new name gets a new file. Each child is copied into the new group in its
original order (addLayerToGroup copies the layer, symbology included), the old group is removed,
and the top-level drawing order is restored. Never moveLayer inside a group: it drops layers
(KB §31.5).

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must sit
BESIDE the real .aprx (it stores relative paths, §31.5). Run audit_aprx.py afterwards.
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else r"Z:\Mars Project\Mars Project.aprx")
BKDIR = r"Z:\Mars Project\.backups"
GROUPS = [("Mars \u00b160\u00b0 Analysis", "Superseded: the 29\u201330 Sep GUI SVMs (KB \u00a730)"),
          ("Ius Chasma \u2014 digitising", "Digitising classes (empty)")]

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def top_level(m):
    """Top-level layers, top to bottom (a layer's longName has no backslash at the top level)."""
    return [l for l in m.listLayers() if "\\" not in l.longName]


def main():
    if "--aprx" not in sys.argv:
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    for map_name, group_name in GROUPS:
        m = p.listMaps(map_name)[0]
        old = [l for l in top_level(m) if l.isGroupLayer and l.name == group_name]
        if len(old) != 1:
            sys.exit("%s: expected one group %r, found %d" % (map_name, group_name, len(old)))
        old = old[0]
        before_top = [l.name for l in top_level(m)]
        children = [l for l in old.listLayers() if l.longName.count("\\") == 1]
        before_kids = [(c.name, c.visible) for c in children]
        new = m.createGroupLayer(group_name + " \u00b7new")
        new.visible = old.visible
        for c in children:                       # BOTTOM in top-to-bottom order keeps their order
            m.addLayerToGroup(new, c, "BOTTOM")
        m.removeLayer(old)
        new.name = group_name
        after_kids = [(c.name, c.visible) for c in new.listLayers() if c.longName.count("\\") == 1]
        assert after_kids == before_kids, (before_kids, after_kids)
        # restore the top-level drawing order
        tops = {l.name: l for l in top_level(m)}
        for above, below in zip(before_top, before_top[1:]):
            m.moveLayer(tops[above], tops[below], "AFTER")
        after_top = [l.name for l in top_level(m)]
        assert after_top == before_top, (before_top, after_top)
        print("  %s: %r rebuilt, %d children, order kept" % (map_name, group_name, len(after_kids)))
    p.save()
    print("saved", APRX)


if __name__ == "__main__":
    main()
