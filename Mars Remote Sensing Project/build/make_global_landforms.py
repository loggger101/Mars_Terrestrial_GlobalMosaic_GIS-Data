# -*- coding: utf-8 -*-
r"""Crater and channel candidates over the WHOLE +/-60 extent - tasks 11 + 12.

make_crater_candidates.py and make_channel_candidates.py did this for Ius
Chasma, 8891 x 4150, by reading the whole scene into RAM. G200 is 3.79 Gpx -
103x the type area, 15.2 GB as float32 - so the same approach cannot work. This
is the tiled form of the identical method.

DESKTOP JOB. Estimated 6-8 h. It is resumable: every tile checkpoints to
SCRATCH\tile_XXX.npz and a completed tile is skipped on re-run, so a crash or a
reboot costs one tile, not the run. Delete the scratch directory to start over.

---------------------------------------------------------------- the two scales

Fill is a global operation - a depression's fill depth is set by its lowest rim
pass, which may be far outside any one tile. One tile size therefore cannot
serve both a 1 km crater and Hellas. So there are two passes:

  COARSE   the whole +/-60 DEM decimated 8x to 1600 m (13337 x 4446 = 59 Mpx),
           filled in ONE piece. Catches basins >= ~20 km with no tile edges at
           all: Hellas, Argyre, Isidis, and every large crater.

  FINE     G200 in 8192 px cores with a 1024 px (205 km) halo. Fill runs on
           core+halo; only candidates whose centroid lands in the CORE are
           kept, so tiles neither duplicate nor drop along their seams.

Merged on centre distance, the fine measurement preferred where both see the
same feature. A crater wider than the halo is found by the coarse pass only and
is flagged Preservation='coarse-pass' - its diameter is good to ~1.6 km, not
~0.2 km.

--------------------------------------------------------------- what stays true

Everything the type-area runs established carries over unchanged:

  * KB 25.1 - Fill floods closed basins. Ius was raised 2,077 m and 56% of the
    first network was routing across a lake that does not exist. The fill-depth
    mask (keep fill - dem <= 1 m) is applied here too, and at +/-60 it matters
    far MORE, not less: Valles Marineris, Hellas, Argyre and every crater
    interior are all closed basins. The discard fraction is measured per tile
    and reported.
  * KB 26.3 - this finds CLOSED depressions. A breached crater is invisible to
    it. Oudemans is the worked example. Report the output as a complete
    inventory of closed depressions >= 1 km, never as a crater inventory.
  * Filters stay at the values verify_crater_detection.py tuned them to:
    aspect <= 2.0, fill ratio >= 0.55 (KB 26.4).
  * Output goes to SEPARATE feature classes. Landform_CraterRims and
    Landform_ChannelCenterlines stay manual.

------------------------------------------------------------------- resolution

200 m, the DEM's native grid - an open decision, 2026-09-19. The type-area products ran
at 100 m because the imagery stack is 100 m, but HRSC/MOLA is 200 m: that run
was resampling a 200 m product and finding flow paths in the interpolation. At
G200 the warp is exact (grid60) and the detail is measured rather than invented.
"""
import os
import sys
import time
import glob
import datetime

import numpy as np
from osgeo import gdal
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grid60 as G

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_CACHEMAX", "1024")

# --------------------------------------------------------------------- config
GRID = G.G200
DEM = os.path.join(G.OUTDIR_NOSPACE, "global60_dem.tif")
IDX200 = os.path.join(G.OUTDIR_NOSPACE, "global60_thermal_contrast_200m.tif")
GDB = r"Z:\Mars Project\Mars Project.gdb"

# KB 2.2: intermediates go on internal SSD, never on the USB bus
SCRATCH = r"C:\MarsScratch\global60"
FC_CRATER = "Landform_CraterCandidates_auto_60"
FC_CHANNEL = "Landform_ChannelCandidates_auto_60"
# the coarse pass alone is a product: every closed basin >= 20 km over the
# whole extent, 48 s, no tile seams. Kept in its own class so nobody mistakes
# it for the full >= 1 km inventory.
FC_BASIN = "Landform_BasinCandidates_auto_60"

