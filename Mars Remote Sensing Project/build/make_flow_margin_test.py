# -*- coding: utf-8 -*-
r"""Test T5 (H1): do the THEMIS IR mosaics show lava-flow contacts that Viking misses? (NEXT-STEPS §4; KB §47)

H1, from the prospectus: day IR delineates flow boundaries under dust that Viking misses.

Prediction, written before the run (2026-10-08): Viking red separates the units on either side of the
geologic map's contacts at Athabasca at least as often as day IR does, and contacts that only IR
separates are no more common than contacts that only Viking separates. Night IR separates the fewest.
Reason: at Athabasca, Viking albedo tracks calibrated thermal inertia (r -0.55 / -0.64) and the THEMIS
DN do not (§42.4). If so, H1 is not supported at the scale of a 1:20 M map.

Design (fixed before any profile was measured):
- Contacts: shared boundaries between different SIM 3292 units inside the Athabasca window (§42.1),
  from PolygonToLine with neighbours; window-edge lines dropped. Primary set: contacts with lAv on
  one side, the Athabasca flood lava (§41). Also reported: all contacts.
- Profiles every 2 km along each contact, perpendicular to it, -20 to +20 km at 100 m. The two sides
  are 3-20 km out; the central +-3 km is skipped because a 1:20 M contact is generalised by km.
- Separation per band and profile: d = |mean(side A) - mean(side B)| / sqrt((var A + var B) / 2).
- Null: 2,000 profiles at random points and random azimuths, >= 25 km from any contact, same d.
  A contact profile "separates" in a band when its d exceeds that band's null 90th percentile, so
  10 % of null profiles separate by construction.
- Uncertainty: profiles along one contact are correlated, so 95 % intervals come from a bootstrap
  over contacts (2,000 resamples), not over profiles.
- Verdict rule, fixed in advance: H1 supported only if day IR's separation rate exceeds Viking red's
  with the 95 % interval of the difference above zero, AND IR-only contacts outnumber Viking-only.
- Registration check: the unit under each profile's +-10 km points (point in polygon) must differ
  on most contact profiles and agree on every null profile.

Coordinates: the unit class is labelled GCS_Mars_2000 (WKID 104905, the ellipsoid) but its vertices
are the source's spherical coordinates, checked to 5e-10 deg (KB §47.1). They are converted here
directly, x = R (lon - 180 deg), y = R lat on R = 3,396,190 m, the stack's CM 180 grid, so no datum
transformation can enter. Read-only; writes build\logs\t5_flow_margins.json.
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, junction
import areas

A = dict(areas.AREAS["ath"], key="ath")
WS = junction(A["folder"])
UNITS = os.path.join(GDB, "Ref_SIM3292_GeologicUnits")
OUT = os.path.join(HERE, "logs", "t5_flow_margins.json")
R = 3396190.0
STEP, HALF, GAP, RES = 2000.0, 20000.0, 3000.0, 100.0
NNULL, NBOOT, SEED, NULL_MIN_KM = 2000, 2000, 20261008, 25.0
BANDS = [("viking_r", "ath_viking.tif", 0), ("viking_g", "ath_viking.tif", 1), ("viking_b", "ath_viking.tif", 2),
         ("day_ir", "ath_day.tif", 0), ("night_ir", "ath_night.tif", 0), ("contrast_index", "ath_thermal_contrast.tif", 0)]
PRIMARY = "lAv"
t0 = time.time()


def log(msg):
    print("[%6.1fs] %s" % (time.time() - t0, msg), flush=True)


def to_xy(lon, lat):
    lon = np.asarray(lon, float); lat = np.asarray(lat, float)
    return R * np.radians(((lon % 360.0) - 180.0)), R * np.radians(lat)


def geom_xy(g):
    """Polygon/polyline geometry in raw lon/lat -> list of parts, each a list of rings (arrays in metres)."""
    parts = []
    for part in g:
        rings, cur = [], []
        for p in part:
            if p is None:
                if cur: rings.append(cur)
                cur = []
            else:
                cur.append((p.X, p.Y))
        if cur: rings.append(cur)
        parts.append([np.column_stack(to_xy(*np.array(r).T)) for r in rings])
    return parts


# ------------------------------------------------------------------ units and contacts, in the window
gsr = arcpy.Describe(UNITS).spatialReference
lo0, lo1 = A["lon"]; la0, la1 = A["lat"]
win = arcpy.Polygon(arcpy.Array([arcpy.Point(*p) for p in
                                 [(lo0, la0), (lo0, la1), (lo1, la1), (lo1, la0), (lo0, la0)]]), gsr)
arcpy.env.overwriteOutput = True
mem_u, mem_l = r"memory\t5_units", r"memory\t5_lines"
arcpy.management.CreateFeatureclass("memory", "t5_units", "POLYGON", spatial_reference=gsr)
arcpy.management.AddField(mem_u, "Unit", "TEXT", field_length=8)
unit_of, unit_paths = {}, {}
with arcpy.da.SearchCursor(UNITS, ["SHAPE@", "Unit"]) as c, \
        arcpy.da.InsertCursor(mem_u, ["SHAPE@", "Unit"]) as ic:
    for g, u in c:
        if g.disjoint(win):
            continue
        gi = g.intersect(win, 4)
        if gi.area > 0:
            oid = ic.insertRow([gi, u])
            unit_of[oid] = u
            unit_paths[oid] = [Path(r) for part in geom_xy(gi) for r in part]
arcpy.management.PolygonToLine(mem_u, mem_l, "IDENTIFY_NEIGHBORS")
contacts = []
with arcpy.da.SearchCursor(mem_l, ["SHAPE@", "LEFT_FID", "RIGHT_FID"]) as c:
    for g, lf, rf in c:
        if lf < 0 or rf < 0 or unit_of[lf] == unit_of[rf]:
            continue
        pair = tuple(sorted((unit_of[lf], unit_of[rf])))
        for part in geom_xy(g):
            for line in part:
                contacts.append((pair, line))
log("units in window: %s; contacts: %d lines, %.0f km" % (
    sorted(set(unit_of.values())), len(contacts),
    sum(np.hypot(*np.diff(l, axis=0).T).sum() for _, l in contacts) / 1000.0))


def unit_at(xy):
    """Unit name at each point (None outside every polygon), even-odd over each polygon's rings."""
    out = np.full(len(xy), None, object)
    for oid, paths in unit_paths.items():
        n = np.zeros(len(xy), int)
        for p in paths:
            n += p.contains_points(xy)
        out[(n % 2 == 1) & (out == None)] = unit_of[oid]
    return out


