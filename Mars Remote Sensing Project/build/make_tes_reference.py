# -*- coding: utf-8 -*-
r"""TES thermal inertia (Putzig & Mellon 2007) as GeoTIFFs, with the orientation PROVED (KB §41).

Downloaded 2026-10-08 to Mars Project\Reference\TES_thermal_inertia_2007\ (NEXT-STEPS D5d):
DBmap2007.bin / NBmap2007.bin (dayside / nightside), 14,400-byte ASCII header then 3600 records of
7200 big-endian int16, 0 = no data, 5-5000 tiu; DBmsk2007.bin / NBmsk2007.bin the interpolation
masks (7,200-byte header, uint8). Read: 1 on ~90 % of pixels, so 1 = MEASURED, 0 = interpolated or
no data (the page says under 8 % is infilled; 3.2 % is no data poleward of 87°). The header says longitudes run "0 W to 360 W" and
latitudes "-90 N to 90 N": first row south, columns WEST longitude.

An orientation read wrongly is silent (KB §4). So the four candidates (rows south- or north-first,
columns west or east) are each correlated with Viking red over ±60°; dust is bright and has low
thermal inertia, so the right one is the strongly negative one. The script refuses to write
unless the documented orientation is that one.

Output (north-up, east longitude -180..180, 0.05°, GCS_Mars_2000_Sphere), beside the downloads:
TES_TI_2007_dayside.tif, _nightside.tif (Int16, nodata 0) and _measured.tif files (Byte, 1 =
measured). Use measured pixels only for any test. Read-only on the downloads.
"""
import os, sys, json
import numpy as np
from osgeo import gdal, osr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive

gdal.UseExceptions()
REF = on_drive(r"Mars Project\Reference\TES_thermal_inertia_2007")
VIK = os.path.join(HERE, "pres1_img", "_global60_viking_red.npy")   # ±60°, CM 180 (east 0..360), north up
NX, NY, STEP = 7200, 3600, 0.05
PROVINCES = {                 # east longitude -180..180, latitude; the boxes of KB §28.10's figure
    "Tharsis (dusty)": (-120, -100, 5, 25), "Arabia Terra (dusty)": (0, 20, 10, 30),
    "Amazonis (dusty)": (-170, -145, 20, 40), "Syrtis Major (rocky)": (65, 80, 0, 15),
    "Acidalia (rocky)": (-30, -10, 35, 55)}
WKT_GCS = ('GEOGCS["GCS_Mars_2000_Sphere",DATUM["D_Mars_2000_Sphere",SPHEROID["Mars_2000_Sphere_IAU_IAG",'
           '3396190.0,0.0]],PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]]')


def read(fn, header, dtype):
    raw = np.fromfile(os.path.join(REF, fn), dtype=np.uint8)
    a = raw[header:].view(dtype)
    assert a.size == NX * NY, (fn, a.size)
    # to NATIVE byte order: numpy reads >i2 correctly, but GDAL's WriteArray writes the raw bytes,
    # so a big-endian array came out byte-swapped (Tharsis read 9728 tiu instead of 38) -- caught by
    # the province check that now runs after every write
    return a.reshape(NY, NX).astype(np.dtype(dtype).newbyteorder("="))


def to_east_north(a, south_first, west):
    """-> rows north-first, columns east longitude 0..360 (first column 0-0.05 °E)."""
    b = a[::-1] if south_first else a
    if west:
        # column j covers west longitude [j*0.05, (j+1)*0.05) = east (360 - (j+1)*0.05, 360 - j*0.05]
        b = b[:, ::-1]
    return b


