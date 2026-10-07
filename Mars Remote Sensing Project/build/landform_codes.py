# -*- coding: utf-8 -*-
r"""Recode a classified raster so each pixel holds its class code (KB §36). ArcGIS Python.

ClassifyRaster writes pixel values 0..n-1 and keeps the class codes in the attribute table's
Classvalue column, so on global60_landforms_svm_400m.tif pixel 0 was Crater (code 1) and 3 was
Normal Ground (code 4). Anyone reading raw pixels without the table got every class off by one.
recode() rewrites the raster with pixel = Classvalue, taken from the raster's own table rather
than assumed, and carries across what the old file had: colours, NoData 255, overviews, the
projection, statistics and a table whose Value now equals its Classvalue.
"""
import os
import numpy as np
from osgeo import gdal
import arcpy

gdal.UseExceptions()
CO = ["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"]
STRIP = 2048


def rat(path):
    """{pixel value: (Classvalue, Class_name, (R, G, B))} from the attribute table."""
    out = {}
    with arcpy.da.SearchCursor(path, ["Value", "Classvalue", "Class_name", "Red", "Green", "Blue"]) as c:
        for v, cv, n, r, g, b in c:
            out[int(v)] = (int(cv), n, (int(r), int(g), int(b)))
    return out


def recode(src, dst):
    """Write dst = src with every pixel replaced by its Classvalue. Returns (src, dst) histograms."""
    table = rat(src)
    lut = np.arange(256, dtype=np.uint8)
    for v, (cv, _, _) in table.items():
        assert 0 <= cv < 255, f"class code {cv} does not fit beside NoData 255"
        lut[v] = cv
    s = gdal.Open(src)
    sb = s.GetRasterBand(1)
    assert sb.GetNoDataValue() == 255, "expected NoData 255"
    d = gdal.GetDriverByName("GTiff").Create(dst, s.RasterXSize, s.RasterYSize, 1, gdal.GDT_Byte, options=CO)
    d.SetGeoTransform(s.GetGeoTransform())
    d.SetProjection(s.GetProjection())
    db = d.GetRasterBand(1)
    db.SetNoDataValue(255)
    ct = gdal.ColorTable()
    for v, (cv, _, rgb) in table.items():
        ct.SetColorEntry(cv, rgb + (255,))
    db.SetRasterColorTable(ct)
    h_src = np.zeros(256, np.int64)
    h_dst = np.zeros(256, np.int64)
    for y0 in range(0, s.RasterYSize, STRIP):
        a = sb.ReadAsArray(0, y0, s.RasterXSize, min(STRIP, s.RasterYSize - y0))
        out = lut[a]
        h_src += np.bincount(a.ravel(), minlength=256)
        h_dst += np.bincount(out.ravel(), minlength=256)
        db.WriteArray(out, 0, y0)
    d.FlushCache()
    d.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
    d = s = None
    arcpy.management.DefineProjection(dst, arcpy.Describe(src).spatialReference)
    arcpy.management.BuildRasterAttributeTable(dst, "Overwrite")
    for fld, typ in [("Classvalue", "SHORT"), ("Class_name", "TEXT"), ("Red", "SHORT"),
                     ("Green", "SHORT"), ("Blue", "SHORT")]:
        arcpy.management.AddField(dst, fld, typ)
    by_code = {cv: (cv, n, rgb) for cv, n, rgb in table.values()}
    with arcpy.da.UpdateCursor(dst, ["Value", "Classvalue", "Class_name", "Red", "Green", "Blue"]) as c:
        for r in c:
            cv, n, rgb = by_code[int(r[0])]
            c.updateRow([r[0], cv, n] + list(rgb))
    arcpy.management.CalculateStatistics(dst)
    return h_src, h_dst, table


def check(src, dst, h_src, h_dst, table):
    """Every class keeps its pixel count under its new value; NoData and the grid are unchanged."""
    problems = []
    for v, (cv, n, _) in table.items():
        if h_src[v] != h_dst[cv]:
            problems.append(f"{n}: {h_src[v]:,} px at {v} became {h_dst[cv]:,} at {cv}")
    if h_src[255] != h_dst[255]:
        problems.append(f"NoData {h_src[255]:,} -> {h_dst[255]:,}")
    a, b = gdal.Open(src), gdal.Open(dst)
    if a.GetGeoTransform() != b.GetGeoTransform() or (a.RasterXSize, a.RasterYSize) != (b.RasterXSize, b.RasterYSize):
        problems.append("grid changed")
    a = b = None
    for v, cv, n in arcpy.da.SearchCursor(dst, ["Value", "Classvalue", "Class_name"]):
        if v != cv or table_name(table, cv) != n:
            problems.append(f"attribute table row {v} reads Classvalue {cv} '{n}'")
    return problems


def table_name(table, cv):
    return next(n for c, n, _ in table.values() if c == cv)
