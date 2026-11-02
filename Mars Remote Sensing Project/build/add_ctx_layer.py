# -*- coding: utf-8 -*-
r"""Stream the global CTX mosaic (~5 m) into the two digitising maps, for judging candidates in Pro (KB §69.52).

    python add_ctx_layer.py                      # back up the .aprx, add the layer to both maps, save
    python add_ctx_layer.py --aprx <copy.aprx>   # the same on a copy, no backup
    python add_ctx_layer.py --aprx <copy.aprx> --check <out.png> <class> <oid> [km]
                                                 # also export one window around a candidate, CTX under its line

The layer is Esri's tiled service of the Murray Lab's global CTX mosaic, V01 (Dickson et al. 2024; credit NASA/JPL/
MSSS/The Murray Lab, free use for all purposes): nothing is downloaded to the drive, Pro fetches tiles while the map
is drawn, so it needs a network connection. It goes at the top level of "Ius Chasma — digitising" and "Athabasca
Valles — digitising", under the digitising classes and the candidates, over the 100 m type-area rasters, visible.
The service is in geographic Mars 2000 sphere coordinates; Pro projects it to the maps' equidistant cylindrical
(central meridian 180°) frame, which --check confirms against a candidate line. Rerunning skips a map that has it.
ArcGIS Python, Pro closed.
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
from make_global60_maps import order, BKDIR

CTX_URL = "https://astro.arcgis.com/arcgis/rest/services/OnMars/CTX1/MapServer"
CTX_NAME = "CTX mosaic, ~5 m (Murray Lab V01, streamed: needs a network)"
MAPS = ["Ius Chasma — digitising", "Athabasca Valles — digitising"]
RASTERS = "Type-area rasters (100 m)"
APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    for name in MAPS:
        m = p.listMaps(name)[0]
        top = [l.name for l in m.listLayers() if not l.longName.count("\\")]
        if CTX_NAME in top:
            print(name, ": has the layer")
            continue
        l = m.addDataFromPath(CTX_URL)
        l.name, l.visible = CTX_NAME, True
        top = [x.name for x in m.listLayers() if not x.longName.count("\\")]
        assert RASTERS in top, "no %s group in %s: %s" % (RASTERS, name, top)
        rest = [n for n in top if n not in (CTX_NAME, RASTERS)]
        order(m, rest + [CTX_NAME, RASTERS])
        print(name, ":", [x.name for x in m.listLayers() if not x.longName.count("\\")])
    p.save()
    if "--check" in sys.argv:
        i = sys.argv.index("--check")
        out, cls, oid = sys.argv[i + 1], sys.argv[i + 2], int(sys.argv[i + 3])
        km = float(sys.argv[i + 4]) if len(sys.argv) > i + 4 and not sys.argv[i + 4].startswith("--") else 20.0
        check(p, out, cls, oid, km)


def check(p, out, cls, oid, km):
    """One window around candidate oid of cls: CTX with the line drawn on it, everything else off."""
    m = p.listMaps(MAPS[1] if cls.endswith("_ath") else MAPS[0])[0]
    g = next(r[0] for r in arcpy.da.SearchCursor(os.path.join(GDB, cls), ["SHAPE@"], "OBJECTID = %d" % oid))
    for l in m.listLayers():
        if not l.isGroupLayer:
            l.visible = l.name == CTX_NAME
    probe = m.addDataFromPath(os.path.join(GDB, cls))
    probe.definitionQuery = "OBJECTID = %d" % oid
    probe.visible = True
    sym = probe.symbology
    sym.renderer.symbol.color = {"RGB": [235, 104, 52, 100]}
    sym.renderer.symbol.width = 1.2
    probe.symbology = sym
    lyt = p.createLayout(6, 6, "INCH", "ctx_check")
    mf = lyt.createMapFrame(arcpy.Extent(0, 0, 6, 6), m, "frame")
    c = g.extent
    cx, cy, h = (c.XMin + c.XMax) / 2, (c.YMin + c.YMax) / 2, km * 500.0
    mf.camera.setExtent(arcpy.Extent(cx - h, cy - h, cx + h, cy + h, spatial_reference=m.spatialReference))
    lyt.exportToPNG(out, resolution=120)
    print("check:", out)


if __name__ == "__main__":
    main()
