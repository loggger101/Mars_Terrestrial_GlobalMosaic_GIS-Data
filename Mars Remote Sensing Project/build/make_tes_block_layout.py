# -*- coding: utf-8 -*-
r"""T3 by 5° block into the project: where the THEMIS pair tracks calibrated thermal inertia (KB §69.29).

  map "T3a — night IR against TES inertia, 5° blocks (±60°)"
        global60_tes_r5deg_nightIR.tif over the hillshade, the type areas outlined, the 30° graticule;
        global60_tes_r5deg_viking.tif present but off, for comparison
  map "T3b — thermal-contrast index against TES inertia, 5° blocks (±60°)"
        global60_tes_r5deg_index.tif, the same base
  layout 18_t3_tes_blocks
        the two maps over ±60°; one legend in which blue always means "tracks inertia the physical way"
        (night IR positive, the index negative), so the two panels read alike; r by block size and the type
        areas' blocks, every figure read from logs\tes_block_scale.json at run time

The rasters come from make_tes_block_scale.py (nightside TES, measured ~3 km cells, one cell per 5° block).
Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy beside the real .aprx (§31.5).
Run polish_layouts.py afterwards, as after every layout builder.
"""
import os, sys, time, shutil, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import grid60 as G
from layoutkit import text, rect, poly_geom
from make_global60_maps import (outline, add, get_map, order, page, add_text, extent_polygon, CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30
from make_global60_candidate_sheets import table

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
G60 = G.OUTDIR
LOG = os.path.join(HERE, "logs", "tes_block_scale.json")
RASTER = {k: os.path.join(G60, "global60_tes_r5deg_%s.tif" % k) for k in ("nightIR", "index", "viking")}
MAP_A = "T3a — night IR against TES inertia, 5° blocks (±60°)"
MAP_B = "T3b — thermal-contrast index against TES inertia, 5° blocks (±60°)"
L18 = "18_t3_tes_blocks"
# r class bounds, and colours from "the opposite way" to "the physical way": the dataviz reference blue arm
# (steps 600 / 400 / 200), its neutral grey, and a red arm stepped to match
BOUNDS = [-0.30, -0.15, -0.05, 0.05, 0.15, 0.30, 1.0]
AGAINST = [(163, 32, 31), (227, 73, 72), (244, 179, 173)]
NEUTRAL = (240, 239, 236)
WITH = [(158, 197, 244), (57, 135, 229), (24, 79, 149)]
RAMP = AGAINST + [NEUTRAL] + WITH           # index 0 = strongly against ... 6 = strongly with

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def classify_r(layer, sign):
    """Seven r classes; colour by agreement with physics, so sign -1 reverses the ramp."""
    cols = RAMP if sign > 0 else RAMP[::-1]
    labels = ["≤ −0.30", "−0.30 to −0.15", "−0.15 to −0.05", "−0.05 to +0.05", "+0.05 to +0.15",
              "+0.15 to +0.30", "> +0.30"]
    sym = layer.symbology
    sym.updateColorizer("RasterClassifyColorizer")
    sym.colorizer.classificationField = "Value"
    sym.colorizer.breakCount = len(BOUNDS)
    for brk, ub, lab, col in zip(sym.colorizer.classBreaks, BOUNDS, labels, cols):
        brk.upperBound = ub; brk.label = lab; brk.color = {"RGB": list(col) + [100]}
    layer.symbology = sym


def build_map(p, name, main, sign, extra=()):
    m = get_map(p, name)
    ta = add(m, os.path.join(GDB, "Type_Areas"), "Type areas (Ius Chasma, Athabasca Valles)")
    outline(ta, (20, 20, 20), 1.6)
    ext = add(m, os.path.join(GDB, "Analysis_Extent_60"), "Analysis extent ±60°")
    outline(ext, (232, 128, 74), 1.5)
    lr = add(m, RASTER[main[0]], main[1], transparency=15)
    classify_r(lr, sign)
    names = [ta.name, ext.name, lr.name]
    for key, lname, s in extra:
        lx = add(m, RASTER[key], lname, visible=False, transparency=15)
        classify_r(lx, s); names.append(lx.name)
    hs = add(m, os.path.join(G60, "global60_hillshade.tif"), "Hillshade (±60°, 200 m)")
    order(m, names + [hs.name])
    add_graticule(p, name, G30, 7)
    return m


def legend(x, y):
    """One key for both panels: blue = tracks inertia the physical way, whichever sign that is."""
    dark = (40, 40, 40)
    els = [text(x, y, "Colour: r per 5° block, by direction", 9.5, "key_title", bold=True, colour=dark)]
    rows = [(WITH[2], "physical way, |r| > 0.30"), (WITH[1], "physical way, 0.15–0.30"),
            (WITH[0], "physical way, 0.05–0.15"), (NEUTRAL, "none, |r| < 0.05"),
            (AGAINST[2], "opposite way, 0.05–0.15"), (AGAINST[1], "opposite way, 0.15–0.30"),
            (AGAINST[0], "opposite way, |r| > 0.30")]
    yy = y - 0.27
    for i, (col, lab) in enumerate(rows):
        els.append(rect(x, yy, 0.30, 0.17, "key_sw%d" % i, fill=col, stroke=(150, 150, 150), stroke_w=0.4))
        els.append(text(x + 0.40, yy + 0.02, lab, 8.2, "key_lab%d" % i, colour=dark))
        yy -= 0.215
    els.append(text(x, yy - 0.40, "The physical way: night IR r > 0 (rock stays warm);\nthe index r < 0 "
                    "(damped swing = high inertia).\nBlue on both panels = the physical way.", 7.6, "key_note",
                    colour=(70, 70, 70)))
    return els


def sheet(p, ma, mb):
    R = json.load(open(LOG, encoding="utf-8"))
    nt = R["nightside"]; mp = R["map_5deg"]
    lyt = page(p, L18)
    fw, fh = 6.90, 2.30
    ext = extent_polygon()
    for m, y, nm in ((ma, 4.70, "frame_a"), (mb, 1.72, "frame_b")):
        mf = lyt.createMapFrame(poly_geom(0.45, y, fw, fh), m, nm)
        mf.camera.setExtent(ext.projectAs(m.spatialReference).extent)
    fA, fB = mp["files"]["THEMIS night DN"], mp["files"]["diurnal-contrast index"]
    pk = lambda n: nt[n]["by_block_deg"]["5"]["layer"]
    dark, grey = (40, 40, 40), (70, 70, 70)
    rows = [["block", "night IR", "index", "Viking"]]
    for k in ("15", "10", "5", "2", "1", "0.5"):
        rows.append(["%s°" % k] + ["%+.3f" % nt[n]["by_block_deg"][k]["layer"]["pooled"]
                                   for n in ("THEMIS night DN", "diurnal-contrast index", "Viking red")])

    def area_line(a):
        bl = [d for d in mp["type_areas"][a] if d["THEMIS night DN"] is not None]
        rn = [d["THEMIS night DN"] for d in bl]; ri = [d["diurnal-contrast index"] for d in bl]
        rv = [d["Viking red"] for d in bl]
        return "%s (%d blocks): night IR %+.2f to %+.2f, index %+.2f to %+.2f, Viking %+.2f to %+.2f" % (
            a, len(bl), min(rn), max(rn), min(ri), max(ri), min(rv), max(rv))

    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60°: where the THEMIS mosaics track thermal inertia, in 5° blocks (T3)", 18,
             "title", bold=True),
        text(0.45, 7.47, "Correlation with log TES thermal inertia (nightside, measured ~3 km cells) inside each "
             "5° × 5° block (~88,000 km² at the equator).", 10, "subtitle", colour=grey),
        text(0.45, 4.70 + fh + 0.06, "A  Night IR: the physical sign in %.0f %% of {:,} blocks; pooled r %+.3f".format(fA["blocks"])
             % (100 * fA["share_physical_sign"], pk("THEMIS night DN")["pooled"]),
             10, "label_a", bold=True),
        text(0.45, 1.72 + fh + 0.06, ("B  Diurnal-contrast index: the physical sign in %.0f %% of {:,} blocks; "
             "pooled r %+.3f").format(fB["blocks"]) % (100 * fB["share_physical_sign"], pk("diurnal-contrast index")["pooled"]),
             10, "label_b", bold=True),
        text(7.65, 3.70, "Pooled within-block r by block size", 9.5, "table_title", bold=True, colour=dark),
        text(0.45, 1.20, area_line("Ius Chasma") + ".\n" + area_line("Athabasca Valles") + ".", 7.9,
             "areas", colour=dark),
        text(0.45, 0.64, "The 5° blocks show where a weak signal holds; one block's r is noisy (10,000 cells, "
             "strongly autocorrelated), so read the pattern, not a single block. The THEMIS mosaics are\n"
             "contrast-stretched region by region, so a block can only compare places with one another, never "
             "two blocks. Viking red, the albedo, is in map T3a (off) for comparison (KB §43.1, §69.29).",
             7.9, "notes", colour=dark),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + legend(7.65, 6.95)
        + table(7.65, 3.62, rows, [0.62, 0.76, 0.76, 0.76], size=7.8)
        + [text(7.65, 3.62 - 7 * 0.20 - 0.42, "Strongest at 2–5°; below 2° the 3 km TES grid runs out.\n"
                "Shifted 180°, every layer scores ≈ 0 at every size.", 7.6, "table_note", colour=grey)])
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L18 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    for k, v in RASTER.items():
        assert os.path.exists(v), "run make_tes_block_scale.py first: %s" % v
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("1. map:", MAP_A)
    ma = build_map(p, MAP_A, ("nightIR", "Night IR r with TES inertia, 5° blocks"), +1,
                   extra=[("viking", "Viking red r with TES inertia, 5° blocks", -1)])
    print("2. map:", MAP_B)
    mb = build_map(p, MAP_B, ("index", "Thermal-contrast index r with TES inertia, 5° blocks"), -1)
    print("3. layout", L18)
    sheet(p, ma, mb)
    p.save()
    for name in (MAP_A, MAP_B):
        m = next(x for x in p.listMaps() if x.name == name)
        print("   %s: %s" % (name, [l.name for l in m.listLayers()]))
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
