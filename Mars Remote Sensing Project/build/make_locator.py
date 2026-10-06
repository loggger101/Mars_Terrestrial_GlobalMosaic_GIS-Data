# -*- coding: utf-8 -*-
"""Global locator: where the two type areas sit on the planet.

Reads the whole Viking colour mosaic decimated to ~3000 px. The TIFFs are
stripped one scanline per block and carry no pyramids, so this is a full-file
read -- about a minute -- which is itself the argument for building pyramids.
"""
import math
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402
import numpy as np                                                # noqa: E402
import matplotlib.patheffects as pe                               # noqa: E402
from matplotlib.patches import Rectangle                          # noqa: E402
from osgeo import gdal                                            # noqa: E402

import marsfig as M                                               # noqa: E402

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "1024")
OUT = r"Z:\Mars Remote Sensing Project\build\le_img"

NAVY, CYAN = "#0E2841", "#0E9ED4"
# a dark stroke keeps white labels legible over Hellas and the polar caps
HALO = [pe.withStroke(linewidth=2.6, foreground="#0B1A2B", alpha=0.92)]

t0 = time.time()
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "viking_global_3000.npy")
if os.path.exists(CACHE):
    img = np.load(CACHE)
    print("reusing cached decimation %s" % (img.shape,))
else:
    ds = gdal.Open(M.VIKING, gdal.GA_ReadOnly)
    W = 3000
    H = int(W * ds.RasterYSize / ds.RasterXSize)
    print("reading %dx%d -> %dx%d (stripped, no pyramids: full-file read) ..."
          % (ds.RasterXSize, ds.RasterYSize, W, H))
    arr = ds.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize,
                         buf_xsize=W, buf_ysize=H)
    ds = None
    print("   read in %.1f s" % (time.time() - t0))
    img = M.stretch_rgb(np.transpose(arr, (1, 2, 0)), 0.5, 99.5)
    np.save(CACHE, img)

fig, ax = plt.subplots(figsize=(13.2, 4.7), dpi=170)
ax.imshow(img, extent=[-180, 180, -90, 90], interpolation="bilinear")

for lon in range(-180, 181, 30):
    ax.axvline(lon, color="white", lw=0.4, alpha=0.28)
for lat in range(-60, 61, 30):
    ax.axhline(lat, color="white", lw=0.4, alpha=0.28)

w = M.WINDOW
ax.add_patch(Rectangle((w["lon0"], w["lat0"]),
                       w["lon1"] - w["lon0"], w["lat1"] - w["lat0"],
                       fill=False, ec=CYAN, lw=2.2, zorder=5))
ax.annotate("Type area 1 \u2014 Ius Chasma / Louros Valles\n"
            "271\u2013286\u00b0E, 6\u201313\u00b0S  (mosaic viewer extent)",
            xy=(w["lon1"], w["lat0"]), xytext=(-30, -26),
            textcoords="offset points", color="white", fontsize=14,
            ha="left", va="top", path_effects=HALO,
            arrowprops=dict(arrowstyle="-", color=CYAN, lw=1.2))

jez_lon, jez_lat = 77.58 - 360 if False else 77.58, 18.44
ax.plot([jez_lon], [jez_lat], marker="o", ms=7, mfc="none", mec=CYAN, mew=2.2,
        zorder=5)
ax.annotate("Type area 2 \u2014 Jezero Crater\n77.6\u00b0E, 18.4\u00b0N  "
            "(Perseverance services)",
            xy=(jez_lon, jez_lat), xytext=(-18, 16),
            textcoords="offset points",
            color="white", fontsize=14, ha="right", path_effects=HALO,
            arrowprops=dict(arrowstyle="-", color=CYAN, lw=1.2))

for lon, lat, name in ((226.2, 18.65, "Olympus Mons"), (70.5, -42.4, "Hellas"),
                       (247.0, -1.0, "Tharsis Montes")):
    lon = lon - 360 if lon > 180 else lon
    ax.plot([lon], [lat], marker="+", ms=9, color="white", mew=1.6,
            path_effects=HALO)
    ax.annotate(name, xy=(lon, lat), xytext=(8, -13),
                textcoords="offset points", color="white", fontsize=11.5,
                path_effects=HALO)

ax.set_xlim(-180, 180)
ax.set_ylim(-60, 60)
ax.set_xticks(range(-180, 181, 60))
ax.set_yticks(range(-60, 61, 30))
ax.set_xticklabels(["%d\u00b0E" % ((v + 360) % 360) for v in range(-180, 181, 60)],
                   fontsize=12)
ax.set_yticklabels(["%d\u00b0" % v for v in range(-60, 61, 30)], fontsize=12)
ax.tick_params(colors=NAVY, length=3)
for s in ax.spines.values():
    s.set_edgecolor(NAVY)
    s.set_linewidth(0.8)

fig.tight_layout(pad=0.4)
p = os.path.join(OUT, "locator_global.png")
fig.savefig(p, facecolor="white")
print("wrote", p, "in %.1f s total" % (time.time() - t0))
