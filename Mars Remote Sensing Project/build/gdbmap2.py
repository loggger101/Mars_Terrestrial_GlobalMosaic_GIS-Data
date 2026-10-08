# -*- coding: utf-8 -*-
"""Authoritative table map: walk GDB_SystemCatalog through its .gdbtablx row index.

The .gdbtablx gives one entry per ObjectID; entry value 0 means the row is
deleted, so this reads only LIVE catalog rows -- unlike scraping the .gdbtable,
which also picks up stale names sitting in free space.
"""
import os
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
import re
import struct

GDB = on_drive(r"Mars Project\Mars Project.gdb")
tab = open(os.path.join(GDB, "a00000001.gdbtable"), "rb").read()
idx = open(os.path.join(GDB, "a00000001.gdbtablx"), "rb").read()

n_rows = struct.unpack("<I", idx[8:12])[0]
entry_sz = struct.unpack("<I", idx[12:16])[0]
print("catalog: %d row slots, %d-byte index entries\n" % (n_rows, entry_sz))


def stat(objid):
    f = os.path.join(GDB, "a%08x.gdbtable" % objid)
    if not os.path.exists(f):
        return None, 0.0
    with open(f, "rb") as fh:
        rows = struct.unpack("<I", fh.read(8)[4:8])[0]
    return rows, os.path.getsize(f) / 1e6


print("%-6s %-46s %10s %11s" % ("OID", "TABLE (live catalog row)", "ROWS", "SIZE MB"))
live = 0
for i in range(n_rows):
    raw = idx[16 + i * entry_sz: 16 + (i + 1) * entry_sz]
    if len(raw) < entry_sz:
        break
    off = int.from_bytes(raw, "little") & 0x00FFFFFFFF
    if off == 0:
        continue
    live += 1
    row_len = struct.unpack("<I", tab[off:off + 4])[0]
    blob = tab[off + 4: off + 4 + min(row_len, 200)]
    m = re.search(rb"[A-Za-z][A-Za-z0-9_]{3,79}", blob)
    name = m.group().decode() if m else "?"
    oid = i + 1
    rows, size = stat(oid)
    tag = "" if rows is not None else "   <NO TABLE FILE>"
    print("%-6d %-46s %10s %11.1f%s"
          % (oid, name, "-" if rows is None else rows, size, tag))
print("\n%d live catalog rows" % live)
