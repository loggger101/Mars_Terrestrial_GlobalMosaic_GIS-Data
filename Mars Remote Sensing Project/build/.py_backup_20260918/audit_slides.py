# -*- coding: utf-8 -*-
"""Scan rendered slides for ink outside the safe area.

The deck is 960x540 pt with a 65 pt left margin and content ending by ~520 pt.
Rendered at 1280x720, that is 86.7 px left and 693 px bottom. Anything darker
than the background outside those bounds is content crowding the slide edge.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

DECK = sys.argv[1]
MARGIN_PT, BOTTOM_PT, RIGHT_PT = 65, 522, 895
W_PT, H_PT = 960.0, 540.0

print("%-5s %-7s %-7s %-7s %-7s %s"
      % ("slide", "left", "right", "top", "bottom", "notes"))
print("-" * 78)
worst = []
for p in sorted(glob.glob(os.path.join(DECK, "Slide*.PNG")),
                key=lambda s: int(''.join(c for c in os.path.basename(s)
                                          if c.isdigit()))):
    im = Image.open(p).convert("L")
    a = np.asarray(im, dtype=np.int16)
    h, w = a.shape
    bg = int(np.median(a))                      # white or navy ground
    ink = np.abs(a - bg) > 28
    if not ink.any():
        print("%-5s %s" % (os.path.basename(p), "blank"))
        continue
    ys, xs = np.where(ink)
    l_pt = xs.min() * W_PT / w
    r_pt = (xs.max() + 1) * W_PT / w
    t_pt = ys.min() * H_PT / h
    b_pt = (ys.max() + 1) * H_PT / h
    notes = []
    if l_pt < MARGIN_PT - 2:
        notes.append("left edge at %.0f pt (margin %d)" % (l_pt, MARGIN_PT))
    if r_pt > RIGHT_PT + 2:
        notes.append("right edge at %.0f pt (limit %d)" % (r_pt, RIGHT_PT))
    if b_pt > BOTTOM_PT + 2:
        notes.append("bottom at %.0f pt (limit %d)" % (b_pt, BOTTOM_PT))
    if t_pt < 40:
        notes.append("top at %.0f pt" % t_pt)
    n = os.path.basename(p).replace(".PNG", "").replace("Slide", "")
    print("%-5s %-7.0f %-7.0f %-7.0f %-7.0f %s"
          % (n, l_pt, r_pt, t_pt, b_pt, "; ".join(notes) or "ok"))
    if notes:
        worst.append((n, notes))

print()
if worst:
    print("SLIDES NEEDING ATTENTION:")
    for n, notes in worst:
        print("   slide %-3s %s" % (n, "; ".join(notes)))
else:
    print("every slide sits inside the safe area")
