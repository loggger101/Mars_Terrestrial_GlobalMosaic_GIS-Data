# -*- coding: utf-8 -*-
r"""X5c: a pixel classifier (U-Net) on the training-split labels, scored per pixel on the held-out polygons the way
the SVM was (§31.3, §57). ArcGIS Python, on the desktop. The author's decision, 2026-10-20 (KB §66.6): train it
beside the box detector, which reverses the "boxes only" of q26 (§50) for this one model.

    python make_dl_pixels.py --export          Classified_Tiles from the training split, to C:\MarsScratch\x5c
    python make_dl_pixels.py --train [--epochs 30] [--backbone RESNET34]
    python make_dl_pixels.py --classify --emd <model .emd>   one raster per held-out 15° window (as X5's)
    python make_dl_pixels.py --score <folder of window rasters> [--out <json>]
    python make_dl_pixels.py --score-svm       the same scorer on the published SVM map's windows (the baseline)
    python make_dl_pixels.py --classify-global --emd <model .emd> [--tiles N]
                                               all of ±60° in 4,096 px tiles, each read with a 256 px margin
    python make_dl_pixels.py --mosaic          the tiles' cores into Global60\global60_landforms_unet_200m.tif
    python make_dl_pixels.py --classify-global --pass B --emd <model .emd>
                                               the second pass, every window 128 px later (KB §66.8)
    python make_dl_pixels.py --mosaic --two-pass   each pixel from the pass that puts it farther from a
                                               tile edge -> Global60\global60_landforms_unet_200m_seamfix.tif
    python make_dl_pixels.py --seams <raster> [<raster> ...]
                                               class changes by column and row phase, for periodic tile seams

The ±60° map (the author's yes, 2026-10-20, KB §66.7): tile cores 4,096 x 4,096 px on the G200 grid, each classified
with a 256 px (51.2 km) margin that is then cut away, so no core edge is a window edge. Written on internal disk
(C:\MarsScratch\x5c\global), mosaicked there, then copied to Global60. It is scored by
verify_global60_classification.py --cell 200 --raster <it>, the script behind every SVM figure in §31.3 and §57.

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

--labels v2 (labelsets.py; decision D17, KB §68, NEXT-STEPS §11.5 step 3): the same steps on the seven-class
labels. Exports from Landform_TrainingSamples_v2_60_train, works in C:\MarsScratch\x5c_v2, names the model
global60_unet_x5c_v2_<date> and the maps global60_landforms_unet_v2_200m[_seamfix].tif; --score-svm scores the v2
SVM maps. Seven classes, codes 1-7. Nothing of the four-class run is read or replaced, and --train refuses an
export made from the other label set.
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
import labelsets as L

gdal.UseExceptions()
LABELS = os.path.join(GDB, L.TRAIN)
WORK = r"C:\MarsScratch\x5c" + L.TAG                             # internal disk first (KB §36.4)
NAMES = L.NAMES                                                  # class values 1-4, or 1-7 with --labels v2
K = len(NAMES)
SVM = {"svm%s_200m_mode11" % L.TAG: os.path.join(G.OUTDIR, "global60_landforms_svm%s_200m_mode11.tif" % L.TAG),
       "svm%s_200m" % L.TAG: os.path.join(G.OUTDIR, "global60_landforms_svm%s_200m.tif" % L.TAG)}
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
    marker = training_split(data)
    assert "\\%s\n" % L.TRAIN in marker, "REFUSING: %s was not exported from %s" % (data, L.TRAIN)   # any drive letter
    name = "global60_unet_x5c%s_%s" % (L.TAG, time.strftime("%Y%m%d"))
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
    """read(k, extent) -> (class array 0..K-1 / 255 none, geotransform). Sums each window's confusion on its own
    polygons, at 200 m and on the 400 m lattice."""
    polys = heldout_by_block()
    w = windows()
    res = {"label": label}
    for step in (2, 1):
        cmx = np.zeros((K, K)); own = []; npx = [0, 0]
        for k, e in w.items():
            a, gt = read(k, e)
            col0 = int(round((gt[0] - G.G200.ox) / 200.0)); row0 = int(round((G.G200.oy - gt[3]) / 200.0))
            a = a[(-row0) % step::step, (-col0) % step::step]    # keep the pixels on the global step lattice
            x_left = gt[0] + ((-col0) % step) * 200.0; y_top = gt[3] - ((-row0) % step) * 200.0
            m = a != 255
            npx[0] += m.sum(); npx[1] += m.size
            g = dict(dpx=200.0 * step * DEG, dpy=200.0 * step * DEG, lat_top=y_top * DEG,
                     lon_left=G.G200.lon_of(x_left) % 360)
            c, o = training_score(np.where(m, a, 0).astype(np.uint8), m, g, polys.get(k, []), K)
            cmx += c; own += o
        oa, kp = kappa(cmx)
        maj = {NAMES[i]: "%d/%d" % (sum(1 for c, f in own if c == i and f > .5), sum(1 for c, f in own if c == i))
               for i in range(K)}
        res["%dm" % (200 * step)] = dict(
            accuracy=round(oa, 4), kappa=round(kp, 4), polygons=len(own),
            one_class_everywhere=round(cmx.sum(1).max() / cmx.sum(), 4),
            producers=dict(zip(NAMES, (np.diag(cmx) / np.maximum(cmx.sum(1), 1e-12)).round(3).tolist())),
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
    """pixel value -> 0..K-1 in NAMES order (255 none), from the raster's attribute table by class name."""
    lut = np.full(256, 255, np.uint8)
    try:
        flds = [f.name for f in arcpy.ListFields(path)]
    except Exception:
        flds = []
    name = next((f for f in ("Class_name", "ClassName", "Class", "CLASSNAME") if f in flds), None)
    if name is None:                               # no attribute table: the export's class values 1..K
        lut[1:K + 1] = np.arange(K)
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
    out = os.path.join(HERE, "logs", "dl_pixels_score_svm%s_baseline.json" % L.TAG)
    json.dump(dict(allres, scored=time.strftime("%Y-%m-%d %H:%M")), open(out, "w"), indent=1)
    print("->", out)


