# -*- coding: utf-8 -*-
r"""A10: crater size-frequency distributions, the closed depressions against Robbins (NEXT-STEPS §12.2 A10, KB §69.35).

The standard planetary figure for a crater catalogue: the cumulative number of craters at least D across per km²,
log-log, at the standard sqrt(2) diameters (1, 1.41, 2, 2.83 ... km). Three windows:

  ±60°        Landform_CraterCandidates_auto_60 (465,354 closed depressions >= 1 km) against Ref_Craters_Robbins2020
  Ius, Ath    each type area's closed depressions (Landform_CraterCandidates_auto, _ath), the review's accepts among
              them (Review = 'accept', the rows Landform_CraterRims holds, §69.31) and Robbins inside the window
              (areas.AREAS lon / lat, which the projected bounds match to the degree)

Densities are per km² of true area on the sphere R = 3396.19 km. Every set is cut at D >= 1 km. Per type area
the review's precision, accept / (accept + reject), is also split by diameter: 1-2, 2-5, 5-10 and >= 10 km.

Predictions, written before the first run (derived from §53.4's recall and precision by diameter, whose ratio
recall / precision is the expected candidates-to-Robbins count ratio: 1.33 at 1 km, 0.74 at 5 km, 0.55-0.61 at
10-100 km):
  P1  ±60°: the cumulative ratio candidates / Robbins is above 1 at 1 km, crosses 1 between 2 and 5 km, and lies
      within 0.45-0.80 at every standard diameter from 10 to 100 km.
  P2  ±60°: over 1-5 km the candidates' cumulative slope (least squares, log N against log D) is steeper than
      Robbins' by 0.2-0.5; over 5-50 km the two slopes differ by less than 0.25.
  P3  at each type area the review's precision at D >= 5 km is at least 3 times its precision at 1-2 km (the same
      rise as against Robbins, 15 % to 62 %, §53.4); reported with its n.
  P4  at each type area the accepted rims number 30-70 % of the Robbins craters in the window at D >= 5 km (recall
      levels off near one half, §26.3, and the review removes false positives, not misses).
Each is reported as held or not held; none is adjusted after the run.

  "<ArcGIS Pro Python>" make_crater_sfd.py        writes logs\crater_sfd.json; reads the gdb only (Pro may be open)
make_fig_crater_sfd.py draws it.
"""
import os, sys, json, math, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import areas

R_KM = 3396.19
DS = [2 ** (k / 2) for k in range(0, 17)]                   # 1 km to 256 km, sqrt(2) steps
BINS = [(1, 2), (2, 5), (5, 10), (10, None)]
OUT = os.path.join(HERE, "logs", "crater_sfd.json")


def area_km2(lon, lat):
    return R_KM ** 2 * math.radians(lon[1] - lon[0]) * (math.sin(math.radians(lat[1])) - math.sin(math.radians(lat[0])))


def cumulative(d, area):
    d = np.sort(np.asarray(d, float))
    n = len(d) - np.searchsorted(d, DS, side="left")
    return {"%g" % D: {"n": int(k), "per_km2": float(k / area)} for D, k in zip(DS, n)}


def slope(cum, lo, hi):
    pts = [(math.log10(float(k)), math.log10(v["per_km2"])) for k, v in cum.items()
           if lo <= float(k) <= hi and v["n"] > 0]
    x, y = np.array(pts).T
    return float(np.polyfit(x, y, 1)[0])


def rows(fc, fields, where=None):
    return [r for r in arcpy.da.SearchCursor(os.path.join(GDB, fc), fields, where)]


t0 = time.time()
rob = np.array(rows("Ref_Craters_Robbins2020", ["Lon", "Lat", "DiamKm"]), float)
rob[:, 0] = np.mod(rob[:, 0], 360.0)
rob = rob[rob[:, 2] >= 1.0]
res = {"script": "make_crater_sfd.py", "when": time.strftime("%Y-%m-%d %H:%M"), "diameters_km": DS,
       "sphere_radius_km": R_KM, "windows": {}}

# ------------------------------------------------------------------ ±60°
cand = np.array([r[0] for r in rows("Landform_CraterCandidates_auto_60", ["DiameterKm"])], float)
cand = cand[cand >= 1.0]
r60 = rob[np.abs(rob[:, 1]) <= 60.0]
a60 = area_km2((0, 360), (-60, 60))
w = {"area_km2": a60, "candidates": cumulative(cand, a60), "robbins": cumulative(r60[:, 2], a60)}
w["ratio"] = {k: (w["candidates"][k]["n"] / w["robbins"][k]["n"] if w["robbins"][k]["n"] else None) for k in w["candidates"]}
w["slopes"] = {"candidates_1_5": slope(w["candidates"], 1, 5), "robbins_1_5": slope(w["robbins"], 1, 5),
               "candidates_5_50": slope(w["candidates"], 5, 50), "robbins_5_50": slope(w["robbins"], 5, 50)}
res["windows"]["±60°"] = w
print("±60°: %d candidates, %d Robbins >= 1 km (%.0f s)" % (len(cand), len(r60), time.time() - t0))

