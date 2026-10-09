# -*- coding: utf-8 -*-
r"""Figures for tests T5, T6 and T7 (KB §47), for the interim deck and report.

Read from the tests' own logs, never retyped:
  logs\t5_flow_margins.json        -> interim_img\t5_margins.png    share of lAv contact profiles each band
                                                                       separates, 95 % interval, chance line
  logs\t6_composite_stability.json -> interim_img\t6_stability.png  stability (ARI) and coherence per input,
                                                                       two panels on their own scales
  logs\t7_order_sweep.json         -> interim_img\t7_orders.png     max Strahler order, and the order-1
                                                                       share on >= 2 deg, against the threshold

Colours: the deck's validated pair (dataviz reference palette; CVD dE 24.7, contrast >= 3:1, KB §45):
blue = visible / single inputs, orange = thermal / composites; identity also given by the row labels.
One axis per panel, never a dual axis. Light ground for the deck.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(HERE, "interim_img")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "Arial", "font.size": 11})


def load(name):
    with open(os.path.join(HERE, "logs", name), encoding="utf-8") as f:
        return json.load(f)


def tidy(ax, xgrid=True):
    ax.grid(axis="x" if xgrid else "y", color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)


TICKS = [1, 2.5, 5, 10, 20, 50, 100, 200, 500]


def km2_axis(ax):
    ax.set_xscale("log")
    ax.set_xticks(TICKS)
    ax.set_xticklabels(["%g" % t for t in TICKS])
    ax.minorticks_off()


def save(fig, name):
    fig.tight_layout()
    os.makedirs(OUTD, exist_ok=True)
    p = os.path.join(OUTD, name)
    fig.savefig(p, facecolor="white")
    plt.close(fig)
    print("wrote", p)


# ------------------------------------------------------------------ T5
t5 = load("t5_flow_margins.json")["sets"]["lAv contacts"]
rows = [("Viking red", "viking_r", BLUE), ("Viking green", "viking_g", BLUE), ("Viking blue", "viking_b", BLUE),
        ("THEMIS day IR", "day_ir", ORANGE), ("THEMIS night IR", "night_ir", ORANGE),
        ("diurnal-contrast index", "contrast_index", ORANGE)]
fig, ax = plt.subplots(figsize=(10, 4.4), dpi=200)
for i, (label, key, col) in enumerate(rows):
    y = len(rows) - 1 - i
    b = t5["bands"][key]
    lo, hi = (100 * v for v in b["ci95"])
    ax.plot([lo, hi], [y, y], color=col, lw=2, solid_capstyle="round", zorder=3)
    ax.plot(100 * b["separates"], y, "o", ms=8, color=col, mec="white", mew=2, zorder=4)
    ax.text(41.5, y, "%.0f %%" % (100 * b["separates"]), va="center", color=INK, fontsize=10)
ax.axvline(10, color=INK, lw=1, zorder=2)
ax.text(10.4, len(rows) - 0.55, "chance: 10 %", color=MUTED, fontsize=9.5)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], color=INK)
ax.set_xlim(0, 45); ax.set_ylim(-0.6, len(rows) - 0.3)
ax.set_xlabel("share of %d profiles across %d lAv contacts that the band separates (dot) and 95 %% interval"
              % (t5["profiles"], t5["contacts"]), color=MUTED)
tidy(ax)
h1, = ax.plot([], [], "o-", color=BLUE, ms=8, lw=2, label="visible")
h2, = ax.plot([], [], "o-", color=ORANGE, ms=8, lw=2, label="thermal infrared")
ax.legend(handles=[h1, h2], loc="upper right", bbox_to_anchor=(0.88, 1.0), frameon=False, fontsize=10)
save(fig, "t5_margins.png")

# ------------------------------------------------------------------ T6
t6 = load("t6_composite_stability.json")["inputs"]
order = ["Viking RGB", "day IR", "night IR", "4-band composite", "5-band composite"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=200, sharey=True)
for ax, key, title in ((axes[0], "stability_ari", "stability: west- vs east-trained maps (ARI)"),
                       (axes[1], "coherence", "coherence: neighbouring pixels in one class")):
    for i, name in enumerate(order):
        y = len(order) - 1 - i
        v = t6[name][key]
        col = ORANGE if "composite" in name else BLUE
        ax.plot([0, v], [y, y], color=GRID, lw=2, zorder=2)
        ax.plot(v, y, "o", ms=9, color=col, mec="white", mew=2, zorder=4)
        ax.text(v + 0.025, y, "%.2f" % v, va="center", color=INK, fontsize=10)
    ax.set_xlim(0, 1.05); ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    tidy(ax)
axes[0].set_yticks(range(len(order))); axes[0].set_yticklabels(order[::-1], color=INK)
h1, = axes[0].plot([], [], "o", color=BLUE, ms=9, label="single input")
h2, = axes[0].plot([], [], "o", color=ORANGE, ms=9, label="composite")
axes[0].legend(handles=[h1, h2], loc="lower right", frameon=False, fontsize=10)
save(fig, "t6_stability.png")

# ------------------------------------------------------------------ T7
t7 = load("t7_order_sweep.json")["thresholds"]
km2 = [v["km2"] for v in t7.values()]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=200)
ax = axes[0]
ax.step(km2, [v["max_order"] for v in t7.values()], where="mid", color=BLUE, lw=2, zorder=3)
ax.plot(km2, [v["max_order"] for v in t7.values()], "o", ms=8, color=BLUE, mec="white", mew=2, zorder=4)
km2_axis(ax); ax.set_ylim(0, 6); ax.set_yticks(range(0, 7))
ax.set_title("highest Strahler order", color=INK, fontsize=11, loc="left")
ax.set_xlabel("channel threshold, km² of catchment", color=MUTED)
tidy(ax, xgrid=False)
ax = axes[1]
share = [100 * v["order1_steep_share"] for v in t7.values()]
ax.plot(km2, share, "-", color=BLUE, lw=2, zorder=3)
ax.plot(km2, share, "o", ms=8, color=BLUE, mec="white", mew=2, zorder=4)
ax.axhline(50, color=INK, lw=1, zorder=2)
ax.text(1.05, 51.5, "the rule: ≥ 50 % on real slopes", color=MUTED, fontsize=9.5)
km2_axis(ax); ax.set_ylim(0, 60)
ax.set_title("first-order stream cells on slopes ≥ 2°, %", color=INK, fontsize=11, loc="left")
ax.set_xlabel("channel threshold, km² of catchment", color=MUTED)
tidy(ax, xgrid=False)
save(fig, "t7_orders.png")
