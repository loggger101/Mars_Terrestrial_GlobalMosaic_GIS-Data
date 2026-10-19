# -*- coding: utf-8 -*-
r"""The +/-60 province test: can the day-night pair discriminate material? (KB 28.10)

Two panels, every number parsed from section 28.10 of PROJECT-KNOWLEDGE.md at run time, never retyped:

  A  the diurnal-contrast index over the seven provinces (mean, +/- 1 sd). Dusty (Arabia Terra,
     Amazonis, Tharsis dust) against rocky (Syrtis Major, Acidalia, Hellas floor, Valles Marineris)
     differs by -0.0009 against within-province scatter of 0.13-0.23.
  B  mean DN +/- sd of the four provinces 28.10 tabulates DN for, in THEMIS day IR, THEMIS night IR and
     Viking red, against the whole-mosaic mean +/- sd, with 28.10's dusty-minus-rocky differences
     (-0.19, +0.02, +47.67 DN). Every province reproduces the mosaic-wide mean and spread in both THEMIS
     products (locally contrast-normalised); Viking keeps its albedo differences.

The script checks the record against itself before drawing: the index difference recomputed from the
seven rows must round to the recorded -0.0009 (it does only for three dusty against four rocky), and the
recorded dusty and rocky DN rows must match the means of the two dusty and two rocky provinces of the
per-province table (within 0.07 DN, the rounding of that table). Either check failing stops the script.

Replaces the dark Presentation 1 version, which drew both maps with five boxes of its own and quoted
54.4 DN (logs\global_fig2.log). No raster is read. System Python with matplotlib.
Writes build\pres1_img\global60_thermal.png.
"""
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(os.path.dirname(HERE), "PROJECT-KNOWLEDGE.md")
OUT = os.path.join(HERE, "pres1_img", "global60_thermal.png")
INK, MUTED, GRID, BAND = "#1A1A1A", "#5A6570", "#D9DEE3", "#ECEFF2"
DUST, ROCK = "#eb6834", "#2a78d6"      # the validated pair of make_fig_tes.py
MINUS = "−"


def num(s):
    return float(s.replace("*", "").replace(MINUS, "-").strip())


def section_2810():
    text = open(KB, encoding="utf-8").read()
    i = text.index("### 28.10 ")
    return text[i:text.index("\n### ", i + 10)]


def rows(sec, header):
    """The body rows of the markdown table whose header line starts with `header`."""
    lines = sec.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(header))
    out = []
    for l in lines[i + 2:]:
        if not l.startswith("|"):
            break
        out.append([c.strip() for c in l.strip().strip("|").split("|")])
    return out


def mean_sd(cell):
    m, s = cell.replace("*", "").split("±")
    return num(m), num(s)


def read_record():
    sec = section_2810()
    index = []
    for name, m, sd in rows(sec, "| province | index mean | sd |"):
        label = name.replace("*", "")
        short = label.split(" — ")[0].strip()
        index.append((short, "dusty" if "dust" in label.lower() else "rocky", num(m), num(sd)))
    groups = {r[0].replace("*", ""): [num(c) for c in r[1:]] for r in rows(sec, "| | day IR | night IR |")}
    prov = {}
    for r in rows(sec, "| | day DN | night DN | Viking R |"):
        name = r[0].replace("*", "")
        prov[name] = [None if c in ("—", "-") else mean_sd(c) for c in r[1:]]
    recorded = num(re.search(r"Dusty against rocky: ([%s+\-]?[\d.]+)" % MINUS, sec).group(1))
    return index, groups, prov, recorded


def check(index, groups, prov, recorded):
    dusty = [m for _, k, m, _ in index if k == "dusty"]
    rocky = [m for _, k, m, _ in index if k == "rocky"]
    d = sum(dusty) / len(dusty) - sum(rocky) / len(rocky)
    print("   index: %d dusty, %d rocky, difference %+.6f (recorded %+.4f)" % (len(dusty), len(rocky), d, recorded))
    assert round(d, 4) == recorded, "the index rows do not reproduce the recorded difference"
    names = [n for n in prov if not n.startswith("whole mosaic")]
    kinds = {n: next(k for s, k, _, _ in index if s == n) for n in names}
    for j, band in enumerate(("day IR", "night IR", "Viking red")):
        for kind, row in (("dusty", "dusty provinces"), ("rocky", "rocky provinces")):
            vals = [prov[n][j][0] for n in names if kinds[n] == kind]
            m = sum(vals) / len(vals)
            print("   %-10s %s: mean of %d provinces %.3f, recorded %.2f" % (band, kind, len(vals), m, groups[row][j]))
            assert abs(m - groups[row][j]) <= 0.07, "the DN rows are not the per-province table's provinces"
        diff = groups["dusty provinces"][j] - groups["rocky provinces"][j]
        assert abs(diff - groups["difference"][j]) <= 0.011, "difference row inconsistent"
    return names, kinds


