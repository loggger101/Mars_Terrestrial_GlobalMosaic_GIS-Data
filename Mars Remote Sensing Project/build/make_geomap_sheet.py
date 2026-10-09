# -*- coding: utf-8 -*-
r"""Layout 13: the ±60° landform classes against the USGS geologic map, as a sheet (test T8, KB §43.2).

T8 was measured by make_geomap_check.py (logs\geomap_check.json) and had no sheet (NEXT-STEPS §7
row 13). This puts it in the project:

  map "Mars ±60° — geologic check"   the published 5 x 5 classification over hillshade, the SIM 3292
                                     unit contacts, the volcanic groups (v, ve, vf) outlined, graticule
  layout 13_geomap_check             the map, and the cross-tabulation as a table of native layout
                                     elements (editable in Pro): per unit group, its share of the ±60°
                                     area and, per class, enrichment P(class | group) / P(class) with
                                     the class's share of the group in brackets

Every number on the sheet is read from logs\geomap_check.json; nothing is typed in. Not an accuracy:
the classes are landforms, the units geologic (§43.2).

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must sit
BESIDE the real .aprx (it stores relative paths, §31.5). Run polish_layouts.py afterwards (§33).
"""
import os, sys, time, json, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from layoutkit import text, rect, cell_text
from make_global60_maps import (outline, add, get_map, page, add_text, legend_classes, order, frame,
                                extent_polygon, CREDIT, BKDIR, OUTD, CLEAN_PATH, CLEAN, CLASS_COLOURS)
from make_reference_maps import add_graticule, G30

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
LOG = os.path.join(HERE, "logs", "geomap_check.json")
MAPNAME, LNAME = "Mars ±60° — geologic check", "13_geomap_check"
CLASSES = list(CLASS_COLOURS)                     # Crater, steep/windy hills, lava tube, Normal Ground
HEAD = {"Crater": "Crater", "steep/windy hills": "steep/windy\nhills", "lava tube": "lava tube",
        "Normal Ground": "Normal\nGround"}
# SIM 3292 unit groups (the type code without its age, §41), in geological order
GROUPS = [("v", "Volcanic"), ("ve", "Volcanic edifice"), ("vf", "Volcanic field"),
          ("h", "Highland"), ("hm", "Highland massif"), ("hu", "Highland undivided"),
          ("i", "Impact"), ("a", "Apron"), ("t", "Transition"), ("tu", "Transition undivided"),
          ("l", "Lowland"), ("p", "Polar")]
# Enrichment bins, diverging blue - grey - red (the dataviz reference pair: #2a78d6, #f0efec, #e34948)
BLUE, GREY, RED = (42, 120, 214), (240, 239, 236), (227, 73, 72)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


BINS = [(0.0, 0.5, BLUE, (255, 255, 255), "under ×0.5"),
        (0.5, 0.8, mix(GREY, BLUE, 0.45), (30, 30, 30), "×0.5–0.8"),
        (0.8, 1.25, GREY, (30, 30, 30), "×0.8–1.25"),
        (1.25, 2.0, mix(GREY, RED, 0.45), (30, 30, 30), "×1.25–2"),
        (2.0, 1e9, RED, (30, 30, 30), "over ×2")]

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def pct(x):
    return "%.0f%%" % (100 * x) if x >= 0.005 else "< 1%"


def bin_of(e):
    return next(b for b in BINS if b[0] <= e < b[1])


def build_map(p):
    m = get_map(p, MAPNAME)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    units = os.path.join(GDB, "Ref_SIM3292_GeologicUnits")
    v = add(m, units, "Volcanic unit groups v, ve, vf (SIM 3292)")
    v.definitionQuery = "UnitGroup IN ('v', 've', 'vf')"
    outline(v, (230, 76, 0), 1.1)
    u = add(m, units, "Geologic unit contacts, USGS SIM 3292")
    outline(u, (25, 25, 25), 0.35)
    cls = add(m, CLEAN_PATH, "Landforms — SVM, %d × %d majority (±60°)" % (CLEAN, CLEAN),
              transparency=30)
    hs = add(m, os.path.join(G.OUTDIR, "global60_hillshade.tif"), "Hillshade")
    order(m, [ext.name, v.name, u.name, cls.name, hs.name])
    m.clipLayers(extent_polygon())
    return m, [cls.name, u.name, v.name, ext.name]


