# -*- coding: utf-8 -*-
r"""Copy reviewed candidates marked "accept" into the digitising classes (NEXT-STEPS D10; KB §46).

    python accept_reviewed.py                          # dry run: the review tally, what would be copied
    python accept_reviewed.py --apply --by "<name>"    # copy; MappedBy = <name>, the reviewer

  Landform_ChannelCandidates_auto[_ath]  ->  Landform_ChannelCenterlines
  Landform_CraterCandidates_auto[_ath]   ->  Landform_CraterRims

Run with the ArcGIS Pro Python, after add_review_fields.py. In Pro, save edits first.

Rules:
- Only Review = accept is copied. reject / unsure / empty are never copied; the tally reports them
  (rejections give the detector its precision, accept / (accept + reject)).
- The geometry is copied unchanged. UnitName, Confidence, Origin, Preservation are copied as they
  stand on the candidate row, so set them there before accepting (a candidate carries
  Confidence = inferred, Origin = indeterminate). Notes = ReviewNote, then the machine note.
  Evidence = the candidate's evidence + "; accepted in review". GradientPct stays empty: the
  candidates' SlopeDeg is terrain slope along the line, not the channel's gradient (KB §25).
- SourceID = "<candidate class>:<OBJECTID>". A candidate already copied is skipped, so a rerun
  copies only new accepts.
- Nothing is deleted. A copied row whose candidate is no longer "accept" is listed for manual
  removal in Pro.
- Every value is checked against its target field's length before anything is written.
"""
import os, sys, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import GDB

ACCEPT_NOTE = "; accepted in review"
JOBS = [  # candidate class, target class, kind
    ("Landform_ChannelCandidates_auto", "Landform_ChannelCenterlines", "channel"),
    ("Landform_ChannelCandidates_auto_ath", "Landform_ChannelCenterlines", "channel"),
    ("Landform_CraterCandidates_auto", "Landform_CraterRims", "crater"),
    ("Landform_CraterCandidates_auto_ath", "Landform_CraterRims", "crater"),
]
READ = {"channel": ["UnitName", "Confidence", "Evidence", "Notes", "Origin", "StrahlerOrd"],
        "crater": ["UnitName", "Confidence", "Evidence", "Notes", "DiameterKm", "Preservation"]}

apply = "--apply" in sys.argv
by = sys.argv[sys.argv.index("--by") + 1] if "--by" in sys.argv else None
if apply and not by:
    sys.exit('--apply needs --by "<reviewer name>" (written to MappedBy)')


def target_row(kind, src_id, r, now):
    """The values for the target class, from one candidate row r (a dict)."""
    notes = "; ".join(s for s in ((r["ReviewNote"] or "").strip(), (r["Notes"] or "").strip()) if s)
    row = {"SHAPE@": r["SHAPE@"], "UnitName": r["UnitName"], "Confidence": r["Confidence"],
           "Evidence": (r["Evidence"] or "candidate") + ACCEPT_NOTE, "Notes": notes or None,
           "MappedBy": by, "MappedOn": now, "SourceID": src_id}
    if kind == "channel":
        row.update(Origin=r["Origin"], OrderStrahler=r["StrahlerOrd"], GradientPct=None)
    else:
        row.update(DiameterKm=r["DiameterKm"], Preservation=r["Preservation"])
    return row


for src, dst, _ in JOBS:
    if "Review" not in [f.name for f in arcpy.ListFields(os.path.join(GDB, src))]:
        sys.exit("%s has no Review field: run add_review_fields.py first" % src)

# what each target already holds, by SourceID
copied = {}
for dst in sorted({j[1] for j in JOBS}):
    with arcpy.da.SearchCursor(os.path.join(GDB, dst), ["SourceID", "OID@"]) as c:
        copied[dst] = {s: oid for s, oid in c if s}

now = datetime.datetime.now().replace(microsecond=0)
pending = {}                    # target -> rows to insert
withdrawn, errors = [], []
print("%-38s %6s %6s %6s %6s %6s  %s" % ("candidate class", "rows", "accept", "reject", "unsure",
                                         "open", "precision"))
for src, dst, kind in JOBS:
    cols = ["OID@", "SHAPE@", "Review", "ReviewNote"] + READ[kind]
    tally = {"accept": 0, "reject": 0, "unsure": 0, "": 0}
    with arcpy.da.SearchCursor(os.path.join(GDB, src), cols) as c:
        for vals in c:
            r = dict(zip(cols, vals))
            decision = (r["Review"] or "").strip().lower()
            if decision not in tally:
                errors.append("%s:%d Review = %r (expected accept / reject / unsure)" % (src, r["OID@"], r["Review"]))
                continue
            tally[decision] += 1
            sid = "%s:%d" % (src, r["OID@"])
            if decision == "accept" and sid not in copied[dst]:
                pending.setdefault(dst, []).append(target_row(kind, sid, r, now))
            elif decision != "accept" and sid in copied[dst]:
                withdrawn.append("%s OBJECTID %d (from %s, now %r)" % (dst, copied[dst][sid], sid, decision or "empty"))
    judged = tally["accept"] + tally["reject"]
    print("%-38s %6d %6d %6d %6d %6d  %s" % (src, sum(tally.values()), tally["accept"], tally["reject"],
                                             tally["unsure"], tally[""],
                                             "%.0f %% of %d" % (100.0 * tally["accept"] / judged, judged) if judged else "-"))

# every text value must fit its target field, checked before anything is written
for dst, rows in pending.items():
    length = {f.name: f.length for f in arcpy.ListFields(os.path.join(GDB, dst)) if f.type == "String"}
    for row in rows:
        for k, v in row.items():
            if k in length and isinstance(v, str) and len(v) > length[k]:
                errors.append("%s: %s is %d characters, %s.%s holds %d" % (row["SourceID"], k, len(v), dst, k, length[k]))

print()
for dst in sorted(copied):
    print("%-38s holds %d copied candidates; %d new accepts to copy" % (dst, len(copied[dst]), len(pending.get(dst, []))))
for w in withdrawn:
    print("NO LONGER ACCEPTED, remove by hand if intended:", w)
if errors:
    print("\nNothing written. Fix these first:")
    for e in errors:
        print("  ", e)
    sys.exit(1)
if not apply:
    print("\nDry run, nothing written. Copy with: --apply --by \"<reviewer name>\"")
    sys.exit(0)

for dst, rows in pending.items():
    cols = list(rows[0])
    with arcpy.da.InsertCursor(os.path.join(GDB, dst), cols) as ic:
        for row in rows:
            ic.insertRow([row[k] for k in cols])
    print("copied %d rows into %s, MappedBy = %s" % (len(rows), dst, by))
if not pending:
    print("\nNothing new to copy.")
