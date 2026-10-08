# -*- coding: utf-8 -*-
r"""Writes docs\rasters.md in the GitHub repo: every backed-up raster, what it is, read from its header (KB §35).

    <ArcGIS python.exe> github_catalog_rasters.py

For each raster in Global60\, TypeArea\ and the two gdb rasters exported for the release, the
grid, size, data type, band count and NoData come from GDAL, not from memory; the description
and the release asset that holds it come from the tables below. A raster on the drive that the
tables don't describe is listed with "(not described)" so a new product can't slip in silently.
Reads Z: only (headers, not pixels: a few seconds). --repo as in github_sync.py.
"""
import os, sys, glob, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from osgeo import gdal, osr
gdal.UseExceptions()

DRIVE = Path(__file__).resolve().parents[2]
MP = DRIVE / "Mars Project"
REPO = Path(sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else
            Path.home() / "OneDrive" / "Documents" / "GitHub" / "Mars_Terrestrial_GlobalMosaic_GIS-Data")
URL = "https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/"
DATA, DERIV = "data-2026-10-06", "derivatives-2026-10-06"

LANDFORM_VALUES = "Classes 1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground, 255 no class"
IUS_SUP_VALUES = ("Classes 1 crater interior, 2 steep wall, 3 moderate wall, 4 chasma floor, 5 plateau flank, "
                  "6 plateau")
