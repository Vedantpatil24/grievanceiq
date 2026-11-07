$ErrorActionPreference = "Stop"
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $presPath = "C:\Users\prajw\Downloads\Seva_Innovation_Challenge_2026_GrievanceIQ.pptx"
    $pdfPath = "C:\Users\prajw\Downloads\Seva_Innovation_Challenge_2026_GrievanceIQ.pdf"
    $pdfPathDocs = "G:\Mini_project\docs\SPIT_Report\Seva_Innovation_Challenge_2026_GrievanceIQ.pdf"
    
    $presentation = $ppt.Presentations.Open($presPath, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    $ppSaveAsPDF = 32
    $presentation.SaveAs($pdfPath, $ppSaveAsPDF)
    $presentation.SaveAs($pdfPathDocs, $ppSaveAsPDF)
    $presentation.Close()
    $ppt.Quit()
    Write-Host "SUCCESS: Exported PDF to $pdfPath and $pdfPathDocs"
} catch {
    Write-Host "PowerPoint export failed or not available: $($_.Exception.Message)"
}
