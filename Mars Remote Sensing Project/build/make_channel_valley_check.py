# -*- coding: utf-8 -*-
r"""A1: the ±60° routed channels scored against the mapped valleys (NEXT-STEPS §12.2 A1, KB §69.50).

The 969,822 routed channel segments (Landform_ChannelCandidates_auto_60, X2, KB §53-§54) have no precision or recall.
The only independent channel map held is Alemanno & Orofino (2017), 3,772 valley polylines, 714,434 km (KB §68.5):
mapped valleys, not every channel, so "precision" here is the share of routed length that lies on a mapped valley.

  precision(d)  share of routed channel length (by Strahler order) within d km of a mapped valley
  recall(d)     share of mapped valley length within d km of a routed channel of order >= 3 (and of any order)
at d = 2, 5 and 10 km. Distances on the sphere: segment midpoints and valley points (densified to <= 0.5 km) as unit
vectors in a KD tree; chord ~ arc at these distances. Both layers are clipped to ±60°.

Chance baseline: the valley map rotated in longitude by 30°, 60°, ... 330° (11 rotations), which keeps every
valley's latitude and shape but moves it off the terrain it was mapped on; the observed value is set beside the
rotations' median and maximum. Also by latitude band (15°) and by SIM 3292 unit group at the segment midpoint.

Predictions, written before the first run (each reported as held or not held):
  P1  order >= 3 precision at 5 km is at least 1.5 times the rotations' median, and above every rotation;
  P2  recall at 5 km of the valley length by order >= 3 channels is at least 50 %;
  P3  precision at 5 km rises with Strahler order (orders 1, 2, 3, 4, >= 5).

  "<ArcGIS Pro Python>" make_channel_valley_check.py     -> logs\channel_valley_check.json  (reads the drive only)
"""
import os, sys, json, time, hashlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import numpy as np
from scipy.spatial import cKDTree
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive
import grid60 as G

OUT = os.path.join(HERE, "logs", "channel_valley_check.json")
CHANNELS = os.path.join(GDB, "Landform_ChannelCandidates_auto_60")
VALLEYS = on_drive(r"Mars Project\Reference\Alemanno2017_valleys\Giulia Valleys.shp")
VALLEY_SHA = "bf853acd13545d19387e83596353318912f4b598d3b274d932a2bf764e306715"
R_KM = G.R_MARS / 1000.0
DISTS = (2.0, 5.0, 10.0)
ROTS = tuple(range(30, 360, 30))
STEP_KM = 0.5
LAT_MAX = 60.0


def unit(lon, lat):
    p, l = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(p) * np.cos(l), np.cos(p) * np.sin(l), np.sin(p)]


def read_channels():
    t = time.time()
    a = arcpy.da.FeatureClassToNumPyArray(CHANNELS, ["OID@", "SHAPE@X", "SHAPE@Y", "StrahlerOrd"], explode_to_points=True)
    oid, x, y, order = a["OID@"], a["SHAPE@X"], a["SHAPE@Y"], a["StrahlerOrd"].astype(np.int16)
    del a
    lon = (np.degrees(x / G.R_MARS) + 180.0 + 180.0) % 360.0 - 180.0      # CM 180 metres -> -180..180
    lat = np.degrees(y / G.R_MARS)
    xyz = unit(lon, lat)
    same = oid[1:] == oid[:-1]                                           # consecutive vertices of one segment
    seg_len = np.linalg.norm(xyz[1:] - xyz[:-1], axis=1) * R_KM
    mid = (xyz[1:] + xyz[:-1]) / 2.0
    mid /= np.linalg.norm(mid, axis=1)[:, None]
    keep = same & (seg_len < 5.0)                                        # a jump > 5 km is a part break
    mlat = np.degrees(np.arcsin(np.clip(mid[keep][:, 2], -1, 1)))
    mlon = np.degrees(np.arctan2(mid[keep][:, 1], mid[keep][:, 0]))
    out = dict(xyz=mid[keep], km=seg_len[keep], order=order[1:][keep], lat=mlat, lon=mlon)
    print("channels: %d vertices, %d segments' pieces, %.0f km (%.0f s)" % (oid.size, keep.sum(), out["km"].sum(),
                                                                          time.time() - t))
    return out


