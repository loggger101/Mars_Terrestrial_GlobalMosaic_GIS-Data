@echo off
rem X5 detect then score (KB 66.1). Launched detached; output to dl_detect_score_<host>.log.
set PYTHONUNBUFFERED=1
set PY=D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe
set S=F:\Mars Remote Sensing Project\build\make_dl_model.py
set EMD=F:\Mars Project\DLModels\global60_retinanet_20261019\global60_retinanet_20261019.emd
set FC=C:\MarsScratch\x5\dl_detections_heldout_20261019.shp
echo detect started %DATE% %TIME%
"%PY%" "%S%" --detect --emd "%EMD%"
if errorlevel 1 (echo FAILED detect exit %ERRORLEVEL% & exit /b 1)
echo score started %DATE% %TIME%
"%PY%" "%S%" --score "%FC%"
if errorlevel 1 (echo FAILED score exit %ERRORLEVEL% & exit /b 1)
echo finished %DATE% %TIME%
