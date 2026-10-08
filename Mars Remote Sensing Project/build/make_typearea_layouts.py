# -*- coding: utf-8 -*-
"""Task 13: real map layouts for the Ius Chasma type area.

The project had ZERO layouts, so every figure so far was matplotlib off the raw
rasters - no legend, no scale bar, no graticule, none of the cartography a
remote-sensing deliverable is marked on. These are built in ArcGIS from the
harmonised stack.

arcpy.mp has no createTextElement in Pro 3.x; text is built through the CIM.
Run polish_layouts.py afterwards: legend fonts and headings are fixed there (KB §33).
"""
import os, time, shutil, arcpy
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction

C     = arcpy.cim.CreateCIMObjectFromClassName
APRX  = on_drive(r"Mars Project\Mars Project.aprx")
BKDIR = on_drive(r"Mars Project\.backups")
TA    = on_drive(r"Mars Project\TypeArea")
OUTD  = os.path.join(TA, "layouts")
MAPNM = "Ius Chasma Type Area"
PAGE_W, PAGE_H = 11.0, 8.5
DATA_AR = 8891.0 / 4150.0                    # the stack is 2.14:1 - match it or get white bands
FR_W = 10.10
FRAME = (0.45, 2.42, FR_W, FR_W / DATA_AR)   # x, y, w, h inches

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), \
    "close ArcGIS Pro first"
os.makedirs(OUTD, exist_ok=True); os.makedirs(BKDIR, exist_ok=True)
shutil.copy2(APRX, os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S")))

def rgb(r, g, b):
    c = C("CIMRGBColor", "V3"); c.values = [r, g, b, 100]; return c

def text(x, y, s, size, name, bold=False, colour=(0, 0, 0)):
    g = C("CIMTextGraphic", "V3"); g.text = s
    sym = C("CIMTextSymbol", "V3")
    sym.fontFamilyName = "Arial"      # Aptos is not installed on the laptop (KB §33)
    sym.fontStyleName  = "Bold" if bold else "Regular"
    sym.height = size
    sym.horizontalAlignment = "Left"; sym.verticalAlignment = "Bottom"
    fill = C("CIMSolidFill", "V3"); fill.color = rgb(*colour)
    poly = C("CIMPolygonSymbol", "V3"); poly.symbolLayers = [fill]
    sym.symbol = poly
    ref = C("CIMSymbolReference", "V3"); ref.symbol = sym
    g.symbol = ref; g.shape = arcpy.Point(x, y)
    el = C("CIMGraphicElement", "V3")
    el.graphic = g; el.name = name; el.visible = True; el.anchor = "BottomLeftCorner"
    return el

def poly_geom(x, y, w, h):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x, y), arcpy.Point(x, y+h),
                                      arcpy.Point(x+w, y+h), arcpy.Point(x+w, y)]))

# ---------------------------------------------------------------------------
# NO GRATICULE. Three attempts at building CIMGraticule through the CIM failed
# to render anything: the object accepts gridLines with orientation and a
# CIMGridPattern (interval/start/stop) without error, but still draws nothing -
# it also wants mapGridEdges and label components that are not exposed as
# creatable CIM classes here (CIMGraticuleLine and CIMSimpleMapGridEdge both
# raise LookupError). Rather than leave an invisible dead element on every
# sheet, there is none. Add one in the Pro GUI in seconds if wanted; the
# coordinate range is stated in the credit block meanwhile.
# ---------------------------------------------------------------------------


p = arcpy.mp.ArcGISProject(APRX)

# ------------------------------------------------------------------- map ---
m = next((x for x in p.listMaps() if x.name == MAPNM), None)
if m is None:
    m = p.createMap(MAPNM, "Map"); print("created map:", MAPNM)
for l in list(m.listLayers()):
    m.removeLayer(l)
LAYERS = [("ius_isocluster_10.tif", "Classification, 10 classes"),
          ("ius_slope_deg.tif",     "Slope (degrees)"),
          ("ius_hillshade.tif",     "Hillshade 225\u00b0/45\u00b0"),
          ("ius_night.tif",         "THEMIS Night IR"),
          ("ius_day.tif",           "THEMIS Day IR"),
          ("ius_viking.tif",        "Viking MDIM 2.1 (visible)")]
for fn, label in LAYERS:
    lyr = m.addDataFromPath(os.path.join(TA, fn)); lyr.name = label; lyr.visible = False
m.spatialReference = arcpy.Raster(os.path.join(TA, "ius_day.tif")).spatialReference
print("layers:", [l.name for l in m.listLayers()])

# Default Iso Cluster colours put class 2 and class 10 both at pure red -
# indistinguishable on the map AND in the legend. A qualitative 10-colour set,
# ordered so the plateau/dust classes read warm and the wall/bedrock ones cool.
CLASS_COLOURS = [(142, 202, 230), (33, 158, 188), (2, 48, 71), (255, 183, 3),
                 (251, 133, 0), (214, 40, 40), (114, 9, 183), (67, 97, 238),
                 (67, 170, 139), (181, 23, 158)]


