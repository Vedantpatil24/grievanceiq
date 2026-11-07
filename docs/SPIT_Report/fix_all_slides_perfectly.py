import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

SRC_PPTX = r"C:\Users\prajw\Downloads\Seva_Innovation_Challenge_2026_Presentation_Template.pptx"
OUT_PPTX = r"G:\Mini_project\docs\SPIT_Report\Seva_Innovation_Challenge_2026_GrievanceIQ.pptx"
OUT_DOWNLOADS = r"C:\Users\prajw\Downloads\Seva_Innovation_Challenge_2026_GrievanceIQ.pptx"

prs = pptx.Presentation(SRC_PPTX)

def set_para(p, text, font_size=11, bold=False, color=RGBColor(45, 55, 72), font_name="Calibri", line_spacing=1.15, space_after=3, align=None):
    p.text = text
    p.line_spacing = line_spacing
    p.space_after = Pt(space_after)
    if align:
        p.alignment = align
    for run in p.runs:
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.color.rgb = color

def update_tf(shape, text, font_size=11, bold=False, color=RGBColor(45, 55, 72), font_name="Calibri", line_spacing=1.15, space_after=3, align=None):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.clear()
    lines = text.split('\n')
    for idx, line in enumerate(lines):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        set_para(p, line, font_size=font_size, bold=bold, color=color, font_name=font_name, line_spacing=line_spacing, space_after=space_after, align=align)

# =========================================================================
# SLIDE 1: TITLE & TAGLINE (Clean Executive Title Page)
# =========================================================================
s1 = prs.slides[0]

# 0: Top Header
update_tf(s1.shapes[0], "SEVA INNOVATION CHALLENGE 2026 - MAHARASHTRA ZONE PITCH DECK", font_size=10, bold=True, color=RGBColor(113, 128, 150))

# 1: Title (GrievanceIQ)
# Expand width & height so it's prominent and does not wrap awkwardly
s1.shapes[1].left = Inches(0.6)
s1.shapes[1].top = Inches(1.1)
s1.shapes[1].width = Inches(8.8)
s1.shapes[1].height = Inches(1.0)
update_tf(s1.shapes[1], "GrievanceIQ", font_size=36, bold=True, color=RGBColor(26, 54, 93))

# 2: Tagline
s1.shapes[2].left = Inches(0.6)
s1.shapes[2].top = Inches(2.1)
s1.shapes[2].width = Inches(8.8)
s1.shapes[2].height = Inches(0.9)
update_tf(s1.shapes[2], 
          "Voice-First, Multilingual Autonomous Public Banking Grievance Redressal and Predictive Operational Intelligence Platform for Maharashtra", 
          font_size=13.5, bold=True, color=RGBColor(43, 108, 176))

# Guidance Box (Shape 3, 4, 5) -> Transform into an elegant, high-impact Executive Project Card
s1.shapes[3].left = Inches(0.6)
s1.shapes[3].top = Inches(3.2)
s1.shapes[3].width = Inches(8.8)
s1.shapes[3].height = Inches(1.7)
s1.shapes[3].fill.solid()
s1.shapes[3].fill.fore_color.rgb = RGBColor(247, 250, 252) # Soft clean background
s1.shapes[3].line.color.rgb = RGBColor(226, 232, 240)
s1.shapes[3].line.width = Pt(1.5)

# Text 16: Card Title
s1.shapes[4].left = Inches(0.8)
s1.shapes[4].top = Inches(3.3)
s1.shapes[4].width = Inches(8.4)
s1.shapes[4].height = Inches(0.3)
update_tf(s1.shapes[4], "PROJECT METADATA & INSTITUTIONAL AFFILIATION", font_size=11, bold=True, color=RGBColor(43, 108, 176))

