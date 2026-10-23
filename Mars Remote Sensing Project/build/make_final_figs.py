# -*- coding: utf-8 -*-
r"""Exports the layouts the final paper and deck show to build\final_img\ (NEXT-STEPS.md §7).

The same export as the interim's (make_interim_figs.py: 200 dpi, the sheet's prose hidden in memory, trimmed, a map
and a legend split out where the sheet has one), pointed at final.py's FIGURES and its own folder, so the interim's
crops in interim_img\ are never touched. The .aprx is opened, never saved; Pro may be open.

  <ArcGIS Pro Python> make_final_figs.py [--only 15_athabasca_type_area,17_x5c_unet_provinces]
  (desktop: D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe)

The charts drawn from logs come from make_fig_final.py (system Python).
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_interim_figs as M
import final as F

M.I = F                                     # which layouts: final.py's FIGURES
M.OUT = os.path.join(HERE, "final_img")     # where: its own folder

if __name__ == "__main__":
    M.main()
