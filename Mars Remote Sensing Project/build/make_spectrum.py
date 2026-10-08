# -*- coding: utf-8 -*-
"""Which parts of the spectrum this project uses, and what sits where.

Wavelengths are the published instrument ranges already quoted in the
prospectus; the figure adds no new claims, it just places them on an axis.
Each label sits directly above its own bar so nothing reaches across the plot.
"""
import os
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402
from matplotlib.patches import Rectangle                          # noqa: E402

OUT = on_drive(r"Mars Remote Sensing Project\build\le_img")
NAVY, CYAN, GREY = "#0E2841", "#0E9ED4", "#555F66"
INK = "#000000"

fig, ax = plt.subplots(figsize=(11.6, 4.3), dpi=190)

lo, hi = 0.33, 26.0
ax.set_xscale("log")
ax.set_xlim(lo, hi)
ax.set_ylim(-0.6, 10.4)

# ---- the visible strip, drawn in its own colours -------------------------
for x0, x1, c in [(0.40, 0.45, "#4b0f8a"), (0.45, 0.49, "#1f3fd0"),
                  (0.49, 0.56, "#1f9d55"), (0.56, 0.59, "#d8c520"),
                  (0.59, 0.63, "#e07b1e"), (0.63, 0.70, "#c02420")]:
    ax.add_patch(Rectangle((x0, 7.4), x1 - x0, 1.4, fc=c, ec="none", alpha=0.92))
ax.text(0.53, 9.0, "visible", ha="center", fontsize=9.5, color=INK)

# ---- thermal infrared window used by THEMIS ------------------------------
ax.add_patch(Rectangle((6.8, 7.4), 14.9 - 6.8, 1.4, fc=NAVY, ec="none",
                       alpha=0.88))
ax.text(10.1, 9.0, "thermal infrared", ha="center", fontsize=9.5, color=INK)

# ---- CO2 absorption, the reason the bands stop where they do -------------
ax.add_patch(Rectangle((14.2, 6.9), 1.6, 2.3, fc="#c02420", ec="none",
                       alpha=0.20))
ax.text(15.0, 6.55, "CO$_2$ 15 \u00b5m", ha="center", va="top", fontsize=7.5,
        color="#8d1a1a")

# ---- what the project actually holds -------------------------------------
rows = [
    (4.7, 0.40, 0.70, "Viking MDIM 2.1 colour \u2014 3 bands, 232 m", CYAN, True),
    (3.0, 0.57, 0.61,
     "Viking band 1 (red, \u2248 0.59 \u00b5m) \u2014 dust vs basalt", CYAN, True),
    (1.3, 6.80, 14.90, "THEMIS Day IR v12 \u2014 100 m, held", NAVY, True),
    (-0.3, 6.80, 14.90, "THEMIS Night IR \u2014 not yet acquired", GREY, False),
]
for y, x0, x1, label, colour, held in rows:
    ax.plot([x0, x1], [y, y], lw=7, color=colour, solid_capstyle="butt",
            alpha=0.95 if held else 0.5,
            linestyle="-" if held else (0, (2, 1.6)))
    ax.text(x0, y + 0.42, label, ha="left", va="bottom", fontsize=9,
            color=INK if held else GREY)

# altimetry is active, so it gets a marker rather than a band
ax.plot([1.064], [6.15], marker="v", ms=9, color=NAVY)
ax.text(1.064, 6.58, "MOLA laser altimetry \u2014 1064 nm, active",
        ha="center", va="bottom", fontsize=9, color=INK)

ax.text(hi * 0.985, 9.9,
        "solid = held      dashed = planned", ha="right", fontsize=8, color=GREY)

ax.set_yticks([])
ax.set_xticks([0.4, 0.5, 0.7, 1.0, 2.0, 5.0, 10.0, 20.0])
ax.set_xticklabels(["0.4", "0.5", "0.7", "1", "2", "5", "10", "20"], fontsize=9)
ax.set_xlabel("wavelength (\u00b5m, log scale)", fontsize=9.5, color=INK)
ax.tick_params(axis="x", colors=NAVY, length=4)
for side in ("top", "left", "right"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(NAVY)
ax.grid(axis="x", color=GREY, alpha=0.16, lw=0.6)

fig.tight_layout(pad=0.5)
p = os.path.join(OUT, "em_spectrum.png")
fig.savefig(p, facecolor="white")
print("wrote", p)
