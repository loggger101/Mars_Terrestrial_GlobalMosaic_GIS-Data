# -*- coding: utf-8 -*-
"""The mapping extent: 360 degrees of longitude, 60 N to 60 S.

This replaces the old locator, which drew a box around one window and labelled it
the type area. That framed a close-up as the subject of the project. The subject
is the whole mosaic inside this band; the close-ups elsewhere in the deck are
there to show what 100 m and 232 m data actually resolve.

The band is not arbitrary. Every product here is plate carree (SimpleCylindrical
with standard_parallel_1 = 0), where a degree of longitude is R*cos(lat) on the
ground but a constant width in the grid, so the east-west scale error is
1/cos(lat): 1.15x at 30 degrees, 2.00x at 60, 5.76x at 80, unbounded at the pole.
Cutting at 60 caps the distortion at 2x and still keeps sin(60) = 86.6% of the
surface area.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402
import matplotlib.patheffects as pe                               # noqa: E402
import numpy as np                                                # noqa: E402
from matplotlib.patches import Rectangle                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "le_img")

NAVY, CYAN = "#0E2841", "#0E9ED4"
HALO = [pe.withStroke(linewidth=2.8, foreground="#0B1A2B", alpha=0.92)]

CUT = 60.0
img = np.load(os.path.join(HERE, "viking_global_3000.npy"))

fig, ax = plt.subplots(figsize=(13.0, 6.6), dpi=170)
ax.imshow(img, extent=[-180, 180, -90, 90], interpolation="bilinear")

# grey out what is not mapped, rather than cropping it away -- the point of the
# slide is that the exclusion is a decision, so the excluded ground has to show
for y0, y1 in ((CUT, 90.0), (-90.0, -CUT)):
    ax.add_patch(Rectangle((-180, y0), 360, y1 - y0, facecolor="white",
                           alpha=0.74, zorder=3, edgecolor="none"))
for y in (CUT, -CUT):
    ax.axhline(y, color=CYAN, lw=2.2, zorder=4)

for lon in range(-180, 181, 30):
    ax.axvline(lon, color="white", lw=0.4, alpha=0.25, zorder=2)
for lat in (-30, 0, 30):
    ax.axhline(lat, color="white", lw=0.4, alpha=0.25, zorder=2)

ax.annotate("mapped  —  60°N to 60°S, all 360° of longitude"
            "  ·  86.6% of the surface",
            xy=(-176, 52), color="white", fontsize=15.5, va="top",
            path_effects=HALO, zorder=6)
for y, va in ((76, "center"), (-76, "center")):
    ax.annotate("not mapped — plate-carrée east-west scale error "
                "passes 2× beyond 60°",
                xy=(0, y), color=NAVY, fontsize=13, ha="center", va=va,
                zorder=6)

ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_xticks(range(-180, 181, 60))
ax.set_yticks([-90, -60, -30, 0, 30, 60, 90])
ax.set_xticklabels(["%d°E" % ((v + 360) % 360)
                    for v in range(-180, 181, 60)], fontsize=14)
ax.set_yticklabels(["%d°" % v for v in (-90, -60, -30, 0, 30, 60, 90)],
                   fontsize=14)
ax.tick_params(colors=NAVY, length=3)
for s in ax.spines.values():
    s.set_edgecolor(NAVY)
    s.set_linewidth(0.8)

fig.tight_layout(pad=0.4)
p = os.path.join(OUT, "g_extent.png")
fig.savefig(p, facecolor="white", bbox_inches="tight", pad_inches=0.1)
print("wrote", p, " (1/cos60 = %.2f, sin60 = %.3f)"
      % (1 / math.cos(math.radians(CUT)), math.sin(math.radians(CUT))))
