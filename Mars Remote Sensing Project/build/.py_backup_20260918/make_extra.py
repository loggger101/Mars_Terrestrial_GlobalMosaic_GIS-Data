# -*- coding: utf-8 -*-
"""Four diagnostic figures that turn stated problems into shown ones.

  f_meridian.png   the central-meridian mismatch, read off the actual rasters
  f_zfactor.png    what WARNING 000869 does to a slope layer
  f_hypsometry.png global elevation distribution and the 8-bit DN ranges
  f_daedalia.png   visible vs thermal over a dust-mantled flow field (H1)

Everything here is read from the three global TIFFs on Z: -- nothing is quoted
from product documentation and nothing is screenshotted.
"""
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402
import numpy as np                                                # noqa: E402

import marsfig as M                                               # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "le_img")
os.makedirs(OUT, exist_ok=True)

NAVY, CYAN, RED = "#0E2841", "#0E9ED4", "#B4342B"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": NAVY,
                     "axes.labelcolor": NAVY, "xtick.color": NAVY,
                     "ytick.color": NAVY, "axes.titlecolor": NAVY})


def save(fig, name, tight=True):
    if tight:
        fig.tight_layout(pad=0.5)
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor="white", dpi=170, bbox_inches="tight",
                pad_inches=0.12)
    plt.close(fig)
    print("   wrote %s" % name)


def panel(ax, title, sub=None, colour=NAVY):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor(colour)
        s.set_linewidth(1.6)
    ax.set_title(title, fontsize=12.5, color=colour, pad=6, fontweight="bold")
    if sub:
        ax.set_xlabel(sub, fontsize=10, color=colour, labelpad=5)


# ------------------------------------------------------- 1. the meridian ----
t0 = time.time()
print("central-meridian mismatch ...")
W = M.WINDOW
vik, _ = M.read_window(M.VIKING, W, max_px=1400)
the_ok, _ = M.read_window(M.THEMIS, W, max_px=1400)
naive = dict(W)
naive["lon0"] += 180.0                    # what a CM-0 assumption actually grabs
naive["lon1"] += 180.0
the_bad, _ = M.read_window(M.THEMIS, naive, max_px=1400)

fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.9))
axes[0].imshow(M.stretch_rgb(vik))
panel(axes[0], "Viking MDIM 2.1 — the reference",
      "271–286°E, 6–13°S  ·  CM 0°, metres")
axes[1].imshow(M.stretch(the_bad, 2, 98), cmap="gray")
panel(axes[1], "THEMIS read as if CM 0°",
      "same numbers, ground at 91–106°E — half a planet away", RED)
axes[2].imshow(M.stretch(the_ok, 2, 98), cmap="gray")
panel(axes[2], "THEMIS read on CM 180°",
      "same ground as Viking — registers pixel for pixel", CYAN)
save(fig, "f_meridian.png")

# --------------------------------------------------------- 2. z-factor ------
print("z-factor / WARNING 000869 ...")
dem, ext = M.read_window(M.DEM, W, max_px=1400)
dem = dem.astype(np.float32)
cell_deg = (ext[1] - ext[0]) / dem.shape[1]
mid_lat = 0.5 * (ext[2] + ext[3])
m_per_deg = M.R * np.pi / 180.0
cell_m = cell_deg * m_per_deg


def slope_deg(z, dx, dy):
    gy, gx = np.gradient(z, dy, dx)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


bad = slope_deg(dem, cell_deg, cell_deg)          # degrees treated as linear
good = slope_deg(dem, cell_m * np.cos(np.radians(mid_lat)), cell_m)
print("   default z-factor 1 on a degree grid: %.2f–%.2f°, mean %.2f°"
      % (bad.min(), bad.max(), bad.mean()))
print("   metric grid:                         %.2f–%.2f°, mean %.2f°"
      % (good.min(), good.max(), good.mean()))

fig = plt.figure(figsize=(13.2, 4.4), layout="constrained")
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.86])
ax0, ax1, ax2 = (fig.add_subplot(gs[0]), fig.add_subplot(gs[1]),
                 fig.add_subplot(gs[2]))
ax0.imshow(bad, cmap="magma", vmin=0, vmax=90, aspect="auto")
panel(ax0, "Slope, z-factor 1 on a degree grid",
      "%.1f–%.1f°, mean %.1f° — saturated"
      % (bad.min(), bad.max(), bad.mean()), RED)
im = ax1.imshow(good, cmap="magma", vmin=0, vmax=90, aspect="auto")
panel(ax1, "Slope, horizontal units in metres",
      "%.1f–%.1f°, mean %.1f° — usable"
      % (good.min(), good.max(), good.mean()), CYAN)
cb = fig.colorbar(im, ax=[ax0, ax1], orientation="horizontal",
                  fraction=0.055, pad=0.14, aspect=55)
