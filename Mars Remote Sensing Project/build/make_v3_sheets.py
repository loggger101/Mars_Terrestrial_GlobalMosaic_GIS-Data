# -*- coding: utf-8 -*-
r"""The v3 maps into the project, as three sheets beside the v2 ones (the author's decision D36, 2026-11-07: both v3 maps
lead the final; KB §69.81, §69.82). The v2 and four-class sheets stay as history.

  map "Mars ±60° — seven classes (v3)"           the SVM v3 map (11 x 11) over hillshade, the v3 labels held out / training
  map "Mars ±60° — geologic check, v3"           the same map with the SIM 3292 unit contacts and volcanic groups
  map "U-Net — seven classes, v3 (±60°)"         the U-Net v3 (two passes) over hillshade, the v3 held-out labels on a white
                                                 halo; the v2 U-Net and the SVM v3 present but off
  layout 04c_global60_landforms_v3               beside 04b: the SVM map and its held-out scores per class
  layout 13c_geomap_check_v3                     beside 13b: test T8 on the SVM v3 map (logs\geomap_check_v3.json)
  layout 17c_unet_v3_provinces                   beside 17b: the U-Net map over ±60° and a held-out block, against the SVM
                                                 v3 and the v2 U-Net on the same polygons

The sheet text is written from the v3 results (KB §69.77), the helpers are make_v2_sheets.py's, and every figure is read
from the logs at run time. Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy. Run
polish_layouts.py afterwards (§33).
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_v2_sheets as S
from make_v2_sheets import (by_class7, load, metrics, pc, pcs, t8_key, t8_notes, t8_table, won, zoom_block, text, table, page,
                            add, add_text, get_map, frame, order, outline, extent_polygon, add_graticule, legend_classes,
                            poly_geom, CREDIT, BKDIR, OUTD, GDB, G60, LOGS, G30, GREY, DARK, SEVEN, T8)

APRX = S.APRX
SVM = os.path.join(G60, "global60_landforms_svm_v3_200m_mode11.tif")
UNET = os.path.join(G60, "global60_landforms_unet_v3_200m_seamfix.tif")
UNET2 = os.path.join(G60, "global60_landforms_unet_v2_200m_seamfix.tif")
TEST = os.path.join(GDB, "Landform_TrainingSamples_v3_60_test")
TRAIN = os.path.join(GDB, "Landform_TrainingSamples_v3_60_train")
log = lambda n: os.path.join(LOGS, "global60_classification_check_%s.json" % n)
CHECK_S = log("v3_200m_mode11")
CHECK_S2 = log("v3_200m_mode11_on_v2_labels")
CHECK_V2S = log("v2_200m_mode11_on_v3_labels")
CHECK_U = log("global60_landforms_unet_v3_200m_seamfix")
CHECK_U2 = log("global60_landforms_unet_v3_200m_seamfix_on_v2_labels")
CHECK_V2U = log("global60_landforms_unet_v2_200m_seamfix_on_v3_labels")
METRICS_S = os.path.join(LOGS, "score_metrics_v3_svm.json")
METRICS_U = os.path.join(LOGS, "score_metrics_v3_unet.json")
V3 = os.path.join(LOGS, "v3_maps.json")
R2 = os.path.join(LOGS, "r2", "r2_v3_result.json")
GEOMAP = os.path.join(LOGS, "geomap_check_v3.json")
MOSAIC = os.path.join(LOGS, "dl_unet_v3_global_mosaic_seamfix.json")
MAP_S, MAP_T8, MAP_U = "Mars ±60° — seven classes (v3)", "Mars ±60° — geologic check, v3", "U-Net — seven classes, v3 (±60°)"
L04, L13, L17 = "04c_global60_landforms_v3", "13c_geomap_check_v3", "17c_unet_v3_provinces"
S.TEST = TEST


def sheet_svm(p):
    s, s2, s2v, ms = load(CHECK_S), load(CHECK_S2), load(CHECK_V2S), metrics(METRICS_S, CHECK_S)
    v3, r2 = load(V3), load(R2)
    h, tr = s["held_out"], s["training_set"]
    falls = v3["recommendation"]["svm"]["c_falls"]
    m = get_map(p, MAP_S)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    tst = add(m, TEST, "Held-out labels")
    by_class7(tst, 1.2)
    trn = add(m, TRAIN, "v3 labels — used to train", visible=False)
    by_class7(trn, 0.5)
    cls = add(m, SVM, "SVM, seven classes, v3 labels", transparency=30)
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
    nw, nt = won(h)
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: landform classification, seven classes, v3 labels", 21, "title", bold=True),
        text(0.45, 7.22, "Support vector machine on the third label set (%s training polygons: the reviewed labels cut and "
             "screened, others added by rule), over the\nsame 7-band stack as layout 04; smoothed by majority filter, "
             "11 × 11 (2.2 km). The v2 map is layout 04b, the four-class map layout 04."
             % format(tr["polygons"], ","), 10, "subtitle", colour=GREY),
        text(0.45, 3.24, "Scored on %s held-out polygons: whole 15° blocks the classifier never saw"
             % format(h["polygons"], ","), 10.5, "acc_head", bold=True),
        text(0.45, 1.00, "Overall %s, κ %.2f (one class everywhere %s); balanced accuracy %.2f; %s of %s polygons won.\n"
             "The v2 map on the same polygons: %s, κ %.2f. On the 237 v2 polygons this map: %s, κ %.2f.\n"
             "Fluvial channel covers %s of the map against %s of the held-out labels: it is over-predicted."
             % (pc(h["accuracy"]), h["kappa"], pc(h["one_class_everywhere"]), ms["balanced_accuracy"], format(nw, ","),
                format(nt, ","), pc(s2v["held_out"]["accuracy"]), s2v["held_out"]["kappa"], pc(s2["held_out"]["accuracy"]),
                s2["held_out"]["kappa"], pc(sh["fluvial channel"]), pc(per["fluvial channel"]["label_share"])),
             8.8, "acc_body", colour=DARK),
        text(0.45, 0.62, "Grey streaks: no data in the stack (THEMIS gaps), the hillshade showing through.\n"
             "Checks (KB §31): elevation bins alone reproduce %s of it, one class alone %s. Tile-seam "
             "ratio %.2f. 'Crater' inside IAU craters %s, in a ring around them %s (n = %d)."
             % (pc(s["elevation_only_reproduces"]), pc(s["largest_class_alone"]), s["seam_ratio"]["tile_4096_at_100m"],
                pc(s["iau_craters"]["crater_inside"]), pc(s["iau_craters"]["crater_ring"]), s["iau_craters"]["n"]),
             8.2, "checks", colour=GREY),
        text(7.10, 0.86, "The rule set before the run would keep the v2\nmap: κ falls and Crater loses %.1f points of\n"
             "producer's accuracy. On the probability sample\nit scores %s. The author leads with it (D36, KB §69.82)."
             % (100 * falls["Crater"], pc(r2["overall"]["svm_v3"]["est"], 1)), 8.2, "d36", colour=DARK),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + table(0.45, 3.16, rows, [1.55, 0.95, 0.95, 1.10, 1.60], size=7.8))
    legend_classes(p, lyt, mf, 7.10, 3.30, 3.40, 1.80, [cls.name, tst.name], cols=2)
    out = os.path.join(OUTD, L04 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def sheet_t8(p):
    res = load(GEOMAP)
    assert res.get("map") == os.path.basename(SVM), "%s scored %s, the sheet shows %s" % (GEOMAP, res.get("map"), os.path.basename(SVM))
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
    cls = add(m, SVM, "Landforms — SVM, seven classes, v3 labels, 11 × 11 majority (±60°)", transparency=30)
    hs = add(m, os.path.join(G60, "global60_hillshade.tif"), "Hillshade")
    order(m, [ext.name, v.name, u.name, cls.name, hs.name])
    m.clipLayers(extent_polygon())
    add_graticule(p, MAP_T8, G30, 7)

    lyt = page(p, L13)
    fw = 9.3; fh = fw / 3.0
    mf = frame(lyt, m, (0.45, 3.86, fw, fh), "frame")
    tab, ybot, total = t8_table(res, 0.45, 3.66)
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: the v3 SVM map against the USGS geologic map", 21, "title", bold=True),
        text(0.45, 7.17, "Test T8 on the seven-class SVM map on the v3 labels (11 × 11 majority, read at %.1f km, "
             "area-weighted) against the unit groups of SIM 3292\n(Tanaka et al. 2014, 1:20 M). Not an accuracy: the classes "
             "are landforms, the units geologic. Each cell: enrichment, and the class's share of the group."
             % (res["cell_m"] / 1000.0), 9.6, "subtitle", colour=GREY),
        text(7.55, 0.62, t8_notes(res), 7.2, "notes", colour=DARK),
        text(0.45, 0.22, CREDIT + "\nUnit groups under 2%% of the area are omitted unless relevant (%.1f%% of it "
             "shown). The v2 version is layout 13b." % (100 * total), 7.5, "credit", colour=(90, 90, 90))]
        + tab + t8_key(7.55, 2.30))
    legend_classes(p, lyt, mf, 7.55, 3.66, 2.85, 1.25, [cls.name, u.name, v.name, ext.name], names=False, cols=2)
    out = os.path.join(OUTD, L13 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def sheet_unet(p):
    u, s, u2 = load(CHECK_U), load(CHECK_S), load(CHECK_V2U)
    mu, ms, mu2 = metrics(METRICS_U, CHECK_U), metrics(METRICS_S, CHECK_S), metrics(METRICS_U, CHECK_V2U)
    v3, r2, mo = load(V3), load(R2), load(MOSAIC)
    hu, hs, h2 = u["held_out"], s["held_out"], u2["held_out"]
    hv2 = load(CHECK_U2)["held_out"]
    n = load(os.path.join(LOGS, "named_feature_check_v3.json"))["unet_v3"]["edifice"]
    assert n["pct_inside_gt_outside"] == 0.0, "the sheet says none of the named edifices"
    f2 = v3["v2_polygons"]["full"]
    m = get_map(p, MAP_U)
    tln = add(m, TEST, "Held-out labels (never trained on)")
    by_class7(tln, 0.8)
    halo = add(m, TEST, "Held-out labels — halo")
    outline(halo, (255, 255, 255), 2.0)
    trn = add(m, TRAIN, "v3 labels — used to train", visible=False)
    by_class7(trn, 0.5)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    uln = add(m, UNET, "Landforms — U-Net, seven classes, v3 labels, two passes (±60°, 200 m)", transparency=30)
    svm = add(m, SVM, "SVM, v3 labels (layout 04c)", visible=False, transparency=30)
    u2l = add(m, UNET2, "U-Net, v2 labels (layout 17b)", visible=False, transparency=30)
    hsl = add(m, os.path.join(G60, "global60_hillshade.tif"), "Hillshade (±60°, 200 m)")
    order(m, [tln.name, halo.name, trn.name, ext.name, uln.name, svm.name, u2l.name, hsl.name])
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
    fmt = lambda t: "%s / %s" % (format(t[0], ","), format(t[1], ","))
    rows = [["held out (%s polygons)" % format(hu["polygons"], ","), "U-Net, v3", "SVM, v3", "U-Net, v2"],
            ["accuracy, κ"] + ["%s, %.3f" % (pc(h["accuracy"], 1), h["kappa"]) for h in (hu, hs, h2)],
            ["balanced accuracy, macro F1"] + ["%.2f, %.2f" % (x["balanced_accuracy"], x["macro_f1"]) for x in (mu, ms, mu2)],
            ["polygons won (majority own class)"] + [fmt(won(h)) for h in (hu, hs, h2)],
            ["producer's, the 7 classes in order (%)"] + [seq(h, "producers") for h in (hu, hs, h2)],
            ["user's, the 7 classes in order (%)"] + [seq(h, "users") for h in (hu, hs, h2)],
            ["IAU craters (%d): Crater inside / ring" % u["iau_craters"]["n"]]
            + ["%.0f / %.0f %%" % (100 * x["iau_craters"]["crater_inside"], 100 * x["iau_craters"]["crater_ring"]) for x in (u, s, u2)],
            ["elevation bins alone reproduce"] + [pc(x["elevation_only_reproduces"]) for x in (u, s, u2)],
            ["seam ratio, 4096 px tiles at 100 m"] + ["%.2f" % x["seam_ratio"]["tile_4096_at_100m"] for x in (u, s, u2)]]
    lon = lambda v: "%d°E" % (v % 360)
    lat = lambda v: "%d°%s" % (abs(v), "N" if v > 0 else "S") if v else "0°"
    sh = u["share_area_weighted"]
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: seven landform classes from a U-Net, v3 labels", 19, "title", bold=True),
        text(0.45, 7.47, "A pixel classifier on the 7-band 200 m stack, trained on the third label set's training split "
             "only; two passes on tile grids 128 px apart remove the tile seams.", 10, "subtitle", colour=GREY),
        text(0.45, 4.62 + fh + 0.06, "A  ±60°: Normal Ground %.0f %%, Crater %.0f %%, edifice %.0f %%, fluvial %.0f %%, "
             "apron %.0f %%, lava tube %.1f %%, hills %.1f %%"
             % tuple(100 * sh[k] for k in ("Normal Ground", "Crater", "volcanic edifice", "fluvial channel", "apron",
                                           "lava tube", "steep/windy hills")), 9.5, "label_a", bold=True),
        text(0.45, 1.15 + zh + 0.06, "B  A held-out block with %d classes (%d polygons), %s–%s, %s–%s" % (
            len(z["classes"]), z["polygons"], lon(z["lon"]), lon(z["lon"] + 15), lat(z["lat"]), lat(z["lat"] + 15)),
             10, "label_b", bold=True),
        text(4.60, 4.06, "Three maps under the same scorer, on the v3 held-out polygons (KB §69.81)", 10, "table_title", bold=True),
        text(4.60, 1.80, "The lead map (the author's choice, D36). On the 237 v2 polygons it scores %s, κ %.3f, against the "
             "v2 U-Net's %s;\non the probability sample %s against %s (the AI assistant's labels, gate waived). Polygons "
             "flatter this map.\nIts faults: lava tube's user's accuracy, and edifice is denser inside none of %d named small edifices."
             % (pc(hv2["accuracy"], 1), hv2["kappa"], pc(f2["unet_v2"]["accuracy"], 1), pc(r2["overall"]["unet_v3"]["est"], 1),
                pc(r2["overall"]["unet7"]["est"], 1), n["n"]), 7.6, "findings", colour=DARK),
        text(0.45, 0.64, "Held-out polygons lie in 14 whole 15° blocks the model never saw; scored at 400 m, "
             "area-weighted, by the script behind every SVM figure. Classes in order: Crater, hills, lava tube, "
             "Normal Ground,\nedifice, apron, fluvial. The second pass, offset 128 px, took %.0f %% of the pixels "
             "and changed %.1f %%. Held-out labels are outlined in their class colours on a white halo. Grey streaks: "
             "no data\nin the stack (THEMIS gaps), the hillshade showing through. The v2 U-Net is layout 17b." % (
                 100 * mo["share_from_pass_b"], 100 * mo["share_a_b_disagree"]), 7.6, "notes", colour=DARK),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + table(4.60, 3.98, rows, [2.30, 1.22, 1.22, 1.21], size=7.2))
    legend_classes(p, lyt, mfa, 7.98, 7.12, 2.42, 2.40, [uln.name], names=True, cols=1)
    items = p.listStyleItems("ArcGIS 2D", "SCALE_BAR")
    add_text(lyt, [text(8.40, 1.58, "Scale of B", 8.2, "sbar_label", bold=True, colour=DARK)])
    sb = lyt.createMapSurroundElement(arcpy.Point(8.40, 1.16), "SCALE_BAR", mfb,
                                      next((i for i in items if i.name == "Double Alternating Scale Bar 1 Metric"), items[0]), "sbar")
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
