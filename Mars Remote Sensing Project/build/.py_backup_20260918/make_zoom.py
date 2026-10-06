# -*- coding: utf-8 -*-
"""Three matched panels over the Louros Valles fan, at the slide's aspect (~1.14).

Same ground in all three, read from the three global rasters, so the
three-way comparison on the data-sources slide is genuinely co-registered.
"""
import os

import numpy as np
from PIL import Image

import marsfig as M

OUT = r"C:\Users\Loggg\Downloads\Mars Remote Sensing Project\build\le_img"

# Louros Valles, the sapping-fed tributary fan on the south wall of Ius Chasma
ZOOM = dict(lon0=-85.7, lon1=-81.7, lat0=-10.75, lat1=-7.25)


def save(name, arr, mode=None):
    Image.fromarray(arr, mode).save(os.path.join(OUT, name), optimize=True)
    print("   %-20s %s" % (name, arr.shape))


def ramp(norm, stops):
    pos = np.array([s[0] for s in stops], dtype=np.float32)
    cols = np.array([s[1] for s in stops], dtype=np.float32)
    out = np.empty(norm.shape + (3,), dtype=np.float32)
    for c in range(3):
        out[..., c] = np.interp(norm, pos, cols[:, c])
    return out.astype(np.uint8)


print("Louros Valles zoom, %.1f-%.1f E / %.2f-%.2f lat"
      % (ZOOM["lon0"] + 360, ZOOM["lon1"] + 360, ZOOM["lat0"], ZOOM["lat1"]))

vik, ext = M.read_window(M.VIKING, ZOOM, max_px=2600)
save("lz_viking.png", M.stretch_rgb(vik))

the, _ = M.read_window(M.THEMIS, ZOOM, max_px=2600)
save("lz_themis.png", M.stretch(the, 2, 98))

dem, _ = M.read_window(M.DEM, ZOOM, max_px=2600)
dem = dem.astype(np.float32)
lo, hi = np.percentile(dem, [1, 99])
norm = np.clip((dem - lo) / max(hi - lo, 1), 0, 1)
save("lz_dem.png", ramp(norm, [
    (0.00, (26, 38, 64)), (0.25, (32, 96, 122)), (0.50, (196, 148, 92)),
    (0.75, (222, 196, 150)), (1.00, (250, 244, 232))]))

print("\naspect %.3f (slide boxes are 262x232 = 1.129)"
      % (vik.shape[1] / float(vik.shape[0])))
print("elevation in this window: %.0f m to %.0f m, relief %.0f m"
      % (dem.min(), dem.max(), dem.max() - dem.min()))
