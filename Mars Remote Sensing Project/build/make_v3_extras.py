# -*- coding: utf-8 -*-
r"""Runs the v3 maps left unanswered (the author's word, 2026-11-07, D36: "any additional runs you think you should do").

Three limits of KB §69.81, each given its own retraining of the U-Net (and, for the first, of the SVM):

  fresh, fresh2  The 14 held-out blocks have been used three times. Fourteen other blocks, drawn at random from v3's 178
                 training blocks with a fixed seed (60, 61) and never yet held out, leave training and become the test.
                 Training polygons that touch a held-out one go too. U-Net and SVM (11 x 11 mode) are retrained without
                 them; each is scored beside the nearest-polygon baseline. The draw reads polygon counts only.
  noth           The thermal infrared has only been ablated on the SVM (§56, §69.50). The v3 U-Net retrained on the five
                 bands of global60_svm_stack_200m_nothermal.tif, on v3's training polygons.
  cut, add       Why the U-Net rose is not measured (§69.81). cut trains on the v2 polygons' screened pieces alone (Action
                 piece or keep), so cutting without adding; add trains on the v2 polygons plus v3's new ones (Action new
                 or fan), so adding without cutting. Beside v2 (neither) and v3 (both) that is a two-by-two.
  base           The finished v3 model classifying the same windows, so noth, cut and add are compared with a window
                 classification (one pass) and not with the two-pass mosaic.

Nothing here replaces a map. Each run classifies its windows only, 15 degree blocks with a 25 km margin, not all of ±60°.
The labels of a run live in C:\MarsScratch\x5c_v3x\extras.gdb, rebuilt by --plan from the seed, so the project's gdb is
not written. Models go to DLModels under their own tag, window rasters to Global60\v3_extras\<run>.

Written 2026-11-07 before any of these runs. Nothing below is adjusted after them.

**Predictions** (each reported held or not held):
  F1  fresh: the U-Net's accuracy lies in 70-92 % (86.5 % on the 1,652 polygons of the used blocks).
  F2  fresh: the U-Net's balanced accuracy lies in 60-85 % (77.3 %).
  F3  fresh: U-Net minus SVM, accuracy, block bootstrap: the interval lies above 0.
  F4  fresh: SVM minus nearest polygon, accuracy: the interval includes 0, as on the used blocks (§69.81, P7).
  F5  fresh: U-Net minus nearest polygon, accuracy: the interval lies above 0.
  F6  fresh2 repeats F1-F5 on its own draw, reported apart.
  T1  noth: its accuracy on each polygon set is within 3 points of base's.
  T2  base minus noth, accuracy, block bootstrap: the interval includes 0 on each polygon set. The SVM's thermal gain is
      1.4-2.0 points overall on four classes and 1.1 on seven (§69.50).
  C1  cut's balanced accuracy on the v2 polygons is above unet_v2's 56.9 %.
  C2  add's is above 56.9 % too.
  C3  add's is above cut's: hills and lava tube train in 150 and 11 blocks only because of the added polygons (§69.76).
  C4  each stays below base's: the two together do more than either.

Route, or --report writes nothing: the published unet_v3 and svm_v3 400 m arrays, scored here, must give their logged
accuracy and kappa within 0.001 on both held-out sets, and base must be the same model read the same way: its accuracy and kappa within 0.005 of the published U-Net on both held-out sets,
and its array matching the published one on at least 85 % of valid pixels. The first gate here, 90 %, was a guess made before
any window ran and base missed it, 0.8946: its scores match (87.54 % against 87.62 %, 86.37 against 86.47) while a chip grid at
another phase changes single pixels, so the scores are the gate and the pixels only catch a misplaced array (KB §69.83). --plant rolls base's array half a planet, and that check must refuse.

  "<ArcGIS Pro Python>" make_v3_extras.py --plan
  "<ArcGIS Pro Python>" make_v3_extras.py --run <name> --step export | train | classify | svm-train | svm-classify
  "<ArcGIS Pro Python>" make_v3_extras.py --report [--plant]
run_v3x.ps1 runs them in order, one process per step. Writes logs\v3_extras_plan.json and logs\v3_extras.json.
"""
import os, sys, json, glob, time, shutil, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if "--labels" not in sys.argv:
    sys.argv += ["--labels", "v3"]                           # labelsets reads this as it is imported
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import arcpy
from osgeo import gdal
from scipy import ndimage
import grid60 as G
import make_dl_model as MD
import make_dl_pixels as D
import make_block_bootstrap as B
import labelsets as L
from labelsets import SEVEN
from paths import GDB, on_drive

