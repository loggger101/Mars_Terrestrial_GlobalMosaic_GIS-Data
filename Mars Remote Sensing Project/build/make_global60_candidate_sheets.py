# -*- coding: utf-8 -*-
r"""Layouts 11 and 12: the ±60° fine pass as two sheets (KB §53.6, §55.4).

  11_global60_depressions   closed depressions >= 1 km per 0.5° cell, beside the Robbins & Hynek 2020
                            catalogue on the same colour breaks; the Robbins table of
                            logs\global60_candidates_check.json; the blind spots
  12_global60_channels      the channel network, Strahler order >= 3, over the ±60° hillshade; the
                            order counts; the blind spots (plateau routing, first-order threshold)

Inputs: Landform_CraterCandidates_auto_60, Landform_ChannelCandidates_auto_60 (make_global_landforms.py),
Ref_Craters_Robbins2020, logs\global60_candidates_check.json (verify_global60_candidates.py, run first).
Writes two density rasters on the CM 180 grid, 720 x 240 cells of 0.5°, Int16 counts per 10^4 km² of
true (spherical) area, NoData -1:
  Global60\global60_depression_density_0p5deg.tif   the detector's candidates, D >= 1 km
  Global60\global60_robbins_density_0p5deg.tif      Robbins craters, D >= 1 km, |lat| <= 60°
and logs\global60_candidate_sheets.json (the numbers printed on the sheets).

The channel plateau share is measured, not assumed: the 200 m slope under the midpoint of every
24th segment (KB §53.6).

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must sit
BESIDE the real .aprx (it stores relative paths, §31.5). Builder order: after make_reference_maps.py
(this adds its own 30° graticules), then polish_layouts.py.
"""
import os, sys, time, shutil, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import numpy as np
from osgeo import gdal
import arcpy
import grid60 as G
from layoutkit import text, poly_geom, rect, cell_text
from make_global60_maps import (add, get_map, page, add_text, legend_classes, order, extent_polygon,
                                CREDIT, BKDIR, OUTD)
from make_reference_maps import add_graticule, G30

gdal.UseExceptions()
APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
CRAT = os.path.join(GDB, "Landform_CraterCandidates_auto_60")
CHAN = os.path.join(GDB, "Landform_ChannelCandidates_auto_60")
ROBBINS = os.path.join(GDB, "Ref_Craters_Robbins2020")
CHECK = os.path.join(HERE, "logs", "global60_candidates_check.json")
DENS_C = os.path.join(G.OUTDIR, "global60_depression_density_0p5deg.tif")
DENS_R = os.path.join(G.OUTDIR, "global60_robbins_density_0p5deg.tif")
SLOPE = os.path.join(G.OUTDIR, "global60_slope_deg.tif")
LOG = os.path.join(HERE, "logs", "global60_candidate_sheets.json")
M_DEP, M_ROB, M_CHAN = ("Mars ±60° — closed depressions", "Mars ±60° — Robbins craters",
                        "Mars ±60° — channels")
L11, L12 = "11_global60_depressions", "12_global60_channels"
R_KM = 3396.19
NX, NY, CELL_DEG = 720, 240, 0.5
# counts per 10^4 km2: medians ~18 (detector) and ~22 (Robbins), p99 ~210 / ~130 (KB §53.6)
BREAKS = [(0, "none", (225, 225, 225)), (5, "1–5", (255, 245, 204)), (15, "5–15", (254, 217, 118)),
          (40, "15–40", (253, 141, 60)), (100, "40–100", (227, 26, 28)),
          (250, "100–250", (177, 0, 38)), (1000, "> 250", (90, 0, 30))]

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


