# -*- coding: utf-8 -*-
r"""Which held-out polygons carry the difference between a window run and base (make_v3_extras.py).

Accuracy here is pixel accuracy, so large polygons weigh most. For one run (noth, cut, add or rep) against base this
scores every held-out polygon of both sets on both window maps and lists the polygons whose correct-pixel count moves
most, with class, block, size, both maps' share correct and what the run reads instead; the net change by class and block; and the share of the run's
total change in correct pixels that its 10 largest movers carry.

Written 2026-11-09 after noth's scores were read (§69.86: its drop sits on blocks -5_-1 and -9_-1): a description, not a
test. Reads only; writes logs\v3_<run>_polygons.json.

  "<ArcGIS Pro Python>" check_v3_run_polygons.py --run noth
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN = sys.argv[sys.argv.index("--run") + 1] if "--run" in sys.argv else "noth"
import make_v3_extras as X
import numpy as np
B, SEVEN = X.B, X.SEVEN
assert RUN in ("noth", "cut", "add", "rep"), RUN


def main():
    a3 = np.load(os.path.join(X.HERE, X.ARR % "v3"), mmap_mode="r")
    g = B.grid(a3.shape)
    maps = {k: X.window_array(os.path.join(X.WORK, "classified", k), a3.shape) for k in ("base", RUN)}
    res = dict(script="check_v3_run_polygons.py", run=RUN)
    for name, fcn in (("v2_polygons", X.V2_TEST), ("v3_polygons", X.V3_TEST)):
        P = B.polys(fcn)
        R = {k: B.rows(a, a != 255, g, P, len(SEVEN)) for k, a in maps.items()}
        rows = []
        for i, (v, _, blk) in enumerate(P):
            rb, rr = R["base"][i][v - 1], R[RUN][i][v - 1]
            n = rb.sum()
            if not n:
                continue
            reads = {SEVEN[j]: round(float(rr[j] / n), 3) for j in np.argsort(-rr)[:2] if rr[j] and j != v - 1}
            rows.append(dict(cls=SEVEN[v - 1], block=blk, pixels=int(n), base=round(float(rb[v - 1] / n), 3),
                             run=round(float(rr[v - 1] / n), 3), moved=int(rr[v - 1] - rb[v - 1]), run_reads=reads))
        tot_px = sum(r["pixels"] for r in rows)
        net = sum(r["moved"] for r in rows)
        cb = {}
        for r in rows:
            cb[(r["cls"], r["block"])] = cb.get((r["cls"], r["block"]), 0) + r["moved"]
        by_cb = sorted(((round(100 * m / tot_px, 2), c, b) for (c, b), m in cb.items() if m), key=lambda t: t[0])
        rows.sort(key=lambda r: -abs(r["moved"]))
        top = rows[:10]
        res[name] = dict(polygons=len(rows), pixels=tot_px, net_moved=net, net_points=round(100 * net / tot_px, 2),
                         top10_net=sum(r["moved"] for r in top), top10_points=round(100 * sum(r["moved"] for r in top) / tot_px, 2),
                         largest_polygon_share=round(max(r["pixels"] for r in rows) / tot_px, 4), top=rows[:25],
                         by_class_block=[dict(points=p, cls=c, block=b) for p, c, b in by_cb])
        print(name, {k: res[name][k] for k in ("polygons", "net_points", "top10_points", "largest_polygon_share")})
        print("   class x block, points of the set's pixels, most lost first:", [(p, c, b) for p, c, b in by_cb[:6]],
              "most gained:", [(p, c, b) for p, c, b in by_cb[-3:]])
        for r in top:
            print("   %-18s %-7s %7d px  base %.3f  %s %.3f  reads %s" % (r["cls"], r["block"], r["pixels"], r["base"], RUN, r["run"], r["run_reads"]))
    p = os.path.join(HERE, "logs", "v3_%s_polygons.json" % RUN)
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", p)


if __name__ == "__main__":
    main()
