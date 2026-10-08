# -*- coding: utf-8 -*-
"""Map FileGDB table ids to names and read each table's row count."""
import os, re, struct
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction

gdb = on_drive(r"Mars Project\Mars Project.gdb")

# a00000001.gdbtable is GDB_SystemCatalog: one row per table, in ObjectID order.
data = open(os.path.join(gdb, "a00000001.gdbtable"), "rb").read()

# Rows are length-prefixed; pull printable names in file order.
names = []
for m in re.finditer(rb"[\x20-\x7e]{4,80}", data):
    s = m.group().decode()
    if s.startswith(("GDB_", "fras_", "VAT_")) or len(s) < 4:
        continue
    names.append((m.start(), s))

print("### names in catalog order")
for off, n in names:
    print("   %6d  %s" % (off, n))

# Row count lives at offset 4 of each .gdbtable (uint32 LE).
print()
print("### row counts per table file")
rows = {}
for f in sorted(os.listdir(gdb)):
    if not re.fullmatch(r"a[0-9a-f]{8}\.gdbtable", f):
        continue
    with open(os.path.join(gdb, f), "rb") as fh:
        head = fh.read(8)
    if len(head) < 8:
        continue
    n = struct.unpack("<I", head[4:8])[0]
    size = os.path.getsize(os.path.join(gdb, f))
    rows[f] = (n, size)

for f, (n, size) in rows.items():
    if n and n < 50_000_000 and size > 2000:
        print("   %-22s rows=%-10d size=%.1fMB" % (f, n, size / 1e6))
