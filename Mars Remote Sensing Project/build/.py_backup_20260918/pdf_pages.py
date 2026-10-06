# -*- coding: utf-8 -*-
"""Rasterise a PDF to page PNGs, and flag obvious layout faults.

Faults worth catching in a written deliverable: a heading stranded as the last
line on a page, a table split across a page break, a nearly empty page, and
text running outside the margins.
"""
import os
import sys

import pymupdf

src = sys.argv[1]
out = sys.argv[2]
zoom = float(sys.argv[3]) if len(sys.argv) > 3 else 1.6
os.makedirs(out, exist_ok=True)

doc = pymupdf.open(src)
print("%s : %d pages" % (os.path.basename(src), doc.page_count))
print()
print("%-5s %-9s %-7s %-9s %s" % ("page", "text px", "fill %", "blocks", "notes"))
print("-" * 78)

for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    pix.save(os.path.join(out, "p%02d.png" % i))
    rect = page.rect
    blocks = page.get_text("blocks")
    text_blocks = [b for b in blocks if b[6] == 0 and b[4].strip()]
    covered = sum((b[3] - b[1]) for b in text_blocks)
    fill = 100.0 * covered / rect.height if rect.height else 0
    notes = []
    if text_blocks:
        # margins: Word was set to 1 inch = 72 pt
        left = min(b[0] for b in text_blocks)
        right = max(b[2] for b in text_blocks)
        if left < 66:
            notes.append("left margin %.0f pt" % left)
        if right > rect.width - 66:
            notes.append("right overrun to %.0f of %.0f" % (right, rect.width))
        last = sorted(text_blocks, key=lambda b: b[3])[-1]
        tail = last[4].strip()
        if len(tail) < 60 and not tail.endswith((".", ":", "?", "!")) \
                and i < doc.page_count:
            notes.append("page ends on a short line: %r" % tail[:48])
    if fill < 45 and i < doc.page_count:
        notes.append("page only %.0f%% full" % fill)
    print("%-5d %-9d %-7.0f %-9d %s"
          % (i, len(page.get_text()), fill, len(text_blocks),
             "; ".join(notes) or "ok"))

print()
print("wrote %d page PNGs to %s" % (doc.page_count, out))
