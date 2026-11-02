# Lava-flow margins at Athabasca traced on CTX, and T5 (H1) on them (KB 69.52), registered 2026-11-02 before tracing

Source: CTX only (Murray Lab V01, ~5 m, visible), through the checked renders of make_ctx_chips (close views kept only
when they agree with the 40 km view). Neither THEMIS band nor Viking is shown while tracing, so margins traced here are
independent of the bands T5 compares.

Where: windows along SIM 3292's lAv contacts inside the Athabasca window (the 1:20 M map says where flow edges are;
the tracing places them at CTX resolution). A margin is traced only where CTX shows a lava-flow edge: a lobate or
digitate front, or the sharp boundary of the platy-ridged flood-lava surface against other ground. No edge visible:
nothing traced in that window. Each traced line is one Landform_LavaFlowMargins row, MappedBy "agent CTX (KB 69.52)",
Confidence probable where the edge is sharp along the whole line, inferred where it fades.

T5 on the traced margins (make_flow_margin_test.py --margins): the design of KB 47.2 unchanged (profiles every 2 km,
perpendicular, sides 3-20 km out, null 2,000 random profiles >= 25 km from any margin, bootstrap over margins), except
the contacts are the traced margins.
Prediction: H1 NOT supported again: day IR's separation rate does not exceed Viking red's with an interval above zero
(KB 47.2: +8.7 pt [-1.7, +18.1] on the lAv contacts; A9: the lean survives topography). A sharper margin should raise
every band's rate above the 1:20 M contacts' 11-21 %.
Rule: KB 47.2's, unchanged.

## Amendment, 2026-11-02, before any line was traced
Plates W001-W003 were viewed (no line traced). Scope cut for time: margins are traced on W001-W003 plus a seeded random
sample of 37 more of the 126 plates (random.Random(5252).sample of W004-W126), 40 in all; the rest stay untraced and
are listed as such. T5's design is unchanged; its contacts are whatever the 40 plates yield. If fewer than 10 lines
(or under 100 km in all) are traced, T5 is not run on them and that is reported instead.