def read_valleys():
    h = hashlib.sha256(open(VALLEYS, "rb").read()).hexdigest()
    assert h == VALLEY_SHA, "valley map SHA-256 %s" % h
    gcs = arcpy.SpatialReference(104905)
    lon, lat, km = [], [], 0.0
    with arcpy.da.SearchCursor(VALLEYS, ["SHAPE@"], spatial_reference=gcs) as c:
        for (g,) in c:
            for part in g:
                pts = np.array([(p.X, p.Y) for p in part if p is not None])
                if len(pts) < 2:
                    continue
                v = unit(pts[:, 0], pts[:, 1])
                for a, b, la, lb in zip(v[:-1], v[1:], pts[:-1], pts[1:]):
                    d = np.linalg.norm(b - a) * R_KM
                    n = max(1, int(np.ceil(d / STEP_KM)))
                    f = (np.arange(n) + 0.5) / n                         # midpoints of n equal pieces
                    q = a[None] * (1 - f[:, None]) + b[None] * f[:, None]
                    q /= np.linalg.norm(q, axis=1)[:, None]
                    qlat = np.degrees(np.arcsin(q[:, 2]))
                    ok = np.abs(qlat) <= LAT_MAX
                    lon.append(np.degrees(np.arctan2(q[ok, 1], q[ok, 0]))); lat.append(qlat[ok])
                    km += d * ok.mean()
    lon, lat = np.concatenate(lon), np.concatenate(lat)
    print("valleys: %d points, %.0f km within ±60°" % (lon.size, km))
    return lon, lat, km


def within(tree, pts, d_km):
    dist, _ = tree.query(pts, k=1, distance_upper_bound=max(DISTS) / R_KM * 1.01)
    return dist * R_KM                                                   # inf beyond the largest distance


def unit_groups(lon, lat):
    """SIM 3292 UnitGroup at each point, from a 0.05° raster of the unit polygons."""
    from osgeo import gdal, ogr
    res = 0.05
    W, H = int(360 / res), int(2 * LAT_MAX / res)
    drv = gdal.GetDriverByName("MEM")
    vec = drv.Create("", 0, 0, 0, gdal.GDT_Unknown) if int(gdal.VersionInfo()) >= 3110000 else \
        ogr.GetDriverByName("Memory").CreateDataSource("")
    lyr = vec.CreateLayer("u", geom_type=ogr.wkbMultiPolygon)
    lyr.CreateField(ogr.FieldDefn("k", ogr.OFTInteger))
    names = []
    with arcpy.da.SearchCursor(os.path.join(GDB, "Ref_SIM3292_GeologicUnits"), ["UnitGroup", "SHAPE@"],
                               spatial_reference=arcpy.SpatialReference(104905)) as c:
        for grp, g in c:
            if grp not in names:
                names.append(grp)
            f = ogr.Feature(lyr.GetLayerDefn()); f.SetField("k", names.index(grp) + 1)
            f.SetGeometry(ogr.CreateGeometryFromWkt(g.WKT)); lyr.CreateFeature(f)
    r = drv.Create("", W, H, 1, gdal.GDT_Byte)
    r.SetGeoTransform((-180, res, 0, LAT_MAX, 0, -res))
    gdal.RasterizeLayer(r, [1], lyr, options=["ATTRIBUTE=k"])
    a = r.ReadAsArray()
    i = np.clip(((LAT_MAX - lat) / res).astype(int), 0, H - 1)
    j = np.clip(((lon + 180) / res).astype(int), 0, W - 1)
    k = a[i, j]
    return np.array(["none"] + names, dtype=object)[k]


def rotate(lon, lat, deg):
    return unit((lon + deg + 180.0) % 360.0 - 180.0, lat)


