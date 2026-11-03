$ErrorActionPreference = "Stop"
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $docPath = "G:\Mini_project\docs\SPIT_Report\GrievanceIQ_SPIT_Mini_Project_Report.docx"
    $pdfPath = "G:\Mini_project\docs\SPIT_Report\GrievanceIQ_SPIT_Mini_Project_Report.pdf"
    $doc = $word.Documents.Open($docPath)
    $wdFormatPDF = 17
    $doc.SaveAs([ref]$pdfPath, [ref]$wdFormatPDF)
    $doc.Close()
    $word.Quit()
    Write-Host "SUCCESS: PDF successfully generated at $pdfPath"
} catch {
    Write-Host "Failed: $($_.Exception.Message)"
}
