# The edifice retraining (make_v3_edf.py; D37, KB 69.107, 69.108): edf's export, training and windows, then edf's model
# on fresh's windows (edfv) and fresh's model on the standard windows (freshw). run_v3x.ps1's queue with other chains:
# one process per step, a chain stops at its first failure and the next still runs; each step's output goes to
# logs\run_v3_edf\<step>.log, one line per step to queue.log. Desktop only. First: make_v3_edf.py --negatives.
# Then, from build\:  powershell -File run_v3_edf.ps1 [-From <step>]
# $p.Handle is read before WaitForExit because without it Start-Process -PassThru leaves ExitCode empty (KB 69.83).
param([string]$From = "")
$ErrorActionPreference = "Stop"
$py = "D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$logs = Join-Path $here "logs\run_v3_edf"
New-Item -ItemType Directory -Force $logs | Out-Null
$queue = Join-Path $logs "queue.log"

function Log([string]$line) {   # a reader holding queue.log open must not end the queue (it did, 2026-10-25)
    for ($i = 0; $i -lt 30; $i++) {
        try { [IO.File]::AppendAllText($queue, $line + "`r`n"); return } catch { Start-Sleep -Seconds 2 }
    }
}

$chains = @(
    @("edf", @("export", "train", "classify")),
    @("edfv", @("classify")),
    @("freshw", @("classify"))
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
        $p = Start-Process -FilePath $py -ArgumentList @("make_v3_extras.py", "--run", $run, "--step", $step) -WorkingDirectory $here `
            -RedirectStandardOutput (Join-Path $logs "$name.log") -RedirectStandardError (Join-Path $logs "$name.err.log") -NoNewWindow -PassThru
        $null = $p.Handle                        # keeps the process handle, so ExitCode is there after the wait
        $p.WaitForExit()
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Log ("$stamp  end   $name" + ": exit $($p.ExitCode), " + ("{0:N1}" -f ((Get-Date) - $t).TotalMinutes) + " min")
        if ($p.ExitCode -ne 0) { Log "$stamp  chain stopped: $run"; break }
    }
}
Log "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  queue done"