CORE = 8192            # px of core per tile  (1638 km at 200 m)
HALO = 1024            # px of overlap        ( 205 km at 200 m)
COARSE_FACTOR = 8      # 200 m -> 1600 m for the basin pass

CELL_KM2 = (GRID.res / 1000.0) ** 2        # 0.04 km2 at 200 m
MIN_DEPTH_M = 20.0
MIN_DIAM_KM = 1.0
MAX_ASPECT = 2.0
MIN_FILLRATIO = 0.55
COARSE_MIN_DIAM_KM = 20.0

# 50 km2 of catchment, as the type-area run used - but the cell is 4x bigger
THRESH_KM2 = 50.0
THRESH = int(round(THRESH_KM2 / CELL_KM2))
MIN_SEG_KM = 2.0
MAX_FILL_M = 1.0       # KB 25.1: off filled ground

R = 3396190.0
DEG = R * np.pi / 180.0
TODAY = datetime.datetime(2026, 9, 19)
T0 = time.time()


def step(m):
    print("  [%7.1fs] %s" % (time.time() - T0, m), flush=True)


def hms(s):
    return "%d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)


# ------------------------------------------------------------------ utilities
def write_tif(path, arr, grid, dtype, nodata):
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(path, grid.nx, grid.ny, 1, dtype,
                    options=["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=IF_SAFER"])
    ds.SetGeoTransform(grid.geotransform)
    ds.SetProjection(G.TARGET_WKT)
    b = ds.GetRasterBand(1)
    b.WriteArray(arr)
    if nodata is not None:
        b.SetNoDataValue(float(nodata))
    b.FlushCache()
    del b, ds
    return path


def arcpy_fill(dem_path, out_path):
    """arcpy.sa.Fill - the same tool the type-area runs used, so the results are
    the same method and not merely a similar one."""
    import arcpy
    from arcpy.sa import Fill
    arcpy.env.overwriteOutput = True
    if arcpy.Exists(out_path):
        arcpy.management.Delete(out_path)
    Fill(dem_path).save(out_path)
    return out_path


def shape_measure(depth, min_depth, min_diam_km, cell_km2):
    """Label closed depressions and measure each. Returns a dict of arrays.

    Identical arithmetic to make_crater_candidates.py, lifted out so the coarse
    pass and every fine tile use one implementation rather than two."""
    sink = depth > min_depth
    lab, n = ndimage.label(sink)
    if n == 0:
        return None, None, 0
    idx = np.arange(1, n + 1)
    area_px = np.bincount(lab.ravel(), minlength=n + 1)[1:]
    maxd = ndimage.maximum(depth, lab, idx)
    meand = ndimage.mean(depth, lab, idx)
    objs = ndimage.find_objects(lab)
    com = ndimage.center_of_mass(sink, lab, idx)
    cy = np.array([c[0] for c in com])
    cx = np.array([c[1] for c in com])
    diam_km = 2.0 * np.sqrt(area_px * cell_km2 / np.pi)
    hh = np.array([o[0].stop - o[0].start for o in objs], float)
    ww = np.array([o[1].stop - o[1].start for o in objs], float)
    aspect = np.maximum(hh, ww) / np.maximum(np.minimum(hh, ww), 1.0)
    fillratio = area_px / np.maximum(hh * ww, 1.0)
    keep = ((diam_km >= min_diam_km) & (aspect <= MAX_ASPECT) &
            (fillratio >= MIN_FILLRATIO))
    rec = dict(label=idx[keep], cx=cx[keep], cy=cy[keep], diam_km=diam_km[keep],
               depth_max=maxd[keep], depth_mean=meand[keep],
               aspect=aspect[keep], fillratio=fillratio[keep],
               area_px=area_px[keep])
    drop = dict(small=int((diam_km < min_diam_km).sum()),
                elong=int((aspect > MAX_ASPECT).sum()),
                ragged=int((fillratio < MIN_FILLRATIO).sum()))
    return rec, drop, n


def to_lonlat(cx, cy, grid):
    X = grid.ox + (cx + 0.5) * grid.res
    Y = grid.oy - (cy + 0.5) * grid.res
    return (180.0 + X / DEG) % 360.0, Y / DEG


