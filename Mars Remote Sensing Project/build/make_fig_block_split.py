# -*- coding: utf-8 -*-
r"""Figure for W4: the held-out split, the 15° blocks and the labels by class (NEXT-STEPS §12.4; KB §31.3, §69.41).

Two panels over ±60°, centred on 0°E as the paper's maps, ticks in degrees east 0-360 as its text: the four-class
labels (512) and the seven-class labels (971). Blocks with training labels light grey, held-out blocks blue with a darker edge, the
grid of 15° blocks a hairline; each label a dot at its label point in its class's map colour (labelsets.COLOURS),
held-out labels ringed. Light ground, Arial, as make_fig_crater_sfd.py.
Reads logs\block_split.json (make_block_split.py); writes build\final_img\block_split.png. System Python.
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from labelsets import FOUR, SEVEN, COLOURS

R = json.load(open(os.path.join(HERE, "logs", "block_split.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "final_img", "block_split.png")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
TRAIN_FILL, TEST_FILL, TEST_EDGE = "#E4E7EB", "#CFE3F7", "#2A78D6"
PANELS = [("four", FOUR, "Four classes"), ("v2", SEVEN, "Seven classes")]


def block_box(b):
    """A Block field ("i_j": floor(lon / 15), floor(lat / 15), longitude -180..180): its south-west corner."""
    i, j = (int(k) for k in b.split("_"))
    return i * 15, j * 15


def west(lon_e):
    """Degrees east 0-360 to -180..180, so the figure is centred on 0°E like the paper's maps."""
    return lon_e - 360 if lon_e >= 180 else lon_e


def rgb(c):
    return tuple(v / 255.0 for v in COLOURS[c])


plt.rcParams.update({"font.family": "Arial", "font.size": 10})
fig, axes = plt.subplots(2, 1, figsize=(10, 7.6), dpi=200)
for ax, (key, names, label) in zip(axes, PANELS):
    s = R[key]
    for blocks, fill, edge, lw, z in ((s["train_blocks"], TRAIN_FILL, "none", 0, 1),
                                      (s["test_blocks"], TEST_FILL, TEST_EDGE, 1.3, 2)):
        for b in blocks:
            x, y = block_box(b)
            ax.add_patch(Rectangle((x, y), 15, 15, facecolor=fill, edgecolor=edge, lw=lw, zorder=z))
    for v in range(-180, 181, 15):
        ax.axvline(v, color=GRID, lw=0.5, zorder=0)
    for h in range(-60, 61, 15):
        ax.axhline(h, color=GRID, lw=0.5, zorder=0)
    ax.axhline(0, color=MUTED, lw=0.6, zorder=0.5)
    for k, cls in enumerate(names, 1):           # the larger classes first, so the rarer dots sit on top
        for split, ec, size in (("train", "none", 9), ("test", INK, 13)):
            pts = [(west(p["lon_e"]), p["lat"]) for p in s["polygons"] if p["cls"] == k and p["split"] == split]
            if pts:
                x, y = zip(*pts)
                ax.scatter(x, y, s=size, color=rgb(cls), edgecolors=ec, linewidths=0.6, zorder=3 + k / 10.0)
    ax.set_xlim(-180, 180); ax.set_ylim(-60, 60)
    ax.set_aspect("equal")
    ax.set_xticks(range(-180, 181, 45)); ax.set_xticklabels(["%d°E" % (v % 360) for v in range(-180, 181, 45)])
    ax.set_yticks(range(-60, 61, 30)); ax.set_yticklabels(["60°S", "30°S", "0°", "30°N", "60°N"])
    ax.tick_params(colors=MUTED, length=0, labelsize=8.5)
    for sp in ax.spines.values():
        sp.set_color(GRID)
    ax.set_title("%s: %d training labels in %d blocks; %d held out in %d blocks"
                 % (label, s["n_train"], len(s["train_blocks"]), s["n_test"], len(s["test_blocks"])),
                 loc="left", color=INK, fontsize=11)
    handles = [Line2D([], [], ls="", marker="o", ms=5.5, color=rgb(c),
                      label="%s  %d / %d" % (c, s["per_class"][c]["train"], s["per_class"][c]["test"]))
               for c in names]
    ax.legend(handles=handles, title="class  training / held out", title_fontsize=8.5, fontsize=8.5,
              frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1.0), labelcolor=INK, handletextpad=0.3)
fig.legend(handles=[Patch(facecolor=TRAIN_FILL, label="15° block with training labels"),
                    Patch(facecolor=TEST_FILL, edgecolor=TEST_EDGE, label="held-out block (the same 14 in both)"),
                    Line2D([], [], ls="", marker="o", ms=5, mfc="white", mec=INK, label="held-out label")],
           loc="lower center", ncol=3, frameon=False, fontsize=9, labelcolor=INK)
assert R["same_held_out_blocks"], "the two label sets no longer hold out the same blocks: fix the legend"
fig.tight_layout(rect=(0, 0.04, 1, 1))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
