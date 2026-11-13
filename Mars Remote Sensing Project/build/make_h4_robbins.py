# -*- coding: utf-8 -*-
r"""H4 below 100 km: do image gradients find the rims of 20-100 km craters, and which ones? (KB §69.140)

H4 was tested as written on the 117 IAU craters >= 100 km (make_h4_q6.py, KB §69.132): the five spectral bands'
gradient finds 104 of 109 rims. This runs the same rim rule on Robbins & Hynek 2020 craters of 20-100 km
(`Reference\Robbins_craters_2020\Catalog_Mars_Release_2020_1kmPlus_FullMorphData.csv`, centres within 58 deg), in three
diameter bins, 20-30, 30-50 and 50-100 km, 400 craters drawn at random per bin (seed fixed), on the same 1.6 km
gradients (imported). Rim rule unchanged: the strongest 0.05 R annulus between 0.5 and 1.5 R lies at 0.8-1.2 R and the
rim contrast exceeds the 95th percentile of 1,000 random placements; the placements are drawn per bin, radii from that
bin's sample, centres at least 1.5 (R + r) from any Robbins crater of at least half the bin's smallest diameter.
Robbins' DEG_RIM (1 most degraded to 4 freshest, KB §69.45) splits each bin.

Predictions, written 2026-11-13 before the first run:
  K1  The composite finds more than half of the 50-100 km craters.
  K2  The share found falls with size: 20-30 < 30-50 < 50-100 km (rims thin toward the 1.6 km pixel).
  K3  In every bin the freshest rims (DEG_RIM 4) are found more often than the most degraded (DEG_RIM 1).
  K4  Night IR finds fewer than the composite in every bin.

  "<ArcGIS Pro Python>" make_h4_robbins.py   -> logs\h4_robbins.json
"""
import os, sys, csv, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
import make_h4_q6 as H

OUT = os.path.join(HERE, "logs", "h4_robbins.json")
SRC = os.path.join(os.path.dirname(G.OUTDIR), "Reference", "Robbins_craters_2020",
                   "Catalog_Mars_Release_2020_1kmPlus_FullMorphData.csv")
BINS = [(20, 30), (30, 50), (50, 100)]
NPER, NNULL, SEED = 400, 1000, 20261113
INPUTS = ["Viking red", "night IR", "day IR", "composite", "slope"]


def read_robbins():
    rows = []
    with open(SRC, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            d = float(r["DIAM_CIRC_IMG"])
            if d < 10:
                continue
            try:
                deg = int(r["DEG_RIM"])
            except ValueError:
                deg = 0
            rows.append((r["CRATER_ID"], d, float(r["LAT_CIRC_IMG"]), (float(r["LON_CIRC_IMG"]) + 180) % 360 - 180, deg))
    return rows


def gc_km(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    c = np.sin(la1) * np.sin(la2) + np.cos(la1) * np.cos(la2) * np.cos(lo2 - lo1)
    return G.R_MARS / 1000 * np.arccos(np.clip(c, -1, 1))


def main():
    rng = np.random.default_rng(SEED)
    rob = read_robbins()
    D = np.array([r[1] for r in rob]); LA = np.array([r[2] for r in rob]); LO = np.array([r[3] for r in rob])
    DEG = np.array([r[4] for r in rob])
    print("Robbins >= 10 km: %d" % len(rob), flush=True)
    arr, cell, lat, lon, gt = H.read_stack()
    grads, valid = H.gradients(arr, cell, lat)
    del arr
    res = {"bins": {}, "inputs": INPUTS, "n_per_bin": NPER}
    for lo_d, hi_d in BINS:
        pool = np.flatnonzero((D >= lo_d) & (D < hi_d) & (np.abs(LA) <= 58))
        pick = rng.choice(pool, min(NPER, pool.size), replace=False)
        av = (D >= lo_d / 2)
        radii = D[pick] / 2
        nulls, tries = [], 0
        while len(nulls) < NNULL and tries < 50000:
            tries += 1
            Rk = float(rng.choice(radii))
            la = math.degrees(math.asin(rng.uniform(math.sin(math.radians(-58)), math.sin(math.radians(58)))))
            lo = rng.uniform(-180, 180)
            if (gc_km(la, lo, LA[av], LO[av]) >= 1.5 * (Rk + D[av] / 2)).all():
                nulls.append((la, lo, Rk))
        B = {"pool": int(pool.size), "sampled": int(pick.size), "n_null": len(nulls), "null_tries": tries, "inputs": {}}
        for name in INPUTS:
            img = grads[name]
            null_c = []
            for la, lo, Rk in nulls:
                p = H.profile(img, valid, lat, cell, gt, la, lo, Rk)
                if p is not None and np.isfinite(p).all():
                    null_c.append(H.rim_stats(p))
            thr = float(np.percentile([c for _, c in null_c], 95))
            chance = float(np.mean([(0.8 <= pk <= 1.2) and c > thr for pk, c in null_c]))
            found, scored, by_deg = 0, 0, {}
            for i in pick:
                p = H.profile(img, valid, lat, cell, gt, LA[i], LO[i], D[i] / 2)
                if p is None or not np.isfinite(p).all():
                    continue
                pk, c = H.rim_stats(p)
                ok = (0.8 <= pk <= 1.2) and c > thr
                scored += 1; found += ok
                s = by_deg.setdefault(int(DEG[i]), [0, 0]); s[0] += ok; s[1] += 1
            B["inputs"][name] = {"found": found, "scored": scored, "share": found / scored,
                                 "lower95": H.binom_lower(found, scored), "chance": chance, "null_threshold": thr,
                                 "null_scored": len(null_c),
                                 "by_deg_rim": {str(k): {"found": v[0], "scored": v[1]} for k, v in sorted(by_deg.items())}}
            print("%3d-%-3d km  %-11s found %3d of %3d (%.1f %%), chance %.1f %%; by DEG_RIM %s" % (
                lo_d, hi_d, name, found, scored, 100 * found / scored, 100 * chance,
                " ".join("%d:%d/%d" % (k, v[0], v[1]) for k, v in sorted(by_deg.items()))), flush=True)
        res["bins"]["%d-%d" % (lo_d, hi_d)] = B
    sh = lambda b, n: res["bins"][b]["inputs"][n]["share"]
    dg = lambda b, k: res["bins"][b]["inputs"]["composite"]["by_deg_rim"].get(k, {"found": 0, "scored": 0})
    frac = lambda d: d["found"] / d["scored"] if d["scored"] else float("nan")
    res["predictions"] = {
        "K1 composite finds > half of 50-100 km": sh("50-100", "composite") > 0.5,
        "K2 composite share 20-30 < 30-50 < 50-100": sh("20-30", "composite") < sh("30-50", "composite") < sh("50-100", "composite"),
        "K3 DEG_RIM 4 found more often than DEG_RIM 1 in every bin":
            all(frac(dg(b, "4")) > frac(dg(b, "1")) for b in res["bins"]),
        "K4 night IR finds fewer than the composite in every bin":
            all(sh(b, "night IR") < sh(b, "composite") for b in res["bins"])}
    for k, v in res["predictions"].items():
        print("prediction %-60s %s" % (k, "held" if v else "NOT HELD"), flush=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
