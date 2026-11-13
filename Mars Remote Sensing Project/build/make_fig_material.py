# -*- coding: utf-8 -*-
r"""Charts of the material-label tests, read from their logs (KB §69.133-§69.142):

  final_img\material_thermal_gain.png   A: the thermal gain (all 7 bands minus without thermal) across held-out blocks,
                                        accuracy points with block-bootstrap 95 % intervals, for every material-label
                                        run: T12's 7 label variants x 2 classifiers (T10 and T11 among them), T16's
                                        dust-cover classes, and T15's runs with map coordinates.
                                        B: T14, night IR and Viking red separating duricrust from dust, AUC within
                                        1, 2 and 5 deg windows (median, 95 %) and pooled over +-60 deg.
  final_img\maps_on_units.png           T13: each lead map class's enrichment in each thermophysical unit (share in the
                                        class over the share overall), U-Net v3 and SVM v3.

Light ground, the palette of make_fig_final.py. System Python:  py -3.13 make_fig_material.py
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final_img")
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D9DEE3"
BLUE, ORANGE, PALE = "#2E7BD6", "#EE6A2F", "#B3BAC0"


def log(name):
    return json.load(open(os.path.join(HERE, "logs", name), encoding="utf-8"))


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=8.5)


def thermal_gain():
    t12, t15, t16, t14 = (log("t12_label_robustness.json"), log("t15_coords_control.json"),
                          log("t16_dust_cover_labels.json"), log("t14_crust_dust_local.json"))
    rows = []
    for v in t12["variants"]:
        e = v["edges"]
        lab = ("inertia %d/%d tiu" % tuple(e)) if v["kind"] == "TI3" else ("units %d tiu, albedo %.2f" % (e[0], e[1]))
        base = (v["kind"] == "TI3" and e == [150, 350]) or (v["kind"] == "UNITS" and e == [150, 0.2])
        for clf in ("ML", "GBT"):
            g = v["runs"]["block " + clf]["thermal_gain"]
            rows.append(("%s, %s%s" % (lab, "max. likelihood" if clf == "ML" else "boosted trees", "  (T10)" if base and
                         v["kind"] == "TI3" and clf == "ML" else "  (T11)" if base and clf == "ML" else ""),
                         g["accuracy"], g["accuracy_ci95"], g["thermal_helps"], "T12"))
    g = t16["splits"]["block"]["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
    rows.append(("dust cover (DCI), max. likelihood  (T16)", g["accuracy"], g["accuracy_ci95"], t16["splits"]["block"]["thermal_helps"], "T16"))
    for v in t15["variants"]:
        lab = "inertia 150/350" if v["kind"] == "TI3" else "units 150, 0.20"
        for clf in ("ML", "GBT"):
            g = v["runs"]["block " + clf]["thermal_gain"]
            rows.append(("%s + coordinates, %s  (T15)" % (lab, "max. likelihood" if clf == "ML" else "boosted trees"),
                         g["accuracy"], g["accuracy_ci95"], g["thermal_helps"], "T15"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 6.4), gridspec_kw={"width_ratios": [1.55, 1]})
    y = np.arange(len(rows))[::-1]
    for yi, (lab, m, ci, helps, src) in zip(y, rows):
        col = ORANGE if helps else (PALE if src == "T15" else BLUE)
        a.plot([100 * ci[0], 100 * ci[1]], [yi, yi], color=col, lw=2)
        a.plot(100 * m, yi, "o", color=col, ms=5)
    a.axvline(0, color=MUTED, lw=0.8)
    a.set_yticks(y); a.set_yticklabels([r[0] for r in rows], fontsize=7.6)
    a.set_xlabel("thermal gain across held-out blocks, accuracy points (95 %)", fontsize=9, color=INK)
    a.set_title("A  What the thermal pair adds on calibrated material labels", loc="left", fontsize=10, color=INK)
    a.plot([], [], color=BLUE, lw=2, label="does not help by the rule")
    a.plot([], [], color=ORANGE, lw=2, label="helps by the rule")
    a.plot([], [], color=PALE, lw=2, label="with map coordinates (T15)")
    a.legend(frameon=False, fontsize=8, loc="lower right")
    a.grid(axis="x", color=GRID, lw=0.6); clean(a)
    W = t14["windows"]
    xs = [1, 2, 5]
    for band, col, off in (("night IR", ORANGE, -0.08), ("Viking red", BLUE, 0.08)):
        med = [W["%g deg" % s]["bands"][band]["median_auc"] for s in xs]
        lo = [W["%g deg" % s]["bands"][band]["median_auc_ci95"][0] for s in xs]
        hi = [W["%g deg" % s]["bands"][band]["median_auc_ci95"][1] for s in xs]
        pos = np.arange(3) + off
        b.errorbar(pos, med, yerr=[np.array(med) - lo, np.array(hi) - med], fmt="o", color=col, ms=5, capsize=3, label=band)
        b.plot(3.3 + off, t14["pooled_auc"][band], "s", color=col, ms=6)
    b.axhline(0.5, color=MUTED, lw=0.8)
    b.set_xticks([0, 1, 2, 3.3]); b.set_xticklabels(["1° windows", "2°", "5°", "pooled\n±60°"], fontsize=8.5)
    b.set_ylabel("AUC, duricrust against dust (0.5 = none)", fontsize=9, color=INK)
    b.set_title("B  The night mosaic's crust-dust contrast is local (T14)", loc="left", fontsize=10, color=INK)
    b.legend(frameon=False, fontsize=8, loc="lower left")
    b.grid(axis="y", color=GRID, lw=0.6); clean(b)
    fig.tight_layout()
    p = os.path.join(OUT, "material_thermal_gain.png")
    fig.savefig(p, dpi=200, facecolor="white"); plt.close(fig)
    print("wrote", p)


def maps_on_units():
    t13 = log("t13_maps_on_units.json")
    units = t13["units"]; classes = t13["classes"]
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6), gridspec_kw={"wspace": 0.75})
    norm = TwoSlopeNorm(vmin=0, vcenter=1, vmax=3)
    for ax, name in zip(axes, ("U-Net v3", "SVM v3")):
        M = t13["maps"][name]
        E = np.array([[M["classes"][c]["enrichment"][u] for u in units] for c in classes])
        im = ax.imshow(E, cmap="RdBu_r", norm=norm, aspect="auto")
        for i in range(E.shape[0]):
            for j in range(E.shape[1]):
                ax.text(j, i, "%.2f" % E[i, j], ha="center", va="center", fontsize=8.5,
                        color="white" if (E[i, j] > 2.2 or E[i, j] < 0.35) else INK)
        ax.set_xticks(range(3)); ax.set_xticklabels(["dust (A)", "duricrust (C)", "sand, rock (B)"], fontsize=8.5)
        ax.set_yticks(range(len(classes)))
        ax.set_yticklabels(["%s  %.1f %%" % (c, 100 * M["classes"][c]["area_share"]) for c in classes], fontsize=8.5)
        ax.set_title("%s   Cramér's V %.3f" % (name, M["cramers_v"]), loc="left", fontsize=10, color=INK)
    cb = fig.colorbar(im, ax=axes, shrink=0.8, pad=0.02)
    cb.set_label("enrichment: share in the class / share overall", fontsize=8.5)
    p = os.path.join(OUT, "maps_on_units.png")
    fig.savefig(p, dpi=200, facecolor="white", bbox_inches="tight"); plt.close(fig)
    print("wrote", p)


if __name__ == "__main__":
    plt.rcParams.update({"font.family": "Arial", "font.size": 10})
    thermal_gain()
    maps_on_units()
