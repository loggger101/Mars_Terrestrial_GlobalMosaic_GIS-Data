# -*- coding: utf-8 -*-
r"""Layout 15: the Athabasca Valles type area in its four inputs (KB §63).

Athabasca Valles is the project's scientific hook (flood lava once read as a water-cut channel), but
until this sheet its only layout was 09, candidates over a hillshade. Ius Chasma has its visible and
night-IR sheets (01, 02); this gives the second type area the same, in the four-panel form of
layout 08, one small map per panel so each frame shows its own layer live in Pro (KB §31.1):

  "Athabasca Valles — visible"     ath_viking.tif   Viking MDIM 2.1 colour, 100 m
  "Athabasca Valles — night IR"    ath_night.tif    THEMIS Night IR v14
  "Athabasca Valles — day IR"      ath_day.tif      THEMIS Day IR v12
  "Athabasca Valles — topography"  ath_dem.tif over ath_hillshade.tif

On every panel: unit lAv (Late Amazonian volcanic) of the USGS geologic map SIM 3292, the project's
lava-flow reference, as an outline, and the 2° graticule. The diurnal-contrast index is not a panel:
at Athabasca it does not track calibrated inertia (KB §42.4). The DEM's range in the caption is read
from the raster at run time, never typed.

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must sit
BESIDE the real .aprx (it stores relative paths, §31.5). Run polish_layouts.py afterwards (§33).
"""
import os, sys, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy
import numpy as np

import areas
from layoutkit import text, poly_geom, rect
from make_global60_maps import get_map, page, add_text, outline, BKDIR, OUTD
from make_reference_maps import add_graticule, G2

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
AREA = dict(areas.AREAS["ath"])
DIR = on_drive(os.path.join("Mars Project", AREA["folder"]))
GDB = on_drive(r"Mars Project\Mars Project.gdb")
NAME = "15_athabasca_type_area"
VIS, NIGHT, DAY, TOPO = ("Athabasca Valles — " + s for s in ("visible", "night IR", "day IR", "topography"))
LAV = "Unit lAv, Late Amazonian volcanic (USGS SIM 3292)"
LAV_RGB = (255, 120, 0)
CREDIT = ("Logan M Edwards  ·  OCN 4704 Remote Sensing  ·  Mars Global Mosaic\n"
          "Equidistant Cylindrical, central meridian 180°, Mars 2000 sphere (R = 3 396 190 m)  ·  "
          "100 m/pixel  ·  150–162°E, 4–14°N")

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def tif(stem):
    return os.path.join(DIR, "%s_%s.tif" % (AREA["prefix"], stem))


def dem_range():
    """Lowest and highest elevation in the window, metres, from the raster itself."""
    r = arcpy.Raster(tif("dem"))
    a = arcpy.RasterToNumPyArray(r).astype("float64")
    nd = r.noDataValue
    if nd is not None:
        a = a[a != nd]
    return int(round(a.min())), int(round(a.max()))


def lav_outline(m):
    l = m.addDataFromPath(os.path.join(GDB, "Ref_SIM3292_GeologicUnits"))
    l.name = LAV
    l.definitionQuery = "Unit = 'lAv'"
    outline(l, LAV_RGB, 1.4)
    return l


