# Agent review on CTX (KB 69.52), registered 2026-11-02 before any CTX sheet is viewed

Context: the blind check at 100 m failed (KB 69.51, kappa 0.08). The author then asked for the work to be done for
him. CTX (Murray Lab global mosaic V01, ~5 m, visible) is independent of the 100 m DEM, slope and THEMIS layers that
H1 and H2 test, so judgements made on it do not make those tests circular. Only one CTX view was seen before this
file: candidate 986 (calibration slot D3), used to check registration.

Sheets: make_ctx_chips.py, four panels per row (CTX + line, CTX with ends only, CTX 40 km around, local relief).
No Review, ThermIdx, slope or gradient on the sheets.

Channel rule (Review):
- accept: CTX shows an incised channel, trough, groove or a channel between banks under the line for at least
  half of its length (small offsets of up to ~0.5 km allowed: the line is routed on a 100 m DEM).
- reject: the line runs over ground with no such feature along it (plains, crater ejecta, terraces), or crosses
  ridges, scarps or crater rims rather than following a channel.
- unsure: anything in between.

Origin rule (on accepted copies; fluvial / volcanic / indeterminate), morphology on CTX only:
- fluvial: streamlined islands or longitudinal grooves of an outflow channel, a branching network whose branches
  join downslope, or a valley cut into a wall or slope (gully, alcove-fed channel).
- volcanic: a channel with raised banks (levees) on a lobate flow, a sinuous rille starting at a pit, fissure or
  vent, or a channel within a flow showing platy or ridged lava surface texture along it.
- indeterminate: neither clear, or both (Athabasca's flood-carved channels draped by lava are debated: an
  outflow-channel form under a lava surface is called indeterminate unless the channel itself shows levees).

Checks:
1. Reported, not gating: agreement with the author on 48 author-reviewed Athabasca rows not used in KB 69.51 (seed
   52). Prediction: agreement 55-75 %, kappa 0.1-0.5 (the author judged at 100 m).
2. Gate: a blind repeat of 30 of the 200 open rows (new slots, new order, seed 53) after the main pass, and of 30 of
   the 199 copies for origin. Agreement >= 80 % and kappa >= 0.60 on rows decided both times. If a gate fails, that
   set's decisions are not written to the gdb; they stay in logs\agent_review\.
3. If written: Review rows get ReviewNote "sheets <date>, agent CTX"; accept copies get MappedBy "agent CTX (KB
   69.52)"; the author's own decisions are never changed (apply_sheet_review.py refuses).

Amendment, 2026-11-02, after the 199 origin rows were decided and before any repeat sheet is drawn: the origin
repeat's 30 rows are drawn from the 199 copies pooled (105 Athabasca + 94 Ius), sorted by area, class and OBJECTID,
shuffled with random.Random(54), first 30. They are drawn per area by make_ctx_chips.py --redo on sub-indexes
holding only those rows (seed 54 for the new order) and scored as one set by score_agent_repeat.py. Prediction:
the gate fails or passes narrowly; most repeat rows will be indeterminate both times (65 of 94 Ius and 105 of 105
Athabasca are), and the f / i boundary on wall gullies is the likely place for changes.
