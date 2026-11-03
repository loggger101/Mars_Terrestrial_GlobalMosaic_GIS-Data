# -*- coding: utf-8 -*-
r"""The layer and map for the author's off-Tharsis edifice and apron labels (NEXT-STEPS §14 row 3, KB §69.63).

Makes, once (a rerun changes nothing that exists):
  Landform_TrainingSamples_offtharsis_draw   an empty polygon class in the project gdb, in the label sets' own
                                             coordinate system: Classvalue (5 volcanic edifice, 6 apron), Classname,
                                             MappedBy (default "author"), Notes. The author draws into it in Pro.
  map "Off-Tharsis labels (author)"          in Mars Project.aprx (backed up first): the class above, the targets
                                             (IAU names make_offtharsis_targets.py lists), the v2 and v3 held-out
                                             labels for context, and the CTX mosaic (streamed, KB §69.52). No
                                             classification map is in it, so the labels are drawn blind to the maps.

  "<ArcGIS Pro Python>" make_offtharsis_layer.py        (Pro closed)
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
from make_global60_maps import BKDIR
from add_ctx_layer import CTX_URL, CTX_NAME

FC = "Landform_TrainingSamples_offtharsis_draw"
TEMPLATE_SR = "Landform_TrainingSamples_v2_60_test"
MAP = "Off-Tharsis labels (author)"
APRX = on_drive(r"Mars Project\Mars Project.aprx")
TARGETS = ["Nili Patera", "Meroe Patera", "Nili Tholus", "Nilosyrtis Mensae", "Colles Nili", "Nia Tholus"]
COLOURS = {5: (255, 170, 0), 6: (115, 178, 255)}               # labelsets.COLOURS: edifice, apron


def make_fc():
    path = os.path.join(GDB, FC)
    if arcpy.Exists(path):
        print("exists:", path, int(arcpy.management.GetCount(path)[0]), "rows")
        return path
    sr = arcpy.Describe(os.path.join(GDB, TEMPLATE_SR)).spatialReference
    arcpy.management.CreateFeatureclass(GDB, FC, "POLYGON", spatial_reference=sr)
    for name, kind, length in (("Classvalue", "SHORT", None), ("Classname", "TEXT", 32), ("MappedBy", "TEXT", 40),
                               ("Notes", "TEXT", 200)):
        arcpy.management.AddField(path, name, kind, field_length=length)
    arcpy.management.AssignDefaultToField(path, "MappedBy", "author")
    print("made:", path, "in", sr.name)
    return path


def make_map(fc):
    p = arcpy.mp.ArcGISProject(APRX)
    if p.listMaps(MAP):
        print("map exists:", MAP)
        return
    os.makedirs(BKDIR, exist_ok=True)
    bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(APRX, bk)
    print("backup", bk)
    m = p.createMap(MAP, "MAP")
    for lyr in m.listLayers():                                   # createMap adds an Earth basemap: Mars only (§37)
        m.removeLayer(lyr)
    m.spatialReference = arcpy.Describe(fc).spatialReference
    ctx = m.addDataFromPath(CTX_URL)
    ctx.name = CTX_NAME
    for title, src in (("v3 held out (context)", "Landform_TrainingSamples_v3_60_test"),
                       ("v2 held out (context)", "Landform_TrainingSamples_v2_60_test")):
        lyr = m.addDataFromPath(os.path.join(GDB, src))
        lyr.name, lyr.visible = title, False
    arcpy.env.workspace = GDB
    q = "clean_name IN (%s)" % ", ".join("'%s'" % t for t in TARGETS)
    for nfc in arcpy.ListFeatureClasses("MARS_nomenclature*") or []:
        if "crater" in nfc.lower():
            continue
        with arcpy.da.SearchCursor(nfc, ["clean_name"], q) as c:
            if not any(True for _ in c):
                continue
        lyr = m.addDataFromPath(os.path.join(GDB, nfc))
        lyr.name, lyr.definitionQuery = "Targets (IAU names)", q
        if lyr.supports("SHOWLABELS"):
            lyr.showLabels = True
    lyr = m.addDataFromPath(fc)
    lyr.name = "Draw here: off-Tharsis edifice (5) and apron (6)"
    sym = lyr.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = ["Classvalue"]
    lyr.symbology = sym
    p.save()
    print("map %r:" % MAP, [l.name for l in m.listLayers()])


def main():
    assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"
    make_map(make_fc())


if __name__ == "__main__":
    main()
