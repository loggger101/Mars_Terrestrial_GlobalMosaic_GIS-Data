# -*- coding: utf-8 -*-
r"""Task 7, the SUPERVISED half - and the project's first accuracy assessment.

KB 19.2 established that Iso Cluster -> ML Classify is a no-op: re-classifying
auto-generated signatures teaches nothing. The supervised half needs training
labels that did not come from the classifier.

The circularity trap: if the labels are defined using the same bands being
classified, the accuracy is meaningless. So every class here is defined from
TERRAIN ALONE - slope, elevation, and the crater candidates of KB 26. None of
the five spectral bands touches a label. The question the numbers then answer
is a real one: how much of the landform structure is visible spectrally?

Train/test are split by SPATIAL BLOCKS, not random pixels. A random pixel split
in remote sensing inflates accuracy badly, because neighbouring pixels are not
independent samples.

Run with the ArcGIS interpreter.
"""
import os, time, datetime
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
import numpy as np
from osgeo import gdal
from scipy import ndimage
import arcpy
gdal.UseExceptions()

WS = junction("TypeArea")
GDB = on_drive(r"Mars Project\Mars Project.gdb")
SCRATCH = os.path.join(WS, "sup_scratch.gdb")
P = lambda n: os.path.join(WS, n)
NBLOCK_X, NBLOCK_Y = 10, 6      # checkerboard for the spatial split
# erode=4 / blob=400 wiped out the two thin transitional classes (wall_moderate
# kept 1,918 px of 540,901). They are narrow bands by nature, so the cores have
# to be thinner than the plateau's.
CORE_ERODE = 2                  # px, pull labels away from class boundaries
MIN_BLOB_PX = 120               # 1.2 km2 - a polygon worth training on
t0 = time.time()
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("ImageAnalyst")
arcpy.env.overwriteOutput = True


def step(m):
    print("  [%6.1fs] %s" % (time.time() - t0, m), flush=True)


def band(p, i=1):
    ds = gdal.Open(p)
    b = ds.GetRasterBand(i)
    a = b.ReadAsArray().astype(np.float32)
    del b, ds
    return a


print("=" * 78)
print("TASK 7 SUPERVISED - terrain-defined labels, spatially split, measured")
print("=" * 78)

slope = band(P("ius_slope_deg.tif"))
dem = band(P("ius_dem.tif"))
valid = np.isfinite(slope) & (slope > -1e30) & (dem > -32000)
step("terrain read  %d x %d" % (dem.shape[1], dem.shape[0]))

crater = np.zeros(dem.shape, bool)
cm = P("ius_cratermask.tif")
if os.path.exists(cm):
    crater = band(cm) > 0
step("crater mask: %s px" % format(int(crater.sum()), ","))

# ---- classes, every one of them from terrain only -------------------------
CLASSES = [
    (1, "crater_interior", crater & valid),
    (2, "wall_steep",      valid & (slope > 20)),
    (3, "wall_moderate",   valid & (slope > 12) & (slope <= 20) & (dem > 800) & (dem < 3000)),
    (4, "chasma_floor",    valid & (dem < 800) & (slope < 8)),
    (5, "plateau_flank",   valid & (dem > 2500) & (slope > 5) & (slope <= 12)),
    (6, "plateau",         valid & (dem > 3000) & (slope <= 5)),
]

lab = np.zeros(dem.shape, np.uint8)
for cv, nm, m in CLASSES:                 # earlier classes win overlaps
    lab[(lab == 0) & m] = cv
print("\n  class pixel counts before erosion:")
for cv, nm, _ in CLASSES:
    n = int((lab == cv).sum())
    print("   %d  %-16s %10s  %5.2f%%" % (cv, nm, format(n, ","), 100.0 * n / lab.size))

# cores only - a label on a class boundary is a label on a mixed pixel
core = np.zeros_like(lab)
for cv, nm, _ in CLASSES:
    e = ndimage.binary_erosion(lab == cv, iterations=CORE_ERODE)
    core[e] = cv
step("eroded %d px to class cores" % CORE_ERODE)

