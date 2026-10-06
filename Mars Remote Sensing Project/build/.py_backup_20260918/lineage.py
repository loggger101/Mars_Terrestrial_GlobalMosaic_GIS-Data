# -*- coding: utf-8 -*-
"""Recover the geoprocessing lineage recorded in the file geodatabase item table."""
import re, sys

path = r"Z:\Mars Project\Mars Project.gdb\a00000004.gdbtable"
txt = open(path, "rb").read().decode("latin-1")

procs = re.findall(
    r'<Process\s+ToolSource="([^"]*)"\s+Date="(\d{8})"\s+Time="(\d{6})"[^>]*>(.*?)</Process>',
    txt, re.S)

print("### %d <Process> entries recovered" % len(procs))
seen = set()
rows = []
for tool, date, time, body in procs:
    body = re.sub(r"\s+", " ", body).strip()
    key = (date, time, body[:90])
    if key in seen:
        continue
    seen.add(key)
    rows.append((date, time, tool.split("\\")[-1], body))

for date, time, tool, body in sorted(rows):
    ts = "%s-%s-%s %s:%s:%s" % (date[:4], date[4:6], date[6:], time[:2], time[2:4], time[4:])
    print()
    print("%s  [%s]" % (ts, tool))
    print("   " + body[:600])

print()
print("### distinct tools")
for t in sorted(set(r[2] for r in rows)):
    print("  ", t)

# any other dataset names in the catalog
print()
print("### other dataset names mentioned")
for m in sorted(set(re.findall(r'gdb\\([A-Za-z0-9_]{4,60})', txt))):
    print("  ", m)
