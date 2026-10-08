# -*- coding: utf-8 -*-
r"""Figure for test T3: each layer against calibrated TES thermal inertia (KB §43.1).

Dot plot, one row per layer: r across the whole ±60° band (blue) and the median r inside 15° x 15°
blocks with its interquartile range (orange), against nightside TES inertia on measured cells.
Colours from the dataviz reference palette, validated (CVD and contrast pass). Light ground for the
interim deck. Writes build\interim_img\tes_check.png.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "logs", "tes_global_check.json")))["nightside"]
OUT = os.path.join(HERE, "interim_img", "tes_check.png")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
GLOBAL, LOCAL = "#2a78d6", "#eb6834"

rows = ["Viking red", "THEMIS night DN", "diurnal-contrast index", "THEMIS day DN", "slope"]
plt.rcParams.update({"font.family": "Arial", "font.size": 11})
fig, ax = plt.subplots(figsize=(10, 4.4), dpi=200)
for i, name in enumerate(rows):
    y = len(rows) - 1 - i
    d = R[name]
    lo, hi = d["r_within_blocks_p25_p75"]
    ax.plot([lo, hi], [y - 0.12, y - 0.12], color=LOCAL, lw=2, solid_capstyle="round", zorder=3)
    ax.plot(d["r_within_blocks_median"], y - 0.12, "o", ms=8, color=LOCAL, mec="white", mew=2, zorder=4)
    ax.plot(d["r_global"], y + 0.12, "o", ms=8, color=GLOBAL, mec="white", mew=2, zorder=4)
    ax.text(0.47, y, "%+.2f   %+.2f" % (d["r_global"], d["r_within_blocks_median"]), va="center", color=INK, fontsize=10)
ax.text(0.47, len(rows) - 0.45, "global  within", color=MUTED, fontsize=9.5)
ax.axvline(0, color=INK, lw=1)
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows[::-1], color=INK)
ax.set_xlim(-0.45, 0.62); ax.set_ylim(-0.6, len(rows) - 0.3)
ax.set_xlabel("correlation with log thermal inertia (TES nightside, measured cells, ~3 km)", color=MUTED)
ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(colors=MUTED, length=0)
h1, = ax.plot([], [], "o", color=GLOBAL, ms=8, label="across all of ±60°")
h2, = ax.plot([], [], "o-", color=LOCAL, ms=8, lw=2, label="median within 15° blocks (bar: middle half)")
ax.legend(handles=[h1, h2], loc="upper right", bbox_to_anchor=(0.84, 1.0), frameon=False, fontsize=10)
fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