CORE, MARGIN = 4096, 256
GLOBAL = os.path.join(WORK, "global")
UNET_MAP = "global60_landforms_unet%s_200m.tif" % L.TAG
UNET_SEAMFIX = "global60_landforms_unet%s_200m_seamfix.tif" % L.TAG   # two passes, KB §66.8


def tiles():
    """[(row0, col0, nrows, ncols)] cores on the G200 grid, row-major."""
    return [(r, c, min(CORE, G.G200.ny - r), min(CORE, G.G200.nx - c))
            for r in range(0, G.G200.ny, CORE) for c in range(0, G.G200.nx, CORE)]


def classify_global():
    """--pass A (default): windows from 256 px before each core, so the tool's own 256 px tiles meet at multiples
    of 256. --pass B: every window 128 px later (128 px later still at the map's left and top edges, where an
    earlier start would be clipped and shift the phase), so B's tile edges fall at A's tile centres."""
    ready()
    emd = arg("--emd", "")
    assert emd.endswith(".emd") and os.path.exists(emd), "--emd <trained model .emd>"
    B = arg("--pass", "A").upper() == "B"
    outdir = os.path.join(GLOBAL, "tiles_b" if B else "tiles")
    os.makedirs(outdir, exist_ok=True)
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.env.processorType = "GPU"
    arcpy.env.overwriteOutput = True
    arcpy.env.snapRaster = STACK
    arcpy.env.cellSize = STACK
    T = tiles()
    if "--only" in sys.argv:                                     # one tile, "row,col", for tests
        T = [t for t in T if "%d,%d" % t[:2] == arg("--only", "")]
    T = T[:arg("--tiles", 10 ** 6)]
    t0 = time.time(); done = 0
    for i, (r, c, nr, nc) in enumerate(T):
        part = os.path.join(outdir, "t_r%05d_c%06d.tif" % (r, c))
        if os.path.exists(part):                                 # rerunnable: finished tiles are kept
            continue
        if B:
            cs = c - 128 if c >= 128 else 128; rs = r - 128 if r >= 128 else 128
            ce, re_ = c + nc + MARGIN + 128, r + nr + MARGIN + 128
        else:
            cs, rs, ce, re_ = c - MARGIN, r - MARGIN, c + nc + MARGIN, r + nr + MARGIN
        arcpy.env.extent = arcpy.Extent(G.G200.ox + cs * 200.0, G.G200.oy - re_ * 200.0,
                                        G.G200.ox + ce * 200.0, G.G200.oy - rs * 200.0)
        t = time.time()
        res = arcpy.ia.ClassifyPixelsUsingDeepLearning(STACK, emd, "padding 64;batch_size 8;predict_background False",
                                                       "PROCESS_AS_MOSAICKED_IMAGE")
        res.save(part)
        done += 1
        left = sum(1 for (a, b, _, _) in T[i + 1:]
                   if not os.path.exists(os.path.join(outdir, "t_r%05d_c%06d.tif" % (a, b))))
        el = time.time() - t0
        print("pass %s tile %3d/%d row %5d col %6d: %4.0f s; %d to go, ~%.1f h" % (
            "B" if B else "A", i + 1, len(T), r, c, time.time() - t, left, el / done * left / 3600), flush=True)
    arcpy.env.extent = None
    print("classified ->", outdir)