# ------------------------------------------------------------------ bands
xmin, ymin, xmax, ymax = A["bounds"]
bands = {}
for name, f, b in BANDS:
    path = os.path.join(WS, f)
    r = arcpy.Raster(path)
    assert abs(r.extent.XMin - xmin) < 1 and abs(r.extent.YMax - ymax) < 1 and abs(r.meanCellWidth - RES) < 1e-6, f
    arr = arcpy.RasterToNumPyArray(path)
    if arr.ndim == 3:
        arr = arr[b]
    nd = r.noDataValue
    arr = arr.astype("float32")
    if nd is not None:
        arr[arr == nd] = np.nan
    bands[name] = arr
H, W = bands["day_ir"].shape
log("bands read: %d x %d px; valid %s" % (W, H, ", ".join("%s %.1f%%" % (k, 100 * np.isfinite(v).mean()) for k, v in bands.items())))

S = np.arange(-HALF, HALF + RES / 2, RES)
SIDE_A, SIDE_B = (S <= -GAP), (S >= GAP)


def profiles(px, py, nx, ny):
    """Sample every band on the perpendicular profiles; return {band: (n, len(S))} and a validity mask."""
    X = px[:, None] + S[None, :] * nx[:, None]
    Y = py[:, None] + S[None, :] * ny[:, None]
    col = np.floor((X - xmin) / RES).astype(int); row = np.floor((ymax - Y) / RES).astype(int)
    ok = ((col >= 0) & (col < W) & (row >= 0) & (row < H)).all(axis=1)
    col = np.clip(col, 0, W - 1); row = np.clip(row, 0, H - 1)
    vals = {k: v[row, col] for k, v in bands.items()}
    for v in vals.values():
        ok &= np.isfinite(v).all(axis=1)
    return vals, ok


