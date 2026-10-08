# -*- coding: utf-8 -*-
r"""Puts the ±60° work INTO the ArcGIS project, where it shows when the project opens in Pro (KB §31).

  1. clips every Mars map to the ±60° analysis extent (Map.clipLayers - display only,
     nothing is deleted; clipLayers(None) undoes it)
  2. builds the map "Mars ±60° Analysis": the corrected classification over hillshade, the hand-drawn
     labels split train / held-out, the inputs, the two 29-30 Sep GUI SVMs as superseded layers
  3. builds two small maps, "Check — 29 Sep SVM" and "Check — 30 Sep SVM", so each check layout
     shows the right layer live, not whichever layer was last switched on
  4. layouts 04_global60_landforms and 05_svm_checks, exported to Global60\layouts\
  5. gives the type-area sheets 01 and 02 a map each, so they show Viking and night IR in Pro
     instead of the classification that 03 shares the old map with

Pro must be closed. The .aprx is copied to Z:\Mars Project\.backups\ first.
Needs make_global60_svm_stack.py, make_global60_classification.py and
verify_global60_classification.py to have run. Run polish_layouts.py afterwards (KB §33).
"""
import os, sys, time, json, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # cp1252 console: ≥ and — would crash a print
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
from make_global60_classification import OUT as CLS_PATH, CELL
from layoutkit import C, rgb, text, poly_geom

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv      # a copy, for a dry run
        else r"Z:\Mars Project\Mars Project.aprx")
BKDIR = r"Z:\Mars Project\.backups"
GDB = r"Z:\Mars Project\Mars Project.gdb"
G60 = G.OUTDIR          # the real folder, NOT the junction: it breaks when the drive is F: (KB §34)
OUTD = os.path.join(G.OUTDIR, "layouts")
MARS = arcpy.SpatialReference(104905)
MARKER = "make_global60_maps.py"
CHECK_PATH = os.path.join(HERE, "logs", "global60_classification_check_%dm.json" % CELL)
# The corrected classification may still be running: everything else is built without it,
# and a rerun once it and its check exist adds the layer and layout 04.
HAVE_CLS = os.path.exists(CLS_PATH) and os.path.exists(CHECK_PATH)
CHECK = json.load(open(CHECK_PATH)) if HAVE_CLS else None
# The published layer is the 5 x 5 (2 km) majority-filtered map, KB §32.2: half the ~4 km resolving
# limit of a 400 m map. The window was fixed by feature size; polygon scores rise with any smoothing.
CLEAN = 5
CLEAN_PATH = CLS_PATH.replace(".tif", "_mode%d.tif" % CLEAN)
CLEAN_CHECK = os.path.join(HERE, "logs", "global60_classification_check_%dm_mode%d.json" % (CELL, CLEAN))
HAVE_CLEAN = HAVE_CLS and os.path.exists(CLEAN_PATH) and os.path.exists(CLEAN_CHECK)
RAW = CHECK
if HAVE_CLEAN:
    CHECK = json.load(open(CLEAN_CHECK))
OLD = json.load(open(os.path.join(HERE, "logs", "svm_check.json")))
TILES = os.path.join(GDB, "Check_Tiles_4096px_60")

MAIN, C29, C30 = "Mars \u00b160\u00b0 Analysis", "Check \u2014 29 Sep SVM", "Check \u2014 30 Sep SVM"
CLASS_COLOURS = {"Crater": (255, 0, 0), "steep/windy hills": (28, 119, 85),
                 "lava tube": (158, 25, 147), "Normal Ground": (81, 51, 13)}   # the RAT colours
NOT_MARS = ("Map", "Map1", "Enceladus", "Mercury", "mars")   # Earth, Enceladus, Mercury, broken HiRISE
PAGE_W, PAGE_H = 11.0, 8.5
CREDIT = ("Logan Edwards  \u00b7  OCN 4704 Remote Sensing  \u00b7  Mars Global Mosaic  \u00b7  "
          "analysis extent \u00b160\u00b0 latitude (the THEMIS night mosaic)  \u00b7  Mars 2000 sphere")

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def extent_polygon():
    with arcpy.da.SearchCursor(os.path.join(GDB, "Analysis_Extent_60"), ["SHAPE@"]) as c:
        return next(c)[0]


