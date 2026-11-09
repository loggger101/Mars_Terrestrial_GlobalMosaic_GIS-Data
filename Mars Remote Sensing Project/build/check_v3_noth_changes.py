# -*- coding: utf-8 -*-
r"""Where the U-Net without thermal (make_v3_extras.py, run noth) maps differently from the same model with it (base).

KB §69.86: noth scores 6.4 and 7.6 points below base on the held-out polygons, a drop not resolved by block. The
polygons sample a small part of each window, so this reads the whole of both window maps (the 14 held-out blocks with
their 25 km margins, on the published 400 m lattice), area-weighted by cos(latitude):
  - how much of the ground changes class, and the base -> noth transition matrix;
  - the same on SIM 3292's volcanic unit groups (v, ve, vf) and off them (make_geomap_check.unit_raster);
  - by 15 degree block.

Written 2026-11-09 after the noth scores were read: a description of the two maps, not a test. A thermal effect would be
expected to sit on material contrasts, such as lava plains and aprons, more than on relief; a difference from one
training to another has no such reason to sit anywhere. Reads only; writes logs\v3_noth_changes.json.

  "<ArcGIS Pro Python>" check_v3_noth_changes.py
"""
import os, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv += ["--labels", "v3"]
import make_v3_extras as X
import numpy as np
B, SEVEN = X.B, X.SEVEN
K = len(SEVEN)
VOLCANIC = ("v", "ve", "vf")


def main():
    import make_geomap_check as M
    a3 = np.load(os.path.join(X.HERE, X.ARR % "v3"), mmap_mode="r")
    shape = a3.shape
    g = B.grid(shape)
    base = X.window_array(os.path.join(X.WORK, "classified", "base"), shape)
    noth = X.window_array(os.path.join(X.WORK, "classified", "noth"), shape)
    units, names = M.unit_raster()
    volc = np.array([names.get(k) in VOLCANIC for k in range(256)])
    H, W = shape
    lat = g["lat_top"] - (np.arange(H) + 0.5) * g["dpy"]
    lon = g["lon_left"] + (np.arange(W) + 0.5) * g["dpx"]
    lon = (lon + 180.0) % 360.0 - 180.0
    ur = np.clip(((60.0 - lat) / M.STEP).astype(int), 0, units.shape[0] - 1)
    uc = np.clip(((lon + 180.0) / M.STEP).astype(int), 0, units.shape[1] - 1)
    bx = np.floor(lon / 15.0).astype(int)
    T = {"all": np.zeros((K, K)), "volcanic": np.zeros((K, K)), "other": np.zeros((K, K)), "no_unit": np.zeros((K, K))}
    blk = collections.defaultdict(lambda: np.zeros((K, K)))
    for r in range(H):
        b, n = base[r], noth[r]
        ok = (b != 255) & (n != 255)
        if not ok.any():
            continue
        w = np.cos(np.radians(lat[r]))
        cols = np.nonzero(ok)[0]
        idx = b[cols].astype(np.int64) * K + n[cols]
        u = units[ur[r], uc[cols]]
        v = volc[u]
        T["all"] += w * np.bincount(idx, minlength=K * K).reshape(K, K)
        T["volcanic"] += w * np.bincount(idx[v], minlength=K * K).reshape(K, K)
        T["other"] += w * np.bincount(idx[~v & (u > 0)], minlength=K * K).reshape(K, K)
        T["no_unit"] += w * np.bincount(idx[u == 0], minlength=K * K).reshape(K, K)
        by = int(np.floor(lat[r] / 15.0))
        for x in np.unique(bx[cols]):
            m = bx[cols] == x
            blk["%d_%d" % (x, by)] += w * np.bincount(idx[m], minlength=K * K).reshape(K, K)

    def summary(t):
        tot = t.sum()
        if not tot:
            return None
        off = t.copy(); np.fill_diagonal(off, 0)
        top = sorted(((off[i, j] / tot, SEVEN[i], SEVEN[j]) for i in range(K) for j in range(K) if off[i, j]), reverse=True)[:6]
        return dict(area_share_of_windows=None, changed=round(float(off.sum() / tot), 4),
                    base_area={SEVEN[i]: round(float(t[i].sum() / tot), 4) for i in range(K)},
                    noth_area={SEVEN[j]: round(float(t[:, j].sum() / tot), 4) for j in range(K)},
                    top_changes=[dict(base=a, noth=b2, share=round(float(s), 4)) for s, a, b2 in top])

    grand = T["all"].sum()
    res = dict(script="check_v3_noth_changes.py", lattice=list(shape))
    for k, t in T.items():
        res[k] = summary(t)
        if res[k]:
            res[k]["area_share_of_windows"] = round(float(t.sum() / grand), 4)
    res["by_block"] = {b: dict(share_of_windows=round(float(t.sum() / grand), 4), changed=round(float((t.sum() - np.trace(t)) / t.sum()), 4))
                       for b, t in sorted(blk.items()) if t.sum() / grand >= 0.005}
    for k in T:
        if res[k]:
            print(k, "share", res[k]["area_share_of_windows"], "changed", res[k]["changed"])
            for c in res[k]["top_changes"]:
                print("    %-18s -> %-18s %.4f" % (c["base"], c["noth"], c["share"]))
    print("by block:", {b: v["changed"] for b, v in res["by_block"].items()})
    p = os.path.join(HERE, "logs", "v3_noth_changes.json")
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", p)


if __name__ == "__main__":
    main()
