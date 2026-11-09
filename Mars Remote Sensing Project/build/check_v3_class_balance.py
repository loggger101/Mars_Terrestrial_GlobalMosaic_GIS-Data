# -*- coding: utf-8 -*-
r"""Class areas of each v3 training set and the weights class balancing would give them (KB §69.88, §69.90).

Every v3 U-Net trained on the added polygons (base, fresh, noth) had its validation loss rise far late in training; cut,
without them, did not (§69.88). The training runs with class_balancing True, which weights each class by the inverse of
its pixel share, so a class with a small share carries a large weight. This lists, for each run's training polygons:
per class the polygon count, area (km2, geodesic on the Mars sphere) and share, and the inverse-share weight scaled to
the largest class = 1; and, from the chip folders that still exist (v3's on C:, add's on D:), the chips per class.

Written 2026-11-09 while add_train runs, after cut was scored and S1 registered: a description, not a test. Reads only;
writes logs\v3_class_balance.json.

  "<ArcGIS Pro Python>" check_v3_class_balance.py
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_v3_extras as X
import arcpy
B, SEVEN = X.B, X.SEVEN
CHIPS = {"base": r"C:\MarsScratch\x5c_v3\export_tiles", "add": X.EXPORT}


def areas(fcn):
    n, a = [0] * 7, [0.0] * 7
    with arcpy.da.SearchCursor(fcn, ["SHAPE@", "Classvalue"]) as c:
        for g, v in c:
            n[v - 1] += 1
            a[v - 1] += g.getArea("GEODESIC", "SQUAREKILOMETERS")
    tot = sum(a)
    share = [x / tot for x in a]
    top = max(share)
    return dict(polygons=dict(zip(SEVEN, n)), area_km2=dict(zip(SEVEN, [round(x) for x in a])),
                share=dict(zip(SEVEN, [round(s, 4) for s in share])),
                weight_vs_largest=dict(zip(SEVEN, [round(top / s, 1) if s else None for s in share])))


def chips(folder):
    p = os.path.join(folder, "esri_accumulated_stats.json")
    if not os.path.exists(p):
        return None
    made = open(os.path.join(folder, "MADE_BY_make_global60_dl_export.txt"), encoding="utf-8").read()
    fs = json.load(open(p, encoding="utf-8"))["FeatureStats"]
    return dict(labels=[l for l in made.splitlines() if l.startswith("labels")][0],
                chips_per_class=dict(zip(SEVEN, fs["NumImagesPerClass"])), chips=fs["NumImagesTotal"],
                features_per_class=dict(zip(SEVEN, fs["NumFeaturesPerClass"])))


def main():
    runs = {"v2 (unet_v2)": X.V2_TRAIN, "base / noth (v3)": X.V3_TRAIN, "fresh": X.fc("fresh", "train"),
            "cut": X.fc("cut", "train"), "add": X.fc("add", "train")}
    res = dict(script="check_v3_class_balance.py", runs={}, chips={})
    for k, f in runs.items():
        res["runs"][k] = areas(f)
        r = res["runs"][k]
        print("%-18s" % k, " | ".join("%s %d, %.1f%%, w %s" % (c[:6], r["polygons"][c], 100 * r["share"][c], r["weight_vs_largest"][c])
                                    for c in SEVEN), flush=True)
    for k, f in CHIPS.items():
        res["chips"][k] = chips(f)
        print(k, res["chips"][k], flush=True)
    p = os.path.join(HERE, "logs", "v3_class_balance.json")
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", p)


if __name__ == "__main__":
    main()
