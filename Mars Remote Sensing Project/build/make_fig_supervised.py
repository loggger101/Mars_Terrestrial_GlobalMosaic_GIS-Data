# -*- coding: utf-8 -*-
r"""Figure: task 7's supervised half, with the accuracy assessment made visible
- including the comparison that does NOT support the easy story.

A  the supervised classification on his 5-band composite
B  the spatial train/test split - the thing that makes the number honest
C  confusion matrix on held-out blocks, spectral stack
D  three stacks compared, with the circular one marked as such

Reads Z:\TypeArea\ius_sup_spectral.tif and sup_confusion.npy from
make_typearea_supervised.py (order: spectral, thermal, augmented).
"""
import os, numpy as np
from osgeo import gdal
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
gdal.UseExceptions()

WS = r"Z:\TypeArea"
P = lambda n: os.path.join(WS, n)
LON0, LON1, LAT0, LAT1 = 271.0, 286.0, -13.0, -6.0
BG, CY, SUB, WARN = "#0E2841", "#0E9ED4", "#9ED8ED", "#E8804A"
W = 1150
NAMES = ["crater interior", "wall steep", "wall moderate",
         "chasma floor", "plateau flank", "plateau"]
COLS = ["#C4553B", "#5B3A8C", "#2E7BB8", "#14A88A", "#C8A23C", "#9EA9B5"]
NBX, NBY = 10, 6


def read(p, w=W):
    ds = gdal.Open(p)
    b = ds.GetRasterBand(1)
    h = int(w * ds.RasterYSize / ds.RasterXSize)
    a = b.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, buf_xsize=w,
                      buf_ysize=h, resample_alg=gdal.GRIORA_NearestNeighbour)
    del b, ds
    return a.astype(np.float32)


# ClassifyRaster is 0-indexed; +1 recovers the Classvalue (see KB 27)
cls = read(P("ius_sup_spectral.tif")) + 1.0
cls = np.where(cls > 6.5, np.nan, cls)
cms = np.load(P("sup_confusion.npy"))          # spectral, thermal, augmented
oas = [np.trace(c) / c.sum() for c in cms]
ext = [LON0, LON1, LAT0, LAT1]

fig = plt.figure(figsize=(13.4, 12.2), facecolor=BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1.24, 1.0], hspace=0.42, wspace=0.34)

# ---- A  the classification
axA = fig.add_subplot(gs[0, :])
axA.imshow(cls, cmap=ListedColormap(COLS), vmin=0.5, vmax=6.5, extent=ext,
           aspect="auto", interpolation="nearest")
axA.set_title("A   Supervised classification of the 5-band composite  \u2014  Random Trees, "
              "training labels from terrain only",
              color=CY, fontsize=12.5, pad=9, loc="left")
axA.set_xlabel("East longitude (\u00b0)", color=SUB)
axA.set_ylabel("Latitude (\u00b0)", color=SUB)
axA.legend(handles=[plt.Line2D([], [], marker="s", ls="", ms=8, mfc=c, mec="none", label=n)
                    for c, n in zip(COLS, NAMES)],
           ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.145), frameon=False,
           labelcolor=SUB, fontsize=9, handletextpad=0.4, columnspacing=1.4)

# ---- B  the spatial split
axB = fig.add_subplot(gs[1, 0])
by = (np.arange(NBY * 9) * NBY // (NBY * 9))[:, None]
bx = (np.arange(NBX * 9) * NBX // (NBX * 9))[None, :]
axB.imshow(((by + bx) % 2 == 0).astype(float), cmap=ListedColormap(["#16324B", CY]),
           extent=ext, aspect="auto", interpolation="nearest")
axB.set_title("B   Train / test are spatial blocks", color=CY, fontsize=11.5,
              pad=9, loc="left")
axB.set_xlabel("East longitude (\u00b0)", color=SUB)
axB.text(0.0, -0.20, "A random pixel split would sit a test pixel next\n"
                     "to its own training pixel and inflate every\nnumber here.",
         transform=axB.transAxes, color=SUB, fontsize=8.3, va="top")

# ---- C  confusion matrix, spectral
axC = fig.add_subplot(gs[1, 1])
cm = cms[0].astype(float)
row = cm.sum(1, keepdims=True)
norm = np.divide(cm, np.where(row == 0, 1, row))
axC.imshow(norm, cmap="magma", vmin=0, vmax=1)
axC.set_xticks(range(6)); axC.set_yticks(range(6))
axC.set_xticklabels(NAMES, rotation=42, ha="right", fontsize=7.2, color=SUB)
axC.set_yticklabels(NAMES, fontsize=7.2, color=SUB)
for i in range(6):
    for j in range(6):
        if norm[i, j] >= 0.005:
            axC.text(j, i, "%.0f" % (100 * norm[i, j]), ha="center", va="center",
                     fontsize=7.2, color="white" if norm[i, j] < 0.55 else "#1A1008")
axC.set_xlabel("predicted   (rows = actual, % of row)", color=SUB, fontsize=8.6)
axC.set_title("C   Confusion, spectral \u2014 OA %.1f%%" % (100 * oas[0]),
              color=CY, fontsize=11.5, pad=9, loc="left")

# ---- D  the three stacks
axD = fig.add_subplot(gs[1, 2])
labels = ["5-band\ncomposite", "+ diurnal\ncontrast", "+ contrast\nAND slope"]
bars = axD.bar(range(3), [100 * o for o in oas],
               color=[CY, CY, WARN], edgecolor="#2A4A66")
axD.set_xticks(range(3))
axD.set_xticklabels(labels, fontsize=8.4, color=SUB)
axD.set_ylabel("overall accuracy (%)", color=SUB)
axD.set_ylim(0, 100)
for i, o in enumerate(oas):
    axD.text(i, 100 * o + 2, "%.1f%%" % (100 * o), ha="center", color="white", fontsize=9.5)
axD.annotate("", xy=(1, 100 * oas[1] - 6), xytext=(0, 100 * oas[0] - 6),
             arrowprops=dict(arrowstyle="->", color="white", lw=1.2))
axD.text(0.5, 100 * oas[0] - 16, "+%.1f pt" % (100 * (oas[1] - oas[0])),
         ha="center", color="white", fontsize=9)
axD.text(0.02, 0.985, "the orange bar is CIRCULAR:\nslope is both a band and a\nlabel input, so read it as an\nupper bound, not a result.",
         transform=axD.transAxes, ha="left", va="top", color=WARN, fontsize=8.2)
axD.set_title("D   What each band buys", color=CY, fontsize=11.5, pad=9, loc="left")

for a in fig.axes:
    a.set_facecolor(BG)
    a.tick_params(colors=SUB, labelsize=8.4)
    for sp in a.spines.values():
        sp.set_color("#2A4A66")

fig.suptitle("Ius Chasma \u00b7 task 7 supervised \u00b7 the thermal index adds +0.4 pt to a "
             "TERRAIN task \u2014 exactly as \u00a724 predicts",
             color="white", fontsize=14, y=0.977, x=0.055, ha="left")
fig.tight_layout(rect=[0, 0.035, 1, 0.955])
out = r"Z:\Mars Remote Sensing Project\build\pres1_img\ius_supervised.png"
fig.savefig(out, dpi=115, facecolor=BG)
print("wrote", out)
print("OA  spectral %.1f%%   thermal %.1f%%   augmented %.1f%%"
      % tuple(100 * o for o in oas))
