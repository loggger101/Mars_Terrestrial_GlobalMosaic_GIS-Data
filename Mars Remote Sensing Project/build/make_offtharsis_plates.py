# -*- coding: utf-8 -*-
r"""Plates for drawing the off-Tharsis edifice and apron labels on CTX (NEXT-STEPS §14 row 3; KB §69.63, §69.105;
registered in logs\agent_review\offtharsis_registration.md before any plate was drawn).

    python make_offtharsis_plates.py [--out <folder>] [--only S1,A1]
                                     (default <drive>\Mars Project\review_sheets\offtharsis\plates)

Each plate is a lon/lat box inside one held-out block (4_0 for the edifice targets at Syrtis Major, 4_2 for the
apron targets at Nilosyrtis Mensae and Colles Nili; review_sheets\offtharsis\README.md), drawn twice side by side:
1. CTX (Murray Lab V01 through Esri's tiles, make_ctx_chips' checked renders: a close view kept only if it agrees
with a view three times as wide, else re-rendered at another zoom level, else the wide view stands in), and 2. the
hillshade of the ±60° DEM (global60_dem.tif, 200 m; light from the north-west). Both carry a grid in degrees, for
reading vertices. No classification map, label set or geologic unit is shown, so the labels are drawn from the
images alone. plates.json gives each plate's box and its CTX note. Read-only on the gdb and the rasters.
ArcGIS Python, needs a network for CTX views not yet cached.
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
from paths import on_drive
from make_ctx_chips import Renderer, checked_far, checked_near
from make_review_chips import arg
from check_v3_labels import hillshade
import propose_v3_labels as P

R = 3396190.0
# name: (lon0, lon1, lat0, lat1, what); overviews first (O*), then the close plates
PLATES = {
    "O1": (65.0, 71.0, 5.0, 11.0, "Syrtis Major summit: Nili and Meroe Paterae (block 4_0)"),
    "O2": (66.0, 72.0, 32.0, 38.0, "Nilosyrtis Mensae (block 4_2)"),
    "O3": (60.0, 66.0, 36.0, 42.0, "Colles Nili (block 4_2)"),
    "S1": (66.3, 68.1, 8.1, 9.9, "Nili Patera and Nili Tholus"),
    "S2": (67.9, 69.7, 6.1, 7.9, "Meroe Patera"),
}


OVERLAY = None   # --overlay <drawing.json>: the drawn polygons over both panels, written as <name>_drawn.png


def to_x(lon):
    return R * math.radians((lon % 360.0) - 180.0)


def to_lon(x):
    return math.degrees(x / R) + 180.0


def plate(name, box, what, renderer, dem, out):
    lon0, lon1, lat0, lat1 = box
    cx, cy = to_x((lon0 + lon1) / 2), R * math.radians((lat0 + lat1) / 2)
    half = R * math.radians((lat1 - lat0) / 2)
    key = "offth_%s_%.2f_%.2f_%.2f" % (name, lon0, lat0, lat1 - lat0)
    far, e_far, ok = checked_far(renderer, key, cx, cy, 3 * 2 * half / 1000.0)
    img, ext, note = checked_near(renderer, key, cx, cy, half, far, e_far)
    if not ok:
        note = "CTX UNCHECKED: no two zoom levels agree"
    ext_deg = [to_lon(ext[0]), to_lon(ext[1]), math.degrees(ext[2] / R), math.degrees(ext[3] / R)]
    r0, r1 = int((P.LAT0 - lat1) / P.DP), int(math.ceil((P.LAT0 - lat0) / P.DP))
    c0, c1 = int(math.floor(lon0 / P.DP)), int(math.ceil(lon1 / P.DP))
    z = dem.window(r0, r1, c0, c1)
    step = max(1, (r1 - r0) // 900)
    hs = hillshade(z[::step, ::step] if step > 1 else z, (lat0 + lat1) / 2)
    span = lon1 - lon0
    major = 1.0 if span > 3 else 0.2
    minor = 0.5 if span > 3 else 0.1
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 8.2), dpi=110)
    for ax, (im, e, title) in zip(axes, ((img, ext_deg, note),
                                         (hs, (c0 * P.DP, c1 * P.DP, P.LAT0 - r1 * P.DP, P.LAT0 - r0 * P.DP),
                                          "DEM hillshade (200 m, light from NW)"))):
        if im.ndim == 2:
            ax.imshow(im, extent=e, cmap="gray", vmin=-0.2, vmax=1.0, interpolation="bilinear")
        else:
            ax.imshow(im, extent=e, interpolation="bilinear")
        ax.set_xlim(lon0, lon1); ax.set_ylim(lat0, lat1)
        ax.set_xticks(np.arange(math.ceil(lon0 / major) * major, lon1 + 1e-9, major))
        ax.set_yticks(np.arange(math.ceil(lat0 / major) * major, lat1 + 1e-9, major))
        ax.set_xticks(np.arange(math.ceil(lon0 / minor) * minor, lon1 + 1e-9, minor), minor=True)
        ax.set_yticks(np.arange(math.ceil(lat0 / minor) * minor, lat1 + 1e-9, minor), minor=True)
        ax.grid(which="major", color="#ffff66", lw=0.6, alpha=0.6)
        ax.grid(which="minor", color="#ffff66", lw=0.3, alpha=0.35)
        ax.tick_params(labelsize=7, top=True, right=True, labeltop=True, labelright=True)
        for k, p in (OVERLAY or {}).items():
            a = np.array(p["pts"] + p["pts"][:1])
            if not (lon0 < a[:, 0].mean() < lon1 and lat0 < a[:, 1].mean() < lat1):
                continue
            ax.plot(a[:, 0], a[:, 1], color="#ff7a1a", lw=1.2)
            ax.text(a[:, 0].mean(), a[:, 1].mean(), k, color="#ff7a1a", fontsize=9, fontweight="bold")
        ax.set_title("%s  %s  |  %s" % (name, what, title), loc="left", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "%s%s.png" % (name, "_drawn" if OVERLAY else "")), facecolor="white")
    plt.close(fig)
    return note


def main():
    out = arg("--out", on_drive(r"Mars Project\review_sheets\offtharsis\plates"))
    os.makedirs(out, exist_ok=True)
    only = set(arg("--only", "").split(",")) - {""}
    global OVERLAY
    if arg("--overlay"):
        OVERLAY = json.load(open(arg("--overlay"), encoding="utf-8"))
    extra = arg("--plates")          # a JSON file of further plates, {name: [lon0, lon1, lat0, lat1, what]}
    plates = dict(PLATES)
    if extra:
        plates.update({k: tuple(v) for k, v in json.load(open(extra, encoding="utf-8")).items()})
    state = {}

    def renderer():
        if "r" not in state:
            state["r"] = Renderer()
        return state["r"]

    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    dem = P.Dem()
    meta_p = os.path.join(out, "plates.json")
    meta = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {}
    for name, (lon0, lon1, lat0, lat1, what) in plates.items():
        if only and name not in only:
            continue
        note = plate(name, (lon0, lon1, lat0, lat1), what, renderer, dem, out)
        meta[name] = {"box": [lon0, lon1, lat0, lat1], "what": what, "ctx": note}
        print(name, note, flush=True)
    json.dump(meta, open(meta_p, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
