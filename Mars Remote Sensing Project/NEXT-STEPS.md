# Mars Global Mosaic — next steps

The plan. `PROJECT-KNOWLEDGE.md` ("KB", § numbers point into it) is the record and the authority on what
is true; when the two disagree, the KB wins and this file is fixed. Done work is recorded there and
**removed** from here, not struck through; sections 1–10 keep their numbers (scripts and the KB cite them). The
interim has its own plan, `INTERIM-PLAN.md`; how to work on either machine, including the start-of-session
checklist, is `HANDOFF-DESKTOP.md`.

| deadline | date |
|---|---|
| interim data cut | **26 October** (D20; was 2 November): the interim covers what is measured by then |
| interim presentation | **10 November** (D16, the author, 2026-10-27); the report's date not given, plan against the same day |
| label review, v2 runs, digitising: for the final | **27 October – 22 November** (the v2 runs need ~2 days after the label review) |
| data freeze | **22 November** |
| final | **Tuesday 8 December 2026** |

---

## Resume here — 2026-11-11 (§69.112)

Only the state, what waits on whom and the next step; the history behind each line is the KB section it cites
(condensed 2026-10-31, §13.1 P10: the dated paragraphs since 10-18 are in git history and KB §58–§69.34).

**Where it stands.**
- **The author does no more manual review (11-10); the agent did the items left (§69.105):** the 86 traced margins read again blind (56 of 85 kept; T5 on them not supported, +3.3 pt, −7.2 to +13.8), and six off-Tharsis edifice polygons at Syrtis Major (U-Net v3 7.7 %, SVM v3 0.6 %; no apron drawn). D33 closed; blocks 12, 15 and 19 (a)–(c), (g), (h) are in the paper (26 pages) and deck.
- **Both v3 maps lead the final (D36, §69.82; the author, 11-07), every extra run is scored, rep last, 11-11** (`run_v3x.ps1`, about 50–65 h from 11-07 14:47, queue replaced 15:30 after a fault in its exit codes, §69.83; fresh done 11-08, F1–F5 held, U-Net 86.6 % on 14 other blocks, in the paper and deck, §69.84; its weak hills are the rule-placed kind, §69.85; noth done 11-09: T1 not held, T2 held, −6.4 and −7.6 pt, not resolved by block, in the paper and deck, §69.86; the noth map differs more off the volcanic units than on them, and the rule's hills sit on crater flanks, §69.87; cut done 11-09: C1 held, 78.1 % balanced on the v2 polygons, no loss spikes, S1 registered for add, §69.88; a second v3 training, rep, queued after fresh2 at the author's yes (R1–R3 written first, second queue PID 64600; everything ends about early 11 Nov, add_train running ~23.5 min an epoch), §69.89; the loss spikes go with the added polygons, not the class weights, §69.90; noth's drop is apron read as edifice in the Tharsis block −9_−1, §69.91; cut falls short of base on Crater, gains edifice on Tharsis, §69.92; add done 11-09: C2, C4 held, C3 not, the halves about equal; S1 not decided (3.51); in the paper and deck, §69.93; the extra runs drawn in one figure, paper Figure 25 and deck slide 35, rerun when rep ends, §69.94; why the SVM did not rise: one pixel's bands, not its 1,000-a-class sample or its labels (stand-in, Q0–Q3 held), and the third set's hills take Crater, §69.95; surroundings to 20 km lift its stand-in 39.2 → 57.1 %, the third set still no help, §69.97; to 51 km 62.0 %, the U-Net still +9.7 to +37.1 ahead, §69.98; without the thermal bands that stand-in loses 8.0 points, resolved, mostly apron (N1, N2 not held), §69.99; all of it in the window statistics and most or all of it made up by map coordinates instead (S1 held, S2 not), §69.100; a second draw of the points repeats both (D1–D3 held; the coordinates make up 80 % there), §69.101; fresh2 scored 11-10: F6.1–F6.4 held, F6.5 not (U-Net 85.4 %, its lead over the nearest training polygon, 80.6 % there, resolved by balanced accuracy only), §69.96; that miss is fresh2's class mix: at the 1,652 polygons' mix the lead is resolved there, and over both draws as scored (P1–P4 held), §69.102; rep done 11-11 07:39: R1 and R2 held, R3 not; by score the thermal drop is larger than one training against another, by map it is not, and volcanic edifice covers 8.7 % of the windows against 16.3 %, so the class areas are one training's; in the paper, deck and release `data-2026-11-10`, §69.106). Scores (§69.81, §69.80): U-Net v3 87.6 %, κ 0.844 on the 237 v2 polygons (v2 69.0 %, 0.606) and 49.6 % (40.8–58.5) on the probability sample (21.7 %), edifice 18.0 % of ±60° (40.0), no polygon leak; the rule recommends it. SVM v3 39.1 %, κ 0.288 (v2 42.5 %, 0.310), sample 40.2 % (39.9): the rule does not, its Crater falls 21.8 points. The paper and deck moved to both on 11-07: the U-Net with the rule, the SVM against it, which both say.
- **The ±60° products** (KB §53–§57, §66): 465,354 closed depressions ≥ 1 km and 969,822 routed channel segments
  (layouts 11, 12), which find the mapped valleys no better than a rotated valley map (A1, §69.50): the DEM's
  drainage paths, not a channel map; the four-class SVM map at 200 m with an 11 × 11 majority filter, 73.8 %, κ 0.58 held out (§57,
  layout 04); the two-pass U-Net province map, 98.9 %, κ 0.980 held out (§66.8, layout 17). **A geography-only
  baseline**, each pixel the nearest training polygon's class, scores 83.2 % on the same polygons, above the SVM
  map, which leads it only by balanced accuracy (§69.35); in the paper since 11-01 (D30, §69.48). Crater size-frequency curves: §69.35.
- **How firm the scores are** (A5, §69.44): resampling the 14 held-out blocks, the four-class U-Net's lead over the
  SVM map (+11.1 to +41.0 pt) and T1's thermal gain (+0.46 to +2.67 pt) hold; the seven-class U-Net's 26.5-point
  accuracy lead over the seven-class SVM does not (−9.7 to +47.8; by balanced accuracy it does, +2.3 to +19.5), nor
  does the SVM map's position against the baseline either way. Three blocks hold 61.6 % of the four-class held-out
  area; the seven-class lead sits on the two Tharsis blocks. In the paper since 11-01 (D31, §69.47).
- **Crater recall explained** (A11, §69.45): recall rises with Robbins' rim state, 34.9 → 66.0 % at ≥ 5 km; fresh
  rims ≥ 10 km are found at 90–100 %; partial rims 18–27 points less often. C5's rule cuts both sets at Dmin, which
  understates recall by 4.5–8 points at every Dmin above 1 km (≥ 5 km: 52.4 % with one side cut) and precision at
  ≥ 50 km by 15–20. The paper's figure and text take the one-side cut since 11-01 (D32, §69.47).
