# -*- coding: utf-8 -*-
"""Dark-ground versions of the Presentation 1 figures.

The deck is now navy throughout, and a matplotlib sheet saved on white reads as
a lit rectangle floating in it. These are the same figures -- same extents, same
landmarks, same labels, same numbers -- re-rendered so the paper goes away and
only the data is left on the slide.

Nothing here touches the source TIFFs: the three globals come from the cached
decimations, so this runs under the stock interpreter with no GDAL.

    python make_figs_dark.py [out_dir]
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402
import matplotlib.patheffects as pe                               # noqa: E402
import numpy as np                                                # noqa: E402
from matplotlib.colors import LinearSegmentedColormap             # noqa: E402
from matplotlib.patches import Rectangle                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "pres1_img")
os.makedirs(OUT, exist_ok=True)

GROUND = "#0E2841"           # the slide ground; every figure sits on it
CYAN = "#0E9ED4"
PALE = "#9ED8ED"
LINE = "#3E5C76"             # spines and ticks, dark enough to stay quiet
TEXT = "#D6E4EE"
HALO = [pe.withStroke(linewidth=2.8, foreground="#071726", alpha=0.95)]

LANDMARKS = ((226.2, 18.65, "Olympus Mons", 8, -13, "left"),
             (247.0, -1.0, "Tharsis Montes", -9, 5, "right"),
             (305.0, -10.0, "Valles Marineris", 8, -14, "left"),
             (70.5, -42.4, "Hellas Planitia", 8, -13, "left"),
             (290.0, 22.0, "Chryse Planitia", 8, 6, "left"),
             (67.0, 8.0, "Syrtis Major", -9, 6, "right"))

MOLA = LinearSegmentedColormap.from_list("mola", [
    (0.000, "#2B1A6B"), (0.097, "#1C46B4"), (0.194, "#268CD8"),
    (0.258, "#3FB8C4"), (0.290, "#3E9B4E"), (0.355, "#8FBE3E"),
    (0.452, "#E2CC55"), (0.548, "#D98B36"), (0.677, "#B54530"),
    (0.806, "#9C5560"), (1.000, "#F5EFF2")])


def stretch(a, lo=1, hi=99, mask=None):
    """Percentile stretch to 0-255, ignoring fill."""
    vals = a[mask] if mask is not None else a
    p0, p1 = np.percentile(vals, [lo, hi])
    out = np.clip((a.astype(np.float32) - p0) / max(p1 - p0, 1e-6), 0, 1)
    return out


def frame(ax, ticks=True):
    for lon in range(-180, 181, 30):
        ax.axvline(lon, color="white", lw=0.4, alpha=0.22)
    for lat in range(-30, 31, 30):
        ax.axhline(lat, color="white", lw=0.4, alpha=0.22)
    for lon, lat, name, dx, dy, ha in LANDMARKS:
        lon = lon - 360 if lon > 180 else lon
        ax.plot([lon], [lat], marker="+", ms=8, color="white", mew=1.5,
                path_effects=HALO)
        ax.annotate(name, xy=(lon, lat), xytext=(dx, dy),
                    textcoords="offset points", color="white", ha=ha,
                    fontsize=14, path_effects=HALO)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 60)
    ax.set_xticks(range(-180, 181, 60))
    ax.set_yticks(range(-60, 61, 30))
    ax.set_xticklabels(["%d°E" % ((v + 360) % 360)
                        for v in range(-180, 181, 60)], fontsize=14)
    ax.set_yticklabels(["%d°" % v for v in range(-60, 61, 30)],
                       fontsize=14)
    ax.tick_params(colors=TEXT, length=3)
    for s in ax.spines.values():
        s.set_edgecolor(LINE)
        s.set_linewidth(0.9)


def save(fig, name, pad=0.1):
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor=GROUND, bbox_inches="tight", pad_inches=pad)
    plt.close(fig)
    print("   wrote %s" % name)


def sheet(name, draw, figsize=(13.0, 4.8)):
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    fig.patch.set_facecolor(GROUND)
    ax.set_facecolor(GROUND)
    draw(fig, ax)
    fig.tight_layout(pad=0.4)
    save(fig, name)


# ============================================================ the globals ====

print("global sheets ...")
vik = np.load(os.path.join(HERE, "viking_global_3000.npy"))
sheet("g_viking_dark.png", lambda f, ax: (
    ax.imshow(vik, extent=[-180, 180, -90, 90], interpolation="bilinear"),
    frame(ax)))

the = np.load(os.path.join(HERE, "themis_global_3000.npy"))
the8 = stretch(the, 1, 99, mask=the > 0)
sheet("g_themis_dark.png", lambda f, ax: (
    ax.imshow(the8, extent=[-180, 180, -90, 90], cmap="gray", vmin=0, vmax=1,
              interpolation="bilinear"),
    frame(ax)))

dem = np.load(os.path.join(HERE, "dem_global_3000_f32.npy"))


def draw_dem(fig, ax):
    im = ax.imshow(dem / 1000.0, extent=[-180, 180, -90, 90], cmap=MOLA,
                   vmin=-9, vmax=22, interpolation="bilinear")
    frame(ax)
    cb = fig.colorbar(im, ax=ax, fraction=0.028, pad=0.035)
    cb.set_label("elevation above datum (km)", color=TEXT, fontsize=13)
    cb.ax.tick_params(colors=TEXT, labelsize=12)
    cb.outline.set_edgecolor(LINE)


sheet("g_dem_dark.png", draw_dem)

# ============================================================== the extent ===

print("mapping extent ...")
CUT = 60.0
fig, ax = plt.subplots(figsize=(13.0, 6.6), dpi=170)
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)
ax.imshow(vik, extent=[-180, 180, -90, 90], interpolation="bilinear")

# The excluded band is dimmed rather than bleached -- on a dark ground a white
# veil is the brightest thing on the slide, which is the wrong emphasis.
for y0, y1 in ((CUT, 90.0), (-90.0, -CUT)):
    ax.add_patch(Rectangle((-180, y0), 360, y1 - y0, facecolor="#071726",
                           alpha=0.80, zorder=3, edgecolor="none"))
for y in (CUT, -CUT):
    ax.axhline(y, color=CYAN, lw=2.2, zorder=4)
for lon in range(-180, 181, 30):
    ax.axvline(lon, color="white", lw=0.4, alpha=0.25, zorder=2)
for lat in (-30, 0, 30):
    ax.axhline(lat, color="white", lw=0.4, alpha=0.25, zorder=2)

ax.annotate("mapped  —  60°N to 60°S, all 360° of longitude"
            "  ·  86.6% of the surface",
            xy=(-176, 52), color="white", fontsize=15.5, va="top",
            path_effects=HALO, zorder=6)
for y in (76, -76):
    ax.annotate("not mapped — plate-carrée east-west scale error "
                "passes 2× beyond 60°",
                xy=(0, y), color=PALE, fontsize=13, ha="center", va="center",
                zorder=6)

ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_xticks(range(-180, 181, 60))
ax.set_yticks([-90, -60, -30, 0, 30, 60, 90])
ax.set_xticklabels(["%d°E" % ((v + 360) % 360)
                    for v in range(-180, 181, 60)], fontsize=14)
ax.set_yticklabels(["%d°" % v for v in (-90, -60, -30, 0, 30, 60, 90)],
                   fontsize=14)
ax.tick_params(colors=TEXT, length=3)
for s in ax.spines.values():
    s.set_edgecolor(LINE)
    s.set_linewidth(0.9)
fig.tight_layout(pad=0.4)
save(fig, "g_extent_dark.png")

# ============================================================ the spectrum ===
# Reproduces the version that is in his deck: no THEMIS Night IR row and no
# held/planned legend. make_spectrum.py draws a later variant with both, which
# would be new content on the slide rather than a restyle of it.

print("spectrum ...")
fig, ax = plt.subplots(figsize=(11.6, 4.3), dpi=190)
fig.patch.set_facecolor(GROUND)
ax.set_facecolor(GROUND)

ax.set_xscale("log")
ax.set_xlim(0.33, 26.0)
ax.set_ylim(0.4, 10.4)

for x0, x1, c in [(0.40, 0.45, "#7B3FD6"), (0.45, 0.49, "#3E63E8"),
                  (0.49, 0.56, "#2FBE74"), (0.56, 0.59, "#EADB45"),
                  (0.59, 0.63, "#F0913A"), (0.63, 0.70, "#E04B42")]:
    ax.add_patch(Rectangle((x0, 7.4), x1 - x0, 1.4, fc=c, ec="none", alpha=0.95))
ax.text(0.53, 9.0, "visible", ha="center", fontsize=9.5, color=TEXT)

ax.add_patch(Rectangle((6.8, 7.4), 14.9 - 6.8, 1.4, fc="#5C8FB8", ec="none",
                       alpha=0.95))
ax.text(10.1, 9.0, "thermal infrared", ha="center", fontsize=9.5, color=TEXT)

ax.add_patch(Rectangle((14.2, 6.9), 1.6, 2.3, fc="#E04B42", ec="none",
                       alpha=0.22))
ax.text(15.0, 6.55, "CO$_2$ 15 µm", ha="center", va="top", fontsize=7.5,
        color="#F0A09A")

for y, x0, x1, label in [
    (4.7, 0.40, 0.70, "Viking MDIM 2.1 colour — 3 bands, 232 m"),
    (3.0, 0.57, 0.61,
     "Viking band 1 (red, ≈ 0.59 µm) — dust vs basalt"),
    (1.3, 6.80, 14.90, "THEMIS Day IR v12 — 100 m, held"),
]:
    ax.plot([x0, x1], [y, y], lw=7, color=CYAN, solid_capstyle="butt",
            alpha=0.95)
    ax.text(x0, y + 0.42, label, ha="left", va="bottom", fontsize=9, color=TEXT)

ax.plot([1.064], [6.15], marker="v", ms=9, color=PALE)
ax.text(1.064, 6.58, "MOLA laser altimetry — 1064 nm, active",
        ha="center", va="bottom", fontsize=9, color=TEXT)

ax.set_yticks([])
ax.set_xticks([0.4, 0.5, 0.7, 1.0, 2.0, 5.0, 10.0, 20.0])
ax.set_xticklabels(["0.4", "0.5", "0.7", "1", "2", "5", "10", "20"], fontsize=9)
ax.set_xlabel("wavelength (µm, log scale)", fontsize=9.5, color=TEXT)
ax.tick_params(axis="x", colors=TEXT, length=4)
for side in ("top", "left", "right"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(LINE)
ax.grid(axis="x", color=PALE, alpha=0.12, lw=0.6)

fig.tight_layout(pad=0.5)
save(fig, "em_spectrum_dark.png", pad=0.06)

print("done")