def table(res, x0, ytop):
    """The cross-tabulation as layout elements; returns them and the y of its bottom edge."""
    wl, wa, wc, hh, hr, fs = 1.62, 0.62, 0.84, 0.34, 0.19, 7.2
    els, y = [], ytop - hh
    xs = [x0, x0 + wl, x0 + wl + wa] + [x0 + wl + wa + wc * (i + 1) for i in range(len(CLASSES))]
    els.append(cell_text(xs[0], y, wl, hh, "SIM 3292 unit group", fs, "t8_h0", bold=True, align="Left"))
    els.append(cell_text(xs[1], y, wa, hh, "area of\n±60°", fs, "t8_h1", bold=True))
    for i, c in enumerate(CLASSES):
        els.append(cell_text(xs[2 + i], y, wc, hh, HEAD[c], fs, "t8_hc%d" % i, bold=True))
    total = 0.0
    for k, (code, label) in enumerate(GROUPS):
        g = res["groups"][code]
        total += g["area_share"]
        y -= hr
        els.append(cell_text(xs[0], y, wl, hr, "%s  (%s)" % (label, code), fs, "t8_l%d" % k, align="Left"))
        els.append(cell_text(xs[1], y, wa, hr, "%.1f%%" % (100 * g["area_share"]) if g["area_share"] >= 0.0005 else "< 0.1%", fs, "t8_a%d" % k,
                             colour=(70, 70, 70), align="Right"))
        for i, c in enumerate(CLASSES):
            e = g["classes"][c]["enrichment"]; sh = g["classes"][c]["share_in_group"]
            lo, hi, fill, ink, _ = bin_of(e)
            els.append(rect(xs[2 + i] + 0.015, y + 0.012, wc - 0.03, hr - 0.024, "t8_r%d_%d" % (k, i), fill))
            els.append(cell_text(xs[2 + i], y, wc, hr, "×%.2f  (%s)" % (e, pct(sh)), fs,
                                 "t8_c%d_%d" % (k, i), colour=ink))
    y -= hr + 0.04
    els.append(cell_text(xs[0], y, wl, hr, "All ±60°: class share", fs, "t8_lall", bold=True, align="Left"))
    els.append(cell_text(xs[1], y, wa, hr, "%.1f%%" % (100 * total), fs, "t8_aall", colour=(70, 70, 70), align="Right"))
    for i, c in enumerate(CLASSES):
        els.append(cell_text(xs[2 + i], y, wc, hr, "%.0f%%" % (100 * res["p_class"][c]), fs, "t8_call%d" % i, bold=True))
    els.append(rect(x0, ytop - hh - 0.01, xs[-1] - x0, 0.012, "t8_rule", (120, 120, 120)))
    return els, y, total


def key(x, ytop):
    els = [text(x, ytop - 0.16, "Enrichment: P(class | group) ÷ P(class); ×1 = no association", 7.6,
                "key_head", bold=True)]
    w = 0.78
    for i, (_, _, fill, ink, lab) in enumerate(BINS):
        xx = x + i * (w + 0.04)
        els.append(rect(xx, ytop - 0.48, w, 0.2, "key_r%d" % i, fill))
        els.append(cell_text(xx, ytop - 0.48, w, 0.2, lab, 6.8, "key_t%d" % i, colour=ink))
    return els


def notes(res):
    E = lambda g, c: res["groups"][g]["classes"][c]["enrichment"]
    S = lambda g, c: res["groups"][g]["classes"][c]["share_in_group"]
    return ("• “lava tube” is not enriched on the volcanic plains (×%.2f); it gathers\n"
            "   on volcanic edifices (×%.2f) and aprons (×%.2f): steep volcano flanks.\n"
            "• The other classes sit where the map says they should: Crater on\n"
            "   highland (×%.2f) and impact units (×%.2f); Normal Ground on lowland\n"
            "   (×%.2f) and volcanic plains (×%.2f); steep/windy hills on highland\n"
            "   undivided (×%.2f) and aprons (×%.2f).\n"
            "• %.0f%% of the volcanic plains come out Normal Ground: a coherent terrain\n"
            "   map, not a lava-flow map. Lava flows come from the geologic map\n"
            "   (layout 10, KB §43.3)."
            % (E("v", "lava tube"), E("ve", "lava tube"), E("a", "lava tube"), E("h", "Crater"), E("i", "Crater"),
               E("l", "Normal Ground"), E("v", "Normal Ground"), E("hu", "steep/windy hills"),
               E("a", "steep/windy hills"), 100 * S("v", "Normal Ground")))


def main():
    res = json.load(open(LOG))
    missing = [g for g, _ in GROUPS if g not in res["groups"]]
    assert not missing, "groups missing from %s: %s" % (LOG, missing)
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("1. map:", MAPNAME)
    m, legend_names = build_map(p)
    add_graticule(p, MAPNAME, G30, 7)
    print("2. layout", LNAME)
    lyt = page(p, LNAME)
    fw = 9.3; fh = fw / 3.0
    mf = frame(lyt, m, (0.45, 3.86, fw, fh), "frame")
    tab, ybot, total = table(res, 0.45, 3.66)
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60° — the landform classes against the USGS geologic map", 21, "title", bold=True),
        text(0.45, 7.17, "Test T8. The published four-class map (%d × %d majority, read at %.1f km, area-weighted) "
             "against the unit groups of SIM 3292\n(Tanaka et al. 2014, 1:20 M). Not an accuracy: the classes are "
             "landforms, the units geologic. Each cell: enrichment, and the class's share of the group."
             % (CLEAN, CLEAN, res["cell_m"] / 1000.0), 9.6, "subtitle", colour=(70, 70, 70)),
        text(6.55, 0.62, notes(res), 7.6, "notes", colour=(40, 40, 40)),
        text(0.45, 0.30, CREDIT + "  ·  groups under 2%% of the area omitted unless relevant (%.1f%% shown)"
             % (100 * total), 7.5, "credit", colour=(90, 90, 90))] + tab + key(6.55, 2.50))
    legend_classes(p, lyt, mf, 6.55, 3.66, 4.0, 1.0, legend_names, names=False, cols=2)
    out = os.path.join(OUTD, LNAME + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)
    p.save()
    print("saved. layouts:", sorted(x.name for x in p.listLayouts()))


if __name__ == "__main__":
    main()
