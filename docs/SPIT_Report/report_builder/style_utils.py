# style_utils.py
# Document styling and layout primitives for GrievanceIQ Report

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

COLOR_PRIMARY = RGBColor(15, 23, 42)      # Deep Navy / Slate 900
COLOR_SECONDARY = RGBColor(30, 41, 59)    # Slate 800
COLOR_TEXT = RGBColor(30, 30, 30)         # Charcoal Black
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate 500
COLOR_CODE = RGBColor(15, 23, 42)         # Deep slate for code

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_cell_borders(cell, top="CCCCCC", bottom="CCCCCC", left="CCCCCC", right="CCCCCC"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{top}"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="{left}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{bottom}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="{right}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

def add_p(doc, text="", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, bold=False, italic=False, size=12, color=None, line_spacing=1.15):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.size = Pt(size)
        run.font.name = 'Times New Roman'
        if color:
            run.font.color.rgb = color
    return p

def add_h1(doc, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = 'Times New Roman'
    run.font.color.rgb = COLOR_PRIMARY
    return p

def add_h2(doc, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(13.5)
    run.font.name = 'Times New Roman'
    run.font.color.rgb = COLOR_SECONDARY
    return p

def add_h3(doc, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = 'Times New Roman'
    run.font.color.rgb = COLOR_SECONDARY
    return p

def add_styled_table(doc, headers, rows, col_widths=None, alignment=WD_TABLE_ALIGNMENT.CENTER):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = alignment
    table.autofit = False
    
    # Header row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.05
        run = p.add_run(h)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(hdr_cells[i], "1E293B")  # Slate 900
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=140, right=140)
        set_cell_borders(hdr_cells[i], top="0F172A", bottom="0F172A", left="0F172A", right="0F172A")
        
    # Data rows
    for r_idx, row in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = ""
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.05
            run = p.add_run(str(val))
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            run.font.color.rgb = COLOR_TEXT
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            set_cell_borders(row_cells[c_idx], top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")

    # Set column widths if provided
    if col_widths:
        for row in table.rows:
            for c_idx, w in enumerate(col_widths):
                if c_idx < len(row.cells):
                    row.cells[c_idx].width = Inches(w)
                    
    # Space after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(8)
    return table

def add_algorithm_box(doc, alg_num, title, requires, ensures, steps):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.02)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    set_cell_borders(cell, top="94A3B8", bottom="94A3B8", left="94A3B8", right="94A3B8")
    
    # Title
    p_title = cell.paragraphs[0]
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    run_t = p_title.add_run(f"ALGORITHM {alg_num}: {title.upper()}")
    run_t.bold = True
    run_t.font.name = "Consolas"
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = COLOR_PRIMARY
    
    # Requires / Ensures
    p_req = cell.add_paragraph()
    p_req.paragraph_format.space_before = Pt(0)
    p_req.paragraph_format.space_after = Pt(2)
    p_req.paragraph_format.line_spacing = 1.05
    run_req = p_req.add_run(f"Input: {requires}\nOutput: {ensures}")
    run_req.italic = True
    run_req.font.name = "Times New Roman"
    run_req.font.size = Pt(9.5)
    run_req.font.color.rgb = RGBColor(71, 85, 105)
    
    # Divider
    p_div = cell.add_paragraph()
    p_div.paragraph_format.space_before = Pt(2)
    p_div.paragraph_format.space_after = Pt(4)
    r_div = p_div.add_run("─" * 68)
    r_div.font.name = "Consolas"
    r_div.font.size = Pt(8)
    r_div.font.color.rgb = RGBColor(203, 213, 225)
    
    # Steps
    for step_num, step_text in enumerate(steps, 1):
        p_step = cell.add_paragraph()
        p_step.paragraph_format.space_before = Pt(1)
        p_step.paragraph_format.space_after = Pt(2)
        p_step.paragraph_format.line_spacing = 1.05
        
        # Format step number and bold keywords
        r_num = p_step.add_run(f"{step_num:2d}. ")
        r_num.bold = True
        r_num.font.name = "Consolas"
        r_num.font.size = Pt(9)
        r_num.font.color.rgb = RGBColor(100, 116, 139)
        
        r_body = p_step.add_run(step_text)
        r_body.font.name = "Consolas"
        r_body.font.size = Pt(9)
        r_body.font.color.rgb = COLOR_CODE
        
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(8)

def add_equation_box(doc, eq_str, eq_num_str):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c1, c2 = tbl.cell(0, 0), tbl.cell(0, 1)
    c1.width = Inches(5.2)
    c2.width = Inches(0.82)
    
    set_cell_background(c1, "F8FAFC")
    set_cell_background(c2, "F8FAFC")
    set_cell_margins(c1, top=80, bottom=80, left=140, right=140)
    set_cell_margins(c2, top=80, bottom=80, left=40, right=40)
    set_cell_borders(c1, top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")
    set_cell_borders(c2, top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0")
    
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run(eq_str)
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(11)
    r1.italic = True
    
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r2 = p2.add_run(eq_num_str)
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(10)
    r2.bold = True
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(6)

def add_figure_box(doc, fig_num, caption, image_path=None):
    # Auto-discover image from figures directory if image_path is None or missing
    fig_dir = "G:/Mini_project/docs/SPIT_Report/figures"
    if (not image_path or not os.path.exists(image_path)) and os.path.exists(fig_dir):
        # Try finding by figure number pattern
        try:
            num = int(fig_num)
            for fname in os.listdir(fig_dir):
                if fname.startswith(f"fig{num:02d}_") or fname.startswith(f"fig{num}_"):
                    image_path = os.path.join(fig_dir, fname)
                    break
        except (ValueError, TypeError):
            pass

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.02)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
    set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1")
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    
    if image_path and os.path.exists(image_path):
        p.add_run().add_picture(image_path, width=Inches(5.5))
    else:
        r_ph = p.add_run(f"Figure {fig_num}: {caption}")
        r_ph.italic = True
        r_ph.font.name = "Times New Roman"
        r_ph.font.size = Pt(10)
        r_ph.font.color.rgb = COLOR_MUTED
        
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(4)
    p_cap.paragraph_format.space_after = Pt(12)
    r_cap = p_cap.add_run(f"Figure {fig_num}: {caption}")
    r_cap.bold = True
    r_cap.font.name = "Times New Roman"
    r_cap.font.size = Pt(10)
    r_cap.font.color.rgb = COLOR_PRIMARY
