# -*- coding: utf-8 -*-
r"""Does a close CTX view show the same ground as the 40 km view? (KB §69.52)

Esri's tiled CTX service holds misplaced tiles at some zoom levels: around one Athabasca candidate the 12 and 16 km
windows show a canyon wall pasted over lava plains, in the maps' frame and in the service's own, while 8, 24 and 40 km
show the plains and the crater the DEM puts there. So every close view is compared with the 40 km view over the same
ground: both are cut to the close view's extent, block-averaged to a 30 x 30 grid of greys, and correlated after
removing each grid's mean plane (a lighting or stretch difference between zoom levels is not a mismatch).

    python ctx_consistency.py <cache folder>              # the correlation of every cached near / far pair
    python ctx_consistency.py <cache folder> --key <key>  # one pair

make_ctx_chips.py imports agree() to re-render a close view whose correlation falls under its threshold.
"""
import os, sys, json, glob
import numpy as np
import matplotlib.image as mpimg

N = 30


def grey(img):
    a = img[..., :3].mean(axis=2) if img.ndim == 3 else img
    return a.astype(np.float64)


def crop(img, ext, to):
    """The part of img (extent ext = x0, x1, y0, y1) inside extent to, by pixel."""
    h, w = img.shape[:2]
    c0 = int(round((to[0] - ext[0]) / (ext[1] - ext[0]) * w)); c1 = int(round((to[1] - ext[0]) / (ext[1] - ext[0]) * w))
    r0 = int(round((ext[3] - to[3]) / (ext[3] - ext[2]) * h)); r1 = int(round((ext[3] - to[2]) / (ext[3] - ext[2]) * h))
    return img[max(0, r0):r1, max(0, c0):c1]


def blocks(a, n=N):
    h, w = a.shape
    a = a[:h - h % n, :w - w % n]
    return a.reshape(n, a.shape[0] // n, n, a.shape[1] // n).mean(axis=(1, 3))


def detrend(g):
    y, x = np.mgrid[:g.shape[0], :g.shape[1]]
    A = np.c_[np.ones(g.size), x.ravel(), y.ravel()]
    coef = np.linalg.lstsq(A, g.ravel(), rcond=None)[0]
    return g - (A @ coef).reshape(g.shape)


def agree(near, e_near, far, e_far):
    """Correlation of the two views over the close view's extent (1 = same ground, ~0 = unrelated)."""
    a = detrend(blocks(grey(near)))
    b = detrend(blocks(grey(crop(far, e_far, e_near))))
    if a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])


def main():
    cache = sys.argv[1]
    keys = ([sys.argv[sys.argv.index("--key") + 1]] if "--key" in sys.argv else
            sorted({os.path.basename(p)[:-len("_near.png")] for p in glob.glob(os.path.join(cache, "*_near.png"))}))
    for k in keys:
        f = lambda s: os.path.join(cache, k + s)
        if not os.path.exists(f("_far.png")):
            continue
        r = agree(mpimg.imread(f("_near.png")), json.load(open(f("_near.json")))["extent"],
                  mpimg.imread(f("_far.png")), json.load(open(f("_far.json")))["extent"])
        print("%-48s %.3f" % (k, r))


if __name__ == "__main__":
    main()