def separation(v):
    a, b = v[:, SIDE_A], v[:, SIDE_B]
    sd = np.sqrt((a.var(axis=1) + b.var(axis=1)) / 2.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.abs(a.mean(axis=1) - b.mean(axis=1)) / sd


# ------------------------------------------------------------------ contact profiles
px, py, nx, ny, cid, cpair = [], [], [], [], [], []
for i, (pair, line) in enumerate(contacts):
    seg = np.hypot(*np.diff(line, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    L = cum[-1]
    if L < STEP:
        continue
    for d in np.arange(STEP / 2, L, STEP):
        p = np.array([np.interp(d, cum, line[:, 0]), np.interp(d, cum, line[:, 1])])
        q0 = np.array([np.interp(max(d - 500, 0), cum, line[:, 0]), np.interp(max(d - 500, 0), cum, line[:, 1])])
        q1 = np.array([np.interp(min(d + 500, L), cum, line[:, 0]), np.interp(min(d + 500, L), cum, line[:, 1])])
        t = q1 - q0
        t /= np.hypot(*t)
        px.append(p[0]); py.append(p[1]); nx.append(-t[1]); ny.append(t[0]); cid.append(i); cpair.append(pair)
px, py, nx, ny, cid = map(np.array, (px, py, nx, ny, cid))
cpair = np.array(["-".join(p) for p in cpair])
cv, cok = profiles(px, py, nx, ny)
log("contact profiles: %d sampled, %d inside the window and valid in every band" % (len(px), cok.sum()))

# ------------------------------------------------------------------ null profiles
rng = np.random.default_rng(SEED)
all_lines = arcpy.Polyline(arcpy.Array([arcpy.Array([arcpy.Point(x, y) for x, y in l]) for _, l in contacts]))
nxs, nys, nnx, nny = [], [], [], []
tries = 0
while len(nxs) < NNULL and tries < 200000:
    tries += 1
    x = rng.uniform(xmin + HALF + RES, xmax - HALF - RES); y = rng.uniform(ymin + HALF + RES, ymax - HALF - RES)
    if all_lines.distanceTo(arcpy.Point(x, y)) < NULL_MIN_KM * 1000:
        continue
    a = rng.uniform(0, np.pi)
    nxs.append(x); nys.append(y); nnx.append(np.cos(a)); nny.append(np.sin(a))
nv, nok = profiles(*map(np.array, (nxs, nys, nnx, nny)))
log("null profiles: %d drawn (%d tries), %d valid" % (len(nxs), tries, nok.sum()))

# ------------------------------------------------------------------ registration check
def sides_differ(x, y, ux, uy):
    a = unit_at(np.column_stack([x - 10000 * ux, y - 10000 * uy]))
    b = unit_at(np.column_stack([x + 10000 * ux, y + 10000 * uy]))
    return (a != b) & (a != None) & (b != None), a, b

c_diff, _, _ = sides_differ(px, py, nx, ny)
n_diff, _, _ = sides_differ(*map(np.array, (nxs, nys, nnx, nny)))
log("registration: contact profiles with different units at +-10 km %.1f %%; null profiles %.1f %%"
    % (100 * c_diff[cok].mean(), 100 * n_diff[nok].mean()))

# ------------------------------------------------------------------ separation, thresholds, rates
res = {"test": "T5", "hypothesis": "H1",
       "prediction": "Viking red separates at least as many contacts as day IR; IR-only <= Viking-only; night IR fewest; H1 not supported",
       "design": {"step_km": STEP / 1000, "half_km": HALF / 1000, "gap_km": GAP / 1000, "null_n": NNULL,
                  "null_min_km": NULL_MIN_KM, "boot": NBOOT, "seed": SEED, "null_quantile": 0.9},
       "contacts_by_pair_km": {}, "registration": {"contact_sides_differ": float(c_diff[cok].mean()),
                                                   "null_sides_differ": float(n_diff[nok].mean())},
       "sets": {}}
for pr in sorted(set(cpair)):
    km = sum(np.hypot(*np.diff(l, axis=0).T).sum() for p, l in contacts if "-".join(p) == pr) / 1000
    res["contacts_by_pair_km"][str(pr)] = round(float(km), 1)

dc = {k: separation(cv[k]) for k in bands}
dn = {k: separation(nv[k]) for k in bands}
thr = {k: float(np.nanquantile(dn[k][nok], 0.9)) for k in bands}

is_primary = np.array([PRIMARY in p.split("-") for p in cpair])      # exact unit name: lAvf is not lAv
for set_name, sel in (("lAv contacts", is_primary), ("all contacts", np.ones(len(cpair), bool))):
    m = sel & cok & np.all([np.isfinite(dc[k]) for k in bands], axis=0)
    hit = {k: dc[k][m] > thr[k] for k in bands}
    ids = cid[m]
    uniq = np.unique(ids)
    boot = {k: [] for k in bands}
    diff_day, diff_night = [], []
    for _ in range(NBOOT):
        pick = rng.choice(uniq, len(uniq), replace=True)
        w = np.concatenate([np.flatnonzero(ids == u) for u in pick])
        for k in bands:
            boot[k].append(hit[k][w].mean())
        diff_day.append(hit["day_ir"][w].mean() - hit["viking_r"][w].mean())
        diff_night.append(hit["night_ir"][w].mean() - hit["viking_r"][w].mean())
    s = {"profiles": int(m.sum()), "contacts": int(len(uniq)), "bands": {}}
    for k in bands:
        s["bands"][k] = {"null_p90": round(thr[k], 3), "median_d_contact": round(float(np.median(dc[k][m])), 3),
                         "median_d_null": round(float(np.nanmedian(dn[k][nok])), 3),
                         "separates": round(float(hit[k].mean()), 3),
                         "ci95": [round(float(np.quantile(boot[k], q)), 3) for q in (0.025, 0.975)]}
    s["day_minus_viking_r"] = {"diff": round(float(hit["day_ir"].mean() - hit["viking_r"].mean()), 3),
                               "ci95": [round(float(np.quantile(diff_day, q)), 3) for q in (0.025, 0.975)]}
    s["night_minus_viking_r"] = {"diff": round(float(hit["night_ir"].mean() - hit["viking_r"].mean()), 3),
                                 "ci95": [round(float(np.quantile(diff_night, q)), 3) for q in (0.025, 0.975)]}
    s["day_only"] = int((hit["day_ir"] & ~hit["viking_r"]).sum())
    s["viking_only"] = int((hit["viking_r"] & ~hit["day_ir"]).sum())
    s["night_only"] = int((hit["night_ir"] & ~hit["viking_r"]).sum())
    s["viking_only_vs_night"] = int((hit["viking_r"] & ~hit["night_ir"]).sum())
    s["h1_supported"] = bool(s["day_minus_viking_r"]["ci95"][0] > 0 and s["day_only"] > s["viking_only"])
    res["sets"][set_name] = s

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)

print("\nT5 - contacts at Athabasca: share of profiles each band separates (null 90th pct = 10 % by construction)")
for set_name, s in res["sets"].items():
    print("\n%s: %d profiles on %d contacts" % (set_name, s["profiles"], s["contacts"]))
    for k, b in s["bands"].items():
        print("  %-15s %5.1f %%  [%5.1f, %5.1f]   median d %.2f (null %.2f)" % (
            k, 100 * b["separates"], 100 * b["ci95"][0], 100 * b["ci95"][1], b["median_d_contact"], b["median_d_null"]))
    print("  day - Viking red   %+.1f pt [%+.1f, %+.1f]; day-only %d, Viking-only %d" % (
        100 * s["day_minus_viking_r"]["diff"], 100 * s["day_minus_viking_r"]["ci95"][0],
        100 * s["day_minus_viking_r"]["ci95"][1], s["day_only"], s["viking_only"]))
    print("  night - Viking red %+.1f pt [%+.1f, %+.1f]; night-only %d, Viking-only %d" % (
        100 * s["night_minus_viking_r"]["diff"], 100 * s["night_minus_viking_r"]["ci95"][0],
        100 * s["night_minus_viking_r"]["ci95"][1], s["night_only"], s["viking_only_vs_night"]))
    print("  H1 supported by the rule fixed in advance:", s["h1_supported"])
print("\ncontacts by unit pair (km):", res["contacts_by_pair_km"])
log("wrote %s" % OUT)
