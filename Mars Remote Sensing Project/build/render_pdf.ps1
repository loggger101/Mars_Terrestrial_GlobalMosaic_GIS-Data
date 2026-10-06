param([string]$Deck, [string]$Pdf)

# PowerPoint COM only behaves from inside a Start-Job wrapper here; a wedged
# POWERPNT poisons every retry, so the job is killed rather than waited on.
$job = Start-Job -ScriptBlock {
    param($Deck, $Pdf)
    $ErrorActionPreference = 'Stop'
    $app = New-Object -ComObject PowerPoint.Application
    try {
        $pres = $app.Presentations.Open($Deck, $true, $false, $false)
        $pres.SaveAs($Pdf, 32)          # ppSaveAsPDF
        $pres.Close()
    } finally {
        $app.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
    }
    "done"
} -ArgumentList $Deck, $Pdf

$done = Wait-Job $job -Timeout 240
if ($null -eq $done) { Stop-Job $job; "TIMEOUT" } else { Receive-Job $job }
Remove-Job $job -Force
