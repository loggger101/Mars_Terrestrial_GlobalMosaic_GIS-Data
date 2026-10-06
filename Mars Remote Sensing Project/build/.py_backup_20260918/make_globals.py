# -*- coding: utf-8 -*-
"""Global sheets for the three source rasters -- one slide each.

Presentation 1 carried three slides titled after the three global rasters with
nothing on them. These are the figures those slides were reaching for: the mapped
surface, read out of the project's own TIFFs, with a graticule and -- for the DEM
-- a real elevation scale.

The sheets are cropped to 60 N - 60 S. That is the mapping extent, not a framing
choice: this is plate carree, where the east-west scale error is 1/cos(lat), so it
is 2x at 60 degrees and 5.8x at 80. The band still holds 86.6% of the surface.

THEMIS ships on central meridian 180 while Viking and the DEM ship on 0, so the
THEMIS array is rolled by half its width before plotting. Without that the three
sheets would not line up and every feature would sit half a planet from where the
other two put it -- the same mismatch that is the subject of make_meridian.py.
"""
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402
import matplotlib.patheffects as pe                               # noqa: E402
import numpy as np                                                # noqa: E402
from matplotlib.colors import LinearSegmentedColormap             # noqa: E402
from osgeo import gdal                                            # noqa: E402

import marsfig as M                                               # noqa: E402

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "1024")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "le_img")
os.makedirs(OUT, exist_ok=True)

NAVY, CYAN = "#0E2841", "#0E9ED4"
HALO = [pe.withStroke(linewidth=2.6, foreground="#0B1A2B", alpha=0.92)]
DARK_HALO = [pe.withStroke(linewidth=2.6, foreground="white", alpha=0.9)]

#         lon     lat    name               dx   dy   ha
LANDMARKS = ((226.2, 18.65, "Olympus Mons", 8, -13, "left"),
             (247.0, -1.0, "Tharsis Montes", -9, 5, "right"),
             (305.0, -10.0, "Valles Marineris", 8, -14, "left"),
             (70.5, -42.4, "Hellas Planitia", 8, -13, "left"),
             (290.0, 22.0, "Chryse Planitia", 8, 6, "left"),
             (67.0, 8.0, "Syrtis Major", -9, 6, "right"))

# MOLA's own hypsometric ramp, rebuilt: deep blue at the Hellas floor through
# green at datum to white on the Tharsis summits.
MOLA = LinearSegmentedColormap.from_list("mola", [
    (0.000, "#2B1A6B"), (0.097, "#1C46B4"), (0.194, "#268CD8"),
    (0.258, "#3FB8C4"), (0.290, "#3E9B4E"), (0.355, "#8FBE3E"),
    (0.452, "#E2CC55"), (0.548, "#D98B36"), (0.677, "#B54530"),
    (0.806, "#9C5560"), (1.000, "#F5EFF2")])


