# -*- coding: utf-8 -*-
r"""Figure for test T1: held-out accuracy by band set, from logs\thermal_ablation.json (KB §40).

One bar per band set, sorted; bars that include the terrain bands (slope, relief) in the deck's
cyan, those without in grey; the one-class baseline as a reference line; the thermal gain with
its paired-bootstrap 95% interval as a note. Light ground, to sit on the interim deck's white
slides. Writes build\interim_img\thermal_ablation.png.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "logs", "thermal_ablation.json")))
OUT = os.path.join(HERE, "interim_img", "thermal_ablation.png")

INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
TERRAIN, OTHER = "#0E9ED4", "#AEB6BD"          # deck cyan; neutral grey

sets = sorted(R["sets"].items(), key=lambda kv: kv[1]["accuracy"])
names = [k for k, _ in sets]
acc = [100 * v["accuracy"] for _, v in sets]
kap = [v["kappa"] for _, v in sets]
col = [TERRAIN if ("slope" in v["bands"]) else OTHER for _, v in sets]

plt.rcParams.update({"font.family": "Arial", "font.size": 11})
fig, ax = plt.subplots(figsize=(10, 4.6), dpi=200)
y = range(len(names))
ax.barh(y, acc, height=0.62, color=col, edgecolor="white", linewidth=2, zorder=3)
base = 100 * R["one_class_everywhere"]
ax.axvline(base, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=4)
ax.text(base + 0.6, len(names) - 0.45, "one class everywhere: %.1f%%" % base, color=INK, fontsize=10, va="bottom")
for i, (a, k) in enumerate(zip(acc, kap)):
    ax.text(a + 0.8, i, "%.1f%%   κ %.2f" % (a, k), va="center", color=INK, fontsize=10.5)
ax.set_yticks(list(y)); ax.set_yticklabels(names, color=INK)
ax.set_xlim(0, 100); ax.set_xlabel("held-out accuracy, area-weighted (%)", color=MUTED)
ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(colors=MUTED, length=0)
g = R["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
fig.text(0.01, 0.015,
         "Cyan: band sets that include slope and relief.  Thermal bands add %+.1f pt (95%% CI %+.1f to %+.1f), "
         "κ %+.3f.  Gaussian maximum likelihood, 183 held-out polygons, 400 m."
         % (100 * g["accuracy"], 100 * g["accuracy_ci95"][0], 100 * g["accuracy_ci95"][1], g["kappa"]),
         color=MUTED, fontsize=9.5)
fig.tight_layout(rect=(0, 0.05, 1, 1))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
