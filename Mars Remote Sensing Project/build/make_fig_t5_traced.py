# -*- coding: utf-8 -*-
r"""Figure for T5 (H1) on both sets of margins, for the final paper (KB §47.2, §69.52; v2_drafts.tex block 15).

Read from the tests' own logs, never retyped:
  logs\t5_flow_margins.json         the geologic map's lAv contacts at 1:20 M (§47.2; the interim's t5_margins.png)
  logs\t5_flow_margins_traced.json  the 86 lava margins traced on CTX by the agent (§69.52)
  -> final_img\t5_traced.png        per band: the share of profiles each set separates (dot) and its 95 % interval

The interim's t5_margins.png (make_fig_tests567.py) is left as it is: the interim is cut at 26 October (D20).
Colours as there (blue = visible, orange = thermal infrared); the set is told by the marker, open for the map's
contacts, filled for the traced margins, and named in the legend. One axis.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final_img", "t5_traced.png")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "Arial", "font.size": 11})


def load(name):
    with open(os.path.join(HERE, "logs", name), encoding="utf-8") as f:
        return json.load(f)["sets"]["lAv contacts"]


SETS = [("map", load("t5_flow_margins.json"), +0.17), ("traced", load("t5_flow_margins_traced.json"), -0.17)]
ROWS = [("Viking red", "viking_r", BLUE), ("Viking green", "viking_g", BLUE), ("Viking blue", "viking_b", BLUE),
        ("THEMIS day IR", "day_ir", ORANGE), ("THEMIS night IR", "night_ir", ORANGE),
        ("diurnal-contrast index", "contrast_index", ORANGE)]

fig, ax = plt.subplots(figsize=(10, 5.3), dpi=200)
for i, (label, key, col) in enumerate(ROWS):
    y0 = len(ROWS) - 1 - i
    for kind, t5, dy in SETS:
        b = t5["bands"][key]
        lo, hi = (100 * v for v in b["ci95"])
        y = y0 + dy
        ax.plot([lo, hi], [y, y], color=col, lw=2, solid_capstyle="round", zorder=3, alpha=0.55 if kind == "map" else 1)
        if kind == "map":
            ax.plot(100 * b["separates"], y, "o", ms=8, mfc="white", mec=col, mew=2, zorder=4)
        else:
            ax.plot(100 * b["separates"], y, "o", ms=8, color=col, mec="white", mew=2, zorder=4)
        ax.text(41.5, y, "%.1f %%" % (100 * b["separates"]), va="center", color=INK if kind == "traced" else MUTED,
                fontsize=9.5)
ax.axvline(10, color=INK, lw=1, zorder=2)
ax.text(10.4, len(ROWS) - 0.4, "chance: 10 %", color=MUTED, fontsize=9.5)
ax.set_yticks(range(len(ROWS))); ax.set_yticklabels([r[0] for r in ROWS][::-1], color=INK)
ax.set_xlim(0, 45); ax.set_ylim(-0.6, len(ROWS) - 0.2)
ax.set_xlabel("share of profiles the band separates (dot) and 95 % interval over margins", color=MUTED)
ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(colors=MUTED, length=0)
m, t = SETS[0][1], SETS[1][1]
handles = [Line2D([], [], marker="o", ls="-", color=MUTED, mfc="white", mec=MUTED, mew=2, ms=8,
                  label="geologic-map contacts, 1:20 M (%d profiles, %d contacts)" % (m["profiles"], m["contacts"])),
           Line2D([], [], marker="o", ls="-", color=INK, mec="white", mew=2, ms=8,
                  label="lava margins traced on CTX (%d profiles, %d margins)" % (t["profiles"], t["contacts"]))]
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False, fontsize=9.5)
fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
