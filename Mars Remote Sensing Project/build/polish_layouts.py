# -*- coding: utf-8 -*-
r"""Presentation fixes to every layout, found by exporting and reading every sheet (KB §33, §61, §63-§65).

Run it after any layout builder (HANDOFF-DESKTOP.md §3 lists them in the order they run). It began with
the first seven sheets; the fixes below name the sheets they touch. Idempotent: every step checks before
it changes anything.

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
  (KB §61, 2026-10-18, from reading every sheet again)
  graticules  white labels with no halo vanished on light ground (layout 11's density maps,
              the chasma walls on 01-02); every graticule label now has a dark halo.
  legends     a legend's border is drawn ~0.15 in outside its position: on 12 and 14 it stood
              left of the map frame, on 03 and 06 it cut into the frame's bottom edge.
              03's "Graticule 2°" entry and the "Analysis extent ±60°" entries of 04, 10 and 13
              had no visible symbol (the extent outline is the frame edge): removed from the legend,
              the layers kept. 07's IAU entry printed its name as heading and label: once now.
  (KB §63, 2026-10-19)
  credit      every sheet's footer said "Logan Edwards"; the public name is "Logan M Edwards"
              (the builders' CREDIT now says so too).
  08          caption A named Tharsis among the dusty provinces of the 47.7 DN difference, which
              covers Arabia and Amazonis against Syrtis Major and Acidalia only (KB §62).
  (KB §64, 2026-10-19, from reading all fifteen sheets)
  scale bars  the first division split in two crowded "0 20 40" into the bar's start (01-03, 06,
              09): no subdivisions, a label at every division.
  legends     a legend whose border ran past the 10.55 in page margin (04, 07, 10, 13: to 10.70)
              moves left until it ends there; the builders now place them so.
  03          (KB §65) the legend auto-added every map layer, so the graticule entry came back on
              each run; auto-add off, and a title: the ten clusters carry no landform names.
  11          the "matching a Robbins crater" table ran to 10.76 in: its columns narrowed to
              make_global60_candidate_sheets.TABLE_W in place (rerunning that builder recomputes
              1.4 million features).

Pro must be closed. The .aprx is backed up first. --aprx <copy> rehearses on a copy, which must
sit BESIDE the real .aprx (it stores relative paths, §31.5). --export <dir> writes every sheet to
PNG afterwards.
"""
import os, sys, time, shutil
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

APRX = (sys.argv[sys.argv.index("--aprx") + 1] if "--aprx" in sys.argv
        else on_drive(r"Mars Project\Mars Project.aprx"))
EXPORT = sys.argv[sys.argv.index("--export") + 1] if "--export" in sys.argv else None
BKDIR = on_drive(r"Mars Project\.backups")
FONT = "Arial"
REPLACE_FONTS = {"Aptos", "Tahoma"}
HEADING_PT = 11
SUB04_OLD = "local relief. No raw elevation band.\nSmoothed"
SUB04_NEW = "local relief.\nNo raw elevation band. Smoothed"
ARROW_X_06 = 10.25
HALO_RGB, HALO_PT = [40, 40, 40, 100], 1.2          # as the type-area labels (make_reference_maps.py)
LEGEND_POS = {"03_classification": (None, 2.22, None), "06_ius_digitising": (None, 2.22, None),
              "12_global60_channels": (0.60, None, None), "14_validation": (0.60, None, 9.80)}  # x, y, width
LEGEND_DROP = {"03_classification": ("Graticule",), "04_global60_landforms": ("Analysis extent",),
               "10_global60_locator": ("Analysis extent",), "13_geomap_check": ("Analysis extent",)}

SUBTITLE_02 = ("THEMIS Night IR v14, 100 m. Bright = warmer at night than its surroundings, as rock and "
               "coarse debris are.\nLocal contrast, not calibrated thermal inertia (KB \u00a728.10).")
NAME_OLD, NAME_NEW = "Logan Edwards  ·", "Logan M Edwards  ·"
CAP08_OLD, CAP08_NEW = "Bright dust (Arabia, Tharsis, Amazonis)", "Bright dust (Arabia, Amazonis)"
RIGHT = 10.40                                       # a legend's x + width; its border ends 0.15 in further
T11_OLD = [0.50, 0.70, 0.58, 0.50, 0.50]
T11_NEW = [0.44, 0.66, 0.53, 0.47, 0.47]            # = make_global60_candidate_sheets.TABLE_W
T11_X = 7.98
LEGEND_TITLE = {"03_classification": "Iso Cluster class (spectral clusters, not named landforms)"}
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


def halo_graticules(p):
    """A dark halo on every graticule label class. Returns the number of layers changed."""
    n = 0
    for m in p.listMaps():
        for l in m.listLayers():
            if not l.name.startswith("Graticule") or not l.supports("SHOWLABELS"):
                continue
            d = l.getDefinition("V3")
            done = False
            for c in d.labelClasses:
                s = c.textSymbol.symbol
                cur = getattr(getattr(s, "haloSymbol", None), "symbolLayers", None) or []
                if (s.haloSize == HALO_PT and cur
                        and list(getattr(cur[0].color, "values", [])) == HALO_RGB):
                    continue
                fill = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidFill", "V3")
                col = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3"); col.values = HALO_RGB
                fill.color = col
                halo = arcpy.cim.CreateCIMObjectFromClassName("CIMPolygonSymbol", "V3")
                halo.symbolLayers = [fill]
                s.haloSymbol = halo
                s.haloSize = HALO_PT
                done = True
            if done:
                l.setDefinition(d); n += 1
    return n


