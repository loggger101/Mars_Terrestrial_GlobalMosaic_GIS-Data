# -*- coding: utf-8 -*-
r"""Majority (mode) filter on the ±60° landform classification (KB §32).

Per-pixel SVM output is speckled. A mode filter replaces each pixel by the commonest class in an
n x n window. Nodata (255) never votes and stays nodata. Ties keep the original class.

  python make_global60_landforms_clean.py --size 3      -> global60_landforms_svm_400m_mode3.tif
  python make_global60_landforms_clean.py --size 5      -> ..._mode5.tif

Whether it helps is decided by verify_global60_classification.py --raster <output> on the held-out
polygons, not by how it looks. Streams 1024-row strips with an n//2 halo; longitude wraps.
"""
import os, sys, time
import numpy as np
from osgeo import gdal
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_global60_classification import OUT as SRC

gdal.UseExceptions()
N = int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else 3
DST = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
       else SRC.replace(".tif", "_mode%d.tif" % N))
STRIP, H = 1024, N // 2


def class_values(band):
    """The pixel values that are classes, from the attribute table: 1..4 since the recode (KB §36).
    Read, not assumed, so the filter is right for either encoding."""
    rat = band.GetDefaultRAT()
    col = next(i for i in range(rat.GetColumnCount()) if rat.GetNameOfCol(i).lower() == "value")
    return np.array(sorted(rat.GetValueAsInt(r, col) for r in range(rat.GetRowCount())), np.uint8)


def main():
    t0 = time.time()
    src = gdal.Open(SRC)
    b = src.GetRasterBand(1)
    W, Ht = src.RasterXSize, src.RasterYSize
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(DST, W, Ht, 1, gdal.GDT_Byte,
                    options=["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"])
    ds.SetGeoTransform(src.GetGeoTransform()); ds.SetProjection(src.GetProjection())
    ob = ds.GetRasterBand(1); ob.SetNoDataValue(255)
    ob.SetRasterColorTable(b.GetRasterColorTable())
    codes = class_values(b)
    slot = np.zeros(256, np.int64)                             # pixel value -> its row in votes
    slot[codes] = np.arange(len(codes))
    changed = valid = 0
    for y0 in range(0, Ht, STRIP):
        h = min(STRIP, Ht - y0)
        a0, a1 = max(0, y0 - H), min(Ht, y0 + h + H)
        a = b.ReadAsArray(0, a0, W, a1 - a0)
        votes = np.stack([ndimage.uniform_filter((a == k).astype(np.float32), size=N, mode="wrap")
                          for k in codes])
        best = codes[votes.argmax(0)]
        top = votes.max(0)
        mine = np.take_along_axis(votes, slot[a][None], 0)[0]
        out = np.where(mine >= top, a, best)                 # a tie keeps the original class
        out[a == 255] = 255
        out = out[y0 - a0:y0 - a0 + h]
        orig = a[y0 - a0:y0 - a0 + h]
        v = orig != 255
        changed += int((out[v] != orig[v]).sum()); valid += int(v.sum())
        ob.WriteArray(out, 0, y0)
    ds.FlushCache()
    ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64]); ds = None
    import arcpy
    arcpy.management.DefineProjection(DST, arcpy.Describe(SRC).spatialReference)
    arcpy.management.BuildRasterAttributeTable(DST, "Overwrite")
    rat = {}
    with arcpy.da.SearchCursor(SRC, ["Value", "Classvalue", "Class_name", "Red", "Green", "Blue"]) as c:
        for r in c:
            rat[int(r[0])] = r[1:]
    for fld, typ in [("Classvalue", "SHORT"), ("Class_name", "TEXT"), ("Red", "SHORT"),
                     ("Green", "SHORT"), ("Blue", "SHORT")]:
        arcpy.management.AddField(DST, fld, typ)
    with arcpy.da.UpdateCursor(DST, ["Value", "Classvalue", "Class_name", "Red", "Green", "Blue"]) as c:
        for r in c:
            c.updateRow([r[0]] + list(rat[int(r[0])]))
    arcpy.management.CalculateStatistics(DST)
    print("mode %dx%d: %.2f%% of valid pixels changed class -> %s  (%.0f s)"
          % (N, N, 100.0 * changed / valid, DST, time.time() - t0))


if __name__ == "__main__":
    main()