def recolour_classes(layer):
    """Give the classification raster a distinguishable unique-value ramp."""
    try:
        d = layer.getDefinition("V3")
        col = d.colorizer
        groups = getattr(col, "groups", None)
        if not groups:
            print("   recolour skipped: colorizer has no groups (%s)" % type(col).__name__)
            return False
        n = 0
        for grp in groups:
            for i, cls in enumerate(grp.classes):
                r, g, b = CLASS_COLOURS[i % len(CLASS_COLOURS)]
                cls.color = rgb(r, g, b)
                n += 1
        layer.setDefinition(d)
        print("   recoloured %d classes" % n)
        return True
    except Exception as e:
        print("   recolour skipped: %s" % str(e)[:70])
        return False


CREDIT = ("Logan Edwards  \u00b7  OCN 4704 Remote Sensing  \u00b7  Mars Global Mosaic\n"
          "Equidistant Cylindrical, central meridian 180\u00b0, Mars 2000 sphere "
          "(R = 3 396 190 m)  \u00b7  100 m/pixel  \u00b7  271\u2013286\u00b0E, 13\u20136\u00b0S")
SHEETS = [
 ("01_visible",       "Viking MDIM 2.1 (visible)",
  "Ius Chasma type area \u2014 visible mosaic",
  "Viking MDIM 2.1, 232 m resampled to 100 m. Albedo only: the chasma reads as shadow.",
  False),
 ("02_night_ir",      "THEMIS Night IR",
  "Ius Chasma type area \u2014 night-time thermal infrared",
  "THEMIS Night IR v14, 100 m. Bright = warmer at night than its surroundings, as rock and "
  "coarse debris are.\nLocal contrast, not calibrated thermal inertia (KB §28.10).",
  False),
 ("03_classification","Classification, 10 classes",
  "Ius Chasma type area \u2014 unsupervised classification",
  "Iso Cluster, 10 classes, five-band stack (Viking RGB + THEMIS day + night IR).",
  True),
]

for name, visible, title, subtitle, legend in SHEETS:
    lyt = next((x for x in p.listLayouts() if x.name == name), None)
    if lyt is None:
        lyt = p.createLayout(PAGE_W, PAGE_H, "INCH"); lyt.name = name
    for e in lyt.listElements():
        lyt.deleteElement(e)
    mf = lyt.createMapFrame(poly_geom(*FRAME), m, "frame")
    for l in m.listLayers():
        l.visible = (l.name == visible)
    if visible.startswith("Classification"):
        recolour_classes(m.listLayers(visible)[0])
    mf.camera.setExtent(mf.getLayerExtent(m.listLayers(visible)[0], False, True))

    cim = lyt.getDefinition("V3")
    extra = [text(FRAME[0], 7.85, title, 21, "title", bold=True),
             text(FRAME[0], 7.50, subtitle, 10.5, "subtitle", colour=(70, 70, 70)),
             text(FRAME[0], 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
    cim.elements = list(cim.elements) + extra
    lyt.setDefinition(cim)

    # createMapSurroundElement wants a StyleItem OBJECT, not its name
    # createMapSurroundElement wants a StyleItem OBJECT, not its name.
    # Scale bar sits BELOW the frame at the left; the arrow at the right, well
    # clear of it - at the page edge the bar's "Kilometers" label is clipped.
    surrounds = [("SCALE_BAR",   0.50, 1.72, "Double Alternating Scale Bar 1 Metric", "sbar"),
                 ("NORTH_ARROW", 9.95, 1.52, "ArcGIS North 1", "narrow")]
    if legend:
        surrounds.append(("LEGEND", 4.30, 2.20, "Legend 1", "legend"))
    for kind, x, y, style, nm in surrounds:
        try:
            items = p.listStyleItems("ArcGIS 2D", kind)
            item = next((i for i in items if i.name == style), items[0])
            el = lyt.createMapSurroundElement(arcpy.Point(x, y), kind, mf, item, nm)
            el.name = nm
            if kind == "SCALE_BAR":
                el.elementWidth = 3.1
            if kind == "LEGEND":
                report_overflow = True
                # 10 classes in one column overflows the page and collides with
                # the credit; three columns fit the band under the frame
                el.columnCount = 4
                el.showTitle = False
                el.fittingStrategy = "AdjustColumns"
                el.elementWidth = 5.35
                el.elementHeight = 1.70
                d = el.getDefinition("V3")
                d.showTitle = False
                for it in getattr(d, "items", []) or []:
                    for att in ("showHeading", "showLayerName", "showGroupLayerName"):
                        if hasattr(it, att):
                            setattr(it, att, False)
                el.setDefinition(d)
                el.setAnchor("TOP_LEFT_CORNER")
                el.elementPositionX = 4.15
                el.elementPositionY = 2.30
        except Exception as e:
            print("   %-12s skipped: %s" % (kind, str(e)[:70]))

    for e in lyt.listElements("LEGEND_ELEMENT"):
        if e.isOverflowing:
            print("   legend OVERFLOWING - enlarge it")
    out = os.path.join(OUTD, name + ".png")
    t0 = time.time(); lyt.exportToPNG(out, resolution=150)
    print("%-18s %5.1fs  %5.1f MB  elements: %s" % (name, time.time()-t0,
          os.path.getsize(out)/1048576, [e.name for e in lyt.listElements()]))

p.save()
print("saved. layouts:", [l.name for l in p.listLayouts()])