def panel_map(p, name, stem, label):
    m = get_map(p, name)
    m.spatialReference = arcpy.Describe(tif(stem)).spatialReference
    lav_outline(m)
    r = m.addDataFromPath(tif(stem)); r.name = label
    return m, r


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    os.makedirs(OUTD, exist_ok=True)
    lo, hi = dem_range()
    print("DEM range %d to %d m" % (lo, hi))
    p = arcpy.mp.ArcGISProject(APRX)

    print("1. maps")
    mv, lv = panel_map(p, VIS, "viking", "Viking MDIM 2.1 colour (100 m)")
    mn, ln = panel_map(p, NIGHT, "night", "THEMIS Night IR v14 (100 m)")
    md, ld = panel_map(p, DAY, "day", "THEMIS Day IR v12 (100 m)")
    mt = get_map(p, TOPO)
    mt.spatialReference = arcpy.Describe(tif("dem")).spatialReference
    lav_outline(mt)
    dem = mt.addDataFromPath(tif("dem")); dem.name = "Elevation, HRSC/MOLA blend"
    hs = mt.addDataFromPath(tif("hillshade")); hs.name = "Hillshade 225°/45°"
    sym = dem.symbology
    ramp = next((r for r in p.listColorRamps("Elevation #1")), None)
    if ramp is not None:
        sym.colorizer.colorRamp = ramp
    dem.symbology = sym
    dem.transparency = 35
    mt.moveLayer(dem, hs, "AFTER")                  # hillshade under the colour, as layout 08
    for m in (mv, mn, md, mt):
        add_graticule(p, m.name, G2, 6)
        print("   %s: %s" % (m.name, [l.name for l in m.listLayers()]))

    print("2. layout", NAME)
    lyt = page(p, NAME)
    aspect = AREA_W / AREA_H
    fh = 2.50; fw = fh * aspect
    xl, xr = 0.45, 5.62
    yt, yb = 4.33, 1.30
    frames = []
    for i, (m, ref, x, y) in enumerate([(mv, lv, xl, yt), (mn, ln, xr, yt), (md, ld, xl, yb), (mt, dem, xr, yb)]):
        mf = lyt.createMapFrame(poly_geom(x, y, fw, fh), m, "frame%d" % (i + 1))
        mf.camera.setExtent(mf.getLayerExtent(ref, False, True))
        frames.append(mf)
    cx_l, cx_r = xl + fw + 0.14, xr + fw + 0.14
    grey, dark = (70, 70, 70), (40, 40, 40)
    head, cap = 11, 8.2
    add_text(lyt, [
        text(0.45, 7.85, "Athabasca Valles type area: the four inputs", 21, "title", bold=True),
        text(0.45, 7.30, "The flood-lava type area, 150–162°E, 4–14°N, on its 100 m grid: once "
             "read as a water-cut outflow channel, now as flood lava.\nOrange outline on every panel: unit lAv "
             "(Late Amazonian volcanic) of the USGS geologic map SIM 3292, the project's lava-flow reference.",
             9.5, "subtitle", colour=grey),
        text(xl, yt + fh + 0.08, "A  Visible: Viking MDIM 2.1 colour", head, "hA", bold=True),
        text(cx_l, yt + 0.05, "232 m resampled to 100 m.\nThe three bands correlate\n0.81–0.95 with each "
             "other:\none dimension of albedo.\n\nAgainst TES thermal inertia\n(~3 km cells): r −0.55 "
             "dayside,\n−0.64 nightside. The only\nlayer here that tracks it\n(KB §42.4).",
             cap, "cA", colour=dark),
        text(xr, yt + fh + 0.08, "B  THEMIS Night IR", head, "hB", bold=True),
        text(cx_r, yt + 0.05, "Bright = warmer at night\nthan its surroundings.\nThe most independent band:\n"
             "|r| ≤ 0.15 against every\nother (KB §42.1).\n\nr +0.05 against TES inertia:\n"
             "local contrast, not\ncalibrated thermal inertia\n(KB §28.10).", cap, "cB", colour=dark),
        text(xl, yb + fh + 0.08, "C  THEMIS Day IR", head, "hC", bold=True),
        text(cx_l, yb + 0.85, "Bright = warm by day.\nr −0.35 to −0.42 against\nthe visible bands: "
             "dust is\nbright in visible light and\ncool by day (KB §42.1).", cap, "cC", colour=dark),
        text(xr, yb + fh + 0.08, "D  Topography: HRSC/MOLA blended DEM", head, "hD", bold=True),
        text(cx_r, yb + 0.85, "%s to %s m, low to high:\ncyan, yellow-green, red-\nbrown, white, over a 225° "
             "hillshade.\nSmooth lava plains: mean\nslope 1.8°; 97 %% of the\nchannel candidates lie "
             "under\n2° (layout 09)." % (format(lo, ",").replace("-", "−"),
                                               format(hi, ",").replace("-", "−")),
             cap, "cD", colour=dark),
        text(0.45, 0.58, "Test T5 (H1): across the 10 lAv contacts (905 profiles) each band separates 11–21 % "
             "against 10 % for random lines; day IR leans toward H1, unresolved. At 1:20 M the\ncontacts are "
             "generalised by kilometres (KB §47.2). Test T2: lAv is the least cratered large unit here, "
             "1,122 Robbins craters ≥ 1 km per 10⁶ km² against 1,760 (AHv)\nand 2,183 (HNt) "
             "(KB §42.2). The diurnal-contrast index is not a panel: here it does not track calibrated "
             "inertia (KB §42.4).", 7.8, "notes", colour=dark),
        # the lAv outline's key: a drawn swatch, smaller than a legend element
        rect(cx_l, yt + fh - 0.22, 0.34, 0.16, "lav_swatch", fill=(255, 255, 255), stroke=LAV_RGB, stroke_w=1.4),
        text(cx_l + 0.44, yt + fh - 0.30, "Unit lAv, Late Amazonian\nvolcanic (USGS SIM 3292)", cap, "lav_key",
             colour=dark),
        text(0.45, 0.22, CREDIT, 7.5, "credit", colour=(90, 90, 90))])
    items = p.listStyleItems("ArcGIS 2D", "SCALE_BAR")
    sb = lyt.createMapSurroundElement(arcpy.Point(cx_r, yb + 0.20), "SCALE_BAR", frames[3],
                                      next((i for i in items if i.name == "Double Alternating Scale Bar 1 Metric"),
                                           items[0]), "sbar")
    d = sb.getDefinition("V3")                       # 0, 100, 200 km: the default crammed six labels
    d.divisions, d.subdivisions, d.division = 2, 0, 100.0
    d.labelFrequency = "Divisions"                   # not "...AndFirstMidpoint", which added a 25
    d.fittingStrategy = "AdjustFrame"
    sb.setDefinition(d)
    out = os.path.join(OUTD, NAME + ".png")
    t = time.time(); lyt.exportToPNG(out, resolution=150)
    print("   %s (%.0f s)" % (out, time.time() - t))
    p.save()
    print("saved. layouts:", sorted(x.name for x in p.listLayouts()))


xmin, ymin, xmax, ymax = AREA["bounds"]
AREA_W, AREA_H = xmax - xmin, ymax - ymin

if __name__ == "__main__":
    main()
