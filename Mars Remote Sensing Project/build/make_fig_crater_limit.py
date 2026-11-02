# -*- coding: utf-8 -*-
r"""Figure for the paper (NEXT-STEPS §12.4 W4): the closed-depression detector's limit, on the two named craters it was
tuned on (KB §26.3, §26.4).

Two panels, the windows verify_crater_detection.py built around each crater (TypeArea\val\<crater>_dem.tif and
_depth.tif, depth = Fill − DEM): the DEM in grey, every closed depression deeper than 20 m coloured by its depth, and
the IAU rim as a dashed circle. Perrotin (82.8 km) is a closed basin and is found at 77.0 km (−7.1 %), ranked first of
1,321 candidates; Oudemans (124.2 km) is breached, its lowest rim point 33 m below its floor, so Fill leaves it empty
and the detector cannot see it. The same drawing as panels C and D of make_fig_craters.py (the interim's figure), on the
paper's light ground with a depth scale instead of a title note. Reads the drive (two small windows); writes
build\final_img\crater_limit.png. ArcGIS Python (GDAL).
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from osgeo import gdal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive

gdal.UseExceptions()
VAL = on_drive(r"Mars Project\TypeArea\val")
OUT = os.path.join(HERE, "final_img", "crater_limit.png")
R = 3396190.0
DEG = R * np.pi / 180.0
INK, MUTED, EDGE = "#0b0b0b", "#52514e", "#d9dee3"
FOUND, MISSED = "#2a78d6", "#eb6834"
DEPTH_MIN, DEPTH_MAX = 20, 400
# name, IAU diameter (km), centre (°E, °N), found, the note (KB §26.3)
CRATERS = [("oudemans", "Oudemans", 124.2, 268.23, -9.84, False,
            "Missed: the rim is breached, its lowest\npoint 33 m below the floor, so Fill\nleaves no closed basin"),
           ("perrotin", "Perrotin", 82.8, 282.06, -2.82, True,
            "Found at 77.0 km (−7.1 %), first of\n1,321 candidates in its window")]


def read(p, w=700):
    """The window averaged down to w columns, with its extent in degrees (the grid is CM180, metres)."""
    ds = gdal.Open(p)
    h = int(w * ds.RasterYSize / ds.RasterXSize)
    a = ds.GetRasterBand(1).ReadAsArray(buf_xsize=w, buf_ysize=h, resample_alg=gdal.GRIORA_Average)
    gt = ds.GetGeoTransform()
    ext = [180.0 + gt[0] / DEG, 180.0 + (gt[0] + gt[1] * ds.RasterXSize) / DEG,
           (gt[3] + gt[5] * ds.RasterYSize) / DEG, gt[3] / DEG]
    return a.astype(np.float32), ext


plt.rcParams.update({"font.family": "Arial", "font.size": 9})
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.9), dpi=200)
for ax, (key, name, dia, lo, la, found, note) in zip(axes, CRATERS):
    dem, ext = read(os.path.join(VAL, "%s_dem.tif" % key))
    dep, ext2 = read(os.path.join(VAL, "%s_depth.tif" % key))
    assert np.allclose(ext, ext2, atol=1e-6), "the DEM and depth windows differ"
    dem = np.where(dem < -32000, np.nan, dem)
    ax.imshow(dem, cmap="gray", extent=ext, interpolation="bilinear")
    im = ax.imshow(np.where(dep > DEPTH_MIN, dep, np.nan), cmap="YlOrRd", extent=ext, vmin=0, vmax=DEPTH_MAX,
                   alpha=0.9, interpolation="nearest")
    col = FOUND if found else MISSED
    ax.add_patch(Circle((lo, la), dia / 2.0 / (DEG / 1000.0), fill=False, edgecolor=col, lw=1.6, ls=(0, (4, 2.5))))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_aspect("equal")              # or the IAU circle draws as an ellipse
    ax.set_title("%s, %.0f km: %s" % (name, dia, "found" if found else "missed"), loc="left", color=INK, fontsize=10)
    ax.text(0.03, 0.03, note, transform=ax.transAxes, fontsize=7.5, color=INK, va="bottom", ha="left",
            bbox=dict(boxstyle="square,pad=0.35", fc="white", ec=col, lw=0.8, alpha=0.92))
    ax.set_xlabel("East longitude (°)", color=MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    for sp in ax.spines.values():
        sp.set_color(EDGE)
axes[0].set_ylabel("Latitude (°)", color=MUTED)
fig.subplots_adjust(left=0.08, right=0.88, bottom=0.13, top=0.92, wspace=0.18)
cax = fig.add_axes([0.905, 0.2, 0.018, 0.62])
cb = fig.colorbar(im, cax=cax)
cb.set_label("closed-depression depth, m (Fill − DEM; > %d m)" % DEPTH_MIN, color=MUTED, fontsize=7.5)
cb.ax.tick_params(colors=MUTED, labelsize=7)
cb.outline.set_edgecolor(EDGE)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