# ------------------------------------------------------------------ data
def density(lonlat, path):
    """Counts per 10^4 km2 in 0.5° cells, rows from 60°N down, columns from 0°E (the CM 180 grid's
    left edge), written on the ±60° grid's own extent."""
    lat_e = np.linspace(60, -60, NY + 1); lon_e = np.linspace(0, 360, NX + 1)
    H, _, _ = np.histogram2d(-lonlat[:, 1], np.mod(lonlat[:, 0], 360), bins=[-lat_e, lon_e])
    area = R_KM ** 2 * np.radians(CELL_DEG) * (np.sin(np.radians(lat_e[:-1])) - np.sin(np.radians(lat_e[1:])))
    d = np.rint(H / area[:, None] * 1e4).astype(np.int16)
    xmin, ymin, xmax, ymax = G.G200.bounds
    ds = gdal.GetDriverByName("GTiff").Create(path, NX, NY, 1, gdal.GDT_Int16, ["COMPRESS=DEFLATE"])
    ds.SetGeoTransform((xmin, (xmax - xmin) / NX, 0, ymax, 0, -(ymax - ymin) / NY))
    ds.SetProjection(G.TARGET_WKT)
    b = ds.GetRasterBand(1); b.SetNoDataValue(-1); b.WriteArray(d); b.ComputeStatistics(False)
    ds = None
    return d, int(H.sum())


def plateau_share():
    ds = gdal.Open(SLOPE); b = ds.GetRasterBand(1); gt = ds.GetGeoTransform()
    s, o = [], []
    with arcpy.da.SearchCursor(CHAN, ["SHAPE@", "StrahlerOrd"]) as cur:
        for k, (g, order_) in enumerate(cur):
            if k % 24:
                continue
            p = g.positionAlongLine(0.5, True).firstPoint
            col, row = int((p.X - gt[0]) / gt[1]), int((p.Y - gt[3]) / gt[5])
            s.append(float(b.ReadAsArray(col, row, 1, 1)[0, 0])); o.append(order_)
    s, o = np.array(s), np.array(o)
    return {"sampled": int(len(s)), "share_lt2deg": float((s < 2).mean()),
            "share_lt2deg_order3up": float((s[o >= 3] < 2).mean()),
            "by_order": {str(int(k)): float((s[o == k] < 2).mean()) for k in np.unique(o)}}


def fill_discard():
    """The fine pass's own figure for stream cells removed as fill artefacts, from its log."""
    import re
    log = os.path.join(HERE, "logs", "landform_fine_DESKTOP-PJS73RO.log")
    m = re.search(r"fill-artefact discard across all tiles: ([\d.]+)%", open(log, encoding="utf-8", errors="replace").read())
    return float(m.group(1))


# ------------------------------------------------------------------ symbology
def classify_raster(layer):
    sym = layer.symbology
    sym.updateColorizer("RasterClassifyColorizer")
    sym.colorizer.classificationField = "Value"
    sym.colorizer.breakCount = len(BREAKS)
    for brk, (ub, lab, col) in zip(sym.colorizer.classBreaks, BREAKS):
        brk.upperBound = ub; brk.label = lab; brk.color = {"RGB": list(col) + [100]}
    layer.symbology = sym


def line_layer(m, where, name, colour, width):
    l = add(m, CHAN, name)
    l.definitionQuery = where
    sym = l.symbology
    sym.renderer.symbol.color = {"RGB": list(colour) + [100]}
    sym.renderer.symbol.size = width
    l.symbology = sym
    return l


def hillshade(m, name="Hillshade (±60°, 200 m)"):
    return add(m, os.path.join(G.OUTDIR, "global60_hillshade.tif"), name)   # not the junction (KB §34)


TABLE_W = [0.44, 0.66, 0.53, 0.47, 0.47]     # ends at 10.55 in, the page margin (it ran to 10.76, KB §64)


def table(x, y_top, rows, widths, size=8.2):
    """rows[0] is the header; returns the elements; y_top is the top edge of the header row."""
    els, h = [], 0.20
    for i, r in enumerate(rows):
        y = y_top - (i + 1) * h; xx = x
        for j, (s, w) in enumerate(zip(r, widths)):
            fill = (235, 235, 235) if i == 0 else (255, 255, 255)
            els.append(rect(xx, y, w, h, "t%d_%d_bg" % (i, j), fill=fill, stroke=(190, 190, 190), stroke_w=0.4))
            els.append(cell_text(xx, y, w, h, s, size, "t%d_%d" % (i, j), bold=(i == 0),
                                 align="Left" if j == 0 else "Right"))
            xx += w
    return els


