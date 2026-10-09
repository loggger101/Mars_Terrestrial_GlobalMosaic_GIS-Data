# -*- coding: utf-8 -*-
r"""Test T4 (H2): do fluvial and volcanic channels separate on gradient and thermal response? (NEXT-STEPS §4; KB §51)

H2, from the prospectus: fluvial channels have shallower gradients than volcanic ones, and the two
separate on gradient against thermal response.

Two stages, as NEXT-STEPS §4 designs it:
  stage 1 (now)    the machine channel candidates, with the window standing in for origin: Ius Chasma
                   (fluvial and collapse) against Athabasca Valles (volcanic, flood lava, §41)
  stage 2 (later)  reviewed channels in Landform_ChannelCenterlines with Origin = fluvial / volcanic
                   (§46). Run automatically once at least 10 of each exist; until then reported as waiting.

Prediction, written before the run (2026-10-09):
  gradient   H2's direction FAILS at stage 1: Ius candidates are steeper than Athabasca's, because the
             Ius window holds the chasma walls and its plateau, and Athabasca's lava plains are flat
             (mean slope 1.8°, 97 % of candidates under 2°, §42.1). The window, not the origin, sets it.
  thermal    the two windows' candidates differ from their own backgrounds by little (|d| < 0.5), since
             the index is a weak indicator (§42.4, §43.1); so they do not separate on thermal response.

Design (fixed before any number was read):
  - Candidates of length >= 1 km. Also reported: Strahler order >= 2 only (less DEM noise, §25, §47.4).
  - Gradient = |z(first vertex) - z(last vertex)| / length, m per km, on the window's 100 m DEM
    (the 200 m HRSC/MOLA blend resampled, §18). A straight-line drop over the routed length.
  - Thermal response = (ThermIdx - background mean) / background sd, the index compared within its own
    window only (§28.10). Background: 200,000 random valid pixels of that window's index.
  - Separation between the windows: Cohen's d per variable, and the area under the ROC curve of a
    logistic regression on (log10 gradient, thermal z), 5-fold cross-validated.
  - Uncertainty: segments of one network are correlated, so 95 % intervals come from a bootstrap over
    50 km x 50 km cells (2,000 resamples), not over segments.
  - Verdict rule, fixed in advance: stage 1 is CONSISTENT with H2 only if (a) Athabasca's median
    gradient exceeds Ius's with the interval of the difference above zero, AND (b) the thermal z differs
    between the windows with |d| >= 0.5 and its interval excluding zero. Otherwise NOT SUPPORTED at
    stage 1. Either way stage 1 cannot confirm H2: window is a proxy for origin.

Read-only; writes build\logs\t4_channel_h2.json.
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive
import areas

gdal.UseExceptions()
OUT = os.path.join(HERE, "logs", "t4_channel_h2.json")
NBG, NBOOT, CELL, SEED, MIN_KM = 200000, 2000, 50000.0, 20261009, 1.0
ORIGIN_MIN = 10
t0 = time.time()
rng = np.random.default_rng(SEED)


def log(msg):
    print("[%6.1fs] %s" % (time.time() - t0, msg), flush=True)


class Grid:
    def __init__(self, path):
        self.ds = gdal.Open(path)
        b = self.ds.GetRasterBand(1)
        self.a = b.ReadAsArray().astype("float64")
        nd = b.GetNoDataValue()
        self.valid = np.isfinite(self.a) & ((self.a != nd) if nd is not None else True)
        self.gt = self.ds.GetGeoTransform()

    def at(self, x, y):
        c = int((x - self.gt[0]) / self.gt[1]); r = int((y - self.gt[3]) / self.gt[5])
        if 0 <= r < self.a.shape[0] and 0 <= c < self.a.shape[1] and self.valid[r, c]:
            return self.a[r, c]
        return np.nan


def segments(fc, where, dem, label, origin=None):
    out = []
    flds = ["SHAPE@", "ThermIdx", "StrahlerOrd"] if origin is None else ["SHAPE@", "Origin"]
    with arcpy.da.SearchCursor(fc, flds, where) as c:
        for r in c:
            g = r[0]
            if g is None:
                continue
            km = g.length / 1000.0
            if km < MIN_KM:
                continue
            z0, z1 = dem.at(g.firstPoint.X, g.firstPoint.Y), dem.at(g.lastPoint.X, g.lastPoint.Y)
            mid = g.positionAlongLine(0.5, True).firstPoint
            out.append(dict(win=label, km=km, grad=abs(z0 - z1) / km, therm=r[1] if origin is None else np.nan,
                            order=r[2] if origin is None else 0, x=mid.X, y=mid.Y,
                            origin=r[1] if origin is not None else None))
    return [s for s in out if np.isfinite(s["grad"])]


def cohen_d(a, b):
    return (np.mean(b) - np.mean(a)) / np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)


def auc(score, y):
    order = np.argsort(score); ranks = np.empty(len(score)); ranks[order] = np.arange(1, len(score) + 1)
    n1 = y.sum(); n0 = len(y) - n1
    return (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n0 * n1)


def cv_auc(X, y, k=5):
    """5-fold cross-validated AUC of a plain logistic regression (Newton steps, standardised inputs)."""
    idx = rng.permutation(len(y)); folds = np.array_split(idx, k); scores = np.empty(len(y))
    for f in folds:
        tr = np.setdiff1d(idx, f)
        mu, sd = X[tr].mean(0), X[tr].std(0); sd[sd == 0] = 1
        A = np.c_[np.ones(len(tr)), (X[tr] - mu) / sd]; w = np.zeros(A.shape[1])
        for _ in range(25):
            p = 1 / (1 + np.exp(-A @ w)); H = A.T @ (A * (p * (1 - p))[:, None]) + 1e-6 * np.eye(len(w))
            w -= np.linalg.solve(H, A.T @ (p - y[tr]))
        scores[f] = np.c_[np.ones(len(f)), (X[f] - mu) / sd] @ w
    return auc(scores, y)


def compare(a, b, name_a, name_b):
    """b against a: medians, d, AUCs, with a cell bootstrap."""
    def stats(A, B):
        ga, gb = np.array([s["grad"] for s in A]), np.array([s["grad"] for s in B])
        ta, tb = np.array([s["tz"] for s in A]), np.array([s["tz"] for s in B])
        return dict(grad_median_a=np.median(ga), grad_median_b=np.median(gb), grad_median_diff=np.median(gb) - np.median(ga),
                    d_log_grad=cohen_d(np.log10(ga + 0.01), np.log10(gb + 0.01)), d_thermal=cohen_d(ta, tb),
                    therm_z_mean_a=ta.mean(), therm_z_mean_b=tb.mean())
    point = stats(a, b)
    X = np.array([[np.log10(s["grad"] + 0.01), s["tz"]] for s in a + b]); y = np.r_[np.zeros(len(a)), np.ones(len(b))]
    point["auc_both"] = cv_auc(X, y); point["auc_gradient"] = cv_auc(X[:, :1], y); point["auc_thermal"] = cv_auc(X[:, 1:], y)
    cells = {}
    for s in a + b:
        cells.setdefault((s["win"], int(s["x"] // CELL), int(s["y"] // CELL)), []).append(s)
    ca = [v for k, v in cells.items() if k[0] == a[0]["win"]]; cb = [v for k, v in cells.items() if k[0] == b[0]["win"]]
    boot = {k: [] for k in ("grad_median_diff", "d_log_grad", "d_thermal")}
    for _ in range(NBOOT):
        A = [s for i in rng.integers(0, len(ca), len(ca)) for s in ca[i]]
        B = [s for i in rng.integers(0, len(cb), len(cb)) for s in cb[i]]
        st = stats(A, B)
        for k in boot:
            boot[k].append(st[k])
    for k, v in boot.items():
        point[k + "_ci95"] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    point.update(n_a=len(a), n_b=len(b), cells_a=len(ca), cells_b=len(cb), a=name_a, b=name_b)
    return {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in point.items()}


def verdict(r):
    a = r["grad_median_diff_ci95"][0] > 0
    b = abs(r["d_thermal"]) >= 0.5 and (r["d_thermal_ci95"][0] > 0 or r["d_thermal_ci95"][1] < 0)
    return dict(gradient_volcanic_steeper=bool(a), thermal_separates=bool(b),
                stage1="CONSISTENT with H2 (window as proxy)" if a and b else "NOT SUPPORTED at stage 1")


def selftest():
    """The statistics on data with known answers, before they touch real data."""
    y = np.r_[np.zeros(500), np.ones(500)]
    sep = np.c_[np.r_[rng.normal(0, 1, 500), rng.normal(10, 1, 500)], rng.normal(0, 1, 1000)]
    rnd = rng.normal(0, 1, (1000, 2))
    checks = {"auc perfect = 1": abs(auc(sep[:, 0], y) - 1) < 1e-9,
              "cv auc separated > 0.99": cv_auc(sep, y) > 0.99,
              "cv auc random 0.43-0.57": 0.43 < cv_auc(rnd, y) < 0.57,
              "d of a 0.8 sd shift 0.65-0.95": 0.65 < cohen_d(rng.normal(0, 1, 2000), rng.normal(0.8, 1, 2000)) < 0.95}
    for k, ok in checks.items():
        log("selftest %-30s %s" % (k, "ok" if ok else "FAIL"))
    assert all(checks.values()), "statistics self-test failed"


def main():
    selftest()
    res = {"prediction": "gradient: Ius steeper than Athabasca (H2 direction fails); thermal: |d| < 0.5",
           "design": {"min_km": MIN_KM, "background_pixels": NBG, "bootstrap": NBOOT, "cell_m": CELL, "seed": SEED}}
    data = {}
    for key, A in areas.AREAS.items():
        folder = on_drive(os.path.join("Mars Project", A["folder"]))
        dem = Grid(os.path.join(folder, A["prefix"] + "_dem.tif"))
        idx = Grid(os.path.join(folder, A["prefix"] + "_thermal_contrast.tif"))
        rr, cc = np.nonzero(idx.valid)
        pick = rng.choice(len(rr), min(NBG, len(rr)), replace=False)
        bg = idx.a[rr[pick], cc[pick]]
        segs = segments(os.path.join(GDB, A["channels"]), None, dem, key)
        th = np.array([s["therm"] for s in segs], float)
        log("%s: %d candidates >= %.0f km; background index mean %.4f sd %.4f; candidate ThermIdx mean %.4f"
            % (A["name"], len(segs), MIN_KM, bg.mean(), bg.std(), np.nanmean(th)))
        for s in segs:
            s["tz"] = (s["therm"] - bg.mean()) / bg.std() if s["therm"] is not None else np.nan
        segs = [s for s in segs if np.isfinite(s["tz"])]
        data[key] = segs
        res.setdefault("windows", {})[key] = dict(name=A["name"], n=len(segs), background_mean=float(bg.mean()),
            background_sd=float(bg.std()), grad_median=float(np.median([s["grad"] for s in segs])),
            grad_p90=float(np.percentile([s["grad"] for s in segs], 90)),
            therm_z_mean=float(np.mean([s["tz"] for s in segs])))
    res["stage1_all"] = compare(data["ius"], data["ath"], "Ius Chasma", "Athabasca Valles")
    res["stage1_all"]["verdict"] = verdict(res["stage1_all"])
    hi = {k: [s for s in v if (s["order"] or 0) >= 2] for k, v in data.items()}
    res["stage1_order2"] = compare(hi["ius"], hi["ath"], "Ius Chasma, order >= 2", "Athabasca Valles, order >= 2")
    res["stage1_order2"]["verdict"] = verdict(res["stage1_order2"])
    for k in ("stage1_all", "stage1_order2"):
        r = res[k]
        log("%s: n %d / %d; median gradient %.2f vs %.2f m/km (diff %+.2f [%+.2f, %+.2f]); d thermal %+.2f [%+.2f, %+.2f]; "
            "AUC both %.2f, gradient %.2f, thermal %.2f -> %s"
            % (k, r["n_a"], r["n_b"], r["grad_median_a"], r["grad_median_b"], r["grad_median_diff"],
               *r["grad_median_diff_ci95"], r["d_thermal"], *r["d_thermal_ci95"], r["auc_both"], r["auc_gradient"],
               r["auc_thermal"], r["verdict"]["stage1"]))
    # stage 2: reviewed channels with an origin
    cnt = {}
    with arcpy.da.SearchCursor(os.path.join(GDB, "Landform_ChannelCenterlines"), ["Origin"]) as c:
        for (o,) in c:
            cnt[o] = cnt.get(o, 0) + 1
    res["stage2"] = {"origin_counts": cnt}
    if cnt.get("fluvial", 0) >= ORIGIN_MIN and cnt.get("volcanic", 0) >= ORIGIN_MIN:
        res["stage2"]["note"] = "enough reviewed channels: extend this script to compare by Origin"
    else:
        res["stage2"]["note"] = ("waiting: needs >= %d fluvial and >= %d volcanic reviewed channels" % (ORIGIN_MIN, ORIGIN_MIN))
    log("stage 2: %s %s" % (cnt, res["stage2"]["note"]))
    json.dump(res, open(OUT, "w"), indent=1, default=float)
    log("wrote " + OUT)


if __name__ == "__main__":
    main()