# ------------------------------------------------------------------ type areas
for key, a in areas.AREAS.items():
    c = rows(a["craters"], ["DiameterKm", "Review"])
    d = np.array([r[0] for r in c], float)
    rv = np.array([(r[1] or "open").strip().lower() for r in c])
    keep = d >= 1.0
    d, rv = d[keep], rv[keep]
    inw = ((rob[:, 0] >= a["lon"][0]) & (rob[:, 0] < a["lon"][1]) &
           (rob[:, 1] >= a["lat"][0]) & (rob[:, 1] < a["lat"][1]))
    ar = area_km2(a["lon"], a["lat"])
    acc = d[rv == "accept"]
    by = {}
    for lo, hi in BINS:
        m = (d >= lo) & ((d < hi) if hi else True)
        na, nr, nu = int((rv[m] == "accept").sum()), int((rv[m] == "reject").sum()), int((rv[m] == "unsure").sum())
        rb = int(((rob[inw, 2] >= lo) & ((rob[inw, 2] < hi) if hi else True)).sum())
        by["%g-%s" % (lo, "%g" % hi if hi else "")] = dict(
            candidates=int(m.sum()), accept=na, reject=nr, unsure=nu, robbins=rb,
            precision=(na / (na + nr) if na + nr else None))
    res["windows"][a["name"]] = {
        "area_km2": ar, "candidates": cumulative(d, ar), "accepted": cumulative(acc, ar),
        "robbins": cumulative(rob[inw, 2], ar), "by_diameter": by}
    print("%s: %d candidates, %d accepted, %d Robbins >= 1 km" % (a["name"], len(d), len(acc), int(inw.sum())))

# ------------------------------------------------------------------ predictions
w = res["windows"]["±60°"]
ratio = dict(zip(DS, w["ratio"].values()))                  # the keys are "%g" strings, in DS's order
cross = [D for D, E in zip(DS, DS[1:]) if ratio[D] is not None and ratio[E] is not None and ratio[D] >= 1 > ratio[E]]
p = {}
p["P1"] = dict(
    rule="ratio > 1 at 1 km; crosses 1 between 2 and 5 km; 0.45-0.80 at every diameter 10-100 km",
    ratio_1=ratio[1.0], crosses_below_1_after_km=cross,
    ratio_10_100={"%g" % D: ratio[D] for D in DS if 10 <= D <= 100},
    held=bool(ratio[1.0] > 1 and len(cross) == 1 and 2 <= cross[0] < 5
              and all(0.45 <= ratio[D] <= 0.80 for D in DS if 10 <= D <= 100)))
s = w["slopes"]
p["P2"] = dict(rule="1-5 km: candidates steeper by 0.2-0.5; 5-50 km: slopes within 0.25", **s,
               steeper_1_5=s["robbins_1_5"] - s["candidates_1_5"],
               diff_5_50=abs(s["candidates_5_50"] - s["robbins_5_50"]),
               held=bool(0.2 <= s["robbins_1_5"] - s["candidates_1_5"] <= 0.5
                         and abs(s["candidates_5_50"] - s["robbins_5_50"]) < 0.25))
p3, p4 = {}, {}
for key, a in areas.AREAS.items():
    by = res["windows"][a["name"]]["by_diameter"]
    big = [by["5-10"], by["10-"]]
    na, nr = sum(b["accept"] for b in big), sum(b["reject"] for b in big)
    pb = na / (na + nr) if na + nr else None
    ps = by["1-2"]["precision"]
    p3[a["name"]] = dict(precision_1_2=ps, n_1_2=by["1-2"]["accept"] + by["1-2"]["reject"],
                         precision_5_up=pb, n_5_up=na + nr,
                         held=bool(pb is not None and ps and pb >= 3 * ps))
    nrob = sum(b["robbins"] for b in big)
    p4[a["name"]] = dict(accepted_5_up=na, robbins_5_up=nrob, share=(na / nrob if nrob else None),
                         held=bool(nrob and 0.30 <= na / nrob <= 0.70))
p["P3"] = dict(rule="precision at D >= 5 km at least 3x that at 1-2 km, each area", by_area=p3,
               held=all(v["held"] for v in p3.values()))
p["P4"] = dict(rule="accepted rims 30-70 % of Robbins in the window at D >= 5 km, each area", by_area=p4,
               held=all(v["held"] for v in p4.values()))
res["predictions"] = p

for k, v in p.items():
    print("%s %-10s %s" % (k, "HELD" if v["held"] else "NOT HELD", v["rule"]))
print("ratio by D: " + ", ".join("%g %.2f" % (D, ratio[D]) for D in DS if ratio[D] is not None))
print("slopes: " + ", ".join("%s %.2f" % kv for kv in s.items()))
for name, v in p3.items():
    print("%s precision 1-2 km %s (n %d), >= 5 km %s (n %d); accepted / Robbins >= 5 km %d / %d" % (
        name, "-" if v["precision_1_2"] is None else "%.3f" % v["precision_1_2"], v["n_1_2"],
        "-" if v["precision_5_up"] is None else "%.3f" % v["precision_5_up"], v["n_5_up"],
        p4[name]["accepted_5_up"], p4[name]["robbins_5_up"]))
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print("wrote %s (%.0f s)" % (OUT, time.time() - t0))
