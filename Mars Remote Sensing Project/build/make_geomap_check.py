# -*- coding: utf-8 -*-
r"""Test T8: the ±60° landform classification against the USGS geologic map (KB §43, NEXT-STEPS §4).

The classes (Crater, steep/windy hills, lava tube, Normal Ground) are landforms; SIM 3292's units
are geologic. So this is not an accuracy: it asks whether each class concentrates where the map
says it should. Enrichment = P(class | unit group) / P(class), area-weighted (cos latitude); 1 =
no association, > 1 = the class is over-represented there.

Prediction, written before the run: "lava tube" NOT enriched in the volcanic groups (v, ve, vf),
because §31.3 found it right 2 % of the time; "Crater" enriched in the impact (i) and highland (h)
groups; "Normal Ground" enriched in the lowland / plains groups (l, p).

The 5 x 5 majority map (§32.2) is read at its 1.6 km overview; unit groups are rasterised on a
0.02° lon/lat grid and sampled at each pixel's centre. Read-only; writes build\logs\geomap_check.json.
"""
import os, sys, json
import numpy as np
from osgeo import gdal, ogr, osr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB
import grid60 as G

gdal.UseExceptions(); ogr.UseExceptions()
CLS = os.path.join(G.OUTDIR, "global60_landforms_svm_400m_mode5.tif")
NAMES = {1: "Crater", 2: "steep/windy hills", 3: "lava tube", 4: "Normal Ground"}
OUT = os.path.join(HERE, "logs", "geomap_check.json")
STEP = 0.02
GROUPS_OF_INTEREST = ["v", "ve", "vf", "i", "h", "hu", "l", "p", "t", "a"]


def unit_raster():
    """Unit-group codes on a 0.02° grid, -180..180 x -60..60, rasterised from the gdb class."""
    import arcpy
    feats, codes = [], {}
    with arcpy.da.SearchCursor(os.path.join(GDB, "Ref_SIM3292_GeologicUnits"), ["SHAPE@WKT", "UnitGroup"]) as c:
        for wkt, g in c:
            codes.setdefault(g, len(codes) + 1)
            feats.append((wkt, codes[g]))
    mem = ogr.GetDriverByName("MEM").CreateDataSource("u")
    lyr = mem.CreateLayer("u", geom_type=ogr.wkbMultiPolygon)
    lyr.CreateField(ogr.FieldDefn("code", ogr.OFTInteger))
    for wkt, k in feats:
        f = ogr.Feature(lyr.GetLayerDefn()); f.SetGeometry(ogr.CreateGeometryFromWkt(wkt)); f.SetField("code", k)
        lyr.CreateFeature(f)
    W, H = int(360 / STEP), int(120 / STEP)
    ds = gdal.GetDriverByName("MEM").Create("", W, H, 1, gdal.GDT_Byte)
    ds.SetGeoTransform((-180.0, STEP, 0, 60.0, 0, -STEP))
    gdal.RasterizeLayer(ds, [1], lyr, options=["ATTRIBUTE=code"])
    return ds.ReadAsArray(), {v: k for k, v in codes.items()}


def main():
    units, names_of = unit_raster()
    ds = gdal.Open(CLS)
    band = ds.GetRasterBand(1)
    gt = ds.GetGeoTransform()
    o = min((band.GetOverview(i) for i in range(band.GetOverviewCount())),
            key=lambda ov: abs(gt[1] * band.XSize / ov.XSize - 1600))
    cell = gt[1] * band.XSize / o.XSize
    cls = o.ReadAsArray()
    H, W = cls.shape
    xs = gt[0] + (np.arange(W) + .5) * cell
    ys = gt[3] - (np.arange(H) + .5) * cell
    lon = (180.0 + np.degrees(xs / G.R_MARS) + 180.0) % 360.0 - 180.0
    lat = np.degrees(ys / G.R_MARS)
    col = ((lon + 180.0) / STEP).astype(int).clip(0, units.shape[1] - 1)
    row = ((60.0 - lat) / STEP).astype(int).clip(0, units.shape[0] - 1)
    u = units[row[:, None], col[None, :]]
    w = np.repeat(np.cos(np.radians(lat))[:, None], W, axis=1)
    ok = np.isin(cls, list(NAMES)) & (u > 0)
    print("classification read at %.0f m: %d x %d; %.1f%% of pixels have both a class and a unit" % (cell, W, H, 100 * ok.mean()))
    c, g, ww = cls[ok], u[ok], w[ok]
    p_class = {k: ww[c == k].sum() / ww.sum() for k in NAMES}
    res = {"cell_m": cell, "p_class": {NAMES[k]: float(v) for k, v in p_class.items()}, "groups": {}}
    print("\n  %-6s %8s   %s" % ("group", "area %", "   ".join("%-18s" % NAMES[k] for k in NAMES)))
    for code, gname in sorted(names_of.items(), key=lambda kv: kv[1]):
        sel = g == code
        if not sel.any():
            continue
        share = ww[sel].sum() / ww.sum()
        if gname not in GROUPS_OF_INTEREST and share < 0.02:
            continue
        enr = {}
        for k in NAMES:
            pc_g = ww[sel & (c == k)].sum() / ww[sel].sum()
            enr[NAMES[k]] = {"share_in_group": float(pc_g), "enrichment": float(pc_g / p_class[k])}
        res["groups"][gname] = {"area_share": float(share), "classes": enr}
        print("  %-6s %7.1f%%   %s" % (gname, 100 * share, "   ".join(
            "%5.1f%% (x%.2f)      " % (100 * enr[NAMES[k]]["share_in_group"], enr[NAMES[k]]["enrichment"]) for k in NAMES)))
    json.dump(res, open(OUT, "w"), indent=1)
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
