# -*- coding: utf-8 -*-
r"""Two charts the final paper and deck need that the interim never drew; both read from the logs, never retyped.

  final_img\depressions_vs_robbins.png   the ±60° closed depressions against Robbins by minimum diameter (KB §53.4,
                                         §54.4; logs\global60_candidates_check.json, run 3): recall and precision
                                         beside the 3-diameter-shift chance baseline
  final_img\svm_vs_unet.png              the published SVM map and the two-pass U-Net map under the same scorer
                                         (KB §57, §66.8; logs\global60_classification_check_200m_mode11.json and
                                         ..._global60_landforms_unet_200m_seamfix.json): producer's and user's per class

Light ground, the palette of the interim charts (accuracy_200m.png). System Python:  py -3.13 make_fig_final.py
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final_img")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
BLUE, ORANGE, PALE = "#2E7BD6", "#EE6A2F", "#B3BAC0"
CLASSES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]


def log(name):
    return json.load(open(os.path.join(HERE, "logs", name), encoding="utf-8"))


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)


def depressions():
    d = log("global60_candidates_check.json")
    obs, base = d["robbins"], d["robbins_shifted_3D"]
    keys = sorted(obs, key=float)
    x = range(len(keys))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), dpi=200)
    for ax, what, title in ((axes[0], "precision", "A  Precision: candidates that are catalogued craters"),
                            (axes[1], "recall", "B  Recall: catalogued craters found")):
        o = [100 * obs[k][what] for k in keys]
        b = [100 * base[k][what] for k in keys]
        ax.plot(x, o, "-o", color=BLUE, lw=2, ms=6, zorder=3, label="closed depressions")
        ax.plot(x, b, "--o", color=PALE, lw=1.6, ms=5, zorder=2, label="chance (shifted 3 diameters east)")
        for i, v in enumerate(o):
            ax.text(i, v + 3, "%.1f" % v, ha="center", color=INK, fontsize=8.5)
        ax.set_xticks(list(x)); ax.set_xticklabels(["≥ %s" % k for k in keys])
        ax.set_xlabel("minimum diameter (km)", color=MUTED)
        ax.set_ylim(0, 100); ax.set_ylabel("%", color=MUTED)
        ax.set_title(title, loc="left", color=INK, fontsize=11)
        clean(ax)
    axes[0].legend(frameon=False, loc="upper left", fontsize=9)
    n = obs["1"]["candidates"]
    fig.text(0.01, 0.01, "%s closed depressions ≥ 1 km over ±60° against the Robbins & Hynek database; a match is a centre "
             "within half the catalogued diameter and a diameter within a factor of 2." % format(n, ","),
             color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    p = os.path.join(OUT, "depressions_vs_robbins.png")
    fig.savefig(p, facecolor="white"); plt.close(fig)
    print("wrote", p)


def svm_unet():
    svm = log("global60_classification_check_200m_mode11.json")["held_out"]
    unet = log("global60_classification_check_global60_landforms_unet_200m_seamfix.json")["held_out"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), dpi=200, sharey=True)
    w = 0.36
    for ax, what, title in ((axes[0], "producers", "A  Producer's accuracy (held-out area found)"),
                            (axes[1], "users", "B  User's accuracy (map class right)")):
        for j, (h, colour, label) in enumerate(((svm, ORANGE, "SVM 200 m, 11 × 11 (published): %.1f %%, κ %.2f"
                                                 % (100 * svm["accuracy"], svm["kappa"])),
                                                (unet, BLUE, "U-Net, two passes: %.1f %%, κ %.2f"
                                                 % (100 * unet["accuracy"], unet["kappa"])))):
            v = [100 * h[what][c] for c in CLASSES]
            xs = [i + (j - 0.5) * w for i in range(4)]
            ax.bar(xs, v, w, color=colour, zorder=3, label=label)
            for xx, vv in zip(xs, v):
                ax.text(xx, vv + 1.5, "%.0f" % vv, ha="center", color=INK, fontsize=8.5)
        ax.set_xticks(range(4)); ax.set_xticklabels(["Crater", "steep/windy\nhills", "lava tube", "Normal\nGround"])
        ax.set_ylim(0, 110); ax.set_title(title, loc="left", color=INK, fontsize=11)
        clean(ax)
    axes[0].set_ylabel("%", color=MUTED)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=2, fontsize=9)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    p = os.path.join(OUT, "svm_vs_unet.png")
    fig.savefig(p, facecolor="white"); plt.close(fig)
    print("wrote", p)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    depressions()
    svm_unet()
