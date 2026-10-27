# -*- coding: utf-8 -*-
r"""The apron and fluvial proposals reviewed by a written rule, at the author's request (KB §69.8).

The author reviewed the other proposals in Pro and left the new apron (6) and fluvial channel (7)
polygons to the agent ("the classification of aprons and fluvial channels i will leave to you to
accept", 2026-10-27). This sets Review and ReviewNote on those rows by the rule below, fixed before
it was run; it never touches a row that already holds a Review, any other class, or any outline.

  fluvial channel (new, class 7)  accept if the strip sits on a floor: the median DEM height of its
                                  cells is at least FLOOR_M below the median of a flank ring 0-FLANK_KM
                                  outside it; and it is not mostly on volcanic plains (ShareVolc <
                                  VOLC_MAX), where a channel's origin, water or lava, is open (H2).
                                  Otherwise reject.
  apron (new, class 6)            accept if the piece is not flat (SlopeMed >= APRON_SLOPE, from the
                                  proposals' own evidence) and not mostly inside crater rims
                                  (CraterCover < APRON_CRATER). Otherwise reject.

These are screens, not the author's eye: an accepted piece keeps its proposed outline (a 3° piece of a
SIM 3292 unit, or a 2.4 km strip), untrimmed. Pro closed.

  python review_v2_by_rule.py --dry-run     the verdicts and the tally; nothing written
  python review_v2_by_rule.py               also write Review / ReviewNote (the class is copied to
                                            <drive>\Mars Project\.backups first)
Writes logs\label_review_by_rule.json (per row: the measures and the verdict).
"""
import os, sys, json, time, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
import numpy as np
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, GDB
import propose_label_changes as plc            # Dem: the cells of a polygon, as the evidence was read

DRY = "--dry-run" in sys.argv
PROPOSALS = os.path.join(GDB, "Landform_TrainingSamples_v2_proposals")
LOG = os.path.join(HERE, "logs", "label_review_by_rule.json")
STAMP = "agent rule §69.8"                       # the full rule and measures are in the log

FLOOR_M, FLANK_KM, VOLC_MAX = 20.0, 4.8, 0.5
APRON_SLOPE, APRON_CRATER = 1.0, 0.5


def floor_depth(dem, sr, strip):
    """Median height of the flank ring minus that of the strip (m); None if either has no cells."""
    # a geodesic buffer, so the ring is FLANK_KM wide on the ground at any latitude
    outer = arcpy.analysis.Buffer(strip, arcpy.Geometry(), "%s Kilometers" % FLANK_KM, method="GEODESIC")[0]
    inner = strip.projectAs(sr)
    ring = outer.projectAs(sr).difference(inner)
    a, b = dem.cells(inner), dem.cells(ring)
    if a is None or b is None:
        return None
    return float(np.median(b["z"]) - np.median(a["z"]))


def main():
    t0 = time.time()
    dem = plc.Dem(plc.DEM)
    sr = arcpy.Describe(plc.DEM).spatialReference
    F = ["OID@", "Action", "ProposedClass", "Review", "ShareVolc", "SlopeMed", "CraterCover", "Split", "Block",
         "SHAPE@"]
    rows = []
    with arcpy.da.SearchCursor(PROPOSALS, F) as cur:
        for oid, act, pc, rev, volc, slope, cc, split, blk, g in cur:
            if act != "new" or pc not in (6, 7) or rev:
                continue
            r = dict(oid=oid, cls=pc, split=split, block=blk, volc=volc, slope=slope, crater=cc)
            if pc == 7:
                d = floor_depth(dem, sr, g)
                r["floor_m"] = None if d is None else round(d, 1)
                why = []
                if d is None or d < FLOOR_M:
                    why.append("no floor (%s m)" % ("no cells" if d is None else "%.0f" % d))
                if (volc or 0) >= VOLC_MAX:
                    why.append("volcanic plains %.2f" % volc)
                good = "floor %.0f m below flank" % d if not why else ""
            else:
                why = []
                if slope is None or slope < APRON_SLOPE:
                    why.append("flat (%s°)" % ("?" if slope is None else "%.1f" % slope))
                if (cc or 0) >= APRON_CRATER:
                    why.append("in craters %.2f" % cc)
                good = "slope %.1f°, craters %.2f" % (slope, cc) if not why else ""
            r["review"] = "reject" if why else "accept"
            r["note"] = "%s: %s" % (STAMP, good or "; ".join(why))
            assert len(r["note"]) <= 60, r["note"]           # ReviewNote is 60 characters
            rows.append(r)
            if len(rows) % 50 == 0:
                print("  %d rows, %.0f s" % (len(rows), time.time() - t0))

    tally = collections.Counter((r["cls"], r["split"], r["review"]) for r in rows)
    blocks = collections.defaultdict(set)
    for r in rows:
        if r["review"] == "accept":
            blocks[(r["cls"], r["split"])].add(r["block"])
    for k in sorted(tally):
        print(k, tally[k])
    for k in sorted(blocks):
        print("accepted", k, "in", len(blocks[k]), "blocks")

    if not DRY:
        bak_dir = on_drive(r"Mars Project\.backups")
        bak = os.path.join(bak_dir, "proposals_%s.gdb" % time.strftime("%Y%m%d-%H%M%S"))
        arcpy.management.CreateFileGDB(bak_dir, os.path.basename(bak))
        arcpy.conversion.FeatureClassToFeatureClass(PROPOSALS, bak, "Landform_TrainingSamples_v2_proposals")
        print("backed up to", bak)
        verdict = {r["oid"]: r for r in rows}
        with arcpy.da.UpdateCursor(PROPOSALS, ["OID@", "Review", "ReviewNote"]) as cur:
            for oid, rev, note in cur:
                if oid in verdict and not rev:
                    cur.updateRow([oid, verdict[oid]["review"], verdict[oid]["note"]])

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    json.dump(dict(dry_run=DRY, rule=dict(FLOOR_M=FLOOR_M, FLANK_KM=FLANK_KM, VOLC_MAX=VOLC_MAX,
                                          APRON_SLOPE=APRON_SLOPE, APRON_CRATER=APRON_CRATER),
                   tally={"%s/%s/%s" % k: v for k, v in sorted(tally.items())},
                   accepted_blocks={"%s/%s" % k: sorted(v) for k, v in sorted(blocks.items())},
                   rows=rows, seconds=round(time.time() - t0)),
              open(LOG if not DRY else LOG.replace(".json", "_dryrun.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("done, %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
