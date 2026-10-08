# -*- coding: utf-8 -*-
r"""Scores global60_landforms_svm_<cell>m.tif the way §30 scored the two Pro-GUI maps (KB §31).

  1. HELD-OUT accuracy on Landform_TrainingSamples_terrain_60_test: whole 15° blocks the SVM
     never saw. This is the accuracy figure; the training-set score is printed beside it only
     to show the gap.
  2. IAU named craters >= 5 km: 'Crater' inside 0.7 R against a 1.5-2.5 R ring
  3. tile seams: class changes across 4096-px tile edges against elsewhere (the §30.2 defect)
  4. how much of it 500 m elevation bins alone reproduce (the §30.3 defect)

Reads the 400 m pyramid level. Read-only. Writes build\logs\global60_classification_check.json.
"""
import os, sys, json, time
import numpy as np
import arcpy
from osgeo import gdal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
from svmcheck import kappa, training_score, crater_score, KPD

gdal.UseExceptions()
GDB = r"Z:\Mars Project\Mars Project.gdb"
from make_global60_classification import OUT as CLS, CELL   # --cell 400 (default) or 200
# --raster scores another version of the map, e.g. a mode-filtered one; it is named in the outputs
TAG = "%dm" % CELL
if "--raster" in sys.argv:
    CLS = sys.argv[sys.argv.index("--raster") + 1]
    TAG = os.path.splitext(os.path.basename(CLS))[0].replace("global60_landforms_svm_", "")
OUT = os.path.join(HERE, "logs", "global60_classification_check_%s.json" % TAG)
NAMES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]
MARS = arcpy.SpatialReference(104905)


def polys(fc):
    out = []
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@", "Classvalue"], spatial_reference=MARS) as c:
        for g, v in c:
            out.append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g]))
    return out


def lut_from_rat():
    """Pixel value -> 0..3 in NAMES order, read from the raster's own attribute table."""
    lut = np.full(256, 255, np.uint8)
    with arcpy.da.SearchCursor(CLS, ["Value", "Class_name"]) as c:
        for v, n in c:
            k = [x.lower() for x in NAMES].index(n.strip().lower())
            lut[int(v)] = k
    return lut


