# -*- coding: utf-8 -*-
r"""Presentation fixes to the seven layouts, found by exporting and reading every sheet (KB §33).

Run it after any of the three layout builders (make_typearea_layouts.py, make_global60_maps.py,
make_candidate_maps.py). Idempotent: every step checks before it changes anything.

  all sheets  every font -> Arial. The builders asked for Aptos (text) and the legend style
              brings Tahoma; NEITHER is installed on the laptop, so Pro substituted a different
              fallback for each and the legends came out in a serif face.
  02          the caption said "Bright = high thermal inertia". The THEMIS mosaics are locally
              contrast-normalised 8-bit DN (§28.10, §24): bright is warmer at night than its
              surroundings, not a calibrated thermal inertia.
  04          the extent outline's name was printed twice in the legend (heading and label);
              the grey streaks were unexplained: they are no-data in the classification
              (2.6 % of the band, 19 % south of 48°S), the hillshade showing through.
  legends     layer-name headings capped at 11 pt: in Arial the 16 pt default wrapped badly.
  04, 06      (KB §34) 04's subtitle rewrapped inside the frame; 06's north arrow moved clear
              of the legend box.
  07          the legend broke the five basin size classes across two columns, under the IAU
              entry; now basins in column 1, IAU craters in column 2.

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must
sit BESIDE the real .aprx (it stores relative paths, §31.5). --export <dir> writes every sheet to
PNG afterwards.
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else r"Z:\Mars Project\Mars Project.aprx")
EXPORT = sys.argv[sys.argv.index("--export") + 1] if "--export" in sys.argv else None
BKDIR = r"Z:\Mars Project\.backups"
FONT = "Arial"
REPLACE_FONTS = {"Aptos", "Tahoma"}
HEADING_PT = 11
SUB04_OLD = "local relief. No raw elevation band.\nSmoothed"
SUB04_NEW = "local relief.\nNo raw elevation band. Smoothed"
ARROW_X_06 = 10.25

SUBTITLE_02 = ("THEMIS Night IR v14, 100 m. Bright = warmer at night than its surroundings, as rock and "
               "coarse debris are.\nLocal contrast, not calibrated thermal inertia (KB \u00a728.10).")
NODATA_NOTE_04 = ("Grey streaks: no class. Gaps between THEMIS orbits leave 2.6% of the band "
                  "unclassified, 19% south of 48\u00b0S.")

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def refont(obj, seen=None):
    """Walk a CIM object tree; set every replaced fontFamilyName to FONT. Returns the count."""
    seen = set() if seen is None else seen
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    n = 0
    if isinstance(obj, (list, tuple)):
        for x in obj:
            n += refont(x, seen)
        return n
    if isinstance(obj, dict):
        if obj.get("fontFamilyName") in REPLACE_FONTS:
            obj["fontFamilyName"] = FONT; n += 1
        for v in obj.values():
            n += refont(v, seen)
        return n
    if not hasattr(obj, "__dict__") or isinstance(obj, (str, bytes, int, float)):
        return 0
    if getattr(obj, "fontFamilyName", None) in REPLACE_FONTS:
        obj.fontFamilyName = FONT; n += 1
    for k, v in vars(obj).items():
        if not k.startswith("_"):
            n += refont(v, seen)
    return n


def graphic(cim, name):
    return next((e for e in cim.elements if e.name == name), None)


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)

    for lyt in sorted(p.listLayouts(), key=lambda l: l.name):
        cim = lyt.getDefinition("V3")
        changed = []
        n = refont(cim.elements)
        if n:
            changed.append("%d fonts" % n)

        if lyt.name == "02_night_ir":
            g = graphic(cim, "subtitle")
            if g is not None and g.graphic.text != SUBTITLE_02:
                g.graphic.text = SUBTITLE_02
                changed.append("caption")

        if lyt.name == "04_global60_landforms":
            g = graphic(cim, "subtitle")                  # ran 0.2 in past the frame's right edge
            if g is not None and SUB04_OLD in g.graphic.text:
                g.graphic.text = g.graphic.text.replace(SUB04_OLD, SUB04_NEW)
                changed.append("subtitle rewrapped")
            g = graphic(cim, "checks")
            if g is not None and NODATA_NOTE_04 not in g.graphic.text:
                g.graphic.text = g.graphic.text + "\n" + NODATA_NOTE_04
                changed.append("no-data note")

        if changed:
            lyt.setDefinition(cim)

        for leg in lyt.listElements("LEGEND_ELEMENT"):
            d = leg.getDefinition("V3")
            for it in d.items:                            # Arial is wider than the fallback was:
                s = getattr(getattr(it, "layerNameSymbol", None), "symbol", None)  # 16 pt wrapped "400 m"
                if s is not None and getattr(s, "height", 0) > HEADING_PT:
                    s.height = HEADING_PT
                    changed.append("legend heading %g pt" % HEADING_PT)
            if lyt.name == "04_global60_landforms":
                for it in d.items:
                    if it.name.startswith("Analysis extent") and it.showLayerName:
                        it.showLayerName = False          # the label already says it
                        changed.append("legend: extent named once")
            if lyt.name == "07_global60_basins":
                for it in d.items:
                    want = it.name.startswith("IAU")
                    if it.newColumn != want:
                        it.newColumn = want
                        changed.append("legend: %s %s" % ("break before" if want else "no break", it.name[:20]))
            leg.setDefinition(d)
            if lyt.name == "07_global60_basins" and leg.fittingStrategy != "ManualColumns":
                leg.fittingStrategy = "ManualColumns"
                leg.columnCount = 2
                changed.append("legend: manual columns")
            if leg.isOverflowing:
                print("   %s: legend OVERFLOWING" % lyt.name)
        if lyt.name == "06_ius_digitising":
            for el in lyt.listElements("MAPSURROUND_ELEMENT", "narrow"):
                if el.elementPositionX < ARROW_X_06 - 0.01:   # its "N" sat against the legend box
                    el.elementPositionX = ARROW_X_06
                    changed.append("north arrow moved right")
        print("%-22s %s" % (lyt.name, ", ".join(changed) or "no change"))

    p.save()
    print("saved", APRX)
    if EXPORT:
        os.makedirs(EXPORT, exist_ok=True)
        for lyt in p.listLayouts():
            lyt.exportToPNG(os.path.join(EXPORT, lyt.name + ".png"), resolution=150)
        print("exported to", EXPORT)


if __name__ == "__main__":
    main()
