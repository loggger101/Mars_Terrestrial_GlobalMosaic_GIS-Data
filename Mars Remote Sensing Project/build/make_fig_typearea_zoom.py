# -*- coding: utf-8 -*-
r"""Figure for the paper (NEXT-STEPS §12.4 W4): the published map against the imagery at full resolution, in one
window of the Ius Chasma type area.

Three panels over the same window (WINDOW, degrees east and north): the Viking colour bands and THEMIS day IR at
their 100 m pixels (ius_composite_5band.tif, bands 1-3 and 4; Viking is high-pass filtered and its colour an
uncalibrated blend, KB §69.50, so the panel says "Viking colour"), and the published four-class map
(global60_landforms_svm_200m_mode11.tif, 200 m, 11 x 11 majority filter; 73.8 % held out, KB §57) in the class
colours, each pixel drawn as a 2 x 2 block of the 100 m grid, nothing resampled. The map's pixel values are checked
against its attribute table (pixel = class code, KB §36) before any colour is drawn. Reads two windows from the
drive; writes build\final_img\typearea_zoom.png. ArcGIS Python (arcpy for the table, GDAL for the pixels).
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from osgeo import gdal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive
from labelsets import FOUR, COLOURS
import landform_codes

gdal.UseExceptions()
COMP = on_drive(r"Mars Project\TypeArea\ius_composite_5band.tif")
MAP = on_drive(r"Mars Project\Global60\global60_landforms_svm_200m_mode11.tif")
OUT = os.path.join(HERE, "final_img", "typearea_zoom.png")
DEG = 3396190.0 * np.pi / 180.0
WINDOW = [float(v) for v in (sys.argv[sys.argv.index("--window") + 1].split(",")
                             if "--window" in sys.argv else (277.0, 280.0, -10.5, -7.5))]   # lon0, lon1, lat0, lat1
INK, MUTED, EDGE = "#0b0b0b", "#52514e", "#d9dee3"


def window(path, lon0, lon1, lat0, lat1):
    """The pixels of path inside the window (snapped outward to its pixel edges) and their extent in degrees."""
    ds = gdal.Open(path)
    gt = ds.GetGeoTransform()
    c0 = int(np.floor(((lon0 - 180.0) * DEG - gt[0]) / gt[1]))
    c1 = int(np.ceil(((lon1 - 180.0) * DEG - gt[0]) / gt[1]))
    r0 = int(np.floor((lat1 * DEG - gt[3]) / gt[5]))
    r1 = int(np.ceil((lat0 * DEG - gt[3]) / gt[5]))
    assert 0 <= c0 < c1 <= ds.RasterXSize and 0 <= r0 < r1 <= ds.RasterYSize, "window outside %s" % path
    a = ds.ReadAsArray(c0, r0, c1 - c0, r1 - r0)
    ext = [180.0 + (gt[0] + c0 * gt[1]) / DEG, 180.0 + (gt[0] + c1 * gt[1]) / DEG,
           (gt[3] + r1 * gt[5]) / DEG, (gt[3] + r0 * gt[5]) / DEG]
    return a, ext


def stretch(b, lo=1, hi=99):
    """A percentile stretch over the valid (non-zero) pixels, to 0-1."""
    v = b[b > 0]
    p0, p1 = np.percentile(v, (lo, hi))
    return np.clip((b.astype(np.float32) - p0) / (p1 - p0), 0, 1)


def main():
    table = landform_codes.rat(MAP)
    names = {v: n for v, (code, n, _) in table.items()}
    assert all(v == code for v, (code, _, _) in table.items()), "pixel != class code: %s" % table
    assert [names[c] for c in sorted(names)] == FOUR, "class names %s, expected %s" % (names, FOUR)
    lon0, lon1, lat0, lat1 = WINDOW
    comp, ext_c = window(COMP, lon0, lon1, lat0, lat1)
    cls, ext_m = window(MAP, lon0, lon1, lat0, lat1)
    rgb = np.dstack([stretch(comp[i]) for i in range(3)])
    rgb[(comp[:3] == 0).any(0)] = 1.0
    day = np.where(comp[3] > 0, stretch(comp[3]), np.nan)
    lut = np.full((256, 4), 0.0)
    for v, n in names.items():
        lut[v, :3] = np.array(COLOURS[n]) / 255.0
        lut[v, 3] = 1.0
    shares = {n: float((cls == v).sum()) / max(1, int((cls != 255).sum())) for v, n in names.items()}
    print("window", WINDOW, "composite", comp.shape, "map", cls.shape, "shares",
          {n: round(100 * s, 1) for n, s in shares.items()})

    plt.rcParams.update({"font.family": "Arial", "font.size": 9})
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.0), dpi=300, sharey=True)
    panels = [(rgb, ext_c, None, "Viking colour, 100 m"), (day, ext_c, "gray", "THEMIS day IR, 100 m"),
              (lut[cls], ext_m, None, "Published map, 200 m (11 × 11)")]
    for ax, (img, ext, cmap, title) in zip(axes, panels):
        ax.imshow(img, extent=ext, cmap=cmap, interpolation="nearest")
        ax.set_xlim(lon0, lon1); ax.set_ylim(lat0, lat1)
        ax.set_xticks(np.arange(np.ceil(lon0), lon1 + 1e-9, 1.0))
        ax.set_xticklabels(["%g" % v for v in ax.get_xticks()])
        ax.set_aspect("equal")
        ax.set_title(title, loc="left", color=INK, fontsize=9)
        ax.tick_params(colors=MUTED, labelsize=7)
        ax.set_xlabel("East longitude (°)", color=MUTED, fontsize=8)
        for sp in ax.spines.values():
            sp.set_color(EDGE)
    axes[0].set_ylabel("Latitude (°)", color=MUTED, fontsize=8)
    present = [n for n in FOUR if shares[n] > 0]
    fig.legend(handles=[Patch(fc=np.array(COLOURS[n]) / 255.0, ec="none", label="%s %.0f %%" % (n, 100 * shares[n]))
                        for n in present], loc="lower center", ncol=len(present), frameon=False, fontsize=7.5,
               bbox_to_anchor=(0.5, 0.0), handlelength=1.2, columnspacing=1.4)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.25, top=0.92, wspace=0.08)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, facecolor="white")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
