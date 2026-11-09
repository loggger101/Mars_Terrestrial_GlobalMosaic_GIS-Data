# -*- coding: utf-8 -*-
r"""Why hills and fluvial channel score low on the fresh blocks (KB §69.84, §69.85). Reads only.

The third label set makes its polygons three ways (Action in Landform_TrainingSamples_v3_proposals): "keep", a small
v2 polygon kept whole; "piece", a 0.5 degree piece of a large v2 polygon that passed its class's screen; "new", a
polygon placed by propose_v3_labels.py's rule (hills: 4 per 15 degree block on steep, high-relief cells; fluvial:
strips along the mapped valleys). For hills and fluvial channel this scores each kind apart, the published U-Net v3
on its own 1,652 held-out polygons and the fresh U-Net (make_v3_extras.py, run fresh) on the 895 fresh polygons,
with each kind's confusion row and the fresh blocks one by one.

  "<ArcGIS Pro Python>" check_v3_fresh_classes.py        -> logs\v3_fresh_classes.json

Written 2026-11-08 after the fresh scores were read, so a diagnosis, not a test.
"""
import os, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_v3_extras as X
import numpy as np
import arcpy
B, SEVEN = X.B, X.SEVEN
CLASSES = (1, 6)                                   # steep/windy hills, fluvial channel


def table(fcn, arrs, act):
    acts = [act.get(p, "?") for p, in arcpy.da.SearchCursor(fcn, ["ProposalOID"])]
    P = B.polys(fcn)
    assert len(acts) == len(P)
    R = B.rows(*arrs, P, len(SEVEN))
    out = {}
    for ci in CLASSES:
        kinds, blocks = collections.defaultdict(lambda: np.zeros(len(SEVEN))), collections.defaultdict(lambda: np.zeros(len(SEVEN)))
        nk, nb = collections.Counter(), collections.Counter()
        for (v, _, b), a, r in zip(P, acts, R):
            if v - 1 == ci:
                kinds[a] += r[ci]; nk[a] += 1; blocks[b] += r[ci]; nb[b] += 1
        row = lambda c, n: dict(polygons=n, pixels=int(c.sum()),
                                producers=round(float(c[ci] / c.sum()), 4) if c.sum() else None,
                                to={SEVEN[j]: round(float(c[j] / c.sum()), 4) for j in range(len(SEVEN)) if c.sum() and c[j]})
        out[SEVEN[ci]] = dict(all=row(sum(kinds.values()), sum(nk.values())),
                              by_kind={a: row(kinds[a], nk[a]) for a in sorted(kinds)},
                              by_block={b: row(blocks[b], nb[b]) for b in sorted(blocks)})
    return out


def main():
    act = {o: a for o, a in arcpy.da.SearchCursor(X.V3_PROP, ["OID@", "Action"])}
    a3 = np.load(os.path.join(X.HERE, X.ARR % "v3"), mmap_mode="r")
    g = B.grid(a3.shape)
    fr = X.window_array(os.path.join(X.WORK, "classified", "fresh"), a3.shape)
    res = dict(script="check_v3_fresh_classes.py",
               published_on_v3_test=table(X.V3_TEST, X.published(X.ARR % "v3"), act),
               fresh_on_fresh_test=table(X.fc("fresh", "test"), (fr, fr != 255, g), act))
    for k in ("published_on_v3_test", "fresh_on_fresh_test"):
        for c, t in res[k].items():
            print(k, c, "all", t["all"]["polygons"], t["all"]["producers"])
            for a, s in t["by_kind"].items():
                print("   ", a, s["polygons"], s["producers"], s["to"])
    p = os.path.join(HERE, "logs", "v3_fresh_classes.json")
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", p)


if __name__ == "__main__":
    main()
