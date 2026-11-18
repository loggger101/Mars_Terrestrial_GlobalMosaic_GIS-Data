# Mars Project

The ArcGIS Pro project and everything small enough to keep beside it. The rasters themselves are
in the [releases](https://github.com/loggger101/Mars_Terrestrial_GlobalMosaic_GIS-Data/releases);
[`docs/rasters.md`](../docs/rasters.md) says what each one is and which release holds it.

| Folder or file | What it holds |
|---|---|
| `Mars Project.aprx` | the ArcGIS Pro project: 63 maps and 32 layouts |
| [`Global60/`](Global60) | the ±60° products: sidecars, attribute tables, models and the map layouts in `layouts/` (its own [README](Global60/README.md) gives the grid) |
| [`TypeArea/`](TypeArea) | the Ius Chasma type area's products (`ius_*`) and its layouts |
| [`Athabasca/`](Athabasca) | the Athabasca Valles type area's products |
| [`DLModels/`](DLModels) | the fourteen deep-learning models' metadata and training plots; the weights are in the release |
| [`LabeledObjects/`](LabeledObjects) | the deep-learning training exports' metadata; the image chips are in the release |
| [`review_sheets/`](review_sheets) | the guides to the candidate review and the answer files |
| [`GpMessages/`](GpMessages), [`ImportLog/`](ImportLog) | ArcGIS Pro's own geoprocessing logs |
| `THERMAL NIGHT.ecs`, `ClassDefinitions_*.ecd` | the class schema of the hand-drawn labels (1 Crater, 2 steep/windy hills, 3 lava tube, 4 Normal Ground) and the two support vector machine models trained in the Pro interface; `THERMAL NIGHT1.ecs` is an identical copy Pro saved |
| `Composite Object Classes.ecs` | a later schema of 1 Oct that swaps codes 2 and 3; superseded |
| `Mars Project.atbx` | the project's toolbox |

The vector layers of `Mars Project.gdb` (the hand-drawn labels, the candidates and the digitised
landforms) are exported to [`exports/`](../exports/README.md). The landform layouts are shown,
grouped, on the [project page](../README.md#layouts).
