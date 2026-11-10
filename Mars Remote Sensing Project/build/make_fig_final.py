# -*- coding: utf-8 -*-
r"""Charts the final paper and deck need that the interim never drew; all read from the logs, never retyped.

  final_img\depressions_vs_robbins.png   the ±60° closed depressions against Robbins by minimum diameter (KB §53.4,
                                         §69.45; logs\crater_recall_by_state.json, make_crater_recall_by_state.py):
                                         recall and precision beside the 3-diameter-shift chance baseline, each set cut
                                         at the minimum diameter only where it is scored (D32; the two-sided cut of
                                         global60_candidates_check.json understated both)
  final_img\svm_vs_unet.png              the four-class SVM map and the two-pass U-Net map under the same scorer
                                         (KB §57, §66.8; logs\global60_classification_check_200m_mode11.json and
                                         ..._global60_landforms_unet_200m_seamfix.json): producer's and user's per class
  final_img\svm_vs_unet_v2.png           the same for the seven-class SVM and U-Net on the 237 v2 held-out polygons
                                         (KB §69.24, §69.25)
  final_img2_vs_polygons.png           the four maps' held-out scores beside their estimates on the probability sample,
                                         the AI assistant's labels, its gate waived (KB §69.55, §69.79; the final deck only)
  final_img\extra_runs.png               the U-Net's window maps of the extra runs (make_v3_extras.py; KB §69.86, §69.88,
                                         §69.93): neither, cut only, added only, both, both without thermal (and rep, the
                                         second training, once scored), accuracy and balanced accuracy on both held-out sets
                                         with their block-bootstrap 95 % intervals; logs\v3_extras.json

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
    c = log("crater_recall_by_state.json")["curve_one_side_cut"]
    keys = sorted(c, key=float)
    x = range(len(keys))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), dpi=200)
    for ax, what, title in ((axes[0], "precision", "A  Precision: candidates that are catalogued craters"),
                            (axes[1], "recall", "B  Recall: catalogued craters found")):
        o = [100 * c[k][what + "_uncut"] for k in keys]
        b = [100 * c[k]["baseline_%s_uncut" % what] for k in keys]
        ax.plot(x, o, "-o", color=BLUE, lw=2, ms=6, zorder=3, label="closed depressions")
        ax.plot(x, b, "--o", color=PALE, lw=1.6, ms=5, zorder=2, label="chance (shifted 3 diameters east)")
        for i, v in enumerate(o):
            ax.text(i, v + 3, "%.1f" % v, ha="center", color=INK, fontsize=8.5)
        ax.set_xticks(list(x)); ax.set_xticklabels(["≥ %s" % k for k in keys])
        ax.set_xlabel("minimum diameter (km)", color=MUTED)
        ax.set_ylim(0, 100); ax.set_ylabel("%", color=MUTED)
        ax.set_title(title, loc="left", color=INK, fontsize=11)
        clean(ax)
    axes[0].legend(frameon=False, loc="lower right", bbox_to_anchor=(1, 0.3), fontsize=9)
    n = c["1"]["depressions"]
    fig.text(0.01, 0.01, "%s closed depressions ≥ 1 km over ±60° against the Robbins & Hynek database; a match is a centre "
             "within half the catalogued diameter and a diameter within a factor of 2;\n"
             "each set is cut at the minimum diameter only where it is scored." % format(n, ","),
             color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
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
        for j, (h, colour, label) in enumerate(((svm, ORANGE, "SVM 200 m, 11 × 11, four classes: %.1f %%, κ %.2f"
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


def svm_unet_v2(tag="v2", checks=("v2_200m_mode11", "global60_landforms_unet_v2_200m_seamfix")):
    """svm_unet() for the seven-class maps on the 237 v2 held-out polygons (KB §69.24, §69.25); tag v3 draws the v3 maps
    on the same polygons, the like-for-like set (KB §69.49)."""
    svm = log("global60_classification_check_%s.json" % checks[0])["held_out"]
    unet = log("global60_classification_check_%s.json" % checks[1])["held_out"]
    seven = CLASSES + ["volcanic edifice", "apron", "fluvial channel"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), dpi=200, sharey=True)
    w = 0.38
    for ax, what, title in ((axes[0], "producers", "A  Producer's accuracy (held-out area found)"),
                            (axes[1], "users", "B  User's accuracy (map class right)")):
        which = "seven classes" if tag == "v2" else "seven classes, v3 labels"
        for j, (h, colour, label) in enumerate(((svm, ORANGE, "SVM, %s: %.1f %%, κ %.2f"
                                                 % (which, 100 * svm["accuracy"], svm["kappa"])),
                                                (unet, BLUE, "U-Net, %s, two passes: %.1f %%, κ %.2f"
                                                 % (which, 100 * unet["accuracy"], unet["kappa"])))):
            v = [100 * h[what][c] for c in seven]
            xs = [i + (j - 0.5) * w for i in range(len(seven))]
            ax.bar(xs, v, w, color=colour, zorder=3, label=label)
            for xx, vv in zip(xs, v):
                ax.text(xx, vv + 1.5, "%.0f" % vv, ha="center", color=INK, fontsize=7.5)
        ax.set_xticks(range(len(seven)))
        ax.set_xticklabels(["Crater", "hills", "lava\ntube", "Normal\nGround", "volcanic\nedifice", "apron",
                            "fluvial\nchannel"], fontsize=8.5)
        ax.set_ylim(0, 110); ax.set_title(title, loc="left", color=INK, fontsize=11)
        clean(ax)
    axes[0].set_ylabel("%", color=MUTED)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=2, fontsize=9)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    p = os.path.join(OUT, "svm_vs_unet_%s.png" % tag)
    fig.savefig(p, facecolor="white"); plt.close(fig)
    print("wrote", p)


def r2_sample():
    """Each map's score on its held-out polygons beside its estimate on the probability sample (KB §69.55, §69.79)."""
    r = log(os.path.join("r2", "r2_agent_waived_result.json"))
    r["overall"].update({k: v for k, v in log(os.path.join("r2", "r2_v3_result.json"))["overall"].items() if k.endswith("_v3")})
    rows = [("Lead: U-Net, v3 labels", "unet_v3", "global60_landforms_unet_v3_200m_seamfix_on_v2_labels"),
            ("Lead: SVM, v3 labels", "svm_v3", "v3_200m_mode11_on_v2_labels"),
            ("Four-class SVM", "svm4", "200m_mode11"),
            ("Four-class U-Net", "unet4", "global60_landforms_unet_200m_seamfix"),
            ("Seven-class SVM", "svm7", "v2_200m_mode11"),
            ("Seven-class U-Net", "unet7", "global60_landforms_unet_v2_200m_seamfix")]
    fig, ax = plt.subplots(figsize=(10, 4.4), dpi=200)
    for y, (name, key, check) in enumerate(rows):
        h = 100 * log("global60_classification_check_%s.json" % check)["held_out"]["accuracy"]
        s = {k: 100 * v for k, v in r["overall"][key].items()}
        ax.plot([s["est"], h], [y, y], color=GRID, lw=1.2, zorder=1)
        ax.plot([s["lo"], s["hi"]], [y, y], color=ORANGE, lw=2, solid_capstyle="round", zorder=2)
        ax.plot(s["est"], y, "o", color=ORANGE, ms=8, zorder=3, label="probability sample, 95 % interval" if y == 0 else None)
        ax.plot(h, y, "o", mfc="white", mec=BLUE, mew=2, ms=8, zorder=3, label="held-out polygons" if y == 0 else None)
        near = h - s["est"] < 8                    # the two labels would touch
        ax.text(s["est"], y - 0.27, "%.1f" % s["est"], ha=("right" if s["est"] < h else "left") if near else "center", color=INK, fontsize=9)
        ax.text(h, y - 0.27, "%.1f" % h, ha=("left" if s["est"] < h else "right") if near else "center", color=INK, fontsize=9)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([x[0] for x in rows], color=INK)
    ax.set_ylim(len(rows) - 0.5, -0.65); ax.set_xlim(0, 100); ax.set_xlabel("overall accuracy (%)", color=MUTED)
    clean(ax)
    ax.grid(False); ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    ax.spines["left"].set_visible(False)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.text(0.01, 0.01, "Sample: %d of 175 points decided by the AI assistant, whose agreement on the hidden check points was "
             "%.1f %% against a 70 %% bar.\nPolygons: 183 for the four-class maps, 237 for the others."
             % (r["rows"], 100 * r["gate"]["agreement"]), color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    p = os.path.join(OUT, "r2_vs_polygons.png")
    fig.savefig(p, facecolor="white"); plt.close(fig)
    print("wrote", p)


def extra_runs():
    """What the v3 U-Net's score rests on: each window map of make_v3_extras.py on both held-out sets (KB §69.93)."""
    r = log("v3_extras.json")
    rows = [("unet_v2", "Neither: second label set"), ("cut", "Cut pieces only"), ("add", "Added polygons only"),
            ("base", "Both: third label set"), ("noth", "Both, without the thermal bands"),
            ("rep", "Both, trained a second time")]
    rows = [(k, n) for k, n in rows if k in r["v2_polygons"]["full"]]
    sets = [("v2_polygons", "237 v2 polygons", BLUE, -0.14), ("v3_polygons", "1,652 v3 polygons", ORANGE, 0.14)]
    fig, axes = plt.subplots(1, 2, figsize=(10, 0.62 * len(rows) + 1.5), dpi=200, sharey=True)
    for ax, metric, title in zip(axes, ("accuracy", "balanced"), ("A  Accuracy", "B  Balanced accuracy")):
        for y, (k, _) in enumerate(rows):
            for s, lab, col, dy in sets:
                v = 100 * r[s]["full"][k][metric]
                lo, hi = (100 * x for x in r[s]["block_bootstrap"][k][metric + "_ci95"])
                ax.plot([lo, hi], [y + dy, y + dy], color=col, lw=2, solid_capstyle="round", alpha=0.55, zorder=2)
                ax.plot(v, y + dy, "o", color=col, ms=7, mec="white", mew=1.2, zorder=3, label=lab if y == 0 else None)
                ax.text(hi + 1.2, y + dy, "%.1f" % v, va="center", color=INK, fontsize=8.5)
        ax.set_title(title, loc="left", color=INK, fontsize=11)
        ax.set_xlim(30, 105); ax.set_xlabel("% (dot: score; line: 95 % interval, the 14 blocks resampled)", color=MUTED, fontsize=8.5)
        clean(ax)
        ax.grid(False); ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
        ax.spines["left"].set_visible(False)
    axes[0].set_yticks(range(len(rows))); axes[0].set_yticklabels([n for _, n in rows], color=INK)
    axes[0].set_ylim(len(rows) - 0.5, -0.6)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, loc="upper right", ncol=2, fontsize=9)
    fig.text(0.01, 0.01, "U-Net window maps, one training each, the published model's settings; the first row is the published "
             "second-label-set map.", color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    p = os.path.join(OUT, "extra_runs.png")
    fig.savefig(p, facecolor="white"); plt.close(fig)
    print("wrote", p)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    depressions()
    svm_unet()
    svm_unet_v2()
    r2_sample()
    extra_runs()
    v3 = ("v3_200m_mode11_on_v2_labels", "global60_landforms_unet_v3_200m_seamfix_on_v2_labels")
    if all(os.path.exists(os.path.join(HERE, "logs", "global60_classification_check_%s.json" % c)) for c in v3):
        svm_unet_v2("v3", v3)
