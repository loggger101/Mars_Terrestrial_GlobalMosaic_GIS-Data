# -*- coding: utf-8 -*-
r"""X5: train an object-detection model on the training-split chips and score it on the held-out polygons
(q25 / q26 answered 2026-10-09: yes, boxes; KB §50, §51). ArcGIS Python, on the desktop.

    python make_dl_model.py --score-selftest          the scorer on synthetic detections (runs anywhere)
    python make_dl_model.py --train [--epochs 20] [--model RETINANET]
    python make_dl_model.py --detect                  detections over the held-out polygons
    python make_dl_model.py --score <detections fc>   the held-out score of any detection layer

Refuses --train / --detect unless desktop_check.py's log for this machine says X5 is ready (deep-learning
libraries, CUDA, the training-split export intact). Training reads ONLY
LabeledObjects\global60_svm_stack_200m_train\ (329 training polygons, §50.2): the all-labels export holds
the held-out polygons and would make the score meaningless.

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
import os, sys, json, time, socket, shutil, random
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import arcpy
import grid60 as G

STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
TRAIN = on_drive(r"Mars Project\LabeledObjects\global60_svm_stack_200m_train")
TEST = os.path.join(GDB, "Landform_TrainingSamples_terrain_60_test")
MODELS = on_drive(r"Mars Project\DLModels")
CHECK = os.path.join(HERE, "logs", "desktop_check_%s.json" % socket.gethostname())
OUT = os.path.join(HERE, "logs", "dl_heldout_score.json")
NAMES = {1: "Crater", 2: "steep/windy hills", 3: "lava tube", 4: "Normal Ground"}


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
    for d, c in dets:
        cen = d.centroid
        pt = (cen.X, cen.Y, cen.X, cen.Y)
        hit = next((v for (g, v), pb in zip(polys, pbox) if meet(pt, pb)
                    and g.contains(arcpy.PointGeometry(cen, sr))), None)
        if hit is None:
            continue
        prec[c][1] += 1; prec[c][0] += hit == c
    f = lambda a: a[0] / a[1] if a[1] else None
    return {"recall": {NAMES[k]: f(v) for k, v in rec.items()}, "recall_n": {NAMES[k]: v[1] for k, v in rec.items()},
            "precision": {NAMES[k]: f(v) for k, v in prec.items()}, "precision_n": {NAMES[k]: v[1] for k, v in prec.items()},
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


def train():
    ready()
    marker = open(os.path.join(TRAIN, "MADE_BY_make_global60_dl_export.txt")).read()
    assert "_60_train" in marker, "the export is not the training split"
    model = arg("--model", "RETINANET")
    out = os.path.join(MODELS, "global60_%s_%s" % (model.lower(), time.strftime("%Y%m%d")))
    os.makedirs(MODELS, exist_ok=True)
    t = time.time()
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.ia.TrainDeepLearningModel(in_folder=TRAIN, out_folder=out, max_epochs=arg("--epochs", 20),
                                    model_type=model, batch_size=arg("--batch", 8), validation_percentage=10,
                                    stop_training="STOP_TRAINING", freeze="FREEZE_MODEL", chip_size=256)
    print(arcpy.GetMessages())
    print("trained in %.0f s -> %s" % (time.time() - t, out))


def detect():
    ready()
    model = arg("--emd", "")
    assert model.endswith(".emd") and os.path.exists(model), "--emd <trained model .emd>"
    stamp = time.strftime("%Y%m%d")                         # the start's date, though the run may pass midnight
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.env.processorType = "GPU"
    arcpy.env.overwriteOutput = True
    sr = arcpy.Describe(STACK).spatialReference
    # One window per held-out 15° block (its polygons' extent + 25 km), no mask. A geographic mask (the buffer of
    # the test class, degrees) made the tool fail with ERROR 000599, outside the geometry domain, however the
    # output was written; the same buffer projected to the stack's SR stalled for 17 min on one 300 km window
    # that runs in 147 s without it (2026-10-19, KB §66.2). Each window keeps the boxes that touch its own
    # polygons' extent, so the windows' 25 km overlaps are not counted twice.
    blocks = {}
    with arcpy.da.SearchCursor(TEST, ["SHAPE@"]) as c:          # native geographic: 15° blocks by centroid
        for (g,) in c:
            k = (int(g.centroid.X // 15) * 15, int(g.centroid.Y // 15) * 15)
            e = g.projectAs(sr).extent
            b = blocks.get(k, (e.XMin, e.YMin, e.XMax, e.YMax))
            blocks[k] = (min(b[0], e.XMin), min(b[1], e.YMin), max(b[2], e.XMax), max(b[3], e.YMax))
    outdir = arg("--outdir", r"C:\MarsScratch\x5")      # internal disk first (KB §36.4)
    os.makedirs(outdir, exist_ok=True)
    kept = []
    for i, (k, core) in enumerate(sorted(blocks.items())):
        part = os.path.join(outdir, "dl_det_block_%+04d_%+03d.shp" % k)
        if not arcpy.Exists(part):                          # rerunnable: finished windows are kept
            arcpy.env.extent = "%f %f %f %f" % (core[0] - 25e3, core[1] - 25e3, core[2] + 25e3, core[3] + 25e3)
            t = time.time()
            arcpy.ia.DetectObjectsUsingDeepLearning(STACK, part, model, "padding 64;threshold 0.3;batch_size 8",
                                                    "NMS", "Confidence", "Class", 0, "PROCESS_AS_MOSAICKED_IMAGE")
            print("block %2d/%d lon %4d lat %4d: %6s boxes in %4.0f s" % (
                i + 1, len(blocks), k[0], k[1], arcpy.management.GetCount(part)[0], time.time() - t), flush=True)
        core_poly = arcpy.Extent(*core).polygon
        with arcpy.da.SearchCursor(part, ["SHAPE@", "Class", "Confidence"]) as c:
            kept += [r for r in c if not r[0].disjoint(core_poly)]
    arcpy.env.extent = None
    out = os.path.join(outdir, "dl_detections_heldout_%s.shp" % stamp)
    arcpy.management.CreateFeatureclass(outdir, os.path.basename(out), "POLYGON", spatial_reference=sr)
    arcpy.management.AddField(out, "Class", "TEXT", field_length=32)
    arcpy.management.AddField(out, "Confidence", "DOUBLE")
    with arcpy.da.InsertCursor(out, ["SHAPE@", "Class", "Confidence"]) as c:
        for r in kept:
            c.insertRow(r)
    print("detections ->", out, len(kept))


def score_layer(fc):
    sr = arcpy.Describe(fc).spatialReference
    flds = [f.name for f in arcpy.ListFields(fc)]
    cls = "Class" if "Class" in flds else "Classvalue"
    with arcpy.da.SearchCursor(fc, ["SHAPE@", cls]) as c:
        dets = [(g, int(v) if str(v).isdigit() else {n: k for k, n in NAMES.items()}.get(v)) for g, v in c]
    s = score([d for d in dets if d[1]], sr)
    s.update(layer=fc, scored=time.strftime("%Y-%m-%d %H:%M"))
    json.dump(s, open(OUT, "w"), indent=1)
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    if "--score-selftest" in sys.argv:
        score_selftest()
    elif "--train" in sys.argv:
        train()
    elif "--detect" in sys.argv:
        detect()
    elif "--score" in sys.argv:
        score_layer(sys.argv[sys.argv.index("--score") + 1])
    else:
        print(__doc__)
