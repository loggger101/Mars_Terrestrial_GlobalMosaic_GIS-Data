# -*- coding: utf-8 -*-
r"""Contact sheets on the CTX mosaic (~5 m) for reviewing channel candidates (KB §69.52).

    python make_ctx_chips.py --area ath --where "ThermIdx < -0.15 AND Review IS NULL" --out <folder>
    python make_ctx_chips.py --area ath --where "Review IS NOT NULL" --exclude <index.json> --sample 48 --seed 52 --out <folder>
    python make_ctx_chips.py --copies --area ius --out <folder>
    python make_ctx_chips.py --redo <index.json> --sample 30 --seed 53 --out <folder>    # the same rows, new slots

Each candidate is one row of four panels: CTX over the review window (the line's extent padded by 40 %, at least
--min-km, 12 km) with the line drawn; the same CTX without the line, its two ends marked; CTX over a 40 km window
around it with the line, for its setting; and the local relief (make_review_chips.relief) over the review window
with the line. The CTX views are exported by Pro from Esri's tiled service of the Murray Lab mosaic V01 (the layer
add_ctx_layer.py puts in the digitising maps) into a scratch copy of the .aprx, 600 x 600 px each, and cached in
<drive>\Mars Project\review_sheets\ctx_cache\ with their exact extents, so a rerun draws only what is missing.
The sheets show no Review, ThermIdx, slope or gradient; --redo draws rows of an earlier index under new slot names in
a new order, for a blind repeat. index.json maps each slot to its class and OBJECTID. Read-only on the gdb and the
.aprx. ArcGIS Python, needs a network.
"""
import os, sys, json, random, string, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive
from make_review_chips import AREAS, rows, Grid, relief, arg
from add_ctx_layer import CTX_URL
from ctx_consistency import agree

AGREE = 0.9                  # known good close views 0.97-0.99 against the 40 km view, misplaced ones 0.14-0.16
CACHE = on_drive(r"Mars Project\review_sheets\ctx_cache")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", os.environ.get("TEMP", ".")), "Temp", "mars_scratch", "ctx")
INK, MUTED, EDGE, LINE = "#0b0b0b", "#52514e", "#d9dee3", "#eb6834"
PX = 600


