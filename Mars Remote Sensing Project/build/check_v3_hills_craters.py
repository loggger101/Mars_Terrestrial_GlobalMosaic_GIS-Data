# -*- coding: utf-8 -*-
r"""Why the rule's hills read as Crater (KB §69.85): how close each hills polygon of the third label set sits to craters.

propose_v3_labels.py placed "new" hills on 3 x 3 cells of steep, high-relief ground with no crater >= 10 km within
1.3 R; the author's hills ("piece", "keep") were drawn by eye. The published U-Net v3 reads 39.6 % of the new held-out
hills as Crater, the fresh U-Net 46.6 % of the fresh ones. If the rule's squares sit just outside large craters, on
their rims' outer flanks, or on densely cratered ground, the model's Crater would be reading crater terrain there.

For every hills polygon (training and held out), from Robbins & Hynek (2020):
  r_norm   distance from the polygon's centroid to the nearest crater >= 10 km, in that crater's radii (min over craters)
  dens     craters >= 1 km per 1,000 km2 within 25 km of the centroid
and, for the held-out ones, the share of the polygon's pixels each map reads as Crater: the published U-Net on the
1,652, the fresh U-Net on the fresh 895 (Spearman correlation of that share with r_norm and with dens, new hills only).

Written 2026-11-09 after §69.85 was read: a diagnosis, not a test. Reads only; writes logs\v3_hills_craters.json.

  "<ArcGIS Pro Python>" check_v3_hills_craters.py
"""
import os, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_v3_extras as X
import numpy as np
import arcpy
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from paths import GDB
B, SEVEN = X.B, X.SEVEN
RM = 3389.5                                   # Mars radius, km
HILLS = 2                                     # Classvalue of steep/windy hills


def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def chord(km):
    return 2 * np.sin(km / RM / 2)


def main():
    lon, lat, d = [], [], []
    with arcpy.da.SearchCursor(os.path.join(GDB, "Ref_Craters_Robbins2020"), ["Lon", "Lat", "DiamKm"]) as c:
        for a, b, k in c:
            lon.append(a); lat.append(b); d.append(k)
    lon, lat, d = np.array(lon), np.array(lat), np.array(d)
    big = d >= 10
    tb, rb = cKDTree(unit(lon[big], lat[big])), d[big] / 2
    t1 = cKDTree(unit(lon[d >= 1], lat[d >= 1]))
    act = {o: a for o, a in arcpy.da.SearchCursor(X.V3_PROP, ["OID@", "Action"])}

    def measure(fcn):
        out = []
        with arcpy.da.SearchCursor(fcn, ["SHAPE@XY", "ProposalOID", "Classvalue", "Block"], spatial_reference=B.MARS) as c:
            for (x, y), p, v, blk in c:
                if v != HILLS:
                    continue
                u = unit(np.array([x]), np.array([y]))[0]
                near = tb.query_ball_point(u, chord(600.0))
                dist = 2 * np.arcsin(np.clip(np.linalg.norm(tb.data[near] - u, axis=1) / 2, 0, 1)) * RM if near else np.array([])
                r_norm = float((dist / rb[near]).min()) if near else None
                n = len(t1.query_ball_point(u, chord(25.0)))
                out.append(dict(kind=act.get(p, "?"), block=blk, r_norm=r_norm, dens=n / (np.pi * 25.0 ** 2) * 1000))
        return out

    def crater_share(fcn, arrs):
        P = [p for p in B.polys(fcn)]
        R = B.rows(*arrs, P, len(SEVEN))
        return [float(r[HILLS - 1, 0] / r[HILLS - 1].sum()) if v == HILLS and r[HILLS - 1].sum() else None
                for (v, _, _), r in zip(P, R) if v == HILLS]

    res = dict(script="check_v3_hills_craters.py")
    rows = {"v3_train": measure(X.V3_TRAIN), "v3_test": measure(X.V3_TEST), "fresh_test": measure(X.fc("fresh", "test"))}
    for k, sh in (("v3_test", crater_share(X.V3_TEST, X.published(X.ARR % "v3"))),):
        for r, s in zip(rows[k], sh):
            r["crater_share"] = s
    a3 = np.load(os.path.join(X.HERE, X.ARR % "v3"), mmap_mode="r")
    fr = X.window_array(os.path.join(X.WORK, "classified", "fresh"), a3.shape)
    for r, s in zip(rows["fresh_test"], crater_share(X.fc("fresh", "test"), (fr, fr != 255, B.grid(a3.shape)))):
        r["crater_share"] = s

    summ = {}
    for k, rr in rows.items():
        by = collections.defaultdict(list)
        for r in rr:
            by["author" if r["kind"] in ("piece", "keep") else r["kind"]].append(r)
        summ[k] = {}
        for kind, g in sorted(by.items()):
            rn = np.array([r["r_norm"] for r in g if r["r_norm"] is not None])
            de = np.array([r["dens"] for r in g])
            s = dict(polygons=len(g), r_norm_median=round(float(np.median(rn)), 2), within_2R=round(float((rn <= 2).mean()), 3),
                     dens_median=round(float(np.median(de)), 1))
            cs = [(r["crater_share"], r["r_norm"], r["dens"]) for r in g if r.get("crater_share") is not None and r["r_norm"] is not None]
            if len(cs) >= 8:
                c, rn2, de2 = map(np.array, zip(*cs))
                s["crater_share_mean"] = round(float(c.mean()), 3)
                s["spearman_crater_share_r_norm"] = round(float(spearmanr(c, rn2)[0]), 3)
                s["spearman_crater_share_dens"] = round(float(spearmanr(c, de2)[0]), 3)
            summ[k][kind] = s
            print(k, kind, s, flush=True)
    res["summary"], res["polygons"] = summ, rows
    p = os.path.join(HERE, "logs", "v3_hills_craters.json")
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", p)


if __name__ == "__main__":
    main()
