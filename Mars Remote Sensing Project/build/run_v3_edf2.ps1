# The edifice retraining a second time (KB 69.125): edf's labels and chips, unchanged, trained with the learning rate
# fixed at the control's (fresh's 3.311e-4, slice(lr/10, lr)), because the tool's finder gave edf 2.512e-3, 2.5 to 10
# times any other v3 training's, and edf's chip accuracy peaked at 67 % where the others end at 88-89 %. Decided after
# edf was scored; E1-E5 and the rule are unchanged (make_v3_edf.py). No export: D:\MarsScratch\x5c_v3x\export_tiles
# is edf's. Then edf2's model on the standard windows (edf2) and on fresh's (edf2v). run_v3_edf.ps1's queue.
# Then:  "<ArcGIS Pro Python>" make_v3_edf.py --report --rerun   -> logs\v3_edf2.json
# From build\:  powershell -File run_v3_edf2.ps1 [-From <step>]
param([string]$From = "")
$ErrorActionPreference = "Stop"
$py = "D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$logs = Join-Path $here "logs\run_v3_edf2"
New-Item -ItemType Directory -Force $logs | Out-Null
$queue = Join-Path $logs "queue.log"
$LR = "0.0003311311214825911"

function Log([string]$line) {
    for ($i = 0; $i -lt 30; $i++) {
        try { [IO.File]::AppendAllText($queue, $line + "`r`n"); return } catch { Start-Sleep -Seconds 2 }
    }
}

$chains = @(
    @("edf2", @("train", "classify")),
    @("edf2v", @("classify"))
)

$env:PYTHONDONTWRITEBYTECODE = "1"
$started = $From -eq ""
foreach ($c in $chains) {
    $run = $c[0]
    foreach ($step in $c[1]) {
        $name = "$($run)_$step"
        if (-not $started) { if ($name -eq $From) { $started = $true } else { continue } }
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Log "$stamp  start $name"
        $t = Get-Date
        $a = @("make_v3_extras.py", "--run", $run, "--step", $step)
        if ($step -eq "train") { $a += @("--lr", $LR) }
        $p = Start-Process -FilePath $py -ArgumentList $a -WorkingDirectory $here `
            -RedirectStandardOutput (Join-Path $logs "$name.log") -RedirectStandardError (Join-Path $logs "$name.err.log") -NoNewWindow -PassThru
        $null = $p.Handle
        $p.WaitForExit()
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Log ("$stamp  end   $name" + ": exit $($p.ExitCode), " + ("{0:N1}" -f ((Get-Date) - $t).TotalMinutes) + " min")
        if ($p.ExitCode -ne 0) { Log "$stamp  chain stopped: $run"; break }
    }
}
Log "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  queue done"
