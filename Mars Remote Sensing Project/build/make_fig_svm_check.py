# -*- coding: utf-8 -*-
r"""Figure: the two Pro-GUI SVM classifications (KB §29, §30) checked against independent evidence.

A  29 Sep SVM over the ±60° segments - the 4096-px processing tiles drawn over it
B  30 Sep SVM over the 7-band CompositeBand - the ±60° edge of the thermal bands marked
C  training-set score: how much of his own polygons each map gives back, per class
D  IAU named craters: 'Crater' inside the rim against a ring outside it

Reads logs\svm_check.json and the two pyramid-level caches written by
verify_svm_classifications.py. Run that first.
"""
import os, json, textwrap
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(HERE, "logs", "svm_check.json")))
night = np.load(os.path.join(HERE, "svm_night_ov4.npy"))
night = np.roll(night, night.shape[1] // 2, axis=1)            # CM 180 -> CM 0
comp7 = np.load(os.path.join(HERE, "svm_comp7_ov3.npy"))

BG, CY, SUB, WARN = "#0E2841", "#0E9ED4", "#9ED8ED", "#E8804A"
NAMES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
COLS = ["#FF0000", "#1C7755", "#9E1993", "#51330D"]                # his RAT colours
CMAP = ListedColormap(COLS)
KPD = 3396.19 * np.pi / 180.0
TILE_DEG = 4096 * 100 / 1000 / KPD                                 # 4096 px at 100 m = 6.91 deg


fig = plt.figure(figsize=(16, 12.6), facecolor=BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.78], hspace=0.42, wspace=0.26,
                      left=0.045, right=0.985, top=0.93, bottom=0.17)


def frame(ax):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color("#3A5A7A")
    ax.tick_params(colors=SUB, labelsize=8.5)


def caption(ax, s, width, colour=SUB, y=-0.14):
    ax.text(0.0, y, textwrap.fill(s, width), transform=ax.transAxes, color=colour,
            fontsize=8.8, va="top", linespacing=1.35)


def title(ax, s):
    ax.set_title(s, color=CY, fontsize=11.5, loc="left", pad=8)


# A ---------------------------------------------------------------------------
axA = fig.add_subplot(gs[0, :])
axA.imshow(night, extent=[-180, 180, -60, 60], cmap=CMAP, vmin=-.5, vmax=3.5,
           interpolation="nearest")
# tile edges: column 0 of the night grid is 0 E, so its tiles start at 0 E and 60 N
for k in range(int(360 / TILE_DEG) + 1):
    axA.axvline(((k * TILE_DEG + 180) % 360) - 180, color="white", lw=0.4, alpha=0.6)
for k in range(int(120 / TILE_DEG) + 1):
    axA.axhline(60 - k * TILE_DEG, color="white", lw=0.4, alpha=0.6)
axA.set_xlim(-180, 180); axA.set_ylim(-60, 60)
axA.set_xticks(range(-180, 181, 30)); axA.set_yticks(range(-60, 61, 30))
title(axA, "A   29 Sep SVM over the ±60° segments + Night IR: one class per processing tile")
ts = res["night"]["training_score"]
caption(axA, "White lines: the 4096 px × 100 m = %.2f° tile grid, drawn from arithmetic, "
        "not from the map. The class edges fall on it: every measured vertical edge is a whole "
        "number of tiles from the last. Each tile has come out mostly one class, so the map "
        "records which tile a pixel is in, not the terrain under it." % TILE_DEG, 190, y=-0.075)
frame(axA)
axA.legend(handles=[Patch(color=c, label=n) for c, n in zip(COLS, NAMES)],
           loc="lower right", bbox_to_anchor=(1.0, 1.005), ncol=4, frameon=False,
           labelcolor=SUB, fontsize=9.5, handlelength=1.2, borderaxespad=0)

# B ---------------------------------------------------------------------------
axB = fig.add_subplot(gs[1, 0])
axB.imshow(comp7, extent=[-180, 180, -90, 90], cmap=CMAP, vmin=-.5, vmax=3.5,
           interpolation="nearest")
for y in (60, -60):
    axB.axhline(y, color=WARN, lw=1.1, ls="--")
