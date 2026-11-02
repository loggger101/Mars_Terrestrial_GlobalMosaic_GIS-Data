# -*- coding: utf-8 -*-
r"""Test T4, stage 1b (H2): fluvial against volcanic channels, by reference origin rather than by window (NEXT-STEPS §12.2
A7; KB §51.1, §69.50).

H2, from the prospectus: fluvial channels have shallower gradients than volcanic ones, and the two separate on
gradient against thermal response. Stage 1 (make_t4_channel_h2.py) let the window stand in for origin (Ius against
Athabasca) and found the window, not the origin, set the result. Stage 1b takes origin from two independent maps over
the whole ±60° network (Landform_ChannelCandidates_auto_60, 969,822 routed segments, KB §53):
  fluvial    a segment whose middle vertex lies within 2 km of an Alemanno & Orofino (2017) valley (KB §68.5);
  volcanic   a segment whose middle vertex lies on a SIM 3292 volcanic unit (UnitGroup v, ve or vf, the groups of
             KB §69.37) and more than 25 km from any mapped valley.
Still a stand-in: a routed segment near a mapped valley is not proven fluvial, and one on a lava unit not proven
volcanic. Stage 2 (reviewed channels with Origin) stays the authority if the review reaches it.

Measures, as stage 1: gradient = |z(first vertex) - z(last vertex)| / LengthKm, m per km, on the 200 m DEM
(global60_dem.tif); thermal response = the mean of the diurnal-contrast index (global60_thermal_contrast_200m.tif)
over the segment's vertices, as a z-score against its own 15° block's index (every 4th pixel each way), since the
index is relative within a region (KB §28.10). Segments >= 1 km; primary set Strahler order >= 2 (less DEM noise),
also all orders. Separation: medians, Cohen's d of log10 gradient and of thermal z, and the 5-fold cross-validated
AUC of a logistic regression (at most 20,000 segments of each origin, drawn at random). Intervals: 2,000 bootstrap
resamples of 50 km x 50 km cells, each origin's cells drawn separately, as stage 1.

Verdict rule, stage 1's unchanged: CONSISTENT with H2 only if (a) the volcanic median gradient exceeds the fluvial
one with the interval of the difference above zero, AND (b) thermal z differs with |d| >= 0.5 and its interval
excluding zero; otherwise NOT SUPPORTED.

Prediction, written before the first run (2026-11-01), order >= 2:
  P1  H2's gradient direction fails again: the volcanic median gradient does not exceed the fluvial one with its
      interval above zero (the valleys cut the rough highlands, the volcanic units are mostly plains);
  P2  thermal does not separate them: |d| < 0.5;
  P3  so the verdict is NOT SUPPORTED.
Each is reported as held or not held.

  "<ArcGIS Pro Python>" make_t4_channel_origin.py   -> logs\t4_channel_origin.json  (reads the drive only; ~10 GB read)
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import numpy as np
from scipy.spatial import cKDTree
import arcpy
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import grid60 as G
import make_channel_valley_check as A1
from make_t4_channel_h2 import auc

gdal.UseExceptions()
OUT = os.path.join(HERE, "logs", "t4_channel_origin.json")
CHANNELS = os.path.join(GDB, "Landform_ChannelCandidates_auto_60")
DEM = os.path.join(G.OUTDIR, "global60_dem.tif")
IDX = os.path.join(G.OUTDIR, "global60_thermal_contrast_200m.tif")
FLUVIAL_KM, VOLC_OFF_KM, VOLC_GROUPS = 2.0, 25.0, ("v", "ve", "vf")
MIN_KM, NBOOT, CELL, SEED, NAUC, STRIP, BLOCK = 1.0, 2000, 50000.0, 20261101, 20000, 512, 15.0
PX = 200.0
OX, OY = -10669400.0, 3556500.0
t0 = time.time()
rng = np.random.default_rng(SEED)


def log(msg):
    print("[%6.1fs] %s" % (time.time() - t0, msg), flush=True)


def read_segments():
    a = arcpy.da.FeatureClassToNumPyArray(CHANNELS, ["OID@", "SHAPE@X", "SHAPE@Y", "StrahlerOrd", "LengthKm"],
                                          explode_to_points=True)
    oid, x, y = a["OID@"], a["SHAPE@X"], a["SHAPE@Y"]
    order, km = a["StrahlerOrd"].astype(np.int16), a["LengthKm"].astype(np.float64)
    del a
    start = np.r_[True, oid[1:] != oid[:-1]]
    first = np.flatnonzero(start)
    last = np.r_[first[1:] - 1, oid.size - 1]
    seg = np.cumsum(start) - 1                                          # segment index of each vertex
    log("channels: %d vertices in %d segments" % (oid.size, first.size))
    return dict(x=x, y=y, seg=seg, first=first, last=last, mid=(first + last) // 2,
                order=order[first], km=km[first])


def sample(S):
    """DEM at each segment's ends, the index's mean over its vertices, and each 15° block's index mean and sd,
    reading both rasters in strips of rows."""
    col = ((S["x"] - OX) / PX).astype(np.int64)
    row = ((OY - S["y"]) / PX).astype(np.int64)
    dsd, dsi = gdal.Open(DEM), gdal.Open(IDX)
    bd, bi = dsd.GetRasterBand(1), dsi.GetRasterBand(1)
    W, H = dsd.RasterXSize, dsd.RasterYSize
    assert dsd.GetGeoTransform() == dsi.GetGeoTransform() == (OX, PX, 0.0, OY, 0.0, -PX), "grids differ"
    col = np.clip(col, 0, W - 1); row = np.clip(row, 0, H - 1)
    nd_d, nd_i = bd.GetNoDataValue(), bi.GetNoDataValue()
    ends = np.r_[S["first"], S["last"]]
    zend = np.full(ends.size, np.nan)
    tv = np.full(row.size, np.nan, np.float32)
    nbx, nby = int(360 / BLOCK), int(120 / BLOCK)
    bsum, bsq, bn = np.zeros((nby, nbx)), np.zeros((nby, nbx)), np.zeros((nby, nbx))
    lat_px = np.degrees((OY - (np.arange(H) + 0.5) * PX) / G.R_MARS)
    lon_px = (np.arange(W) + 0.5) * 360.0 / W                           # columns are east longitude from 0°
    bx_col = np.minimum((lon_px / BLOCK).astype(int), nbx - 1)
    order_v = np.argsort(row, kind="stable"); rs = row[order_v]
    order_e = np.argsort(row[ends], kind="stable"); re_ = row[ends][order_e]
    for r0 in range(0, H, STRIP):
        r1 = min(H, r0 + STRIP)
        d = bd.ReadAsArray(0, r0, W, r1 - r0)
        t = bi.ReadAsArray(0, r0, W, r1 - r0)
        a, b = np.searchsorted(rs, r0), np.searchsorted(rs, r1)
        i = order_v[a:b]
        v = t[row[i] - r0, col[i]]
        tv[i] = np.where(v == nd_i, np.nan, v)
        a, b = np.searchsorted(re_, r0), np.searchsorted(re_, r1)
        j = order_e[a:b]
        v = d[row[ends[j]] - r0, col[ends[j]]]
        zend[j] = np.where(v == nd_d, np.nan, v)
        sub = t[::4, ::4].astype(np.float64)
        ok = sub != nd_i
        by = np.minimum(((60.0 - lat_px[r0:r1:4]) / BLOCK).astype(int), nby - 1)
        bx = bx_col[::4]
        for k in np.unique(by):
            rows_k = by == k
            s, okk = sub[rows_k], ok[rows_k]
            bsum[k] += np.bincount(np.broadcast_to(bx, s.shape)[okk], weights=s[okk], minlength=nbx)
            bsq[k] += np.bincount(np.broadcast_to(bx, s.shape)[okk], weights=s[okk] ** 2, minlength=nbx)
            bn[k] += np.bincount(np.broadcast_to(bx, s.shape)[okk], minlength=nbx)
        if r0 % (STRIP * 10) == 0:
            log("  strip %d / %d" % (r0 // STRIP + 1, (H + STRIP - 1) // STRIP))
    # the check: 25 vertices read one pixel at a time must match the strip reads
    for k in rng.choice(row.size, 25, replace=False):
        v = bi.ReadAsArray(int(col[k]), int(row[k]), 1, 1)[0, 0]
        assert (np.isnan(tv[k]) and v == nd_i) or tv[k] == v, ("index sample", k, tv[k], v)
    for k in rng.choice(ends.size, 25, replace=False):
        v = bd.ReadAsArray(int(col[ends[k]]), int(row[ends[k]]), 1, 1)[0, 0]
        assert (np.isnan(zend[k]) and v == nd_d) or zend[k] == v, ("dem sample", k, zend[k], v)
    log("check: 50 single-pixel reads match the strip reads")
    n = S["first"].size
    ok = np.isfinite(tv)
    tsum = np.bincount(S["seg"][ok], weights=tv[ok].astype(np.float64), minlength=n)
    tcnt = np.bincount(S["seg"][ok], minlength=n)
    with np.errstate(invalid="ignore", divide="ignore"):
        therm = tsum / tcnt
        bmean = bsum / bn
        bsd = np.sqrt(bsq / bn - bmean ** 2)
    xm, ym = S["x"][S["mid"]], S["y"][S["mid"]]
    lat = np.degrees(ym / G.R_MARS)
    lon360 = (np.degrees(xm / G.R_MARS) + 180.0) % 360.0
    by = np.clip(((60.0 - lat) / BLOCK).astype(int), 0, nby - 1)
    bx = np.clip((lon360 / BLOCK).astype(int), 0, nbx - 1)
    tz = (therm - bmean[by, bx]) / bsd[by, bx]
    grad = np.abs(zend[:n] - zend[n:]) / S["km"]
    return dict(grad=grad, tz=tz, lat=lat, lon=(lon360 + 180.0) % 360.0 - 180.0, xm=xm, ym=ym,
                block_index=dict(mean=bmean.round(3).tolist(), sd=bsd.round(3).tolist()))


def wmedian(v, w):
    o = np.argsort(v); c = np.cumsum(w[o])
    return v[o][np.searchsorted(c, c[-1] / 2.0)]


def wd(a, wa, b, wb):
    """Cohen's d of b against a, each value weighted (bootstrap multiplicities)."""
    ma, mb = np.average(a, weights=wa), np.average(b, weights=wb)
    va, vb = np.average((a - ma) ** 2, weights=wa), np.average((b - mb) ** 2, weights=wb)
    return (mb - ma) / np.sqrt((va + vb) / 2)


