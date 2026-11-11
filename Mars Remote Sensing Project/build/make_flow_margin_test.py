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

A9, --topo (NEXT-STEPS §12.2, KB §69.50): T5's day-IR lean (+8.7 pt over Viking red on the lAv contacts, interval
across 0) could be illumination, since day temperature follows the slope's facing to the sun. Day IR and, for a fair
comparison, Viking red are each replaced by their residual from one least-squares fit over the window on the DEM's
topography: the two gradient components (any sun azimuth, to first order), slope and the type area's hillshade
(azimuth 225, altitude 45), all at 100 m. Both residuals are profiled as further bands, with everything else
unchanged; the six original bands must reproduce t5_flow_margins.json exactly or nothing is written. Writes
logs\t5_flow_margins_topo.json. Prediction, written before the first run (2026-11-01), lAv contacts:
  P1  the day-IR residual's lead over Viking red is smaller than the raw +8.7 pt;
  P2  its 95 % interval still includes 0 (H1 still not supported by the rule above);
  P3  topography explains >= 5 % of day IR's variance in the window (R^2), and less of Viking red's.
Each is reported as held or not held. A flow front is itself a slope, so the residual can also remove a real
contact signal: a lean that vanishes is read as "not shown to be material", not as "shown to be illumination".

--margins (KB §69.52): the same test on the lava-flow margins traced on CTX at Athabasca (Landform_LavaFlowMargins,
apply_margin_tracing.py) in place of the 1:20 M contacts; every other part of the design unchanged. They form the
"lAv contacts" set; the registration check is reported, not enforced (a traced edge need not be a map contact).
Writes logs\t5_flow_margins_traced.json. Prediction and rule: logs\agent_review\ctx_margins_registration.md.

