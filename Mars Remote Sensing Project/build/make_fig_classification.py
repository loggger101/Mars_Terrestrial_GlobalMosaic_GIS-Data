# -*- coding: utf-8 -*-
"""Ius Chasma unsupervised classification, 10 classes, over the day-IR relief."""
import numpy as np
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import on_drive, junction
from osgeo import gdal
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
gdal.UseExceptions()

S=4
def rd(p, band=1):
    d=gdal.Open(p)
    return d.GetRasterBand(band).ReadAsArray(buf_xsize=d.RasterXSize//S,
            buf_ysize=d.RasterYSize//S, resample_alg=gdal.GRIORA_NearestNeighbour)
cls=rd(os.path.join(junction("TypeArea"), r"ius_isocluster_10.tif")).astype(np.int16)
day=gdal.Open(os.path.join(junction("TypeArea"), r"ius_day.tif"))
d=day.GetRasterBand(1).ReadAsArray(buf_xsize=day.RasterXSize//S,
        buf_ysize=day.RasterYSize//S, resample_alg=gdal.GRIORA_Average).astype(np.float32)
p1,p2=np.percentile(d[d>0],[1,99]); shade=np.clip((d-p1)/(p2-p1),0,1)

pal=["#8ecae6","#219ebc","#023047","#ffb703","#fb8500",
     "#d62828","#7209b7","#4361ee","#43aa8b","#b5179e"]
cmap=ListedColormap(pal); norm=BoundaryNorm(np.arange(0.5,11.5,1),10)
pct={6:25.25,4:15.21,3:12.39,5:10.21,7:9.34,8:6.31,9:6.29,2:5.95,1:5.64,10:3.41}

BG="#0E2841"; CY="#0E9ED4"; SUB="#9ED8ED"; ext=[271,286,-13,-6]
fig,ax=plt.subplots(2,1,figsize=(12,10.6),facecolor=BG)
ax[0].imshow(shade,cmap="gray",extent=ext,aspect="auto")
ax[0].set_title("THEMIS Day IR  \u2014  the surface being classified",color=CY,fontsize=12.5,pad=8,loc="left")
ax[1].imshow(shade,cmap="gray",extent=ext,aspect="auto")
ax[1].imshow(np.ma.masked_less(cls,1),cmap=cmap,norm=norm,extent=ext,aspect="auto",alpha=0.62)
ax[1].set_title("Iso Cluster \u2192 Maximum Likelihood  \u2014  10 classes, 5-band stack",
                color=CY,fontsize=12.5,pad=8,loc="left")
for a in ax:
    a.set_facecolor(BG); a.tick_params(colors=SUB,labelsize=9)
    for s in a.spines.values(): s.set_color("#2A4A66")
ax[1].set_xlabel("East longitude (\u00b0)",color=SUB)
ax[1].legend(handles=[Patch(facecolor=pal[i-1],label="%2d  %5.2f%%"%(i,pct[i]))
                      for i in range(1,11)],
             loc="center left",bbox_to_anchor=(1.005,0.5),frameon=False,
             labelcolor=SUB,fontsize=8.5,title="class",title_fontsize=9)
ax[1].get_legend().get_title().set_color(CY)
fig.suptitle("Unsupervised classification  \u00b7  Ius Chasma type area",
             color="white",fontsize=15.5,x=0.098,ha="left",y=0.985)
fig.tight_layout(rect=[0,0.01,0.93,0.962],h_pad=2.6)
out=on_drive(r"Mars Remote Sensing Project\build\pres1_img\ius_classification.png")
fig.savefig(out,dpi=112,facecolor=BG); print("wrote",out)
