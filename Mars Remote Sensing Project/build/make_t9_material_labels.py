# -*- coding: utf-8 -*-
r"""Test T9: does thermal IR help predict material labels? (NEXT-STEPS §4 T9, §12.2 A8; KB §56, §69.50)

T1 and T1b scored thermal on landform labels (+1.36 and +1.1 pt, none by balanced accuracy), and the paper's own limit
says a test of thermal value needs material labels. The only material map held is SIM 3292 (Tanaka et al. 2014,
Ref_SIM3292_GeologicUnits, 1,311 polygons); its UnitGroup field is the label here. Unit groups are partly age and
stratigraphy, not material alone, so this is the nearest test available, not the ideal one.

Method
  * Samples: every 10th pixel each way of the stack's 400 m overview (global60_svm_stack_200m.tif, the cell of
    T1 and T1b), a 4 km lattice over ±60°; valid in all 7 bands (> 0). Area weight cos(latitude).
  * Labels: the unit groups rasterised onto the same lattice (Pillow, exterior rings drawn largest first, so the
    units that fill a polygon's holes, always smaller rings, are drawn over it); a group needs >= 1,000 training and
    >= 200 held-out samples at the block split, or it is dropped from both splits.
    Checked against arcpy point-in-polygon at 400 random samples (>= 95 % agreement required; the same check on the
    labels shifted 25 cells, 100 km, east must fall below it, or the check is not trusted).
  * Two splits: (1) the label sets' 14 held-out 15° blocks (logs\block_split.json) against every other block, so a
    group is predicted where none of it was trained, as T1; (2) within blocks: 3° cells, a random half held out, so
    training and testing share each region.
  * Classifier: Gaussian maximum likelihood, equal priors, as make_thermal_ablation.py (not the published SVM; the
    comparison between band sets is the result). Band sets: all 7, without thermal, thermal only, without visible.
  * Score: area-weighted overall accuracy, kappa, balanced accuracy (mean producer's over the groups held out).
    Intervals: 1,000 paired bootstrap resamples of whole 15° blocks of the held-out samples.

Answer rule: thermal HELPS on material labels at a split if the all-7 set beats "without thermal" in overall accuracy
with the 95 % interval above 0 AND in balanced accuracy with the interval above 0; otherwise it does NOT HELP there.

Prediction, written before the first run (2026-11-01):
  P1  at the block split, thermal adds under 3 points of overall accuracy (the mosaics are contrast-normalised
      within regions, KB §28.10, which removes the regional contrast that would separate units);
  P2  thermal adds more within blocks than at the block split (local contrast survives the normalisation);
  P3  at the block split the balanced-accuracy gain's interval includes 0, as T1's did.
Each is reported as held or not held.

  "<ArcGIS Pro Python>" make_t9_material_labels.py [--fresh]   -> logs\t9_material_labels.json
  (reads ~6.6 GB of the 400 m overview, once; the samples are cached in %LOCALAPPDATA%\Temp\mars_scratch)
"""
import os, sys, json, time, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G

STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
SIM = "Ref_SIM3292_GeologicUnits"
OUT = os.path.join(HERE, "logs", "t9_material_labels.json")
SPLIT = os.path.join(HERE, "logs", "block_split.json")
CACHE = os.path.join(os.environ.get("LOCALAPPDATA", HERE), "Temp", "mars_scratch", "t9_samples.npz")
BANDS = ["Viking R", "Viking G", "Viking B", "Night IR", "Day IR", "slope", "relief"]
BANDSETS = {"all 7 bands": [0, 1, 2, 3, 4, 5, 6], "without thermal (no night, day)": [0, 1, 2, 5, 6],
            "thermal only": [3, 4], "without visible (no Viking)": [3, 4, 5, 6]}
R = G.R_MARS
OX, OY, OV = -10669400.0, 3556500.0, 400.0
STEP, OFF = 10, 5                      # lattice: overview pixels OFF, OFF + STEP, ...
CELL = STEP * OV                       # 4 km
BLOCK, WCELL = 15.0, 3.0
MIN_TRAIN, MIN_TEST, NBOOT, SEED = 1000, 200, 1000, 20261101
t0 = time.time()


