# -*- coding: utf-8 -*-
r"""The v3 labels: the v2 labels cut into pieces and screened, plus new polygons from reference data (KB §69.49).

The author's request, 2026-11-01: the seven-class deep-learning and SVM maps score far below the four-class ones;
more training polygons are wanted, "a few thousand samples", based on available data, and the large polygons split
into much smaller ones, "especially if the polygon risks covering multiple classes". Every row is screened by a rule
fixed in this file before it ran (the constants below), as the apron and fluvial rows of §69.8 were: screens, not
anyone's eye, and the record must say so. Landform_TrainingSamples_terrain and every v2 class are only read.

Two parts:
  pieces  every v2 polygon (Landform_TrainingSamples_v2_60_train / _test) larger than SPLIT_KM2 or wider than
          SPLIT_DEG is cut by a PIECE_DEG grid; each piece is kept if it passes its class's screen (below), so a
          piece that holds another class's ground is dropped. A piece keeps its parent's split, so no v2 held-out
          ground can become training. Smaller v2 polygons are kept whole and unscreened.
  new     polygons placed from reference data, every one checked against the same terrain cells, never touching
          any v2 polygon's ground (kept or dropped) or another new polygon, capped per 15° block for spread:
            1 Crater          Robbins & Hynek (2020) craters 6-120 km, a disc at the rim, one per diameter bin per
                              block, kept if the rim stands above the floor in the DEM
            2 hills           3 x 3 cells (9.6 km) of steep, high-relief ground outside crater rims and off
                              edifice, apron and landslide units
            3 lava tube       troughs inside the mapped extent of each named catena (IAU nomenclature): a
                              black top-hat of the DEM (4.2 km closing) >= 50 m deep, elongated >= 3, >= 6 km
                              long, outside crater rims. Lava-tube polygons of v2 are kept whole (not split): no
                              data can screen a piece of a pit chain
            4 Normal Ground   4 x 4 cells (12.8 km) of flat, smooth, crater-free ground off edifice, apron and
                              landslide units: volcanic and highland plains alike
            5 volcanic edifice  the summit of each named mons, tholus or patera on SIM 3292 edifice units, and
                              4 x 4 cells of sloping edifice-unit ground
            6 apron           4 x 4 cells of sloping, crater-free apron-unit ground (ANa, lAa, the aureole's Aa)
            7 fluvial channel 20 km strips, 2.4 km wide, along every second segment of the Alemanno & Orofino
                              (2017) valleys, kept if they sit on a floor (the §69.8 rule)
The split: new polygons go by the 15° block of their centroid (the 14 held-out blocks of
Landform_TrainingSamples_terrain_60_test), as every earlier set. So v3 adds held-out polygons too; the v2 held-out
set is untouched and stays the like-for-like score.

Terrain cells: global60_dem.tif (the G200 DEM) summarised once in 16 x 16 px cells (3.2 km): median and 90th
percentile slope (degrees, metric), 5th / 50th / 95th percentile height. Crater cover per cell from Robbins discs
drawn on an 800 m grid. SIM 3292 unit kinds per cell. Cached in C:\MarsScratch\label_v3 (internal disk).

Writes Landform_TrainingSamples_v3_proposals (every row, accepted or not, with its measures and reason),
Landform_TrainingSamples_v3, _v3_60_train and _v3_60_test (accepted rows only; MappedBy = this script), and with
--map the map "Labels v3" in the .aprx. Classes this script did not write are never replaced. Pro closed.

  python propose_v3_labels.py --dry-run     everything but the writes; logs\label_v3_dryrun.json
  python propose_v3_labels.py [--map]       logs\label_v3.json
"""
import os, sys, json, math, time, shutil, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import numpy as np
from scipy import ndimage
import arcpy
from osgeo import gdal, ogr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G

gdal.UseExceptions()
gdal.SetCacheMax(1 << 30)
DRY = "--dry-run" in sys.argv
MARKER = "propose_v3_labels.py"
STAMP = "agent rule §69.49"
LOG = os.path.join(HERE, "logs", "label_v3%s.json" % ("_dryrun" if DRY else ""))
APRX = on_drive(r"Mars Project\Mars Project.aprx")
MAP = "Labels v3"
CACHE = r"C:\MarsScratch\label_v3"
DEM60 = os.path.join(G.OUTDIR, "global60_dem.tif")
VALLEYS = on_drive(r"Mars Project\Reference\Alemanno2017_valleys\Giulia Valleys.shp")
V2 = {"train": "Landform_TrainingSamples_v2_60_train", "test": "Landform_TrainingSamples_v2_60_test"}
TEST4 = "Landform_TrainingSamples_terrain_60_test"
OUT = "Landform_TrainingSamples_v3_proposals"
V3 = ("Landform_TrainingSamples_v3", "Landform_TrainingSamples_v3_60_train", "Landform_TrainingSamples_v3_60_test")

CLASSES = {1: ("Crater", (255, 0, 0)), 2: ("steep/windy hills", (28, 119, 85)), 3: ("lava tube", (158, 25, 147)),
           4: ("Normal Ground", (81, 51, 13)), 5: ("volcanic edifice", (255, 170, 0)),
           6: ("apron", (115, 178, 255)), 7: ("fluvial channel", (0, 92, 230))}

# ---------------------------------------------------------------------------- the grid
R_KM = G.R_MARS / 1000.0
KM_DEG = math.pi * R_KM / 180.0
DP = math.degrees(200.0 / G.R_MARS)                  # degrees per 200 m pixel; columns are east longitude from 0°
NX, NY = 106694, 35565
LAT0 = math.degrees(3556500.0 / G.R_MARS)            # the G200 grid's top edge (60.00002°)
CELL, FINE = 16, 4                                   # 3.2 km cells; 800 m crater-mask pixels
NC, NR = NX // CELL, NY // CELL
DC, DF = DP * CELL, DP * FINE
NFC, NFR = NC * CELL // FINE, NR * CELL // FINE
BLOCK, LAT_MAX = 15.0, 60.0
GRID_NAMES = {"DRY", "R_KM", "KM_DEG", "DP", "NX", "NY", "LAT0", "CELL", "FINE", "NC", "NR", "DC", "DF", "NFC", "NFR"}
KIND = {"volc": 1, "ve": 2, "apron": 3, "slide": 4, "highland": 5, "other": 6}

# ---------------------------------------------------------------------------- the rules (fixed before the run)
SPLIT_KM2, SPLIT_DEG, PIECE_DEG, MIN_PIECE_KM2 = 1500.0, 1.0, 0.5, 25.0
P_CRATER_RIM = 0.5          # 1: piece share inside a Robbins rim (craters >= 4 km, 1.0 R)
P_HILLS_ROUGH = 8.0         # 2: piece median of the cells' 90th-percentile slope, degrees
P_NG_SLOPE, P_NG_CRATER = 2.0, 0.3   # 4: piece median slope; crater cover (>= 4 km, 1.3 R)
P_NG_CUT_KM, P_NG_CUT_R, P_NG_KEEP = 8.0, 1.2, 0.5   # 4: craters >= 8 km cut out at 1.2 R; half must remain
MASK_MAX_KM = 100.0         # crater cover and cut-outs count craters up to this size (a 51 km chip shows no larger rim)
P_VE_SLOPE, P_VE_SUMMIT = 1.0, 0.3   # 5: sloping, or within 0.3 of a named volcano's radius (calderas are flat)
P_APRON_SLOPE, P_APRON_ROUGH = 0.7, 15.0
P_APRON_ROUGH_LAT = 30.0    # 6: the roughness cap (mesa scarps) only for the mid-latitude debris aprons, not the
                            # ridged Olympus aureole or the Tharsis fans (read on the first sheets, KB §69.49)
P_CRATER10 = 0.3            # 5, 6: crater cover (>= 10 km, 1.3 R) below this
FLOOR_M, FLANK_KM, VOLC_MAX = 20.0, 4.8, 0.5        # 7: the §69.8 floor rule, per piece
OFF_UNITS = 0.5             # 2, 4: edifice + apron + landslide unit share below this

