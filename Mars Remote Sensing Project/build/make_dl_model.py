# -*- coding: utf-8 -*-
r"""X5: train an object-detection model on the training-split chips and score it on the held-out polygons
(q25 / q26 answered 2026-10-09: yes, boxes; KB §50, §51). ArcGIS Python, on the desktop.

    python make_dl_model.py --score-selftest          the scorer on synthetic detections (runs anywhere)
    python make_dl_model.py --prepare [--out C:\MarsScratch\x5b]
                                                      cleaned copies of the training-split exports (below)
    python make_dl_model.py --train [--tag x5b] [--data <folder;folder>] [--epochs 30] [--model RETINANET]
                                    [--freeze] [--early-stop] [--batch 8]
    python make_dl_model.py --detect --emd <model .emd> [--threshold 0.3] [--outdir <folder>]
                                                      detections over the held-out polygons
    python make_dl_model.py --score <detections fc> [--out <json>]
                                                      the held-out score of any detection layer

X5 (2026-10-19) was --train with the backbone frozen and early stopping (now --freeze --early-stop --epochs 20).
The defaults since 2026-10-20 (X5b, KB §66.5): the backbone UNFROZEN (four of the seven bands are not RGB, and
the frozen ImageNet layers could not adapt to them), early stopping OFF (every epoch runs; arcgis.learn still
keeps the epoch with the lowest validation loss), 30 epochs, the model written to internal disk and copied to
DLModels when done, the run's settings and the tool's messages saved beside it. --prepare drops edge slivers and
--data trains on several folders (the cleaned main export plus the rare-class chips of
make_global60_dl_export.py --rare). --detect writes each model's windows to its own folder (X5's
C:\MarsScratch\x5 windows would otherwise be reused) and copies the merged layer beside the model. --score scores
at several confidence cutoffs from one layer, the primary one 0.3 as for X5, and refuses to overwrite another
layer's score file.

Refuses --train / --detect unless desktop_check.py's log for this machine says X5 is ready (deep-learning
libraries, CUDA, the training-split export intact). Training reads ONLY
LabeledObjects\global60_svm_stack_200m_train\ (329 training polygons, §50.2): the all-labels export holds
the held-out polygons and would make the score meaningless.

X5b's verdict rule, written before it ran (§47 practice; KB §66.5), at the primary cutoff 0.3:
  X5b improves on X5 if (a) Crater recall > 41.9 % with Crater precision >= 71.1 % (X5's numbers and the
  one-class rate), (b) Normal Ground recall > 22.7 % with its precision >= 20.9 %, and (c) at least one rare
  class (steep/windy hills, lava tube) is named in a held-out polygon of its own class at least once.
  All three: improved. (a) and (b) without (c): better on the common classes only. Otherwise: not improved.
  The other cutoffs are reported, never used to pick a winner (choosing on the held-out polygons would make
  them a validation set).

STATUS: --train ran on the desktop 2026-10-19 (RETINANET takes the 7 bands; 25 min, early-stopped; §66.1).
--detect runs one window per held-out 15° block, no mask, into C:\MarsScratch\x5\ (--outdir); it and --score
ran 2026-10-19 (23 min; §66.2).
Whether other detection models accept 7-band input is not verified [?]; --model chooses. --score and
--score-selftest are tested.

The score, at polygon level (boxes cannot score per pixel on area classes, §31.4):
  recall per class      share of held-out polygons whose own class's detection boxes cover >= 50 % of them
  precision per class   of the detections whose centre falls inside a held-out polygon, the share whose
                        class matches that polygon's; detections on unlabelled ground are not counted
Written to build\logs\dl_heldout_score.json, beside the SVM's held-out per-pixel numbers (§31.3, §32.2)
for context, not as a like-for-like comparison.
"""
import os, sys, json, time, socket, shutil, random, collections
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import arcpy
import grid60 as G
import labelsets as L

STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
TRAIN = on_drive(r"Mars Project\LabeledObjects\global60_svm_stack_200m_train")
TEST = os.path.join(GDB, L.TEST)                     # labelsets.py: --labels v2 for make_dl_pixels.py's v2 run
MODELS = on_drive(r"Mars Project\DLModels")
CHECK = os.path.join(HERE, "logs", "desktop_check_%s.json" % socket.gethostname())
OUT = os.path.join(HERE, "logs", "dl_heldout_score.json")      # X5's; later models get their own (--out)
NAMES = {1: "Crater", 2: "steep/windy hills", 3: "lava tube", 4: "Normal Ground"}
MARK = "MADE_BY_make_global60_dl_export.txt"
WORK = r"C:\MarsScratch\x5b"                                     # internal disk first (KB §36.4)
CUTOFFS = (0.1, 0.2, 0.3, 0.4, 0.5)
PRIMARY = 0.3
SLIVER = 16      # px; a box this thin that touches the chip edge on its thin side is a polygon's clipped edge


def arg(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def ready():
    if not os.path.exists(CHECK) or not json.load(open(CHECK)).get("x5_ready"):
        sys.exit("REFUSING: run desktop_check.py on this machine first; X5 is not ready (%s)" % CHECK)


def heldout(sr):
    with arcpy.da.SearchCursor(TEST, ["SHAPE@", "Classvalue"], spatial_reference=sr) as c:
        return [(g, int(v)) for g, v in c]


def score(dets, sr, polys=None):
    """dets: [(polygon geometry, class value)] in sr. Returns the polygon-level score."""
    polys = polys if polys is not None else heldout(sr)
    # extent prefilters (pure speed-ups: a box whose extent misses a polygon's cannot touch it)
    box = lambda g: (g.extent.XMin, g.extent.YMin, g.extent.XMax, g.extent.YMax)
    meet = lambda a, b: a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]
    dbox = [box(d) for d, c in dets]
    pbox = [box(g) for g, v in polys]
    rec = {k: [0, 0] for k in NAMES}
    for (g, v), pb in zip(polys, pbox):
        own = [d for (d, c), db in zip(dets, dbox) if c == v and meet(db, pb) and not d.disjoint(g)]
        cover = 0.0
        if own:
            u = own[0]
            for d in own[1:]:
                u = u.union(d)
            cover = u.intersect(g, 4).area / g.area
        rec[v][1] += 1; rec[v][0] += cover >= 0.5
    prec = {k: [0, 0] for k in NAMES}
    inside = collections.Counter()      # detections centred in a polygon, by the polygon's class
    for d, c in dets:
        cen = d.centroid
        pt = (cen.X, cen.Y, cen.X, cen.Y)
        hit = next((v for (g, v), pb in zip(polys, pbox) if meet(pt, pb)
                    and g.contains(arcpy.PointGeometry(cen, sr))), None)
        if hit is None:
            continue
        prec[c][1] += 1; prec[c][0] += hit == c; inside[hit] += 1
    f = lambda a: a[0] / a[1] if a[1] else None
    n_in = sum(inside.values())
    return {"recall": {NAMES[k]: f(v) for k, v in rec.items()}, "recall_n": {NAMES[k]: v[1] for k, v in rec.items()},
            "recall_hits": {NAMES[k]: v[0] for k, v in rec.items()},
            "precision": {NAMES[k]: f(v) for k, v in prec.items()}, "precision_n": {NAMES[k]: v[1] for k, v in prec.items()},
            "precision_hits": {NAMES[k]: v[0] for k, v in prec.items()},
            # the precision an all-one-class labeller would get on the same in-polygon detections
            "one_class_rate": {NAMES[k]: (inside[k] / n_in if n_in else None) for k in NAMES},
            "detections": len(dets)}