# ------------------------------------------------------------------ main
def main():
    chk = json.load(open(CHECK))
    assert not chk["failed"], "verify_global60_candidates.py failed: %s" % chk["failed"]
    rob = chk["robbins"]; base = chk["robbins_shifted_3D"]
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)

    print("1. density rasters")
    c = np.array([r for r in arcpy.da.SearchCursor(CRAT, ["CenterLon", "CenterLat", "DiameterKm"])], float)
    rb = np.array([r for r in arcpy.da.SearchCursor(ROBBINS, ["Lon", "Lat", "DiamKm"])], float)
    rb = rb[(np.abs(rb[:, 1]) <= 60) & (rb[:, 2] >= 1)]
    dc, nc = density(c[c[:, 2] >= 1], DENS_C)
    dr, nr = density(rb, DENS_R)
    both = (dc > 0) | (dr > 0)                      # cells with any count (empty cells only inflate r)
    r_cells = float(np.corrcoef(np.log1p(dc[both]), np.log1p(dr[both]))[0, 1])
    lat_c = np.linspace(60 - CELL_DEG / 2, -60 + CELL_DEG / 2, NY)
    bands = {}
    for nm, s in (("30-60N", lat_c > 30), ("0-30N", (lat_c > 0) & (lat_c <= 30)),
                  ("0-30S", (lat_c <= 0) & (lat_c > -30)), ("30-60S", lat_c <= -30)):
        bands[nm] = {"detector": float(dc[s].mean()), "robbins": float(dr[s].mean())}
    print("   %d candidates, %d Robbins craters; log-density r over cells with any count %.2f; bands %s"
          % (nc, nr, r_cells, {k: (round(v["detector"]), round(v["robbins"])) for k, v in bands.items()}))
    # by size class, 1° cells: small candidates follow the DEM's makeup, large ones the craters (KB §53.6)
    lat1, lon1 = np.arange(60, -61, -1.0), np.arange(0, 361, 1.0)
    cnt = lambda a: np.histogram2d(-a[:, 1], np.mod(a[:, 0], 360), bins=[-lat1, lon1])[0].ravel()
    r_size = {}
    for lo, hi, nm in ((1, 2, "1-2"), (2, 5, "2-5"), (5, 1e9, ">=5")):
        a = cnt(c[(c[:, 2] >= lo) & (c[:, 2] < hi)]); b = cnt(rb[(rb[:, 2] >= lo) & (rb[:, 2] < hi)])
        r_size[nm] = float(np.corrcoef(np.log1p(a), np.log1p(b))[0, 1])
    print("   detector vs Robbins by size, 1° cells:", {k: round(v, 2) for k, v in r_size.items()})
    print("2. channel plateau share (every 24th segment)")
    pl = plateau_share()
    print("   %d sampled, %.1f %% on < 2°" % (pl["sampled"], 100 * pl["share_lt2deg"]))
    orders = {}
    chx = []
    with arcpy.da.SearchCursor(CHAN, ["StrahlerOrd", "LengthKm", "SHAPE@TRUECENTROID"]) as cur:
        for o, km, (x, y) in cur:
            n, s = orders.get(int(o), (0, 0.0)); orders[int(o)] = (n + 1, s + km)
            if o >= 3:
                chx.append((180 + np.degrees(x / (R_KM * 1000)), np.degrees(y / (R_KM * 1000)), km))
    # where the DEM holds many closed pits the fill mask breaks the routed network (KB §53.6)
    chx = np.array(chx); small = c[(c[:, 2] >= 1) & (c[:, 2] < 2)]
    L = np.histogram2d(-chx[:, 1], np.mod(chx[:, 0], 360), bins=[-lat1, lon1], weights=chx[:, 2])[0].ravel()
    r_chan_pits = float(np.corrcoef(np.log1p(L), np.log1p(cnt(small)))[0, 1])
    print("   order >= 3 km per 1° cell vs 1-2 km closed depressions: r = %.2f" % r_chan_pits)
    res = {"when": time.strftime("%Y-%m-%d %H:%M"), "candidates": nc, "robbins": nr,
           "log_density_r_cells_with_any_count": r_cells, "band_means_per_1e4km2": bands,
           "r_by_size_1deg": r_size, "r_order3up_km_vs_small_depressions_1deg": r_chan_pits, "plateau": pl,
           "orders": {str(k): {"segments": v[0], "km": v[1]} for k, v in sorted(orders.items())},
           "density_p50_p99": {"candidates": [float(np.percentile(dc, 50)), float(np.percentile(dc, 99))],
                               "robbins": [float(np.percentile(dr, 50)), float(np.percentile(dr, 99))]}}
    json.dump(res, open(LOG, "w"), indent=1)

    p = arcpy.mp.ArcGISProject(APRX)
    clip = extent_polygon()
    print("3. maps")
    md = get_map(p, M_DEP)
    ld = add(md, DENS_C, "Closed depressions ≥ 1 km per 10⁴ km²"); classify_raster(ld)
    md.clipLayers(clip); add_graticule(p, M_DEP, G30, 7)
    mr = get_map(p, M_ROB)
    lr = add(mr, DENS_R, "Robbins craters ≥ 1 km per 10⁴ km²"); classify_raster(lr)
    mr.clipLayers(clip); add_graticule(p, M_ROB, G30, 7)
    mc = get_map(p, M_CHAN)
    n5, n4, n3 = (orders.get(k, (0, 0))[0] for k in (5, 4, 3))
    l5 = line_layer(mc, "StrahlerOrd >= 5", "Order 5 (%d segments)" % n5, (0, 20, 90), 2.0)
    l4 = line_layer(mc, "StrahlerOrd = 4", "Order 4 (%s)" % f"{n4:,}", (0, 70, 170), 1.1)
    l3 = line_layer(mc, "StrahlerOrd = 3", "Order 3 (%s)" % f"{n3:,}", (0, 120, 220), 0.6)
    hs = hillshade(mc)
    hs.transparency = 35
    order(mc, [l5.name, l4.name, l3.name, hs.name])
    mc.clipLayers(clip); add_graticule(p, M_CHAN, G30, 7)

    print("4. layout 11")
    lyt = page(p, L11)
    fw = 7.35; fh = fw / 3.0
    ext = clip.projectAs(md.spatialReference).extent
    mfa = lyt.createMapFrame(poly_geom(0.45, 4.62, fw, fh), md, "frame_detector")
    mfa.camera.setExtent(ext)
    mfb = lyt.createMapFrame(poly_geom(0.45, 1.80, fw, fh), mr, "frame_robbins")
    mfb.camera.setExtent(ext)
    rows = [["D ≥", "candidates", "matched", "chance", "recall"]]
    for d in ("1", "2", "5", "10", "20", "50", "100"):
        s, b = rob[d], base[d]
        rows.append(["%s km" % d, f"{s['candidates']:,}", "%.0f %%" % (100 * s["precision"]),
                     "%.0f %%" % (100 * b["precision"]), "%.0f %%" % (100 * s["recall"])])
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60° — closed depressions ≥ 1 km, against the Robbins crater catalogue",
             19, "title", bold=True),
        text(0.45, 7.47, "%s closed depressions in the HRSC/MOLA DEM at 200 m (fill depth, 70 tiles, seams checked), "
             "counted per 0.5° cell of true area." % f"{nc:,}", 10, "subtitle", colour=(70, 70, 70)),
        text(0.45, 4.62 + fh + 0.06, "The detector: closed depressions ≥ 1 km", 10, "label_a", bold=True),
        text(0.45, 1.80 + fh + 0.06, "Robbins & Hynek (2020): %s catalogued craters ≥ 1 km" % f"{nr:,}",
             10, "label_b", bold=True),
        text(7.98, 7.12, "Per 10⁴ km²", 10, "legend_title", bold=True),
        text(7.98, 4.50, "Candidates matching a Robbins crater", 9, "table_title", bold=True),
        text(7.98, 1.62, "Matched: centre within half the Robbins\ndiameter, diameter within 2× (KB §42.3).\n"
             "Chance: each candidate moved 3 of its\nown diameters east (KB §53.4).", 7.6, "table_note",
             colour=(60, 60, 60)),
        text(0.45, 0.64, "Below ~2 km most candidates are not catalogued craters; from ~5 km up most are. The maps do NOT "
             "agree cell by cell (log density r = %.2f): the detector's density hardly changes from the\nsmooth north "
             "(%.0f per 10⁴ km² at 30–60°N, Robbins %.0f) to the cratered south (%.0f at 0–30°S, "
             "Robbins %.0f). Its north–south stripes and blocks are the DEM's makeup, not geology: small\ncandidates "
             "gather where the HRSC/MOLA blend is sharp (inferred; no source mask is held). By 1° cell it tracks Robbins "
             "at r = %.2f for 1–2 km, %.2f for ≥ 5 km.\nClosed depressions only: breached and degraded craters are "
             "invisible to this method, so recall levels off near half (KB §26.3). Not a crater count; for craters, "
             "use Ref_Craters_Robbins2020."
             % (r_cells, bands["30-60N"]["detector"], bands["30-60N"]["robbins"], bands["0-30S"]["detector"],
                bands["0-30S"]["robbins"], r_size["1-2"], r_size[">=5"]), 7.9, "notes", colour=(40, 40, 40)),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
        + table(7.98, 4.42, rows, TABLE_W, size=7.6))
    legend_classes(p, lyt, mfa, 7.98, 6.92, 2.4, 2.0, [ld.name], names=False, cols=1)
    out = os.path.join(OUTD, L11 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)

    print("5. layout 12")
    lyt = page(p, L12)
    fw = 10.1; fh = fw / 3.0
    mf = lyt.createMapFrame(poly_geom(0.45, 3.55, fw, fh), mc, "frame")
    mf.camera.setExtent(clip.projectAs(mc.spatialReference).extent)
    total = sum(v[0] for v in orders.values()); km = sum(v[1] for v in orders.values())
    add_text(lyt, [
        text(0.45, 7.80, "Mars ±60° — the channel network routed on the DEM, Strahler order ≥ 3",
             19, "title", bold=True),
        text(0.45, 7.46, "%s channel segments (%.1f million km) from flow accumulation > 50 km² on the HRSC/MOLA "
             "DEM at 200 m; orders 1–2 (%s segments) are not drawn." % (
                 f"{total:,}", km / 1e6, f"{orders[1][0] + orders[2][0]:,}"), 10, "subtitle", colour=(70, 70, 70)),
        text(0.45, 1.45, "These are routed flow paths, not mapped valleys. %.0f %% of segments lie on ground under 2° "
             "at their midpoint (%.0f %% of order 3 and up), where routing follows\nDEM noise as much as relief "
             "(KB §25, §47.4); flow crossing the floors of filled basins (%.0f %% of stream cells) was "
             "already removed (KB §25.1). Where the DEM\nholds many closed pits, that removal breaks the network: "
             "long high-order paths gather on smooth ground (volcano flanks, plains), and order ≥ 3 length per "
             "1° cell\nruns against the count of 1–2 km closed depressions (r = %.2f). The first-order threshold "
             "is a setting, not a measurement (test T7, KB §47).\nOrigin (fluvial or volcanic) is not known for any "
             "segment; the reviewed type-area channels carry that (KB §46)." % (
                 100 * pl["share_lt2deg"], 100 * pl["share_lt2deg_order3up"], fill_discard(), r_chan_pits),
             8.3, "notes", colour=(40, 40, 40)),
        text(0.45, 0.40, CREDIT, 7.5, "credit", colour=(90, 90, 90))])
    legend_classes(p, lyt, mf, 0.45, 3.28, 6.0, 0.35, [l5.name, l4.name, l3.name], names=False, cols=3)
    out = os.path.join(OUTD, L12 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)

    p.save()
    print("saved. layouts:", [x.name for x in p.listLayouts()])


if __name__ == "__main__":
    main()
