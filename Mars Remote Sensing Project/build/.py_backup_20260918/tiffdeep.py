# -*- coding: utf-8 -*-
"""Count TIFF IFDs (internal pyramids) and read the GeoTIFF CRS citation."""
import os
import re
import struct
import sys

GEO_ASCII = 34737          # GeoAsciiParamsTag
GEO_KEYS = 34735           # GeoKeyDirectoryTag
PIXEL_SCALE = 33550


def walk(path):
    fh = open(path, "rb")
    end = "<" if fh.read(2) == b"II" else ">"
    ver = struct.unpack(end + "H", fh.read(2))[0]
    big = ver == 43
    if big:
        struct.unpack(end + "HH", fh.read(4))
        nxt = struct.unpack(end + "Q", fh.read(8))[0]
        esz, cfmt, off_fmt = 20, end + "HHQ8s", end + "Q"
    else:
        nxt = struct.unpack(end + "I", fh.read(4))[0]
        esz, cfmt, off_fmt = 12, end + "HHI4s", end + "I"

    ifds, first = [], {}
    while nxt and len(ifds) < 64:
        fh.seek(nxt)
        n = struct.unpack(off_fmt, fh.read(8 if big else 2).ljust(8 if big else 2,
                                                                  b"\0"))[0] \
            if big else struct.unpack(end + "H", fh.read(0) or b"")[0] \
            if False else None
        fh.seek(nxt)
        n = struct.unpack(end + "Q", fh.read(8))[0] if big else \
            struct.unpack(end + "H", fh.read(2))[0]
        tags = {}
        for _ in range(n):
            tag, typ, cnt, val = struct.unpack(cfmt, fh.read(esz))
            tags[tag] = (typ, cnt, val)
        w = tags.get(256), tags.get(257)
        ifds.append((tags.get(256), tags.get(257)))
        if not first:
            first = tags
        nxt = struct.unpack(off_fmt, fh.read(8 if big else 4))[0]

    def ascii_tag(tag):
        if tag not in first:
            return ""
        typ, cnt, val = first[tag]
        off = int.from_bytes(val[:8 if big else 4], "little" if end == "<" else "big")
        if cnt <= (8 if big else 4):
            return val[:cnt].decode("latin-1", "replace")
        fh.seek(off)
        return fh.read(cnt).decode("latin-1", "replace")

    def num(tagtuple):
        if not tagtuple:
            return None
        typ, cnt, val = tagtuple
        width = 2 if typ == 3 else (4 if typ == 4 else 8)
        return int.from_bytes(val[:width], "little" if end == "<" else "big")

    print(os.path.basename(path))
    print("   IFDs (image + internal overviews): %d" % len(ifds))
    for i, (w, h) in enumerate(ifds):
        print("      level %d: %s x %s" % (i, num(w), num(h)))
    cite = ascii_tag(GEO_ASCII)
    if cite:
        print("   GeoASCII: %s" % re.sub(r"\|", " | ", cite.strip("\0")))
    for ext in (".ovr", ".rrd", ".aux"):
        side = path + ext
        print("   %-5s sidecar: %s" % (ext, "yes" if os.path.exists(side) else "no"))
    print()


for p in sys.argv[1:]:
    try:
        walk(p)
    except Exception as exc:
        print("%s -> ERROR %s\n" % (os.path.basename(p), exc))
