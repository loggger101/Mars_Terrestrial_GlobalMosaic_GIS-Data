# -*- coding: utf-8 -*-
r"""Day-night thermal analysis over the Ius Chasma type area.

The prospectus rests on one claim (KB 14.4): day-night pairing converts
brightness temperature into THERMAL INERTIA, the best dust-versus-bedrock
discriminator from orbit. Both held THEMIS mosaics are 8-bit DN with no
radiometric scaling - the night ISIS label states Type=UnsignedByte,
Base=0.0, Multiplier=1.0 - so calibrated thermal inertia is NOT derivable
from these products. What IS derivable is a relative diurnal-contrast index.

This script (a) proves that limit from the data, (b) builds the index, and
(c) tests it against the object-based classification and the terrain, to see
whether it carries information the other bands do not.

Outputs to Z:\TypeArea (junction - legacy SA tools reject the space).
"""
import os, sys, time
import numpy as np
from osgeo import gdal
gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "512")

OUT = r"Z:\TypeArea"
P = lambda n: os.path.join(OUT, n)
NODATA = -9999.0
t0 = time.time()


def band(path, idx=1):
    """Read one band as float32 + its nodata. Hold the dataset in a name:
    gdal.Open(p).GetRasterBand(1) frees the dataset before the band is read."""
    ds = gdal.Open(path)
    b = ds.GetRasterBand(idx)
    nod = b.GetNoDataValue()
    a = b.ReadAsArray().astype(np.float32)
    del b, ds
    return a, nod


def write_like(ref, path, arr, nodata=NODATA):
    rds = gdal.Open(ref)
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(path, rds.RasterXSize, rds.RasterYSize, 1, gdal.GDT_Float32,
                    options=["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=IF_SAFER"])
    ds.SetGeoTransform(rds.GetGeoTransform())
    ds.SetProjection(rds.GetProjection())
    b = ds.GetRasterBand(1)
    b.WriteArray(arr)
    b.SetNoDataValue(nodata)
    b.FlushCache()
    del b, ds, rds
    return path


# ---------------------------------------------------------------- 1. the inputs
print("=" * 78)
print("1. WHAT THE TWO THERMAL PRODUCTS ACTUALLY ARE")
print("=" * 78)
for n in ("ius_day", "ius_night"):
    ds = gdal.Open(P(n + ".tif"))
    b = ds.GetRasterBand(1)
    print("  %-10s %5dx%-5d  %-8s  nodata=%s" % (
        n, ds.RasterXSize, ds.RasterYSize,
        gdal.GetDataTypeName(b.DataType), b.GetNoDataValue()))
    del b, ds

day, _ = band(P("ius_day.tif"))
night, _ = band(P("ius_night.tif"))

# nodata is 0 on both (set by make_typearea_stack); treat 0 as no observation
valid = (day > 0) & (night > 0)
nv = int(valid.sum())
tot = day.size
print("\n  co-valid pixels %s / %s  = %.2f%%" % (f"{nv:,}", f"{tot:,}", 100.0 * nv / tot))

d = day[valid].astype(np.float64); n_ = night[valid].astype(np.float64)
for nm, a in (("day  DN", d), ("night DN", n_)):
    q = np.percentile(a, [0, 2, 25, 50, 75, 98, 100])
    print("  %-9s mean %6.2f  sd %5.2f   p0/p2/p25/p50/p75/p98/p100 = %s"
          % (nm, a.mean(), a.std(), "/".join("%.0f" % v for v in q)))

print("""
  >> Both are 8-bit DN, 0-255, independently stretched by ASU for display.
     There is no Base/Multiplier to Kelvin in either label. A raw day-night
     subtraction is therefore NOT a temperature difference and NOT thermal
     inertia - the two stretches are not on a common scale.""")

# ------------------------------------------------- 2. the two derived products
print("=" * 78)
print("2. TWO PRODUCTS, AND WHY THE SECOND IS THE DEFENSIBLE ONE")
print("=" * 78)

# (a) raw DN difference - kept because it is what a reader expects to see,
#     labelled for what it is
diff = np.full(day.shape, NODATA, np.float32)
diff[valid] = day[valid] - night[valid]
write_like(P("ius_day.tif"), P("ius_dn_diff.tif"), diff)
print("  ius_dn_diff.tif        raw DN(day) - DN(night)   mean %6.2f  sd %5.2f"
      % (diff[valid].astype(np.float64).mean(), diff[valid].astype(np.float64).std()))
del diff