G60 = {
    "global60_svm_stack_200m.tif": "The classification stack, KB §31.2. Bands: Viking R, G, B, night IR, day IR, "
        "slope (°), 9 × 9 relief; each stretched p1–p99 to 1–255 over ±60° (limits in the `STRETCH` metadata). "
        "No elevation band, on purpose.",
    "global60_thermal_contrast.tif": "Diurnal-contrast index × 10000, KB §24, §28.3. Relative only: the THEMIS "
        "mosaics are locally stretched 8-bit DN, so values compare within one area, not across the planet "
        "(§28.10). Not thermal inertia.",
    "global60_thermal_contrast_200m.tif": "The same index aggregated to the 200 m DEM grid.",
    "global60_dem.tif": "HRSC/MOLA elevation in metres, nearest-neighbour onto the 200 m grid (exact: the "
        "DEM's native cell is 200 m to within 10 µm).",
    "global60_slope_deg.tif": "Slope in **degrees**, from the DEM on a metric grid (KB §28.8).",
    "global60_aspect.tif": "Aspect in degrees clockwise from north (gdaldem, Horn); flat ground is NoData.",
    "global60_hillshade.tif": "Hillshade, sun azimuth 225°, altitude 45° (gdaldem, Horn).",
    "global60_landforms_svm_400m.tif": "Landform classification, SVM on the hand-drawn labels, per pixel at 400 m "
        "(KB §31.3): 70.5 %, κ 0.54 on held-out polygons. " + LANDFORM_VALUES + ".",
    "global60_landforms_svm_400m_mode3.tif": "The same, 3 × 3 majority filter (KB §32.2).",
    "global60_landforms_svm_400m_mode5.tif": "The same, **5 × 5 majority filter: the published version** "
        "(73.5 %, κ 0.58 held out; KB §32.2).",
    "global60_landforms_svm_400m_mode7.tif": "The same, 7 × 7 majority filter.",
    "global60_landforms_svm_400m_mode9.tif": "The same, 9 × 9 majority filter.",
    "smoke60_composite_4band.tif": "Smoke-test window of the ±60° pipeline (KB §28.11): Viking RGB + day IR.",
    "smoke60_composite_5band.tif": "Smoke-test window: Viking RGB + day IR + night IR.",
    "smoke60_day.tif": "Smoke-test window: THEMIS day IR.",
    "smoke60_night.tif": "Smoke-test window: THEMIS night IR.",
    "smoke60_viking.tif": "Smoke-test window: Viking RGB.",
}
IUS = {
    "ius_viking.tif": "Viking RGB, cubic convolution onto the type-area 100 m grid (KB §18).",
    "ius_day.tif": "THEMIS day IR, a window read (never warped).",
    "ius_night.tif": "THEMIS night IR, a window read.",
    "ius_dem.tif": "HRSC/MOLA elevation in metres, cubic convolution from 200 m to 100 m.",
    "ius_composite_4band.tif": "Viking R, G, B + day IR (KB §18.2).",
    "ius_composite_5band.tif": "Viking R, G, B + day IR + night IR: the type-area composite.",
    "ius_slope_deg.tif": "Slope in degrees (KB §20).",
    "ius_slope_pct.tif": "Slope in percent rise, kept to compare with the legacy layers (KB §7).",
    "ius_aspect.tif": "Aspect in degrees.",
    "ius_hillshade.tif": "Hillshade, 225° / 45°.",
    "ius_dn_diff.tif": "Raw day − night DN difference. A reader's first guess, kept to show why it misleads (KB §24.2).",
    "ius_thermal_contrast.tif": "Diurnal-contrast index in [−1, 1], each band scaled by its own p2–p98 first "
        "(KB §24.2). Stretched over Ius only: don't compare with the ±60° index.",
    "ius_fill.tif": "`Fill` of the DEM. Floods Ius Chasma up to 2,077 m (KB §25.1): don't route on it unmasked.",
    "ius_filldepth.tif": "Fill − DEM in metres: the flooded depth, and the crater detector's input (KB §25.1, §26).",
    "ius_fdr.tif": "Flow direction (D8) on the filled DEM.",
    "ius_fac.tif": "Flow accumulation, cells.",
    "ius_streams.tif": "Stream cells: > 5,000 upslope cells, filled ground masked out (KB §25).",
    "ius_strlink.tif": "Stream links.",
    "ius_strord.tif": "Stream order.",
    "ius_cratermask.tif": "The 1,685 crater candidates as a raster, one id per crater (KB §26).",
    "ius_segmented.tif": "First object-based pass: SegmentMeanShift 20/20/5 on bands 1, 4, 5 (KB §19, §23.2).",
    "ius_seg_isocluster_10.tif": "Iso Cluster on that segmentation, 10 classes.",
    "ius_seg_fine.tif": "Segmentation sweep, 20/20/5 (the inherited Mercury settings; KB §23.5).",
    "ius_seg_medium.tif": "Segmentation sweep, **14/14/30: the recommended setting** (KB §23.5).",
    "ius_seg_coarse.tif": "Segmentation sweep, 9/9/80.",
    "ius_obj_fine.tif": "Object-based classification of the fine segmentation.",
    "ius_obj_medium.tif": "Object-based classification of the medium segmentation.",
    "ius_obj_coarse.tif": "Object-based classification of the coarse segmentation.",
    "ius_obj_isocluster_10.tif": "Object-based Iso Cluster, 10 classes.",
    "ius_isocluster_10.tif": "Per-pixel Iso Cluster, 10 classes, on the 5-band composite (KB §19).",
    "ius_mlclassify_10.tif": "Maximum-likelihood pass on the Iso Cluster signatures: a no-op as run (KB §19.2).",
    "ius_train_lab.tif": "Terrain-derived training labels for the KB §27 accuracy test (6 classes, eroded cores).",
    "ius_stack_therm.tif": "5-band composite + diurnal-contrast index (6 bands, one NoData, KB §27).",
    "ius_stack_aug.tif": "5-band composite + index + slope (7 bands). Slope is in the labels too, so its "
        "score is an upper bound only (KB §27.2).",
    "ius_sup_spectral.tif": "Supervised, 5-band composite: 62.7 %, κ 0.41 (KB §27.2). " + IUS_SUP_VALUES + ".",
    "ius_sup_thermal.tif": "Supervised, + thermal index: 63.1 %, κ 0.41. Same class codes as `ius_sup_spectral`.",
    "ius_sup_augmented.tif": "Supervised, + index + slope: 82.6 %, circular (KB §27.2). Same class codes.",
    "val/oudemans_dem.tif": "Crater-detector validation window, Oudemans: DEM (KB §26.3).",
    "val/oudemans_fill.tif": "Oudemans: filled DEM.",
    "val/oudemans_depth.tif": "Oudemans: fill depth. The breached crater the detector misses.",
    "val/perrotin_dem.tif": "Crater-detector validation window, Perrotin: DEM.",
    "val/perrotin_fill.tif": "Perrotin: filled DEM.",
    "val/perrotin_depth.tif": "Perrotin: fill depth. Recovered within −7.1 % in diameter.",
}
CM0 = "Classified_202609300147338582853"   # the one raster on a 0° central meridian (Viking's grid)
GDB = {
    "Classified_202609292109007048151": "The 29 Sep SVM classification made in the Pro GUI. Follows its 4096-px "
        "processing tiles; below chance on its own labels (KB §30.2). Superseded, kept. " + LANDFORM_VALUES + ".",
    "Classified_202609300147338582853": "The 30 Sep SVM classification made in the Pro GUI. Mostly an elevation map (KB §30.3). "
        "Superseded, kept. " + LANDFORM_VALUES + ".",
    "Segmented_202609290011302066080": "The ±60° mean-shift segmentation made in the Pro GUI, 29 Sep (KB §29.5).",
}


