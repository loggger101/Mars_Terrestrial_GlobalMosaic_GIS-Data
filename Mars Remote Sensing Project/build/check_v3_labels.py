# -*- coding: utf-8 -*-
r"""Contact sheets of the v3 label rows over DEM hillshade, one sheet per class, to read the screens by eye (KB §69.49).

Reads Landform_TrainingSamples_v3_proposals (propose_v3_labels.py). Per class: up to 8 accepted rows (new and pieces
alike) drawn solid, and up to 4 rejected ones dashed, each over the hillshade of global60_dem.tif with its
neighbours of any class outlined thin. Random with a fixed seed; --seed N for another draw.

  python check_v3_labels.py [--out <folder>] [--seed N]       default out: logs\v3_label_sheets
"""
import os, sys, math, random
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import propose_v3_labels as P

OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "logs", "v3_label_sheets")
SEED = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1
FC = os.path.join(GDB, P.OUT)


def hillshade(z, lat):
    dy = 200.0
    dx = 200.0 * math.cos(math.radians(lat))
    gy, gx = np.gradient(np.nan_to_num(z, nan=np.nanmedian(z)), dy, dx)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    az, alt = math.radians(315), math.radians(45)
    return np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)


def rings(g):
    for part in g:
        ring = []
        for p in part:
            if p is None:
                if ring:
                    yield ring
                ring = []
            else:
                ring.append((p.X, p.Y))
        if ring:
            yield ring


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    with arcpy.da.SearchCursor(FC, ["OID@", "ProposedClass", "Action", "Review", "ReviewNote", "Source", "SHAPE@"]) as c:
        for r in c:
            rows.append(r)
    rng = random.Random(SEED)
    dem = P.Dem()
    for cls, (name, rgb) in P.CLASSES.items():
        acc = [r for r in rows if r[1] == cls and r[3] == "accept" and r[2] != "keep"]
        rej = [r for r in rows if r[1] == cls and r[3] == "reject"]
        pick = rng.sample(acc, min(8, len(acc))) + rng.sample(rej, min(4, len(rej)))
        if not pick:
            continue
        fig, axes = plt.subplots(3, 4, figsize=(16, 12.5))
        for ax in axes.ravel():
            ax.axis("off")
        for ax, (oid, _, act, rev, note, src, g) in zip(axes.ravel(), pick):
            e = g.extent
            cx, cy = (e.XMin + e.XMax) / 2, (e.YMin + e.YMax) / 2
            half = max(e.XMax - e.XMin, e.YMax - e.YMin) * 0.9 + 0.08
            x0, x1, y0, y1 = cx - half, cx + half, max(cy - half, -60), min(cy + half, 60)
            r0, r1 = int((P.LAT0 - y1) / P.DP), int((P.LAT0 - y0) / P.DP)
            c0, c1 = int(math.floor(x0 / P.DP)), int(math.ceil(x1 / P.DP))
            step = max(1, (r1 - r0) // 500)
            z = dem.window(r0, r1, c0, c1)[::step, ::step]
            ax.imshow(hillshade(z, cy) if step == 1 else hillshade(z, cy), cmap="gray", vmin=-0.2, vmax=1.0,
                      extent=(c0 * P.DP, c1 * P.DP, P.LAT0 - r1 * P.DP, P.LAT0 - r0 * P.DP), interpolation="bilinear")
            for o in rows:                                     # neighbours of any class, accepted only
                if o[0] == oid or o[3] != "accept":
                    continue
                oe = o[6].extent
                if oe.XMax < x0 or oe.XMin > x1 or oe.YMax < y0 or oe.YMin > y1:
                    continue
                col = [v / 255 for v in P.CLASSES[o[1]][1]]
                for ring in rings(o[6]):
                    a = np.array(ring)
                    ax.plot(a[:, 0], a[:, 1], color=col, lw=0.7, alpha=0.8)
            col = [v / 255 for v in rgb]
            for ring in rings(g):
                a = np.array(ring)
                ax.plot(a[:, 0], a[:, 1], color=col, lw=2.2, ls="-" if rev == "accept" else "--")
            ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
            ax.axis("on"); ax.tick_params(labelsize=7)
            ax.set_title("%s %s %d: %s\n%s\n%s" % (rev.upper(), act, oid, src[:48], note[18:78], note[78:138]),
                         fontsize=7.5, loc="left")
        fig.suptitle("v3 labels: %d %s, %d accepted of %d non-keep rows, %d rejected (solid accepted, dashed rejected)" % (
            cls, name, len(acc), len([r for r in rows if r[1] == cls and r[2] != "keep"]), len(rej)), fontsize=12)
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        p = os.path.join(OUT, "v3_class%d_%s.png" % (cls, name.split()[0].replace("/", "_")))
        fig.savefig(p, dpi=80)
        plt.close(fig)
        print(p)


if __name__ == "__main__":
    main()
