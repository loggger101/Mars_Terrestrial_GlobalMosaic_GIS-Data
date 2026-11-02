# -*- coding: utf-8 -*-
r"""Write the author's answers from the review contact sheets into the gdb (KB §69.51).

    python apply_sheet_review.py <sheet folder> <answers.txt>                       # dry run: what would be written
    python apply_sheet_review.py <sheet folder> <answers.txt> --apply --by "<name>"  # back up the class, then write

<sheet folder> is one make_review_chips.py wrote (its index.json says which class, row and field each slot is).
<answers.txt> is free text: a slot then a letter, in any layout ("A1 a, A2 r", "A1a A2r", one per line, "A1=a").

  candidate sheets (field Review):  a accept, r reject, u unsure            -> Review; ReviewNote "sheets <date>, <by>"
  copy sheets      (field Origin):  f fluvial, v volcanic, i indeterminate  -> Origin on the Landform_ChannelCenterlines copy;
                                                                               Notes begins "Origin <date>, <by>; "

Partial answers are fine: slots not answered are left as they are. Refused, with nothing written: a slot not on the
sheets, a letter that is not one of the field's, one slot given two different letters, and a row whose field already
holds a different value (a decision is never overwritten; change it in Pro). Answers equal to the stored value are
skipped. The one exception (KB §69.55): a decision the agent wrote (--by "agent ...", stamped in ReviewNote or Notes)
is open to anyone else's answer, which replaces it and its stamp, or restamps it when the two agree; the agent never
replaces a decision, its own or the author's. With --apply the class is first copied to <drive>\Mars Project\.backups\sheets_<time>.gdb. A log of every
slot goes to logs\sheet_review_<folder>_<time>.json. --gdb <path> points the script at a scratch copy (for tests).
ArcGIS Python.
"""
import os, sys, re, json, time, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import GDB, on_drive

CODES = {"Review": {"a": "accept", "r": "reject", "u": "unsure"},
         "Origin": {"f": "fluvial", "v": "volcanic", "i": "indeterminate"}}
NOTE = {"Review": "ReviewNote", "Origin": "Notes"}      # where each write says who made it


def is_agent(by):
    return by.lower().startswith("agent")


def agent_wrote(field, note):
    """True when the stored decision was written by the agent ("sheets <date>, agent ..." in ReviewNote, "Origin
    <date>, agent ...; " leading Notes): the author's answer may replace it (KB §69.55)."""
    head = note.split("; ", 1)[0] if field == "Origin" else note
    if not head.startswith("sheets " if field == "Review" else "Origin "):
        return False
    return ", " in head and is_agent(head.split(", ", 1)[1])


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def parse(text, slots, codes):
    """{slot: value} from free text; raises ValueError on any unknown slot, bad letter or conflict."""
    out, errors = {}, []
    words = {w: v for c, v in codes.items() for w in (c, v)}
    for slot, word in re.findall(r"\b([A-Z]+\d+)\s*[=:\-]?\s*([A-Za-z]+)\b", text):
        word = word.lower()
        if slot not in slots:
            errors.append("%s is not on these sheets" % slot)
        elif word not in words:
            errors.append("%s: '%s' is not one of %s" % (slot, word, ", ".join(sorted(codes))))
        elif slot in out and out[slot] != words[word]:
            errors.append("%s given both %s and %s" % (slot, out[slot], words[word]))
        else:
            out[slot] = words[word]
    if errors:
        raise ValueError("; ".join(errors))
    return out


