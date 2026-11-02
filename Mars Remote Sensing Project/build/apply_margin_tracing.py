# -*- coding: utf-8 -*-
r"""Write lava-flow margins traced on the CTX plates into Landform_LavaFlowMargins (KB §69.52).

    python apply_margin_tracing.py <plates folder> <tracing.json>                     # dry run
    python apply_margin_tracing.py <plates folder> <tracing.json> --apply --by "<name>"

<tracing.json>: {"W040": [{"pts": [[x_km, y_km], ...], "conf": "probable" | "inferred", "type": "<MarginType>",
"note": "..."}], ...}, vertices in km from the plate's south-west corner as make_margin_plates.py labels them. Each
line becomes one row: geometry in the class's CM180 frame (index.json gives each plate's corner), FlowUnit "lAv",
UnitName "Athabasca Valles flood lava (SIM 3292 lAv)", Confidence as given, MarginType as given, Evidence "traced on
CTX (Murray Lab V01), plate <W>", MappedBy <name>, MappedOn today.

Refused, with nothing written: an unknown plate; a vertex outside its plate (0-24 km); a line under 2 vertices or
shorter than 1 km; a confidence other than certain / probable / inferred; a value longer than its field. A plate whose
lines are already in the class (Evidence names the plate) is skipped, so a rerun adds only new plates. With --apply
the class is first copied to <drive>\Mars Project\.backups\margins_<time>.gdb. --gdb <path> for a scratch copy.
ArcGIS Python.
"""
import os, sys, json, time, datetime, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive

FC = "Landform_LavaFlowMargins"
UNIT = "Athabasca Valles flood lava (SIM 3292 lAv)"
CONF = {"certain", "probable", "inferred"}


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    folder, tracing = sys.argv[1], sys.argv[2]
    apply, by, gdb = "--apply" in sys.argv, arg("--by"), arg("--gdb", GDB)
    if apply and not by:
        sys.exit('--apply needs --by "<mapper name>"')
    idx = json.load(open(os.path.join(folder, "index.json")))
    plates, size = idx["windows"], 2 * idx["half_m"] / 1000.0
    lines = json.load(open(tracing, encoding="utf-8"))
    fc = os.path.join(gdb, FC)
    fields = {f.name: f for f in arcpy.ListFields(fc)}
    done = set()
    with arcpy.da.SearchCursor(fc, ["Evidence"]) as cur:
        for (ev,) in cur:
            if ev and "plate W" in ev:
                done.add(ev.rsplit("plate ", 1)[1].split()[0].strip(",;)"))
    errors, rows = [], []
    today = datetime.datetime.combine(datetime.date.today(), datetime.time())
    for w, items in sorted(lines.items()):
        if w not in plates:
            errors.append("%s is not a plate" % w); continue
        if w in done:
            print("%s: already in the class, skipped" % w); continue
        p = plates[w]
        for k, it in enumerate(items, 1):
            pts = it.get("pts", [])
            bad = [q for q in pts if not (0 <= q[0] <= size and 0 <= q[1] <= size)]
            km = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
            if len(pts) < 2 or km < 1.0:
                errors.append("%s line %d: %d vertices, %.2f km" % (w, k, len(pts), km)); continue
            if bad:
                errors.append("%s line %d: vertices outside the plate %s" % (w, k, bad)); continue
            if it.get("conf") not in CONF:
                errors.append("%s line %d: confidence %r" % (w, k, it.get("conf"))); continue
            vals = {"UnitName": UNIT, "Confidence": it["conf"], "FlowUnit": "lAv",
                    "MarginType": it.get("type", "flow edge"),
                    "Evidence": "traced on CTX (Murray Lab V01), plate %s" % w,
                    "Notes": it.get("note", ""), "MappedBy": by or "", "MappedOn": today}
            for f, v in vals.items():
                if isinstance(v, str) and len(v) > fields[f].length:
                    errors.append("%s line %d: %s longer than %d" % (w, k, f, fields[f].length))
            xy = [(p["x0"] + 1000.0 * q[0], p["y0"] + 1000.0 * q[1]) for q in pts]
            rows.append((w, km, xy, vals))
    if errors:
        sys.exit("refused, nothing written: " + "; ".join(errors))
    print("%d lines on %d plates, %.0f km, to write" % (len(rows), len({r[0] for r in rows}), sum(r[1] for r in rows)))
    if not apply:
        print('Dry run, nothing written. Write with: --apply --by "<mapper name>"'); return
    if not rows:
        return
    bak_dir = on_drive(r"Mars Project\.backups") if "--gdb" not in sys.argv else os.path.dirname(gdb)
    bak = "margins_%s.gdb" % time.strftime("%Y%m%d-%H%M%S")
    arcpy.management.CreateFileGDB(bak_dir, bak)
    arcpy.conversion.FeatureClassToFeatureClass(fc, os.path.join(bak_dir, bak), FC)
    print("backed up to", os.path.join(bak_dir, bak))
    sr = arcpy.Describe(fc).spatialReference
    cols = ["SHAPE@"] + list(rows[0][3])
    with arcpy.da.InsertCursor(fc, cols) as cur:
        for w, km, xy, vals in rows:
            g = arcpy.Polyline(arcpy.Array([arcpy.Point(x, y) for x, y in xy]), sr)
            cur.insertRow([g] + list(vals.values()))
    print("written:", len(rows))


if __name__ == "__main__":
    main()
