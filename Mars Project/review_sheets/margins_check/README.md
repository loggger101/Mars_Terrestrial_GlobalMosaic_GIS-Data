# The traced lava margins, checked without Pro (D33; KB §69.52, §69.104)

The agent traced 86 lava-flow margins at Athabasca Valles on CTX (1,476 km, all 126 plates, KB §69.52), and T5 ran on
them (H1 not supported: day IR minus Viking red +4.9 pt, interval −2.7 to +13.1). A self-check is not a check, so the
author checks them (D33, 11-03). Pro works as before (`Landform_LavaFlowMargins`, MappedBy "agent CTX (KB 69.52)");
these sheets are the same check without Pro, answered as letters like the other folders here.

Each sheet (`margins_01.png` … `margins_29.png`) holds three margins, one per row, on the 24 km plate it was traced on
(the same CTX view the tracing used; km from the plate's south-west corner):

1. **CTX + line**: the margin in orange, its slot (`M01` … `M86`) at its middle; the plate's other margins thin and white.
2. **CTX**: the same view with only the line's two ends ringed, so the ground under it stays visible.

Neither the agent's confidence nor its margin type nor the geologic map's contact is shown.

## Letters

| letter | when |
|---|---|
| `k` keep | the line follows the edge of a lava flow (a lobate or digitate front, or the sharp boundary of the platy-ridged flood lava against other ground) along most of its length, within about 0.5 km (a quarter of a 2 km grid square) |
| `p` partly | a flow edge is there, but the line strays more than ~0.5 km from it over part of its length, or follows it for under half its length |
| `n` no margin | the line follows no lava-flow edge for most of its length (a scarp, a channel wall, a texture change that is not a flow edge, or nothing) |
| `u` unsure | always allowed |

Write `answers.txt` in this folder, one `M01 k` per margin in any layout (`M01 k, M02 n` works). Part of the folder is
fine; the T5 rerun waits for all 86. Then:

```
python build\score_margin_check.py "<drive>\Mars Project\review_sheets\margins_check\answers.txt"
```

It refuses the whole file on any unknown slot or letter. About an hour for all 86 (29 sheets).

## What the answers decide (registered 2026-11-10, before any answer)

- **Reported, no gate:** the share of the decided margins (`k`, `p`, `n`) kept as `k`, and as `k` or `p`, with
  Wilson 95 % intervals and the km each keeps; the same by the agent's own confidence (does its confidence track the
  check?).
- **T5 rerun, two forms, in this order:** `make_flow_margin_test.py --margins --check build\logs\margin_check.json
  --keep k` (the margins kept as `k`), then `--keep kp`. The design and rule of KB §47.2 are unchanged; only the lines
  differ. If a form keeps fewer than 10 lines or under 100 km, it is not run, and that is reported (the floor of the
  tracing's own amendment, `logs\agent_review\ctx_margins_registration.md`).
- **Prediction:** H1 not supported on either form (day IR minus Viking red, interval includes 0), as on all 86. A
  check that keeps every margin reproduces the all-86 result exactly (planted 11-10, KB §69.104).
- **The paper:** block 15 of `v2_drafts.tex` then names the check: its (a)–(g) take the checked result in place of
  the all-86 one, and "the AI assistant traced" becomes "traced by the AI assistant and checked by the author".
- **The data:** nothing is written into `Landform_LavaFlowMargins` from these answers; the class keeps all 86 and
  the check lives in `build\logs\margin_check.json`. Redrawing a margin is done in Pro, as before.

Redraw the sheets with `build\make_margin_check_sheets.py` (it reads the class and the cached CTX views, never renders).

## Amendment, 2026-11-10, before any answer: the agent answers (KB §69.105)

The author will do no more manual review ("i will not be doing any more manual review work myself, please perform
them yourself if there are any left that should be done", 2026-11-10). The agent answers these sheets instead, as a
**blind second reading of its own lines**: the sheets hide the confidence and type it gave when tracing, and it
reads them without opening `index.json`'s per-slot values. That measures whether the same reader, on a clean view,
keeps its own lines; it is not an independent check, and the paper says so. The letters, the scoring and the two T5
forms are unchanged; the answers go in `answers_agent.txt`, and the result in `build\logs\margin_check.json`.
**Prediction:** most lines kept (k at least 60 % of those decided), H1 not supported on either form.