def core_of(p, r, c, nr, nc):
    """The class values 1..K (0 none) of a tile raster over the core (r, c, nr, nc), and where the tile covers it."""
    lut = lut_of(p)                                              # pixel -> 0..K-1 by class name; 255 none
    t = gdal.Open(p)
    gt = t.GetGeoTransform()
    c0 = int(round((gt[0] - G.G200.ox) / 200.0)); r0 = int(round((G.G200.oy - gt[3]) / 200.0))
    v = np.zeros((nr, nc), np.uint8); cov = np.zeros((nr, nc), bool)
    a0, b0 = max(c, c0), max(r, r0)
    a1, b1 = min(c + nc, c0 + t.RasterXSize), min(r + nr, r0 + t.RasterYSize)
    if a1 > a0 and b1 > b0:
        a = t.GetRasterBand(1).ReadAsArray(a0 - c0, b0 - r0, a1 - a0, b1 - b0)
        w = lut[a.astype(np.int64).clip(0, 255)]
        v[b0 - r:b1 - r, a0 - c:a1 - c] = np.where(w == 255, 0, w + 1)
        cov[b0 - r:b1 - r, a0 - c:a1 - c] = True
    return v, cov


def edge_distance(idx, phase):
    """Pixels from the nearest edge of the tool's 256 px tiles, for tiles that start at index = phase (mod 256)."""
    p = (idx - phase) % 256
    return np.minimum(p, 255 - p)


