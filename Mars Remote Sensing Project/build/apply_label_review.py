# -*- coding: utf-8 -*-
r"""The v2 labels from the author's review of the proposals (decision D17, KB §68; NEXT-STEPS §11.5).

Reads Landform_TrainingSamples_v2_proposals (propose_label_changes.py, then the author's Review) and
writes

  Landform_TrainingSamples_v2            every label as it stands after the review
  Landform_TrainingSamples_v2_60_train   clipped to ±60° and split as the four-class labels were:
  Landform_TrainingSamples_v2_60_test    the same 14 held-out blocks, the block of each clipped
                                         polygon's centroid (make_global60_classification.py)

A row counts only when its Review is "accept": it then enters with its own outline (as the author left
it) and its ProposedClass; an accepted "delete" drops the label. Any other row of the 512 enters as it
was, outline and class read from Landform_TrainingSamples_terrain by OldOID; any other new row is left
out. "unsure" counts as not accepted. To change a class the author sets ProposedClass and accepts.

Refuses to write if two labels of different classes, or a training and a held-out label, share ground;
reports each class against the minimum of NEXT-STEPS §11.3 and leaves a class short of it out of the two
split classes (--keep-short keeps it). Classes this script did not write are never replaced. Pro closed.

  python apply_label_review.py --dry-run     the tally and the checks, nothing written
  python apply_label_review.py
Options --gdb (labels and proposals) and --out-gdb (default the same) point it at a test copy.
Writes logs\label_review_applied.json (--log to move it).
"""
import os, sys, json, math, time, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB as DRIVE_GDB

def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

GDB = opt("--gdb", DRIVE_GDB)
OUT_GDB = opt("--out-gdb", GDB)
LOG = opt("--log", os.path.join(HERE, "logs", "label_review_applied.json"))
DRY = "--dry-run" in sys.argv
MARKER = "apply_label_review.py"
LABELS = "Landform_TrainingSamples_terrain"
TEST4 = "Landform_TrainingSamples_terrain_60_test"
PROPOSALS = "Landform_TrainingSamples_v2_proposals"
EXTENT = "Analysis_Extent_60"
V2, TRAIN, TEST = "Landform_TrainingSamples_v2", "Landform_TrainingSamples_v2_60_train", "Landform_TrainingSamples_v2_60_test"
BLOCK = 15.0
MIN_TEST, MIN_TEST_BLOCKS, MIN_TRAIN, MIN_TRAIN_BLOCKS = 10, 2, 20, 3

# codes 1-4 and their colours as in the hand-drawn labels (KB §29.2); 5-7 new (KB §68.1)
CLASSES = {1: ("Crater", (255, 0, 0)), 2: ("steep/windy hills", (28, 119, 85)), 3: ("lava tube", (158, 25, 147)),
           4: ("Normal Ground", (81, 51, 13)), 5: ("volcanic edifice", (255, 170, 0)),
           6: ("apron", (115, 178, 255)), 7: ("fluvial channel", (0, 92, 230))}


def km2(g):
    return g.getArea("GEODESIC", "SQUAREKILOMETERS")


def safe_to_replace(fc):
    if not arcpy.Exists(fc):
        return True
    if "MappedBy" not in [f.name for f in arcpy.ListFields(fc)]:
        return False
    with arcpy.da.SearchCursor(fc, ["MappedBy"]) as c:
        return all(r[0] == MARKER for r in c)


def final_labels():
    orig = {}
    with arcpy.da.SearchCursor(os.path.join(GDB, LABELS), ["OID@", "Classvalue", "SHAPE@"]) as c:
        for oid, cv, g in c:
            orig[oid] = (cv, g)
    out, tally, seen = [], collections.Counter(), set()
    flds = ["OID@", "OldOID", "Action", "ProposedClass", "Subtype", "Review", "SHAPE@"]
    with arcpy.da.SearchCursor(os.path.join(GDB, PROPOSALS), flds) as c:
        for pid, old, act, pc, sub, rev, g in c:
            rev = (rev or "").strip()
            ok = rev == "accept"
            tally[(act, rev or "(none)")] += 1
            if old is not None:
                seen.add(old)
            if ok:
                if act == "delete":
                    continue
                if pc not in CLASSES or g is None or g.area <= 0:
                    sys.exit("accepted row %d has class %r or an empty outline" % (pid, pc))
                out.append(dict(cls=pc, geom=g, sub=sub or "", pid=pid, old=old))
            elif old is not None:
                cv, og = orig[old]
                out.append(dict(cls=cv, geom=og, sub="", pid=pid, old=old))
    missing = sorted(set(orig) - seen)
    if missing:
        sys.exit("the proposals lack %d of the hand-drawn labels (OldOID %s): rerun propose_label_changes.py" % (
            len(missing), missing[:10]))
    return out, tally


def split(rows, held, ext):
    for r in rows:
        g = r["geom"].intersect(ext, 4)
        r["g60"] = g if g is not None and g.area > 0 else None
        if r["g60"] is None:
            r["split"] = r["block"] = None
            continue
        c = r["g60"].centroid
        r["block"] = "%d_%d" % (math.floor(c.X / BLOCK), math.floor(c.Y / BLOCK))
        r["split"] = "test" if r["block"] in held else "train"


def overlaps(rows):
    clash, cross = [], []
    for i, a in enumerate(rows):
        ea = a["geom"].extent
        for b in rows[i + 1:]:
            eb = b["geom"].extent
            if ea.XMax < eb.XMin or eb.XMax < ea.XMin or ea.YMax < eb.YMin or eb.YMax < ea.YMin:
                continue
            if a["geom"].disjoint(b["geom"]):
                continue
            x = a["geom"].intersect(b["geom"], 4)
            if x is None or x.area <= 0 or km2(x) < 0.01:
                continue
            k = round(km2(x), 2)
            if a["cls"] != b["cls"]:
                clash.append((a["pid"], b["pid"], a["cls"], b["cls"], k))
            if a["split"] and b["split"] and a["split"] != b["split"]:
                cross.append((a["pid"], b["pid"], k))
    return clash, cross


