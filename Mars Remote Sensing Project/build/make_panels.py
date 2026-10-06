# -*- coding: utf-8 -*-
"""Matched-extent panels over the project's own saved type-area window.

Every panel is the SAME ground read from the three global rasters on Z:, so the
three-way comparison on the data-sources slide is genuinely co-registered rather
than three separate screenshots.
"""
import os
import time

import numpy as np
from PIL import Image

import marsfig as M

OUT = r"Z:\Mars Remote Sensing Project\build\le_img"
os.makedirs(OUT, exist_ok=True)


def save(name, arr, mode=None):
    Image.fromarray(arr, mode).save(os.path.join(OUT, name), optimize=True)
    print("   wrote %-22s %s" % (name, arr.shape))


def ramp(norm, stops):
    """Interpolate an RGB ramp over a 0..1 array."""
    pos = np.array([s[0] for s in stops], dtype=np.float32)
    cols = np.array([s[1] for s in stops], dtype=np.float32)
    out = np.empty(norm.shape + (3,), dtype=np.float32)
    for c in range(3):
        out[..., c] = np.interp(norm, pos, cols[:, c])
    return out.astype(np.uint8)


t0 = time.time()
print("Viking colour ...")
vik, ext = M.read_window(M.VIKING)
save("lv_viking.png", M.stretch_rgb(vik))

print("THEMIS day IR ...")
the, _ = M.read_window(M.THEMIS)
save("lv_themis.png", M.stretch(the, 2, 98))

print("HRSC/MOLA elevation ...")
dem, _ = M.read_window(M.DEM)
dem = dem.astype(np.float32)
lo, hi = np.percentile(dem, [1, 99])
norm = np.clip((dem - lo) / max(hi - lo, 1), 0, 1)
save("lv_dem.png", ramp(norm, [
    (0.00, (26, 38, 64)), (0.25, (32, 96, 122)), (0.50, (196, 148, 92)),
    (0.75, (222, 196, 150)), (1.00, (250, 244, 232))]))

print("hillshade, latitude-correct z-factor ...")
cell_deg = (ext[1] - ext[0]) / dem.shape[1]
mid_lat = 0.5 * (ext[2] + ext[3])
hs = M.hillshade(dem, mid_lat, cell_deg)
save("lv_hillshade.png", (hs * 255).astype(np.uint8))

print("DN gradients, legibly stretched ...")
for label, src in (("viking", vik), ("themis", the)):
    g = M.gradient(src)
    g8 = M.stretch(g, 1, 99)
    # dark-on-light like the originals, but using the full tonal range
    save("lv_grad_%s.png" % label, 255 - g8)

print("\nelevation over this window: %.0f m to %.0f m  (1-99%%: %.0f to %.0f)"
      % (dem.min(), dem.max(), lo, hi))
print("cell size %.5f deg  ~ %.0f m at %.1f deg lat"
      % (cell_deg, cell_deg * M.R * np.pi / 180, mid_lat))
print("done in %.1f s" % (time.time() - t0))
