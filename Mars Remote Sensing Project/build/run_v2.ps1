# The v2 runs on the reviewed labels (--labels v2, KB §69.8; NEXT-STEPS §11.5 steps 2-3), the queue of
# run_rehearsal_v2p.ps1 with v2 for v2p. Two chains, one after the other: the SVM, then the U-Net. A chain
# stops at its first failure; the other still runs. Each step's output goes to logs\run_v2\<step>.log, and one
# line per step to queue.log. Pro closed. Run from build\:  powershell -File run_v2.ps1 [-From <step>]
param([string]$From = "")
$ErrorActionPreference = "Stop"
$py = "D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$g60 = "F:\Mars Project\Global60"
$logs = Join-Path $here "logs\run_v2"
New-Item -ItemType Directory -Force $logs | Out-Null
$queue = Join-Path $logs "queue.log"

function Log([string]$line) {   # a reader holding queue.log open must not end the queue (it did, 2026-10-25)
    for ($i = 0; $i -lt 30; $i++) {
        try { [IO.File]::AppendAllText($queue, $line + "`r`n"); return } catch { Start-Sleep -Seconds 2 }
    }
}

function Emd {
    $m = Get-ChildItem "C:\MarsScratch\x5c_v2\models" -Recurse -Filter "global60_unet_x5c_v2_*.emd" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime | Select-Object -Last 1
    if (-not $m) { throw "no v2 model .emd under C:\MarsScratch\x5c_v2\models" }
    return $m.FullName
}

$chains = @(
    @(
        @("01_svm_train_classify", { @("make_global60_classification.py", "--cell", "200", "--labels", "v2") }),
        @("02_svm_mode11", { @("make_global60_landforms_clean.py", "--cell", "200", "--size", "11", "--labels", "v2") }),
        @("03_score_svm_v2", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2", "--raster", "$g60\global60_landforms_svm_v2_200m_mode11.tif") }),
        @("04_score_svm_four_on_v2", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2", "--raster", "$g60\global60_landforms_svm_200m_mode11.tif") }),
        @("05_d18_verdict_v2", { @("score_d18_verdict.py", "--four", "logs\global60_classification_check_200m_mode11_on_v2_labels.json", "--v2", "logs\global60_classification_check_v2_200m_mode11.json", "--out", "logs\d18_verdict.json") }),
        @("06_geomap_v2", { @("make_geomap_check.py", "--labels", "v2") })
    ),
    @(
        @("07_unet_export", { @("make_dl_pixels.py", "--export", "--labels", "v2") }),
        @("08_unet_train", { @("make_dl_pixels.py", "--train", "--labels", "v2") }),
        # each pass in chunks of <= 60 new tiles, one process each: a pass's process grows ~0.28 GB a tile
        # (40 GB by tile 144 of pass A, 2026-10-26); --tiles N runs the first N, finished tiles skipped
        @("09a_unet_pass_a_to180", { @("make_dl_pixels.py", "--classify-global", "--labels", "v2", "--tiles", "180", "--emd", (Emd)) }),
        @("09b_unet_pass_a_to243", { @("make_dl_pixels.py", "--classify-global", "--labels", "v2", "--tiles", "243", "--emd", (Emd)) }),
        @("10a_unet_pass_b_to60", { @("make_dl_pixels.py", "--classify-global", "--labels", "v2", "--pass", "B", "--tiles", "60", "--emd", (Emd)) }),
        @("10b_unet_pass_b_to120", { @("make_dl_pixels.py", "--classify-global", "--labels", "v2", "--pass", "B", "--tiles", "120", "--emd", (Emd)) }),
        @("10c_unet_pass_b_to180", { @("make_dl_pixels.py", "--classify-global", "--labels", "v2", "--pass", "B", "--tiles", "180", "--emd", (Emd)) }),
        @("10d_unet_pass_b_to243", { @("make_dl_pixels.py", "--classify-global", "--labels", "v2", "--pass", "B", "--tiles", "243", "--emd", (Emd)) }),
        @("11_unet_mosaic", { @("make_dl_pixels.py", "--mosaic", "--two-pass", "--labels", "v2") }),
        @("12_score_unet_v2", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2", "--raster", "$g60\global60_landforms_unet_v2_200m_seamfix.tif") }),
        @("13_score_unet_four_on_v2", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2", "--raster", "$g60\global60_landforms_unet_200m_seamfix.tif") })
    )
)

$started = $From -eq ""
foreach ($chain in $chains) {
    foreach ($step in $chain) {
        $name = $step[0]
        if (-not $started) { if ($name -like "$From*") { $started = $true } else { continue } }
        $t0 = Get-Date
        try {
            $a = & $step[1]
            $quoted = $a | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }
            Log ("{0:yyyy-MM-dd HH:mm:ss}  start {1}: {2}" -f $t0, $name, ($quoted -join " "))
            $p = Start-Process -FilePath $py -ArgumentList (@("-u") + $quoted) -WorkingDirectory $here -NoNewWindow -Wait -PassThru `
                -RedirectStandardOutput (Join-Path $logs "$name.log") -RedirectStandardError (Join-Path $logs "$name.err.log")
            $code = $p.ExitCode
        } catch {
            Log "  $name could not start: $_"
            $code = -1
        }
        $min = ((Get-Date) - $t0).TotalMinutes
        Log ("{0:yyyy-MM-dd HH:mm:ss}  end   {1}: exit {2}, {3:N1} min" -f (Get-Date), $name, $code, $min)
        if ($code -ne 0) { Log "  chain stopped at $name"; break }
    }
}
Log ("{0:yyyy-MM-dd HH:mm:ss}  queue done" -f (Get-Date))