# (b) robust percentile scaling puts each band on its own [0,1] before
#     differencing, so the index measures RELATIVE diurnal contrast within the
#     type area rather than an artefact of two unrelated stretches.
def robust01(a, mask):
    lo, hi = np.percentile(a[mask], [2, 98])
    out = (a - lo) / (hi - lo)
    return np.clip(out, 0.0, 1.0), lo, hi

dS, dlo, dhi = robust01(day, valid)
nS, nlo, nhi = robust01(night, valid)
print("  scaling  day  p2=%.0f p98=%.0f     night p2=%.0f p98=%.0f" % (dlo, dhi, nlo, nhi))

idx = np.full(day.shape, NODATA, np.float32)
idx[valid] = dS[valid] - nS[valid]
write_like(P("ius_day.tif"), P("ius_thermal_contrast.tif"), idx)
iv = idx[valid].astype(np.float64)
q = np.percentile(iv, [0, 2, 25, 50, 75, 98, 100])
print("  ius_thermal_contrast.tif  scaled(day)-scaled(night)  range [-1,1]")
print("      mean %+.4f  sd %.4f   p0/p2/p25/p50/p75/p98/p100 = %s"
      % (iv.mean(), iv.std(), "/".join("%+.2f" % v for v in q)))
print("""
      HIGH  = large diurnal swing  = low thermal inertia = dust / fines
      LOW   = damped diurnal swing = high thermal inertia = bedrock / coarse""")
del dS, nS

# --------------------------------------------- 3. is it a NEW dimension or not?
print("=" * 78)
print("3. DOES THE INDEX CARRY INFORMATION THE STACK DOES NOT ALREADY HAVE?")
print("=" * 78)

def corr(a, b, mask):
    x = a[mask].astype(np.float64)
    y = b[mask].astype(np.float64)
    x -= x.mean(); y -= y.mean()
    den = np.sqrt((x * x).sum() * (y * y).sum())
    return float((x * y).sum() / den) if den else float("nan")

others = [("day IR", P("ius_day.tif"), 1),
          ("night IR", P("ius_night.tif"), 1),
          ("Viking red", P("ius_viking.tif"), 1),
          ("elevation", P("ius_dem.tif"), 1),
          ("slope deg", P("ius_slope_deg.tif"), 1)]

print("  Pearson r of the contrast index against every other layer:")
for nm, path, bi in others:
    a, nod = band(path, bi)
    m = valid.copy()
    if nod is not None:
        m &= (a != nod)
    if nm == "elevation":
        m &= (a > -32000)
    print("     %-12s r = %+.3f   (n=%s)" % (nm, corr(idx, a, m), f"{int(m.sum()):,}"))
    del a

# ------------------------------------- 4. read it against the landform classes
print("=" * 78)
print("4. THE INDEX PER OBJECT-BASED CLASS  (ius_obj_medium, 14/14/30)")
print("=" * 78)
cls_path = P("ius_obj_medium.tif")
if os.path.exists(cls_path):
    cls, cnod = band(cls_path)
    m = valid & (cls > 0)
    if cnod is not None:
        m &= (cls != cnod)
    sl, snod = band(P("ius_slope_deg.tif"))
    el, enod = band(P("ius_dem.tif"))
    # both carry NoData sentinels; an unmasked one turns every class mean to -inf
    m &= np.isfinite(sl) & (sl > -1e30) & (el > -32000)
    if snod is not None:
        m &= (sl != snod)
    if enod is not None:
        m &= (el != enod)
    c = cls[m].astype(np.int32)
    v = idx[m].astype(np.float64)
    sv = sl[m].astype(np.float64)
    ev = el[m].astype(np.float64)
    del sl, el
    print("  class      px        %%    contrast   sd     slope deg   elev m")
    rows = []
    for k in np.unique(c):
        sel = c == k
        rows.append((k, int(sel.sum()), v[sel].mean(), v[sel].std(),
                     sv[sel].mean(), ev[sel].mean()))
    for k, npx, mu, sd, slm, elm in sorted(rows, key=lambda r: r[2]):
        print("   %5d  %9s  %5.1f   %+.4f  %.4f   %6.2f   %+8.1f"
              % (k, f"{npx:,}", 100.0 * npx / len(c), mu, sd, slm, elm))
    print("""
  Sorted coldest-index first: the top rows are the surfaces that damp the
  diurnal swing (rock), the bottom rows are the ones that swing hardest (dust).""")
else:
    print("  ius_obj_medium.tif not found - skipped")

print("=" * 78)
print("done in %.1f s" % (time.time() - t0))
