# -*- coding: utf-8 -*-
r"""The ±60° landform classification, redone on the corrected stack (KB §31).

  1. Analysis_Extent_60       the ±60° polygon every Mars map is clipped to (§16)
  2. a spatial train/test split of the 512 hand-drawn polygons, clipped to ±60°:
       Landform_TrainingSamples_terrain_60_train / _60_test
     Whole 15° x 15° blocks go to one side or the other, so a test polygon never sits beside
     a training polygon from the same patch of ground (the §27 rule).
  3. Train Support Vector Machine on the _train polygons over global60_svm_stack_200m.tif
  4. Classify Raster -> Z:\Mars Project\Global60\global60_landforms_svm_<cell>m.tif
     The model is trained on the 200 m stack either way. Classifying all of ±60° at 200 m is
     ~15 h on the laptop (smoke-timed, 14 µs/px), so the laptop run is --cell 400 (~4 h) and
     --cell 200 is a desktop job.
     The delivered map's pixel values are the class codes: 1 Crater, 2 steep/windy hills,
     3 lava tube, 4 Normal Ground, 255 no class (recoded after the mosaic, KB §36).

The hand-drawn class `Landform_TrainingSamples_terrain` is READ only. Every class this script writes
carries MappedBy = MARKER, and safe_to_replace() refuses to delete any class holding a row it
did not write (the §29.8 guard).

  python make_global60_classification.py --cell 400            all steps (laptop)
  python make_global60_classification.py --cell 200            all steps (desktop)
  python make_global60_classification.py --classify-only ...   reuse the split and the .ecd
  python make_global60_classification.py --smoke               steps 1-3, one 4096 px window
"""
import os, sys, time, ctypes
import numpy as np
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G

GDB = r"Z:\Mars Project\Mars Project.gdb"
HAND_LABELS = os.path.join(GDB, "Landform_TrainingSamples_terrain")
EXTENT = os.path.join(GDB, "Analysis_Extent_60")
TRAIN = os.path.join(GDB, "Landform_TrainingSamples_terrain_60_train")
TEST = os.path.join(GDB, "Landform_TrainingSamples_terrain_60_test")
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")
ECD = os.path.join(G.OUTDIR, "global60_landforms_svm.ecd")
CELL = int(sys.argv[sys.argv.index("--cell") + 1]) if "--cell" in sys.argv else 400
OUT = os.path.join(G.OUTDIR, "global60_landforms_svm_%dm.tif" % CELL)
MARKER = "make_global60_classification.py"
BLOCK_DEG, TEST_SHARE, SEED = 15.0, 0.3, 60
MARS = arcpy.SpatialReference(104905)                # GCS_Mars_2000_Sphere, the hand-drawn labels' CRS
arcpy.env.overwriteOutput = False


def keep_awake(on=True):
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | (0x00000001 if on else 0))


def safe_to_replace(fc):
    """True if fc is absent, empty, or every row is ours. Never deletes manual work."""
    if not arcpy.Exists(fc):
        return True
    if "MappedBy" not in [f.name for f in arcpy.ListFields(fc)]:
        return int(arcpy.management.GetCount(fc)[0]) == 0
    with arcpy.da.SearchCursor(fc, ["MappedBy"]) as cur:
        return all(r[0] == MARKER for r in cur)


def replace(fc):
    if arcpy.Exists(fc):
        if not safe_to_replace(fc):
            sys.exit("REFUSING: %s holds rows this script did not write. Nothing deleted." % fc)
        arcpy.management.Delete(fc)


def make_extent():
    replace(EXTENT)
    arcpy.management.CreateFeatureclass(GDB, os.path.basename(EXTENT), "POLYGON", spatial_reference=MARS)
    arcpy.management.AddField(EXTENT, "MappedBy", "TEXT", field_length=64)
    arcpy.management.AddField(EXTENT, "Note", "TEXT", field_length=200)
    lat = G.G100.lat_of(G.G100.oy)                   # the night mosaic's own edge, 60.0003°
    ring = ([(-180 + i, -lat) for i in range(0, 361)] + [(180, lat)] +
            [(180 - i, lat) for i in range(0, 361)] + [(-180, -lat)])
    poly = arcpy.Polygon(arcpy.Array([arcpy.Point(x, y) for x, y in ring]), MARS)
    with arcpy.da.InsertCursor(EXTENT, ["SHAPE@", "MappedBy", "Note"]) as cur:
        cur.insertRow([poly, MARKER, "±%.4f° latitude: the THEMIS night mosaic's extent (KB §16)" % lat])
    print("  %s  ±%.4f°" % (os.path.basename(EXTENT), lat))