axB.set_xlim(-180, 180); axB.set_ylim(-90, 90); axB.set_anchor("N")
axB.set_xticks(range(-180, 181, 90)); axB.set_yticks(range(-90, 91, 30))
title(axB, "B   30 Sep SVM, 7-band composite")
eo = res["comp7"]["elevation_only_reproduces"]
lc = res["comp7"]["largest_class_alone"]
sb = res["comp7"]["share_by_lat"]["-90..-60"]
caption(axB, "Elevation sets the class: 500 m elevation bins alone reproduce %.0f%% of this map at "
        "±60° (the largest class alone: %.0f%%). Lowlands come out Normal Ground, "
        "highlands lava tube, Tharsis 'Crater'. Past the dashed lines the thermal bands are "
        "empty; %.0f%% of the south polar region is 'Crater'." % (100 * eo, 100 * lc, 100 * sb[0]), 62)
frame(axB)

# C ---------------------------------------------------------------------------
axC = fig.add_subplot(gs[1, 1])
x = np.arange(4); wbar = 0.38
for i, (key, col, lab) in enumerate([("night", WARN, "29 Sep"), ("comp7", CY, "30 Sep")]):
    t = res[key]["training_score"]
    own = [t["row_normalised"][j][j] for j in range(4)]
    bars = axC.bar(x + (i - .5) * wbar, [100 * o for o in own], wbar, color=col,
                   label="%s   %.0f%%, κ %.2f" % (lab, 100 * t["accuracy"], t["kappa"]))
    for b_, o, j in zip(bars, own, range(4)):
        axC.text(b_.get_x() + b_.get_width() / 2, 100 * o + 1.5,
                 t["polygons_majority_own_class"][NAMES[j]], ha="center", color="white", fontsize=7.4)
axC.set_xticks(x); axC.set_xticklabels(["Crater", "steep/windy\nhills", "lava tube", "Normal\nGround"],
                                       color=SUB, fontsize=8.8)
axC.set_ylim(0, 122); axC.set_ylabel("% of polygon area returned as its own class", color=SUB, fontsize=8.8)
axC.legend(frameon=False, labelcolor="white", fontsize=9, loc="upper left", ncol=2)
title(axC, "C   His 512 polygons, scored on each map")
caption(axC, "A training-set score: the upper bound on accuracy. Over each bar, polygons whose own "
        "class wins. A map that says Normal Ground everywhere scores %.0f%%; the 29 Sep map scores "
        "%.0f%% and returns none of his 122 Normal Ground or 44 lava tube polygons."
        % (100 * res["night"]["training_score"]["one_class_everywhere"],
           100 * res["night"]["training_score"]["accuracy"]), 62, colour=WARN, y=-0.2)
frame(axC)

# D ---------------------------------------------------------------------------
axD = fig.add_subplot(gs[1, 2])
ticks, labs = [], []
for i, (key, col, lab) in enumerate([("night", WARN, "29 Sep"), ("comp7", CY, "30 Sep")]):
    c = res[key]["iau_craters"]
    x0 = i * 2.6
    axD.bar([x0, x0 + 1], [100 * c["crater_inside"], 100 * c["crater_ring"]], 0.9, color=[col, "#3A5A7A"])
    axD.text(x0, 100 * c["crater_inside"] + 2, "inside\n%.0f%%" % (100 * c["crater_inside"]),
             ha="center", color="white", fontsize=8.6)
    axD.text(x0 + 1, 100 * c["crater_ring"] + 2, "ring\n%.0f%%" % (100 * c["crater_ring"]),
             ha="center", color="white", fontsize=8.6)
    ticks.append(x0 + .5)
    labs.append("%s, %d craters\ninside > ring for %.0f%%" % (lab, c["n"], c["pct_inside_gt_ring"]))
axD.set_xticks(ticks); axD.set_xticklabels(labs, color=SUB, fontsize=8.8)
axD.set_xlim(-0.8, 4.4); axD.set_ylim(0, 100)
axD.set_ylabel("% of pixels classed 'Crater'", color=SUB, fontsize=8.8)
title(axD, "D   IAU named craters ≥ 5 km")
ag = res["agreement"]
caption(axD, "'Crater' inside the rim (0–0.7 R) against a ring outside it (1.5–2.5 R); "
        "craters near any training polygon left out. A map with no skill gives inside ≈ ring. "
        "The two maps agree on %.0f%% of ±60° against %.0f%% by chance "
        "(κ %.2f): they are close to independent."
        % (100 * ag["agreement"], 100 * (ag["agreement"] - ag["kappa"]) / (1 - ag["kappa"]), ag["kappa"]),
        62, y=-0.2)
frame(axD)

fig.suptitle("His two SVM classifications, checked against his own labels, the IAU craters and the DEM",
             color="white", fontsize=15, x=0.045, ha="left", y=0.985)
out = os.path.join(HERE, "pres1_img", "svm_check.png")
fig.savefig(out, dpi=110, facecolor=BG)
print("wrote", out)