N_CRATER_BINS = (6, 12, 25, 50, 120)                # 1: one crater per bin per block
CRATER_RELIEF_M, CRATER_RELIEF_PER_KM = 50.0, 5.0   # 1: rim median - floor median >= max(50, 5 D) m
HILL_K, HILL_SP90, HILL_MIN, HILL_RELIEF, HILL_CAP = 3, 10.0, 7, 1000.0, 4
NG_K, NG_SMED, NG_SP90, NG_RELIEF, NG_CAP = 4, 1.0, 3.0, 150.0, 5
VE_K, VE_SMED, VE_CAP, VE_SUMMIT_KM, VE_SUMMIT_FRAC = 4, 1.0, 12, 25.0, 0.5
AP_K, AP_SMED, AP_SP90, AP_MIN, AP_CAP = 4, 0.7, 15.0, 14, 12
CAT_PAD_DEG, CAT_WIN, CAT_DEPTH_M, CAT_MIN_PX, CAT_ELONG, CAT_LEN_KM, CAT_CAP, CAT_DILATE = 0.2, 21, 50.0, 20, 3.0, 6.0, 15, 2
FLU_SEG_KM, FLU_HALF_KM, FLU_CAP, FLU_PER_VALLEY = 20.0, 1.2, 6, 2
SEED = 69


def say(*a):
    print("[%s]" % time.strftime("%H:%M:%S"), *a)


def km2(g):
    return g.getArea("GEODESIC", "SQUAREKILOMETERS")


def block_of_xy(x, y):
    return "%d_%d" % (math.floor(x / BLOCK), math.floor(y / BLOCK))


def mem_vector():
    if int(gdal.VersionInfo()) >= 3110000:
        return gdal.GetDriverByName("MEM").Create("", 0, 0, 0, gdal.GDT_Unknown)
    return ogr.GetDriverByName("Memory").CreateDataSource("")


def plain(g):
    return g.densify("ANGLE", 1.0, 0.01) if getattr(g, "hasCurves", False) else g


# ---------------------------------------------------------------------------- terrain cells
def terrain_cells():
    path = os.path.join(CACHE, "terrain_cells_3200m.npz")
    if os.path.exists(path):
        return dict(np.load(path))
    os.makedirs(CACHE, exist_ok=True)
    ds = gdal.Open(DEM60)
    b = ds.GetRasterBand(1)
    assert ds.GetGeoTransform() == (-10669400.0, 200.0, 0.0, 3556500.0, 0.0, -200.0), ds.GetGeoTransform()
    nod = b.GetNoDataValue()
    out = {k: np.full((NR, NC), np.nan, np.float32) for k in ("smed", "sp90", "z05", "z50", "z95")}
    W, k = NC * CELL, CELL * CELL
    t = time.time()
    for i0 in range(0, NR, 32):
        i1 = min(NR, i0 + 32)
        r0, r1 = i0 * CELL, i1 * CELL
        a0, a1 = max(0, r0 - 1), min(NY, r1 + 1)
        z = b.ReadAsArray(0, a0, W, a1 - a0).astype(np.float32)
        z[z == nod] = np.nan
        lat = LAT0 - (np.arange(a0, a1) + 0.5) * DP
        gy, gx = np.gradient(z)
        s = np.degrees(np.arctan(np.hypot(gx / (200.0 * np.cos(np.radians(lat)))[:, None], gy / 200.0)))
        del gx, gy
        z, s = z[r0 - a0:r1 - a0], s[r0 - a0:r1 - a0]
        n = i1 - i0
        cells = lambda a: np.sort(a.reshape(n, CELL, NC, CELL).transpose(0, 2, 1, 3).reshape(n, NC, k), axis=-1)
        zs = cells(z)
        out["z05"][i0:i1], out["z50"][i0:i1], out["z95"][i0:i1] = (zs[..., int(.05 * (k - 1))], zs[..., k // 2],
                                                                   zs[..., int(.95 * (k - 1))])
        bad = np.isnan(zs[..., -1])
        del zs
        ss = cells(s)
        out["smed"][i0:i1], out["sp90"][i0:i1] = ss[..., k // 2], ss[..., int(.9 * (k - 1))]
        bad |= np.isnan(ss[..., -1])
        for key in out:
            out[key][i0:i1][bad] = np.nan
        say("  terrain cells rows %d-%d of %d (%.0f s)" % (i0, i1, NR, time.time() - t))
    np.savez(path, **out)
    return out


def crater_masks(rob):
    """Per 800 m pixel, the largest Robbins diameter (km, capped 255) whose disc covers it: at 1.0 R (every crater,
    the rim test) and 1.3 R (3 to MASK_MAX_KM km, the exclusion: a larger basin's floor is plains at chip scale)."""
    path = os.path.join(CACHE, "crater_masks_800m.npz")
    if os.path.exists(path):
        d = np.load(path)
        return d["m10"], d["m13"]
    lon, lat, dk = rob["lon"] % 360.0, rob["lat"], rob["d"]
    out = []
    t = time.time()
    for fac, dmin, dmax in ((1.0, 1.0, 1e9), (1.3, 3.0, MASK_MAX_KM)):
        m = np.zeros((NFR, NFC), np.uint8)
        sel = np.nonzero((dk >= dmin) & (dk <= dmax) & (np.abs(lat) < LAT_MAX + 3))[0]
        for i in sel[np.argsort(dk[sel])]:                     # largest last, so np.maximum keeps the largest
            code = min(255, int(math.ceil(dk[i])))
            rr = fac * dk[i] / 2.0 / KM_DEG / DF
            rc = rr / max(math.cos(math.radians(lat[i])), 0.2)
            yc, xc = (LAT0 - lat[i]) / DF, lon[i] / DF
            rows = np.arange(max(0, int(yc - rr)), min(NFR, int(yc + rr) + 2))
            if rows.size == 0:
                continue
            cols = np.arange(int(xc - rc), int(xc + rc) + 2)
            inside = ((rows + .5 - yc) / rr)[:, None] ** 2 + ((cols + .5 - xc) / rc)[None, :] ** 2 <= 1.0
            if not inside.any():
                r, c = int(yc), int(xc)
                if 0 <= r < NFR:
                    m[r, c % NFC] = max(m[r, c % NFC], code)
                continue
            ix = np.ix_(rows, cols % NFC)
            m[ix] = np.where(inside, np.maximum(m[ix], code), m[ix])
        out.append(m)
        say("  crater mask %.1f R: %d craters (%.0f s)" % (fac, sel.size, time.time() - t))
    np.savez(path, m10=out[0], m13=out[1])
    return out


def cover(mask, dmin):
    return (mask >= dmin).reshape(NR, FINE, NC, FINE).mean(axis=(1, 3)).astype(np.float32)


# ---------------------------------------------------------------------------- rasterising
def raster_idx(geom, step, nrows, ncols, all_touched=False):
    """(rows, cols) of the global lon/lat grid of `step` degrees (columns east from 0°, rows from LAT0) whose
    centres fall in geom (or that it touches); the window is built in the polygon's own longitude frame."""
    e = geom.extent
    c0, c1 = int(math.floor(e.XMin / step)), int(math.ceil(e.XMax / step))
    r0 = max(0, int(math.floor((LAT0 - e.YMax) / step)))
    r1 = min(nrows, int(math.ceil((LAT0 - e.YMin) / step)))
    if c1 <= c0 or r1 <= r0:
        return np.zeros(0, int), np.zeros(0, int)
    mem = gdal.GetDriverByName("MEM").Create("", c1 - c0, r1 - r0, 1, gdal.GDT_Byte)
    mem.SetGeoTransform((c0 * step, step, 0, LAT0 - r0 * step, 0, -step))
    src = mem_vector()
    lyr = src.CreateLayer("p")
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(plain(geom).WKT))
    lyr.CreateFeature(f)
    gdal.RasterizeLayer(mem, [1], lyr, burn_values=[1], options=["ALL_TOUCHED=TRUE"] if all_touched else [])
    rr, cc = np.nonzero(mem.ReadAsArray())
    if rr.size == 0:
        c = geom.centroid
        r, cl = int((LAT0 - c.Y) / step), int(math.floor(c.X / step))
        if not 0 <= r < nrows:
            return np.zeros(0, int), np.zeros(0, int)
        return np.array([r]), np.array([cl % ncols])
    return rr + r0, (cc + c0) % ncols


def cells_of(geom, all_touched=False):
    return raster_idx(geom, DC, NR, NC, all_touched)


class Dem:
    def __init__(self):
        self.ds = gdal.Open(DEM60)
        self.b = self.ds.GetRasterBand(1)
        self.nod = self.b.GetNoDataValue()

    def window(self, r0, r1, c0, c1):
        cols = np.arange(c0, c1) % NX
        parts, s = [], 0
        for i in range(1, cols.size + 1):                      # contiguous runs, so a window over 0°E reads twice
            if i == cols.size or cols[i] != cols[i - 1] + 1:
                parts.append(self.b.ReadAsArray(int(cols[s]), r0, i - s, r1 - r0)); s = i
        z = np.hstack(parts).astype(np.float64)
        z[z == self.nod] = np.nan
        return z

    def values(self, geom):
        rr, cc = raster_idx(geom, DP, NY, NX)
        if rr.size == 0:
            return np.zeros(0)
        r0, r1 = rr.min(), rr.max() + 1
        # columns in the polygon's frame: recover a contiguous range from the wrapped indices
        e = geom.extent
        c0 = int(math.floor(e.XMin / DP))
        z = self.window(r0, r1, c0, int(math.ceil(e.XMax / DP)) + 1)
        v = z[rr - r0, (cc - c0) % NX]
        return v[np.isfinite(v)]

    def crater_relief(self, lon, lat, dkm):
        """Median height of the rim annulus (0.85-1.15 R) minus that of the floor (< 0.5 R), m."""
        R = dkm / 2.0
        ry = 1.2 * R / 0.2
        rx = ry / max(math.cos(math.radians(lat)), 0.2)
        yc, xc = (LAT0 - lat) / DP, (lon % 360.0) / DP
        r0, r1 = max(0, int(yc - ry)), min(NY, int(yc + ry) + 2)
        c0, c1 = int(xc - rx), int(xc + rx) + 2
        z = self.window(r0, r1, c0, c1)
        dy = (np.arange(r0, r1) + .5 - yc) * 0.2
        dx = (np.arange(c0, c1) + .5 - xc) * 0.2 * math.cos(math.radians(lat))
        r = np.hypot(dy[:, None], dx[None, :]) / R
        fl, rim = z[(r < 0.5) & np.isfinite(z)], z[(r > 0.85) & (r < 1.15) & np.isfinite(z)]
        if fl.size < 4 or rim.size < 8:
            return None
        return float(np.median(rim) - np.median(fl))


# ---------------------------------------------------------------------------- geometry helpers
def rect(x0, y0, x1, y1, sr):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1), arcpy.Point(x1, y1),
                                      arcpy.Point(x1, y0), arcpy.Point(x0, y0)]), sr)


