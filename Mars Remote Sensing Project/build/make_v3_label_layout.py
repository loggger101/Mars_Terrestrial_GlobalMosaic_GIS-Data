# -*- coding: utf-8 -*-
r"""The v3 labels on a sheet (layout 20; KB §69.49, §69.50): what the desktop's v3 runs will train and score on.

  map    "Labels v3 — sheet"   its own map, so propose_v3_labels.py's map "Labels v3" (rebuilt by that script) is left
         alone: Landform_TrainingSamples_v3_60_train and _test in the class colours (labelsets.COLOURS), the held-out
         polygons outlined in black, over the hillshade and the 30° graticule
  layout 20_labels_v3
         A ±60°; B Tharsis (135–75°W, 10°S–10°N), where edifice and apron sit; per class the polygons and their area
         on the sphere, v3 beside v2, every count read from the gdb at run time

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy. Run polish_layouts.py afterwards.
"""
import os, sys, time, shutil
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
SETS = {"v3": ("Landform_TrainingSamples_v3_60_train", "Landform_TrainingSamples_v3_60_test"),
        "v2": ("Landform_TrainingSamples_v2_60_train", "Landform_TrainingSamples_v2_60_test")}
MAPN = "Labels v3 — sheet"
L20 = "20_labels_v3"
ZOOM = (-135.0, -10.0, -75.0, 10.0)

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def tally():
    """Per set, half and class: polygons and km² on the sphere."""
    out = {}
    for s, fcs in SETS.items():
        for half, fc in zip(("train", "test"), fcs):
            d = {n: [0, 0.0] for n in SEVEN}
            with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue"]) as cur:
                for g, v in cur:
                    d[SEVEN[int(v) - 1]][0] += 1
                    d[SEVEN[int(v) - 1]][1] += g.getArea("GEODESIC", "SQUAREKILOMETERS")
            out[(s, half)] = d
    return out


def by_class(layer, held):
    sym = layer.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = ["Classname"]
    for grp in sym.renderer.groups:
        for it in grp.items:
            col = COLOURS.get(it.values[0][0])
            if col:
                it.symbol.color = {"RGB": list(col) + [100]}
                it.symbol.outlineColor = {"RGB": [0, 0, 0, 100] if held else list(col) + [100]}
                it.symbol.outlineWidth = 0.25 if held else 0.2      # thicker merges the small pieces into black at ±60°
    layer.symbology = sym


def build_map(p):
    m = get_map(p, MAPN)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    te = add(m, os.path.join(GDB, SETS["v3"][1]), "v3 held out (black outline)")
    by_class(te, True)
    tr = add(m, os.path.join(GDB, SETS["v3"][0]), "v3 training")
    by_class(tr, False)
    hs = hillshade(m)
    order(m, [ext.name, te.name, tr.name, hs.name])
    add_graticule(p, MAPN, G30, 7)
    return m


def legend(x, y):
    dark = (40, 40, 40)
    els = [text(x, y, "Classes", 9.5, "key_title", bold=True, colour=dark)]
    yy = y - 0.27
    for i, n in enumerate(SEVEN):
        els.append(rect(x, yy, 0.30, 0.17, "key_sw%d" % i, fill=COLOURS[n], stroke=(150, 150, 150), stroke_w=0.4))
        els.append(text(x + 0.40, yy + 0.02, "%d %s" % (i + 1, n), 8.2, "key_lab%d" % i, colour=dark))
        yy -= 0.215
    els.append(rect(x, yy, 0.30, 0.17, "key_held", fill=(255, 255, 255), stroke=(0, 0, 0), stroke_w=1.0))
    els.append(text(x + 0.40, yy + 0.02, "black outline: held out", 8.2, "key_held_lab", colour=dark))
    return els


def sheet(p, m, T):
    lyt = page(p, L20)
    fw, fh = 6.90, 2.30
    mfa = lyt.createMapFrame(poly_geom(0.45, 4.70, fw, fh), m, "frame_a")
    mfa.camera.setExtent(extent_polygon().projectAs(m.spatialReference).extent)
    mfb = lyt.createMapFrame(poly_geom(0.45, 1.72, fw, fh), m, "frame_b")
    zoom = arcpy.Polygon(arcpy.Array([arcpy.Point(ZOOM[0], ZOOM[1]), arcpy.Point(ZOOM[2], ZOOM[1]),
                                      arcpy.Point(ZOOM[2], ZOOM[3]), arcpy.Point(ZOOM[0], ZOOM[3])]),
                         arcpy.SpatialReference(104905))
    mfb.camera.setExtent(zoom.projectAs(m.spatialReference).extent)
    n = lambda s, h: sum(v[0] for v in T[(s, h)].values())
    rows = [["class", "v3 train", "v3 held", "v2 train", "v2 held"]]
    for c in SEVEN:
        rows.append(["%d %s" % (SEVEN.index(c) + 1, c.replace("steep/windy hills", "hills")),
                     "{:,}".format(T[("v3", "train")][c][0]), "{:,}".format(T[("v3", "test")][c][0]),
                     "{:,}".format(T[("v2", "train")][c][0]), "{:,}".format(T[("v2", "test")][c][0])])
    rows.append(["all", "{:,}".format(n("v3", "train")), "{:,}".format(n("v3", "test")),
                 "{:,}".format(n("v2", "train")), "{:,}".format(n("v2", "test"))])
    km = lambda s, h: sum(v[1] for v in T[(s, h)].values())
    dark, grey = (40, 40, 40), (70, 70, 70)
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: the v3 seven-class labels", 18, "title", bold=True),
        text(0.45, 7.47, "%s polygons, the v2 labels cut into screened pieces and new polygons from the reference "
             "maps, in the same 14 held-out 15° blocks (KB §69.49)." % "{:,}".format(n("v3", "train") + n("v3", "test")),
             10, "subtitle", colour=grey),
        text(0.45, 4.70 + fh + 0.06, "A  ±60°: %s training polygons (%s km²), %s held out (%s km²)"
             % ("{:,}".format(n("v3", "train")), "{:,.0f}".format(km("v3", "train")),
                "{:,}".format(n("v3", "test")), "{:,.0f}".format(km("v3", "test"))), 10, "label_a", bold=True),
        text(0.45, 1.72 + fh + 0.06, "B  Tharsis, 135–75°W, 10°S–10°N: the volcanic edifice and apron labels",
             10, "label_b", bold=True),
        text(7.65, 4.50, "Polygons per class", 9.5, "table_title", bold=True, colour=dark),
        text(0.45, 0.80, "Labels by written rule, not drawn by hand (propose_v3_labels.py, KB §69.49); the v2 held-out "
             "polygons stay the like-for-like score for any v3 map.\nThe v3 runs (U-Net, then SVM) wait for the "
             "desktop: run_v3.ps1 (NEXT-STEPS item 3b).", 7.9, "notes", colour=dark),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + legend(7.65, 6.95)
        + table(7.65, 4.42, rows, [0.98, 0.50, 0.46, 0.46, 0.46], size=7.6))
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L20 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    print("1. tally")
    T = tally()
    for k, d in T.items():
        print("   %s %-5s %s" % (k[0], k[1], {c: v[0] for c, v in d.items()}))
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("2. map:", MAPN)
    m = build_map(p)
    print("3. layout", L20)
    sheet(p, m, T)
    p.save()
    print("   %s: %s" % (MAPN, [l.name for l in m.listLayers()]))
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
