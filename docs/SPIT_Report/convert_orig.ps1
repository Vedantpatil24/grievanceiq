$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open("C:\Users\prajw\Downloads\Seva_Innovation_Challenge_2026_Presentation_Template.pptx")
$pres.SaveAs("G:\Mini_project\docs\SPIT_Report\original_template.pdf", 32)
$pres.Close()
$ppt.Quit()
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
