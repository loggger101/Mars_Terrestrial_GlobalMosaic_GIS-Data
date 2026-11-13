# -*- coding: utf-8 -*-
r"""Test T4, stage 2 (H2): fluvial against volcanic channels whose origin geologists mapped (KB §69.133).

H2, from the prospectus: fluvial channels have shallower gradients than volcanic ones, and the two separate on gradient
against thermal response. Stage 1 (make_t4_channel_h2.py) let the type area stand in for origin and stage 1b
(make_t4_channel_origin.py) took origin from two reference maps for routed segments; stage 2 was to use channels whose
origin is known, in a window that holds both (KB §51.1, §69.63). The USGS geologic map (SIM 3292, Tanaka et al. 2014)
maps such channels in its structure layer (`SIM3292_Global_Structure`, held since 2026-10-08 in
`Mars Project\Reference\SIM3292_geologic_map\`): Interpretation "Rille" (Origin Volcanic, 18 lines) and "Channel axis" and
"Outflow Channel" (Origin Fluvial, 568 lines). Five 15 deg blocks hold both (found 2026-11-12 before this was written:
-120/-45, 105/-30, 75/0, 150/15, -120/15 by south-west corner).

Measures, close to stages 1 and 1b: each line sampled every 1 km along its length (lon/lat interpolation between its
vertices, ground distance by the haversine); the floor at each sample is the lowest DEM value within 1 km (11 x 11
pixels of the 200 m DEM: a line drawn at 1:20 M is not on the floor); each line cut into consecutive 10 km pieces;
gradient = |floor(end) - floor(start)| / 10 km, m per km; thermal response = the mean of the diurnal-contrast index over
the piece's samples as a z-score against its own 15 deg block (every 4th pixel each way), as stage 1b.

Two scopes: SHARED, the pieces inside the five blocks that hold both origins (the window stage 2 asked for, primary),
and ALL, every piece within 60 deg. Separation: medians, Cohen's d of log10 gradient and of thermal z, Mann-Whitney AUC
of each. Intervals: 2,000 resamples of whole LINES, each origin's lines drawn separately (pieces of one line are not
independent).

Verdict rule, stages 1 and 1b's unchanged: CONSISTENT with H2 only if (a) the volcanic median gradient exceeds the fluvial
one with the interval of the difference above zero, AND (b) thermal z differs with |d| >= 0.5 and its interval
excluding zero; otherwise NOT SUPPORTED.

Predictions, written 2026-11-12 before the first run (SHARED scope):
  P1  H2's gradient direction holds here: the rilles lie on volcano flanks (Tharsis, Elysium), so the volcanic median
      gradient exceeds the fluvial one with its interval above zero.
  P2  Thermal does not separate them: |d| < 0.5.
  P3  So the verdict is NOT SUPPORTED, now on (b) alone.
  P4  In the ALL scope the gradient direction also holds.

  "<ArcGIS Pro Python>" make_t4_channel_sim3292.py   -> logs\t4_channel_sim3292.json
"""
import os, sys, json, math, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import numpy as np
from scipy import ndimage
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G

gdal.UseExceptions()
OUT = os.path.join(HERE, "logs", "t4_channel_sim3292.json")
STRUCT = os.path.join(os.path.dirname(G.OUTDIR), "Reference", "SIM3292_geologic_map", "SIM3292_MarsGlobalGeologicGIS_20M",
                      "SIM3292_geodatabase.gdb", "SIM3292_MGM_Robinson_Mars2000_Sphere", "SIM3292_Global_Structure")
DEM = os.path.join(G.OUTDIR, "global60_dem.tif")
IDX = os.path.join(G.OUTDIR, "global60_thermal_contrast_200m.tif")
ORIGIN = {"Rille": "volcanic", "Channel axis": "fluvial", "Outflow Channel": "fluvial"}
SHARED = [(-120, -45), (105, -30), (75, 0), (150, 15), (-120, 15)]
STEP_KM, PIECE_KM, FLOOR_PX, BLOCK, NBOOT, SEED = 1.0, 10, 5, 15.0, 2000, 20261112
PX, OX, OY = 200.0, -10669400.0, 3556500.0
RKM = G.R_MARS / 1000.0
t0 = time.time()
rng = np.random.default_rng(SEED)


def log(m):
    print("[%6.1fs] %s" % (time.time() - t0, m), flush=True)