WORK = r"C:\MarsScratch\x5c_v3x"
EX = os.path.join(WORK, "extras.gdb")
EXPORT = r"D:\MarsScratch\x5c_v3x\export_tiles"     # the 6 TB disk: C: has room for no second chip set beside its pagefile
OUT = on_drive(r"Mars Project\Global60\v3_extras")
PLAN = os.path.join(HERE, "logs", "v3_extras_plan.json")
PREFIX = "Landform_TrainingSamples_%s_60_%s"
V3_TRAIN, V3_TEST, V2_TRAIN, V2_TEST = (os.path.join(GDB, PREFIX % s) for s in (("v3", "train"), ("v3", "test"),
                                                                               ("v2", "train"), ("v2", "test")))
V3_PROP = os.path.join(GDB, "Landform_TrainingSamples_v3_proposals")
BASE_EMD = r"C:\MarsScratch\x5c_v3\models\global60_unet_x5c_v3_20261105"
STACK5 = os.path.join(G.OUTDIR, "global60_svm_stack_200m_nothermal.tif")
BLOCKS, NEED, SIZE = 14, 30, (800, 2500)      # a draw: 14 blocks, >= 30 polygons of each class on each side, this many
SEEDS = {"fresh": 60, "fresh2": 61}
TAGS = {"fresh": "v3f", "fresh2": "v3g", "noth": "v3nt", "cut": "v3c", "add": "v3a", "base": None}
ARR = "global60_landforms_global60_landforms_unet_%s_200m_seamfix_ov400.npy"
SVM_ARR = "global60_landforms_%s_200m_mode11_ov400.npy"
PAIRS_F = [("unet", "svm"), ("unet", "near"), ("svm", "near")]
PAIRS_B = [("base", "noth"), ("base", "cut"), ("base", "add"), ("add", "cut"), ("cut", "unet_v2"), ("add", "unet_v2")]


def fc(run, side):
    return os.path.join(EX, PREFIX % (TAGS[run], side))


def actions():
    act = {o: a for o, a in arcpy.da.SearchCursor(V3_PROP, ["OID@", "Action"])}
    return {o: act[p] for o, p in arcpy.da.SearchCursor(V3_TRAIN, ["OID@", "ProposalOID"])}


def draw(seed, rows):
    """The first seeded draw of 14 blocks that leaves every class >= NEED polygons on each side, and SIZE in all."""
    blocks = sorted({b for _, b in rows})
    rng = np.random.default_rng(seed)
    for n in range(1, 100001):
        pick = set(rng.choice(blocks, BLOCKS, replace=False).tolist())
        c = collections.Counter(v for v, b in rows if b in pick)
        r = collections.Counter(v for v, b in rows if b not in pick)
        if all(c[k] >= NEED and r[k] >= NEED for k in range(1, 8)) and SIZE[0] <= sum(c.values()) <= SIZE[1]:
            return sorted(pick), n, {SEVEN[k - 1]: c[k] for k in range(1, 8)}
    sys.exit("no draw meets the conditions")


def select(src, dst, where):
    arcpy.conversion.FeatureClassToFeatureClass(src, os.path.dirname(dst), os.path.basename(dst), where)
    return int(arcpy.management.GetCount(dst)[0])


