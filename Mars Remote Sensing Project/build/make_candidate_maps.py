# -*- coding: utf-8 -*-
r"""Puts the machine candidates and the empty digitising classes INTO the project (KB §32).

Digitising is the critical path (KB §11 q16), but nothing needed for it was in any map: the
three empty Landform_* digitising classes, the 2,610 channel candidates (§25), the 1,685
crater candidates (§26) and the 5,144 ±60° basin candidates (§28.11). This adds:

  map "Ius Chasma — digitising"   the three empty digitising classes on top (ready to edit), the candidates
                                  under them, the type-area rasters under those
  map "Mars ±60° — basins"        basin candidates sized by diameter, IAU craters > 100 km
  layouts 06_ius_digitising, 07_global60_basins, exported to Global60\layouts\

The 188 candidates worth the time (slope >= 5° AND thermal index < -0.15, §25) are a definition
query, not a copy: accepting one is still a copy into Landform_ChannelCenterlines, manually.

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must
sit BESIDE the real .aprx (it stores relative paths, §31.5). Run polish_layouts.py afterwards (§33).
"""
import os, sys, time, shutil
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import json
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
import areas
from layoutkit import text, poly_geom
from make_global60_maps import (outline, add, group, get_map, page, add_text, legend_classes, order,
                                extent_polygon, CREDIT, BKDIR, OUTD)

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
GDB = on_drive(r"Mars Project\Mars Project.gdb")
TA = on_drive(r"Mars Project\TypeArea")
BAS = "Mars \u00b160\u00b0 \u2014 basins"
LAYOUTS = {"ius": "06_ius_digitising", "ath": "09_athabasca_digitising"}
GOOD = "SlopeDeg >= 5 AND ThermIdx < -0.15"          # §25: steep AND rock-floored
# The prompt per area. Ius: steep and rock-floored (§25). Athabasca: rock-floored only; 97 % of its
# candidates lie under 2°, so a slope test leaves 5 of 3,283 and separates nothing there (§42).
PROMPT = {"ius": (GOOD, "steep and rock-floored",
                  "are steep (\u2265 5\u00b0) and rock-floored (thermal index < \u22120.15): start there"),
          "ath": ("ThermIdx < -0.15", "rock-floored",
                  "are rock-floored (thermal index < \u22120.15): start there; on these lava plains slope cannot help")}
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


