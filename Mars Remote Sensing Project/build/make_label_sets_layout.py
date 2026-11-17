# -*- coding: utf-8 -*-
r"""Layout 26: the three label sets side by side — how the training ground grew (KB §19.4, §69.8, §69.49, §69.150).

The lead maps owe most of their gain to the third label set (paper Section sec:v3; Appendix A), but no sheet sets the
three label sets beside each other. This one draws each over ±60° in the class colours of labelsets.COLOURS, filled:
  A  Landform_TrainingSamples_terrain   the four-class polygons the author drew (§19.4)
  B  Landform_TrainingSamples_v2        the seven-class second set (§69.8)
  C  Landform_TrainingSamples_v3        the third set, placed by written rules (§69.49)
with, measured here on every run and written to logs\label_sets.json: the polygons of each class; the total area on
the sphere (geodesic, km²) and its share of ±60°; and the number of 15° blocks that hold a label (by the polygon's
centroid, floor(lon / 15)_floor(lat / 15) as make_block_split.py names them).

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy. Run polish_layouts.py afterwards.
"""
import os, sys, time, shutil, json, math, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
from labelsets import SEVEN, COLOURS
from layoutkit import text, rect, poly_geom
from make_global60_maps import (outline, add, get_map, order, page, add_text, extent_polygon, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table, hillshade

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
LOG = os.path.join(HERE, "logs", "label_sets.json")
L26 = "26_label_sets"
SETS = [("four", "Landform_TrainingSamples_terrain", "A", "The four-class polygons, drawn by the author"),
        ("second", "Landform_TrainingSamples_v2", "B", "The second label set, seven classes"),
        ("third", "Landform_TrainingSamples_v3", "C", "The third label set, placed by written rules")]
R_KM = 3396.19
AREA60 = 4 * math.pi * R_KM ** 2 * math.sin(math.radians(60))      # the ±60° band, km²
FW, FH = 5.85, 1.95
FY = {"four": 5.05, "second": 2.80, "third": 0.55}

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def measure():
    res = {"area_pm60_km2": round(AREA60), "sets": {}}
    for k, fc, _, _ in SETS:
        cls, area, blocks = collections.Counter(), 0.0, set()
        with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["Classname", "SHAPE@"]) as c:
            for name, g in c:
                cls[name] += 1
                area += g.getArea("GEODESIC", "SQUAREKILOMETERS")
                pt = g.centroid
                blocks.add("%d_%d" % (math.floor(pt.X / 15.0), math.floor(pt.Y / 15.0)))
        res["sets"][k] = {"fc": fc, "polygons": sum(cls.values()), "by_class": {n: cls.get(n, 0) for n in SEVEN},
                          "area_km2": round(area), "share_pm60": round(area / AREA60, 5), "blocks": len(blocks)}
        print("   %-7s %6d polygons  %12.0f km2  %d blocks" % (k, sum(cls.values()), area, len(blocks)))
    json.dump(res, open(LOG, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return res


def filled(layer):
    sym = layer.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = ["Classname"]
    for grp in sym.renderer.groups:
        for it in grp.items:
            col = list(COLOURS.get(it.values[0][0], (255, 255, 255)))
            it.symbol.color = {"RGB": col + [100]}
            it.symbol.outlineColor = {"RGB": col + [100]}
            it.symbol.outlineWidth = 0.4
    layer.symbology = sym


def build_map(p, k, fc):
    m = get_map(p, "Mars ±60° — label set: %s" % k)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.2)
    lab = add(m, os.path.join(GDB, fc), "Training and held-out polygons")
    filled(lab)
    hs = hillshade(m)
    order(m, [ext.name, lab.name, hs.name])
    add_graticule(p, m.name, G30, 6)
    return m


def sheet(p, maps, R):
    lyt = page(p, L26)
    els, dark, grey = [], (40, 40, 40), (70, 70, 70)
    S = R["sets"]
    V = json.load(open(os.path.join(HERE, "logs", "v3_maps.json"), encoding="utf-8"))["v2_polygons"]["full"]
    for k, _, letter, lab in SETS:
        y = FY[k]
        mf = lyt.createMapFrame(poly_geom(0.45, y, FW, FH), maps[k], "frame_" + k)
        mf.camera.setExtent(extent_polygon().projectAs(maps[k].spatialReference).extent)
        els.append(text(0.45, y + FH + 0.06, "%s  %s: {:,} polygons, %.2f %% of ±60°, in %d blocks".format(S[k]["polygons"])
                        % (letter, lab, 100 * S[k]["share_pm60"], S[k]["blocks"]), 9, "label_" + letter.lower(), bold=True))
    rows = [["class", "four", "second", "third"]]
    for n in SEVEN:
        rows.append([n] + ["{:,}".format(S[k]["by_class"][n]) if S[k]["by_class"][n] else "–" for k, _, _, _ in SETS])
    rows.append(["area, km²"] + ["{:,}".format(S[k]["area_km2"]) for k, _, _, _ in SETS])
    yk = 7.00
    els.append(text(6.60, yk, "Classes", 9.5, "key_title", bold=True, colour=dark))
    for i, n in enumerate(SEVEN):
        els.append(rect(6.60, yk - 0.27 - 0.205 * i, 0.30, 0.14, "key_sw%d" % i, fill=COLOURS[n]))
        els.append(text(7.00, yk - 0.26 - 0.205 * i, n, 7.8, "key_lab%d" % i, colour=dark))
    els += [
        text(0.45, 7.80, "Mars ±60°: the three label sets, and how the training ground grew", 18, "title", bold=True),
        text(0.45, 7.47, "Every polygon of each set, training and held out, filled in its class colour over the "
             "hillshade; area on the sphere, blocks by each polygon's centroid.", 10, "subtitle", colour=grey),
        text(6.60, 4.95, "Polygons by class", 9.5, "table_title", bold=True, colour=dark),
        text(6.60, 1.30, ("The third set holds %.0f times the second's polygons and %.1f times its\narea, spread over "
                          "%d blocks against %d: more polygons of every class, in\nsmaller pieces. Its lead U-Net scores "
                          "%.1f %% on the second set's held-out\npolygons, the second set's own U-Net %.1f %% (KB §69.81).")
             % (S["third"]["polygons"] / S["second"]["polygons"], S["third"]["area_km2"] / S["second"]["area_km2"],
                S["third"]["blocks"], S["second"]["blocks"], 100 * V["unet_v3"]["accuracy"],
                100 * V["unet_v2"]["accuracy"]), 7.8, "notes", colour=dark),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
    els += table(6.60, 4.88, rows, [1.25, 0.62, 0.68, 0.80], size=7.3)
    add_text(lyt, els)
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L26 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    print("1. measure")
    R = measure()
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("2. maps")
    maps = {k: build_map(p, k, fc) for k, fc, _, _ in SETS}
    print("3. layout", L26)
    sheet(p, maps, R)
    p.save()
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
