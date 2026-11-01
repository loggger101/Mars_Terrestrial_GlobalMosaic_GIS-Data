# The v3 runs (--labels v3, KB §69.49): the seven classes on propose_v3_labels.py's labels, the v2 polygons cut into
# screened pieces plus a few thousand new ones. run_v2.ps1's queue with v3 for v2, the U-Net chain first (the
# author's request was for the deep-learning map), then the SVM. Each v3 map is scored on the v3 held-out polygons
# and on the v2 ones (the like-for-like comparison with §69.24-§69.25), and each v2 map on the v3 held-out polygons.
# A chain stops at its first failure; the other still runs. Each step's output goes to logs\run_v3\<step>.log, and one
# line per step to queue.log. Pro closed. Desktop only. Run from build\:  powershell -File run_v3.ps1 [-From <step>] [-ClassifyOnly]
# -ClassifyOnly resumes the SVM step on its trained .ecd and finished tiles (a restart stopped run_v2's, KB §69.23).
param([string]$From = "", [switch]$ClassifyOnly)
$ErrorActionPreference = "Stop"
$py = "D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$g60 = "F:\Mars Project\Global60"
$logs = Join-Path $here "logs\run_v3"
New-Item -ItemType Directory -Force $logs | Out-Null
$queue = Join-Path $logs "queue.log"

function Log([string]$line) {   # a reader holding queue.log open must not end the queue (it did, 2026-10-25)
    for ($i = 0; $i -lt 30; $i++) {
        try { [IO.File]::AppendAllText($queue, $line + "`r`n"); return } catch { Start-Sleep -Seconds 2 }
    }
}

function Emd {
    $m = Get-ChildItem "C:\MarsScratch\x5c_v3\models" -Recurse -Filter "global60_unet_x5c_v3_*.emd" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime | Select-Object -Last 1
    if (-not $m) { throw "no v3 model .emd under C:\MarsScratch\x5c_v3\models" }
    return $m.FullName
}

$chains = @(
    @(
        @("01_unet_export", { @("make_dl_pixels.py", "--export", "--labels", "v3") }),
        @("02_unet_train", { @("make_dl_pixels.py", "--train", "--labels", "v3") }),
        # each pass in chunks of <= 60 new tiles, one process each: a pass's process grows ~0.28 GB a tile (KB §69.4);
        # --tiles N runs the first N, finished tiles skipped
        @("03a_unet_pass_a_to60", { @("make_dl_pixels.py", "--classify-global", "--labels", "v3", "--tiles", "60", "--emd", (Emd)) }),
        @("03b_unet_pass_a_to120", { @("make_dl_pixels.py", "--classify-global", "--labels", "v3", "--tiles", "120", "--emd", (Emd)) }),
        @("03c_unet_pass_a_to180", { @("make_dl_pixels.py", "--classify-global", "--labels", "v3", "--tiles", "180", "--emd", (Emd)) }),
        @("03d_unet_pass_a_to243", { @("make_dl_pixels.py", "--classify-global", "--labels", "v3", "--tiles", "243", "--emd", (Emd)) }),
        @("04a_unet_pass_b_to60", { @("make_dl_pixels.py", "--classify-global", "--labels", "v3", "--pass", "B", "--tiles", "60", "--emd", (Emd)) }),
        @("04b_unet_pass_b_to120", { @("make_dl_pixels.py", "--classify-global", "--labels", "v3", "--pass", "B", "--tiles", "120", "--emd", (Emd)) }),
        @("04c_unet_pass_b_to180", { @("make_dl_pixels.py", "--classify-global", "--labels", "v3", "--pass", "B", "--tiles", "180", "--emd", (Emd)) }),
        @("04d_unet_pass_b_to243", { @("make_dl_pixels.py", "--classify-global", "--labels", "v3", "--pass", "B", "--tiles", "243", "--emd", (Emd)) }),
        @("05_unet_mosaic", { @("make_dl_pixels.py", "--mosaic", "--two-pass", "--labels", "v3") }),
        @("06_score_unet_v3", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v3", "--raster", "$g60\global60_landforms_unet_v3_200m_seamfix.tif") }),
        @("07_score_unet_v3_on_v2", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2", "--raster", "$g60\global60_landforms_unet_v3_200m_seamfix.tif") }),
        @("08_score_unet_v2_on_v3", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v3", "--raster", "$g60\global60_landforms_unet_v2_200m_seamfix.tif") })
    ),
    @(
        @("09_svm_train_classify", { @("make_global60_classification.py", "--cell", "200", "--labels", "v3") + @(if ($ClassifyOnly) { "--classify-only" }) }),
        @("10_svm_mode11", { @("make_global60_landforms_clean.py", "--cell", "200", "--size", "11", "--labels", "v3") }),
        @("11_score_svm_v3", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v3", "--raster", "$g60\global60_landforms_svm_v3_200m_mode11.tif") }),
        @("12_score_svm_v3_on_v2", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2", "--raster", "$g60\global60_landforms_svm_v3_200m_mode11.tif") }),
        @("13_score_svm_v2_on_v3", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v3", "--raster", "$g60\global60_landforms_svm_v2_200m_mode11.tif") }),
        @("14_geomap_v3", { @("make_geomap_check.py", "--labels", "v3") })
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
            foreach ($ext in ".log", ".err.log") {   # a re-run step keeps the log of its earlier try
                $f = Join-Path $logs "$name$ext"
                if (Test-Path $f) { Move-Item $f (Join-Path $logs ("{0}.{1:yyyyMMdd_HHmm}{2}" -f $name, (Get-Item $f).LastWriteTime, $ext)) }
            }
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