def score_selftest():
    """Perfect boxes (each polygon's own envelope, true class) must score recall 1 everywhere; the same
    boxes with classes rotated (1->2->3->4->1) must score recall 0 and precision 0."""
    sr = arcpy.Describe(TEST).spatialReference
    polys = heldout(sr)
    env = lambda g: arcpy.Polygon(arcpy.Array([g.extent.lowerLeft, g.extent.upperLeft, g.extent.upperRight,
                                               g.extent.lowerRight]), sr)
    perfect = score([(env(g), v) for g, v in polys], sr, polys)
    rotated = score([(env(g), v % 4 + 1) for g, v in polys], sr, polys)
    checks = {"perfect: recall 1 for every class": all(r == 1 for r in perfect["recall"].values()),
              "perfect: precision 1 where counted": all(p in (1, None) for p in perfect["precision"].values()),
              "rotated: recall 0 for every class": all(r == 0 for r in rotated["recall"].values()),
              "rotated: precision 0 where counted": all(p in (0, None) for p in rotated["precision"].values())}
    for k, ok in checks.items():
        print("%-4s %s" % ("ok" if ok else "FAIL", k))
    print("perfect:", perfect, "\nrotated:", rotated)
    sys.exit(0 if all(checks.values()) else 1)


def training_split(folder):
    marker = open(os.path.join(folder, MARK)).read()
    assert "_60_train" in marker, "%s is not from the training split" % folder
    return marker


def prepare():
    """Cleaned copies, on internal disk, of the training-split export and of the rare-class chips: boxes thinner
    than SLIVER px that touch the chip edge on their thin side are dropped (a polygon's clipped edge, not an
    object), and so are chips left with no box. Images are copied, never changed."""
    out = arg("--out", WORK)
    summary = {"rule": "drop boxes < %d px thin touching the chip edge on that side; drop chips left empty" % SLIVER}
    for name, src in (("main", TRAIN), ("rare", os.path.join(out, "export_rare"))):
        marker = training_split(src)
        dst = os.path.join(out, name + "_clean")
        if os.path.exists(dst):
            assert os.path.exists(os.path.join(dst, MARK)), "REFUSING: %s was not made here" % dst
            shutil.rmtree(dst)
        for sub in ("images", "labels"):
            os.makedirs(os.path.join(dst, sub))
        s = {"chips_in": 0, "chips_out": 0, "boxes_in": collections.Counter(), "slivers": collections.Counter(),
             "boxes_out": collections.Counter()}
        kept = []
        for line in open(os.path.join(src, "map.txt")):
            if not line.strip():
                continue
            img, lab = line.split()
            s["chips_in"] += 1
            tree = ET.parse(os.path.join(src, lab))
            root = tree.getroot()
            for o in root.findall("object"):
                c = NAMES[int(o.find("name").text)]
                b = o.find("bndbox")
                x0, y0, x1, y1 = [float(b.find(k).text) for k in ("xmin", "ymin", "xmax", "ymax")]
                s["boxes_in"][c] += 1
                if (y1 - y0 < SLIVER and (y0 <= 0.5 or y1 >= 255.5)) or (x1 - x0 < SLIVER and (x0 <= 0.5 or x1 >= 255.5)):
                    root.remove(o); s["slivers"][c] += 1
                else:
                    s["boxes_out"][c] += 1
            if not root.findall("object"):
                continue
            tree.write(os.path.join(dst, lab))
            for ext in (".tif", ".tfw"):
                p = os.path.splitext(img)[0] + ext
                shutil.copy2(os.path.join(src, p), os.path.join(dst, p))
            kept.append(line)
            s["chips_out"] += 1
        open(os.path.join(dst, "map.txt"), "w").writelines(kept)
        for f in ("esri_model_definition.emd", "esri_accumulated_stats.json", "stats.txt"):
            shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
        open(os.path.join(dst, MARK), "w").write(marker + "cleaned by make_dl_model.py --prepare from %s (%s)\n"
                                                 % (src, summary["rule"]))
        summary[name] = s
        print(name, json.dumps(s))
    json.dump(summary, open(os.path.join(out, "prepare_summary.json"), "w"), indent=1)
    json.dump(summary, open(os.path.join(HERE, "logs", "dl_prepare_x5b.json"), "w"), indent=1)


