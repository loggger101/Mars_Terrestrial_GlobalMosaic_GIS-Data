# -*- coding: utf-8 -*-
r"""Figure: candidate channel centrelines over Ius Chasma, triaged thermally,
with the filled-basin exclusion shown rather than hidden.

Panel A  the candidates on a hillshade, coloured by diurnal-contrast index
Panel B  what Fill did, and why 56% of the first network was thrown away

--light writes the repo's light version to interim_img\ (KB §65). B's flooded share and depth are read
from ius_filldepth.tif at full resolution (> 1 m, as §25.1 counts it); the title had said "23%" against
the record's 21.8 %.
"""
import os, numpy as np, arcpy
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
from osgeo import gdal
import matplotlib; matplotlib.use("Agg")
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
gdal.UseExceptions()

WS = on_drive(r"Mars Project\TypeArea")      # the junction holds one drive letter (KB §58)
FC = on_drive(r"Mars Project\Mars Project.gdb\Landform_ChannelCandidates_auto")
R = 3396190.0
DEG = R * np.pi / 180.0
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


def read(p):
    ds = gdal.Open(p)
    b = ds.GetRasterBand(1)
    h = int(W * ds.RasterYSize / ds.RasterXSize)
    a = b.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, buf_xsize=W,
                      buf_ysize=h, resample_alg=gdal.GRIORA_Average).astype(np.float32)
    del b, ds
    return a


hs = read(os.path.join(WS, "ius_hillshade.tif"))
fd = read(os.path.join(WS, "ius_filldepth.tif"))
_ds = gdal.Open(os.path.join(WS, "ius_filldepth.tif"))
_full = _ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
_ok = np.isfinite(_full) & (_full > -1e30)
FLOODED = float(((_full > 1.0) & _ok).sum()) / float(_ok.sum())
MAXRAISE = float(_full[_ok].max())
del _ds, _full, _ok
print("raised > 1 m: %.1f %%, max %.0f m" % (100 * FLOODED, MAXRAISE))
fd = np.where(fd > 1.0, fd, np.nan)

segs, vals, lens = [], [], []
with arcpy.da.SearchCursor(FC, ["SHAPE@", "ThermIdx", "LengthKm"]) as c:
    for shp, ti, km in c:
        for part in shp:
            pts = [(180.0 + p.X / DEG, p.Y / DEG) for p in part if p]
            if len(pts) > 1:
                segs.append(pts)
                vals.append(np.nan if ti is None else ti)
                lens.append(km)
vals = np.array(vals, float)
print("plotting %d candidate lines, %.0f km" % (len(segs), sum(lens)))

ext = [LON0, LON1, LAT0, LAT1]
fig, ax = plt.subplots(2, 1, figsize=(12.6, 12.4), facecolor=BG)

# ---- A
ax[0].imshow(hs, cmap="gray", extent=ext, aspect="auto", vmin=0, vmax=255, alpha=0.85)
lc = LineCollection(segs, cmap="RdBu_r", linewidths=np.clip(np.array(lens) / 7.0, 0.35, 2.4))
lc.set_array(vals)
lc.set_clim(-0.35, 0.35)
ax[0].add_collection(lc)
ax[0].set_xlim(LON0, LON1); ax[0].set_ylim(LAT0, LAT1)
ax[0].set_title("A   %d candidate centrelines, %,.0f km \u2014 coloured by diurnal-contrast index"
                .replace("%,.0f", "{:,.0f}".format(sum(lens))) % len(segs),
                color=CY, fontsize=13, pad=9, loc="left")
cb = fig.colorbar(lc, ax=ax[0], orientation="horizontal", fraction=0.043, pad=0.115, aspect=55)
cb.ax.tick_params(colors=SUB, labelsize=9)
cb.outline.set_color(EDGE)
cb.set_label("\u2190  damped floor: rock / lava?            mantled floor: fines  \u2192",
             color=SUB, fontsize=9.5, labelpad=6)

# ---- B
ax[1].imshow(hs, cmap="gray", extent=ext, aspect="auto", vmin=0, vmax=255, alpha=0.5)
im = ax[1].imshow(fd, cmap="magma", extent=ext, aspect="auto", vmin=0, vmax=800)
ax[1].set_title("B   What Fill flooded \u2014 %.1f%% of the scene raised > 1 m, up to %s m. "
                "56.1%% of the first network ran across it and was discarded."
                % (100 * FLOODED, "{:,.0f}".format(MAXRAISE)),
                color=CY, fontsize=12, pad=9, loc="left")
cb2 = fig.colorbar(im, ax=ax[1], orientation="horizontal", fraction=0.043, pad=0.115, aspect=55)
cb2.ax.tick_params(colors=SUB, labelsize=9)
cb2.outline.set_color(EDGE)
cb2.set_label("depth of synthetic fill (m)", color=SUB, fontsize=9.5, labelpad=6)

for a in ax:
    a.set_facecolor(BG)
    a.set_xlabel("East longitude (\u00b0)", color=SUB)
    a.set_ylabel("Latitude (\u00b0)", color=SUB)
    a.tick_params(colors=SUB, labelsize=9)
    for sp in a.spines.values():
        sp.set_color(EDGE)

fig.suptitle("Ius Chasma \u00b7 candidate channels are inferred, not mapped \u00b7 "
             "Landform_ChannelCandidates_auto (KB §25)",
             color=HEAD, fontsize=15, y=0.978, x=0.075, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.958])
out = os.path.join(IMG_DIR, "ius_channel_candidates.png")
fig.savefig(out, dpi=115, facecolor=BG)
print("wrote", out)
