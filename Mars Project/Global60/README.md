# `Global60` — derived products at the analysis extent

Everything in this folder is on the **same content area as the source mosaics at
`Z:\`**, not on the Ius Chasma type area. That is the whole point of the folder:
`Z:\Mars Project\TypeArea\` holds the `ius_*` products for one 15 × 7° box, and
this holds the `global60_*` products for the full ±60° analysis extent.

Started 2026-09-19. See `PROJECT-KNOWLEDGE.md` §28 (the grid and the first products) and §31–32
(the classification).

## The grid

Defined once, in `build\grid60.py`, and **read from the night mosaic** rather
than hardcoded — so a product built through that module is co-registered with
the downloaded imagery by construction.

|  | G100 | G200 |
|---|---|---|
| size | 213,388 × 71,130 | 106,694 × 35,565 |
| cell | 100 m | 200 m |
| pixels | 15.18 bn | 3.79 bn |
| origin | −10,669,400 , +3,556,500 | identical |
| footprint | ±60.0003° lat, 360° lon | identical |
| CRS | `Mars_Equidistant_Cylindrical_CM180`, R = 3,396,190 m | identical |

`G200` is an exact 2 × 2 aggregation of `G100` — same origin, same footprint,
every 200 m cell edge falls on a 100 m cell edge. The two nest, so a 200 m
product and a 100 m product overlay without a reproject.

**The template is `Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif`**, per
KB §16.4: it is the binding raster, and the day mosaic sits at an exact integer
offset from it (+1 px in x, +17,783 px in y). So on this grid the day–night pair
is **never resampled** — it is a window read, not a warp.

## Which grid a product belongs on

- **100 m** for anything derived from the THEMIS mosaics. They are native here.
- **200 m** for anything derived from the DEM. HRSC/MOLA is natively
  0.0033741208°, which is **199.999990 m** on this sphere — 200 m to within
  10 µm, drifting 0.005 px across the full width. So at G200 the DEM warp is
  *exact*: nearest neighbour reproduces the original elevations, no
  interpolation. Running terrain at 100 m costs 4× and manufactures detail that
  was never measured. (`ius_dem.tif` had to interpolate, because the type-area
  stack targets 100 m.)

## Files

| file | grid | what |
|---|---|---|
| `global60_thermal_contrast.tif` | G100 | diurnal-contrast index ×10000, Int16, nodata −32768 |
| `global60_thermal_contrast_200m.tif` | G200 | the index aggregated to the DEM grid |
| `global60_dem.tif` | G200 | HRSC/MOLA, exact, Int16 |
| `global60_slope_deg.tif` | G200 | slope in **degrees** on a metric grid |
| `global60_aspect.tif` | G200 | aspect |
| `global60_hillshade.tif` | G200 | 225° / 45° |
| `global60_svm_stack_200m.tif` | G200 | the 7-band classification stack, 8-bit, no elevation band (§31.2) |
| `global60_landforms_svm.ecd` | | the support vector machine, trained on the training split of the hand-drawn labels (§31) |
| `global60_landforms_svm_400m.tif` | 400 m | the landform classification; pixel = class code 1–4, 255 none |
| `global60_landforms_svm_400m_mode3 / 5 / 7 / 9.tif` | 400 m | the same after an n × n majority filter; `_mode5` is the one to use (§32.2) |
| `smoke60_*.tif` | G100 | smoke-test windows of the pipeline: Viking, day, night, 4- and 5-band composites (§28.11) |
| `global60_svm_s_ClassifyRaste*.crf` | | temporary outputs `ClassifyRaster` wrote on 2 Oct; no layer uses them |
| `layouts\` | | PNG exports of layouts 04–07 |
| `_0based_originals\` | | the landform maps before their pixel values became the class codes (§36) |

The full-extent harmonised bands and Composite Bands (`global60_viking`, `_composite_4band`, …)
were never built at ±60°: only their smoke-test windows exist. The classification uses the stack above instead.

## Two things to keep straight

**The thermal index is not thermal inertia.** Both THEMIS mosaics are 8-bit DN
with no radiometric scaling, so calibrated inertia is not derivable from them
(KB §24.1). This is a *relative* index: high = large diurnal swing = dust,
low = damped = bedrock.

**It is stretched over ±60°, not over Ius.** The percentiles come from the whole
extent, so the numbers here are **not comparable** to `ius_thermal_contrast.tif`.
That is deliberate — a planet-wide index scaled to one canyon would be
meaningless — but it means a value from one cannot be quoted against the other.

## Checking it

```
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" verify_global60.py
```

Checks every product's corners to the millimetre, its cell size, its shape, its
CRS, and — for 200 m products — that it nests on the 100 m grid. Non-zero exit
if anything fails.

## `Z:\Global60`

A junction to this folder, for the legacy Spatial Analyst tools that reject the
space in `Mars Project` (KB §19.1). Same pattern as `Z:\TypeArea`.