def info(src):
    ds = gdal.Open(src)
    b = ds.GetRasterBand(1)
    wkt = ds.GetProjection()
    sr = osr.SpatialReference(wkt=wkt) if wkt else None
    srs = sr.GetName() if sr else "none"
    cm = sr.GetProjParm("central_meridian") if sr else None
    nd = b.GetNoDataValue()
    nd = "none" if nd is None else (f"{nd:.4g}" if abs(nd) > 1e6 else f"{nd:g}")
    out = dict(w=ds.RasterXSize, h=ds.RasterYSize, n=ds.RasterCount, cell=ds.GetGeoTransform()[1],
               dt=gdal.GetDataTypeName(b.DataType), nd=nd, srs=srs, cm=cm,
               proj=sr.GetAttrValue("PROJECTION") if sr else None, R=sr.GetSemiMajor() if sr else None)
    ds = None
    return out


def row(name, desc, i, size, where):
    grid = f"{i['w']:,} × {i['h']:,} @ {i['cell']:g} m"
    bands = f"{i['dt']}" + (f" × {i['n']}" if i["n"] > 1 else "")
    return (f"| `{name}` | {desc or '(not described)'} | {grid} | {bands} | {i['nd']} | "
            f"{size / 1e9:.2f} GB | {where} |" if size > 1e9 else
            f"| `{name}` | {desc or '(not described)'} | {grid} | {bands} | {i['nd']} | "
            f"{size / 1e6:.0f} MB | {where} |")


