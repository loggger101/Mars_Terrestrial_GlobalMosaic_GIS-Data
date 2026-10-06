# -*- coding: utf-8 -*-
"""Audit every picture in a deck: placement, aspect distortion, effective DPI, crop."""
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import sys
import zipfile

from pptx import Presentation
from pptx.util import Emu

EMU_PT = 12700
DECK = sys.argv[1] if len(sys.argv) > 1 else (
    r"Z:\Mars Remote Sensing Project"
    r"\ocean first pres LE.pptx")

prs = Presentation(DECK)
W = prs.slide_width / EMU_PT
H = prs.slide_height / EMU_PT
print("deck %.0f x %.0f pt   (%s)\n" % (W, H, os.path.basename(DECK)))

zf = zipfile.ZipFile(DECK)
print("%-3s %-22s %5s %5s %6s %6s  %-11s %-9s %-7s %s"
      % ("sl", "image", "x", "y", "w", "h", "native px", "aspect", "eff dpi", "notes"))
print("-" * 118)

for i, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        if sh.shape_type != 13 and not hasattr(sh, "image"):
            continue
        try:
            img = sh.image
        except Exception:
            continue
        px_w, px_h = img.size
        x, y = sh.left / EMU_PT, sh.top / EMU_PT
        w, h = sh.width / EMU_PT, sh.height / EMU_PT
        cl = getattr(sh, "crop_left", 0) or 0
        cr = getattr(sh, "crop_right", 0) or 0
        ct = getattr(sh, "crop_top", 0) or 0
        cb = getattr(sh, "crop_bottom", 0) or 0
        vis_w = px_w * (1 - cl - cr)
        vis_h = px_h * (1 - ct - cb)
        native = vis_w / vis_h
        box = w / h
        stretch = 100 * (box / native - 1)
        # a 960 pt slide shown at 1920 px => 2 px per pt
        eff_dpi = 72.0 * vis_w / w
        notes = []
        if abs(stretch) > 1.0:
            notes.append("STRETCHED %+.1f%%" % stretch)
        if any((cl, cr, ct, cb)):
            notes.append("crop L%.0f R%.0f T%.0f B%.0f%%"
                         % (cl * 100, cr * 100, ct * 100, cb * 100))
        if eff_dpi < 110:
            notes.append("LOW DPI")
        if x < 0 or y < 0 or x + w > W + 0.5 or y + h > H + 0.5:
            notes.append("OFF-SLIDE")
        name = os.path.basename(img.blob and getattr(img, "filename", "") or "")
        print("%-3d %-22s %5.0f %5.0f %6.0f %6.0f  %5dx%-5d %-9.3f %-7.0f %s"
              % (i, name or ("sha1:" + img.sha1[:10]), x, y, w, h,
                 px_w, px_h, native, eff_dpi, "; ".join(notes) or "ok"))

print()
sizes = {}
for n in zf.namelist():
    if n.startswith("ppt/media/"):
        sizes[n] = zf.getinfo(n).file_size
print("embedded media: %d files, %.1f MB total"
      % (len(sizes), sum(sizes.values()) / 1e6))
for n, s in sorted(sizes.items(), key=lambda kv: -kv[1]):
    print("   %-28s %7.2f MB" % (os.path.basename(n), s / 1e6))
