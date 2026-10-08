# -*- coding: utf-8 -*-
r"""D6, fast test: does relabelling "lava tube" from the geologic map help? (KB §43, NEXT-STEPS D6)

The hand-drawn "lava tube" class is right 2 % of the time (§31.3) and sits on volcano flanks and
aprons, not on volcanic plains (T8). Approved 2026-10-08: relabel it from SIM 3292's volcanic units.
This measures whether that is worth the ~3 h Pro SVM rerun, with the same classifier as T1
(Gaussian maximum likelihood, equal priors, numpy) at the stack's 1.6 km overview.

Variants, all scored on the SAME held-out 15° blocks of the §31 split:
  A  the four hand-drawn classes, as published
  B  Crater, steep/windy hills, Normal Ground from the hand labels + "volcanic (map)": pixels of
     SIM 3292 units v / ve / vf outside every hand polygon; training from training blocks and from
     blocks with no labels, testing from held-out blocks only
  C  three classes: lava tube dropped
Common ground: accuracy on the held-out Crater / hills / Normal Ground polygons for all three; the
volcanic class scored separately; and where B puts the held-out hand "lava tube" polygons.
Prediction, written before the run: B's volcanic class reaches a useful producer's accuracy only
if volcanic plains differ spectrally from other plains, which T8 suggests they do not (they come
out Normal Ground 75 % of the time); so expect a weak volcanic class and little change elsewhere.
Read-only; writes build\logs\lava_relabel_test.json.
"""
import os, sys, json
import numpy as np
from osgeo import gdal, ogr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import grid60 as G
from make_geomap_check import unit_raster, STEP
from make_thermal_ablation import fit, predict, scores

gdal.UseExceptions(); ogr.UseExceptions()
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
VOLCANIC = {"v", "ve", "vf"}
OUT = os.path.join(HERE, "logs", "lava_relabel_test.json")
COLS = list(range(7))


def hand_raster():
    """OID of the hand polygon covering each 0.02° cell (0 = none), and per OID: class, split, block."""
    import arcpy
    mem = ogr.GetDriverByName("MEM").CreateDataSource("h")
    lyr = mem.CreateLayer("h", geom_type=ogr.wkbMultiPolygon)
    lyr.CreateField(ogr.FieldDefn("k", ogr.OFTInteger))
    meta, k = {}, 0
    for split in ("train", "test"):
        fc = os.path.join(GDB, "Landform_TrainingSamples_terrain_60_" + split)
        with arcpy.da.SearchCursor(fc, ["SHAPE@WKT", "Classvalue", "Block"], spatial_reference=arcpy.SpatialReference(104905)) as c:
            for wkt, v, blk in c:
                k += 1
                meta[k] = (int(v), split, blk)
                f = ogr.Feature(lyr.GetLayerDefn()); f.SetGeometry(ogr.CreateGeometryFromWkt(wkt)); f.SetField("k", k)
                lyr.CreateFeature(f)
    W, H = int(360 / STEP), int(120 / STEP)
    ds = gdal.GetDriverByName("MEM").Create("", W, H, 1, gdal.GDT_Int32)
    ds.SetGeoTransform((-180.0, STEP, 0, 60.0, 0, -STEP))
    gdal.RasterizeLayer(ds, [1], lyr, options=["ATTRIBUTE=k"])
    return ds.ReadAsArray(), meta


