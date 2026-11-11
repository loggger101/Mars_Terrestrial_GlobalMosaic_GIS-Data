# Review sheets: the candidate review without opening Pro (KB §69.51)

Each PNG shows six candidates, one per row, as four panels over the same square:

1. **local relief + line**: the elevation model minus its 2 km average. Troughs and valleys are dark, ridges and
   rims light. The orange line is the candidate.
2. **hillshade, 5x**: the same elevation model shaded with 5x vertical exaggeration.
3. **Viking colour** and 4. **THEMIS day IR**: the images. Only the two ends of the line are marked (orange
   circles), so the ground between them stays visible.

White means outside the type area's rasters (windows at its edge). The row's label gives its slot (for example `C4`), the line's length, its stream order and the window's width.

**Stair-step patterns** in panels 1 and 2 (straight terraces at 45° or 90°) are the elevation model's 1 m height
steps on flat ground, not landforms. A line that only follows those steps is a routing artefact.

## The CTX sheets (`ctx_*` folders, KB §69.52)

The same candidates on the CTX mosaic (~5 m, visible light), which shows the channels themselves:
1. **CTX + line**, 2. **CTX** with the line's ends only, 3. **CTX over 40 km** around it with the line, 4. **local
relief + line**. Esri's CTX tile service holds misplaced tiles at some zoom levels, so every close view is checked
against the 40 km view and rendered again at another zoom level when they disagree. The panel title says so:
"render x1.5" means it was redrawn, and "close tiles misplaced, 40 km view" means only the coarser view could be
trusted. White means no CTX coverage. The `ctx_*` folders take the same `answers.txt`.

## R2, the accuracy check (`r2` folder, KB §69.53)

210 points, six to a sheet: 175 drawn at random over the seven-class map's classes and 35 inside the author's own
held-out polygons, mixed together. No map class is shown. Per point: 1. **CTX over 8 km**, the point ringed (1 km
radius), 2. **CTX over 40 km**, 3. **DEM hillshade over 40 km**, 4. **over 160 km** for setting. Answer with the class
of the ground inside the ring, by the seven-class key (KB §68.1):

| letter | class | includes |
|---|---|---|
| `c` | Crater | impact only: floor, wall, rim, continuous ejecta |
| `h` | steep/windy hills | massifs, chasma walls, knobs, mesas |
| `t` | lava tube | pit chains, sinuous rilles, lava channels |
| `n` | Normal Ground | plains, volcanic plains included |
| `e` | volcanic edifice | shields, flanks, calderas, cones |
| `a` | apron | lobate debris aprons; Tharsis fan-shaped deposits; **the Olympus Mons aureole** |
| `f` | fluvial channel | water-cut channels and valleys |
| `u` | unsure | always allowed |

`answers.txt` in the `r2` folder, the same layout as below; then `python build\score_r2.py "<drive>\Mars
Project\review_sheets\r2\answers.txt" --author`. It first checks the answers on the 35 hidden polygon points against the
author's own classes, then estimates every map's accuracy and the class areas. About 2–3 hours for all 210.

## R1, the spot-check of the rule-screened labels (`r1` folder, KB §69.54)

The 172 apron and 276 fluvial channel labels of the seven-class training set were accepted or rejected by a written
rule, not by eye (KB §69.8). R1 measures how often the rule was right: 80 of them, 30 of the rule's accepts and 10 of
its rejects in each class, shuffled together; the rule's verdict is not shown. Per row: 1. the label's outline (orange)
over the **DEM hillshade** and 2. over **CTX**, each across the whole piece, two close windows boxed in blue; 3. and 4.
**CTX over 20 km** at those windows. The row title names the class to judge:

| class asked | `a` accept when | `r` reject when |
|---|---|---|
| **FLUVIAL CHANNEL?** (a 2.4 km strip) | the strip follows a water-cut channel or valley for most of its length | most of it runs over plains, ridges or crater walls, or the channel it follows is a lava channel |
| **APRON?** (a piece up to 3° across) | most of the piece is lobate debris apron, Tharsis fan-shaped deposit or Olympus Mons aureole (ridged, lobate terrain), as a training label would need | most of it is plains, mesas, crater or something else |

`u` (unsure) is always allowed. `answers.txt` in the `r1` folder, the same layout as below (every one of the 80
slots, `u` included); then `python build\score_r1.py "<drive>\Mars Project\review_sheets\r1\answers.txt"`. It reports,
per class, the share of the rule's accepts the author accepts, with an interval, and how many of all 192 fluvial and
155 apron accepts that makes fair labels. About 45 minutes.

## Answering

