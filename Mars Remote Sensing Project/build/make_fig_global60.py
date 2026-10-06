# -*- coding: utf-8 -*-
r"""The +/-60 thermal figure - and why it cannot be read as a material map.

Two earlier versions of this figure were wrong in the same way: they drew the
diurnal-contrast index across +/-60 as though its colours meant dust and
bedrock planet-wide. They do not. Building the index at this extent is what
made it testable against known geology for the first time, and it failed that
test (KB 28.10):

    dusty provinces minus rocky provinces = -0.0009

Zero, and faintly the wrong sign, against within-province scatter of 0.13-0.23.
Syrtis Major and Arabia Terra - one of the strongest thermal-inertia contrasts
on the planet - are indistinguishable in it.

The cause is the source data, not the index. Both THEMIS mosaics are locally
contrast-normalised: every province reproduces the mosaic-wide mean AND spread,
which a region cannot do unless it was stretched to fill the range on its own.
Viking is not normalised that way and separates the same provinces by 47.67 DN.

So this figure shows the comparison instead of the claim. Viking on top as the
control, the index below it on the identical extent, and the measurement that
separates them. A reader can see in one look that the visible mosaic resolves
the provinces and the thermal pair does not.

Run with the ArcGIS interpreter, after make_global_thermal.py and
make_global_terrain.py.
"""
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from scipy import ndimage
from osgeo import gdal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grid60 as G

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "1024")

IDX = os.path.join(G.OUTDIR_NOSPACE, "global60_thermal_contrast.tif")
HILL = os.path.join(G.OUTDIR_NOSPACE, "global60_hillshade.tif")
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pres1_img")
FIG = os.path.join(OUTDIR, "global60_thermal.png")
CACHE = os.path.join(OUTDIR, "_global60_viking_red.npy")

W = 2600
SMOOTH_PX = 4

BG = "#100e0c"
FG = "#ece4d8"
MUTED = "#9a8f80"
FAINT = "#6b6257"
DUST = "#d98032"
ROCK = "#3f8fc4"

CMAP = LinearSegmentedColormap.from_list(
    "diurnal", ["#1b4f72", "#2e86c1", "#9dc9e5", "#efe8dc",
                "#e8a976", "#ca6f1e", "#7e3b0c"])

PROV = [
    ("Arabia Terra", 340.0, 20.0, 10.0, 30.0, "dusty"),
    ("Amazonis", 190.0, 215.0, 20.0, 40.0, "dusty"),
    ("Tharsis dust", 240.0, 260.0, 5.0, 25.0, "dusty"),
    ("Syrtis Major", 65.0, 80.0, 0.0, 15.0, "rocky"),
    ("Acidalia", 330.0, 350.0, 35.0, 55.0, "rocky"),
]
DEG = G.R_MARS * np.pi / 180.0


def read_display(path, target_w, scale=1.0, band=1):
    ds = gdal.Open(path)
    b = ds.GetRasterBand(band)
    nod = b.GetNoDataValue()
    pick, pw = None, ds.RasterXSize
    for i in range(b.GetOverviewCount()):
        o = b.GetOverview(i)
        if o.XSize >= target_w and o.XSize < pw:
            pick, pw = i, o.XSize
    src = b.GetOverview(pick) if pick is not None else b
    h = int(round(target_w * src.YSize / float(src.XSize)))
    a = src.ReadAsArray(buf_xsize=target_w, buf_ysize=h).astype(np.float32)
    ds = None
    if nod is not None:
        a[a == nod] = np.nan
    return a * scale


