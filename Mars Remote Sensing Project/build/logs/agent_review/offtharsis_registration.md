# Off-Tharsis edifice and apron labels drawn by the agent on CTX, and their score (KB 69.105), registered 2026-11-10 before any plate was drawn

Why the agent: the author will do no more manual review (2026-11-10: "i will not be doing any more manual review work
myself, please perform them yourself if there are any left that should be done"). NEXT-STEPS §14 row 3 asked for
volcanic edifice and apron labels in held-out blocks outside Tharsis, so the seven-class maps' lead in those classes
can be tested off the two Tharsis blocks that hold nearly all of it (§69.44, §69.57, §69.61). The targets are those
of review_sheets\offtharsis\README.md (§69.63): Syrtis Major's paterae in block 4_0 (edifice); Nilosyrtis Mensae
and Colles Nili in block 4_2 (apron). The labels are the agent's, marked as such (§69.55's standing rule), and no one
checks them.

## Drawing

Source: make_offtharsis_plates.py, CTX (checked renders) beside the 200 m DEM hillshade, a degree grid on both. No
classification map, label set or geologic unit is shown while drawing.
- **5 volcanic edifice**: ground CTX or the hillshade shows as part of the volcanic construct: a caldera's floor,
  walls and rim; a cone; the summit flanks next to a caldera where the shield's surface is visible. Not the far,
  plains-like flanks of the shield, where nothing on the image separates edifice from plains.
- **6 apron**: lobate debris aprons: the lobate, lineated, convex aprons at the foot of mesas and knobs, from the foot
  of the scarp to the apron's toe; not the mesa tops, not the plains beyond the toe.
- Each polygon is drawn only where the class is clear, at least ~5 km across (the maps are scored at 400 m), inside
  its block (60–75°E; 0–15°N or 30–45°N). Five to ten per class. Vertices are read off the plates' grid (to about
  0.02°) and written by apply_offtharsis_labels.py into Landform_TrainingSamples_offtharsis_draw (not a digitising
  class), MappedBy "agent CTX (KB 69.105)", Notes naming the plate.
- If fewer than 3 polygons or under 300 km² of a class can be drawn, that class is not scored and that is reported.

## Score (score_offtharsis.py)

Maps: the seven-class v3 SVM (11 x 11 mode) and U-Net, the maps the final leads with (D36), at the scorer's 400 m
(the cached arrays), and the nearest-v3-training-polygon baseline (make_block_bootstrap's); the v2 maps reported
beside them with no prediction. The four-class maps cannot name either class and are not scored. Per class: the
area-weighted share of the drawn polygons each map calls that class (producer's accuracy), with a 95 % interval from
resampling the polygons (2,000 draws, seed 105), and what the maps call the rest. One block per class, so no block
interval; the paper's Limits says so.

Reference: on the 1,652 v3 held-out polygons, nearly all of whose edifice and apron lie in the Tharsis blocks,
producer's accuracy is U-Net v3 0.795 (edifice), 0.819 (apron); SVM v3 0.401, 0.038
(logs\global60_classification_check_*v3*.json).

Predictions:
- P1 U-Net v3's edifice share on the off-Tharsis edifice polygons is below its 0.795 on the v3 held-out set.
- P2 U-Net v3's apron share on the off-Tharsis apron polygons is below its 0.819.
- P3 U-Net v3 leads SVM v3 on each class (pooled share; the interval of the difference is not required to exclude 0).
- P4 The nearest-training-polygon baseline gives each class a share below 0.10 (the nearest training polygons off
  Tharsis are seldom edifice or apron).
Each is reported held or not held; none is changed after the score is read.
