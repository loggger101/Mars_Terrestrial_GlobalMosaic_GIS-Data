# -*- coding: utf-8 -*-
r"""How much of each held-out set lies under the v3 training polygons (KB §69.80).

The split assigns whole polygons to blocks, so a polygon can cross into the next block; the 512 hand-drawn labels had one
such leak (labels 290 and 291, KB §45). v3 has 14 times the training polygons, and U-Net v3 scored above its registered
range (§69.80), so the same question is asked of it: Landform_TrainingSamples_v3_60_train against the v2 and v3 held-out
polygons, area weighted by cos latitude.

The check can fail: Landform_TrainingSamples_v2_60_train is run the same way and must be mostly covered, v3's training
polygons being cut from it (§69.49), or the script stops with exit 2 and writes nothing.

  "<ArcGIS Pro Python>" check_held_out_overlap.py
Writes logs\held_out_overlap_v3.json. Reads the gdb only (Pro may be open); ~1 min.
"""
import os, sys, json, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy
from shapely import wkb
from shapely.ops import unary_union
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
from labelsets import SEVEN

TRAIN = "v3_60_train"
SETS = ("v2_60_test", "v3_60_test", "v2_60_train")
CONTROL_MIN = 0.5                                 # share of v2_60_train the v3 training polygons must cover


def load(name):
    """(OID, class code, geometry), and the OIDs of any polygon too degenerate to read as a shape."""
    out, bad = [], []
    with arcpy.da.SearchCursor(os.path.join(GDB, "Landform_TrainingSamples_%s" % name),
                               ["OID@", "Classvalue", "SHAPE@WKB"]) as c:
        for oid, v, b in c:
            try:
                g = wkb.loads(bytes(b))
            except Exception:
                bad.append(oid)
                continue
            out.append((oid, int(v), g if g.is_valid else g.buffer(0)))
    return out, bad


def area(g):
    return g.area * math.cos(math.radians(g.centroid.y))


def main():
    train, _ = load(TRAIN)
    geoms = [g for _, _, g in train]
    tree = STRtree(geoms)
    res = dict(script="check_held_out_overlap.py", training=TRAIN, polygons=len(train), sets={})
    for name in SETS:
        test, bad = load(name)
        total, cover, touching = 0.0, 0.0, 0
        by_total, by_cover = {}, {}
        for _, v, g in test:
            a = area(g)
            total += a
            by_total[v] = by_total.get(v, 0.0) + a
            near = [geoms[i] for i in tree.query(g) if geoms[i].intersects(g)]
            if near:
                c = area(g.intersection(unary_union(near)))
                touching += 1
                cover += c
                by_cover[v] = by_cover.get(v, 0.0) + c
        res["sets"][name] = dict(polygons=len(test), unreadable=bad, touching=touching, share_covered=cover / total,
                                 by_class={SEVEN[v - 1]: by_cover.get(v, 0.0) / by_total[v] for v in sorted(by_total)})
        print("%-12s %5d polygons, %d touching, %.4f %% of the area covered%s" % (
            name, len(test), touching, 100 * cover / total, "; unreadable OID %s" % bad if bad else ""))
    if res["sets"]["v2_60_train"]["share_covered"] < CONTROL_MIN:
        sys.exit("the control covers under %.0f %%: the check is not measuring overlap" % (100 * CONTROL_MIN))
    p = os.path.join(HERE, "logs", "held_out_overlap_v3.json")
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote", p)


if __name__ == "__main__":
    main()
