# -*- coding: utf-8 -*-
"""Pull raster properties/statistics for the derived gdb rasters from the item XML."""
import re
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction

path = on_drive(r"Mars Project\Mars Project.gdb\a00000004.gdbtable")
txt = open(path, "rb").read().decode("latin-1")

names = ["Slope_Mars_H1", "Slope_Mars_M1", "Slope_Mars_V1", "Surface_Mars1",
         "HillSha_Mars1", "Slope_Mars_V1_CompositeBands"]

for n in names:
    # window around the dataset's catalog path entry
    i = txt.find("<CatalogPath>\\%s</CatalogPath>" % n)
    if i < 0:
        print("== %-30s NOT FOUND" % n)
        continue
    seg = txt[i:i + 60000]
    print("=" * 72)
    print("==", n)
    for tag in ("rasterDataset", "compressionType", "pixelType", "hasColormap",
                "bandCount", "format", "cellSizeX", "cellSizeY", "numberRows",
                "numberColumns", "noDataValue", "min", "max", "mean",
                "standardDeviation", "isInteger"):
        for m in re.findall(r"<%s[^>]*>([^<]{1,60})</%s>" % (tag, tag), seg)[:3]:
            print("   %-20s %s" % (tag + ":", m))
    for m in re.findall(r"(rowCount|columnCount|XCellSize|YCellSize)\D{0,4}([0-9.eE+-]{1,24})", seg)[:8]:
        print("   attr %-16s %s" % m)
    # projection
    pm = re.search(r"<WKT>(PROJCS|GEOGCS)\[&quot;([^&]{1,50})&quot;", seg)
    if pm:
        print("   %-20s %s (%s)" % ("CRS:", pm.group(2), pm.group(1)))
    # extent
    em = re.search(r"westBL[^>]*>([-0-9.]+).{0,400}?eastBL[^>]*>([-0-9.]+)", seg, re.S)
    if em:
        print("   %-20s %s .. %s" % ("lon extent:", em.group(1), em.group(2)))
    em = re.search(r"southBL[^>]*>([-0-9.]+).{0,400}?northBL[^>]*>([-0-9.]+)", seg, re.S)
    if em:
        print("   %-20s %s .. %s" % ("lat extent:", em.group(1), em.group(2)))
