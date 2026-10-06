# -*- coding: utf-8 -*-
"""Central meridian of each global raster, read without needing GDAL here.

The GeoTIFF keeps its projection in the GeoAsciiParams / GeoDoubleParams tags;
the ArcGIS Pro interpreter has GDAL but the stock one does not, so shell out.
"""
import json
import subprocess

PY = r"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
CODE = (
    "import json;from osgeo import gdal,osr;gdal.UseExceptions();"
    "p={'Viking':r'Z:\\Mars_Viking_MDIM21_ClrMosaic_global_232m.tif',"
    "'THEMIS':r'Z:\\Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v12.tif',"
    "'DEM':r'Z:\\Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif'};"
    "o={};"
    "\nfor k,v in p.items():\n"
    "    d=gdal.Open(v);s=osr.SpatialReference(wkt=d.GetProjection());"
    "o[k]=float(s.GetProjParm('Central_Meridian',0.0) or 0.0)\n"
    "print(json.dumps(o))")


def central_meridians():
    out = subprocess.check_output([PY, "-c", CODE], text=True)
    return json.loads(out.strip().splitlines()[-1])
