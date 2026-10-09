# -*- coding: utf-8 -*-
r"""Figure for test T8 (KB §43.2, §49), for the interim deck and report: the enrichment table of layout 13,
legible at slide size (the whole sheet, map and table, is too tall for a slide; layout 13 stays the Pro sheet).

Read from logs\geomap_check.json, never retyped -> interim_img\t8_enrichment.png. Same groups, order, bins and
colours as layout 13 (make_geomap_sheet.py): diverging blue - grey - red, the dataviz reference pair.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "interim_img", "t8_enrichment.png")
INK, MUTED = "#1A1A1A", "#5A6570"
plt.rcParams.update({"font.family": "Arial", "font.size": 11})
CLASSES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
GROUPS = [("v", "Volcanic"), ("ve", "Volcanic edifice"), ("vf", "Volcanic field"),
          ("h", "Highland"), ("hm", "Highland massif"), ("hu", "Highland undivided"),
          ("i", "Impact"), ("a", "Apron"), ("t", "Transition"), ("tu", "Transition undivided"),
          ("l", "Lowland"), ("p", "Polar")]
BLUE, GREY, RED = (42, 120, 214), (240, 239, 236), (227, 73, 72)
mix = lambda a, b, t: tuple((a[i] + (b[i] - a[i]) * t) / 255 for i in range(3))
BINS = [(0, 0.5, mix(BLUE, BLUE, 0), "white", "under ×0.5"), (0.5, 0.8, mix(GREY, BLUE, 0.45), INK, "×0.5–0.8"),
        (0.8, 1.25, mix(GREY, GREY, 0), INK, "×0.8–1.25"), (1.25, 2, mix(GREY, RED, 0.45), INK, "×1.25–2"),
        (2, 1e9, mix(RED, RED, 0), INK, "over ×2")]

d = json.load(open(os.path.join(HERE, "logs", "geomap_check.json"), encoding="utf-8"))
fig, ax = plt.subplots(figsize=(11, 4.6))
W0, W1, CW, RH = 2.4, 0.9, 1.6, 1.0
n = len(GROUPS)
for j, c in enumerate(CLASSES):
    ax.text(W0 + W1 + CW * (j + 0.5), n + 0.35, c, ha="center", va="center", fontsize=11, color=INK, weight="bold")
ax.text(W0 + W1 / 2, n + 0.35, "area", ha="center", va="center", fontsize=10, color=MUTED)
for i, (code, name) in enumerate(GROUPS):
    y = n - 1 - i
    g = d["groups"][code]
    ax.text(0, y + 0.5, "%s (%s)" % (name, code), va="center", fontsize=10.5, color=INK)
    a = g["area_share"]
    ax.text(W0 + W1 - 0.1, y + 0.5, "%.1f%%" % (100 * a) if a >= 0.0005 else "< 0.1%", ha="right", va="center",
            fontsize=10, color=MUTED)
    for j, c in enumerate(CLASSES):
        e, sh = g["classes"][c]["enrichment"], g["classes"][c]["share_in_group"]
        _, _, fill, ink, _ = next(b for b in BINS if b[0] <= e < b[1])
        x = W0 + W1 + CW * j
        ax.add_patch(Rectangle((x + 0.04, y + 0.06), CW - 0.08, RH - 0.12, color=fill, lw=0))
        ax.text(x + CW / 2, y + 0.5, "×%.2f" % e, ha="center", va="center", fontsize=10.5, color=ink)
kx = W0 + W1 + CW * 4 + 0.35
ax.text(kx, n - 0.4, "Enrichment", fontsize=10, color=INK, weight="bold", va="center")
ax.text(kx, n - 1.0, "P(class | group) ÷ P(class)", fontsize=9, color=MUTED, va="center")
for k, (_, _, fill, ink, lab) in enumerate(BINS):
    y = n - 2.3 - k * 0.9
    ax.add_patch(Rectangle((kx, y), 0.5, 0.7, color=fill, lw=0))
    ax.text(kx + 0.65, y + 0.35, lab, fontsize=9.5, color=INK, va="center")
ax.set_xlim(-0.05, kx + 2.0); ax.set_ylim(-0.1, n + 0.8)
ax.axis("off")
fig.tight_layout()
fig.savefig(OUT, dpi=100, facecolor="white")
print("wrote", OUT)