- **Seven classes** (D17, D28): 971 reviewed v2 labels, 734 training and 237 held out (§69.8). On the v2 held-out
  polygons the seven-class SVM scores 42.5 %, κ 0.310 and the seven-class U-Net 69.0 %, κ 0.606; both fail D18's
  rule, and **they lead all the same** (layouts 04b, 13b, 17b; §69.24–§69.27). The U-Net maps edifice on 40.0 % of
  ±60° (§69.25; 39.5 % on T8's 1.6 km mask), 70 % of it off the volcanic units, most on SIM 3292's highland group, 46.8 % of which it calls edifice
  (T8, A14, §69.37). Against named features (A15, §69.39), fluvial channel concentrates on the named valleys' lines
  on both maps (U-Net 83 % of 83 valles), edifice on none of the 10 named small edifices on the U-Net.
  On the 1,652 v3 held-out polygons (A16, §69.57) both v2 maps score ~3 points lower (65.8 %, 39.8 %), and the
  U-Net's balanced lead (+12.5 pt) is not resolved by block; the paper and deck say so since 11-02 (D35).
- **Thermal:** T1, +1.36 pt at 200 m in overall accuracy and none by balanced accuracy (§56, §69.18, D25); T9 (A8,
  §69.50), on SIM 3292's unit groups, cannot price it: the stack predicts them no better than the commonest group; T3, the
  THEMIS pair against TES inertia peaks in 2–5° blocks at r ≈ 0.12 (§69.29; layout 18, §69.30).
- **The review, the critical path** (§69.33): **3,791 of 9,287 candidates**: every closed depression at both type
  areas, the 188 steep Ius channels, 209 of the 409 rock-floored Athabasca channels. The digitising classes hold 202
  channels, 381 crater rims, none drawn by hand, and 86 lava margins the agent traced on CTX (below). **The agent cannot stand in** (§69.51, 11-02): blind on 48 of the author's calls it agreed at chance
  (46.5 %, κ 0.08), so the review stays the author's, now **without Pro**: contact sheets and a guide in
  `Mars Project\review_sheets\`, answered as letters in `answers.txt`, written in by `apply_sheet_review.py`.
  **On CTX (§69.52, 11-02)** the agent traced **86 Athabasca lava margins (1,476 km, all 126 plates)** into
  `Landform_LavaFlowMargins` (MappedBy "agent CTX"), so T5 has run on traced margins: H1 still not supported
  (day IR − Viking red +4.9 pt [−2.7, +13.1]). Its
  channel review (3 accepts of 200) and its Origin (29 fluvial, 0 volcanic of 199) both **failed their repeat gates**;
  **at the author's word (11-02, §69.55) they are written in all the same, marked as the agent's** (ReviewNote /
  Notes "agent CTX (KB 69.55)"; any answer of the author's replaces them): the channel class now holds 202 (3 the
  agent's), Athabasca channel precision 27 % combined, the author's own 50 %. H2's stage 2 cannot run in these type
  areas: all 29 fluvial Origins are at Ius, and the author said skip drawing volcanic ones (§69.63). R1 and R2 are scored on the agent's labels too (§69.55).
- **The project and the deliverables:** 45 maps and 26 layouts, no broken source (§5; the 42nd, "Off-Tharsis labels (author)", 11-03, §69.63); every sheet's text read against the record and seven corrected 11-03, layout 14's recall now "–" until a feature is drawn by hand (§69.69). The interim at its 26 October
  cut (D20): 32 slides and a 21-page report, rebuilt 10-31 for layout 11's corrected citation (§69.34); speaker
  notes on every slide since 11-01, the slides unchanged (§69.41). The final
  paper (39 pages since 11-11, §69.117; the deck 51 slides since 11-11, §69.122, compiled by the repository's CI on every push that touches it, §69.42) and deck lead with the seven-class maps (§69.27); their review figures stay at §69.7's until the
  freeze (§12.1). Backup: release `data-2026-11-10` (§69.105; `data-2026-10-29`, §69.28, before it).
- **The machines:** the drive-root junctions point at `F:` and are broken on the laptop (§58); the drive and the
  clone agree, and `github_sync.py` refuses if the clone ever holds work the drive lacks (§69.20). `run_v3.ps1` ended 11-07 (§69.81):
  the drive and Pro are free again.
  The laptop runs scorer work from the cached 400 m class arrays (`build\*_ov400.npy`) in minutes; run
  one such job at a time: two together ran out of memory on 11-01 (§69.44).

**Next, in this order:**

| # | what | who | how | done when |
|---|---|---|---|---|
| 1 | **The author's review items: done by the agent, 11-10** (the author's word: no more manual review, KB §69.105): the 86 CTX-traced margins read again blind on the 29 sheets (`answers_agent.txt`; 56 `k`, 25 `p`, 4 `n`, 1 `u`); six off-Tharsis edifice polygons drawn at Syrtis Major, no apron (none clear on the CTX views). Nothing else is left for the author to review; the other 200 rock-floored Athabasca channels, the rest of the candidates and breached craters stay unreviewed unless asked | agent | §6 | done (§69.105) |
| 2 | After each review session: copy the accepts, refresh layout 14, re-export the gdb, push | agent | §3 | the repo's gdb export matches the drive; layout 14's table matches the tally |
| 3 | Retests: **done 11-10** (§69.105): T5 on the margins the second reading kept, form `k` +3.3 pt (−7.2 to +13.8), form `kp` +4.6 (−3.4 to +12.6), H1 not supported on either; the off-Tharsis edifice scored (U-Net v3 7.7 %, SVM v3 0.6 %; P1, P3, P4 held, P2 not tested). H2's stage 2 stays skipped (§69.63) | agent | §4 | done |
| 3b | **The v3 runs: done 11-07; D36: both lead; sheets, paper and deck moved (KB §69.82). Every extra run is done: rep, the second v3 training, scored 11-11 (R1, R2 held, R3 not), placed and added to release `data-2026-11-10` (§69.106; the others §69.84–§69.102, the release §69.105)** (KB §69.80, §69.81; `logs\v3_maps.json`, `logs\r2\r2_v3_result.json`). Every run and check in the sequence is finished; the rule recommends U-Net v3 and not SVM v3. **If the author picks a v3 map** (§69.77 has the audit): the layouts first, `make_v2_sheets.py`'s sheet text being specific to the v2 results, so v3 sheets are written from the v3 results, not by a flag, and `score_metrics.py` run on the v3 check logs for them; then the three figures and every v2 map number in the paper and `final.py`, by `verify_interim.py`; the `\VV` numbers in `v2_drafts.tex` blocks 18 and 19; a new data release (`github_release_bundle.py`'s globs already take the v3 maps and model) | agent, desktop | KB §69.49 | v3 maps scored on the v3 and the v2 held-out polygons |
| 4 | ~~The paper's analyses that need no author time~~: all done (A1–A16, KB §69.34–§69.57); nothing in §12.2 is left | agent | §12.2 | done |
| 5 | The interim: **the report went in on 5 Nov** (KB §69.79); the talk was given on **10 Nov** (the author, 11-11, KB §69.107) | author | `INTERIM-PLAN.md` §0, §6 | done |
| 7 | **The edifice retraining (D37, yes 11-11, KB §69.107):** the lead U-Net trained again with validation blocks of its own, edifice negatives on the highland group and class weights (§14 row 4); rule and predictions registered before the run; scored on the same held-out polygons and windows as base and rep; the paper and deck move only if the registered rule says it leads and the author picks it. **Registered and running since 11-11 12:10 (KB §69.108):** run `edf` = fresh's training polygons plus 420 rule-placed Normal Ground squares where the published map says edifice; `run_v3_edf.ps1` (PID 77672; export, ~13 h training, then the windows of edf, edfv and freshw), log `build/logs/run_v3_edf/queue.log`. **At "queue done":** `make_v3_edf.py --report` (ArcGIS Python) → `logs/v3_edf.json`, E1–E5 and the rule into a KB section. **Decided ahead (11-11, KB §69.109):** all five held (D39), classify ±60° in two passes at once and make it the lead U-Net (layouts, paper, deck); otherwise (D40) a paragraph in the paper and a row on the deck's extra-runs slide, the lead map unchanged. **Made ready 11-11 (KB §69.120):** for D39 `run_v3e_lead.ps1` (`make_v3e_global.py`; own scratch and names, dry-run only so far); the text for either outcome is `v2_drafts.tex` block 22 | agent, desktop | §14 row 4 | scored, in the KB, before **22 Nov** |
| 8 | ~~A derivatives release with §54's patch (D15)~~ **Done 11-11** (KB §69.113): `derivatives-2026-11-11`, the five patched rasters, 35.3 GB in 23 assets; hashes differ from `derivatives-2026-10-06`, `restore.py --dry-run` takes the patched copies (87.7 GB in all), `tools/check_remote.py` passes, `docs/backup.md`, `docs/rasters.md` and the README updated, `data-2026-11-10` latest again. Not done: a download and rejoin of the patched pieces | agent, desktop | KB §69.113 | done |
| 9 | **The TES figure and layout 18 into the final (D38, both, 11-11):** `final_img\tes_block_scale.png` into the paper's thermal results, layout 18 into the deck beside T3; rebuild and read both. **Done 11-11** (KB §69.107): paper 27 pages, the figure on page 10; deck 44 slides, the new one slide 13 | agent | KB §69.30 | done |
| 6 | The freeze: §12.1's lines and every result into the KB, then `final.py` and the `.tex` (the settled blocks 8–11, 14 and "Viking colour" went in early, 11-02, §69.58, and into the deck, §69.59; the deck builds and renders on the laptop; blocks 16 (a), (b), (d), 18 and 19 (d), (e), (f), (i) applied 11-07, §69.82, 21, the abstract, 11-10, §69.103, and 12, 15 and 19 (a)–(c), (g), (h) 11-10 once D33 closed, the paper at 26 pages, §69.105; 16 (c) as a note the same night; block 13 the same night without a DOI (D23, §69.105) and block 20's rep text 11-11 (§69.106); left: the open decisions' clauses; all but block 18's numbers tried on a scratch copy 11-05, every anchor found, §69.78; the deck's share, block 19, drafted and tried the same day, §69.79); rebuild, read, `verify_interim.py` on both | agent | §12.6 step 4 | by **22 Nov** |
| 10 | **The paper expanded (D42, 11-11, KB §69.109):** no length limit, possibly a published paper or report, "the longer and more in depth the better"; the agent expands whatever is useful: appendices (the full method detail, every registered prediction with its outcome, the per-class and per-block tables, the label rules), and fuller Methods, Results and Discussion with more figures. Every number from the KB, `verify_interim.py` after each pass; AASTeX kept, no journal chosen. **Done so far (11-11):** Appendix A, the third label set's rules; Appendix B, 28 registered predictions with their outcomes (E1-E5 to add when scored); Appendix C, every U-Net training by class and by block (KB §69.110); two Methods subsections, on predictions, checks and repeatability and on who judged what (KB §69.111; 31 pages). **Wording (the author, 11-11, KB §69.111):** in the paper and deck the readings the author did not make are "an automated process", never an AI or another person; one acknowledgment sentence names the AI assistant. Results gained "Where the two methods agree" with its figure and the crater size-frequency paragraph and figure (KB §69.112; 33 pages). **Next:** the retraining's result, then a fuller Discussion | agent | §12.4 | built, read page by page, before **22 Nov** |
| 11 | **The repository as a deliverable (D43, 11-11):** the professor receives the GitHub repository beside the PDF and the deck. At the freeze the README becomes a finished-work page for a reader: what was asked, what was found, where the paper, deck, maps and record are; the working plan moves off the front page. **Drafted 11-11** ("Draft now, finish at freeze", KB §69.114): findings, where to start, a state table and a section naming the working record ("Keep, link from README"); at the freeze drop the status line, add the retraining's result and read Results against the frozen paper | agent | §13.1 P12 | at the freeze, `tools/check_repo.py` passing |
| 12 | **A final data release at the freeze (D41, 11-11):** a new tagged release with the maps and models as they stand, checked against its checksums, cited by the paper's data section; no DOI; published without asking again. **Tallied ahead 11-11 (KB §69.123):** 14.41 GB in six groups, no file over one part, 75.6 GB free for staging; the five steps in order are in that section | agent, desktop | KB §57.4 | uploaded, `tools/check_remote.py` passing |

The class revision (§11) is done to the final's text (2a–2c, KB §69.2–§69.27). Deep learning (X5, X5b, X5c) is done
and scored (§66); further tuning first needs validation blocks of its own (§66.5), the author's call.

**Where the results are weakest and what would most improve them:** §14 (11-01), ranked.

**Waiting on the author:** no review (11-10: the author does no more manual review, so R1, R2, the margins and the off-Tharsis labels stay on the agent's reading, §69.55, §69.105); no decision is open since 11-11 (KB §69.107: the talk given, D15 yes, D27 yes without an ORCID, D37 yes, D38 both; D22 stays on the agent's labels); the author deletes the duplicate `F:\check_repo.py` and empties the Recycle Bins (~21 GB of finished scratch, §57.5) later; nothing after row 7 is scored: what follows either outcome is decided (D39, D40, KB §69.109). The final talk has no length limit, the paper none either; the project ends with the final (P13 dropped).

---

## 1. Where the project stands against its own goal

The prospectus promises **one internally consistent landform inventory of three families — lava flows,
fluvial channels, impact craters — from a co-registered visible + thermal-IR mosaic.**

| | type areas (Ius Chasma, Athabasca Valles) | ±60° analysis extent |
|---|---|---|
| **Co-registered mosaic** | done, 100 m (§18, §42.1) | done: one 100 m / 200 m grid, 7-band stack, layout 08 (§28, §31.2, §38) |
| **Craters** | closed depressions ≥ 1 km in both windows, 11–13 % catalogued craters (§26, §42.3) | 465,354 closed depressions ≥ 1 km: 15.3 % catalogued at ≥ 1 km, 62.2 % at ≥ 5 km (§53.4, §54.4); layout 11 |
| **Channels** | 2,610 candidates at Ius, 188 steep and rock-floored (§25); 3,283 at Athabasca | 969,822 routed segments, layout 12 (§53.6): against the mapped valleys no better than a rotated valley map (A1, layout 19, §69.50), so the DEM's drainage paths, not a channel map |
| **Lava flows** | the geologic map's `lAv` unit at Athabasca is the reference (§42) | SIM 3292 volcanic units, layout 10 (§44); the classifier cannot separate volcanic plains (§43.2–43.3) |
| **Manual digitising** | 202 channels and 381 crater rims copied from the review (3,791 of 9,287 candidates, §69.33, §69.55), 86 lava margins traced by the agent on CTX (§69.52); none drawn by hand | — |
| **Classification** | Iso Cluster and supervised on terrain labels (§19, §27) | **seven classes lead** (D28): U-Net 69.0 %, κ 0.606 and SVM 42.5 %, κ 0.310 on 237 held-out polygons (§69.24–§69.27); four classes: SVM 73.8 %, κ 0.58 (§57), U-Net 98.9 % (§66.8); nearest-training-polygon baseline 83.2 % (§69.35) |

**The central claim, measured:** the thermal bands add a small, resolved amount to the classification
(+1.3 to +2.0 pt with two classifiers, §40.1, §56), from crater and hill terrain, in overall accuracy and none by
balanced accuracy (D25, §69.18), while the seven-class U-Net, trained once without them, loses 6.4–7.6 pt, not resolved by block (§69.86); against calibrated TES thermal inertia the THEMIS mosaics keep only a weak local
signal and the Viking colour, not a calibrated albedo, carries the regional signal (§42.4, §43.1, §69.50). The hand-drawn classes are landform classes (§40.1, §56.1).

**Hypotheses** (status table in `INTERIM-PLAN.md` §5): H1 not supported at the geologic map's 1:20 M
nor on the 86 CTX-traced margins (§69.52), nor on those the agent's blind second reading kept (§69.105); H2 not supported at stages 1 and
1b, stage 2 cannot run in these type areas (§69.63); H3 not supported;
H4 answered by another method. Q1, Q2, Q4, Q5 answered; Q3 overtaken; Q6 unexamined.

---

## 2. Open decisions

D1–D13 were all answered on 2026-10-08/09 (KB §50); the published filter on 2026-10-16 (§57) and the
400 m map on 2026-10-16 (§57.2). Open, each the author's:

| # | decision | recommendation |
|---|---|---|
| D15 | a derivatives release with the §54 patch (33 GB upload) | **Answered 11-11: "Yes, upload it"** (KB §69.107), against the recommendation (not needed: the catalogue gives the two commands that patch a restore, §57.4); "Resume here" row 8; **uploaded and checked 11-11, KB §69.113** |
| D22 | the two blind checks: the rule-screened v2 rows (§12.3 R1, ~45 min) and a probability-sample accuracy check (R2, ~2–3 h) | R1 yes, after the candidate review; R2 if time is free. **Both now scored on the agent's labels at the author's word (§69.55)**; the author's answers, if given, replace them |
| D23 | a DOI for the data release through Zenodo, and a data statement (§12.4 W7); publishing | **Answered 11-10: "Release, no DOI"** (§69.105): release `data-2026-11-10`, the data paragraph cites the tag; no Zenodo. Before that: yes, with the pre-final release (§7). **Asked 11-03: "Not now"**; block 13 waits |
| D26 | **Answered 11-03 (KB §69.74):** "everything should be in the repo, there's no point in holding back on anything". `github_sync.py` now mirrors the built deck, report and paper PDF like every other file (`--hold-deliverables` leaves them out for one run); the 44 earlier copies stay in the history (no rewrite was asked for) | done |
| D27 | closing the project after 8 Dec: final tag and release, `CITATION.cff` completed, the README rewritten as finished work (§13.1 P12); an ORCID for the citation if the author has one | **Answered 11-11: "Yes, but no ORCID"** (KB §69.107) |
| D37 | retraining the lead U-Net for its volcanic edifice (§14 row 4) | **Answered 11-11: "Yes, retrain before the freeze"** (KB §69.107), against the recommendation (state it as a limit); row 7 |
| D38 | layout 18 or `final_img\tes_block_scale.png` in a deliverable (§69.30) | **Answered 11-11: "Both"** (KB §69.107), against the recommendation (neither); row 9 |
| D39 | if the edifice retraining meets its rule | **Answered 11-11: "Yes, classify and lead"** (KB §69.109) |
| D40 | if it does not | **Answered 11-11: "Reported as a test"** (KB §69.109) |
| D41 | a final data release at the freeze | **Answered 11-11: "Yes, publish at the freeze"** (KB §69.109); row 12 |
| D42 | how far to expand the paper, there being no length limit | **Answered 11-11:** every part the agent finds useful, appendices and fuller main text included (KB §69.109); row 10 |
| D43 | the README rewritten for a reader before the final, the repository being handed to the professor | **Answered 11-11: "Yes, before the final"** (KB §69.109); row 11 |
D14, D16, D23 and D24 were answered 2026-11-03 (KB §69.64–§69.65). **D14, yes:** the two `_60_smoke` classes
deleted after a checked copy to `.backups\smoke_D14_20261103-014337.gdb`. **D16:** the interim report goes in on
Thursday 5 November. **D23: not now.** **D24, yes:** the final deck is drawn in `mars_theme`, done the same day.
D21, D25, D29 and D33 were answered 2026-11-03 (KB §69.62). **D21:** the paper is retitled "A Co-registered
Visible, Thermal-Infrared and Elevation Stack of Mars at ±60°: What It Maps and What It Cannot"; the project, the
repository, the README, `CITATION.cff`, the data release and the deck keep "Mars Global Mosaic". **D25, yes:** the
abstract, Conclusion 5, Table `tab:hyp`'s T1 row and the deck (T1 slide and row, Limits, Conclusions) give the thermal
gain in overall accuracy and none by balanced accuracy; the README's T1 section already did. **D29, yes:** the
paper's seven-class SVM and U-Net paragraphs, the deck's "Seven classes lead" slide and the README's class-scheme
row say the gain is in overall accuracy and macro F1, not in balanced accuracy. **D33: the author checks the 86
traced margins first** (in Pro, before the 22 Nov freeze); then T5 is rerun and block 15 (a)'s clause drops. If the
check has not happened by the freeze, block 15 goes in with the clause as drafted, saying who traced them. **Closed 11-10** (§69.105): the author does no more manual review, so the agent read the margins again blind, T5 ran on the lines it kept, and block 15 went in naming both readings and no other check.
The same day the author asked for the off-Tharsis labels (§14 row 3: "Yes, I'll draw them"; the agent prepares the
target blocks and a guide first) and for the review items the agent can do itself to be done by it (§69.62).
D30 was answered 2026-11-01, yes: the baseline is a Table 3 row in each half and a paragraph, and the published
map's score leads with balanced accuracy in the `.tex` and `final.py` (KB §69.48).
D34 was answered 2026-11-02, "Yes, fix it for v3": the flat Tharsis fan-shaped deposits (SIM 3292 `lAa`) skip the
apron slope test, and the v2 apron proposals rejected as flat are cut and screened again on that ground; +106 apron
labels, all on `lAa`, the registered prediction held; v3 is now 11,921 labels, 10,269 / 1,652 (KB §69.56).
D36 was answered 2026-11-07: "both v3s will be what leads the final", with leave for further runs: the U-Net follows the rule, the SVM goes against it, and the paper and deck say so (KB §69.82).
D35 was answered 2026-11-02, "Yes, qualify it": the paper's Results and Conclusions and the final deck's U-Net slide now
say the balanced-accuracy lead is resolved on the v2 held-out polygons but not on the 1,652 v3 ones (A16, KB §69.57).
D31 and D32 were answered 2026-11-01, yes to both: the block intervals and the seven-class lead by balanced
accuracy, and the crater curve with each set cut only where it is scored, are in the `.tex` and `final.py` (KB
§69.47).
D19 was answered 2026-10-24, before any v2 score existed: D18's rule (a) is judged on the held-out polygons whose
v2 class is 1–4, the ground both maps can name (KB §68.4 amended, §69.4); `score_d18_verdict.py` does so.
D28 was answered 2026-10-29, after both seven-class maps had failed D18's rule (KB §69.24–69.25): **the
seven-class maps lead** all the same, as the most up-to-date and detailed maps; the four-class maps stay as
history, and D18's result stays on the record and on the sheets (KB §69.26).
D20 was answered 2026-10-26: **the interim's data cut is 26 October** (KB §69.5); the class revision, the
review and the retests go to the final, and D17 / D18's "before the interim" and "in the interim" below now read
"for the final".
D17, the class revision, was answered 2026-10-22: seven classes, before the interim, the agent proposes and the
author accepts (KB §68.1; §11 here). D18 the same day: **the interim shows both maps**, four-class and
seven-class, each scored on its own held-out polygons and both on v2's; the seven-class map is expected to
supersede the four-class one for the final, by KB §68.4's rule (v2's accuracy and κ at least the four-class
map's on the v2 held-out polygons, each new class above its base rate, the old three within 5 pt); failing it,
v2 is a reported test. The author makes time for both reviews: no cap.

---

## 3. What the agent does after each review session

1. `accept_reviewed.py` (ArcGIS Python; a dry run prints the tally and the precision so far), then
   `accept_reviewed.py --apply --by "<reviewer>"`. Reruns copy only new accepts.
2. Layout 14: `make_validation_sheet.py` (Pro closed), then `polish_layouts.py`; export and read it.
3. `make_t4_channel_h2.py`: it reports stage 2 waiting until ≥ 10 fluvial and ≥ 10 volcanic reviewed
   channels exist. **Stage 2 is not written yet:** when the counts are reached, extend the script to compare
   by `Origin` (sample the type-area index along the reviewed channels), prediction and rule written first.
4. When lava margins exist at Athabasca: give `make_flow_margin_test.py` a `--margins` source
   (`Landform_LavaFlowMargins` in place of the SIM 3292 contacts) and rerun T5 (H1). The script reads the
   Athabasca folder by its real path, not the drive-root junction, so it runs on either machine (KB §69.50).
5. `github_export_gdb.py`, then the end-of-session sequence (`HANDOFF-DESKTOP.md` §4).

---

## 4. Tests

Each writes its prediction and verdict rule into the script before it runs.

| # | question | status |
|---|---|---|
| T1 | does thermal IR improve the classification? | **done**: +1.3 pt numpy (§40.1); Pro's SVM +1.36 (200 m), +1.97 (400 m); without visible and terrain only tie (§56, §56.1) |
| T2 | is Athabasca younger than Ius's plateau? | **done** (§42.2) |
| T3 | which layer tracks calibrated thermal inertia? | **done**: Viking does, the THEMIS pair barely (§42.4, §43.1) |
| T4 | H2: do volcanic and fluvial channels separate on gradient and thermal response? | stage 1 done, not supported (§51.1); **stage 2 open**, on reviewed channels (§3 step 3) |
| T5 | H1: does IR show flow margins Viking misses? | inconclusive at 1:20 M (§47.2); the lean survives removing topography (A9, §69.50); **open**, on digitised margins (§3 step 4) |
| T6 | H3: is the composite more stable than any single input? | **done**, not supported (§47.3) |
| T7 | Q5: how many tributary orders does 100 m resolve? | **done**: no DEM-supported answer (§47.4) |
| T8 | the classes against the geologic map | **done** (§43.2), rerun on the published map (§57.1) |
| T1b | T1 on the seven v2 classes | **done** 11-01: +1.1 pt [+0.6, +1.7], balanced +0.8; Crater +4.4, fluvial +1.5, hills −3.1; no new class gains ≥ 2 pt (KB §69.50) |
| T4, stage 1b | H2 with the valley map and SIM 3292 standing in for origin | **done** 11-01, not supported: the segments on mapped valleys are 5.7 times steeper than those on volcanic units (order ≥ 2), thermal |d| ≤ 0.31 (KB §69.50); stage 2 stays the authority |
| T9 | does thermal IR help predict geologic-unit groups, material labels? | **done 11-02** (KB §69.50): does not help as registered; the stack cannot predict the unit groups above the commonest group under either prior, so they are not material labels the stack sees; thermal adds at most ~1 pt |

**Scope:** every open test is optional; if time runs short, drop tests, never the digitising checkpoint or
the cut dates.

---

## 5. Desktop jobs

| # | job | cost | notes |
|---|---|---|---|
| X5 | deep learning on the 2080 Ti (approved, q25) | hours | trained, detected and scored 2026-10-19, RetinaNet, model and detections in `DLModels\global60_retinanet_20261019\` (KB §66.1–66.2); the detections in the gdb, a map and layout 16, `make_dl_map.py` (§66.3–66.4). X5b and X5c 2026-10-20 (§66.5–66.6): `DLModels\global60_retinanet_x5b_20261020\`, `global60_unet_x5c_20261020\`; queues `build\logs\run_x5b.cmd`, `run_x5c.cmd`. Commands: `make_dl_model.py --prepare`, `--train [--tag] [--data a;b] [--epochs 30] [--freeze] [--early-stop]`, `--detect --emd <model.emd> [--threshold]`, `--score <detections> --out <json>`; `make_dl_pixels.py --export`, `--train`, `--classify --emd`, `--score <folder>`, `--score-svm`. Train on `LabeledObjects\global60_svm_stack_200m_train\` only; score on the 183 held-out polygons. Which other detection models take 7-band input is unverified **[?]** |
| X7 | optional, q12: one source mosaic as a tiled, compressed copy, timed against the original | ~1 h | only if panning stays slow after the pyramids (§53.1) |

Done on the desktop and recorded: X0 junctions, X1 GPU, X2 fine pass, X3 200 m classification, X4
pyramids, X6 q24 (§53–§55); T1 in Pro (§56).

---

## 6. Manual GUI work, the critical path

**Review, then draw only what is missing** (decision D10, KB §46):

1. Open the map "Ius Chasma — digitising" (later "Athabasca Valles — digitising"); start with the layer
   "Channels: steep and rock-floored (188)", then "Closed depressions ≥ 1 km".
2. In the layer's attribute table, set `Review` (accept / reject / unsure), and a `ReviewNote` if useful.
   Before accepting, set `Origin` (channels: fluvial / volcanic / indeterminate), `Preservation` (craters:
   fresh / degraded / ghost) and `Confidence` (certain / probable / inferred); they are copied as they stand.
3. Save edits; the agent then runs §3.
4. Draw what the machine missed straight into the digitising classes: breached craters, and **lava-flow
   margins at Athabasca** (the `lAv` unit of the geologic map shows where; these settle H1).

Rejections are data too: they become the detector's precision. Suggested minimum for the validation to mean
something: ~30 channel segments, ~50 crater rims, every defensible lava margin.

**Contingency, decided now, applied to the interim at its 26 Oct cut (D20):** if the three `Landform_*` classes
are still empty on **1 November**, the interim presents every machine product as **candidates with its measured recall**, never as a landform map, and says
so; lava flows rest on T8 and the geologic map alone. The final stands on the machine products, the 512
training polygons, the held-out scores and the tests.

---

## 7. Figures for the two deadlines (no rubric exists, D2)

| # | sheet | interim | final |
|---|---|---|---|
| 10 | locator: ±60°, both type areas, the volcanic units | ✓ | ✓ |
| 08 | the mosaic at ±60°: visible, day, night, topography | ✓ | ✓ |
| 01–02 | Ius visible; Ius night IR | ✓ | ✓ |
| — | the province test (Viking separates, THEMIS does not) and T3 against TES | ✓ | ✓ |
| 03 | Ius Iso Cluster | ✓ | maybe superseded |
| 06, 09 | Ius and Athabasca digitising candidates | ✓ | replaced by layout 14 |
| 07 | ±60° basins ≥ 20 km | ✓ | ✓ |
| 11–12 | ±60° closed depressions ≥ 1 km; ±60° channels | ✓ | ✓ |
| 04 | ±60° landforms, the published 200 m 11 × 11 map, scored | ✓ | ✓ |
| — | T1: the numpy ablation and the Pro confirmation | ✓ | ✓ |
| 13 | the classes against the geologic map (T8) | ✓ (as a chart) | ✓ |
| 05 | the 29–30 Sep GUI SVMs checked | ✓ | appendix |
| 14 | validation of the review | if reviewing has started | ✓ |

**Final report outline** (to fill after the freeze, not before): 1 question and hook (Athabasca) · 2 data and
the ±60° decision · 3 co-registration and the frames trap · 4 the thermal pair: what it can and cannot do ·
5 craters · 6 channels · 7 lava flows · 8 classification and accuracy · 9 limits · 10 what next. Each section
closes on a measured number and a sheet. **The final builders exist since 2026-10-22 (KB §69):** the AASTeX paper
`NEXT STUFF\Final\paper\mars_global_mosaic.tex` (`build_final_paper.py` copies its figures and compiles it with
MiKTeX) and the deck from `final.py` (`build_final_deck.py`), figures from `make_final_figs.py` (ArcGIS Python) and
`make_fig_final.py`. After the review and the freeze: bring the numbers in `final.py` and the `.tex` to the record,
re-export, rebuild both, read every page and slide, run `verify_interim.py final.py` and `verify_interim.py` on
the `.tex` (KB §69.3).

**Before each deadline:** a new GitHub data release (`github_release_bundle.py --upload data-YYYY-MM-DD`), then
point `github_catalog_rasters.py`'s `DATA` and `github_export_gdb.py`'s `RELEASE` at it, then run
`tools/check_remote.py` by hand (KB §57.4). Check that the releases hold every figure the documents need.

---

## 8. Schedule

| window | focus |
|---|---|
| **16–26 Oct** | Done: X5 on the desktop (KB §66); the class revision's proposals (22–23 Oct) and its rehearsal (KB §69.4). |
| **26 Oct** | **Interim data cut** (D20, KB §69.5). What is measured is in the interim; the rest goes to the final. |
| **27 Oct – 22 Nov** | For the final: review and digitising (§6), after each session §3; the label review (§11.4), then the v2 runs (~2 days, §11.5); H1 and H2 retests, layout 14 from the review. **Data freeze 22 Nov.** GitHub release refreshed. |
| **by 10 Nov** | The interim per `INTERIM-PLAN.md` §6: any last change, rebuild, read every page, `verify_interim.py`. **Interim presentation 10 Nov** (the report's date not given). |
| **23 Nov – 4 Dec** | The final report and deck, built by script from the layouts. Thanksgiving 26 Nov: nothing planned. |
| **5–8 Dec** | Buffer and rehearsal. Nothing new. |

---

## 9. Risks to plan around

- **The drive is the only full copy** of the project; GitHub holds the tree and the releases, not the gdb's
  rasters. The USB drive has dropped off mid-write twice (§36.4): big writes go to internal disk first, then one
  copy (§7 has the release step).
- **Two deadlines three weeks apart** compete for the same days: hence the hard cut on 26 Oct (D20) and documents
  built by script, not by hand.
- **The thermal argument is weaker than the prospectus says** (§28.10, §43.1): write both documents around what
  is measured; the wording traps are `INTERIM-PLAN.md` §7.
- **The review may not start in time:** the §6 contingency is the plan for that case.

---

## 10. Considered and ruled out, so they aren't proposed again

- **Segmentation at ±60°:** ~92 h at 14/14/30 (§23.6). Object-based work stays on the type areas.
- **Calibrated thermal inertia from the held mosaics:** impossible, they are stretched 8-bit DN (§24);
  calibrated inertia only from outside data (TES), and then at ~3 km.
- **Copying the project to internal disk:** ruled out by the author (§2.2).
- **The 100 m Composite Bands run** (`make_global_stack.py`): overtaken by the 200 m stack (q7).
- **CRISM, SHARAD/MARSIS, a global CTX mosaic:** out of scope (§14).
- **Correcting the delivered prospectus or Presentation 1:** they are history (§1).
- **Crater ages from the closed-depression counts:** the detector misses breached craters (§26.3); relative
  density between windows (T2) is the most it supports.
- **Rerunning the 400 m map's 180° column:** superseded by the 200 m map (§57.2).
- **The decks' and paper's images as JPEG** (was §13.1 P5): ruled out by the author, 2026-10-27; the figures stay
  PNG (KB §69.19).
- **The agent digitising for the author:** the judgement is the point of task 11. Machine output enters the
  digitising classes only through an accept in review (§25, D10).

---

## 11. The class revision (D17), for the final

The author's scheme, the audit and the plan are KB §68; this section is the work.

### 11.1 The classes

| code | class | changes from today |
|---|---|---|
| 1 | Crater | impact only: volcano summits and calderas leave it (labels 22 Arsia, 465 Ascraeus) |
| 2 | steep/windy hills | aprons leave it |
| 3 | lava tube | narrowed to volcanic pit chains, sinuous rilles and lava channels; fluvial ones leave it (six labels), flow fields go to Normal Ground or edifice |
| 4 | Normal Ground | volcanic plains are drawn as Normal Ground |
| 5 | volcanic edifice | new |
| 6 | apron | new: lobate debris aprons and the Tharsis fan-shaped deposits; the Olympus aureole with its origin open |
| 7 | fluvial channel | new, the author's "fluvial tubes"; `Subtype`: valley / inverted channel / esker / fluvial pit chain |

### 11.2 The proposals (agent, needs the drive)

`propose_label_changes.py` (written and tested on the laptop 2026-10-22, KB §68.5; ArcGIS Python, Pro
closed) writes `Landform_TrainingSamples_v2_proposals` and, with `--map`, the map "Labels v2: proposals" (one
layer per `Action`). **Before the first run on the desktop:** download the valley map to
`<drive>\Mars Project\Reference\Alemanno2017_valleys\` (Zenodo 10.5281/zenodo.1051038, CC BY-SA 4.0: the
`Giulia Valleys` `.shp`, `.shx`, `.dbf`, `.prj`; the script checks the `.shp`'s SHA-256) and add it to
`Reference\README.md`; then `--dry-run`, read the tally, then the real run with `--map`. At the session's end,
`github_sync.py` lists the two new scripts: give them a group in its `GROUPS` ("Digitising by review" fits) and
bring the README's script count to 155 (`tools/check_repo.py` fails until then). The geologic map, the crater
database and the DEM are already on the drive. The outlines of Levy et al. 2014's lobate-apron catalogue sit
behind a bot check on Wiley's site: only the author can download them (the article's "GIS data set").

1. **Every one of the 512**, with evidence: SIM 3292 unit-group shares, the largest Robbins crater inside against
   the polygon's size, relief and slope from the stack, elongation, the IAU names inside and within 100 km.
2. **Rules, each giving an `Action` and a `Reason`:** Crater with no Robbins crater near its size, or mostly on
   `ve` units → relabel 5 or check; lava tube by a named vallis off volcanic units → 7; lava tube mostly on volcanic
   plains without a catena → 4; lava tube or hills mostly on apron units → 6; nested same-class duplicates (350)
   → delete; 290/291 → clip at the block edge; label 512 → fix attributes, check its class; everything else keep.
3. **New polygons for 5–7**, inside the held-out blocks first (KB §68.3), then training: edifices and the Tharsis
   fans from the SIM 3292 units and the IAU names; valley floors for 7 from the DEM inside each named vallis's
   extent; lobate debris aprons around the Nilosyrtis, Deuteronilus and Protonilus mensae from the DEM. Any
   outside catalogue (e.g. a published lobate-apron map) only with the author's yes to download it.
4. Read back: counts per `Action` and class and split; every proposed polygon drawn on a chip and checked by eye.

**What the laptop run proposes** (KB §68.5; the desktop run will differ only if the drive's data do): 12
relabels (five Crater polygons that are volcanoes, five lava-tube polygons on valleys, two lava-tube flow fields
to Normal Ground), 23 checks, 1 clip, 1 delete, 1 fix, 574 new (276 valley strips, 172 apron and 126 edifice
pieces); ~8–12 min.

### 11.3 The minimum

Per new class, accepted: ≥ 10 held-out polygons in ≥ 2 held-out blocks, ≥ 20 training in ≥ 3 training blocks.
A class short of it stays out of v2 and is reported as such; its polygons stay in the proposals. **Hills and
lava tube fall short of the training half today** (hills in 2 training blocks; lava tube 18 training polygons
after the relabels): the author draws a few more of each in other training blocks (lava tube: Tractus,
Ceraunius and the Elysium catenae; hills: massifs outside Valles Marineris).

### 11.4 The author's review

The map "Labels v2: proposals", like §6: set `Review` on every row whose `Action` is not `keep`; edit an outline
before accepting it; set `Subtype` on class 7; draw missing polygons straight into the proposals class with
`Action` new, `ProposedClass` set and `Review` accept. **Only `accept` counts:** an accepted row enters with its
outline and `ProposedClass`; any other row of the 512 enters as it was, and any other new row is left out. To
change the class of a `keep` row, set its `ProposedClass` and accept it. The clip of label 290 must be
accepted (or the two outlines otherwise separated): `apply_label_review.py` refuses labels that share ground
across the split.

### 11.5 After the review (agent, desktop)

0. If `import arcpy` says "The Product License has not been initialized" (it did for some hours on 2026-10-23,
   then cleared by itself, KB §68.6), open Pro and sign in. Optional, the author's call: `verify_global60_classification.polys()`
   reads curved label 512 as 2 points and so leaves it out of every training-set score (KB §68.6); densifying
   curves there adds it, changing recorded training-set figures only. Held-out polygons have no curves.
1. `apply_label_review.py --dry-run`, then without it → `Landform_TrainingSamples_v2`, `_v2_60_train`,
   `_v2_60_test` (same 14 held-out blocks; centroid rule; no ground shared across classes or the split,
   checked; a new class short of §11.3 left out of the split unless `--keep-short`). The originals untouched.
2. SVM on v2: train (~1.8 h with seven classes), classify at 200 m (**~20 h** with seven classes, ~3 × the
   four-class run: measured in the rehearsal, KB §69.4), 11 × 11 filter; score v2 and the published
   map on the v2 held-out polygons; D18's verdict. T8 on v2. Every script takes `--labels v2` (`labelsets.py`,
   KB §68.6): it reads `_v2_60_train` / `_v2_60_test`, writes names with `_v2`, and never replaces a four-class
   file. In `build\`, ArcGIS Python, with `<G60>` = `F:\Mars Project\Global60`:
   ```
   python make_global60_classification.py --cell 200 --labels v2
   python make_global60_landforms_clean.py --cell 200 --size 11 --labels v2
   python verify_global60_classification.py --cell 200 --labels v2 --raster <G60>\global60_landforms_svm_v2_200m_mode11.tif
   python verify_global60_classification.py --cell 200 --labels v2 --raster <G60>\global60_landforms_svm_200m_mode11.tif
   python score_d18_verdict.py
   python make_geomap_check.py --labels v2
   ```
   The first refuses to start unless both v2 halves exist and every row is `apply_label_review.py`'s with a
   code 1–7; it skips the four-class split. The fourth scores the published map on the v2 polygons; the fifth
   prints (a)–(c) and the verdict into `logs\d18_verdict.json`.
3. U-Net on v2: export the v2 training split, train (**~7.8 h** in the rehearsal: 21,711 chips, 6.4 × the
   four-class time), two passes over ±60° (**~12.6 h**, run in chunks of ≤ 60 tiles: one process leaks ~0.28 GB a
   tile, KB §69.4); scored the same way. `run_rehearsal_v2p.ps1` is the queue to copy for v2.
   Dropped first if the dates slip.
   ```
   python make_dl_pixels.py --export --labels v2
   python make_dl_pixels.py --train --labels v2
   python make_dl_pixels.py --classify-global --labels v2 --emd <the new model's .emd>
   python make_dl_pixels.py --classify-global --labels v2 --pass B --emd <the same .emd>
   python make_dl_pixels.py --mosaic --two-pass --labels v2
   python verify_global60_classification.py --cell 200 --labels v2 --raster <G60>\global60_landforms_unet_v2_200m_seamfix.tif
   python verify_global60_classification.py --cell 200 --labels v2 --raster <G60>\global60_landforms_unet_200m_seamfix.tif
   ```
   Work goes to `C:\MarsScratch\x5c_v2`; `--train` refuses an export made from the four-class labels.
   `make_unet_map.py` (the per-polygon table and layout 17's layers) is still four-class: step 4's work.
4. **Done 2026-10-29 (KB §69.26):** `make_v2_sheets.py` → 04b, 13b, 17b. Layouts: a new sheet for the seven-class SVM map beside 04 (the four-class map, kept), 13 on both, 17 for
   the U-Net on v2; legends name seven classes. The X5 detector and layout 16 stay four-class, as history.
   `polish_layouts.py`, export, read.
5. **Text done 2026-10-29 (KB §69.27):** paper and deck rewritten, the seven-class maps leading. The final rebuilt **with both maps**, the seven-class maps leading (D28; D18, moved from the interim by D20): the four-class map and its scores,
   the seven-class map and its scores, and both scored on the v2 held-out polygons; the class wording in
   `final.py` and the paper updated; `verify_interim.py final.py` and on the `.tex`.

### 11.6 Dates, and what gives first

| by | what |
|---|---|
| 23 Oct | proposals built on the drive and read (the script is tested, KB §68.5): **done** (KB §69.2) |
| 26 Oct | the interim's data cut (D20, KB §69.5): the interim shows the four-class maps and describes the seven-class scheme as proposed, with §68's audit as its evidence |
| ~18 Nov | the author's label review done |
| review + ~1 day | v2 SVM map scored; D18 verdict (~22 h after the review, KB §69.4) |
| review + ~2 days | v2 U-Net scored (~21 h after its export) |
| 22 Nov | data freeze: layouts and the final rebuilt with both maps |

**What gives first** if the label review runs late: the U-Net rerun, then the SVM rerun; the final then shows the
four-class maps and reports the seven-class scheme as a proposal. The author makes time for both reviews
(no cap, D18).

---

## 12. Strengthening the final paper (brainstormed 2026-10-27, laptop, while `run_v2.ps1` runs)

Read against the paper as built (`NEXT STUFF\Final\paper\mars_global_mosaic.tex`, KB §69) and this plan; nothing
was measured (KB §69.17). Each item says what it adds, where it runs and what it waits on. **Priority:** A, before
the 22 Nov freeze if at all possible; B, if time allows; C, only if cheap. Every new test writes its prediction and
verdict rule into its script before it runs (§4). Drive items wait for "queue done" in
`build\logs\run_v2\queue.log` and for the v2 scoring (§11.5), which comes first. Nothing here goes ahead of the
author's review (§6). A14 and W10 (done 10-31, KB §69.37–§69.38), A15 (done 11-01, §69.39), W11, the additions to A3 (c), A5 and
W6, and P13 (§13) come from an outside brainstorm audited on 2026-10-31 against the record (KB §69.36); the rest of that
brainstorm was dropped. Done 11-01 on the laptop and removed from the table (KB §69.50): A1 (the routed channels find the mapped valleys no better than a rotated valley map), A2 (T1b, thermal +1.1 pt on seven classes), A8 (T9, 11-02: the stack predicts SIM 3292's unit groups no better than the commonest group, with or without thermal), A3 (b) (11-02: elevation and latitude alone score 62.5 % on four classes and 31.8 % on seven, 3.9 and 2.3 points over one class everywhere: the SVM is not mostly elevation) and (c), A7 (T4 stage 1b, H2 not supported), A9 (the lean survives topography) and A13 (under 10 % of rows change).

### 12.1 Lines in the paper and `final.py` that the freeze must change

The abstract, the limits on the labels and the candidates, the channel reference and the two citations were brought
current on 2026-10-27 (KB §69.18). **Applied early, 2026-11-02 (KB §69.58):** the blocks no answer can change,
`v2_drafts.tex` 8 (W11), 9 (W3), 10 (A1, A7), 11 (A3 (b), A8) and 14 (W4's three figures), and "Viking colour" (W5)
in the paper and the final deck. Left for the freeze, each drafted in `NEXT STUFF\Final\paper\v2_drafts.tex`:

| where | today | true since |
|---|---|---|
| before the acknowledgments | — | W7, block 13, and W6, block 12: applied 11-10 (§69.105; no DOI, D23) |
| the PDF and the final deck | the paper compiled by CI on every push (27 pages since 11-11, §69.107), its committed PDF and the deck rebuilt 11-11 with the TES figure and layout 18 (D38, §69.107; 44 slides) | after the freeze's edits: `build_final_paper.py` with MiKTeX on the desktop, since CI's PDF is only a run artifact and the committed one is the drive's; `build_final_deck.py` on either machine; read every page; note the page count (the trial of §69.78, every block in and the `\VV` numbers at placeholder width, came to 22; the 11-10 trial of blocks 12, 13 and 15, 26, §69.103) |

### 12.2 Analyses that need no author time

| # | what | adds | where | pri |
|---|---|---|---|---|

### 12.3 Small asks of the author (each after the candidate review, never ahead of it)

| # | what | adds | cost | pri |
|---|---|---|---|---|
| R1 | **A blind spot-check of the rule-screened rows**: 30 accepted and 10 rejected of each of fluvial and apron, shown without the rule's verdict; agreement gives the rule a measured precision; **registered, drawn and rendered 11-02 (KB §69.54)**: 80 rows on 14 sheets in `Mars Project\review_sheets\r1\` (no Pro), `score_r1.py answers.txt`; **answered by the agent at the author's word (§69.55)**: fluvial 27 of 27 rule accepts kept (κ 0.45), apron 20 of 26 (77 %, κ 0.02), and 5 of the apron rejects it kept are flat Tharsis fan-shaped deposits the slope test drops (D34) | the paper can say how good the screen is, not only that it is one | ~45 min on the sheets | A |
| R2 | **A probability-sample accuracy check** (Olofsson et al. 2014): stratified random points on the published map (and the U-Net and v2 maps), 25–50 per mapped class, labelled blind from the imagery with the maps hidden; **points, sheets and scorer done 11-02 (KB §69.53)**: 210 points in `Mars Project\review_sheets\r2\` (35 hidden calibration points), `score_r2.py answers.txt --author`; the agent's own labelling failed its gate (66.7 %, κ 0.60); **scored all the same at the author's word (§69.55, `--waive-gate`)**: four-class SVM 56.9 % (48.8–65.0), seven-class SVM 39.9 %, U-Nets 44.4 % and 21.7 %; Normal Ground 79.8 % of the ground against 33.3 % mapped; an upper bound on the gap, the labeller leaning to Normal Ground | unbiased map accuracy and area-adjusted class areas with intervals; hand-drawn polygons sit where a class is clear, so the polygon score flatters every map | ~2–3 h for ~200 points | A if any time is free |
| R3 | Lava margins at Athabasca, for H1 (already §6 step 4) | H1 tested at the stack's own scale | | |
| R4 | A few hills polygons in a third training block (§11.3) | only if v2 is rerun; otherwise the limit is stated | ~20 min | C |

### 12.4 The paper's text and figures

- **W2, the title** (D21, **answered 11-03**: retitled, KB §69.62): it promised "Mapping Lava Flows" though the lava flows come from the geologic map; a
  title that names the stack and what it can and cannot map would match the results.
- **W3, prior work**: the introduction cites the data but no earlier automated mapping, and the discussion compares
  with none. The six candidates are checked by DOI and in `references.bib` (DeLatte2019, Silburt2019, Bue2006,
  Luo2009, Wilhelm2020, Olofsson2014; KB §69.40), and cited since 11-01 by a prior-work paragraph in the
  introduction and a Limits sentence on polygon bias. The Discussion's comparison with prior work is drafted (11-01,
  `v2_drafts.tex` block 9, KB §69.50): a subsection "Against earlier automated mapping", in the paper since 11-02 (KB §69.58).
- **W4, figures** (17 pages when these went in, 11-01; **21** since the citations of 11-03, KB §69.67, §69.69):
  ~~the pipeline in Methods~~ (in since 10-31, `fig:pipeline`, KB §69.38; page 5, read); ~~the block split~~ (in since
  11-01, `fig:split`, `final_img\block_split.png`, KB §69.41; page 6, read); ~~a type-area zoom of the published map against the imagery at full resolution; Perrotin found and Oudemans breached, the detector's limit in one panel~~ (made 11-02, `final_img\typearea_zoom.png` and `crater_limit.png`, with A3's `svm_baselines.png`, in the paper since 11-02, KB §69.58); after v2, the seven-class map and its confusion; A6's `final_img\map_agreement.png` (KB §69.46) and A10's `final_img\crater_sfd.png` (KB §69.35).
- **W5, limits to add**: one labeller; the rule-screened v2 rows; hills short; THEMIS strips differ in local time,
  season and dust, a physical cause beside the stretch (Edwards et al. 2011's abstract confirms running contrast
  stretches; the rest needs its full text **[?]**); **Viking, checked 11-01 (KB §69.50):** MDIM 2.1 is high-pass
  filtered at ~50 km to remove regional albedo and normalised so equal slopes show equal contrast, and its colour
  is an older mosaic blended over it "artistically", which most likely carries §43.1's regional signal: the
  Viking bands are shading, local albedo and an uncalibrated regional colour. Say so in Data and Limits, beside
  the stack's "no elevation band"; and (done 11-02, KB §69.58) read "Viking albedo" as "Viking colour" in the
  paper, Conclusion 2 among them.
- **W6, future work**: the outline's item 10 (§7) has no section in the paper: calibrated THEMIS inertia where it
  exists, CTX for margins, validation blocks for the deep-learning models, R2 if not done. Once the models have
  validation blocks, the seven-class U-Net's over-predicted edifice (§69.25; by A14 mostly on the highland group,
  §69.37) is the first target of any retraining. **Drafted 11-02** (`v2_drafts.tex` block 12, KB §69.50): a
  "Future work" subsection after Limits, adding material labels by photo interpretation (T9) and the crater
  detector's rim-based diameter (§14 row 7); `Malin2007` (CTX) added to `references.bib`, its DOI checked.
- **W7, data availability** (D23): a DOI for the data release through Zenodo's GitHub link, cited as
  `Edwards2026data`, and a data statement as AAS asks. Publishing: the author's yes (D23: with the pre-final
  release). **The statement is drafted 11-02** (`v2_drafts.tex` block 13, KB §69.50); at the release, add the DOI
  and version to `Edwards2026data`.
- **W9, the thermal claim** (D25, **answered 11-03, yes**: qualified everywhere, KB §69.62): by balanced accuracy the thermal gain vanishes (−0.3 and +0.1 points, KB
  §69.18); the paper says so in Results, but the abstract and conclusions still give "a resolved 1.4 to 2.0
  points" alone. Since D25 they carry the qualifier.
- **W11, the values Methods leaves out**: the detector's, the router's and the SVM's thresholds are already in the
  prose (read 10-31), so a parameter table would repeat them on a tight page budget. Missing: the review rule's
  thresholds (fluvial, floor ≥ 20 m below a 4.8 km flank ring and `ShareVolc` < 0.5; apron, `SlopeMed` ≥ 1° and
  `CraterCover` < 0.5; KB §69.8), which §12.1's line and A13 need stated; the U-Net's batch of 8, 10 % of chips for
  validation, backbone unfrozen, 64-pixel padding at inference (`make_dl_pixels.py`). One sentence each, every
  value read from its script at the freeze. **B**, with §12.1. Drafted 11-01 (`v2_drafts.tex` block 8, KB §69.50); in the paper since 11-02 (§69.58).

### 12.5 The two talks

- **The interim, 10 Nov:** ~~speaker notes on every slide~~ (done 11-01, `interim.NOTES`, KB §69.41: 2,348 words,
  about 17 min read aloud; they answer the four likely questions below in the notes of the slides that raise them);
  one timed run-through (the slot's length from the author; trim the notes to it); backup slides for the likely
  questions only if the author wants them on screen: why no calibrated thermal inertia, why the U-Net's 98.9 % is
  not the headline, what a held-out block is, what has changed since the cut (the v2 labels). Before the talk, bring
  the "Next Steps" note's review tally to the day's.
- **The final deck** (D24, yes 11-03; **done 11-03**, KB §69.65): rebuilt in the interim's dark `mars_theme` so the two talks look alike; `final.py`
  keeps the words.

### 12.6 Order of work

1. **Laptop, now:** nothing left from this list (W4's block split and §12.5's speaker notes done 11-01, KB §69.41; W3
   done 11-01, KB §69.40; A4, A12, W1 and the paper's half of W8 done 10-27, KB §69.18; the
   deck's half of W8 with the D28 rewrite 10-29, §69.27; A14 and W10 done 10-31, §69.37–§69.38; A15 done 11-01,
   §69.39).
2. **Desktop:** the v2 scoring and D18 done (§11.5; A4b done 10-31, KB §69.34); A1, A2, A3 (b) and (c), A7, A8, A9 and
   A13 done 11-01/02 on the laptop (KB §69.50), A5, A6 and A11 11-01 (§69.44–§69.46): nothing in §12.2 is left.
3. **The author:** the candidate review (§6) first; then R1; R2 if any time is free.
4. **By 22 Nov:** the freeze; §12.1's lines and every result above that ran, into the KB, then `final.py` and the
   `.tex`; rebuild and read; `verify_interim.py` on both.

---

## 13. The repository and the project, beyond the paper (brainstormed 2026-10-27, laptop)

Read against the repository as it stands at `d3f79a5`; what was measured is KB §69.19. Same priorities as §12 (A,
before the freeze if at all possible; B, if time allows; C, only if cheap). None of it goes ahead of the author's
review (§6) or the v2 scoring (§11.5); most of it is laptop work that fills the wait for `run_v2.ps1`.

### 13.1 The work

| # | what | adds | where | pri |
|---|---|---|---|---|
| P11 | ~~**Which runs repeat exactly**~~ **done 11-02** (KB §2.6, §69.50): every random draw in the scripts is seeded; none of Pro's training tools takes a seed, but Pro's SVM repeats byte for byte (two trainings on one block, 0 pixels differ) while Random Trees differs on 5.0 % of pixels; the U-Nets were not tested and are re-made from their saved models | the paper's methods can say what is deterministic | done | C |
| P12 | **Closing the project, after 8 Dec** (D27): a tag `final-2026-12-08` and a final release (the deck, the paper's PDF, the maps); `CITATION.cff` given `version`, the DOI (D23), a `preferred-citation` for the paper and its date; the README's "Where it stands" turned into what was found; this plan closed with a header saying so; the memory and "Resume here" retired; D14's smoke classes settled | the repository reads as finished work, not a project paused mid-term | laptop, ~1 h, 9–12 Dec | after |
| P13 | **Dropped 11-11: the project ends with the final (KB §69.109).** ~~The maps viewable without ArcGIS, after 8 Dec and only if the project continues~~: the two seven-class maps as cloud-optimised GeoTIFFs (`gdal_translate -of COG` under the ArcGIS Python, which has GDAL) in a release, and a simple web map of them on the project page | a reader can pan the maps in a browser instead of downloading 106,694 × 35,565-pixel rasters | laptop, ~2 h | after |

**The thermal wording beyond the paper** (D25, widened): the README's T1 section is qualified (§69.62); the interim
talk gives the overall-accuracy gain alone. The interim's content is cut at 26 October (D20), but this result is a
reanalysis of logs that existed at the cut; one backup slide for "does thermal really help?" would answer the
question without changing the cut, if the author wants it on screen (§12.5).

### 13.2 Order of work

1. **Laptop:** nothing left. P1–P3 done 10-27 (KB §69.20), P2's first real use 10-28 (§69.23); P9 and P10 done
   10-31 (§69.34); P4 and P6 done 11-01 (§69.42).
2. **Desktop:** nothing left. P7 and P8 done 11-05 (KB §69.75).
3. **After 8 Dec:** P12 (its README part at the freeze, D43); P13 dropped (KB §69.109).

---

## 14. Where the results are weakest, and what would most improve them (2026-11-01, laptop)

Read against the record after A5, A6 and A11 (KB §69.44–§69.46); ranked by how much each limits what the final can
claim. "Cost" is who and how long; nothing here goes ahead of the review (§6) or the freeze (22 Nov).

| # | weakness | evidence | what would improve it | cost |
|---|---|---|---|---|
| 1 | **The held-out score rests on a few large polygons in a few blocks.** Three blocks hold 61.6 % of the four-class held-out area; one Normal Ground polygon is 73.7 % of its class's, Arsia Mons 30.7 % of Crater's; dropping one block moves the published map by 8.7 pt | §69.44 | **R2, the probability-sample check** (§12.3): stratified random points labelled blind give unbiased accuracy and class areas with intervals, independent of where polygons were drawn. The single most valuable hour of the author's after the review | done on the agent's labels, gate waived (§69.55: every map well below its polygon score); the author's ~2–3 h on the `r2` sheets would replace them |
| 2 | **The SVM maps do not beat geography.** The nearest training polygon scores 83.2 % against the published map's 73.8 % (four classes) and 45.6 % against 42.5 % (seven); by block neither gap is resolved either way | §69.35, §69.44 | A3 (c), done 11-01 (KB §69.50): a 51 km mode filter lifts the four-class SVM from 69.9 % to 82.1 %, still below the baseline, and leaves the seven-class SVM flat (at most 43.9 %); context alone closes neither gap. A3 (b), done 11-02 (KB §69.50): elevation and latitude alone score 62.5 % and 31.8 %, below the raw SVM by 7.4 and 10.6 points (24.2 and 14.5 by balanced accuracy): what beats the SVM is position, not height. The U-Net, which uses context, already clears the baseline. In the paper since 11-01 (D30, KB §69.48): the baseline beside every score, the SVM map led by balanced accuracy, where it is ahead | done |
| 3 | **The seven-class lead is two blocks wide.** By accuracy, the seven-class U-Net's lead over the seven-class SVM is not resolved by block (−9.7 to +47.8 pt); it sits on the Tharsis blocks −9_−1 and −9_0; the SVM leads in 8 of 14 blocks | §69.44; A16 (11-02, §69.57): on the 1,652 v3 held-out polygons the balanced lead (+12.5 pt) is not resolved by block either (−3.7 to +16.3); the paper and deck qualified 11-02 (D35) | Done 11-01 (D31, KB §69.47): the paper leads with balanced accuracy, which is resolved (+2.3 to +19.5). For a firmer test, edifice and apron labels in held-out blocks outside Tharsis (Elysium, Syrtis, Hesperia); the v3 held-out set cannot stand in, holding off Tharsis 6 edifice polygons in one block and 16 apron in another (§69.61). **The author draws them (yes, 11-03)**: map "Off-Tharsis labels (author)", guide `Mars Project\review_sheets\offtharsis\README.md`; the targets are Syrtis Major's paterae (block 4_0) and the Nilosyrtis Mensae / Colles Nili aprons (4_2): one held-out block per class, so a polygon-level score, no block interval (§69.63). **Done by the agent 11-10** (§69.105): six edifice polygons at Nili and Meroe Paterae; the U-Net v3 calls 7.7 % of them edifice (1.4–20.5), the SVM v3 0.6 %: off Tharsis the lead is small and the class weak; no apron could be drawn | done |
| 4 | **The seven-class U-Net's edifice is wrong over much of the planet**: 40.0 % of ±60°, 46.8 % of the highland group, none of the 10 named small edifices | §69.25, §69.37, §69.39 | Retrain with validation blocks of its own (§66.5), edifice negatives drawn on the highland group and class weights; score on the same held-out blocks. Not a post-hoc mask by the geologic map: T8 scores against that map | desktop, hours, as X5c (§66.6); the author's call (§66.5) |
| 5 | **The routed channels are not a channel map.** Against the valley map (A1), order ≥ 3 precision 2.8 % and recall 2.0 % at 5 km, no better than the valley map rotated in longitude (median 3.3 %); 46 % of the order ≥ 3 length lies at 0–30° N, where 0.1 % meets a valley | §53.6, §69.50 | Call the network the DEM's drainage paths in the final, not channels; a channel claim rests on the reviewed candidates (§6), or on the order ≥ 5 trunks and the southern highlands, where precision reaches 10–18 % | the score done 11-01; the wording at the freeze |
| 6 | **Two hypotheses wait on the review**: H2 stage 2 needs `Origin` on ≥ 10 fluvial and ≥ 10 volcanic of the 199 copied channels; H1 now runs on 86 agent-traced CTX margins (§69.52: not supported, +4.9 pt [−2.7, +13.1]), the author has not checked them | §69.33 | `Origin` on the 199 channels: the agent's is in (§69.55), 29 fluvial and 0 volcanic. All 29 fluvial are at Ius, so volcanic channels drawn at Athabasca would give only the pooled, window-confounded comparison that repeats stage 1, and stage 2's thermal term needs a source candidate a drawn line lacks (§69.63): the agent did not draw them, and the author said skip them (11-03); H2 stays at stages 1 and 1b. The margins: the author checks them (D33, 11-03) | done: the agent's blind second reading, T5 on the lines kept, not supported (§69.105) |
| 7 | **Crater recall stops near one half**, mostly from degraded and partial rims (77 % of the misses are rim states 1–2) and, at 5–10 km, from C5's two-sided cut | §69.45 | The figure and sentence: done 11-01 (D32, KB §69.47). To recover recall: 23 % of the misses (72 % at ≥ 50 km) hold only a smaller closed basin, which a rim-based diameter or merging nested basins would match; that is a change to the detector and an 11 h fine pass, so future work (W6), not before the freeze | detector: after 8 Dec |
| 8 | **The thermal gain is small** (+1.36 pt, resolved by block; none by balanced accuracy) | §56, §69.18, §69.44 | Nothing to fix: A2 (done 11-01, KB §69.50) found +1.1 pt on seven classes, not concentrated in the new classes; A8 (done 11-02, KB §69.50): SIM 3292's unit groups are not predictable from the stack above the commonest group, with or without thermal, so the mapped units are not the material labels a thermal test needs; that test waits on photo-interpreted labels (W6) | done |

**Order for the agent:** D31 and D32 done 11-01 (KB §69.47), and §12.6 step 2's list (A1–A3, A7–A9, A13; KB
§69.50); the v3 maps were picked 11-07 (D36, KB §69.82); rep was scored 11-11 (§69.106); what is left is the freeze. **For the author:** nothing required since §69.55; volcanic channels drawn by hand would unblock H2 stage 2, and any answer on the sheets replaces the agent's.
