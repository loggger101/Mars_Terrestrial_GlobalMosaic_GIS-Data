# -*- coding: utf-8 -*-
"""Final sweep: assert every disk-checkable claim in the deliverables.

Each check names the evidence it reads. Anything that cannot be checked from
disk (published wavelengths, the schedule, the hypotheses) is listed as such
rather than silently passed.
"""
import sys as _sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import re
import struct
import sys

sys.path.insert(0, on_drive(r"Mars Remote Sensing Project\build"))
import content as C                                            # noqa: E402

Z = on_drive()
PROJ = on_drive(r"Mars Project")
GDB = os.path.join(PROJ, "Mars Project.gdb")
TIFS = {
    "THEMIS": "Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif",
    "Viking": "Mars_Viking_MDIM21_ClrMosaic_global_232m.tif",
    "DEM": "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif",
}

results = []


def check(claim, ok, evidence):
    results.append((bool(ok), claim, evidence))


def tiff(path):
    fh = open(path, "rb")
    end = "<" if fh.read(2) == b"II" else ">"
    big = struct.unpack(end + "H", fh.read(2))[0] == 43
    if big:
        fh.read(4)
        nxt = struct.unpack(end + "Q", fh.read(8))[0]
        esz, cfmt = 20, end + "HHQ8s"
    else:
        nxt = struct.unpack(end + "I", fh.read(4))[0]
        esz, cfmt = 12, end + "HHI4s"
    ifds, tags = 0, {}
    while nxt and ifds < 64:
        fh.seek(nxt)
        n = (struct.unpack(end + "Q", fh.read(8))[0] if big
             else struct.unpack(end + "H", fh.read(2))[0])
        cur = {}
        for _ in range(n):
            tag, typ, cnt, val = struct.unpack(cfmt, fh.read(esz))
            w = 2 if typ == 3 else (4 if typ == 4 else 8)
            cur[tag] = int.from_bytes(val[:w], "little" if end == "<" else "big")
        if not ifds:
            tags = cur
        ifds += 1
        nxt = struct.unpack(end + ("Q" if big else "I"),
                            fh.read(8 if big else 4))[0]
    return tags, ifds


def stats(name):
    x = open(os.path.join(Z, TIFS[name] + ".aux.xml"), encoding="utf-8").read()
    g = lambda k: [float(v) for v in re.findall(r'%s">([-\d.e+]+)' % k, x)]
    return g("STATISTICS_MINIMUM"), g("STATISTICS_MAXIMUM"), \
        g("STATISTICS_MEAN"), g("STATISTICS_STDDEV"), g("STATISTICS_COUNT")


# ---------------------------------------------------------------- rasters ---
dims = {}
for k, fn in TIFS.items():
    t, ifds = tiff(os.path.join(Z, fn))
    dims[k] = (t[256], t[257], t.get(277, 1), t.get(258, 8), ifds)

check("THEMIS is 213,390 x 106,696",
      dims["THEMIS"][:2] == (213390, 106696), "TIFF header tags 256/257")
check("Viking is 92,160 x 46,080, 3 bands",
      dims["Viking"][:3] == (92160, 46080, 3), "TIFF header tags 256/257/277")
check("DEM is 106,694 x 53,347, 16-bit",
      dims["DEM"][:2] == (106694, 53347) and dims["DEM"][3] == 16,
      "TIFF header tags 256/257/258")
check("Pyramids are NOT built (1 IFD, no .ovr)",
      all(dims[k][4] == 1 for k in dims)
      and not any(os.path.exists(os.path.join(Z, f + e))
                  for f in TIFS.values() for e in (".ovr", ".rrd")),
      "IFD chain length + sidecar absence")

mn, mx, me, sd, cnt = stats("THEMIS")
check("THEMIS DN 1-255, mean 125.7, sigma 34.4",
      (mn[0], mx[0]) == (1, 255) and round(me[0], 1) == 125.7
      and round(sd[0], 1) == 34.4, "THEMIS .aux.xml statistics")
total = dims["THEMIS"][0] * dims["THEMIS"][1]
check("THEMIS 22.14 of 22.77 bn valid = 97.3%%",
      round(cnt[0] / 1e9, 2) == 22.14 and round(total / 1e9, 2) == 22.77
      and round(100 * cnt[0] / total, 1) == 97.3,
      "STATISTICS_COUNT vs array size")

mn, mx, me, sd, _c = stats("Viking")
check("Viking band 1 DN 18-207, mean 122.8, sigma 31.6",
      (mn[0], mx[0]) == (18, 207) and round(me[0], 1) == 122.8
      and round(sd[0], 1) == 31.6, "Viking .aux.xml band 1 statistics")

mn, mx, me, sd, _c = stats("DEM")
check("DEM -8,528 m to +21,226 m, mean -720.5, relief 29,754 m",
      (mn[0], mx[0]) == (-8528, 21226) and round(me[0], 1) == -720.5
      and mx[0] - mn[0] == 29754, "DEM .aux.xml statistics")

