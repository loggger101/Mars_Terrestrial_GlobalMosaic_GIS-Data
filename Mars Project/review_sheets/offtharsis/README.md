# Off-Tharsis edifice and apron labels: a guide (about 1 hour, in Pro)

> **Done by the agent, 2026-11-10 (PROJECT-KNOWLEDGE.md §69.105).** The author does no more manual review, so the agent drew the labels on CTX and the DEM hillshade (`plates\`, made by `build\make_offtharsis_plates.py`), by the rule in `build\logs\agent_review\offtharsis_registration.md`: six volcanic edifice polygons at Nili and Meroe Paterae (block 4_0), MappedBy "agent CTX (KB 69.105)"; no apron, since no lobate debris apron was clear on the CTX views. Scored by `build\score_offtharsis.py`: U-Net v3 7.7 % edifice, SVM v3 0.6 %. The guide below is kept as written; an analyst's polygons drawn in Pro would be scored the same way.

**Why.** The seven-class U-Net leads the seven-class SVM by balanced accuracy, but most of that lead sits in the two
Tharsis held-out blocks (−9_−1 and −9_0), which hold nearly all the held-out volcanic edifice and apron ground
(PROJECT-KNOWLEDGE.md §69.44, §69.57, §69.61). New edifice and apron labels in held-out blocks outside Tharsis would
show whether the two maps recognise these classes elsewhere. The author agreed to draw them on 2026-11-03 (NEXT-STEPS.md §14
row 3).

**What to expect from it.** The held-out blocks are fixed (the same 14 since the first split), and outside Tharsis
they hold very little of either class. SIM 3292 maps no edifice or apron unit in 10 of the 12 blocks (`targets.md`,
made by `build\make_offtharsis_targets.py`). The real targets are:

| class | block | where | what to outline |
|---|---|---|---|
| 5 volcanic edifice | **4_0** (60–75°E, 0–15°N) | **Syrtis Major**: Nili Patera (67.2°E, 9.0°N, 68 km), Meroe Patera (68.8°E, 7.0°N, 53 km), Nili Tholus (a 7 km cone inside Nili Patera) | the two calderas and the shield's summit flanks around them, where CTX shows the edifice |
| 6 apron | **4_2** (60–75°E, 30–45°N) | **Nilosyrtis Mensae** (68.5°E, 34.8°N) and **Colles Nili** (62.9°E, 38.7°N) | lobate debris aprons around the mesas and knobs: the lobate, lineated aprons at their bases, not the mesas themselves |
| 6 apron (optional) | −11_1 (195–210°E, 15–30°N) | the Olympus Mons aureole, already 16 v3 apron pieces | only if CTX shows clear aureole lobes the v3 pieces miss |
| check first | −5_−1 (285–300°E) | Nia Tholus (285.1°E, 6.6°S, 34 km), in Valles Marineris | draw it as edifice only if CTX shows a volcanic cone; otherwise skip |

Anseris Mons (5_−2), Coprates Montes (−5_−1) and Nectaris Montes (−4_−1) are named "Mons" but are massifs and
chasma-wall relief, not volcanoes: not edifice. So each new class will rest on one block, two at most. The score will
say whether the maps find these features, polygon by polygon, but a block interval cannot be drawn from one block.
That limit goes in the paper either way.

**How.**
1. Open `Mars Project.aprx`, map **"Off-Tharsis labels (author)"**. It holds the CTX mosaic (streamed; needs a
   network), the target names, and the empty class **`Landform_TrainingSamples_offtharsis_draw`**. The v2 and v3
   held-out labels are there for context, switched off. No classification map is in this map: keep it that
   way, so the labels are drawn without seeing what the maps say.
2. Edit → Create Features → the "Draw here" layer. Draw each polygon where the class is clear on CTX, at least a few
   km across (the maps are scored at 400 m), inside one block (do not cross a 15° line).
3. Set **Classvalue** 5 (volcanic edifice) or 6 (apron) and **Classname** "volcanic edifice" or "apron". MappedBy
   fills itself with "author". Put any doubt in **Notes**.
4. About 5–10 polygons per class is plenty. Save edits and close Pro.

**After.** The agent scores the four-class and seven-class SVM and U-Net maps, and the nearest-training-polygon
baseline, on the drawn polygons (the cached 400 m arrays, about 15 minutes on the laptop), with predictions written before
any score is read, and records the result in the KB and the paper's Limits.
