# -*- coding: utf-8 -*-
"""CIM helpers for layouts, extracted verbatim from make_typearea_layouts.py by ast.

arcpy.mp has no createTextElement in Pro 3.x; text is built through the CIM."""
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
