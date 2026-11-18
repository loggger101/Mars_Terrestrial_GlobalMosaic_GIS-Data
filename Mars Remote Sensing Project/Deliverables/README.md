# Deliverables

What was handed in for OCN 4704 Remote Sensing, Fall 2026, newest first. The prospectus and
Presentation 1 are in [`../Earlier deliverables/`](../Earlier%20deliverables).

| Deliverable | File | Date |
|---|---|---|
| Final paper (AASTeX, 51 pages, 47 figures) | [`Final/paper/mars_global_mosaic.pdf`](Final/paper/mars_global_mosaic.pdf); its source `mars_global_mosaic.tex`, `references.bib` and `figures/` beside it | final, 8 Dec 2026 |
| Final presentation (53 slides) | [`Final/Mars Global Mosaic - Final Presentation.pptx`](Final/Mars%20Global%20Mosaic%20-%20Final%20Presentation.pptx) | final, 8 Dec 2026 |
| Interim report | [`Mars Mosaic - Interim Report.pdf`](Mars%20Mosaic%20-%20Interim%20Report.pdf) and [`.docx`](Mars%20Mosaic%20-%20Interim%20Report.docx) | submitted 5 Nov 2026 |
| Interim presentation | [`Mars Global Mosaic - Interim Presentation.pptx`](Mars%20Global%20Mosaic%20-%20Interim%20Presentation.pptx) | presented 10 Nov 2026 |

`2 Interim Presentation Template.pptx` is the course's template the interim deck follows.
`Final/paper/v2_drafts.tex` holds paragraphs drafted for the paper and kept for the record; it is
not part of the paper.

Each file is built by a script in [`../build/`](../build), never edited by hand: the paper by
`build_final_paper.py`, the final deck by `build_final_deck.py` from `final.py`, the interim
deck and report by `build_interim_live.py` and `build_interim_report_live.py` from `interim.py`.
Every number in them is checked against the knowledge base by `verify_interim.py`.
