# -*- coding: utf-8 -*-
r"""R1: contact sheets for the author's blind spot-check of the rule-screened apron and fluvial rows (NEXT-STEPS
§12.3; registration logs\r1\r1_registration.md; scored by score_r1.py).

    "<ArcGIS Pro Python>" make_r1_sheets.py --sample          draw the 80 rows (seed 5401); writes logs\r1\r1_key.json
                                                             and r1_slots.json; refuses if they exist
    "<ArcGIS Pro Python>" make_r1_sheets.py [--out <folder>] [--only <sheet>]
                                                             the sheets (default <drive>\Mars Project\review_sheets\r1)

The sample: 30 of the rule's accepts and 10 of its rejects in each class (fluvial channel 7, apron 6), from
logs\label_review_by_rule.json, shuffled together, six to a sheet. The sheets read only r1_slots.json (slot -> OID,
class): no verdict or measure of the rule is shown. Per row: the piece's outline over the DEM hillshade and over CTX,
each across the whole piece, the two close windows boxed; CTX over 20 km at the piece's label point (1) and at its
far end (2), each a make_ctx_chips checked render (checked against a 40 km view at the same place). Every panel is in
a local equidistant cylindrical frame centred on the piece. Read-only on the gdb and the .aprx (a scratch copy
renders). ArcGIS Python, needs a network.
"""
import os, sys, json, math, random
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
from osgeo import gdal
from scipy.ndimage import map_coordinates
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
from make_review_chips import shade
from make_ctx_chips import checked_far, checked_near, INK, MUTED, EDGE, LINE
from make_r2_sheets import LocalRenderer, WKT

gdal.UseExceptions()
R = 3396190.0
DEM = on_drive(r"Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")
PROPOSALS = os.path.join(GDB, "Landform_TrainingSamples_v2_proposals")
RULE = os.path.join(HERE, "logs", "label_review_by_rule.json")
D = os.path.join(HERE, "logs", "r1")
KEY, SLOTS = os.path.join(D, "r1_key.json"), os.path.join(D, "r1_slots.json")
SEED, N_ACC, N_REJ = 5401, 30, 10
ASK = {7: "FLUVIAL CHANNEL? (most of the strip)",
       6: "APRON? (most of the piece)"}
CLOSE = 10000.0                              # half-width of the close views, m
BLUE = "#2a78d6"


