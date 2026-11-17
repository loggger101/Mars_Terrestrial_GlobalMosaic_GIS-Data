# -*- coding: utf-8 -*-
r"""Layout 22: how much of the four-class map each band set decides (T1's band sets mapped; KB §56.1, §69.149).

  data   Global60\global60_bandset_change_<set>_0p5deg.tif   per 0.5° cell, the share whose class differs from the
                                                             all-band 400 m map, for nothermal, novisible, terrain
         from make_bandset_change.py, whose log logs\bandset_change.json gives every share on the sheet; the held-out
         scores are read from logs\global60_classification_check_<set>400m.json (§56.1)
  maps   "Mars ±60° — band set: <set>", one per set, the grid over the hillshade
  layout 22_bandset_change
         A without the thermal bands, B without the visible bands, C slope and relief alone, on layout 21's scale;
         a table of each set's change and held-out score, and one of the class areas each set gives

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy. Run polish_layouts.py afterwards.
"""
import os, sys, time, shutil, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from layoutkit import text, poly_geom
from make_global60_maps import (outline, add, get_map, order, page, add_text, extent_polygon, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table, hillshade
from make_thermal_change_layout import classify, key, SHARE

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
LOG = os.path.join(HERE, "logs", "bandset_change.json")
CHECK = os.path.join(HERE, "logs", "global60_classification_check_%s400m.json")   # "" for all bands, "nothermal_" ...
L22 = "22_bandset_change"
SETS = [("nothermal", "A", "No thermal bands (Viking RGB, slope, relief)", "no thermal"),
        ("novisible", "B", "No visible bands (night, day, slope, relief)", "no visible"),
        ("terrain", "C", "Slope and relief alone", "terrain only")]
FW, FH = 5.85, 1.95                                  # 3:1, the ±60° extent
FY = {"nothermal": 5.05, "novisible": 2.80, "terrain": 0.55}

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def build_map(p, k, grid):
    m = get_map(p, "Mars ±60° — band set: %s" % k)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.2)
    g = add(m, grid, "Share of each 0.5° cell whose class differs from the all-band map", transparency=15)
    classify(g, SHARE)
    hs = hillshade(m)
    order(m, [ext.name, g.name, hs.name])
    add_graticule(p, m.name, G30, 6)
    return m


def sheet(p, maps, R):
    lyt = page(p, L22)
    ck = {k: json.load(open(CHECK % ("" if k == "all" else k + "_"), encoding="utf-8"))["held_out"]
          for k in ["all"] + [s[0] for s in SETS]}
    pc = lambda v: "%.1f %%" % (100 * v)
    els, dark, grey = [], (40, 40, 40), (70, 70, 70)
    for k, letter, lab, _ in SETS:
        y = FY[k]
        mf = lyt.createMapFrame(poly_geom(0.45, y, FW, FH), maps[k], "frame_" + k)
        mf.camera.setExtent(extent_polygon().projectAs(maps[k].spatialReference).extent)
        s = R["sets"][k]
        els.append(text(0.45, y + FH + 0.06, "%s  %s: %s changes, held-out accuracy %s"
                        % (letter, lab, pc(s["share_changed"]), pc(ck[k]["accuracy"])), 9, "label_" + letter.lower(),
                        bold=True))
    rows = [["map", "changes", "held-out", "Crater won"],
            ["all seven bands", "–", pc(ck["all"]["accuracy"]), ck["all"]["polygons_majority_own_class"]["Crater"]]]
    for k, _, _, short in SETS:
        rows.append([short, pc(R["sets"][k]["share_changed"]), pc(ck[k]["accuracy"]),
                     ck[k]["polygons_majority_own_class"]["Crater"]])
    names = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
    arows = [["class", "all", "no th.", "no vis.", "terrain"]]
    for n in names:
        arows.append([n, pc(R["sets"]["nothermal"]["class_area_all"][n])]
                     + [pc(R["sets"][k]["class_area_set"][n]) for k, _, _, _ in SETS])
    terr = R["sets"]["terrain"]["share_changed"]
    els += [
        text(0.45, 7.80, "Mars ±60°: how much of the map each band set decides (T1's band sets mapped)", 18, "title",
             bold=True),
        text(0.45, 7.47, "The four-class SVM at 400 m, each band set trained on the same polygons; each panel: the share "
             "of each 0.5° cell whose class differs from the all-band map.", 10, "subtitle", colour=grey),
        text(6.60, 4.20, "Each set against the all-band map", 9.5, "table_title", bold=True, colour=dark),
        text(6.60, 2.75, "Class shares of ±60°", 9.5, "table2_title", bold=True, colour=dark),
        text(6.60, 1.05, ("Slope and relief alone give %s of the map the all-band class; the\nvisible bands decide "
                          "more of the rest than the thermal bands. Held-out\naccuracy hardly separates the sets (KB "
                          "§56.1), the map does. Cos-latitude\nweighted; 1° either side of 180° left out.")
             % pc(1 - terr), 7.8, "notes", colour=dark),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
    els += key(6.60, 6.85, "Share of the cell that changes", [(l, c) for _, l, c in SHARE], "keya")
    els += table(6.60, 4.13, rows, [1.05, 0.62, 0.68, 0.72], size=7.4)
    els += table(6.60, 2.68, arows, [1.02, 0.55, 0.55, 0.58, 0.62], size=7.2)
    add_text(lyt, els)
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L22 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    R = json.load(open(LOG, encoding="utf-8"))
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("1. maps")
    maps = {k: build_map(p, k, os.path.join(G.OUTDIR, R["sets"][k]["grid"])) for k, _, _, _ in SETS}
    print("2. layout", L22)
    sheet(p, maps, R)
    p.save()
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
