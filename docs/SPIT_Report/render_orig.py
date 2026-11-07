import fitz, os

doc = fitz.open(r"G:\Mini_project\docs\SPIT_Report\original_template.pdf")
out_dir = r"G:\Mini_project\docs\SPIT_Report\orig_slides"
os.makedirs(out_dir, exist_ok=True)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    pix.save(os.path.join(out_dir, f"orig_slide_{i+1}.png"))
print(f"Rendered {len(doc)} original template slides.")
