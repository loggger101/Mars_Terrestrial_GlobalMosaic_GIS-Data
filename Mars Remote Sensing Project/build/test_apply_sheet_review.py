# -*- coding: utf-8 -*-
r"""Rehearses apply_sheet_review.py's rules for agent and author decisions on a scratch gdb (KB §69.55): the agent
writes open rows, stamped; never changes a decision, its own or the author's; the author's answer replaces or restamps
the agent's, Review and Origin alike. Nothing on the drive is written.

    "<ArcGIS Pro Python>" test_apply_sheet_review.py [<script under test>]    every check must PASS
"""
import os, sys, json, subprocess, shutil, tempfile
sys.path.insert(0, r"Z:\Mars Remote Sensing Project\build")
import arcpy
from paths import GDB

PY = sys.executable
SCRIPT = sys.argv[1] if len(sys.argv) > 1 else r"Z:\Mars Remote Sensing Project\build\apply_sheet_review.py"
SHEETS = r"Z:\Mars Project\review_sheets"
tmp = tempfile.mkdtemp(prefix="r55_")
g = os.path.join(tmp, "t.gdb")
arcpy.management.CreateFileGDB(tmp, "t.gdb")
for c in ("Landform_ChannelCandidates_auto_ath", "Landform_ChannelCenterlines"):
    arcpy.conversion.FeatureClassToFeatureClass(os.path.join(GDB, c), g, c)

open_idx = json.load(open(os.path.join(SHEETS, "ctx_1_athabasca_channels_open", "index.json"), encoding="utf-8"))
ori_idx = json.load(open(os.path.join(SHEETS, "ctx_3_origin_ius", "index.json"), encoding="utf-8"))
cal_idx = json.load(open(os.path.join(SHEETS, "ctx_0_calibration", "index.json"), encoding="utf-8"))


def run(folder, text, by=None):
    a = os.path.join(tmp, "a.txt")
    open(a, "w", encoding="utf-8").write(text)
    cmd = [PY, SCRIPT, os.path.join(SHEETS, folder), a, "--gdb", g] + (["--apply", "--by", by] if by else [])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def val(cls, field, oid):
    with arcpy.da.SearchCursor(os.path.join(g, cls), [field, "ReviewNote" if field == "Review" else "Notes"],
                               "OBJECTID = %d" % oid) as cur:
        return next(cur)


C, L = "Landform_ChannelCandidates_auto_ath", "Landform_ChannelCenterlines"
s0, s1 = "A1", "A2"
o0, o1 = open_idx["slots"][s0]["oid"], open_idx["slots"][s1]["oid"]
cal = next(s for s, v in cal_idx["slots"].items() if val(C, "Review", v["oid"])[0] in ("accept", "reject"))
ocal = cal_idx["slots"][cal]["oid"]
author_val = val(C, "Review", ocal)[0]
other = "r" if author_val == "accept" else "a"
os0 = ori_idx["slots"]["A1"]["oid"]
checks = []

rc, out = run("ctx_1_athabasca_channels_open", "%s r, %s a" % (s0, s1), "agent CTX (KB 69.55)")
checks.append(("agent writes open rows, stamped", rc == 0 and val(C, "Review", o0) [0] == "reject"
               and val(C, "Review", o0)[1].endswith("agent CTX (KB 69.55)")))
rc, out = run("ctx_1_athabasca_channels_open", "%s a" % s0, "agent CTX (KB 69.55)")
checks.append(("agent cannot change its own decision", rc != 0 and "refused" in out and val(C, "Review", o0)[0] == "reject"))
rc, out = run("ctx_1_athabasca_channels_open", "%s a, %s a" % (s0, s1), "Logan M Edwards")
checks.append(("author replaces an agent decision", rc == 0 and val(C, "Review", o0)[0] == "accept"
               and val(C, "Review", o0)[1].endswith("Logan M Edwards")))
checks.append(("author agreeing restamps it", val(C, "Review", o1)[1].endswith("Logan M Edwards")))
rc, out = run("ctx_1_athabasca_channels_open", "%s r" % s0, "Someone Else")
checks.append(("an author decision is never replaced", rc != 0 and val(C, "Review", o0)[0] == "accept"))
rc, out = run("ctx_0_calibration", "%s %s" % (cal, other), "agent CTX (KB 69.55)")
checks.append(("agent cannot replace the author's own review", rc != 0 and val(C, "Review", ocal)[0] == author_val))

rc, out = run("ctx_3_origin_ius", "A1 i", "agent CTX (KB 69.55)")
o, n = val(L, "Origin", os0)
checks.append(("agent 'indeterminate' on the default is stamped", rc == 0 and o == "indeterminate"
               and n.startswith("Origin ") and "agent CTX (KB 69.55); " in n))
rc, out = run("ctx_3_origin_ius", "A1 v", "Logan M Edwards")
o, n2 = val(L, "Origin", os0)
checks.append(("author replaces the agent's Origin, stamp replaced, old notes kept",
               rc == 0 and o == "volcanic" and n2.startswith("Origin ") and "Logan M Edwards; " in n2
               and "agent" not in n2 and n2.split("; ", 1)[1] == n.split("; ", 1)[1]))
rc, out = run("ctx_3_origin_ius", "A1 f", "agent CTX (KB 69.55)")
checks.append(("agent cannot replace the author's Origin", rc != 0 and val(L, "Origin", os0)[0] == "volcanic"))
for name, ok in checks:
    print("PASS" if ok else "FAIL", name)
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(0 if all(ok for _, ok in checks) else 1)
