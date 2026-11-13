# -*- coding: utf-8 -*-
r"""H2 stage 2 (make_t4_channel_sim3292.py, KB §69.133): how much do its two settings matter, and what difference could
seven rilles have resolved? (KB §69.137)

Stage 2 found the rilles steeper by median (8.70 against 5.45 m/km in the five shared blocks) but unresolved
(+3.25, -3.20 to +6.80) and thermal d -0.49, just short of the rule's 0.5. Two settings were one choice each: the
floor window (the lowest 200 m DEM value within 1 km of the drawn line) and the piece length (10 km). This reruns the
same lines, measures, line bootstrap (2,000) and verdict rule over
  floor half-window  3, 5, 10 px  (0.6, 1.0, 2.0 km; 5 is stage 2's)
  piece length       5, 10, 20 km (10 is stage 2's)
and, at stage 2's own setting, finds the smallest shift added to every volcanic piece's gradient (0.25 m/km steps) at
which the shared scope's interval of the median difference would sit above 0: the difference these lines could
resolve.

Predictions, written 2026-11-12 before the first run (SHARED scope):
  S1  The verdict is NOT SUPPORTED in all 9 settings.
  S2  The volcanic median is the steeper in at least 7 of the 9.
  S3  |d thermal| is under 0.5 in at least 5 of the 9 (it sits at the edge).
  S4  The smallest resolvable shift exceeds the observed +3.25 m/km.

  "<ArcGIS Pro Python>" make_t4_sim3292_sensitivity.py   -> logs\t4_sim3292_sensitivity.json
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_t4_channel_sim3292 as S2

OUT = os.path.join(HERE, "logs", "t4_sim3292_sensitivity.json")
FLOORS, PIECES = (3, 5, 10), (5, 10, 20)
log = S2.log


def pieces(lines, lon, lat, lid, idx, org, inside, F, TZ, piece_km):
    piece = idx // piece_km
    P = {"line": [], "origin": [], "grad": [], "tz": [], "lon": [], "lat": []}
    for n in range(len(lines)):
        m = lid == n
        for k in np.unique(piece[m]):
            q = np.flatnonzero(m & (idx >= k * piece_km) & (idx <= (k + 1) * piece_km))
            if q.size != piece_km + 1:
                continue
            if not (inside[q].all() and np.isfinite(F[q[[0, -1]]]).all() and np.isfinite(TZ[q]).any()):
                continue
            P["line"].append(n); P["origin"].append(org[q[0]])
            P["grad"].append(abs(F[q[-1]] - F[q[0]]) / ((q.size - 1) * S2.STEP_KM))
            P["tz"].append(np.nanmean(TZ[q])); P["lon"].append(lon[q].mean()); P["lat"].append(lat[q].mean())
    P = {k: np.array(v) for k, v in P.items()}
    blk = [(int(math.floor(lo / S2.BLOCK) * S2.BLOCK), int(math.floor(la / S2.BLOCK) * S2.BLOCK))
           for lo, la in zip(P["lon"], P["lat"])]
    return P, np.array([b in S2.SHARED for b in blk])


def lower_bound(P, sel, shift, nboot=1000, seed=7):
    rng = np.random.default_rng(seed)
    f, v = sel & (P["origin"] == "fluvial"), sel & (P["origin"] == "volcanic")
    g = P["grad"] + np.where(v, shift, 0.0)
    lf, lv = np.unique(P["line"][f]), np.unique(P["line"][v])
    by_f = {l: np.flatnonzero(f & (P["line"] == l)) for l in lf}
    by_v = {l: np.flatnonzero(v & (P["line"] == l)) for l in lv}
    dm = [np.median(g[np.concatenate([by_v[l] for l in rng.choice(lv, lv.size)])])
          - np.median(g[np.concatenate([by_f[l] for l in rng.choice(lf, lf.size)])]) for _ in range(nboot)]
    return float(np.percentile(dm, 2.5))


def main():
    lines = S2.read_lines()
    lon, lat, lid, org, idx = [], [], [], [], []
    for n, (oid, o, pts) in enumerate(lines):
        lo, la = S2.densify(pts)
        lon.append(lo); lat.append(la); lid.append(np.full(lo.size, n)); org += [o] * lo.size
        idx.append(np.arange(lo.size))
    lon, lat, lid, idx = map(np.concatenate, (lon, lat, lid, idx)); org = np.array(org)
    inside = np.abs(lat) <= 60
    by = np.minimum(((60.0 - lat) / S2.BLOCK).astype(int), int(120 / S2.BLOCK) - 1).clip(0)
    bx = np.minimum(((lon % 360.0) / S2.BLOCK).astype(int), int(360 / S2.BLOCK) - 1)
    res = {"floors_px": FLOORS, "pieces_km": PIECES, "settings": {}}
    base = None
    for fp in FLOORS:
        S2.FLOOR_PX = fp
        S2.rng = np.random.default_rng(S2.SEED)
        floor, tv, bmean, bsd = S2.sample(lon[inside], lat[inside])
        F = np.full(lon.size, np.nan); T = np.full(lon.size, np.nan)
        F[inside], T[inside] = floor, tv
        with np.errstate(invalid="ignore"):
            TZ = (T - bmean[by, bx]) / bsd[by, bx]
        for pk in PIECES:
            P, shared = pieces(lines, lon, lat, lid, idx, org, inside, F, TZ, pk)
            S2.rng = np.random.default_rng(S2.SEED)
            s = S2.scope_stats(P, shared)
            key = "floor %.1f km, piece %d km" % (fp * 0.2, pk)
            res["settings"][key] = s
            log("%-28s pieces %d/%d  median fluv %.2f volc %.2f  diff %+.2f [%+.2f, %+.2f]  d thermal %+.2f [%+.2f, %+.2f]  %s" % (
                key, s["pieces"]["fluvial"], s["pieces"]["volcanic"], s["median_gradient"]["fluvial"],
                s["median_gradient"]["volcanic"], s["median_difference_volc_minus_fluv"], *s["median_difference_ci95"],
                s["d_thermal"], *s["d_thermal_ci95"], s["verdict"]))
            if fp == 5 and pk == 10:
                base = (P, shared)
    # check: stage 2's own setting reproduces its published numbers
    s = res["settings"]["floor 1.0 km, piece 10 km"]
    assert (s["median_gradient"]["fluvial"], s["median_gradient"]["volcanic"]) == (5.45, 8.70), s["median_gradient"]
    assert abs(s["d_thermal"] - (-0.48875910672441525)) < 1e-9
    log("check: the base setting reproduces stage 2 (5.45, 8.70 m/km; d -0.489)")
    P, shared = base
    shift, lb = 0.0, lower_bound(P, shared, 0.0)
    while lb <= 0 and shift < 40:
        shift += 0.25
        lb = lower_bound(P, shared, shift)
    res["smallest_resolvable_shift_m_per_km"] = shift
    res["observed_difference_m_per_km"] = s["median_difference_volc_minus_fluv"]
    log("smallest shift of the volcanic gradients the shared scope resolves: +%.2f m/km (observed difference %+.2f)" % (
        shift, s["median_difference_volc_minus_fluv"]))
    st = list(res["settings"].values())
    res["predictions"] = {
        "S1 NOT SUPPORTED in all 9": all(x["verdict"] == "NOT SUPPORTED" for x in st),
        "S2 volcanic median steeper in >= 7 of 9": sum(x["median_difference_volc_minus_fluv"] > 0 for x in st) >= 7,
        "S3 |d thermal| < 0.5 in >= 5 of 9": sum(abs(x["d_thermal"]) < 0.5 for x in st) >= 5,
        "S4 smallest resolvable shift > observed +3.25": shift > s["median_difference_volc_minus_fluv"]}
    for k, v in res["predictions"].items():
        log("prediction %-45s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
