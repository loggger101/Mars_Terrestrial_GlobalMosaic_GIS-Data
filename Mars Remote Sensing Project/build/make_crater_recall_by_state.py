# -*- coding: utf-8 -*-
r"""A11: is the closed-depression detector's recall limited by degraded and breached craters? (NEXT-STEPS §12.2 A11)

The paper says recall against Robbins levels off near one half (45.8 % at >= 5 km, 48.1 % at >= 20 km, KB §53.4,
§54.4) "because breached and degraded craters are not closed". This measures it. The Robbins & Hynek 2020 release
(`Catalog_Mars_Release_2020_1kmPlus_FullMorphData.csv`) carries, per crater:
  DEG_RIM 1-4, DEG_FLR 1-4, DEG_EJC 1-3   degradation states; read before this script (descriptive, no recall): they
      cover 203 of 280,944 craters of 1-3 km within ±60°, 85.8 % at 3-5 km, 95.7 % at 5-10 km, 99.0 % at >= 10 km;
      higher is fresher (craters with layered ejecta have DEG_EJC 2 or 3 in 98.8 % of cases, those without in 40.4 %).
  ARC_IMG   the share of the rim traced in the imagery, 1 for a full circle: below 1 is a partial rim (breached,
      buried or overlapped); 64 % of craters >= 10 km within ±60° have one.
Recall is the §42.3 rule exactly as verify_global60_candidates.py's C5 applies it: a Robbins crater is found when a
closed depression lies within half its diameter of its centre and has a diameter within a factor of 2, both sets at
D >= Dmin. Beside each recall, C5b's local chance baseline (every depression moved east by 3 of its own diameters).

Route check first: the overall recall at each Dmin must equal logs\global60_candidates_check.json's, or nothing is
written.

Predictions, written before the first run (Dmin 5 km, where the states are near complete):
  P1  Recall rises with rim preservation: DEG_RIM 1 < 2 < 3 < 4.
  P2  The freshest rims (DEG_RIM 4) are found at >= 70 %, the most degraded (DEG_RIM 1) at <= 35 %. If P2 holds,
      the paper's explanation is measured; if not, its sentence changes.
  P3  Partial rims (ARC_IMG < 1) are found at least 15 points less often than full rims, in each diameter bin
      5-10, 10-20, 20-50 km (partial rims are commoner among large craters, so the bins keep size apart).
Each is reported as held or not held; none is adjusted after the run.

Added 2026-11-01 for D32 (the paper's figure takes the one-side-cut curve): the chance baseline cut the same way,
checked first against C5b's logged baseline at 5 km.

Added after the first run (2026-11-01; it changes no verdict): why each missed crater >= 5 km is missed. Within half
its diameter of its centre, is there no closed depression >= 1 km at all, or only ones smaller than half its
diameter, or only larger than twice it, or one within the factor of 2 that C5's rule drops because it is itself below
Dmin (the rule cuts both sets at Dmin)? By rim state and diameter bin. "Only smaller" means the floor holds a closed
basin the size rule rejects, so a looser rule or a rim-based diameter could recover it; "none" means no closed basin
at the 200 m grid (breached, filled or too shallow). Beside C5's recall, not in place of it: the recall the same rule
gives with the depressions uncut (Robbins >= Dmin against every depression >= 1 km).

  "<ArcGIS Pro Python>" make_crater_recall_by_state.py      -> logs\crater_recall_by_state.json; reads only
"""
import os, sys, csv, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from scipy.spatial import cKDTree
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive

FC_C = os.path.join(GDB, "Landform_CraterCandidates_auto_60")
ROBBINS = os.path.join(GDB, "Ref_Craters_Robbins2020")
SRC = on_drive(r"Mars Project\Reference\Robbins_craters_2020\Catalog_Mars_Release_2020_1kmPlus_FullMorphData.csv")
OUT = os.path.join(HERE, "logs", "crater_recall_by_state.json")
R_KM = 3396.19
DMIN = 5.0
BINS = [(5, 10), (10, 20), (20, 50), (50, 1e9)]