def make_tiles():
    """The 4096 x 4096 px processing-tile grid of the night grid, as polygons (§30.2)."""
    sr = arcpy.SpatialReference(); sr.loadFromString(G.TARGET_WKT)
    if arcpy.Exists(TILES):
        with arcpy.da.SearchCursor(TILES, ["MappedBy"]) as c:
            if not all(r[0] == MARKER for r in c):
                sys.exit("REFUSING: %s holds rows this script did not write" % TILES)
        arcpy.management.Delete(TILES)
    arcpy.management.CreateFeatureclass(GDB, os.path.basename(TILES), "POLYGON", spatial_reference=sr)
    arcpy.management.AddField(TILES, "MappedBy", "TEXT", field_length=64)
    arcpy.management.AddField(TILES, "Tile", "TEXT", field_length=16)
    step = 4096 * G.G100.res
    with arcpy.da.InsertCursor(TILES, ["SHAPE@", "MappedBy", "Tile"]) as cur:
        for (col, row, x0, y0, w, h) in G.G100.tiles(4096):
            x = G.G100.ox + x0 * G.G100.res; y = G.G100.oy - y0 * G.G100.res
            pts = [(x, y), (x + w * 100, y), (x + w * 100, y - h * 100), (x, y - h * 100), (x, y)]
            cur.insertRow([arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in pts]), sr), MARKER,
                           "c%02d_r%02d" % (col, row)])
    print("  %s: %d tiles of %.0f km" % (os.path.basename(TILES), int(arcpy.management.GetCount(TILES)[0]), step / 1000))


def outline(layer, colour, width=1.2, dashed=False):
    sym = layer.symbology
    sym.renderer.symbol.color = {"RGB": [0, 0, 0, 0]}
    sym.renderer.symbol.outlineColor = {"RGB": list(colour) + [100]}
    sym.renderer.symbol.outlineWidth = width
    layer.symbology = sym


def by_class(layer, width):
    """Hollow polygons outlined in the class colours."""
    sym = layer.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = ["Classname"]
    for grp in sym.renderer.groups:
        for it in grp.items:
            col = CLASS_COLOURS.get(it.values[0][0], (255, 255, 255))
            it.symbol.color = {"RGB": [0, 0, 0, 0]}
            it.symbol.outlineColor = {"RGB": list(col) + [100]}
            it.symbol.outlineWidth = width
    layer.symbology = sym


def get_map(p, name):
    m = next((x for x in p.listMaps() if x.name == name), None)
    if m is None:
        m = p.createMap(name, "MAP")
    for l in list(m.listLayers()):
        m.removeLayer(l)
    m.spatialReference = MARS
    return m


def add(m, path, name, visible=True, group=None, transparency=0):
    l = m.addDataFromPath(path)
    l.name = name; l.visible = visible
    if transparency:
        l.transparency = transparency
    if group is not None:
        # BOTTOM, added in top-to-bottom order: moveLayer inside a group DELETES layers (KB §31.5)
        m.addLayerToGroup(group, l, "BOTTOM"); m.removeLayer(l)
        l = [x for x in group.listLayers() if x.name == name][0]
    return l


def order(m, names):
    """Stack these TOP-LEVEL layers top to bottom. Never use it inside a group: there moveLayer
    drops layers from the map."""
    for above, below in zip(names, names[1:]):
        a = [l for l in m.listLayers() if l.name == above][0]
        b = [l for l in m.listLayers() if l.name == below][0]
        m.moveLayer(a, b, "AFTER")


def group(m, name, visible=True):
    g = m.createGroupLayer(name); g.visible = visible
    return g


def legend_classes(p, lyt, mf, x, y, w, h, layer_names, names=True, cols=1):
    """Legend of just these layers, in this order; names=False shows the swatches alone."""
    items = p.listStyleItems("ArcGIS 2D", "LEGEND")
    el = lyt.createMapSurroundElement(arcpy.Point(x, y), "LEGEND", mf,
                                      next((i for i in items if i.name == "Legend 1"), items[0]), "legend")
    d = el.getDefinition("V3")
    d.showTitle = False
    byname = {it.name: it for it in d.items}
    keep = []
    for n in layer_names:
        it = byname.get(n)
        if it is None:
            continue
        for att in ("showHeading", "showLayerName", "showGroupLayerName"):
            if hasattr(it, att):
                setattr(it, att, names and att == "showLayerName")
        keep.append(it)
    d.items = keep
    d.autoAdd = False
    fr = getattr(d, "frame", None)                   # no box round it; the CIM may hand back a dict
    if isinstance(fr, dict):
        fr["borderSymbol"] = None
    elif fr is not None:
        fr.borderSymbol = None
    el.setDefinition(d)
    el.columnCount = cols
    el.elementWidth = w; el.elementHeight = h
    el.setAnchor("TOP_LEFT_CORNER"); el.elementPositionX = x; el.elementPositionY = y
    return el


