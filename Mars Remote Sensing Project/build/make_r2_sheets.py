# -*- coding: utf-8 -*-
r"""Contact sheets for labelling the R2 sample points blind (KB §69.53; points from make_r2_points.py).

    "<ArcGIS Pro Python>" make_r2_sheets.py [--out <folder>] [--only <sheet>]   (default <drive>\Mars Project\review_sheets\r2)

One row per point, six to a sheet, named by the points' slots: CTX over 8 km with the point ringed (1 km radius,
about the 11 x 11 mode's unit); CTX over 40 km with the 8 km window boxed; the 200 m DEM hillshade over 40 km and over
160 km. No map class, stratum or polygon is shown, and the key file is never opened. The CTX views come through
make_ctx_chips's checked renders (misplaced tiles caught and re-rendered), each in a local equidistant cylindrical
projection centred on the point (true scale there at any latitude); the DEM is resampled to the same square ground
window. Read-only on the gdb and the .aprx (a scratch copy renders). ArcGIS Python, needs a network.
"""
import os, sys, json, math
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
from paths import on_drive
from make_review_chips import shade
from make_ctx_chips import Renderer, checked_far, checked_near, INK, MUTED, EDGE, LINE

gdal.UseExceptions()
R = 3396190.0
DEM = on_drive(r"Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")
POINTS = os.path.join(HERE, "logs", "r2", "r2_points.json")
WKT = ('PROJCS["Mars_EqC_local",GEOGCS["GCS_Mars_2000_Sphere",DATUM["D_Mars_2000_Sphere",'
       'SPHEROID["Mars_2000_Sphere_IAU_IAG",3396190.0,0.0]],PRIMEM["Reference_Meridian",0.0],'
       'UNIT["Degree",0.0174532925199433]],PROJECTION["Equidistant_Cylindrical"],PARAMETER["False_Easting",0.0],'
       'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",%.6f],PARAMETER["Standard_Parallel_1",%.6f],'
       'UNIT["Meter",1.0]]')


class LocalRenderer(Renderer):
    """The CTX renderer, its map re-projected to a local frame for each point."""

    def at(self, lon, lat):
        sr = arcpy.SpatialReference()
        sr.loadFromString(WKT % (((lon + 180) % 360) - 180, lat))
        self.m.spatialReference = sr
        self.sr = sr


def dem_window(ds, lon, lat, half_km, n):
    """n x n samples of the DEM over a square ground window (2 x half_km) centred on the point, metres."""
    gt = ds.GetGeoTransform()
    dlat = math.degrees(half_km * 1000.0 / R)
    dlon = dlat / max(math.cos(math.radians(lat)), 0.2)
    lo = ((lon + 180) % 360) - 180
    c0 = int(math.floor((lo - dlon - gt[0]) / gt[1])) - 2
    c1 = int(math.ceil((lo + dlon - gt[0]) / gt[1])) + 2
    r0 = max(int(math.floor((gt[3] - (lat + dlat)) / -gt[5])) - 2, 0)
    r1 = min(int(math.ceil((gt[3] - (lat - dlat)) / -gt[5])) + 2, ds.RasterYSize)
    W = ds.RasterXSize
    cols = np.arange(c0, c1) % W
    b = ds.GetRasterBand(1)
    runs, s = [], 0
    for k in range(1, len(cols) + 1):                       # contiguous runs, split at the 180 deg seam
        if k == len(cols) or cols[k] != cols[k - 1] + 1:
            runs.append(b.ReadAsArray(int(cols[s]), r0, k - s, r1 - r0).astype(np.float32)); s = k
    a = np.hstack(runs)
    yy = np.linspace(lat + dlat, lat - dlat, n); xx = np.linspace(lo - dlon, lo + dlon, n)
    rr = (gt[3] - yy) / -gt[5] - r0 - 0.5
    cc = (xx - gt[0]) / gt[1] - c0 - 0.5
    R_, C_ = np.meshgrid(rr, cc, indexing="ij")
    return map_coordinates(a, [R_, C_], order=1, mode="nearest")