def main():
    t0 = time.time()
    res = {}
    lut = lut_from_rat()
    res["rat"] = {int(v): NAMES[k] for v, k in enumerate(lut) if k != 255}
    ds = gdal.Open(CLS)
    band = ds.GetRasterBand(1)
    b = band if CELL >= 400 else band.GetOverview(0)        # always score at 400 m
    raw = b.ReadAsArray()
    m = (b.GetMaskBand().ReadAsArray() > 0) & (lut[raw] != 255)
    a = np.where(m, lut[raw], 0).astype(np.uint8)
    H, W = a.shape
    g = dict(dpx=360.0 / W, dpy=2 * G.G100.lat_of(G.G100.oy) / H,
             lat_top=G.G100.lat_of(G.G100.oy), lon_left=G.G100.lon_of(G.G100.ox))
    px_m = 2 * 3.141592653589793 * G.R_MARS / W                # metres per pixel at the equator
    print("read %d x %d at %.0f m, %.1f s" % (W, H, px_m, time.time() - t0))

    lat = g["lat_top"] - (np.arange(H) + .5) * g["dpy"]
    w = np.repeat(np.cos(np.radians(lat))[:, None], W, 1)
    sh = np.bincount(a[m], weights=w[m], minlength=4); sh /= sh.sum()
    res["share_area_weighted"] = dict(zip(NAMES, sh.round(3).tolist()))
    print("area shares", res["share_area_weighted"])

    for key, fc in [("held_out", "Landform_TrainingSamples_terrain_60_test"),
                    ("training_set", "Landform_TrainingSamples_terrain_60_train")]:
        P = polys(fc)
        cmx, own = training_score(a, m, g, P)
        oa, k = kappa(cmx)
        maj = ["%d/%d" % (sum(1 for c, f in own if c == i and f > .5), sum(1 for c, f in own if c == i))
               for i in range(4)]
        prod = (np.diag(cmx) / cmx.sum(1)).round(3).tolist()
        user = (np.diag(cmx) / np.maximum(cmx.sum(0), 1e-12)).round(3).tolist()
        res[key] = dict(polygons=len(P), accuracy=round(oa, 3), kappa=round(k, 3),
                        one_class_everywhere=round(cmx.sum(1).max() / cmx.sum(), 3),
                        producers=dict(zip(NAMES, prod)), users=dict(zip(NAMES, user)),
                        polygons_majority_own_class=dict(zip(NAMES, maj)),
                        confusion_area_weighted=(cmx / cmx.sum()).round(4).tolist())
        print("%-12s %3d polygons  accuracy %.3f  kappa %.3f  (one class everywhere %.3f)" %
              (key, len(P), oa, k, cmx.sum(1).max() / cmx.sum()))
        print("             producer's", dict(zip(NAMES, prod)))
        print("             won", dict(zip(NAMES, maj)))

    craters = []
    for fc in ["MARS_nomenclature_craters_lt100km_March2019", "MARS_nomenclature_craters_gt100km_March2019"]:
        with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["name", "diameter", "center_lat", "center_lon"]) as c:
            craters += list(c)
    allp = polys("Landform_TrainingSamples_terrain_60_train") + polys("Landform_TrainingSamples_terrain_60_test")
    tbox = np.array([[min(p[0] for r in rs for p in r), max(p[0] for r in rs for p in r),
                      min(p[1] for r in rs for p in r), max(p[1] for r in rs for p in r)] for _, rs in allp])
    fin, frg = crater_score(a, m, g, craters, tbox)
    res["iau_craters"] = dict(n=len(fin), crater_inside=round(fin.mean(), 3), crater_ring=round(frg.mean(), 3),
                              pct_inside_gt_ring=round(100 * (fin > frg).mean(), 1), px_m=round(px_m))
    print("IAU craters n=%d: 'Crater' inside %.3f vs ring %.3f; inside > ring %.1f%%"
          % (len(fin), fin.mean(), frg.mean(), 100 * (fin > frg).mean()))

    T = 4096 * 100.0 / px_m                                  # a 4096 px G100 tile in these pixels
    T2 = 4096 * 200.0 / px_m                                 # and a 4096 px G200 tile
    dc = (a[:, 1:] != a[:, :-1]) & m[:, 1:] & m[:, :-1]
    colj = dc.mean(0)
    seams = {}
    for nm, t in [("tile_4096_at_100m", T), ("tile_4096_at_200m", T2)]:
        on = np.array([j for j in range(len(colj)) if abs((j + 1) / t - round((j + 1) / t)) < 0.5 / t])
        off = np.setdiff1d(np.arange(len(colj)), on)
        seams[nm] = round(float(colj[on].mean() / colj[off].mean()), 3)
    res["seam_ratio"] = seams
    print("seam ratio (1.0 = no seams; the 29 Sep GUI map 2.77):", seams)

    dem = np.load(os.path.join(HERE, "dem_global_3000_f32.npy"))   # CM 0, -180..180, 90..-90
    Hd, Wd = dem.shape
    dl = 90 - (np.arange(Hd) + .5) * 180 / Hd
    dlon = -180 + (np.arange(Wd) + .5) * 360 / Wd
    rows = np.where(np.abs(dl) < g["lat_top"] - 0.1)[0]
    r = ((g["lat_top"] - dl[rows]) / g["dpy"]).astype(int)
    c = (((dlon % 360) - g["lon_left"]) % 360 / g["dpx"]).astype(int) % W
    cl = a[r][:, c]; ok = m[r][:, c]
    ww = np.repeat(np.cos(np.radians(dl[rows]))[:, None], Wd, 1)[ok]
    bins = np.digitize(dem[rows][ok], np.arange(-9000, 22001, 500))
    tab = np.zeros((bins.max() + 1, 4)); np.add.at(tab, (bins, cl[ok]), ww)
    res["elevation_only_reproduces"] = round(tab.max(1).sum() / tab.sum(), 3)
    res["largest_class_alone"] = round(tab.sum(0).max() / tab.sum(), 3)
    print("elevation alone reproduces %.1f%% (largest class alone %.1f%%; the 30 Sep map: 62.1%%)"
          % (100 * res["elevation_only_reproduces"], 100 * res["largest_class_alone"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(res, open(OUT, "w"), indent=1)
    np.save(os.path.join(HERE, "global60_landforms_%s_ov400.npy" % TAG), np.where(m, a, 255).astype(np.uint8))
    print("wrote %s  (%.0f s)" % (OUT, time.time() - t0))


if __name__ == "__main__":
    main()