def page(p, name):
    lyt = next((x for x in p.listLayouts() if x.name == name), None)
    if lyt is None:
        lyt = p.createLayout(PAGE_W, PAGE_H, "INCH"); lyt.name = name
    for e in lyt.listElements():
        lyt.deleteElement(e)
    return lyt


def add_text(lyt, items):
    cim = lyt.getDefinition("V3")
    cim.elements = list(cim.elements) + items
    lyt.setDefinition(cim)


def frame(lyt, m, geom, name):
    mf = lyt.createMapFrame(poly_geom(*geom), m, name)
    ext = extent_polygon().projectAs(m.spatialReference).extent
    mf.camera.setExtent(ext)
    return mf


def main():
    os.makedirs(BKDIR, exist_ok=True); os.makedirs(OUTD, exist_ok=True)
    bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(APRX, bk); print("backup", bk)
    print("1. tile grid"); make_tiles()
    p = arcpy.mp.ArcGISProject(APRX)
    clip = extent_polygon()

    # ------------------------------------------------------------------ main map
    print("2. map:", MAIN)
    m = get_map(p, MAIN)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent \u00b160\u00b0")
    outline(ext, (232, 128, 74), 1.5)
    tst = add(m, os.path.join(GDB, "Landform_TrainingSamples_terrain_60_test"),
              "Hand-drawn labels \u2014 held out (scored, never trained on)")
    by_class(tst, 1.6)
    trn = add(m, os.path.join(GDB, "Landform_TrainingSamples_terrain_60_train"), "Hand-drawn labels \u2014 used to train")
    by_class(trn, 0.7)
    cls = raw = None
    if HAVE_CLS:
        raw = add(m, os.path.join(G60, os.path.basename(CLS_PATH)),
                  "Landforms \u2014 raw per-pixel SVM (\u00b160\u00b0, %d m)" % CELL,
                  visible=not HAVE_CLEAN, transparency=30)
        cls = raw
    if HAVE_CLEAN:
        cls = add(m, os.path.join(G60, os.path.basename(CLEAN_PATH)),
                  "Landforms \u2014 SVM, %d \u00d7 %d majority (\u00b160\u00b0, %d m)" % (CLEAN, CLEAN, CELL),
                  transparency=30)
    gin = group(m, "Inputs (\u00b160\u00b0, 200 m)", visible=True)
    add(m, os.path.join(G60, "global60_svm_stack_200m.tif"), "Stack: Viking RGB (bands 1\u20133 of 7)", False, gin)
    # §28.10: the THEMIS mosaics are locally contrast-normalised, so this is never a planet-wide material map
    add(m, os.path.join(G60, "global60_thermal_contrast.tif"),
        "Diurnal contrast index — compare within one area only (KB §28.10)", False, gin)
    add(m, os.path.join(G60, "global60_slope_deg.tif"), "Slope (degrees)", False, gin)
    add(m, os.path.join(G60, "global60_dem.tif"), "Elevation (HRSC/MOLA)", False, gin)
    add(m, os.path.join(G60, "global60_hillshade.tif"), "Hillshade", True, gin)
    gold = group(m, "Superseded: the 29\u201330 Sep GUI SVMs (KB \u00a730)", visible=False)
    add(m, os.path.join(GDB, "Classified_202609292109007048151"), "29 Sep SVM \u2014 tile artefact", False, gold)
    add(m, os.path.join(GDB, "Classified_202609300147338582853"), "30 Sep SVM \u2014 mostly elevation", False, gold)
    gc = group(m, "Reference", visible=False)
    add(m, os.path.join(GDB, "MARS_nomenclature_craters_gt100km_March2019"), "IAU craters > 100 km", False, gc)
    add(m, os.path.join(GDB, "MARS_nomenclature_craters_lt100km_March2019"), "IAU craters < 100 km", False, gc)
    add(m, os.path.join(GDB, "Landform_BasinCandidates_auto_60"), "Basin candidates \u2265 20 km (auto)", False, gc)
    # Pro auto-arranges what is added (and a new group lands on top), which put the opaque hillshade
    # over the classification. Set the drawing order explicitly, top to bottom.
    top = ([ext.name, tst.name, trn.name] + ([cls.name] if cls is not None else [])
           + ([raw.name] if raw is not None and raw is not cls else []) + [gc.name, gold.name, gin.name])
    order(m, top)
    print("   drawing order:", [l.name for l in m.listLayers()])

    # ------------------------------------------------------------------ check maps
    print("3. check maps")
    m29 = get_map(p, C29)
    tl = add(m29, TILES, "4096-px processing tiles"); outline(tl, (255, 255, 255), 0.4)
    add(m29, os.path.join(GDB, "Classified_202609292109007048151"), "29 Sep SVM over the \u00b160\u00b0 segments")
    m30 = get_map(p, C30)
    add(m30, os.path.join(GDB, "Classified_202609300147338582853"), "30 Sep SVM over the 7-band CompositeBand")

    # ------------------------------------------------------------------ clip
    print("4. clip every Mars map to \u00b160\u00b0")
    for mp in p.listMaps():
        if mp.name in NOT_MARS or mp.name == "Ius Chasma Type Area":
            continue
        sr = mp.spatialReference
        mp.clipLayers(clip.projectAs(sr) if sr and sr.name != clip.spatialReference.name else clip)
        print("   clipped:", mp.name)

    # ------------------------------------------------------------------ layout 04
    print("5. layouts")
    if not HAVE_CLS:
        print("   04_global60_landforms skipped: %s not built yet" % os.path.basename(CLS_PATH))
    else:
        ho, tr = CHECK["held_out"], CHECK["training_set"]
        lyt = page(p, "04_global60_landforms")
        fw = 10.1; fh = fw / 3.0
        mf = frame(lyt, m, (0.45, 3.55, fw, fh), "frame")
        add_text(lyt, [
            text(0.45, 7.80, "Mars \u00b160\u00b0 \u2014 landform classification", 21, "title", bold=True),
            text(0.45, 7.22, "Support vector machine on the 512 hand-drawn labels, over a corrected 7-band stack: "
                 "Viking RGB, THEMIS night + day IR, slope (\u00b0), local relief.\nNo raw elevation band."
                 + (" Smoothed with a %d \u00d7 %d (2 km) majority filter." % (CLEAN, CLEAN) if HAVE_CLEAN else ""),
                 10, "subtitle", colour=(70, 70, 70)),
            text(0.45, 2.95, "Scored on %d held-out polygons: whole 15\u00b0 blocks the classifier never saw"
                 % ho["polygons"], 10.5, "acc_head", bold=True),
            text(0.45, 1.80, "Overall %.0f%%, \u03ba %.2f   (one class everywhere would score %.0f%%)\n"
                 "Producer's:  Crater %.0f%%, steep/windy hills %.0f%%, lava tube %.0f%%, Normal Ground %.0f%%\n"
                 "User's:        Crater %.0f%%, steep/windy hills %.0f%%, lava tube %.0f%%, Normal Ground %.0f%%\n"
                 "Lava tube is unreliable: %.0f%% of the map, and %.0f%% of its held-out pixels are right.\n"
                 "On its own training polygons: %.0f%%, \u03ba %.2f.   Raw per-pixel map, before smoothing: %.0f%%, \u03ba %.2f held out."
                 % (100 * ho["accuracy"], ho["kappa"], 100 * ho["one_class_everywhere"],
                    *[100 * ho["producers"][k] for k in CLASS_COLOURS],
                    *[100 * ho["users"][k] for k in CLASS_COLOURS],
                    100 * CHECK["share_area_weighted"]["lava tube"], 100 * ho["users"]["lava tube"],
                    100 * tr["accuracy"], tr["kappa"],
                    100 * RAW["held_out"]["accuracy"], RAW["held_out"]["kappa"]),
                 9.2, "acc_body", colour=(40, 40, 40)),
            text(0.45, 0.80, "Checks (KB \u00a731): elevation bins alone reproduce %.0f%% of it, one class alone %.0f%%\n"
                 "(the 30 Sep map: 62%%). Tile-seam ratio %.2f (the 29 Sep map: 2.77). 'Crater' inside\n"
                 "IAU craters %.0f%%, in a ring around them %.0f%% (n = %d)."
                 % (100 * CHECK["elevation_only_reproduces"], 100 * CHECK["largest_class_alone"],
                    CHECK["seam_ratio"]["tile_4096_at_100m"],
                    100 * CHECK["iau_craters"]["crater_inside"], 100 * CHECK["iau_craters"]["crater_ring"],
                    CHECK["iau_craters"]["n"]), 8.6, "checks", colour=(70, 70, 70)),
            text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))])
        legend_classes(p, lyt, mf, 7.25, 3.30, 3.3, 1.9, [cls.name, tst.name, ext.name], cols=2)
        out = os.path.join(OUTD, "04_global60_landforms.png"); lyt.exportToPNG(out, resolution=150)
        print("   ", out)

    # ------------------------------------------------------------------ layout 05
    lyt = page(p, "05_svm_checks")
    fw = 7.2; fh = fw / 3.0
    mfa = frame(lyt, m29, (0.45, 4.55, fw, fh), "frame29")
    mfb = frame(lyt, m30, (0.45, 1.05, fw, fh), "frame30")
    a, b = OLD["night"], OLD["comp7"]
    add_text(lyt, [
        text(0.45, 7.80, "The first two SVM classifications, checked", 21, "title", bold=True),
        text(0.45, 7.36, "29 Sep \u2014 SVM over the \u00b160\u00b0 segments + Night IR", 11, "h29", bold=True),
        text(0.45, 7.10, "Uniform blocks on the 4096-px tile grid (white).", 9, "s29", colour=(70, 70, 70)),
        text(7.85, 4.62, "On their own training polygons:\n%.0f%%, \u03ba %.2f\n(one class everywhere: %.0f%%)\n\n"
             "Normal Ground polygons won: %s\nlava tube: %s\n\n'Crater' inside IAU craters %.0f%%,\naround them %.0f%%\n\n"
             "Seams appear only at the classify step:\ninput 1.00, segments 1.01, output 2.77"
             % (100 * a["training_score"]["accuracy"], a["training_score"]["kappa"],
                100 * a["training_score"]["one_class_everywhere"],
                a["training_score"]["polygons_majority_own_class"]["Normal Ground"],
                a["training_score"]["polygons_majority_own_class"]["lava tube"],
                100 * a["iau_craters"]["crater_inside"], 100 * a["iau_craters"]["crater_ring"]),
             8.6, "t29", colour=(40, 40, 40)),
        text(0.45, 3.86, "30 Sep \u2014 SVM over the 7-band CompositeBand", 11, "h30", bold=True),
        text(0.45, 3.60, "Shown clipped to \u00b160\u00b0; past it the thermal bands were empty.", 9, "s30",
             colour=(70, 70, 70)),
        text(7.85, 1.10, "On their own training polygons:\n%.0f%%, \u03ba %.2f\n\nElevation bins alone\nreproduce %.0f%% of it\n"
             "(raw DEM band in metres\nbeside 8-bit bands)\n\n'Crater' inside IAU craters %.0f%%,\naround them %.0f%%"
             % (100 * b["training_score"]["accuracy"], b["training_score"]["kappa"],
                100 * b["elevation_only_reproduces"],
                100 * b["iau_craters"]["crater_inside"], 100 * b["iau_craters"]["crater_ring"]),
             8.6, "t30", colour=(40, 40, 40)),
        text(0.45, 0.40, CREDIT + "  \u00b7  the corrected map is layout 04", 7.5, "credit", colour=(90, 90, 90))])
    legend_classes(p, lyt, mfa, 7.85, 4.20, 2.2, 1.15,
                   ["29 Sep SVM over the ±60° segments"], names=False)
    out = os.path.join(OUTD, "05_svm_checks.png"); lyt.exportToPNG(out, resolution=150)
    print("   ", out)

    # ------------------------------------------------------------------ type-area sheets
    # 01-03 all framed the one map "Ius Chasma Type Area", so in Pro all three showed whichever
    # layer was switched on last (the classification). Give 01 and 02 a map each.
    print("6. type-area layouts get their own maps")
    ius = p.listMaps("Ius Chasma Type Area")[0]
    for lname, layer, mname in [("01_visible", "Viking MDIM 2.1 (visible)", "Ius Chasma — visible"),
                                ("02_night_ir", "THEMIS Night IR", "Ius Chasma — night IR")]:
        src = ius.listLayers(layer)[0]
        mm = next((x for x in p.listMaps() if x.name == mname), None) or p.createMap(mname, "MAP")
        for l in list(mm.listLayers()):
            mm.removeLayer(l)
        mm.spatialReference = ius.spatialReference
        nl = mm.addDataFromPath(src.dataSource); nl.name = layer; nl.visible = True
        lyt = p.listLayouts(lname)[0]
        mf = lyt.listElements("MAPFRAME_ELEMENT")[0]
        cam = (mf.camera.X, mf.camera.Y, mf.camera.scale)
        mf.map = mm
        mf.camera.X, mf.camera.Y, mf.camera.scale = cam
        print("   %s -> %s" % (lname, mname))
    for l in ius.listLayers():
        l.visible = l.name.startswith("Classification")      # 03 keeps the shared map

    p.save()
    print("saved. maps:", [x.name for x in p.listMaps()])
    print("layouts:", [x.name for x in p.listLayouts()])


if __name__ == "__main__":
    main()
