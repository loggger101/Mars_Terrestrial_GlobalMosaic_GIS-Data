# R2, the probability-sample accuracy check (KB 69.53), registered 2026-11-02 before any point is drawn

Why: every score in the record is on hand-drawn held-out polygons, which sit where a class is clear (KB 69.46: the
maps agree more there, 73.6 against 61.4 %); only a probability sample gives unbiased accuracy and class areas
(Olofsson et al. 2014, Remote Sensing of Environment 148, 42-57). The author asked for the remaining work to be done
for him, so the agent labels the points; whether that labelling stands is decided by a gate against the author's own
classes, below.

Design (make_r2_points.py, seed 5301):
- Strata: the seven classes of the seven-class SVM map (11 x 11 mode), 400 m cached array, pixels valid in all four
  scored maps; 25 points per stratum, drawn with probability proportional to area (cos latitude); weights W_h the
  strata's area shares over the same pixels.
- Calibration: 5 points per class (35) inside the author's held-out polygons (Landform_TrainingSamples_v2_60_test),
  hidden among the 175 sample points in one shuffled order. The key (kind, strata, map classes) is written to a
  separate file the labeller does not open before scoring.
- Sheets (make_r2_sheets.py): per point, CTX over 8 km with the point marked, CTX over 40 km, DEM hillshade over 40 km
  and over 160 km. No map class, no stratum, no polygon is shown.
- Label: the class of the ground within ~1 km of the point (the 11 x 11 mode's 2.2 km unit) by KB 68.1's key:
  c Crater (impact only, floor, wall, rim and continuous ejecta), h steep/windy hills (massifs, chasma walls, knobs,
  mesas), t lava tube (pit chains, sinuous rilles, lava channels), n Normal Ground (plains, volcanic plains included),
  e volcanic edifice (shields, flanks, calderas, cones), a apron (lobate debris aprons; Tharsis fan-shaped deposits
  and the Olympus Mons aureole), f fluvial channel (water-cut channels and valleys), u unsure.

Gate (agent labelling): on the 35 calibration rows, at least 25 decided (not u), and on those agreement with the
polygon's class >= 0.70 and Cohen's kappa >= 0.60. If it fails, the agent's labels are reported as a failed attempt,
no accuracy or area estimate is reported from them, and the sheets are left for the author.

Scoring (score_r2.py): for each of the four maps, overall accuracy by the stratified estimator with its standard error
(unsure rows dropped, counts reported); for the seven-class SVM, user's and producer's accuracy per class and the
area-adjusted class areas with 95 % intervals. Rehearsed on planted labels before the real labels are read.

Predictions:
1. The gate: more likely fails than passes; calibration agreement 50-75 %, kappa 0.4-0.65.
2. If it passes: each map's sample accuracy is below its held-out polygon score (published four-class SVM 73.8 %,
   four-class U-Net 98.9 %, seven-class SVM 42.5 %, seven-class U-Net 69.0 %; KB 69.44).
3. If it passes: the seven-class SVM's fluvial channel (about a third of its map) has a user's accuracy below 20 %,
   and Normal Ground's reference area is larger than its mapped area.