def main():
    units, gname = unit_raster()
    hand, meta = hand_raster()
    test_blocks = {b for (_, s, b) in meta.values() if s == "test"}
    ds = gdal.Open(STACK)
    b1 = ds.GetRasterBand(1)
    ov = min(range(b1.GetOverviewCount()), key=lambda i: abs(G.G200.res * b1.XSize / b1.GetOverview(i).XSize - 1600))
    cell = G.G200.res * b1.XSize / b1.GetOverview(ov).XSize
    X = np.stack([ds.GetRasterBand(b + 1).GetOverview(ov).ReadAsArray() for b in range(7)], axis=-1)
    H, W = X.shape[:2]
    xs = G.G200.ox + (np.arange(W) + .5) * cell
    ys = G.G200.oy - (np.arange(H) + .5) * cell
    lon = (180.0 + np.degrees(xs / G.R_MARS) + 180.0) % 360.0 - 180.0
    lat = np.degrees(ys / G.R_MARS)
    col = ((lon + 180.0) / STEP).astype(int).clip(0, units.shape[1] - 1)
    row = ((60.0 - lat) / STEP).astype(int).clip(0, units.shape[0] - 1)
    U = units[row[:, None], col[None, :]]
    K = hand[row[:, None], col[None, :]]
    blk = np.char.add(np.char.add(np.floor(lon / 15).astype(int).astype(str)[None, :].repeat(H, 0), "_"),
                      np.floor(lat / 15).astype(int).astype(str)[:, None].repeat(W, 1))
    w = np.repeat(np.cos(np.radians(lat))[:, None], W, axis=1)
    valid = (X > 0).all(-1)
    volc_codes = [c for c, n in gname.items() if n in VOLCANIC]
    is_volc = np.isin(U, volc_codes)
    hc = np.zeros(K.shape, int); hsplit = np.zeros(K.shape, "U5")
    for k, (v, s, b) in meta.items():
        m = K == k
        hc[m] = v; hsplit[m] = s
    in_test_block = np.isin(blk, list(test_blocks))
    print("1.6 km grid %d x %d; hand pixels %d (test %d); volcanic-unit pixels outside hand polygons %d"
          % (W, H, (hc > 0).sum(), (hsplit == "test").sum(), (is_volc & (hc == 0) & valid).sum()))
    # sample sets (class codes 1..4; 3 = lava tube or volcanic (map) depending on variant)
    hand_tr = valid & (hsplit == "train"); hand_te = valid & (hsplit == "test")
    volc_tr = valid & is_volc & (hc == 0) & ~in_test_block
    volc_te = valid & is_volc & (hc == 0) & in_test_block
    common_te = hand_te & np.isin(hc, [1, 2, 4])
    res = {"cell_m": cell, "variants": {}}

    def run(name, train_masks, classes):
        Xtr = np.concatenate([X[m] for m, _ in train_masks]); ytr = np.concatenate([np.full(m.sum(), c) if c else hc[m] for m, c in train_masks])
        keep = np.isin(ytr, classes)
        Xtr, ytr = Xtr[keep], ytr[keep]
        # fit() expects classes 0..3; map our codes onto that range
        order = sorted(classes)
        ymap = np.array([order.index(v) for v in ytr])
        models = []
        for i in range(len(order)):
            Z = Xtr[ymap == i].astype(np.float64)
            cov = np.cov(Z, rowvar=False) + np.eye(7) * 1e-3
            models.append((Z.mean(0), np.linalg.inv(cov), np.linalg.slogdet(cov)[1]))
        def pred(mask):
            return np.array(order)[predict(models, X[mask], COLS)]
        out = {}
        p = pred(common_te); t = hc[common_te]; ww = w[common_te]
        acc = float((ww * (p == t)).sum() / ww.sum())
        out["common_heldout_accuracy"] = acc
        out["common_per_class_producers"] = {str(c): float((ww * ((t == c) & (p == c))).sum() / max((ww * (t == c)).sum(), 1e-9)) for c in (1, 2, 4)}
        if 3 in classes:
            if name.startswith("B"):
                pv = pred(volc_te); wv = w[volc_te]
                out["volcanic_producers"] = float((wv * (pv == 3)).sum() / wv.sum())
                # user's: of held-out-block pixels called volcanic, how many are in volcanic units
                tb = valid & in_test_block
                pall = pred(tb)
                called = pall == 3
                out["volcanic_users"] = float((w[tb][called] * is_volc[tb][called]).sum() / max(w[tb][called].sum(), 1e-9))
                lt = hand_te & (hc == 3)
                pl = pred(lt)
                out["heldout_lava_tube_polygons_called"] = {str(c): float((w[lt] * (pl == c)).sum() / w[lt].sum()) for c in classes}
            else:
                lt = hand_te & (hc == 3); pl = pred(lt); wl = w[lt]
                out["lava_tube_producers"] = float((wl * (pl == 3)).sum() / wl.sum())
        res["variants"][name] = out
        print("  %-38s %s" % (name, json.dumps(out)))

    def run5(name, hmask, vmask):
        """The four hand-drawn classes kept as they are, plus class 5 = volcanic (map)."""
        Xtr = np.concatenate([X[hmask], X[vmask]])
        ytr = np.concatenate([hc[hmask], np.full(vmask.sum(), 5)])
        order = [1, 2, 3, 4, 5]
        models = []
        for c in order:
            Z = Xtr[ytr == c].astype(np.float64)
            cov = np.cov(Z, rowvar=False) + np.eye(7) * 1e-3
            models.append((Z.mean(0), np.linalg.inv(cov), np.linalg.slogdet(cov)[1]))
        pred = lambda m: np.array(order)[predict(models, X[m], COLS)]
        out = {}
        p = pred(common_te); t = hc[common_te]; ww = w[common_te]
        out["common_heldout_accuracy"] = float((ww * (p == t)).sum() / ww.sum())
        out["common_per_class_producers"] = {str(c): float((ww * ((t == c) & (p == c))).sum() / (ww * (t == c)).sum()) for c in (1, 2, 4)}
        lt = hand_te & (hc == 3); pl = pred(lt); wl = w[lt]
        out["lava_tube_producers"] = float((wl * (pl == 3)).sum() / wl.sum())
        pv = pred(volc_te); wv = w[volc_te]
        out["volcanic_producers"] = float((wv * (pv == 5)).sum() / wv.sum())
        tb = valid & in_test_block; pall = pred(tb); called = pall == 5
        out["volcanic_users"] = float((w[tb][called] * is_volc[tb][called]).sum() / max(w[tb][called].sum(), 1e-9))
        out["volcanic_area_share_in_test_blocks"] = float((w[tb] * is_volc[tb]).sum() / w[tb].sum())
        res["variants"][name] = out
        print("  %-38s %s" % (name, json.dumps(out)))

    run("A: four hand-drawn classes", [(hand_tr, 0)], [1, 2, 3, 4])
    run("B: lava tube -> volcanic (map)", [(hand_tr, 0), (volc_tr, 3)], [1, 2, 3, 4])
    run("C: three classes", [(hand_tr, 0)], [1, 2, 4])
    run5("D: four hand-drawn + volcanic (map) as a fifth", hand_tr, volc_tr)
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
