# -*- coding: utf-8 -*-
"""Do the repeated figures agree in CONTEXT, or only co-occur?

Pulls every sentence in the built deliverables that carries one of the key
numbers, so contradictory phrasings show up side by side.
"""
import sys as _sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import re
import zipfile

DELIV = on_drive(r"Mars Remote Sensing Project")
FILES = {
    "P1": "ocean first pres LE.pptx",
    "PROS": "Mars Mosaic - Project Prospectus.docx",
    "IDECK": r"NEXT STUFF\Mars Global Mosaic - Interim Presentation.pptx",
    "IREP": r"NEXT STUFF\Mars Mosaic - Interim Report.docx",
}

PROBES = [
    ("THEMIS pixel count", r"22\.\d+\s*(?:of\s*22\.\d+\s*)?b(?:n|illion)[^.;]*"),
    ("size on disk", r"\d{2}(?:\.\d)?\s*GB[^.;]*"),
    ("Viking slope runtime", r"1\s*h\s*05[^.;]*"),
    ("hillshade runtime", r"(?:11|12)\s*min[^.;]*"),
    ("composite attempts", r"(?:Three|Four) attempts[^.;]*"),
    ("crater counts", r"141[^.;]*"),
    ("relief", r"29,754[^.;]*"),
    ("central meridian", r"central meridian[^.;]*"),
    ("pyramids", r"[Pp]yramids[^.;]*"),
]


def text(path):
    out = []
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if re.match(r"(word/document|ppt/(slides|notesSlides)/[a-zA-Z]+\d+)\.xml$", n):
                out += re.findall(r"<[aw]:t[^>]*>([^<]*)</[aw]:t>",
                                  z.read(n).decode("utf-8"))
    return re.sub(r"\s+", " ", " ".join(out))


docs = {k: text(os.path.join(DELIV, v)) for k, v in FILES.items()}

for label, pat in PROBES:
    print("=" * 96)
    print(label.upper())
    seen = {}
    for k, t in docs.items():
        for m in re.finditer(pat, t):
            frag = m.group(0).strip()[:120]
            seen.setdefault(frag, []).append(k)
    if not seen:
        print("   (no match)")
    for frag, where in sorted(seen.items()):
        print("   [%-16s] %s" % (",".join(sorted(set(where))), frag))
