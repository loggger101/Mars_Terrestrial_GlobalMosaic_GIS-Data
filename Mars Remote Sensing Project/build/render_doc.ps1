param([string]$Doc, [string]$Pdf)

$job = Start-Job -ScriptBlock {
    param($Doc, $Pdf)
    $ErrorActionPreference = 'Stop'
    $app = New-Object -ComObject Word.Application
    $app.Visible = $false
    $app.DisplayAlerts = 0
    try {
        $d = $app.Documents.Open($Doc, $false, $true)
        $d.ExportAsFixedFormat($Pdf, 17)   # wdExportFormatPDF
        "pages=$($d.ComputeStatistics(2))"
        $d.Close($false)
    } finally {
        $app.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
    }
} -ArgumentList $Doc, $Pdf

$done = Wait-Job $job -Timeout 180
if ($null -eq $done) { Stop-Job $job; "TIMEOUT" } else { Receive-Job $job }
Remove-Job $job -Force