_EXT = {}
def clip60(g):
    sr = g.spatialReference
    if sr.name not in _EXT:
        _EXT[sr.name] = rect(-180, -LAT_MAX, 180, LAT_MAX, sr)
    x = g.intersect(_EXT[sr.name], 4)
    return x if x is not None and x.area > 0 else None


def disc(lon, lat, r_km, sr, n=48):
    d, p, l = r_km / R_KM, math.radians(lat), math.radians(lon)
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    p2 = np.arcsin(np.sin(p) * np.cos(d) + np.cos(p) * np.sin(d) * np.cos(t))
    l2 = l + np.arctan2(np.sin(t) * np.sin(d) * np.cos(p), np.cos(d) - np.sin(p) * np.sin(p2))
    x, y = np.degrees(l2), np.degrees(p2)
    if np.abs(x).max() >= 180 or np.abs(y).max() >= LAT_MAX:
        return None
    pts = [arcpy.Point(a, b) for a, b in zip(x, y)]
    return arcpy.Polygon(arcpy.Array(pts + [pts[0]]), sr)


_LSR = {}
def local_sr(lon, lat):
    """An equidistant cylindrical frame true at this latitude, for metric buffers (cached per degree)."""
    k = (round(lon), round(lat))
    if k not in _LSR:
        wkt = ('PROJCS["local",GEOGCS["GCS_Mars_2000_Sphere",DATUM["D_Mars_2000_Sphere",SPHEROID['
               '"Mars_2000_Sphere_IAU_IAG",3396190.0,0.0]],PRIMEM["Reference_Meridian",0.0],UNIT["Degree",'
               '0.0174532925199433]],PROJECTION["Equidistant_Cylindrical"],PARAMETER["False_Easting",0.0],'
               'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",%d],PARAMETER["Standard_Parallel_1",'
               '%d],UNIT["Meter",1.0]]' % k)
        s = arcpy.SpatialReference()
        s.loadFromString(wkt)
        _LSR[k] = s
    return _LSR[k]


def grid_pieces(g, sr):
    e = g.extent
    out = []
    for gx in np.arange(math.floor(e.XMin / PIECE_DEG) * PIECE_DEG, e.XMax, PIECE_DEG):
        for gy in np.arange(math.floor(e.YMin / PIECE_DEG) * PIECE_DEG, e.YMax, PIECE_DEG):
            c = rect(gx, gy, gx + PIECE_DEG, gy + PIECE_DEG, sr)
            if c.disjoint(g):
                continue
            x = g.intersect(c, 4)
            if x is not None and x.area > 0 and km2(x) >= MIN_PIECE_KM2:
                out.append(x)
    return out


def square(i, j, k, sr):
    e0, e1 = j * DC, (j + k) * DC
    if e0 < 180 < e1 or j + k > NC:
        return None
    x0 = e0 - 360 if e0 >= 180 else e0
    y1, y0 = LAT0 - i * DC, LAT0 - (i + k) * DC
    if y0 < -LAT_MAX or y1 > LAT_MAX + 0.01:
        return None
    return clip60(rect(x0, y0, x0 + k * DC, y1, sr))


# ---------------------------------------------------------------------------- inputs
def read_v2():
    rows = []
    for split, fc in V2.items():
        flds = ["OID@", "Classvalue", "Subtype", "OldOID", "Block", "SHAPE@"]
        with arcpy.da.SearchCursor(os.path.join(GDB, fc), flds) as c:
            for oid, cv, sub, old, blk, g in c:
                rows.append(dict(v2oid=oid, split=split, cls=int(cv), sub=sub or "", old=old, block=blk,
                                 geom=plain(g)))
    sr = arcpy.Describe(os.path.join(GDB, V2["train"])).spatialReference
    with arcpy.da.SearchCursor(os.path.join(GDB, TEST4), ["Block"]) as c:
        held = sorted(set(r[0] for r in c))
    return sr, rows, held


def read_robbins():
    lon, lat, d, ids = [], [], [], []
    with arcpy.da.SearchCursor(os.path.join(GDB, "Ref_Craters_Robbins2020"), ["Lon", "Lat", "DiamKm", "CraterID"]) as c:
        for a, b, dk, i in c:
            lon.append(a); lat.append(b); d.append(dk); ids.append(i)
    lon = np.array(lon)
    lon = np.where(lon > 180, lon - 360, lon)
    return dict(lon=lon, lat=np.array(lat), d=np.array(d), id=np.array(ids))


def unit_kind(u, grp, x):
    if grp in ("v", "vf"):
        return "volc"
    if grp == "ve":
        return "ve"
    if u in ("ANa", "lAa") or (u == "Aa" and x < -100):
        return "apron"
    if u == "Aa":
        return "slide"                                        # Valles Marineris landslides: not an ice apron
    if (grp or "")[:1] == "h":                                # h, hm, hu and the highland edifice group
        return "highland"
    return "other"


