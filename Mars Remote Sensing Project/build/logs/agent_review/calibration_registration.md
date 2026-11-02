# Agent review, calibration against the author (KB §69.51), registered before any sheet is viewed

Sample: 48 of the author's 209 reviewed Athabasca channel candidates (all rock-floored, ThermIdx < -0.15),
drawn with make_review_chips.py --where "Review IS NOT NULL" --sample 48 --seed 51; shown blind (no Review value,
no ThermIdx or slope on the sheets). The agent writes accept / reject / unsure for each slot to
calibration_decisions.json before the author's decisions are read.

Question per slot: is the line a real channel (a trough or valley the line follows along most of its length,
visible in the hillshade or the images), or a routing artefact across flat or featureless ground?

Prediction: agreement with the author >= 70 % on rows both decided (unsure dropped), Cohen's kappa >= 0.40.
Rule: if both hold, the agent reviews the 200 open rock-floored Athabasca channels the same way; if either fails,
the agent reviews none of them, they stay open, and the result is reported.