def main():
    head = "| File | What it is | Grid | Type | NoData | Size | In release |\n|---|---|---|---|---|---|---|"
    rel = lambda tag, asset: f"[`{tag}`]({URL}{tag}) `{asset}`"
    g60, ius, crs, frames = [], [], set(), {}
    for p in sorted((MP / "Global60").glob("*.tif")):
        i = info(str(p)); crs.add(i["srs"]); frames[p.name] = i
        big = p.name in G60 and not p.name.startswith(("global60_landforms", "smoke60"))
        where = rel(DERIV, p.name + ".part*") if big else rel(DATA, "global60-classification.zip")
        g60.append(row(p.name, G60.get(p.name), i, p.stat().st_size, where))
    ta = MP / "TypeArea"
    for p in sorted(ta.glob("*.tif")) + sorted((ta / "val").glob("*.tif")):
        key = p.relative_to(ta).as_posix()
        i = info(str(p)); crs.add(i["srs"]); frames[key] = i
        ius.append(row(key, IUS.get(key), i, p.stat().st_size, rel(DATA, "typearea-part*.zip")))
    gdb = []
    for name, desc in GDB.items():
        i = info(f"OpenFileGDB:{MP / 'Mars Project.gdb'}:{name}")
        frames[name] = dict(i)
        i["nd"] = "255"   # the gdb keeps a mask only; github_export_gdb.py writes 255 under it in the release file
        tag = DERIV if name.startswith("Segmented") else DATA
        gdb.append(row(name + ".tif", desc, i, 0, rel(tag, name + ".tif")).replace("| 0 MB |", "| — |"))
    # The coordinate-system note below states these facts; stop if a header no longer agrees with it.
    odd = {k: (f["proj"], f["cm"], f["R"]) for k, f in frames.items()
           if (f["proj"], f["R"]) != ("Equirectangular", 3396190.0) or f["cm"] != (0.0 if k == CM0 else 180.0)}
    assert not odd and crs - {"unknown"} == {"Mars_Equidistant_Cylindrical_CM180"}, \
        f"coordinate systems changed; rewrite the note: {odd} {crs}"
    missing = [n for n in G60 if not (MP / "Global60" / n).exists()] + \
              [n for n in IUS if not (ta / n).exists()]

    text = f"""# Rasters

Every raster backed up in the [releases]({URL.rsplit("/tag/", 1)[0]}), read from its own header by
[`github_catalog_rasters.py`](../Mars%20Remote%20Sensing%20Project/build/github_catalog_rasters.py)
on {time.strftime('%Y-%m-%d')}. "KB §N" is a section of
[`PROJECT-KNOWLEDGE.md`](../Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md).
[`restore.py`](../restore.py) puts each one back where the table's first column says, under
`Mars Project/Global60/`, `Mars Project/TypeArea/` or `Mars Project/restored_from_gdb/`. The type-area
zip also holds `TypeArea/_0based_originals/`, the `ius_sup_*` maps before the recode below; they are not listed.

**Classified rasters** hold the class code itself as the pixel value. Before 2026-10-07 they held
ClassifyRaster's 0-based values instead (KB §36), so a copy downloaded earlier needs +1.

**Coordinate system.** Every raster here is equidistant cylindrical on the Mars sphere
(R = 3,396,190 m), in metres, and all but one have the **central meridian at 180°**, so x runs
0–360°E. Software that assumes Earth or a 0° meridian will misplace them. The CRS is named
`Mars_Equidistant_Cylindrical_CM180` in `Global60/` and `TypeArea/`; the validation windows under
`TypeArea/val/` carry the same projection unnamed (`unknown`), and the geodatabase rasters call it
`SimpleCylindrical_Mars`. **The exception is `{CM0}`, the 30 Sep map: central meridian 0°**, on
Viking's 231.5 m global grid, so its x runs −180 to +180°E. The ±60° grids: 100 m is 213,388 × 71,130 and 200 m is
106,694 × 35,565, nested, with the origin at −10,669,400, +3,556,500
([`Global60/README.md`](../Mars%20Project/Global60/README.md)).

**Sizes** are on the drive; the release copies are the same bytes (split into 1.9 GB pieces where
the file is bigger). The `.ovr` pyramids are not in the releases: build them after restoring.

## ±60° analysis extent: `Mars Project/Global60/`

{head}
{chr(10).join(g60)}

## Ius Chasma type area: `Mars Project/TypeArea/`

All on one 100 m grid, 8,891 × 4,150, ~271–286°E, 6–13°S. The validation windows under `val/`
are on their own grids.

{head}
{chr(10).join(ius)}

## From the geodatabase: `Mars Project/restored_from_gdb/`

Made in the Pro GUI and kept inside `Mars Project.gdb`; exported as DEFLATE GeoTIFF for the release.

{head}
{chr(10).join(gdb)}
"""
    if missing:
        text += "\n**Described but no longer on the drive:** " + ", ".join(f"`{m}`" for m in missing) + "\n"
    out = REPO / "docs" / "rasters.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    undescribed = sum(r.count("(not described)") for r in g60 + ius + gdb)
    print(f"{len(g60)} Global60, {len(ius)} TypeArea, {len(gdb)} gdb rasters -> {out}")
    print(f"undescribed: {undescribed}, described but missing: {len(missing)}")


if __name__ == "__main__":
    main()
