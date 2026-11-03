# -*- coding: utf-8 -*-
r"""Preflight for run_v3.ps1 on any machine, before the desktop spends ~2 days on it (KB §69.60). Reads only.

run_v2.ps1 was rehearsed end to end (v2p, KB §69.4); run_v3.ps1 never ran. This checks what can be checked without
running a step:

  labels   Landform_TrainingSamples_v3_60_train / _test exist, hold 10,269 / 1,652 polygons, all written by
           propose_v3_labels.py (labelsets.WRITER, the guard of make_global60_classification.py), codes 1-7; the
           held-out blocks are v2's 14, and no training polygon lies in one.
  steps    each of run_v3.ps1's 20 steps, parsed from the file: its script exists, every flag it passes is one the
           script knows (or labelsets.py, make_dl_model.py or make_global60_classification.py, which it imports and
           which read its argv), and the script loads with that argv (a fresh process per step, --probe), its labels
           resolving to the set the step names.
  names    the chain between steps: the U-Net mosaic's final path is the raster steps 06 and 07 score; the SVM's
           output is the mode filter's source, the filter's output the raster steps 11, 12 and 14 read; the model
           folder and name are what run_v3.ps1's Emd function looks for.
  files    inputs that no step makes (the stack, the v2 maps of steps 08 and 13) exist; outputs (every "_v3" file,
           each scorer's log) do not, so no step refuses and no earlier result is overwritten.

Paths: run_v3.ps1 names the desktop's F: drive; they are read here on this machine's drive (paths.DRIVE), and the
desktop's internal-disk paths (C:\MarsScratch) are compared, not checked for existence.

  "<ArcGIS Pro Python>" preflight_v3.py [--plant]
--plant changes step 11's raster to a name no step makes; the names check must then fail (exit 1).
"""
import os, sys, re, json, subprocess, importlib.util
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
QUEUE = os.path.join(HERE, "run_v3.ps1")
EXPECT = {"train": 10269, "test": 1652}                    # KB §69.56
FLAG_SOURCES = ("labelsets.py", "make_dl_model.py", "make_global60_classification.py")   # imported; they read the argv too


