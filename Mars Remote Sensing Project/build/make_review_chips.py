# -*- coding: utf-8 -*-
r"""Contact sheets for reviewing type-area candidates by eye, outside Pro (KB §69.51).

    python make_review_chips.py --area ath --where "ThermIdx < -0.15 AND Review IS NULL" --out <folder>
    python make_review_chips.py --area ath --where "Review IS NOT NULL" --sample 60 --seed 51 --out <folder>
    python make_review_chips.py --copies --area ath --out <folder> --context 60      # the digitising class's copies

Each candidate is one row of four panels over the same square window, at the rasters' own 100 m pixels: local
relief (the DEM minus its 2.1 km moving mean, troughs dark) with the candidate line drawn on it, then a hillshade
computed from the DEM with 5x vertical exaggeration, Viking colour (bands 1-3 of <area>_composite_5band.tif) and
THEMIS day IR (band 4), each with only the line's two ends marked, so the ground under the line stays visible. The
drive's 8-bit hillshade is not used: stretched over the flat Athabasca plains it shows only its quantisation steps. The window
is the line's extent padded by 40 %, at least --min-km on a side (or --context km, for judging origin from the
surroundings). Each row is labelled by its slot (sheet letter and row number) with the line's length and Strahler
order; the measures a review could be scored against (ThermIdx, SlopeDeg, the gradient) are not shown, and neither
is any existing Review value, so a sheet of already-judged rows can be reviewed blind. index.json maps every slot to
its class and OBJECTID. Read-only on the gdb. ArcGIS Python (arcpy for the lines, GDAL for the pixels).
"""
import os, sys, json, random, string
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from osgeo import gdal
from scipy.ndimage import uniform_filter
import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive

gdal.UseExceptions()
AREAS = {"ius": ("Landform_ChannelCandidates_auto", r"Mars Project\TypeArea\ius_composite_5band.tif",
                 r"Mars Project\TypeArea\ius_dem.tif"),
         "ath": ("Landform_ChannelCandidates_auto_ath", r"Mars Project\Athabasca\ath_composite_5band.tif",
                 r"Mars Project\Athabasca\ath_dem.tif")}
INK, MUTED, EDGE, LINE = "#0b0b0b", "#52514e", "#d9dee3", "#eb6834"


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def rows(fc, where, copies, area):
    """(class, OBJECTID, [[x, y], ...] parts, length km, Strahler order) for each line."""
    out = []
    if copies:
        cand = AREAS[area][0]
        with arcpy.da.SearchCursor(os.path.join(GDB, "Landform_ChannelCenterlines"),
                                   ["OID@", "SHAPE@", "OrderStrahler", "SourceID"],
                                   "SourceID LIKE '%s:%%'" % cand) as cur:
            for oid, g, order, _ in cur:
                out.append(("Landform_ChannelCenterlines", oid, [[(p.X, p.Y) for p in part] for part in g],
                            g.length / 1000.0, order))
        return out
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["OID@", "SHAPE@", "LengthKm", "StrahlerOrd"], where) as cur:
        for oid, g, km, order in cur:
            out.append((fc, oid, [[(p.X, p.Y) for p in part] for part in g], km, order))
    return out


class Grid:
    def __init__(self, comp, dem):
        self.c, self.h = gdal.Open(comp), gdal.Open(dem)
        self.gt = self.c.GetGeoTransform()
        assert self.gt == self.h.GetGeoTransform(), "composite and DEM grids differ"
        self.nx, self.ny = self.c.RasterXSize, self.c.RasterYSize

    def read(self, x0, x1, y0, y1):
        gt = self.gt
        c0 = max(0, int((x0 - gt[0]) / gt[1])); c1 = min(self.nx, int(np.ceil((x1 - gt[0]) / gt[1])))
        r0 = max(0, int((y1 - gt[3]) / gt[5])); r1 = min(self.ny, int(np.ceil((y0 - gt[3]) / gt[5])))
        comp = self.c.ReadAsArray(c0, r0, c1 - c0, r1 - r0)
        dem = self.h.ReadAsArray(c0, r0, c1 - c0, r1 - r0).astype(np.float64)
        ext = [gt[0] + c0 * gt[1], gt[0] + c1 * gt[1], gt[3] + r1 * gt[5], gt[3] + r0 * gt[5]]
        return comp, dem, ext


