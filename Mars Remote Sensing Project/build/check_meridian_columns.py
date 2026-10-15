# -*- coding: utf-8 -*-
r"""Do the G200 columns around 180 deg (53346, x -200..0) look like their neighbours? Read-only.

Written 2026-10-14 for the 180 deg stripe (KB §54). For each raster and each column c in
53330..53362, roughness = mean over rows of |v[c] - (v[c-1] + v[c+1]) / 2| (valid pixels only),
reported as a ratio to the median over the window's columns. Also nodata per column.
Rule, written before the run after the patch: every column 53340-53355 has ratio <= 2.0 and no
excess nodata (a column's count within 2x the window median + 50). Before the patch the slope
columns 53345-53348 were 13-16x and relief 53342-53351 2-9x (the author's check), so the rule
can fail; the --backup switch runs it on the pre-patch pixels saved in mars_scratch to show that.
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from osgeo import gdal
gdal.UseExceptions()

GDIR = r"F:\Mars Project\Global60"
BK = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mars_scratch", "meridian_backup_20261014")
X0, X1 = 53330, 53362
CHECK = range(53340, 53356)
SETS = [("dem", "global60_dem.tif", 1, -32768), ("slope", "global60_slope_deg.tif", 1, -9999),
        ("hillshade", "global60_hillshade.tif", 1, 0), ("stack b6 slope", "global60_svm_stack_200m.tif", 6, 0),
        ("stack b7 relief", "global60_svm_stack_200m.tif", 7, 0), ("stack b4 night", "global60_svm_stack_200m.tif", 4, 0)]


def load(fn, band, backup):
    if backup:
        a = np.load(os.path.join(BK, fn.replace(".tif", "_cols%d-%d.npy" % (X0, X1))))
        return a[band - 1] if a.ndim == 3 else a
    d = gdal.Open(os.path.join(GDIR, fn))
    return d.GetRasterBand(band).ReadAsArray(X0, 0, X1 - X0 + 1, d.RasterYSize)


def main():
    backup = "--backup" in sys.argv
    print("pre-patch pixels (backup)" if backup else "current files")
    ok_all = True
    for label, fn, band, nd in SETS:
        a = load(fn, band, backup).astype(np.float64)
        v = a != nd
        a[~v] = np.nan
        sec = np.abs(a[:, 1:-1] - 0.5 * (a[:, :-2] + a[:, 2:]))
        rough = np.nanmean(sec, axis=0)
        cols = np.arange(X0 + 1, X1)
        ratio = rough / np.nanmedian(rough)
        nod = (~v).sum(axis=0)[1:-1]
        nmed = np.median(nod)
        bad = [c for c, r, n in zip(cols, ratio, nod) if c in CHECK and (r > 2.0 or n > 2 * nmed + 50)]
        ok_all &= not bad
        print("%-16s max ratio in 53340-53355 %5.2f (col %d)   nodata max %d (median %d)   %s"
              % (label, max(r for c, r in zip(cols, ratio) if c in CHECK),
                 max((r, c) for c, r in zip(cols, ratio) if c in CHECK)[1],
                 max(n for c, n in zip(cols, nod) if c in CHECK), nmed, "FAIL %s" % bad if bad else "ok"))
        if "-v" in sys.argv:
            print("   ", " ".join("%d:%.1f" % (c % 1000, r) for c, r in zip(cols, ratio)))
    print("RESULT", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
