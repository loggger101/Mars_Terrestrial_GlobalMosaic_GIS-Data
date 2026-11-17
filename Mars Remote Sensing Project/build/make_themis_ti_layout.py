# -*- coding: utf-8 -*-
r"""Layout 24: the night infrared against calibrated THEMIS thermal inertia at the two type areas (T17; KB §69.144,
§69.150).

T17 compared the display mosaics with the USGS quantitative THEMIS inertia mosaic (Fergason et al. 2006) in windows read
over HTTP and kept in Reference\THEMIS_TI_quantitative_windows\, but no sheet showed the calibrated inertia. This one
sets each window's night infrared beside its inertia:
  A, B  Ius Chasma: TypeArea\ius_night.tif (the stack's 100 m night band) and ius_themis_ti_quant.tif
  C, D  Athabasca Valles: Athabasca\ath_night.tif and ath_themis_ti_quant.tif
Inertia on fixed classes in tiu (J m^-2 K^-1 s^-1/2), the same in both windows; the night band stretched as Pro does by
default (it is locally contrast-normalised DN, not a physical value, KB §24). The table reads logs\
t17_themis_ti_windows.json: Spearman's rho of each input with log inertia over the whole window and the median over
10 km tiles.

Pro must be closed; the .aprx is backed up first. --aprx <copy> rehearses on a copy. Run polish_layouts.py afterwards.
"""
import os, sys, time, shutil, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive
import grid60 as G
from layoutkit import text, poly_geom
from make_global60_maps import (add, get_map, order, page, add_text, CREDIT, BKDIR, OUTD)
from make_global60_candidate_sheets import table
from make_thermal_change_layout import classify, key

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
ROOT = os.path.dirname(G.OUTDIR)
TI = os.path.join(ROOT, "Reference", "THEMIS_TI_quantitative_windows", "%s_themis_ti_quant.tif")
NIGHT = {"ius": os.path.join(ROOT, "TypeArea", "ius_night.tif"), "ath": os.path.join(ROOT, "Athabasca", "ath_night.tif")}
LOG = os.path.join(HERE, "logs", "t17_themis_ti_windows.json")
L24 = "24_themis_inertia"
TIU = [(100, "under 100", (68, 1, 84)), (150, "100–150", (70, 50, 127)), (200, "150–200", (54, 92, 141)),
       (250, "200–250", (39, 127, 142)), (300, "250–300", (31, 161, 135)), (400, "300–400", (74, 193, 109)),
       (5000, "over 400", (190, 223, 38))]
FR = {"a": (0.45, 4.45, 4.85, 2.27), "b": (5.60, 4.45, 4.85, 2.27),      # Ius: 15° x 7°, 2.14 : 1
      "c": (0.45, 1.20, 2.62, 2.18), "d": (3.27, 1.20, 2.62, 2.18)}      # Athabasca: 12° x 10°, 1.2 : 1
AREA = {"ius": "Ius Chasma", "ath": "Athabasca Valles"}

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def one_map(p, name, path, lname, ti):
    m = get_map(p, name)
    r = add(m, path, lname)
    if ti:
        classify(r, TIU)
    return m, r


def sheet(p, maps, R):
    lyt = page(p, L24)
    dark, grey = (40, 40, 40), (70, 70, 70)
    A = R["areas"]
    rho = lambda a, i: A[AREA[a]]["inputs"][i]
    labels = {"a": "A  Ius Chasma: night infrared (DN, stretched)",
              "b": "B  Ius Chasma: THEMIS thermal inertia; night IR ρ %+.2f, %+.2f within 10 km"
                   % (rho("ius", "night IR")["rho_whole"], rho("ius", "night IR")["rho_tile_median"]),
              "c": "C  Athabasca Valles: night infrared",
              "d": "D  Athabasca: inertia; ρ %+.2f, %+.2f in 10 km"
                   % (rho("ath", "night IR")["rho_whole"], rho("ath", "night IR")["rho_tile_median"])}
    els = []
    for k, (x, y, w, h) in FR.items():
        m, r = maps[k]
        mf = lyt.createMapFrame(poly_geom(x, y, w, h), m, "frame_" + k)
        mf.camera.setExtent(mf.getLayerExtent(r, False, True))
        els.append(text(x, y + h + 0.06, labels[k], 8.6, "label_" + k, bold=True))
    rows = [["input", "Ius", "10 km", "Athab.", "10 km"]]
    for i in ["night IR", "day IR", "diurnal contrast", "Viking red", "slope"]:
        rows.append([i, "%+.2f" % rho("ius", i)["rho_whole"], "%+.2f" % rho("ius", i)["rho_tile_median"],
                     "%+.2f" % rho("ath", i)["rho_whole"], "%+.2f" % rho("ath", i)["rho_tile_median"]])
    els += [
        text(0.45, 7.80, "The night infrared against calibrated thermal inertia (T17)", 18, "title", bold=True),
        text(0.45, 7.47, "The display mosaic's night band beside the USGS quantitative THEMIS inertia mosaic (Fergason "
             "et al. 2006), 100 m, at the two type areas; median inertia %.0f and %.0f tiu."
             % (A["Ius Chasma"]["ti_median"], A["Athabasca Valles"]["ti_median"]), 10, "subtitle", colour=grey),
        text(6.20, 3.25, "Spearman's ρ with log inertia", 9.5, "table_title", bold=True, colour=dark),
        text(6.20, 2.98, "the whole window, and the median over 10 km tiles", 7.6, "table_sub", colour=grey),
        text(6.20, 0.70, "Within 10 km the night band follows inertia closely at both sites;\nacross a window less so. "
             "The inertia mosaic is built from image strips,\neach offset from its neighbours (B, D), and the night "
             "mosaic is\nstretched region by region (KB §28.10): a 10 km tile sees fewer of\neither (inferred, not "
             "measured). Inertia in tiu, J m⁻² K⁻¹ s⁻½;\nevery 5th pixel (KB §69.144).", 7.8, "notes", colour=dark),
        text(0.45, 0.30, CREDIT, 7.5, "credit", colour=(90, 90, 90))]
    els += key(9.30, 3.25, "Inertia, tiu (B, D)", [(l, c) for _, l, c in TIU], "keyb")
    els += table(6.20, 2.90, rows, [0.95, 0.48, 0.45, 0.50, 0.45], size=7.2)
    add_text(lyt, els)
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, L24 + ".png"); lyt.exportToPNG(out, resolution=150); print("   ", out)


def main():
    R = json.load(open(LOG, encoding="utf-8"))
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("1. maps")
    maps = {"a": one_map(p, "Ius Chasma — night IR (T17)", NIGHT["ius"], "Night IR, 100 m", False),
            "b": one_map(p, "Ius Chasma — THEMIS thermal inertia (T17)", TI % "ius", "THEMIS inertia, tiu", True),
            "c": one_map(p, "Athabasca Valles — night IR (T17)", NIGHT["ath"], "Night IR, 100 m", False),
            "d": one_map(p, "Athabasca Valles — THEMIS thermal inertia (T17)", TI % "ath", "THEMIS inertia, tiu", True)}
    print("2. layout", L24)
    sheet(p, maps, R)
    p.save()
    print("saved. maps:", len(p.listMaps()), "layouts:", len(p.listLayouts()))


if __name__ == "__main__":
    main()
