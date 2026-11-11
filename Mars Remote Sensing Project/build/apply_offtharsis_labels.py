# -*- coding: utf-8 -*-
r"""Write off-Tharsis edifice and apron labels into Landform_TrainingSamples_offtharsis_draw (KB §69.63, §69.105).

    python apply_offtharsis_labels.py <drawing.json>                               # dry run
    python apply_offtharsis_labels.py <drawing.json> --apply --by "<mapped by>"

<drawing.json>: {"E1": {"class": 5 | 6, "plate": "S1", "pts": [[lon, lat], ...], "note": "..."}, ...}, vertices in
degrees east (0-360) and north, GCS Mars 2000 sphere, the class's own frame. Each polygon becomes one row: Classvalue,
Classname ("volcanic edifice" or "apron"), MappedBy as given, Notes "<id> plate <plate>: <note>".

Refused, nothing written: a class other than 5 or 6; under 3 vertices; a polygon crossing a 15° block line or outside
the two target blocks (4_0: 60-75°E, 0-15°N; 4_2: 60-75°E, 30-45°N); a polygon under 20 km² (about 5 km across);
an id already in the class's Notes (a rerun adds only new ids). With --apply the class is first copied to
<drive>\Mars Project\.backups\offtharsis_<time>.gdb. Pro must be closed. Not one of the three digitising classes
(those go through accept_reviewed.py only). ArcGIS Python.
"""
import os, sys, json, time, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive

FC = os.path.join(GDB, "Landform_TrainingSamples_offtharsis_draw")
NAMES = {5: "volcanic edifice", 6: "apron"}
BLOCKS = {"4_0": (60.0, 75.0, 0.0, 15.0), "4_2": (60.0, 75.0, 30.0, 45.0)}
MARS = arcpy.SpatialReference(104905)
KM2_PER_DEG2 = (3396.19 * math.pi / 180.0) ** 2


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def area_km2(pts):
    """Shoelace area on the sphere's local scale (cos of the mean latitude)."""
    k = math.cos(math.radians(sum(p[1] for p in pts) / len(pts)))
    s = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return abs(s) / 2.0 * k * KM2_PER_DEG2


def main():
    drawing = json.load(open(sys.argv[1], encoding="utf-8"))
    apply, by = "--apply" in sys.argv, arg("--by")
    if apply and not by:
        sys.exit('--apply needs --by "<mapped by>"')
    have = set()
    with arcpy.da.SearchCursor(FC, ["Notes"]) as cur:
        for (n,) in cur:
            if n:
                have.add(n.split()[0])
    errors, rows = [], []
    for pid, p in sorted(drawing.items()):
        if pid in have:
            print("%s: already in the class, skipped" % pid); continue
        pts, cls = p.get("pts", []), p.get("class")
        if cls not in NAMES:
            errors.append("%s: class %r" % (pid, cls)); continue
        if len(pts) < 3:
            errors.append("%s: %d vertices" % (pid, len(pts))); continue
        lons, lats = [q[0] for q in pts], [q[1] for q in pts]
        blk = [b for b, (x0, x1, y0, y1) in BLOCKS.items()
               if x0 <= min(lons) and max(lons) <= x1 and y0 <= min(lats) and max(lats) <= y1]
        if not blk:
            errors.append("%s: not inside one target block (%.2f-%.2f E, %.2f-%.2f N)" % (
                pid, min(lons), max(lons), min(lats), max(lats))); continue
        a = area_km2(pts)
        if a < 20:
            errors.append("%s: %.1f km2, under 20" % (pid, a)); continue
        note = "%s plate %s: %s" % (pid, p.get("plate", "?"), p.get("note", ""))
        rows.append((pid, cls, blk[0], a, pts, note[:255]))
        print("%s  %d %-16s block %s  %7.1f km2  %s" % (pid, cls, NAMES[cls], blk[0], a, p.get("note", "")))
    if errors:
        sys.exit("refused, nothing written:\n  " + "\n  ".join(errors))
    for c in NAMES:
        n = [r for r in rows if r[1] == c]
        print("class %d %s: %d polygons, %.0f km2" % (c, NAMES[c], len(n), sum(r[3] for r in n)))
    if not apply:
        print("dry run: nothing written (--apply --by \"...\" to write)")
        return
    bak = on_drive(os.path.join("Mars Project", ".backups", "offtharsis_%s.gdb" % time.strftime("%Y%m%d-%H%M%S")))
    arcpy.management.CreateFileGDB(os.path.dirname(bak), os.path.basename(bak))
    arcpy.management.Copy(FC, os.path.join(bak, os.path.basename(FC)))
    print("backup:", bak)
    with arcpy.da.InsertCursor(FC, ["SHAPE@", "Classvalue", "Classname", "MappedBy", "Notes"]) as cur:
        for pid, cls, blk, a, pts, note in rows:
            ring = arcpy.Array([arcpy.Point(x, y) for x, y in pts + pts[:1]])
            cur.insertRow((arcpy.Polygon(ring, MARS), cls, NAMES[cls], by, note))
    print("wrote %d rows to %s" % (len(rows), FC))


if __name__ == "__main__":
    main()
