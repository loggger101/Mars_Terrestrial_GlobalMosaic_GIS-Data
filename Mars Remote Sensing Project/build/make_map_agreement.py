# -*- coding: utf-8 -*-
r"""A6: where the SVM and U-Net maps agree, per class, over ±60° (NEXT-STEPS §12.2 A6).

Each pair is scored on held-out polygons alone (KB §57, §66.8, §69.24, §69.25); this asks where the two methods
disagree on the whole ±60° extent. Read from the cached 400 m class arrays verify_global60_classification.py wrote
(refuses one older than its raster), cos-latitude weighted, on pixels valid in both maps:
  four    the published SVM map (200 m, 11 x 11 mode) against the two-pass U-Net
  v2      the seven-class SVM (200 m, 11 x 11 mode) against the seven-class U-Net
Per pair: the share of ±60° where they agree; the cross-table of classes (area shares); per class, the area where
both call it, where only one does, and its agreement as intersection over union; the agreement on the held-out and on
the training polygons (svmcheck.training_score on an agree/disagree array: the same pixels the scorer reads); by
10° latitude band. Writes a 3.2 km array of the agreed class (255 where they disagree, 254 outside the extent) for
make_fig_map_agreement.py.

Predictions, written before the first run:
  P1  four classes: the two maps agree on less than 75 % of ±60°.
  P2  seven classes: they agree on less than 50 %, and the largest off-diagonal cell is the U-Net's edifice where
      the SVM gives another class (edifice is 40.0 % of the U-Net map and 12.2 % of the SVM's, KB §69.39).
  P3  for both pairs, agreement on the held-out polygons is higher than on ±60° as a whole (hand-drawn polygons sit
      where a class is clear: NEXT-STEPS §12.3 R2's premise).
Each is reported as held or not held; none is adjusted after the run.

  "<ArcGIS Pro Python>" make_map_agreement.py   -> logs\map_agreement.json, map_agreement_<pair>_3200m.npy; read-only
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from svmcheck import training_score
from labelsets import FOUR, SEVEN

MARS = arcpy.SpatialReference(104905)
G60 = r"Mars Project\Global60\%s.tif"
OUT = os.path.join(HERE, "logs", "map_agreement.json")
STEP = 8                                                    # 400 m -> 3.2 km for the figure
PAIRS = [("four", FOUR, ("global60_landforms_200m_mode11_on_v2_labels_ov400.npy", "global60_landforms_svm_200m_mode11"),
          ("global60_landforms_global60_landforms_unet_200m_seamfix_ov400.npy", "global60_landforms_unet_200m_seamfix"),
          "Landform_TrainingSamples_terrain_60_train", "Landform_TrainingSamples_terrain_60_test"),
         ("v2", SEVEN, ("global60_landforms_v2_200m_mode11_ov400.npy", "global60_landforms_svm_v2_200m_mode11"),
          ("global60_landforms_global60_landforms_unet_v2_200m_seamfix_ov400.npy", "global60_landforms_unet_v2_200m_seamfix"),
          "Landform_TrainingSamples_v2_60_train", "Landform_TrainingSamples_v2_60_test")]


def load(npy, tif):
    p = os.path.join(HERE, npy)
    if os.path.getmtime(p) < os.path.getmtime(on_drive(G60 % tif)):
        sys.exit("%s is older than %s.tif: rerun verify_global60_classification.py on it first" % (npy, tif))
    return np.load(p, mmap_mode="r")


def polys(fc):
    out = []
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue"], spatial_reference=MARS) as c:
        for g, v in c:
            out.append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g]))
    return out


def main():
    t0 = time.time()
    res = dict(script="make_map_agreement.py", when=time.strftime("%Y-%m-%d %H:%M"))
    for key, names, (na, ta), (nb, tb), train, test in PAIRS:
        a, b = load(na, ta), load(nb, tb)
        assert a.shape == b.shape
        H, W = a.shape; K = len(names)
        g = dict(dpx=360.0 / W, dpy=2 * G.G100.lat_of(G.G100.oy) / H,
                 lat_top=G.G100.lat_of(G.G100.oy), lon_left=G.G100.lon_of(G.G100.ox))
        lat = g["lat_top"] - (np.arange(H) + .5) * g["dpy"]
        w = np.cos(np.radians(lat))
        tab = np.zeros((K, K)); band = np.zeros((12, 2))
        agree = np.zeros((H, W), np.uint8)                     # 0 disagree, 1 agree; the scorer's class index
        small = np.full(((H + STEP - 1) // STEP, (W + STEP - 1) // STEP), 254, np.uint8)
        for r0 in range(0, H, 512):
            r1 = min(r0 + 512, H)
            x, y = np.asarray(a[r0:r1]), np.asarray(b[r0:r1])
            ok = (x != 255) & (y != 255)
            ww = np.broadcast_to(w[r0:r1, None], x.shape)[ok]
            tab += np.bincount(x[ok].astype(np.int64) * K + y[ok], ww, K * K).reshape(K, K)
            same = ok & (x == y)
            agree[r0:r1] = same
            bi = np.clip(((60 - lat[r0:r1]) // 10).astype(int), 0, 11)
            for j in np.unique(bi):
                s = bi == j
                band[j] += [(same[s] * w[r0:r1][s, None]).sum(), (ok[s] * w[r0:r1][s, None]).sum()]
            sub = slice(r0 + (-r0) % STEP, r1, STEP)
            xs, ys, oks = np.asarray(a[sub, ::STEP]), np.asarray(b[sub, ::STEP]), None
            oks = (xs != 255) & (ys != 255)
            small[(sub.start // STEP):(sub.start // STEP) + xs.shape[0]] = np.where(oks, np.where(xs == ys, xs, 255), 254)
        tot = tab.sum()
        m = (a != 255) & (b != 255)
        on = {}
        for side, fc in (("held_out", test), ("training", train)):
            cm, _ = training_score(agree, m, g, polys(fc), max(K, 2))
            on[side] = round(float(cm[:, 1].sum() / cm.sum()), 4)
        per = {}
        for i, n in enumerate(names):
            both, sa, sb = tab[i, i], tab[i].sum(), tab[:, i].sum()
            per[n] = dict(svm_share=round(sa / tot, 4), unet_share=round(sb / tot, 4), both_share=round(both / tot, 4),
                          iou=round(both / (sa + sb - both), 4) if sa + sb > both else None)
        off = tab.copy(); np.fill_diagonal(off, 0)
        i, j = np.unravel_index(off.argmax(), off.shape)
        res[key] = dict(svm=ta, unet=tb, grid_400m=g, figure_step=STEP, agreement=round(float(np.trace(tab) / tot), 4), on_polygons=on,
                        crosstab_rows_svm_cols_unet=(tab / tot).round(5).tolist(), classes=per,
                        largest_disagreement=dict(svm=names[i], unet=names[j], share=round(float(off[i, j] / tot), 4)),
                        by_latitude_band={"%d to %d" % (60 - 10 * k, 50 - 10 * k): round(float(band[k, 0] / band[k, 1]), 4)
                                          for k in range(12) if band[k, 1]})
        np.save(os.path.join(HERE, "map_agreement_%s_3200m.npy" % key), small)
        print("%s: agree on %.1f %% of ±60°; held-out polygons %.1f %%, training %.1f %%; largest disagreement: "
              "SVM %s / U-Net %s, %.1f %% (%.0f s)" % (key, 100 * res[key]["agreement"], 100 * on["held_out"],
              100 * on["training"], names[i], names[j], 100 * off[i, j] / tot, time.time() - t0))
        for n, d in per.items():
            print("   %-18s SVM %5.1f %%  U-Net %5.1f %%  both %5.1f %%  IoU %s" % (n, 100 * d["svm_share"],
                  100 * d["unet_share"], 100 * d["both_share"], d["iou"]))
        print("   by latitude:", res[key]["by_latitude_band"])
        del a, b, agree, m
    f, v = res["four"], res["v2"]
    res["predictions"] = {
        "P1": dict(agreement=f["agreement"], held=bool(f["agreement"] < 0.75)),
        "P2": dict(agreement=v["agreement"], largest=v["largest_disagreement"],
                   held=bool(v["agreement"] < 0.50 and v["largest_disagreement"]["unet"] == "volcanic edifice")),
        "P3": dict(four=[f["on_polygons"]["held_out"], f["agreement"]], v2=[v["on_polygons"]["held_out"], v["agreement"]],
                   held=bool(f["on_polygons"]["held_out"] > f["agreement"] and v["on_polygons"]["held_out"] > v["agreement"]))}
    for p, d in res["predictions"].items():
        print(p, "held" if d["held"] else "NOT held", {k: x for k, x in d.items() if k != "held"})
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s  (%.0f s)" % (OUT, time.time() - t0))


if __name__ == "__main__":
    main()