def sample():
    if os.path.exists(KEY) or os.path.exists(SLOTS):
        sys.exit("refused: %s exists (the sample is drawn once)" % KEY)
    rows = json.load(open(RULE, encoding="utf-8"))["rows"]
    rnd = random.Random(SEED)
    picked = []
    for cls in (7, 6):
        for verdict, n in (("accept", N_ACC), ("reject", N_REJ)):
            pool = sorted(r["oid"] for r in rows if r["cls"] == cls and r["review"] == verdict)
            picked += [(oid, cls, verdict) for oid in rnd.sample(pool, n)]
    rnd.shuffle(picked)
    tags = [chr(65 + i) for i in range(26)]
    key, slots = {}, {}
    for i, (oid, cls, verdict) in enumerate(picked):
        slot = "%s%d" % (tags[i // 6], i % 6 + 1)
        key[slot] = {"oid": oid, "cls": cls, "rule": verdict}
        slots[slot] = {"oid": oid, "cls": cls}
    os.makedirs(D, exist_ok=True)
    json.dump({"seed": SEED, "source": RULE, "slots": key}, open(KEY, "w", encoding="utf-8"), indent=1)
    json.dump({"slots": slots}, open(SLOTS, "w", encoding="utf-8"), indent=1)
    print("drew", len(key), "rows ->", KEY)


def dem_frame(ds, lon0, lat0, x0, x1, y0, y1, n):
    """n x n DEM samples (m) over a square window of the local frame (x = R cos(lat0) dlon, y = R lat)."""
    gt = ds.GetGeoTransform()
    xx, yy = np.linspace(x0, x1, n), np.linspace(y1, y0, n)
    X, Y = np.meshgrid(xx, yy)
    lat = np.degrees(Y / R)
    lon = (lon0 + np.degrees(X / (R * math.cos(math.radians(lat0)))) + 180) % 360 - 180
    W, H = ds.RasterXSize, ds.RasterYSize
    col = (lon - gt[0]) / gt[1]
    row = (gt[3] - lat) / -gt[5]
    seam = col.max() - col.min() > W / 2                    # the window crosses 180 deg: shift the west part
    if seam:
        col = np.where(col < W / 2, col + W, col)
    c0, c1 = int(col.min()) - 2, int(col.max()) + 3
    r0, r1 = max(int(row.min()) - 2, 0), min(int(row.max()) + 3, H)
    step = max(1, int(math.ceil(max(c1 - c0, r1 - r0) / 1600.0)))
    b = ds.GetRasterBand(1)
    cols = np.arange(c0, c1, step) % W
    nr = int(math.ceil((r1 - r0) / step))
    parts, s = [], 0
    for k in range(1, len(cols) + 1):                       # contiguous runs, split at the 180 deg seam
        if k == len(cols) or cols[k] != cols[k - 1] + step:
            w = int(min(cols[k - 1] + step, W) - cols[s])
            parts.append(b.ReadAsArray(int(cols[s]), r0, w, r1 - r0, buf_xsize=k - s, buf_ysize=nr).astype(np.float32))
            s = k
    a = np.hstack(parts)
    return map_coordinates(a, [(row - r0) / step - 0.5, (col - c0) / step - 0.5], order=1, mode="nearest")


def outline(ax, g):
    for part in g:
        xs, ys = [], []
        for p in part:
            if p is None:
                ax.plot(xs, ys, color=LINE, lw=0.9); xs, ys = [], []
            else:
                xs.append(p.X); ys.append(p.Y)
        if xs:
            ax.plot(xs, ys, color=LINE, lw=0.9)


def box(ax, x, y, h, label):
    ax.plot([x - h, x + h, x + h, x - h, x - h], [y - h, y - h, y + h, y + h, y - h], color=BLUE, lw=0.9)
    ax.text(x + h, y + h, label, color=BLUE, fontsize=7, va="bottom", ha="left")


def sheets():
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else on_drive(r"Mars Project\review_sheets\r1")
    os.makedirs(out, exist_ok=True)
    slots = json.load(open(SLOTS, encoding="utf-8"))["slots"]
    geoms = {}
    oids = sorted({v["oid"] for v in slots.values()})
    with arcpy.da.SearchCursor(PROPOSALS, ["OID@", "SHAPE@"], "OBJECTID IN (%s)" % ",".join(map(str, oids))) as cur:
        for oid, g in cur:
            geoms[oid] = g
    ds = gdal.Open(DEM)
    state = {}

    def renderer():
        if "r" not in state:
            state["r"] = LocalRenderer()
        return state["r"]

    by_sheet = {}
    for slot in slots:
        by_sheet.setdefault(slot.rstrip("0123456789"), []).append(slot)
    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    notes = {}
    for tag, ss in by_sheet.items():
        if "--only" in sys.argv and tag != sys.argv[sys.argv.index("--only") + 1]:
            continue
        png = os.path.join(out, "sheet_%s.png" % tag)
        if os.path.exists(png):
            continue
        H = 3.0 * len(ss) + 0.2
        fig, axes = plt.subplots(len(ss), 4, figsize=(10.0, H), dpi=130, squeeze=False)
        for i, slot in enumerate(ss):
            cls, g = slots[slot]["cls"], geoms[slots[slot]["oid"]]
            e = g.extent
            lon0, lat0 = ((e.XMin + e.XMax) / 2 + 180) % 360 - 180, (e.YMin + e.YMax) / 2
            renderer().at(lon0, lat0)
            sr = arcpy.SpatialReference(); sr.loadFromString(WKT % (lon0, lat0))
            gl = g.projectAs(sr)
            el = gl.extent
            cx, cy = (el.XMin + el.XMax) / 2, (el.YMin + el.YMax) / 2
            h = max(el.XMax - el.XMin, el.YMax - el.YMin) / 2 * 1.15 + 3000.0
            p1 = gl.labelPoint
            verts = [p for part in gl for p in part if p is not None]
            p2 = max(verts, key=lambda p: (p.X - p1.X) ** 2 + (p.Y - p1.Y) ** 2)
            key = "r1_" + slot
            whole, e_whole, whole_ok = checked_far(renderer, key + "_w", cx, cy, 2 * h / 1000.0)
            close, note = [], ["" if whole_ok else "CTX UNCHECKED"]
            for j, p in enumerate((p1, p2)):
                f40, e40, ok40 = checked_far(renderer, "%s_p%d" % (key, j + 1), p.X, p.Y, 40)
                img, ext, nt = checked_near(renderer, "%s_p%d" % (key, j + 1), p.X, p.Y, CLOSE, f40, e40)
                close.append((img, ext, p, nt if ok40 else "CTX UNCHECKED"))
                note.append(close[-1][3])
            notes[slot] = note
            dem = dem_frame(ds, lon0, lat0, cx - h, cx + h, cy - h, cy + h, 500)
            hs = shade(dem, z=3.0, cell=2 * h / 500)
            lat_s = "%.2f %s" % (abs(lat0), "N" if lat0 >= 0 else "S")
            panels = [(hs, [cx - h, cx + h, cy - h, cy + h], "gray",
                       "%s   %s\n%.2f E, %s   DEM hillshade, %.0f km" % (slot, ASK[cls], lon0 % 360, lat_s, 2 * h / 1000), (cx, cy, h)),
                      (whole, e_whole, None, "CTX, %.0f km%s" % (2 * h / 1000, "" if whole_ok else "  (UNCHECKED)"), (cx, cy, h))]
            for j, (img, ext, p, nt) in enumerate(close):
                panels.append((img, ext, None, "(%d) CTX, 20 km%s" % (j + 1, "" if nt == "CTX" else "  " + nt), (p.X, p.Y, CLOSE)))
            for j, (img, ext, cmap, title, (x, y, hh)) in enumerate(panels):
                ax = axes[i][j]
                ax.imshow(img, extent=ext, cmap=cmap, interpolation="nearest" if j else "bilinear")
                outline(ax, gl)
                if j < 2:
                    for k, (_, _, p, _) in enumerate(close):
                        box(ax, p.X, p.Y, CLOSE, str(k + 1))
                ax.set_xlim(x - hh, x + hh); ax.set_ylim(y - hh, y + hh)
                ax.set_xticks([]); ax.set_yticks([])
                for sp in ax.spines.values():
                    sp.set_color(EDGE)
                ax.set_title(title, loc="left", color=INK if j == 0 else MUTED, fontsize=7.5 if j == 0 else 8)
            print(" ", slot, flush=True)
        fig.subplots_adjust(left=0.01, right=0.99, top=1 - 0.42 / H, bottom=0.05 / H, wspace=0.04, hspace=0.2)
        fig.savefig(png, facecolor="white")
        plt.close(fig)
        print("sheet", tag, flush=True)
    idx = os.path.join(out, "index.json")
    old = json.load(open(idx, encoding="utf-8"))["ctx"] if os.path.exists(idx) else {}
    old.update(notes)
    json.dump({"slots": SLOTS, "ctx": old}, open(idx, "w", encoding="utf-8"), indent=1)
    print("sheets", len(by_sheet), "->", out)


if __name__ == "__main__":
    sample() if "--sample" in sys.argv else sheets()
