# -*- coding: utf-8 -*-
r"""Figure: the diurnal-contrast index over Ius Chasma, and the case that it
is a MATERIAL discriminator rather than a restatement of topography.

Three panels:
  A  the index itself, mapped
  B  mean index per object-based class, sorted
  C  slope vs index per class - the decoupling argument in one plot

Reads <drive>\TypeArea\ius_thermal_contrast.tif (make_typearea_thermal.py). --light writes the repo's
light version to interim_img\ (KB §65). The index is relative (8-bit DN, each band stretched on its own)
and at ~3 km does not track calibrated TES inertia (§42.4): the titles say what the panels show, no more.
"""
import os, numpy as np
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
from osgeo import gdal
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
gdal.UseExceptions()

OUT = on_drive(r"Mars Project\TypeArea")      # the junction holds one drive letter (KB §58)
P = lambda n: os.path.join(OUT, n)
LON0, LON1, LAT0, LAT1 = 271.0, 286.0, -13.0, -6.0
# --light (KB §65): the repo's light style, written to interim_img\ beside the other result charts;
# without it, Presentation 1's navy original in pres1_img\. Wording follows the record in both.
LIGHT = "--light" in sys.argv
if LIGHT:
    BG, TITLE, SUB, EDGE, HEAD, ACC = "white", "#1A1A1A", "#5A6570", "#D9DEE3", "#1A1A1A", "#2a78d6"
else:
    BG, TITLE, SUB, EDGE, HEAD, ACC = "#0E2841", "#0E9ED4", "#9ED8ED", "#2A4A66", "white", "#0E9ED4"
CY = TITLE
IMG_DIR = on_drive(r"Mars Remote Sensing Project\build\%s" % ("interim_img" if LIGHT else "pres1_img"))
W = 1200


def read(path, dec=True):
    ds = gdal.Open(path)
    b = ds.GetRasterBand(1)
    if dec:
        h = int(W * ds.RasterYSize / ds.RasterXSize)
        a = b.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, buf_xsize=W,
                          buf_ysize=h, resample_alg=gdal.GRIORA_Average)
    else:
        a = b.ReadAsArray()
    nod = b.GetNoDataValue()
    del b, ds
    return a.astype(np.float32), nod


idx, inod = read(P("ius_thermal_contrast.tif"))
idx = np.where(idx <= -999, np.nan, idx)

# full-res class statistics (cheap enough; 37 Mpx)
cls, _ = read(P("ius_obj_medium.tif"), dec=False)
ful, _ = read(P("ius_thermal_contrast.tif"), dec=False)
slp, _ = read(P("ius_slope_deg.tif"), dec=False)
dem, _ = read(P("ius_dem.tif"), dec=False)
m = (cls > 0) & (ful > -999) & np.isfinite(slp) & (slp > -1e30) & (dem > -32000)
c = cls[m].astype(np.int32)
v = ful[m].astype(np.float64)
s = slp[m].astype(np.float64)
e = dem[m].astype(np.float64)
del cls, ful, slp, dem

rows = []
for k in np.unique(c):
    sel = c == k
    rows.append(dict(k=int(k), n=int(sel.sum()), idx=v[sel].mean(),
                     sd=v[sel].std(), slope=s[sel].mean(), elev=e[sel].mean()))
rows.sort(key=lambda r: r["idx"])
frac = np.array([r["n"] for r in rows], float)
frac /= frac.sum()

fig = plt.figure(figsize=(12.6, 12.0), facecolor=BG)
gs = fig.add_gridspec(2, 2, height_ratios=[1.32, 1.0], hspace=0.30, wspace=0.26)

# ---- A  the map
axA = fig.add_subplot(gs[0, :])
vmax = np.nanpercentile(np.abs(idx), 97)
im = axA.imshow(idx, cmap="RdBu_r", vmin=-vmax, vmax=vmax,
                extent=[LON0, LON1, LAT0, LAT1], aspect="auto")
axA.set_title("A   Diurnal-contrast index  \u2014  scaled(day IR) \u2212 scaled(night IR)",
              color=CY, fontsize=13, pad=9, loc="left")
