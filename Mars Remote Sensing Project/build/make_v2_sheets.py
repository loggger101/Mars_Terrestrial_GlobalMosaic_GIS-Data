# -*- coding: utf-8 -*-
r"""The seven-class maps into the project, as three sheets beside the four-class ones (NEXT-STEPS §11.5 step 4;
the author's decision D28, 2026-10-29: the seven-class maps lead, the four-class sheets stay as history).

  map "Mars ±60° — seven classes (v2)"      the seven-class SVM map (11 x 11) over hillshade, the reviewed v2
                                             labels split held out / training, graticule
  map "Mars ±60° — geologic check, seven classes"
                                             the same map with the SIM 3292 unit contacts and volcanic groups
  map "U-Net — seven classes (±60°)"         the seven-class U-Net (two passes) over hillshade, the held-out v2
                                             labels on a white halo; the four-class U-Net and the seven-class SVM
                                             present but off
  layout 04b_global60_landforms_v2           beside 04: the SVM map and its held-out scores per class
  layout 13b_geomap_check_v2                 beside 13: test T8 on the seven-class map (logs\geomap_check_v2.json)
  layout 17b_unet_v2_provinces               beside 17: the U-Net map over ±60° and a held-out block, against
                                             the seven-class SVM and the four-class U-Net on the same polygons

Every figure is read from the logs at run time (KB §69.24, §69.25); nothing is typed in. The four-class maps,
layouts and their builders are not touched.

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy beside the real .aprx
(§31.5). Run polish_layouts.py afterwards (§33).
"""
import os, sys, time, shutil, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from layoutkit import text, rect, cell_text, poly_geom
from labelsets import SEVEN, COLOURS
from make_global60_maps import (outline, add, get_map, order, page, add_text, legend_classes, frame,
                                extent_polygon, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table
import make_geomap_sheet as T8

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
G60 = G.OUTDIR
LOGS = os.path.join(HERE, "logs")
SVM = os.path.join(G60, "global60_landforms_svm_v2_200m_mode11.tif")
UNET = os.path.join(G60, "global60_landforms_unet_v2_200m_seamfix.tif")
UNET4 = os.path.join(G60, "global60_landforms_unet_200m_seamfix.tif")
TEST = os.path.join(GDB, "Landform_TrainingSamples_v2_60_test")
TRAIN = os.path.join(GDB, "Landform_TrainingSamples_v2_60_train")
CHECK_S = os.path.join(LOGS, "global60_classification_check_v2_200m_mode11.json")
CHECK_S4 = os.path.join(LOGS, "global60_classification_check_200m_mode11_on_v2_labels.json")
CHECK_U = os.path.join(LOGS, "global60_classification_check_global60_landforms_unet_v2_200m_seamfix.json")
CHECK_U4 = os.path.join(LOGS, "global60_classification_check_global60_landforms_unet_200m_seamfix_on_v2_labels.json")
METRICS_S = os.path.join(LOGS, "score_metrics_v2_svm.json")
METRICS_U = os.path.join(LOGS, "score_metrics_v2_unet.json")
VERDICT_S = os.path.join(LOGS, "d18_verdict.json")
VERDICT_U = os.path.join(LOGS, "d18_verdict_unet_v2.json")
GEOMAP = os.path.join(LOGS, "geomap_check_v2.json")
MOSAIC = os.path.join(LOGS, "dl_unet_v2_global_mosaic_seamfix.json")
MAP_S, MAP_T8, MAP_U = ("Mars ±60° — seven classes (v2)", "Mars ±60° — geologic check, seven classes",
                        "U-Net — seven classes (±60°)")
L04, L13, L17 = "04b_global60_landforms_v2", "13b_geomap_check_v2", "17b_unet_v2_provinces"
SHORT = {"Crater": "Crater", "steep/windy hills": "hills", "lava tube": "lava tube", "Normal Ground": "Normal Ground",
         "volcanic edifice": "edifice", "apron": "apron", "fluvial channel": "fluvial"}
DARK, GREY = (40, 40, 40), (70, 70, 70)

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def load(path):
    return json.load(open(path, encoding="utf-8"))


def metrics(path, check):
    """The score_metrics.py entry for one check log."""
    return load(path)["maps"][os.path.basename(check)]


def by_class7(layer, width, field="Classname"):
    """Hollow polygons outlined in the seven class colours."""
    sym = layer.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = [field]
    for grp in sym.renderer.groups:
        for it in grp.items:
            col = list(COLOURS.get(it.values[0][0], (255, 255, 255)))
            it.symbol.color = {"RGB": [0, 0, 0, 0]}
            it.symbol.outlineColor = {"RGB": col + [100]}
            it.symbol.outlineWidth = width
    layer.symbology = sym


def won(h):
    """Held-out polygons whose majority is their own class, summed over the classes."""
    a = [tuple(int(x) for x in h["polygons_majority_own_class"][k].split("/")) for k in SEVEN]
    return sum(x for x, _ in a), sum(y for _, y in a)


def pc(v, nd=0):
    return ("%." + str(nd) + "f %%") % (100 * v)


def pcs(v):
    """A share for the per-class table: one decimal under 1 %, so 0.4 % does not print as 0 %."""
    return pc(v, 1) if v < 0.01 else pc(v)


# ------------------------------------------------------------------ 04b
def sheet_svm(p):
    s, s4, ms = load(CHECK_S), load(CHECK_S4), metrics(METRICS_S, CHECK_S)
    vd = load(VERDICT_S)
    h, tr, h4 = s["held_out"], s["training_set"], s4["held_out"]
    m = get_map(p, MAP_S)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    tst = add(m, TEST, "Held-out labels")
    by_class7(tst, 1.6)
    trn = add(m, TRAIN, "Reviewed labels — used to train", visible=False)
    by_class7(trn, 0.7)
    cls = add(m, SVM, "SVM, seven classes", transparency=30)
    hs = add(m, os.path.join(G60, "global60_hillshade.tif"), "Hillshade (±60°, 200 m)")
    order(m, [ext.name, tst.name, trn.name, cls.name, hs.name])
    m.clipLayers(extent_polygon())
    add_graticule(p, MAP_S, G30, 7)

    lyt = page(p, L04)
    fw = 10.1; fh = fw / 3.0
    mf = frame(lyt, m, (0.45, 3.55, fw, fh), "frame")
    sh, per = s["share_area_weighted"], ms["per_class"]
    rows = [["class", "producer's", "user's", "share of map", "share of held-out labels"]]
    for k in SEVEN:
        rows.append([k, pcs(h["producers"][k]), pcs(h["users"][k]), pcs(sh[k]), pcs(per[k]["label_share"])])
    a = vd["a_accuracy_and_kappa"]
    nw, nt = won(h)
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: landform classification, seven classes", 21, "title", bold=True),
        text(0.45, 7.22, "Support vector machine on the reviewed labels (%d training polygons), over the same 7-band "
             "stack as layout 04; smoothed by majority filter, 11 × 11 (2.2 km).\nCrater narrowed to impact craters; "
             "three new classes: volcanic edifice, apron, fluvial channel. The four-class map is layout 04."
             % tr["polygons"], 10, "subtitle", colour=GREY),
        text(0.45, 3.24, "Scored on %d held-out polygons: whole 15° blocks the classifier never saw" % h["polygons"],
             10.5, "acc_head", bold=True),
        text(0.45, 1.00, "Overall %s, κ %.2f (one class everywhere %s); balanced accuracy %.2f; %d of %d polygons "
             "won.\nThe four-class map on the same polygons: %s, κ %.2f. On its own training polygons: %s, κ %.2f.\n"
             "Fluvial channel covers %s of the map against %s of the held-out labels: it is over-predicted."
             % (pc(h["accuracy"]), h["kappa"], pc(h["one_class_everywhere"]), ms["balanced_accuracy"], nw, nt,
                pc(h4["accuracy"]), h4["kappa"], pc(tr["accuracy"]), tr["kappa"],
                pc(sh["fluvial channel"]), pc(per["fluvial channel"]["label_share"])),
             8.8, "acc_body", colour=DARK),
        # the short line first: the long one, at the bottom, runs under the D28 note
        text(0.45, 0.62, "Grey streaks: no data in the stack (THEMIS gaps), the hillshade showing through.\n"
             "Checks (KB §31): elevation bins alone reproduce %s of it, one class alone %s. Tile-seam "
             "ratio %.2f. 'Crater' inside IAU craters %s, in a ring around them %s (n = %d)."
             % (pc(s["elevation_only_reproduces"]), pc(s["largest_class_alone"]), s["seam_ratio"]["tile_4096_at_100m"],
                pc(s["iau_craters"]["crater_inside"]), pc(s["iau_craters"]["crater_ring"]), s["iau_craters"]["n"]),
             8.2, "checks", colour=GREY),
        text(7.10, 0.86, "D18's rule (KB §68.4) would keep the four-class\nmap: on classes 1–4 this map scores %s\n"
             "against %s. The author leads with the seven\nclasses as the more detailed map (D28, KB §69.26)."
             % (pc(a["accuracy"][0]), pc(a["accuracy"][1])), 8.2, "d28", colour=DARK),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + table(0.45, 3.16, rows, [1.55, 0.95, 0.95, 1.10, 1.60], size=7.8))
    legend_classes(p, lyt, mf, 7.10, 3.30, 3.40, 1.80, [cls.name, tst.name], cols=2)
    out = os.path.join(OUTD, L04 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


# ------------------------------------------------------------------ 13b
HEAD7 = {"Crater": "Crater", "steep/windy hills": "steep/windy\nhills", "lava tube": "lava tube",
         "Normal Ground": "Normal\nGround", "volcanic edifice": "volcanic\nedifice", "apron": "apron",
         "fluvial channel": "fluvial\nchannel"}


def t8_table(res, x0, ytop):
    """make_geomap_sheet.table with seven class columns, narrower."""
    wl, wa, wc, hh, hr, fs = 1.45, 0.55, 0.70, 0.34, 0.19, 6.8
    els, y = [], ytop - hh
    xs = [x0, x0 + wl, x0 + wl + wa] + [x0 + wl + wa + wc * (i + 1) for i in range(len(SEVEN))]
    els.append(cell_text(xs[0], y, wl, hh, "SIM 3292 unit group", fs, "t8_h0", bold=True, align="Left"))
    els.append(cell_text(xs[1], y, wa, hh, "area of\n±60°", fs, "t8_h1", bold=True))
    for i, c in enumerate(SEVEN):
        els.append(cell_text(xs[2 + i], y, wc, hh, HEAD7[c], fs, "t8_hc%d" % i, bold=True))
    total = 0.0
    for k, (code, label) in enumerate(T8.GROUPS):
        g = res["groups"][code]
        total += g["area_share"]
        y -= hr
        els.append(cell_text(xs[0], y, wl, hr, "%s  (%s)" % (label, code), fs, "t8_l%d" % k, align="Left"))
        els.append(cell_text(xs[1], y, wa, hr, "%.1f%%" % (100 * g["area_share"]) if g["area_share"] >= 0.0005
                             else "< 0.1%", fs, "t8_a%d" % k, colour=GREY, align="Right"))
        for i, c in enumerate(SEVEN):
            e = g["classes"][c]["enrichment"]; s = g["classes"][c]["share_in_group"]
            lo, hi, fill, ink, _ = T8.bin_of(e)
            els.append(rect(xs[2 + i] + 0.015, y + 0.012, wc - 0.03, hr - 0.024, "t8_r%d_%d" % (k, i), fill))
            els.append(cell_text(xs[2 + i], y, wc, hr, "×%.2f (%s)" % (e, T8.pct(s)), fs, "t8_c%d_%d" % (k, i),
                                 colour=ink))
    y -= hr + 0.04
    els.append(cell_text(xs[0], y, wl, hr, "All ±60°: class share", fs, "t8_lall", bold=True, align="Left"))
    els.append(cell_text(xs[1], y, wa, hr, "%.1f%%" % (100 * total), fs, "t8_aall", colour=GREY, align="Right"))
    for i, c in enumerate(SEVEN):
        els.append(cell_text(xs[2 + i], y, wc, hr, "%.0f%%" % (100 * res["p_class"][c]), fs, "t8_call%d" % i,
                             bold=True))
    els.append(rect(x0, ytop - hh - 0.01, xs[-1] - x0, 0.012, "t8_rule", (120, 120, 120)))
    return els, y, total


def t8_key(x, ytop):
    els = [text(x, ytop - 0.16, "Enrichment: P(class | group) ÷ P(class);\n×1 = no association", 7.4, "key_head",
                bold=True)]
    w = 0.56                                    # five swatches end on the 10.55 in margin (KB §64)
    for i, (_, _, fill, ink, lab) in enumerate(T8.BINS):
        xx = x + i * (w + 0.04)
        els.append(rect(xx, ytop - 0.58, w, 0.2, "key_r%d" % i, fill))
        els.append(cell_text(xx, ytop - 0.58, w, 0.2, lab, 6.0, "key_t%d" % i, colour=ink))
    return els


def t8_notes(res):
    E = lambda g, c: res["groups"][g]["classes"][c]["enrichment"]
    S = lambda g, c: res["groups"][g]["classes"][c]["share_in_group"]
    return ("• The new classes find their units: volcanic\n"
            "   edifice on edifice units (×%.2f), apron on\n"
            "   apron units (×%.2f).\n"
            "• Fluvial channel covers %.0f%% of ±60°, %.0f%% of the\n"
            "   highland (h): over-predicted, not a valley map.\n"
            "• Crater on impact (×%.2f) and highland (×%.2f)\n"
            "   units; Normal Ground on lowland (×%.2f) and\n"
            "   volcanic plains (×%.2f)."
            % (E("ve", "volcanic edifice"), E("a", "apron"), 100 * res["p_class"]["fluvial channel"],
               100 * S("h", "fluvial channel"), E("i", "Crater"), E("h", "Crater"), E("l", "Normal Ground"),
               E("v", "Normal Ground")))


def sheet_t8(p):
    res = load(GEOMAP)
    assert res.get("map") == os.path.basename(SVM), "%s scored %s, the sheet shows %s" % (
        GEOMAP, res.get("map"), os.path.basename(SVM))
    missing = [g for g, _ in T8.GROUPS if g not in res["groups"]]
    assert not missing, "groups missing from %s: %s" % (GEOMAP, missing)
    m = get_map(p, MAP_T8)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    units = os.path.join(GDB, "Ref_SIM3292_GeologicUnits")
    v = add(m, units, "Volcanic unit groups v, ve, vf (SIM 3292)")
    v.definitionQuery = "UnitGroup IN ('v', 've', 'vf')"
    outline(v, (230, 76, 0), 1.1)
    u = add(m, units, "Geologic unit contacts, USGS SIM 3292")
    outline(u, (25, 25, 25), 0.35)
    cls = add(m, SVM, "Landforms — SVM, seven classes, 11 × 11 majority (±60°)", transparency=30)
    hs = add(m, os.path.join(G60, "global60_hillshade.tif"), "Hillshade")
    order(m, [ext.name, v.name, u.name, cls.name, hs.name])
    m.clipLayers(extent_polygon())
    add_graticule(p, MAP_T8, G30, 7)

    lyt = page(p, L13)
    fw = 9.3; fh = fw / 3.0
    mf = frame(lyt, m, (0.45, 3.86, fw, fh), "frame")
    tab, ybot, total = t8_table(res, 0.45, 3.66)
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: the seven landform classes against the USGS geologic map", 21, "title",
             bold=True),
        text(0.45, 7.17, "Test T8 on the seven-class SVM map (11 × 11 majority, read at %.1f km, area-weighted) "
             "against the unit groups of SIM 3292\n(Tanaka et al. 2014, 1:20 M). Not an accuracy: the classes are "
             "landforms, the units geologic. Each cell: enrichment, and the class's share of the group."
             % (res["cell_m"] / 1000.0), 9.6, "subtitle", colour=GREY),
        text(7.55, 0.62, t8_notes(res), 7.2, "notes", colour=DARK),
        text(0.45, 0.22, CREDIT + "\nUnit groups under 2%% of the area are omitted unless relevant (%.1f%% of it "
             "shown). The four-class version is layout 13." % (100 * total), 7.5, "credit", colour=(90, 90, 90))]
        + tab + t8_key(7.55, 2.30))
    legend_classes(p, lyt, mf, 7.55, 3.66, 2.85, 1.25, [cls.name, u.name, v.name, ext.name], names=False, cols=2)
    out = os.path.join(OUTD, L13 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


# ------------------------------------------------------------------ 17b
def zoom_block():
    """The held-out 15° block with the most classes (then the most polygons), as on layout 17."""
    blocks = collections.defaultdict(lambda: [set(), []])
    with arcpy.da.SearchCursor(TEST, ["SHAPE@", "Classname"]) as c:
        for g, n in c:
            k = (int(g.centroid.X // 15) * 15, int(g.centroid.Y // 15) * 15)
            blocks[k][0].add(n); blocks[k][1].append(g.extent)
    k, (cls, ex) = max(blocks.items(), key=lambda kv: (len(kv[1][0]), len(kv[1][1])))
    return dict(lon=k[0], lat=k[1], classes=sorted(cls), polygons=len(ex),
                extent_deg=[min(e.XMin for e in ex), min(e.YMin for e in ex),
                            max(e.XMax for e in ex), max(e.YMax for e in ex)])


def sheet_unet(p):
    u, s, u4 = load(CHECK_U), load(CHECK_S), load(CHECK_U4)
    mu, ms, mu4 = metrics(METRICS_U, CHECK_U), metrics(METRICS_S, CHECK_S), metrics(METRICS_U, CHECK_U4)
    vd, mo = load(VERDICT_U), load(MOSAIC)
    hu, hs, h4 = u["held_out"], s["held_out"], u4["held_out"]
    m = get_map(p, MAP_U)
    tln = add(m, TEST, "Held-out labels (never trained on)")
    by_class7(tln, 1.0)
    # a white halo under the class-colour outlines, as on layout 17 (KB §66.9)
    halo = add(m, TEST, "Held-out labels — halo")
    outline(halo, (255, 255, 255), 2.6)
    trn = add(m, TRAIN, "Reviewed labels — used to train", visible=False)
    by_class7(trn, 0.7)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    uln = add(m, UNET, "Landforms — U-Net, seven classes, two passes (±60°, 200 m)", transparency=30)
    svm = add(m, SVM, "SVM, seven classes (layout 04b)", visible=False, transparency=30)
    u4l = add(m, UNET4, "U-Net, four classes (layout 17)", visible=False, transparency=30)
    hsl = add(m, os.path.join(G60, "global60_hillshade.tif"), "Hillshade (±60°, 200 m)")
    order(m, [tln.name, halo.name, trn.name, ext.name, uln.name, svm.name, u4l.name, hsl.name])
    m.clipLayers(extent_polygon())
    add_graticule(p, MAP_U, G30, 7)

    z = zoom_block()
    lyt = page(p, L17)
    fw = 7.35; fh = fw / 3.0
    mfa = lyt.createMapFrame(poly_geom(0.45, 4.62, fw, fh), m, "frame_all")
    mfa.camera.setExtent(extent_polygon().projectAs(m.spatialReference).extent)
    zw, zh = 3.90, 3.05
    mfb = lyt.createMapFrame(poly_geom(0.45, 1.15, zw, zh), m, "frame_block")
    pad = 0.4
    mfb.camera.setExtent(arcpy.Extent(z["extent_deg"][0] - pad, z["extent_deg"][1] - pad,
                                      z["extent_deg"][2] + pad, z["extent_deg"][3] + pad))
    seq = lambda h, key: "/".join("%.0f" % (100 * h[key][k]) for k in SEVEN)
    rows = [["held out (%d polygons)" % hu["polygons"], "U-Net, 7", "SVM, 7", "U-Net, 4"],
            ["accuracy, κ"] + ["%s, %.3f" % (pc(h["accuracy"], 1), h["kappa"]) for h in (hu, hs, h4)],
            ["balanced accuracy, macro F1"] + ["%.2f, %.2f" % (x["balanced_accuracy"], x["macro_f1"])
                                               for x in (mu, ms, mu4)],
            ["polygons won (majority own class)"] + ["%d / %d" % won(h) for h in (hu, hs, h4)],
            ["producer's, the 7 classes in order (%)"] + [seq(h, "producers") for h in (hu, hs, h4)],
            ["user's, the 7 classes in order (%)"] + [seq(h, "users") for h in (hu, hs, h4)],
            ["IAU craters (%d): Crater inside / ring" % u["iau_craters"]["n"]]
            + ["%.0f / %.0f %%" % (100 * x["iau_craters"]["crater_inside"], 100 * x["iau_craters"]["crater_ring"])
               for x in (u, s, u4)],
            ["elevation bins alone reproduce"] + [pc(x["elevation_only_reproduces"]) for x in (u, s, u4)],
            ["seam ratio, 4096 px tiles at 100 m"] + ["%.2f" % x["seam_ratio"]["tile_4096_at_100m"]
                                                      for x in (u, s, u4)]]
    lon = lambda v: "%d°E" % (v % 360)
    lat = lambda v: "%d°%s" % (abs(v), "N" if v > 0 else "S") if v else "0°"
    sh = u["share_area_weighted"]
    b = vd["b_new_classes"]
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: seven landform classes from a U-Net", 19, "title", bold=True),
        text(0.45, 7.47, "A pixel classifier on the 7-band 200 m stack, trained on the reviewed labels' training "
             "split only; two passes on tile grids 128 px apart remove the tile seams.", 10, "subtitle", colour=GREY),
        text(0.45, 4.62 + fh + 0.06, "A  ±60°: edifice %.0f %%, Normal Ground %.0f %%, apron %.0f %%, Crater %.0f %%, "
             "fluvial %.0f %%, lava tube %.1f %%, hills %.1f %%"
             % tuple(100 * sh[k] for k in ("volcanic edifice", "Normal Ground", "apron", "Crater", "fluvial channel",
                                           "lava tube", "steep/windy hills")), 9.5, "label_a", bold=True),
        text(0.45, 1.15 + zh + 0.06, "B  A held-out block with %d classes (%d polygons), %s–%s, %s–%s" % (
            len(z["classes"]), z["polygons"], lon(z["lon"]), lon(z["lon"] + 15), lat(z["lat"]), lat(z["lat"] + 15)),
             10, "label_b", bold=True),
        text(4.60, 4.06, "Three maps under the same scorer, on the reviewed labels (KB §69.24–69.25)", 10,
             "table_title", bold=True),
        text(4.60, 1.80, "The most detailed map of the project (the author's choice, D28). It learns the new classes "
             "(user's: edifice %.0f %%,\napron %.0f %%, fluvial %.0f %%, each above its share of the labels) and "
             "scores %s against the seven-class SVM's %s.\nIts faults: volcanic edifice covers %.0f %% of ±60°, and on "
             "classes 1–4 it scores %s against the four-class U-Net's %s." % (
                 100 * b["volcanic edifice"]["users"], 100 * b["apron"]["users"], 100 * b["fluvial channel"]["users"],
                 pc(hu["accuracy"]), pc(hs["accuracy"]), 100 * sh["volcanic edifice"],
                 pc(vd["a_accuracy_and_kappa"]["accuracy"][0]), pc(vd["a_accuracy_and_kappa"]["accuracy"][1])),
             7.6, "findings", colour=DARK),
        text(0.45, 0.64, "Held-out polygons lie in 14 whole 15° blocks the model never saw; scored at 400 m, "
             "area-weighted, by the script behind every SVM figure. Classes in order: Crater, hills, lava tube, "
             "Normal Ground,\nedifice, apron, fluvial. The second pass, offset 128 px, took %.0f %% of the pixels "
             "and changed %.1f %%. Held-out labels are outlined in their class colours on a white halo. Grey streaks: "
             "no data\nin the stack (THEMIS gaps), the hillshade showing through. The four-class U-Net is layout 17." % (
                 100 * mo["share_from_pass_b"], 100 * mo["share_a_b_disagree"]),
             7.6, "notes", colour=DARK),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + table(4.60, 3.98, rows, [2.30, 1.22, 1.22, 1.21], size=7.2))
    legend_classes(p, lyt, mfa, 7.98, 7.12, 2.42, 2.40, [uln.name], names=True, cols=1)
    items = p.listStyleItems("ArcGIS 2D", "SCALE_BAR")
    add_text(lyt, [text(8.40, 1.58, "Scale of B", 8.2, "sbar_label", bold=True, colour=DARK)])
    sb = lyt.createMapSurroundElement(arcpy.Point(8.40, 1.16), "SCALE_BAR", mfb,
                                      next((i for i in items if i.name == "Double Alternating Scale Bar 1 Metric"),
                                           items[0]), "sbar")
    d = sb.getDefinition("V3")
    d.divisions, d.subdivisions, d.division = 2, 0, 100.0
    d.labelFrequency = "Divisions"
    d.fittingStrategy = "AdjustFrame"
    sb.setDefinition(d)
    out = os.path.join(OUTD, L17 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    os.makedirs(OUTD, exist_ok=True)
    p = arcpy.mp.ArcGISProject(APRX)
    print("1.", L04); sheet_svm(p)
    print("2.", L13); sheet_t8(p)
    print("3.", L17); sheet_unet(p)
    p.save()
    print("saved. maps:", len(p.listMaps()), "layouts:", sorted(x.name for x in p.listLayouts()))


if __name__ == "__main__":
    main()
