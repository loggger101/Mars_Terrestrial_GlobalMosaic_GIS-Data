# -*- coding: utf-8 -*-
r"""Writes docs\environment.md in the GitHub repo: what each machine runs, read from the machine itself (NEXT-STEPS §13 P8).

    python github_environment.py        (the system Python; it asks the ArcGIS Python for its own versions)

One section per machine, headed by its host name; a run replaces its own machine's section and keeps the others', so
a run on each machine gives both. Read, not typed: the OS, CPU, memory, GPU and driver from Windows (and nvidia-smi
where present); ArcGIS Pro's version, licensed extensions and packages from the ArcGIS Python; the system Python's
packages that the build scripts import; MiKTeX and the AASTeX class from the TeX on the path. Also writes
docs\requirements-system.txt, those system packages pinned at the versions of the machine that ran last. --repo as in
github_sync.py. Reads only; seconds.
"""
import os, sys, json, platform, re, shutil, subprocess, time
from importlib import metadata
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import arcgis_python

REPO = Path(sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else
            Path.home() / "OneDrive" / "Documents" / "GitHub" / "Mars_Terrestrial_GlobalMosaic_GIS-Data")
SYSTEM_PKGS = ["numpy", "matplotlib", "Pillow", "python-pptx", "python-docx", "PyMuPDF"]
ARCGIS_PKGS = ["numpy", "scipy", "matplotlib", "Pillow", "GDAL", "arcgis", "torch", "torchvision", "fastai"]
CLASS = "aastex701"                     # the paper's \documentclass (NEXT STUFF\Final\paper\mars_global_mosaic.tex)

# Run inside the ArcGIS Python: its own versions, as JSON on stdout
ARCGIS_PROBE = r"""
import json, sys, glob, os
from importlib import metadata
out = {"python": sys.version.split()[0], "executable": sys.executable}
import arcpy
info = arcpy.GetInstallInfo()
out["pro"] = "%s %s (build %s)" % (info.get("ProductName"), info.get("Version"), info.get("BuildNumber"))
out["extensions"] = {e: arcpy.CheckExtension(e) for e in ("3D", "Spatial", "ImageAnalyst")}
pk = {}
for p in PKGS:
    try:
        pk[p] = metadata.version(p)
    except metadata.PackageNotFoundError:
        pk[p] = None
if pk.get("GDAL") is None:
    from osgeo import gdal
    pk["GDAL"] = gdal.__version__
out["packages"] = pk
meta = os.path.join(sys.prefix, "conda-meta")
dl = sorted(glob.glob(os.path.join(meta, "deep-learning-essentials-*.json")))
out["deep_learning_essentials"] = json.load(open(dl[-1]))["version"] if dl else None
if pk.get("torch"):
    import torch
    out["cuda"] = torch.version.cuda if torch.cuda.is_available() else "not available to torch"
print("JSON" + json.dumps(out))
"""


def run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL,
                           encoding="utf-8", errors="replace")
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def ps(expr):
    return run(["powershell", "-NoProfile", "-Command", expr])


def machine():
    m = {"OS": "%s %s (build %s)" % (platform.system(), platform.release(), platform.version())}
    m["CPU"] = ps("(Get-CimInstance Win32_Processor | Select-Object -First 1).Name") or platform.processor()
    ram = ps("(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory")
    m["Memory"] = "%.1f GB" % (int(ram) / 1e9) if ram and ram.isdigit() else "unknown"
    smi = run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]) \
        if shutil.which("nvidia-smi") else None
    if smi:
        m["GPU"] = "; ".join("%s, driver %s, %s" % tuple(x.strip() for x in line.split(",")[:3])
                             for line in smi.splitlines())
    else:
        vc = ps("Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name + ', driver ' + $_.DriverVersion }")
        m["GPU"] = "; ".join(vc.splitlines()) if vc else "unknown"
    return m


