# -*- coding: utf-8 -*-
"""CIM helpers for layouts, extracted verbatim from make_typearea_layouts.py by ast.

arcpy.mp has no createTextElement in Pro 3.x; text is built through the CIM.
rect() and cell_text(), at the end, were added later for the table sheets (13, 14)."""
import arcpy

C     = arcpy.cim.CreateCIMObjectFromClassName


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


# ---- added 2026-10-08 for the table sheets 13 and 14 (not part of the verbatim extract above)

def rect(x, y, w, h, name, fill=(255, 255, 255), stroke=None, stroke_w=0.5):
    """A filled rectangle on the page (inches): a table cell or a swatch."""
    g = C("CIMPolygonGraphic", "V3")
    g.polygon = poly_geom(x, y, w, h)
    layers = []
    if stroke is not None:
        s = C("CIMSolidStroke", "V3"); s.color = rgb(*stroke); s.width = stroke_w
        layers.append(s)
    f = C("CIMSolidFill", "V3"); f.color = rgb(*fill)
    layers.append(f)
    sym = C("CIMPolygonSymbol", "V3"); sym.symbolLayers = layers
    ref = C("CIMSymbolReference", "V3"); ref.symbol = sym
    g.symbol = ref
    el = C("CIMGraphicElement", "V3")
    el.graphic = g; el.name = name; el.visible = True; el.anchor = "BottomLeftCorner"
    return el


def cell_text(x, y, w, h, s, size, name, bold=False, colour=(0, 0, 0), align="Center"):
    """Text centred vertically in the box (x, y, w, h); align Left / Center / Right."""
    tx = {"Left": x + 0.06, "Center": x + w / 2.0, "Right": x + w - 0.06}[align]
    el = text(tx, y + h / 2.0, s, size, name, bold, colour)
    sym = el.graphic.symbol.symbol
    sym.horizontalAlignment = align
    sym.verticalAlignment = "Center"
    return el
