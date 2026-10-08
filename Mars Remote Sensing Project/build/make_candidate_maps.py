# -*- coding: utf-8 -*-
r"""Puts the machine candidates and the empty digitising classes INTO the project (KB §32).

Digitising is the critical path (KB §11 q16), but nothing he needs for it was in any map: the
three empty Landform_* classes he digitises into, the 2,610 channel candidates (§25), the 1,685
crater candidates (§26) and the 5,144 ±60° basin candidates (§28.11). This adds:

  map "Ius Chasma — digitising"   his three empty classes on top (ready to edit), the candidates
                                  under them, the type-area rasters under those
  map "Mars ±60° — basins"        basin candidates sized by diameter, IAU craters > 100 km
  layouts 06_ius_digitising, 07_global60_basins, exported to Global60\layouts\

The 188 candidates worth his time (slope >= 5° AND thermal index < -0.15, §25) are a definition
query, not a copy: accepting one is still a copy into Landform_ChannelCenterlines, by him.

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must
sit BESIDE the real .aprx (it stores relative paths, §31.5). Run polish_layouts.py afterwards (§33).
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
from layoutkit import text, poly_geom
from make_global60_maps import (outline, add, group, get_map, page, add_text, legend_classes, order,
                                extent_polygon, CREDIT, BKDIR, OUTD)

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else r"Z:\Mars Project\Mars Project.aprx")
GDB = r"Z:\Mars Project\Mars Project.gdb"
TA = r"Z:\Mars Project\TypeArea"
DIG, BAS = "Ius Chasma \u2014 digitising", "Mars \u00b160\u00b0 \u2014 basins"
GOOD = "SlopeDeg >= 5 AND ThermIdx < -0.15"          # §25: steep AND rock-floored
PAGE_W, PAGE_H = 11.0, 8.5

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def line_style(layer, colour, width):
    sym = layer.symbology
    sym.renderer.symbol.color = {"RGB": list(colour) + [100]}
    sym.renderer.symbol.size = width
    layer.symbology = sym


def count(fc, where=None):
    with arcpy.da.SearchCursor(fc, ["OID@"], where) as c:
        return sum(1 for _ in c)


def surrounds(p, lyt, mf, sbar_xy, arrow_xy):
    for kind, (x, y), style, nm in [("SCALE_BAR", sbar_xy, "Double Alternating Scale Bar 1 Metric", "sbar"),
                                    ("NORTH_ARROW", arrow_xy, "ArcGIS North 1", "narrow")]:
        items = p.listStyleItems("ArcGIS 2D", kind)
        item = next((i for i in items if i.name == style), items[0])
        el = lyt.createMapSurroundElement(arcpy.Point(x, y), kind, mf, item, nm)
        if kind == "SCALE_BAR":
            el.elementWidth = 3.1


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    ius = p.listMaps("Ius Chasma Type Area")[0]

    # ------------------------------------------------------------------ Ius digitising map
    print("1. map:", DIG)
    m = get_map(p, DIG)
    m.spatialReference = ius.spatialReference
    chan = os.path.join(GDB, "Landform_ChannelCandidates_auto")
    n_good, n_all = count(chan, GOOD), count(chan)
    n_crat = count(os.path.join(GDB, "Landform_CraterCandidates_auto"))
    gyou = group(m, "YOURS to digitise into (empty)")
    l = add(m, os.path.join(GDB, "Landform_ChannelCenterlines"), "Channel centrelines", True, gyou)
    line_style(l, (0, 92, 230), 2.5)
    l = add(m, os.path.join(GDB, "Landform_LavaFlowMargins"), "Lava flow margins", True, gyou)
    line_style(l, (230, 76, 0), 2.5)
    l = add(m, os.path.join(GDB, "Landform_CraterRims"), "Crater rims", True, gyou)
    outline(l, (255, 255, 0), 2.0)
    gc = group(m, "Machine candidates \u2014 prompts, not results (KB \u00a725\u201326)")
    good = add(m, chan, "Channels: steep and rock-floored (%d)" % n_good, True, gc)
    good.definitionQuery = GOOD
    line_style(good, (0, 255, 255), 1.6)
    rest = add(m, chan, "Channels: other (%d, 64%% on < 2\u00b0 plateau)" % (n_all - n_good), False, gc)
    rest.definitionQuery = "NOT (%s)" % GOOD
    line_style(rest, (150, 150, 150), 0.5)
    cr = add(m, os.path.join(GDB, "Landform_CraterCandidates_auto"),
             "Craters: closed depressions \u2265 1 km (%d)" % n_crat, True, gc)
    outline(cr, (255, 0, 197), 0.8)
    gb = group(m, "Type-area rasters (100 m)")
    add(m, os.path.join(TA, "ius_thermal_contrast.tif"), "Diurnal contrast index (valid inside this window)", False, gb)
    add(m, os.path.join(TA, "ius_viking.tif"), "Viking MDIM 2.1 (visible)", False, gb)
    add(m, os.path.join(TA, "ius_slope_deg.tif"), "Slope (degrees)", False, gb)
    add(m, os.path.join(TA, "ius_hillshade.tif"), "Hillshade 225\u00b0/45\u00b0", True, gb)
    order(m, [gyou.name, gc.name, gb.name])
    print("   ", [l.longName for l in m.listLayers()])

    # ------------------------------------------------------------------ ±60° basins map
    print("2. map:", BAS)
    mb = get_map(p, BAS)
    iau = add(mb, os.path.join(GDB, "MARS_nomenclature_craters_gt100km_March2019"), "IAU named craters > 100 km")
    bas = add(mb, os.path.join(GDB, "Landform_BasinCandidates_auto_60"), "Basin candidates \u2265 20 km (5,144)")
    sym = bas.symbology
    sym.updateRenderer("GraduatedSymbolsRenderer")
    sym.renderer.classificationField = "DiameterKm"
    sym.renderer.breakCount = 5
    sym.renderer.minimumSymbolSize = 1.5
    sym.renderer.maximumSymbolSize = 12
    lo = 20
    for br in sym.renderer.classBreaks:           # whole-km labels, one colour: size carries diameter
        br.symbol.color = {"RGB": [0, 197, 255, 100]}
    bas.symbology = sym
    d = bas.getDefinition("V3")                    # labels set through arcpy.mp did not stick; set them in the CIM
    for br in d.renderer.breaks:
        br.label = "%d\u2013%d km" % (round(lo), round(br.upperBound)); lo = br.upperBound
    bas.setDefinition(d)
    sym = iau.symbology
    sym.renderer.symbol.color = {"RGB": [0, 0, 0, 0]}
    sym.renderer.symbol.outlineColor = {"RGB": [255, 60, 0, 100]}
    sym.renderer.symbol.outlineWidth = 1.5
    sym.renderer.symbol.size = 9
    iau.symbology = sym
    hs = add(mb, os.path.join(G.OUTDIR, "global60_hillshade.tif"), "Hillshade (\u00b160\u00b0, 200 m)")  # not the junction (KB §34)
    order(mb, [iau.name, bas.name, hs.name])
    mb.clipLayers(extent_polygon())

    # ------------------------------------------------------------------ layout 06
    print("3. layouts")
    lyt = page(p, "06_ius_digitising")
    src = p.listLayouts("01_visible")[0].listElements("MAPFRAME_ELEMENT")[0]
    fw = 10.10; fh = fw / (8891.0 / 4150.0)             # the type-area stack's 2.14:1
    mf = lyt.createMapFrame(poly_geom(0.45, 2.42, fw, fh), m, "frame")
    mf.camera.X, mf.camera.Y, mf.camera.scale = src.camera.X, src.camera.Y, src.camera.scale
    add_text(lyt, [
        text(0.45, 7.85, "Ius Chasma \u2014 candidates to digitise", 21, "title", bold=True),
        text(0.45, 7.50, "Machine candidates are prompts: accept one by copying it into your own class. "
             "Your three classes are empty and on top, ready to edit.", 10.5, "subtitle", colour=(70, 70, 70)),
        text(0.45, 0.72, "Cyan: %d of %d channel candidates are steep (\u2265 5\u00b0) and rock-floored (thermal index < \u22120.15): "
             "start there.\nThe other %d stay switched off; 64%% of all candidates sit on plateau under 2\u00b0, "
             "where routing follows DEM noise.\nMagenta: %d closed depressions \u2265 1 km. A breached crater is not a "
             "closed depression and is missing (Oudemans, just outside, KB \u00a726)."
             % (n_good, n_all, n_all - n_good, n_crat), 8.8, "notes", colour=(40, 40, 40)),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))])
    surrounds(p, lyt, mf, (0.50, 1.72), (10.25, 1.52))   # 9.95 sat against the legend box (KB §34)
    legend_classes(p, lyt, mf, 4.3, 2.30, 5.4, 0.62,
                   [good.name, cr.name, "Channel centrelines", "Crater rims", "Lava flow margins"],
                   names=False, cols=3)
    out = os.path.join(OUTD, "06_ius_digitising.png"); lyt.exportToPNG(out, resolution=150); print("   ", out)

    # ------------------------------------------------------------------ layout 07
    lyt = page(p, "07_global60_basins")
    fw = 10.1; fh = fw / 3.0
    mf = lyt.createMapFrame(poly_geom(0.45, 3.55, fw, fh), mb, "frame")
    mf.camera.setExtent(extent_polygon().projectAs(mb.spatialReference).extent)
    add_text(lyt, [
        text(0.45, 7.80, "Mars \u00b160\u00b0 \u2014 basin and crater candidates \u2265 20 km", 21, "title", bold=True),
        text(0.45, 7.46, "5,144 closed depressions in the HRSC/MOLA DEM at 200 m, found by fill depth in 48 s. "
             "Red rings: IAU named craters over 100 km.", 10, "subtitle", colour=(70, 70, 70)),
        text(0.45, 1.70, "Against all 117 named IAU craters \u2265 100 km inside \u00b158\u00b0: 68% recovered with "
             "diameter within \u00b150%;\ndiameter error median +2.2% (p10 \u221212.6%, p90 +20.8%). Hellas, Utopia "
             "and Isidis come out unprompted.\nThe missing third are the breached craters: not closed depressions, "
             "so invisible to this method (KB \u00a726, \u00a728.11).", 9.2, "notes", colour=(40, 40, 40)),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))])
    legend_classes(p, lyt, mf, 7.25, 3.30, 3.3, 1.9, [bas.name, iau.name], names=True, cols=1)
    out = os.path.join(OUTD, "07_global60_basins.png"); lyt.exportToPNG(out, resolution=150); print("   ", out)

    p.save()
    print("saved. layouts:", [x.name for x in p.listLayouts()])


if __name__ == "__main__":
    main()
