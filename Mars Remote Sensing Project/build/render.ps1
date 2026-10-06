param([string]$Deck, [string]$OutDir)

$job = Start-Job -ScriptBlock {
    param($Deck, $OutDir)
    $ErrorActionPreference = 'Stop'
    if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
    $app = New-Object -ComObject PowerPoint.Application
    try {
        $pres = $app.Presentations.Open($Deck, $true, $false, $false)
        $pres.SaveCopyAs($(Join-Path $OutDir 'deck.png'), 18)   # ppSaveAsPNG
        $pres.Close()
    } finally {
        $app.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
    }
    "done"
} -ArgumentList $Deck, $OutDir

$done = Wait-Job $job -Timeout 180
if ($null -eq $done) { Stop-Job $job; "TIMEOUT" } else { Receive-Job $job }
Remove-Job $job -Force
