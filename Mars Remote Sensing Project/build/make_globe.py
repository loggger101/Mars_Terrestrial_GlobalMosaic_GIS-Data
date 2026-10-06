# -*- coding: utf-8 -*-
"""A whole-Mars orthographic disc for the title slide, from his own Viking mosaic.

Reads the cached global decimation rather than the 12.7 GB TIFF, so this runs in
seconds under the stock interpreter -- no GDAL needed.

    python make_globe.py [out.png] [lon0] [lat0]

Default view is centred on 75 deg W, which puts Valles Marineris across the
middle of the disc with Tharsis on the limb -- the face of Mars people recognise.
"""

import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "viking_global_3000.npy")

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    HERE, "pres1_img", "globe_viking.png")
LON0 = float(sys.argv[2]) if len(sys.argv) > 2 else -75.0
LAT0 = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0

SIZE = 2600                       # pixels across the full image
PAD = 0.995                       # disc radius as a fraction of SIZE/2


def main():
    src = np.load(SRC)                        # (1500, 3000, 3), -180..180 E
    sh, sw = src.shape[:2]

    R = SIZE / 2.0 * PAD
    cx = cy = SIZE / 2.0
    yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(np.float64)
    X = (xx - cx) / R
    Y = (cy - yy) / R
    rho = np.hypot(X, Y)
    disc = rho <= 1.0

    # Inverse orthographic. rho == 0 is the sub-observer point; guard the
    # division, then overwrite that pixel with the centre lon/lat.
    safe = np.where(disc & (rho > 0), rho, 1.0)
    c = np.arcsin(np.clip(safe, -1, 1))
    sin_c, cos_c = np.sin(c), np.cos(c)
    lat0 = np.radians(LAT0)

    lat = np.arcsin(np.clip(cos_c * np.sin(lat0) +
                            Y * sin_c * np.cos(lat0) / safe, -1, 1))
    lon = np.radians(LON0) + np.arctan2(
        X * sin_c, safe * cos_c * np.cos(lat0) - Y * sin_c * np.sin(lat0))

    # Equirectangular sample, nearest neighbour at 1:1 -- the disc is wider than
    # the source is tall, so this upsamples and no averaging is called for.
    col = np.mod(np.degrees(lon) + 180.0, 360.0) / 360.0 * sw
    row = (90.0 - np.degrees(lat)) / 180.0 * sh
    col = np.clip(col.astype(np.int32), 0, sw - 1)
    row = np.clip(row.astype(np.int32), 0, sh - 1)

    rgb = src[row, col]
    rgb[~disc] = 0

    # Antialiased limb, and a terminator-free lambertian shade so the disc reads
    # as a sphere rather than as a circular crop.
    edge = np.clip((1.0 - rho) * R, 0.0, 1.0)
    shade = np.clip(0.42 + 0.58 * np.sqrt(np.clip(1.0 - rho ** 2, 0, 1)), 0, 1)
    shade = shade[..., None] ** 0.75
    rgb = np.clip(rgb.astype(np.float32) * shade, 0, 255).astype(np.uint8)

    alpha = (edge * 255).astype(np.uint8)
    out = np.dstack([rgb, alpha])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    Image.fromarray(out, "RGBA").save(OUT, optimize=True)
    print("wrote %s -- %d x %d" % (OUT, SIZE, SIZE))


if __name__ == "__main__":
    main()
