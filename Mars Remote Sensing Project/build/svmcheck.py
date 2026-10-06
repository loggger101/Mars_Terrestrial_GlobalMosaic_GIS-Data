# -*- coding: utf-8 -*-
"""Scoring a landform classification against independent evidence (KB §30, §31).

Moved verbatim out of verify_svm_classifications.py so every classification is scored by the
same code, the code that passed the planted-map tests of §30.4.

  g = dict(dpx, dpy, lat_top, lon_left) describes the array: degrees per pixel, the latitude of
  its top edge, the east longitude of its left edge. Class value 0 is Crater.
"""
import numpy as np
from matplotlib.path import Path

KPD = 3396.19 * np.pi / 180.0                       # km per degree, Mars sphere


def kappa(ct):
    po = np.trace(ct) / ct.sum(); pe = (ct.sum(0) * ct.sum(1)).sum() / ct.sum() ** 2
    return po, (po - pe) / (1 - pe)


def training_score(a, m, g, polys):
    """Area-weighted confusion of his polygons (rows) against the map's classes (cols)."""
    H, W = a.shape
    cmx = np.zeros((4, 4)); own = []
    for v, rings in polys:
        hit = np.zeros(4)
        for ring in rings:
            xy = np.array(ring)
            lo_ = xy[0, 0] % 360 + ((xy[:, 0] % 360 - xy[0, 0] % 360 + 180) % 360 - 180)
            col = (lo_ - g["lon_left"]) / g["dpx"]; row = (g["lat_top"] - xy[:, 1]) / g["dpy"]
            r0, r1 = max(int(row.min()), 0), min(int(np.ceil(row.max())) + 1, H)
            c0, c1 = int(np.floor(col.min())), int(np.ceil(col.max())) + 1
            if r1 <= r0:
                continue
            rr, cc = np.mgrid[r0:r1, c0:c1]
            ins = Path(np.c_[col, row]).contains_points(
                np.c_[cc.ravel() + .5, rr.ravel() + .5]).reshape(rr.shape)
            sel = ins & m[rr, cc % W]
            if sel.any():
                np.add.at(hit, a[rr[sel], (cc % W)[sel]],
                          np.cos(np.radians(g["lat_top"] - (rr[sel] + .5) * g["dpy"])))
        if hit.sum():
            cmx[v - 1] += hit; own.append((v - 1, hit[v - 1] / hit.sum()))
    return cmx, own


def crater_score(a, m, g, craters, tbox):
    """'Crater' (value 0) fraction inside 0.7 R and in a 1.5-2.5 R ring, per IAU crater >= 5 km
    that does not touch any training polygon's bounding box."""
    H, W = a.shape
    fin, frg = [], []
    for name, D, clat, clon in craters:
        if D is None or D < 5:
            continue
        R = D / 2; rlat = R / KPD; rlon = rlat / max(np.cos(np.radians(clat)), .05)
        if abs(clat) + 2.5 * rlat > g["lat_top"] - .5:
            continue
        l180 = (clon + 180) % 360 - 180
        if len(tbox) and ((tbox[:, 0] <= l180 + 2.5 * rlon) & (tbox[:, 1] >= l180 - 2.5 * rlon) &
                          (tbox[:, 2] <= clat + 2.5 * rlat) & (tbox[:, 3] >= clat - 2.5 * rlat)).any():
            continue
        cc0 = ((clon % 360 - g["lon_left"]) % 360) / g["dpx"]; rc0 = (g["lat_top"] - clat) / g["dpy"]
        hw = int(np.ceil(2.5 * rlon / g["dpx"])) + 1; hh = int(np.ceil(2.5 * rlat / g["dpy"])) + 1
        r0, r1 = int(rc0) - hh, int(rc0) + hh + 1
        if r0 < 0 or r1 > H:
            continue
        cols = np.arange(int(cc0) - hw, int(cc0) + hw + 1)
        win = a[r0:r1][:, cols % W]; wm = m[r0:r1][:, cols % W]
        dy = (np.arange(r0, r1) + .5 - rc0) * g["dpy"]; dx = (cols + .5 - cc0) * g["dpx"]
        dist = np.hypot(dy[:, None] * KPD, dx[None, :] * KPD * np.cos(np.radians(clat - dy[:, None]))) / R
        ins = (dist < .7) & wm; ring = (dist > 1.5) & (dist < 2.5) & wm
        if ins.sum() < 9 or ring.sum() < 9:
            continue
        fin.append((win[ins] == 0).mean()); frg.append((win[ring] == 0).mean())
    return np.array(fin), np.array(frg)
