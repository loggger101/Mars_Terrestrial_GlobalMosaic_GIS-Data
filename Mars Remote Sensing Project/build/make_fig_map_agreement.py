# -*- coding: utf-8 -*-
r"""Figure for A6: where the SVM and U-Net maps agree over ±60° (NEXT-STEPS §12.2 A6, §12.4 W4).

Two panels, centred on 0°E as the paper's maps, ticks in degrees east 0-360: the four-class pair (the published SVM
map against the two-pass U-Net) and the seven-class pair. Where both maps give the same class, that class's map colour
(labelsets.COLOURS); where they differ, light grey. Each panel's title gives the share of ±60° in agreement; the
legend gives each class's intersection over union. Light ground, Arial, as make_fig_block_split.py.
Reads logs\map_agreement.json and map_agreement_<pair>_3200m.npy (make_map_agreement.py); writes
build\final_img\map_agreement.png. System Python.
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from labelsets import FOUR, SEVEN, COLOURS

R = json.load(open(os.path.join(HERE, "logs", "map_agreement.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "final_img", "map_agreement.png")
INK, MUTED, DIFFER = "#1A1A1A", "#5A6570", "#D9DEE3"
PANELS = [("four", FOUR, "Four classes: published SVM map against the two-pass U-Net"),
          ("v2", SEVEN, "Seven classes: SVM against U-Net")]

plt.rcParams.update({"font.family": "Arial", "font.size": 10})
fig, axes = plt.subplots(2, 1, figsize=(10, 7.6), dpi=200)
for ax, (key, names, title) in zip(axes, PANELS):
    d = R[key]
    a = np.load(os.path.join(HERE, "map_agreement_%s_3200m.npy" % key))
    g = d["grid_400m"]; step = d["figure_step"]
    lut = np.ones((256, 3))
    for i, n in enumerate(names):
        lut[i] = np.array(COLOURS[n]) / 255
    lut[255] = matplotlib.colors.to_rgb(DIFFER)                     # disagree; 254 (outside) stays white
    img = lut[a]
    dpx = g["dpx"] * step
    lon0 = g["lon_left"] % 360
    shift = int(round(((180 - lon0) % 360) / dpx))                  # put 180°E at the left edge: centred on 0°E
    img = np.roll(img, shift, axis=1)
    top = g["lat_top"]; bottom = top - a.shape[0] * g["dpy"] * step
    ax.imshow(img, extent=[-180, -180 + a.shape[1] * dpx, bottom, top], interpolation="nearest", aspect="equal")
    ax.set_xlim(-180, 180); ax.set_ylim(-60, 60)
    ax.set_xticks(range(-180, 181, 60))
    ax.set_xticklabels(["%d°E" % (x % 360) for x in range(-180, 181, 60)], color=MUTED, fontsize=8.5)
    ax.set_yticks([-60, -30, 0, 30, 60])
    ax.set_yticklabels(["60°S", "30°S", "0°", "30°N", "60°N"], color=MUTED, fontsize=8.5)
    for s in ax.spines.values():
        s.set_color(MUTED); s.set_linewidth(0.5)
    ax.set_title("%s  ·  agree on %.1f%% of ±60°" % (title, 100 * d["agreement"]), loc="left", color=INK, fontsize=11)
    handles = [Patch(facecolor=np.array(COLOURS[n]) / 255, label="%s  (IoU %.2f)" % (n, d["classes"][n]["iou"] or 0))
               for n in names] + [Patch(facecolor=DIFFER, label="the maps differ")]
    ax.legend(handles=handles, fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False,
              labelcolor=INK)
fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