def cv_auc(X, y, k=5):
    idx = rng.permutation(len(y)); folds = np.array_split(idx, k); scores = np.empty(len(y))
    for f in folds:
        tr = np.setdiff1d(idx, f)
        mu, sd = X[tr].mean(0), X[tr].std(0); sd[sd == 0] = 1
        A = np.c_[np.ones(len(tr)), (X[tr] - mu) / sd]; w = np.zeros(A.shape[1])
        for _ in range(25):
            p = 1 / (1 + np.exp(-A @ w)); Hs = A.T @ (A * (p * (1 - p))[:, None]) + 1e-6 * np.eye(len(w))
            w -= np.linalg.solve(Hs, A.T @ (p - y[tr]))
        scores[f] = np.c_[np.ones(len(f)), (X[f] - mu) / sd] @ w
    return auc(scores, y)


def compare(F, V):
    """V (volcanic) against F (fluvial): point values, AUCs, and the cell bootstrap."""
    lg = lambda g: np.log10(g + 0.01)
    out = dict(n_fluvial=int(F["grad"].size), n_volcanic=int(V["grad"].size),
               grad_median_fluvial=float(np.median(F["grad"])), grad_median_volcanic=float(np.median(V["grad"])))
    out["grad_median_diff"] = out["grad_median_volcanic"] - out["grad_median_fluvial"]
    one_f, one_v = np.ones(F["grad"].size), np.ones(V["grad"].size)
    out["d_log_grad"] = float(wd(lg(F["grad"]), one_f, lg(V["grad"]), one_v))
    out["d_thermal"] = float(wd(F["tz"], one_f, V["tz"], one_v))
    out["therm_z_mean_fluvial"], out["therm_z_mean_volcanic"] = float(F["tz"].mean()), float(V["tz"].mean())
    pf = rng.choice(F["grad"].size, min(NAUC, F["grad"].size), replace=False)
    pv = rng.choice(V["grad"].size, min(NAUC, V["grad"].size), replace=False)
    X = np.r_[np.c_[lg(F["grad"][pf]), F["tz"][pf]], np.c_[lg(V["grad"][pv]), V["tz"][pv]]]
    y = np.r_[np.zeros(pf.size), np.ones(pv.size)]
    out["auc_both"], out["auc_gradient"], out["auc_thermal"] = cv_auc(X, y), cv_auc(X[:, :1], y), cv_auc(X[:, 1:], y)
    cells = {}
    for name, S in (("f", F), ("v", V)):
        _, inv = np.unique(np.c_[np.floor(S["xm"] / CELL), np.floor(S["ym"] / CELL)], axis=0, return_inverse=True)
        cells[name] = inv.ravel()
    out["cells_fluvial"], out["cells_volcanic"] = int(cells["f"].max() + 1), int(cells["v"].max() + 1)
    boot = {k: [] for k in ("grad_median_diff", "d_log_grad", "d_thermal")}
    for _ in range(NBOOT):
        w = {}
        for name in ("f", "v"):
            nc = cells[name].max() + 1
            cnt = np.bincount(rng.integers(0, nc, nc), minlength=nc)
            w[name] = cnt[cells[name]].astype(np.float64)
        mf, mv = w["f"] > 0, w["v"] > 0
        boot["grad_median_diff"].append(wmedian(V["grad"][mv], w["v"][mv]) - wmedian(F["grad"][mf], w["f"][mf]))
        boot["d_log_grad"].append(wd(lg(F["grad"][mf]), w["f"][mf], lg(V["grad"][mv]), w["v"][mv]))
        boot["d_thermal"].append(wd(F["tz"][mf], w["f"][mf], V["tz"][mv], w["v"][mv]))
    for k, v in boot.items():
        out[k + "_ci95"] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    a = out["grad_median_diff_ci95"][0] > 0
    b = abs(out["d_thermal"]) >= 0.5 and (out["d_thermal_ci95"][0] > 0 or out["d_thermal_ci95"][1] < 0)
    out["verdict"] = dict(gradient_volcanic_steeper=bool(a), thermal_separates=bool(b),
                          stage1b="CONSISTENT with H2 (reference origin)" if a and b else "NOT SUPPORTED at stage 1b")
    return out


