# Mars Global Mosaic drive

This drive is the working copy of the OCN 4704 Mars Global Mosaic project (ArcGIS Pro). It is `Z:` on
the laptop and `F:` on the desktop; every build script finds its own drive (`build\paths.py`).

**Start here, in this order:**
1. `Mars Remote Sensing Project\HANDOFF-DESKTOP.md`: the first ten minutes on a machine, where
   everything is, the working rules, and every open task with its command (written 2026-10-09).
2. `Mars Remote Sensing Project\NEXT-STEPS.md`, section "Resume here": the state at the last stop.
3. `Mars Remote Sensing Project\PROJECT-KNOWLEDGE.md`: the record and the authority on what is true.

**Never, without explicit approval:** delete anything on this drive; write into the three `Landform_*`
digitising classes except through `accept_reviewed.py`; start a global segmentation or another
multi-hour job not listed in the handoff; install software. Writes to the `.aprx` or the gdb need
ArcGIS Pro closed. Big outputs are built on internal disk first, then copied here once.