def read_viking_60(target_w):
    """Viking red over exactly +/-60, rolled to CM 180 to match the others."""
    if os.path.exists(CACHE):
        a = np.load(CACHE)
        if a.shape[1] == target_w:
            print("   viking (cached)")
            return a
    t = time.time()
    ds = gdal.Open(G.SRC_VIKING)
    gt = ds.GetGeoTransform()
    r0 = int(round((gt[3] - G.G100.oy) / -gt[5]))
    r1 = int(round((gt[3] - G.G100.ymin) / -gt[5]))
    h = int(round(target_w * (r1 - r0) / float(ds.RasterXSize)))
    a = ds.GetRasterBand(1).ReadAsArray(0, r0, ds.RasterXSize, r1 - r0,
                                        buf_xsize=target_w, buf_ysize=h)
    ds = None
    a = a.astype(np.float32)
    a[a == 0] = np.nan
    a = np.roll(a, target_w // 2, axis=1)      # CM 0 -> CM 180
    np.save(CACHE, a)
    print("   viking read %.1f s  %s" % (time.time() - t, a.shape))
    return a


def nan_gaussian(a, sigma):
    m = np.isfinite(a)
    num = ndimage.gaussian_filter(np.where(m, a, 0.0), sigma, mode=("nearest", "wrap"))
    den = ndimage.gaussian_filter(m.astype(np.float32), sigma, mode=("nearest", "wrap"))
    return np.where(den > 0.25, num / np.maximum(den, 1e-6), np.nan)


def source_boxmean(path, lon0, lon1, lat0, lat1, ox, oy, res=100.0, step=40):
    """Mean raw DN of a lon/lat box read straight from a CM-180 source mosaic.

    Strided, so it costs a few MB rather than a full decimated pass. Sampling
    the sources with the same boxes as the display arrays is what makes the
    bar panel internally consistent."""
    ds = gdal.Open(path)
    f = lambda L: (((L - 180.0 + 540.0) % 360.0) - 180.0) * DEG
    x0, x1 = f(lon0), f(lon1)
    c0 = int((min(x0, x1) - ox) / res)
    w = int((max(x0, x1) - min(x0, x1)) / res)
    r0 = int((oy - lat1 * DEG) / res)
    h = int(((lat1 - lat0) * DEG) / res)
    c0 = max(0, min(c0, ds.RasterXSize - 1))
    r0 = max(0, min(r0, ds.RasterYSize - 1))
    w = min(w, ds.RasterXSize - c0)
    h = min(h, ds.RasterYSize - r0)
    a = ds.GetRasterBand(1).ReadAsArray(c0, r0, w, h,
                                        buf_xsize=max(1, w // step),
                                        buf_ysize=max(1, h // step)).astype(np.float32)
    ds = None
    a[a == 0] = np.nan
    v = a[np.isfinite(a)]
    return float(v.mean()) if v.size else np.nan


def boxmean(arr, lon0, lon1, lat0, lat1):
    """Mean of a lon/lat box on a CM-180 +/-60 display array."""
    h, w = arr.shape
    f = lambda L: (((L - 180.0 + 540.0) % 360.0) - 180.0)
    x0, x1 = f(lon0), f(lon1)
    c0 = int((min(x0, x1) + 180.0) / 360.0 * w)
    c1 = int((max(x0, x1) + 180.0) / 360.0 * w)
    r0 = int((60.0 - lat1) / 120.0 * h)
    r1 = int((60.0 - lat0) / 120.0 * h)
    sub = arr[max(0, r0):min(h, r1), max(0, c0):min(w, c1)]
    v = sub[np.isfinite(sub)]
    return float(v.mean()) if v.size else np.nan


def panel(ax, img, cmap, vmin, vmax, title, sub):
    ax.set_facecolor(BG)
    # aspect="auto": the axes box is laid out to the 3:1 data ratio already, and
    # "equal" would shrink the map to half the panel width instead of filling it
    ax.imshow(img, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto",
              extent=[0, 360, -60, 60], origin="upper", interpolation="bilinear")
    ax.set_xlim(0, 360)
    ax.set_ylim(-60, 60)
    ax.set_xticks(range(0, 361, 30))
    ax.set_yticks([-60, -30, 0, 30, 60])
    ax.tick_params(colors=MUTED, labelsize=7.5)
    for s in ax.spines.values():
        s.set_color("#39332b")
    for nm, a, b, c, d, kind in PROV:
        col = DUST if kind == "dusty" else ROCK
        # a box that crosses 0/360 is drawn as its two visible halves
        spans = [(a, b)] if b > a else [(a, 360.0), (0.0, b)]
        for s0, s1 in spans:
            ax.add_patch(plt.Rectangle((s0, c), s1 - s0, d - c, fill=False,
                                       edgecolor=col, linewidth=1.1, alpha=0.95))
        lon = (a + b) / 2.0 if b > a else ((a + b + 360.0) / 2.0) % 360.0
        ax.text(min(max(lon, 14.0), 346.0), (c + d) / 2.0, nm, color="#fff6e8",
                fontsize=7.2, ha="center", va="center",
                path_effects=[pe.withStroke(linewidth=2.2, foreground="#0e0c0a", alpha=0.9)])
    ax.text(0.0, 1.075, title, transform=ax.transAxes, color=FG,
            fontsize=11.5, fontweight="bold", va="bottom")
    ax.text(0.0, 1.020, sub, transform=ax.transAxes, color=MUTED,
            fontsize=8.2, va="bottom")


def main():
    for p in (IDX, HILL):
        if not os.path.exists(p):
            print("!! %s not built yet" % p)
            return 1
    os.makedirs(OUTDIR, exist_ok=True)
    t0 = time.time()

    print("1. read at display size")
    idx = read_display(IDX, W, scale=1.0 / 10000.0)
    vik = read_viking_60(W)
    h = min(idx.shape[0], vik.shape[0])
    idx, vik = idx[:h], vik[:h]
    sm = nan_gaussian(idx, SMOOTH_PX)
    vs = nan_gaussian(vik, SMOOTH_PX)
    print("   index %s  viking %s" % (idx.shape, vik.shape))

    print("2. the measurement - all four products, the SAME five boxes")
    rows = []
    for nm, a, b, c, d, kind in PROV:
        rows.append((nm, kind,
                     boxmean(vik, a, b, c, d),
                     source_boxmean(G.SRC_DAY, a, b, c, d, -10669500.0, 5334800.0),
                     source_boxmean(G.SRC_NIGHT, a, b, c, d, -10669400.0, 3556500.0),
                     boxmean(idx, a, b, c, d)))
        print("   %-14s %-6s  viking %6.1f   day %6.2f   night %6.2f   index %+.4f"
              % rows[-1])

    def sep(i):
        return (np.mean([r[i] for r in rows if r[1] == "dusty"]),
                np.mean([r[i] for r in rows if r[1] == "rocky"]))
    vik_d, vik_r = sep(2)
    day_d, day_r = sep(3)
    ngt_d, ngt_r = sep(4)
    idx_d, idx_r = sep(5)
    print("   SEPARATION  viking %+.2f DN   day %+.2f DN   night %+.2f DN   index %+.4f"
          % (vik_d - vik_r, day_d - day_r, ngt_d - ngt_r, idx_d - idx_r))

    print("3. draw")
    # laid out to the data's own 3:1 aspect so the maps fill their panels
    # Explicit vertical layout. The maps are 360 x 120 degrees = 3:1, so their
    # panel height follows from the width; everything else is placed from the
    # top down rather than by subtracting guesses from 1.0.
    FW, FH = 13.4, 15.4
    LEFT, PW = 0.055, 0.885
    PH = PW * FW / 3.0 / FH        # matching height for a 3:1 map
    A_TOP = 0.885                  # below the title block
    A_Y = A_TOP - PH
    B_Y = A_Y - 0.080 - PH         # gap leaves room for panel B's own titles
    ROW_H = 0.150
    BOT = B_Y - 0.095 - ROW_H
    fig = plt.figure(figsize=(FW, FH), facecolor=BG)

    fig.text(LEFT, 0.962, "Can the day–night pair discriminate material at ±60°?",
             color=FG, fontsize=19, fontweight="bold")
    fig.text(LEFT, 0.939,
             "The same five provinces, the same extent, two products. "
             "Orange boxes are dust-mantled, blue are rock-dominated.",
             color=MUTED, fontsize=10.0)

    axa = fig.add_axes([LEFT, A_Y, PW, PH])
    v = vs[np.isfinite(vs)]
    panel(axa, vs, "pink", *np.percentile(v, [1, 99]),
          title="Viking MDIM 2.1, red band — visible albedo",
          sub="the control: a product that is NOT contrast-normalised")

    axb = fig.add_axes([LEFT, B_Y, PW, PH])
    sv = sm[np.isfinite(sm)]
    lo, hi = np.percentile(sv, [2, 98])
    mid = float(np.median(sv))
    m = max(hi - mid, mid - lo)
    panel(axb, sm, CMAP, mid - m, mid + m,
          title="Diurnal thermal contrast — THEMIS day − night",
          sub="100 m, 213,388 × 71,130, 14.78 bn valid px · colour smoothed ~%.0f km"
              % (SMOOTH_PX * 21338800.0 / W / 1000.0))

    # ---- the bar panel --------------------------------------------------
    axc = fig.add_axes([LEFT, BOT, 0.375, ROW_H])
    axc.set_facecolor(BG)
    labels = ["Viking\nred DN", "THEMIS\nday DN", "THEMIS\nnight DN"]
    dusty = [vik_d, day_d, ngt_d]
    rocky = [vik_r, day_r, ngt_r]
    x = np.arange(3)
    axc.bar(x - 0.19, dusty, 0.36, color=DUST, label="dusty provinces")
    axc.bar(x + 0.19, rocky, 0.36, color=ROCK, label="rocky provinces")
    for i, (a, b) in enumerate(zip(dusty, rocky)):
        axc.text(i, max(a, b) + max(dusty) * 0.06, "%+.2f" % (a - b), ha="center",
                 color=FG if i == 0 else "#d8695a", fontsize=9.5, fontweight="bold")
    axc.set_xticks(x)
    axc.set_xticklabels(labels, color=MUTED, fontsize=8)
    axc.set_ylim(0, max(max(dusty), max(rocky)) * 1.42)
    axc.set_ylabel("mean DN", color=MUTED, fontsize=8.5)
    axc.tick_params(colors=MUTED, labelsize=7.5)
    for s in axc.spines.values():
        s.set_color("#39332b")
    axc.legend(frameon=False, fontsize=8, labelcolor=MUTED, loc="upper right")
    axc.text(0, 1.10, "Separation of dusty from rocky terrain",
             transform=axc.transAxes, color=FG, fontsize=10.5, fontweight="bold")

    # ---- the conclusion -------------------------------------------------
    axd = fig.add_axes([LEFT + 0.445, BOT, 0.495, ROW_H])
    axd.axis("off")
    axd.text(0, 1.14, "What this means", transform=axd.transAxes,
             color=FG, fontsize=10.5, fontweight="bold")
    axd.text(
        0, 0.97,
        "Viking separates the provinces by %.1f DN, from the identical boxes — so the\n"
        "sampling is right and the geography is real. Both THEMIS mosaics separate them\n"
        "by under 0.3 DN, and every province reproduces the mosaic-wide mean AND spread\n"
        "(day 125.5–126.0 ± 29–34, against 125.75 ± 34.36 overall).\n\n"
        "A region cannot do that unless it was stretched to fill the range on its own.\n"
        "Both THEMIS mosaics are locally contrast-normalised: their DN is local contrast,\n"
        "not radiance, so the regional signal was gone before any differencing.\n\n"
        "The index is therefore a LOCAL contrast field. It is a measured material\n"
        "discriminator inside the type area and must not be mapped planet-wide.\n"
        "For ±60° material work, lead with visible albedo."
        % (vik_d - vik_r),
        transform=axd.transAxes, color=MUTED, fontsize=8.5, va="top", linespacing=1.55)

    fig.text(LEFT + PW, 0.015,
             "A relative index, not thermal inertia — both THEMIS products are 8-bit DN "
             "with no radiometric scaling.   PROJECT-KNOWLEDGE.md §28.10",
             color=FAINT, fontsize=7.6, ha="right")

    fig.savefig(FIG, dpi=150, facecolor=BG)
    plt.close(fig)
    print("   %s  %.1f MB" % (FIG, os.path.getsize(FIG) / 1048576))
    print("done in %.1f min" % ((time.time() - t0) / 60))
    return 0


if __name__ == "__main__":
    sys.exit(main())