# ---- spatial block split ---------------------------------------------------
H, W = lab.shape
by = (np.arange(H) * NBLOCK_Y // H)[:, None]
bx = (np.arange(W) * NBLOCK_X // W)[None, :]
is_train = ((by + bx) % 2 == 0)
step("checkerboard %dx%d  train %.1f%% of area" % (NBLOCK_X, NBLOCK_Y, 100.0 * is_train.mean()))

train_lab = np.where(is_train, core, 0).astype(np.uint8)

# drop small blobs so training polygons are meaningful
keep = np.zeros_like(train_lab)
for cv, nm, _ in CLASSES:
    cc, n = ndimage.label(train_lab == cv)
    if n == 0:
        continue
    sizes = np.bincount(cc.ravel())
    big = np.isin(cc, np.nonzero(sizes >= MIN_BLOB_PX)[0][1:])
    keep[big] = cv
train_lab = keep
print("\n  training-core pixels per class:")
for cv, nm, _ in CLASSES:
    print("   %d  %-16s %10s" % (cv, nm, format(int((train_lab == cv).sum()), ",")))

# ---- write the training samples as a real feature class --------------------
ref = gdal.Open(P("ius_dem.tif"))
tl = P("ius_train_lab.tif")
drv = gdal.GetDriverByName("GTiff")
ds = drv.Create(tl, ref.RasterXSize, ref.RasterYSize, 1, gdal.GDT_Byte,
                options=["TILED=YES", "COMPRESS=DEFLATE"])
ds.SetGeoTransform(ref.GetGeoTransform())
ds.SetProjection(ref.GetProjection())
b = ds.GetRasterBand(1)
b.WriteArray(train_lab)
b.SetNoDataValue(0)
b.FlushCache()
del b, ds
step("training label raster")

if not arcpy.Exists(SCRATCH):
    arcpy.management.CreateFileGDB(WS, "sup_scratch.gdb")
raw = os.path.join(SCRATCH, "train_raw")
arcpy.conversion.RasterToPolygon(tl, raw, "SIMPLIFY", "Value")
AUTO_MARK = "auto-seed (make_typearea_supervised.py)"


def safe_to_replace(fc):
    """True only if fc is absent or every row in it was written by this script.

    KB 29.3: the class this used to write, Landform_TrainingSamples_terrain,
    now holds the hand-drawn labels, and the old Delete would have destroyed them on
    a single-copy drive. Never delete a class this script cannot prove it made.
    """
    if not arcpy.Exists(fc):
        return True
    if "MappedBy" not in [f.name for f in arcpy.ListFields(fc)]:
        return False
    with arcpy.da.SearchCursor(fc, ["MappedBy"]) as c:
        return all(r[0] == AUTO_MARK for r in c)


# Its own `_auto` class, like the other machine products (KB 25). Never the
# hand-label class Landform_TrainingSamples_terrain.
TRAIN_FC = os.path.join(GDB, "Landform_TrainingSamples_terrain_auto")
if not safe_to_replace(TRAIN_FC):
    raise SystemExit("REFUSING: %s holds rows this script did not write (KB 29.3). "
                     "Nothing deleted; choose another TRAIN_FC." % TRAIN_FC)
if arcpy.Exists(TRAIN_FC):
    arcpy.management.Delete(TRAIN_FC)
arcpy.management.CopyFeatures(raw, TRAIN_FC)
for f, t, l in [("Classvalue", "LONG", None), ("Classname", "TEXT", 30),
                ("Origin", "TEXT", 90), ("MappedBy", "TEXT", 44)]:
    arcpy.management.AddField(TRAIN_FC, f, t, field_length=l) if l else \
        arcpy.management.AddField(TRAIN_FC, f, t)
names = {cv: nm for cv, nm, _ in CLASSES}
with arcpy.da.UpdateCursor(TRAIN_FC, ["gridcode", "Classvalue", "Classname",
                                      "Origin", "MappedBy"]) as uc:
    for r in uc:
        r[1] = int(r[0])
        r[2] = names.get(int(r[0]), "?")
        r[3] = "terrain rule (slope/elevation/crater mask) - no spectral band used"
        r[4] = AUTO_MARK
        uc.updateRow(r)
ntr = int(arcpy.management.GetCount(TRAIN_FC)[0])
step("%d training polygons -> Landform_TrainingSamples_terrain_auto" % ntr)

# ---- classify, twice, to price the thermal index ---------------------------
def classify(tag, raster):
    ecd = P("ius_sup_%s.ecd" % tag)
    out = P("ius_sup_%s.tif" % tag)
    if os.path.exists(out) and os.path.exists(ecd):
        step("%-10s reused" % tag)
        return out
    t = time.time()
    arcpy.ia.TrainRandomTreesClassifier(raster, TRAIN_FC, ecd, None, 50, 30, 100000)
    r = arcpy.ia.ClassifyRaster(raster, ecd)
    r.save(out)
    del r
    step("%-10s trained + classified in %.0f s" % (tag, time.time() - t))
    return out


# the augmented stack: the 5-band composite + the diurnal-contrast index + slope
# A BuildVRT of these three inherits THREE different NoData values - 0.0 on the
# composite, -9999 on the index, -3.4e38 on slope. ClassifyRaster collapsed to a
# single class on that stack and wrote a nonsense nodata=3.0. Build it by hand
# with one consistent sentinel that no band can legitimately take.
aug = P("ius_stack_aug.tif")
if not os.path.exists(aug):
    comp = gdal.Open(P("ius_composite_5band.tif"))
    parts = [comp.GetRasterBand(i + 1).ReadAsArray().astype(np.float32)
             for i in range(comp.RasterCount)]
    del comp
    ti = band(P("ius_thermal_contrast.tif"))
    sl = band(P("ius_slope_deg.tif"))
    ti = np.where(ti <= -999, 0.0, ti) * 100.0      # onto a DN-like scale
    sl = np.where(np.isfinite(sl) & (sl > -1e30), sl, 0.0)
    parts += [ti.astype(np.float32), sl.astype(np.float32)]
    drv2 = gdal.GetDriverByName("GTiff")
    a2 = drv2.Create(aug, ref.RasterXSize, ref.RasterYSize, len(parts),
                     gdal.GDT_Float32,
                     options=["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=IF_SAFER"])
    a2.SetGeoTransform(ref.GetGeoTransform())
    a2.SetProjection(ref.GetProjection())
    for i, arr in enumerate(parts):
        bb = a2.GetRasterBand(i + 1)
        bb.WriteArray(arr)
        bb.SetNoDataValue(-9999.0)
        bb.FlushCache()
        del bb
    del a2, parts, ti, sl
    step("augmented 7-band stack, one NoData")

def build_stack(path, extra):
    """Mixed-type stack with ONE NoData sentinel - see the augmented note above."""
    if os.path.exists(path):
        return path
    comp = gdal.Open(P("ius_composite_5band.tif"))
    parts = [comp.GetRasterBand(i + 1).ReadAsArray().astype(np.float32)
             for i in range(comp.RasterCount)]
    del comp
    parts += extra()
    d2 = gdal.GetDriverByName("GTiff")
    a2 = d2.Create(path, ref.RasterXSize, ref.RasterYSize, len(parts), gdal.GDT_Float32,
                   options=["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=IF_SAFER"])
    a2.SetGeoTransform(ref.GetGeoTransform())
    a2.SetProjection(ref.GetProjection())
    for i, arr in enumerate(parts):
        bb = a2.GetRasterBand(i + 1)
        bb.WriteArray(arr); bb.SetNoDataValue(-9999.0); bb.FlushCache()
        del bb
    del a2, parts
    step("built %s" % os.path.basename(path))
    return path


def _ti():
    a = band(P("ius_thermal_contrast.tif"))
    return [(np.where(a <= -999, 0.0, a) * 100.0).astype(np.float32)]


therm = build_stack(P("ius_stack_therm.tif"), _ti)

runs = [("spectral", P("ius_composite_5band.tif")),
        ("thermal", therm),
        ("augmented", aug)]
results = {}
for tag, ras in runs:
    results[tag] = classify(tag, ras)

# ---- accuracy assessment on the HELD-OUT blocks ----------------------------
test_mask = (~is_train) & (core > 0)
truth = core[test_mask]
print("\n" + "=" * 78)
print("ACCURACY ON SPATIALLY HELD-OUT BLOCKS  (n = %s test pixels)" % format(int(truth.size), ","))
print("=" * 78)

summary = {}
def vat_map(path):
    """ClassifyRaster writes VALUE 0..n-1; the real class is the VAT's
    Classvalue column. Comparing raw VALUE against the labels shifts every
    class by one and produced a 2.1% 'accuracy' on the first run."""
    m = {}
    flds = [f.name for f in arcpy.ListFields(path)]
    cvf = next((f for f in flds if f.lower() == "classvalue"), None)
    if cvf is None:
        return None
    for v, cv in arcpy.da.SearchCursor(path, ["Value", cvf]):
        m[int(v)] = int(cv)
    return m


for tag, path in results.items():
    raw = band(path)
    vm = vat_map(path)
    if vm is None:
        raise RuntimeError("no Classvalue column in the VAT of %s" % path)
    print("   %s VAT mapping VALUE->Classvalue: %s" % (tag, vm))
    lut = np.zeros(int(max(vm) ) + 2, np.uint8)
    for v, cv in vm.items():
        lut[v] = cv
    ri = np.clip(raw, 0, len(lut) - 1).astype(np.int32)
    pred = lut[ri][test_mask]
    k = len(CLASSES)
    cm_ = np.zeros((k, k), np.int64)
    for i in range(k):
        ti = truth == (i + 1)
        if not ti.any():
            continue
        pi = pred[ti].astype(np.int32) - 1
        pi = pi[(pi >= 0) & (pi < k)]
        cm_[i] = np.bincount(pi, minlength=k)[:k]
    oa = np.trace(cm_) / max(cm_.sum(), 1)
    pe = (cm_.sum(0) * cm_.sum(1)).sum() / float(max(cm_.sum(), 1) ** 2)
    kappa = (oa - pe) / (1 - pe) if pe < 1 else float("nan")
    summary[tag] = (oa, kappa, cm_)
    print("\n  %s stack:  overall accuracy %.1f%%   kappa %.3f" % (tag.upper(), 100 * oa, kappa))
    print("   %-17s %7s %7s   %s" % ("class", "prod.", "user", "n test"))
    for i, (cv, nm, _) in enumerate(CLASSES):
        r_, c_ = cm_[i].sum(), cm_[:, i].sum()
        prod = cm_[i, i] / r_ if r_ else float("nan")
        user = cm_[i, i] / c_ if c_ else float("nan")
        print("   %-17s %6.1f%% %6.1f%%   %9s" % (nm, 100 * prod, 100 * user, format(int(r_), ",")))

a = summary["spectral"][0]
th = summary["thermal"][0]
b_ = summary["augmented"][0]
print("\n" + "=" * 78)
print("  spectral (the 5-band composite)      %.1f%%   kappa %.3f" % (100 * a, summary["spectral"][1]))
print("  + diurnal-contrast index ONLY        %.1f%%   kappa %.3f   (%+.1f points)  <- fair"
      % (100 * th, summary["thermal"][1], 100 * (th - a)))
print("  + index AND slope                    %.1f%%   kappa %.3f   (%+.1f points)  <- circular"
      % (100 * b_, summary["augmented"][1], 100 * (b_ - a)))
print("""
  Labels came from terrain alone, so the spectral number is not circular.
  The augmented number IS partly circular - slope is both a label input and a
  band - so read it as an upper bound, not as a fair comparison.""")
np.save(os.path.join(WS, "sup_confusion.npy"),
        np.array([summary["spectral"][2], summary["thermal"][2], summary["augmented"][2]]))
arcpy.CheckInExtension("Spatial")
arcpy.CheckInExtension("ImageAnalyst")
print("done in %.1f s" % (time.time() - t0))
