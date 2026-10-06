# -*- coding: utf-8 -*-
"""Audit the parts nobody has checked yet: the calendar, leftover placeholders,
and numbers that appear in more than one place and must agree."""
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import datetime as dt
import re
import sys

sys.path.insert(0, r"Z:\Mars Remote Sensing Project\build")
import content as C                                              # noqa: E402

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
issues = []

# ---------------------------------------------------------------- calendar --
print("=" * 78)
print("SCHEDULE vs the real 2026 calendar")
print("%-6s %-22s %-10s %-10s %s" % ("week", "dates", "start", "end", "check"))
prev_end = None
for wk, dates, _act, _dl in C.SCHEDULE:
    a, b = [s.strip() for s in dates.replace("\u2013", "-").split("-")]
    d = []
    for part in (a, b):
        mon, day = part.split()
        d.append(dt.date(2026, MONTHS[mon[:3]], int(day)))
    start, end = d
    notes = []
    if start.weekday() != 0:
        notes.append("start is %s, not Monday" % start.strftime("%A"))
    if end.weekday() != 4:
        notes.append("end is %s, not Friday" % end.strftime("%A"))
    span_weeks = (end - start).days // 7 + 1
    declared = len(wk.split("\u2013")) if "\u2013" in wk else 1
    if span_weeks != declared:
        notes.append("spans %d weeks, labelled %s" % (span_weeks, wk))
    if prev_end and (start - prev_end).days != 3:
        notes.append("%d-day gap after previous week" % ((start - prev_end).days - 3))
    prev_end = end
    if notes:
        issues.append("week %s: %s" % (wk, "; ".join(notes)))
    print("%-6s %-22s %-10s %-10s %s"
          % (wk, dates, start.strftime("%a %d %b"), end.strftime("%a %d %b"),
             "; ".join(notes) or "ok"))

# US Thanksgiving 2026 = 4th Thursday of November
nov = [dt.date(2026, 11, d) for d in range(1, 31)]
thanks = [d for d in nov if d.weekday() == 3][3]
print("\nUS Thanksgiving 2026 falls on %s" % thanks.strftime("%A %d %B"))

# --------------------------------------------------------- placeholders ----
print()
print("=" * 78)
print("PLACEHOLDERS AND UNRESOLVED TEXT")
PATTERNS = [r"\[[^\]]{3,60}\]", r"\bTBD\b", r"\bXXX+\b", r"\bLorem\b",
            r"\bYour Name\b", r"\bInstructor\b", r"are assumed",
            r"should be adjusted", r"\bTODO\b", r"\bFIXME\b", r"\bplaceholder\b"]
hits = 0
for name in dir(C):
    if name.startswith("_"):
        continue
    val = getattr(C, name)
    if not isinstance(val, (str, list, tuple)):
        continue
    flat = val if isinstance(val, str) else str(val)
    for pat in PATTERNS:
        for m in re.finditer(pat, flat, re.I):
            hits += 1
            s = max(0, m.start() - 70)
            print("   %-16s %r" % (name, flat[s:m.end() + 70]))
if not hits:
    print("   none found")

print()
print("INVESTIGATORS block:")
for row in C.INVESTIGATORS:
    print("   %s" % (row,))

# ------------------------------------------------- repeated-number check ---
print()
print("=" * 78)
print("NUMBERS THAT APPEAR IN MORE THAN ONE BLOCK (must agree)")
blocks = {n: str(getattr(C, n)) for n in dir(C)
          if not n.startswith("_") and isinstance(getattr(C, n), (str, list, tuple))}
KEY = ["213,390", "106,696", "106,694", "53,347", "92,160", "46,080",
       "22.14", "22.77", "22.8", "43.7", "44 GB", "8,528", "21,226", "29,754",
       "141", "972", "1,113", "7 min 15 s", "11 min 42 s", "1 h 05 min",
       "1 h 26 min 45 s", "47 min 57 s", "1 min 41 s", "1 h 14 min 51 s",
       "000869", "180", "100 m", "232 m", "200 m"]
for k in KEY:
    where = sorted(n for n, t in blocks.items() if k in t)
    if len(where) > 1:
        print("   %-18s %s" % (k, ", ".join(where)))

print()
print("=" * 78)
if issues:
    print("SCHEDULE ISSUES:")
    for i in issues:
        print("   -", i)
else:
    print("no schedule issues")
