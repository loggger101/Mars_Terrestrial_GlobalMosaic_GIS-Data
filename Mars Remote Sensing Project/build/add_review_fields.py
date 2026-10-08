# -*- coding: utf-8 -*-
r"""Review fields for digitising by review (NEXT-STEPS D10, item 3.6; KB §46).

Digitising starts by judging the machine candidates instead of redrawing them. Each candidate
class gets two fields, filled in the attribute table in Pro:

  Review      accept / reject / unsure, a drop-down from the gdb domain ReviewDecision;
              empty = not yet reviewed
  ReviewNote  free text, up to 60 characters; it becomes the start of Notes on the copied row

The two digitising classes that receive accepted candidates get

  SourceID    "<candidate class>:<OBJECTID>", set by accept_reviewed.py, so a rerun never copies
              a row twice and every copied feature can be traced to its candidate

Nothing here writes a row. Copying is accept_reviewed.py, and only an explicit accept moves a
candidate into a Landform_* class (NEXT-STEPS §10). Idempotent: an existing field or domain is
left as it is. Pro must be closed (adding a field needs a schema lock).
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import GDB

CANDIDATES = ["Landform_ChannelCandidates_auto", "Landform_ChannelCandidates_auto_ath",
              "Landform_CraterCandidates_auto", "Landform_CraterCandidates_auto_ath"]
TARGETS = ["Landform_ChannelCenterlines", "Landform_CraterRims"]
DOMAIN = "ReviewDecision"
CHOICES = ["accept", "reject", "unsure"]
NOTE_LEN = 60        # + "; " + the longest machine note must fit the target's Notes (255)
SOURCE_LEN = 48      # "Landform_ChannelCandidates_auto_ath:" is 36 characters

assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"


def fields(fc):
    return {f.name: f for f in arcpy.ListFields(fc)}


def add(fc, name, length, alias):
    have = fields(fc)
    if name in have:
        print("  %-38s %-10s exists (TEXT %d)" % (os.path.basename(fc), name, have[name].length))
        return
    arcpy.management.AddField(fc, name, "TEXT", field_length=length, field_alias=alias)
    print("  %-38s %-10s added  (TEXT %d)" % (os.path.basename(fc), name, length))


if DOMAIN not in [d.name for d in arcpy.da.ListDomains(GDB)]:
    arcpy.management.CreateDomain(GDB, DOMAIN, "Candidate review: accept, reject or unsure",
                                  "TEXT", "CODED")
    for c in CHOICES:
        arcpy.management.AddCodedValueToDomain(GDB, DOMAIN, c, c)
    print("domain %s created: %s" % (DOMAIN, ", ".join(CHOICES)))
else:
    print("domain %s exists" % DOMAIN)

for name in CANDIDATES:
    fc = os.path.join(GDB, name)
    add(fc, "Review", 6, "Review (accept / reject / unsure)")
    add(fc, "ReviewNote", NOTE_LEN, "Review note")
    if fields(fc)["Review"].domain != DOMAIN:
        arcpy.management.AssignDomainToField(fc, "Review", DOMAIN)
        print("  %-38s Review     domain %s assigned" % (name, DOMAIN))

for name in TARGETS:
    add(os.path.join(GDB, name), "SourceID", SOURCE_LEN, "Source candidate (class:OBJECTID)")

# ------------------------------------------------------------------ check what is on disk now
print()
bad = 0
for name in CANDIDATES:
    f = fields(os.path.join(GDB, name))
    ok = ("Review" in f and f["Review"].domain == DOMAIN and "ReviewNote" in f)
    n = int(arcpy.management.GetCount(os.path.join(GDB, name))[0])
    print("%-4s %-38s %5d rows, Review domain=%s" % ("ok" if ok else "FAIL", name, n,
                                                    f["Review"].domain if "Review" in f else "-"))
    bad += not ok
for name in TARGETS:
    ok = "SourceID" in fields(os.path.join(GDB, name))
    print("%-4s %-38s SourceID" % ("ok" if ok else "FAIL", name))
    bad += not ok
codes = sorted(next(d for d in arcpy.da.ListDomains(GDB) if d.name == DOMAIN).codedValues)
print("domain codes:", codes)
sys.exit(1 if bad or codes != sorted(CHOICES) else 0)