def log(msg):
    print("[%6.1fs] %s" % (time.time() - t0, msg), flush=True)


def to_uv(lon, lat):
    """Degrees (lon east, any range) -> lattice image coordinates; a lattice sample's centre maps to (j + .5, i + .5)."""
    x = R * np.radians(np.asarray(lon, float) - 180.0)
    y = R * np.radians(np.asarray(lat, float))
    shift = (OFF + 0.5) / STEP - 0.5                   # the sample sits at overview pixel OFF of each STEP
    return (x - OX) / CELL - shift, (OY - y) / CELL - shift


def lattice_lonlat(i, j):
    """Lattice row i, column j -> (lon east 0-360, lat) of the sample's centre."""
    x = OX + (STEP * np.asarray(j) + OFF + 0.5) * OV
    y = OY - (STEP * np.asarray(i) + OFF + 0.5) * OV
    return 180.0 + np.degrees(x / R), np.degrees(y / R)


def ring_area(r):
    a = np.asarray(r)
    return 0.5 * abs(np.dot(a[:, 0], np.roll(a[:, 1], 1)) - np.dot(a[:, 1], np.roll(a[:, 0], 1)))


def rasterise(rings, ny, nx):
    """rings: (code, [(lon, lat), ...]) exterior rings in degrees, longitude -180..180. Largest first; each drawn at
    its own longitude and +360, so a ring west of 0 lands on the 0-360 lattice and nothing is lost at the seam."""
    from PIL import Image, ImageDraw
    img = Image.new("L", (nx, ny), 0)
    dr = ImageDraw.Draw(img)
    for code, ring in sorted(rings, key=lambda cr: -ring_area(cr[1])):
        a = np.asarray(ring, float)
        for off in (0.0, 360.0):
            u, v = to_uv(a[:, 0] + off, a[:, 1])
            if u.max() < 0 or u.min() > nx:
                continue
            dr.polygon(list(zip(u.tolist(), v.tolist())), fill=int(code))
    return np.asarray(img)


def read_units():
    import arcpy
    from paths import GDB
    rings, polys = [], []
    with arcpy.da.SearchCursor(os.path.join(GDB, SIM), ["SHAPE@", "UnitGroup"],
                               spatial_reference=arcpy.SpatialReference(104905)) as cur:
        for shp, grp in cur:
            polys.append((shp, grp))
            for part in shp:
                ring = []
                for p in part:
                    if p is None:                      # interior rings follow: their units are drawn after
                        break
                    ring.append((p.X, p.Y))
                if len(ring) >= 3:
                    rings.append((grp, ring))
    return rings, polys


