# -*- coding: utf-8 -*-
"""Second pass: check what verify_all.py did NOT.

  A. The BUILT .pptx/.docx, not content.py -- a stale build would have slipped
     through the first sweep entirely.
  B. The .gdbtablx reader itself, cross-validated against GDB_SystemCatalog,
     since every geodatabase conclusion depends on it.
  C. Claims the first sweep tested too narrowly or not at all.
"""
import os
import re
import struct
import sys
import zipfile

DELIV = r"C:\Users\Loggg\Downloads\Mars Remote Sensing Project"
GDB = r"Z:\Mars Project\Mars Project.gdb"
FILES = {
    "Presentation 1": "Mars Global Mosaic - Presentation 1.pptx",
    "Prospectus": "Mars Mosaic - Project Prospectus.docx",
    "Interim deck": "Mars Global Mosaic - Interim Presentation.pptx",
    "Interim report": "Mars Mosaic - Interim Report.docx",
}
res = []


def check(claim, ok, ev):
    res.append((bool(ok), claim, ev))


def doc_text(path):
    """All visible text from an OOXML package, speaker notes included."""
    out = []
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if re.match(r"(word/document|word/(header|footer)\d*|"
                        r"ppt/(slides|notesSlides)/[a-zA-Z]+\d+)\.xml$", n):
                xml = z.read(n).decode("utf-8")
                out += re.findall(r"<[aw]:t[^>]*>([^<]*)</[aw]:t>", xml)
    return " ".join(out)


texts = {k: doc_text(os.path.join(DELIV, v)) for k, v in FILES.items()}
allt = " ".join(texts.values())

# ---- A. the built artefacts carry the corrections -------------------------
MUST_GO = [
    # he holds three rasters only: Viking MDIM, THEMIS Day IR, HRSC/MOLA DEM
    ("re-acquire", "nothing may be planned around imagery he does not have"),
    ("restored HiRISE", "same"),
    ("ground reference", "there is no ground reference"),
    ("Type area 2", "Jezero is a context map, not a second type area"),
    ("has to be downloaded again", "it is not coming back"),
    ("pyramids built", "pyramids do not exist"),
    ("Four attempts", "there was no fourth composite run"),
    ("fourth on 13 September", "there was no fourth composite run"),
    ("Roughly 32 GB", "the three rasters are 43.7 GB"),
    ("22.1 billion pixels", "22.14 bn valid of 22.77 bn"),
    ("no atmosphere correction", "contradicts the CO2 note"),
    ("work already assembled", "the HiRISE file is missing"),
    ("'Slope'", "straight quotes"),
    ("'slope'", "straight quotes"),
]
for bad, why in MUST_GO:
    hits = [k for k, t in texts.items() if bad in t]
    check("no built file says %r" % bad, not hits,
          "%s (%s)" % (why, "clean" if not hits else "still in " + ", ".join(hits)))

MUST_SAY = [
    ("213,390", "Presentation 1"), ("106,694", "Presentation 1"),
    ("44 GB", "Presentation 1"), ("22.8 billion", "Presentation 1"),
    ("Pyramids are not built", "Presentation 1"),
    ("Three attempts on 9 September", "Presentation 1"),
    ("No pyramids on the global rasters", "Presentation 1"),
    ("6 mbar of CO", "Presentation 1"),
    ("\u201cSlope\u201d on imagery is not slope", "Presentation 1"),
    ("Thanksgiving week", "Presentation 1"),
    ("43.7 GB of source imagery", "Interim report"),
    ("dead raster references", "Interim report"),
    ("so the project opens", "Interim report"),
    ("213,390", "Prospectus"),
    ("97.3% coverage", "Prospectus"),
]
for needle, where in MUST_SAY:
    check("%s contains %r" % (where, needle[:38]), needle in texts[where],
          "text extracted from the built file")

# speaker notes really are in the shipped deck
with zipfile.ZipFile(os.path.join(DELIV, FILES["Presentation 1"])) as z:
    notes = [n for n in z.namelist()
             if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n)]
check("shipped deck carries a note per slide", len(notes) == 22,
      "%d notesSlide parts for 22 slides" % len(notes))

# ---- the figure work -----------------------------------------------------
with zipfile.ZipFile(os.path.join(DELIV, FILES["Presentation 1"])) as z:
    media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    media_bytes = sum(z.getinfo(n).file_size for n in media)
check("deck embeds 11 figures and stays small",
      len(media) == 11 and media_bytes < 6e6,
      "%d media files, %.1f MB" % (len(media), media_bytes / 1e6))

for needle, where in [
        ("Type Areas for the Mosaic", "Presentation 1"),
        ("Where the Project\u2019s Data Sit on the Spectrum", "Presentation 1"),
        ("Louros Valles", "Presentation 1"),
        ("Ius Chasma", "Presentation 1"),
        ("mosaic seams", "Presentation 1"),
        ("central meridian", "Presentation 1"),
        ("USGS global geologic map", "Presentation 1"),
        ("No ground truth, and no sub-metre imagery", "Presentation 1"),
        ("hosted rover services", "Presentation 1"),
        ("Three dead raster references", "Interim report"),
        ("hosted Perseverance rover services", "Interim report"),
        ("Three coordinate frames", "Presentation 1"),
        ("central meridians", "Interim report"),
]:
    check("%s says %r" % (where, needle[:40]), needle in texts[where],
          "text extracted from the built file")

