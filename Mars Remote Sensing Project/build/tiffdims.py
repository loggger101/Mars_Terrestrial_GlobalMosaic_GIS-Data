# -*- coding: utf-8 -*-
"""Read width/height/bands straight out of the (Big)TIFF header."""
import struct
import sys

TAGS = {256: "ImageWidth", 257: "ImageLength", 258: "BitsPerSample",
        277: "SamplesPerPixel", 339: "SampleFormat"}


def dims(path):
    fh = open(path, "rb")
    bo = fh.read(2)
    end = "<" if bo == b"II" else ">"
    ver = struct.unpack(end + "H", fh.read(2))[0]
    if ver == 42:
        off = struct.unpack(end + "I", fh.read(4))[0]
        fh.seek(off)
        n = struct.unpack(end + "H", fh.read(2))[0]
        entry, cnt_fmt = 12, end + "HHI4s"
    else:                                     # BigTIFF
        struct.unpack(end + "HH", fh.read(4))
        off = struct.unpack(end + "Q", fh.read(8))[0]
        fh.seek(off)
        n = struct.unpack(end + "Q", fh.read(8))[0]
        entry, cnt_fmt = 20, end + "HHQ8s"
    out = {}
    for _ in range(n):
        raw = fh.read(entry)
        tag, typ, cnt, val = struct.unpack(cnt_fmt, raw)
        if tag in TAGS:
            width = 2 if typ == 3 else (4 if typ == 4 else 8)
            v = int.from_bytes(val[:width], "little" if end == "<" else "big")
            out[TAGS[tag]] = v
    return out


for p in sys.argv[1:]:
    d = dims(p)
    w, h = d.get("ImageWidth"), d.get("ImageLength")
    print(p)
    print("   %s x %s  = %.2f billion pixels   bands=%s  bits=%s"
          % (w, h, w * h / 1e9, d.get("SamplesPerPixel"), d.get("BitsPerSample")))
