# R1, the blind spot-check of the rule-screened apron and fluvial labels (NEXT-STEPS §12.3), registered 2026-11-02 before any row is drawn

Why: the 172 new apron and 276 new fluvial channel rows of the v2 labels were accepted or rejected by a written rule,
not by eye (KB 69.8, `review_v2_by_rule.py`): fluvial, a floor at least 20 m below a 4.8 km flank ring and ShareVolc
< 0.5 (192 accept, 84 reject); apron, SlopeMed >= 1 deg and CraterCover < 0.5 (155 accept, 17 reject). The final must
say so (§12.1). R1 gives the screen a measured precision: how many of its accepts the author's eye also accepts.

Who labels: the author. The agent does not answer R1: on R2's hidden calibration points (KB 69.53) it agreed with the
author's polygons on 16 of 17 decided rows of the four original classes but on 1 of 4 apron and 0 of 4 fluvial, the two
classes R1 asks about. An agent reading here would measure the agent, not the rule.

Design (make_r1_sheets.py --sample, seed 5401), from logs\label_review_by_rule.json (the rule's verdict per row):
- fluvial (class 7): 30 of the 192 accepts and 10 of the 84 rejects; apron (class 6): 30 of the 155 accepts and 10 of
  the 17 rejects; 80 rows, drawn without replacement, then shuffled together into one order, six to a sheet.
- The key (slot -> OID, class, the rule's verdict) goes to logs\r1\r1_key.json; the sheets read only
  logs\r1\r1_slots.json (slot -> OID, class). No sheet shows the verdict or the rule's measures.
- Per row (make_r1_sheets.py): the piece's outline over the DEM hillshade and over CTX, each across the whole piece;
  CTX over 20 km at the piece's label point and at its far end, outline drawn. The row title names the class asked.
- Answer: a accept (the piece is a fair training label of the class named: for fluvial, the strip follows a
  water-cut channel or valley for most of its length; for apron, most of the piece is lobate debris apron, Tharsis
  fan-shaped deposit or Olympus Mons aureole), r reject, u unsure.

Scoring (score_r1.py; reported, no gate: the author's eye is the reference): per class, the share of the rule's
accepts the author accepts (the screen's precision) and of its rejects the author rejects, each with a Wilson 95 %
interval; agreement and Cohen's kappa between rule and author on the rows the author decided; and the precision
applied to all of the class's accepts (an estimate of how many of the 192 / 155 are fair labels). Unsure rows are
dropped and counted. Rehearsed on planted answers before any real answer is read.

Predictions:
1. Fluvial: the author accepts at least 60 % of the rule's accepts.
2. Apron: the author accepts a smaller share of the rule's accepts than for fluvial (the pieces are 3 deg pieces of
   SIM 3292 units, untrimmed, with mesas and plains inside, KB 68.5).
3. Kappa between rule and author below 0.4 in both classes.