def make_split():
    for fc in (TRAIN, TEST):
        replace(fc)
    tmp = "memory\\his60"
    if arcpy.Exists(tmp):
        arcpy.management.Delete(tmp)
    arcpy.analysis.Clip(HAND_LABELS, EXTENT, tmp)
    arcpy.management.AddField(tmp, "MappedBy", "TEXT", field_length=64)
    arcpy.management.AddField(tmp, "Split", "TEXT", field_length=8)
    arcpy.management.AddField(tmp, "Block", "TEXT", field_length=16)
    rows = []
    with arcpy.da.SearchCursor(tmp, ["OID@", "SHAPE@XY", "Classvalue"]) as cur:
        for oid, (x, y), v in cur:
            rows.append((oid, "%d_%d" % (np.floor(x / BLOCK_DEG), np.floor(y / BLOCK_DEG)), v))
    blocks = sorted(set(b for _, b, _ in rows))
    rng = np.random.default_rng(SEED)
    # draw until every class has test polygons and the test share is near TEST_SHARE
    for attempt in range(500):
        test = set(b for b in blocks if rng.random() < TEST_SHARE)
        cls_t = [sum(1 for _, b, v in rows if b in test and v == c) for c in (1, 2, 3, 4)]
        cls_a = [sum(1 for _, b, v in rows if v == c) for c in (1, 2, 3, 4)]
        if all(t >= max(5, 0.15 * a) and t <= 0.5 * a for t, a in zip(cls_t, cls_a)):
            break
    else:
        sys.exit("no acceptable block split found")
    split = {oid: ("test" if b in test else "train", b) for oid, b, _ in rows}
    with arcpy.da.UpdateCursor(tmp, ["OID@", "MappedBy", "Split", "Block"]) as cur:
        for r in cur:
            r[1] = MARKER; r[2], r[3] = split[r[0]]; cur.updateRow(r)
    arcpy.analysis.Select(tmp, TRAIN, "Split = 'train'")
    arcpy.analysis.Select(tmp, TEST, "Split = 'test'")
    arcpy.management.Delete(tmp)
    print("  %d blocks, %d to test (attempt %d)" % (len(blocks), len(test), attempt + 1))
    print("  test polygons per class (Crater, hills, lava tube, Normal):", cls_t, "of", cls_a)


def train():
    if os.path.exists(ECD):
        os.remove(ECD)
    t = time.time()
    arcpy.CheckOutExtension("ImageAnalyst")
    arcpy.ia.TrainSupportVectorMachineClassifier(STACK, TRAIN, ECD, max_samples_per_class=1000)
    print("  trained in %.0f s -> %s" % (time.time() - t, ECD))


def classify(out, extent=None, cell=200):
    t = time.time()
    arcpy.CheckOutExtension("ImageAnalyst")
    with arcpy.EnvManager(extent=extent, snapRaster=STACK, cellSize=cell,
                          parallelProcessingFactor="100%", compression="LZ77",
                          pyramid="PYRAMIDS -1 NEAREST", rasterStatistics="STATISTICS 8 8"):
        r = arcpy.ia.ClassifyRaster(STACK, ECD)
        if os.path.exists(out):
            arcpy.management.Delete(out)
        r.save(out)
    dt = time.time() - t
    print("  classified -> %s  in %.0f s" % (out, dt))
    return dt


SCRATCH = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mars_scratch")   # internal SSD (§2.2)
TILE = 16384                                     # G200 px per tile side: 21 tiles over ±60°
COLOURS = {"Crater": (255, 0, 0), "steep/windy hills": (28, 119, 85),
           "lava tube": (158, 25, 147), "Normal Ground": (81, 51, 13)}   # the RAT colours


