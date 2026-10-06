# -*- coding: utf-8 -*-
"""Match the THEMIS Night IR display stretch to the Day IR.

Added via addDataFromPath, the night layer took ArcGIS's default
PercentMinimumMaximum 0.5/0.5 while the day mosaic uses StandardDeviations n=5.
Flipping between the two to judge thermal response is then partly reading a
stretch artefact rather than the data - which matters, because that comparison
is the project's core method.

The two bands are near-identically distributed (day mean 125.75 sigma 34.36,
night mean 124.26 sigma 32.79), so the same stretch makes them genuinely
comparable.
"""
import os, time, shutil, arcpy

APRX  = r"Z:\Mars Project\Mars Project.aprx"
BKDIR = r"Z:\Mars Project\.backups"
DAY   = "Mars_MO_THEMIS-IR-Day"
NIGHT = "Mars_MO_THEMIS-IR-Night"

assert not any("ArcGISPro" in l for l in
               os.popen("tasklist").read().splitlines()), "close ArcGIS Pro first"

os.makedirs(BKDIR, exist_ok=True)
bk = os.path.join(BKDIR, "Mars Project %s.aprx" % time.strftime("%Y%m%d-%H%M%S"))
shutil.copy2(APRX, bk)
print("backed up ->", os.path.basename(bk))

p = arcpy.mp.ArcGISProject(APRX)
changed = []
for m in p.listMaps():
    day = next((l for l in m.listLayers() if l.name.startswith(DAY)), None)
    nit = next((l for l in m.listLayers() if l.name.startswith(NIGHT)), None)
    if not (day and nit):
        continue
    dsym = day.getDefinition("V3")
    nsym = nit.getDefinition("V3")
    src, dst = dsym.colorizer, nsym.colorizer
    before = "%s sd=%s min=%s max=%s" % (dst.stretchType,
             getattr(dst, "standardDeviationParam", ""), dst.minPercent, dst.maxPercent)
    dst.stretchType             = src.stretchType
    dst.standardDeviationParam  = src.standardDeviationParam
    dst.minPercent              = src.minPercent
    dst.maxPercent              = src.maxPercent
    nit.setDefinition(nsym)
    after = "%s sd=%s min=%s max=%s" % (dst.stretchType,
            dst.standardDeviationParam, dst.minPercent, dst.maxPercent)
    print("%-38s %s  ->  %s" % (m.name[:37], before, after))
    changed.append(m.name)
p.save()
print("saved. maps changed:", changed or "none")