Write the answers in a text file named `answers.txt` in the same folder as the sheets: the slot, then one letter,
in any layout (`A1 a, A2 r, A3 u` or one per line). Part of a folder is fine; unanswered slots stay open. Then
tell the agent which folder is done. `build\apply_sheet_review.py` checks every answer, refuses the whole file on
any typo (nothing is written), backs up the layer, and writes the answers in.

| folder | what is asked | letters |
|---|---|---|
| `1_athabasca_channels_open` | the 200 rock-floored Athabasca channels not yet reviewed: is it a real channel? | `a` accept, `r` reject, `u` unsure |
| `2_origin_athabasca` | the 105 accepted Athabasca channels, 40 km windows: what made it? | `f` fluvial, `v` volcanic, `i` indeterminate |
| `3_origin_ius` | the 94 accepted Ius channels, 40 km windows: what made it? | `f`, `v`, `i` |

**Accept** when the line runs along a trough or valley for most of its length: a dark line under it in panel 1, a
groove in panel 2, or a linear band in day IR. **Reject** when it wanders across flat or pitted ground, follows only
the stair-steps, or cuts across ridges and rims. `u` costs nothing; use it whenever a row is not clear.

**Origin** (H2 needs at least 10 `f` and 10 `v`; `i` is always acceptable):

- *fluvial*: part of a branching network that joins downhill; cut into a slope or a crater wall; one of the
  grooves and streamlined islands that run along the outflow channel.
- *volcanic*: starts at a pit, fissure or vent and runs down a flow; sits on a lava lobe (a lobe with a sharp,
  rounded edge in day IR) and follows its length; a channel between raised banks (levees).
- *indeterminate*: neither is clear. At 100 m most rows may be indeterminate; that is a result, not a failure.

## Worked examples (`0_worked_examples`)

48 rows the author has already judged (from the 209 reviewed Athabasca channels), drawn the same way. Answers are
`author/agent`, where the agent judged them blind before reading the author's (KB §69.51):

```
A1 a/r  A2 a/r  A3 a/r  A4 r/r  A5 r/r  A6 a/u
B1 a/a  B2 r/u  B3 r/r  B4 a/r  B5 a/r  B6 r/r
C1 a/a  C2 r/r  C3 a/r  C4 a/a  C5 a/r  C6 a/r
D1 r/r  D2 a/r  D3 a/a  D4 r/u  D5 a/r  D6 r/r
E1 r/r  E2 a/r  E3 r/r  E4 a/r  E5 a/r  E6 a/r
F1 a/r  F2 r/r  F3 a/r  F4 r/r  F5 r/r  F6 r/r
G1 a/r  G2 r/a  G3 r/u  G4 r/r  G5 a/r  G6 a/u
H1 r/r  H2 a/r  H3 a/r  H4 r/r  H5 a/r  H6 a/r
```

The two agree on 20 of the 43 rows both decided (46.5 %, Cohen's kappa 0.08, no better than chance). Both accept
B1, C1, C4 and D3 (D3 is the 34 km line along a sinuous trough). The author accepts many short lines the agent rejects.
Neither judgement can be checked at 100 m.

## The agent's answers are in (KB §69.55)

At the author's word (2026-11-02) the agent's own CTX answers are written into the data, each marked as the agent's:
the 200 open Athabasca channels (`ctx_1`: 3 accept, 186 reject, 11 unsure), `Origin` on all 199 copies (`ctx_2`,
`ctx_3`: 29 fluvial, 0 volcanic), and R1 and R2 scored on the agent's labels. **Any answer of the author's replaces the
agent's**: answer any folder as below and `apply_sheet_review.py` overwrites the agent's row (never one of the
author's own). For R1 and R2, the author's `answers.txt` gives the author's scores beside the agent's.

Redraw any folder with `build\make_review_chips.py` (its docstring gives the commands). Of this folder only the
guides (`.md`) and the answer files (`.txt`) are mirrored to GitHub; the sheets themselves stay on the drive.

## The traced lava margins (`margins_check` folder, KB §69.104)

The author's check of the 86 margins the agent traced on CTX (D33), without Pro: 29 sheets, three margins each, every margin on the plate it was traced on, in orange beside the same view with only its ends ringed. Letters `k` keep, `p` partly, `n` no margin, `u` unsure; `answers.txt` in that folder, then `build\score_margin_check.py`. The folder's README gives the rule, written before any answer, and how T5 is rerun on the margins kept. Nothing is written into the layer from these answers.

## Off-Tharsis labels (`offtharsis` folder, KB §69.63)

Not a sheet: edifice and apron polygons drawn in Pro, in the map "Off-Tharsis labels (author)", for the held-out
blocks outside Tharsis. The folder's README gives the targets and the steps.
