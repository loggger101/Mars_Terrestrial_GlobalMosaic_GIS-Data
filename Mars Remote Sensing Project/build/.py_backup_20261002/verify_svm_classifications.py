# -*- coding: utf-8 -*-
"""Checks his two SVM classifications (29-30 Sep, KB §29) against independent evidence.

Read-only. Reads pyramid levels only, so it runs on the laptop in about two minutes.
Nothing in the gdb or the .aprx is written.

  1. class shares by latitude band
  2. agreement between the two maps (area-weighted, kappa)
  3. training-set score: how much of each of his 512 polygons comes back as its own class
     (an UPPER bound on accuracy, not an accuracy assessment)
  4. IAU named craters: is 'Crater' commoner inside a named crater than in a ring round it?
  5. the 4096-px block period in the night-grid map
  6. how much of the 7-band map elevation alone reproduces

Run with ArcGIS Pro's Python (arcpy + osgeo.gdal):
  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" verify_svm_classifications.py
"""
import os, json, time
import numpy as np
import arcpy
from osgeo import gdal
from matplotlib.path import Path

gdal.UseExceptions()
HERE  = os.path.dirname(os.path.abspath(__file__))
DRIVE = os.path.splitdrive(HERE)[0] or "Z:"          # Z: on the laptop, F: on the desktop (KB §2.4)
GDB   = os.path.join(DRIVE + os.sep, "Mars Project", "Mars Project.gdb")
OUT   = os.path.join(HERE, "logs", "svm_check.json")

KPD   = 3396.19 * np.pi / 180.0                       # km per degree, Mars sphere
NAMES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]   # Value 0..3 (RAT), Classvalue 1..4

# name, pyramid level for the coarse pass, level for the polygon/crater pass, central meridian
RUNS = {
    "night": ("Classified_202609292109007048151", 4, 2, 180.0,
              "SVM over the ±60° segments + Night IR (29 Sep)"),
    "comp7": ("Classified_202609300147338582853", 3, 1, 0.0,
              "SVM over the 7-band CompositeBand (30 Sep)"),
}


def read_level(fc, lvl):
    ds = gdal.Open("OpenFileGDB:%s:%s" % (GDB, fc))
    gt = ds.GetGeoTransform()
    b = ds.GetRasterBand(1).GetOverview(lvl)
    a = b.ReadAsArray(); m = b.GetMaskBand().ReadAsArray() > 0
    H, W = a.shape
    geo = dict(dpx=gt[1] * ds.RasterXSize / W / 1000 / KPD,
               dpy=-gt[5] * ds.RasterYSize / H / 1000 / KPD,
               lat_top=gt[3] / 1000 / KPD, x0=gt[0], px_m=gt[1] * ds.RasterXSize / W)
    return a, m, geo


def lats(H, geo):
    return geo["lat_top"] - (np.arange(H) + 0.5) * geo["dpy"]


def cursor(fc, fields):
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), fields,
                               spatial_reference=arcpy.SpatialReference(104905)) as cur:
        return list(cur)


def kappa(ct):
    po = np.trace(ct) / ct.sum(); pe = (ct.sum(0) * ct.sum(1)).sum() / ct.sum() ** 2
    return po, (po - pe) / (1 - pe)


t0 = time.time()
res = {}
coarse = {}

# ---------------------------------------------------------------- 1. shares
for key, (fc, lc, lf, cm, label) in RUNS.items():
    a, m, geo = read_level(fc, lc)
    geo["lon_left"] = cm + geo["x0"] / 1000 / KPD
    coarse[key] = (a, m, geo)
    lat = lats(a.shape[0], geo)
    bands = {}
    for lo, hi in [(60, 90), (30, 60), (0, 30), (-30, 0), (-60, -30), (-90, -60)]:
        sel = (lat >= lo) & (lat < hi)
        if not sel.any():
            continue
        v = a[sel][m[sel]]
        bands["%d..%d" % (lo, hi)] = (np.bincount(v, minlength=4) / max(v.size, 1)).round(3).tolist()
    w = np.repeat(np.cos(np.radians(lat))[:, None], a.shape[1], 1)
    sh = np.bincount(a[m], weights=w[m], minlength=4); sh /= sh.sum()
    res[key] = dict(raster=fc, label=label, share_area_weighted=sh.round(3).tolist(), share_by_lat=bands)
    print("%s\n  area shares %s" % (label, dict(zip(NAMES, sh.round(3)))))