def hav(lo1, la1, lo2, la2):
    lo1, la1, lo2, la2 = map(np.radians, (lo1, la1, lo2, la2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * RKM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def read_lines():
    import arcpy
    lines = []
    with arcpy.da.SearchCursor(STRUCT, ["OID@", "Interpretation", "SHAPE@"],
                               spatial_reference=arcpy.SpatialReference(104905)) as cur:
        for oid, interp, shp in cur:
            if interp not in ORIGIN:
                continue
            for part in shp:
                pts = [(p.X, p.Y) for p in part if p is not None]
                if len(pts) >= 2:
                    lines.append((oid, ORIGIN[interp], np.array(pts)))
    return lines


def densify(pts):
    lo, la = pts[:, 0].copy(), pts[:, 1]
    lo = np.degrees(np.unwrap(np.radians(lo)))
    d = np.r_[0, np.cumsum(hav(lo[:-1], la[:-1], lo[1:], la[1:]))]
    s = np.arange(0, d[-1] + 1e-9, STEP_KM)
    return (np.interp(s, d, lo) + 180) % 360 - 180, np.interp(s, d, la)


def to_px(lon, lat):
    x = G.R_MARS * np.radians((lon - 180.0 + 180.0) % 360.0 - 180.0)
    y = G.R_MARS * np.radians(lat)
    return ((x - OX) / PX).astype(np.int64), ((OY - y) / PX).astype(np.int64)


def sample(lon, lat):
    """Floor (min DEM within 1 km) and index at each sample, and each 15 deg block's index mean and sd."""
    col, row = to_px(lon, lat)
    dsd, dsi = gdal.Open(DEM), gdal.Open(IDX)
    bd, bi = dsd.GetRasterBand(1), dsi.GetRasterBand(1)
    W, H = dsd.RasterXSize, dsd.RasterYSize
    col = np.clip(col, 0, W - 1); row = np.clip(row, 0, H - 1)
    ndd, ndi = bd.GetNoDataValue(), bi.GetNoDataValue()
    floor = np.full(row.size, np.nan); tv = np.full(row.size, np.nan)
    nbx, nby = int(360 / BLOCK), int(120 / BLOCK)
    bsum, bsq, bn = np.zeros((nby, nbx)), np.zeros((nby, nbx)), np.zeros((nby, nbx))
    lat_px = np.degrees((OY - (np.arange(H) + 0.5) * PX) / G.R_MARS)
    lon_px = (np.arange(W) + 0.5) * 360.0 / W
    bx_col = np.minimum((lon_px / BLOCK).astype(int), nbx - 1)
    order = np.argsort(row, kind="stable"); rs = row[order]
    S = 512
    for r0 in range(0, H, S):
        r1 = min(H, r0 + S)
        a0, a1 = max(0, r0 - FLOOR_PX), min(H, r1 + FLOOR_PX)
        a, b = np.searchsorted(rs, r0), np.searchsorted(rs, r1)
        i = order[a:b]
        t = bi.ReadAsArray(0, r0, W, r1 - r0)
        if i.size:
            d = bd.ReadAsArray(0, a0, W, a1 - a0).astype(np.float64)
            d[d == ndd] = np.inf
            for k in i:                                      # the lowest value within 1 km, wrapping at the seam
                rr = slice(row[k] - a0 - FLOOR_PX, row[k] - a0 + FLOOR_PX + 1)
                cc = np.arange(col[k] - FLOOR_PX, col[k] + FLOOR_PX + 1) % W
                m = d[max(rr.start, 0):rr.stop][:, cc].min()
                floor[k] = m if np.isfinite(m) else np.nan
            v = t[row[i] - r0, col[i]]
            tv[i] = np.where(v == ndi, np.nan, v)
        sub = t[::4, ::4].astype(np.float64); ok = sub != ndi
        by = np.minimum(((60.0 - lat_px[r0:r1:4]) / BLOCK).astype(int), nby - 1)
        bx = bx_col[::4]
        for kk in np.unique(by):
            rk = by == kk
            s, okk = sub[rk], ok[rk]
            bb = np.broadcast_to(bx, s.shape)[okk]
            bsum[kk] += np.bincount(bb, weights=s[okk], minlength=nbx)
            bsq[kk] += np.bincount(bb, weights=s[okk] ** 2, minlength=nbx)
            bn[kk] += np.bincount(bb, minlength=nbx)
        if r0 % (S * 20) == 0:
            log("  strip %d / %d" % (r0 // S + 1, (H + S - 1) // S))
    for k in rng.choice(row.size, 25, replace=False):           # the check: single reads equal the strip reads
        v = bi.ReadAsArray(int(col[k]), int(row[k]), 1, 1)[0, 0]
        assert (np.isnan(tv[k]) and v == ndi) or tv[k] == v
        r_lo, r_hi = max(0, row[k] - FLOOR_PX), min(H, row[k] + FLOOR_PX + 1)
        c_lo = int(col[k]) - FLOOR_PX
        if 0 <= c_lo and c_lo + 2 * FLOOR_PX + 1 <= W:
            w = bd.ReadAsArray(c_lo, int(r_lo), 2 * FLOOR_PX + 1, int(r_hi - r_lo)).astype(np.float64)
            w[w == ndd] = np.inf
            m = w.min()
            assert (np.isnan(floor[k]) and not np.isfinite(m)) or floor[k] == m
    log("check: 25 single-window reads match the strip reads")
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = bsum / bn; sd = np.sqrt(bsq / bn - mean ** 2)
    return floor, tv, mean, sd


def cohen_d(a, b):
    sp = math.sqrt(((a.size - 1) * a.var(ddof=1) + (b.size - 1) * b.var(ddof=1)) / (a.size + b.size - 2))
    return (b.mean() - a.mean()) / sp


def auc(pos, neg):
    """P(pos > neg) + 0.5 ties, by ranks."""
    allv = np.r_[pos, neg]
    r = np.argsort(np.argsort(allv, kind="mergesort"), kind="mergesort") + 1.0
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); r = (csum - (cnt - 1) / 2.0)[inv]
    return (r[:pos.size].sum() - pos.size * (pos.size + 1) / 2) / (pos.size * neg.size)


def scope_stats(P, sel):
    out = {}
    f, v = sel & (P["origin"] == "fluvial"), sel & (P["origin"] == "volcanic")
    lf, lv = np.unique(P["line"][f]), np.unique(P["line"][v])
    out["pieces"] = {"fluvial": int(f.sum()), "volcanic": int(v.sum())}
    out["lines"] = {"fluvial": int(lf.size), "volcanic": int(lv.size)}
    g, z = P["grad"], P["tz"]
    lg = np.log10(np.maximum(g, 0.01))
    out["median_gradient"] = {"fluvial": float(np.median(g[f])), "volcanic": float(np.median(g[v]))}
    out["d_log_gradient"] = float(cohen_d(lg[f], lg[v]))
    out["d_thermal"] = float(cohen_d(z[f], z[v]))
    out["auc_gradient"] = float(auc(g[v], g[f]))          # volcanic steeper -> > 0.5
    out["auc_thermal"] = float(max(auc(z[v], z[f]), 1 - auc(z[v], z[f])))
    by_f = {l: np.flatnonzero(f & (P["line"] == l)) for l in lf}
    by_v = {l: np.flatnonzero(v & (P["line"] == l)) for l in lv}
    dm, dd = [], []
    for _ in range(NBOOT):
        i_f = np.concatenate([by_f[l] for l in rng.choice(lf, lf.size)])
        i_v = np.concatenate([by_v[l] for l in rng.choice(lv, lv.size)])
        dm.append(np.median(g[i_v]) - np.median(g[i_f]))
        dd.append(cohen_d(z[i_f], z[i_v]))
    ci = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    out["median_difference_volc_minus_fluv"] = float(out["median_gradient"]["volcanic"] - out["median_gradient"]["fluvial"])
    out["median_difference_ci95"] = ci(dm)
    out["d_thermal_ci95"] = ci(dd)
    a_ok = out["median_difference_ci95"][0] > 0
    b_ok = abs(out["d_thermal"]) >= 0.5 and (out["d_thermal_ci95"][0] > 0 or out["d_thermal_ci95"][1] < 0)
    out["verdict"] = "CONSISTENT with H2" if (a_ok and b_ok) else "NOT SUPPORTED"
    out["gradient_direction_holds"] = bool(a_ok)
    return out


def main():
    lines = read_lines()
    log("SIM 3292 channels: %d line parts (%d volcanic, %d fluvial)" % (
        len(lines), sum(o == "volcanic" for _, o, _ in lines), sum(o == "fluvial" for _, o, _ in lines)))
    lon, lat, lid, org, idx = [], [], [], [], []
    for n, (oid, o, pts) in enumerate(lines):
        lo, la = densify(pts)
        lon.append(lo); lat.append(la); lid.append(np.full(lo.size, n)); org += [o] * lo.size
        idx.append(np.arange(lo.size))
    lon, lat, lid, idx = map(np.concatenate, (lon, lat, lid, idx)); org = np.array(org)
    inside = np.abs(lat) <= 60
    log("%d samples at %.0f km, %d within 60 deg" % (lon.size, STEP_KM, inside.sum()))
    floor, tv, bmean, bsd = sample(lon[inside], lat[inside])
    F = np.full(lon.size, np.nan); T = np.full(lon.size, np.nan)
    F[inside], T[inside] = floor, tv
    by = np.minimum(((60.0 - lat) / BLOCK).astype(int), int(120 / BLOCK) - 1).clip(0)
    bx = np.minimum((((lon % 360.0)) / BLOCK).astype(int), int(360 / BLOCK) - 1)
    with np.errstate(invalid="ignore"):
        TZ = (T - bmean[by, bx]) / bsd[by, bx]
    piece = idx // PIECE_KM
    P = {"line": [], "origin": [], "grad": [], "tz": [], "lon": [], "lat": []}
    for n in range(len(lines)):
        m = lid == n
        for k in np.unique(piece[m]):
            q = np.flatnonzero(m & (idx >= k * PIECE_KM) & (idx <= (k + 1) * PIECE_KM))   # 11 samples, 10 km
            if q.size != PIECE_KM + 1:                                                  # full pieces only
                continue
            if not (inside[q].all() and np.isfinite(F[q[[0, -1]]]).all() and np.isfinite(TZ[q]).any()):
                continue
            P["line"].append(n); P["origin"].append(org[q[0]])
            P["grad"].append(abs(F[q[-1]] - F[q[0]]) / ((q.size - 1) * STEP_KM))
            P["tz"].append(np.nanmean(TZ[q])); P["lon"].append(lon[q].mean()); P["lat"].append(lat[q].mean())
    P = {k: np.array(v) for k, v in P.items()}
    blk = [(int(math.floor(lo / BLOCK) * BLOCK), int(math.floor(la / BLOCK) * BLOCK)) for lo, la in zip(P["lon"], P["lat"])]
    shared = np.array([b in SHARED for b in blk])
    res = {"source": "SIM 3292 SIM3292_Global_Structure: Rille (volcanic), Channel axis and Outflow Channel (fluvial)",
           "step_km": STEP_KM, "piece_km": PIECE_KM, "floor_window_km": 2 * FLOOR_PX * PX / 1000 / 2,
           "shared_blocks": SHARED, "scopes": {}}
    for name, sel in (("shared", shared), ("all", np.ones(shared.size, bool))):
        s = scope_stats(P, sel)
        res["scopes"][name] = s
        log("%-6s pieces fluvial %d (%d lines), volcanic %d (%d lines)" % (name, s["pieces"]["fluvial"], s["lines"]["fluvial"],
            s["pieces"]["volcanic"], s["lines"]["volcanic"]))
        log("%-6s median gradient fluvial %.2f, volcanic %.2f m/km; volcanic - fluvial %+.2f [%+.2f, %+.2f]" % (
            name, s["median_gradient"]["fluvial"], s["median_gradient"]["volcanic"], s["median_difference_volc_minus_fluv"],
            *s["median_difference_ci95"]))
        log("%-6s d log gradient %+.2f, d thermal %+.2f [%+.2f, %+.2f]; AUC gradient %.2f, thermal %.2f; %s" % (
            name, s["d_log_gradient"], s["d_thermal"], *s["d_thermal_ci95"], s["auc_gradient"], s["auc_thermal"], s["verdict"]))
    sh, al = res["scopes"]["shared"], res["scopes"]["all"]
    res["predictions"] = {"P1 shared: volcanic steeper, interval above 0": sh["gradient_direction_holds"],
                          "P2 shared: |d thermal| < 0.5": abs(sh["d_thermal"]) < 0.5,
                          "P3 shared: NOT SUPPORTED": sh["verdict"] == "NOT SUPPORTED",
                          "P4 all: volcanic steeper, interval above 0": al["gradient_direction_holds"]}
    for k, v in res["predictions"].items():
        log("prediction %-50s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
