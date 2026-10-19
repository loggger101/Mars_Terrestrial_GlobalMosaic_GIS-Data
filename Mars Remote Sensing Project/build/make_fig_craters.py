# -*- coding: utf-8 -*-
r"""Figure: closed depressions >= 1 km over Ius Chasma (crater candidates), their size-frequency
distribution the gazetteer cannot give, and the validation - including the
failure.

A  candidates on the hillshade, scaled by diameter
B  cumulative size-frequency distribution, log-log
C  Oudemans - detector MISS, and why: the rim is breached
D  Perrotin - detector hit, -7.1% on diameter

--light writes the repo's light version to interim_img\ (KB §65). The candidates are closed depressions,
not a crater count (§42.3: 11 % of them match a Robbins crater); the titles say so.
"""
import os, numpy as np, arcpy
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
from osgeo import gdal
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
gdal.UseExceptions()

WS = on_drive(r"Mars Project\TypeArea")      # the junction holds one drive letter (KB §58)
VAL = os.path.join(WS, "val")
FC = on_drive(r"Mars Project\Mars Project.gdb\Landform_CraterCandidates_auto")
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
WARN = "#E8804A" if not LIGHT else "#eb6834"
W = 1200


def read(p, w=W):
    ds = gdal.Open(p)
    b = ds.GetRasterBand(1)
    h = int(w * ds.RasterYSize / ds.RasterXSize)
    a = b.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize, buf_xsize=w,
                      buf_ysize=h, resample_alg=gdal.GRIORA_Average).astype(np.float32)
    gt = ds.GetGeoTransform()
    sx = ds.RasterXSize / float(w)
    del b, ds
    return a, gt, sx


hs, _, _ = read(os.path.join(WS, "ius_hillshade.tif"))
rows = [r for r in arcpy.da.SearchCursor(FC, ["CenterLon", "CenterLat", "DiameterKm",
                                              "DepthMaxM", "ThermIdx"])]
lon = np.array([r[0] for r in rows]); lat = np.array([r[1] for r in rows])
dia = np.array([r[2] for r in rows]); dep = np.array([r[3] for r in rows])
print("%d candidates" % len(rows))

fig = plt.figure(figsize=(12.8, 12.6), facecolor=BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1.30, 1.0], hspace=0.30, wspace=0.26)

# ---- A  the map
axA = fig.add_subplot(gs[0, :])
axA.imshow(hs, cmap="gray", extent=[LON0, LON1, LAT0, LAT1], aspect="auto",
           vmin=0, vmax=255, alpha=0.9)
sc = axA.scatter(lon, lat, s=np.clip(dia ** 1.7 * 1.1, 2, 900),
                 facecolor="none", edgecolor=ACC if not LIGHT else "#ff00c5", linewidth=0.7, alpha=0.85)
axA.set_xlim(LON0, LON1); axA.set_ylim(LAT0, LAT1)
axA.set_title("A   {:,} closed depressions \u2265 1 km in the DEM, circle scaled by diameter; "
              "11% match a catalogued crater".format(len(rows)),
              color=CY, fontsize=12.5, pad=9, loc="left")

# ---- B  size-frequency
axB = fig.add_subplot(gs[1, 0])
d = np.sort(dia)
cum = np.arange(len(d), 0, -1)
area_km2 = (LON1 - LON0) * DEG / 1000.0 * (LAT1 - LAT0) * DEG / 1000.0 * np.cos(np.radians(9.5))
axB.loglog(d, cum / area_km2 * 1e6, color=ACC, lw=1.9)
axB.axvline(1.0, color=WARN, lw=1.2, ls="--")
axB.text(1.08, axB.get_ylim()[0] * 3.0, "1 km \u2014 the project's\nown resolving limit",
         color=WARN, fontsize=8.5, va="bottom")   # bottom left: clear of the curve
axB.set_xlabel("diameter (km)", color=SUB)
axB.set_ylabel("cumulative N per 10$^6$ km$^2$", color=SUB)
axB.set_title("B   Size-frequency of the depressions", color=CY, fontsize=12, pad=9, loc="left")
axB.grid(alpha=0.14, color=SUB)

# ---- C, D  the two validation windows
truth = {"oudemans": ("Oudemans", 124.2, 268.23, -9.84, False),
         "perrotin": ("Perrotin", 82.8, 282.06, -2.82, True)}
for k, (key, (nm, tdia, tlo, tla, hit)) in enumerate(truth.items()):
    ax = fig.add_subplot(gs[1, 1 + k])
    demp = os.path.join(VAL, "%s_dem.tif" % key)
    depp = os.path.join(VAL, "%s_depth.tif" % key)
    if not (os.path.exists(demp) and os.path.exists(depp)):
        ax.text(0.5, 0.5, "window not built", color=SUB, ha="center")
        continue
    dm, gt, _ = read(demp, 700)
    dp, _, _ = read(depp, 700)
    nx, ny = dm.shape[1], dm.shape[0]
    x0 = 180.0 + gt[0] / DEG
    x1 = 180.0 + (gt[0] + gt[1] * nx * (gdal.Open(demp).RasterXSize / float(nx))) / DEG
    y1 = gt[3] / DEG
    y0 = (gt[3] + gt[5] * gdal.Open(demp).RasterYSize) / DEG
    ext = [x0, x1, y0, y1]
    dm = np.where(dm < -32000, np.nan, dm)
    ax.imshow(dm, cmap="gray", extent=ext, aspect="auto")
    ax.imshow(np.where(dp > 20, dp, np.nan), cmap="YlOrRd", extent=ext,
              aspect="auto", vmin=0, vmax=400, alpha=0.85)
    rad_deg = (tdia / 2.0) / (DEG / 1000.0)
    ax.add_patch(Circle((tlo, tla), rad_deg, fill=False, edgecolor=ACC, lw=1.8, ls="--"))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    # equal aspect, or the dashed IAU circle renders as an ellipse and reads as
    # a claim about the crater's shape
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("%s   %s \u2014 IAU %.0f km   %s"
                 % ("CD"[k], nm, tdia, "HIT  \u22127.1%" if hit else "MISS"),
                 color=ACC if hit else WARN, fontsize=11.5, pad=9, loc="left")
    ax.text(0.03, 0.04,
            ("detected as the largest\ncandidate in its window"
             if hit else "rim breached \u2014 lowest rim\npoint 33 m BELOW the floor,\nso it is not a closed basin"),
            transform=ax.transAxes, color="white", fontsize=8.2, va="bottom",
            bbox=dict(boxstyle="round,pad=0.35", fc="#0E2841", ec=ACC if hit else WARN, alpha=0.9))

for a in fig.axes:
    a.set_facecolor(BG)
    a.tick_params(colors=SUB, labelsize=8.5)
    for sp in a.spines.values():
        sp.set_color(EDGE)
axA.set_xlabel("East longitude (\u00b0)", color=SUB)
axA.set_ylabel("Latitude (\u00b0)", color=SUB)

fig.suptitle("Ius Chasma \u00b7 closed depressions, not a crater count \u00b7 "
             "C, D: yellow\u2013red = depth (fill \u2212 DEM)",
             color=HEAD, fontsize=14, y=0.977, x=0.075, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.957])
out = os.path.join(IMG_DIR, "ius_crater_candidates.png")
fig.savefig(out, dpi=115, facecolor=BG)
print("wrote", out)
