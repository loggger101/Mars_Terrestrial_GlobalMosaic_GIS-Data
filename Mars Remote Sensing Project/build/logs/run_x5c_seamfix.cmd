@echo off
rem X5c seam fix (KB 66.8): pass B (windows 128 px later), the two-pass mosaic, scored as before, seams.
rem Launched detached; output to dl_x5c_seamfix_<host>.log. Rerunnable: finished tiles are kept.
set PYTHONUNBUFFERED=1
set PY=D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe
set B=F:\Mars Remote Sensing Project\build
set EMD=F:\Mars Project\DLModels\global60_unet_x5c_20261020\global60_unet_x5c_20261020.emd
set G=F:\Mars Project\Global60
cd /d "%B%"
echo pass B started %DATE% %TIME%
"%PY%" make_dl_pixels.py --classify-global --pass B --emd "%EMD%"
if errorlevel 1 (echo FAILED pass B exit %ERRORLEVEL% & exit /b 1)
echo mosaic started %DATE% %TIME%
"%PY%" make_dl_pixels.py --mosaic --two-pass
if errorlevel 1 (echo FAILED mosaic exit %ERRORLEVEL% & exit /b 1)
echo score started %DATE% %TIME%
"%PY%" verify_global60_classification.py --cell 200 --raster "%G%\global60_landforms_unet_200m_seamfix.tif"
if errorlevel 1 (echo FAILED score exit %ERRORLEVEL% & exit /b 1)
echo seams started %DATE% %TIME%
"%PY%" make_dl_pixels.py --seams "%G%\global60_landforms_unet_200m_seamfix.tif" "%G%\global60_landforms_unet_200m.tif" "%G%\global60_landforms_svm_200m_mode11.tif" "%G%\global60_landforms_svm_200m.tif"
if errorlevel 1 (echo FAILED seams exit %ERRORLEVEL% & exit /b 1)
echo finished %DATE% %TIME%