def main():
    folder, answers = sys.argv[1], sys.argv[2]
    apply, by = "--apply" in sys.argv, arg("--by")
    if apply and not by:
        sys.exit('--apply needs --by "<reviewer name>"')
    gdb = arg("--gdb", GDB)
    idx = json.load(open(os.path.join(folder, "index.json"), encoding="utf-8"))
    field = "Origin" if idx.get("copies") else "Review"
    slots = idx["slots"]
    classes = {v["class"] for v in slots.values()}
    assert len(classes) == 1, "one class per sheet folder, found %s" % classes
    fc = os.path.join(gdb, classes.pop())
    try:
        given = parse(open(answers, encoding="utf-8").read(), slots, CODES[field])
    except ValueError as e:
        sys.exit("refused, nothing written: %s" % e)
    by_oid = {slots[s]["oid"]: (s, v) for s, v in given.items()}
    nf = NOTE[field]
    stored, notes = {}, {}
    with arcpy.da.SearchCursor(fc, ["OID@", field, nf]) as cur:
        for oid, val, n in cur:
            if oid in by_oid:
                stored[oid], notes[oid] = val, n or ""
    missing = sorted(set(by_oid) - set(stored))
    if missing:
        sys.exit("refused, nothing written: rows not in %s: %s" % (fc, missing))
    blank = (None, "") if field == "Review" else (None, "", "indeterminate")
    mine = by is not None and is_agent(by)
    open_ = {oid for oid in by_oid if stored[oid] in blank or (not mine and agent_wrote(field, notes[oid]))}
    clash = ["%s (row %d) holds %s, answer %s" % (s, oid, stored[oid], v)
             for oid, (s, v) in by_oid.items() if oid not in open_ and stored[oid] != v]
    if clash:
        sys.exit("refused, nothing written: %s" % "; ".join(clash))
    note = "%s %s, %s" % ("sheets" if field == "Review" else "Origin", datetime.date.today().isoformat(), by or "")
    # Review: the rows whose value changes. Origin: also every answered row not yet stamped with who read it, since
    # "indeterminate" is the copies' default and an answer equal to it would otherwise leave no trace.
    todo = {oid: (s, v) for oid, (s, v) in by_oid.items()
            if stored[oid] != v or (field == "Origin" and not notes[oid].startswith(note))
            or (not mine and agent_wrote(field, notes[oid]))}
    tally = {}
    for s, v in todo.values():
        tally[v] = tally.get(v, 0) + 1
    print("%s: %d slots, %d answered, %d to write %s, %d already so" %
          (os.path.basename(fc), len(slots), len(given), len(todo), tally, len(given) - len(todo)))
    log = {"folder": folder, "answers": answers, "field": field, "class": fc, "apply": apply, "by": by,
           "rows": [{"slot": s, "oid": oid, "was": stored[oid], "now": v} for oid, (s, v) in sorted(todo.items())]}
    if apply and todo:
        bak_dir = on_drive(r"Mars Project\.backups") if "--gdb" not in sys.argv else os.path.dirname(gdb)
        bak = "sheets_%s.gdb" % time.strftime("%Y%m%d-%H%M%S")
        arcpy.management.CreateFileGDB(bak_dir, bak)
        arcpy.conversion.FeatureClassToFeatureClass(fc, os.path.join(bak_dir, bak), os.path.basename(fc))
        print("backed up to", os.path.join(bak_dir, bak))
        with arcpy.da.UpdateCursor(fc, ["OID@", field, nf]) as cur:
            for row in cur:
                if row[0] in todo:
                    row[1] = todo[row[0]][1]
                    if field == "Review":
                        row[2] = note[:60]
                    else:                                        # stamp first, the earlier stamp replaced
                        rest = (row[2] or "").split("; ", 1)[1] if (row[2] or "").startswith("Origin ") else (row[2] or "")
                        row[2] = ("%s; %s" % (note, rest) if rest else note)[:255]
                    cur.updateRow(row)
        print("written:", len(todo))
    elif not apply:
        print('Dry run, nothing written. Write with: --apply --by "<reviewer name>"')
    if "--gdb" not in sys.argv:
        out = os.path.join(HERE, "logs", "sheet_review_%s_%s.json" % (os.path.basename(os.path.normpath(folder)),
                                                                      time.strftime("%Y%m%d-%H%M%S")))
        json.dump(log, open(out, "w", encoding="utf-8"), indent=1)
        print("log", out)


if __name__ == "__main__":
    main()
