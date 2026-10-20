@echo off
rem X5b: clean the exports, train (backbone unfrozen, no early stopping, rare-class chips added), detect at
rem 0.1, score at every cutoff (KB 66.5). Launched detached; output to dl_x5b_<host>.log.
set PYTHONUNBUFFERED=1
set PY=D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe
set S=F:\Mars Remote Sensing Project\build\make_dl_model.py
set M=global60_retinanet_x5b_20261020
set EMD=F:\Mars Project\DLModels\%M%\%M%.emd
set FC=C:\MarsScratch\x5\%M%\dl_det_heldout_%M%.shp
echo prepare started %DATE% %TIME%
"%PY%" "%S%" --prepare
if errorlevel 1 (echo FAILED prepare exit %ERRORLEVEL% & exit /b 1)
echo train started %DATE% %TIME%
"%PY%" "%S%" --train --tag x5b --data "C:\MarsScratch\x5b\main_clean;C:\MarsScratch\x5b\rare_clean" --epochs 30
if errorlevel 1 (echo FAILED train exit %ERRORLEVEL% & exit /b 1)
echo detect started %DATE% %TIME%
"%PY%" "%S%" --detect --emd "%EMD%" --threshold 0.1
if errorlevel 1 (echo FAILED detect exit %ERRORLEVEL% & exit /b 1)
echo score started %DATE% %TIME%
"%PY%" "%S%" --score "%FC%" --out "F:\Mars Remote Sensing Project\build\logs\dl_heldout_score_x5b.json"
if errorlevel 1 (echo FAILED score exit %ERRORLEVEL% & exit /b 1)
echo finished %DATE% %TIME%
