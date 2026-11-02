# -*- coding: utf-8 -*-
r"""Figure for A3: the SVM maps under mode filters against the geography baselines (NEXT-STEPS §12.2 A3, §14 row 2).

Two panels, four classes and seven: the SVM map's held-out accuracy and balanced accuracy as the mode filter widens
from the raw 400 m map to 51 km (A3 (c), logs\mode_curve.json), against flat reference lines read from their own logs:
the nearest training polygon's class (A3 (a), spatial_baseline_nearest*.json), a classifier on elevation and latitude
alone (A3 (b), elevation_baseline.json), one class everywhere, and the U-Net. The panels are stacked so one right-hand
margin holds the reference labels (pushed apart where two lines sit close); the filter widths are evenly spaced steps.
A legend and direct labels; blue and orange are the reference palette's first two slots, checked for colour-vision
deficiency.
Light ground, Arial, as make_fig_map_agreement.py. Writes build\final_img\svm_baselines.png. System Python.
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(HERE, "logs")
OUT = os.path.join(HERE, "final_img", "svm_baselines.png")
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
ACC, BAL = "#2a78d6", "#eb6834"

load = lambda f: json.load(open(os.path.join(LOGS, f), encoding="utf-8"))
MC, EB = load("mode_curve.json"), load("elevation_baseline.json")
NEAR = {"svm4": load("spatial_baseline_nearest.json")["held_out"], "svm7": load("spatial_baseline_nearest_v2.json")["held_out"]}
PANELS = [("svm4", "four", "Four classes (183 held-out polygons)"),
          ("svm7", "seven", "Seven classes (237 held-out polygons)")]
LIFT = {"svm4": (8, -4), "svm7": (16, 8)}          # series-label offsets in points, set where no reference line runs;
                                                    # a negative second value puts the balanced label above its line

def spread(ys, gap):
    """Label heights for reference lines at ys: the lines' own heights, pushed apart to at least gap."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    out = list(ys)
    for a, b in zip(order, order[1:]):
        out[b] = max(out[b], out[a] + gap)
    return out


plt.rcParams.update({"font.family": "Arial", "font.size": 10})
fig, axes = plt.subplots(2, 1, figsize=(7.4, 7.0), dpi=200, sharex=True)
km = MC["sizes_km"]                                   # 0.4 km is the raw 400 m map
xs = list(range(len(km)))                             # the filter widths as steps, evenly spaced
for ax, (key, eb, title) in zip(axes, PANELS):
    by = MC["maps"][key]["by_size"]
    sizes = [str(s) for s in MC["sizes_px_400m"]]
    acc = [100 * by[s]["accuracy"] for s in sizes]
    bal = [100 * by[s]["balanced"] for s in sizes]
    refs = [(100 * MC["maps"][key]["unet_accuracy"], "U-Net"),
            (100 * NEAR[key]["accuracy"], "nearest training polygon"),
            (100 * EB["sets"][eb]["accuracy"], "elevation and latitude only"),
            (100 * NEAR[key]["one_class_everywhere"], "one class everywhere")]
    xr = xs[-1] + 0.35
    for (y, lab), ly in zip(refs, spread([y for y, _ in refs], 4.2)):
        ax.plot([xs[0] - 0.3, xr], [y, y], color=MUTED, lw=1, ls=(0, (2, 2)), zorder=1, clip_on=False)
        ax.plot([xr, xr + 0.12], [y, ly], color=MUTED, lw=0.6, zorder=1, clip_on=False)
        ax.text(xr + 0.16, ly, "%s  %.1f%%" % (lab, y), color=MUTED, fontsize=8, va="center", ha="left",
                clip_on=False)
    ax.plot(xs, acc, color=ACC, lw=2, marker="o", ms=4.5, zorder=3, label="SVM, accuracy")
    ax.plot(xs, bal, color=BAL, lw=2, marker="o", ms=4.5, zorder=3, label="SVM, balanced accuracy")
    up, down = LIFT[key]                              # points above the accuracy line, below the balanced line
    ax.annotate("SVM, accuracy", (xs[1], acc[1]), xytext=(0, up), textcoords="offset points", color=INK,
                fontsize=8.5, ha="center", va="bottom")
    ax.annotate("SVM, balanced accuracy", (xs[1], bal[1]), xytext=(0, -down), textcoords="offset points", color=INK,
                fontsize=8.5, ha="center", va="top" if down > 0 else "bottom")
    ax.set_xticks(xs)
    ax.set_xticklabels(["raw\n400 m"] + ["%g km" % k for k in km[1:]], color=MUTED, fontsize=8)
    ax.set_xlim(xs[0] - 0.3, xr)
    ax.set_ylim(20, 100)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED); ax.spines[s].set_linewidth(0.5)
    ax.set_title(title, loc="left", color=INK, fontsize=10.5)
    ax.set_ylabel("held-out score, %", color=MUTED, fontsize=9)
axes[1].set_xlabel("mode filter width (reference lines: accuracy)", color=MUTED, fontsize=9)
axes[0].legend(loc="lower left", bbox_to_anchor=(0, 1.08), ncol=2, frameon=False, fontsize=8.5, handlelength=1.8,
               borderaxespad=0)
fig.subplots_adjust(left=0.09, right=0.68, top=0.89, bottom=0.10, hspace=0.30)   # the right margin holds the labels
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