def read_lattice(ny, nx):
    from osgeo import gdal
    gdal.UseExceptions()
    ds = gdal.Open(STACK)
    b1 = ds.GetRasterBand(1)
    k = [i for i in range(b1.GetOverviewCount()) if b1.GetOverview(i).XSize == G.G200.nx // 2]
    assert k, "no 400 m overview on the stack"
    ovs = [ds.GetRasterBand(b + 1).GetOverview(k[0]) for b in range(7)]
    W, H = ovs[0].XSize, ovs[0].YSize
    X = np.zeros((ny, nx, 7), np.uint8)
    cols = OFF + STEP * np.arange(nx)
    for r0 in range(0, H, 512):
        h = min(512, H - r0)
        rows = np.arange(r0, r0 + h)
        keep = rows[((rows - OFF) % STEP == 0) & ((rows - OFF) // STEP < ny)]
        if keep.size == 0:
            continue
        ii = (keep - OFF) // STEP
        for b, o in enumerate(ovs):
            X[ii, :, b] = o.ReadAsArray(0, r0, W, h)[keep - r0][:, cols]
        if (r0 // 512) % 5 == 0:
            log("  strip %d / %d" % (r0 // 512 + 1, (H + 511) // 512))
    rng = np.random.default_rng(SEED)
    pi, pj = rng.integers(0, ny, 50), rng.integers(0, nx, 50)
    for i, j in zip(pi, pj):
        for b in (0, 3, 6):
            v = int(ovs[b].ReadAsArray(int(OFF + STEP * j), int(OFF + STEP * i), 1, 1)[0, 0])
            assert v == X[i, j, b], "lattice read disagrees at %d, %d band %d" % (i, j, b)
    log("check: 150 single-pixel reads match the strip reads")
    return X


def spot_check(lab, polys, codes, rng, shift=0):
    """Share of 400 random labelled samples whose lattice label is the group of the polygon arcpy says holds them."""
    import arcpy
    mars = arcpy.SpatialReference(104905)
    ext = [(s.extent.XMin, s.extent.YMin, s.extent.XMax, s.extent.YMax) for s, _ in polys]
    lab = np.roll(lab, shift, axis=1)
    ii, jj = np.nonzero(lab > 0)
    pick = rng.choice(ii.size, 400, replace=False)
    agree = n = 0
    for q in pick:
        lon, lat = lattice_lonlat(ii[q], jj[q])
        lon = lon - 360.0 if lon >= 180.0 else lon
        pt = arcpy.PointGeometry(arcpy.Point(float(lon), float(lat)), mars)
        hit = [g for (s, g), e in zip(polys, ext)
               if e[0] <= lon <= e[2] and e[1] <= lat <= e[3] and s.contains(pt)]
        if hit:
            n += 1
            agree += codes.get(hit[0]) == lab[ii[q], jj[q]]
    return agree / max(n, 1), n


def fit(X, y, cols, K):
    models = []
    for k in range(K):
        Z = X[y == k][:, cols].astype(np.float64)
        cov = np.cov(Z, rowvar=False) + np.eye(len(cols)) * 1e-3
        models.append((Z.mean(0), np.linalg.inv(cov), np.linalg.slogdet(cov)[1]))
    return models


def predict(models, X, cols, chunk=500000):
    out = np.empty(len(X), np.int16)
    for i in range(0, len(X), chunk):
        Z = X[i:i + chunk][:, cols].astype(np.float64)
        ll = np.stack([-0.5 * (np.einsum("ij,jk,ik->i", Z - mu, icov, Z - mu) + logdet)
                       for mu, icov, logdet in models], axis=1)
        out[i:i + chunk] = ll.argmax(1)
    return out


def stats(cms):
    """cms: ... x K x K (rows truth) -> accuracy, kappa, balanced accuracy (mean producer's over rows present)."""
    tot = cms.sum(axis=(-2, -1))
    po = np.trace(cms, axis1=-2, axis2=-1) / tot
    pe = (cms.sum(-2) * cms.sum(-1)).sum(-1) / tot ** 2
    rows = cms.sum(-1)
    prod = np.where(rows > 0, np.diagonal(cms, axis1=-2, axis2=-1) / np.where(rows > 0, rows, 1), np.nan)
    return po, (po - pe) / (1 - pe), np.nanmean(prod, -1), prod


def selftest():
    u, v = to_uv(*lattice_lonlat(np.array([0, 7, 1777]), np.array([0, 9, 5333])))
    ok_map = np.allclose(u, [0.5, 9.5, 5333.5]) and np.allclose(v, [0.5, 7.5, 1777.5])
    # a 20 x 20-cell square of code 1 with a 6 x 6 hole holding code 2, and a square across the 180° seam
    d = CELL / R * 180 / math.pi
    sq = lambda lo, la, n: [(lo, la), (lo + n * d, la), (lo + n * d, la - n * d), (lo, la - n * d)]
    lo0, la0 = lattice_lonlat(100, 1000)
    lo0 = lo0 - 180.0
    img = rasterise([(2, sq(lo0 + 7 * d, la0 - 7 * d, 6)), (1, sq(lo0, la0, 20)),
                     (3, sq(-180.0 - 4 * d * 0, -10.0, 10))], 1778, 5334)
    ok_hole = (img == 2).sum() in range(30, 50) and (img == 1).sum() in range(330, 420)
    s3 = (img == 3)
    ok_seam = s3.sum() in range(80, 130) and s3[:, 2667 - 10:2667 + 10].any()
    a = np.zeros((2, 2)); a[0, 0], a[1, 1], a[1, 0] = 6, 2, 2
    po, k, ba, _ = stats(a)
    ok_stats = abs(po - 0.8) < 1e-12 and abs(ba - 0.75) < 1e-12
    checks = {"lattice -> image centres": ok_map, "a hole filled by the unit inside it": ok_hole,
              "a ring at -180 lands mid-lattice": ok_seam, "accuracy and balanced accuracy": ok_stats}
    for name, ok in checks.items():
        log("selftest %-36s %s" % (name, "ok" if ok else "FAIL"))
    assert all(checks.values()), "self-test failed"


def main():
    selftest()
    if "--selftest" in sys.argv:
        return
    ny, nx = (G.G200.ny // 2 + 1 - OFF + STEP - 1) // STEP, (G.G200.nx // 2 - OFF + STEP - 1) // STEP
    rng = np.random.default_rng(SEED)
    rings, polys = read_units()
    groups = sorted({g for g, _ in rings})
    codes = {g: c for c, g in enumerate(groups, 1)}
    log("SIM 3292: %d polygons, %d exterior rings, %d unit groups" % (len(polys), len(rings), len(groups)))
    lab = rasterise([(codes[g], r) for g, r in rings], ny, nx)
    agree, n = spot_check(lab, polys, codes, rng)
    agree_shift, n_shift = spot_check(lab, polys, codes, rng, shift=25)
    log("check: lattice labels agree with arcpy at %.1f %% of %d samples; shifted 100 km, %.1f %% of %d"
        % (100 * agree, n, 100 * agree_shift, n_shift))
    assert agree >= 0.95 and agree_shift < 0.95, "the label raster check failed, or does not bite"
    if os.path.exists(CACHE) and "--fresh" not in sys.argv:
        X = np.load(CACHE)["X"]
        log("lattice from cache %s" % CACHE)
    else:
        X = read_lattice(ny, nx)
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        np.savez_compressed(CACHE, X=X)
    assert X.shape == (ny, nx, 7)
    ii, jj = np.mgrid[0:ny, 0:nx]
    lon, lat = lattice_lonlat(ii, jj)
    lon_g = np.where(lon >= 180.0, lon - 360.0, lon)
    valid = (lab > 0) & (X > 0).all(-1)
    split = json.load(open(SPLIT, encoding="utf-8"))
    assert split["same_held_out_blocks"]
    held = set(split["v2"]["test_blocks"])
    code = lambda bx, by: (bx + 100) * 100 + (by + 10)          # the block "bx_by" as one integer
    bid = code(np.floor(lon_g / BLOCK).astype(np.int32), np.floor(lat / BLOCK).astype(np.int32))
    test_block = np.isin(bid, [code(*map(int, b.split("_"))) for b in held])
    cx, cy = np.floor(lon_g / WCELL).astype(int), np.floor(lat / WCELL).astype(int)
    cell = (cx + 1000) * 1000 + (cy + 100)
    uc = np.unique(cell)
    test_cells = rng.choice(uc, uc.size // 2, replace=False)
    test_within = np.isin(cell, test_cells)
    # groups with enough samples at the block split, in both splits
    y_all = lab.astype(int)
    keep = [g for g in groups if ((y_all == codes[g]) & valid & ~test_block).sum() >= MIN_TRAIN
            and ((y_all == codes[g]) & valid & test_block).sum() >= MIN_TEST]
    dropped = [g for g in groups if g not in keep]
    K = len(keep)
    remap = np.full(len(groups) + 1, -1, int)
    for k, g in enumerate(keep):
        remap[codes[g]] = k
    y = remap[y_all]
    valid &= y >= 0
    w = np.cos(np.radians(lat)).astype(np.float64)
    log("lattice %d x %d; %d valid labelled samples; groups kept %s, dropped %s"
        % (ny, nx, valid.sum(), keep, dropped))
    res = {"method": "Gaussian maximum likelihood, equal priors, numpy; 4 km lattice of the 400 m overview; "
                     "labels SIM 3292 UnitGroup; area-weighted", "bands": BANDS, "groups": keep, "dropped": dropped,
           "label_check": {"agree": agree, "n": n, "agree_shifted_100km": agree_shift},
           "held_out_blocks": sorted(held), "within_cell_deg": WCELL, "splits": {}}
    for sname, te_mask in (("block", test_block), ("within", test_within)):
        tr, te = valid & ~te_mask, valid & te_mask
        Xtr, ytr = X[tr], y[tr]
        Xte, yte, wte, bte = X[te], y[te], w[te], bid[te]
        ub, binv = np.unique(bte, return_inverse=True)
        B = ub.size
        counts = np.stack([np.bincount(rng.integers(0, B, B), minlength=B) for _ in range(NBOOT)])
        area = np.bincount(yte, weights=wte, minlength=K)
        out = {"n_train": int(tr.sum()), "n_test": int(te.sum()), "test_blocks": int(B),
               "one_group_everywhere": float(area.max() / area.sum()),
               "test_share_by_group": dict(zip(keep, (area / area.sum()).round(4).tolist())), "sets": {}}
        boot = {}
        for name, cols in BANDSETS.items():
            p = predict(fit(Xtr, ytr, cols, K), Xte, cols)
            cmb = np.zeros((B, K, K))
            np.add.at(cmb, (binv, yte, p), wte)
            po, kap, ba, prod = stats(cmb.sum(0))
            boot[name] = stats(np.tensordot(counts, cmb, axes=1))
            out["sets"][name] = {"accuracy": float(po), "kappa": float(kap), "balanced_accuracy": float(ba),
                                 "producers": dict(zip(keep, np.round(prod, 4).tolist()))}
            log("%-6s %-32s acc %5.1f %%  kappa %.3f  balanced %5.1f %%" % (sname, name, 100 * po, kap, 100 * ba))
        ci = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
        full = out["sets"]["all 7 bands"]
        for name in BANDSETS:
            if name == "all 7 bands":
                continue
            s = out["sets"][name]
            s["gain_from_full_stack"] = {
                "accuracy": full["accuracy"] - s["accuracy"], "accuracy_ci95": ci(boot["all 7 bands"][0] - boot[name][0]),
                "kappa": full["kappa"] - s["kappa"], "kappa_ci95": ci(boot["all 7 bands"][1] - boot[name][1]),
                "balanced_accuracy": full["balanced_accuracy"] - s["balanced_accuracy"],
                "balanced_accuracy_ci95": ci(boot["all 7 bands"][2] - boot[name][2]),
                "producers": {g: dict(gain=float(full["producers"][g] - s["producers"][g]),
                                      ci95=ci(boot["all 7 bands"][3][:, k] - boot[name][3][:, k]))
                              for k, g in enumerate(keep)}}
            g = s["gain_from_full_stack"]
            log("%-6s   all 7 minus %-30s acc %+5.1f pt [%+.1f, %+.1f]  balanced %+5.1f pt [%+.1f, %+.1f]" % (
                sname, name, 100 * g["accuracy"], 100 * g["accuracy_ci95"][0], 100 * g["accuracy_ci95"][1],
                100 * g["balanced_accuracy"], 100 * g["balanced_accuracy_ci95"][0], 100 * g["balanced_accuracy_ci95"][1]))
        g = out["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
        out["thermal_helps"] = bool(g["accuracy_ci95"][0] > 0 and g["balanced_accuracy_ci95"][0] > 0)
        for gname, v in g["producers"].items():
            log("%-6s     %-4s producer's %+5.1f pt [%+.1f, %+.1f]" % (sname, gname, 100 * v["gain"], 100 * v["ci95"][0], 100 * v["ci95"][1]))
        log("%-6s thermal %s on material labels (one group everywhere: %.1f %%)"
            % (sname, "HELPS" if out["thermal_helps"] else "does NOT HELP", 100 * out["one_group_everywhere"]))
        res["splits"][sname] = out
    gb = res["splits"]["block"]["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
    gw = res["splits"]["within"]["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
    res["predictions"] = {
        "P1 block split: thermal adds < 3 pt of accuracy": bool(gb["accuracy"] < 0.03),
        "P2 thermal adds more within blocks than at the block split": bool(gw["accuracy"] > gb["accuracy"]),
        "P3 block split: balanced gain's interval includes 0": bool(gb["balanced_accuracy_ci95"][0] <= 0
                                                                   <= gb["balanced_accuracy_ci95"][1])}
    for k, v in res["predictions"].items():
        log("prediction %-60s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
