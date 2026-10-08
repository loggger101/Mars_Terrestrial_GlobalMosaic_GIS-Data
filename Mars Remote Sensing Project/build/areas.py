# -*- coding: utf-8 -*-
r"""The type areas: one place that says where each window is and what its products are called (KB §42).

The type-area chain (make_typearea_stack / _terrain / _thermal, make_channel_candidates,
make_crater_candidates, verify_typearea) was written for Ius Chasma alone. Each now takes
--area <key> (default ius) and reads its window, folder, file prefix and output feature classes
from here, so Ius rebuilds exactly as before and a second area is one entry.

Bounds are in Mars_Equidistant_Cylindrical_CM180 metres, snapped to the THEMIS day mosaic's
100 m pixel edges (origin -10669500, +5334800), so the day-night pair is never resampled (§18.1).
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction

AREAS = {
    "ius": dict(
        name="Ius Chasma", lon=(271, 286), lat=(-13, -6),
        bounds=(5394000.0, -770600.0, 6283100.0, -355600.0),      # xmin ymin xmax ymax, as built 2026-09-18
        prefix="ius", folder="TypeArea",
        channels="Landform_ChannelCandidates_auto", craters="Landform_CraterCandidates_auto"),
    "ath": dict(
        # Athabasca Valles, IAU 153.2-156.8E 7.2-10.0N, with the Cerberus Fossae source region to its east
        # (approved as the second type area 2026-10-08, NEXT-STEPS D4)
        name="Athabasca Valles", lon=(150, 162), lat=(4, 14),
        bounds=(-1778300.0, 237000.0, -1066900.0, 829900.0),
        prefix="ath", folder="Athabasca",
        channels="Landform_ChannelCandidates_auto_ath", craters="Landform_CraterCandidates_auto_ath"),
}
RES = 100.0


def current():
    """The area named by --area (default ius), with derived fields: key, W, H, out (folder with
    spaces, for GDAL and layers) and ws() (the no-space junction, for Spatial Analyst)."""
    key = sys.argv[sys.argv.index("--area") + 1] if "--area" in sys.argv else "ius"
    if key not in AREAS:
        raise SystemExit("unknown --area %r; known: %s" % (key, ", ".join(AREAS)))
    a = dict(AREAS[key], key=key)
    xmin, ymin, xmax, ymax = a["bounds"]
    a["W"], a["H"] = int(round((xmax - xmin) / RES)), int(round((ymax - ymin) / RES))
    a["out"] = on_drive(os.path.join("Mars Project", a["folder"]))
    a["ws"] = lambda: junction(a["folder"])
    a["label"] = "%s, %d-%d%s / %d-%d%s" % (
        a["name"], a["lon"][0], a["lon"][1], "E",
        abs(a["lat"][0]), abs(a["lat"][1]), "S" if a["lat"][1] <= 0 else "N")
    return a


def name(a, stem):
    """<prefix>_<stem>, e.g. ius_dem.tif / ath_dem.tif."""
    return "%s_%s" % (a["prefix"], stem)