def digitising(p, key, sr, camera_from=None):
    """Map "<area> — digitising" and its layout: the empty digitising classes on top, the area's
    machine candidates under them, its 100 m rasters under those (KB §32.1; Athabasca §42)."""
    A = dict(areas.AREAS[key], key=key)
    W = (A["bounds"][2] - A["bounds"][0]) / 100.0; H = (A["bounds"][3] - A["bounds"][1]) / 100.0
    folder = on_drive(os.path.join("Mars Project", A["folder"]))
    pre = A["prefix"] + "_"
    name, lname = "%s \u2014 digitising" % A["name"], LAYOUTS[key]
    print("map:", name)
    m = get_map(p, name)
    m.spatialReference = sr
    chan = os.path.join(GDB, A["channels"]); crat = os.path.join(GDB, A["craters"])
    q, short, why = PROMPT[key]
    n_good, n_all = count(chan, q), count(chan)
    plateau = count(chan, "SlopeDeg < 2") / float(n_all)
    n_crat = count(crat)
    prec = json.load(open(os.path.join(HERE, "logs", "crater_density.json")))["areas"][key]["detector_vs_robbins"]["1.0"]["precision"]
    gyou = group(m, "Digitising classes (empty)")
    l = add(m, os.path.join(GDB, "Landform_ChannelCenterlines"), "Channel centrelines", True, gyou)
    line_style(l, (0, 92, 230), 2.5)
    l = add(m, os.path.join(GDB, "Landform_LavaFlowMargins"), "Lava flow margins", True, gyou)
    line_style(l, (230, 76, 0), 2.5)
    l = add(m, os.path.join(GDB, "Landform_CraterRims"), "Crater rims", True, gyou)
    outline(l, (255, 255, 0), 2.0)
    gc = group(m, "Machine candidates \u2014 prompts, not results (KB \u00a725\u201326, \u00a742)")
    good = add(m, chan, "Channels: %s (%d)" % (short, n_good), True, gc)
    good.definitionQuery = q
    line_style(good, (0, 255, 255), 1.6)
    rest = add(m, chan, "Channels: other (%d, %.0f%% on < 2\u00b0 plateau)" % (n_all - n_good, 100 * plateau), False, gc)
    rest.definitionQuery = "NOT (%s)" % q
    line_style(rest, (150, 150, 150), 0.5)
    cr = add(m, crat, "Closed depressions \u2265 1 km (%d)" % n_crat, True, gc)
    outline(cr, (255, 0, 197), 0.8)
    gb = group(m, "Type-area rasters (100 m)")
    add(m, os.path.join(folder, pre + "thermal_contrast.tif"), "Diurnal contrast index (valid inside this window)", False, gb)
    add(m, os.path.join(folder, pre + "viking.tif"), "Viking MDIM 2.1 (visible)", False, gb)
    add(m, os.path.join(folder, pre + "slope_deg.tif"), "Slope (degrees)", False, gb)
    add(m, os.path.join(folder, pre + "hillshade.tif"), "Hillshade 225\u00b0/45\u00b0", True, gb)
    order(m, [gyou.name, gc.name, gb.name])
    print("   ", [l.longName for l in m.listLayers()])

    lyt = page(p, lname)
    aspect = W / H
    wide = aspect >= 1.6
    fh_max = 4.71
    fw = 10.10 if wide else fh_max * aspect
    fh = fw / aspect
    mf = lyt.createMapFrame(poly_geom(0.45, 2.42, fw, fh), m, "frame")
    if camera_from is not None:
        mf.camera.X, mf.camera.Y, mf.camera.scale = camera_from.camera.X, camera_from.camera.Y, camera_from.camera.scale
    else:
        xmin, ymin, xmax, ymax = A["bounds"]
        mf.camera.setExtent(arcpy.Extent(xmin, ymin, xmax, ymax, spatial_reference=sr))
    breached = ("Breached craters are missed (Oudemans, KB \u00a726)." if key == "ius"
                else "Breached craters are missed (KB \u00a726).")
    add_text(lyt, [
        text(0.45, 7.85, "%s \u2014 candidates to digitise" % A["name"], 21, "title", bold=True),
        text(0.45, 7.50, "Machine candidates are prompts: accept one by copying it into the matching digitising class. "
             "The three digitising classes are empty and on top, ready to edit.", 10.5, "subtitle", colour=(70, 70, 70)),
        text(0.45, 0.72, "Cyan: %d of %d channel candidates %s."
             "\nThe other %d stay switched off; %.0f%% of all candidates sit on plateau under 2\u00b0, "
             "where routing follows DEM noise.\nMagenta: %d closed depressions \u2265 1 km; only %.0f%% match a catalogued (Robbins) "
             "crater (KB \u00a742.3). %s"
             % (n_good, n_all, why, n_all - n_good, 100 * plateau, n_crat, 100 * prec, breached), 8.8, "notes", colour=(40, 40, 40)),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))])
    names = [good.name, cr.name, "Channel centrelines", "Crater rims", "Lava flow margins"]
    if wide:
        surrounds(p, lyt, mf, (0.50, 1.72), (10.25, 1.52))   # 9.95 sat against the legend box (KB §34)
        legend_classes(p, lyt, mf, 4.3, 2.30, 5.4, 0.62, names, names=False, cols=3)
    else:                                                     # a squarer window: legend beside the frame
        x = 0.45 + fw + 0.35
        surrounds(p, lyt, mf, (x, 2.55), (10.25, 2.45))
        legend_classes(p, lyt, mf, x, 7.10, 10.55 - x, 2.4, names, names=False, cols=1)
    out = os.path.join(OUTD, lname + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)
    return m



def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    ius = p.listMaps("Ius Chasma Type Area")[0]

    # ------------------------------------------------------------------ digitising maps and layouts
    print("1. digitising maps")
    src06 = p.listLayouts("01_visible")[0].listElements("MAPFRAME_ELEMENT")[0]
    digitising(p, "ius", ius.spatialReference, camera_from=src06)
    digitising(p, "ath", ius.spatialReference)

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
