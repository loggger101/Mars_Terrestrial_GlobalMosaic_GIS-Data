# -*- coding: utf-8 -*-
r"""Graticules on the sheets, and layout 10: the ±60° locator with both type areas (KB §44).

  Graticule_30deg       latitude/longitude lines every 30° over ±60°, labelled ("30°N", "120°E")
  Graticule_2deg        every 2° over the two type-area windows (Ius Chasma, Athabasca Valles)
  Type_Areas            the two windows of areas.py as polygons, with their names
  map "Mars ±60° — locator", layout 10_global60_locator: Viking colour, the analysis extent, the type
                        areas, and the volcanic units of the USGS geologic map (SIM 3292 groups v, ve,
                        vf) as the lava-flow reference layer (KB §43.3: lava flows are shown from the
                        map, not from the classifier)

CIMGraticule would not render (§22.3), so the graticule is plain data. Lines are densified every
0.5° so they bend correctly in the CM 180 projection. The graticule layers are added to the ±60°
and type-area maps here, AFTER the other builders (which wipe their maps): run this after
make_global60_maps / make_candidate_maps / make_mosaic_layout, then polish_layouts.py.

Every feature class it writes carries MappedBy = this script's name; one holding other rows is
never replaced. Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy
beside the real .aprx (§31.5).
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import areas
import grid60 as G
from layoutkit import text, poly_geom
from make_global60_maps import (outline, add, get_map, page, add_text, legend_classes, order,
                                extent_polygon, CREDIT, BKDIR, OUTD)

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
MARS = arcpy.SpatialReference(104905)
MARKER = "make_reference_maps.py"
LOCATOR, LNAME = "Mars ±60° — locator", "10_global60_locator"
G30, G2, TA = "Graticule_30deg", "Graticule_2deg", "Type_Areas"
MAPS_30 = ["Mars ±60° Analysis", "Mars ±60° — basins", LOCATOR]
MAPS_2 = ["Ius Chasma — digitising", "Athabasca Valles — digitising", "Ius Chasma — visible",
          "Ius Chasma — night IR", "Ius Chasma Type Area"]
GRAT_NAME = {G30: "Graticule 30°", G2: "Graticule 2°"}

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def replaceable(fc):
    if not arcpy.Exists(fc):
        return True
    with arcpy.da.SearchCursor(fc, ["MappedBy"]) as c:
        return all(r[0] == MARKER for r in c)


def new_fc(name, geom):
    fc = os.path.join(GDB, name)
    if not replaceable(fc):
        sys.exit("REFUSING: %s holds rows this script did not write" % fc)
    if arcpy.Exists(fc):
        arcpy.management.Delete(fc)
    arcpy.management.CreateFeatureclass(GDB, name, geom, spatial_reference=MARS)
    arcpy.management.AddField(fc, "Label", "TEXT", field_length=32)
    arcpy.management.AddField(fc, "MappedBy", "TEXT", field_length=40)
    return fc


def lat_label(v):
    return "0°" if v == 0 else "%d°%s" % (abs(v), "N" if v > 0 else "S")


def lon_label(v):
    v = (v + 180) % 360 - 180
    return "%d°E" % (v % 360)          # east longitude 0-360, as the project's figures use


def line(pts):
    return arcpy.Polyline(arcpy.Array([arcpy.Point(x, y) for x, y in pts]), MARS)


def densify(a, b, step=0.5):
    n = max(2, int(abs(b - a) / step) + 1)
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def build_graticules():
    fc = new_fc(G30, "POLYLINE")
    with arcpy.da.InsertCursor(fc, ["SHAPE@", "Label", "MappedBy"]) as cur:
        for la in (-60, -30, 0, 30, 60):
            cur.insertRow([line([(x, la) for x in densify(-180, 180)]), lat_label(la), MARKER])
        for lo in range(-180, 180, 30):
            cur.insertRow([line([(lo, y) for y in densify(-60, 60)]), lon_label(lo), MARKER])
    fc2 = new_fc(G2, "POLYLINE")
    with arcpy.da.InsertCursor(fc2, ["SHAPE@", "Label", "MappedBy"]) as cur:
        for key, a in areas.AREAS.items():
            lo0, lo1 = [((v + 180) % 360) - 180 for v in a["lon"]]
            la0, la1 = a["lat"]
            for la in range(la0 - la0 % 2, la1 + 1, 2):
                if la0 <= la <= la1:
                    cur.insertRow([line([(x, la) for x in densify(lo0, lo1, 0.1)]), lat_label(la), MARKER])
            for lo in range(int(lo0) - int(lo0) % 2, int(lo1) + 1, 2):
                if lo0 <= lo <= lo1:
                    cur.insertRow([line([(lo, y) for y in densify(la0, la1, 0.1)]), lon_label(lo), MARKER])
    ta = new_fc(TA, "POLYGON")
    with arcpy.da.InsertCursor(ta, ["SHAPE@", "Label", "MappedBy"]) as cur:
        for key, a in areas.AREAS.items():
            lo0, lo1 = [((v + 180) % 360) - 180 for v in a["lon"]]
            la0, la1 = a["lat"]
            ring = [(lo0, la0), (lo0, la1), (lo1, la1), (lo1, la0), (lo0, la0)]
            cur.insertRow([arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in ring]), MARS), a["name"], MARKER])
    for f in (fc, fc2, ta):
        print("  %-18s %s rows" % (os.path.basename(f), arcpy.management.GetCount(f)[0]))


def style_graticule(l, size):
    """Thin grey lines, small grey labels from the Label field."""
    sym = l.symbology
    sym.renderer.symbol.color = {"RGB": [255, 255, 255, 60]}
    sym.renderer.symbol.size = 0.4
    l.symbology = sym
    l.showLabels = True
    lc = l.listLabelClasses()[0]
    lc.expression = "$feature.Label"
    d = l.getDefinition("V3")
    for c in d.labelClasses:
        c.textSymbol.symbol.height = size
        fill = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidFill", "V3")
        col = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3"); col.values = [255, 255, 255, 100]
        fill.color = col
        c.textSymbol.symbol.symbol.symbolLayers = [fill]
        c.textSymbol.symbol.fontFamilyName = "Arial"
        c.textSymbol.symbol.fontStyleName = "Regular"
    l.setDefinition(d)


def add_graticule(p, map_name, fc, size):
    m = next((x for x in p.listMaps() if x.name == map_name), None)
    if m is None:
        print("   (no map %r)" % map_name); return
    for l in list(m.listLayers()):
        if l.name in GRAT_NAME.values():
            m.removeLayer(l)
    l = m.addDataFromPath(os.path.join(GDB, fc))
    l.name = GRAT_NAME[fc]
    style_graticule(l, size)
    top = m.listLayers()[0]
    if top.name != l.name:
        m.moveLayer(top, l, "BEFORE")
    print("   graticule -> %s" % map_name)


def build_locator(p):
    m = get_map(p, LOCATOR)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    ta = add(m, os.path.join(GDB, TA), "Type areas")
    outline(ta, (255, 255, 0), 2.2)
    ta.showLabels = True
    ta.listLabelClasses()[0].expression = "$feature.Label"
    d = ta.getDefinition("V3")                       # yellow bold labels, readable on the mosaic
    for c in d.labelClasses:
        c.textSymbol.symbol.height = 10
        c.textSymbol.symbol.fontFamilyName = "Arial"; c.textSymbol.symbol.fontStyleName = "Bold"
        fill = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidFill", "V3")
        col = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3"); col.values = [255, 255, 0, 100]
        fill.color = col
        c.textSymbol.symbol.symbol.symbolLayers = [fill]
        # beside the box, not inside it: at the locator's scale the boxes are smaller than their names
        # and the label sat on the outline (seen on the 2026-10-08 export). A dark halo keeps it legible.
        c.maplexLabelPlacementProperties.polygonPlacementMethod = "HorizontalAroundPolygon"
        halo_fill = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidFill", "V3")
        hcol = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3"); hcol.values = [0, 0, 0, 70]
        halo_fill.color = hcol
        halo = arcpy.cim.CreateCIMObjectFromClassName("CIMPolygonSymbol", "V3"); halo.symbolLayers = [halo_fill]
        c.textSymbol.symbol.haloSymbol = halo
        c.textSymbol.symbol.haloSize = 1.2
    ta.setDefinition(d)
    v = add(m, os.path.join(GDB, "Ref_SIM3292_GeologicUnits"), "Volcanic units, USGS SIM 3292 (lava-flow reference)",
            transparency=45)
    v.definitionQuery = "UnitGroup IN ('v', 've', 'vf')"
    sym = v.symbology
    sym.renderer.symbol.color = {"RGB": [230, 76, 0, 100]}
    sym.renderer.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}
    v.symbology = sym
    vk = add(m, os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif"), "Viking MDIM 2.1 colour (±60° stack, bands 1–3)")
    d = vk.getDefinition("V3")                       # no-data black, as on layout 08, not the page's white
    col = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3"); col.values = [0, 0, 0, 100]
    d.colorizer.noDataColor = col
    vk.setDefinition(d)
    order(m, [ta.name, ext.name, v.name, vk.name])
    m.clipLayers(extent_polygon())
    lyt = page(p, LNAME)
    fw = 10.1; fh = fw / 3.0
    mf = lyt.createMapFrame(poly_geom(0.45, 3.55, fw, fh), m, "frame")
    mf.camera.setExtent(extent_polygon().projectAs(m.spatialReference).extent)
    add_text(lyt, [
        text(0.45, 7.80, "Mars Global Mosaic — the analysis extent and the two type areas", 21, "title", bold=True),
        text(0.45, 7.46, "Ius Chasma (fluvial and collapse, 271–286°E) and Athabasca Valles (flood lava, 150–162°E) "
             "on the Viking colour mosaic, ±60°.", 10, "subtitle", colour=(70, 70, 70)),
        text(0.45, 1.30, "Orange: volcanic units of the USGS geologic map (Tanaka et al. 2014, groups v, ve, vf), the project's "
             "lava-flow reference.\nThe landform classifier cannot separate volcanic plains from other plains (KB §43.2–43.3), "
             "so lava flows are shown from the map.\nAthabasca Valles lies in unit lAv, Late Amazonian volcanic.", 9.2, "notes",
             colour=(40, 40, 40)),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))])
    legend_classes(p, lyt, mf, 7.25, 3.30, 3.3, 1.2, [ta.name, v.name, ext.name], names=False, cols=1)
    out = os.path.join(OUTD, LNAME + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    print("1. graticule and type-area feature classes")
    build_graticules()
    p = arcpy.mp.ArcGISProject(APRX)
    print("2. locator map and layout 10")
    build_locator(p)
    print("3. graticules on the maps")
    for name in MAPS_30:
        add_graticule(p, name, G30, 7)
    for name in MAPS_2:
        add_graticule(p, name, G2, 7)
    p.save()
    print("saved. layouts:", [x.name for x in p.listLayouts()])


if __name__ == "__main__":
    main()