def unit_cells(sr):
    path = os.path.join(CACHE, "unit_kinds_3200m.npy")
    if os.path.exists(path):
        return np.load(path)
    src = mem_vector()
    lyr = src.CreateLayer("u", geom_type=ogr.wkbMultiPolygon)
    lyr.CreateField(ogr.FieldDefn("k", ogr.OFTInteger))
    with arcpy.da.SearchCursor(os.path.join(GDB, "Ref_SIM3292_GeologicUnits"), ["Unit", "UnitGroup", "SHAPE@"]) as c:
        for u, grp, g in c:
            g = g.projectAs(sr)
            f = ogr.Feature(lyr.GetLayerDefn())
            f.SetField("k", KIND[unit_kind(u, grp, g.centroid.X)])
            f.SetGeometry(ogr.CreateGeometryFromWkt(g.WKT))
            lyr.CreateFeature(f)
    out = np.zeros((NR, NC), np.uint8)
    for x0 in (0.0, -360.0):                                  # east of 0° and west of it, onto one 0-360 grid
        mem = gdal.GetDriverByName("MEM").Create("", NC, NR, 1, gdal.GDT_Byte)
        mem.SetGeoTransform((x0, DC, 0, LAT0, 0, -DC))
        gdal.RasterizeLayer(mem, [1], lyr, options=["ATTRIBUTE=k"])
        a = mem.ReadAsArray()
        out = np.where(out > 0, out, a)
    np.save(path, out)
    return out


def read_named(sr):
    out = []
    for fc in arcpy.ListFeatureClasses("MARS_nomenclature*") or []:
        if "crater" in fc.lower():
            continue
        with arcpy.da.SearchCursor(fc, ["clean_name", "type", "diameter", "SHAPE@"]) as c:
            for nm, ty, dia, g in c:
                t = (ty or "").split(",")[0].strip()
                if g is None or t not in ("Mons", "Tholus", "Patera") or not dia:
                    continue
                p = g.projectAs(sr).centroid
                out.append(dict(name=nm, type=t, diam=float(dia), x=p.X, y=p.Y))
    return out


def read_catenae():
    """The named catenae (pit chains) and their mapped extents, east longitude 0-360."""
    out = []
    for fc in arcpy.ListFeatureClasses("MARS_nomenclature*") or []:
        with arcpy.da.SearchCursor(fc, ["clean_name", "type", "min_lon", "max_lon", "min_lat", "max_lat"]) as c:
            for nm, ty, x0, x1, y0, y1 in c:
                if (ty or "").startswith("Catena") and None not in (x0, x1, y0, y1):
                    out.append(dict(name=nm, box=(x0 % 360.0, x1 % 360.0, y0, y1)))
    return out


# ---------------------------------------------------------------------------- measures
class Ctx:
    pass


def measures(ctx, g):
    rr, cc = cells_of(g)
    if rr.size == 0:
        return None
    kinds = np.bincount(ctx.kind[rr, cc], minlength=7) / rr.size
    f = lambda a, fn=np.nanmedian: float(fn(a[rr, cc])) if np.isfinite(a[rr, cc]).any() else float("nan")
    return dict(cells=int(rr.size), slope=f(ctx.T["smed"]), rough=f(ctx.T["sp90"]),
                relief=float(np.nanmax(ctx.T["z95"][rr, cc]) - np.nanmin(ctx.T["z05"][rr, cc]))
                if np.isfinite(ctx.T["z95"][rr, cc]).any() else float("nan"),
                rim4=float(ctx.rim4[rr, cc].mean()), cov4=float(ctx.cov4[rr, cc].mean()),
                cov10=float(ctx.cov10[rr, cc].mean()),
                volc=float(kinds[1]), ve=float(kinds[2]), apron=float(kinds[3]), slide=float(kinds[4]),
                highland=float(kinds[5]))


def ev_text(m):
    if m is None:
        return "no cells"
    s = "slope %.1f° p90 %.1f°, relief %.0f m; in rims %.2f, craters>=4km %.2f >=10km %.2f; units volc %.2f ve %.2f " \
        "apron %.2f slide %.2f highland %.2f" % (m["slope"], m["rough"], m["relief"], m["rim4"], m["cov4"], m["cov10"],
                                                 m["volc"], m["ve"], m["apron"], m["slide"], m["highland"])
    if m.get("floor") is not None:
        s += "; floor %.0f m below flanks" % m["floor"]
    if m.get("crater_relief") is not None:
        s += "; rim above floor %.0f m" % m["crater_relief"]
    return s[:254]


def floor_depth(ctx, strip, sr):
    c = strip.centroid
    lsr = local_sr(c.X, c.Y)
    p = strip.projectAs(lsr)
    ring = p.buffer(FLANK_KM * 1000.0).difference(p).projectAs(sr)
    a, b = ctx.dem.values(strip), ctx.dem.values(ring)
    if a.size < 3 or b.size < 3:
        return None
    return float(np.median(b) - np.median(a))


def named_volcano(ctx, x, y):
    """The named volcano whose radius holds (x, y), as (name, distance / radius), or None."""
    best = None
    for v in ctx.volcanoes:
        if abs(v["y"] - y) > 6 or abs(v["x"] - x) > 12:
            continue
        dx = (x - v["x"]) * KM_DEG * math.cos(math.radians(y))
        f = math.hypot(dx, (y - v["y"]) * KM_DEG) / (v["diam"] / 2.0)
        if f <= 1.0 and (best is None or f < best[1]):
            best = (v["name"], f)
    return best


# ---------------------------------------------------------------------------- part 1: the v2 polygons in pieces
def screen_piece(ctx, cls, g, m, sr):
    """(keep, why, geometry) for one piece of a v2 polygon of class cls."""
    if m is None:
        return False, "no terrain cells", g
    off = m["ve"] + m["apron"] + m["slide"]
    if cls == 1:
        ok = m["rim4"] >= P_CRATER_RIM
        return ok, "inside Robbins rims %.2f (>= %.2f)" % (m["rim4"], P_CRATER_RIM), g
    if cls == 2:
        ok = m["rough"] >= P_HILLS_ROUGH and off < OFF_UNITS
        return ok, "slope p90 %.1f° (>= %.0f), edifice/apron/slide units %.2f" % (m["rough"], P_HILLS_ROUGH, off), g
    if cls == 4:
        if not (m["slope"] <= P_NG_SLOPE and m["cov4"] <= P_NG_CRATER and off < OFF_UNITS):
            return False, "slope %.1f° (<= %.0f), craters %.2f (<= %.1f), edifice/apron/slide %.2f" % (
                m["slope"], P_NG_SLOPE, m["cov4"], P_NG_CRATER, off), g
        a0 = km2(g)
        e, rob = g.extent, ctx.rob
        pad = 1.0
        sel = np.nonzero((rob["d"] >= P_NG_CUT_KM) & (rob["d"] <= MASK_MAX_KM) & (rob["lon"] >= e.XMin - pad) & (rob["lon"] <= e.XMax + pad) &
                         (rob["lat"] >= e.YMin - pad) & (rob["lat"] <= e.YMax + pad))[0]
        cut = 0
        for i in sel:
            d = disc(rob["lon"][i], rob["lat"][i], P_NG_CUT_R * rob["d"][i] / 2.0, sr)
            if d is not None and not d.disjoint(g):
                g = g.difference(d); cut += 1
                if g is None or g.area <= 0:
                    return False, "nothing left after cutting %d craters" % cut, None
        left = km2(g) / a0
        return left >= P_NG_KEEP and km2(g) >= MIN_PIECE_KM2, \
            "slope %.1f°, craters %.2f; %d craters >= %.0f km cut out, %.0f%% left" % (
                m["slope"], m["cov4"], cut, P_NG_CUT_KM, 100 * left), g
    if cls == 5:
        c = g.centroid
        nv = named_volcano(ctx, c.X, c.Y)
        on = m["ve"] >= 0.5 or nv is not None
        slope_ok = m["slope"] >= P_VE_SLOPE or (nv is not None and nv[1] <= P_VE_SUMMIT)
        ok = on and slope_ok and m["cov10"] <= P_CRATER10
        return ok, "edifice units %.2f%s, slope %.1f° (>= %.0f), craters>=10km %.2f" % (
            m["ve"], ", in %s at %.2f R" % nv if nv else "", m["slope"], P_VE_SLOPE, m["cov10"]), g
    if cls == 6:
        rough_ok = m["rough"] <= P_APRON_ROUGH or abs(g.centroid.Y) < P_APRON_ROUGH_LAT
        ok = (m["apron"] >= 0.5 and m["slope"] >= P_APRON_SLOPE and rough_ok and
              m["cov10"] <= P_CRATER10)
        return ok, "apron units %.2f, slope %.1f° (>= %.1f) p90 %.1f° (<= %.0f above 30°), craters>=10km %.2f" % (
            m["apron"], m["slope"], P_APRON_SLOPE, m["rough"], P_APRON_ROUGH, m["cov10"]), g
    if cls == 7:
        d = floor_depth(ctx, g, sr)
        m["floor"] = d
        ok = d is not None and d >= FLOOR_M and m["volc"] < VOLC_MAX
        return ok, "floor %s m below flanks (>= %.0f), volcanic plains %.2f" % (
            "?" if d is None else "%.0f" % d, FLOOR_M, m["volc"]), g
    raise ValueError(cls)


