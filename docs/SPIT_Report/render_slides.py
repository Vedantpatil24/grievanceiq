import fitz, os, shutil

pdf_path = r"C:\Users\prajw\Downloads\Seva_Innovation_Challenge_2026_GrievanceIQ.pdf"
desktop_path = r"C:\Users\prajw\OneDrive\Desktop\Seva_Innovation_Challenge_2026_GrievanceIQ.pdf"
repo_path = r"G:\Mini_project\docs\SPIT_Report\Seva_Innovation_Challenge_2026_GrievanceIQ.pdf"

shutil.copyfile(pdf_path, desktop_path)
shutil.copyfile(pdf_path, repo_path)

doc = fitz.open(pdf_path)
out_dir = r"G:\Mini_project\docs\SPIT_Report\rendered_slides"
os.makedirs(out_dir, exist_ok=True)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    pix.save(os.path.join(out_dir, f"slide_{i+1}.png"))
print(f"Rendered {len(doc)} slides successfully.")
