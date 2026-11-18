# build

Every script the project was run from: 274 of them (`.py`, and `.ps1` for the run queues and the
Office renderers). Nothing in the project was made by hand that a script here can make: the
rasters, the map layouts, the charts, the audits, the paper and the decks.

**The index is [`docs/scripts.md`](../../docs/scripts.md):** every script, grouped by what it makes,
with the Python it needs and the first line of its own docstring. Each script's docstring says how
to run it and which knowledge-base sections it serves.

Two interpreters are used:

- **ArcGIS** — ArcGIS Pro's `arcgispro-py3` environment, for anything that uses `arcpy`, GDAL or
  the deep-learning tools.
- **System** — a plain Python 3 with the packages in
  [`docs/requirements-system.txt`](../../docs/requirements-system.txt), for the charts, the
  deliverables and the repository tools.

[`docs/environment.md`](../../docs/environment.md) has each machine's versions.

| Folder | What it holds |
|---|---|
| [`logs/`](logs) | every run's log and the scores as JSON; the charts and the paper's numbers are read from them |
| `final_img/`, `interim_img/`, `pres1_img/` | the figures of the final, the interim and Presentation 1, each listed in [`docs/figures.md`](../../docs/figures.md) with the script that draws it |

The grid every ±60° product shares is defined once, in [`grid60.py`](grid60.py).
