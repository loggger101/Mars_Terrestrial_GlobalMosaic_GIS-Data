# -*- coding: utf-8 -*-
r"""Figure: candidate craters for the Ius Chasma type area, the size-frequency
distribution the gazetteer cannot give, and the validation - including the
failure.

A  candidates on the hillshade, scaled by diameter
B  cumulative size-frequency distribution, log-log
C  Oudemans - detector MISS, and why: the rim is breached
D  Perrotin - detector hit, -7.1% on diameter
"""
import os, numpy as np, arcpy
from osgeo import gdal
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
gdal.UseExceptions()

WS = r"Z:\TypeArea"
VAL = os.path.join(WS, "val")
FC = r"Z:\Mars Project\Mars Project.gdb\Landform_CraterCandidates_auto"
R = 3396190.0
DEG = R * np.pi / 180.0
LON0, LON1, LAT0, LAT1 = 271.0, 286.0, -13.0, -6.0
BG, CY, SUB, WARN = "#0E2841", "#0E9ED4", "#9ED8ED", "#E8804A"
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
                 facecolor="none", edgecolor=CY, linewidth=0.7, alpha=0.85)
axA.set_xlim(LON0, LON1); axA.set_ylim(LAT0, LAT1)
axA.set_title("A   %d candidate craters \u2265 1 km \u2014 closed depressions in the DEM, "
              "circle scaled by diameter" % len(rows),
              color=CY, fontsize=12.5, pad=9, loc="left")

# ---- B  size-frequency
axB = fig.add_subplot(gs[1, 0])
d = np.sort(dia)
cum = np.arange(len(d), 0, -1)
area_km2 = (LON1 - LON0) * DEG / 1000.0 * (LAT1 - LAT0) * DEG / 1000.0 * np.cos(np.radians(9.5))
axB.loglog(d, cum / area_km2 * 1e6, color=CY, lw=1.9)
axB.axvline(1.0, color=WARN, lw=1.2, ls="--")
axB.text(1.06, axB.get_ylim()[1] * 0.35, "1 km \u2014 the project's\nown resolving limit",
         color=WARN, fontsize=8.5, va="top")
axB.set_xlabel("diameter (km)", color=SUB)
axB.set_ylabel("cumulative N per 10$^6$ km$^2$", color=SUB)
axB.set_title("B   Size-frequency", color=CY, fontsize=12, pad=9, loc="left")
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
    ax.add_patch(Circle((tlo, tla), rad_deg, fill=False, edgecolor=CY, lw=1.8, ls="--"))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    # equal aspect, or the dashed IAU circle renders as an ellipse and reads as
    # a claim about the crater's shape
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("%s   %s \u2014 IAU %.0f km   %s"
                 % ("CD"[k], nm, tdia, "HIT  \u22127.1%" if hit else "MISS"),
                 color=CY if hit else WARN, fontsize=11.5, pad=9, loc="left")
    ax.text(0.03, 0.04,
            ("detected as the largest\ncandidate in its window"
             if hit else "rim breached \u2014 lowest rim\npoint 33 m BELOW the floor,\nso it is not a closed basin"),
            transform=ax.transAxes, color="white", fontsize=8.2, va="bottom",
            bbox=dict(boxstyle="round,pad=0.35", fc=BG, ec=CY if hit else WARN, alpha=0.9))

for a in fig.axes:
    a.set_facecolor(BG)
    a.tick_params(colors=SUB, labelsize=8.5)
    for sp in a.spines.values():
        sp.set_color("#2A4A66")
axA.set_xlabel("East longitude (\u00b0)", color=SUB)
axA.set_ylabel("Latitude (\u00b0)", color=SUB)

fig.suptitle("Ius Chasma \u00b7 candidate craters are inferred, not mapped \u00b7 "
             "orange = depth Fill removed",
             color="white", fontsize=15, y=0.977, x=0.075, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.957])
out = r"Z:\Mars Remote Sensing Project\build\pres1_img\ius_crater_candidates.png"
fig.savefig(out, dpi=115, facecolor=BG)
print("wrote", out)