--margins --check <margin_check.json> [--keep k|kp] (KB §69.104): only the margins a check kept (since 11-10 the agent's blind second reading, KB §69.105)
(score_margin_check.py's output; k = keep, p = partly), as registered in review_sheets\margins_check\README.md before
any answer: form k first, kp second. Writes logs\t5_flow_margins_checked_<keep>.json. --out <path> writes elsewhere
(for planted runs: a check that keeps all 86 must reproduce t5_flow_margins_traced.json).
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive
import areas

A = dict(areas.AREAS["ath"], key="ath")
WS = on_drive(os.path.join("Mars Project", A["folder"]))   # read only: the folder itself, not its junction
UNITS = os.path.join(GDB, "Ref_SIM3292_GeologicUnits")
TOPO = "--topo" in sys.argv
MARGINS = "--margins" in sys.argv
CHECK = sys.argv[sys.argv.index("--check") + 1] if "--check" in sys.argv else None
KEEP = sys.argv[sys.argv.index("--keep") + 1] if "--keep" in sys.argv else "k"
assert not CHECK or (MARGINS and KEEP in ("k", "kp")), "--check needs --margins and --keep k or kp"
OUT0 = os.path.join(HERE, "logs", "t5_flow_margins.json")
OUT = (os.path.join(HERE, "logs", "t5_flow_margins_checked_%s.json" % KEEP) if CHECK else
       os.path.join(HERE, "logs", "t5_flow_margins_traced.json") if MARGINS else
       os.path.join(HERE, "logs", "t5_flow_margins_topo.json") if TOPO else OUT0)
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else OUT
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
if MARGINS:
    # --margins (KB §69.52): the lines in Landform_LavaFlowMargins (traced on CTX, already in the CM180 frame) take
    # the contacts' place; each is labelled lAv-traced, so the "lAv contacts" set below is the traced set.
    contacts = []
    kept = None
    if CHECK:   # KB §69.104, §69.105: the check, scored by score_margin_check.py
        chk = json.load(open(CHECK, encoding="utf-8"))
        assert chk["answered"] == chk["margins"], "the check is not complete: %d of %d answered" % (chk["answered"], chk["margins"])
        kept = {int(o) for o, a in chk["answers_by_oid"].items() if a in KEEP}
    with arcpy.da.SearchCursor(os.path.join(GDB, "Landform_LavaFlowMargins"), ["OID@", "SHAPE@"]) as c:
        for oid, g in c:
            if kept is not None and oid not in kept:
                continue
            for part in g:
                pts = np.array([(p.X, p.Y) for p in part if p is not None])
                if len(pts) > 1:
                    contacts.append((("lAv", "traced"), pts))
    if not contacts:
        sys.exit("--margins: Landform_LavaFlowMargins holds no lines; nothing written")
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
ORIGINAL = list(bands)
r2 = {}
if TOPO:
    def read1(f):
        path = os.path.join(WS, f)
        r = arcpy.Raster(path)
        assert abs(r.extent.XMin - xmin) < 1 and abs(r.extent.YMax - ymax) < 1 and abs(r.meanCellWidth - RES) < 1e-6, f
        a = arcpy.RasterToNumPyArray(path).astype("float32")
        assert a.shape == (H, W), (f, a.shape)
        if r.noDataValue is not None:
            a[a == r.noDataValue] = np.nan
        return a
    dem = read1("ath_dem.tif")
    gy, gx = np.gradient(dem, RES)
    del dem
    topo = [gx.astype("float32"), gy.astype("float32"), read1("ath_slope_deg.tif"), read1("ath_hillshade.tif")]
    del gx, gy
    for src in ("day_ir", "viking_r"):
        v = bands[src]
        ok = np.isfinite(v) & np.all([np.isfinite(t) for t in topo], axis=0)
        fit = ok.copy(); fit[1::3, :] = False; fit[2::3, :] = False; fit[:, 1::3] = False; fit[:, 2::3] = False
        Xf = np.column_stack([np.ones(fit.sum())] + [t[fit].astype(np.float64) for t in topo])
        coef = np.linalg.lstsq(Xf, v[fit].astype(np.float64), rcond=None)[0]
        res_ = v[fit] - Xf @ coef
        r2[src] = float(1 - res_.var() / v[fit].var())
        out = np.full(v.shape, np.nan, "float32")
        pred = float(coef[0]) + sum(float(c) * t for c, t in zip(coef[1:], topo))     # float32, not float64
        out[ok] = (v - pred)[ok]
        bands[src + "_topo"] = out
        del pred, Xf
        log("%s on topography (gx, gy, slope, hillshade): R^2 %.3f on %d px" % (src, r2[src], fit.sum()))
    del topo

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
    for k in ORIGINAL:                      # T5's own bands decide validity, so --topo leaves T5's profiles alone
        ok &= np.isfinite(vals[k]).all(axis=1)
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
log("registration: contact profiles with different units at +-10 km %.1f %%; null profiles %.1f %%%s"
    % (100 * c_diff[cok].mean(), 100 * n_diff[nok].mean(),
       " (traced margins: a CTX edge need not be a SIM 3292 contact, so this is reported, not a check)" if MARGINS else ""))

# ------------------------------------------------------------------ separation, thresholds, rates
res = {"test": "T5" + (" on CTX-traced margins (KB 69.52)" if MARGINS else "")
        + (", those the check kept (%s; KB 69.104, 69.105)" % KEEP if CHECK else ""), "hypothesis": "H1",
       "prediction": ("H1 not supported: day IR's rate does not exceed Viking red's with an interval above 0 "
                      "(logs/agent_review/ctx_margins_registration.md)" if MARGINS else
                      "Viking red separates at least as many contacts as day IR; IR-only <= Viking-only; night IR fewest; H1 not supported"),
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
    m = sel & cok & np.all([np.isfinite(dc[k]) for k in ORIGINAL], axis=0)
    if TOPO:
        bad = sum(int((~np.isfinite(dc[k][m])).sum()) for k in bands if k not in ORIGINAL)
        if bad:
            sys.exit("%d of T5's profiles have no topography-residual value: nothing written" % bad)
    hit = {k: dc[k][m] > thr[k] for k in bands}
    ids = cid[m]
    uniq = np.unique(ids)
    boot = {k: [] for k in bands}
    diff_day, diff_night, diff_topo, diff_fair = [], [], [], []
    for _ in range(NBOOT):
        pick = rng.choice(uniq, len(uniq), replace=True)
        w = np.concatenate([np.flatnonzero(ids == u) for u in pick])
        for k in bands:
            boot[k].append(hit[k][w].mean())
        diff_day.append(hit["day_ir"][w].mean() - hit["viking_r"][w].mean())
        diff_night.append(hit["night_ir"][w].mean() - hit["viking_r"][w].mean())
        if TOPO:
            diff_topo.append(hit["day_ir_topo"][w].mean() - hit["viking_r"][w].mean())
            diff_fair.append(hit["day_ir_topo"][w].mean() - hit["viking_r_topo"][w].mean())
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
    if TOPO:
        q = lambda a: [round(float(np.quantile(a, x)), 3) for x in (0.025, 0.975)]
        s["day_topo_minus_viking_r"] = {"diff": round(float(hit["day_ir_topo"].mean() - hit["viking_r"].mean()), 3),
                                        "ci95": q(diff_topo)}
        s["day_topo_minus_viking_r_topo"] = {"diff": round(float(hit["day_ir_topo"].mean() - hit["viking_r_topo"].mean()), 3),
                                             "ci95": q(diff_fair)}
        s["day_topo_only"] = int((hit["day_ir_topo"] & ~hit["viking_r"]).sum())
        s["viking_only_vs_day_topo"] = int((hit["viking_r"] & ~hit["day_ir_topo"]).sum())
        s["h1_supported_topo"] = bool(s["day_topo_minus_viking_r"]["ci95"][0] > 0
                                      and s["day_topo_only"] > s["viking_only_vs_day_topo"])
    res["sets"][set_name] = s

if TOPO:
    ref = json.load(open(OUT0, encoding="utf-8"))["sets"]
    same = all(res["sets"][n]["bands"][k] == ref[n]["bands"][k] and
               res["sets"][n]["day_minus_viking_r"] == ref[n]["day_minus_viking_r"] for n in ref for k in ORIGINAL)
    log("check: the six original bands %s t5_flow_margins.json" % ("reproduce" if same else "DO NOT reproduce"))
    if not same:
        sys.exit("the check failed: nothing written")
    lav = res["sets"]["lAv contacts"]
    res["a9"] = {"r2": {k: round(v, 4) for k, v in r2.items()},
                 "predictions": {
                     "P1 the residual's lead < raw +8.7 pt": lav["day_topo_minus_viking_r"]["diff"] < lav["day_minus_viking_r"]["diff"],
                     "P2 its interval includes 0": lav["day_topo_minus_viking_r"]["ci95"][0] <= 0 <= lav["day_topo_minus_viking_r"]["ci95"][1],
                     "P3 R^2 day >= 0.05 and > Viking red's": r2["day_ir"] >= 0.05 and r2["day_ir"] > r2["viking_r"]}}

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
    if TOPO:
        for key, lab in (("day_topo_minus_viking_r", "day(topo) - Viking red     "),
                         ("day_topo_minus_viking_r_topo", "day(topo) - Viking red(topo)")):
            print("  %s %+.1f pt [%+.1f, %+.1f]" % (lab, 100 * s[key]["diff"], 100 * s[key]["ci95"][0], 100 * s[key]["ci95"][1]))
        print("  day(topo)-only %d, Viking-only %d; H1 supported on the residual: %s" % (
            s["day_topo_only"], s["viking_only_vs_day_topo"], s["h1_supported_topo"]))
if TOPO:
    print("\nA9:", res["a9"])
print("\ncontacts by unit pair (km):", res["contacts_by_pair_km"])
log("wrote %s" % OUT)