def unit(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def found(c_lon, c_lat, c_d, r_lon, r_lat, r_d, dmin):
    """verify_global60_candidates.score's rule, returning which Robbins craters >= dmin are found."""
    cs = c_d >= dmin; rs = r_d >= dmin
    C = unit(c_lon[cs], c_lat[cs]); Rr = unit(r_lon[rs], r_lat[rs]); cd, rd = c_d[cs], r_d[rs]
    t = cKDTree(C)
    rad = 2 * np.sin(0.5 * (0.5 * rd) / R_KM)          # chord of half the Robbins diameter
    hits = t.query_ball_point(Rr, rad)
    rec = np.zeros(len(rd), bool)
    for k, h in enumerate(hits):
        if h:
            h = np.asarray(h)
            rec[k] = bool((np.abs(np.log(cd[h] / rd[k])) <= np.log(2)).any())
    out = np.zeros(len(r_d), bool); out[rs] = rec
    return out


def main():
    t0 = time.time()
    rows = list(arcpy.da.SearchCursor(FC_C, ["CenterLon", "CenterLat", "DiameterKm"]))
    lon, lat, D = (np.array(x, float) for x in zip(*rows))
    rb = list(arcpy.da.SearchCursor(ROBBINS, ["CraterID", "Lon", "Lat", "DiamKm"]))
    ids = [r[0] for r in rb]
    rlon, rlat, rd = (np.array(x, float) for x in list(zip(*rb))[1:])
    rlon = np.mod(rlon, 360.0)
    keep = np.abs(rlat) <= 60.0
    ids = [i for i, k in zip(ids, keep) if k]; rlon, rlat, rd = rlon[keep], rlat[keep], rd[keep]
    print("read %d depressions, %d Robbins craters within ±60° (%.0f s)" % (len(D), len(rd), time.time() - t0))

    # route check: C5's recall at every Dmin
    log = json.load(open(os.path.join(HERE, "logs", "global60_candidates_check.json"), encoding="utf-8"))["robbins"]
    for d, s in log.items():
        if not s:
            continue
        f = found(lon, lat, D, rlon, rlat, rd, float(d))
        r = f[rd >= float(d)].mean()
        ok = abs(r - s["recall"]) < 1e-9 and int((rd >= float(d)).sum()) == s["robbins"]
        print("route check D >= %s km: recall %.6f, its log %.6f -> %s" % (d, r, s["recall"], "ok" if ok else "MISMATCH"))
        if not ok:
            sys.exit(2)

    morph = {}
    with open(SRC, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            morph[r["CRATER_ID"]] = r
    def field(name, cast):
        out = []
        for i in ids:
            v = morph[i][name].strip()
            out.append(cast(v) if v else np.nan)
        return np.array(out, float)
    deg = {f: field(f, int) for f in ("DEG_RIM", "DEG_FLR", "DEG_EJC")}
    arc = field("ARC_IMG", float)

    obs = found(lon, lat, D, rlon, rlat, rd, DMIN)
    dlon = np.degrees(3.0 * D / (R_KM * np.cos(np.radians(lat))))
    base = found(np.mod(lon + dlon, 360), lat, D, rlon, rlat, rd, DMIN)
    big = rd >= DMIN

    def tally(sel):
        n = int(sel.sum())
        return dict(n=n, recall=round(float(obs[sel].mean()), 4) if n else None,
                    baseline=round(float(base[sel].mean()), 4) if n else None)

    res = dict(script="make_crater_recall_by_state.py", when=time.strftime("%Y-%m-%d %H:%M"), dmin_km=DMIN,
               all=tally(big), states_missing=int((big & np.isnan(deg["DEG_RIM"])).sum()))
    for f, v in deg.items():
        res[f] = {str(s): tally(big & (v == s)) for s in sorted(set(v[big & ~np.isnan(v)].astype(int)))}
        res[f + "_by_diameter"] = {"%g-%g" % b if b[1] < 1e8 else ">=%g" % b[0]:
                                   {str(s): tally(big & (v == s) & (rd >= b[0]) & (rd < b[1]))
                                    for s in sorted(set(v[big & ~np.isnan(v)].astype(int)))} for b in BINS}
    part, full = big & (arc < 0.999), big & (arc >= 0.999)
    res["ARC_IMG"] = dict(full=tally(full), partial=tally(part))
    res["ARC_IMG_by_diameter"] = {"%g-%g" % b if b[1] < 1e8 else ">=%g" % b[0]:
                                  dict(full=tally(full & (rd >= b[0]) & (rd < b[1])),
                                       partial=tally(part & (rd >= b[0]) & (rd < b[1]))) for b in BINS}
    res["ARC_IMG_by_DEG_RIM"] = {str(s): dict(full=tally(full & (deg["DEG_RIM"] == s)),
                                              partial=tally(part & (deg["DEG_RIM"] == s))) for s in (1, 2, 3, 4)}

    # why the misses are missed (added after the first run): every depression >= 1 km within half the diameter
    t = cKDTree(unit(lon, lat))
    miss = np.where(big & ~obs)[0]
    near = t.query_ball_point(unit(rlon[miss], rlat[miss]), 2 * np.sin(0.5 * (0.5 * rd[miss]) / R_KM))
    why = np.empty(len(miss), object)
    for k, h in enumerate(near):
        ratio = D[np.asarray(h, int)] / rd[miss[k]]
        why[k] = "none" if not len(h) else "in_factor_2_below_dmin" if ((ratio >= .5) & (ratio <= 2)).any() else \
            "only_smaller" if (ratio < .5).all() else "only_larger" if (ratio > 2).all() else "smaller_and_larger"
    kinds = ["none", "in_factor_2_below_dmin", "only_smaller", "only_larger", "smaller_and_larger"]
    def share(sel):
        n = int(sel.sum())
        return dict(n=n, **{k: round(float((why[sel] == k).mean()), 4) if n else None for k in kinds})
    rs = deg["DEG_RIM"][miss]; dm = rd[miss]
    res["misses"] = dict(all=share(np.ones(len(miss), bool)),
                         by_rim_state={str(s): share(rs == s) for s in (1, 2, 3, 4)},
                         by_diameter={"%g-%g" % b if b[1] < 1e8 else ">=%g" % b[0]: share((dm >= b[0]) & (dm < b[1]))
                                      for b in BINS},
                         rim_state_share_of_misses={str(s): round(float((rs == s).sum() / (~np.isnan(rs)).sum()), 4)
                                                    for s in (1, 2, 3, 4)})
    uncut = found(lon, lat, D, rlon, rlat, rd, 1.0)          # depressions >= 1 km; recall read on Robbins >= DMIN
    # the same for every Dmin of C5's curve, and precision the other way round (depressions >= Dmin against every
    # Robbins crater >= 1 km), so only the set being scored is cut
    def precise(tree):
        """Which depressions (in tree's order) match some Robbins crater >= 1 km, by C5's rule."""
        out = np.zeros(len(D), bool)
        for k, h in enumerate(tree.query_ball_point(unit(rlon, rlat), 2 * np.sin(0.5 * (0.5 * rd) / R_KM))):
            if h:
                h = np.asarray(h)
                out[h[np.abs(np.log(D[h] / rd[k])) <= np.log(2)]] = True
        return out
    prec_uncut = precise(t)
    # and the chance baseline the same way (C5b's shift, 3 diameters east), for the paper's figure (D32)
    slon = np.mod(lon + dlon, 360)
    base_rec = found(slon, lat, D, rlon, rlat, rd, 1.0)
    base_prec = precise(cKDTree(unit(slon, lat)))
    shifted_log = json.load(open(os.path.join(HERE, "logs", "global60_candidates_check.json"),
                                 encoding="utf-8"))["robbins_shifted_3D"]
    ok = abs(base[big].mean() - shifted_log["5"]["recall"]) < 1e-9
    print("route check, the chance baseline at D >= 5 km: %.6f, its log %.6f -> %s"
          % (base[big].mean(), shifted_log["5"]["recall"], "ok" if ok else "MISMATCH"))
    if not ok:
        sys.exit(2)
    curve = {}
    for d, s in log.items():
        if s:
            curve[d] = dict(recall_c5=round(s["recall"], 4), recall_uncut=round(float(uncut[rd >= float(d)].mean()), 4),
                            precision_c5=round(s["precision"], 4), precision_uncut=round(float(prec_uncut[D >= float(d)].mean()), 4),
                            robbins=int((rd >= float(d)).sum()), depressions=int((D >= float(d)).sum()),
                            baseline_recall_uncut=round(float(base_rec[rd >= float(d)].mean()), 4),
                            baseline_precision_uncut=round(float(base_prec[D >= float(d)].mean()), 4))
    res["curve_one_side_cut"] = curve
    print("C5's curve with only the scored set cut:", curve)
    def rec(sel):
        return round(float(uncut[sel].mean()), 4)
    res["recall_candidates_uncut"] = dict(all=rec(big), DEG_RIM={str(s): rec(big & (deg["DEG_RIM"] == s)) for s in (1, 2, 3, 4)},
                                          DEG_RIM_by_diameter={"%g-%g" % b if b[1] < 1e8 else ">=%g" % b[0]:
                                              {str(s): rec(big & (deg["DEG_RIM"] == s) & (rd >= b[0]) & (rd < b[1]))
                                               for s in (1, 2, 3, 4)} for b in BINS},
                                          ARC_IMG=dict(full=rec(full), partial=rec(part)))
    print("recall with the depressions uncut (>= 1 km):", res["recall_candidates_uncut"])
    print("misses: %s" % res["misses"]["all"])
    for k in ("by_rim_state", "by_diameter"):
        for s, d in res["misses"][k].items():
            print("   %-12s %-6s %s" % (k, s, d))
    print("   rim states' share of the misses:", res["misses"]["rim_state_share_of_misses"])

    rr = [res["DEG_RIM"][str(s)]["recall"] for s in (1, 2, 3, 4)]
    gaps = {k: round(100 * (v["full"]["recall"] - v["partial"]["recall"]), 1)
            for k, v in res["ARC_IMG_by_diameter"].items() if k != ">=50"}
    res["predictions"] = {
        "P1": dict(recall_by_rim_state=rr, held=bool(all(a < b for a, b in zip(rr, rr[1:])))),
        "P2": dict(rim4=rr[3], rim1=rr[0], held=bool(rr[3] >= 0.70 and rr[0] <= 0.35)),
        "P3": dict(full_minus_partial_pt=gaps, held=bool(all(g >= 15 for g in gaps.values())))}
    print("D >= %g km: %d Robbins craters, recall %.3f (baseline %.3f); states missing on %d"
          % (DMIN, res["all"]["n"], res["all"]["recall"], res["all"]["baseline"], res["states_missing"]))
    for f in deg:
        print("  %-8s" % f, ", ".join("%s: %.3f of %d (base %.3f)" % (s, t["recall"], t["n"], t["baseline"])
                                      for s, t in res[f].items()))
    print("  ARC_IMG  full %.3f of %d, partial %.3f of %d" % (res["ARC_IMG"]["full"]["recall"], res["ARC_IMG"]["full"]["n"],
                                                            res["ARC_IMG"]["partial"]["recall"], res["ARC_IMG"]["partial"]["n"]))
    for k, v in res["ARC_IMG_by_diameter"].items():
        print("    %-6s full %s, partial %s" % (k, v["full"], v["partial"]))
    for k, v in res["DEG_RIM_by_diameter"].items():
        print("    rim states %-6s %s" % (k, {s: (t["recall"], t["n"]) for s, t in v.items()}))
    for p, d in res["predictions"].items():
        print(p, "held" if d["held"] else "NOT held", {k: x for k, x in d.items() if k != "held"})
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s  (%.0f s)" % (OUT, time.time() - t0))


if __name__ == "__main__":
    main()