def probe(script, args):
    """In a fresh process: load <script> with this argv (its main() is not run) and report its names."""
    sys.argv = [script] + args
    spec = importlib.util.spec_from_file_location("probed", os.path.join(HERE, script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import labelsets as L, grid60 as G
    names = {k: v for k, v in vars(mod).items() if isinstance(v, str) and k.isupper()}
    print("PROBE " + json.dumps(dict(names=names, tag=L.TAG, writer=L.WRITER, train=L.TRAIN, test=L.TEST,
                                     outdir=G.OUTDIR)))


def parse_queue(plant):
    text = open(QUEUE, encoding="utf-8").read()
    g60 = re.search(r'^\$g60 = "([^"]+)"', text, re.M).group(1)
    emd_dir = re.search(r'Get-ChildItem "([^"]+)" -Recurse -Filter "([^"]+)"', text)
    steps = []
    for m in re.finditer(r'@\("(\d\d[a-z]?_\w+)", \{ @\((.*?)\)( \+ @\(.*?\))? \}\)', text):
        args = []
        for q, emd in re.findall(r'"([^"]*)"|\((Emd)\)', m.group(2)):
            args.append("<emd>" if emd else q.replace("$g60", g60))
        steps.append(dict(name=m.group(1), script=args[0], args=args[1:], extra=bool(m.group(3))))
    if plant:
        for s in steps:
            if s["name"].startswith("11_"):
                i = s["args"].index("--raster") + 1
                s["args"][i] = s["args"][i].replace("_mode11", "_mode13")
    return g60, emd_dir.group(1), emd_dir.group(2), steps


def local(p, desktop_root):
    """A desktop path read on this machine: its drive letter swapped for paths.DRIVE."""
    from paths import DRIVE
    if p.lower().startswith(desktop_root.lower()):
        p = os.path.join(DRIVE, p[len(desktop_root):])
    return os.path.normcase(os.path.normpath(p))


def main():
    plant = "--plant" in sys.argv
    import arcpy
    from paths import DRIVE
    import labelsets
    gdb = os.path.join(DRIVE, "Mars Project", "Mars Project.gdb")
    fails, oks = [], []
    def check(ok, what, detail=""):
        (oks if ok else fails).append(what)
        print("  %-4s %s%s" % ("ok" if ok else "FAIL", what, ("  " + detail) if detail else ""))

    print("labels")
    rows = {}
    for half in ("train", "test"):
        fc = os.path.join(gdb, "Landform_TrainingSamples_v3_60_%s" % half)
        if not arcpy.Exists(fc):
            check(False, "%s exists" % os.path.basename(fc)); continue
        with arcpy.da.SearchCursor(fc, ["MappedBy", "Classvalue", "Block"]) as c:
            rows[half] = list(c)
        n = len(rows[half])
        check(n == EXPECT[half], "v3 %s: %d polygons" % (half, n), "expected %d" % EXPECT[half])
        bad = [r for r in rows[half] if r[0] != "propose_v3_labels.py" or r[1] not in range(1, 8)]
        check(not bad, "v3 %s: every row propose_v3_labels.py's, codes 1-7" % half, "%d not" % len(bad) if bad else "")
    with arcpy.da.SearchCursor(os.path.join(gdb, "Landform_TrainingSamples_v2_60_test"), ["Block"]) as c:
        v2blocks = {r[0] for r in c}
    if "test" in rows and "train" in rows:
        tb = {r[2] for r in rows["test"]}
        check(tb == v2blocks, "v3 held-out blocks are v2's %d" % len(v2blocks), "v3 has %d" % len(tb))
        leak = [r for r in rows["train"] if r[2] in tb]
        check(not leak, "no v3 training polygon in a held-out block", "%d do" % len(leak) if leak else "")

    g60, emd_dir, emd_glob, steps = parse_queue(plant)
    root = g60[:3]                                            # "F:\"
    print("steps (%d parsed from run_v3.ps1)" % len(steps))
    check(len(steps) == 20, "20 steps parsed (01-08 with 03a-d and 04a-d, then 09-14)", "%d" % len(steps))
    flagsrc = "".join(open(os.path.join(HERE, f), encoding="utf-8").read() for f in FLAG_SOURCES)
    P = {}
    for s in steps:
        path = os.path.join(HERE, s["script"])
        if not os.path.exists(path):
            check(False, "%s: %s exists" % (s["name"], s["script"])); continue
        src = open(path, encoding="utf-8").read() + flagsrc
        unknown = [a for a in s["args"] if a.startswith("--") and '"%s"' % a not in src]
        if s["extra"] and '"--classify-only"' not in src:
            unknown.append("--classify-only")
        check(not unknown, "%s: every flag known to %s" % (s["name"], s["script"]), str(unknown) if unknown else "")
        args = [a if a != "<emd>" else os.path.join(emd_dir, "probe.emd") for a in s["args"]]
        r = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "--probe", s["script"]] + args,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600, cwd=HERE)
        line = [l for l in r.stdout.splitlines() if l.startswith("PROBE ")]
        if r.returncode or not line:
            check(False, "%s: %s loads with its argv" % (s["name"], s["script"]), (r.stderr or r.stdout).strip()[-300:])
            continue
        P[s["name"]] = d = json.loads(line[0][6:])
        want = "_" + s["args"][s["args"].index("--labels") + 1]
        check(d["tag"] == want, "%s: loads, labels %s" % (s["name"], d["tag"]), "expected %s" % want)

    print("names")
    S = {s["name"][:2]: s for s in steps}
    def raster(k):
        a = S[k]["args"]
        return a[a.index("--raster") + 1]
    if all(k in P for k in ("01_unet_export", "05_unet_mosaic")):
        d = P["05_unet_mosaic"]
        final = os.path.join(d["outdir"], d["names"]["UNET_SEAMFIX"])
        for k in ("06", "07"):
            check(local(raster(k), root) == local(final, root), "step %s scores the mosaic step 05 writes" % k,
                  "%s vs %s" % (raster(k), final))
        work = P["01_unet_export"]["names"]["WORK"]
        check(os.path.normcase(os.path.join(work, "models")) == os.path.normcase(emd_dir),
              "the U-Net trains in %s, where Emd looks" % emd_dir, work)
        check(emd_glob.startswith("global60_unet_x5c_v3_"), "Emd's filter %s is the model name make_dl_pixels.py gives" % emd_glob)
    s09 = [n for n in P if n.startswith("09")]
    s10 = [n for n in P if n.startswith("10")]
    if s09 and s10:
        out9, src10, dst10 = P[s09[0]]["names"]["OUT"], P[s10[0]]["names"]["SRC"], P[s10[0]]["names"]["DST"]
        check(local(out9, root) == local(src10, root), "step 10 filters the map step 09 writes", "%s vs %s" % (out9, src10))
        for k in ("11", "12"):
            check(local(raster(k), root) == local(dst10, root), "step %s scores the map step 10 writes" % k,
                  "%s vs %s" % (raster(k), dst10))
        cls14 = [P[n]["names"]["CLS"] for n in P if n.startswith("14")]
        if cls14:
            check(local(cls14[0], root) == local(dst10, root), "step 14 reads the map step 10 writes",
                  "%s vs %s" % (cls14[0], dst10))

    print("files")
    made = set()
    for n in P:
        nm = P[n]["names"]
        if n.startswith("05"):
            made.add(local(os.path.join(P[n]["outdir"], nm["UNET_SEAMFIX"]), root))
        if n.startswith("09"):
            made |= {local(nm["OUT"], root), local(nm["ECD"], root)}
        if n.startswith("10"):
            made.add(local(nm["DST"], root))
    for f in sorted(made):
        check(not os.path.exists(f), "not made yet: %s" % os.path.basename(f))
    stack = [P[n]["names"].get("STACK") for n in P if P[n]["names"].get("STACK")]
    if stack:
        check(os.path.exists(local(stack[0], root)), "the stack exists: %s" % os.path.basename(stack[0]))
    logs = set()
    for s in steps:
        if "--raster" not in s["args"] or s["name"] not in P:
            continue
        r = local(raster(s["name"][:2]), root)
        if r not in made:
            check(os.path.exists(r), "%s: its raster exists (no step makes it): %s" % (s["name"], os.path.basename(r)))
        out = P[s["name"]]["names"]["OUT"]
        check(out not in logs and not os.path.exists(out), "%s: its log is new: %s" % (s["name"], os.path.basename(out)))
        logs.add(out)
    for n in P:
        if n.startswith("14"):
            out = P[n]["names"]["OUT"]
            check(not os.path.exists(out), "%s: its log is new: %s" % (n, os.path.basename(out)))

    print("\n%d checks, %d failed%s" % (len(oks) + len(fails), len(fails), " (planted)" if plant else ""))
    for f in fails:
        print("  FAILED: " + f)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if "--probe" in sys.argv:
        i = sys.argv.index("--probe")
        probe(sys.argv[i + 1], sys.argv[i + 2:])
    else:
        main()