def selftest():
    """The weighted statistics against their unweighted forms, and a planted shift, before real data."""
    v = rng.normal(0, 1, 1001); w = np.ones(v.size)
    a, b = rng.normal(0, 1, 3000), rng.normal(0.8, 1, 3000)
    w2 = rng.integers(1, 4, 3000).astype(float)
    checks = {"weighted median = median": wmedian(v, w) == np.median(v),
              "weighted d = d with unit weights": abs(wd(a, np.ones(3000), b, np.ones(3000))
                                                      - (b.mean() - a.mean()) / np.sqrt((a.var() + b.var()) / 2)) < 1e-12,
              "d of a 0.8 sd shift 0.65-0.95": 0.65 < wd(a, w2, b, w2) < 0.95,
              "weights 2 = values twice": abs(wmedian(v, 2 * w) - np.median(np.r_[v, v])) < 1e-12}
    for k, ok in checks.items():
        log("selftest %-34s %s" % (k, "ok" if ok else "FAIL"))
    assert all(checks.values()), "statistics self-test failed"


def main():
    selftest()
    S = read_segments()
    M = sample(S)
    del S["x"], S["y"], S["seg"]
    vlon, vlat, vkm = A1.read_valleys()
    tree = cKDTree(A1.unit(vlon, vlat))
    dist, _ = tree.query(A1.unit(M["lon"], M["lat"]), k=1, distance_upper_bound=(VOLC_OFF_KM + 1) / A1.R_KM)
    dist_km = dist * A1.R_KM                                            # inf beyond 26 km
    grp = A1.unit_groups(M["lon"], M["lat"])
    ok = (S["km"] >= MIN_KM) & np.isfinite(M["grad"]) & np.isfinite(M["tz"]) & (np.abs(M["lat"]) <= 60.0)
    fluv = ok & (dist_km <= FLUVIAL_KM)
    volc = ok & np.isin(grp, VOLC_GROUPS) & (dist_km > VOLC_OFF_KM)
    log("segments >= %.0f km with both measures: %d; fluvial %d, volcanic %d" % (MIN_KM, ok.sum(), fluv.sum(), volc.sum()))
    res = {"test": "T4 stage 1b", "hypothesis": "H2",
           "design": dict(fluvial_km=FLUVIAL_KM, volcanic_groups=VOLC_GROUPS, volcanic_off_valley_km=VOLC_OFF_KM,
                          min_km=MIN_KM, boot=NBOOT, cell_m=CELL, seed=SEED, auc_max_per_origin=NAUC,
                          block_deg=BLOCK, valley_sha256=A1.VALLEY_SHA),
           "counts": dict(segments=int(ok.size), usable=int(ok.sum()), fluvial=int(fluv.sum()), volcanic=int(volc.sum()),
                          volcanic_by_group={g: int((volc & (grp == g)).sum()) for g in VOLC_GROUPS}),
           "block_index": M["block_index"]}
    for name, sel in (("order >= 2", S["order"] >= 2), ("all orders", np.ones(ok.size, bool))):
        pick = lambda m: {k: M[k][m & sel] for k in ("grad", "tz", "xm", "ym")}
        r = compare(pick(fluv), pick(volc))
        res[name] = r
        log("%s: n %d / %d; median gradient %.2f vs %.2f m/km (diff %+.2f [%+.2f, %+.2f]); d log gradient %+.2f; "
            "d thermal %+.2f [%+.2f, %+.2f]; AUC both %.2f, gradient %.2f, thermal %.2f -> %s"
            % (name, r["n_fluvial"], r["n_volcanic"], r["grad_median_fluvial"], r["grad_median_volcanic"],
               r["grad_median_diff"], *r["grad_median_diff_ci95"], r["d_log_grad"], r["d_thermal"],
               *r["d_thermal_ci95"], r["auc_both"], r["auc_gradient"], r["auc_thermal"], r["verdict"]["stage1b"]))
    p = res["order >= 2"]
    res["predictions"] = {"P1 the gradient direction fails": not p["verdict"]["gradient_volcanic_steeper"],
                          "P2 thermal |d| < 0.5": abs(p["d_thermal"]) < 0.5,
                          "P3 NOT SUPPORTED": p["verdict"]["stage1b"].startswith("NOT")}
    log("predictions: %s" % res["predictions"])
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, default=float)
    log("wrote " + OUT)


if __name__ == "__main__":
    main()
