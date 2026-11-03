# Exports a Word document to PDF through Word COM; killed after 180 s.
#   render_doc.ps1 -Doc <file.docx> -Pdf <out.pdf>
param([string]$Doc, [string]$Pdf)

$job = Start-Job -ScriptBlock {
    param($Doc, $Pdf)
    $ErrorActionPreference = 'Stop'
    $app = New-Object -ComObject Word.Application
    $app.Visible = $false
    $app.DisplayAlerts = 0
    try {
        $d = $app.Documents.Open($Doc, $false, $true)
        # wdExportFormatPDF, for print, the whole document; with its title and author (IncludeDocProps, off by
        # default, left the PDF's properties empty), heading bookmarks and accessibility tags (KB §69.73)
        $d.ExportAsFixedFormat($Pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
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
