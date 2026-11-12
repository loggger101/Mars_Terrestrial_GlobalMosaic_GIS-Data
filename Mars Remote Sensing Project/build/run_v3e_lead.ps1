# The edifice retraining's model over all of ±60° (make_v3e_global.py): run ONLY if make_v3_edf.py --report gives
# E1-E5 all held (D39, KB 69.109). run_v3.ps1's U-Net chain from its first pass on, with edf's model, its own scratch
# (C:\MarsScratch\x5c_v3e) and its own names (unet_v3e); no v3 file is read or replaced. One process per step; each
# pass in chunks of <= 60 new tiles, because a pass's process grows ~0.28 GB a tile (KB 69.4); finished tiles are
# skipped, so a stopped queue is resumed with -From <step>. Each step's output goes to logs\run_v3e_lead\<step>.log,
# one line per step to queue.log. Pro closed. Desktop only. From build\:  powershell -File run_v3e_lead.ps1 [-From <step>]
param([string]$From = "")
$ErrorActionPreference = "Stop"
$py = "D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$map = "F:\Mars Project\Global60\global60_landforms_unet_v3e_200m_seamfix.tif"
$logs = Join-Path $here "logs\run_v3e_lead"
New-Item -ItemType Directory -Force $logs | Out-Null
$queue = Join-Path $logs "queue.log"

function Log([string]$line) {   # a reader holding queue.log open must not end the queue (it did, 2026-10-25)
    for ($i = 0; $i -lt 30; $i++) {
        try { [IO.File]::AppendAllText($queue, $line + "`r`n"); return } catch { Start-Sleep -Seconds 2 }
    }
}

$steps = @(
    @("03a_pass_a_to60", @("make_v3e_global.py", "--classify", "--tiles", "60")),
    @("03b_pass_a_to120", @("make_v3e_global.py", "--classify", "--tiles", "120")),
    @("03c_pass_a_to180", @("make_v3e_global.py", "--classify", "--tiles", "180")),
    @("03d_pass_a_to243", @("make_v3e_global.py", "--classify", "--tiles", "243")),
    @("04a_pass_b_to60", @("make_v3e_global.py", "--classify", "--pass", "B", "--tiles", "60")),
    @("04b_pass_b_to120", @("make_v3e_global.py", "--classify", "--pass", "B", "--tiles", "120")),
    @("04c_pass_b_to180", @("make_v3e_global.py", "--classify", "--pass", "B", "--tiles", "180")),
    @("04d_pass_b_to243", @("make_v3e_global.py", "--classify", "--pass", "B", "--tiles", "243")),
    @("05_mosaic", @("make_v3e_global.py", "--mosaic")),
    @("06_score_on_v3", @("verify_global60_classification.py", "--cell", "200", "--labels", "v3", "--raster", $map)),
    @("07_score_on_v2", @("verify_global60_classification.py", "--cell", "200", "--labels", "v2", "--raster", $map))
)

$env:PYTHONDONTWRITEBYTECODE = "1"
$started = $From -eq ""
foreach ($step in $steps) {
    $name = $step[0]
    if (-not $started) { if ($name -like "$From*") { $started = $true } else { continue } }
    $t0 = Get-Date
    $quoted = $step[1] | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }
    foreach ($ext in ".log", ".err.log") {   # a re-run step keeps the log of its earlier try
        $f = Join-Path $logs "$name$ext"
        if (Test-Path $f) { Move-Item $f (Join-Path $logs ("{0}.{1:yyyyMMdd_HHmm}{2}" -f $name, (Get-Item $f).LastWriteTime, $ext)) }
    }
    Log ("{0:yyyy-MM-dd HH:mm:ss}  start {1}: {2}" -f $t0, $name, ($quoted -join " "))
    $p = Start-Process -FilePath $py -ArgumentList (@("-u") + $quoted) -WorkingDirectory $here -NoNewWindow -PassThru `
        -RedirectStandardOutput (Join-Path $logs "$name.log") -RedirectStandardError (Join-Path $logs "$name.err.log")
    $null = $p.Handle                        # keeps the process handle, so ExitCode is there after the wait (KB 69.83)
    $p.WaitForExit()
    Log ("{0:yyyy-MM-dd HH:mm:ss}  end   {1}: exit {2}, {3:N1} min" -f (Get-Date), $name, $p.ExitCode, ((Get-Date) - $t0).TotalMinutes)
    if ($p.ExitCode -ne 0) { Log "  queue stopped at $name"; break }
}
Log ("{0:yyyy-MM-dd HH:mm:ss}  queue done" -f (Get-Date))