# ---------------------------------------------------------------- 2. agreement on a 0.1° grid, ±60°
lon = np.arange(0.05, 360, 0.1); lat = np.arange(59.95, -60, -0.1)
LON, LAT = np.meshgrid(lon, lat)
samp = {}
for key in RUNS:
    a, m, g = coarse[key]
    r = ((g["lat_top"] - LAT) / g["dpy"]).astype(int)
    c = (((LON - g["lon_left"]) % 360) / g["dpx"]).astype(int)
    samp[key] = (a[r, c], m[r, c])
ok = samp["night"][1] & samp["comp7"][1]
ct = np.zeros((4, 4))
np.add.at(ct, (samp["night"][0][ok], samp["comp7"][0][ok]), np.cos(np.radians(LAT[ok])))
po, k = kappa(ct)
res["agreement"] = dict(rows="night", cols="comp7", table=(ct / ct.sum()).round(3).tolist(),
                        agreement=round(po, 3), kappa=round(k, 3))
print("agreement between the two maps, ±60°: %.3f, kappa %.3f" % (po, k))

# ---------------------------------------------------------------- 3 + 4 need the finer level
polys = []
for g, v in cursor("Landform_TrainingSamples_terrain", ["SHAPE@", "Classvalue"]):
    polys.append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g]))
tbox = np.array([[min(p[0] for r in rs for p in r), max(p[0] for r in rs for p in r),
                  min(p[1] for r in rs for p in r), max(p[1] for r in rs for p in r)] for _, rs in polys])
craters = []
for fc in ["MARS_nomenclature_craters_lt100km_March2019", "MARS_nomenclature_craters_gt100km_March2019"]:
    craters += cursor(fc, ["name", "diameter", "center_lat", "center_lon"])

def training_score(a, m, g, polys):
    """Area-weighted confusion of his polygons (rows) against the map's classes (cols)."""
    H, W = a.shape
    cmx = np.zeros((4, 4)); own = []
    for v, rings in polys:
        hit = np.zeros(4)
        for ring in rings:
            xy = np.array(ring)
            lo_ = xy[0, 0] % 360 + ((xy[:, 0] % 360 - xy[0, 0] % 360 + 180) % 360 - 180)
            col = (lo_ - g["lon_left"]) / g["dpx"]; row = (g["lat_top"] - xy[:, 1]) / g["dpy"]
            r0, r1 = max(int(row.min()), 0), min(int(np.ceil(row.max())) + 1, H)
            c0, c1 = int(np.floor(col.min())), int(np.ceil(col.max())) + 1
            if r1 <= r0:
                continue
            rr, cc = np.mgrid[r0:r1, c0:c1]
            ins = Path(np.c_[col, row]).contains_points(
                np.c_[cc.ravel() + .5, rr.ravel() + .5]).reshape(rr.shape)
            sel = ins & m[rr, cc % W]
            if sel.any():
                np.add.at(hit, a[rr[sel], (cc % W)[sel]],
                          np.cos(np.radians(g["lat_top"] - (rr[sel] + .5) * g["dpy"])))
        if hit.sum():
            cmx[v - 1] += hit; own.append((v - 1, hit[v - 1] / hit.sum()))
    return cmx, own


def crater_score(a, m, g, craters, tbox):
    """'Crater' (value 0) fraction inside 0.7 R and in a 1.5-2.5 R ring, per IAU crater >= 5 km
    that does not touch any training polygon's bounding box."""
    H, W = a.shape
    fin, frg = [], []
    for name, D, clat, clon in craters:
        if D is None or D < 5:
            continue
        R = D / 2; rlat = R / KPD; rlon = rlat / max(np.cos(np.radians(clat)), .05)
        if abs(clat) + 2.5 * rlat > g["lat_top"] - .5:
            continue
        l180 = (clon + 180) % 360 - 180
        if len(tbox) and ((tbox[:, 0] <= l180 + 2.5 * rlon) & (tbox[:, 1] >= l180 - 2.5 * rlon) &
                          (tbox[:, 2] <= clat + 2.5 * rlat) & (tbox[:, 3] >= clat - 2.5 * rlat)).any():
            continue
        cc0 = ((clon % 360 - g["lon_left"]) % 360) / g["dpx"]; rc0 = (g["lat_top"] - clat) / g["dpy"]
        hw = int(np.ceil(2.5 * rlon / g["dpx"])) + 1; hh = int(np.ceil(2.5 * rlat / g["dpy"])) + 1
        r0, r1 = int(rc0) - hh, int(rc0) + hh + 1
        if r0 < 0 or r1 > H:
            continue
        cols = np.arange(int(cc0) - hw, int(cc0) + hw + 1)
        win = a[r0:r1][:, cols % W]; wm = m[r0:r1][:, cols % W]
        dy = (np.arange(r0, r1) + .5 - rc0) * g["dpy"]; dx = (cols + .5 - cc0) * g["dpx"]
        dist = np.hypot(dy[:, None] * KPD, dx[None, :] * KPD * np.cos(np.radians(clat - dy[:, None]))) / R
        ins = (dist < .7) & wm; ring = (dist > 1.5) & (dist < 2.5) & wm
        if ins.sum() < 9 or ring.sum() < 9:
            continue
        fin.append((win[ins] == 0).mean()); frg.append((win[ring] == 0).mean())
    return np.array(fin), np.array(frg)


