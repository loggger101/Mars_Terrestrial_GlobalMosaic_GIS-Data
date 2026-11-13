# -*- coding: utf-8 -*-
r"""Test T13: what surface material do the lead maps' landform classes sit on? (KB §69.136)

The two lead seven-class maps (D36: the U-Net v3 and the SVM v3, KB §69.82) are landform maps; T11 (KB §69.134) gave a
calibrated material label, the thermophysical units of TES inertia x TES albedo. This crosses them: for every 0.05 deg
TES cell within 60 deg that TES measured, the map class at the cell centre's 200 m pixel against the cell's unit.

Units: T11's, unchanged (inertia 150 tiu, albedo 0.20; A dust = low inertia bright, C duricrust = high inertia bright,
B sand and rock = high inertia dark; the low-inertia dark corner, 0.9 % of the area, left out). Weights cos(latitude).
Per class: its unit shares and each unit's enrichment (share in the class / share over all classes), the median
inertia and albedo. Association: Cramer's V of class x unit, and the share of the unit's entropy the class removes
(uncertainty coefficient U(unit|class)). Intervals: 1,000 resamples of whole 15 deg blocks.

Predictions, written 2026-11-12 before the first run:
  P1  U-Net: volcanic edifice is dust-rich, its A share more than 1.5 times A's share over the map (Tharsis and Elysium
      are the dustiest provinces).
  P2  U-Net: Crater and fluvial channel are each enriched in B (sand and rock), enrichment above 1.
  P3  Both maps: Cramer's V under 0.30, the landform classes are not material classes.
  P4  The SVM's V exceeds the U-Net's: its classes follow each pixel's colour, which tracks albedo, where the U-Net's
      follow shape.

  "<ArcGIS Pro Python>" make_t13_maps_on_units.py   -> logs\t13_maps_on_units.json
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
import labelsets
from osgeo import gdal

gdal.UseExceptions()
OUT = os.path.join(HERE, "logs", "t13_maps_on_units.json")
TES = os.path.join(os.path.dirname(G.OUTDIR), "Reference", "TES_thermal_inertia_2007")
ALB = os.path.join(os.path.dirname(G.OUTDIR), "Reference", "TES_albedo_USGS", "Mars_MGS_TES_Albedo_mosaic_global_7410m.tif")
MAPS = {"U-Net v3": ("global60_landforms_unet_v3_200m_seamfix.tif", 0),
        "SVM v3": ("global60_landforms_svm_v3_200m.tif", 255)}
CLASSES = labelsets.SEVEN
UNITS = ["A dust", "C duricrust", "B sand and rock"]
TI_EDGE, ALB_EDGE, NBOOT, SEED = 150, 0.20, 1000, 20261112
OX, OY, PX, R = G.G200.ox, G.G200.oy, 200.0, G.R_MARS


def log(m):
    print(m, flush=True)


def tes_cells():
    ti = gdal.Open(os.path.join(TES, "TES_TI_2007_nightside.tif")).ReadAsArray()
    meas = gdal.Open(os.path.join(TES, "TES_TI_2007_nightside_measured.tif")).ReadAsArray()
    ds = gdal.Open(ALB)
    a, gt = ds.ReadAsArray(), ds.GetGeoTransform()
    r, c = np.mgrid[0:3600, 0:7200]
    lat, lon = 90.0 - (r + 0.5) * 0.05, -180.0 + (c + 0.5) * 0.05
    keep = (np.abs(lat) < 59.9) & (meas == 1) & (ti > 0)
    lat, lon, tv = lat[keep], lon[keep], ti[keep].astype(float)
    ac = np.clip(((np.radians(lon) * 3396000.0 - gt[0]) / gt[1]).astype(int), 0, a.shape[1] - 1)
    ar = np.clip(((np.radians(lat) * 3396000.0 - gt[3]) / gt[5]).astype(int), 0, a.shape[0] - 1)
    av = a[ar, ac].astype(float)
    unit = np.full(lat.size, -1, np.int8)
    hi, br = tv >= TI_EDGE, av >= ALB_EDGE
    unit[~hi & br], unit[hi & br], unit[hi & ~br] = 0, 1, 2
    return lat, lon, tv, av, unit


def map_classes(path, nodata, lat, lon):
    lon360 = np.mod(lon, 360.0)
    col = np.floor((R * np.radians(lon360 - 180.0) - OX) / PX).astype(np.int64)
    row = np.floor((OY - R * np.radians(lat)) / PX).astype(np.int64)
    ds = gdal.Open(path)
    b = ds.GetRasterBand(1)
    ok = (row >= 0) & (row < ds.RasterYSize) & (col >= 0) & (col < ds.RasterXSize)
    out = np.full(lat.size, -1, np.int16)
    order = np.argsort(row)
    rs = row[order]
    STRIP = 1024
    for r0 in range(0, ds.RasterYSize, STRIP):
        lo, hi = np.searchsorted(rs, r0), np.searchsorted(rs, r0 + STRIP)
        if lo == hi:
            continue
        idx = order[lo:hi]
        idx = idx[ok[idx]]
        n = min(STRIP, ds.RasterYSize - r0)
        A = b.ReadAsArray(0, r0, ds.RasterXSize, n)
        v = A[row[idx] - r0, col[idx]].astype(np.int16)
        out[idx] = np.where((v == nodata) | (v < 1) | (v > len(CLASSES)), -1, v - 1)
    # check: 50 cells against single-pixel reads
    rng = np.random.default_rng(SEED)
    pick = rng.choice(np.flatnonzero(ok), 50, replace=False)
    same = 0
    for i in pick:
        v = int(b.ReadAsArray(int(col[i]), int(row[i]), 1, 1)[0, 0])
        same += (v - 1 if 1 <= v <= len(CLASSES) and v != nodata else -1) == int(out[i])
    assert same == 50, same
    log("check: 50 of 50 cells equal single-pixel reads of %s" % os.path.basename(path))
    return out


def assoc(T):
    """T: ... x C x U weighted table -> Cramer's V, uncertainty coefficient U(unit | class)."""
    n = T.sum((-2, -1), keepdims=True)
    P = T / n
    pc, pu = P.sum(-1, keepdims=True), P.sum(-2, keepdims=True)
    E = pc * pu
    chi = np.where(E > 0, (P - E) ** 2 / np.where(E > 0, E, 1), 0).sum((-2, -1))
    k = min(T.shape[-2], T.shape[-1]) - 1
    V = np.sqrt(chi / k)
    with np.errstate(divide="ignore", invalid="ignore"):
        Hu = -np.nansum(np.where(pu > 0, pu * np.log(pu), 0), (-2, -1))
        Huc = -np.nansum(np.where(P > 0, P * np.log(np.where(P > 0, P, 1) / np.where(pc > 0, pc, 1)), 0), (-2, -1))
    return V, (Hu - Huc) / Hu