check("the deck never mentions HiRISE at all",
      "HiRISE" not in texts["Presentation 1"],
      "no sub-metre imagery is held, so the prospectus does not invoke any")
hir = texts["Interim report"].count("HiRISE")
check("HiRISE survives only as housekeeping in the interim",
      hir == 2 and "dead raster references" in texts["Interim report"],
      "%d mentions: the dead-reference item and its next step" % hir)
check("the location placeholder is gone from every file",
      not any("[Name the location here.]" in t for t in texts.values()),
      "resolved to Louros Valles from the map's own saved extent")

# the three source rasters really are on three different frames
from osgeo_shim import central_meridians                      # noqa: E402
cms = central_meridians()
check("THEMIS is on central meridian 180, the other two on 0",
      cms == {"Viking": 0.0, "THEMIS": 180.0, "DEM": 0.0},
      "read from each GeoTIFF's projection: %s" % cms)

# ---- B. cross-validate the .gdbtablx reader -------------------------------
def live(oid_file):
    tab = open(os.path.join(GDB, oid_file + ".gdbtable"), "rb").read()
    idx = open(os.path.join(GDB, oid_file + ".gdbtablx"), "rb").read()
    n, esz = struct.unpack("<II", idx[8:16])
    rows = []
    for i in range(n):
        raw = idx[16 + i * esz:16 + (i + 1) * esz]
        if len(raw) < esz:
            break
        off = int.from_bytes(raw, "little") & 0xFFFFFFFF
        if off:
            ln = struct.unpack("<I", tab[off:off + 4])[0]
            rows.append((i + 1, tab[off + 4:off + 4 + ln]))
    return rows


cat = live("a00000001")
declared = struct.unpack("<I", open(os.path.join(GDB, "a00000001.gdbtable"),
                                    "rb").read(8)[4:8])[0]
check("reader's live-row count matches the table header",
      len(cat) == declared,
      "%d rows walked vs %d declared in the header" % (len(cat), declared))

cat_names = []
for oid, blob in cat:
    m = re.search(rb"[A-Za-z][A-Za-z0-9_]{3,79}", blob)
    cat_names.append((oid, m.group().decode() if m else "?"))

on_disk = {int(f[1:9], 16) for f in os.listdir(GDB)
           if re.fullmatch(r"a[0-9a-f]{8}\.gdbtable", f)}
walked = {oid for oid, _n in cat_names}
missing = walked - on_disk
check("every live catalog row has a table file on disk",
      missing == {8},
      "only OID 8 (GDB_ReplicaLog) lacks one" if missing == {8}
      else "unexpected: %s" % sorted(missing))
check("no table file is absent from the live catalog",
      not (on_disk - walked), "orphans: %s" % sorted(on_disk - walked))

# the two independent readers must agree on the dataset list
items = live("a00000004")
item_paths = {m.group(1) for _o, b in items
              for m in [re.search(rb"<CatalogPath>\\([^<]*)</CatalogPath>",
                                  b)] if m
              for m in [re.search(r"<CatalogPath>\\([^<]*)</CatalogPath>",
                                  b.decode("latin-1"))] if m}
base = {n for _o, n in cat_names
        if not n.startswith(("GDB_", "fras_", "VAT_"))}
item_paths.discard("")            # the gdb root item's CatalogPath is '\\'
check("GDB_Items datasets == GDB_SystemCatalog base tables",
      item_paths == base,
      "%d datasets, symmetric difference %s"
      % (len(item_paths), sorted(item_paths ^ base) or "none"))

raw = open(os.path.join(GDB, "a00000004.gdbtable"), "rb").read().decode("latin-1")
check("the composite name exists ONLY in free space",
      "Slope_Mars_V1_CompositeBands" not in item_paths
      and raw.count("Slope_Mars_V1_CompositeBands") > 0,
      "%d raw byte hits, 0 live rows -- this is the trap I fell into"
      % raw.count("Slope_Mars_V1_CompositeBands"))

# ---- C. things the first sweep tested too narrowly ------------------------
nomen = sorted(n for n in base if n.startswith("MARS_nomenclature"))
groups = {}
for n in nomen:
    groups.setdefault(re.sub(r"_[23]$", "", n), []).append(n)
counts = {k: len(v) for k, v in groups.items()}
check("nomenclature copies are NOT uniformly three",
      len(nomen) == 14 and sorted(counts.values()) == [2, 3, 3, 3, 3],
      "%d feature classes: %s" % (len(nomen), counts))

# independent pyramid test: ArcGIS/GDAL would leave overviews in the aux.xml too
for fn in ("Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif",
           "Mars_Viking_MDIM21_ClrMosaic_global_232m.tif",
           "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif"):
    aux = open(os.path.join("Z:\\", fn + ".aux.xml"), encoding="utf-8").read()
    check("%s: no overview record in its sidecar either" % fn[5:20],
          not re.search(r"Overview|PyramidLevel|RRD", aux, re.I),
          "second, independent line of evidence for 'no pyramids'")

print("%-5s %-64s %s" % ("", "CHECK", "EVIDENCE"))
print("-" * 122)
for ok, claim, ev in res:
    print("%-5s %-64s %s" % ("ok" if ok else "FAIL", claim, ev))
bad = [r for r in res if not r[0]]
print("\n%d checks, %d failed" % (len(res), len(bad)))
sys.exit(1 if bad else 0)
