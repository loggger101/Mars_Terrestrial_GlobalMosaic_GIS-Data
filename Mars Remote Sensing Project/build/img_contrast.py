# -*- coding: utf-8 -*-
"""Measure how much tonal range each figure actually uses.

A panel that lives in the top few percent of the luminance range will read as
a blank white rectangle once a projector's gamma and ambient light are applied.
"""
import glob
import os

import numpy as np
from PIL import Image

DIR = r"Z:\Mars Remote Sensing Project\build\le_img"

print("%-12s %7s %7s %7s %7s %7s  %s"
      % ("image", "mean", "p1", "p99", "range", "std", "verdict"))
print("-" * 84)
for p in sorted(glob.glob(os.path.join(DIR, "*.png"))):
    a = np.asarray(Image.open(p).convert("L"), dtype=np.float32)
    p1, p99 = np.percentile(a, [1, 99])
    rng, std = p99 - p1, float(a.std())
    if a.mean() > 215 and rng < 90:
        verdict = "WASHED OUT - will project as near-blank"
    elif rng < 70:
        verdict = "low contrast"
    else:
        verdict = "ok"
    print("%-12s %7.1f %7.1f %7.1f %7.1f %7.1f  %s"
          % (os.path.basename(p), a.mean(), p1, p99, rng, std, verdict))
