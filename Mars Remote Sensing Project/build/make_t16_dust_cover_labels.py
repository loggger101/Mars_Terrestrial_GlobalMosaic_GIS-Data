# -*- coding: utf-8 -*-
r"""Test T16: do the thermal bands help predict TES dust cover, a label independent of inertia and albedo? (KB §69.142)

T10-T12 (KB §69.133-§69.135) used labels built from TES thermal inertia and albedo. The TES Dust Cover Index (DCI,
Ruff & Christensen 2002), the mean emissivity at 1350-1400 cm-1, measures dust from the spectrum itself, independent
of both. ASU serves it only as a colour picture (`tes_ruffdust.png`, 5760 x 2880, 16 pixels per degree, simple
cylindrical, -180 to 180 E, 90 N to 90 S, colour-coded over shaded relief; downloaded 2026-11-13 at the author's yes,
with the labelled version `tes_ruffdust_label.png` that holds its scale, to `Mars Project\Reference\
TES_dust_cover_index_ASU\`). The scale steps one colour per 0.01 of DCI: red 0.92-0.93, orange 0.93-0.94, yellow
0.94-0.95, green 0.95-0.96, cyan 0.96-0.97, blue 0.97-0.98, magenta 0.98-0.99; grey is no data. The values cannot be
read back, the colour step can, by hue (HSV, saturation above 0.35 so the grey relief is left out). Three classes,
fixed before any model ran, on Ruff & Christensen's reading that DCI below about 0.94 marks dust:
  1 dusty       red, orange       DCI < 0.94      hue < 45 or >= 330 deg
  2 transitional yellow, green    0.94-0.96        45-150 deg
  3 clear       cyan, blue, magenta  >= 0.96       150-330 deg
Everything else is T10's and T9's: the 4 km lattice, the 14 held-out 15 deg blocks and the within-block split,
Gaussian maximum likelihood with equal priors, cos-latitude weights, 1,000 block resamples, the four band sets and the
answer rule.

Predictions, written 2026-11-13 before the first run:
  D1  At the block split thermal does NOT HELP by the rule.
  D2  Within blocks thermal HELPS.
  D3  At the block split leaving out Viking costs more balanced accuracy than leaving out thermal.
  D4  At the block split all 7 bands reach at least 43.3 % balanced.
  Descriptive, not predicted: the agreement of the DCI classes with T11's thermophysical units (Cramer's V).

  "<ArcGIS Pro Python>" make_t16_dust_cover_labels.py   -> logs\t16_dust_cover_labels.json
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_t9_material_labels as T9
import make_t11_thermophysical_units as T11
import grid60 as G

DCI = os.path.join(os.path.dirname(G.OUTDIR), "Reference", "TES_dust_cover_index_ASU", "tes_ruffdust.png")
OUT = os.path.join(HERE, "logs", "t16_dust_cover_labels.json")
CLASSES = ["dusty (DCI < 0.94)", "transitional (0.94-0.96)", "clear (>= 0.96)"]
log = T9.log


def dci_classes_image():
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    a = np.asarray(Image.open(DCI).convert("RGB")).astype(np.float32) / 255.0
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.where(mx > 0, mx, 1), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = np.where(mx - mn > 0, mx - mn, 1)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60.0
    cls = np.zeros(a.shape[:2], np.int8)
    col = sat > 0.35
    cls[col & ((h < 45) | (h >= 330))] = 1
    cls[col & (h >= 45) & (h < 150)] = 2
    cls[col & (h >= 150) & (h < 330)] = 3
    return cls, h, sat


def main():
    T9.selftest()
    cls_img, hue, sat = dci_classes_image()
    # check: the six pure colours of the scale land in their classes
    probe = {(1.0, 0.0, 0.0): 1, (1.0, 0.55, 0.0): 1, (1.0, 1.0, 0.0): 2, (0.0, 0.8, 0.0): 2, (0.0, 1.0, 1.0): 3,
             (0.0, 0.0, 1.0): 3, (1.0, 0.0, 1.0): 3, (0.8, 0.8, 0.8): 0}
    for rgb, want in probe.items():
        r, g, b = rgb
        mx, mn = max(rgb), min(rgb)
        s = (mx - mn) / mx if mx else 0
        dd = (mx - mn) or 1
        hh = (((g - b) / dd) % 6 if mx == r else (b - r) / dd + 2 if mx == g else (r - g) / dd + 4) * 60
        got = 0 if s <= 0.35 else 1 if (hh < 45 or hh >= 330) else 2 if hh < 150 else 3
        assert got == want, (rgb, got, want)
    log("check: the scale's colours fall in their classes; image %s, shares (no data, 1, 2, 3) %s" % (
        cls_img.shape, np.round(np.bincount(cls_img.ravel(), minlength=4) / cls_img.size, 3).tolist()))
    X = np.load(T9.CACHE)["X"]
    ny, nx = X.shape[:2]
    rng = np.random.default_rng(T9.SEED)
    ii, jj = np.mgrid[0:ny, 0:nx]
    lon, lat = T9.lattice_lonlat(ii, jj)
    lon_g = np.where(lon >= 180.0, lon - 360.0, lon)
    c = np.clip(((lon_g + 180.0) * 16).astype(int), 0, 5759)
    r = np.clip(((90.0 - lat) * 16).astype(int), 0, 2879)
    lab = cls_img[r, c].astype(np.int16)
    unit, _ = T11.unit_labels(lon_g, lat)
    valid = (lab > 0) & (X > 0).all(-1)
    y = lab.astype(int) - 1
    w = np.cos(np.radians(lat)).astype(np.float64)
    K = 3
    shares = [float(w[valid & (y == k)].sum() / w[valid].sum()) for k in range(K)]
    log("%d labelled samples; class shares %s" % (valid.sum(), [round(s, 3) for s in shares]))
    # descriptive: DCI class against T11's units
    both = valid & (unit > 0)
    T = np.zeros((3, 3))
    np.add.at(T, (y[both], unit[both] - 1), w[both])
    P = T / T.sum(); E = P.sum(1, keepdims=True) * P.sum(0, keepdims=True)
    V = float(np.sqrt(((P - E) ** 2 / E).sum() / 2))
    log("DCI class x T11 unit (rows dusty/transitional/clear, columns A dust/C duricrust/B sand and rock), shares of row:")
    for k in range(3):
        log("  %-26s %s" % (CLASSES[k], np.round(T[k] / T[k].sum(), 3).tolist()))
    log("  Cramer's V %.3f" % V)
    split = json.load(open(T9.SPLIT, encoding="utf-8"))
    held = set(split["v2"]["test_blocks"])
    code = lambda bx, by: (bx + 100) * 100 + (by + 10)
    bid = code(np.floor(lon_g / T9.BLOCK).astype(np.int32), np.floor(lat / T9.BLOCK).astype(np.int32))
    test_block = np.isin(bid, [code(*map(int, b.split("_"))) for b in held])
    cx, cy = np.floor(lon_g / T9.WCELL).astype(int), np.floor(lat / T9.WCELL).astype(int)
    cell = (cx + 1000) * 1000 + (cy + 100)
    uc = np.unique(cell)
    test_within = np.isin(cell, rng.choice(uc, uc.size // 2, replace=False))
    res = {"classes": CLASSES, "class_shares": shares, "cramers_v_with_t11_units": V,
           "dci_by_t11_unit_row_shares": (T / T.sum(1, keepdims=True)).round(4).tolist(), "splits": {}}
    for sname, te_mask in (("block", test_block), ("within", test_within)):
        tr, te = valid & ~te_mask, valid & te_mask
        Xtr, ytr = X[tr], y[tr]
        Xte, yte, wte, bte = X[te], y[te], w[te], bid[te]
        ub, binv = np.unique(bte, return_inverse=True)
        B = ub.size
        counts = np.stack([np.bincount(rng.integers(0, B, B), minlength=B) for _ in range(T9.NBOOT)])
        area = np.bincount(yte, weights=wte, minlength=K)
        out = {"n_train": int(tr.sum()), "n_test": int(te.sum()), "one_class_everywhere": float(area.max() / area.sum()),
               "sets": {}}
        boot = {}
        for name, cols in T9.BANDSETS.items():
            p = T9.predict(T9.fit(Xtr, ytr, cols, K), Xte, cols)
            cmb = np.zeros((B, K, K))
            np.add.at(cmb, (binv, yte, p), wte)
            po, kap, ba, prod = T9.stats(cmb.sum(0))
            boot[name] = T9.stats(np.tensordot(counts, cmb, axes=1))
            out["sets"][name] = {"accuracy": float(po), "kappa": float(kap), "balanced_accuracy": float(ba),
                                 "producers": dict(zip(CLASSES, np.round(prod, 4).tolist()))}
            log("%-6s %-32s acc %5.1f %%  kappa %.3f  balanced %5.1f %%  producers %s" % (
                sname, name, 100 * po, kap, 100 * ba, " ".join("%.1f" % (100 * v) for v in prod)))
        ci = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
        full = out["sets"]["all 7 bands"]
        for name in T9.BANDSETS:
            if name == "all 7 bands":
                continue
            s = out["sets"][name]
            s["gain_from_full_stack"] = {
                "accuracy": full["accuracy"] - s["accuracy"], "accuracy_ci95": ci(boot["all 7 bands"][0] - boot[name][0]),
                "balanced_accuracy": full["balanced_accuracy"] - s["balanced_accuracy"],
                "balanced_accuracy_ci95": ci(boot["all 7 bands"][2] - boot[name][2])}
            g = s["gain_from_full_stack"]
            log("%-6s   all 7 minus %-30s acc %+5.1f pt [%+.1f, %+.1f]  balanced %+5.1f pt [%+.1f, %+.1f]" % (
                sname, name, 100 * g["accuracy"], 100 * g["accuracy_ci95"][0], 100 * g["accuracy_ci95"][1],
                100 * g["balanced_accuracy"], 100 * g["balanced_accuracy_ci95"][0], 100 * g["balanced_accuracy_ci95"][1]))
        g = out["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
        out["thermal_helps"] = bool(g["accuracy_ci95"][0] > 0 and g["balanced_accuracy_ci95"][0] > 0)
        log("%-6s thermal %s on dust-cover classes (one class everywhere %.1f %%)"
            % (sname, "HELPS" if out["thermal_helps"] else "does NOT HELP", 100 * out["one_class_everywhere"]))
        res["splits"][sname] = out
    S = res["splits"]
    gb = S["block"]["sets"]["without thermal (no night, day)"]["gain_from_full_stack"]
    gv = S["block"]["sets"]["without visible (no Viking)"]["gain_from_full_stack"]
    res["predictions"] = {
        "D1 block: thermal does not help": not S["block"]["thermal_helps"],
        "D2 within: thermal helps": S["within"]["thermal_helps"],
        "D3 block: Viking costs more balanced accuracy than thermal": gv["balanced_accuracy"] > gb["balanced_accuracy"],
        "D4 block: all 7 bands >= 43.3 % balanced": S["block"]["sets"]["all 7 bands"]["balanced_accuracy"] >= 0.433}
    for k, v in res["predictions"].items():
        log("prediction %-65s %s" % (k, "held" if v else "NOT HELD"))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
