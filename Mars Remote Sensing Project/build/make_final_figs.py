# -*- coding: utf-8 -*-
r"""Exports the layouts the final paper and deck show to build\final_img\ (NEXT-STEPS.md §7).

The same export as the interim's (make_interim_figs.py: 200 dpi, the sheet's prose hidden in memory, trimmed, a map
and a legend split out where the sheet has one), pointed at final.py's FIGURES and its own folder, so the interim's
crops in interim_img\ are never touched. The .aprx is opened, never saved; Pro may be open.

  <ArcGIS Pro Python> make_final_figs.py [--only 15_athabasca_type_area,17_x5c_unet_provinces]
  (desktop: D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe)

The charts drawn from logs come from make_fig_final.py (system Python).
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import make_interim_figs as M
import final as F

class _Figures:                             # which layouts: final.py's FIGURES, and those the paper alone shows
    FIGURES = F.FIGURES + [{"images": [("layout", n)]} for n in (
        "20_labels_v3",                                     # KB §69.146
        "11_global60_depressions", "19_channels_vs_valleys", "14_validation")]   # KB §69.147


M.I = _Figures
# The paper gives their tables' numbers in its text, so the tables are hidden like the prose: 19's cells, which Pro
# renamed "t5_1 1" when the sheet got a second table; 14's table (v_c<row>_<col>, its labels, bands and rule); 19's
# line of counts and second table's title. None of final.py's layouts has such an element (checked 2026-11-17,
# KB §69.147). 14's legend names the review field that records who traced each margin; the caption says it.
M.TABLE_CELL = re.compile(r"t\d+_\d+(_bg)?( \d+)?$|v_(c\d+_\d+|l\d+|h\d*|band\d+|rule)$|counts$|table2_title$")
M.PLAIN_NAMES = M.PLAIN_NAMES + [(re.compile(r"\s*\(MappedBy says who\)"), "")]
M.OUT = os.path.join(HERE, "final_img")     # where: its own folder

# The final's own changes, in memory like the hidden prose, so the interim's figures stay as they are (KB §69.69).
# On the four-panel sheets the hidden captions left blank bands beside and between the panels, which shrank the
# maps on the paper's page: 15's key moves beside panel B, as the scale bar sits beside D, and every blank band
# wider than GUTTER is cut to it.
MOVE = {"15_athabasca_type_area": {"lav_swatch": 8.76, "lav_key": 9.20}}    # x, in inches
COMPACT = {"08_global60_mosaic", "15_athabasca_type_area"}
GUTTER = 60                                 # px at 200 dpi (0.3 in)

_plain_names, _trim = M.plain_names, M.trim


def plain_names(lyt):
    _plain_names(lyt)
    for e in lyt.listElements():
        x = MOVE.get(lyt.name, {}).get(e.name)
        if x is not None:
            e.elementPositionX = x


def keep(blank):
    """False on the inner part of every blank run longer than GUTTER, so GUTTER px of it remain."""
    k = np.ones(len(blank), bool)
    i = 0
    while i < len(blank):
        j = i
        while j < len(blank) and blank[j]:
            j += 1
        if j - i > GUTTER:
            k[i + GUTTER // 2:j - (GUTTER - GUTTER // 2)] = False
        i = max(j, i + 1)
    return k


def trim(path):
    size = _trim(path)
    if os.path.basename(path)[:-4] not in COMPACT:
        return size
    a = np.asarray(Image.open(path).convert("RGB"))
    white = (a >= 250).all(axis=2)
    a = a[keep(white.all(axis=1))][:, keep(white.all(axis=0))]
    Image.fromarray(a).save(path, optimize=True)
    return a.shape[1], a.shape[0]


M.plain_names, M.trim = plain_names, trim

if __name__ == "__main__":
    M.main()