def pieces_of_v2(ctx, v2, sr):
    rows = []
    t = time.time()
    for n, r in enumerate(v2):
        g, e = r["geom"], r["geom"].extent
        base = dict(cls=r["cls"], split=r["split"], block=r["block"], v2oid=r["v2oid"], old=r["old"], sub=r["sub"])
        if r["cls"] == 3 or (km2(g) <= SPLIT_KM2 and max(e.XMax - e.XMin, e.YMax - e.YMin) <= SPLIT_DEG):
            rows.append(dict(base, geom=g, action="keep", ok=True, why="v2 polygon kept whole (%.0f km²)" % km2(g),
                             m=measures(ctx, g), src="v2 %s OID %d" % (r["split"], r["v2oid"])))
            continue
        ps = grid_pieces(g, sr)
        for k, p in enumerate(ps):
            m = measures(ctx, p)
            ok, why, pg = screen_piece(ctx, r["cls"], p, m, sr)
            rows.append(dict(base, geom=pg if pg is not None else p, action="piece", ok=bool(ok), why=why, m=m,
                             src="v2 %s OID %d, piece %d of %d" % (r["split"], r["v2oid"], k + 1, len(ps))))
        if (n + 1) % 100 == 0:
            say("  v2 polygons %d of %d, %d rows (%.0f s)" % (n + 1, len(v2), len(rows), time.time() - t))
    return rows


# ---------------------------------------------------------------------------- part 2: new polygons
class Occupancy:
    def __init__(self):
        self.a = np.zeros((NR, NC), bool)

    def free(self, rr, cc):
        if rr.size == 0:
            return False
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if self.a[np.clip(rr + dr, 0, NR - 1), (cc + dc) % NC].any():
                    return False
        return True

    def mark(self, rr, cc):
        self.a[rr, cc] = True


def block_of_cell(i, j, k=1):
    lat = LAT0 - (i + k / 2.0) * DC
    lon = (j + k / 2.0) * DC
    lon = lon - 360 if lon >= 180 else lon
    return block_of_xy(lon, lat)


def window_count(mask, k):
    s = np.zeros((mask.shape[0] + 1, mask.shape[1] + 1), np.int32)
    s[1:, 1:] = np.cumsum(np.cumsum(mask, 0, dtype=np.int32), 1)
    return s[k:, k:] - s[:-k, k:] - s[k:, :-k] + s[:-k, :-k]


def anchors_by_block(ok, k, rng, per_block=300):
    """Up to per_block random anchors (top-left cells of an eligible k x k window) per 15° block."""
    ii, jj = np.nonzero(ok)
    if ii.size == 0:
        return {}
    o = rng.permutation(ii.size)
    ii, jj = ii[o], jj[o]
    lat = LAT0 - (ii + k / 2.0) * DC
    lon = (jj + k / 2.0) * DC
    lon = np.where(lon >= 180, lon - 360, lon)
    bid = (np.floor(lon / BLOCK).astype(int) + 100) * 1000 + np.floor(lat / BLOCK).astype(int) + 100
    out = collections.defaultdict(list)
    for a, b, c in zip(ii, jj, bid):
        lst = out[c]
        if len(lst) < per_block:
            lst.append((int(a), int(b)))
    return out


def new_squares(ctx, cls, ok_cells, k, need, cap, sr, rng, what, extra=None):
    ok = window_count(ok_cells, k) >= need
    rows = []
    for bid, lst in anchors_by_block(ok, k, rng).items():
        got = 0
        for i, j in lst:
            if got >= cap:
                break
            if j == 0 or j + k >= NC:
                continue
            rr, cc = np.mgrid[i:i + k, j:j + k]
            rr, cc = rr.ravel(), cc.ravel()
            if not ctx.occ.free(rr, cc):
                continue
            g = square(i, j, k, sr)
            if g is None:
                continue
            m = measures(ctx, g)
            if extra is not None and not extra(m):
                continue
            ctx.occ.mark(rr, cc)
            got += 1
            c = g.centroid
            rows.append(dict(cls=cls, geom=g, action="new", ok=True, m=m, why=what, sub="",
                             src="cells %dx%d at row %d col %d" % (k, k, i, j), block=block_of_xy(c.X, c.Y)))
    return rows


def place(ctx, g, rows, **kw):
    """Add a candidate polygon if its ground is free; mark it."""
    if g is None:
        return False
    g = clip60(g)
    if g is None:
        return False
    rr, cc = cells_of(g, all_touched=True)
    if not ctx.occ.free(rr, cc):
        return False
    ctx.occ.mark(rr, cc)
    c = g.centroid
    rows.append(dict(kw, geom=g, action="new", block=block_of_xy(c.X, c.Y)))
    return True


def new_craters(ctx, sr, rng):
    rob = ctx.rob
    ok = (rob["d"] >= N_CRATER_BINS[0]) & (rob["d"] < N_CRATER_BINS[-1]) & \
         (np.abs(rob["lat"]) + rob["d"] / 2 / KM_DEG < LAT_MAX - 0.05)
    idx = np.nonzero(ok)[0]
    idx = idx[rng.permutation(idx.size)]
    groups = collections.defaultdict(list)
    for i in idx:
        b = np.searchsorted(N_CRATER_BINS, rob["d"][i], side="right") - 1
        groups[(block_of_xy(rob["lon"][i], rob["lat"][i]), b)].append(i)
    rows, tried = [], 0
    for key, lst in groups.items():
        for i in lst[:8]:                                 # up to 8 tries for this block and diameter bin
            lon, lat, dk = rob["lon"][i], rob["lat"][i], rob["d"][i]
            g = disc(lon, lat, dk / 2.0, sr)
            if g is None:
                continue
            rr, cc = cells_of(g, all_touched=True)
            if not ctx.occ.free(rr, cc):
                continue
            tried += 1
            rel = ctx.dem.crater_relief(lon, lat, dk)
            need = max(CRATER_RELIEF_M, CRATER_RELIEF_PER_KM * dk)
            if rel is None or rel < need:
                continue
            m = measures(ctx, g)
            m["crater_relief"] = rel
            if place(ctx, g, rows, cls=1, ok=True, m=m, sub="", src="Robbins %s, D %.1f km" % (rob["id"][i], dk),
                     why="Robbins crater %.1f km, a disc at the rim; rim %.0f m above the floor (>= %.0f)" % (
                         dk, rel, need)):
                break
    say("  craters: %d placed of %d measured" % (len(rows), tried))
    return rows