def mosaic():
    """--two-pass: each pixel from pass A or pass B, whichever puts it farther from its tile's edge (the smaller of
    its row and column distances); A where B does not cover it or has no class."""
    two = "--two-pass" in sys.argv
    name = UNET_SEAMFIX if two else UNET_MAP
    out = os.path.join(GLOBAL, name)
    T = tiles()
    dirs = [os.path.join(GLOBAL, "tiles")] + ([os.path.join(GLOBAL, "tiles_b")] if two else [])
    for d in dirs:
        missing = [t for t in T if not os.path.exists(os.path.join(d, "t_r%05d_c%06d.tif" % t[:2]))]
        assert not missing, "%s: %d tiles missing, first %s" % (d, len(missing), missing[0])
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(out, G.G200.nx, G.G200.ny, 1, gdal.GDT_Byte,
                    ["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512"])
    ds.SetGeoTransform((G.G200.ox, 200.0, 0, G.G200.oy, 0, -200.0))
    ds.SetProjection(gdal.Open(STACK).GetProjection())
    b = ds.GetRasterBand(1)
    b.SetNoDataValue(0)
    count = np.zeros(K + 1, np.int64); fromB = 0; differ = 0
    for r, c, nr, nc in T:
        v, _ = core_of(os.path.join(dirs[0], "t_r%05d_c%06d.tif" % (r, c)), r, c, nr, nc)
        if two:
            w, cov = core_of(os.path.join(dirs[1], "t_r%05d_c%06d.tif" % (r, c)), r, c, nr, nc)
            cols = np.arange(c, c + nc); rows = np.arange(r, r + nr)
            dA = np.minimum(edge_distance(rows, 0)[:, None], edge_distance(cols, 0)[None, :])
            dB = np.minimum(edge_distance(rows, 128)[:, None], edge_distance(cols, 128)[None, :])
            useB = cov & (w != 0) & ((dB > dA) | (v == 0))
            fromB += int(useB.sum()); differ += int(((v != w) & cov & (v != 0) & (w != 0)).sum())
            v = np.where(useB, w, v)
        count += np.bincount(v.ravel(), minlength=K + 1)
        b.WriteArray(v.astype(np.uint8), c, r)
    b.FlushCache()
    ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
    ds = None
    arcpy.management.CalculateStatistics(out)
    arcpy.management.BuildRasterAttributeTable(out, "Overwrite")
    arcpy.management.AddField(out, "Class_name", "TEXT", field_length=32)
    for f in ("Classvalue", "Red", "Green", "Blue"):           # as the SVM maps carry them (KB §66.9)
        arcpy.management.AddField(out, f, "LONG")
    colours = L.COLOURS
    with arcpy.da.UpdateCursor(out, ["Value", "Class_name", "Classvalue", "Red", "Green", "Blue"]) as cur:
        for row in cur:
            n = NAMES[int(row[0]) - 1]
            cur.updateRow([row[0], n, row[0]] + list(colours[n]))
    share = {NAMES[i]: round(float(count[i + 1] / count[1:].sum()), 4) for i in range(K)}
    rec = dict(raster=out, tiles=len(T), pixels_by_value=count.tolist(), class_share=share,
               made=time.strftime("%Y-%m-%d %H:%M"))
    if two:
        rec.update(share_from_pass_b=round(fromB / count[1:].sum(), 4),
                   share_a_b_disagree=round(differ / count[1:].sum(), 4))
    json.dump(rec, open(os.path.join(HERE, "logs", "dl_unet%s_global_mosaic%s.json" % (L.TAG, "_seamfix" if two else "")), "w"),
              indent=1)
    print("mosaic ->", out, json.dumps(rec))
    final = os.path.join(G.OUTDIR, name)
    assert not os.path.exists(final), "REFUSING: %s exists" % final
    for f in os.listdir(GLOBAL):
        if f.startswith(name):
            shutil.copy2(os.path.join(GLOBAL, f), G.OUTDIR)
    print("copied ->", final)


def seams(paths):
    """Class changes between neighbouring pixels, folded by column (and row) index modulo each period P; a tile seam
    of period P puts one phase far above the rest. Ratio = the highest phase's rate over the median phase's."""
    out = {}
    for p in paths:
        ds = gdal.Open(p); b = ds.GetRasterBand(1)
        nx, ny = ds.RasterXSize, ds.RasterYSize
        cch = np.zeros(nx - 1); cn = np.zeros(nx - 1); rch = np.zeros(ny - 1); rn = np.zeros(ny - 1)
        prev = None
        for y in range(0, ny, 1024):
            a = b.ReadAsArray(0, y, nx, min(1024, ny - y))
            if prev is not None:                                 # the row pair across the strip edge
                a = np.vstack([prev, a]); y -= 1
            v = (a != 0) & (a != 255)                            # 0 none here, 255 none in the SVM maps
            ok = v[:, 1:] & v[:, :-1]
            cch += ((a[:, 1:] != a[:, :-1]) & ok).sum(0); cn += ok.sum(0)
            okr = v[1:] & v[:-1]
            rch[y:y + a.shape[0] - 1] += ((a[1:] != a[:-1]) & okr).sum(1); rn[y:y + a.shape[0] - 1] += okr.sum(1)
            prev = a[-1:]
        res = {}
        for P in (128, 256, 4096):
            for name, ch, n in (("columns", cch, cn), ("rows", rch, rn)):
                ph = np.array([ch[k::P].sum() / max(n[k::P].sum(), 1) for k in range(P)])
                res["%s_%d" % (name, P)] = dict(ratio=round(float(ph.max() / np.median(ph)), 3),
                                                 at_phase=int(ph.argmax()))
        res["change_rate"] = round(float(cch.sum() / cn.sum()), 4)
        out[os.path.basename(p)] = res
        print(os.path.basename(p), json.dumps(res), flush=True)
    json.dump(out, open(os.path.join(HERE, "logs", "dl_seams.json"), "w"), indent=1)


if __name__ == "__main__":
    if "--classify-global" in sys.argv:
        classify_global()
    elif "--mosaic" in sys.argv:
        mosaic()
    elif "--seams" in sys.argv:
        seams(sys.argv[sys.argv.index("--seams") + 1:])
    elif "--export" in sys.argv:
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