size = sum(os.path.getsize(os.path.join(Z, f)) for f in TIFS.values())
check("Three global rasters total ~44 GB",
      43.0 < size / 2 ** 30 < 45.0, "file sizes: %.2f GiB" % (size / 2 ** 30))

# ------------------------------------------------------------------- CRS ----
def geoascii(path):
    fh = open(path, "rb")
    end = "<" if fh.read(2) == b"II" else ">"
    big = struct.unpack(end + "H", fh.read(2))[0] == 43
    if big:
        fh.read(4)
        nxt = struct.unpack(end + "Q", fh.read(8))[0]
        esz, cfmt = 20, end + "HHQ8s"
    else:
        nxt = struct.unpack(end + "I", fh.read(4))[0]
        esz, cfmt = 12, end + "HHI4s"
    fh.seek(nxt)
    n = (struct.unpack(end + "Q", fh.read(8))[0] if big
         else struct.unpack(end + "H", fh.read(2))[0])
    for _ in range(n):
        tag, typ, cnt, val = struct.unpack(cfmt, fh.read(esz))
        if tag == 34737:
            off = int.from_bytes(val[:8 if big else 4],
                                 "little" if end == "<" else "big")
            fh.seek(off)
            return fh.read(cnt).decode("latin-1")
    return ""


check("DEM sits in GCS_Mars_2000_Sphere (degrees)",
      "GCS_Mars_2000_Sphere" in geoascii(os.path.join(Z, TIFS["DEM"])),
      "GeoAsciiParamsTag")
check("THEMIS and Viking sit in SimpleCylindrical Mars (metres)",
      all("SimpleCylindrical" in geoascii(os.path.join(Z, TIFS[k]))
          for k in ("THEMIS", "Viking")), "GeoAsciiParamsTag")

# ------------------------------------------------------------ gdb & logs ----
def live_rows(oid_file):
    tab = open(os.path.join(GDB, oid_file + ".gdbtable"), "rb").read()
    idx = open(os.path.join(GDB, oid_file + ".gdbtablx"), "rb").read()
    n, esz = struct.unpack("<II", idx[8:16])
    out = []
    for i in range(n):
        raw = idx[16 + i * esz:16 + (i + 1) * esz]
        if len(raw) < esz:
            break
        off = int.from_bytes(raw, "little") & 0xFFFFFFFF
        if not off:
            continue
        ln = struct.unpack("<I", tab[off:off + 4])[0]
        out.append(tab[off + 4:off + 4 + ln].decode("latin-1"))
    return out


items = live_rows("a00000004")
paths = [m.group(1) for r in items
         for m in [re.search(r"<CatalogPath>\\([^<]*)</CatalogPath>", r)] if m]
check("Five derived rasters live in the gdb",
      all(p in paths for p in ("Slope_Mars_H1", "Slope_Mars_M1", "Slope_Mars_V1",
                               "Surface_Mars1", "HillSha_Mars1")),
      "GDB_Items live rows via .gdbtablx")
check("No Composite Bands output exists",
      "Slope_Mars_V1_CompositeBands" not in paths,
      "GDB_Items live rows (the name survives only in free space)")


def rows(oid):
    p = os.path.join(GDB, "a%08x.gdbtable" % oid)
    return struct.unpack("<I", open(p, "rb").read(8)[4:8])[0]


check("IAU gazetteer: 141 craters >100 km, 972 <100 km, 1,113 total",
      rows(0x0d) == 141 and rows(0x0e) == 972 and rows(0x0d) + rows(0x0e) == 1113,
      "row counts of the two crater feature classes")
check("Nomenclature imported three times each",
      rows(0x0d) == rows(0x12) == rows(0x1d) == 141,
      "_2 and _3 duplicates carry identical counts")

msgs = "".join(open(os.path.join(PROJ, "GpMessages", f), encoding="utf-8-sig").read()
               for f in os.listdir(os.path.join(PROJ, "GpMessages")))
for claim, needle in [
    ("Slope on the DEM took 7 min 15 s", "Elapsed Time: 7 minutes 15 seconds"),
    ("Hillshade took 11 min 42 s", "Elapsed Time: 11 minutes 42 seconds"),
    ("Slope on Viking took 1 h 05 min 01 s",
     "Elapsed Time: 1 hours 5 minutes 1 seconds"),
    ("Surface Parameters took 1 h 26 min 45 s",
     "Elapsed Time: 1 hours 26 minutes 45 seconds"),
    ("No compatible GPU was detected", "No compatible GPU device has been detected"),
    ("WARNING 000869 on the DEM derivatives", "WARNING 000869"),
    ("Composite Bands cancelled by user", "Operation cancelled by user"),
    ("Composite attempt 1: 47 min 57 s", "Elapsed Time: 47 minutes 57 seconds"),
    ("Composite attempt 2: 1 min 41 s", "Elapsed Time: 1 minutes 41 seconds"),
    ("Composite attempt 3: 1 h 14 min 51 s",
     "Elapsed Time: 1 hours 14 minutes 51 seconds"),
]:
    check(claim, needle in msgs, "GpMessages XML")