def scale_bars(lyt):
    """No subdivisions, a label at each division. Returns the number changed."""
    n = 0
    for sb in lyt.listElements("MAPSURROUND_ELEMENT"):
        d = sb.getDefinition("V3")
        if not hasattr(d, "subdivisions"):            # north arrows
            continue
        if d.subdivisions == 0 and d.labelFrequency == "Divisions":
            continue
        d.subdivisions = 0
        d.labelFrequency = "Divisions"
        sb.setDefinition(d); n += 1
    return n


def table_11(lyt):
    """Narrow the Robbins table's columns in place: each cell keeps its row, moves to its new column."""
    cells = [e for e in lyt.listElements() if e.name.startswith("t")]     # rects and texts alike
    first = [e for e in cells if e.name == "t0_0_bg"]
    if not first or abs(first[0].elementWidth - T11_OLD[0]) > abs(first[0].elementWidth - T11_NEW[0]):
        return 0                                      # already narrowed (or no table)
    left = lambda ws, j: T11_X + sum(ws[:j])
    n = 0
    for el in cells:
        parts = el.name.split("_")
        if len(parts) < 2 or not parts[1].isdigit():
            continue
        j = int(parts[1])
        if el.name.endswith("_bg"):
            el.elementWidth = el.elementWidth - T11_OLD[j] + T11_NEW[j]     # left edge stays
            el.elementPositionX += left(T11_NEW, j) - left(T11_OLD, j)
        elif j == 0:                                  # left-aligned: follows the left edge
            el.elementPositionX += left(T11_NEW, j) - left(T11_OLD, j)
        else:                                         # right-aligned: follows the right edge
            el.elementPositionX += (left(T11_NEW, j) + T11_NEW[j]) - (left(T11_OLD, j) + T11_OLD[j])
        n += 1
    return n


def main():
    if "--aprx" not in sys.argv:
        os.makedirs(BKDIR, exist_ok=True)
        bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(APRX, bk); print("backup", bk)
    p = arcpy.mp.ArcGISProject(APRX)
    print("graticule halos         %d layers" % halo_graticules(p))

    for lyt in sorted(p.listLayouts(), key=lambda l: l.name):
        cim = lyt.getDefinition("V3")
        changed = []
        n = refont(cim.elements)
        if n:
            changed.append("%d fonts" % n)

        for e in cim.elements:
            t = getattr(getattr(e, "graphic", None), "text", None)
            if isinstance(t, str) and NAME_OLD in t:
                e.graphic.text = t.replace(NAME_OLD, NAME_NEW)
                changed.append("credit name")

        if lyt.name == "08_global60_mosaic":
            g = graphic(cim, "cA")
            if g is not None and CAP08_OLD in g.graphic.text:
                g.graphic.text = g.graphic.text.replace(CAP08_OLD, CAP08_NEW)
                changed.append("caption A")

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
            if lyt.name in LEGEND_DROP and d.autoAdd:     # or the dropped layers come back on the next open
                d.autoAdd = False
                changed.append("legend: auto-add off")
            want = LEGEND_TITLE.get(lyt.name)
            if want and (not d.showTitle or d.title != want):
                d.showTitle, d.title = True, want
                ts = getattr(getattr(d, "titleSymbol", None), "symbol", None)
                if ts is not None:
                    ts.fontFamilyName, ts.fontStyleName, ts.height = FONT, "Bold", 10
                changed.append("legend title")
            keep = [it for it in d.items if not it.name.startswith(LEGEND_DROP.get(lyt.name, ()))]
            if len(keep) < len(d.items):                  # no visible symbol on the sheet
                changed.append("legend: dropped %s" % ", ".join(it.name for it in d.items if it not in keep))
                d.items = keep
            if lyt.name == "07_global60_basins":
                for it in d.items:
                    want = it.name.startswith("IAU")
                    if it.newColumn != want:
                        it.newColumn = want
                        changed.append("legend: %s %s" % ("break before" if want else "no break", it.name[:20]))
                    if want and it.showLayerName:         # heading and label said the same
                        it.showLayerName = False
                        changed.append("legend: IAU named once")
            leg.setDefinition(d)
            x, y, w = LEGEND_POS.get(lyt.name, (None, None, None))
            for attr, v in (("elementWidth", w), ("elementPositionX", x), ("elementPositionY", y)):
                if v is not None and abs(getattr(leg, attr) - v) > 0.005:
                    setattr(leg, attr, v)
                    changed.append("legend %s %.2f" % (attr[7:] if attr != "elementWidth" else "width", v))
            if leg.elementPositionX + leg.elementWidth > RIGHT + 0.005:   # border past the page margin
                leg.elementPositionX = RIGHT - leg.elementWidth
                changed.append("legend x %.2f (margin)" % leg.elementPositionX)
            if lyt.name == "07_global60_basins" and leg.fittingStrategy != "ManualColumns":
                leg.fittingStrategy = "ManualColumns"
                leg.columnCount = 2
                changed.append("legend: manual columns")
            if leg.isOverflowing:
                print("   %s: legend OVERFLOWING" % lyt.name)
        n = scale_bars(lyt)
        if n:
            changed.append("%d scale bar(s): no subdivisions" % n)
        if lyt.name == "11_global60_depressions":
            n = table_11(lyt)
            if n:
                changed.append("table: %d cells to the margin" % n)
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