def classify_tiled(out, cell, limit=None):
    """Classify ±60° tile by tile, then mosaic.

    One full-extent ClassifyRaster hands the job to LocalWorker processes and gives no sign of
    progress; tiles show progress and survive a sleep or a crash, because a finished tile is
    marked done and skipped on re-run. Every tile is snapped to one `cell` lattice from the grid's
    top-left corner, so the tiles mosaic without resampling.
    """
    from osgeo import gdal
    gdal.UseExceptions()
    tdir = os.path.join(SCRATCH, "cls_%dm_tiles" % cell)
    os.makedirs(tdir, exist_ok=True)
    tiles = list(G.G200.tiles(TILE))[:limit]
    t0 = time.time()
    files = []
    for k, (col, row, x0, y0, w, h) in enumerate(tiles):
        f = os.path.join(tdir, "t_r%02d_c%02d.tif" % (row, col))
        files.append(f)
        if os.path.exists(f + ".done"):
            continue
        left = G.G200.ox + x0 * G.G200.res
        top = G.G200.oy - y0 * G.G200.res
        wm = -(-w * G.G200.res // cell) * cell                 # widths rounded UP to whole cells
        hm = -(-h * G.G200.res // cell) * cell
        classify(f, arcpy.Extent(left, top - hm, left + wm, top), cell=cell)
        gt = gdal.Open(f).GetGeoTransform()
        assert abs(gt[1] - cell) < 1e-6 and abs((gt[0] - G.G200.ox) % cell) < 1e-6 \
            and abs((G.G200.oy - gt[3]) % cell) < 1e-6, "tile %s off the %d m lattice: %s" % (f, cell, gt)
        open(f + ".done", "w").write("ok")
        el = time.time() - t0
        print("   tile %2d/%d  r%d c%d  %s elapsed" % (k + 1, len(tiles), row, col,
                                                    time.strftime("%H:%M:%S", time.gmtime(el))), flush=True)

    print("  mosaic %d tiles -> %s" % (len(files), out))
    # ClassifyRaster writes pixel values 0..3; the mosaic is built as before, then recoded so
    # the delivered map's pixels ARE the class codes 1..4 (KB §36).
    final, out = out, out.replace(".tif", "_0based_tmp.tif")
    vrt = os.path.join(tdir, "mosaic.vrt")
    gdal.BuildVRT(vrt, files, srcNodata=255, VRTNodata=255)
    b = G.G200.bounds                                        # (xmin, ymin, xmax, ymax)
    hgt = -(-G.G200.ny * G.G200.res // cell) * cell          # whole cells: ny is odd at 200 m
    if os.path.exists(out):
        arcpy.management.Delete(out)
    gdal.Translate(out, vrt, projWin=[b[0], b[3], b[2], b[3] - hgt], noData=255,
                   creationOptions=["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=IF_SAFER",
                                    "NUM_THREADS=ALL_CPUS"])
    names = {}
    with arcpy.da.SearchCursor(files[0], ["Value", "Classvalue", "Class_name"]) as c:
        for v, cv, n in c:
            names[int(v)] = (int(cv), n)
    ds = gdal.Open(out, gdal.GA_Update)
    ct = gdal.ColorTable()
    for v, n in names.items():
        ct.SetColorEntry(v, tuple(COLOURS[n[1]]) + (255,))
    ds.GetRasterBand(1).SetRasterColorTable(ct)
    ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
    ds = None
    sr = arcpy.SpatialReference(); sr.loadFromString(G.TARGET_WKT)
    arcpy.management.DefineProjection(out, sr)
    arcpy.management.BuildRasterAttributeTable(out, "Overwrite")
    for fld, typ in [("Classvalue", "SHORT"), ("Class_name", "TEXT"), ("Red", "SHORT"),
                     ("Green", "SHORT"), ("Blue", "SHORT")]:
        arcpy.management.AddField(out, fld, typ)
    with arcpy.da.UpdateCursor(out, ["Value", "Classvalue", "Class_name", "Red", "Green", "Blue"]) as c:
        for r in c:
            cv, n = names[int(r[0])]
            c.updateRow([r[0], cv, n] + list(COLOURS[n]))
    arcpy.management.CalculateStatistics(out)
    import landform_codes
    if os.path.exists(final):
        arcpy.management.Delete(final)
    h_src, h_dst, table, nd = landform_codes.recode(out, final)
    problems = landform_codes.check(out, final, h_src, h_dst, table, nd)
    assert not problems, "recode to class codes failed: %s" % problems
    arcpy.management.Delete(out)
    print("  mosaic done, pixel = class code, %s total" % time.strftime("%H:%M:%S", time.gmtime(time.time() - t0)))


def main():
    smoke = "--smoke" in sys.argv
    keep_awake(True)
    if "--classify-only" not in sys.argv:
        print("1. analysis extent"); make_extent()
        print("2. train / test split of the hand-drawn labels"); make_split()
        print("3. train SVM"); train()
    if smoke:
        # one 4096 x 4096 G200 window at the equator, 169-183°E (Elysium / Cerberus), timed
        x0 = G.G200.ox + 50000 * 200; y0 = G.G200.oy - 16000 * 200
        ext = arcpy.Extent(x0, y0 - 4096 * 200, x0 + 4096 * 200, y0)
        dt = classify(os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mars_scratch", "smoke_cls.tif"), ext)
        print("  -> %.1f µs / px; ±60° (%.2f Gpx) would take ~%.1f h"
              % (dt / 4096 ** 2 * 1e6, G.G200.npix / 1e9, dt / 4096 ** 2 * G.G200.npix / 3600))
    else:
        print("4. classify ±60° at %d m" % CELL)
        lim = int(sys.argv[sys.argv.index("--tiles") + 1]) if "--tiles" in sys.argv else None
        classify_tiled(OUT if lim is None else os.path.join(SCRATCH, "tiletest_%dm.tif" % CELL), CELL, lim)
    keep_awake(False)


if __name__ == "__main__":
    main()
