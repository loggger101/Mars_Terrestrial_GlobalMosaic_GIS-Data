# -*- coding: utf-8 -*-
"""Segmentation parameter sweep, shown on a zoom across the Ius Chasma wall."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import numpy as np
from osgeo import gdal
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
gdal.UseExceptions()

TA = r"Z:\TypeArea"
X, Y, W, H = 3400, 1100, 1700, 1100          # wall + tributary fans + plateau
PAL = ["#8ecae6", "#219ebc", "#023047", "#ffb703", "#fb8500",
       "#d62828", "#7209b7", "#4361ee", "#43aa8b", "#b5179e"]

def win(fn, band=1):
    ds = gdal.Open(fn if "\\" in fn else TA + "\\" + fn)
    a = ds.GetRasterBand(band).ReadAsArray(X, Y, W, H)
    ds = None
    return a

day = win("ius_day.tif").astype(np.float32)
p1, p2 = np.percentile(day, [1, 99]); shade = np.clip((day - p1) / (p2 - p1), 0, 1)

PANELS = [("ius_isocluster_10.tif", "Per-pixel  \u2014  no segmentation",
           "43.1% boundary pixels, mean run 5.0 px"),
          ("ius_obj_fine.tif",      "Object-based  \u2014  spectral 20 / spatial 20 / min 5 px",
           "the Mercury rehearsal settings: maximum detail. 35.2%, run 6.9 px"),
          ("ius_obj_medium.tif",    "Object-based  \u2014  14 / 14 / min 30 px",
           "13.0% boundary pixels, mean run 18.6 px \u2248 1.9 km"),
          ("ius_obj_coarse.tif",    "Object-based  \u2014  9 / 9 / min 80 px",
           "6.4%, mean run 37.3 px \u2248 3.7 km \u2014 below the project's own 1 km mapping limit")]

BG, CY, SUB = "#0E2841", "#0E9ED4", "#9ED8ED"
cmap = ListedColormap(PAL); norm = BoundaryNorm(np.arange(0.5, 11.5, 1), 10)
fig, ax = plt.subplots(2, 2, figsize=(13.2, 9.4), facecolor=BG)
for a, (fn, ttl, sub) in zip(ax.ravel(), PANELS):
    a.imshow(shade, cmap="gray")
    a.imshow(np.ma.masked_less(win(fn), 1), cmap=cmap, norm=norm, alpha=0.70)
    a.set_title(ttl, color=CY, fontsize=11, pad=7, loc="left")
    a.text(0.0, -0.045, sub, transform=a.transAxes, color=SUB, fontsize=8.6, va="top")
    a.set_xticks([]); a.set_yticks([]); a.set_facecolor(BG)
    for s in a.spines.values(): s.set_color("#2A4A66")
fig.suptitle("Segmentation detail controls the result far more than the classifier does",
             color="white", fontsize=15, x=0.012, ha="left", y=0.985)
fig.tight_layout(rect=[0, 0.005, 1, 0.955], h_pad=3.0, w_pad=1.6)
out = r"Z:\Mars Remote Sensing Project\build\pres1_img\ius_segmentation_sweep.png"
fig.savefig(out, dpi=112, facecolor=BG); print("wrote", out)
