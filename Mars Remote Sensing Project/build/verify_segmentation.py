# -*- coding: utf-8 -*-
"""Did segmentation de-speckle, and which parameters? Measure, don't eyeball.

  boundary px    fraction with >=1 four-neighbour of a different class
                 (high = salt-and-pepper)
  mean run       horizontal pixels travelled before the class changes

One identical full-resolution window for every raster.
"""
import sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import numpy as np
from osgeo import gdal
gdal.UseExceptions()

TA = junction("TypeArea")
RASTERS = [
    ("per-pixel (no seg)",   "ius_isocluster_10.tif",      "-",      "-"),
    ("legacy on segments",   "ius_seg_isocluster_10.tif",  "20/20/5", "-"),
    ("object fine",          "ius_obj_fine.tif",           "20/20/5", "103 + 52 s"),
    ("object medium",        "ius_obj_medium.tif",         "14/14/30", "712 + 93 s"),
    ("object coarse",        "ius_obj_coarse.tif",         "9/9/80",  "817 + 87 s"),
]
X, Y, W, H = 2600, 900, 3200, 2200


def win(path):
    ds = gdal.Open(path)                      # hold it; chaining frees it early
    a = ds.GetRasterBand(1).ReadAsArray(X, Y, W, H).astype(np.int16)
    ds = None
    return a


def speckle(a):
    d = np.zeros(a.shape, bool)
    v = a[:-1, :] != a[1:, :]; d[:-1, :] |= v; d[1:, :] |= v
    h = a[:, :-1] != a[:, 1:]; d[:, :-1] |= h; d[:, 1:] |= h
    return d.mean()


def runs(a):
    return a.size / max(int((a[:, 1:] != a[:, :-1]).sum()), 1)


print("window %d x %d at (%d, %d) = %s px\n" % (W, H, X, Y, format(W * H, ",")))
print("%-20s %-9s %-12s %11s %9s %8s %9s"
      % ("method", "params", "cost", "boundary px", "mean run", "classes", "vs base"))
base_s = base_r = None
for lab, fn, par, cost in RASTERS:
    p = os.path.join(TA, fn)
    if not os.path.exists(p):
        print("%-20s %-9s  MISSING" % (lab, par)); continue
    a = win(p)
    s, r = speckle(a), runs(a)
    if base_s is None:
        base_s, base_r = s, r
        rel = "baseline"
    else:
        rel = "-%.1f%%" % (100 * (1 - s / base_s))
    print("%-20s %-9s %-12s %10.2f%% %9.1f %8d %9s"
          % (lab, par, cost, 100 * s, r, len(np.unique(a)), rel))
