# -*- coding: utf-8 -*-
r"""Do the X2 fine-pass candidates show an artefact along x = 0 (180°)? Read-only; ArcGIS Python.

Written 2026-10-14 for the 180° column of the DEM (KB §54). Within 60 km of x = 0:
  D  closed-depression centres per 2 km column band; the two bands at x = 0 against the others.
  E  channel-segment end points per 400 m column band; the two bands at x = 0 against the others.
  X  polylines whose extent straddles x = L, for L = 0 and ±2, ±20, ±40 km.
Rule, written before the post-fix run: D in the six bands within ±6 km (the pre-fix deficit's
width) and E in the two bands at x = 0 within mean ± 3 sd of the other bands (|x| > 10 km for D, > 4 km for E);
X at 0 not below 0.75 x the smallest crossing count of the six other lines. The pre-fix classes
(7 and 10 depressions against 50.0 ± 8.8; 200 / 198 end points against 41.1 ± 8.5; 28 crossings
against 176-215) fail it, so the rule can fail.

  python check_x2_meridian.py [gdb]      default: the project gdb
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import numpy as np
import arcpy

W = 60000.0
LINES = [-40000, -20000, -2000, 0, 2000, 20000, 40000]


def main():
    argv = sys.argv[1:]
    if "--json" in argv:
        k = argv.index("--json"); argv = argv[:k] + argv[k + 2:]
    args = [a for a in argv if not a.startswith("--")]
    gdb = args[0] if args else GDB
    fc_c = os.path.join(gdb, "Landform_CraterCandidates_auto_60")
    fc_l = os.path.join(gdb, "Landform_ChannelCandidates_auto_60")
    print(gdb)
    sr = arcpy.Describe(fc_c).spatialReference
    box = arcpy.Polygon(arcpy.Array([arcpy.Point(-W, -4e6), arcpy.Point(W, -4e6),
                                     arcpy.Point(W, 4e6), arcpy.Point(-W, 4e6)]), sr)
    cx = np.array([r[0] for r in arcpy.da.SearchCursor(fc_c, ["SHAPE@X"], spatial_filter=box)])
    h, _ = np.histogram(cx, np.arange(-W, W + 1, 2000.0))
    m = len(h) // 2
    ref = np.r_[h[:m - 5], h[m + 5:]]
    okD = all(abs(v - ref.mean()) <= 3 * ref.std() for v in h[m - 3:m + 3])
    print("D  depressions per 2 km band, x = -10..+10 km:", h[m - 5:m + 5].tolist())
    print("   x = -6..+6 km: %s   others %.1f ± %.1f   %s" % (h[m - 3:m + 3].tolist(), ref.mean(), ref.std(), "ok" if okD else "FAIL"))

    ends, cross, n = [], {L: 0 for L in LINES}, 0
    for (g,) in arcpy.da.SearchCursor(fc_l, ["SHAPE@"], spatial_filter=box):
        n += 1
        ends.append(g.firstPoint.X); ends.append(g.lastPoint.X)
        e = g.extent
        for L in LINES:
            if e.XMin < L < e.XMax:
                cross[L] += 1
    hend, _ = np.histogram(np.array(ends), np.arange(-W, W + 1, 400.0))
    k = len(hend) // 2
    refe = np.r_[hend[:k - 10], hend[k + 10:]]
    okE = all(abs(v - refe.mean()) <= 3 * refe.std() for v in (hend[k - 1], hend[k]))
    print("E  channel end points per 400 m band, x = -2..+2 km:", hend[k - 5:k + 5].tolist())
    print("   at x = 0: %d, %d   others %.1f ± %.1f   %s" % (hend[k - 1], hend[k], refe.mean(), refe.std(), "ok" if okE else "FAIL"))
    others = [cross[L] for L in LINES if L != 0]
    okX = cross[0] >= 0.75 * min(others)
    print("X  polylines straddling x = L:", cross, "  %s" % ("ok" if okX else "FAIL"))
    print("   (%d segments touch the 120 km band, %d depressions)" % (n, len(cx)))
    res = dict(gdb=gdb, depr_bands=h.tolist(), end_bands=hend.tolist(), crossings={str(a): b for a, b in cross.items()},
               D=okD, E=okE, X=okX)
    if "--json" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    ok = okD and okE and okX
    print("RESULT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