def train():
    ready()
    folders = arg("--data", "").split(";") if "--data" in sys.argv else [TRAIN]
    for f in folders:
        training_split(f)
    model = arg("--model", "RETINANET")
    tag = arg("--tag", "")
    name = "global60_%s%s_%s" % (model.lower(), "_" + tag if tag else "", time.strftime("%Y%m%d"))
    out = os.path.join(arg("--workdir", os.path.join(WORK, "models")), name)
    final = os.path.join(MODELS, name)
    assert not os.path.exists(out) and not os.path.exists(final), "REFUSING: %s already exists" % name
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cfg = dict(in_folder=folders, out_folder=out, max_epochs=arg("--epochs", 30), model_type=model,
               batch_size=arg("--batch", 8), validation_percentage=10,
               stop_training="STOP_TRAINING" if "--early-stop" in sys.argv else "CONTINUE_TRAINING",
               freeze="FREEZE_MODEL" if "--freeze" in sys.argv else "UNFREEZE_MODEL",
               chip_size=256, monitor="VALID_LOSS")
    print("training", json.dumps(cfg), flush=True)
    t = time.time()
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.ia.TrainDeepLearningModel(**cfg)
    msgs = arcpy.GetMessages()
    print(msgs)
    secs = time.time() - t
    open(os.path.join(out, "training_messages.txt"), "w", encoding="utf-8").write(msgs)
    json.dump(dict(cfg, host=socket.gethostname(), seconds=round(secs), finished=time.strftime("%Y-%m-%d %H:%M"),
                   script="make_dl_model.py"), open(os.path.join(out, "run_config.json"), "w"), indent=1)
    shutil.copytree(out, final)
    print("trained in %.0f s -> %s, copied to %s" % (secs, out, final))


