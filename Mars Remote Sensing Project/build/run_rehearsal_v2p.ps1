# The v2 runs rehearsed on the proposals as proposed (--labels v2p, KB §69.4; NEXT-STEPS §11.5 steps 2-3).
# Two chains, one after the other: the SVM, then the U-Net. A chain stops at its first failure; the other
# still runs. Each step's output goes to logs\rehearsal_v2p\<step>.log, and one line per step to queue.log.
# Pro closed. Run from build\:  powershell -File run_rehearsal_v2p.ps1 [-From <step>]
param([string]$From = "")
$ErrorActionPreference = "Stop"
$py = "D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$g60 = "F:\Mars Project\Global60"
$logs = Join-Path $here "logs\rehearsal_v2p"
New-Item -ItemType Directory -Force $logs | Out-Null
$queue = Join-Path $logs "queue.log"

function Emd {
    $m = Get-ChildItem "C:\MarsScratch\x5c_v2p\models" -Recurse -Filter "global60_unet_x5c_v2p_*.emd" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime | Select-Object -Last 1
    if (-not $m) { throw "no v2p model .emd under C:\MarsScratch\x5c_v2p\models" }
    return $m.FullName
}

$chains = @(
    @(
        @("01_svm_train_classify", { @("make_global60_classification.py", "--cell", "200", "--labels", "v2p") }),
        @("02_svm_mode11", { @("make_global60_landforms_clean.py", "--cell", "200", "--size", "11", "--labels", "v2p") }),
        @("03_score_svm_v2p", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2p", "--raster", "$g60\global60_landforms_svm_v2p_200m_mode11.tif") }),
        @("04_score_svm_four_on_v2p", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2p", "--raster", "$g60\global60_landforms_svm_200m_mode11.tif") }),
        @("05_d18_verdict_v2p", { @("score_d18_verdict.py", "--four", "logs\global60_classification_check_200m_mode11_on_v2p_labels.json", "--v2", "logs\global60_classification_check_v2p_200m_mode11.json", "--out", "logs\d18_verdict_v2p.json") }),
        @("06_geomap_v2p", { @("make_geomap_check.py", "--labels", "v2p") })
    ),
    @(
        @("07_unet_export", { @("make_dl_pixels.py", "--export", "--labels", "v2p") }),
        @("08_unet_train", { @("make_dl_pixels.py", "--train", "--labels", "v2p") }),
        @("09_unet_pass_a", { @("make_dl_pixels.py", "--classify-global", "--labels", "v2p", "--emd", (Emd)) }),
        @("10_unet_pass_b", { @("make_dl_pixels.py", "--classify-global", "--labels", "v2p", "--pass", "B", "--emd", (Emd)) }),
        @("11_unet_mosaic", { @("make_dl_pixels.py", "--mosaic", "--two-pass", "--labels", "v2p") }),
        @("12_score_unet_v2p", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2p", "--raster", "$g60\global60_landforms_unet_v2p_200m_seamfix.tif") }),
        @("13_score_unet_four_on_v2p", { @("verify_global60_classification.py", "--cell", "200", "--labels", "v2p", "--raster", "$g60\global60_landforms_unet_200m_seamfix.tif") })
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
            "{0:yyyy-MM-dd HH:mm:ss}  start {1}: {2}" -f $t0, $name, ($quoted -join " ") | Add-Content $queue
            $p = Start-Process -FilePath $py -ArgumentList (@("-u") + $quoted) -WorkingDirectory $here -NoNewWindow -Wait -PassThru `
                -RedirectStandardOutput (Join-Path $logs "$name.log") -RedirectStandardError (Join-Path $logs "$name.err.log")
            $code = $p.ExitCode
        } catch {
            "  $name could not start: $_" | Add-Content $queue
            $code = -1
        }
        $min = ((Get-Date) - $t0).TotalMinutes
        "{0:yyyy-MM-dd HH:mm:ss}  end   {1}: exit {2}, {3:N1} min" -f (Get-Date), $name, $code, $min | Add-Content $queue
        if ($code -ne 0) { "  chain stopped at $name" | Add-Content $queue; break }
    }
}
"{0:yyyy-MM-dd HH:mm:ss}  queue done" -f (Get-Date) | Add-Content $queue
