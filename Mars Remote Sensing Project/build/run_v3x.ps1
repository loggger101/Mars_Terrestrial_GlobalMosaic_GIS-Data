# The extra v3 runs (make_v3_extras.py; D36, KB §69.82): the finished v3 model on the windows, then fresh blocks (U-Net and
# SVM), no thermal, cut only, added only, and a second draw of fresh blocks. One process per step; a chain stops at its
# first failure and the next still runs. Each step's output goes to logs\run_v3x\<step>.log, one line per step to queue.log.
# Desktop only. First: make_v3_extras.py --plan. Then, from build\:  powershell -File run_v3x.ps1 [-From <step>] [-AfterPid <pid>]
# -AfterPid waits for a process already running before the first step starts. A failed step's exit code stops its chain;
# $p.Handle is read before WaitForExit because without it Start-Process -PassThru leaves ExitCode empty, and an empty code
# reads as a failure (the first queue, 2026-11-07, stopped every chain that way).
param([string]$From = "", [int]$AfterPid = 0)
$ErrorActionPreference = "Stop"
$py = "D:\ArcGISPro\bin\Python\envs\arcgispro-py3\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$logs = Join-Path $here "logs\run_v3x"
New-Item -ItemType Directory -Force $logs | Out-Null
$queue = Join-Path $logs "queue.log"

function Log([string]$line) {   # a reader holding queue.log open must not end the queue (it did, 2026-10-25)
    for ($i = 0; $i -lt 30; $i++) {
        try { [IO.File]::AppendAllText($queue, $line + "`r`n"); return } catch { Start-Sleep -Seconds 2 }
    }
}

$chains = @(
    @("base", @("classify")),
    @("fresh", @("export", "train", "classify", "svm-train", "svm-classify")),
    @("noth", @("export", "train", "classify")),
    @("cut", @("export", "train", "classify")),
    @("add", @("export", "train", "classify")),
    @("fresh2", @("export", "train", "classify", "svm-train", "svm-classify")),
    @("rep", @("export", "train", "classify"))           # added 2026-11-09 (KB §69.89); queued as -From rep_export -AfterPid
)

$env:PYTHONDONTWRITEBYTECODE = "1"
if ($AfterPid) {
    Log "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  waiting for process $AfterPid"
    Wait-Process -Id $AfterPid -ErrorAction SilentlyContinue
    Log "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  process $AfterPid gone (its exit code is not known here; read its log)"
}
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
