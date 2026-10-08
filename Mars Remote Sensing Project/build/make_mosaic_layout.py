# -*- coding: utf-8 -*-
r"""The mosaic itself at ±60°, as a layout: visible, day IR, night IR and topography (KB §38).

The project is the Mars Global Mosaic, and until this sheet no layout showed the mosaic: 01-03 are
the Ius type area, 04-07 are products made from it. This adds four small maps, one per panel so
each frame shows its own layer live in Pro (KB §31.1), and layout 08_global60_mosaic:

  "Mosaic ±60° — visible"     Viking MDIM 2.1 colour   stack bands 1-3
  "Mosaic ±60° — day IR"      THEMIS day IR            stack band 5
  "Mosaic ±60° — night IR"    THEMIS night IR          stack band 4
  "Mosaic ±60° — topography"  HRSC/MOLA DEM over its hillshade

The three image panels read global60_svm_stack_200m.tif (KB §31.2): G200, every band already
stretched p1/p99 -> 1-255 over ±60°, with overviews, so the page draws from a 200 m product off one
file instead of three 14 GB sources without pyramids. The diurnal-contrast index is deliberately
NOT a panel: at ±60° it is local texture, never a material map (KB §28.10).

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must
sit BESIDE the real .aprx (it stores relative paths, §31.5). Run polish_layouts.py afterwards (§33).
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grid60 as G
from layoutkit import text, rgb, poly_geom
from make_global60_maps import get_map, page, add_text, CREDIT, BKDIR, OUTD

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else r"Z:\Mars Project\Mars Project.aprx")
STACK = os.path.join(G.OUTDIR, "global60_svm_stack_200m.tif")     # not the junction (KB §34)
DEM = os.path.join(G.OUTDIR, "global60_dem.tif")
HS = os.path.join(G.OUTDIR, "global60_hillshade.tif")
NAME = "08_global60_mosaic"
VIS, DAY, NIGHT, TOPO = ("Mosaic \u00b160\u00b0 \u2014 " + s for s in ("visible", "day IR", "night IR", "topography"))

# The four maps draw in the stack's own CRS (Mars_Equidistant_Cylindrical_CM180), not the GCS the
# other ±60° maps use: reprojected, the raster's edge at 0°/360° left a white seam down the middle
# of each small frame. Native, the edges are the frame edges and nothing is resampled.
NATIVE = arcpy.Describe(STACK).spatialReference
EXTENT = arcpy.Describe(STACK).extent

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def band(name):
    """One band of the stack as its own layer. Esri names the bands by their descriptions
    (viking_red ... relief_m), not Band_<n>."""
    return os.path.join(STACK, name)


def unstretched(layer):
    """The stack is already stretched p1/p99 -> 1-255 (KB §31.2): draw it linear, no second stretch."""
    d = layer.getDefinition("V3")
    c = d.colorizer
    c.stretchType = "None"
    c.useGammaStretch = False
    c.noDataColor = rgb(0, 0, 0)          # the 2.7 % without THEMIS cover: black, not the page's white
    layer.setDefinition(d)


def one_layer_map(p, name, path, label):
    m = get_map(p, name)
    m.spatialReference = NATIVE
    l = m.addDataFromPath(path); l.name = label; l.visible = True
    return m, l


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    os.makedirs(OUTD, exist_ok=True)
    p = arcpy.mp.ArcGISProject(APRX)

    print("1. maps")
    mv, lv = one_layer_map(p, VIS, STACK, "Viking MDIM 2.1 colour (bands 1\u20133 of the \u00b160\u00b0 stack)")
    d = lv.getDefinition("V3")                      # R, G, B = bands 1, 2, 3 (0-based indices)
    d.colorizer.redBandIndex, d.colorizer.greenBandIndex, d.colorizer.blueBandIndex = 0, 1, 2
    lv.setDefinition(d)
    unstretched(lv)
    md, ld = one_layer_map(p, DAY, band("day_ir"),"THEMIS Day IR (band 5 of the \u00b160\u00b0 stack)")
    unstretched(ld)
    mn, ln = one_layer_map(p, NIGHT, band("night_ir"),"THEMIS Night IR (band 4 of the \u00b160\u00b0 stack)")
    unstretched(ln)
    mt = get_map(p, TOPO)
    mt.spatialReference = NATIVE
    dem = mt.addDataFromPath(DEM); dem.name = "Elevation, HRSC/MOLA blend (200 m)"
    hs = mt.addDataFromPath(HS); hs.name = "Hillshade 225\u00b0/45\u00b0"
    sym = dem.symbology
    ramp = next((r for r in p.listColorRamps("Elevation #1")), None)
    if ramp is not None:
        sym.colorizer.colorRamp = ramp
    dem.symbology = sym
    dem.transparency = 35
    mt.moveLayer(dem, hs, "AFTER")                  # (reference, moved): hillshade goes under the colour
    for m in (mv, md, mn, mt):
        print("   %s: %s" % (m.name, [l.name for l in m.listLayers()]))

    print("2. layout", NAME)
    lyt = page(p, NAME)
    fw = 4.8; fh = fw / 3.0                          # ±60° x 360° is 3:1
    xl, xr = 0.45, 5.75
    yt, yb = 5.20, 2.55                              # frame bottoms, top row and bottom row
    frames = [(mv, xl, yt), (md, xr, yt), (mn, xl, yb), (mt, xr, yb)]
    for i, (m, x, y) in enumerate(frames):
        mf = lyt.createMapFrame(poly_geom(x, y, fw, fh), m, "frame%d" % (i + 1))
        mf.camera.setExtent(EXTENT)
    grey, dark = (70, 70, 70), (40, 40, 40)
    head = 11; cap = 8.3
    add_text(lyt, [
        text(0.45, 7.85, "Mars Global Mosaic \u2014 the inputs at \u00b160\u00b0", 21, "title", bold=True),
        text(0.45, 7.52, "Visible colour, thermal infrared by day and by night, and topography, each on the "
             "same 200 m grid of the analysis extent.", 10, "subtitle", colour=grey),
        # top row
        text(xl, yt + fh + 0.08, "A  Visible: Viking MDIM 2.1 colour", head, "hA", bold=True),
        text(xl, yt - 0.42, "Real albedo. Bright dust (Arabia, Tharsis, Amazonis) against dark, rocky\n"
             "Syrtis Major and Acidalia: 47.7 DN apart in the red band.", cap, "cA", colour=dark),
        text(xr, yt + fh + 0.08, "B  THEMIS Day IR", head, "hB", bold=True),
        text(xr, yt - 0.42, "Bright = warm by day. Dust is bright in visible light and cool by day:\n"
             "r = \u22120.49 against Viking at Ius Chasma, \u22120.15 across \u00b160\u00b0.", cap, "cB", colour=dark),
        # bottom row
        text(xl, yb + fh + 0.08, "C  THEMIS Night IR", head, "hC", bold=True),
        text(xl, yb - 0.42, "Bright = warmer at night than its surroundings: rock and coarse material\n"
             "hold heat. The most independent band: |r| \u2264 0.12 against every other at Ius.", cap, "cC",
             colour=dark),
        text(xr, yb + fh + 0.08, "D  Topography: HRSC/MOLA blended DEM", head, "hD", bold=True),
        text(xr, yb - 0.42, "Pale blue lowest, then green, red-brown, white highest: \u22128.5 km (Hellas)\n"
             "to +21.2 km (Olympus Mons), over a 225\u00b0 hillshade. Not a classification band (KB \u00a731.2).",
             cap, "cD",
             colour=dark),
        # the argument, and the caveat that limits it
        text(0.45, 1.05, "Why all three: at Ius Chasma the three Viking bands correlate 0.93\u20130.99 with each other, "
             "so visible colour is one dimension; day IR and night IR\nadd two more. Effective dimensionality \u2248 3. "
             "Caveat: both THEMIS mosaics are locally contrast-normalised 8-bit products, so compare brightness\n"
             "within a region, never across the planet (KB \u00a728.10). Across \u00b160\u00b0 the regional material "
             "signal is carried by Viking albedo.\nEach panel is drawn on the mosaics' own grid, centred on 180°E. "
             "Black streaks in the south: no THEMIS cover there; the stack keeps only pixels valid in every band "
             "(97.3 %).", 8.6, "notes", colour=dark),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))])
    out = os.path.join(OUTD, NAME + ".png")
    t = time.time(); lyt.exportToPNG(out, resolution=150)
    print("   %s (%.0f s)" % (out, time.time() - t))
    p.save()
    print("saved. layouts:", [x.name for x in p.listLayouts()])


if __name__ == "__main__":
    main()