axA.set_xlabel("East longitude (\u00b0)", color=SUB)
axA.set_ylabel("Latitude (\u00b0)", color=SUB)
cb = fig.colorbar(im, ax=axA, orientation="horizontal", fraction=0.045,
                  pad=0.115, aspect=55)
cb.ax.tick_params(colors=SUB, labelsize=9)
cb.outline.set_color(EDGE)
cb.set_label("←  damped: rock, coarse debris           large day–night swing: dust-like  →",
             color=SUB, fontsize=9.5, labelpad=6)

# ---- B  per-class means
axB = fig.add_subplot(gs[1, 0])
y = np.arange(len(rows))
cols = plt.cm.RdBu_r(plt.Normalize(-0.5, 0.5)([r["idx"] for r in rows]))
axB.barh(y, [r["idx"] for r in rows], color=cols, edgecolor=EDGE, height=0.72)
axB.set_yticks(y)
axB.set_yticklabels(["class %d  (%.0f%%)" % (r["k"], 100 * f) for r, f in zip(rows, frac)],
                    color=SUB, fontsize=9)
axB.axvline(0, color=SUB, lw=0.8)
axB.set_xlabel("mean diurnal-contrast index", color=SUB)
axB.set_title("B   Mean index per object-based class (14/14/30)", color=CY, fontsize=12,
              pad=9, loc="left")

# ---- C  the decoupling
axC = fig.add_subplot(gs[1, 1])
sizes = 40 + 1400 * frac
sc = axC.scatter([r["slope"] for r in rows], [r["idx"] for r in rows], s=sizes,
                 c=[r["idx"] for r in rows], cmap="RdBu_r", vmin=-0.5, vmax=0.5,
                 edgecolor="white", linewidth=0.9, zorder=3)
for r in rows:
    axC.annotate(str(r["k"]), (r["slope"], r["idx"]),
                 color="white" if abs(r["idx"]) > 0.16 else "#0E2841", fontsize=8,
                 ha="center", va="center", zorder=4)
# the pair that makes the argument: same steepness, opposite index
a = next(r for r in rows if r["k"] == 2)
b = next(r for r in rows if r["k"] == 8)
axC.annotate("", xy=(b["slope"], b["idx"]), xytext=(a["slope"], a["idx"]),
             arrowprops=dict(arrowstyle="<->", color=ACC, lw=1.4, ls="--"), zorder=2)
axC.text(0.55, 0.30, "the two steepest classes:\n%.1f\u00b0 apart in slope,\n%.2f apart in index"
         % (abs(a["slope"] - b["slope"]), abs(a["idx"] - b["idx"])),
         transform=axC.transAxes, color=ACC, fontsize=8.5, va="center", ha="left")
axC.axhline(0, color=SUB, lw=0.8)
axC.set_xlabel("mean slope (\u00b0)", color=SUB)
axC.set_ylabel("mean diurnal-contrast index", color=SUB)
axC.set_title("C   Index against slope: same steepness, opposite sign", color=CY, fontsize=12, pad=9, loc="left")
axC.text(0.985, 0.035, "marker area ∝ class area", transform=axC.transAxes,
         color=SUB, fontsize=8, ha="right")

for a_ in (axA, axB, axC):
    a_.set_facecolor(BG)
    a_.tick_params(colors=SUB, labelsize=9)
    for sp in a_.spines.values():
        sp.set_color(EDGE)

fig.suptitle("Ius Chasma, 271\u2013286\u00b0E, 13\u20136\u00b0S  \u00b7  a relative index from 8-bit DN, "
             "not calibrated thermal inertia (KB \u00a724)",
             color=HEAD, fontsize=14, y=0.977, x=0.085, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.958])
out = os.path.join(IMG_DIR, "ius_thermal_contrast.png")
fig.savefig(out, dpi=115, facecolor=BG)
print("wrote", out)
print("class order (coldest index first):",
      " ".join("%d(%+.2f)" % (r["k"], r["idx"]) for r in rows))
