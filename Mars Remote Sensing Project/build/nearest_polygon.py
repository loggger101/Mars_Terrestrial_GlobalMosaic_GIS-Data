# -*- coding: utf-8 -*-
"""The nearest training polygon as a stand-in map (KB §69.35): moved verbatim out of make_spatial_baseline.py so
the A3(a) baseline and the block bootstrap (make_block_bootstrap.py, A5) read it through the same code."""
import numpy as np

STEP = 0.005                                                                      # degrees between boundary points


def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def boundary_points(P):
    """Every training ring densified to <= STEP degrees, with its polygon's class index (code - 1)."""
    xs, ys, ks = [], [], []
    for v, rings in P:
        for ring in rings:
            xy = np.array(ring, float)
            xy = np.r_[xy, xy[:1]]
            for (x0, y0), (x1, y1) in zip(xy[:-1], xy[1:]):
                dx = (x1 - x0 + 180) % 360 - 180                                  # the short way round
                n = max(1, int(np.ceil(max(abs(dx), abs(y1 - y0)) / STEP)))
                t = np.arange(n) / n
                xs.append(x0 + t * dx); ys.append(y0 + t * (y1 - y0)); ks.append(np.full(n, v - 1))
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(ks).astype(np.uint8)


class Nearest:
    """Stands in for the map array: a[rows, cols] is the nearest training polygon's class at those pixels."""
    def __init__(self, tree, cls, g, shape):
        self.tree, self.cls, self.g, self.shape = tree, cls, g, shape

    def __getitem__(self, rc):
        r, c = (np.asarray(x) for x in rc)
        lon = self.g["lon_left"] + (c + .5) * self.g["dpx"]
        lat = self.g["lat_top"] - (r + .5) * self.g["dpy"]
        _, i = self.tree.query(unit(lon.ravel(), lat.ravel()))
        return self.cls[i].reshape(r.shape)
