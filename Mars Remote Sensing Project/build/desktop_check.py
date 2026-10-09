# -*- coding: utf-8 -*-
r"""Desktop-day preflight: X0, X1 and X5's preconditions in one run (NEXT-STEPS §5; KB §2.3, §11 q10, §51).

    <ArcGIS python.exe> desktop_check.py          X0 + X5 preflight (seconds)
    <ArcGIS python.exe> desktop_check.py --gpu    also X1: Slope on the Ius DEM, CPU_ONLY then GPU_THEN_CPU

X0  the two no-space junctions (TypeArea, Global60) resolve on this drive; paths.junction() prints
    the mklink command for any that does not.
X1  q10: does GPU_THEN_CPU engage? The same Slope on the 37 Mpx Ius DEM twice, timed, output to the
    internal disk. Engaged = the GP messages no longer say "No compatible GPU device has been detected"
    (the laptop's answer in 2026-09, §7). Timings are wall clock: check the machine did not sleep.
X5  deep learning needs ArcGIS Pro's separately installed "Deep Learning Libraries" (torch, fastai,
    torchvision in the Pro environment); on the laptop on 2026-10-09 none were present. Also checks
    CUDA from torch, and that the training-split export (make_global60_dl_export.py --train-only)
    is intact: its marker names the _60_train labels and its chip count matches stats.txt.

Writes build\logs\desktop_check_<hostname>.json. Writes nothing on the drive besides that log.
"""
import os, sys, json, time, socket, tempfile, importlib, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import on_drive, DRIVE
import arcpy

HOST = socket.gethostname()
OUT = os.path.join(HERE, "logs", "desktop_check_%s.json" % HOST)
TRAIN = on_drive(r"Mars Project\LabeledObjects\global60_svm_stack_200m_train")
NO_GPU = "No compatible GPU device has been detected"
res = {"host": HOST, "drive": DRIVE, "when": time.strftime("%Y-%m-%d %H:%M"), "pro": arcpy.GetInstallInfo()["Version"]}


def say(k, ok, detail=""):
    print("%-4s %-34s %s" % ("ok" if ok else "--", k, detail), flush=True)


# X0: junctions
res["junctions"] = {}
for name in ("TypeArea", "Global60"):
    alias, target = on_drive(name), on_drive(os.path.join("Mars Project", name))
    ok = os.path.isdir(alias) and os.path.samefile(alias, target)
    res["junctions"][name] = ok
    say("X0 junction " + name, ok, alias if ok else 'fix: rmdir "%s" then mklink /J "%s" "%s"' % (
        alias.rstrip("\\"), alias.rstrip("\\"), target))

# X5 preflight: libraries, CUDA, the export
res["dl_libraries"] = {}
for m in ("torch", "torchvision", "fastai", "arcgis.learn"):
    try:
        importlib.import_module(m); res["dl_libraries"][m] = "ok"
    except Exception as e:
        res["dl_libraries"][m] = "%s: %s" % (type(e).__name__, str(e)[:80])
    say("X5 import " + m, res["dl_libraries"][m] == "ok", "" if res["dl_libraries"][m] == "ok" else res["dl_libraries"][m])
try:
    import torch
    res["cuda"] = {"available": torch.cuda.is_available(),
                   "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
except Exception:
    res["cuda"] = {"available": False, "device": None, "note": "torch not importable"}
say("X5 CUDA", res["cuda"]["available"], str(res["cuda"].get("device") or res["cuda"].get("note", "")))
marker = os.path.join(TRAIN, "MADE_BY_make_global60_dl_export.txt")
stats = os.path.join(TRAIN, "stats.txt")
exp = {"exists": os.path.isdir(TRAIN)}
if exp["exists"]:
    exp["labels_train_only"] = os.path.exists(marker) and "_60_train" in open(marker).read()
    m = re.search(r"images = (\d+)", open(stats).read()) if os.path.exists(stats) else None
    exp["chips_stats"] = int(m.group(1)) if m else None
    exp["chips_found"] = len([f for f in os.listdir(os.path.join(TRAIN, "images")) if f.lower().endswith(".tif")])
    exp["intact"] = exp["labels_train_only"] and exp["chips_stats"] == exp["chips_found"]
res["train_export"] = exp
say("X5 training-split export", exp.get("intact", False),
    "%s chips, labels %s" % (exp.get("chips_found"), "training split" if exp.get("labels_train_only") else "NOT the training split"))
res["x5_ready"] = all(v == "ok" for v in res["dl_libraries"].values()) and res["cuda"]["available"] and exp.get("intact", False)

# X1: the GPU test
if "--gpu" in sys.argv:
    # The tool form, not arcpy.sa.Slope: map algebra returns NO messages, so the absence of the
    # no-GPU line would prove nothing (found 2026-10-09: the first version called the laptop's
    # integrated graphics "engaged"). arcpy.ddd.Slope returns a Result that carries them.
    arcpy.CheckOutExtension("3D")
    dem = os.path.join(on_drive("TypeArea"), "ius_dem.tif")
    tmp = tempfile.mkdtemp(prefix="x1_gpu_")
    res["x1"] = {}
    for dev in ("CPU_ONLY", "GPU_THEN_CPU"):
        t = time.time()
        r = arcpy.ddd.Slope(dem, os.path.join(tmp, "slope_%s.tif" % dev.lower()), "DEGREE", 1, "PLANAR", "METER", dev)
        msgs = r.getMessages()
        res["x1"][dev] = {"seconds": round(time.time() - t, 1), "no_gpu_message": NO_GPU in msgs,
                          "messages": msgs.splitlines()[:6]}
        say("X1 Slope " + dev, bool(msgs), "%.1f s%s" % (res["x1"][dev]["seconds"],
            "; says no compatible GPU" if res["x1"][dev]["no_gpu_message"] else ""))
    g = res["x1"]["GPU_THEN_CPU"]
    res["x1"]["gpu_engaged"] = bool(g["messages"]) and not g["no_gpu_message"]
    res["x1"]["output_folder"] = tmp
    say("X1 GPU engaged", res["x1"]["gpu_engaged"])

json.dump(res, open(OUT, "w"), indent=1)
print("X5 ready to train: %s\nwrote %s" % (res["x5_ready"], OUT))