# ------------------------------------------------------------- 0. prerequisite
def ensure_thermal_200():
    """A 2x2 mean of the 100 m index, so every zonal statistic below runs on the
    DEM's own grid instead of straddling two resolutions."""
    src = os.path.join(G.OUTDIR_NOSPACE, "global60_thermal_contrast.tif")
    if not os.path.exists(src):
        print("  !! %s missing - run make_global_thermal.py first" % src)
        return None
    if os.path.exists(IDX200):
        d = gdal.Open(IDX200)
        ok = (d.RasterXSize, d.RasterYSize) == (GRID.nx, GRID.ny)
        d = None
        if ok:
            step("thermal index at 200 m  (reused)")
            return IDX200
    t = time.time()
    gdal.Warp(IDX200, src,
              creationOptions=["TILED=YES", "COMPRESS=DEFLATE", "BIGTIFF=YES"],
              **GRID.warp_kwargs("average", nodata=-32768))
    # gdal.Warp writes a PROJ WKT that ArcGIS reads as "unknown" (KB 18, 20.2).
    # verify_global60.py caught this one; relabel at the source so it cannot
    # recur on a re-run.
    try:
        import arcpy
        sr = arcpy.SpatialReference()
        sr.loadFromString(G.TARGET_WKT)
        arcpy.management.DefineProjection(IDX200, sr)
    except ImportError:
        print("  arcpy unavailable - 200 m index CRS left as the PROJ WKT")
    step("thermal index resampled to 200 m  %s" % hms(time.time() - t))
    return IDX200