for key, (fc, lc, lf, cm, label) in RUNS.items():
    a, m, g = read_level(fc, lf)
    g["lon_left"] = cm + g["x0"] / 1000 / KPD

    # 3. training-set score
    cmx, own = training_score(a, m, g, polys)
    oa, k = kappa(cmx)
    maj = [sum(1 for c, f in own if c == i and f > .5) for i in range(4)]
    tot = [sum(1 for c, f in own if c == i) for i in range(4)]
    res[key]["training_score"] = dict(
        accuracy=round(oa, 3), kappa=round(k, 3),
        one_class_everywhere=round(cmx.sum(1).max() / cmx.sum(), 3),
        row_normalised=(cmx / cmx.sum(1, keepdims=True)).round(3).tolist(),
        polygons_majority_own_class=dict(zip(NAMES, ["%d/%d" % x for x in zip(maj, tot)])))
    print("%s\n  training-set score %.3f, kappa %.3f; polygons won: %s" %
          (label, oa, k, dict(zip(NAMES, ["%d/%d" % x for x in zip(maj, tot)]))))

    # 4. IAU craters, D >= 5 km, not touching any training polygon's box
    fin, frg = crater_score(a, m, g, craters, tbox)
    res[key]["iau_craters"] = dict(n=len(fin), crater_inside=round(fin.mean(), 3),
                                   crater_ring=round(frg.mean(), 3),
                                   pct_inside_gt_ring=round(100 * (fin > frg).mean(), 1),
                                   px_m=round(g["px_m"]))
    print("  IAU craters n=%d: 'Crater' inside %.3f vs ring %.3f; inside > ring for %.1f%%" %
          (len(fin), fin.mean(), frg.mean(), 100 * (fin > frg).mean()))

# ---------------------------------------------------------------- 5. block period, night map
a, m, g = coarse["night"]
dcol = (a[:, 1:] != a[:, :-1]).mean(0)
edges = (np.where(dcol > 4 * np.median(dcol))[0] + 1) * g["dpx"]
full_px_per_deg = KPD * 1000 / 100.0
period = np.diff(edges) * full_px_per_deg
res["night"]["block_edges_deg_from_0E"] = edges.round(2).tolist()
res["night"]["edge_spacing_in_full_res_px"] = period.round(0).tolist()
print("night map: vertical block edges are %s x 4096 full-res px apart (4096 px = one processing tile)"
      % sorted(set(np.round(period / 4096, 2).tolist())))

# ---------------------------------------------------------------- 6. elevation alone, 7-band map
dem = np.load(os.path.join(HERE, "dem_global_3000_f32.npy"))      # CM 0, -180..180, 90..-90
a, m, g = coarse["comp7"]
Hd, Wd = dem.shape
vv = a[((np.arange(Hd) + .5) / Hd * a.shape[0]).astype(int)][:, ((np.arange(Wd) + .5) / Wd * a.shape[1]).astype(int)]
dl = 90 - (np.arange(Hd) + .5) * 180 / Hd
sel = np.abs(dl) < 60
w = np.repeat(np.cos(np.radians(dl[sel]))[:, None], Wd, 1).ravel()
b = np.digitize(dem[sel].ravel(), np.arange(-9000, 22001, 500))
tab = np.zeros((b.max() + 1, 4)); np.add.at(tab, (b, vv[sel].ravel()), w)
elev_only = tab.max(1).sum() / tab.sum()
res["comp7"]["elevation_only_reproduces"] = round(elev_only, 3)
res["comp7"]["largest_class_alone"] = round(tab.sum(0).max() / tab.sum(), 3)
print("7-band map: elevation alone (500 m bins) reproduces %.1f%% of it at ±60° (largest class alone %.1f%%)"
      % (100 * elev_only, 100 * tab.sum(0).max() / tab.sum()))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w"), indent=1)
np.save(os.path.join(HERE, "svm_night_ov4.npy"), coarse["night"][0])
np.save(os.path.join(HERE, "svm_comp7_ov3.npy"), coarse["comp7"][0])
print("wrote %s  (%.0f s)" % (OUT, time.time() - t0))
