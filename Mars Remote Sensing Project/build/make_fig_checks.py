# -*- coding: utf-8 -*-
r"""Three results that had a log and a KB table but no figure (KB §64), for the repo and the deck.

Read from the logs, never retyped:
  logs\global60_classification_check_200m_mode11.json  -> interim_img\accuracy_200m.png
        A: the published map's held-out confusion, area-weighted, each row a hand-drawn class (rows
           sum to 100 %), producer's accuracy on the diagonal, user's accuracy under each column;
        B: held-out accuracy against the majority window, 200 m and 400 m, from
           global60_classification_check_{200m,400m}[_modeN].json, the one-class line, 11 x 11 marked
           (KB §55.3, §57)
  logs\crater_density.json   -> interim_img\t2_density.png   T2: craters >= 1 km per 10^6 km² on each
        geologic unit >= 20,000 km² of each window, Robbins against the detector (KB §42.2)
  logs\lava_relabel_test.json -> interim_img\lava_relabel.png  the lava-tube relabel, variants A-D:
        held-out accuracy on the Crater / hills / Normal Ground polygons (KB §43.3)

Colours: the deck's validated pair (blue / orange, KB §45), as make_fig_tests567.py; light ground.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(HERE, "interim_img")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "Arial", "font.size": 11})
CLASSES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]


def load(name):
    with open(os.path.join(HERE, "logs", name), encoding="utf-8") as f:
        return json.load(f)


def tidy(ax, grid="x"):
    ax.grid(axis=grid, color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)


def save(fig, name, tight=True):
    if tight:
        fig.tight_layout()
    os.makedirs(OUTD, exist_ok=True)
    p = os.path.join(OUTD, name)
    fig.savefig(p, dpi=150, facecolor="white")
    plt.close(fig)
    print("wrote", p)


def mix(t):
    """white -> the deck's blue, t in 0..1."""
    b = (42, 120, 214)
    return tuple((255 + (c - 255) * t) / 255 for c in b)


# ------------------------------------------------------------------ the published map
pub = load("global60_classification_check_200m_mode11.json")
h = pub["held_out"]
cm = h["confusion_area_weighted"]                       # rows: hand-drawn class; columns: map class
rows = [sum(r) for r in cm]
assert abs(rows[0] - h["one_class_everywhere"]) < 0.002          # rows are the labels (Crater is the majority)
assert abs(cm[0][0] / rows[0] - h["producers"]["Crater"]) < 0.002
fig = plt.figure(figsize=(12.5, 5.0))
ax = fig.add_axes([0.02, 0.10, 0.50, 0.80])
n = len(CLASSES)
for i, c in enumerate(CLASSES):
    y = n - 1 - i
    for j in range(n):
        v = cm[i][j] / rows[i]
        ax.add_patch(Rectangle((j + 0.03, y + 0.03), 0.94, 0.94, color=mix(min(v, 1.0)), lw=0))
        ax.text(j + 0.5, y + 0.5, "%.0f %%" % (100 * v), ha="center", va="center", fontsize=11,
                color="white" if v > 0.55 else INK, weight="bold" if i == j else "normal")
    ax.text(-0.08, y + 0.5, "%s\n%.0f %% of the held-out area" % (c, 100 * rows[i]), ha="right", va="center", fontsize=10,
            color=INK)
for j, c in enumerate(CLASSES):
    ax.text(j + 0.5, n + 0.12, c, ha="center", va="bottom", fontsize=10, color=INK)
    ax.text(j + 0.5, -0.12, "user's %.0f %%" % (100 * h["users"][c]), ha="center", va="top", fontsize=9.5,
            color=ORANGE if h["users"][c] < 0.1 else MUTED, weight="bold" if h["users"][c] < 0.1 else "normal")
ax.text(n / 2, n + 0.55, "map class", ha="center", fontsize=10, color=MUTED)
ax.text(-2.1, n + 0.55, "hand-drawn class (held out)", ha="left", fontsize=10, color=MUTED)
ax.set_xlim(-2.2, n + 0.05); ax.set_ylim(-0.6, n + 0.85); ax.axis("off")
ax.set_title("A  Where each held-out class lands: %.1f %% overall, κ %.2f, %d polygons"
             % (100 * h["accuracy"], h["kappa"], h["polygons"]), loc="left", fontsize=11.5, color=INK, pad=4)

ax = fig.add_axes([0.60, 0.17, 0.38, 0.70])
for cell, col, sizes in ((200, BLUE, (None, 3, 5, 7, 9, 11)), (400, ORANGE, (None, 3, 5, 7, 9))):
    xs, ys = [], []
    for s in sizes:
        f = "global60_classification_check_%dm%s.json" % (cell, "" if s is None else "_mode%d" % s)
        xs.append(1 if s is None else s); ys.append(100 * load(f)["held_out"]["accuracy"])
    ax.plot(xs, ys, "o-", color=col, lw=2, ms=7, mec="white", mew=1.5, label="%d m map" % cell, zorder=3)
