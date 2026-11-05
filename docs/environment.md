# The software environment

What each machine that built this project runs, read from the machine by `Mars Remote Sensing Project/build/github_environment.py`; a run replaces its own machine's section. Rasters and arcpy run on the ArcGIS Python, decks and reports on the system Python (KB §2.4); the U-Net and RetinaNet need the Deep Learning Libraries and a CUDA GPU. `requirements-system.txt` pins the system Python's packages as the last machine to run this had them. Generated; don't edit it here.

<!-- machine: desktop -->
## desktop

| | |
|---|---|
| Written | 2026-11-05 |
| OS | Windows 11 (build 10.0.26100) |
| CPU | Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz |
| Memory | 68.6 GB |
| GPU | NVIDIA GeForce RTX 2080 Ti, driver 617.42, 11264 MiB |
| ArcGIS Pro | ArcGISPro 3.7 (build 1901) |
| Licensed extensions | 3D Available, Spatial Available, ImageAnalyst Available |
| ArcGIS Python | 3.13.13, `D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe` |
| ArcGIS Python packages | numpy `2.3.5`, scipy `1.16.3`, matplotlib `3.10.8`, Pillow `12.2.0`, GDAL `3.12.2`, arcgis `2.4.3`, torch `2.9.1`, torchvision `0.25.0`, fastai `1.0.63` |
| Deep Learning Libraries | `3.7` |
| CUDA (torch) | 12.9 |
| System Python | 3.13.9, `C:\Users\Owner\AppData\Local\Programs\Python\Python313\python.exe` |
| System Python packages | numpy `2.2.6`, matplotlib `3.10.6`, Pillow `11.3.0`, python-pptx `1.0.2`, python-docx `1.2.0`, PyMuPDF `1.28.2` |
| TeX | One MiKTeX Utility 1.11 (MiKTeX 25.12) |
| aastex701.cls | 2025/05/09 Version 7.0.1/AAS markup document class |
<!-- end: desktop -->

<!-- machine: laptop -->
## laptop

| | |
|---|---|
| Written | 2026-11-03 |
| OS | Windows 11 (build 10.0.26300) |
| CPU | Intel(R) Core(TM) Ultra 5 225U |
| Memory | 16.5 GB |
| GPU | Intel(R) Graphics, driver 32.0.101.8626 |
| ArcGIS Pro | ArcGISPro 3.7 (build 1901) |
| Licensed extensions | 3D Available, Spatial Available, ImageAnalyst Available |
| ArcGIS Python | 3.13.13, `C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe` |
| ArcGIS Python packages | numpy `2.3.5`, scipy `1.16.3`, matplotlib `3.10.8`, Pillow `12.2.0`, GDAL `3.12.2`, arcgis `2.4.3`, torch not installed, torchvision not installed, fastai not installed |
| Deep Learning Libraries | not installed |
| System Python | 3.14.6, `C:\Users\Loggg\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| System Python packages | numpy `2.5.2`, matplotlib `3.11.1`, Pillow `12.3.0`, python-pptx `1.0.2`, python-docx `1.2.0`, PyMuPDF `1.28.2` |
| TeX | not on the path |
| aastex701.cls | not found by kpsewhich |
<!-- end: laptop -->
