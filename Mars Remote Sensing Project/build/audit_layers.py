# -*- coding: utf-8 -*-
"""Full data connections, group-layer membership, layouts and renderer settings."""
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import json
import os

DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aprx_live")

docs = {}
for root, _d, files in os.walk(DEST):
    for fn in files:
        if fn.endswith(".json"):
            p = os.path.join(root, fn)
            try:
                docs[os.path.relpath(p, DEST).replace("\\", "/")] = json.load(
                    open(p, encoding="utf-8"))
            except Exception:
                pass


def by_uri(uri):
    key = uri.replace("CIMPATH=", "")
    return docs.get(key)


print("=" * 78)
print("LAYOUTS")
lay = [d for d in docs.values() if isinstance(d, dict)
       and d.get("type") in ("CIMLayout",)]
print("  %d layout(s) in the project" % len(lay))
for d in lay:
    print("   -", d.get("name"))

print()
print("=" * 78)
print("GROUP LAYERS in the mosaic viewer")
for name, d in docs.items():
    if not isinstance(d, dict) or d.get("type") != "CIMGroupLayer":
        continue
    print("\n  GROUP: %s   (%s)" % (d.get("name"), name))
    for uri in d.get("layers", []) or []:
        child = by_uri(uri)
        if child:
            conn = child.get("dataConnection", {}) or {}
            print("      - %-52s %s | %s"
                  % (child.get("name"), conn.get("dataset", ""),
                     conn.get("workspaceConnectionString", "")))
        else:
            print("      - <unresolved> %s" % uri)

print()
print("=" * 78)
print("EVERY RASTER LAYER: dataset, workspace, stretch")
for name, d in docs.items():
    if not isinstance(d, dict) or d.get("type") != "CIMRasterLayer":
        continue
    conn = d.get("dataConnection", {}) or {}
    col = d.get("colorizer", {}) or {}
    print("\n  %s" % d.get("name"))
    print("      dataset   : %s" % conn.get("dataset"))
    print("      workspace : %s" % conn.get("workspaceConnectionString"))
    print("      colorizer : %s" % col.get("type"))
    for k in ("stretchType", "standardDeviationParam", "minPercent", "maxPercent",
              "useCustomStretchMinMax", "customStretchMin", "customStretchMax"):
        if k in col:
            print("      %-10s: %s" % (k, col[k]))

print()
print("=" * 78)
print("SERVICE LAYERS (live web services)")
for name, d in docs.items():
    if not isinstance(d, dict):
        continue
    conn = d.get("dataConnection", {}) or {}
    url = conn.get("URL") or conn.get("url")
    if url:
        print("  %-52s %s" % (d.get("name"), url))
