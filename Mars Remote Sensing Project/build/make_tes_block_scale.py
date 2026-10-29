# -*- coding: utf-8 -*-
r"""Test T3 at finer blocks: does the thermal signal against calibrated inertia grow as the block shrinks? (KB §43.1)

§43.1 measured each ±60° layer against log TES thermal inertia within 15° x 15° blocks (~782,000 km²,
§69.15) only. A block that size spans several dust and bedrock provinces, and the THEMIS mosaics are
stretched region by region (§28.10), so a local signal may be diluted. This repeats the test with the
same inputs (the 1.6 km overview averaged into TES's 0.05° cells, measured TES cells only) at blocks of
15, 10, 5, 2, 1 and 0.5 degrees, aligned to multiples of the block size as in §31.3.

Per block size and layer:
  * median and interquartile range of the per-block r (as §43.1);
  * the share of blocks whose r has the physical sign (negative for Viking red and the index,
    positive for night IR: §42.4);
  * the pooled within-block r: r of the block-demeaned layer against block-demeaned log inertia over
    every cell, one number free of the small-block noise that spreads the median;
  * the same two figures for a null, the layer shifted 180° in longitude (the §4 misregistration):
    what block size alone produces from latitude trends and noise;
  * the median within-block standard deviation of log inertia, since a small block also narrows the
    range a correlation can use.

Also THEMIS day against night DN within blocks (the Ius r = 0.098 of §24.1), every ±60° cell valid in both.

The 5° nightside r of night IR, the index and Viking red is also written as rasters on the ±60° frame (one 5°
cell per block, Mars_Equidistant_Cylindrical_CM180; blocks below the cell minimum are NoData):
Global60\global60_tes_r5deg_{nightIR,index,viking}.tif, for layout 18 (make_tes_block_layout.py), with the
5° blocks over the two type areas in the log. Registration is checked, not assumed: Viking's 5° block means from
the TES cells, placed on the frame, must match the same means read straight off the frame's own overview (r > 0.99),
and the same grid shifted 180° must not.

Blocks need at least the §43.1 share of measured cells (2,000 of 90,000) and never fewer than 30 cells,
so the 15° row repeats §43.1. Prediction, written before the run: the index and night IR stronger within
5° blocks than within 15°, |r| perhaps 0.15-0.2; Viking weaker still within small blocks (its signal is
regional); day IR near zero at every size. Read-only; writes build\logs\tes_block_scale.json.
"""
import os, sys, json
import numpy as np
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
from make_tes_global_check import TES, STACK, INDEX, STEP, TARGET_M, overview, to_tes_cells

gdal.UseExceptions()
OUT = os.path.join(HERE, "logs", "tes_block_scale.json")
SIZES = (15.0, 10.0, 5.0, 2.0, 1.0, 0.5)
R0, R1 = 600, 3000                # TES rows inside ±60°
NR, NC = R1 - R0, 7200
MIN_SHARE, MIN_CELLS = 2000.0 / 90000.0, 30
MAP_SIZE, MAP_SIDE = 5.0, "nightside"
MAPS = {"THEMIS night DN": "nightIR", "diurnal-contrast index": "index", "Viking red": "viking"}
CELL_B = G.R_MARS * np.radians(MAP_SIZE)
X0, Y0 = -np.pi * G.R_MARS, G.R_MARS * np.radians(60.0)
MAP_W, MAP_H = int(round(360 / MAP_SIZE)), int(round(120 / MAP_SIZE))
AREAS = {"Ius Chasma": ((271, 286), (-13, -6)), "Athabasca Valles": ((150, 162), (4, 14))}   # areas.py, °E
SIGN = {"Viking red": -1, "THEMIS night DN": +1, "THEMIS day DN": +1, "diurnal-contrast index": -1, "slope": 0}


def cell_means(arr, cell, g, nodata):
    s, n = to_tes_cells(arr, cell, g.ox, g.oy, nodata)
    m = np.where(n > 0, s / np.maximum(n, 1), np.nan).reshape(3600, 7200)[R0:R1]
    return m.astype(np.float32)