def new_volcano_summits(ctx, sr):
    rows = []
    for v in ctx.volcanoes:
        r = min(VE_SUMMIT_KM, VE_SUMMIT_FRAC * v["diam"] / 2.0)
        g = disc(v["x"], v["y"], r, sr)
        if g is None:
            continue
        m = measures(ctx, g)
        if m is None or m["ve"] < 0.5:
            continue
        place(ctx, g, rows, cls=5, ok=True, m=m, sub=v["type"].lower(), src="IAU %s %s" % (v["type"], v["name"]),
              why="summit of %s (%s, %.0f km), %.0f km disc on edifice units %.2f" % (
                  v["name"], v["type"], v["diam"], r, m["ve"]))
    return rows


def new_catena_troughs(ctx, sr, m10):
    rows, found = [], 0
    for cat in ctx.catenae:
        x0, x1, y0, y1 = cat["box"]
        if x1 < x0:
            x1 += 360.0
        y0, y1 = max(y0 - CAT_PAD_DEG, -LAT_MAX + 0.1), min(y1 + CAT_PAD_DEG, LAT_MAX - 0.1)
        if y1 <= y0:
            continue
        r0, r1 = int((LAT0 - y1) / DP), int((LAT0 - y0) / DP) + 1
        c0, c1 = int(math.floor((x0 - CAT_PAD_DEG) / DP)), int(math.ceil((x1 + CAT_PAD_DEG) / DP)) + 1
        z = ctx.dem.window(r0, r1, c0, c1)
        z = np.where(np.isfinite(z), z, np.nanmedian(z))
        th = ndimage.grey_closing(z, size=(CAT_WIN, CAT_WIN)) - z
        lab, n = ndimage.label(th >= CAT_DEPTH_M)
        if n == 0:
            continue
        objs = ndimage.find_objects(lab)
        sizes = np.bincount(lab.ravel())[1:]
        cand = []
        for k in np.nonzero(sizes >= CAT_MIN_PX)[0]:
            sl = objs[k]
            yy, xx = np.nonzero(lab[sl] == k + 1)
            lat_c = LAT0 - (r0 + sl[0].start + yy.mean() + 0.5) * DP
            X, Y = xx * 0.2 * math.cos(math.radians(lat_c)), yy * 0.2
            ev = np.sort(np.linalg.eigvalsh(np.cov(np.c_[X, Y].T)))
            elong = math.sqrt(ev[1] / max(ev[0], 1e-6))
            length = math.sqrt(12.0 * ev[1])                   # a uniform line of length L has sd L / sqrt(12)
            lon_c = ((c0 + sl[1].start + xx.mean() + 0.5) * DP) % 360.0
            inrim = m10[min(NFR - 1, int((LAT0 - lat_c) / DF)), int(lon_c / DF) % NFC] >= 3
            if elong >= CAT_ELONG and length >= CAT_LEN_KM and not inrim:
                cand.append((int(sizes[k]), k, elong, length, float(th[sl][lab[sl] == k + 1].max())))
        found += len(cand)
        got = 0
        for size, k, elong, length, depth in sorted(cand, reverse=True):
            if got >= CAT_CAP:
                break
            sl = objs[k]
            a0, a1 = max(0, sl[0].start - CAT_DILATE - 1), min(lab.shape[0], sl[0].stop + CAT_DILATE + 1)
            b0, b1 = max(0, sl[1].start - CAT_DILATE - 1), min(lab.shape[1], sl[1].stop + CAT_DILATE + 1)
            m = ndimage.binary_dilation(lab[a0:a1, b0:b1] == k + 1, iterations=CAT_DILATE).astype(np.uint8)
            ox = (c0 + b0) * DP
            ox = ox - 360.0 if ox >= 180.0 else ox
            mem = gdal.GetDriverByName("MEM").Create("", m.shape[1], m.shape[0], 1, gdal.GDT_Byte)
            mem.SetGeoTransform((ox, DP, 0, LAT0 - (r0 + a0) * DP, 0, -DP))
            mem.GetRasterBand(1).WriteArray(m)
            vec = mem_vector()
            lyr = vec.CreateLayer("t", geom_type=ogr.wkbPolygon)
            lyr.CreateField(ogr.FieldDefn("v", ogr.OFTInteger))
            gdal.Polygonize(mem.GetRasterBand(1), mem.GetRasterBand(1), lyr, 0)
            geom = ogr.Geometry(ogr.wkbMultiPolygon)
            for f in lyr:
                geom.AddGeometry(f.GetGeometryRef().Clone())
            g = arcpy.FromWKT(geom.ExportToWkt(), sr)
            m_ = measures(ctx, g)
            if place(ctx, g, rows, cls=3, ok=True, m=m_, sub="pit chain", src="IAU %s, trough %d" % (cat["name"], k + 1),
                     why="trough in the mapped extent of %s: top-hat %.0f m deep, %.0f km long, elongation %.1f, "
                         "buffered 400 m" % (cat["name"], depth, length, elong)):
                got += 1
    say("  lava: %d named catenae, %d troughs, %d placed" % (len(ctx.catenae), found, len(rows)))
    return rows


