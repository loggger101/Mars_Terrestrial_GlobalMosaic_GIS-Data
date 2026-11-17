# -*- coding: utf-8 -*-
r"""Layout 21: where the thermal bands change the four-class map (T1 mapped; KB §56, §69.148).

  data   Global60\global60_thermal_change_0p5deg.tif   per 0.5° cell, the share whose class differs between the SVM
                                                       map with and without the two THEMIS bands
         Global60\global60_thermal_change_window.tif   the Hellas close-up at 200 m, the change grouped by kind
         both from make_thermal_change.py --window 25 -55 115 -25, whose log logs\thermal_change.json gives every
         number on the sheet
  maps   "Mars ±60° — the thermal bands' effect" (the grid over the hillshade) and
         "Mars ±60° — the thermal bands' effect, Hellas" (the close-up over the hillshade)
  layout 21_thermal_change
         A ±60°, the Hellas box outlined; B Hellas, 25–115°E, 55–25°S (the frame's 3:1); the key of each; the class table and the
         share changed by latitude band

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy. Run polish_layouts.py afterwards,
as after every layout builder.
"""
import os, sys, time, shutil, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from layoutkit import text, rect, poly_geom, C, rgb
from make_global60_maps import (outline, add, get_map, order, page, add_text, extent_polygon, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table, hillshade

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
LOG = os.path.join(HERE, "logs", "thermal_change.json")
GRID = os.path.join(G.OUTDIR, "global60_thermal_change_0p5deg.tif")
WIN = os.path.join(G.OUTDIR, "global60_thermal_change_window.tif")
MAPA, MAPB = "Mars ±60° — the thermal bands' effect", "Mars ±60° — the thermal bands' effect, Hellas"
L21 = "21_thermal_change"
FA = (0.45, 4.70, 6.90, 2.30)            # frame A: x, y, w, h (inches); ±60° fills it, 360° x 120°
FB = (0.45, 1.72, 6.90, 2.30)
SHARE = [(0.05, "under 5 %", (252, 251, 253)), (0.10, "5–10 %", (218, 218, 235)), (0.15, "10–15 %", (188, 189, 220)),
         (0.25, "15–25 %", (158, 154, 200)), (0.40, "25–40 %", (117, 107, 177)), (1.00, "over 40 %", (63, 0, 125))]
KINDS = [(0, "the same class", None),
         (1, "Crater with thermal, Normal Ground without", (230, 97, 1)),
         (2, "Normal Ground with thermal, Crater without", (94, 60, 153)),
         (3, "Crater with thermal, lava tube without", (227, 26, 28)),
         (4, "lava tube with thermal, Crater without", (33, 113, 181)),
         (5, "between lava tube and Normal Ground", (240, 200, 40)),
         (6, "to or from steep/windy hills", (40, 160, 90))]
GROUP_KEY = {1: "Crater with, Normal Ground without", 2: "Normal Ground with, Crater without",
             3: "Crater with, lava tube without", 4: "lava tube with, Crater without",
             5: "between lava tube and Normal Ground", 6: "to or from steep/windy hills"}

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def classify(layer, breaks, transparent_first=False):
    sym = layer.symbology
    sym.updateColorizer("RasterClassifyColorizer")
    sym.colorizer.classificationField = "Value"
    sym.colorizer.breakCount = len(breaks)
    for i, (brk, (ub, lab, col)) in enumerate(zip(sym.colorizer.classBreaks, breaks)):
        brk.upperBound = ub; brk.label = lab
        brk.color = {"RGB": [255, 255, 255, 0]} if col is None else {"RGB": list(col) + [100]}
    layer.symbology = sym


def box(x, y, w, h, name, colour, width):
    """An unfilled rectangle on the page."""
    g = C("CIMPolygonGraphic", "V3"); g.polygon = poly_geom(x, y, w, h)
    s = C("CIMSolidStroke", "V3"); s.color = rgb(*colour); s.width = width
    sym = C("CIMPolygonSymbol", "V3"); sym.symbolLayers = [s]
    ref = C("CIMSymbolReference", "V3"); ref.symbol = sym; g.symbol = ref
    el = C("CIMGraphicElement", "V3"); el.graphic = g; el.name = name; el.visible = True
    el.anchor = "BottomLeftCorner"
    return el


def build_maps(p):
    ma = get_map(p, MAPA)
    ext = add(ma, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    g = add(ma, GRID, "Share of each 0.5° cell whose class changes without the thermal bands", transparency=15)
    classify(g, [(ub, lab, col) for ub, lab, col in SHARE])
    hs = hillshade(ma)
    order(ma, [ext.name, g.name, hs.name])
    add_graticule(p, MAPA, G30, 7)
    mb = get_map(p, MAPB)
    w = add(mb, WIN, "The change at 200 m, by kind")
    classify(w, [(k + 0.5, lab, col) for k, lab, col in KINDS])
    hsb = hillshade(mb)
    order(mb, [w.name, hsb.name])
    add_graticule(p, MAPB, G30, 7)
    return ma, mb


def key(x, y, title, rows, name, swatch_h=0.14):
    dark = (40, 40, 40)
    els = [text(x, y, title, 9.5, name + "_title", bold=True, colour=dark)]
    yy = y - 0.27
    for i, (lab, col) in enumerate(rows):
        els.append(rect(x, yy, 0.30, swatch_h, "%s_sw%d" % (name, i), fill=col or (255, 255, 255),
                        stroke=(150, 150, 150), stroke_w=0.3))
        els.append(text(x + 0.40, yy + 0.01, lab, 7.8, "%s_lab%d" % (name, i), colour=dark))
        yy -= 0.205
    return els


def sheet(p, ma, mb, R):
    lyt = page(p, L21)
    mfa = lyt.createMapFrame(poly_geom(*FA), ma, "frame_a")
    mfa.camera.setExtent(extent_polygon().projectAs(ma.spatialReference).extent)
    mfb = lyt.createMapFrame(poly_geom(*FB), mb, "frame_b")
    W = R["window"]
    mfb.camera.setExtent(arcpy.Extent(W["lon0"], W["lat0"], W["lon1"], W["lat1"], spatial_reference=mb.spatialReference))
    # panel B's box on panel A: ±60° fills frame A, 360° by 120°, centred on 0°E
    bx = FA[0] + (W["lon0"] + 180.0) / 360.0 * FA[2]
    by = FA[1] + (W["lat0"] + 60.0) / 120.0 * FA[3]
    bw = (W["lon1"] - W["lon0"]) / 360.0 * FA[2]
    bh = (W["lat1"] - W["lat0"]) / 120.0 * FA[3]
    dark, grey = (40, 40, 40), (70, 70, 70)
    pc = lambda v: "%.1f %%" % (100 * v)
    t = R["table_with_rows_without_cols"]
    names = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
    crows = [["class", "with", "without", "changes"]]
    for n in names:
        crows.append([n, pc(R["class_area_with"][n]), pc(R["class_area_without"][n]), pc(R["changed_by_class_with"][n])])
    lb = R["changed_by_lat_band"]
    def lab(k):
        a, b = (int(s) for s in k.split(".."))
        h = lambda v: "%d°%s" % (abs(v), "S" if v < 0 else "N") if v else "0°"
        return "%s–%s" % (h(b), h(a)) if a >= 0 else "%s–%s" % (h(b), h(a))
    ks = list(lb)                                       # 12 bands, north to south: two columns of six
    lrows = [["north", "changes", "south", "changes"]] + [[lab(ks[i]), pc(lb[ks[i]]), lab(ks[i + 6]), pc(lb[ks[i + 6]])]
                                                          for i in range(6)]
    big = R["largest_change"]
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: where the thermal bands change the map (T1 mapped)", 18, "title", bold=True),
        text(0.45, 7.47, "The four-class SVM at 200 m, trained on the same polygons with all seven bands and without the "
             "two THEMIS bands: %s of ±60° changes class." % pc(R["share_changed"]), 10, "subtitle", colour=grey),
        text(0.45, FA[1] + FA[3] + 0.06, "A  ±60°: the share of each 0.5° cell that changes; outlined, panel B",
             10, "label_a", bold=True),
        text(0.45, FB[1] + FB[3] + 0.06, "B  Hellas, %d–%d°E, %d–%d°S: %s changes, half of it between Crater and lava tube"
             % (W["lon0"], W["lon1"], -W["lat0"], -W["lat1"], pc(W["share_changed"])), 10, "label_b", bold=True),
        box(bx, by, bw, bh, "hellas_box", (20, 20, 20), 1.2),
        text(7.65, 3.62, "Class shares of ±60°", 9.5, "table_title", bold=True, colour=dark),
        text(7.65, 2.32, "Share that changes, by 10° of latitude", 9.5, "table2_title", bold=True, colour=dark),
        text(0.45, 1.20, "The thermal bands move held-out accuracy by 1.4 points (KB §56) but the class of %s of the map, "
             "so a polygon score can hide that much change.\nThe largest change is %s with thermal, %s without (%s of ±60°). "
             "Cos-latitude weighted; 1° either side of 180° left out (KB §54.3)."
             % (pc(R["share_changed"]), big["with"], big["without"], pc(big["share"])), 7.9, "notes", colour=dark),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + key(7.65, 6.85, "A  Share of the cell that changes", [(l, c) for _, l, c in SHARE], "keya")
        + key(7.65, 5.35, "B  The change, by kind", [(l, c) for _, l, c in KINDS], "keyb")
        + table(7.65, 3.55, crows, [0.95, 0.45, 0.52, 0.55], size=7.4)
        + table(7.65, 2.25, lrows, [0.62, 0.45, 0.62, 0.45], size=7.0))
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L21 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    R = json.load(open(LOG, encoding="utf-8"))
    assert "window" in R, "run make_thermal_change.py --window 25 -55 115 -25 first"
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("1. maps")
    ma, mb = build_maps(p)
    print("2. layout", L21)
    sheet(p, ma, mb, R)
    p.save()
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