def main():
    lat, lon, tv, av, unit = tes_cells()
    w = np.cos(np.radians(lat))
    log("%d measured TES cells within 59.9 deg; %d in units A/C/B" % (lat.size, (unit >= 0).sum()))
    bid = (np.floor(lon / 15).astype(int) + 100) * 100 + (np.floor(lat / 15).astype(int) + 10)
    ub, binv = np.unique(bid, return_inverse=True)
    rng = np.random.default_rng(SEED)
    counts = np.stack([np.bincount(rng.integers(0, ub.size, ub.size), minlength=ub.size) for _ in range(NBOOT)])
    res = {"units": UNITS, "classes": CLASSES, "ti_edge": TI_EDGE, "albedo_edge": ALB_EDGE, "maps": {}}
    boots = {}
    for name, (fn, nd) in MAPS.items():
        cls = map_classes(os.path.join(G.OUTDIR, fn), nd, lat, lon)
        m = (cls >= 0) & (unit >= 0)
        Tb = np.zeros((ub.size, len(CLASSES), len(UNITS)))
        np.add.at(Tb, (binv[m], cls[m], unit[m]), w[m])
        T = Tb.sum(0)
        V, Uc = assoc(T)
        Vb, Ub = assoc(np.tensordot(counts, Tb, axes=1))
        overall = T.sum(0) / T.sum()
        per = {}
        for k, c in enumerate(CLASSES):
            mk = cls == k
            sh = T[k] / T[k].sum() if T[k].sum() > 0 else np.full(3, np.nan)
            per[c] = {"area_share": float(T[k].sum() / T.sum()),
                      "unit_shares": dict(zip(UNITS, np.round(sh, 4).tolist())),
                      "enrichment": dict(zip(UNITS, np.round(sh / overall, 3).tolist())),
                      "median_inertia": float(np.median(tv[mk])) if mk.any() else None,
                      "median_albedo": float(np.median(av[mk])) if mk.any() else None}
            log("%-9s %-18s area %5.1f %%  A %5.1f  C %5.1f  B %5.1f %%  enrich %s  TI %4.0f  alb %.3f" % (
                name, c, 100 * per[c]["area_share"], *(100 * sh), " ".join("%.2f" % e for e in sh / overall),
                per[c]["median_inertia"] or 0, per[c]["median_albedo"] or 0))
        res["maps"][name] = {"overall_unit_shares": dict(zip(UNITS, np.round(overall, 4).tolist())),
                             "cramers_v": float(V), "cramers_v_ci95": np.percentile(Vb, [2.5, 97.5]).tolist(),
                             "uncertainty_coefficient": float(Uc), "uc_ci95": np.percentile(Ub, [2.5, 97.5]).tolist(),
                             "classes": per, "check_single_reads": 50}
        boots[name] = (Vb, Ub)
        log("%-9s overall A/C/B %s; Cramer's V %.3f [%.3f, %.3f]; U(unit|class) %.3f [%.3f, %.3f]" % (
            name, np.round(overall, 3).tolist(), V, *np.percentile(Vb, [2.5, 97.5]), Uc, *np.percentile(Ub, [2.5, 97.5])))
    U, S = res["maps"]["U-Net v3"], res["maps"]["SVM v3"]
    # the two maps on the same block draws: a paired interval of the difference (added after the first run, which
    # gave both intervals separately; not a prediction)
    dV = boots["SVM v3"][0] - boots["U-Net v3"][0]
    dU = boots["SVM v3"][1] - boots["U-Net v3"][1]
    res["svm_minus_unet"] = {"cramers_v": S["cramers_v"] - U["cramers_v"], "cramers_v_ci95": np.percentile(dV, [2.5, 97.5]).tolist(),
                             "uc": S["uncertainty_coefficient"] - U["uncertainty_coefficient"],
                             "uc_ci95": np.percentile(dU, [2.5, 97.5]).tolist()}
    log("SVM minus U-Net, paired: V %+.3f [%+.3f, %+.3f]; U %+.3f [%+.3f, %+.3f]" % (
        res["svm_minus_unet"]["cramers_v"], *res["svm_minus_unet"]["cramers_v_ci95"],
        res["svm_minus_unet"]["uc"], *res["svm_minus_unet"]["uc_ci95"]))
    res["predictions"] = {
        "P1 U-Net: volcanic edifice A enrichment > 1.5": U["classes"]["volcanic edifice"]["enrichment"]["A dust"] > 1.5,
        "P2 U-Net: Crater and fluvial channel B enrichment > 1":
            U["classes"]["Crater"]["enrichment"]["B sand and rock"] > 1
            and U["classes"]["fluvial channel"]["enrichment"]["B sand and rock"] > 1,
        "P3 both maps: Cramer's V < 0.30": U["cramers_v"] < 0.30 and S["cramers_v"] < 0.30,
        "P4 SVM's V > U-Net's": S["cramers_v"] > U["cramers_v"]}
    for k, v in res["predictions"].items():
        log("prediction %-50s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
