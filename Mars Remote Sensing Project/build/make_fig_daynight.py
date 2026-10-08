# -*- coding: utf-8 -*-
"""Day / night / difference over the Ius Chasma type area.

Proves the day-night co-registration empirically and produces
pres1_img/ius_day_night_diff.png. Reads the GLOBAL mosaics directly, computing
each window from that file's own geotransform, so the offsets it prints are an
independent check rather than an assumption (see PROJECT-KNOWLEDGE.md 15.3).
"""
import numpy as np, time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
from osgeo import gdal
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
gdal.UseExceptions()

DAY   = on_drive(r"Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif")
NIGHT = on_drive(r"Mars_MO_THEMIS-IR-Night_mosaic_60N60S_100m_v14.tif")
R = 3396190.0; DEG = R*np.pi/180.0
LON0, LON1, LAT0, LAT1 = 271.0, 286.0, -13.0, -6.0

def window(path, cm=180.0):
    ds = gdal.Open(path); gt = ds.GetGeoTransform()
    c0 = ((LON0-cm)*DEG-gt[0])/gt[1]; c1 = ((LON1-cm)*DEG-gt[0])/gt[1]
    r0 = (gt[3]-LAT1*DEG)/gt[1];      r1 = (gt[3]-LAT0*DEG)/gt[1]
    return ds, c0, r0, int(round(c1-c0)), int(round(r1-r0))

dsD, cD, rD, w, h = window(DAY)
dsN, cN, rN, _, _ = window(NIGHT)
print("offset day->night: dcol=%.3f drow=%.3f  (integers => pixel-aligned)" % (cN-cD, rN-rD))

OUT = 1100
t = time.time()
day = dsD.GetRasterBand(1).ReadAsArray(int(round(cD)), int(round(rD)), w, h,
        buf_xsize=OUT, buf_ysize=int(OUT*h/w), resample_alg=gdal.GRIORA_Average).astype(np.float32)
nig = dsN.GetRasterBand(1).ReadAsArray(int(round(cN)), int(round(rN)), w, h,
        buf_xsize=OUT, buf_ysize=int(OUT*h/w), resample_alg=gdal.GRIORA_Average).astype(np.float32)
print("reads %.1fs" % (time.time()-t))

m = (day > 0) & (nig > 0)
diff = np.where(m, day-nig, np.nan)
print("valid overlap %.2f%%   pearson r(day,night) = %.4f"
      % (100*m.mean(), np.corrcoef(day[m], nig[m])[0, 1]))

BG, CY, SUB = "#0E2841", "#0E9ED4", "#9ED8ED"
ext = [LON0, LON1, LAT0, LAT1]
fig, ax = plt.subplots(3, 1, figsize=(11, 13.6), facecolor=BG)
for a, (im, ttl, cmap, kw) in zip(ax, [
        (day,  "THEMIS Day IR  \u2014  v12, 100 m", "gray", {}),
        (nig,  "THEMIS Night IR  \u2014  v14, 100 m", "gray", {}),
        (diff, "Day \u2212 Night  \u2014  raw DN difference, not thermal inertia", "RdBu_r",
         dict(vmin=np.nanpercentile(diff, 2), vmax=np.nanpercentile(diff, 98)))]):
    a.imshow(im, cmap=cmap, extent=ext, aspect="auto", **kw)
    a.set_title(ttl, color=CY, fontsize=13, pad=9, loc="left")
    a.set_facecolor(BG); a.tick_params(colors=SUB, labelsize=9)
    for sp in a.spines.values(): sp.set_color("#2A4A66")
ax[-1].set_xlabel("East longitude (\u00b0)", color=SUB)
fig.suptitle("Ius Chasma type area  \u00b7  271\u2013286\u00b0E, 13\u20136\u00b0S",
             color="white", fontsize=16, y=0.985, x=0.125, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.965])
out = on_drive(r"Mars Remote Sensing Project\build\pres1_img\ius_day_night_diff.png")
fig.savefig(out, dpi=115, facecolor=BG)
print("wrote", out)
