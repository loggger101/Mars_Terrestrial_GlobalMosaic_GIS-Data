# -*- coding: utf-8 -*-
"""How much vertical slack does each slide have?

Aptos is not installed here, so PowerPoint substitutes when rendering. If the
deck is shown on a machine that HAS Aptos, line wrapping changes and text
blocks can grow. Headroom is the margin of safety: roughly one body line is
18-20 pt, so anything under ~20 pt is one wrapped line away from running off.
"""
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import glob
import os
import sys

import numpy as np
from PIL import Image

DECK = sys.argv[1]
LIMIT = 522.0          # content should end by here on a 540 pt slide
H_PT = 540.0

rows = []
for p in sorted(glob.glob(os.path.join(DECK, "Slide*.PNG")),
                key=lambda s: int(''.join(c for c in os.path.basename(s)
                                          if c.isdigit()))):
    a = np.asarray(Image.open(p).convert("L"), dtype=np.int16)
    bg = int(np.median(a))
    ink = np.abs(a - bg) > 28
    if not ink.any():
        continue
    ys, _xs = np.where(ink)
    bottom = (ys.max() + 1) * H_PT / a.shape[0]
    n = int(''.join(c for c in os.path.basename(p) if c.isdigit()))
    rows.append((n, bottom, LIMIT - bottom))

rows.sort(key=lambda r: r[2])
print("%-6s %-9s %-10s %s" % ("slide", "bottom", "headroom", "risk if the font changes"))
print("-" * 72)
for n, bottom, head in rows:
    if head < 0:
        risk = "ALREADY OVER"
    elif head < 20:
        risk = "tight - one extra wrapped line overflows"
    elif head < 40:
        risk = "one extra line fits, two would not"
    else:
        risk = "comfortable"
    print("%-6d %-9.0f %-10.0f %s" % (n, bottom, head, risk))

tight = [n for n, _b, h in rows if h < 40]
print()
print("slides with less than 40 pt of slack: %s"
      % (", ".join(map(str, sorted(tight))) or "none"))