def composite_cancellations(folder):
    """(start, elapsed) for every cancelled Composite Bands run, read per log.

    A bare count of the whole folder encodes the day it was written: a fifth
    attempt was cancelled on 24 Sep and "== 4" started failing (KB 17.2).
    Dating each run lets the checks below pin what the deliverables claim -
    four by 13 Sep - without breaking when another run is logged.
    """
    import datetime
    runs = []
    for f in os.listdir(folder):
        t = open(os.path.join(folder, f), encoding="utf-8-sig").read()
        if "Failed to execute (CompositeBands)" not in t:
            continue
        s = re.search(r"Start Time: ([^<]+)<", t)
        e = re.search(r"Elapsed Time: ([^)]+)\)", t)
        runs.append((datetime.datetime.strptime(s.group(1).strip(),
                                                "%A, %B %d, %Y %I:%M:%S %p"),
                     e.group(1) if e else ""))
    return sorted(runs)


cancelled = composite_cancellations(os.path.join(PROJ, "GpMessages"))
check("Exactly four Composite Bands runs were cancelled by 13 Sep",
      len([r for r in cancelled if r[0].date().isoformat() <= "2026-09-13"]) == 4,
      "GpMessages XML, dated per log")
check("The fourth attempt ran 13 Sep, 17 min 28 s",
      any(r[0].date().isoformat() == "2026-09-13" and r[1] == "17 minutes 28 seconds"
          for r in cancelled), "GpMessages XML, dated per log")
check("A fifth was cancelled 24 Sep after 10 min 01 s (KB 29.1)",
      any(r[0].date().isoformat() == "2026-09-24" and r[1] == "10 minutes 1 seconds"
          for r in cancelled), "GpMessages XML, dated per log")
check("Both DEM runs carry WARNING 000869",
      msgs.count("WARNING 000869") == 2, "GpMessages XML")

lin = open(os.path.join(GDB, "a00000004.gdbtable"), "rb").read().decode("latin-1")
check("Hillshade used azimuth 225, altitude 45, shadows",
      re.search(r"HillShade[^<]*225 45 SHADOWS", lin) is not None,
      "<Process> lineage")
# The raster itself left the project gdb on 2026-10-07 (KB §37) for Z:\_removed_not_Mars\, where
# its VAT is a00000010 (fields Value, Count). That folder may be deleted: then only the lineage is left.
MERC_VAT = os.path.join(Z, "_removed_not_Mars", "removed_not_Mars.gdb", "a00000010.gdbtable")
merc_rows = (struct.unpack("<I", open(MERC_VAT, "rb").read(8)[4:8])[0]
             if os.path.exists(MERC_VAT) else None)
# Its lineage survived only in the free space of the project gdb's GDB_Items, which the classes added
# on 2026-10-08 overwrote (KB §45); the moved copy keeps it in its own GDB_Items.
MERC_ITEMS = os.path.join(Z, "_removed_not_Mars", "removed_not_Mars.gdb", "a00000004.gdbtable")
merc_lin = lin + (open(MERC_ITEMS, "rb").read().decode("latin-1") if os.path.exists(MERC_ITEMS) else "")
check("Mercury Iso Cluster ran with 10 classes",
      re.search(r"IsoClusterUnsupervisedClassification[^<]*166m\.tif 10", merc_lin)
      is not None and merc_rows in (10, None),
      "<Process> lineage + VAT row count in _removed_not_Mars (KB §37)"
      + ("" if merc_rows is not None else "; VAT gone, lineage only"))

# --------------------------------------------------------- missing files ----
for fn in ("JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first.tif",
           "Mercury_MESSENGER_MDIS_Basemap_BDR_Mosaic_Global_166m.tif",
           "Enceladus_Cassini_DEM_global_200m_schenk2024.tif"):
    check("%s is NOT on the drive" % fn[:34],
          not os.path.exists(os.path.join(Z, fn)),
          "the layer resolves DATABASE=..\\. to Z:\\")

# -------------------------------------------------- deliverable self-check --
text = " ".join(str(x) for x in (C.TASKS, C.SIGNIFICANCE, C.DATA_HELD, C.DATA_NEEDED,
                                 C.PROBLEMS, C.RESOLUTION, C.PRELIM, C.ISSUES,
                                 C.NEXT_STEPS, C.PROGRESS, C.GOALS_SHORT))
for bad, why in [
    ("pyramids built", "claims pyramids that do not exist"),
    ("32 GB", "the three rasters are 43.7 GB"),
    ("22.1 billion pixels", "22.14 bn valid of 22.77 bn total"),
    ("no atmosphere correction", "contradicts the CO2 note"),
    ("already assembled, including the 25 cm HiRISE", "that file is missing"),
]:
    check("deliverables no longer say %r" % bad, bad not in text, why)

print("%-4s %-62s %s" % ("", "CLAIM", "EVIDENCE"))
print("-" * 118)
for ok, claim, ev in results:
    print("%-4s %-62s %s" % ("ok" if ok else "FAIL", claim, ev))
bad = [r for r in results if not r[0]]
print("\n%d checks, %d failed" % (len(results), len(bad)))
sys.exit(1 if bad else 0)
