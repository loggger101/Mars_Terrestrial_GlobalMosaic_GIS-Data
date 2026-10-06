# -*- coding: utf-8 -*-
"""List only the LIVE rows of GDB_Items (the geodatabase catalogue of datasets).

Same trick as gdbmap2: walk the .gdbtablx row index so deleted rows and stale
free-space bytes are excluded.
"""
import os
import re
import struct

GDB = r"Z:\Mars Project\Mars Project.gdb"
tab = open(os.path.join(GDB, "a00000004.gdbtable"), "rb").read()
idx = open(os.path.join(GDB, "a00000004.gdbtablx"), "rb").read()

n_rows, entry_sz = struct.unpack("<II", idx[8:16])
print("GDB_Items: %d row slots\n" % n_rows)

live = []
for i in range(n_rows):
    raw = idx[16 + i * entry_sz: 16 + (i + 1) * entry_sz]
    if len(raw) < entry_sz:
        break
    off = int.from_bytes(raw, "little") & 0x00FFFFFFFF
    if off == 0:
        continue
    row_len = struct.unpack("<I", tab[off:off + 4])[0]
    blob = tab[off + 4: off + 4 + row_len].decode("latin-1")
    m = re.search(r"<CatalogPath>\\([^<]*)</CatalogPath>", blob)
    path = m.group(1) if m else ""
    d = re.search(r"<DatasetType>([^<]*)</DatasetType>", blob)
    s = re.search(r"<DSID>(\d+)</DSID>", blob)
    live.append((i + 1, path, d.group(1) if d else "", s.group(1) if s else "",
                 row_len))

print("%-5s %-46s %-22s %-6s %s" % ("OID", "CatalogPath", "DatasetType", "DSID", "bytes"))
for oid, path, dt, dsid, ln in live:
    print("%-5d %-46s %-22s %-6s %d" % (oid, path or "(root/none)", dt, dsid, ln))

print("\n%d live rows" % len(live))
names = [p for _o, p, _d, _s, _l in live]
for probe in ("Slope_Mars_V1_CompositeBands", "Slope_Mars_H1", "Surface_Mars1",
              "HillSha_Mars1"):
    print("  %-32s %s" % (probe, "LIVE" if probe in names else "NOT A LIVE ROW"))
print("\nraw byte occurrences of the composite name in the file: %d"
      % tab.decode("latin-1").count("Slope_Mars_V1_CompositeBands"))
