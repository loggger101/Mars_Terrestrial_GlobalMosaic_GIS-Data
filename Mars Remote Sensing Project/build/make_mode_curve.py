# -*- coding: utf-8 -*-
r"""A3 (c): how much of the U-Nets' lead a plain majority filter reproduces (NEXT-STEPS §12.2 A3, KB §69.50).

The U-Net classifies 256-pixel chips (51 km at 200 m), so it sees context; the SVM sees one pixel and is then smoothed
by an 11 x 11 (2.2 km) majority filter. Every held-out score rises with the window because the labelled polygons are
large (KB §32.2, §55.3), so this is a curve read as "how much of the lead does context alone give", never as a choice
of window. Each raw 200 m SVM map, four classes (global60_landforms_svm_200m.tif) and seven
(global60_landforms_svm_v2_200m.tif, never scored raw before), is read at its 400 m overview (the scorer's grid) and
majority-filtered there with make_global60_landforms_clean.py's rules (nodata never votes and stays nodata, a tie keeps
the original class, longitude wraps), at 1 (raw), 3, 5, 13, 37 and 127 pixels: 0.4, 1.2, 2.0, 5.2, 14.8 and 50.8 km,
the plan's 25 / 75 / 255 px at 200 m halved. Filtering at 400 m rather than 200 m is the laptop's simplification
(a 400 m array fits in memory; KB §69.50). Each is scored on its held-out polygons by svmcheck.training_score, the
scorer behind every held-out figure, area-weighted at 400 m. The check, or nothing is written: the raw four-class
map must reproduce its own log (accuracy and kappa within 0.001: 0.699, 0.532), and the cached 400 m array of the
published seven-class map (11 x 11) its log's confusion exactly (the raw seven-class map has no log).

Predictions, written before the first run (each reported as held or not held):
  P1  both curves rise from the raw map to the 13-pixel (5 km) window;
  P2  the four-class SVM at 127 px (51 km) stays more than 10 points below the four-class U-Net's 98.9 % (< 88.9 %);
  P3  the seven-class SVM at 127 px stays more than 10 points below the seven-class U-Net's 69.0 % (< 59.0 %).

  "<ArcGIS Pro Python>" make_mode_curve.py        -> logs\mode_curve.json   (reads the drive only; ~1 GB RAM a map)
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import numpy as np
from scipy import ndimage
import arcpy
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import grid60 as G
from svmcheck import kappa, training_score

gdal.UseExceptions()
OUT = os.path.join(HERE, "logs", "mode_curve.json")
MARS = arcpy.SpatialReference(104905)
SIZES = (1, 3, 5, 13, 37, 127)
STRIP = 512
MAPS = [  # name, raster, held-out class, classes, the check (array, log), the U-Net beside it
    ("svm4", "global60_landforms_svm_200m.tif", "Landform_TrainingSamples_terrain_60_test", 4,
     (None, "global60_classification_check_200m.json"), 0.989),
    ("svm7", "global60_landforms_svm_v2_200m.tif", "Landform_TrainingSamples_v2_60_test", 7,
     ("global60_landforms_v2_200m_mode11_ov400.npy", "global60_classification_check_v2_200m_mode11.json"), 0.690),
]


def polys(fc):
    out = []
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue"], spatial_reference=MARS) as c:
        for g, v in c:
            out.append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g]))
    return out


def grid(shape):
    H, W = shape
    return dict(dpx=360.0 / W, dpy=2 * G.G100.lat_of(G.G100.oy) / H,
                lat_top=G.G100.lat_of(G.G100.oy), lon_left=G.G100.lon_of(G.G100.ox))


def read400(path):
    """The raster's 400 m overview as class indices 0..K-1, 255 none (pixel = class code since KB §36)."""
    ds = gdal.Open(path)                                       # held: a band outlives no dataset
    b = ds.GetRasterBand(1)
    k = [i for i in range(b.GetOverviewCount()) if b.GetOverview(i).XSize == G.G200.nx // 2]
    assert k, "no 400 m overview on %s" % path
    a = b.GetOverview(k[0]).ReadAsArray()
    return np.where(a == 255, 255, a.astype(np.int16) - 1).astype(np.uint8)


def mode(a, n, K):
    if n == 1:
        return a
    h = n // 2
    out = np.empty_like(a)
    H = a.shape[0]
    for y0 in range(0, H, STRIP):
        y1 = min(H, y0 + STRIP)
        a0, a1 = max(0, y0 - h), min(H, y1 + h)
        s = a[a0:a1]
        top = np.zeros(s.shape, np.float32); best = np.zeros(s.shape, np.uint8); mine = np.zeros(s.shape, np.float32)
        for k in range(K):
            v = ndimage.uniform_filter((s == k).astype(np.float32), size=n, mode="wrap")
            up = v > top
            best[up] = k; top[up] = v[up]
            mine[s == k] = v[s == k]
        o = np.where(mine >= top, s, best)                    # a tie keeps the original class
        o[s == 255] = 255
        out[y0:y1] = o[y0 - a0:y0 - a0 + (y1 - y0)]
    return out


def score(a, g, P, K):
    cm, own = training_score(a, a != 255, g, P, K)
    oa, kp = kappa(cm)
    rs = cm.sum(1); ok = rs > 0
    bal = float((np.diag(cm)[ok] / rs[ok]).mean())
    return dict(accuracy=round(oa, 4), kappa=round(kp, 4), balanced=round(bal, 4),
                producers=(np.diag(cm) / np.maximum(rs, 1e-12)).round(3).tolist(),
                confusion_unrounded=cm.tolist())


def main():
    t0 = time.time()
    res = dict(sizes_px_400m=list(SIZES), sizes_km=[round(0.4 * s, 1) for s in SIZES], maps={})
    for name, tif, test, K, (chk, logname), unet in MAPS:
        a = read400(os.path.join(G.OUTDIR, tif))
        g = grid(a.shape)
        P = polys(test)
        ref = json.load(open(os.path.join(HERE, "logs", logname), encoding="utf-8"))["held_out"]
        if chk:
            c = score(np.load(os.path.join(HERE, chk)), g, P, K)
            mine, logged = np.array(c["confusion_unrounded"]), np.array(ref["confusion_unrounded"])
            same = np.allclose(mine / mine.sum(), logged / logged.sum(), rtol=1e-9, atol=1e-12)   # the log's sums to 1
            print("check: %s gives %.4f / %.4f, its log %.3f / %.3f, confusion %s" % (
                chk, c["accuracy"], c["kappa"], ref["accuracy"], ref["kappa"], "identical" if same else "DIFFERS"))
            if not same:
                sys.exit("the check failed: nothing written")
        rows = {}
        for n in SIZES:
            t = time.time()
            m = mode(a, n, K)
            rows[n] = score(m, g, P, K)
            print("%s %3d px (%5.1f km): accuracy %.4f kappa %.4f balanced %.4f  (%.0f s)" % (
                name, n, 0.4 * n, rows[n]["accuracy"], rows[n]["kappa"], rows[n]["balanced"], time.time() - t))
            if n == 1 and not chk:
                print("check: its log %.3f / %.3f" % (ref["accuracy"], ref["kappa"]))
                if abs(ref["accuracy"] - rows[1]["accuracy"]) > 0.001 or abs(ref["kappa"] - rows[1]["kappa"]) > 0.001:
                    sys.exit("the raw map's score does not reproduce %s: nothing written" % logname)
            del m
        res["maps"][name] = dict(raster=tif, held_out=test, unet_accuracy=unet, by_size=rows)
        del a
    s4, s7 = res["maps"]["svm4"]["by_size"], res["maps"]["svm7"]["by_size"]
    res["predictions"] = {k: bool(v) for k, v in {
        "P1 both rise raw -> 13 px": s4[13]["accuracy"] > s4[1]["accuracy"] and s7[13]["accuracy"] > s7[1]["accuracy"],
        "P2 four-class at 127 px < 88.9 %": s4[127]["accuracy"] < 0.889,
        "P3 seven-class at 127 px < 59.0 %": s7[127]["accuracy"] < 0.590}.items()}   # numpy bools do not serialise
    print("predictions:", res["predictions"])
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print("->", OUT)


if __name__ == "__main__":
    main()