def main():
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else on_drive(r"Mars Project\review_sheets\r2")
    os.makedirs(out, exist_ok=True)
    pts = json.load(open(POINTS, encoding="utf-8"))["points"]
    ds = gdal.Open(DEM)
    state = {}

    def renderer():
        if "r" not in state:
            state["r"] = LocalRenderer()
        return state["r"]

    sheets = {}
    for slot in pts:
        sheets.setdefault(slot.rstrip("0123456789"), []).append(slot)
    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    notes = {}
    for tag, slots in sheets.items():
        if "--only" in sys.argv and tag != sys.argv[sys.argv.index("--only") + 1]:
            continue
        png = os.path.join(out, "sheet_%s.png" % tag)
        if os.path.exists(png):
            continue
        fig, axes = plt.subplots(len(slots), 4, figsize=(10.0, 2.55 * len(slots)), dpi=130, squeeze=False)
        for i, slot in enumerate(slots):
            lon, lat = pts[slot]["lon"], pts[slot]["lat"]
            renderer().at(lon, lat)
            cy = R * math.radians(lat)
            key = "r2_" + slot
            far, e_far, far_ok = checked_far(renderer, key, 0.0, cy, 40)
            near, e_near, note = checked_near(renderer, key, 0.0, cy, 4000.0, far, e_far)
            if not far_ok:
                note = "CTX UNCHECKED: no two zoom levels agree"
            notes[slot] = note
            d40, d160 = dem_window(ds, lon, lat, 20, 400), dem_window(ds, lon, lat, 80, 400)
            panels = [(near, e_near, None, "%s   %.2f E, %.2f %s   8 km%s" % (slot, lon, abs(lat), "N" if lat >= 0
                       else "S", "" if note == "CTX" else "\n" + note), 4000.0, "ring"),
                      (far, e_far, None, "CTX, 40 km", 20000.0, "box"),
                      (shade(d40, z=3.0, cell=100.0), [-20000, 20000, cy - 20000, cy + 20000], "gray",
                       "DEM hillshade, 40 km", 20000.0, "box"),
                      (shade(d160, z=3.0, cell=400.0), [-80000, 80000, cy - 80000, cy + 80000], "gray",
                       "DEM hillshade, 160 km", 80000.0, "cross")]
            for j, (img, ext, cmap, title, h, mark) in enumerate(panels):
                ax = axes[i][j]
                ax.imshow(img, extent=ext, cmap=cmap, interpolation="nearest")
                if mark == "ring":
                    t = np.linspace(0, 2 * np.pi, 60)
                    ax.plot(1000 * np.cos(t), cy + 1000 * np.sin(t), color=LINE, lw=1.0)
                elif mark == "box":
                    ax.plot([-4000, 4000, 4000, -4000, -4000], [cy - 4000, cy - 4000, cy + 4000, cy + 4000, cy - 4000],
                            color=LINE, lw=0.9)
                else:
                    ax.plot([-12000, -4000], [cy, cy], color=LINE, lw=0.9); ax.plot([4000, 12000], [cy, cy], color=LINE, lw=0.9)
                    ax.plot([0, 0], [cy - 12000, cy - 4000], color=LINE, lw=0.9); ax.plot([0, 0], [cy + 4000, cy + 12000], color=LINE, lw=0.9)
                ax.set_xlim(-h, h); ax.set_ylim(cy - h, cy + h)
                ax.set_xticks([]); ax.set_yticks([])
                for sp in ax.spines.values():
                    sp.set_color(EDGE)
                ax.set_title(title, loc="left", color=INK if j == 0 else MUTED, fontsize=8)
        fig.tight_layout(h_pad=0.6, w_pad=0.3)
        fig.savefig(png, facecolor="white")
        plt.close(fig)
        print("sheet", tag, flush=True)
    idx = os.path.join(out, "index.json")
    old = json.load(open(idx, encoding="utf-8"))["ctx"] if os.path.exists(idx) else {}
    old.update(notes)
    json.dump({"points": POINTS, "ctx": old}, open(idx, "w", encoding="utf-8"), indent=1)
    print("sheets", len(sheets), "->", out)


if __name__ == "__main__":
    main()