def relief(dem, px=21):
    """The DEM minus its px x px moving mean, clipped at its 2nd and 98th percentiles, to 0-1."""
    r = dem - uniform_filter(dem, px, mode="nearest")
    lo, hi = np.percentile(r, (2, 98))
    return np.clip((r - lo) / max(1e-6, hi - lo), 0, 1)


def shade(dem, z=5.0, az=315.0, alt=45.0, cell=100.0):
    """Hillshade of the DEM with vertical exaggeration z, 0-1."""
    gy, gx = np.gradient(dem * z, cell)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    a, e = np.radians(360.0 - az + 90.0), np.radians(alt)
    return np.clip(np.sin(e) * np.cos(slope) + np.cos(e) * np.sin(slope) * np.cos(a - aspect), 0, 1)


def stretch(b, lo=1, hi=99):
    v = b[b > 0]
    if v.size == 0:
        return np.zeros(b.shape, np.float32)
    p0, p1 = np.percentile(v, (lo, hi))
    return np.clip((b.astype(np.float32) - p0) / max(1e-6, p1 - p0), 0, 1)


def main():
    area = arg("--area", "ath")
    fc, comp_p, dem_p = AREAS[area]
    out = arg("--out")
    assert out, "--out <folder> is required"
    per = int(arg("--per", "6"))
    min_km = float(arg("--min-km", "12"))
    context = arg("--context")
    lines = rows(fc, arg("--where", "1=1"), "--copies" in sys.argv, area)
    if "--sample" in sys.argv:
        random.Random(int(arg("--seed", "51"))).shuffle(lines)
        lines = lines[:int(arg("--sample"))]
    elif "--seed" in sys.argv:
        random.Random(int(arg("--seed"))).shuffle(lines)
    else:
        lines.sort(key=lambda r: r[1])
    grid = Grid(on_drive(comp_p), on_drive(dem_p))
    os.makedirs(out, exist_ok=True)
    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    index, letters = {}, string.ascii_uppercase
    nsheet = (len(lines) + per - 1) // per
    for s in range(nsheet):
        tag = letters[s % 26] * (1 + s // 26)
        batch = lines[s * per:(s + 1) * per]
        fig, axes = plt.subplots(len(batch), 4, figsize=(10.0, 2.55 * len(batch)), dpi=130, squeeze=False)
        for i, (cls, oid, parts, km, order) in enumerate(batch):
            slot = "%s%d" % (tag, i + 1)
            index[slot] = {"class": cls, "oid": oid}
            xs = [p[0] for part in parts for p in part]; ys = [p[1] for part in parts for p in part]
            cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            half = (float(context) * 500.0 if context else
                    max(min_km * 500.0, 0.7 * max(max(xs) - min(xs), max(ys) - min(ys))))
            comp, dem, ext = grid.read(cx - half, cx + half, cy - half, cy + half)
            rgb = np.dstack([stretch(comp[b]) for b in range(3)])
            day = stretch(comp[3])
            ends = [parts[0][0], parts[-1][-1]]
            for j, (img, cmap, title) in enumerate([(relief(dem), "gray", "local relief + line"),
                                                    (shade(dem), "gray", "hillshade, 5x"),
                                                    (rgb, None, "Viking colour"), (day, "gray", "day IR")]):
                ax = axes[i][j]
                ax.imshow(img, extent=ext, cmap=cmap, interpolation="nearest")
                if j == 0:
                    for part in parts:
                        ax.plot([p[0] for p in part], [p[1] for p in part], color=LINE, lw=1.0, alpha=0.85)
                else:
                    ax.plot([e[0] for e in ends], [e[1] for e in ends], "o", ms=5, mfc="none", mec=LINE, mew=1.2)
                ax.set_xlim(cx - half, cx + half); ax.set_ylim(cy - half, cy + half)
                ax.set_xticks([]); ax.set_yticks([])
                for sp in ax.spines.values():
                    sp.set_color(EDGE)
                ax.set_title((("%s   %.1f km, order %s   window %.0f km" % (slot, km, order, 2 * half / 1000))
                              if j == 0 else title), loc="left", color=INK if j == 0 else MUTED, fontsize=8)
        fig.tight_layout(h_pad=0.6, w_pad=0.3)
        fig.savefig(os.path.join(out, "sheet_%s.png" % tag), facecolor="white")
        plt.close(fig)
    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"area": area, "where": arg("--where"), "copies": "--copies" in sys.argv, "slots": index}, f, indent=1)
    print("lines", len(lines), "sheets", nsheet, "->", out)


if __name__ == "__main__":
    main()
