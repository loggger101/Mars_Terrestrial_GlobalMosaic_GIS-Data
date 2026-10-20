@echo off
rem X5c over all of +/-60 deg (KB 66.7): classify 243 tiles, mosaic, score as the SVM maps were, seams.
rem Launched detached; output to dl_x5c_global_<host>.log. Rerunnable: finished tiles are kept.
set PYTHONUNBUFFERED=1
set PY=D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe
set B=F:\Mars Remote Sensing Project\build
set EMD=F:\Mars Project\DLModels\global60_unet_x5c_20261020\global60_unet_x5c_20261020.emd
set G=F:\Mars Project\Global60
cd /d "%B%"
echo classify started %DATE% %TIME%
"%PY%" make_dl_pixels.py --classify-global --emd "%EMD%"
if errorlevel 1 (echo FAILED classify exit %ERRORLEVEL% & exit /b 1)
echo mosaic started %DATE% %TIME%
"%PY%" make_dl_pixels.py --mosaic
if errorlevel 1 (echo FAILED mosaic exit %ERRORLEVEL% & exit /b 1)
echo score started %DATE% %TIME%
"%PY%" verify_global60_classification.py --cell 200 --raster "%G%\global60_landforms_unet_200m.tif"
if errorlevel 1 (echo FAILED score exit %ERRORLEVEL% & exit /b 1)
echo seams started %DATE% %TIME%
"%PY%" make_dl_pixels.py --seams "%G%\global60_landforms_unet_200m.tif" "%G%\global60_landforms_svm_200m_mode11.tif" "%G%\global60_landforms_svm_200m.tif"
if errorlevel 1 (echo FAILED seams exit %ERRORLEVEL% & exit /b 1)
echo finished %DATE% %TIME%
