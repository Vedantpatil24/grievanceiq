param(
    [string]$DocPath,
    [string]$PdfPath
)
$ErrorActionPreference = "Stop"
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $doc = $word.Documents.Open($DocPath)
    $wdFormatPDF = 17
    $doc.SaveAs([ref]$PdfPath, [ref]$wdFormatPDF)
    $doc.Close()
    $word.Quit()
    Write-Host "SUCCESS: Exported $PdfPath"
} catch {
    Write-Host "Failed: $($_.Exception.Message)"
}
