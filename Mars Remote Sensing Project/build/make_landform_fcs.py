# -*- coding: utf-8 -*-
"""Task 11 scaffolding: the three landform feature classes.

His prospectus task 8: "Lava flow margins, channel centerlines, and crater rims
as three feature classes in the project geodatabase."

Created in the SAME projected frame as the harmonised type-area stack
(eqc / lon_0=180 / R=3396190) so lengths and areas are measured on the grid the
mapping is actually done on. Equirectangular is neither equal-area nor
conformal, but across 6-13 S the scale error is under 2 percent.
"""
import arcpy, os

GDB = r"Z:\Mars Project\Mars Project.gdb"
WKT = ('PROJCS["Mars_Equidistant_Cylindrical_CM180",'
       'GEOGCS["GCS_Mars_2000_Sphere",DATUM["D_Mars_2000_Sphere",'
       'SPHEROID["Mars_2000_Sphere_IAU_IAG",3396190.0,0.0]],'
       'PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],'
       'PROJECTION["Equidistant_Cylindrical"],PARAMETER["False_Easting",0.0],'
       'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",180.0],'
       'PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]')
SR = arcpy.SpatialReference(); SR.loadFromString(WKT)

COMMON = [
    ("UnitName",   "TEXT",  80, "informal unit or feature name"),
    ("Confidence", "TEXT",  12, "certain / probable / inferred"),
    ("Evidence",   "TEXT", 120, "which band(s) the boundary was drawn from"),
    ("Notes",      "TEXT", 255, ""),
    ("MappedBy",   "TEXT",  40, ""),
    ("MappedOn",   "DATE",   0, ""),
]
SPECS = [
    ("Landform_LavaFlowMargins", "POLYLINE",
     [("FlowUnit", "TEXT", 60, "source vent or flow field"),
      ("MarginType", "TEXT", 30, "lobate / sheet / channelised")]),
    ("Landform_ChannelCenterlines", "POLYLINE",
     [("Origin", "TEXT", 20, "fluvial / volcanic / indeterminate"),
      ("OrderStrahler", "SHORT", 0, ""),
      ("GradientPct", "DOUBLE", 0, "from the projected DEM")]),
    ("Landform_CraterRims", "POLYGON",
     [("DiameterKm", "DOUBLE", 0, "computed from the digitised rim"),
      ("Preservation", "TEXT", 20, "fresh / degraded / ghost")]),
]

arcpy.env.overwriteOutput = False
for name, geom, extra in SPECS:
    path = os.path.join(GDB, name)
    if arcpy.Exists(path):
        print("exists, skipped:", name); continue
    arcpy.management.CreateFeatureclass(GDB, name, geom, spatial_reference=SR)
    for fld, typ, ln, alias in COMMON + extra:
        if typ == "TEXT":
            arcpy.management.AddField(path, fld, typ, field_length=ln)
        else:
            arcpy.management.AddField(path, fld, typ)
    n = len(arcpy.ListFields(path)) - 1
    print("created %-30s %-9s %2d fields  %s" % (name, geom, n, SR.name))
