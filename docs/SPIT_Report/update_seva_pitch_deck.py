import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

SRC_PPTX = r"C:\Users\prajw\Downloads\Seva_Innovation_Challenge_2026_Presentation_Template.pptx"
OUT_PPTX = r"G:\Mini_project\docs\SPIT_Report\Seva_Innovation_Challenge_2026_GrievanceIQ.pptx"
OUT_DOWNLOADS = r"C:\Users\prajw\Downloads\Seva_Innovation_Challenge_2026_GrievanceIQ.pptx"

prs = pptx.Presentation(SRC_PPTX)

def update_tf(shape, text, font_size=None, bold=None, color=None, font_name="Calibri"):
    tf = shape.text_frame
    tf.word_wrap = True
    # grab original styling from first run if available
    orig_size = None
    orig_bold = None
    orig_color = None
    if tf.paragraphs and tf.paragraphs[0].runs:
        r = tf.paragraphs[0].runs[0]
        orig_size = r.font.size
        orig_bold = r.font.bold
        try:
            if r.font.color and r.font.color.rgb:
                orig_color = r.font.color.rgb
        except Exception:
            pass
            
    tf.clear()
    lines = text.split('\n')
    for idx, line in enumerate(lines):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = line
        p.line_spacing = 1.15
        p.space_after = Pt(3)
        for run in p.runs:
            run.font.name = font_name
            run.font.size = font_size or orig_size or Pt(11)
            run.font.bold = bold if bold is not None else (orig_bold or False)
            if color:
                run.font.color.rgb = color
            elif orig_color:
                try:
                    run.font.color.rgb = orig_color
                except Exception:
                    pass

# =========================================================================
# SLIDE 1: TITLE & TAGLINE
# =========================================================================
s1 = prs.slides[0]
update_tf(s1.shapes[1], "GrievanceIQ", font_size=Pt(28), bold=True, color=RGBColor(26, 54, 93))
update_tf(s1.shapes[2], 
          "Voice-First, Multilingual Autonomous Public Banking Grievance Redressal & Predictive Operational Intelligence Platform for Maharashtra", 
          font_size=Pt(13.5), bold=True, color=RGBColor(43, 108, 176))