def plan():
    os.makedirs(WORK, exist_ok=True)
    if arcpy.Exists(EX):
        arcpy.management.Delete(EX)
    arcpy.management.CreateFileGDB(WORK, os.path.basename(EX))
    rows = list(arcpy.da.SearchCursor(V3_TRAIN, ["Classvalue", "Block"]))
    res = dict(script="make_v3_extras.py", when=time.strftime("%Y-%m-%d %H:%M"), training_polygons=len(rows))
    for run, seed in SEEDS.items():
        pick, tries, by_class = draw(seed, rows)
        where = "Block IN (%s)" % ",".join("'%s'" % b for b in pick)
        n_test = select(V3_TRAIN, fc(run, "test"), where)
        lyr = arcpy.management.MakeFeatureLayer(V3_TRAIN, "t_" + run, "NOT (%s)" % where)
        arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", fc(run, "test"), invert_spatial_relationship=True)
        arcpy.management.CopyFeatures(lyr, fc(run, "train"))
        n_train = int(arcpy.management.GetCount(fc(run, "train"))[0])
        res[run] = dict(seed=seed, blocks=pick, tries=tries, held_out=n_test, held_out_by_class=by_class, training=n_train,
                        dropped_touching=len(rows) - n_test - n_train)
        print(run, res[run], flush=True)
    act = actions()
    print(collections.Counter(act.values()), flush=True)
    res["actions"] = dict(collections.Counter(act.values()))
    pieces = [o for o, a in act.items() if a in ("piece", "keep")]
    added = [o for o, a in act.items() if a in ("new", "fan")]
    assert len(pieces) + len(added) == len(act), "an Action this script does not sort"
    res["cut"] = dict(training=select(V3_TRAIN, fc("cut", "train"), "OBJECTID IN (%s)" % ",".join(map(str, pieces))))
    lyr = arcpy.management.MakeFeatureLayer(V3_TRAIN, "t_add", "OBJECTID IN (%s)" % ",".join(map(str, added)))
    arcpy.management.Merge([V2_TRAIN, lyr], fc("add", "train"))
    res["add"] = dict(training=int(arcpy.management.GetCount(fc("add", "train"))[0]), v2=int(arcpy.management.GetCount(V2_TRAIN)[0]),
                      added=len(added))
    arcpy.management.Merge([V3_TEST, V2_TEST], os.path.join(EX, PREFIX % ("window", "test")))
    print(res["cut"], res["add"], flush=True)
    json.dump(res, open(PLAN, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", PLAN)


def windows_fc(run):
    return fc(run, "test") if run in SEEDS else os.path.join(EX, PREFIX % ("window", "test"))


def wire(run):
    """Points make_dl_pixels at this run: its labels, stack, windows, scratch and model name."""
    tag = TAGS[run]
    D.WORK = WORK
    MD.TEST = D.TEST = windows_fc(run)
    D.STACK = STACK5 if run == "noth" else MD.STACK
    if tag:
        L.TAG = "_" + tag
        L.TRAIN = PREFIX % (tag, "train")
        D.LABELS = V3_TRAIN if run == "noth" else fc(run, "train")
        if run == "noth":
            L.TRAIN = PREFIX % ("v3", "train")


def emd(run):
    """The run's finished model: its newest .emd on internal disk."""
    root = BASE_EMD if run == "base" else os.path.join(WORK, "models", "global60_unet_x5c_%s_*" % TAGS[run])
    hit = sorted(glob.glob(os.path.join(root, "*.emd")), key=os.path.getmtime)
    assert hit, "no .emd under %s" % root
    return hit[-1]


def classify(run):
    """One raster per window, as make_dl_pixels.classify, without its copy beside the model."""
    wire(run)
    D.ready()
    model = emd(run)
    part = os.path.join(WORK, "classified", run)
    os.makedirs(part, exist_ok=True)
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.env.processorType = "GPU"
    arcpy.env.overwriteOutput = True
    arcpy.env.snapRaster = D.STACK
    arcpy.env.cellSize = D.STACK
    w = D.windows()
    for i, (k, e) in enumerate(w.items()):
        p = os.path.join(part, "x5c_block_%+04d_%+03d.tif" % k)
        if os.path.exists(p):
            continue
        arcpy.env.extent = arcpy.Extent(*e)
        t = time.time()
        r = arcpy.ia.ClassifyPixelsUsingDeepLearning(D.STACK, model, "padding 64;batch_size 8;predict_background False",
                                                     "PROCESS_AS_MOSAICKED_IMAGE")
        r.save(p)
        print("block %2d/%d lon %4d lat %4d: %.0f s" % (i + 1, len(w), k[0], k[1], time.time() - t), flush=True)
    arcpy.env.extent = None
    shutil.copytree(part, os.path.join(OUT, run), dirs_exist_ok=True)
    print("windows ->", part, "copied ->", os.path.join(OUT, run))


def svm_paths(run):
    return os.path.join(WORK, "svm_%s.ecd" % run), os.path.join(WORK, "classified", run + "_svm")


def svm_train(run):
    ecd, _ = svm_paths(run)
    t = time.time()
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.ia.TrainSupportVectorMachineClassifier(MD.STACK, fc(run, "train"), ecd, max_samples_per_class=1000)
    print("trained in %.0f s -> %s" % (time.time() - t, ecd))


def svm_classify(run):
    wire(run)
    ecd, part = svm_paths(run)
    os.makedirs(part, exist_ok=True)
    arcpy.CheckOutExtension("ImageAnalyst")
    w = D.windows()
    for i, (k, e) in enumerate(w.items()):
        p = os.path.join(part, "x5c_block_%+04d_%+03d.tif" % k)
        if os.path.exists(p):
            continue
        t = time.time()
        with arcpy.EnvManager(extent=arcpy.Extent(*e), snapRaster=MD.STACK, cellSize=200, parallelProcessingFactor="100%"):
            arcpy.ia.ClassifyRaster(MD.STACK, ecd).save(p)
        print("block %2d/%d lon %4d lat %4d: %.0f s" % (i + 1, len(w), k[0], k[1], time.time() - t), flush=True)
    shutil.copy2(ecd, OUT)
    shutil.copytree(part, os.path.join(OUT, run + "_svm"), dirs_exist_ok=True)
    print("windows ->", part)


def mode11(a):
    """The published SVM map's 11 x 11 majority filter (make_global60_landforms_clean.py), inside one window."""
    votes = np.stack([ndimage.uniform_filter((a == k).astype(np.float32), size=11, mode="nearest") for k in range(len(SEVEN))])
    return np.where(a == 255, 255, votes.argmax(0)).astype(np.uint8)


def window_array(folder, shape, mode=False):
    """The window rasters on the published 400 m lattice (every second G200 pixel), 255 elsewhere."""
    H, W = shape
    out = np.full(shape, 255, np.uint8)
    for p in sorted(glob.glob(os.path.join(folder, "x5c_block_*.tif"))):
        lut = D.lut_of(p)
        ds = gdal.Open(p)
        band = ds.GetRasterBand(1)
        raw = band.ReadAsArray()
        a = lut[raw.astype(np.int64).clip(0, 255)]
        if band.GetNoDataValue() is not None:
            a[raw == band.GetNoDataValue()] = 255
        if mode:
            a = mode11(a)
        gt = ds.GetGeoTransform()
        c0 = int(round((gt[0] - G.G200.ox) / 200.0)); r0 = int(round((G.G200.oy - gt[3]) / 200.0))
        rs = np.arange(r0, r0 + a.shape[0]); cs = np.arange(c0, c0 + a.shape[1])
        rk, ck = rs % 2 == 0, cs % 2 == 0
        rr, cc = rs[rk] // 2, (cs[ck] // 2) % W
        inside = rr < H
        out[np.ix_(rr[inside], cc)] = a[np.ix_(rk, ck)][inside]
    return out


def published(name):
    a = np.load(os.path.join(HERE, name), mmap_mode="r")
    return a, a != 255, B.grid(a.shape)


def route():
    for arr, log2, log3 in ((ARR % "v3", "global60_landforms_unet_v3_200m_seamfix_on_v2_labels", "global60_landforms_unet_v3_200m_seamfix"),
                            (SVM_ARR % "v3", "v3_200m_mode11_on_v2_labels", "v3_200m_mode11")):
        a, m, g = published(arr)
        for fcn, log in ((V2_TEST, log2), (V3_TEST, log3)):
            oa, kp, _ = B.scores(B.rows(a, m, g, B.polys(fcn), len(SEVEN)).sum(0))
            h = json.load(open(os.path.join(HERE, "logs", "global60_classification_check_%s.json" % log), encoding="utf-8"))["held_out"]
            ok = abs(oa - h["accuracy"]) <= 0.001 and abs(kp - h["kappa"]) <= 0.001
            print("route %s: %.4f %.4f, its log %s %s -> %s" % (log, oa, kp, h["accuracy"], h["kappa"], "ok" if ok else "MISMATCH"), flush=True)
            if not ok:
                sys.exit(2)


def score(maps, polys, pairs):
    """Every map on one polygon set: full scores and the 14 blocks resampled, every map on the same draw."""
    R = {k: B.rows(a, m, g, polys, len(SEVEN)) for k, (a, m, g) in maps.items()}
    hit = np.all([r.sum((1, 2)) > 0 for r in R.values()], axis=0)
    P = [p for p, h in zip(polys, hit) if h]
    R = {k: r[hit] for k, r in R.items()}
    blocks = sorted({p[2] for p in P})
    bi = np.array([blocks.index(p[2]) for p in P])
    RB = {k: np.array([R[k][bi == j].sum(0) for j in range(len(blocks))]) for k in R}
    full = {}
    for k, r in R.items():
        c = r.sum(0)
        oa, kp, ba = B.scores(c)
        rs = c.sum(1)
        full[k] = dict(accuracy=round(oa, 4), kappa=round(kp, 4), balanced=round(ba, 4),
                       producers=dict(zip(SEVEN, [round(float(c[i, i] / rs[i]), 4) if rs[i] else None for i in range(len(c))])))
    return dict(polygons=len(P), polygons_without_pixels=int((~hit).sum()), blocks=blocks, full=full,
                block_bootstrap=B.boot(blocks, RB, list(R), pairs, B.NBOOT, B.SEED),
                by_block={b: {k: round(B.scores(RB[k][j])[0], 4) for k in R} for j, b in enumerate(blocks)}), R, hit


def report():
    route()
    a3 = np.load(os.path.join(HERE, ARR % "v3"), mmap_mode="r")
    shape, g = a3.shape, B.grid(a3.shape)
    res = dict(script="make_v3_extras.py", when=time.strftime("%Y-%m-%d %H:%M"), boot=B.NBOOT, seed=B.SEED)
    res["plan"] = json.load(open(PLAN, encoding="utf-8"))
    have = lambda f: len(glob.glob(os.path.join(f, "x5c_block_*.tif"))) > 0
    win = lambda run, mode=False: window_array(os.path.join(WORK, "classified", run), shape, mode)
    pack = lambda a: (a, a != 255, g)

    if have(os.path.join(WORK, "classified", "base")):
        base = win("base")
        if "--plant" in sys.argv:
            base = np.roll(base, shape[1] // 2, axis=1)
        both = (base != 255) & (a3 != 255)
        res["base_agrees_with_published"] = round(float((base[both] == a3[both]).mean()), 4)
        print("base against the published U-Net: %.4f of %d pixels" % (res["base_agrees_with_published"], both.sum()), flush=True)
        if res["base_agrees_with_published"] < 0.85:
            sys.exit(2)
        maps = {"base": pack(base), "unet_v3": published(ARR % "v3"), "unet_v2": published(ARR % "v2")}
        for run in ("noth", "cut", "add"):
            if have(os.path.join(WORK, "classified", run)):
                maps[run] = pack(win(run))
        pairs = [p for p in PAIRS_B if p[0] in maps and p[1] in maps]
        for name, f in (("v2_polygons", V2_TEST), ("v3_polygons", V3_TEST)):
            res[name], _, _ = score(maps, B.polys(f), pairs)
            print(name, json.dumps(res[name]["full"], ensure_ascii=False)[:900], flush=True)
            f = res[name]["full"]
            gaps = [abs(f["base"][m] - f["unet_v3"][m]) for m in ("accuracy", "kappa")]
            if max(gaps) > 0.005:
                print("base is not the published model read the same way:", gaps, flush=True)
                sys.exit(2)

    for run in SEEDS:
        if not (have(os.path.join(WORK, "classified", run)) and have(os.path.join(WORK, "classified", run + "_svm"))):
            continue
        polys = B.polys(fc(run, "test"))
        maps = {"unet": pack(win(run)), "svm": pack(win(run + "_svm", True)), "near": B.load("near", None, None, fc(run, "train"))}
        res[run], _, _ = score(maps, polys, PAIRS_F)
        print(run, json.dumps(res[run]["full"], ensure_ascii=False)[:900], flush=True)
    res["predictions"] = judge(res)
    print(res["predictions"])
    p = os.path.join(HERE, "logs", "v3_extras.json")
    json.dump(res, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("->", p)


def judge(res):
    v = {}
    has0 = lambda ci: ci[0] <= 0 <= ci[1]
    above = lambda ci: ci[0] > 0
    for run, tag in (("fresh", "F"), ("fresh2", "F6.")):
        if run in res:
            f, b = res[run]["full"]["unet"], res[run]["block_bootstrap"]
            v[tag + "1"] = 0.70 <= f["accuracy"] <= 0.92
            v[tag + "2"] = 0.60 <= f["balanced"] <= 0.85
            v[tag + "3"] = above(b["unet-svm"]["accuracy_ci95"])
            v[tag + "4"] = has0(b["svm-near"]["accuracy_ci95"])
            v[tag + "5"] = above(b["unet-near"]["accuracy_ci95"])
    if "v2_polygons" in res:
        s2, s3 = res["v2_polygons"], res["v3_polygons"]
        if "noth" in s2["full"]:
            v["T1"] = all(abs(s["full"]["noth"]["accuracy"] - s["full"]["base"]["accuracy"]) <= 0.03 for s in (s2, s3))
            v["T2"] = all(has0(s["block_bootstrap"]["base-noth"]["accuracy_ci95"]) for s in (s2, s3))
        f = s2["full"]
        if "cut" in f:
            v["C1"] = f["cut"]["balanced"] > 0.569
        if "add" in f:
            v["C2"] = f["add"]["balanced"] > 0.569
        if "cut" in f and "add" in f:
            v["C3"] = f["add"]["balanced"] > f["cut"]["balanced"]
            v["C4"] = max(f["add"]["balanced"], f["cut"]["balanced"]) < f["base"]["balanced"]
    return {p: "held" if x else "NOT held" for p, x in v.items()}


def main():
    if "--plan" in sys.argv:
        return plan()
    if "--report" in sys.argv:
        return report()
    run, step = sys.argv[sys.argv.index("--run") + 1], sys.argv[sys.argv.index("--step") + 1]
    assert run in TAGS, run
    os.makedirs(OUT, exist_ok=True)
    if step in ("export", "train"):
        sys.argv += ["--out", EXPORT, "--data", EXPORT]
        wire(run)
        D.export() if step == "export" else D.train()
    elif step == "classify":
        classify(run)
    elif step == "svm-train":
        svm_train(run)
    elif step == "svm-classify":
        svm_classify(run)
    else:
        sys.exit("unknown step " + step)


if __name__ == "__main__":
    main()
