# -*- coding: utf-8 -*-
r"""X5c: a pixel classifier (U-Net) on the training-split labels, scored per pixel on the held-out polygons the way
the SVM was (§31.3, §57). ArcGIS Python, on the desktop. The author's decision, 2026-10-20 (KB §66.6): train it
beside the box detector, which reverses the "boxes only" of q26 (§50) for this one model.

    python make_dl_pixels.py --export          Classified_Tiles from the training split, to C:\MarsScratch\x5c
    python make_dl_pixels.py --train [--epochs 30] [--backbone RESNET34]
    python make_dl_pixels.py --classify --emd <model .emd>   one raster per held-out 15° window (as X5's)
    python make_dl_pixels.py --score <folder of window rasters> [--out <json>]
    python make_dl_pixels.py --score-svm       the same scorer on the published SVM map's windows (the baseline)

Labels: Landform_TrainingSamples_terrain_60_train only; unlabelled ground is value 0 in the tiles and is ignored
by the loss (ignore_classes [0]), so the model is never taught that unlabelled ground is a class. class_balancing
weights the loss by inverse class frequency. Backbone unfrozen, early stopping off (as X5b, §66.5).

The score: svmcheck.training_score (the code behind §31.3 and §57), area-weighted, per window on that window's own
held-out polygons, summed. At 400 m (every second 200 m pixel on the 400 m lattice, as §57 scored the 200 m map
from its first overview) and at 200 m. --score-svm runs the same code on global60_landforms_svm_200m_mode11.tif
and _200m.tif, so the comparison is like for like.

Verdict rule, written before the run (KB §66.6), at 400 m: X5c beats the published SVM map if its held-out
accuracy AND kappa both exceed that map's under this same scorer; within 2 points of accuracy either way is a
match; below that, the SVM stays the better map. Producer's and user's accuracy per class are reported, the
rare classes' above all.
"""
import os, sys, json, time, socket, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import numpy as np
import arcpy
from osgeo import gdal
import grid60 as G
from svmcheck import kappa, training_score, crater_score, KPD
from make_dl_model import STACK, TEST, MODELS, MARK, ready, arg, training_split, heldout_blocks

gdal.UseExceptions()
LABELS = os.path.join(GDB, "Landform_TrainingSamples_terrain_60_train")
WORK = r"C:\MarsScratch\x5c"                                     # internal disk first (KB §36.4)
NAMES = ["Crater", "steep/windy hills", "lava tube", "Normal Ground"]   # class values 1-4
SVM = {"svm_200m_mode11": os.path.join(G.OUTDIR, "global60_landforms_svm_200m_mode11.tif"),
       "svm_200m": os.path.join(G.OUTDIR, "global60_landforms_svm_200m.tif")}
DEG = 180.0 / (np.pi * G.R_MARS)                                 # degrees per metre on this sphere


