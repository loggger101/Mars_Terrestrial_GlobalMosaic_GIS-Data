# -*- coding: utf-8 -*-
r"""Paired bootstrap of two ±60° landform maps on the held-out polygons (T1 in Pro, KB §55.5).

verify_global60_classification.py gives each map one held-out accuracy and kappa. To say whether map B
beats map A, the difference needs an interval. As in make_thermal_ablation.py (KB §40.1), whole held-out
polygons are resampled (pixels inside one polygon are not independent), 1,000 times with seed 60, and the
SAME resample is applied to both maps, so the differences are paired.

Scoring is svmcheck.training_score, the code verify_global60_classification.py uses: area-weighted
(cos latitude) confusion of each polygon against the map, read at 400 m (a 200 m map's first overview).

  python score_t1_bootstrap.py <map A.tif> <map B.tif> [--out logs\t1_bootstrap_<tag>.json]

Read-only apart from the JSON it writes.
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import arcpy
from osgeo import gdal
import grid60 as G
from paths import on_drive
from svmcheck import kappa, training_score

gdal.UseExceptions()
HERE = os.path.dirname(os.path.abspath(__file__))
GDB = on_drive(r"Mars Project\Mars Project.gdb")
TEST = os.path.join(GDB, "Landform_TrainingSamples_terrain_60_test")
NAMES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
MARS = arcpy.SpatialReference(104905)
NBOOT, SEED = 1000, 60


def polys(fc):
    out = []
    with arcpy.da.SearchCursor(fc, ["SHAPE@", "Classvalue"], spatial_reference=MARS) as c:
        for g, v in c:
            out.append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g]))
    return out


def read(path):
    """The map at 400 m as 0..3 in NAMES order, its valid mask, and the grid description."""
    lut = np.full(256, 255, np.uint8)
    with arcpy.da.SearchCursor(path, ["Value", "Class_name"]) as c:
        for v, n in c:
            lut[int(v)] = [x.lower() for x in NAMES].index(n.strip().lower())
    ds = gdal.Open(path); band = ds.GetRasterBand(1)
    b = band if abs(ds.GetGeoTransform()[1] - 400) < 1 else band.GetOverview(0)
    raw = b.ReadAsArray()
    m = (b.GetMaskBand().ReadAsArray() > 0) & (lut[raw] != 255)
    a = np.where(m, lut[raw], 0).astype(np.uint8)
    H, W = a.shape
    g = dict(dpx=360.0 / W, dpy=2 * G.G100.lat_of(G.G100.oy) / H,
             lat_top=G.G100.lat_of(G.G100.oy), lon_left=G.G100.lon_of(G.G100.ox))
    return a, m, g


def per_polygon(path, P):
    """One confusion row per polygon (4 x 4 with one non-zero row), so any resample can be summed."""
    a, m, g = read(path)
    rows = np.zeros((len(P), 4, 4))
    for i, p in enumerate(P):
        cmx, _ = training_score(a, m, g, [p])
        rows[i] = cmx
    return rows


def main():
    A, B = sys.argv[1], sys.argv[2]
    tag = "%s_vs_%s" % tuple(os.path.splitext(os.path.basename(x))[0].replace("global60_landforms_svm_", "") for x in (A, B))
    out = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
           else os.path.join(HERE, "logs", "t1_bootstrap_%s.json" % tag))
    t0 = time.time()
    P = polys(TEST)
    ra, rb = per_polygon(A, P), per_polygon(B, P)
    keep = (ra.sum((1, 2)) > 0) & (rb.sum((1, 2)) > 0)
    ra, rb = ra[keep], rb[keep]
    full = [kappa(r.sum(0)) for r in (ra, rb)]
    rng = np.random.default_rng(SEED)
    n = len(ra); d_acc = np.empty(NBOOT); d_k = np.empty(NBOOT)
    for k in range(NBOOT):
        s = rng.integers(0, n, n)
        (oa, ka), (ob, kb) = kappa(ra[s].sum(0)), kappa(rb[s].sum(0))
        d_acc[k], d_k[k] = ob - oa, kb - ka
    ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
    res = dict(a=A, b=B, polygons=int(n), boot=NBOOT, seed=SEED,
               a_acc_kappa=[round(full[0][0], 4), round(full[0][1], 4)],
               b_acc_kappa=[round(full[1][0], 4), round(full[1][1], 4)],
               diff_acc=round(full[1][0] - full[0][0], 4), diff_acc_ci95=ci(d_acc),
               diff_kappa=round(full[1][1] - full[0][1], 4), diff_kappa_ci95=ci(d_k),
               share_boot_b_better_acc=round(float((d_acc > 0).mean()), 3))
    json.dump(res, open(out, "w"), indent=1)
    print("A %s  acc %.3f  kappa %.3f" % (os.path.basename(A), *full[0]))
    print("B %s  acc %.3f  kappa %.3f" % (os.path.basename(B), *full[1]))
    print("B - A: accuracy %+.4f  95%% CI %s;  kappa %+.4f  95%% CI %s  (%d polygons, %d resamples)"
          % (res["diff_acc"], res["diff_acc_ci95"], res["diff_kappa"], res["diff_kappa_ci95"], n, NBOOT))
    print("wrote %s  (%.0f s)" % (out, time.time() - t0))


if __name__ == "__main__":
    main()
