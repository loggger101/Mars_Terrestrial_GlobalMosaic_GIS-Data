# -*- coding: utf-8 -*-
r"""Figure for test T3 by block size: how each layer's correlation with TES inertia changes as the block shrinks (KB §69.29).

Two panels against block size (15° to 0.5°, finer to the right), nightside TES, measured cells:
  left   the pooled within-block r, signed so that up is the physical direction (night IR +, the index and
         Viking red −), with the 180°-shift null in grey;
  right  the share of blocks whose own r has the physical sign; 50 % is a coin toss.
Colours: the dataviz reference palette's first three categorical slots (validated all-pairs). Light ground.
Reads logs\tes_block_scale.json; writes build\final_img\tes_block_scale.png.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "logs", "tes_block_scale.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "final_img", "tes_block_scale.png")
INK, MUTED, GRID, NULL = "#1A1A1A", "#5A6570", "#D9DEE3", "#9AA3AB"
SERIES = [("THEMIS night DN", "night IR", +1, "#2a78d6"),
          ("diurnal-contrast index", "diurnal-contrast index", -1, "#eb6834"),
          ("Viking red", "Viking red (albedo)", -1, "#1baf7a")]
NUDGE = {"night IR": +0.008, "diurnal-contrast index": -0.006, "Viking red (albedo)": 0.0}   # end labels apart
SIZES = R["sizes_deg"]
KEYS = ["%g" % s for s in SIZES]
side = R["nightside"]

plt.rcParams.update({"font.family": "Arial", "font.size": 11})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=200)
for name, label, sign, col in SERIES:
    by = side[name]["by_block_deg"]
    pooled = [sign * by[k]["layer"]["pooled"] for k in KEYS]
    share = [100 * by[k]["layer"]["share_physical_sign"] for k in KEYS]
    for ax, ys in ((a1, pooled), (a2, share)):
        ax.plot(SIZES, ys, "-", color=col, lw=2, zorder=3)
        ax.plot(SIZES, ys, "o", color=col, ms=8, mec="white", mew=2, zorder=4)
    i = max(range(len(KEYS)), key=lambda j: pooled[j])          # the peak, labelled
    a1.annotate("%.3f" % pooled[i], (SIZES[i], pooled[i]), xytext=(0, 9),
                textcoords="offset points", ha="center", color=INK, fontsize=9.5)
    a1.text(0.43, pooled[-1] + NUDGE[label], label, va="center", color=INK, fontsize=10)
null = [max(abs(side[n]["by_block_deg"][k]["null_shift180"]["pooled"]) for n, *_ in SERIES) for k in KEYS]
a1.fill_between(SIZES, [-v for v in null], null, color=NULL, alpha=0.35, lw=0, zorder=2)
a1.text(15, -0.026, "null: layer shifted 180°", color=MUTED, fontsize=9, ha="left", va="top")
a2.axhline(50, color=NULL, lw=1.2, ls="--", zorder=2)
a2.text(0.5, 48.5, "coin toss", color=MUTED, fontsize=9, ha="right", va="top")
for ax in (a1, a2):
    ax.set_xscale("log"); ax.invert_xaxis()
    ax.set_xticks(SIZES); ax.set_xticklabels(["%g°" % s for s in SIZES])
    ax.minorticks_off()
    ax.set_xlabel("block size (finer to the right)", color=MUTED)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
a1.set_xlim(16.5, 0.2)
a1.set_ylim(-0.035, 0.14)
a1.axhline(0, color=INK, lw=1)
a1.set_title("Pooled within-block r, physical direction up", loc="left", color=INK, fontsize=11.5)
a2.set_ylim(40, 102)
a2.set_title("Blocks whose r has the physical sign", loc="left", color=INK, fontsize=11.5)
a2.set_yticks([50, 60, 70, 80, 90, 100]); a2.set_yticklabels(["%d %%" % v for v in (50, 60, 70, 80, 90, 100)])
h = [plt.Line2D([], [], color=c, lw=2, marker="o", ms=7, mec="white", mew=1.5, label=l) for _, l, _, c in SERIES]
a2.legend(handles=h, loc="upper right", frameon=False, fontsize=10)
fig.text(0.01, 0.005, "Against log TES thermal inertia (nightside, measured ~3 km cells), ±60°. "
         "5° block ≈ 88,000 km² at the equator; 15° ≈ 782,000 km².", color=MUTED, fontsize=8.5)
fig.tight_layout(rect=(0, 0.03, 1, 1))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
