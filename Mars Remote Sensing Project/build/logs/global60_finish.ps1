# Chained after the 400 m classification (KB §31.3): when it exits with the mosaic built, score it,
# then add it to the project (layer + layout 04). Pro must be closed for the second step; the map
# script refuses otherwise and nothing is written.
$py = "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
$b = "Z:\Mars Remote Sensing Project\build"
$log = "$b\logs\global60_finish.log"
"started $(Get-Date)" | Out-File $log -Encoding utf8
Wait-Process -Id 10284 -ErrorAction SilentlyContinue
"classification process gone $(Get-Date)" | Out-File $log -Append -Encoding utf8
if (-not (Select-String -Path "$b\logs\global60_classify_400m.log" -Pattern "mosaic done" -Quiet)) {
    "mosaic not finished - resume with: python make_global60_classification.py --classify-only --cell 400" | Out-File $log -Append -Encoding utf8
    exit 1
}
Set-Location $b
& $py -u verify_global60_classification.py *>> $log
"verify exit $LASTEXITCODE $(Get-Date)" | Out-File $log -Append -Encoding utf8
& $py -u make_global60_maps.py *>> $log
"maps exit $LASTEXITCODE $(Get-Date)" | Out-File $log -Append -Encoding utf8
