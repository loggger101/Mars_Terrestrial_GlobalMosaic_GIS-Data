# -*- coding: utf-8 -*-
r"""The downloaded references as feature classes in the project gdb (KB §41).

  Ref_SIM3292_GeologicUnits   USGS SIM 3292 (Tanaka et al. 2014) unit polygons, projected from the
                              source's Robinson (CM 0) to GCS_Mars_2000_Sphere. Fields Unit, UnitDesc,
                              SphArea_km, plus UnitGroup (the age-free unit family, e.g. "v" volcanic)
  Ref_Craters_Robbins2020     Robbins & Hynek crater database, 2020 release (385,049 craters >= 1 km),
                              points at the circle-fit centre, DiamKm, longitude converted to -180..180

Both carry Source; a class that holds a row this script did not write is never deleted (the
safe_to_replace rule, KB §29.8). Built in a scratch gdb on internal disk and copied to Z: in one
step (§36.4). Read-only on the downloads in Mars Project\Reference\ (NEXT-STEPS D5).
"""
import os, re, sys, csv, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB

REF = on_drive(r"Mars Project\Reference")
SRC_UNITS = os.path.join(REF, r"SIM3292_geologic_map\SIM3292_MarsGlobalGeologicGIS_20M\SIM3292_geodatabase.gdb")
SRC_CRATERS = os.path.join(REF, r"Robbins_craters_2020\Catalog_Mars_Release_2020_1kmPlus_FullMorphData.csv")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", HERE), "Temp", "mars_scratch")
SGDB = os.path.join(SCRATCH, "reference_build.gdb")
MARS = arcpy.SpatialReference(104905)                     # GCS_Mars_2000_Sphere
UNITS, CRATERS = "Ref_SIM3292_GeologicUnits", "Ref_Craters_Robbins2020"
SRC_TAGS = {UNITS: "USGS SIM 3292 (Tanaka et al. 2014)", CRATERS: "Robbins & Hynek, 2020 release"}

arcpy.env.overwriteOutput = True


def safe_to_replace(fc, tag):
    if not arcpy.Exists(fc):
        return True
    names = [f.name for f in arcpy.ListFields(fc)]
    if "Source" not in names:
        return False
    with arcpy.da.SearchCursor(fc, ["Source"]) as c:
        return all(r[0] == tag for r in c)


def find_units():
    arcpy.env.workspace = SRC_UNITS
    for ds in arcpy.ListDatasets() or [""]:
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            if fc == "SIM3292_Global_Geology":
                return os.path.join(SRC_UNITS, ds, fc)
    raise SystemExit("SIM3292_Global_Geology not found")


def unit_group(u):
    """SIM 3292 unit symbols are age prefix(es) + type: 'AHv' -> 'v' (volcanic), 'lAv' -> 'v',
    'Ave' -> 've' (volcanic edifice), 'mAl' -> 'l'. An age is an optional e/m/l (early, middle,
    late) followed by N, H or A, repeated; whatever follows is the type."""
    m = re.match(r"^(?:[eml]?[NHA])+(.+)$", u or "")
    return m.group(1) if m else (u or "")


def build_units():
    src = find_units()
    tmp = os.path.join(SGDB, UNITS)
    arcpy.management.Project(src, tmp, MARS)
    arcpy.management.AddField(tmp, "UnitGroup", "TEXT", field_length=16)
    arcpy.management.AddField(tmp, "Source", "TEXT", field_length=64)
    with arcpy.da.UpdateCursor(tmp, ["Unit", "UnitGroup", "Source"]) as c:
        for r in c:
            c.updateRow([r[0], unit_group(r[0]), SRC_TAGS[UNITS]])
    return tmp


def build_craters():
    tmp_csv = os.path.join(SCRATCH, "robbins_points.csv")
    n, lon_raw = 0, []
    with open(SRC_CRATERS, encoding="utf-8-sig", newline="") as fi, open(tmp_csv, "w", newline="", encoding="utf-8") as fo:
        rd = csv.DictReader(fi)
        wr = csv.writer(fo)
        wr.writerow(["CraterID", "Lat", "Lon", "DiamKm"])
        for r in rd:
            lon = float(r["LON_CIRC_IMG"]); lat = float(r["LAT_CIRC_IMG"]); d = float(r["DIAM_CIRC_IMG"])
            lon_raw.append(lon)
            lon = (lon + 180.0) % 360.0 - 180.0
            wr.writerow([r["CRATER_ID"], lat, lon, d])
            n += 1
    print("   craters read: %d, source longitude range %.2f .. %.2f" % (n, min(lon_raw), max(lon_raw)))
    tmp = os.path.join(SGDB, CRATERS)
    arcpy.management.XYTableToPoint(tmp_csv, tmp, "Lon", "Lat", coordinate_system=MARS)
    arcpy.management.AddField(tmp, "Source", "TEXT", field_length=64)
    arcpy.management.CalculateField(tmp, "Source", repr(SRC_TAGS[CRATERS]), "PYTHON3")
    return tmp


def main():
    t0 = time.time()
    os.makedirs(SCRATCH, exist_ok=True)
    if arcpy.Exists(SGDB):
        arcpy.management.Delete(SGDB)
    arcpy.management.CreateFileGDB(SCRATCH, os.path.basename(SGDB))
    built = {UNITS: build_units(), CRATERS: build_craters()}
    for name, tmp in built.items():
        dst = os.path.join(GDB, name)
        if not safe_to_replace(dst, SRC_TAGS[name]):
            sys.exit("REFUSING: %s holds rows this script did not write" % dst)
        if arcpy.Exists(dst):
            arcpy.management.Delete(dst)
        for attempt in range(3):              # Z: has failed a copy once and worked on retry (§36.4)
            try:
                arcpy.management.Copy(tmp, dst)
                break
            except Exception as e:
                print("   copy attempt %d failed: %s" % (attempt + 1, e))
                time.sleep(5)
        else:
            sys.exit("copy to Z: failed three times")
        print("  %-28s %8s rows  -> %s" % (name, arcpy.management.GetCount(dst)[0], dst))
    print("done in %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
