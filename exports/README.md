# Vector layers from `Mars Project.gdb`

Exported by [`github_export_gdb.py`](../Mars%20Remote%20Sensing%20Project/build/github_export_gdb.py) on 2026-10-27.
Every feature class in the project geodatabase except the third-party reference layers (`Ref_*`:
the USGS geologic map and the Robbins crater database, available from their publishers). Row counts
were checked against the source.
"KB §N" is a section of the project knowledge base,
[`PROJECT-KNOWLEDGE.md`](../Mars%20Remote%20Sensing%20Project/PROJECT-KNOWLEDGE.md).
The same layers are in the release as a GeoPackage (`mars_project_vectors.gpkg.zip`).

**Class codes in the training layers:** 1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground.
Every labelled file and model uses these, and they are the project's schema (decided 2026-10-09, KB §11
q23). The class schema file `Composite Object Classes.ecs` swaps 2 and 3 and is superseded: don't draw
new samples under it (KB §29.2).

The Landform classes are in `Mars_Equidistant_Cylindrical_CM180` (metres, central meridian 180°);
the labels and nomenclature are in geographic `Mars_2000_(Sphere)`.

| Layer | Geometry | Rows | CRS | What it is | Fields |
|---|---|---|---|---|---|
| `MARS_nomenclature_albedo_March2019` | Point | 126 | Mars_2000_(Sphere) | IAU/USGS Gazetteer of Planetary Nomenclature, March 2019: albedo features. | `name`, `clean_name`, `approvaldt`, `origin`, `diameter`, `center_lon`, `center_lat`, `type`, `code`, `approval`, `min_lon`, `max_lon`, `min_lat`, `max_lat`, `ethnicity`, `continent`, `quad_name`, `quad_code`, `link`, `SymbolID` |
| `MARS_nomenclature_misc_March2019` | Point | 337 | Mars_2000_(Sphere) | IAU/USGS Gazetteer, March 2019: other named features. | `name`, `clean_name`, `approvaldt`, `origin`, `diameter`, `center_lon`, `center_lat`, `type`, `code`, `approval`, `min_lon`, `max_lon`, `min_lat`, `max_lat`, `ethnicity`, `continent`, `quad_name`, `quad_code`, `link` |
| `MARS_nomenclature_craters_gt100km_March2019` | Point | 141 | Mars_2000_(Sphere) | IAU/USGS Gazetteer, March 2019: named craters over 100 km. | `name`, `clean_name`, `approvaldt`, `origin`, `diameter`, `center_lon`, `center_lat`, `type`, `code`, `approval`, `min_lon`, `max_lon`, `min_lat`, `max_lat`, `ethnicity`, `continent`, `quad_name`, `quad_code`, `link`, `SymbolID` |
| `MARS_nomenclature_craters_lt100km_March2019` | Point | 972 | Mars_2000_(Sphere) | IAU/USGS Gazetteer, March 2019: named craters under 100 km. | `name`, `clean_name`, `approvaldt`, `origin`, `diameter`, `center_lon`, `center_lat`, `type`, `code`, `approval`, `min_lon`, `max_lon`, `min_lat`, `max_lat`, `ethnicity`, `continent`, `quad_name`, `quad_code`, `link`, `SymbolID` |
| `MARS_nomenclature_classicalbedo_March2019` | Point | 303 | Mars_2000_(Sphere) | IAU/USGS Gazetteer, March 2019: classical albedo features. | `name`, `clean_name`, `approvaldt`, `origin`, `diameter`, `center_lon`, `center_lat`, `type`, `code`, `approval`, `min_lon`, `max_lon`, `min_lat`, `max_lat`, `ethnicity`, `continent`, `quad_name`, `quad_code`, `link`, `SymbolID` |
| `Landform_LavaFlowMargins` | Polyline | 0 | Mars_Equidistant_Cylindrical_CM180 | Digitising target, task 11. Empty until digitised by hand. | `UnitName`, `Confidence`, `Evidence`, `Notes`, `MappedBy`, `MappedOn`, `FlowUnit`, `MarginType` |
| `Landform_ChannelCenterlines` | Polyline | 94 | Mars_Equidistant_Cylindrical_CM180 | Digitising target, task 11. Empty until digitised by hand. | `UnitName`, `Confidence`, `Evidence`, `Notes`, `MappedBy`, `MappedOn`, `Origin`, `OrderStrahler`, `GradientPct`, `SourceID` |
| `Landform_CraterRims` | Polygon | 26 | Mars_Equidistant_Cylindrical_CM180 | Digitising target, task 11. Empty until digitised by hand. | `UnitName`, `Confidence`, `Evidence`, `Notes`, `MappedBy`, `MappedOn`, `DiameterKm`, `Preservation`, `SourceID` |
| `Landform_ChannelCandidates_auto` | Polyline | 2,610 | Mars_Equidistant_Cylindrical_CM180 | Machine channel centrelines over Ius Chasma, from flow routing with filled ground masked out (KB §25). `SlopeDeg >= 5 AND ThermIdx < -0.15` selects the 188 steep, rock-floored ones worth digitising. | `UnitName`, `Origin`, `Confidence`, `Evidence`, `StrahlerOrd`, `LengthKm`, `ThermIdx`, `ThermSd`, `SlopeDeg`, `FillDepthM`, `Notes`, `MappedBy`, `MappedOn`, `Review`, `ReviewNote` |
| `Landform_CraterCandidates_auto` | Polygon | 1,685 | Mars_Equidistant_Cylindrical_CM180 | Machine crater candidates over Ius Chasma: closed depressions ≥ 1 km from fill depth (KB §26). Blind to breached craters. | `UnitName`, `Confidence`, `Evidence`, `DiameterKm`, `DepthMaxM`, `DepthMeanM`, `Aspect`, `FillRatio`, `ThermIdx`, `CenterLon`, `CenterLat`, `IAUName`, `Preservation`, `Notes`, `MappedBy`, `MappedOn`, `Review`, `ReviewNote` |
| `Landform_BasinCandidates_auto_60` | Point | 5,144 | Mars_Equidistant_Cylindrical_CM180 | Closed basins ≥ 20 km over ±60°, the coarse planet-scale pass (KB §28.11, §32.1). | `Confidence`, `Evidence`, `DiameterKm`, `DepthMaxM`, `DepthMeanM`, `Aspect`, `FillRatio`, `CenterLon`, `CenterLat`, `Preservation`, `Notes`, `MappedBy`, `MappedOn`, `ThermIdx` |
| `TrainingSamples_202609290009589587982` | Polygon | 455 | Mars_2000_(Sphere) | The first hand-drawn training set, saved from Pro on 29 Sep (455 polygons, KB §29.2). | `Classcode`, `Classname`, `Classvalue`, `RED`, `GREEN`, `BLUE`, `Count`, `SHAPE_Length`, `SHAPE_Area` |
| `Landform_TrainingSamples_terrain` | Polygon | 512 | Mars_2000_(Sphere) | **The 512 hand-drawn training polygons**, four classes, planet-wide (KB §29.2). The labels everything supervised is trained on. | `Classcode`, `Classname`, `Classvalue`, `RED`, `GREEN`, `BLUE`, `Count`, `ImageURI`, `IShape`, `SHAPE_Length`, `SHAPE_Area` |
| `Analysis_Extent_60` | Polygon | 1 | GCS_Mars_2000 | The analysis extent: ±60.0003° latitude, the THEMIS night mosaic's own edge (KB §16, §31.3). | `MappedBy`, `Note` |
| `Landform_TrainingSamples_terrain_60_train` | Polygon | 329 | Mars_2000_(Sphere) | The hand-drawn polygons clipped to ±60° and split by whole 15° blocks, seed 60: the 329 used for training (KB §31.3). | `Classcode`, `Classname`, `Classvalue`, `RED`, `GREEN`, `BLUE`, `Count`, `ImageURI`, `IShape`, `MappedBy`, `Split`, `Block`, `SHAPE_Length`, `SHAPE_Area` |
| `Landform_TrainingSamples_terrain_60_test` | Polygon | 183 | Mars_2000_(Sphere) | The 183 held out: never trained on, used only for scoring (KB §31.3). | `Classcode`, `Classname`, `Classvalue`, `RED`, `GREEN`, `BLUE`, `Count`, `ImageURI`, `IShape`, `MappedBy`, `Split`, `Block`, `SHAPE_Length`, `SHAPE_Area` |
| `Landform_ChannelCandidates_auto_ath` | Polyline | 3,283 | Mars_Equidistant_Cylindrical_CM180 | Channel candidates over the Athabasca Valles type area (KB §42.1). | `UnitName`, `Origin`, `Confidence`, `Evidence`, `StrahlerOrd`, `LengthKm`, `ThermIdx`, `ThermSd`, `SlopeDeg`, `FillDepthM`, `Notes`, `MappedBy`, `MappedOn`, `Review`, `ReviewNote` |
| `Landform_CraterCandidates_auto_ath` | Polygon | 1,709 | Mars_Equidistant_Cylindrical_CM180 | Crater candidates over the Athabasca Valles type area (KB §42.1). | `UnitName`, `Confidence`, `Evidence`, `DiameterKm`, `DepthMaxM`, `DepthMeanM`, `Aspect`, `FillRatio`, `ThermIdx`, `CenterLon`, `CenterLat`, `IAUName`, `Preservation`, `Notes`, `MappedBy`, `MappedOn`, `Review`, `ReviewNote` |
| `Landform_CraterCandidates_auto_60_smoke` | Point | 8,098 | Mars_Equidistant_Cylindrical_CM180 | X2's smoke-test window (KB §53.3), recreated by the smoke run. | `Confidence`, `Evidence`, `DiameterKm`, `DepthMaxM`, `DepthMeanM`, `Aspect`, `FillRatio`, `CenterLon`, `CenterLat`, `Preservation`, `Notes`, `MappedBy`, `MappedOn`, `ThermIdx` |
| `Landform_ChannelCandidates_auto_60_smoke` | Polyline | 5,305 | Mars_Equidistant_Cylindrical_CM180 | X2's smoke-test window (KB §53.3), recreated by the smoke run. | `UnitName`, `Origin`, `Confidence`, `Evidence`, `StrahlerOrd`, `LengthKm`, `FillDepthM`, `Notes`, `MappedBy`, `MappedOn` |
| `Check_Tiles_4096px_60` | Polygon | 954 | Mars_Equidistant_Cylindrical_CM180 | The 4096-pixel processing tiles that the 29 Sep SVM map follows (KB §30.2). | `MappedBy`, `Tile` |
| `Graticule_30deg` | Polyline | 17 | GCS_Mars_2000 | Latitude / longitude lines every 30° over ±60°, labelled (KB §44). | `Label`, `MappedBy` |
| `Graticule_2deg` | Polyline | 25 | GCS_Mars_2000 | Lines every 2° over the two type-area windows (KB §44). | `Label`, `MappedBy` |
| `Type_Areas` | Polygon | 2 | GCS_Mars_2000 | The Ius Chasma and Athabasca Valles windows as polygons (KB §44). | `Label`, `MappedBy` |
| `DL_Detections_heldout_20261019` | Polygon | 1,838 | Mars_Equidistant_Cylindrical_CM180 |  | `Class`, `Classvalue`, `Confidence`, `Model`, `MappedBy` |
| `DL_UNet_Heldout_Scores_20261020` | Polygon | 183 | Mars_2000_(Sphere) |  | `Classname`, `Classvalue`, `Block`, `UNet_Own`, `UNet_Major`, `SVM_Own`, `SVM_Major`, `MappedBy` |
| `Landform_TrainingSamples_v2_proposals` | Polygon | 1,086 | Mars_2000_(Sphere) | The seven-class revision (D17), proposed, not decided: the 512 with an `Action` and its evidence each, plus 574 new polygons for classes 5-7. Only rows the author sets `Review` accept on enter the v2 labels, through `apply_label_review.py` (KB §68.5, §69.2). | `OldOID`, `OldClass`, `OldName`, `Action`, `ProposedClass`, `ProposedName`, `Subtype`, `Reason`, `Evidence`, `Split`, `Block`, `KM2`, `ShareVolc`, `ShareVE`, `ShareApron`, `CraterCover`, `MaxCraterKm`, `ReliefM`, `SlopeMed`, `ValleyKm`, `Review`, `ReviewNote`, `MappedBy` |
| `Landform_TrainingSamples_v2p` | Polygon | 1,085 | Mars_2000_(Sphere) | A rehearsal, not the author's labels: every v2 proposal taken as proposed (`apply_label_review.py --rehearsal`), to test the v2 runs before the review (KB §69.4). Never a result. | `Classcode`, `Classname`, `Classvalue`, `RED`, `GREEN`, `BLUE`, `Subtype`, `ProposalOID`, `OldOID`, `MappedBy` |
| `Landform_TrainingSamples_v2p_60_train` | Polygon | 827 | Mars_2000_(Sphere) | The rehearsal labels clipped to ±60°, training half (827; KB §69.4). | `Classcode`, `Classname`, `Classvalue`, `RED`, `GREEN`, `BLUE`, `Subtype`, `ProposalOID`, `OldOID`, `MappedBy`, `Split`, `Block` |
| `Landform_TrainingSamples_v2p_60_test` | Polygon | 258 | Mars_2000_(Sphere) | The rehearsal labels clipped to ±60°, held-out half (258; KB §69.4). | `Classcode`, `Classname`, `Classvalue`, `RED`, `GREEN`, `BLUE`, `Subtype`, `ProposalOID`, `OldOID`, `MappedBy`, `Split`, `Block` |

**In the release GeoPackage only** (too big for git: GitHub refuses files over 100 MB): `mars_project_vectors.gpkg.zip` in [`data-2026-10-21`](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases/tag/data-2026-10-21):

- `Landform_CraterCandidates_auto_60`: 465,354 rows. Closed depressions ≥ 1 km over ±60°, the X2 fine pass (KB §53.4; the tiles over 180° rerun, §54).
- `Landform_ChannelCandidates_auto_60`: 969,822 rows. Channel segments over ±60°, the X2 fine pass (KB §53.4, §54).