def heldout_blocks(sr):
    """{(lon, lat) of the 15° block: (xmin, ymin, xmax, ymax) of its held-out polygons, in sr}; blocks by each
    polygon's centroid in the class's native geographic SR. Shared with make_dl_pixels.py."""
    blocks = {}
    with arcpy.da.SearchCursor(TEST, ["SHAPE@"]) as c:
        for (g,) in c:
            k = (int(g.centroid.X // 15) * 15, int(g.centroid.Y // 15) * 15)
            e = g.projectAs(sr).extent
            b = blocks.get(k, (e.XMin, e.YMin, e.XMax, e.YMax))
            blocks[k] = (min(b[0], e.XMin), min(b[1], e.YMin), max(b[2], e.XMax), max(b[3], e.YMax))
    return blocks


def detect():
    ready()
    model = arg("--emd", "")
    assert model.endswith(".emd") and os.path.exists(model), "--emd <trained model .emd>"
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.env.processorType = "GPU"
    arcpy.env.overwriteOutput = True
    sr = arcpy.Describe(STACK).spatialReference
    # One window per held-out 15° block (its polygons' extent + 25 km), no mask. A geographic mask (the buffer of
    # the test class, degrees) made the tool fail with ERROR 000599, outside the geometry domain, however the
    # output was written; the same buffer projected to the stack's SR stalled for 17 min on one 300 km window
    # that runs in 147 s without it (2026-10-19, KB §66.2). Each window keeps the boxes that touch its own
    # polygons' extent, so the windows' 25 km overlaps are not counted twice.
    blocks = heldout_blocks(sr)
    # each model's own folder on internal disk (KB §36.4): finished windows are reused, so two models must never
    # share one (X5's ran in C:\MarsScratch\x5 itself)
    mname = os.path.basename(os.path.dirname(model))
    outdir = arg("--outdir", os.path.join(r"C:\MarsScratch\x5", mname))
    thr = arg("--threshold", PRIMARY)
    os.makedirs(outdir, exist_ok=True)
    print("detect", mname, "threshold", thr, "->", outdir, flush=True)
    kept = []
    for i, (k, core) in enumerate(sorted(blocks.items())):
        part = os.path.join(outdir, "dl_det_block_%+04d_%+03d.shp" % k)
        if not arcpy.Exists(part):                          # rerunnable: finished windows are kept
            arcpy.env.extent = "%f %f %f %f" % (core[0] - 25e3, core[1] - 25e3, core[2] + 25e3, core[3] + 25e3)
            t = time.time()
            arcpy.ia.DetectObjectsUsingDeepLearning(STACK, part, model, "padding 64;threshold %g;batch_size 8" % thr,
                                                    "NMS", "Confidence", "Class", 0, "PROCESS_AS_MOSAICKED_IMAGE")
            print("block %2d/%d lon %4d lat %4d: %6s boxes in %4.0f s" % (
                i + 1, len(blocks), k[0], k[1], arcpy.management.GetCount(part)[0], time.time() - t), flush=True)
        core_poly = arcpy.Extent(*core).polygon
        with arcpy.da.SearchCursor(part, ["SHAPE@", "Class", "Confidence"]) as c:
            kept += [r for r in c if not r[0].disjoint(core_poly)]
    arcpy.env.extent = None
    out = os.path.join(outdir, "dl_det_heldout_%s.shp" % mname)  # X5's was dl_detections_heldout_20261019
    arcpy.management.CreateFeatureclass(outdir, os.path.basename(out), "POLYGON", spatial_reference=sr)
    arcpy.management.AddField(out, "Class", "TEXT", field_length=32)
    arcpy.management.AddField(out, "Confidence", "DOUBLE")
    with arcpy.da.InsertCursor(out, ["SHAPE@", "Class", "Confidence"]) as c:
        for r in kept:
            c.insertRow(r)
    print("detections ->", out, len(kept))
    keep = os.path.join(os.path.dirname(model), "detections_heldout")      # one copy beside the model
    os.makedirs(keep, exist_ok=True)
    base = os.path.splitext(os.path.basename(out))[0]
    for f in os.listdir(outdir):
        if os.path.splitext(f)[0] == base:
            shutil.copy2(os.path.join(outdir, f), keep)
    print("copied ->", keep)


def score_layer(fc):
    sr = arcpy.Describe(fc).spatialReference
    flds = [f.name for f in arcpy.ListFields(fc)]
    cls = "Class" if "Class" in flds else "Classvalue"
    conf = ["Confidence"] if "Confidence" in flds else []
    with arcpy.da.SearchCursor(fc, ["SHAPE@", cls] + conf) as c:
        dets = [(r[0], int(r[1]) if str(r[1]).isdigit() else {n: k for k, n in NAMES.items()}.get(r[1]),
                 r[2] / 100.0 if conf else 1.0) for r in c]
    dets = [d for d in dets if d[1]]
    low = min((d[2] for d in dets), default=1.0)
    by = {}
    for cut in CUTOFFS:                          # a cutoff below the layer's own threshold would be the same layer
        if cut >= low - 0.005 or cut == PRIMARY:     # tolerance: a 0.1 layer's lowest box scores ~0.1003
            by["%.1f" % cut] = score([(g, v) for g, v, p in dets if p >= cut - 1e-9], sr)
            print("cutoff %.1f:" % cut, json.dumps({k: by["%.1f" % cut][k] for k in ("recall", "precision")}), flush=True)
    s = dict(by["%.1f" % PRIMARY], primary_cutoff=PRIMARY, by_cutoff=by)
    s.update(layer=fc, scored=time.strftime("%Y-%m-%d %H:%M"))
    out = arg("--out", OUT)
    if os.path.exists(out):                     # X5's file feeds layout 16: never overwrite another layer's score
        prev = os.path.basename(json.load(open(out)).get("layer", ""))
        assert prev == os.path.basename(fc), "REFUSING: %s holds the score of %s; pass --out" % (out, prev)
    json.dump(s, open(out, "w"), indent=1)
    print(json.dumps({k: s[k] for k in s if k != "by_cutoff"}, indent=1))
    print("->", out)


if __name__ == "__main__":
    if "--score-selftest" in sys.argv:
        score_selftest()
    elif "--prepare" in sys.argv:
        prepare()
    elif "--train" in sys.argv:
        train()
    elif "--detect" in sys.argv:
        detect()
    elif "--score" in sys.argv:
        score_layer(sys.argv[sys.argv.index("--score") + 1])
    else:
        print(__doc__)
