# -*- coding: utf-8 -*-
r"""X5c's ±60° U-Net map into the project beside the published SVM map, as the terrain-province map (the author's
decision, 2026-10-21, KB §66.9). The SVM map stays the published one.

  DL_UNet_Heldout_Scores_20261020   the 183 held-out polygons, each with its own-class share and majority class
                                    under the U-Net (two passes, §66.8) and the published SVM map, at 400 m by
                                    svmcheck.training_score, the code behind §31.3 and §57; fields Classname,
                                    Classvalue, Block, UNet_Own, UNet_Major, SVM_Own, SVM_Major, MappedBy. Their
                                    area-weighted sums must give the maps' held-out accuracies, or it stops.
  the two U-Net rasters' tables     Classvalue, Red, Green, Blue added, as the SVM maps carry, so Pro draws
                                    them in the class colours
  map "X5c — U-Net terrain provinces (±60°)"
                                    the two-pass map at 30 % transparency over the hillshade, the held-out
                                    polygons outlined in their class colours, the 30° graticule; the one-pass
                                    map, the published SVM map and the training labels present but off
  layout 17_x5c_unet_provinces      the map over ±60° and over the held-out block with the most classes; the
                                    U-Net against the published SVM map, every figure read from the logs at run
                                    time (logs\dl_unet_sheet.json); what the map is and is not

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy beside the real .aprx (§31.5).
"""
import os, sys, time, shutil, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from svmcheck import training_score
from layoutkit import text, poly_geom
from make_global60_maps import (outline, by_class, add, get_map, order, page, add_text, legend_classes,
                                extent_polygon, CLASS_COLOURS, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table
from make_dl_map import by_class_field

gdal.UseExceptions()
APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
MARKER = "make_unet_map.py"
G60 = G.OUTDIR
UNET = os.path.join(G60, "global60_landforms_unet_200m_seamfix.tif")
UNET1 = os.path.join(G60, "global60_landforms_unet_200m.tif")
SVM = os.path.join(G60, "global60_landforms_svm_200m_mode11.tif")
TEST = os.path.join(GDB, "Landform_TrainingSamples_terrain_60_test")
FC = os.path.join(GDB, "DL_UNet_Heldout_Scores_20261020")
NAMES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
LOGS = os.path.join(HERE, "logs")
CHECK_U = os.path.join(LOGS, "global60_classification_check_global60_landforms_unet_200m_seamfix.json")
CHECK_S = os.path.join(LOGS, "global60_classification_check_200m_mode11.json")
SEAMS = os.path.join(LOGS, "dl_seams.json")
MOSAIC = os.path.join(LOGS, "dl_unet_global_mosaic_seamfix.json")
SHEET_LOG = os.path.join(LOGS, "dl_unet_sheet.json")
MAP = "X5c — U-Net terrain provinces (±60°)"
L17 = "17_x5c_unet_provinces"
TABLE_W = [2.45, 1.75, 1.75]                       # 5.95 in: x 4.60 to the 10.55 in margin
DEG = 180.0 / (np.pi * G.R_MARS)

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def colour_tables():
    """Classvalue and the class colours in both U-Net rasters' attribute tables, as the SVM maps have them."""
    for p in (UNET, UNET1):
        have = [f.name for f in arcpy.ListFields(p)]
        for f in ("Classvalue", "Red", "Green", "Blue"):
            if f not in have:
                arcpy.management.AddField(p, f, "LONG")
        with arcpy.da.UpdateCursor(p, ["Value", "Class_name", "Classvalue", "Red", "Green", "Blue"]) as cur:
            for v, n, *_ in cur:
                cur.updateRow([v, n, v] + list(CLASS_COLOURS[n]))


def lut_of(path):
    lut = np.full(256, 255, np.uint8)
    with arcpy.da.SearchCursor(path, ["Value", "Class_name"]) as c:
        for v, n in c:
            lut[int(v)] = NAMES.index(n.strip())
    return lut


def heldout_records():
    """Per held-out polygon, at 400 m on each map's own window of the 15° block: own-class share and majority."""
    sr = arcpy.Describe(UNET).spatialReference
    polys = []
    with arcpy.da.SearchCursor(TEST, ["OID@", "SHAPE@", "Classvalue", "Classname"]) as c:
        for oid, g, v, n in c:
            polys.append(dict(oid=oid, shape=g, v=int(v), name=n,
                              block=(int(g.centroid.X // 15) * 15, int(g.centroid.Y // 15) * 15),
                              rings=[[(p.X, p.Y) for p in part if p is not None] for part in g],
                              ext=g.projectAs(sr).extent))
    blocks = collections.defaultdict(list)
    for p in polys:
        blocks[p["block"]].append(p)
    res = {}
    for tag, path in (("unet", UNET), ("svm", SVM)):
        lut = lut_of(path)
        ds = gdal.Open(path); b = ds.GetRasterBand(1); mk = b.GetMaskBand()
        tot = np.zeros((4, 4))
        for k, ps in blocks.items():
            x0 = min(p["ext"].XMin for p in ps) - 25e3; x1 = max(p["ext"].XMax for p in ps) + 25e3
            y0 = min(p["ext"].YMin for p in ps) - 25e3; y1 = max(p["ext"].YMax for p in ps) + 25e3
            c0 = max(int((x0 - G.G200.ox) // 400) * 2, 0); r0 = max(int((G.G200.oy - y1) // 400) * 2, 0)
            c1 = min(int(np.ceil((x1 - G.G200.ox) / 400)) * 2, ds.RasterXSize)
            r1 = min(int(np.ceil((G.G200.oy - y0) / 400)) * 2, ds.RasterYSize)
            raw = b.ReadAsArray(c0, r0, c1 - c0, r1 - r0)[::2, ::2]     # the 400 m lattice, as §57 scored
            m = (mk.ReadAsArray(c0, r0, c1 - c0, r1 - r0)[::2, ::2] > 0) & (lut[raw] != 255)
            a = np.where(m, lut[raw], 0).astype(np.uint8)
            xl = G.G200.ox + c0 * 200.0; yt = G.G200.oy - r0 * 200.0
            g = dict(dpx=400 * DEG, dpy=400 * DEG, lat_top=yt * DEG, lon_left=G.G200.lon_of(xl) % 360)
            for p in ps:
                cmx, _ = training_score(a, m, g, [(p["v"], p["rings"])])
                row = cmx[p["v"] - 1]
                res.setdefault(p["oid"], {})[tag] = (row[p["v"] - 1] / row.sum() if row.sum() else None,
                                                     NAMES[int(row.argmax())] if row.sum() else None)
                tot += cmx
        res.setdefault("_total", {})[tag] = float(np.trace(tot) / tot.sum())
    return polys, res


def write_fc():
    polys, res = heldout_records()
    exp = {"unet": json.load(open(CHECK_U))["held_out"]["accuracy"],
           "svm": json.load(open(CHECK_S))["held_out"]["accuracy"]}
    for tag in exp:                       # the per-polygon records must sum to the maps' held-out accuracy
        assert abs(res["_total"][tag] - exp[tag]) < 0.002, (tag, res["_total"][tag], exp[tag])
    if arcpy.Exists(FC):
        with arcpy.da.SearchCursor(FC, ["MappedBy"]) as c:
            if not all(r[0] == MARKER for r in c):
                sys.exit("REFUSING: %s holds rows this script did not write" % FC)
        arcpy.management.Delete(FC)
    sr = arcpy.Describe(TEST).spatialReference
    arcpy.management.CreateFeatureclass(GDB, os.path.basename(FC), "POLYGON", spatial_reference=sr)
    for f, t, n in (("Classname", "TEXT", 32), ("Classvalue", "SHORT", None), ("Block", "TEXT", 16),
                    ("UNet_Own", "DOUBLE", None), ("UNet_Major", "TEXT", 32), ("SVM_Own", "DOUBLE", None),
                    ("SVM_Major", "TEXT", 32), ("MappedBy", "TEXT", 64)):
        arcpy.management.AddField(FC, f, t, field_length=n) if n else arcpy.management.AddField(FC, f, t)
    with arcpy.da.InsertCursor(FC, ["SHAPE@", "Classname", "Classvalue", "Block", "UNet_Own", "UNet_Major",
                                    "SVM_Own", "SVM_Major", "MappedBy"]) as cur:
        for p in polys:
            r = res[p["oid"]]
            cur.insertRow([p["shape"], p["name"], p["v"], "%+04d%+03d" % p["block"], r["unet"][0], r["unet"][1],
                           r["svm"][0], r["svm"][1], MARKER])
    n = int(arcpy.management.GetCount(FC)[0])
    assert n == len(polys) == int(arcpy.management.GetCount(TEST)[0])
    won = {t: sum(1 for p in polys if res[p["oid"]][t][0] is not None and res[p["oid"]][t][0] > .5)
           for t in ("unet", "svm")}
    print("  %s: %d polygons; summed accuracy U-Net %.4f, SVM %.4f; won (own class > 50 %%) %s" % (
        os.path.basename(FC), n, res["_total"]["unet"], res["_total"]["svm"], won))
    return won


def sheet_numbers(won):
    u, s = json.load(open(CHECK_U)), json.load(open(CHECK_S))
    sm, mo = json.load(open(SEAMS)), json.load(open(MOSAIC))
    blocks = collections.defaultdict(lambda: [set(), []])
    with arcpy.da.SearchCursor(TEST, ["SHAPE@", "Classname"]) as c:
        for g, n in c:
            k = (int(g.centroid.X // 15) * 15, int(g.centroid.Y // 15) * 15)
            blocks[k][0].add(n); blocks[k][1].append(g.extent)
    k, (cls, ex) = max(blocks.items(), key=lambda kv: (len(kv[1][0]), len(kv[1][1])))
    out = {"when": time.strftime("%Y-%m-%d %H:%M"), "unet": u, "svm": s,
           "seams_256": {"unet": sm[os.path.basename(UNET)], "svm": sm[os.path.basename(SVM)]},
           "mosaic": mo, "won": won,
           "zoom_block": {"lon": k[0], "lat": k[1], "classes": sorted(cls), "polygons": len(ex),
                          "extent_deg": [min(e.XMin for e in ex), min(e.YMin for e in ex),
                                         max(e.XMax for e in ex), max(e.YMax for e in ex)]}}
    json.dump(out, open(SHEET_LOG, "w"), indent=1, default=str)
    return out


def sheet(p, m, uln, tln, won):
    n = sheet_numbers(won)
    u, s, z = n["unet"], n["svm"], n["zoom_block"]
    hu, hs = u["held_out"], s["held_out"]
    lyt = page(p, L17)
    fw = 7.35; fh = fw / 3.0
    mfa = lyt.createMapFrame(poly_geom(0.45, 4.62, fw, fh), m, "frame_all")
    mfa.camera.setExtent(extent_polygon().projectAs(m.spatialReference).extent)
    zw, zh = 3.90, 3.05
    mfb = lyt.createMapFrame(poly_geom(0.45, 1.15, zw, zh), m, "frame_block")
    pad = 0.4
    mfb.camera.setExtent(arcpy.Extent(z["extent_deg"][0] - pad, z["extent_deg"][1] - pad,
                                      z["extent_deg"][2] + pad, z["extent_deg"][3] + pad))
    pc = lambda v: "%.1f %%" % (100 * v)
    su, ss = n["seams_256"]["unet"], n["seams_256"]["svm"]
    cu, cs = u["iau_craters"], s["iau_craters"]
    rows = [["held out (%d polygons)" % hu["polygons"], "U-Net, two passes", "SVM 11 × 11, published"],
            ["accuracy, κ", "%s, %.3f" % (pc(hu["accuracy"]), hu["kappa"]),
             "%s, %.3f" % (pc(hs["accuracy"]), hs["kappa"])],
            ["polygons won (own class > 50 %)", "%d" % won["unet"], "%d" % won["svm"]]]
    uu = lambda h: "%s %%" % " / ".join("%.0f" % (100 * h["users"][k]) for k in NAMES)
    rows.append(["user's: Crater / hills / lava tube / plains", uu(hu), uu(hs)])
    rows += [["IAU craters (%d): Crater inside / ring" % cu["n"],
              "%.0f / %.0f %%" % (100 * cu["crater_inside"], 100 * cu["crater_ring"]),
              "%.0f / %.0f %%" % (100 * cs["crater_inside"], 100 * cs["crater_ring"])],
             ["elevation bins alone reproduce", pc(u["elevation_only_reproduces"]),
              pc(s["elevation_only_reproduces"])],
             ["seam ratio at 256 px, columns / rows", "%.2f / %.2f" % (su["columns_256"]["ratio"],
                                                                     su["rows_256"]["ratio"]),
              "%.2f / %.2f" % (ss["columns_256"]["ratio"], ss["rows_256"]["ratio"])]]
    lon = lambda v: "%d°E" % (v % 360)
    lat = lambda v: "%d°%s" % (abs(v), "N" if v > 0 else "S") if v else "0°"
    dark, grey = (40, 40, 40), (70, 70, 70)
    sh = u["share_area_weighted"]
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: terrain provinces from a U-Net, beside the published SVM map "
             "(X5c)", 19, "title", bold=True),
        text(0.45, 7.47, "A pixel classifier on the 7-band 200 m stack, trained on the training split only; "
             "two passes on tile grids 128 px apart remove the tile seams.", 10, "subtitle", colour=grey),
        text(0.45, 4.62 + fh + 0.06, "A  ±60°: Crater %.0f %%, Normal Ground %.0f %%, lava tube %.1f %%, "
             "hills %.1f %% of the area" % (100 * sh["Crater"], 100 * sh["Normal Ground"], 100 * sh["lava tube"],
                                            100 * sh["steep/windy hills"]), 10, "label_a", bold=True),
        text(0.45, 1.15 + zh + 0.06, "B  A held-out block with %d classes (%d polygons), %s–%s, %s–%s" % (
            len(z["classes"]), z["polygons"], lon(z["lon"]), lon(z["lon"] + 15), lat(z["lat"]), lat(z["lat"] + 15)),
             10, "label_b", bold=True),
        text(4.60, 4.06, "The two maps under the same scorer (KB §66.7–66.8, §57)", 10,
             "table_title", bold=True),
        text(4.60, 1.92, "The U-Net maps terrain provinces. It matches the hand-drawn areas almost "
             "everywhere and\nmakes lava tube usable (user's %.0f %% against %.0f %%), but it does not map single "
             "features: 'Crater'\ncovers %.0f %% of the ring round named craters, so it marks cratered terrain "
             "rather than craters;\nelevation alone reproduces %.0f %% of it. The SVM map stays the published one (layout 04)."
             % (100 * hu["users"]["lava tube"], 100 * hs["users"]["lava tube"], 100 * cu["crater_ring"],
                100 * u["elevation_only_reproduces"]), 7.9, "findings", colour=dark),
        text(0.45, 0.64, "Held-out polygons lie in 14 whole 15° blocks the model never saw; scored at 400 m, "
             "area-weighted, by the script behind every SVM figure. A held-out block beside a training block of "
             "the same terrain\nis easier than new terrain, for both maps. One pass left seams on the tool's 256 px "
             "tiles (ratio 8.6–9.2); the second pass, offset 128 px, took %.0f %% of the pixels and changed "
             "%.1f %%.\nHeld-out labels are outlined in their class colours on a white halo. Grey streaks: no data "
             "in the stack (THEMIS gaps), the hillshade showing through." % (
                 100 * n["mosaic"]["share_from_pass_b"], 100 * n["mosaic"]["share_a_b_disagree"]),
             7.9, "notes", colour=dark),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + table(4.60, 3.98, rows, TABLE_W, size=7.6))
    legend_classes(p, lyt, mfa, 7.98, 7.12, 2.42, 2.40, [uln.name, tln.name], names=True, cols=1)
    items = p.listStyleItems("ArcGIS 2D", "SCALE_BAR")
    # beside B, not on it: over the classes its labels could not be read (as on layout 16)
    add_text(lyt, [text(4.60, 1.62, "Scale of B", 8.2, "sbar_label", bold=True, colour=dark)])
    sb = lyt.createMapSurroundElement(arcpy.Point(4.60, 1.20), "SCALE_BAR", mfb,
                                      next((i for i in items if i.name == "Double Alternating Scale Bar 1 Metric"),
                                           items[0]), "sbar")
    d = sb.getDefinition("V3")
    d.divisions, d.subdivisions, d.division = 2, 0, 100.0
    d.labelFrequency = "Divisions"
    d.fittingStrategy = "AdjustFrame"
    sb.setDefinition(d)
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L17 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    print("1. the U-Net rasters' class tables")
    colour_tables()
    print("2. feature class")
    won = write_fc()
    print("3. map:", MAP)
    p = arcpy.mp.ArcGISProject(APRX)
    m = get_map(p, MAP)
    tln = add(m, FC, "Held-out labels (never trained on)")
    by_class_field(tln, "Classname", 1.0)
    # a white halo under the class-colour outlines: a label drawn in its own class colour over a map filled in
    # the same colour vanished exactly where the map agrees with it (rehearsal, KB §66.9)
    halo = add(m, FC, "Held-out labels — halo")
    outline(halo, (255, 255, 255), 2.6)
    trn = add(m, os.path.join(GDB, "Landform_TrainingSamples_terrain_60_train"),
              "Hand-drawn labels — used to train", visible=False)
    by_class(trn, 0.7)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    uln = add(m, UNET, "Landforms — U-Net, two passes (±60°, 200 m)", transparency=30)
    u1 = add(m, UNET1, "U-Net, one pass — 256 px tile seams (KB §66.7)", visible=False, transparency=30)
    svm = add(m, SVM, "SVM 11 × 11 — the published map (layout 04)", visible=False, transparency=30)
    hs = add(m, os.path.join(G60, "global60_hillshade.tif"), "Hillshade (±60°, 200 m)")
    order(m, [tln.name, halo.name, trn.name, ext.name, uln.name, u1.name, svm.name, hs.name])
    add_graticule(p, MAP, G30, 7)
    print("4. layout", L17)
    sheet(p, m, uln, tln, won)
    p.save()
    m = next(x for x in p.listMaps() if x.name == MAP)
    print("   drawing order:", [l.name for l in m.listLayers()])
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