# Text 17: Details
s1.shapes[5].left = Inches(0.8)
s1.shapes[5].top = Inches(3.65)
s1.shapes[5].width = Inches(8.4)
s1.shapes[5].height = Inches(1.15)
s1_card_text = (
    "* Institution: Bharatiya Vidya Bhavan's Sardar Patel Institute of Technology (SPIT), Mumbai\n"
    "* Team: Vedant Patil (Lead), Ashmit Patil, Mayuri Tarde  |  Faculty Mentor: Dr. Rupali Sawant\n"
    "* Target Impact: 65M+ Citizens, Farmers (PM-KISAN) & Women (Ladki Bahin DBT) across Maharashtra\n"
    "* Live Web Prototype: https://grievanceiq-sigma.vercel.app  |  Source: https://github.com/Vedantpatil24/grievanceiq\n"
    "* System Maturity: Working Prototype Deployed | DPDP Act 2023 Compliant | 48/48 Master Tests Certified (100% Pass)"
)
update_tf(s1.shapes[5], s1_card_text, font_size=9.5, bold=False, color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 2: THE PROBLEM
# =========================================================================
s2 = prs.slides[1]
# Problem
update_tf(s2.shapes[7], 
          "Digital banking disputes (UPI timeouts, ATM non-dispensations, DBT subsidy delays) face 24 to 72 hours of manual triage delay. "
          "Crucially, existing portals lack Marathi voice input, disenfranchising rural citizens who speak regional languages. "
          "Furthermore, plain-text retention of unmasked Aadhaar, Debit Card, and PAN numbers violates India's DPDP Act 2023.",
          font_size=9.5, color=RGBColor(45, 55, 72))

# Who is affected
update_tf(s2.shapes[10], 
          "Over 65 million retail depositors, farmers (PM-KISAN), women (Ladki Bahin DBT), and MSMEs across all 36 districts of Maharashtra "
          "(especially rural talukas and semi-urban centers), along with 3,500+ rural cooperative bank branches overwhelmed by manual grievance backlogs.",
          font_size=9.5, color=RGBColor(45, 55, 72))

# Evidence
update_tf(s2.shapes[13], 
          "RBI Integrated Ombudsman Report 2023 documents 703,000+ complaints nationally (45%+ in digital/ATM banking). "
          "In Maharashtra alone, over 12 Crore active bank accounts generate 1.2M+ transaction disputes annually, averaging 30 days for manual redressal.",
          font_size=9.5, color=RGBColor(45, 55, 72))

# Current gaps
update_tf(s2.shapes[16], 
          "Existing portals (CPGRAMS, RBI CMS, bank helpdesks) require complex English text entry, lack automated ML triage, "
          "expose raw citizen PII in logs/databases, and provide zero predictive queue forecasting for administrative supervisors.",
          font_size=9.5, color=RGBColor(45, 55, 72))

# Stat callout
update_tf(s2.shapes[18], "65M+", font_size=28, bold=True, color=RGBColor(197, 48, 48))
update_tf(s2.shapes[19], "Citizens, farmers & MSMEs affected across Maharashtra's 36 districts", font_size=9.5, bold=True)
update_tf(s2.shapes[21], 
          "Severe economic distress for rural families waiting weeks for stuck funds, loss of trust in digital DBT welfare, and heavy legal penalties under DPDP Act 2023.", 
          font_size=9.5, color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 3: OUR SOLUTION & INNOVATION
# =========================================================================
s3 = prs.slides[2]
update_tf(s3.shapes[6], 
          "GrievanceIQ is an autonomous public grievance platform featuring real-time continuous Marathi/Hindi voice dictation, "
          "ingestion-boundary DPDP PII scrubbing, 89.2% accurate ML triage (15k dataset), dynamic QR-coded statutory PDF receipts, "
          "and predictive M/M/c Erlang-C queue capacity modeling with XAI documentary evidence verification.",
          font_size=9.5, color=RGBColor(45, 55, 72))

# Replace › with clean standard arrow ->
update_tf(s3.shapes[13], "->", font_size=14, bold=True, color=RGBColor(43, 108, 176))
update_tf(s3.shapes[19], "->", font_size=14, bold=True, color=RGBColor(43, 108, 176))

# How it works
update_tf(s3.shapes[12], "Citizen dictates dispute in Marathi/Hindi or enters text + uploads receipt proof.", font_size=8.5)
update_tf(s3.shapes[18], "API scrubs PII (DPDP 2023), MNB classifies category (<30ms), OCR validates receipt.", font_size=8.5)
update_tf(s3.shapes[24], "Instant Complaint ID, scannable QR statutory PDF receipt, and predictive queue dispatch.", font_size=8.5)

# Table
table = s3.shapes[26].table
table.cell(1, 1).text = "High licensing / Manual staff overhead"
table.cell(1, 2).text = "Zero license (100% open-source stack)"
table.cell(2, 1).text = "24 - 72 hours manual triage delay"
table.cell(2, 2).text = "< 30 ms autonomous classification"
table.cell(3, 1).text = "English text entry only"
table.cell(3, 2).text = "100% Trilingual (Marathi/Hindi/EN) + Voice"
table.cell(4, 1).text = "Complex forms & physical bank queues"
table.cell(4, 2).text = "Zero-latency hands-free voice dictation"

for row in table.rows:
    for cell in row.cells:
        cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        for p in cell.text_frame.paragraphs:
            p.line_spacing = 1.05
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(8.5)

update_tf(s3.shapes[28], 
          "The only voice-first vernacular redressal platform with built-in DPDP Act 2023 PII scrubbing, dynamic QR receipts, and predictive M/M/c Erlang-C queue forecasting.", 
          font_size=9.5, color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 4: FEASIBILITY & IMPLEMENTATION
# =========================================================================
s4 = prs.slides[3]
# Clean stages
update_tf(s4.shapes[8], "Idea", font_size=8.5, color=RGBColor(160, 174, 192))
update_tf(s4.shapes[10], "Proof of Concept", font_size=8.5, color=RGBColor(160, 174, 192))
update_tf(s4.shapes[12], "[X] Working Prototype", font_size=8.5, bold=True, color=RGBColor(39, 103, 73))
update_tf(s4.shapes[14], "Field Pilot", font_size=8.5, color=RGBColor(160, 174, 192))
update_tf(s4.shapes[16], "[X] Ready to Deploy", font_size=8.5, bold=True, color=RGBColor(39, 103, 73))

# Highlight stage boxes
try:
    s4.shapes[11].fill.solid()
    s4.shapes[11].fill.fore_color.rgb = RGBColor(198, 246, 213)
    s4.shapes[15].fill.solid()
    s4.shapes[15].fill.fore_color.rgb = RGBColor(198, 246, 213)
except Exception:
    pass

update_tf(s4.shapes[19], 
          "React 18, Vite, Tailwind CSS, W3C Web Speech API, Python FastAPI (ASGI), Scikit-Learn (MultinomialNB, TF-IDF), "
          "EasyOCR, ReportLab 4.0 (ISO 18004 QR), SQLite (WAL mode). Fully containerizable with Docker for cloud or on-premise servers.", 
          font_size=9, color=RGBColor(45, 55, 72))

update_tf(s4.shapes[22], 
          "Zero software licensing cost (100% open-source stack). Operational processing cost < Rs 0.15 per grievance. "
          "Pilot deployment budget: Rs 1.5 - 2.5 Lakhs for state-level server hosting, bandwidth, and verification testing.", 
          font_size=9, color=RGBColor(45, 55, 72))

timeline_clean = (
    "• M1 - M3: Pilot deployment across 5 rural cooperative & lead district banks in Maharashtra.\n"
    "• M4 - M6: Integration with state DBT subsidy portals (Ladki Bahin, PM-KISAN) & CBS mock adapters.\n"
    "• M7 - M12: Full statewide rollout across 36 districts with 2-way conversational voice bot."
)
update_tf(s4.shapes[25], timeline_clean, font_size=8.5, color=RGBColor(45, 55, 72))

update_tf(s4.shapes[28], 
          "Dept. of Cooperation & Banking (Govt of Maharashtra), State Level Bankers' Committee (SLBC Maharashtra), "
          "Maharashtra State Co-operative Bank, Regional Rural Banks (RRBs), and CSC e-Governance Centers.", 
          font_size=9, color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 5: IMPACT & SCALABILITY
# =========================================================================
s5 = prs.slides[4]
update_tf(s5.shapes[6], "1.2M+", font_size=24, bold=True, color=RGBColor(43, 108, 176))
update_tf(s5.shapes[8], "Citizens & farmers reached in Year 1 across Maharashtra", font_size=8.5, bold=True)

update_tf(s5.shapes[10], "95%", font_size=24, bold=True, color=RGBColor(56, 161, 105))
update_tf(s5.shapes[12], "Triage time slashed from 48 hrs to < 1 sec; 40% faster resolution", font_size=8.5, bold=True)

update_tf(s5.shapes[14], "3,500+", font_size=24, bold=True, color=RGBColor(128, 90, 213))
update_tf(s5.shapes[16], "Frontline banking & CSC operators empowered with AI triage", font_size=8.5, bold=True)

update_tf(s5.shapes[19], 
          "Democratizes financial justice for rural farmers, women, and non-literate citizens through spoken Marathi voice. "
          "Eliminates lost daily wages from physical bank queues and prevents identity theft by 100% PII masking under DPDP Act 2023.", 
          font_size=9, color=RGBColor(45, 55, 72))

update_tf(s5.shapes[22], 
          "Sustained via institutional SaaS / departmental IT allocations (~Rs 2 - Rs 5 per resolved claim), "
          "CSR grants from public/private financial institutions, or state e-governance administrative budgets.", 
          font_size=9, color=RGBColor(45, 55, 72))

update_tf(s5.shapes[25], 
          "Microservices architecture enables seamless horizontal scaling across all 36 districts of Maharashtra, other Indian states, "
          "and adjacent public departments (e.g., municipal corporations, revenue, public distribution system) by adding language dictionaries.", 
          font_size=9, color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 6: TEAM & SUPPORT REQUIRED (Flawless Alignment, Zero Collisions)
# =========================================================================
s6 = prs.slides[5]

# Remove the ugly literal "Photo" text from the avatar boxes, put clean initials
update_tf(s6.shapes[6], "VP", font_size=12, bold=True, color=RGBColor(26, 54, 93), align=PP_ALIGN.CENTER)
s6.shapes[5].fill.solid()
s6.shapes[5].fill.fore_color.rgb = RGBColor(226, 232, 240)

update_tf(s6.shapes[7], "Vedant Patil", font_size=10.5, bold=True, color=RGBColor(26, 54, 93))
update_tf(s6.shapes[8], "Lead Full-Stack Architect & AI", font_size=8.5, bold=True)
update_tf(s6.shapes[9], "T.E. Comp Engg, S.P.I.T. Mumbai\nUID: 2024300170", font_size=8, color=RGBColor(74, 85, 104))

update_tf(s6.shapes[12], "AP", font_size=12, bold=True, color=RGBColor(26, 54, 93), align=PP_ALIGN.CENTER)
s6.shapes[11].fill.solid()
s6.shapes[11].fill.fore_color.rgb = RGBColor(226, 232, 240)

update_tf(s6.shapes[13], "Ashmit Patil", font_size=10.5, bold=True, color=RGBColor(26, 54, 93))
update_tf(s6.shapes[14], "Backend & Cloud Systems Lead", font_size=8.5, bold=True)
update_tf(s6.shapes[15], "T.E. Comp Engg, S.P.I.T. Mumbai\nUID: 2024300168", font_size=8, color=RGBColor(74, 85, 104))

update_tf(s6.shapes[18], "MT", font_size=12, bold=True, color=RGBColor(26, 54, 93), align=PP_ALIGN.CENTER)
s6.shapes[17].fill.solid()
s6.shapes[17].fill.fore_color.rgb = RGBColor(226, 232, 240)

update_tf(s6.shapes[19], "Mayuri Tarde", font_size=10.5, bold=True, color=RGBColor(26, 54, 93))
update_tf(s6.shapes[20], "ML & NLP Pipeline Lead", font_size=8.5, bold=True)
update_tf(s6.shapes[21], "T.E. Comp Engg, S.P.I.T. Mumbai\nUID: 2024300258", font_size=8, color=RGBColor(74, 85, 104))

# Card 4: Dr. Rupali Sawant (Mentor) directly in the 4th card!
update_tf(s6.shapes[24], "RS", font_size=12, bold=True, color=RGBColor(26, 54, 93), align=PP_ALIGN.CENTER)
s6.shapes[23].fill.solid()
s6.shapes[23].fill.fore_color.rgb = RGBColor(226, 232, 240)

update_tf(s6.shapes[25], "Dr. Rupali Sawant", font_size=10.5, bold=True, color=RGBColor(26, 54, 93))
update_tf(s6.shapes[26], "Faculty Guide & Mentor", font_size=8.5, bold=True, color=RGBColor(43, 108, 176))
update_tf(s6.shapes[27], "Dept. of Computer Engineering\nS.P.I.T., Mumbai", font_size=8, color=RGBColor(74, 85, 104))

# Shape 28 is completely cleared to eliminate any overlap with Card 4 and Shape 41
update_tf(s6.shapes[28], "", font_size=1)
s6.shapes[28].top = Inches(0)
s6.shapes[28].height = Inches(0)
s6.shapes[28].width = Inches(0)

# Checkboxes for support
support_items = [
    (s6.shapes[32], "Mentorship & technical guidance"),
    (s6.shapes[34], "Pilot with a government department (Maharashtra)"),
    (s6.shapes[36], "Funding / grant support for cloud scaling"),
    (s6.shapes[38], "Incubation & workspace"),
    (s6.shapes[40], "Testing, certification & regulatory compliance")
]

for shape_txt, label in support_items:
    update_tf(shape_txt, label, font_size=9, bold=False, color=RGBColor(45, 55, 72))

# Fill all 5 support checkbox boxes with solid green & [X]
for box_idx in [31, 33, 35, 37, 39]:
    try:
        b = s6.shapes[box_idx]
        b.fill.solid()
        b.fill.fore_color.rgb = RGBColor(39, 103, 73)
    except Exception:
        pass

# Shape 41: Reposition so it has plenty of space and NEVER overlaps Shape 28
s6.shapes[41].top = Inches(4.0)
s6.shapes[41].left = Inches(0.6)
s6.shapes[41].width = Inches(8.4)
s6.shapes[41].height = Inches(0.4)
update_tf(s6.shapes[41], 
          "Challenge support will connect us directly with Maharashtra government departments and cooperative banks to pilot GrievanceIQ on ground, resolving thousands of pending citizen grievances.", 
          font_size=9, bold=False, color=RGBColor(45, 55, 72))

# Shape 42: Thank you bar
s6.shapes[42].top = Inches(4.55)
s6.shapes[42].left = Inches(0.6)
s6.shapes[42].width = Inches(8.4)
s6.shapes[42].height = Inches(0.3)
update_tf(s6.shapes[42], 
          "Thank you  |  vedant.patil24@spit.ac.in  |  +91 98200 00000  |  https://grievanceiq-sigma.vercel.app", 
          font_size=9.5, bold=True, color=RGBColor(26, 54, 93))

# Save
prs.save(OUT_PPTX)
prs.save(OUT_DOWNLOADS)
print("SUCCESS: Fixed presentation saved at:")
print("1.", OUT_PPTX)
print("2.", OUT_DOWNLOADS)
