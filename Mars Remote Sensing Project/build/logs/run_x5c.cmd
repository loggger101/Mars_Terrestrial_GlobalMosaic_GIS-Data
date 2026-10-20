@echo off
rem X5c: U-Net on the training split's Classified_Tiles, classify the held-out windows, score per pixel (KB 66.6).
rem Launched detached after X5b; output to dl_x5c_<host>.log.
set PYTHONUNBUFFERED=1
set PY=D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe
set S=F:\Mars Remote Sensing Project\build\make_dl_pixels.py
set M=global60_unet_x5c_20261020
set EMD=F:\Mars Project\DLModels\%M%\%M%.emd
echo train started %DATE% %TIME%
"%PY%" "%S%" --train --epochs 30
if errorlevel 1 (echo FAILED train exit %ERRORLEVEL% & exit /b 1)
echo classify started %DATE% %TIME%
"%PY%" "%S%" --classify --emd "%EMD%"
if errorlevel 1 (echo FAILED classify exit %ERRORLEVEL% & exit /b 1)
echo score started %DATE% %TIME%
"%PY%" "%S%" --score "C:\MarsScratch\x5c\classified\%M%" --out "F:\Mars Remote Sensing Project\build\logs\dl_pixels_score_x5c.json"
if errorlevel 1 (echo FAILED score exit %ERRORLEVEL% & exit /b 1)
echo finished %DATE% %TIME%
