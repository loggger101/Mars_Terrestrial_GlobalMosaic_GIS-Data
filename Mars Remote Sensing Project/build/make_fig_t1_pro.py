# -*- coding: utf-8 -*-
r"""Figure for test T1 in Pro (KB §56, §56.1): what each left-out band group is worth, with its interval.

Read from the four logs\t1_bootstrap_*.json (score_t1_bootstrap.py), never retyped -> interim_img\t1_pro.png.
One row per comparison: the held-out accuracy of the all-band map minus the map without that group, in
points, with the paired-bootstrap 95% interval (183 polygons, 1,000 resamples). Resolved (interval clear of
zero): filled, deck blue; not resolved: open, grey. Every row is labelled in ink, so colour is never the
only cue. Light ground, for the interim deck's white slides.
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "interim_img", "t1_pro.png")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
YES, NO, NO_LINE = "#0A7DB0", "#B3BAC0", "#8A949C"     # validated: normal-vision ΔE 25, CVD ΔE 21
ROWS = [   # (log, label)  - "all bands minus the set" = what the left-out bands add
    ("t1_bootstrap_200m_vs_nothermal_200m.json", "thermal bands, 200 m"),
    ("t1_bootstrap_400m_vs_nothermal_400m.json", "thermal bands, 400 m"),
    ("t1_bootstrap_400m_vs_novisible_400m.json", "visible bands (Viking), 400 m"),
    ("t1_bootstrap_400m_vs_terrain_400m.json", "visible + thermal, 400 m"),
]

rows = []
for f, label in ROWS:
    r = json.load(open(os.path.join(HERE, "logs", f)))
    d = -100 * r["diff_acc"]                                   # the json holds B - A
    lo, hi = sorted(-100 * x for x in r["diff_acc_ci95"])
    rows.append((label, d, lo, hi, lo > 0 or hi < 0, r["polygons"], r["boot"]))

plt.rcParams.update({"font.family": "Arial", "font.size": 11})
fig, ax = plt.subplots(figsize=(10, 4.2), dpi=200)
n = len(rows)
for i, (label, d, lo, hi, ok, _, _) in enumerate(rows):
    y = n - 1 - i
    ax.plot([lo, hi], [y, y], color=YES if ok else NO_LINE, lw=2, solid_capstyle="round", zorder=3)
    ax.scatter([d], [y], s=90, zorder=4, color=YES if ok else "white",
               edgecolor=YES if ok else NO_LINE, linewidth=2)
    ax.text(hi + 0.4, y, ("%+.2f pt  [%+.2f, %+.2f]  %s" % (d, lo, hi, "resolved" if ok else "not resolved"))
            .replace("-", "−"), va="center", color=INK, fontsize=10.5)
ax.axvline(0, color=INK, lw=1.0, zorder=2)
ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], color=INK)
ax.set_xlim(-12, 22)
ax.set_xlabel("held-out accuracy the left-out bands add (points; right of 0 = they help)", color=MUTED)
ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(colors=MUTED, length=0)
fig.text(0.01, 0.02, "ArcGIS Pro SVM over ±60°, the same split and settings for every band set.  Dot: all bands "
         "minus the set;\nline: paired-bootstrap 95%% interval, %d held-out polygons, %s resamples."
         % (rows[0][5], format(rows[0][6], ",")), color=MUTED, fontsize=9.5)
fig.tight_layout(rect=(0, 0.1, 1, 1))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