def block_mean_60(b, nx, ny):
    """Rows covering 60N..60S, block-averaged (no-data excluded) to ny x nx."""
    r0, r1 = int(30 / STEP), int(150 / STEP)          # 90N->60N is 600 rows
    c = b[r0:r1].astype(np.float64)
    v = c > 0
    fy, fx = c.shape[0] / ny, c.shape[1] / nx
    yi = (np.arange(c.shape[0]) / fy).astype(int).clip(0, ny - 1)
    xi = (np.arange(c.shape[1]) / fx).astype(int).clip(0, nx - 1)
    s = np.zeros((ny, nx)); n = np.zeros((ny, nx))
    np.add.at(s, (yi[:, None], xi[None, :]), np.where(v, c, 0))
    np.add.at(n, (yi[:, None], xi[None, :]), v)
    return np.where(n > 0, s / np.maximum(n, 1), np.nan)


def write(path, arr, dtype, nodata):
    # east 0..360 -> -180..180: roll by half the width
    out = np.roll(arr, NX // 2, axis=1)
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(path, NX, NY, 1, dtype, ["TILED=YES", "COMPRESS=DEFLATE"])
    ds.SetGeoTransform((-180.0, STEP, 0, 90.0, 0, -STEP))
    ds.SetProjection(WKT_GCS)
    b = ds.GetRasterBand(1); b.WriteArray(out)
    if nodata is not None:
        b.SetNoDataValue(nodata)
    b.ComputeStatistics(False)
    ds = None


def main():
    vik = np.load(VIK).astype(np.float64)
    ny, nx = vik.shape
    res = {}
    for side, prefix in (("dayside", "DB"), ("nightside", "NB")):
        ti = read(prefix + "map2007.bin", 14400, ">i2")
        msk = read(prefix + "msk2007.bin", 7200, np.uint8)
        print(side, "range", int(ti[ti > 0].min()), int(ti.max()), "no-data share %.4f" % (ti == 0).mean(),
              "measured share %.4f" % (msk == 1).mean())
        trials = {}
        for sf in (True, False):
            for west in (True, False):
                g = block_mean_60(to_east_north(ti, sf, west), nx, ny)
                ok = np.isfinite(g) & np.isfinite(vik)
                r = float(np.corrcoef(np.log(g[ok]), vik[ok])[0, 1])
                trials["rows %s, columns %s" % ("south-first" if sf else "north-first", "west" if west else "east")] = r
        for k, r in sorted(trials.items(), key=lambda kv: kv[1]):
            print("   %-38s r(log TI, Viking red) = %+.3f" % (k, r))
        doc = "rows south-first, columns west"
        best = min(trials, key=trials.get)
        if best != doc:
            raise SystemExit("REFUSING: the documented orientation (%s) is not the most negative (%s)" % (doc, best))
        res[side] = {"r_by_orientation": trials, "chosen": doc}
        write(os.path.join(REF, "TES_TI_2007_%s.tif" % side), to_east_north(ti, True, True), gdal.GDT_Int16, 0)
        write(os.path.join(REF, "TES_TI_2007_%s_measured.tif" % side), to_east_north(msk, True, True), gdal.GDT_Byte, None)
        print("   wrote TES_TI_2007_%s.tif and _measured.tif" % side)
        # read the written file back: values must be in the documented 5-5000 tiu, and the dusty
        # provinces must sit below the rocky ones (the §28.10 boxes)
        chk = gdal.Open(os.path.join(REF, "TES_TI_2007_%s.tif" % side)).ReadAsArray().astype(float)
        assert chk.max() <= 5000, "written values out of range: byte order?"
        med = {}
        for name, (lo0, lo1, la0, la1) in PROVINCES.items():
            v = chk[int((90 - la1) / STEP):int((90 - la0) / STEP), int((lo0 + 180) / STEP):int((lo1 + 180) / STEP)]
            med[name] = float(np.median(v[v > 0]))
        dusty = np.mean([med[k] for k in med if "dusty" in k]); rocky = np.mean([med[k] for k in med if "rocky" in k])
        print("   read back: " + ", ".join("%s %.0f" % kv for kv in med.items()) + "  -> dusty %.0f < rocky %.0f" % (dusty, rocky))
        assert dusty < rocky, "dusty provinces not below rocky ones"
        res[side]["province_medians_tiu"] = med
    json.dump(res, open(os.path.join(HERE, "logs", "tes_reference.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
