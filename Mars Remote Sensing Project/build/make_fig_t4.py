# -*- coding: utf-8 -*-
r"""Figure for test T4 stage 1 (H2, KB §51), for the interim deck and report.

Read from logs\t4_channel_h2.json, never retyped -> interim_img\t4_channels.png, two panels:
  left   median channel gradient (m per km, log axis) in each window, all candidates and order >= 2
  right  how well each variable tells the two windows apart: cross-validated AUC, 0.5 = chance

Colours: the deck's validated pair (KB §45): blue = Ius Chasma, orange = Athabasca Valles in the left
panel; the right panel's two series are ink and muted grey, so no hue changes meaning between panels.
Identity is also given by labels. One axis per panel.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(HERE, "interim_img")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"          # as make_fig_tests567.py (importing it reruns it)
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "Arial", "font.size": 11})


def tidy(ax):
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)


def save(fig, name):
    fig.tight_layout()
    os.makedirs(OUTD, exist_ok=True)
    fig.savefig(os.path.join(OUTD, name), facecolor="white")
    plt.close(fig)
    print("wrote", os.path.join(OUTD, name))


with open(os.path.join(HERE, "logs", "t4_channel_h2.json"), encoding="utf-8") as f:
    d = json.load(f)
A, B = d["stage1_all"], d["stage1_order2"]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 1.15]})

rows = [("All candidates ≥ 1 km", A), ("Strahler order ≥ 2", B)]
for i, (lab, r) in enumerate(rows):
    y = len(rows) - 1 - i
    ax1.plot([r["grad_median_b"], r["grad_median_a"]], [y, y], color=GRID, lw=3, zorder=1)
    ax1.scatter([r["grad_median_a"]], [y], s=90, color=BLUE, zorder=3)
    ax1.scatter([r["grad_median_b"]], [y], s=90, color=ORANGE, zorder=3)
    ax1.annotate("%.1f" % r["grad_median_a"], (r["grad_median_a"], y), xytext=(0, 9), textcoords="offset points",
                 ha="center", color=INK, fontsize=10)
    ax1.annotate("%.1f" % r["grad_median_b"], (r["grad_median_b"], y), xytext=(0, 9), textcoords="offset points",
                 ha="center", color=INK, fontsize=10)
ax1.set_yticks(range(len(rows)))
ax1.set_yticklabels([r[0] for r in rows][::-1])
ax1.set_xscale("log"); ax1.set_xlim(0.5, 20)
ax1.set_xticks([0.5, 1, 2, 5, 10, 20]); ax1.set_xticklabels(["0.5", "1", "2", "5", "10", "20"]); ax1.minorticks_off()
ax1.set_ylim(-0.6, 1.8)
ax1.set_xlabel("Median channel gradient (m per km)", color=MUTED)
ax1.scatter([], [], s=60, color=BLUE, label="Ius Chasma (fluvial / collapse)")
ax1.scatter([], [], s=60, color=ORANGE, label="Athabasca Valles (volcanic)")
ax1.legend(loc="upper left", frameon=False, fontsize=9.5, ncol=1)
ax1.set_title("H2 expects the volcanic channels steeper", loc="left", fontsize=11.5, color=INK)
tidy(ax1)

vars_ = [("Gradient alone", "auc_gradient"), ("Thermal response alone", "auc_thermal"), ("Both", "auc_both")]
h = 0.34
for j, (lab, r, col) in enumerate([("All candidates", A, INK), ("Order ≥ 2", B, MUTED)]):
    ys = [len(vars_) - 1 - i + (h / 2 if j == 0 else -h / 2) for i in range(len(vars_))]
    vals = [r[k] for _, k in vars_]
    ax2.barh(ys, [v - 0.5 for v in vals], left=0.5, height=h * 0.9, color=col, label=lab, zorder=2)
    for yy, v in zip(ys, vals):
        ax2.text(max(v, 0.5) + 0.01, yy, "%.2f" % v, va="center", color=INK, fontsize=9.5)
ax2.axvline(0.5, color=MUTED, lw=1, ls="--", zorder=3)
ax2.text(0.505, -0.62, "chance", color=MUTED, fontsize=9)
ax2.set_yticks(range(len(vars_))); ax2.set_yticklabels([v[0] for v in vars_][::-1])
ax2.set_xlim(0.45, 1.0); ax2.set_ylim(-0.75, len(vars_) - 0.4)
ax2.set_xlabel("Telling the two windows apart (cross-validated AUC)", color=MUTED)
ax2.legend(loc="center right", frameon=False, fontsize=9.5)
ax2.set_title("Thermal response adds nothing", loc="left", fontsize=11.5, color=INK)
tidy(ax2)
save(fig, "t4_channels.png")
