# -*- coding: utf-8 -*-
r"""Figure: the two lead maps (third label set, seven classes) against the unit groups of SIM 3292 (KB §69.81, §69.146).

The seven-class form of the T8 chart (make_fig_t8.py, the four-class map): for each map, how much more often each
class occurs in a unit group than across ±60° (enrichment, P(class | group) / P(class)), with the class's share of the
group beneath it. Read from make_geomap_check.py's logs, never retyped:
  (a) logs\geomap_check_global60_landforms_unet_v3_200m_seamfix.json   the U-Net
  (b) logs\geomap_check_v3.json                                        the support vector machine
-> final_img\geomap_v3.png. Same groups, order, bins and colours as make_fig_t8.py and layout 13c. The two cells
outlined are those the label rules placed on the unit itself (Appendix A: volcanic edifice on edifice units, apron on
apron units), so their match is in part built in. System Python (matplotlib).
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final_img", "geomap_v3.png")
LOGS = [("(a) U-Net", "geomap_check_global60_landforms_unet_v3_200m_seamfix.json"),
        ("(b) Support vector machine", "geomap_check_v3.json")]
INK, MUTED = "#1A1A1A", "#5A6570"
plt.rcParams.update({"font.family": "Arial", "font.size": 11})
CLASSES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground", "volcanic edifice", "apron", "fluvial channel"]
HEAD = ["Crater", "steep/windy\nhills", "lava tube", "Normal\nGround", "volcanic\nedifice", "apron", "fluvial\nchannel"]
GROUPS = [("v", "Volcanic"), ("ve", "Volcanic edifice"), ("vf", "Volcanic field"),
          ("h", "Highland"), ("hm", "Highland massif"), ("hu", "Highland undivided"),
          ("i", "Impact"), ("a", "Apron"), ("t", "Transition"), ("tu", "Transition undivided"),
          ("l", "Lowland"), ("p", "Polar")]
BUILT_IN = {("ve", "volcanic edifice"), ("a", "apron")}
BLUE, GREY, RED = (42, 120, 214), (240, 239, 236), (227, 73, 72)
mix = lambda a, b, t: tuple((a[i] + (b[i] - a[i]) * t) / 255 for i in range(3))
BINS = [(0, 0.5, mix(BLUE, BLUE, 0), "white", "under ×0.5"), (0.5, 0.8, mix(GREY, BLUE, 0.45), INK, "×0.5–0.8"),
        (0.8, 1.25, mix(GREY, GREY, 0), INK, "×0.8–1.25"), (1.25, 2, mix(GREY, RED, 0.45), INK, "×1.25–2"),
        (2, 1e9, mix(RED, RED, 0), INK, "over ×2")]
W0, W1, CW, RH = 2.5, 0.8, 1.25, 1.0


def panel(ax, title, d):
    n = len(GROUPS)
    ax.text(0, n + 1.55, title, fontsize=12.5, color=INK, weight="bold", va="center")
    for j, c in enumerate(HEAD):
        ax.text(W0 + W1 + CW * (j + 0.5), n + 0.5, c, ha="center", va="center", fontsize=9.5, color=INK, weight="bold")
    ax.text(W0 + W1 / 2, n + 0.5, "area", ha="center", va="center", fontsize=9.5, color=MUTED)
    for i, (code, name) in enumerate(GROUPS):
        y = n - 1 - i
        g = d["groups"][code]
        ax.text(0, y + 0.5, "%s (%s)" % (name, code), va="center", fontsize=10, color=INK)
        a = g["area_share"]
        ax.text(W0 + W1 - 0.1, y + 0.5, "%.1f%%" % (100 * a) if a >= 0.0005 else "< 0.1%", ha="right", va="center",
                fontsize=9.5, color=MUTED)
        for j, c in enumerate(CLASSES):
            e, sh = g["classes"][c]["enrichment"], g["classes"][c]["share_in_group"]
            _, _, fill, ink, _ = next(b for b in BINS if b[0] <= e < b[1])
            x = W0 + W1 + CW * j
            ax.add_patch(Rectangle((x + 0.04, y + 0.06), CW - 0.08, RH - 0.12, color=fill, lw=0))
            if (code, c) in BUILT_IN:
                ax.add_patch(Rectangle((x + 0.04, y + 0.06), CW - 0.08, RH - 0.12, fill=False, ec=INK, lw=2.2))
            ax.text(x + CW / 2, y + 0.5, "×%.2f (%.0f%%)" % (e, 100 * sh) if sh >= 0.005 else "×%.2f (<1%%)" % e,
                    ha="center", va="center", fontsize=8.6, color=ink)
    ax.text(0, -0.5, "all ±60°: class share", va="center", fontsize=10, color=INK)
    for j, c in enumerate(CLASSES):
        ax.text(W0 + W1 + CW * (j + 0.5), -0.5, "%.1f%%" % (100 * d["p_class"][c]), ha="center", va="center",
                fontsize=9.5, color=MUTED)
    ax.set_xlim(-0.05, W0 + W1 + CW * 7 + 0.05)
    ax.set_ylim(-1.0, n + 2.0)
    ax.axis("off")


def main():
    fig = plt.figure(figsize=(12.5, 12.4))
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 0.13], hspace=0.02)
    for k, (title, f) in enumerate(LOGS):
        d = json.load(open(os.path.join(HERE, "logs", f), encoding="utf-8"))
        panel(fig.add_subplot(gs[k]), title, d)
    ax = fig.add_subplot(gs[2]); ax.axis("off"); ax.set_xlim(0, 12.5); ax.set_ylim(0, 1)
    ax.text(0, 0.8, "Enrichment, P(class | group) ÷ P(class), ×1 being no association; in brackets the class's "
            "share of the group", fontsize=9.5, color=INK, va="center")
    x = 0.0
    for _, _, fill, ink, lab in BINS:
        ax.add_patch(Rectangle((x, 0.08), 0.35, 0.42, color=fill, lw=0))
        ax.text(x + 0.45, 0.29, lab, fontsize=9, color=INK, va="center")
        x += 1.55
    ax.add_patch(Rectangle((x + 0.2, 0.08), 0.35, 0.42, fill=False, ec=INK, lw=2.2))
    ax.text(x + 0.65, 0.29, "labels placed on this unit (Appendix A)", fontsize=9, color=INK, va="center")
    fig.savefig(OUT, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
