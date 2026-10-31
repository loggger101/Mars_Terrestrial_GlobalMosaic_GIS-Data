# -*- coding: utf-8 -*-
r"""Figure for A10: cumulative crater size-frequency distributions, closed depressions against Robbins (KB §69.35).

Three panels, log-log, craters at least D across per km² at the standard sqrt(2) diameters: ±60° (the 465,354 closed
depressions against the Robbins catalogue), then each type area with the review's accepts as a third curve.
Colours: the dataviz reference palette's first three categorical slots, as make_fig_tes_scale.py. Light ground.
Reads logs\crater_sfd.json (make_crater_sfd.py); writes build\final_img\crater_sfd.png. System Python.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "logs", "crater_sfd.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "final_img", "crater_sfd.png")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
SERIES = [("robbins", "Robbins catalogue", "#2a78d6", 5),        # (key, label, colour, layer): Robbins on top where
          ("candidates", "closed depressions", "#eb6834", 3),     # the curves meet (Ius' accepts equal it above 11 km)
          ("accepted", "accepted in review", "#1baf7a", 4)]
PANELS = [("±60°", "Mars ±60°"), ("Ius Chasma", "Ius Chasma"), ("Athabasca Valles", "Athabasca Valles")]

plt.rcParams.update({"font.family": "Arial", "font.size": 11})
fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), dpi=200, sharey=True)
for ax, (key, title) in zip(axes, PANELS):
    w = R["windows"][key]
    for name, label, col, z in SERIES:
        if name not in w:
            continue
        pts = [(float(D), v["per_km2"]) for D, v in w[name].items() if v["n"] > 0]
        x, y = zip(*pts)
        ax.plot(x, y, "-", color=col, lw=2, zorder=z, label=label)
        ax.plot(x, y, "o", color=col, ms=5.5, mec="white", mew=1.2, zorder=z + 0.5)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks([1, 2, 5, 10, 20, 50, 100, 200]); ax.set_xticklabels(["1", "2", "5", "10", "20", "50", "100", "200"])
    ax.minorticks_off()
    ax.set_xlim(0.85, 300)
    ax.set_xlabel("crater diameter D (km)", color=MUTED)
    ax.grid(color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.set_title("%s  ·  %s km²" % (title, f"{w['area_km2']:,.0f}"), loc="left", color=INK, fontsize=11.5)
axes[0].set_ylabel("craters ≥ D per km²", color=MUTED)
h, l = axes[1].get_legend_handles_labels()
order = [l.index(x) for x in ("closed depressions", "accepted in review", "Robbins catalogue")]
axes[1].legend([h[i] for i in order], [l[i] for i in order], frameon=False, loc="upper right", labelcolor=INK)
p = R["windows"]["±60°"]["ratio"]
axes[0].text(0.97, 0.96, "depressions ÷ Robbins\n%.2f at 1 km\n%.2f at 4 km\n%.2f at 16 km" % (p["1"], p["4"], p["16"]),
             transform=axes[0].transAxes, color=MUTED, fontsize=9, ha="right", va="top")
fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