class Renderer:
    """Pro, headless: one map holding only the CTX layer, one square layout frame, exported per window."""

    def __init__(self):
        os.makedirs(SCRATCH, exist_ok=True)
        aprx = os.path.join(SCRATCH, "ctx_chips.aprx")
        arcpy.mp.ArcGISProject(on_drive(r"Mars Project\Mars Project.aprx")).saveACopy(aprx)
        self.p = arcpy.mp.ArcGISProject(aprx)
        sr = self.p.listMaps("Athabasca Valles — digitising")[0].spatialReference
        self.m = self.p.createMap("ctx_chips")
        self.m.spatialReference = sr
        for l in self.m.listLayers():
            self.m.removeLayer(l)
        self.m.addDataFromPath(CTX_URL)
        lyt = self.p.createLayout(6, 6, "INCH", "ctx_chips")
        self.mf = lyt.createMapFrame(arcpy.Extent(0, 0, 6, 6), self.m, "frame")
        self.lyt, self.sr = lyt, sr

    def export(self, path, x0, y0, x1, y1):
        self.mf.camera.setExtent(arcpy.Extent(x0, y0, x1, y1, spatial_reference=self.sr))
        e = self.mf.camera.getExtent()
        self.lyt.exportToPNG(path, resolution=PX // 6)
        return [e.XMin, e.XMax, e.YMin, e.YMax]


def ctx(renderer, key, x0, y0, x1, y1):
    """The cached CTX view for this window (rendered first if missing): image array and its extent."""
    png, meta = os.path.join(CACHE, key + ".png"), os.path.join(CACHE, key + ".json")
    if not (os.path.exists(png) and os.path.exists(meta)):
        ext = renderer().export(png, x0, y0, x1, y1)
        json.dump({"extent": ext}, open(meta, "w"))
    return plt.imread(png), json.load(open(meta))["extent"]


def checked_far(renderer, key, cx, cy, km):
    """The context view, checked the same way against a 30 km render (another zoom level); if the two disagree, a
    56 km render decides which is sound. Returns image, extent and whether any pair agreed."""
    h = km * 500.0
    far, e = ctx(renderer, key + "_far", cx - h, cy - h, cx + h, cy + h)
    meta = os.path.join(CACHE, key + "_far.json")
    m = json.load(open(meta))
    if "agree" not in m:
        f30, e30 = ctx(renderer, key + "_far30", cx - 0.75 * h, cy - 0.75 * h, cx + 0.75 * h, cy + 0.75 * h)
        m["agree"], m["use"] = agree(f30, e30, far, e), "far"
        if m["agree"] < AGREE:
            f56, e56 = ctx(renderer, key + "_far56", cx - 1.4 * h, cy - 1.4 * h, cx + 1.4 * h, cy + 1.4 * h)
            r40, r30 = agree(far, e, f56, e56), agree(f30, e30, f56, e56)
            m["tried"] = {"40v56": round(r40, 3), "30v56": round(r30, 3)}
            if r40 >= AGREE:
                m["agree"] = r40
            elif r30 >= AGREE:
                m["agree"], m["use"] = r30, "far56"
        json.dump(m, open(meta, "w"))
    if m["use"] == "far56":
        far, e = plt.imread(os.path.join(CACHE, key + "_far56.png")), json.load(open(os.path.join(CACHE, key + "_far56.json")))["extent"]
    return far, e, m["agree"] >= AGREE


def checked_near(renderer, key, cx, cy, half, far, e_far):
    """The close view, checked against the 40 km view (ctx_consistency.agree >= AGREE). The service holds misplaced
    tiles at some zoom levels, so a failing view is rendered again over a window 1.5, 2 and 0.67 times as wide (each a
    different zoom level) and the first that agrees is kept; if none does, the 40 km view stands in. Returns the
    image, its extent and a note for the panel title; the outcome is cached beside the image."""
    meta = os.path.join(CACHE, key + "_near.json")
    near, e = ctx(renderer, key + "_near", cx - half, cy - half, cx + half, cy + half)
    m = json.load(open(meta))
    if "agree" not in m:
        m["agree"], m["scale"] = agree(near, e, far, e_far), 1.0
        for f in (1.5, 2.0, 0.67):
            if m["agree"] >= AGREE:
                break
            alt, e_alt = ctx(renderer, "%s_near%g" % (key, f), cx - f * half, cy - f * half, cx + f * half, cy + f * half)
            r = agree(alt, e_alt, far, e_far)
            if r >= AGREE:
                shutil.copy2(os.path.join(CACHE, "%s_near%g.png" % (key, f)), os.path.join(CACHE, key + "_near.png"))
                m = {"extent": e_alt, "agree": r, "scale": f}
            else:
                m.setdefault("tried", []).append([f, round(r, 3)])
        if m["agree"] < AGREE:
            m["fallback"] = True
        json.dump(m, open(meta, "w"))
    if m.get("fallback"):
        return far, e_far, "CTX: close tiles misplaced, 40 km view"
    near = plt.imread(os.path.join(CACHE, key + "_near.png"))
    return near, m["extent"], "CTX" + ("" if m["scale"] == 1.0 else " (render x%g)" % m["scale"])


def main():
    out = arg("--out")
    assert out, "--out <folder> is required"
    per, min_km, ctx_km = int(arg("--per", "6")), float(arg("--min-km", "12")), float(arg("--context-km", "40"))
    if "--redo" in sys.argv:
        old = json.load(open(arg("--redo"), encoding="utf-8"))
        area = old["area"]
        want = {(v["class"], v["oid"]) for v in old["slots"].values()}
        pool = []
        for cls in sorted({c for c, _ in want}):
            copies = cls == "Landform_ChannelCenterlines"
            pool += [r for r in rows(AREAS[area][0], "1=1", copies, area) if (r[0], r[1]) in want]
    else:
        area = arg("--area", "ath")
        pool = rows(AREAS[area][0], arg("--where", "1=1"), "--copies" in sys.argv, area)
        if "--exclude" in sys.argv:
            skip = {(v["class"], v["oid"]) for v in json.load(open(arg("--exclude"), encoding="utf-8"))["slots"].values()}
            pool = [r for r in pool if (r[0], r[1]) not in skip]
    pool.sort(key=lambda r: (r[0], r[1]))
    if "--seed" in sys.argv:
        random.Random(int(arg("--seed"))).shuffle(pool)
    if "--sample" in sys.argv:
        pool = pool[:int(arg("--sample"))]
    os.makedirs(CACHE, exist_ok=True); os.makedirs(out, exist_ok=True)
    grid = Grid(on_drive(AREAS[area][1]), on_drive(AREAS[area][2]))
    state = {}

    def renderer():
        if "r" not in state:
            state["r"] = Renderer()
        return state["r"]

    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    index, nsheet = {}, (len(pool) + per - 1) // per
    for s in range(nsheet):
        tag = string.ascii_uppercase[s % 26] * (1 + s // 26)
        batch = pool[s * per:(s + 1) * per]
        fig, axes = plt.subplots(len(batch), 4, figsize=(10.0, 2.55 * len(batch)), dpi=130, squeeze=False)
        for i, (cls, oid, parts, km, order) in enumerate(batch):
            slot = "%s%d" % (tag, i + 1)
            index[slot] = {"class": cls, "oid": oid}
            xs = [p[0] for part in parts for p in part]; ys = [p[1] for part in parts for p in part]
            cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            half = max(min_km * 500.0, 0.7 * max(max(xs) - min(xs), max(ys) - min(ys)))
            key = "%s_%d" % (cls, oid)
            far, e_far, far_ok = checked_far(renderer, key, cx, cy, ctx_km)
            near, e_near, note = checked_near(renderer, key, cx, cy, half, far, e_far)
            if not far_ok:
                note = "CTX UNCHECKED: no two zoom levels agree"
            index["%s%d" % (tag, i + 1)] = {"class": cls, "oid": oid, "ctx": note}
            _, dem, e_dem = grid.read(cx - half, cx + half, cy - half, cy + half)
            ends = [parts[0][0], parts[-1][-1]]
            panels = [(near, e_near, None, "CTX + line", "line", half),
                      (near, e_near, None, note, "ends", half),
                      (far, e_far, None, "CTX, %d km around" % ctx_km, "line", ctx_km * 500),
                      (relief(dem), e_dem, "gray", "local relief + line", "line", half)]
            for j, (img, ext, cmap, title, mark, h) in enumerate(panels):
                ax = axes[i][j]
                ax.imshow(img, extent=ext, cmap=cmap, interpolation="nearest")
                if mark == "line":
                    for part in parts:
                        ax.plot([p[0] for p in part], [p[1] for p in part], color=LINE, lw=1.0, alpha=0.85)
                else:
                    ax.plot([e[0] for e in ends], [e[1] for e in ends], "o", ms=5, mfc="none", mec=LINE, mew=1.2)
                ax.set_xlim(cx - h, cx + h); ax.set_ylim(cy - h, cy + h)
                ax.set_xticks([]); ax.set_yticks([])
                for sp in ax.spines.values():
                    sp.set_color(EDGE)
                ax.set_title(("%s   %.1f km, order %s   window %.0f km" % (slot, km, order, 2 * half / 1000))
                             if j == 0 else title, loc="left", color=INK if j == 0 else MUTED, fontsize=8)
        fig.tight_layout(h_pad=0.6, w_pad=0.3)
        fig.savefig(os.path.join(out, "sheet_%s.png" % tag), facecolor="white")
        plt.close(fig)
        print("sheet", tag, flush=True)
    json.dump({"area": area, "where": arg("--where"), "copies": "--copies" in sys.argv or "--redo" in sys.argv and
               any(v["class"] == "Landform_ChannelCenterlines" for v in index.values()),
               "ctx": True, "slots": index}, open(os.path.join(out, "index.json"), "w", encoding="utf-8"), indent=1)
    print("lines", len(pool), "sheets", nsheet, "->", out)


if __name__ == "__main__":
    main()