ax.plot(11, 100 * h["accuracy"], "o", ms=15, mfc="none", mec=INK, mew=1.5, zorder=4)
ax.annotate("published:\n200 m, 11 × 11 (2.2 km)", (11, 100 * h["accuracy"]), (8.2, 71.0), fontsize=9.5,
            color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
base = 100 * h["one_class_everywhere"]
ax.axhline(base, color=INK, lw=1)
ax.text(1, base + 0.5, "one class everywhere: %.1f %%" % base, color=MUTED, fontsize=9.5)
ax.set_xticks([1, 3, 5, 7, 9, 11]); ax.set_xticklabels(["raw", "3×3", "5×5", "7×7", "9×9", "11×11"])
ax.set_ylim(57, 77); ax.set_xlim(0.3, 11.9)
ax.set_ylabel("held-out accuracy (%)", color=MUTED)
ax.set_xlabel("majority filter window (cells)", color=MUTED)
tidy(ax, "y")
ax.legend(frameon=False, loc="lower right", fontsize=10)
ax.set_title("B  Held-out accuracy by majority window", loc="left",
             fontsize=11.5, color=INK)
save(fig, "accuracy_200m.png", tight=False)

# ------------------------------------------------------------------ T2
t2 = load("crater_density.json")
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6), gridspec_kw={"width_ratios": [3, 6]}, sharex=True)
for ax, key in zip(axes, ("ath", "ius")):
    A = t2["areas"][key]
    units = sorted(((u, v) for u, v in A["units"].items() if u != "other"),
                   key=lambda kv: kv[1]["robbins_per_1e6km2"]["1.0"])
    for i, (u, v) in enumerate(units):
        r, d = v["robbins_per_1e6km2"]["1.0"], v["detector_per_1e6km2"]["1.0"]
        ax.barh(i + 0.18, r, 0.34, color=BLUE, zorder=3)
        ax.barh(i - 0.18, d, 0.34, color=ORANGE, zorder=3)
        ax.text(r + 80, i + 0.18, "{:,.0f}".format(r), va="center", fontsize=9, color=INK)
        ax.text(d + 80, i - 0.18, "{:,.0f}".format(d), va="center", fontsize=9, color=MUTED)
    ax.set_yticks(range(len(units)))
    ax.set_yticklabels(["%s\n%s km²" % (u, "{:,.0f}".format(v["km2"])) for u, v in units], fontsize=9.5,
                       color=INK)
    for t, (u, _) in zip(ax.get_yticklabels(), units):
        if u == "lAv":
            t.set_weight("bold")
    ax.set_title(A["name"], loc="left", fontsize=11.5, color=INK)
    tidy(ax)
axes[1].set_xlabel("craters ≥ 1 km per 10⁶ km² of the unit", color=MUTED)
axes[0].set_xlabel("craters ≥ 1 km per 10⁶ km² of the unit", color=MUTED)
axes[0].set_xlim(0, 8600)
axes[1].legend(handles=[Patch(color=BLUE, label="Robbins & Hynek (2020) catalogue"),
                        Patch(color=ORANGE, label="closed-depression detector")],
               frameon=False, loc="lower right", fontsize=10)
save(fig, "t2_density.png")

# ------------------------------------------------------------------ the lava-tube relabel
rl = load("lava_relabel_test.json")["variants"]
order = [("A: four hand-drawn classes", "A  four hand-drawn classes",
          "lava tube found on {:.0f} % of its held-out area", "lava_tube_producers"),
         ("B: lava tube -> volcanic (map)", "B  lava tube → 'volcanic' from the geologic map",
          "volcanic: producer's {:.0f} %, user's {:.0f} %", ("volcanic_producers", "volcanic_users")),
         ("C: three classes", "C  three classes, lava tube dropped", "", None),
         ("D: four hand-drawn + volcanic (map) as a fifth", "D  four classes + 'volcanic' as a fifth",
          "volcanic: user's {:.0f} %, below its {:.0f} % share of the test blocks", ("volcanic_users",
                                                                                  "volcanic_area_share_in_test_blocks"))]
fig, ax = plt.subplots(figsize=(12.5, 3.9))
for i, (k, label, note, keys) in enumerate(order):
    v = rl[k]
    y = len(order) - 1 - i
    acc = 100 * v["common_heldout_accuracy"]
    col = BLUE if k.startswith("A") else ORANGE
    ax.barh(y, acc, 0.55, color=col, zorder=3)
    ax.text(acc + 0.6, y, "%.1f %%" % acc, va="center", fontsize=10.5, color=INK, weight="bold")
    if keys:
        vals = [100 * v[x] for x in (keys if isinstance(keys, tuple) else (keys,))]
        ax.text(acc + 7.5, y, note.format(*vals), va="center", fontsize=9.5, color=MUTED, zorder=4,
                bbox=dict(fc="white", ec="none", pad=1.5))
ax.set_yticks(range(len(order))); ax.set_yticklabels([o[1] for o in order][::-1], color=INK)
ax.set_xlim(0, 125)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xlabel("held-out accuracy on the Crater, steep/windy hills and Normal Ground polygons (%%), classifier at "
              "%.1f km" % (load("lava_relabel_test.json")["cell_m"] / 1000.0), color=MUTED)
tidy(ax)
save(fig, "lava_relabel.png")