# ------------------------------------------------------------- 1. coarse basins
def coarse_pass():
    out = os.path.join(SCRATCH, "coarse.npz")
    if os.path.exists(out):
        step("coarse basin pass  (reused)")
        return dict(np.load(out))
    t = time.time()
    f = COARSE_FACTOR
    cg = G.Grid(GRID.ox, GRID.oy, GRID.res * f, GRID.nx // f, GRID.ny // f, "COARSE")
    step("coarse pass: %d x %d @ %g m, one Fill over the whole extent"
         % (cg.nx, cg.ny, cg.res))
    cpath = os.path.join(SCRATCH, "coarse_dem.tif")
    gdal.Warp(cpath, DEM,
              creationOptions=["TILED=YES", "COMPRESS=DEFLATE"],
              **cg.warp_kwargs("average", nodata=-32768))
    fpath = arcpy_fill(cpath, os.path.join(SCRATCH, "coarse_fill.tif"))
    dem = gdal.Open(cpath).ReadAsArray().astype(np.float32)
    fil = gdal.Open(fpath).ReadAsArray().astype(np.float32)
    depth = np.where(dem > -32000, fil - dem, 0.0).astype(np.float32)
    rec, drop, n = shape_measure(depth, MIN_DEPTH_M, COARSE_MIN_DIAM_KM,
                                 (cg.res / 1000.0) ** 2)
    if rec is None:
        rec = {k: np.array([]) for k in ("diam_km", "depth_max", "depth_mean",
                                         "aspect", "fillratio", "cx", "cy")}
        lon = lat = np.array([])
    else:
        lon, lat = to_lonlat(rec["cx"], rec["cy"], cg)
    rec["lon"], rec["lat"] = lon, lat
    rec["res"] = np.array([cg.res])
    step("coarse: %s depressions, %d basins >= %.0f km  %s"
         % (f"{n:,}", len(rec["diam_km"]), COARSE_MIN_DIAM_KM, hms(time.time() - t)))
    np.savez_compressed(out, **rec)
    return rec


# --------------------------------------------------------------- 2. fine tiles
def tile_list():
    """(tid, core_x0, core_y0, core_w, core_h, hx0, hy0, hw, hh) per tile."""
    out = []
    tid = 0
    if TILE_ORIGIN is not None:            # smoke: one window, not the planet
        ox, oy = TILE_ORIGIN
        ys = range(oy, min(oy + 2 * CORE, GRID.ny), CORE)
        xs = range(ox, min(ox + 2 * CORE, GRID.nx), CORE)
    else:
        ys = range(0, GRID.ny, CORE)
        xs = range(0, GRID.nx, CORE)
    for y0 in ys:
        for x0 in xs:
            cw = min(CORE, GRID.nx - x0)
            ch = min(CORE, GRID.ny - y0)
            hx0 = max(0, x0 - HALO)
            hy0 = max(0, y0 - HALO)
            hx1 = min(GRID.nx, x0 + cw + HALO)
            hy1 = min(GRID.ny, y0 + ch + HALO)
            out.append((tid, x0, y0, cw, ch, hx0, hy0, hx1 - hx0, hy1 - hy0))
            tid += 1
    return out


def do_tile(t):
    """Fill one tile, measure craters, route channels. Checkpointed."""
    tid, cx0, cy0, cw, ch, hx0, hy0, hw, hh = t
    cp = os.path.join(SCRATCH, "tile_%03d.npz" % tid)
    if os.path.exists(cp):
        return cp, True

    import arcpy
    from arcpy.sa import (FlowDirection, FlowAccumulation, StreamLink,
                          StreamOrder, Con, Raster)
    arcpy.env.overwriteOutput = True

    tg = GRID.sub(hx0, hy0, hw, hh, "tile%03d" % tid)
    wd = os.path.join(SCRATCH, "t%03d" % tid)
    os.makedirs(wd, exist_ok=True)
    dpath = os.path.join(wd, "dem.tif")

    ds = gdal.Open(DEM)
    arr = ds.GetRasterBand(1).ReadAsArray(hx0, hy0, hw, hh)
    ds = None
    if (arr > -32000).mean() < 0.001:
        np.savez_compressed(cp, empty=np.array([1]))
        return cp, False
    write_tif(dpath, arr, tg, gdal.GDT_Int16, -32768)
    del arr

    fpath = arcpy_fill(dpath, os.path.join(wd, "fill.tif"))
    dem = gdal.Open(dpath).ReadAsArray().astype(np.float32)
    fil = gdal.Open(fpath).ReadAsArray().astype(np.float32)
    valid = dem > -32000
    depth = np.where(valid, fil - dem, 0.0).astype(np.float32)
    del fil
    dpth_path = write_tif(os.path.join(wd, "depth.tif"), depth, tg,
                          gdal.GDT_Float32, -9999)

    # ---- craters -------------------------------------------------------
    rec, drop, nall = shape_measure(depth, MIN_DEPTH_M, MIN_DIAM_KM, CELL_KM2)
    if rec is None:
        crat = {k: np.array([]) for k in ("diam_km", "depth_max", "depth_mean",
                                          "aspect", "fillratio", "lon", "lat")}
    else:
        # keep only centroids inside the CORE, so seams neither drop nor double
        gx = hx0 + rec["cx"]
        gy = hy0 + rec["cy"]
        inside = ((gx >= cx0) & (gx < cx0 + cw) & (gy >= cy0) & (gy < cy0 + ch))
        lon, lat = to_lonlat(rec["cx"][inside], rec["cy"][inside], tg)
        crat = dict(diam_km=rec["diam_km"][inside], depth_max=rec["depth_max"][inside],
                    depth_mean=rec["depth_mean"][inside], aspect=rec["aspect"][inside],
                    fillratio=rec["fillratio"][inside], lon=lon, lat=lat)

    # ---- channels ------------------------------------------------------
    fdr = FlowDirection(fpath, "NORMAL")
    fdr_p = os.path.join(wd, "fdr.tif")
    fdr.save(fdr_p)
    fac = FlowAccumulation(fdr_p, None, "FLOAT")
    fac_p = os.path.join(wd, "fac.tif")
    fac.save(fac_p)
    nofill = Raster(dpth_path) <= MAX_FILL_M
    st = Con((Raster(fac_p) > THRESH) & (nofill == 1), 1)
    st_p = os.path.join(wd, "streams.tif")
    st.save(st_p)
    # how much of the raw network was routing across filled ground - KB 25.1
    # measured every tile, because at +/-60 the closed basins are far bigger
    # than Ius: Valles Marineris, Hellas, Argyre, every crater interior.
    n_all = int((gdal.Open(fac_p).ReadAsArray() > THRESH).sum())
    n_keep = int((gdal.Open(st_p).ReadAsArray() == 1).sum())

    lk = os.path.join(wd, "link.tif")
    StreamLink(st_p, fdr_p).save(lk)
    od = os.path.join(wd, "ord.tif")
    StreamOrder(st_p, fdr_p, "STRAHLER").save(od)
    sgdb = os.path.join(wd, "s.gdb")
    if not arcpy.Exists(sgdb):
        arcpy.management.CreateFileGDB(wd, "s.gdb")
    lines = os.path.join(sgdb, "cand")
    arcpy.sa.StreamToFeature(lk, fdr_p, lines, "NO_SIMPLIFY")

    zo = os.path.join(sgdb, "zo")
    arcpy.sa.ZonalStatisticsAsTable(lines, "arcid", od, zo, "DATA", "MAXIMUM")
    ordv = {r[0]: r[1] for r in arcpy.da.SearchCursor(zo, ["arcid", "MAX"])}
    zf = os.path.join(sgdb, "zf")
    arcpy.sa.ZonalStatisticsAsTable(lines, "arcid", dpth_path, zf, "DATA", "MEAN")
    filv = {r[0]: r[1] for r in arcpy.da.SearchCursor(zf, ["arcid", "MEAN"])}

    cxmin = GRID.ox + cx0 * GRID.res
    cxmax = cxmin + cw * GRID.res
    cymax = GRID.oy - cy0 * GRID.res
    cymin = cymax - ch * GRID.res

    wkts, lens, ords, fils = [], [], [], []
    for shp, aid in arcpy.da.SearchCursor(lines, ["SHAPE@", "arcid"]):
        km = shp.length / 1000.0
        if km < MIN_SEG_KM:
            continue
        c = shp.trueCentroid
        if not (cxmin <= c.X < cxmax and cymin <= c.Y < cymax):
            continue
        wkts.append(shp.WKT)
        lens.append(km)
        ords.append(int(ordv.get(aid, 0) or 0))
        fils.append(float(filv.get(aid, 0.0) or 0.0))

    np.savez_compressed(
        cp,
        c_diam=crat["diam_km"], c_dmax=crat["depth_max"], c_dmean=crat["depth_mean"],
        c_asp=crat["aspect"], c_fr=crat["fillratio"], c_lon=crat["lon"], c_lat=crat["lat"],
        l_wkt=np.array(wkts, dtype=object), l_km=np.array(lens),
        l_ord=np.array(ords), l_fill=np.array(fils),
        stats=np.array([nall, n_all, n_keep, int(valid.sum()), int((depth > 1).sum())]),
        allow_pickle=True)

    # the tile's rasters are worth nothing once measured, and they are large
    for f in glob.glob(os.path.join(wd, "*")):
        try:
            if os.path.isfile(f):
                os.remove(f)
        except OSError:
            pass
    return cp, False


# ------------------------------------------------------------------- 3. merge
def merge_and_write(coarse, fc_crater=None, write_channels=True):
    fc_crater = fc_crater or FC_CRATER
    import arcpy
    arcpy.env.overwriteOutput = True

    cs = dict(diam=[], dmax=[], dmean=[], asp=[], fr=[], lon=[], lat=[], src=[])
    lw, lk, lo, lf = [], [], [], []
    disc_all = disc_keep = 0
    for cp in sorted(glob.glob(os.path.join(SCRATCH, "tile_*.npz"))):
        z = np.load(cp, allow_pickle=True)
        if "empty" in z:
            continue
        n = len(z["c_diam"])
        cs["diam"].extend(z["c_diam"]); cs["dmax"].extend(z["c_dmax"])
        cs["dmean"].extend(z["c_dmean"]); cs["asp"].extend(z["c_asp"])
        cs["fr"].extend(z["c_fr"]); cs["lon"].extend(z["c_lon"]); cs["lat"].extend(z["c_lat"])
        cs["src"].extend(["fine"] * n)
        lw.extend(list(z["l_wkt"])); lk.extend(list(z["l_km"]))
        lo.extend(list(z["l_ord"])); lf.extend(list(z["l_fill"]))
        s = z["stats"]
        disc_all += int(s[1]); disc_keep += int(s[2])

    nfine = len(cs["diam"])
    # coarse basins the fine pass did not already find
    flon = np.array(cs["lon"]); flat = np.array(cs["lat"]); fdiam = np.array(cs["diam"])
    added = 0
    for i in range(len(coarse["diam_km"])):
        lo_, la_ = float(coarse["lon"][i]), float(coarse["lat"][i])
        if len(flon):
            d = np.sqrt(((flon - lo_) * DEG * np.cos(np.radians(la_)) / 1000.0) ** 2 +
                        ((flat - la_) * DEG / 1000.0) ** 2)
            if d.min() <= 0.5 * float(coarse["diam_km"][i]):
                continue
        cs["diam"].append(float(coarse["diam_km"][i]))
        cs["dmax"].append(float(coarse["depth_max"][i]))
        cs["dmean"].append(float(coarse["depth_mean"][i]))
        cs["asp"].append(float(coarse["aspect"][i]))
        cs["fr"].append(float(coarse["fillratio"][i]))
        cs["lon"].append(lo_); cs["lat"].append(la_); cs["src"].append("coarse")
        added += 1
    step("merged: %s fine + %d coarse-only = %s craters; %s channel segments"
         % (f"{nfine:,}", added, f"{len(cs['diam']):,}", f"{len(lw):,}"))
    if disc_all:
        print("     fill-artefact discard across all tiles: %.1f%% of stream cells"
              % (100.0 * (1 - disc_keep / float(disc_all))))

    sr = arcpy.SpatialReference()
    sr.loadFromString(G.TARGET_WKT)

    # ---- craters (points; the fine pass measures the polygon, we keep the
    #      measurement rather than 1.7 M polygon geometries) ---------------
    if arcpy.Exists(os.path.join(GDB, fc_crater)):
        arcpy.management.Delete(os.path.join(GDB, fc_crater))
    arcpy.management.CreateFeatureclass(GDB, fc_crater, "POINT", spatial_reference=sr)
    out = os.path.join(GDB, fc_crater)
    for nm, ty, ln in [("Confidence", "TEXT", 12), ("Evidence", "TEXT", 120),
                       ("DiameterKm", "DOUBLE", None), ("DepthMaxM", "DOUBLE", None),
                       ("DepthMeanM", "DOUBLE", None), ("Aspect", "DOUBLE", None),
                       ("FillRatio", "DOUBLE", None), ("CenterLon", "DOUBLE", None),
                       ("CenterLat", "DOUBLE", None), ("Preservation", "TEXT", 20),
                       ("Notes", "TEXT", 200), ("MappedBy", "TEXT", 40),
                       ("MappedOn", "DATE", None)]:
        if ln:
            arcpy.management.AddField(out, nm, ty, field_length=ln)
        else:
            arcpy.management.AddField(out, nm, ty)
    cols = ["SHAPE@XY", "Confidence", "Evidence", "DiameterKm", "DepthMaxM",
            "DepthMeanM", "Aspect", "FillRatio", "CenterLon", "CenterLat",
            "Preservation", "Notes", "MappedBy", "MappedOn"]
    ev = ("closed depression in HRSC/MOLA 200 m DEM, fill depth >%.0f m; "
          "tiled +/-60 detection" % MIN_DEPTH_M)
    with arcpy.da.InsertCursor(out, cols) as ic:
        for i in range(len(cs["diam"])):
            lo_, la_ = cs["lon"][i], cs["lat"][i]
            x = ((lo_ - 180.0 + 540.0) % 360.0 - 180.0) * DEG
            y = la_ * DEG
            ic.insertRow(((x, y), "inferred", ev, round(cs["diam"][i], 3),
                          round(cs["dmax"][i], 1), round(cs["dmean"][i], 1),
                          round(cs["asp"][i], 3), round(cs["fr"][i], 3),
                          round(lo_, 4), round(la_, 4), cs["src"][i] + "-pass",
                          "depth/diameter = %.4f" % (cs["dmax"][i] / (cs["diam"][i] * 1000.0)),
                          "auto-candidate (fill-depth detection)", TODAY))
    step("wrote %s -> %s" % (f"{len(cs['diam']):,}", fc_crater))

    # ---- channels -------------------------------------------------------
    if not write_channels or not lw:
        step("no channel segments - channel class not written")
        return len(cs["diam"]), 0
    if arcpy.Exists(os.path.join(GDB, FC_CHANNEL)):
        arcpy.management.Delete(os.path.join(GDB, FC_CHANNEL))
    arcpy.management.CreateFeatureclass(GDB, FC_CHANNEL, "POLYLINE", spatial_reference=sr)
    out = os.path.join(GDB, FC_CHANNEL)
    for nm, ty, ln in [("UnitName", "TEXT", 60), ("Origin", "TEXT", 20),
                       ("Confidence", "TEXT", 12), ("Evidence", "TEXT", 120),
                       ("StrahlerOrd", "SHORT", None), ("LengthKm", "DOUBLE", None),
                       ("FillDepthM", "DOUBLE", None), ("Notes", "TEXT", 200),
                       ("MappedBy", "TEXT", 40), ("MappedOn", "DATE", None)]:
        if ln:
            arcpy.management.AddField(out, nm, ty, field_length=ln)
        else:
            arcpy.management.AddField(out, nm, ty)
    cols = ["SHAPE@", "UnitName", "Origin", "Confidence", "Evidence", "StrahlerOrd",
            "LengthKm", "FillDepthM", "Notes", "MappedBy", "MappedOn"]
    ev = ("DEM flow accumulation > %d cells (%.0f km2) at 200 m, off filled ground"
          % (THRESH, THRESH_KM2))
    with arcpy.da.InsertCursor(out, cols) as ic:
        for i in range(len(lw)):
            shp = arcpy.FromWKT(lw[i], sr)
            ic.insertRow((shp, None, "indeterminate", "inferred", ev,
                          int(lo[i]), round(float(lk[i]), 3), round(float(lf[i]), 3),
                          None, "auto-candidate (flow accumulation)", TODAY))
    step("wrote %s -> %s" % (f"{len(lw):,}", FC_CHANNEL))
    return len(cs["diam"]), len(lw)


def attribute_thermal(fc_crater=None):
    """ThermIdx per candidate, sampled from the 200 m index at each centre."""
    import arcpy
    if not os.path.exists(IDX200):
        print("  thermal index at 200 m missing - ThermIdx left null")
        return
    ds = gdal.Open(IDX200)
    b = ds.GetRasterBand(1)
    gt = ds.GetGeoTransform()          # gt[5] is negative: y decreases downwards
    fc = os.path.join(GDB, fc_crater or FC_CRATER)
    arcpy.management.AddField(fc, "ThermIdx", "DOUBLE")
    n = 0
    with arcpy.da.UpdateCursor(fc, ["SHAPE@XY", "ThermIdx"]) as uc:
        for row in uc:
            x, y = row[0]
            px = int((x - gt[0]) / gt[1])
            py = int((gt[3] - y) / -gt[5])
            if not (0 <= px < ds.RasterXSize and 0 <= py < ds.RasterYSize):
                continue
            v = int(b.ReadAsArray(px, py, 1, 1)[0, 0])
            row[1] = None if v == -32768 else v / 10000.0
            uc.updateRow(row)
            n += 1
    del b, ds
    step("thermal index attached to %s crater candidates" % f"{n:,}")


def parse_args(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--smoke", action="store_true",
                    help="small tiles over Ius Chasma, separate scratch and "
                         "separate output classes - exercises every code path "
                         "in minutes instead of hours")
    ap.add_argument("--core", type=int, help="override the core tile size, px")
    ap.add_argument("--halo", type=int, help="override the halo, px")
    ap.add_argument("--max-tiles", type=int, help="stop after this many tiles")
    ap.add_argument("--skip-coarse", action="store_true")
    ap.add_argument("--skip-fine", action="store_true",
                    help="write ONLY the coarse basin inventory, to Landform_BasinCandidates_auto_60 - 48 s, no tile seams")
    ap.add_argument("--only-coarse", action="store_true",
                    help="run just the whole-extent basin pass and stop")
    return ap.parse_args(argv)


def apply_smoke():
    """Retarget everything at a cheap window over the type area.

    KB 28.7: on jobs measured in hours, test the call on a window first. This
    is that rule built into the script rather than left to whoever runs it.
    Ius Chasma is chosen because the type-area products give something to
    compare the output against - 'it ran' is not a validation.
    """
    global CORE, HALO, SCRATCH, FC_CRATER, FC_CHANNEL, TILE_ORIGIN
    CORE, HALO = 2048, 256
    SCRATCH = SCRATCH + "_smoke"
    FC_CRATER += "_smoke"
    FC_CHANNEL += "_smoke"
    # first tile placed over Ius Chasma (271-286E, 13-6S) on G200
    TILE_ORIGIN = (int((5393998.0 - GRID.ox) / GRID.res),
                   int((GRID.oy - (-355648.0)) / GRID.res))


TILE_ORIGIN = None


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.smoke:
        apply_smoke()
    global CORE, HALO
    if args.core:
        CORE = args.core
    if args.halo:
        HALO = args.halo

    os.makedirs(SCRATCH, exist_ok=True)
    G.check()
    print("=" * 78)
    print("CRATER + CHANNEL CANDIDATES OVER +/-60  (tasks 11 + 12, tiled)")
    if args.smoke:
        print("*** SMOKE TEST - small tiles over Ius Chasma, separate outputs ***")
    print("=" * 78)
    print(" ", GRID)
    print("  tiles       %d cores of %d px + %d px halo  (%.0f km core, %.0f km halo)"
          % (len(tile_list()), CORE, HALO, CORE * GRID.res / 1000, HALO * GRID.res / 1000))
    print("  stream thr  %d cells = %.0f km2" % (THRESH, THRESH_KM2))
    print("  scratch     %s  (internal SSD, KB 2.2)" % SCRATCH)
    if not os.path.exists(DEM):
        print("\n  !! %s missing - run make_global_terrain.py first" % DEM)
        return 1

    ensure_thermal_200()

    if args.skip_coarse:
        print("\ncoarse basin pass SKIPPED")
        coarse = {k: np.array([]) for k in
                  ("diam_km", "depth_max", "depth_mean", "aspect", "fillratio",
                   "lon", "lat")}
    else:
        coarse = coarse_pass()
        if args.only_coarse:
            n = len(coarse["diam_km"])
            print("\n  %d basins >= %.0f km over the whole extent" % (n, COARSE_MIN_DIAM_KM))
            if n:
                d = np.asarray(coarse["diam_km"])
                order = np.argsort(-d)[:15]
                print("  largest:")
                for i in order:
                    print("     %7.1f km  at %7.2fE %+6.2f  depth %6.0f m"
                          % (d[i], coarse["lon"][i], coarse["lat"][i],
                             coarse["depth_max"][i]))
            print("done in %s" % hms(time.time() - T0))
            return 0

    tiles = [] if args.skip_fine else tile_list()
    if args.max_tiles:
        tiles = tiles[:args.max_tiles]
    print("\nfine pass")
    done = 0
    for t in tiles:
        ts = time.time()
        cp, reused = do_tile(t)
        done += 1
        el = time.time() - T0
        print("    tile %3d/%d  %s  %6.1fs   elapsed %s  projected %s"
              % (done, len(tiles), "reused" if reused else "built",
                 time.time() - ts, hms(el), hms(el / done * len(tiles))), flush=True)

    print("\nmerge")
    fcc = FC_BASIN if args.skip_fine else FC_CRATER
    nc, nl = merge_and_write(coarse, fcc, write_channels=not args.skip_fine)
    attribute_thermal(fcc)

    print("\n" + "=" * 78)
    print("  %s crater candidates, %s channel segments over +/-60" % (f"{nc:,}", f"{nl:,}"))
    print("  Both classes are Confidence='inferred'. Landform_CraterRims and")
    print("  Landform_ChannelCenterlines were not touched.")
    print("  This is an inventory of CLOSED DEPRESSIONS - breached craters are")
    print("  invisible to it (KB 26.3, Oudemans). Do not report it as complete.")
    print("done in %s" % hms(time.time() - T0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
