# -*- coding: utf-8 -*-
r"""Recode a classified raster so each pixel holds its class code (KB §36). ArcGIS Python.

ClassifyRaster writes pixel values 0..n-1 and keeps the class codes in the attribute table's
Classvalue column, so on global60_landforms_svm_400m.tif pixel 0 was Crater (code 1) and 3 was
Normal Ground (code 4). Anyone reading raw pixels without the table got every class off by one.
recode() rewrites the raster with pixel = Classvalue, taken from the raster's own table rather
than assumed, and carries across what the old file had: colours, NoData, overviews, the
projection, statistics and a table whose Value now equals its Classvalue.

NoData is kept as the source declares it (255 on the ±60° maps, 15 on two type-area maps). A
source with no NoData value but a mask (the two GUI gdb maps, where masked pixels read as 0, i.e. as
Crater) gets NoData 255 on the masked pixels. A source may be a .tif or a raster in a file gdb;
the output is always a GeoTIFF (copy it into a gdb with arcpy afterwards).
"""
import os
import numpy as np
from osgeo import gdal
import arcpy

gdal.UseExceptions()
CO = ["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"]
STRIP = 2048


def gdal_path(path):
    """A raster inside a file gdb is opened by GDAL as OpenFileGDB:<gdb>:<name>."""
    parent = os.path.dirname(path)
    return f"OpenFileGDB:{parent}:{os.path.basename(path)}" if parent.lower().endswith(".gdb") else path


def rat(path):
    """{pixel value: (Classvalue, Class_name, (R, G, B) or None)} from the attribute table."""
    names = {f.name.lower(): f.name for f in arcpy.ListFields(path)}
    rgb = [names[k] for k in ("red", "green", "blue") if k in names]
    fields = ["Value", names["classvalue"], names.get("class_name", names["classvalue"])] + (rgb if len(rgb) == 3 else [])
    out = {}
    with arcpy.da.SearchCursor(path, fields) as c:
        for r in c:
            out[int(r[0])] = (int(r[1]), str(r[2]), tuple(int(x) for x in r[3:6]) if len(r) == 6 else None)
    return out


def recode(src, dst):
    """Write dst (GeoTIFF) = src with every pixel replaced by its Classvalue.
    Returns (h_src, h_dst, table, nodata): class histograms over valid pixels plus a NoData count."""
    table = rat(src)
    s = gdal.Open(gdal_path(src))
    sb = s.GetRasterBand(1)
    nd = sb.GetNoDataValue()
    use_mask = nd is None
    nd = 255 if nd is None else int(nd)
    codes = [cv for cv, _, _ in table.values()]
    assert nd not in codes and all(0 <= cv <= 255 for cv in codes), f"NoData {nd} collides with a code {codes}"
    lut = np.arange(256, dtype=np.uint8)
    for v, (cv, _, _) in table.items():
        lut[v] = cv
    d = gdal.GetDriverByName("GTiff").Create(dst, s.RasterXSize, s.RasterYSize, 1, gdal.GDT_Byte, options=CO)
    d.SetGeoTransform(s.GetGeoTransform())
    d.SetProjection(s.GetProjection())
    db = d.GetRasterBand(1)
    db.SetNoDataValue(nd)
    sct = sb.GetRasterColorTable()
    if sct is not None or all(rgb for _, _, rgb in table.values()):
        ct = gdal.ColorTable()
        for v, (cv, _, rgb) in table.items():
            ct.SetColorEntry(cv, (sct.GetColorEntry(v)[:3] if sct is not None else rgb) + (255,))
        db.SetRasterColorTable(ct)
    h_src = np.zeros(257, np.int64)            # index 256 counts NoData / masked pixels
    h_dst = np.zeros(257, np.int64)
    for y0 in range(0, s.RasterYSize, STRIP):
        h = min(STRIP, s.RasterYSize - y0)
        a = sb.ReadAsArray(0, y0, s.RasterXSize, h)
        invalid = (sb.GetMaskBand().ReadAsArray(0, y0, s.RasterXSize, h) == 0) if use_mask else (a == nd)
        out = np.where(invalid, nd, lut[a]).astype(np.uint8)
        # int16 first: numpy 2 keeps uint8 for where(mask, 256, uint8) and 256 wraps to 0 (Crater)
        h_src += np.bincount(np.where(invalid, 256, a.astype(np.int16)).ravel(), minlength=257)
        h_dst += np.bincount(np.where(invalid, 256, out.astype(np.int16)).ravel(), minlength=257)
        db.WriteArray(out, 0, y0)
    d.FlushCache()
    d.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
    d = s = None
    arcpy.management.DefineProjection(dst, arcpy.Describe(src).spatialReference)
    arcpy.management.BuildRasterAttributeTable(dst, "Overwrite")
    for fld, typ in [("Classvalue", "SHORT"), ("Class_name", "TEXT"), ("Red", "SHORT"),
                     ("Green", "SHORT"), ("Blue", "SHORT")]:
        arcpy.management.AddField(dst, fld, typ)
    by_code = {cv: (n, rgb) for cv, n, rgb in table.values()}
    with arcpy.da.UpdateCursor(dst, ["Value", "Classvalue", "Class_name", "Red", "Green", "Blue"]) as c:
        for r in c:
            n, rgb = by_code[int(r[0])]
            c.updateRow([r[0], r[0], n] + (list(rgb) if rgb else [None, None, None]))
    arcpy.management.CalculateStatistics(dst)
    return h_src, h_dst, table, nd


def check(src, dst, h_src, h_dst, table, nd):
    """Every class keeps its pixel count under its new value; NoData and the grid are unchanged."""
    problems = []
    for v, (cv, n, _) in table.items():
        if h_src[v] != h_dst[cv]:
            problems.append(f"{n}: {h_src[v]:,} px at {v} became {h_dst[cv]:,} at {cv}")
    if h_src[256] != h_dst[256]:
        problems.append(f"NoData {h_src[256]:,} -> {h_dst[256]:,}")
    a, b = gdal.Open(gdal_path(src)), gdal.Open(gdal_path(dst))
    if a.GetGeoTransform() != b.GetGeoTransform() or (a.RasterXSize, a.RasterYSize) != (b.RasterXSize, b.RasterYSize):
        problems.append("grid changed")
    if b.GetRasterBand(1).GetNoDataValue() != nd:
        problems.append(f"NoData value is {b.GetRasterBand(1).GetNoDataValue()}, expected {nd}")
    a = b = None
    names = {cv: n for cv, n, _ in table.values()}
    for v, cv, n in arcpy.da.SearchCursor(dst, ["Value", "Classvalue", "Class_name"]):
        if v != cv or names.get(cv) != n:
            problems.append(f"attribute table row {v} reads Classvalue {cv} '{n}'")
    return problems
