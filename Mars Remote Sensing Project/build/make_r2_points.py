# -*- coding: utf-8 -*-
r"""R2: the probability sample for unbiased map accuracy and class areas (NEXT-STEPS §12.3 R2, §14 row 1; KB §69.53).

    "<ArcGIS Pro Python>" make_r2_points.py [--per 25] [--cal 5] [--seed 5301]

Strata are the classes of the seven-class SVM map (11 x 11 mode, the paper's lead SVM map), read from the cached
400 m class array (make_map_agreement.load: refuses one older than its raster). In each stratum --per points are drawn
with probability proportional to area: a row by (class pixels valid in all four scored maps) x cos(latitude), then a
column uniformly among those pixels. The stratum weights W_h are the strata's cos-latitude area shares over the same
jointly valid pixels. The four maps scored (make_map_agreement.PAIRS): the published four-class SVM, the four-class
U-Net, the seven-class SVM, the seven-class U-Net; each map's class at every point is recorded.

Hidden among them, --cal points per class inside the author's held-out polygons (Landform_TrainingSamples_v2_60_test,
a polygon drawn at random per point, the point uniform inside it): the calibration rows that test whoever labels the
sheets against the author's own classes. All rows are shuffled into one order. Writes logs\r2\:
  r2_points.json   slot -> lon, lat (what make_r2_sheets.py draws; no class, no kind)
  r2_key.json      slot -> kind (r2 / cal), stratum, each map's class, the polygon's class; the weights. Not shown to
                   the labeller: read only by score_r2.py.
Read-only on the gdb and the maps.
"""
import os, sys, json, math, random
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import grid60 as G
from labelsets import SEVEN
from make_map_agreement import PAIRS, load

OUT = os.path.join(HERE, "logs", "r2")
TEST = "Landform_TrainingSamples_v2_60_test"


def arg(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def maps():
    """(name, array) for the four scored maps; the seven-class SVM, the stratifier, first."""
    four, v2 = PAIRS
    out = [("svm7", load(*v2[2])), ("unet7", load(*v2[3])), ("svm4", load(*four[2])), ("unet4", load(*four[3]))]
    assert len({a.shape for _, a in out}) == 1
    return out


def main():
    per, ncal, seed = arg("--per", 25), arg("--cal", 5), arg("--seed", 5301)
    rng = random.Random(seed)
    M = maps()
    S = M[0][1]
    H, W = S.shape
    K = len(SEVEN)
    dpx, dpy = 360.0 / W, 2 * G.G100.lat_of(G.G100.oy) / H
    lat_top, lon_left = G.G100.lat_of(G.G100.oy), G.G100.lon_of(G.G100.ox)
    lat = lat_top - (np.arange(H) + .5) * dpy
    cnt = np.zeros((H, K))                                      # jointly valid pixels per row and stratum
    for r0 in range(0, H, 512):
        r1 = min(r0 + 512, H)
        blk = [np.asarray(a[r0:r1]) for _, a in M]
        ok = np.all([b < K for b in blk], axis=0)
        s = blk[0]
        for k in range(K):
            cnt[r0:r1, k] = ((s == k) & ok).sum(1)
    wrow = cnt * np.cos(np.radians(lat))[:, None]
    Wh = wrow.sum(0) / wrow.sum()
    rows = []
    for k in range(K):
        p = wrow[:, k] / wrow[:, k].sum()
        cum = np.cumsum(p)
        for _ in range(per):
            r = int(np.searchsorted(cum, rng.random()))
            blk = [np.asarray(a[r]) for _, a in M]
            ok = np.all([b < K for b in blk], axis=0) & (blk[0] == k)
            c = rng.choice(np.flatnonzero(ok).tolist())
            rows.append(dict(kind="r2", stratum=k, row=r, col=c,
                             lon=round((lon_left + (c + .5) * dpx) % 360, 5), lat=round(lat_top - (r + .5) * dpy, 5),
                             maps={n: int(a[r, c]) for n, a in M}))
    polys = {}
    with arcpy.da.SearchCursor(os.path.join(GDB, TEST), ["SHAPE@", "Classvalue"]) as cur:
        for g, v in cur:
            polys.setdefault(int(v) - 1, []).append(g)
    for k in range(K):
        for _ in range(ncal):
            g = rng.choice(polys[k])
            e = g.extent
            while True:
                x, y = e.XMin + rng.random() * e.width, e.YMin + rng.random() * e.height
                if g.contains(arcpy.Point(x, y)):
                    break
            lon = x % 360
            r, c = int((lat_top - y) / dpy), int(((lon - lon_left) % 360) / dpx)
            rows.append(dict(kind="cal", polygon=k, row=r, col=c, lon=round(lon, 5), lat=round(y, 5),
                             maps={n: int(a[min(r, H - 1), c % W]) for n, a in M}))
    rng.shuffle(rows)
    os.makedirs(OUT, exist_ok=True)
    slot = lambda i: "%s%d" % (chr(65 + i // 6) if i < 156 else "Z" + chr(65 + (i - 156) // 6), i % 6 + 1)
    pts, key = {}, {}
    for i, r in enumerate(rows):
        pts[slot(i)] = {"lon": r["lon"], "lat": r["lat"]}
        key[slot(i)] = r
    json.dump({"seed": seed, "points": pts}, open(os.path.join(OUT, "r2_points.json"), "w"), indent=0)
    json.dump({"seed": seed, "per": per, "cal": ncal, "classes": SEVEN, "stratifier": "svm7",
               "Wh": [round(float(x), 6) for x in Wh], "slots": key},
              open(os.path.join(OUT, "r2_key.json"), "w"), indent=0)
    print("%d rows (%d r2, %d cal) -> %s" % (len(rows), per * K, ncal * K, OUT))
    print("stratum weights:", ", ".join("%s %.1f %%" % (n, 100 * w) for n, w in zip(SEVEN, Wh)))


if __name__ == "__main__":
    main()
