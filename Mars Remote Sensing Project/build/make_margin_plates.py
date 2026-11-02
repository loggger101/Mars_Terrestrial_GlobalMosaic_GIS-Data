# -*- coding: utf-8 -*-
r"""Plates for tracing lava-flow margins at Athabasca on CTX (KB §69.52; registered in
logs\agent_review\ctx_margins_registration.md before any plate was drawn).

    python make_margin_plates.py --out <folder> [--only W001,W002]

The windows: SIM 3292's lAv polygons inside the Athabasca window, their boundaries sampled every ~1 km (window-edge
stretches dropped), and every 20 km cell of the CM180 grid such a point falls in; each plate is 24 km square around a
cell's centre, so neighbours overlap by 2 km. Each plate is one CTX view (make_ctx_chips' checked renders: a close
view kept only if it agrees with a 48 km view, else re-rendered at another zoom level, else the 48 km view stands in),
600 px over 24 km (40 m per px), with the lAv boundary dashed (where the 1:20 M map puts the edge; the tracing places
it at CTX resolution) and a 2 km grid labelled in km from the plate's south-west corner, for reading vertices. No
THEMIS or Viking band is shown, so traced margins are independent of the bands T5 compares. index.json holds each
plate's corner and centre. Read-only on the gdb. ArcGIS Python, needs a network.
"""
import os, sys, json, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import areas
from make_ctx_chips import Renderer, checked_far, checked_near
from make_review_chips import arg

R = 3396190.0
CELL, HALF, STEP_DEG = 20000.0, 12000.0, 0.015
UNITS = os.path.join(GDB, "Ref_SIM3292_GeologicUnits")


def to_xy(lon, lat):
    """SIM 3292's vertices are spherical lon/lat (KB §47.1) -> the stack's CM180 metres."""
    return R * math.radians((lon % 360.0) - 180.0), R * math.radians(lat)


def lav_boundaries():
    """lAv boundaries inside the Athabasca window, as lists of CM180 points, window-edge stretches removed."""
    A = areas.AREAS["ath"]
    (lo0, lo1), (la0, la1) = A["lon"], A["lat"]
    sr = arcpy.Describe(UNITS).spatialReference
    win = arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in
                                     [(lo0, la0), (lo0, la1), (lo1, la1), (lo1, la0), (lo0, la0)]]), sr)
    lines = []
    with arcpy.da.SearchCursor(UNITS, ["SHAPE@", "Unit"], "Unit = 'lAv'") as cur:
        for g, _ in cur:
            if g.disjoint(win):
                continue
            b = g.intersect(win, 4).boundary()
            for part in b:
                pts = [(p.X, p.Y) for p in part if p is not None]
                dense = []
                for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / STEP_DEG))
                    dense += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n)]
                edge = lambda q: min(abs(q[0] - lo0), abs(q[0] - lo1), abs(q[1] - la0), abs(q[1] - la1)) < 0.01
                run = []
                for q in dense:
                    if edge(q):
                        if len(run) > 1:
                            lines.append(run)
                        run = []
                    else:
                        run.append(to_xy(*q))
                if len(run) > 1:
                    lines.append(run)
    return lines


def main():
    out = arg("--out")
    assert out, "--out <folder> is required"
    os.makedirs(out, exist_ok=True)
    lines = lav_boundaries()
    cells = sorted({(int(x // CELL), int(y // CELL)) for l in lines for x, y in l}, key=lambda c: (-c[1], c[0]))
    only = set(arg("--only", "").split(",")) - {""}
    state = {}

    def renderer():
        if "r" not in state:
            state["r"] = Renderer()
        return state["r"]

    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    index = {}
    for i, (cx_, cy_) in enumerate(cells, 1):
        wid = "W%03d" % i
        cx, cy = (cx_ + 0.5) * CELL, (cy_ + 0.5) * CELL
        x0, y0 = cx - HALF, cy - HALF
        lon, lat = math.degrees(cx / R) + 180.0, math.degrees(cy / R)
        index[wid] = {"x0": x0, "y0": y0, "cx": cx, "cy": cy, "lon": round(lon, 3), "lat": round(lat, 3)}
        if only and wid not in only:
            continue
        key = "margin_%d_%d" % (cx_, cy_)
        far, e_far, far_ok = checked_far(renderer, key, cx, cy, 48)
        img, ext, note = checked_near(renderer, key, cx, cy, HALF, far, e_far)
        if not far_ok:
            note = "CTX UNCHECKED: no two zoom levels agree"
        index[wid]["ctx"] = note
        fig, ax = plt.subplots(figsize=(7.6, 7.9), dpi=120)
        ax.imshow(img, extent=ext, interpolation="nearest")
        for l in lines:
            a = np.array(l)
            ax.plot(a[:, 0], a[:, 1], color="#00c8ff", lw=0.8, ls=(0, (4, 3)), alpha=0.9)
        ax.set_xlim(x0, x0 + 2 * HALF); ax.set_ylim(y0, y0 + 2 * HALF)
        ticks = np.arange(0, 2 * HALF + 1, 2000.0)
        ax.set_xticks(x0 + ticks); ax.set_xticklabels(["%d" % (t / 1000) for t in ticks])
        ax.set_yticks(y0 + ticks); ax.set_yticklabels(["%d" % (t / 1000) for t in ticks])
        ax.grid(color="#ffff66", lw=0.4, alpha=0.45)
        ax.tick_params(labelsize=7, top=True, right=True, labeltop=True, labelright=True)
        ax.set_title("%s   %.2f E, %.2f N   km from the SW corner   %s" % (wid, lon, lat, note), loc="left", fontsize=8)
        fig.tight_layout()
        fig.savefig(os.path.join(out, "%s.png" % wid), facecolor="white")
        plt.close(fig)
        print(wid, note, flush=True)
    json.dump({"cell_m": CELL, "half_m": HALF, "windows": index}, open(os.path.join(out, "index.json"), "w"), indent=1)
    print("plates", len(cells), "->", out)


if __name__ == "__main__":
    main()