def system_python():
    pk = {}
    for p in SYSTEM_PKGS:
        try:
            pk[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            pk[p] = None
    return {"python": platform.python_version(), "executable": sys.executable, "packages": pk}


def arcgis():
    exe = arcgis_python()
    if not os.path.exists(exe):
        return None
    out = run([exe, "-c", "PKGS = %r\n" % ARCGIS_PKGS + ARCGIS_PROBE], timeout=600)
    line = next((l for l in (out or "").splitlines() if l.startswith("JSON")), None)
    return json.loads(line[4:]) if line else {"error": "the probe failed: %s" % exe}


def tex():
    t = {}
    mik = run(["miktex", "--version"]) if shutil.which("miktex") else None
    pdf = run(["pdflatex", "--version"]) if shutil.which("pdflatex") else None
    t["TeX"] = (mik or pdf or "not on the path").splitlines()[0]
    cls = run(["kpsewhich", CLASS + ".cls"]) if shutil.which("kpsewhich") else None
    if cls and os.path.exists(cls):
        head = open(cls, encoding="utf-8", errors="replace").read(20000)
        m = re.search(r"\\ProvidesClass\{%s\}\s*\[([^\]]*)\]" % CLASS, head)
        t[CLASS + ".cls"] = m.group(1).strip() if m else "found, no \\ProvidesClass line"
    else:
        t[CLASS + ".cls"] = "not found by kpsewhich"
    return t


def fmt(v):
    return "`%s`" % v if v else "not installed"


def section(host, m, sp, ag, tx):
    rows = [("Written", time.strftime("%Y-%m-%d")), *m.items()]
    if ag is None:
        rows.append(("ArcGIS Pro", "not installed"))
    elif "error" in ag:
        rows.append(("ArcGIS Pro", ag["error"]))
    else:
        rows += [("ArcGIS Pro", ag["pro"]),
                 ("Licensed extensions", ", ".join("%s %s" % kv for kv in ag["extensions"].items())),
                 ("ArcGIS Python", "%s, `%s`" % (ag["python"], ag["executable"])),
                 ("ArcGIS Python packages", ", ".join("%s %s" % (k, fmt(v)) for k, v in ag["packages"].items())),
                 ("Deep Learning Libraries", fmt(ag["deep_learning_essentials"]) if ag["deep_learning_essentials"]
                  or not ag["packages"].get("torch") else "torch present; no deep-learning-essentials record")]
        if "cuda" in ag:
            rows.append(("CUDA (torch)", ag["cuda"]))
    rows += [("System Python", "%s, `%s`" % (sp["python"], sp["executable"])),
             ("System Python packages", ", ".join("%s %s" % (k, fmt(v)) for k, v in sp["packages"].items())),
             *tx.items()]
    body = ["## %s" % host, "", "| | |", "|---|---|"] + ["| %s | %s |" % (k, str(v).replace("|", "/")) for k, v in rows]
    return "<!-- machine: %s -->\n%s\n<!-- end: %s -->" % (host, "\n".join(body), host)


def main():
    host = platform.node()
    sp = system_python()
    new = section(host, machine(), sp, arcgis(), tex())
    path = REPO / "docs" / "environment.md"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    blocks = {m.group(1): m.group(0) for m in re.finditer(r"<!-- machine: (\S+) -->.*?<!-- end: \1 -->", old, re.S)}
    blocks[host] = new                                         # this machine's section replaced, the others kept
    head = ["# The software environment", "",
            "What each machine that built this project runs, read from the machine by "
            "`Mars Remote Sensing Project/build/github_environment.py`; a run replaces its own machine's section. "
            "Rasters and arcpy run on the ArcGIS Python, decks and reports on the system Python (KB §2.4); the "
            "U-Net and RetinaNet need the Deep Learning Libraries and a CUDA GPU. "
            "`requirements-system.txt` pins the system Python's packages as the last machine to run this had them. "
            "Generated; don't edit it here.", ""]
    text = "\n".join(head) + "\n" + "\n\n".join(blocks[h] for h in sorted(blocks)) + "\n"
    path.parent.mkdir(exist_ok=True)
    if text != old:
        path.write_text(text, encoding="utf-8", newline="\n")
    req = ["# The system Python's packages the build scripts import, as on %s (%s); see environment.md." % (
        host, time.strftime("%Y-%m-%d"))] + ["%s==%s" % (k, v) for k, v in sp["packages"].items() if v]
    (REPO / "docs" / "requirements-system.txt").write_text("\n".join(req) + "\n", encoding="utf-8", newline="\n")
    print(new)
    print("wrote", path, "(%d machine sections: %s)" % (len(blocks), ", ".join(sorted(blocks))))


if __name__ == "__main__":
    main()