# Guidance Box -> Replace with Project Details
update_tf(s1.shapes[4], "Project Overview & Institutional Affiliation", font_size=Pt(11), bold=True, color=RGBColor(26, 54, 93))
s1_meta = (
    "• Organization: Sardar Patel Institute of Technology (SPIT), Mumbai\n"
    "• Innovation Domain: Public Service Delivery, Financial Inclusion & AI Governance\n"
    "• Team: Vedant Patil, Ashmit Patil, Mayuri Tarde  |  Mentor: Dr. Rupali Sawant\n"
    "• Target Beneficiaries: 65M+ Citizens, Farmers & MSMEs across Maharashtra\n"
    "• Working Prototype Deployed: https://grievanceiq-sigma.vercel.app\n"
    "• Verified Status: DPDP Act 2023 Compliant | 48/48 Master Test Cases Certified (100% Pass)"
)
update_tf(s1.shapes[5], s1_meta, font_size=Pt(9.5), bold=False, color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 2: THE PROBLEM
# =========================================================================
s2 = prs.slides[1]
# Problem description
p_text = (
    "Digital banking disputes (UPI failures, ATM non-dispensations, DBT welfare delays) face 24 to 72 hours of manual triage delay in banks. "
    "Crucially, portals lack Marathi voice input, disenfranchising rural citizens who speak regional languages. "
    "Furthermore, plain-text retention of unmasked Aadhaar, Debit Card, and PAN numbers violates India's DPDP Act 2023."
)
update_tf(s2.shapes[7], p_text, font_size=Pt(10), color=RGBColor(45, 55, 72))

# Who is affected
who_text = (
    "Over 65 million retail depositors, farmers (PM-KISAN), women (Ladki Bahin DBT), and MSMEs across all 36 districts of Maharashtra "
    "(especially rural talukas and semi-urban centers), along with 3,500+ rural cooperative bank branches overwhelmed by manual grievance backlogs."
)
update_tf(s2.shapes[10], who_text, font_size=Pt(10), color=RGBColor(45, 55, 72))

# Evidence
ev_text = (
    "RBI Integrated Ombudsman Report 2023 records 703,000+ complaints nationally (45%+ in digital/ATM banking). "
    "In Maharashtra alone, over 12 Crore active bank accounts generate 1.2M+ transaction disputes annually, averaging 30 days for manual redressal."
)
update_tf(s2.shapes[13], ev_text, font_size=Pt(10), color=RGBColor(45, 55, 72))

# Current gaps
gaps_text = (
    "Existing portals (CPGRAMS, RBI CMS, bank helpdesks) require complex English text entry, lack automated ML triage, "
    "expose raw citizen PII in logs/databases, and provide zero predictive queue forecasting for administrative supervisors."
)
update_tf(s2.shapes[16], gaps_text, font_size=Pt(10), color=RGBColor(45, 55, 72))

# Stat callout
update_tf(s2.shapes[18], "65M+", font_size=Pt(28), bold=True, color=RGBColor(197, 48, 48))
update_tf(s2.shapes[19], "Citizens, farmers & MSMEs affected across Maharashtra's 36 districts", font_size=Pt(10), bold=True)
update_tf(s2.shapes[21], 
          "Severe economic distress for rural families waiting weeks for stuck funds, loss of trust in digital DBT welfare, and heavy legal penalties under DPDP Act 2023.", 
          font_size=Pt(9.5), color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 3: OUR SOLUTION & INNOVATION
# =========================================================================
s3 = prs.slides[2]
sol_brief = (
    "GrievanceIQ is an autonomous public grievance platform featuring real-time continuous Marathi/Hindi voice dictation, "
    "ingestion-boundary DPDP PII scrubbing, 89.2% accurate ML triage (15k dataset), dynamic QR-coded statutory PDF receipts, "
    "and predictive M/M/c Erlang-C queue capacity modeling with XAI documentary evidence verification."
)
update_tf(s3.shapes[6], sol_brief, font_size=Pt(9.5), color=RGBColor(45, 55, 72))

# How it works
update_tf(s3.shapes[12], "Citizen dictates dispute in Marathi/Hindi or enters text + uploads receipt proof.", font_size=Pt(9))
update_tf(s3.shapes[18], "API scrubs PII (DPDP 2023), MNB classifies category (<30ms), OCR validates receipt.", font_size=Pt(9))
update_tf(s3.shapes[24], "Instant Complaint ID, scannable QR statutory PDF receipt, and predictive queue dispatch.", font_size=Pt(9))

# Table
table = s3.shapes[26].table
table.cell(1, 1).text = "High licensing / Manual staff overhead"
table.cell(1, 2).text = "Zero license (100% open-source stack)"
table.cell(2, 1).text = "24–72 hours manual triage delay"
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
          font_size=Pt(9.5), color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 4: FEASIBILITY & IMPLEMENTATION
# =========================================================================
s4 = prs.slides[3]
# Mark Working Prototype & Ready to Deploy
update_tf(s4.shapes[8], "Idea", font_size=Pt(8.5), color=RGBColor(160, 174, 192))
update_tf(s4.shapes[10], "Proof of Concept", font_size=Pt(8.5), color=RGBColor(160, 174, 192))
update_tf(s4.shapes[12], "✔ Working Prototype", font_size=Pt(9), bold=True, color=RGBColor(39, 103, 73))
update_tf(s4.shapes[14], "Field Pilot", font_size=Pt(8.5), color=RGBColor(160, 174, 192))
update_tf(s4.shapes[16], "✔ Ready to Deploy", font_size=Pt(9), bold=True, color=RGBColor(39, 103, 73))

# Fill background of Shape 11 and 15 with light green
try:
    s4.shapes[11].fill.solid()
    s4.shapes[11].fill.fore_color.rgb = RGBColor(198, 246, 213)
    s4.shapes[15].fill.solid()
    s4.shapes[15].fill.fore_color.rgb = RGBColor(198, 246, 213)
except Exception:
    pass

tech_text = (
    "React 18, Vite, Tailwind CSS, W3C Web Speech API, Python FastAPI (ASGI), Scikit-Learn (MultinomialNB, TF-IDF), "
    "EasyOCR, ReportLab 4.0 (ISO 18004 QR), SQLite (WAL mode). Fully containerizable with Docker for cloud or on-premise servers."
)
update_tf(s4.shapes[19], tech_text, font_size=Pt(9.5), color=RGBColor(45, 55, 72))

cost_text = (
    "Zero software licensing cost (100% open-source stack). Operational processing cost < ₹0.15 per grievance. "
    "Pilot deployment budget: ₹1.5–2.5 Lakhs for state-level server hosting, bandwidth, and verification testing."
)
update_tf(s4.shapes[22], cost_text, font_size=Pt(9.5), color=RGBColor(45, 55, 72))

timeline_text = (
    "• M1–M3: Pilot deployment across 5 rural cooperative & lead district banks in Maharashtra.\n"
    "• M4–M6: Integration with state DBT subsidy portals (Ladki Bahin, PM-KISAN) & CBS mock adapters.\n"
    "• M7–M12: Full statewide rollout across 36 districts with 2-way conversational voice bot."
)
update_tf(s4.shapes[25], timeline_text, font_size=Pt(9), color=RGBColor(45, 55, 72))

partners_text = (
    "Dept. of Cooperation & Banking (Govt of Maharashtra), State Level Bankers' Committee (SLBC Maharashtra), "
    "Maharashtra State Co-operative Bank, Regional Rural Banks (RRBs), and CSC e-Governance Centers."
)
update_tf(s4.shapes[28], partners_text, font_size=Pt(9.5), color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 5: IMPACT & SCALABILITY
# =========================================================================
s5 = prs.slides[4]
update_tf(s5.shapes[6], "1.2M+", font_size=Pt(24), bold=True, color=RGBColor(43, 108, 176))
update_tf(s5.shapes[8], "Citizens & farmers reached in Year 1 across Maharashtra", font_size=Pt(9), bold=True)

update_tf(s5.shapes[10], "95%", font_size=Pt(24), bold=True, color=RGBColor(56, 161, 105))
update_tf(s5.shapes[12], "Triage time slashed from 48 hrs to < 1 sec; 40% faster resolution", font_size=Pt(9), bold=True)

update_tf(s5.shapes[14], "3,500+", font_size=Pt(24), bold=True, color=RGBColor(128, 90, 213))
update_tf(s5.shapes[16], "Frontline banking & CSC operators empowered with AI triage", font_size=Pt(9), bold=True)

soc_text = (
    "Democratizes financial justice for rural farmers, women, and non-literate citizens through spoken Marathi voice. "
    "Eliminates lost daily wages from physical bank queues and prevents identity theft by 100% PII masking under DPDP Act 2023."
)
update_tf(s5.shapes[19], soc_text, font_size=Pt(9.5), color=RGBColor(45, 55, 72))

sust_text = (
    "Sustained via institutional SaaS / departmental IT allocations (~₹2–₹5 per resolved claim), "
    "CSR grants from public/private financial institutions, or state e-governance administrative budgets."
)
update_tf(s5.shapes[22], sust_text, font_size=Pt(9.5), color=RGBColor(45, 55, 72))

scale_text = (
    "Microservices architecture enables seamless horizontal scaling across all 36 districts of Maharashtra, other Indian states, "
    "and adjacent public departments (e.g., municipal corporations, revenue, public distribution system) by adding language dictionaries."
)
update_tf(s5.shapes[25], scale_text, font_size=Pt(9.5), color=RGBColor(45, 55, 72))

# =========================================================================
# SLIDE 6: TEAM & SUPPORT REQUIRED
# =========================================================================
s6 = prs.slides[5]
# Team members
update_tf(s6.shapes[7], "Vedant Patil", font_size=Pt(11), bold=True, color=RGBColor(26, 54, 93))
update_tf(s6.shapes[8], "Lead Full-Stack Architect & AI Engineer", font_size=Pt(8.5), bold=True)
update_tf(s6.shapes[9], "T.E. Computer Engineering, S.P.I.T. Mumbai\nUID: 2024300170", font_size=Pt(8), color=RGBColor(74, 85, 104))

update_tf(s6.shapes[13], "Ashmit Patil", font_size=Pt(11), bold=True, color=RGBColor(26, 54, 93))
update_tf(s6.shapes[14], "Backend & Cloud Systems Lead", font_size=Pt(8.5), bold=True)
update_tf(s6.shapes[15], "T.E. Computer Engineering, S.P.I.T. Mumbai\nUID: 2024300168", font_size=Pt(8), color=RGBColor(74, 85, 104))

update_tf(s6.shapes[19], "Mayuri Tarde", font_size=Pt(11), bold=True, color=RGBColor(26, 54, 93))
update_tf(s6.shapes[20], "ML & NLP Pipeline Lead", font_size=Pt(8.5), bold=True)
update_tf(s6.shapes[21], "T.E. Computer Engineering, S.P.I.T. Mumbai\nUID: 2024300258", font_size=Pt(8), color=RGBColor(74, 85, 104))

update_tf(s6.shapes[25], "SPIT APNI Lab Cohort", font_size=Pt(11), bold=True, color=RGBColor(26, 54, 93))
update_tf(s6.shapes[26], "Testing & Verification Group", font_size=Pt(8.5), bold=True)
update_tf(s6.shapes[27], "Dept. of Computer Engineering\nS.P.I.T., Mumbai", font_size=Pt(8), color=RGBColor(74, 85, 104))

# Mentor
update_tf(s6.shapes[28], 
          "Faculty Guide & Mentor: Dr. Rupali Sawant, Department of Computer Engineering, Sardar Patel Institute of Technology (SPIT), Mumbai", 
          font_size=Pt(9), bold=True, color=RGBColor(43, 108, 176))

# Check support items
update_tf(s6.shapes[32], "✔ Mentorship & technical guidance", font_size=Pt(9), bold=True, color=RGBColor(39, 103, 73))
update_tf(s6.shapes[34], "✔ Pilot with a government department (Maharashtra)", font_size=Pt(9), bold=True, color=RGBColor(39, 103, 73))
update_tf(s6.shapes[36], "✔ Funding / grant support for cloud scaling", font_size=Pt(9), bold=True, color=RGBColor(39, 103, 73))
update_tf(s6.shapes[38], "✔ Incubation & workspace", font_size=Pt(9), bold=True, color=RGBColor(39, 103, 73))
update_tf(s6.shapes[40], "✔ Testing, certification & regulatory compliance", font_size=Pt(9), bold=True, color=RGBColor(39, 103, 73))

# Fill checkboxes with light green
for idx_box in [31, 33, 35, 37, 39]:
    try:
        s6.shapes[idx_box].fill.solid()
        s6.shapes[idx_box].fill.fore_color.rgb = RGBColor(198, 246, 213)
    except Exception:
        pass

# One line pitch
update_tf(s6.shapes[41], 
          "Challenge support will connect us directly with Maharashtra government departments and cooperative banks to pilot GrievanceIQ on ground, resolving thousands of pending citizen grievances.", 
          font_size=Pt(9), color=RGBColor(45, 55, 72))

update_tf(s6.shapes[42], 
          "Thank you  |  vedant.patil24@spit.ac.in  |  +91 98200 00000  |  https://grievanceiq-sigma.vercel.app", 
          font_size=Pt(9.5), bold=True, color=RGBColor(26, 54, 93))

# Save presentation
prs.save(OUT_PPTX)
prs.save(OUT_DOWNLOADS)
print("SUCCESS: Updated presentation saved at:")
print("1.", OUT_PPTX)
print("2.", OUT_DOWNLOADS)
