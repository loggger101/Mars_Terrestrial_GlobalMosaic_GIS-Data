# -*- coding: utf-8 -*-
"""Right-size the generated figures for the boxes they actually occupy.

Target ~200 effective dpi at the placed width, which is generous for a 1920-px
projector and still fine in print. Photographic panels go to JPEG; the gradient
panels stay PNG because they are near-binary line work that JPEG rings on.
"""
import os

from PIL import Image

DIR = r"C:\Users\Loggg\Downloads\Mars Remote Sensing Project\build\le_img"
DPI = 200.0

# name -> (placed width in points, codec)
PLAN = {
    "lz_viking.png": (262, "jpg"),
    "lz_themis.png": (262, "jpg"),
    "lz_dem.png": (262, "jpg"),
    "lv_viking.png": (400, "jpg"),
    "lv_themis.png": (400, "jpg"),
    "lv_grad_viking.png": (400, "png"),
    "lv_grad_themis.png": (400, "png"),
    "lv_hillshade.png": (400, "jpg"),
    "locator_global.png": (830, "jpg"),
    "em_spectrum.png": (830, "png"),
}

total_before = total_after = 0
print("%-22s %-13s %-13s %9s %9s" % ("figure", "before", "after", "before", "after"))
print("-" * 74)
for name, (pt_w, codec) in sorted(PLAN.items()):
    src = os.path.join(DIR, name)
    if not os.path.exists(src):
        print("%-22s MISSING" % name)
        continue
    before = os.path.getsize(src)
    im = Image.open(src)
    target = int(round(pt_w * DPI / 72.0))
    if im.width > target:
        im = im.resize((target, int(round(im.height * target / im.width))),
                       Image.LANCZOS)
    out_name = name if codec == "png" else name[:-4] + ".jpg"
    dst = os.path.join(DIR, out_name)
    if codec == "jpg":
        im.convert("RGB").save(dst, "JPEG", quality=90, optimize=True,
                               progressive=True)
        if out_name != name:
            os.remove(src)
    else:
        im.save(dst, "PNG", optimize=True)
    after = os.path.getsize(dst)
    total_before += before
    total_after += after
    print("%-22s %-13s %-13s %8.2fM %8.2fM"
          % (out_name, "%dpx" % Image.open(src).width if os.path.exists(src)
             else "-", "%dpx" % im.width, before / 1e6, after / 1e6))

print("-" * 74)
print("%-50s %8.2fM %8.2fM" % ("total", total_before / 1e6, total_after / 1e6))
