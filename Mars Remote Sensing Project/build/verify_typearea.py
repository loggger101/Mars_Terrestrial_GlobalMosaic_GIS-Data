import numpy as np
from osgeo import gdal
gdal.UseExceptions()
p=r"Z:\Mars Project\TypeArea\ius_composite_5band.tif"
ds=gdal.Open(p)
names=["Viking R","Viking G","Viking B","THEMIS day","THEMIS night"]
print("%-12s %6s %6s %9s %8s %9s" % ("band","min","max","mean","std","valid%"))
arr=[]
for i,n in enumerate(names,1):
    b=ds.GetRasterBand(i); a=b.ReadAsArray().astype(np.float32); arr.append(a)
    v=a[a>0]
    print("%-12s %6.0f %6.0f %9.3f %8.3f %8.2f%%" % (n, v.min(), v.max(), v.mean(), v.std(),
          100.0*v.size/a.size))
A=np.dstack(arr)
m=(A>0).all(axis=2)
print("\nall five bands valid at the same pixel: %.2f%%" % (100*m.mean()))
print("\ncorrelation matrix (on co-valid pixels):")
X=np.vstack([a[m] for a in arr])
C=np.corrcoef(X)
print("            " + " ".join("%9s" % n[:9] for n in names))
for i,n in enumerate(names):
    print("%-12s" % n + " ".join("%9.3f" % C[i,j] for j in range(5)))
dem=gdal.Open(r"Z:\Mars Project\TypeArea\ius_dem.tif").ReadAsArray().astype(np.float32)
dem[dem<-30000]=np.nan
print("\nDEM on same grid: %.0f .. %.0f m  relief %.0f m" % (np.nanmin(dem),np.nanmax(dem),
      np.nanmax(dem)-np.nanmin(dem)))