def decimate(path, width, cache=None, roll=False):
    """Whole-raster read decimated to `width` px. Cached -- these are slow.

    Averaged, not subsampled. GDAL's default decimation is nearest neighbour,
    which at 1:71 turns a 22-billion-pixel mosaic into aliased speckle with no
    large-scale tone left in it -- the planet-wide albedo pattern disappears.
    """
    if cache and os.path.exists(cache):
        print("   reusing %s" % os.path.basename(cache))
        return np.load(cache)
    ds = gdal.Open(path, gdal.GA_ReadOnly)
    h = int(width * ds.RasterYSize / ds.RasterXSize)
    print("   %d x %d -> %d x %d (stripped, no pyramids: full-file read)"
          % (ds.RasterXSize, ds.RasterYSize, width, h))
    t = time.time()
    arr = ds.ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize,
                         buf_xsize=width, buf_ysize=h,
                         resample_alg=gdal.GRIORA_Average)
    ds = None
    print("   read in %.1f s" % (time.time() - t))
    if arr.ndim == 3:
        arr = np.transpose(arr, (1, 2, 0))
    if roll:                                # CM 180 -> CM 0
        arr = np.roll(arr, arr.shape[1] // 2, axis=1)
    if cache:
        np.save(cache, arr)
    return arr


def frame(ax, label_colour="white"):
    """Graticule and landmarks -- identical on all three sheets.

    No window box: the mapped area is the whole sheet. The close-up windows
    elsewhere in the deck are illustrations of what the data resolves, not the
    extent being worked on, and drawing one here said the opposite.
    """
    for lon in range(-180, 181, 30):
        ax.axvline(lon, color=label_colour, lw=0.4, alpha=0.25)
    for lat in range(-30, 31, 30):
        ax.axhline(lat, color=label_colour, lw=0.4, alpha=0.25)
    halo = HALO if label_colour == "white" else DARK_HALO
    for lon, lat, name, dx, dy, ha in LANDMARKS:
        lon = lon - 360 if lon > 180 else lon
        ax.plot([lon], [lat], marker="+", ms=8, color=label_colour, mew=1.5,
                path_effects=halo)
        ax.annotate(name, xy=(lon, lat), xytext=(dx, dy),
                    textcoords="offset points", color=label_colour, ha=ha,
                    fontsize=14, path_effects=halo)
    # 60 N to 60 S: the mapping extent, and the crop the sheets are drawn at
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 60)
    ax.set_xticks(range(-180, 181, 60))
    ax.set_yticks(range(-60, 61, 30))
    ax.set_xticklabels(["%d°E" % ((v + 360) % 360)
                        for v in range(-180, 181, 60)], fontsize=14)
    ax.set_yticklabels(["%d°" % v for v in range(-60, 61, 30)], fontsize=14)
    ax.tick_params(colors=NAVY, length=3)
    for s in ax.spines.values():
        s.set_edgecolor(NAVY)
        s.set_linewidth(0.8)


def sheet(name, draw, figsize=(13.0, 4.8)):
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    draw(fig, ax)
    fig.tight_layout(pad=0.4)
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor="white", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    print("   wrote %s" % name)


t0 = time.time()

# ---------------------------------------------------------------- Viking ----
print("Viking MDIM 2.1 colour, 232 m/px ...")
vik = decimate(M.VIKING, 3000, os.path.join(HERE, "viking_global_3000.npy"))
sheet("g_viking.png", lambda f, ax: (
    ax.imshow(vik, extent=[-180, 180, -90, 90], interpolation="bilinear"),
    frame(ax)))

# ---------------------------------------------------------------- THEMIS ----
print("THEMIS Day IR v12, 100 m/px ...")
the = decimate(M.THEMIS, 3000, os.path.join(HERE, "themis_global_3000.npy"),
               roll=True)
the8 = M.stretch(the, 1, 99, mask=the > 0)          # 2.7% of the globe is fill
sheet("g_themis.png", lambda f, ax: (
    ax.imshow(the8, extent=[-180, 180, -90, 90], cmap="gray",
              interpolation="bilinear"),
    frame(ax)))

# ------------------------------------------------------------------- DEM ----
print("HRSC/MOLA blended DEM, 200 m/px ...")
dem = decimate(M.DEM, 3000, os.path.join(HERE, "dem_global_3000.npy"))
dem = dem.astype(np.float32)
dem[dem < -20000] = np.nan
print("   relief %.0f m to %.0f m" % (np.nanmin(dem), np.nanmax(dem)))


def draw_dem(fig, ax):
    im = ax.imshow(dem / 1000.0, extent=[-180, 180, -90, 90], cmap=MOLA,
                   vmin=-9, vmax=22, interpolation="bilinear")
    frame(ax, label_colour="#10202E")
    cb = fig.colorbar(im, ax=ax, fraction=0.028, pad=0.035)
    cb.set_label("elevation above datum (km)", color=NAVY, fontsize=13)
    cb.ax.tick_params(colors=NAVY, labelsize=12)
    cb.outline.set_edgecolor(NAVY)


sheet("g_dem.png", draw_dem)

np.save(os.path.join(HERE, "dem_global_3000_f32.npy"), dem)
print("done in %.1f s" % (time.time() - t0))
