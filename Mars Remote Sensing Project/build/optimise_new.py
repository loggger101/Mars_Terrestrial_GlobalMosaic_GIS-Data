# -*- coding: utf-8 -*-
"""Right-size the v2 figures. Same rule as optimise_figs.py: ~200 effective dpi
at the placed width, JPEG for anything photographic. All seven of these are
placed at or near the full 830 pt content width."""
import os

from PIL import Image

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "le_img")
DPI, PLACED_PT = 200.0, 830

NAMES = ["g_viking.png", "g_themis.png", "g_dem.png", "g_extent.png",
         "f_meridian.png",
         "f_zfactor.png", "f_hypsometry.png", "f_daedalia.png"]

target = int(round(PLACED_PT * DPI / 72.0))
print("%-20s %-12s %-12s %9s %9s" % ("figure", "before", "after", "MB", "MB"))
print("-" * 68)
before_tot = after_tot = 0
for name in NAMES:
    src = os.path.join(DIR, name)
    if not os.path.exists(src):
        print("%-20s MISSING" % name)
        continue
    before = os.path.getsize(src)
    im = Image.open(src)
    w0 = im.width
    if im.width > target:
        im = im.resize((target, int(round(im.height * target / im.width))),
                       Image.LANCZOS)
    dst = os.path.join(DIR, name[:-4] + ".jpg")
    im.convert("RGB").save(dst, "JPEG", quality=90, optimize=True,
                           progressive=True)
    after = os.path.getsize(dst)
    before_tot += before
    after_tot += after
    print("%-20s %-12s %-12s %8.2f %8.2f"
          % (os.path.basename(dst), "%dpx" % w0, "%dpx" % im.width,
             before / 1e6, after / 1e6))
print("-" * 68)
print("%-46s %8.2f %8.2f" % ("total", before_tot / 1e6, after_tot / 1e6))