def main():
    t0 = time.time()
    ch = read_channels()
    vlon, vlat, vkm = read_valleys()
    vpt_km = vkm / vlon.size                                            # length each valley point stands for
    o = np.minimum(ch["order"], 5)
    hi = ch["order"] >= 3
    res = dict(valley_km=round(vkm), channel_km=round(float(ch["km"].sum())),
               channel_km_order3=round(float(ch["km"][hi].sum())), dists_km=list(DISTS), rotations=list(ROTS))

    def precision(dist, sel):
        return {str(d): float(ch["km"][sel & (dist <= d)].sum() / ch["km"][sel].sum()) for d in DISTS}

    vtree = cKDTree(unit(vlon, vlat))
    dch = within(vtree, ch["xyz"], None)
    res["precision"] = {"order>=3": precision(dch, hi), "all": precision(dch, np.ones_like(hi))}
    res["precision_by_order"] = {("%d" % k if k < 5 else ">=5"): precision(dch, o == k) for k in range(1, 6)}
    ctree3, ctree = cKDTree(ch["xyz"][hi]), cKDTree(ch["xyz"])
    vx = unit(vlon, vlat)
    d3, da = within(ctree3, vx, None), within(ctree, vx, None)
    res["recall"] = {"order>=3": {str(d): float((d3 <= d).mean()) for d in DISTS},
                     "all": {str(d): float((da <= d).mean()) for d in DISTS}}
    print("observed: precision order>=3", res["precision"]["order>=3"], "all", res["precision"]["all"],
          "recall order>=3", res["recall"]["order>=3"], "all", res["recall"]["all"],
          "(%.0f s)" % (time.time() - t0))

    rot_p, rot_r = [], []
    for deg in ROTS:
        rt = cKDTree(rotate(vlon, vlat, deg))
        rot_p.append(precision(within(rt, ch["xyz"], None), hi))              # precision() indexes every piece
        rv = within(ctree3, rotate(vlon, vlat, deg), None)
        rot_r.append({str(d): float((rv <= d).mean()) for d in DISTS})
        print("  rotated %3d°: precision %s recall %s" % (deg, {k: round(v, 3) for k, v in rot_p[-1].items()},
                                                          {k: round(v, 3) for k, v in rot_r[-1].items()}))
    res["rotations_precision_order>=3"] = rot_p
    res["rotations_recall_order>=3"] = rot_r
    summ = lambda L, d: dict(median=float(np.median([x[str(d)] for x in L])), max=float(max(x[str(d)] for x in L)))
    res["baseline"] = {str(d): dict(precision=summ(rot_p, d), recall=summ(rot_r, d)) for d in DISTS}

    bands = np.floor(ch["lat"] / 15.0).astype(int) * 15
    res["precision_by_lat_band_order>=3_5km"] = {
        "%+d..%+d" % (b, b + 15): dict(km=round(float(ch["km"][hi & (bands == b)].sum())),
                                       share=float(ch["km"][hi & (bands == b) & (dch <= 5)].sum() /
                                                   max(ch["km"][hi & (bands == b)].sum(), 1e-9)))
        for b in range(-60, 60, 15)}
    grp = unit_groups(ch["lon"], ch["lat"])
    res["precision_by_unit_group_order>=3_5km"] = {
        g: dict(km=round(float(ch["km"][hi & (grp == g)].sum())),
                share=float(ch["km"][hi & (grp == g) & (dch <= 5)].sum() / max(ch["km"][hi & (grp == g)].sum(), 1e-9)))
        for g in sorted(set(grp[hi]))}

    p5 = res["precision"]["order>=3"]["5.0"]
    b5 = res["baseline"]["5.0"]["precision"]
    po = [res["precision_by_order"][k]["5.0"] for k in ("1", "2", "3", "4", ">=5")]
    res["predictions"] = {
        "P1 precision 5 km >= 1.5 x rotation median and above every rotation": p5 >= 1.5 * b5["median"] and p5 > b5["max"],
        "P2 recall 5 km (order>=3) >= 50 %": res["recall"]["order>=3"]["5.0"] >= 0.5,
        "P3 precision 5 km rises with order": all(a < b for a, b in zip(po, po[1:]))}
    print("precision 5 km by order:", [round(x, 3) for x in po])
    print("predictions:", res["predictions"])
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print("->", OUT, "(%.0f s)" % (time.time() - t0))


if __name__ == "__main__":
    main()
