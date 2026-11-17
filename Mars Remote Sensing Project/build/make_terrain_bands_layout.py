# -*- coding: utf-8 -*-
r"""Layout 23: the two terrain bands, and the map they make alone (KB §56.1, §69.149, §69.150).

Layout 22 found that slope and relief alone give 71 % of the four-class map the class the full seven-band stack gives
it. No sheet showed those two bands or the terrain-only map. This one does:
  A  slope, band 6 of Global60\global60_svm_stack_200m.tif (the stack the SVM reads; stretched 1-255 between the p1 and
     p99 of ±60°, the limits read from its STRETCH metadata)
  B  local relief over 9 x 9 pixels (1.8 km), band 7 of the same stack
  C  the all-band SVM at 400 m, Global60\global60_landforms_svm_400m.tif
  D  slope and relief alone, Global60\global60_landforms_svm_terrain_400m.tif
with a table read from logs\bandset_change.json and the two maps' check logs (held-out accuracy, Crater polygons won,
IAU craters with more Crater inside than in the ring).

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy. Run polish_layouts.py afterwards.
"""
import os, sys, time, shutil, json, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from layoutkit import text, rect, poly_geom
from make_global60_maps import (outline, add, get_map, order, page, add_text, extent_polygon, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table

gdal.UseExceptions()
APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
ALL400 = os.path.join(G.OUTDIR, "global60_landforms_svm_400m.tif")
TERR400 = os.path.join(G.OUTDIR, "global60_landforms_svm_terrain_400m.tif")
LOG = os.path.join(HERE, "logs", "bandset_change.json")
CHECK = os.path.join(HERE, "logs", "global60_classification_check_%s400m.json")
L23 = "23_terrain_bands"
FW, FH = 4.85, 1.617                      # 3:1, the ±60° extent
POS = {"a": (0.45, 5.20), "b": (5.60, 5.20), "c": (0.45, 2.95), "d": (5.60, 2.95)}

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def stretch_limits():
    md = gdal.Open(STACK).GetMetadata()["STRETCH"]
    return {m.group(1): (float(m.group(2)), float(m.group(3)))
            for m in re.finditer(r"(\w+) p1=([\d.]+) p99=([\d.]+)", md)}


def classes():
    ds = gdal.Open(ALL400)                                # kept: the band dies with its dataset
    rat = ds.GetRasterBand(1).GetDefaultRAT()
    cols = {rat.GetNameOfCol(j): j for j in range(rat.GetColumnCount())}
    out = []
    for i in range(rat.GetRowCount()):
        get = lambda c: rat.GetValueAsString(i, cols[c])
        out.append((get("Class_name"), (int(get("Red")), int(get("Green")), int(get("Blue")))))
    return out


def grey(layer, band):
    """One band of a multiband raster in grey: red, green and blue all read it (arcpy adds no single band by path).
    band is 1-based, as GDAL numbers it; the colorizer's indices are 0-based."""
    cim = layer.getDefinition("V3")
    c = cim.colorizer                                     # a multiband raster draws with a CIMRasterRGBColorizer
    assert type(c).__name__ == "CIMRasterRGBColorizer", type(c).__name__
    c.redBandIndex = c.greenBandIndex = c.blueBandIndex = band - 1
    c.stretchType = "MinimumMaximum"
    layer.setDefinition(cim)


def one_map(p, name, path, lname, band=None):
    m = get_map(p, name)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.0)
    r = add(m, path, lname)
    if band:
        grey(r, band)
    order(m, [ext.name, r.name])
    add_graticule(p, name, G30, 6)
    return m


def sheet(p, maps):
    lyt = page(p, L23)
    els, dark, grey_ = [], (40, 40, 40), (70, 70, 70)
    R = json.load(open(LOG, encoding="utf-8"))["sets"]["terrain"]
    ca, ct = (json.load(open(CHECK % s, encoding="utf-8")) for s in ("", "terrain_"))
    lim = stretch_limits()
    pc = lambda v: "%.1f %%" % (100 * v)
    labels = {"a": "A  Slope, %g–%.1f° stretched (dark flat)" % lim["slope_deg"],
              "b": "B  Local relief over 1.8 km, %g–%g m stretched" % lim["relief_m"],
              "c": "C  All seven bands, 400 m: held-out accuracy %s" % pc(ca["held_out"]["accuracy"]),
              "d": "D  Slope and relief alone: held-out %s; %s of ±60° as in C"
                   % (pc(ct["held_out"]["accuracy"]), pc(1 - R["share_changed"]))}
    for k, (x, y) in POS.items():
        mf = lyt.createMapFrame(poly_geom(x, y, FW, FH), maps[k], "frame_" + k)
        mf.camera.setExtent(extent_polygon().projectAs(maps[k].spatialReference).extent)
        els.append(text(x, y + FH + 0.06, labels[k], 9, "label_" + k, bold=True))
    names = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
    rows = [["", "all bands (C)", "terrain (D)"]]
    for n in names:
        rows.append(["%s, share of ±60°" % n, pc(R["class_area_all"][n]), pc(R["class_area_set"][n])])
    rows += [["held-out accuracy", pc(ca["held_out"]["accuracy"]), pc(ct["held_out"]["accuracy"])],
             ["Crater polygons won", ca["held_out"]["polygons_majority_own_class"]["Crater"],
              ct["held_out"]["polygons_majority_own_class"]["Crater"]],
             ["IAU craters, more Crater inside", "%.1f %%" % ca["iau_craters"]["pct_inside_gt_ring"],
              "%.1f %%" % ct["iau_craters"]["pct_inside_gt_ring"]]]
    yk = 2.35
    els.append(text(0.45, yk + 0.05, "Classes (C, D)", 9, "key_title", bold=True, colour=dark))
    for i, (n, col) in enumerate(classes()):
        els.append(rect(0.45, yk - 0.25 - 0.21 * i, 0.30, 0.14, "key_sw%d" % i, fill=col))
        els.append(text(0.85, yk - 0.24 - 0.21 * i, n, 8, "key_lab%d" % i, colour=dark))
    els += [
        text(0.45, 7.80, "Mars ±60°: the terrain bands, and the map they make alone", 18, "title", bold=True),
        text(0.45, 7.47, "Slope and relief are two of the stack's seven bands; trained on the same polygons, they give "
             "%s of the map the all-band class (layout 22)." % pc(1 - R["share_changed"]), 10, "subtitle", colour=grey_),
        text(5.60, 2.45, "The two maps compared", 9, "table_title", bold=True, colour=dark),
        text(2.40, 1.45, "The held-out polygons score the two alike, but terrain alone\nwins a third as many Crater "
             "polygons and finds the named\ncraters no better than chance (50 %): the stack's colour and\nthermal "
             "bands carry the crater rims (KB §56.1).", 7.8, "notes", colour=dark),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
    els += table(5.60, 2.40, rows, [2.05, 1.30, 1.30], size=7.4)
    add_text(lyt, els)
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L23 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("1. maps")
    maps = {"a": one_map(p, "Mars ±60° — terrain band: slope", STACK, "Slope (stack band 6)", band=6),
            "b": one_map(p, "Mars ±60° — terrain band: relief", STACK, "Local relief (stack band 7)", band=7),
            "c": one_map(p, "Mars ±60° — four classes, all bands, 400 m", ALL400, "All seven bands, 400 m"),
            "d": one_map(p, "Mars ±60° — four classes, terrain alone, 400 m", TERR400, "Slope and relief alone, 400 m")}
    print("2. layout", L23)
    sheet(p, maps)
    p.save()
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
