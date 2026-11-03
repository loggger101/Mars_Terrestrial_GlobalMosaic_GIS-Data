r"""P11 (NEXT-STEPS §13): do Pro's trained classifiers repeat exactly?

Pro's TrainSupportVectorMachineClassifier and TrainRandomTreesClassifier take `max_samples_per_class` and no seed
(their parameter lists, read with arcpy.Usage 2026-11-02); the only random-number setting is the
`randomGenerator` environment ("0 ACM599"). Whether a retrain of the published SVM reproduces it has never been
tested. This test does it at small scale: one 15° block of the ±60° stack is clipped to internal disk, and on that
block's four-class training polygons (only those, so classes exceed 1000 pixels and the sample is a real draw):
  svm_a, svm_b  TrainSupportVectorMachineClassifier, max 1000 per class, identical inputs
  svm_r         the same with arcpy.env.randomGenerator = "1 ACM599"
  rt_a, rt_b    TrainRandomTreesClassifier, 50 trees, depth 30, max 1000 per class, identical inputs
Each .ecd is compared as text (and as parsed JSON with any time fields dropped); each is applied with
ClassifyRaster to the clipped block, and the class rasters are compared pixel by pixel.

Predictions, written before the first run (2026-11-02):
  P1  svm_a and svm_b classify every pixel identically (Pro samples with a fixed internal seed).
  P2  rt_a and rt_b classify every pixel identically.
  P3  svm_r classifies identically to svm_a (the randomGenerator environment is not honoured by the trainer).

Reads the stack (one 15° window, ~140 MB) and the gdb; writes only to %LOCALAPPDATA%\Temp\mars_scratch\p11 and
logs\pro_repeatability.json.

    "<ArcGIS python>" -u test_pro_repeatability.py
"""
import os, sys, json, time, shutil, collections
import numpy as np
from osgeo import gdal
import arcpy
from paths import on_drive, machine
import grid60 as G
import labelsets as L

HERE = os.path.dirname(os.path.abspath(__file__))
GDB = on_drive(r"Mars Project\Mars Project.gdb")
TRAIN = os.path.join(GDB, L.TRAIN)
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
SCR = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mars_scratch", "p11")
OUT = os.path.join(HERE, "logs", "pro_repeatability.json")
BLOCK, CELL, MAXS = 15.0, 200.0, 1000


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def pick_block():
    """The 15° block whose training polygons give the most classes over 2 x MAXS pixels (then the largest
    smallest-class count), so each class's sample of MAXS is a draw from many more pixels."""
    sr_eq = arcpy.Describe(STACK).spatialReference
    area = collections.defaultdict(lambda: collections.Counter())
    with arcpy.da.SearchCursor(TRAIN, ["SHAPE@XY", "SHAPE@", "Classvalue"]) as cur:
        for (x, y), shp, v in cur:
            b = (int(np.floor(x / BLOCK)), int(np.floor(y / BLOCK)))
            area[b][v] += shp.projectAs(sr_eq).area / CELL ** 2
    def key(b):
        big = [n for n in area[b].values() if n > 2 * MAXS]
        return (len(big), min(big) if big else 0)
    best = max(area, key=key)
    return best, {int(k): int(n) for k, n in sorted(area[best].items())}


def ecd_text(p):
    return open(p, encoding="utf-8", errors="replace").read()


def ecd_norm(p):
    """The .ecd as JSON with any key naming a time or date dropped, recursively."""
    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if not any(s in k.lower() for s in ("time", "date"))}
        if isinstance(o, list):
            return [strip(v) for v in o]
        return o
    try:
        return strip(json.loads(ecd_text(p)))
    except ValueError:
        return None


