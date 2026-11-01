# -*- coding: utf-8 -*-
r"""The held-out split as data, for the paper's block-split figure (NEXT-STEPS §12.4 W4; KB §31.3, §69.41).

Reads the two label sets' training and held-out halves (Landform_TrainingSamples_terrain_60_train / _test, the four
classes of KB §31.3; Landform_TrainingSamples_v2_60_train / _test, the seven of §69.8) and writes, for each polygon,
its block (the `Block` field make_global60_classification.py and apply_label_review.py wrote: floor(lon / 15)_floor(
lat / 15) in GCS_Mars_2000, longitude -180..180), its half, its class code, its label point in degrees east 0-360
and its area on the sphere in km². Then per set: the blocks with training polygons, the held-out blocks, any block
on both sides, and the polygons and area per class on each side. Descriptive: no test, so no prediction.

  "<ArcGIS Pro Python>" make_block_split.py      -> logs\block_split.json; reads the gdb only (Pro may be open)
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
from labelsets import FOUR, SEVEN

OUT = os.path.join(HERE, "logs", "block_split.json")
MARS = arcpy.SpatialReference(104905)                     # GCS_Mars_2000, as the split was made
SETS = [("four", FOUR, "Landform_TrainingSamples_terrain_60_train", "Landform_TrainingSamples_terrain_60_test"),
        ("v2", SEVEN, "Landform_TrainingSamples_v2_60_train", "Landform_TrainingSamples_v2_60_test")]


def rows(fc):
    out = []
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["OID@", "SHAPE@", "Block", "Split", "Classvalue"],
                               spatial_reference=MARS) as c:
        for oid, shp, block, split, v in c:
            p = shp.labelPoint                            # inside the polygon, unlike a centroid
            out.append(dict(oid=oid, block=block, split=split, cls=int(v), lon_e=round(p.X % 360.0, 4),
                            lat=round(p.Y, 4), km2=round(shp.getArea("GEODESIC", "SQUAREKILOMETERS"), 2)))
    return out


def main():
    res = {}
    for name, names, train, test in SETS:
        a, b = rows(train), rows(test)
        assert all(r["split"] == "train" for r in a) and all(r["split"] == "test" for r in b), name
        tr, te = sorted({r["block"] for r in a}), sorted({r["block"] for r in b})
        per = {}
        for k, cls in enumerate(names, 1):
            per[cls] = dict(train=sum(r["cls"] == k for r in a), test=sum(r["cls"] == k for r in b),
                            train_km2=round(sum(r["km2"] for r in a if r["cls"] == k)),
                            test_km2=round(sum(r["km2"] for r in b if r["cls"] == k)))
        res[name] = dict(train_fc=train, test_fc=test, n_train=len(a), n_test=len(b), train_blocks=tr,
                         test_blocks=te, both=sorted(set(tr) & set(te)), n_blocks=len(set(tr) | set(te)),
                         per_class=per, polygons=a + b)
        print("%-4s %d train in %d blocks, %d held out in %d blocks; %d blocks in all; on both sides: %s"
              % (name, len(a), len(tr), len(b), len(te), len(set(tr) | set(te)), res[name]["both"] or "none"))
        for cls, d in per.items():
            print("     %-18s train %4d (%9s km²)   held out %4d (%9s km²)"
                  % (cls, d["train"], f"{d['train_km2']:,}", d["test"], f"{d['test_km2']:,}"))
    res["same_held_out_blocks"] = res["four"]["test_blocks"] == res["v2"]["test_blocks"]
    print("the two sets hold out the same blocks:", res["same_held_out_blocks"])
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
