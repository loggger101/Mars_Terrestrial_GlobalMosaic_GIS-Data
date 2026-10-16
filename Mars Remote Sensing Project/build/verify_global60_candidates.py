# -*- coding: utf-8 -*-
r"""Check the ±60° fine-pass candidate classes (X2, KB §53.4). Read-only; ArcGIS Python.

verify_global60.py checks the rasters' grids and does not look at the two vector products of
make_global_landforms.py, so this does: Landform_CraterCandidates_auto_60 and
Landform_ChannelCandidates_auto_60. Writes build\logs\global60_candidates_check.json.

Predictions and rules, written before the first run:

  C1  counts equal the run's own log (465,354 craters, 969,822 channel segments: run 3, 2026-10-15, after
      the five tiles over 180° were rerun, KB §54.4; runs 1-2: 467,547 / 973,879), CRS is
      Mars_Equidistant_Cylindrical_CM180, no empty geometry, every point inside the G200 grid.
  C2  the crater filters hold on every fine-pass candidate (KB 26.4): diameter >= 1 km, aspect <= 2.0,
      fill ratio >= 0.55; coarse-pass ones >= 20 km.
  C3  tile seams (8192-px cores, centroid-in-core rule): crater centroid density in 4 km bands on the
      core seams / density in 4 km bands half a core away. Prediction 0.85-1.15 (nothing dropped, nothing
      doubled). Near-duplicates (centres within half the larger diameter, diameters within a factor 2):
      their rate near seams / elsewhere, prediction <= 1.5.
  C4  the Ius Chasma window against the type-area run (KB §26, §42.3: 1,685 candidates >= 1 km at 100 m,
      21 % recall / 11 % precision against Robbins at >= 1 km). The fine pass is 200 m, so fewer small
      candidates are expected; prediction: fewer than 1,685, precision not lower than 11 %. Reported, no
      pass/fail: the resolutions differ.
  C5  against Robbins & Hynek 2020 over ±60°, the §42.3 rule: a candidate matches a Robbins crater whose
      centre lies within half the Robbins diameter and whose diameter is within a factor of 2; both sets
      at D >= Dmin. Prediction: precision rises with Dmin (~10 % at 1 km, as in both type areas, to well
      over half at >= 20 km); recall at >= 100 km near §28.11's 68 %. Reported per Dmin.
      Proof the matcher can fail: the same candidates shifted 2° in longitude must score precision < 2 %
      at every Dmin; if not, the matcher is broken and C5 is not reported.

Run 1, 2026-10-14: C1-C3 pass. C5's control FAILED as written: shifted 2°, precision 0.8 % (>= 1 km) and
1.3 % (>= 2 km), but 3.9-18.6 % from >= 5 km up: a 2° shift (~118 km) is no farther than a large crater's
own size, and large craters are dense enough to overlap by chance. So run 1 reports no C5. C4: 1,709 in the
Ius window, against the predicted "fewer than 1,685"; precision 11.1 %, as predicted.

Added before run 2 (not changing C5's rule, a second control beside it):
  C5b each candidate shifted east by 3 of its own diameters (at its latitude), so it can never overlap its
      own crater but stays in the same terrain: a local chance baseline. Rule: the matcher is valid if the
      observed precision exceeds the C5b baseline at every Dmin; C5 is then reported beside the baseline.
  C4b the Athabasca window too, against §42.3's 1,709 / 592 / 36 % / 13 % (run 1's Ius count equals that
      figure; this rules out a window mix-up).

Run 2, 2026-10-14: C5b passes at every Dmin (e.g. >= 5 km 62.2 % against 4.0 %). From run 2 on, C5's 2°
control is kept in the log as information (it fails as written, run 1) and C5b is the gate.

Run 3, 2026-10-15: after the five fine tiles over x = 0 were rerun on the patched DEM (KB §54), C1's
counts are that run's log (logs\landform_fine_meridian_DESKTOP-PJS73RO.log): 465,354 / 969,822.
Prediction unchanged for C2-C5b; C3's seams are expected to stay within 0.85-1.15.
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import numpy as np
from scipy.spatial import cKDTree
import arcpy
import areas

OUT = os.path.join(HERE, "logs", "global60_candidates_check.json")
FC_C = os.path.join(GDB, "Landform_CraterCandidates_auto_60")
FC_L = os.path.join(GDB, "Landform_ChannelCandidates_auto_60")
ROBBINS = os.path.join(GDB, "Ref_Craters_Robbins2020")
EXPECT = {"craters": 465354, "channels": 969822}     # run 3 (2026-10-15); runs 1-2: 467,547 / 973,879
OX, OY, RES, NX, NY, CORE = -10669400.0, 3556500.0, 200.0, 106694, 35565, 8192
R_KM = 3396.19
res = {"when": time.strftime("%Y-%m-%d %H:%M")}
fails = []


def check(name, ok, detail):
    print("%-4s %-60s %s" % ("ok" if ok else "FAIL", name, detail), flush=True)
    res.setdefault("checks", {})[name] = {"ok": bool(ok), "detail": detail}
    if not ok:
        fails.append(name)


# ------------------------------------------------------------------ C1, C2
t = time.time()
f = ["SHAPE@X", "SHAPE@Y", "DiameterKm", "Aspect", "FillRatio", "CenterLon", "CenterLat", "Preservation"]
rows = [r for r in arcpy.da.SearchCursor(FC_C, f)]
xs = np.array([r[0] if r[0] is not None else np.nan for r in rows])
ys = np.array([r[1] if r[1] is not None else np.nan for r in rows])
D = np.array([r[2] for r in rows], float); asp = np.array([r[3] for r in rows], float)
fr = np.array([r[4] for r in rows], float)
lon = np.array([r[5] for r in rows], float); lat = np.array([r[6] for r in rows], float)
pres = np.array([r[7] for r in rows])
print("read %d craters in %.0f s" % (len(rows), time.time() - t), flush=True)
nl = int(arcpy.management.GetCount(FC_L)[0])
nl_null = sum(1 for (g,) in arcpy.da.SearchCursor(FC_L, ["SHAPE@LENGTH"]) if not g)
srs = {arcpy.Describe(p).spatialReference.name for p in (FC_C, FC_L)}

check("C1 crater count = run log", len(rows) == EXPECT["craters"], "%d" % len(rows))
check("C1 channel count = run log", nl == EXPECT["channels"], "%d" % nl)
check("C1 CRS Mars_Equidistant_Cylindrical_CM180", srs == {"Mars_Equidistant_Cylindrical_CM180"}, str(srs))
check("C1 no empty geometry", not np.isnan(xs).any() and nl_null == 0,
      "%d crater, %d channel" % (int(np.isnan(xs).sum()), nl_null))
inside = (xs >= OX) & (xs <= OX + NX * RES) & (ys <= OY) & (ys >= OY - NY * RES)
check("C1 every crater inside the G200 grid", inside.all(), "%d outside" % int((~inside).sum()))
check("C1 CenterLat within ±60°", (np.abs(lat) <= 60.0001).all(), "max |lat| %.4f" % np.abs(lat).max())
fine = pres == "fine-pass"; coarse = pres == "coarse-pass"
res["preservation"] = {k: int((pres == k).sum()) for k in np.unique(pres)}
check("C2 fine-pass: D >= 1 km, aspect <= 2, fill ratio >= 0.55",
      (D[fine] >= 1.0).all() and (asp[fine] <= 2.0 + 1e-9).all() and (fr[fine] >= 0.55 - 1e-9).all(),
      "min D %.3f, max aspect %.3f, min fill %.3f" % (D[fine].min(), asp[fine].max(), fr[fine].min()))
if coarse.any():
    check("C2 coarse-pass: D >= 20 km", (D[coarse] >= 20.0).all(), "min D %.1f" % D[coarse].min())

# ------------------------------------------------------------------ C3 seams
col = (xs - OX) / RES; row = (OY - ys) / RES
BAND = 10.0                                    # +-10 px = 4 km band
def band_density(coord, seams):
    d = np.min(np.abs(coord[:, None] - np.asarray(seams)[None, :]), axis=1)
    return int((d <= BAND).sum()) / (len(seams) * 2 * BAND)
seams_c = [CORE * k for k in range(1, NX // CORE + 1) if CORE * k < NX]
seams_r = [CORE * k for k in range(1, NY // CORE + 1) if CORE * k < NY]
mid_c = [s - CORE // 2 for s in seams_c]; mid_r = [s - CORE // 2 for s in seams_r]
sel = fine
rc = band_density(col[sel], seams_c) / band_density(col[sel], mid_c)
rr = band_density(row[sel], seams_r) / band_density(row[sel], mid_r)
res["seams"] = {"col_ratio": rc, "row_ratio": rr, "n_col_seams": len(seams_c), "n_row_seams": len(seams_r)}
check("C3 crater density on column seams / mid-tile (0.85-1.15)", 0.85 <= rc <= 1.15, "%.3f" % rc)
check("C3 crater density on row seams / mid-tile (0.85-1.15)", 0.85 <= rr <= 1.15, "%.3f" % rr)

xyz_km = np.c_[xs, ys] / 1000.0                # equirectangular km; fine at the scale of one crater
tree = cKDTree(xyz_km)
pairs = tree.query_pairs(r=float(np.nanmax(D)) / 2.0 if np.nanmax(D) < 50 else 25.0, output_type="ndarray")
i, j = pairs[:, 0], pairs[:, 1]
dist = np.hypot(*(xyz_km[i] - xyz_km[j]).T) * np.cos(np.radians(lat[i]))  # x shrinks with latitude
near = (dist <= 0.5 * np.maximum(D[i], D[j])) & (np.abs(np.log(D[i] / D[j])) <= np.log(2))
dup = np.zeros(len(D), bool); dup[i[near]] = True; dup[j[near]] = True
dseam = np.minimum(np.min(np.abs(col[:, None] - np.array(seams_c)[None, :]), 1),
                   np.min(np.abs(row[:, None] - np.array(seams_r)[None, :]), 1))
ns = dseam <= BAND
rate_seam, rate_else = dup[ns].mean(), dup[~ns].mean()
res["near_duplicates"] = {"all": int(dup.sum()), "rate_near_seams": float(rate_seam), "rate_elsewhere": float(rate_else)}
check("C3 near-duplicate rate at seams / elsewhere (<= 1.5)",
      rate_seam <= 1.5 * max(rate_else, 1e-9), "%.4f / %.4f" % (rate_seam, rate_else))

# ------------------------------------------------------------------ Robbins
rb = np.array([r for r in arcpy.da.SearchCursor(ROBBINS, ["Lon", "Lat", "DiamKm"])], float)
rb[:, 0] = np.mod(rb[:, 0], 360.0)
rb = rb[np.abs(rb[:, 1]) <= 60.0]


def unit(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def score(c_lon, c_lat, c_d, r_lon, r_lat, r_d, dmin):
    """§42.3: candidate within half the Robbins diameter of its centre, diameters within a factor of 2."""
    cs = c_d >= dmin; rs = r_d >= dmin
    if not cs.any() or not rs.any():
        return None
    C = unit(c_lon[cs], c_lat[cs]); Rr = unit(r_lon[rs], r_lat[rs]); cd, rd = c_d[cs], r_d[rs]
    t = cKDTree(C)
    rad = 2 * np.sin(0.5 * (0.5 * rd) / R_KM)          # chord of half the Robbins diameter
    hits = t.query_ball_point(Rr, rad)
    rec = np.zeros(len(rd), bool); prec = np.zeros(len(cd), bool)
    for k, h in enumerate(hits):
        if h:
            h = np.asarray(h)
            ok = h[np.abs(np.log(cd[h] / rd[k])) <= np.log(2)]
            if len(ok):
                rec[k] = True; prec[ok] = True
    return {"robbins": int(rs.sum()), "candidates": int(cs.sum()),
            "recall": float(rec.mean()), "precision": float(prec.mean())}


DMINS = (1, 2, 5, 10, 20, 50, 100)
# proof the matcher can fail: shift every candidate 2° east
shifted = {str(d): score(np.mod(lon + 2.0, 360), lat, D, rb[:, 0], rb[:, 1], rb[:, 2], d) for d in DMINS}
ok_fail = all(s is None or s["precision"] < 0.02 for s in shifted.values())
# information only since run 2 (see the docstring): mis-specified for large craters; C5b is the gate
print("info C5 matcher on candidates shifted 2° (rule: precision < 2 %%): %s -> %s" % (
    ", ".join("%s:%.1f%%" % (k, 100 * v["precision"]) for k, v in shifted.items() if v),
    "holds" if ok_fail else "fails as written"), flush=True)
res["c5_2deg_control_holds"] = ok_fail
res["robbins_shifted_2deg"] = shifted
# C5b: a local baseline, each candidate moved 3 of its own diameters east
dlon = np.degrees(3.0 * D / (R_KM * np.cos(np.radians(lat))))
local = {str(d): score(np.mod(lon + dlon, 360), lat, D, rb[:, 0], rb[:, 1], rb[:, 2], d) for d in DMINS}
obs = {str(d): score(lon, lat, D, rb[:, 0], rb[:, 1], rb[:, 2], d) for d in DMINS}
ok_b = all(obs[k] is None or obs[k]["precision"] > local[k]["precision"] for k in obs)
check("C5b observed precision above the 3-diameter-shift baseline at every Dmin", ok_b,
      ", ".join("%s:%.1f%%>%.1f%%" % (k, 100 * obs[k]["precision"], 100 * local[k]["precision"])
                for k in obs if obs[k]))
res["robbins_shifted_3D"] = local
if ok_fail or ok_b:
    res["robbins"] = {}
    print("\n  Robbins over ±60° (%d craters >= 1 km in the catalogue's ±60° share)" % int((rb[:, 2] >= 1).sum()))
    for d in DMINS:
        s = obs[str(d)]
        res["robbins"][str(d)] = s
        if s:
            b = local[str(d)]
            print("  D >= %3d km: Robbins %7d  recall %5.1f%% (baseline %4.1f%%)   candidates %7d  "
                  "precision %5.1f%% (baseline %4.1f%%)" % (d, s["robbins"], 100 * s["recall"], 100 * b["recall"],
                                                           s["candidates"], 100 * s["precision"], 100 * b["precision"]),
                  flush=True)

# ------------------------------------------------------------------ C4 Ius window
xmin, ymin, xmax, ymax = areas.AREAS["ius"]["bounds"]
w = (xs >= xmin) & (xs <= xmax) & (ys >= ymin) & (ys <= ymax)
rw = (rb[:, 0] >= 271) & (rb[:, 0] <= 286) & (rb[:, 1] >= -13) & (rb[:, 1] <= -6)
ius = {"candidates_ge1km": int((w & (D >= 1)).sum()), "type_area_run_100m": 1685}
s = score(lon[w], lat[w], D[w], rb[rw, 0], rb[rw, 1], rb[rw, 2], 1)
ius["vs_robbins_ge1km"] = s
res["ius_window"] = ius
print("\n  Ius window: %d candidates >= 1 km at 200 m (type-area run at 100 m: 1,685); vs Robbins: %s"
      % (ius["candidates_ge1km"], s))
xmin, ymin, xmax, ymax = areas.AREAS["ath"]["bounds"]
w = (xs >= xmin) & (xs <= xmax) & (ys >= ymin) & (ys <= ymax)
rw = (rb[:, 0] >= 150) & (rb[:, 0] <= 162) & (rb[:, 1] >= 4) & (rb[:, 1] <= 14)
ath = {"candidates_ge1km": int((w & (D >= 1)).sum()), "type_area_run_100m": 1709,
       "vs_robbins_ge1km": score(lon[w], lat[w], D[w], rb[rw, 0], rb[rw, 1], rb[rw, 2], 1)}
res["ath_window"] = ath
print("  Athabasca window: %d candidates >= 1 km at 200 m (type-area run at 100 m: 1,709); vs Robbins: %s"
      % (ath["candidates_ge1km"], ath["vs_robbins_ge1km"]))

res["failed"] = fails
json.dump(res, open(OUT, "w"), indent=1)
print("\n%d checks, %d failed -> %s" % (len(res["checks"]), len(fails), OUT))
sys.exit(1 if fails else 0)