def main():
    t0 = time.time()
    shutil.rmtree(SCR, ignore_errors=True)
    os.makedirs(SCR)
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("ImageAnalyst")
    (bx, by), px = pick_block()
    log("block %d_%d, training pixels per class at 200 m:" % (bx, by), px)

    # the block's polygons, and the stack clipped to their extent plus 10 km
    arcpy.management.CreateFileGDB(SCR, "p11.gdb")
    fc = os.path.join(SCR, "p11.gdb", "train_block")
    lyr = arcpy.management.MakeFeatureLayer(TRAIN, "tr").getOutput(0)
    oids = []
    with arcpy.da.SearchCursor(TRAIN, ["OID@", "SHAPE@XY"]) as cur:
        for oid, (x, y) in cur:
            if (int(np.floor(x / BLOCK)), int(np.floor(y / BLOCK))) == (bx, by):
                oids.append(oid)
    oidf = arcpy.Describe(TRAIN).OIDFieldName
    arcpy.management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "%s IN (%s)" % (oidf, ",".join(map(str, oids))))
    arcpy.management.Project(lyr, fc, arcpy.Describe(STACK).spatialReference)
    e = arcpy.Describe(fc).extent
    clip = os.path.join(SCR, "stack_block.tif")
    gdal.Translate(clip, STACK, projWin=[e.XMin - 1e4, e.YMax + 1e4, e.XMax + 1e4, e.YMin - 1e4],
                   creationOptions=["TILED=YES", "COMPRESS=LZW"])
    ds = gdal.Open(clip)
    log("%d polygons; clip %d x %d x %d" % (len(oids), ds.RasterXSize, ds.RasterYSize, ds.RasterCount))
    ds = None

    runs = [("svm_a", "svm", None), ("svm_b", "svm", None), ("svm_r", "svm", "1 ACM599"),
            ("rt_a", "rt", None), ("rt_b", "rt", None)]
    res = dict(script="test_pro_repeatability.py", when=time.strftime("%Y-%m-%d %H:%M"),
               host=machine(), pro=arcpy.GetInstallInfo()["Version"],
               block="%d_%d" % (bx, by), polygons=len(oids), train_px_per_class=px,
               max_samples_per_class=MAXS, runs={}, compare={})
    maps = {}
    for name, kind, rg in runs:
        ecd = os.path.join(SCR, name + ".ecd")
        t = time.time()
        with arcpy.EnvManager(randomGenerator=rg or "0 ACM599"):
            if kind == "svm":
                arcpy.ia.TrainSupportVectorMachineClassifier(clip, fc, ecd, max_samples_per_class=MAXS)
            else:
                arcpy.ia.TrainRandomTreesClassifier(clip, fc, ecd, None, 50, 30, MAXS)
        tt = time.time() - t
        out = os.path.join(SCR, name + ".tif")
        t = time.time()
        arcpy.ia.ClassifyRaster(clip, ecd).save(out)
        tc = time.time() - t
        maps[name] = gdal.Open(out).ReadAsArray()
        res["runs"][name] = dict(trainer=kind, randomGenerator=rg or "0 ACM599", train_s=round(tt, 1),
                                 classify_s=round(tc, 1), ecd_bytes=os.path.getsize(ecd))
        log("%s: trained %.0f s, classified %.0f s" % (name, tt, tc))

    for a, b in (("svm_a", "svm_b"), ("svm_a", "svm_r"), ("rt_a", "rt_b"), ("svm_a", "rt_a")):
        ta, tb = ecd_text(os.path.join(SCR, a + ".ecd")), ecd_text(os.path.join(SCR, b + ".ecd"))
        ja, jb = ecd_norm(os.path.join(SCR, a + ".ecd")), ecd_norm(os.path.join(SCR, b + ".ecd"))
        diff = maps[a] != maps[b]
        res["compare"]["%s_vs_%s" % (a, b)] = dict(
            ecd_text_identical=ta == tb, ecd_json_identical_without_times=(ja == jb) if ja is not None else None,
            pixels=int(diff.size), pixels_different=int(diff.sum()), share_different=float(diff.mean()))
        log("%s vs %s: ecd text %s, json %s, %d of %d pixels differ"
            % (a, b, ta == tb, ja == jb if ja is not None else "n/a", diff.sum(), diff.size))

    c = res["compare"]
    res["predictions"] = {
        "P1 svm_a = svm_b": "held" if c["svm_a_vs_svm_b"]["pixels_different"] == 0 else "not held",
        "P2 rt_a = rt_b": "held" if c["rt_a_vs_rt_b"]["pixels_different"] == 0 else "not held",
        "P3 svm_r = svm_a": "held" if c["svm_a_vs_svm_r"]["pixels_different"] == 0 else "not held"}
    # the check that the comparison can fail: two different classifiers must differ somewhere
    res["check_svm_vs_rt_differs"] = c["svm_a_vs_rt_a"]["pixels_different"] > 0
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    log("predictions:", res["predictions"], "| check (SVM vs RT differ):", res["check_svm_vs_rt_differs"])
    log("wrote", OUT)


if __name__ == "__main__":
    main()