def new_fluvial(ctx, sr, rng):
    vals = []
    with arcpy.da.SearchCursor(VALLEYS, ["OID@", "Type", "Name", "Age", "SHAPE@"]) as c:
        for oid, ty, nm, age, g in c:
            vals.append((oid, ty, (nm or "").strip(), age, g.projectAs(sr)))
    cands = []
    for oid, ty, nm, age, g in vals:
        L = g.getLength("GEODESIC", "KILOMETERS")
        n = int(L // FLU_SEG_KM)
        for s in range(0, n, 2):
            seg = g.segmentAlongLine(s / n, (s + 1) / n, True)
            if seg is None or seg.length <= 0:
                continue
            p = seg.positionAlongLine(0.5, True).centroid
            if abs(p.Y) > LAT_MAX - 0.3:
                continue
            cands.append((block_of_xy(p.X, p.Y), oid, ty, nm, age, seg))
    order = rng.permutation(len(cands))
    by_block = collections.defaultdict(list)
    for i in order:
        by_block[cands[i][0]].append(cands[i])
    rows, per_valley, rejected, measured = [], collections.Counter(), [], 0
    for b, lst in by_block.items():
        got = tries = 0
        for _, oid, ty, nm, age, seg in lst:
            if got >= FLU_CAP or tries >= 4 * FLU_CAP:
                break
            if per_valley[oid] >= FLU_PER_VALLEY:
                continue
            c = seg.centroid
            lsr = local_sr(c.X, c.Y)
            strip = seg.projectAs(lsr).buffer(FLU_HALF_KM * 1000.0).projectAs(sr)
            strip = clip60(strip)
            if strip is None:
                continue
            rr, cc = cells_of(strip, all_touched=True)
            if not ctx.occ.free(rr, cc):
                continue
            tries += 1; measured += 1
            m = measures(ctx, strip)
            d = floor_depth(ctx, strip, sr)
            if m is None:
                continue
            m["floor"] = d
            what = "%s%s" % (ty.lower() if ty else "valley", " (%s)" % nm if nm else "")
            if d is None or d < FLOOR_M or m["volc"] >= VOLC_MAX:
                rejected.append(dict(cls=7, geom=strip, action="new", ok=False, m=m, sub="", block=b,
                                     src="Alemanno valley %d" % oid,
                                     why="strip along a mapped %s: floor %s m (>= %.0f), volcanic plains %.2f" % (
                                         what, "?" if d is None else "%.0f" % d, FLOOR_M, m["volc"])))
                continue
            if place(ctx, strip, rows, cls=7, ok=True, m=m, sub="valley network" if ty == "Valley Network" else "valley",
                     src="Alemanno valley %d" % oid,
                     why="20 km strip along a mapped %s (Alemanno & Orofino 2017, %s), 2.4 km wide; floor %.0f m "
                         "below a 4.8 km flank ring" % (what, age, d)):
                got += 1; per_valley[oid] += 1
    say("  fluvial: %d segments, %d measured, %d placed" % (len(cands), measured, len(rows)))
    return rows + rejected


# ---------------------------------------------------------------------------- checks and output
def overlaps(rows):
    ext = np.array([[r["geom"].extent.XMin, r["geom"].extent.YMin, r["geom"].extent.XMax, r["geom"].extent.YMax]
                    for r in rows])
    cls = np.array([r["cls"] for r in rows])
    spl = np.array([r["split"] for r in rows])
    clash, cross = [], []
    for i in range(len(rows)):
        j = np.nonzero((ext[i + 1:, 0] < ext[i, 2]) & (ext[i + 1:, 2] > ext[i, 0]) & (ext[i + 1:, 1] < ext[i, 3]) &
                       (ext[i + 1:, 3] > ext[i, 1]) & ((cls[i + 1:] != cls[i]) | (spl[i + 1:] != spl[i])))[0] + i + 1
        for k in j:
            a, b = rows[i]["geom"], rows[k]["geom"]
            if a.disjoint(b):
                continue
            x = a.intersect(b, 4)
            if x is None or x.area <= 0 or km2(x) < 0.01:
                continue
            if cls[i] != cls[k]:
                clash.append((i, int(k), int(cls[i]), int(cls[k]), round(km2(x), 2)))
            if spl[i] != spl[k]:
                cross.append((i, int(k), round(km2(x), 2)))
    return clash, cross


def safe_to_replace(fc):
    if not arcpy.Exists(fc):
        return True
    if "MappedBy" not in [f.name for f in arcpy.ListFields(fc)]:
        return False
    with arcpy.da.SearchCursor(fc, ["MappedBy"]) as c:
        return all(r[0] == MARKER for r in c)


def new_fc(name, sr, flds):
    fc = os.path.join(GDB, name)
    if not safe_to_replace(fc):
        sys.exit("REFUSING: %s holds rows this script did not write" % fc)
    if arcpy.Exists(fc):
        arcpy.management.Delete(fc)
    arcpy.management.CreateFeatureclass(GDB, name, "POLYGON", spatial_reference=sr)
    for n, t, ln in flds:
        arcpy.management.AddField(fc, n, t, field_length=ln)
    return fc


PFIELDS = [("Action", "TEXT", 8), ("ProposedClass", "SHORT", None), ("ProposedName", "TEXT", 24),
           ("Subtype", "TEXT", 24), ("Review", "TEXT", 6), ("ReviewNote", "TEXT", 120), ("Source", "TEXT", 80),
           ("Evidence", "TEXT", 254), ("V2Split", "TEXT", 5), ("V2OID", "LONG", None), ("OldOID", "LONG", None),
           ("Split", "TEXT", 5), ("Block", "TEXT", 8), ("KM2", "DOUBLE", None), ("SlopeMed", "DOUBLE", None),
           ("SlopeP90", "DOUBLE", None), ("ReliefM", "DOUBLE", None), ("CraterCover", "DOUBLE", None),
           ("FloorM", "DOUBLE", None), ("MappedBy", "TEXT", 40)]
LFIELDS = [("Classcode", "TEXT", 8), ("Classname", "TEXT", 24), ("Classvalue", "LONG", None), ("RED", "LONG", None),
           ("GREEN", "LONG", None), ("BLUE", "LONG", None), ("Subtype", "TEXT", 24), ("ProposalOID", "LONG", None),
           ("OldOID", "LONG", None), ("MappedBy", "TEXT", 40), ("Split", "TEXT", 8), ("Block", "TEXT", 16)]


def write(rows, sr):
    fc = new_fc(OUT, sr, PFIELDS)
    num = lambda v: None if v is None or (isinstance(v, float) and not math.isfinite(v)) else round(v, 3)
    with arcpy.da.InsertCursor(fc, ["SHAPE@"] + [n for n, _, _ in PFIELDS]) as cur:
        for r in rows:
            m = r.get("m") or {}
            note = "%s: %s" % (STAMP, r["why"])
            r["pid"] = cur.insertRow([r["geom"], r["action"], r["cls"], CLASSES[r["cls"]][0], r.get("sub", "")[:24],
                                      "accept" if r["ok"] else "reject", note[:120], r["src"][:80], ev_text(r.get("m")),
                                      r.get("v2split") or (r["split"] if r["action"] != "new" else None),
                                      r.get("v2oid"), r.get("old"), r["split"], r["block"], round(km2(r["geom"]), 2),
                                      num(m.get("slope")), num(m.get("rough")), num(m.get("relief")),
                                      num(m.get("cov4")), num(m.get("floor")), MARKER])
    say("wrote %s: %d rows" % (OUT, len(rows)))
    acc = [r for r in rows if r["ok"]]
    for name, sel in ((V3[0], acc), (V3[1], [r for r in acc if r["split"] == "train"]),
                      (V3[2], [r for r in acc if r["split"] == "test"])):
        fc = new_fc(name, sr, LFIELDS)
        with arcpy.da.InsertCursor(fc, ["SHAPE@"] + [n for n, _, _ in LFIELDS]) as cur:
            for r in sel:
                nm, (cr, cg, cb) = CLASSES[r["cls"]]
                cur.insertRow([r["geom"], " ", nm, r["cls"], cr, cg, cb, r.get("sub", "")[:24], r["pid"], r.get("old"),
                               MARKER, r["split"], r["block"]])
        n = int(arcpy.management.GetCount(fc)[0])
        assert n == len(sel), (name, n, len(sel))
        say("wrote %s: %d rows" % (name, n))


def add_map():
    bkdir = os.path.join(os.path.dirname(APRX), ".backups")
    bk = os.path.join(bkdir, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(APRX, bk)
    say("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    for m in p.listMaps(MAP):
        p.deleteItem(m)
    m = p.createMap(MAP, "MAP")
    for lyr in m.listLayers():                               # createMap adds an Earth basemap: Mars only (§37)
        m.removeLayer(lyr)
    m.spatialReference = arcpy.Describe(os.path.join(GDB, V3[1])).spatialReference
    for title, fc, q, vis in (("Rejected by the screens", OUT, "Review = 'reject'", False),
                              ("v2 labels (before)", "Landform_TrainingSamples_v2", None, False),
                              ("v3 held out", V3[2], None, True), ("v3 training", V3[1], None, True)):
        lyr = m.addDataFromPath(os.path.join(GDB, fc))
        lyr.name = title
        if q:
            lyr.definitionQuery = q
        lyr.visible = vis
        if fc != OUT:
            sym = lyr.symbology
            sym.updateRenderer("UniqueValueRenderer")
            sym.renderer.fields = ["Classname"]
            for grp in sym.renderer.groups:
                for it in grp.items:
                    nm = it.values[0][0]
                    rgb = next((c for n, c in CLASSES.values() if n == nm), None)
                    if rgb:
                        it.symbol.color = {"RGB": list(rgb) + [100]}
                        it.symbol.outlineColor = {"RGB": [0, 0, 0, 100] if "held" in title else list(rgb) + [100]}
                        it.symbol.outlineWidth = 0.6 if "held" in title else 0.2
            lyr.symbology = sym
    p.save()
    say("map %r: %d layers" % (MAP, len(m.listLayers())))


# ---------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    if not DRY:
        assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"
    arcpy.env.workspace = GDB
    rng = np.random.default_rng(SEED)
    sr, v2, held = read_v2()
    say("v2 labels %d (train %d, held out %d); held-out blocks %s" % (
        len(v2), sum(r["split"] == "train" for r in v2), sum(r["split"] == "test" for r in v2), " ".join(held)))
    ctx = Ctx()
    ctx.T = terrain_cells()
    say("terrain cells %d x %d (%.0f s)" % (NC, NR, time.time() - t0))
    ctx.rob = read_robbins()
    m10, m13 = crater_masks(ctx.rob)
    ctx.rim4, ctx.cov4, ctx.cov10 = cover(m10, 4), cover(m13, 4), cover(m13, 10)
    ctx.kind = unit_cells(sr)
    ctx.dem = Dem()
    named = read_named(sr)
    ctx.volcanoes = []
    for v in named:
        g = disc(v["x"], v["y"], max(3.0, 0.5 * v["diam"] / 2.0), sr)
        if g is None:
            continue
        rr, cc = cells_of(g)
        k = np.bincount(ctx.kind[rr, cc], minlength=7) / max(rr.size, 1)
        if k[KIND["ve"]] >= 0.3 or (v["type"] != "Mons" and k[KIND["ve"]] + k[KIND["volc"]] >= 0.5):
            ctx.volcanoes.append(v)
    ctx.catenae = read_catenae()
    say("Robbins %d; named volcanoes %d of %d; named catenae %d (%.0f s)" % (
        ctx.rob["d"].size, len(ctx.volcanoes), len(named), len(ctx.catenae), time.time() - t0))
    del m13

    # part 1
    rows = pieces_of_v2(ctx, v2, sr)
    say("v2 pieces done: %d rows (%.0f s)" % (len(rows), time.time() - t0))
    ctx.occ = Occupancy()
    for r in v2:
        ctx.occ.mark(*cells_of(r["geom"], all_touched=True))

    # part 2
    T, kind = ctx.T, ctx.kind
    off = np.isin(kind, (KIND["ve"], KIND["apron"], KIND["slide"])) | (kind == 0)
    new = []
    new += new_volcano_summits(ctx, sr)
    say("  volcano summits: %d" % len(new))
    new += new_craters(ctx, sr, rng)
    new += new_catena_troughs(ctx, sr, m10)
    new += new_fluvial(ctx, sr, rng)
    ok = (T["sp90"] >= HILL_SP90) & ~off & (ctx.cov10 == 0) & (ctx.cov4 <= 0.2)
    new += new_squares(ctx, 2, ok, HILL_K, HILL_MIN, HILL_CAP, sr, rng,
                       "3x3 cells (9.6 km) with >= %d of 9 cells' slope p90 >= %.0f°, no crater >= 10 km within 1.3 R, "
                       "off edifice/apron/landslide units, relief >= %.0f m" % (HILL_MIN, HILL_SP90, HILL_RELIEF),
                       extra=lambda m: m is not None and m["relief"] >= HILL_RELIEF and m["cov4"] <= 0.2)
    ok = (T["smed"] <= NG_SMED) & (T["sp90"] <= NG_SP90) & (T["z95"] - T["z05"] <= NG_RELIEF) & (ctx.cov4 == 0) & ~off
    new += new_squares(ctx, 4, ok, NG_K, NG_K * NG_K, NG_CAP, sr, rng,
                       "4x4 cells (12.8 km), every cell slope <= %.0f° p90 <= %.0f°, relief <= %.0f m, no crater >= "
                       "4 km within 1.3 R, off edifice/apron/landslide units" % (NG_SMED, NG_SP90, NG_RELIEF))
    ok = (kind == KIND["ve"]) & (T["smed"] >= VE_SMED) & (ctx.cov10 == 0)
    new += new_squares(ctx, 5, ok, VE_K, VE_K * VE_K, VE_CAP, sr, rng,
                       "4x4 cells (12.8 km) of SIM 3292 edifice units, every cell slope >= %.0f°, no crater >= 10 km "
                       "within 1.3 R" % VE_SMED)
    lat_rows = (LAT0 - (np.arange(NR) + 0.5) * DC)[:, None]
    ok = (kind == KIND["apron"]) & (T["smed"] >= AP_SMED) & ((T["sp90"] <= AP_SP90) | (np.abs(lat_rows) < P_APRON_ROUGH_LAT)) \
        & (ctx.cov10 == 0)
    new += new_squares(ctx, 6, ok, AP_K, AP_MIN, AP_CAP, sr, rng,
                       "4x4 cells (12.8 km), >= %d of 16 on SIM 3292 apron units with slope >= %.1f° and p90 <= %.0f° above 30°,"
                       " no crater >= 10 km within 1.3 R" % (AP_MIN, AP_SMED, AP_SP90))
    for r in new:
        r["split"] = "test" if r["block"] in held else "train"
    rows += new
    say("new candidates %d (%.0f s)" % (len(new), time.time() - t0))

    # checks on the accepted rows
    acc = [r for r in rows if r["ok"]]
    clash, cross = overlaps(acc)
    say("overlaps between classes %d, across the split %d (%.0f s)" % (len(clash), len(cross), time.time() - t0))
    if clash or cross:
        # a new row that touches anything is dropped; a clash between two v2 rows is a defect upstream
        bad = set()
        for c in clash + cross:
            i, k = c[0], c[1]
            for z in (k, i):
                if acc[z]["action"] == "new":
                    bad.add(id(acc[z])); break
            else:
                sys.exit("v2 rows overlap across classes or the split: %s %s" % (acc[i]["src"], acc[k]["src"]))
        for r in rows:
            if id(r) in bad:
                r["ok"], r["why"] = False, "overlaps another label: " + r["why"]
        acc = [r for r in rows if r["ok"]]
        clash, cross = overlaps(acc)
        assert not clash and not cross
        say("  %d new rows dropped for overlap" % len(bad))

    # tally
    per = collections.defaultdict(lambda: collections.Counter())
    blocks = collections.defaultdict(set)
    area = collections.defaultdict(float)
    for r in rows:
        per[(r["cls"], r["action"])]["%s %s" % (r["split"], "accept" if r["ok"] else "reject")] += 1
        if r["ok"]:
            blocks[(r["cls"], r["split"])].add(r["block"])
            area[(r["cls"], r["split"])] += km2(r["geom"])
    v2a = collections.defaultdict(float)
    for r in v2:
        v2a[(r["cls"], r["split"])] += km2(r["geom"])
    print("\nrows by class and action (split accept/reject):")
    for k in sorted(per):
        print("   %d %-18s %-6s %s" % (k[0], CLASSES[k[0]][0], k[1], dict(sorted(per[k].items()))))
    print("\naccepted per class: polygons (blocks), km²; v2 km² beside")
    summ = {}
    for c in sorted(CLASSES):
        d = {}
        for s in ("train", "test"):
            n = sum(1 for r in acc if r["cls"] == c and r["split"] == s)
            d[s] = dict(polygons=n, blocks=len(blocks[(c, s)]), km2=round(area[(c, s)]), v2_km2=round(v2a[(c, s)]),
                        v2_polygons=sum(1 for r in v2 if r["cls"] == c and r["split"] == s))
        summ[CLASSES[c][0]] = d
        print("   %d %-18s train %5d (%3d) %9.0f km² [v2 %4d, %9.0f]   held out %5d (%3d) %9.0f km² [v2 %4d, %9.0f]" % (
            c, CLASSES[c][0], d["train"]["polygons"], d["train"]["blocks"], d["train"]["km2"],
            d["train"]["v2_polygons"], d["train"]["v2_km2"], d["test"]["polygons"], d["test"]["blocks"],
            d["test"]["km2"], d["test"]["v2_polygons"], d["test"]["v2_km2"]))
    print("   all: train %d, held out %d" % (sum(r["split"] == "train" for r in acc), sum(r["split"] == "test" for r in acc)))

    log = dict(made=time.strftime("%Y-%m-%d %H:%M"), dry_run=DRY, held_out_blocks=held,
               rules={k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float, tuple))
                      and k not in GRID_NAMES},
               classes=summ, tally={"%d %s" % k: dict(v) for k, v in per.items()},
               rows=[dict(cls=r["cls"], action=r["action"], ok=r["ok"], split=r["split"], block=r["block"],
                          src=r["src"], why=r["why"], km2=round(km2(r["geom"]), 2),
                          m={k: (round(v, 3) if isinstance(v, float) and math.isfinite(v) else None)
                             for k, v in (r.get("m") or {}).items()}) for r in rows],
               seconds=round(time.time() - t0))
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    json.dump(log, open(LOG, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    say("log", LOG)
    if DRY:
        say("dry run: nothing written (%.0f s)" % (time.time() - t0))
        return
    write(rows, sr)
    if "--map" in sys.argv:
        add_map()
    say("done in %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
