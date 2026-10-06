# -*- coding: utf-8 -*-
"""Ius Chasma fusion figure - HSV composite so colour carries thermal
information while relief still reads."""
import numpy as np
from osgeo import gdal
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
gdal.UseExceptions()

ds=gdal.Open(r"Z:\Mars Project\TypeArea\ius_composite_5band.tif")
S=4
def band(i):
    return ds.GetRasterBand(i).ReadAsArray(buf_xsize=ds.RasterXSize//S,
            buf_ysize=ds.RasterYSize//S, resample_alg=gdal.GRIORA_Average).astype(np.float32)
R,G,B,D,N=[band(i) for i in range(1,6)]

def st(a,lo=2,hi=98):
    p1,p2=np.percentile(a[a>0],[lo,hi]); return np.clip((a-p1)/(p2-p1),0,1)

nat=np.dstack([st(R),st(G),st(B)])

# false colour -> HSV, tame the chroma, take brightness from day IR morphology
fc=np.dstack([st(N),st(D),st(R)])
hsv=rgb_to_hsv(fc)
hsv[...,1]*=0.50                      # desaturate: colour should hint, not shout
hsv[...,2]=0.15+0.85*st(D,1,99)       # value = day IR, so relief and texture carry
fuse=hsv_to_rgb(hsv)

# day-night difference: the thermal-inertia proxy, on its own scale
dn=np.where((D>0)&(N>0), D-N, np.nan)

BG="#0E2841"; CY="#0E9ED4"; SUB="#9ED8ED"
ext=[271,286,-13,-6]
panels=[(nat,None,"Natural colour  \u2014  Viking MDIM 2.1",
         "albedo only: the canyon reads as shadow, the plateau is uniform dust"),
        (fuse,None,"Fusion  \u2014  hue: THEMIS night / day / Viking red,  value: day IR",
         "colour now separates materials that share the same albedo above"),
        (dn,"RdBu_r","Day \u2212 Night  \u2014  thermal-inertia proxy",
         "red: dust, low inertia    blue: bedrock and coarse debris, high inertia")]
fig,ax=plt.subplots(3,1,figsize=(12,15.2),facecolor=BG)
for a,(im,cmap,t,sub) in zip(ax,panels):
    kw=dict(extent=ext,aspect="auto")
    if cmap: kw.update(cmap=cmap,vmin=np.nanpercentile(dn,2),vmax=np.nanpercentile(dn,98))
    a.imshow(im,**kw); a.set_facecolor(BG)
    a.set_title(t,color=CY,fontsize=12.5,pad=8,loc="left")
    a.text(0.0,-0.10,sub,transform=a.transAxes,color=SUB,fontsize=9.5,va="top")
    for s in a.spines.values(): s.set_color("#2A4A66")
    a.tick_params(colors=SUB,labelsize=9)
ax[-1].set_xlabel("East longitude (\u00b0)",color=SUB,labelpad=22)
fig.suptitle("Co-registered stack  \u00b7  Ius Chasma type area  \u00b7  271\u2013286\u00b0E, 13\u20136\u00b0S",
             color="white",fontsize=15.5,x=0.098,ha="left",y=0.988)
fig.subplots_adjust(hspace=0.30)
fig.tight_layout(rect=[0,0.01,1,0.965],h_pad=3.2)
out=r"Z:\Mars Remote Sensing Project\build\pres1_img\ius_fusion.png"
fig.savefig(out,dpi=112,facecolor=BG); print("wrote",out)