def block_ids(size):
    k = int(round(size / STEP))
    rows = np.arange(R0, R1) // k
    cols = np.arange(NC) // k
    return (rows[:, None] * (NC // k + 1) + cols[None, :]).ravel(), k * k


def block_stats(x, y, b, ncell):
    """Per-block r, pooled within-block r and per-block sd of y, from sums by block."""
    x = x - x.mean(); y = y - y.mean()
    nb = b.max() + 1
    S = lambda w: np.bincount(b, weights=w, minlength=nb)
    n, sx, sy = S(np.ones_like(x)), S(x), S(y)
    sxx, syy, sxy = S(x * x), S(y * y), S(x * y)
    with np.errstate(invalid="ignore", divide="ignore"):
        cxx = sxx - sx * sx / n; cyy = syy - sy * sy / n; cxy = sxy - sx * sy / n
        r = cxy / np.sqrt(cxx * cyy)
        sdy = np.sqrt(cyy / n)
    keep = (n >= max(MIN_CELLS, MIN_SHARE * ncell)) & (cxx > 0) & (cyy > 0)
    pooled = float(cxy[keep].sum() / np.sqrt(cxx[keep].sum() * cyy[keep].sum()))
    return r[keep], pooled, sdy[keep], int(n[keep].sum()), np.nonzero(keep)[0], n[keep]


def to_frame(ids, vals):
    """Per-block values (5° block ids, columns from 180°W) onto the frame's 5° lattice (columns from 0°E)."""
    k = int(round(MAP_SIZE / STEP))
    g = np.full((MAP_H, MAP_W), np.nan, np.float32)
    g[ids // (NC // k + 1) - R0 // k, ids % (NC // k + 1)] = vals
    return np.roll(g, -MAP_W // 2, axis=1)


def frame_block_means(arr, cell, g, nodata):
    """Mean of arr per 5° block, binned straight from its own pixel centres on the frame."""
    H, W = arr.shape
    c = np.floor((g.ox + (np.arange(W) + .5) * cell - X0) / CELL_B).astype(int)
    r = np.floor((Y0 - (g.oy - (np.arange(H) + .5) * cell)) / CELL_B).astype(int)
    ok = (r >= 0) & (r < MAP_H)
    idx = (r[ok][:, None] * MAP_W + c[None, :].clip(0, MAP_W - 1)).ravel()
    a = arr[ok]; v = ((a != nodata) & np.isfinite(a)).ravel()
    s = np.bincount(idx, weights=np.where(v, a.ravel(), 0), minlength=MAP_H * MAP_W)
    n = np.bincount(idx, weights=v.astype(float), minlength=MAP_H * MAP_W)
    return np.where(n > 0, s / np.maximum(n, 1), np.nan).reshape(MAP_H, MAP_W)


def write_map(grid, path, wkt):
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(path, MAP_W, MAP_H, 1, gdal.GDT_Float32)
    ds.SetGeoTransform((X0, CELL_B, 0.0, Y0, 0.0, -CELL_B)); ds.SetProjection(wkt)
    b = ds.GetRasterBand(1); b.SetNoDataValue(-9.0)
    b.WriteArray(np.where(np.isfinite(grid), grid, -9.0).astype(np.float32)); b.ComputeStatistics(False)
    ds = None


def area_blocks(grids, ncells):
    """The 5° blocks that overlap each type area's window, with each mapped layer's r."""
    out = {}
    for a, ((l0, l1), (b0, b1)) in AREAS.items():
        rows = []
        for j in range(int(l0 // MAP_SIZE), int(np.ceil(l1 / MAP_SIZE))):
            for i in range(int((60 - b1) // MAP_SIZE), int(np.ceil((60 - b0) / MAP_SIZE))):
                d = {"lon_e": [j * MAP_SIZE, (j + 1) * MAP_SIZE], "lat": [60 - (i + 1) * MAP_SIZE, 60 - i * MAP_SIZE],
                     "cells": None if np.isnan(ncells[i, j]) else int(ncells[i, j])}
                for name, g in grids.items():
                    d[name] = None if np.isnan(g[i, j]) else float(g[i, j])
                rows.append(d)
        out[a] = rows
    return out


def summarise(r, pooled, sign):
    d = {"median": float(np.median(r)), "p25_p75": [float(np.percentile(r, 25)), float(np.percentile(r, 75))],
         "pooled": pooled, "blocks": int(r.size)}
    if sign:
        d["share_physical_sign"] = float(np.mean(np.sign(r) == sign))
    return d


def main():
    layers = {}
    ds = gdal.Open(STACK)
    for b, name in ((1, "Viking red"), (4, "THEMIS night DN"), (5, "THEMIS day DN"), (6, "slope")):
        o, cell = overview(ds.GetRasterBand(b), G.G200.res, TARGET_M)
        arr = o.ReadAsArray().astype(float)
        layers[name] = cell_means(arr, cell, G.G200, 0)
        if b == 1:
            direct = frame_block_means(arr, cell, G.G200, 0)
        del arr
        print("  %-22s read at %.0f m  %d x %d" % (name, cell, o.XSize, o.YSize), flush=True)
    di = gdal.Open(INDEX)             # held: a band outlives a temporary dataset only as a dangling handle
    o, cell = overview(di.GetRasterBand(1), G.G100.res, TARGET_M)
    layers["diurnal-contrast index"] = cell_means(o.ReadAsArray().astype(float), cell, G.G100, -32768)
    print("  %-22s read at %.0f m  %d x %d" % ("diurnal-contrast index", cell, o.XSize, o.YSize), flush=True)

    bid5, _ = block_ids(MAP_SIZE)                  # registration: Viking's block means two ways must agree
    v = np.isfinite(layers["Viking red"]).ravel()
    S = lambda w: np.bincount(bid5[v], weights=w, minlength=bid5.max() + 1)
    nn = S(np.ones(v.sum())); mean = S(layers["Viking red"].ravel()[v].astype(float)) / np.maximum(nn, 1)
    ids = np.nonzero(nn > 0)[0]
    placed = to_frame(ids, mean[ids])
    both = np.isfinite(placed) & np.isfinite(direct)
    r_reg = float(np.corrcoef(placed[both], direct[both])[0, 1])
    sh = np.roll(placed, MAP_W // 2, axis=1); both_s = np.isfinite(sh) & np.isfinite(direct)
    r_shift = float(np.corrcoef(sh[both_s], direct[both_s])[0, 1])
    print("registration: Viking 5° block means, TES cells placed vs frame direct r %.4f (shifted 180°: %.4f)"
          % (r_reg, r_shift), flush=True)
    assert r_reg > 0.99 and r_shift < 0.9, "the 5° grid is misplaced on the frame"

    blocks = {s: block_ids(s) for s in SIZES}
    grids, ncells = {}, None
    res = {"sizes_deg": list(SIZES), "dayside": {}, "nightside": {}, "day_vs_night": {}}
    for side in ("dayside", "nightside"):
        ti = gdal.Open(os.path.join(TES, "TES_TI_2007_%s.tif" % side)).ReadAsArray()[R0:R1].astype(float)
        meas = gdal.Open(os.path.join(TES, "TES_TI_2007_%s_measured.tif" % side)).ReadAsArray()[R0:R1] == 1
        for name, m in layers.items():
            null = np.roll(m, NC // 2, axis=1)
            ok = (meas & (ti > 0) & np.isfinite(m) & np.isfinite(null)).ravel()
            x, xn, y = m.ravel()[ok].astype(float), null.ravel()[ok].astype(float), np.log(ti.ravel()[ok])
            rows = {}
            for s in SIZES:
                bid, ncell = blocks[s]
                r, pooled, sdy, cells, kid, kn = block_stats(x, y, bid[ok], ncell)
                rn, pooled_n, _, _, _, _ = block_stats(xn, y, bid[ok], ncell)
                if s == MAP_SIZE and side == MAP_SIDE and name in MAPS:
                    grids[name] = to_frame(kid, r)
                    ncells = to_frame(kid, kn) if ncells is None else ncells
                rows["%g" % s] = {"layer": summarise(r, pooled, SIGN[name]),
                                  "null_shift180": summarise(rn, pooled_n, SIGN[name]),
                                  "sd_log_ti_median": float(np.median(sdy)), "cells": cells}
                L, N = rows["%g" % s]["layer"], rows["%g" % s]["null_shift180"]
                print("%-9s %-22s %4g°  median %+.3f [%+.2f, %+.2f]  pooled %+.3f  sign %4s  | null median %+.3f pooled %+.3f"
                      "  | sd(log TI) %.2f  %5d blocks"
                      % (side, name, s, L["median"], *L["p25_p75"], L["pooled"],
                         "%.0f%%" % (100 * L["share_physical_sign"]) if SIGN[name] else "-",
                         N["median"], N["pooled"], rows["%g" % s]["sd_log_ti_median"], L["blocks"]), flush=True)
            res[side][name] = {"r_global": float(np.corrcoef(x, y)[0, 1]), "by_block_deg": rows}

    d, n = layers["THEMIS day DN"], layers["THEMIS night DN"]
    ok = (np.isfinite(d) & np.isfinite(n)).ravel()
    x, y = d.ravel()[ok].astype(float), n.ravel()[ok].astype(float)
    res["day_vs_night"]["r_global"] = float(np.corrcoef(x, y)[0, 1])
    res["day_vs_night"]["by_block_deg"] = {}
    for s in SIZES:
        bid, ncell = blocks[s]
        r, pooled, _, _, _, _ = block_stats(x, y, bid[ok], ncell)
        res["day_vs_night"]["by_block_deg"]["%g" % s] = summarise(r, pooled, 0)
        print("day vs night DN %4g°  median %+.3f [%+.2f, %+.2f]  pooled %+.3f  %5d blocks"
              % (s, np.median(r), np.percentile(r, 25), np.percentile(r, 75), pooled, r.size), flush=True)
    print("day vs night DN global r %+.3f" % res["day_vs_night"]["r_global"])

    wkt = ds.GetProjection()
    res["map_5deg"] = {"side": MAP_SIDE, "registration_r": r_reg, "registration_r_shift180": r_shift,
                       "files": {}, "type_areas": area_blocks(grids, ncells)}
    for name, tag in MAPS.items():
        path = os.path.join(G.OUTDIR, "global60_tes_r5deg_%s.tif" % tag)
        write_map(grids[name], path, wkt)
        g = grids[name]
        res["map_5deg"]["files"][name] = {"path": path, "blocks": int(np.isfinite(g).sum()),
                                         "share_physical_sign": float(np.mean(np.sign(g[np.isfinite(g)]) == SIGN[name]))}
        print("wrote", path, "%d blocks" % np.isfinite(g).sum())
    for a, rows in res["map_5deg"]["type_areas"].items():
        for d in rows:
            print("  %-16s %3g-%3g°E %+3g..%+3g°  night IR %s  index %s  Viking %s  cells %s" % (
                a, *d["lon_e"], *d["lat"], *("%+.2f" % d[n] if d[n] is not None else "  -  "
                                              for n in ("THEMIS night DN", "diurnal-contrast index", "Viking red")),
                d["cells"]))
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