def write(name, rows, sr, geom_key, extra=False):
    fc = os.path.join(OUT_GDB, name)
    if not safe_to_replace(fc):
        sys.exit("REFUSING: %s holds rows this script did not write" % fc)
    if arcpy.Exists(fc):
        arcpy.management.Delete(fc)
    arcpy.management.CreateFeatureclass(OUT_GDB, name, "POLYGON", spatial_reference=sr)
    flds = [("Classcode", "TEXT", 8), ("Classname", "TEXT", 24), ("Classvalue", "LONG", None), ("RED", "LONG", None),
            ("GREEN", "LONG", None), ("BLUE", "LONG", None), ("Subtype", "TEXT", 24), ("ProposalOID", "LONG", None),
            ("OldOID", "LONG", None), ("MappedBy", "TEXT", 40)]
    if extra:
        flds += [("Split", "TEXT", 8), ("Block", "TEXT", 16)]
    for n, t, ln in flds:
        arcpy.management.AddField(fc, n, t, field_length=ln)
    names = ["SHAPE@"] + [n for n, _, _ in flds]
    with arcpy.da.InsertCursor(fc, names) as cur:
        for r in rows:
            nm, (cr, cg, cb) = CLASSES[r["cls"]]
            vals = [r[geom_key], " ", nm, r["cls"], cr, cg, cb, r["sub"], r["pid"], r["old"], MARKER]
            if extra:
                vals += [r["split"], r["block"]]
            cur.insertRow(vals)
    n = int(arcpy.management.GetCount(fc)[0])
    assert n == len(rows), "%s: wrote %d rows, expected %d" % (name, n, len(rows))
    print("   %-40s %4d rows" % (name, n))


def main():
    t0 = time.time()
    if not DRY and OUT_GDB == DRIVE_GDB:
        assert not any("ArcGISPro" in l for l in os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"
    sr = arcpy.Describe(os.path.join(GDB, LABELS)).spatialReference
    with arcpy.da.SearchCursor(os.path.join(GDB, TEST4), ["Block"]) as c:
        held = sorted(set(r[0] for r in c))
    with arcpy.da.SearchCursor(os.path.join(GDB, EXTENT), ["SHAPE@"]) as c:
        ext = next(c)[0].projectAs(sr)
    rows, tally = final_labels()
    print("review tally (action, review):")
    for (a, r), n in sorted(tally.items()):
        print("   %-8s %-7s %4d" % (a, r, n))
    pending = sum(n for (a, r), n in tally.items() if a != "keep" and r == "(none)")
    print("non-keep rows not reviewed: %d (they enter as they were, or not at all if new)" % pending)
    split(rows, held, ext)
    clash, cross = overlaps(rows)
    per = collections.defaultdict(lambda: dict(train=0, test=0, tb=set(), xb=set()))
    for r in rows:
        if r["split"] == "train":
            per[r["cls"]]["train"] += 1; per[r["cls"]]["tb"].add(r["block"])
        elif r["split"] == "test":
            per[r["cls"]]["test"] += 1; per[r["cls"]]["xb"].add(r["block"])
    short = []
    print("classes (minimum: %d held out in %d blocks, %d training in %d):" % (MIN_TEST, MIN_TEST_BLOCKS, MIN_TRAIN, MIN_TRAIN_BLOCKS))
    for c in sorted(per):
        d = per[c]
        ok = d["test"] >= MIN_TEST and len(d["xb"]) >= MIN_TEST_BLOCKS and d["train"] >= MIN_TRAIN and len(d["tb"]) >= MIN_TRAIN_BLOCKS
        if not ok and c > 4:
            short.append(c)
        print("   %d %-18s train %4d in %2d blocks, held out %4d in %2d blocks  %s" % (
            c, CLASSES[c][0], d["train"], len(d["tb"]), d["test"], len(d["xb"]), "ok" if ok else "SHORT"))
    print("overlaps between classes: %d %s" % (len(clash), clash[:10]))
    print("overlaps across the split: %d %s" % (len(cross), cross[:10]))
    log = dict(made=time.strftime("%Y-%m-%d %H:%M"), tally={"%s %s" % k: v for k, v in tally.items()},
               pending=pending, held_out_blocks=held, class_overlaps=clash, split_overlaps=cross,
               classes={CLASSES[c][0]: dict(train=d["train"], test=d["test"], train_blocks=sorted(d["tb"]),
                                            test_blocks=sorted(d["xb"])) for c, d in per.items()},
               short=[CLASSES[c][0] for c in short], keep_short="--keep-short" in sys.argv)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    json.dump(log, open(LOG, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if clash or cross:
        sys.exit("NOT WRITTEN: labels overlap across classes or across the split; fix the outlines in the proposals")
    if DRY:
        print("dry run: nothing written (%.0f s)" % (time.time() - t0))
        return
    drop = set() if "--keep-short" in sys.argv else set(short)
    if drop:
        print("left out of the split, short of the minimum:", [CLASSES[c][0] for c in sorted(drop)])
    write(V2, rows, sr, "geom")
    inside = [r for r in rows if r["split"] and r["cls"] not in drop]
    write(TRAIN, [r for r in inside if r["split"] == "train"], sr, "g60", extra=True)
    write(TEST, [r for r in inside if r["split"] == "test"], sr, "g60", extra=True)
    print("done in %.0f s; log %s" % (time.time() - t0, LOG))


if __name__ == "__main__":
    main()
