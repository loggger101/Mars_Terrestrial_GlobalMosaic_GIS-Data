# -*- coding: utf-8 -*-
r"""Test T11: do the thermal bands help predict thermophysical units, inertia crossed with albedo? (KB §69.134)

T10 (make_t10_ti_labels.py, KB §69.133) used TES nightside thermal inertia alone as the label and found Viking carries
the material signal, the thermal pair about half a point within blocks. Inertia and albedo together define the classic
thermophysical units (Mellon et al. 2000; Putzig et al. 2005), and one of them is the case the thermal bands ought to
win: bright, high-inertia surfaces (unit C, duricrust) look like bright dust (unit A) in albedo and in Viking colour,
and differ only in inertia.

Labels: TES nightside inertia (Putzig & Mellon 2007, measured cells only, as T10) crossed with TES Lambert albedo
(USGS Astrogeology mosaic `Mars_MGS_TES_Albedo_mosaic_global_7410m.tif`, 0.125 deg, downloaded 2026-11-12 at the author's
yes to `Mars Project\Reference\TES_albedo_USGS\`, SHA-256 c91dfcaa...e58178). Edges fixed before any model ran: inertia
150 tiu (T10's), albedo 0.20 (between the dark regions below ~0.15 and the bright above ~0.24). Shares by area within
60 deg were looked at before this header was written (0.275 / 0.009 / 0.251 / 0.466); the low-inertia dark corner,
0.9 %, is dropped as too rare to score, which leaves three units:
  1 A   low inertia (< 150), bright (albedo >= 0.20)    dust
  2 C   high inertia (>= 150), bright                   duricrust, indurated fines
  3 B   high inertia, dark (albedo < 0.20)              sand, rock
Everything else is T10's and so T9's (imported): the 4 km lattice, the 14 held-out 15 deg blocks and the within-block
split, Gaussian maximum likelihood with equal priors, cos-latitude weights, 1,000 block resamples, the four band sets
and the answer rule (thermal HELPS at a split only if all 7 bands beat "without thermal" with both the accuracy and the
balanced-accuracy intervals above 0).

Predictions, written 2026-11-12 before the first run:
  P1  At the block split thermal adds under 3 points of accuracy (as T10).
  P2  Thermal adds more within blocks than at the block split (as T10).
  P3  At the block split leaving out Viking costs more balanced accuracy than leaving out thermal (albedo is half the
      label and Viking tracks it).
  P4  At the block split all 7 bands reach at least 43.3 % balanced (chance + 10).
  P5  Unit C is where thermal counts: at the block split its producer's accuracy gains more from the thermal bands than
      balanced accuracy does.

  "<ArcGIS Pro Python>" make_t11_thermophysical_units.py   -> logs\t11_thermophysical_units.json
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_t9_material_labels as T9
import make_t10_ti_labels as T10
import grid60 as G

ALB = os.path.join(os.path.dirname(G.OUTDIR), "Reference", "TES_albedo_USGS",
                   "Mars_MGS_TES_Albedo_mosaic_global_7410m.tif")
TI_EDGE, ALB_EDGE = 150, 0.20
CLASSES = ["A dust (low inertia, bright)", "C duricrust (high inertia, bright)", "B sand and rock (high inertia, dark)"]
OUT = os.path.join(HERE, "logs", "t11_thermophysical_units.json")
log = T9.log


def albedo_at(lon_g, lat):
    from osgeo import gdal
    gdal.UseExceptions()
    ds = gdal.Open(ALB)
    a, gt = ds.ReadAsArray(), ds.GetGeoTransform()
    # through the file's own geotransform (7,410 m on R 3,396,000); reading it as exactly 1/8 deg instead moves a sample
    # at most 0.025 deg and gives the same correlation with log inertia (-0.718 either way, checked 2026-11-12)
    c = np.clip(((np.radians(lon_g) * 3396000.0 - gt[0]) / gt[1]).astype(int), 0, a.shape[1] - 1)
    r = np.clip(((np.radians(lat) * 3396000.0 - gt[3]) / gt[5]).astype(int), 0, a.shape[0] - 1)
    return a[r, c]


def unit_labels(lon_g, lat):
    ti_lab, tiv = T10.ti_labels(lon_g, lat)          # 0 where not measured
    alb = albedo_at(lon_g, lat)
    lab = np.zeros(tiv.shape, np.int16)
    hi, bright, ok = tiv >= TI_EDGE, alb >= ALB_EDGE, (ti_lab > 0) & (alb > 0)
    lab[ok & ~hi & bright] = 1
    lab[ok & hi & bright] = 2
    lab[ok & hi & ~bright] = 3
    return lab, alb


def main():
    T9.selftest()
    ny, nx = (G.G200.ny // 2 + 1 - T9.OFF + T9.STEP - 1) // T9.STEP, (G.G200.nx // 2 - T9.OFF + T9.STEP - 1) // T9.STEP
    rng = np.random.default_rng(T9.SEED)
    if os.path.exists(T9.CACHE) and "--fresh" not in sys.argv:
        X = np.load(T9.CACHE)["X"]
        log("lattice from cache %s" % T9.CACHE)
    else:
        X = T9.read_lattice(ny, nx)
        os.makedirs(os.path.dirname(T9.CACHE), exist_ok=True)
        np.savez_compressed(T9.CACHE, X=X)
    ii, jj = np.mgrid[0:ny, 0:nx]
    lon, lat = T9.lattice_lonlat(ii, jj)
    lon_g = np.where(lon >= 180.0, lon - 360.0, lon)
    lab, alb = unit_labels(lon_g, lat)
    # check: 200 albedo values against a direct GDAL read through the file's own geotransform (metres, R 3,396,000)
    from osgeo import gdal
    ds = gdal.Open(ALB)
    gt = ds.GetGeoTransform()
    Rm = 3396000.0
    pi_, pj = rng.integers(0, ny, 200), rng.integers(0, nx, 200)
    same = 0
    for i, j in zip(pi_, pj):
        x, y = np.radians(lon_g[i, j]) * Rm, np.radians(lat[i, j]) * Rm
        col = min(int((x - gt[0]) / gt[1]), ds.RasterXSize - 1)
        row = min(int((y - gt[3]) / gt[5]), ds.RasterYSize - 1)
        same += float(ds.ReadAsArray(col, row, 1, 1)[0, 0]) == float(alb[i, j])
    log("check: %d of 200 lattice albedo values equal a direct GDAL read" % same)
    assert same == 200, same
    valid = (lab > 0) & (X > 0).all(-1)
    y = lab.astype(int) - 1
    split = json.load(open(T9.SPLIT, encoding="utf-8"))
    held = set(split["v2"]["test_blocks"])
    code = lambda bx, by: (bx + 100) * 100 + (by + 10)
    bid = code(np.floor(lon_g / T9.BLOCK).astype(np.int32), np.floor(lat / T9.BLOCK).astype(np.int32))
    test_block = np.isin(bid, [code(*map(int, b.split("_"))) for b in held])
    cx, cy = np.floor(lon_g / T9.WCELL).astype(int), np.floor(lat / T9.WCELL).astype(int)
    cell = (cx + 1000) * 1000 + (cy + 100)
    uc = np.unique(cell)
    test_within = np.isin(cell, rng.choice(uc, uc.size // 2, replace=False))
    w = np.cos(np.radians(lat)).astype(np.float64)
    K = 3
    shares = [round(float(w[valid & (y == k)].sum() / w[valid].sum()), 3) for k in range(K)]
    dropped = float(w[(X > 0).all(-1) & (lab == 0) & (alb > 0)].sum())
    log("lattice %d x %d; %d valid labelled samples; class shares %s" % (ny, nx, valid.sum(), shares))
    res = {"method": "T10's design (make_t10_ti_labels.py, T9's) with thermophysical units, TES inertia x TES albedo",
           "classes": CLASSES, "ti_edge_tiu": TI_EDGE, "albedo_edge": ALB_EDGE, "priors": T9.PRIORS,
           "bands": T9.BANDS, "class_shares": shares, "label_check_direct_reads": same,
           "held_out_blocks": sorted(held), "splits": {}}
    for sname, te_mask in (("block", test_block), ("within", test_within)):
        tr, te = valid & ~te_mask, valid & te_mask
        Xtr, ytr = X[tr], y[tr]
        Xte, yte, wte, bte = X[te], y[te], w[te], bid[te]
        ub, binv = np.unique(bte, return_inverse=True)
        B = ub.size
        counts = np.stack([np.bincount(rng.integers(0, B, B), minlength=B) for _ in range(T9.NBOOT)])
        area = np.bincount(yte, weights=wte, minlength=K)
        out = {"n_train": int(tr.sum()), "n_test": int(te.sum()), "test_blocks": int(B),
               "one_class_everywhere": float(area.max() / area.sum()),
               "test_share_by_class": dict(zip(CLASSES, (area / area.sum()).round(4).tolist())), "sets": {}}
        boot = {}
        for name, cols in T9.BANDSETS.items():
            p = T9.predict(T9.fit(Xtr, ytr, cols, K), Xte, cols)
            cmb = np.zeros((B, K, K))
            np.add.at(cmb, (binv, yte, p), wte)
            po, kap, ba, prod = T9.stats(cmb.sum(0))
            boot[name] = T9.stats(np.tensordot(counts, cmb, axes=1))
            out["sets"][name] = {"accuracy": float(po), "kappa": float(kap), "balanced_accuracy": float(ba),
                                 "producers": dict(zip(CLASSES, np.round(prod, 4).tolist())),
                                 "balanced_ci95": [float(np.nanpercentile(boot[name][2], 2.5)),
                                                   float(np.nanpercentile(boot[name][2], 97.5))]}
            log("%-6s %-32s acc %5.1f %%  kappa %.3f  balanced %5.1f %%  producers %s" % (
                sname, name, 100 * po, kap, 100 * ba, " ".join("%.1f" % (100 * v) for v in prod)))
        ci = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
        full = out["sets"]["all 7 bands"]
        for name in T9.BANDSETS:
            if name == "all 7 bands":
                continue
            s = out["sets"][name]
            s["gain_from_full_stack"] = {
                "accuracy": full["accuracy"] - s["accuracy"], "accuracy_ci95": ci(boot["all 7 bands"][0] - boot[name][0]),
                "balanced_accuracy": full["balanced_accuracy"] - s["balanced_accuracy"],
                "balanced_accuracy_ci95": ci(boot["all 7 bands"][2] - boot[name][2]),
                "producers": {c: full["producers"][c] - s["producers"][c] for c in CLASSES},
                "producers_ci95": {c: ci(boot["all 7 bands"][3][:, k] - boot[name][3][:, k])
                                   for k, c in enumerate(CLASSES)}}
            g = s["gain_from_full_stack"]
            log("%-6s   all 7 minus %-30s acc %+5.1f pt [%+.1f, %+.1f]  balanced %+5.1f pt [%+.1f, %+.1f]" % (
                sname, name, 100 * g["accuracy"], 100 * g["accuracy_ci95"][0], 100 * g["accuracy_ci95"][1],
                100 * g["balanced_accuracy"], 100 * g["balanced_accuracy_ci95"][0], 100 * g["balanced_accuracy_ci95"][1]))
            for c in CLASSES:
                log("%-6s       producer's %-38s %+5.1f pt [%+.1f, %+.1f]" % (
                    sname, c, 100 * g["producers"][c], 100 * g["producers_ci95"][c][0], 100 * g["producers_ci95"][c][1]))
        g = out["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
        out["thermal_helps"] = bool(g["accuracy_ci95"][0] > 0 and g["balanced_accuracy_ci95"][0] > 0)
        log("%-6s thermal %s on thermophysical units (one class everywhere %.1f %%)"
            % (sname, "HELPS" if out["thermal_helps"] else "does NOT HELP", 100 * out["one_class_everywhere"]))
        res["splits"][sname] = out
    S = res["splits"]
    gb = S["block"]["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
    gw = S["within"]["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
    gv = S["block"]["sets"]["without visible (no Viking)"]["gain_from_full_stack"]
    res["predictions"] = {
        "P1 block: thermal adds < 3 pt of accuracy": bool(gb["accuracy"] < 0.03),
        "P2 thermal adds more within blocks than at the block split": bool(gw["accuracy"] > gb["accuracy"]),
        "P3 block: leaving out Viking costs more balanced accuracy than leaving out thermal":
            bool(gv["balanced_accuracy"] > gb["balanced_accuracy"]),
        "P4 block: all 7 bands >= 43.3 % balanced": bool(S["block"]["sets"]["all 7 bands"]["balanced_accuracy"] >= 0.433),
        "P5 block: unit C's producer's gain from thermal exceeds the balanced-accuracy gain":
            bool(gb["producers"][CLASSES[1]] > gb["balanced_accuracy"])}
    for k, v in res["predictions"].items():
        log("prediction %-84s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