def export():
    out = arg("--out", os.path.join(WORK, "export_tiles"))
    if os.path.exists(out):
        assert os.path.exists(os.path.join(out, MARK)), "REFUSING: %s was not made here" % out
        shutil.rmtree(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t = time.time()
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.ia.ExportTrainingDataForDeepLearning(
        STACK, out, LABELS, image_chip_format="TIFF", tile_size_x=256, tile_size_y=256, stride_x=128,
        stride_y=128, output_nofeature_tiles="ONLY_TILES_WITH_FEATURES", metadata_format="Classified_Tiles",
        class_value_field="Classvalue")
    open(os.path.join(out, MARK), "w").write("Written by build\\make_dl_pixels.py --export from %s\nlabels: %s\n"
                                             % (STACK, LABELS))
    print("exported in %.0f s -> %s" % (time.time() - t, out))
    print(open(os.path.join(out, "stats.txt")).read()[:1500])


def train():
    ready()
    data = arg("--data", os.path.join(WORK, "export_tiles"))
    training_split(data)
    name = "global60_unet_x5c_%s" % time.strftime("%Y%m%d")
    out = os.path.join(WORK, "models", name)
    final = os.path.join(MODELS, name)
    assert not os.path.exists(out) and not os.path.exists(final), "REFUSING: %s already exists" % name
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cfg = dict(in_folder=[data], out_folder=out, max_epochs=arg("--epochs", 30), model_type="UNET",
               batch_size=arg("--batch", 8), arguments="class_balancing True;ignore_classes [0]",
               backbone_model=arg("--backbone", "RESNET34"), validation_percentage=10,
               stop_training="CONTINUE_TRAINING", freeze="UNFREEZE_MODEL", chip_size=256, monitor="VALID_LOSS")
    print("training", json.dumps(cfg), flush=True)
    t = time.time()
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.ia.TrainDeepLearningModel(**cfg)
    msgs = arcpy.GetMessages()
    print(msgs)
    secs = time.time() - t
    open(os.path.join(out, "training_messages.txt"), "w", encoding="utf-8").write(msgs)
    json.dump(dict(cfg, host=socket.gethostname(), seconds=round(secs), finished=time.strftime("%Y-%m-%d %H:%M"),
                   script="make_dl_pixels.py"), open(os.path.join(out, "run_config.json"), "w"), indent=1)
    shutil.copytree(out, final)
    print("trained in %.0f s -> %s, copied to %s" % (secs, out, final))


def windows():
    """The X5 windows: each held-out block's polygons' extent + 25 km, snapped outward to the 200 m stack grid."""
    sr = arcpy.Describe(STACK).spatialReference
    out = {}
    for k, (x0, y0, x1, y1) in sorted(heldout_blocks(sr).items()):
        s = lambda v, f: G.G200.ox + f((v - G.G200.ox) / 200.0) * 200.0
        t = lambda v, f: G.G200.oy - f((G.G200.oy - v) / 200.0) * 200.0
        out[k] = (s(x0 - 25e3, np.floor), t(y0 - 25e3, np.ceil), s(x1 + 25e3, np.ceil), t(y1 + 25e3, np.floor))
    return out


def classify():
    ready()
    emd = arg("--emd", "")
    assert emd.endswith(".emd") and os.path.exists(emd), "--emd <trained model .emd>"
    mname = os.path.basename(os.path.dirname(emd))
    outdir = arg("--outdir", os.path.join(WORK, "classified", mname))     # rerunnable; one folder per model
    os.makedirs(outdir, exist_ok=True)
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.env.processorType = "GPU"
    arcpy.env.overwriteOutput = True
    arcpy.env.snapRaster = STACK
    arcpy.env.cellSize = STACK
    w = windows()
    for i, (k, e) in enumerate(w.items()):
        part = os.path.join(outdir, "x5c_block_%+04d_%+03d.tif" % k)
        if os.path.exists(part):
            continue
        arcpy.env.extent = arcpy.Extent(*e)
        t = time.time()
        r = arcpy.ia.ClassifyPixelsUsingDeepLearning(STACK, emd, "padding 64;batch_size 8;predict_background False",
                                                     "PROCESS_AS_MOSAICKED_IMAGE")
        r.save(part)
        print("block %2d/%d lon %4d lat %4d: %.0f s" % (i + 1, len(w), k[0], k[1], time.time() - t), flush=True)
    arcpy.env.extent = None
    keep = os.path.join(os.path.dirname(emd), "classified_heldout")             # one copy beside the model
    if os.path.exists(keep):
        shutil.rmtree(keep)
    shutil.copytree(outdir, keep)
    print("windows ->", outdir, "copied ->", keep)


def heldout_by_block():
    """{block: [(class value, rings in lon/lat degrees)]}, blocks as heldout_blocks()."""
    out = {}
    with arcpy.da.SearchCursor(TEST, ["SHAPE@", "Classvalue"]) as c:
        for g, v in c:
            k = (int(g.centroid.X // 15) * 15, int(g.centroid.Y // 15) * 15)
            out.setdefault(k, []).append((int(v), [[(p.X, p.Y) for p in part if p is not None] for part in g]))
    return out


def score_windows(read, label):
    """read(k, extent) -> (class array 0-3 / 255 none, geotransform). Sums each window's confusion on its own
    polygons, at 200 m and on the 400 m lattice."""
    polys = heldout_by_block()
    w = windows()
    res = {"label": label}
    for step in (2, 1):
        cmx = np.zeros((4, 4)); own = []; npx = [0, 0]
        for k, e in w.items():
            a, gt = read(k, e)
            col0 = int(round((gt[0] - G.G200.ox) / 200.0)); row0 = int(round((G.G200.oy - gt[3]) / 200.0))
            a = a[(-row0) % step::step, (-col0) % step::step]    # keep the pixels on the global step lattice
            x_left = gt[0] + ((-col0) % step) * 200.0; y_top = gt[3] - ((-row0) % step) * 200.0
            m = a != 255
            npx[0] += m.sum(); npx[1] += m.size
            g = dict(dpx=200.0 * step * DEG, dpy=200.0 * step * DEG, lat_top=y_top * DEG,
                     lon_left=G.G200.lon_of(x_left) % 360)
            c, o = training_score(np.where(m, a, 0).astype(np.uint8), m, g, polys.get(k, []))
            cmx += c; own += o
        oa, kp = kappa(cmx)
        maj = {NAMES[i]: "%d/%d" % (sum(1 for c, f in own if c == i and f > .5), sum(1 for c, f in own if c == i))
               for i in range(4)}
        res["%dm" % (200 * step)] = dict(
            accuracy=round(oa, 4), kappa=round(kp, 4), polygons=len(own),
            one_class_everywhere=round(cmx.sum(1).max() / cmx.sum(), 4),
            producers=dict(zip(NAMES, (np.diag(cmx) / cmx.sum(1)).round(3).tolist())),
            users=dict(zip(NAMES, (np.diag(cmx) / np.maximum(cmx.sum(0), 1e-12)).round(3).tolist())),
            polygons_majority_own_class=maj, classified_share_of_window_pixels=round(npx[0] / npx[1], 4),
            confusion_area_weighted=(cmx / cmx.sum()).round(4).tolist())
        print(label, "%dm" % (200 * step), json.dumps(res["%dm" % (200 * step)]["accuracy"]),
              "kappa", res["%dm" % (200 * step)]["kappa"], flush=True)
    res["iau_craters_400m"] = crater_test(read)
    return res


def crater_test(read):
    """§31.3's crater test inside the windows at 400 m: 'Crater' inside 0.7 R against a 1.5-2.5 R ring, per IAU crater
    >= 5 km whose 2.5 R box lies wholly in the window and touches no labelled polygon's box. A map that outlines
    craters scores inside > ring; one that paints cratered provinces scores both alike."""
    craters = []
    for fc in ["MARS_nomenclature_craters_lt100km_March2019", "MARS_nomenclature_craters_gt100km_March2019"]:
        with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["name", "diameter", "center_lat", "center_lon"]) as c:
            craters += list(c)
    rings = [r for fc in (TEST, LABELS) for r in
             [[[(p.X, p.Y) for p in part if p] for part in g] for g, in arcpy.da.SearchCursor(fc, ["SHAPE@"])]]
    tbox = np.array([[min(p[0] for r in rs for p in r), max(p[0] for r in rs for p in r),
                      min(p[1] for r in rs for p in r), max(p[1] for r in rs for p in r)] for rs in rings])
    fin, frg = [], []
    for k, e in windows().items():
        a, gt = read(k, e)
        col0 = int(round((gt[0] - G.G200.ox) / 200.0)); row0 = int(round((G.G200.oy - gt[3]) / 200.0))
        a = a[(-row0) % 2::2, (-col0) % 2::2]
        x_left = gt[0] + ((-col0) % 2) * 200.0; y_top = gt[3] - ((-row0) % 2) * 200.0
        m = a != 255
        g = dict(dpx=400.0 * DEG, dpy=400.0 * DEG, lat_top=y_top * DEG, lon_left=G.G200.lon_of(x_left) % 360)
        W = a.shape[1] * g["dpx"]
        inwin = []
        for cr in craters:                          # wholly inside this window (crater_score checks rows itself)
            if cr[1] is None:
                continue
            rlon = cr[1] / 2 / KPD / max(np.cos(np.radians(cr[2])), .05)
            c0 = (cr[3] % 360 - g["lon_left"]) % 360
            if 2.5 * rlon + g["dpx"] * 2 < c0 < W - 2.5 * rlon - g["dpx"] * 2:
                inwin.append(cr)
        f, r = crater_score(np.where(m, a, 0).astype(np.uint8), m, g, inwin, tbox)
        fin += list(f); frg += list(r)
    fin, frg = np.array(fin), np.array(frg)
    out = dict(n=len(fin), crater_inside=round(float(fin.mean()), 3) if len(fin) else None,
               crater_ring=round(float(frg.mean()), 3) if len(fin) else None,
               pct_inside_gt_ring=round(100 * float((fin > frg).mean()), 1) if len(fin) else None)
    print("IAU craters in the windows:", out, flush=True)
    return out


def lut_of(path):
    """pixel value -> 0..3 in NAMES order (255 none), from the raster's attribute table by class name."""
    lut = np.full(256, 255, np.uint8)
    try:
        flds = [f.name for f in arcpy.ListFields(path)]
    except Exception:
        flds = []
    name = next((f for f in ("Class_name", "ClassName", "Class", "CLASSNAME") if f in flds), None)
    if name is None:                               # no attribute table: the export's class values 1-4
        lut[1:5] = np.arange(4)
        return lut
    with arcpy.da.SearchCursor(path, ["Value", name]) as c:
        for v, n in c:
            if n and n.strip().lower() in [x.lower() for x in NAMES]:
                lut[int(v)] = [x.lower() for x in NAMES].index(n.strip().lower())
    return lut


def score(folder):
    parts = {}
    for f in os.listdir(folder):
        if f.startswith("x5c_block_") and f.endswith(".tif"):
            lon, lat = f[len("x5c_block_"):-4].split("_")
            parts[(int(lon), int(lat))] = os.path.join(folder, f)
    luts = {}

    def read(k, e):
        p = parts[k]
        lut = luts.setdefault(p, lut_of(p))
        ds = gdal.Open(p)
        b = ds.GetRasterBand(1)
        raw = b.ReadAsArray()
        nd = b.GetNoDataValue()
        a = lut[raw.astype(np.int64).clip(0, 255)]
        if nd is not None:
            a[raw == nd] = 255
        return a, ds.GetGeoTransform()
    res = score_windows(read, folder)
    res.update(scored=time.strftime("%Y-%m-%d %H:%M"), luts={os.path.basename(p): {int(v): NAMES[i] for v, i in
                                                                                     enumerate(l) if i != 255}
                                                               for p, l in luts.items()})
    out = arg("--out", os.path.join(HERE, "logs", "dl_pixels_score_%s.json" % os.path.basename(folder.rstrip("\\/"))))
    json.dump(res, open(out, "w"), indent=1)
    print("->", out)


def score_svm():
    allres = {}
    for tag, path in SVM.items():
        lut = lut_of(path)
        ds = gdal.Open(path)
        b = ds.GetRasterBand(1)
        gt0 = ds.GetGeoTransform()
        mask = b.GetMaskBand()

        def read(k, e, b=b, gt0=gt0, lut=lut, mask=mask):
            c0 = int(round((e[0] - gt0[0]) / 200.0)); r0 = int(round((gt0[3] - e[3]) / 200.0))
            nx = int(round((e[2] - e[0]) / 200.0)); ny = int(round((e[3] - e[1]) / 200.0))
            c0, r0 = max(c0, 0), max(r0, 0)
            nx, ny = min(nx, ds.RasterXSize - c0), min(ny, ds.RasterYSize - r0)
            raw = b.ReadAsArray(c0, r0, nx, ny)
            a = lut[raw]
            a[mask.ReadAsArray(c0, r0, nx, ny) == 0] = 255
            return a, (gt0[0] + c0 * 200.0, 200.0, 0, gt0[3] - r0 * 200.0, 0, -200.0)
        allres[tag] = score_windows(read, tag)
    out = os.path.join(HERE, "logs", "dl_pixels_score_svm_baseline.json")
    json.dump(dict(allres, scored=time.strftime("%Y-%m-%d %H:%M")), open(out, "w"), indent=1)
    print("->", out)


if __name__ == "__main__":
    if "--export" in sys.argv:
        export()
    elif "--train" in sys.argv:
        train()
    elif "--classify" in sys.argv:
        classify()
    elif "--score-svm" in sys.argv:
        score_svm()
    elif "--score" in sys.argv:
        score(sys.argv[sys.argv.index("--score") + 1])
    else:
        print(__doc__)
