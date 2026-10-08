# -*- coding: utf-8 -*-
r"""Test T2: crater density per geologic unit in each type area (KB §42, NEXT-STEPS §4).

Prediction, written before the run: Athabasca Valles' flood lava (SIM 3292 unit lAv, Late
Amazonian volcanic) carries far fewer craters >= 1 km per unit area than the older units of
either window, because it is among the youngest surfaces on Mars.

Two counts per unit, each per 10^6 km2:
  * Robbins & Hynek 2020 (Ref_Craters_Robbins2020): statistically complete to ~1 km; centres.
  * the project's closed-depression detector (Landform_CraterCandidates_auto / _ath): centroids.
    It misses breached craters by construction (§26.3), so it is shown beside, never instead.
Relative density only: not an age (no production function, no resurfacing model, small areas).

Areas are geodesic on the Mars sphere. Units smaller than MIN_KM2 inside a window are pooled as
"other". Read-only; writes build\logs\crater_density.json.
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy
import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import areas

MARS = arcpy.SpatialReference(104905)
UNITS = os.path.join(GDB, "Ref_SIM3292_GeologicUnits")
ROBBINS = os.path.join(GDB, "Ref_Craters_Robbins2020")
OUT = os.path.join(HERE, "logs", "crater_density.json")
MIN_KM2 = 20000.0
DMIN = (1.0, 2.0)                    # count >= 1 km, and >= 2 km as a check on completeness effects


def rings(geom):
    """Every ring of a polygon (outer and holes) as a matplotlib Path."""
    out = []
    for part in geom:
        cur = []
        for p in part:
            if p is None:
                if len(cur) > 2:
                    out.append(Path(np.array(cur)))
                cur = []
            else:
                cur.append((p.X, p.Y))
        if len(cur) > 2:
            out.append(Path(np.array(cur)))
    return out


def inside(paths, xy):
    """Even-odd rule over all rings: inside an odd number of them = inside the polygon."""
    n = np.zeros(len(xy), int)
    for p in paths:
        n += p.contains_points(xy)
    return n % 2 == 1


def window(a):
    lo0, lo1 = [((x + 180) % 360) - 180 for x in a["lon"]]
    la0, la1 = a["lat"]
    ring = [(lo0, la0), (lo0, la1), (lo1, la1), (lo1, la0), (lo0, la0)]
    return arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in ring]), MARS)


def main():
    t0 = time.time()
    with arcpy.da.SearchCursor(UNITS, ["SHAPE@", "Unit", "UnitDesc"]) as c:
        units = list(c)
    with arcpy.da.SearchCursor(ROBBINS, ["SHAPE@XY", "DiamKm"]) as c:
        rob = [(x, y, d) for (x, y), d in c]
    res = {"prediction": "Athabasca lAv far below the older units", "dmin_km": DMIN, "areas": {}}
    for key in ("ius", "ath"):
        sys.argv = [sys.argv[0], "--area", key]
        a = areas.current()
        win = window(a)
        ext = win.extent
        pieces = []
        for shp, u, desc in units:
            if shp.extent.disjoint(ext):
                continue
            part = shp.intersect(win, 4)
            if part and part.area > 0:
                pieces.append((u, desc, part, part.getArea("GEODESIC", "SQUAREKILOMETERS")))
        # pool small units
        tot = {}
        for u, desc, part, km2 in pieces:
            tot.setdefault(u, [desc, 0.0, []])
            tot[u][1] += km2; tot[u][2].append(part)
        cand = []
        with arcpy.da.SearchCursor(os.path.join(GDB, a["craters"]), ["SHAPE@", "DiameterKm"]) as c:
            for g, d in c:
                cen = g.centroid if g.type == "polygon" else g.firstPoint
                p = arcpy.PointGeometry(arcpy.Point(cen.X, cen.Y), g.spatialReference).projectAs(MARS)
                cand.append((p.firstPoint.X, p.firstPoint.Y, d))
        inwin = [(x, y, d) for x, y, d in rob if ext.XMin <= x <= ext.XMax and ext.YMin <= y <= ext.YMax]
        rows = {}
        for u, (desc, km2, parts) in tot.items():
            label = u if km2 >= MIN_KM2 else "other"
            r = rows.setdefault(label, {"desc": desc if km2 >= MIN_KM2 else "units < %d km2, pooled" % MIN_KM2,
                                        "km2": 0.0, "robbins": {str(k): 0 for k in DMIN}, "detector": {str(k): 0 for k in DMIN}})
            r["km2"] += km2
            paths = [rp for pp in parts for rp in rings(pp)]
            for src, pts in (("robbins", inwin), ("detector", cand)):
                if not pts:
                    continue
                arr = np.array([(x, y, d if d is not None else 0) for x, y, d in pts], float)
                hit = inside(paths, arr[:, :2])
                for k in DMIN:
                    r[src][str(k)] += int((hit & (arr[:, 2] >= k)).sum())
        print("\n%s  (%s)" % (a["name"], a["label"]))
        print("  %-8s %-46s %10s %16s %16s" % ("unit", "description", "km2", "Robbins >=1 km", "detector >=1 km"))
        for u, r in sorted(rows.items(), key=lambda kv: -kv[1]["km2"]):
            for src in ("robbins", "detector"):
                r[src + "_per_1e6km2"] = {k: 1e6 * n / r["km2"] for k, n in r[src].items()}
            print("  %-8s %-46s %10.0f %8d %7.0f/Mkm2 %6d %7.0f/Mkm2" % (
                u, (r["desc"] or "")[:46], r["km2"], r["robbins"]["1.0"], r["robbins_per_1e6km2"]["1.0"],
                r["detector"]["1.0"], r["detector_per_1e6km2"]["1.0"]))
        # the detector against Robbins: a candidate matches a Robbins crater whose centre lies within
        # half the Robbins diameter and whose diameter is within a factor of 2
        km_deg = 3396.19 * np.pi / 180
        R = np.array(inwin, float); Cd = np.array(cand, float)
        match = {}
        for dmin in DMIN:
            r_sel = R[R[:, 2] >= dmin]
            c_sel = Cd[Cd[:, 2] >= dmin]
            if not len(r_sel) or not len(c_sel):
                continue
            dx = (c_sel[None, :, 0] - r_sel[:, None, 0]) * km_deg * np.cos(np.radians(r_sel[:, None, 1]))
            dy = (c_sel[None, :, 1] - r_sel[:, None, 1]) * km_deg
            ok = (np.hypot(dx, dy) <= 0.5 * r_sel[:, None, 2]) & \
                 (np.abs(np.log(c_sel[None, :, 2] / r_sel[:, None, 2])) <= np.log(2))
            match[str(dmin)] = {"robbins": int(len(r_sel)), "detector": int(len(c_sel)),
                                "recall": float(ok.any(1).mean()), "precision": float(ok.any(0).mean())}
            print("  detector vs Robbins, D >= %.0f km: recall %.0f%% of %d Robbins craters, precision %.0f%% of %d candidates"
                  % (dmin, 100 * match[str(dmin)]["recall"], len(r_sel), 100 * match[str(dmin)]["precision"], len(c_sel)))
        res["areas"][key] = {"name": a["name"], "units": rows, "detector_vs_robbins": match}
    json.dump(res, open(OUT, "w"), indent=1)
    print("\nwrote", OUT, "in %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