cb.set_label("slope (°)", fontsize=9)
cb.ax.tick_params(labelsize=8)
ax2.hist(good.ravel(), bins=90, range=(0, 90), color=CYAN, label="metres")
ax2.hist(bad.ravel(), bins=90, range=(0, 90), color=RED,
         label="degrees, z-factor 1")
ax2.set_yscale("log")
ax2.set_xlabel("slope (°)")
ax2.set_ylabel("pixels")
ax2.legend(frameon=False, fontsize=9, loc="upper center")
ax2.set_title("The layer is not wrong by a scale factor — it is saturated",
              fontsize=11, color=NAVY, pad=6, fontweight="bold")
save(fig, "f_zfactor.png", tight=False)

# ------------------------------------------------------- 3. hypsometry ------
print("global hypsometry and DN ranges ...")
cache = os.path.join(HERE, "dem_global_3000_f32.npy")
fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.4))
if os.path.exists(cache):
    g = np.load(cache)
    # the mapped band only: 60 N - 60 S out of a +/-90 array, so the histogram
    # describes the ground the project actually covers
    r0 = int(round(g.shape[0] * (90 - 60) / 180.0))
    g = g[r0:g.shape[0] - r0]
    g = g[np.isfinite(g)] / 1000.0
    axes[0].hist(g, bins=240, color=CYAN)
    axes[0].set_yscale("log")
    axes[0].set_xlabel("elevation (km)")
    axes[0].set_ylabel("pixels")
    axes[0].set_title("Relief across the mapped band, 60°N–60°S",
                      fontsize=12.5, pad=6, fontweight="bold")
    for v, lab, ha in ((g.min(), "Hellas floor", "left"),
                       (g.max(), "Olympus Mons", "right")):
        axes[0].axvline(v, color=RED, lw=1.0, ls="--")
        axes[0].annotate(lab, xy=(v, 0.97), xycoords=("data", "axes fraction"),
                         xytext=(5 if ha == "left" else -5, 0),
                         textcoords="offset points", fontsize=9, color=RED,
                         ha=ha, va="top")
    axes[0].annotate("two peaks = the crustal dichotomy",
                     xy=(0.62, 0.78), xycoords="axes fraction", fontsize=9,
                     color=NAVY, ha="center")
    axes[1].plot(np.linspace(0, 100, 400),
                 np.percentile(g, np.linspace(0, 100, 400))[::-1], color=NAVY,
                 lw=1.8)
    axes[1].set_xlabel("percent of surface above")
    axes[1].set_ylabel("elevation (km)")
    axes[1].set_title("Hypsometric curve", fontsize=12.5, pad=6,
                      fontweight="bold")
    axes[1].grid(alpha=0.25)
else:
    axes[0].set_title("run make_globals.py first")

the_dn, _ = M.read_window(M.THEMIS, W, max_px=1400)
vik_dn, _ = M.read_window(M.VIKING, W, max_px=1400)
axes[2].hist(the_dn[the_dn > 0].ravel(), bins=128, range=(0, 255), color="#555F66",
             alpha=0.85, label="THEMIS day IR")
axes[2].hist(vik_dn[..., 0].ravel(), bins=128, range=(0, 255), color="#B4342B",
             alpha=0.7, label="Viking red")
axes[2].set_xlabel("8-bit DN")
axes[2].set_ylabel("pixels")
axes[2].legend(frameon=False, fontsize=9)
axes[2].set_title("What 8 bits actually delivers", fontsize=12.5, pad=6,
                  fontweight="bold")
axes[2].annotate("Viking clips at DN 207", xy=(207, 0.36),
                 xycoords=("data", "axes fraction"), xytext=(-14, 46),
                 textcoords="offset points", fontsize=9, color="#B4342B",
                 ha="right", va="center",
                 arrowprops=dict(arrowstyle="-", color="#B4342B", lw=0.9))
save(fig, "f_hypsometry.png")

# --------------------------------------------------------- 4. Daedalia ------
print("Daedalia Planum — visible against thermal ...")
DP = dict(lon0=-128.0, lon1=-112.0, lat0=-30.0, lat1=-19.0)
dp_v, _ = M.read_window(M.VIKING, DP, max_px=1600)
dp_t, _ = M.read_window(M.THEMIS, DP, max_px=1600)
fig, axes = plt.subplots(1, 2, figsize=(13.2, 4.8))
axes[0].imshow(M.stretch_rgb(dp_v))
panel(axes[0], "Viking MDIM 2.1 — visible colour",
      "albedo dominated by the dust veneer")
axes[1].imshow(M.stretch(dp_t, 2, 98), cmap="gray")
panel(axes[1], "THEMIS Day IR — thermal",
      "flow lobes and margins the visible mosaic flattens", CYAN)
save(fig, "f_daedalia.png")

print("done in %.1f s" % (time.time() - t0))