def panel_index(ax, index, recorded):
    n = len(index)
    for i, (name, kind, m, sd) in enumerate(index):
        y = n - 1 - i
        col = DUST if kind == "dusty" else ROCK
        ax.plot([m - sd, m + sd], [y, y], color=col, lw=2.2, solid_capstyle="round", zorder=3)
        ax.plot(m, y, "o" if kind == "dusty" else "s", ms=8, color=col, mec="white", mew=1.8, zorder=4)
        ax.text(0.335, y, ("%+.4f ± %.3f" % (m, sd)).replace("-", MINUS), va="center", color=INK, fontsize=9.5)
    ax.text(0.335, n - 0.35, "mean ± sd", color=MUTED, fontsize=9)
    ax.axvline(0, color=INK, lw=1, zorder=2)
    ax.set_yticks(range(n))
    ax.set_yticklabels(["%s (%s)" % (name, kind) for name, kind, _, _ in index][::-1], color=INK, fontsize=10)
    ax.set_xlim(-0.24, 0.5)
    ax.set_ylim(-0.7, n - 0.1)
    ax.set_xticks([-0.2, -0.1, 0, 0.1, 0.2, 0.3])
    ax.set_xticklabels([("%+.1f" % t).replace("-", MINUS) if t else "0" for t in ax.get_xticks()])
    ax.set_xlabel("diurnal-contrast index (THEMIS day − night; relative)", color=MUTED, fontsize=10)
    sds = [sd for _, _, _, sd in index]
    ax.text(0.0, -0.17, ("Dusty − rocky: %+.4f.  Scatter inside one province: %.2f–%.2f."
                         % (recorded, min(sds), max(sds))).replace("-", MINUS, 1),
            transform=ax.transAxes, color=INK, fontsize=10.5, fontweight="bold", va="top")
    ax.text(0.0, 1.04, "A   The index across seven provinces", transform=ax.transAxes,
            color=INK, fontsize=12, fontweight="bold", va="bottom")


def panel_dn(ax, groups, prov, names, kinds):
    bands = ["THEMIS day IR", "THEMIS night IR", "Viking red"]
    whole = prov[next(n for n in prov if n.startswith("whole mosaic"))]
    offs = [-0.27, -0.09, 0.09, 0.27]
    seen = {"dusty": 0, "rocky": 0}
    handles = []
    for n, dx in zip(names, offs):
        kind = kinds[n]
        col = DUST if kind == "dusty" else ROCK
        filled = seen[kind] == 0
        seen[kind] += 1
        for j in range(3):
            m, sd = prov[n][j]
            ax.plot([j + dx, j + dx], [m - sd, m + sd], color=col, lw=2, solid_capstyle="round", zorder=3)
            ax.plot(j + dx, m, "o" if kind == "dusty" else "s", ms=8, zorder=4,
                    color=col if filled else "white", mec=col, mew=2 if not filled else 1.5)
        h, = ax.plot([], [], "o" if kind == "dusty" else "s", ms=8, color=col if filled else "white",
                     mec=col, mew=2, label="%s (%s)" % (n, kind))
        handles.append(h)
    for j in range(3):
        if whole[j] is not None:
            m, sd = whole[j]
            ax.fill_between([j - 0.42, j + 0.42], m - sd, m + sd, color=BAND, zorder=1, lw=0)
            ax.plot([j - 0.42, j + 0.42], [m, m], color=MUTED, lw=1, ls="--", zorder=2)
        d = groups["difference"][j]
        ax.text(j, 196, ("%+.2f DN" % d).replace("-", MINUS), ha="center", va="bottom", color=INK,
                fontsize=12 if j == 2 else 11, fontweight="bold")
    ax.text(-0.45, 213, "dusty − rocky", color=MUTED, fontsize=9, va="bottom")
    hb = plt.Rectangle((0, 0), 1, 1, color=BAND, label="whole mosaic, mean ± sd")
    ax.legend(handles=handles + [hb], loc="upper center", bbox_to_anchor=(0.43, -0.1), ncol=3,
              frameon=False, fontsize=9, handletextpad=0.3, columnspacing=1.2)
    ax.set_xticks(range(3))
    ax.set_xticklabels(bands, color=INK, fontsize=10)
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(30, 225)
    ax.set_ylabel("mean DN ± sd (8-bit)", color=MUTED, fontsize=10)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.text(0.0, 1.04, "B   The sources, four provinces", transform=ax.transAxes,
            color=INK, fontsize=12, fontweight="bold", va="bottom")


def style(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("1. read PROJECT-KNOWLEDGE.md section 28.10")
    index, groups, prov, recorded = read_record()
    print("2. check the record against itself")
    names, kinds = check(index, groups, prov, recorded)
    print("3. draw")
    plt.rcParams.update({"font.family": "Arial", "font.size": 11})
    fig = plt.figure(figsize=(11.5, 4.9), dpi=200)
    axa = fig.add_axes([0.165, 0.27, 0.33, 0.63])
    axb = fig.add_axes([0.6, 0.27, 0.385, 0.63])
    panel_index(axa, index, recorded)
    panel_dn(axb, groups, prov, names, kinds)
    for ax in (axa, axb):
        style(ax)
    axa.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    fig.text(0.01, 0.015,
             "Both THEMIS mosaics are 8-bit DN stretched region by region: each province repeats the mosaic-wide "
             "mean and spread, so the index is local contrast, not thermal inertia.\nViking is not stretched that "
             "way and keeps the albedo difference. Dusty − rocky in B: the provinces' group means. "
             "Night IR has no whole-mosaic figure in the record.  PROJECT-KNOWLEDGE.md §28.10",
             color=MUTED, fontsize=8.6, va="bottom", linespacing=1.4)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, facecolor="white")
    plt.close(fig)
    print("   wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
