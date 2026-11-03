# -*- coding: utf-8 -*-
r"""Where the author can draw volcanic edifice and apron labels in held-out blocks outside Tharsis (NEXT-STEPS §14
row 3, the author's yes of 2026-11-03, KB §69.63). Reads only.

The seven-class U-Net's lead over the SVM rests on the two Tharsis blocks (-9_-1, -9_0), which hold nearly all the
held-out edifice and apron ground: off Tharsis the v3 held-out set has 6 edifice polygons in one block and 16 apron
in another (KB §69.61). This lists, for each of the 12 other held-out blocks, the ground a new label could sit on:

  units   the share of the block on SIM 3292's edifice units (group ve) and apron units (ANa, Aa west of 100°W, lAa),
          from propose_v3_labels.py's cached 3.2 km unit-kind grid (C:\MarsScratch\label_v3\unit_kinds_3200m_d34.npy),
          the same kinds the v3 labels were cut from;
  named   the IAU Mons, Tholus and Patera in the block (the nomenclature layers in the gdb), with diameter;
  labels  how many v2 and v3 held-out polygons of each class the block already holds.

Blocks are 15° by 15°, named <floor(lon/15)>_<floor(lat/15)> with longitude in -180..180, as the label sets name them.
Writes logs\offtharsis_targets.json and Mars Project\review_sheets\offtharsis\targets.md (the guide's table).

  "<ArcGIS Pro Python>" make_offtharsis_targets.py
"""
import os, sys, json, math, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive
import grid60 as G

KINDS = r"C:\MarsScratch\label_v3\unit_kinds_3200m_d34.npy"
KIND = {"volc": 1, "ve": 2, "apron": 3, "slide": 4, "highland": 5, "other": 6, "fan": 7}   # propose_v3_labels.py
DP = math.degrees(200.0 / G.R_MARS)
LAT0 = math.degrees(3556500.0 / G.R_MARS)
DC = DP * 16
THARSIS = {"-9_-1", "-9_0"}
NAMES7 = ["Crater", "hills", "lava tube", "Normal Ground", "volcanic edifice", "apron", "fluvial channel"]
OUT = os.path.join(HERE, "logs", "offtharsis_targets.json")
SHEET = on_drive(r"Mars Project\review_sheets\offtharsis\targets.md")


def block_of(lon, lat):
    lon = lon - 360 if lon > 180 else lon
    return "%d_%d" % (math.floor(lon / 15), math.floor(lat / 15))


def block_bounds(b):
    i, j = map(int, b.split("_"))
    return i * 15, (i + 1) * 15, j * 15, (j + 1) * 15            # lon -180..180, lat


def held_out(fc):
    n = collections.Counter()
    with arcpy.da.SearchCursor(os.path.join(GDB, fc), ["Block", "Classvalue"]) as c:
        for b, v in c:
            n[(b, int(v))] += 1
    return n


def unit_shares(kind, b):
    lo0, lo1, la0, la1 = block_bounds(b)
    lo0, lo1 = lo0 % 360, (lo1 - 1e-9) % 360                     # the grid's columns are east longitude from 0°
    c0, c1 = int(lo0 / DC), int(lo1 / DC) + 1
    r0, r1 = int((LAT0 - la1) / DC), int((LAT0 - la0) / DC) + 1
    r0, r1 = max(r0, 0), min(r1, kind.shape[0])
    k = kind[r0:r1, c0:c1]
    lat = LAT0 - (np.arange(r0, r1) + 0.5) * DC
    w = np.repeat(np.cos(np.radians(lat))[:, None], k.shape[1], 1)
    tot = w.sum()
    share = lambda m: float(w[m].sum() / tot)
    return dict(edifice=round(share(k == KIND["ve"]), 4),
                apron=round(share((k == KIND["apron"]) | (k == KIND["fan"])), 4),
                volcanic_plains=round(share(k == KIND["volc"]), 4))


def named(blocks):
    out = collections.defaultdict(list)
    arcpy.env.workspace = GDB
    for fc in arcpy.ListFeatureClasses("MARS_nomenclature*") or []:
        if "crater" in fc.lower():
            continue
        with arcpy.da.SearchCursor(fc, ["clean_name", "type", "diameter", "SHAPE@XY"],
                                   spatial_reference=arcpy.SpatialReference(104905)) as c:
            for nm, ty, dia, (x, y) in c:
                t = (ty or "").split(",")[0].strip()
                if t not in ("Mons", "Tholus", "Patera") or abs(y) > 60:
                    continue
                b = block_of(x % 360, y)
                if b in blocks:
                    out[b].append(dict(name=nm, type=t, diam_km=round(float(dia or 0), 1),
                                       lon_e=round(x % 360, 2), lat=round(y, 2)))
    return out


def main():
    v2, v3 = held_out("Landform_TrainingSamples_v2_60_test"), held_out("Landform_TrainingSamples_v3_60_test")
    blocks = sorted({b for b, _ in v2} - THARSIS, key=lambda s: tuple(map(int, s.split("_"))))
    assert len(blocks) == 12, blocks
    kind = np.load(KINDS)
    for b in sorted(THARSIS):                                     # control: the same code must find Tharsis's units
        u = unit_shares(kind, b)
        print("control %s: edifice units %.1f %%, apron units %.1f %%" % (b, 100 * u["edifice"], 100 * u["apron"]))
        assert u["edifice"] + u["apron"] > 0.05, "the unit grid reads empty where Tharsis's units are"
    nm = named(set(blocks))
    rows = []
    for b in blocks:
        lo0, lo1, la0, la1 = block_bounds(b)
        u = unit_shares(kind, b)
        rows.append(dict(block=b, lon_e="%d-%d" % (lo0 % 360, (lo1 - 1) % 360 + 1), lat="%d to %d" % (la0, la1),
                         units=u, named=sorted(nm.get(b, []), key=lambda d: -d["diam_km"]),
                         v2_edifice=v2[(b, 5)], v2_apron=v2[(b, 6)], v3_edifice=v3[(b, 5)], v3_apron=v3[(b, 6)]))
    for r in rows:
        print("%-6s %-9s %-10s edifice units %5.1f %%, apron units %5.1f %%; held out v2 %d/%d, v3 %d/%d; named: %s"
              % (r["block"], r["lon_e"], r["lat"], 100 * r["units"]["edifice"], 100 * r["units"]["apron"],
                 r["v2_edifice"], r["v2_apron"], r["v3_edifice"], r["v3_apron"],
                 ", ".join("%s %s (%.0f km)" % (d["name"], d["type"], d["diam_km"]) for d in r["named"]) or "none"))
    json.dump(dict(script="make_offtharsis_targets.py", blocks=rows), open(OUT, "w", encoding="utf-8"), indent=1)
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    with open(SHEET, "w", encoding="utf-8") as f:
        f.write("| block | °E | latitude | edifice units | apron units | held out now, edifice / apron (v2; v3) "
                "| named montes, tholi, paterae |\n|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write("| %s | %s | %s | %.1f %% | %.1f %% | %d / %d; %d / %d | %s |\n" % (
                r["block"], r["lon_e"], r["lat"], 100 * r["units"]["edifice"], 100 * r["units"]["apron"],
                r["v2_edifice"], r["v2_apron"], r["v3_edifice"], r["v3_apron"],
                ", ".join("%s %s, %.0f km (%.1f°E, %.1f°)" % (d["name"], d["type"], d["diam_km"], d["lon_e"], d["lat"])
                          for d in r["named"]) or "none"))
    print("wrote", OUT, "and", SHEET)


if __name__ == "__main__":
    main()
