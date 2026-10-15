# -*- coding: utf-8 -*-
r"""Stripes and seams in a classified ±60° landform map. Read-only; ArcGIS Python (GDAL only).

Written 2026-10-14 for the 180° stripe (KB §54), reproducing the two checks that found it.

  change rate of column c = share of rows where class(c) != class(c-1), both pixels classed
  (255 = no class is skipped). Same for rows (class(r) != class(r-1)).

  A. the 180° stripe: G200 columns 53340-53355 (column 53346 holds the source DEM's edge).
     Rule, written before the post-fix run: every column there within the "normal range",
     i.e. |z| <= 4 against the columns 53000-53300 and 53400-53700 (z = (rate - mean) / sd),
     and the 16-column mean within 25 % of the reference mean. Before the fix the author measured
     0.26-0.28 against 0.08, so the rule can fail (run it with the pre-fix map to see).
  B. tile seams every 16384 px (the classify tiles, columns and rows): z of the seam's change
     rate against the 200 columns (rows) either side, seam ± 2 excluded. Rule: |z| <= 4 at every seam.
  Also by 10° latitude band for columns 53340-53355 (the stripe was worst at +9° to +43°).

  python check_landform_columns.py [map.tif] [--json out.json]
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from osgeo import gdal
gdal.UseExceptions()

MAP = r"F:\Mars Project\Global60\global60_landforms_svm_200m.tif"
TILE, ND, R_MARS = 16384, 255, 3396190.0
STRIPE = np.arange(53340, 53356)
REF = np.r_[53000:53301, 53400:53701]
BANDS = list(range(-60, 60, 10))


def scan(path):
    d = gdal.Open(path)
    b = d.GetRasterBand(1)
    nx, ny = d.RasterXSize, d.RasterYSize
    gt = d.GetGeoTransform()
    col_ch = np.zeros(nx, np.int64); col_n = np.zeros(nx, np.int64)
    row_ch = np.zeros(ny, np.int64); row_n = np.zeros(ny, np.int64)
    band_ch = np.zeros((len(BANDS), STRIPE.size + REF.size), np.int64)
    band_n = np.zeros_like(band_ch)
    cols = np.r_[STRIPE, REF]
    prev = None
    step = 512
    for y0 in range(0, ny, step):
        h = min(step, ny - y0)
        a = b.ReadAsArray(0, y0, nx, h)
        v = a != ND
        both = v[:, 1:] & v[:, :-1]
        ch = (a[:, 1:] != a[:, :-1]) & both
        col_ch[1:] += ch.sum(axis=0); col_n[1:] += both.sum(axis=0)
        lat = (gt[3] + (y0 + np.arange(h) + 0.5) * gt[5]) / R_MARS * 180 / np.pi
        bi = np.clip(((lat + 60) // 10).astype(int), 0, len(BANDS) - 1)
        for k in range(len(BANDS)):
            m = bi == k
            if m.any():
                band_ch[k] += ch[m][:, cols - 1].sum(axis=0)
                band_n[k] += both[m][:, cols - 1].sum(axis=0)
        full = a if prev is None else np.vstack([prev, a])
        vv = full != ND
        bothr = vv[1:] & vv[:-1]
        chr_ = (full[1:] != full[:-1]) & bothr
        r0 = y0 if prev is None else y0 - 1
        row_ch[r0 + 1:r0 + 1 + chr_.shape[0]] += chr_.sum(axis=1)
        row_n[r0 + 1:r0 + 1 + chr_.shape[0]] += bothr.sum(axis=1)
        prev = a[-1:]
    with np.errstate(invalid="ignore", divide="ignore"):
        return (col_ch / col_n, row_ch / row_n, band_ch / np.maximum(band_n, 1), nx, ny)


def z_at(rate, i, w=200):
    ref = np.r_[rate[max(0, i - w):i - 2], rate[i + 3:i + 3 + w]]
    ref = ref[np.isfinite(ref)]
    return (rate[i] - ref.mean()) / ref.std(), rate[i], ref.mean()


def main():
    argv = sys.argv[1:]
    if "--json" in argv:
        k = argv.index("--json"); argv = argv[:k] + argv[k + 2:]
    args = [a for a in argv if not a.startswith("--")]
    path = args[0] if args else MAP
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    print(path)
    col, row, band, nx, ny = scan(path)
    res = {"map": path}
    ref = col[REF]; mu, sd = np.nanmean(ref), np.nanstd(ref)
    zs = (col[STRIPE] - mu) / sd
    print("A. 180° columns: reference mean %.4f sd %.4f" % (mu, sd))
    print("   " + " ".join("%d:%.3f(z%+.1f)" % (c % 1000, r, z) for c, r, z in zip(STRIPE, col[STRIPE], zs)))
    smean = np.nanmean(col[STRIPE])
    okA = bool(np.all(np.abs(zs) <= 4) and abs(smean / mu - 1) <= 0.25)
    print("   16-column mean %.4f (%.2fx reference)   %s" % (smean, smean / mu, "PASS" if okA else "FAIL"))
    print("   by 10° band (stripe mean / reference mean):")
    for k, lo in enumerate(BANDS):
        s, r = band[k, :STRIPE.size].mean(), band[k, STRIPE.size:].mean()
        print("     %+3d..%+3d  %.3f / %.3f  = %.2fx" % (lo, lo + 10, s, r, s / r if r else np.nan))
    res["stripe"] = dict(ref_mean=mu, ref_sd=sd, cols={int(c): float(r) for c, r in zip(STRIPE, col[STRIPE])},
                         max_abs_z=float(np.max(np.abs(zs))), mean_ratio=float(smean / mu), pass_=okA)
    print("B. tile seams every %d px" % TILE)
    seams = []
    for i in range(TILE, nx, TILE):
        z, r, m = z_at(col, i); seams.append(("col", i, z, r, m))
    for i in range(TILE, ny, TILE):
        z, r, m = z_at(row, i); seams.append(("row", i, z, r, m))
    for kind, i, z, r, m in seams:
        print("   %s %6d  rate %.4f  neighbours %.4f  z %+5.2f" % (kind, i, r, m, z))
    okB = all(abs(s[2]) <= 4 for s in seams)
    print("   %s" % ("PASS" if okB else "FAIL"))
    res["seams"] = [dict(kind=k, index=int(i), z=float(z), rate=float(r), ref=float(m)) for k, i, z, r, m in seams]
    res["seams_pass"] = okB
    if out:
        json.dump(res, open(out, "w"), indent=1)
    print("RESULT", "PASS" if okA and okB else "FAIL")
    return 0 if okA and okB else 1


if __name__ == "__main__":
    sys.exit(main())
