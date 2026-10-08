# -*- coding: utf-8 -*-
"""Re-extract the live .aprx and list every map, layer and data connection."""
import sys as _sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import json
import os
import shutil
import zipfile

APRX = on_drive(r"Mars Project\Mars Project.aprx")
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aprx_live")

if os.path.isdir(DEST):
    shutil.rmtree(DEST)
zipfile.ZipFile(APRX).extractall(DEST)

maps, layers = [], []
for root, _dirs, files in os.walk(DEST):
    for fn in files:
        if not fn.endswith(".json"):
            continue
        path = os.path.join(root, fn)
        try:
            d = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        t = d.get("type", "")
        if t == "CIMMap":
            maps.append((os.path.relpath(path, DEST), d))
        elif t.startswith("CIM") and "Layer" in t:
            layers.append((os.path.relpath(path, DEST), d))

print("=" * 78)
print("MAPS (%d)" % len(maps))
for rel, d in sorted(maps, key=lambda kv: kv[1].get("name", "")):
    ext = d.get("defaultExtent", {})
    sr = ext.get("spatialReference", {})
    wkt = sr.get("wkt", "")
    crs = wkt.split('"')[1] if '"' in wkt else str(sr.get("wkid", "?"))
    print("\n  %-38s  [%s]" % (d.get("name"), crs))
    if ext:
        print("     extent  x %.4f .. %.4f   y %.4f .. %.4f"
              % (ext.get("xmin", 0), ext.get("xmax", 0),
                 ext.get("ymin", 0), ext.get("ymax", 0)))
    for key in ("layers", "standaloneTables"):
        for uri in d.get(key, []) or []:
            print("     layer   %s" % uri)
    for b in d.get("bookmarks", []) or []:
        print("     BOOKMARK %s" % b.get("name"))

print()
print("=" * 78)
print("LAYERS (%d)" % len(layers))
for rel, d in sorted(layers, key=lambda kv: kv[1].get("name", "")):
    conn = d.get("dataConnection", {}) or {}
    ws = conn.get("workspaceConnectionString", "")
    ds = conn.get("dataset", "")
    print("  %-14s %-52s" % (d.get("type", "")[3:], d.get("name", "")))
    if ds or ws:
        print("        %s  |  %s" % (ds, ws))
