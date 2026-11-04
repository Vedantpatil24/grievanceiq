# front_matter.py
# Preliminaries: Cover Page, Certificate, Declaration, Acknowledgement, Abstract, TOC, Lists, Abbreviations

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_styled_table, set_cell_background,
    set_cell_margins, set_cell_borders, COLOR_PRIMARY, COLOR_SECONDARY,
    COLOR_TEXT, COLOR_MUTED
)

def build_front_matter(doc, logo_path):
    # =========================================================================
    # 1. TITLE PAGE
    # =========================================================================
    add_p(doc, "A MINI PROJECT REPORT ON", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=12, bold=True, size=13, color=COLOR_MUTED)
    add_p(doc, "GrievanceIQ: Autonomous Banking Grievance Redressal and Predictive Operational Intelligence Platform",
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=18, bold=True, size=18, color=COLOR_PRIMARY)
    
    add_p(doc, "submitted in partial fulfillment of the requirement\nfor the award of the Degree of",
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10, italic=True, size=11)
    
    add_p(doc, "Bachelor of Technology\nin\nComputer Engineering",
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=18, bold=True, size=13, color=COLOR_SECONDARY)
    
    add_p(doc, "by", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=8, italic=True, size=11)
    
    add_p(doc, "VEDANT PATIL   (UID: 2024300170)\nASHMIT PATIL   (UID: 2024300168)\nMAYURI TARDE   (UID: 2024300258)",
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8, bold=True, size=12, color=COLOR_PRIMARY)
    add_p(doc, "Class: T.E. Computer Engineering       Division: C & D",
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=16, size=11, color=COLOR_MUTED)
    
    add_p(doc, "under the guidance of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4, italic=True, size=11)
    add_p(doc, "DR. RUPALI SAWANT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=16, bold=True, size=13, color=COLOR_PRIMARY)
    
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(14)
        p_logo.add_run().add_picture(logo_path, width=Inches(1.5))
        
    add_p(doc, "Department of Computer Engineering\nBharatiya Vidya Bhavan's\nSardar Patel Institute of Technology\n(Autonomous Institute Affiliated to University of Mumbai)\nMunshi Nagar, Andheri-West, Mumbai-400058\nUniversity of Mumbai\nAcademic Year: 2026-2027",
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=0, bold=True, size=11, color=COLOR_SECONDARY)
    
    doc.add_page_break()
    
    # =========================================================================
    # 2. APPROVAL CERTIFICATE
    # =========================================================================
    add_p(doc, "DEPARTMENT OF COMPUTER ENGINEERING\nBHARATIYA VIDYA BHAVAN'S\nSARDAR PATEL INSTITUTE OF TECHNOLOGY\n(Autonomous Institute Affiliated to University of Mumbai)\nMunshi Nagar, Andheri (West), Mumbai - 400 058",
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14, bold=True, size=11, color=COLOR_SECONDARY)
    
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(12)
        p_logo.add_run().add_picture(logo_path, width=Inches(1.2))
        
    add_p(doc, "Approval Certificate", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=16, bold=True, size=16, color=COLOR_PRIMARY)
    
    cert_text = (
        "This is to certify that the Project entitled \"GrievanceIQ: Autonomous Banking Grievance "
        "Redressal and Predictive Operational Intelligence Platform\" submitted by Vedant Patil (UID: 2024300170), "
        "Ashmit Patil (UID: 2024300168), and Mayuri Tarde (UID: 2024300258) is approved for the partial fulfillment "
        "of Mini Project / Bachelor of Technology in Computer Engineering (T.E. Computer Engineering, Divisions C & D) "
        "towards obtaining the Degree of Bachelor of Technology in Computer Engineering from University of Mumbai "
        "during the academic year 2026-2027."
    )
    add_p(doc, cert_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=36, size=11.5)
    
    # Signatures Table 1
    t_sig1 = doc.add_table(rows=2, cols=2)
    t_sig1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sig1.cell(0, 0).width = Inches(3.0)
    t_sig1.cell(0, 1).width = Inches(3.0)
    t_sig1.cell(1, 0).width = Inches(3.0)
    t_sig1.cell(1, 1).width = Inches(3.0)
    
    p00 = t_sig1.cell(0, 0).paragraphs[0]
    p00.add_run("__________________________\n(signature)\n").font.size = Pt(10)
    p00.add_run("Dr. Rupali Sawant\nProject Guide\nDepartment of Computer Engineering").bold = True
    
    p01 = t_sig1.cell(0, 1).paragraphs[0]
    p01.add_run("__________________________\n(signature)\n").font.size = Pt(10)
    p01.add_run("External Examiner\nName: ____________________\nDate: ____________________").bold = True
    
    p10 = t_sig1.cell(1, 0).paragraphs[0]
    p10.paragraph_format.space_before = Pt(36)
    p10.add_run("__________________________\n(signature)\n").font.size = Pt(10)
    p10.add_run("Dr. Dhananjay Kalbande\nHead of Department\nDepartment of Computer Engineering").bold = True
    
    p11 = t_sig1.cell(1, 1).paragraphs[0]
    p11.paragraph_format.space_before = Pt(36)
    p11.add_run("__________________________\n(signature)\n").font.size = Pt(10)
    p11.add_run("Dr. B. N. Chaudhari\nPrincipal\nSardar Patel Institute of Technology").bold = True
    
    add_p(doc, "Seal of the Institute", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=36, space_after=0, italic=True, size=11, color=COLOR_MUTED)
    
    doc.add_page_break()
    
    # =========================================================================
    # 3. DECLARATION
    # =========================================================================
    add_p(doc, "Declaration", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=20, bold=True, size=16, color=COLOR_PRIMARY)
    
    decl_text = (
        "We wish to state that the work embodied in this project titled \"GrievanceIQ: Autonomous Banking Grievance "
        "Redressal and Predictive Operational Intelligence Platform\" forms our own contribution to the work carried "
        "out under the guidance of Dr. Rupali Sawant at the Sardar Patel Institute of Technology, Department of "
        "Computer Engineering, during the academic year 2026-2027. We declare that this written submission represents "
        "our ideas in our own words and where others' ideas or words have been included, we have adequately cited and "
        "referenced the original sources. We also declare that we have adhered to all principles of academic honesty and "
        "integrity and have not misrepresented or fabricated or falsified any idea/data/fact/source in our submission. "
        "We further confirm that the implementation, mathematical models, experimental validations, and benchmark results "
        "reported here are authentic and truthful."
    )
    add_p(doc, decl_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=8, space_after=32, size=11.5)
    
    t_decl = doc.add_table(rows=2, cols=3)
    t_decl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c in range(3):
        t_decl.cell(0, c).width = Inches(2.0)
        t_decl.cell(1, c).width = Inches(2.0)
        
    names = ["Vedant Patil", "Ashmit Patil", "Mayuri Tarde"]
    uids = ["UID: 2024300170", "UID: 2024300168", "UID: 2024300258"]
    for c in range(3):
        p_c = t_decl.cell(0, c).paragraphs[0]
        p_c.add_run(f"___________________\n{names[c]}\n{uids[c]}").bold = True
        p_c.runs[0].font.size = Pt(10.5)
        
    add_p(doc, "Date: 04 November 2026\nPlace: Mumbai", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=40, space_after=0, bold=True, size=11)
    add_p(doc, "ii", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=40, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    
    doc.add_page_break()
    
    # =========================================================================
    # 4. ACKNOWLEDGEMENT
    # =========================================================================
    add_p(doc, "Acknowledgement", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=20, bold=True, size=16, color=COLOR_PRIMARY)
    
    ack1 = (
        "We wish to express our profound gratitude and deep sense of appreciation to our esteemed project guide, "
        "Dr. Rupali Sawant, Department of Computer Engineering, Sardar Patel Institute of Technology, for her invaluable "
        "guidance, technical mentorship, constructive critique, and continuous encouragement throughout the conceptualization, "
        "algorithmic formulation, full-stack software development, and validation of GrievanceIQ. Her rigorous standards "
        "in software engineering, privacy verification, and mathematical modelling were pivotal to the success of this endeavor."
    )
    ack2 = (
        "We extend our sincere thanks to Dr. Dhananjay Kalbande, Professor and Head of the Department of Computer Engineering, "
        "for providing state-of-the-art computational infrastructure, academic support, and fostering a vibrant departmental research "
        "ecosystem that inspired our focus on national BFSI challenges."
    )
    ack3 = (
        "We express our sincere indebtedness to our respected Principal, Dr. B. N. Chaudhari, for his visionary institutional "
        "leadership and for establishing the APNI Leap initiative at Sardar Patel Institute of Technology, which bridges "
        "undergraduate classroom theories in Operating Systems, Networks, and Algorithms with impactful real-world societal systems."
    )
    ack4 = (
        "We also convey our appreciation to all faculty members, laboratory instructors, and administrative staff of the "
        "Department of Computer Engineering for their continuous assistance. Finally, we thank our parents, family members, and "
        "peers for their steadfast moral support, understanding, and encouragement throughout the course of this project."
    )
    add_p(doc, ack1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=12, size=11.5)
    add_p(doc, ack2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=12, size=11.5)
    add_p(doc, ack3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=12, size=11.5)
    add_p(doc, ack4, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=24, size=11.5)
    
    add_p(doc, "Vedant Patil (2024300170)\nAshmit Patil (2024300168)\nMayuri Tarde (2024300258)\nDepartment of Computer Engineering\nS.P.I.T., Mumbai",
          align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=14, space_after=0, bold=True, size=11)
    add_p(doc, "iii", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=30, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    
    doc.add_page_break()
    
    # =========================================================================
    # 5. ABSTRACT
    # =========================================================================
    add_p(doc, "Abstract", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=16, bold=True, size=16, color=COLOR_PRIMARY)
    
    p_abs1 = (
        "The rapid digitization of the Indian banking, financial services, and insurance (BFSI) landscape---spearheaded by "
        "the Unified Payments Interface (UPI), immediate payment services, and mobile banking applications---has broadened credit "
        "and retail payment supply to millions of citizens. However, this massive transactional throughput is accompanied by a severe "
        "escalation in payment failures, unauthorized electronic debits, ATM cash dispensing anomalies, and turnaround delays. Aggrieved "
        "depositors face immense friction navigating manual customer service queues, obscure escalation matrices, and English-centric "
        "static portals. Furthermore, citizens frequently paste unredacted 16-digit payment card numbers, 12-digit Aadhaar identifiers, "
        "and Permanent Account Numbers (PAN) into complaint descriptions, causing widespread compliance infractions under India's "
        "Digital Personal Data Protection (DPDP) Act of 2023. Concurrently, bank operational executives lack forward-looking analytical "
        "tools to forecast queue congestion, predict Service Level Agreement (SLA) breaches, or dynamically balance frontline officer workloads."
    )
    p_abs2 = (
        "GrievanceIQ (Autonomous Banking Grievance Redressal and Predictive Operational Intelligence Platform) addresses these challenges "
        "through an end-to-end, privacy-hardened, and mathematically grounded architecture. The system introduces an ingestion-level "
        "regex sanitization pipeline that enforces case-insensitive, zero-loss masking of payment cards, Aadhaar, and PAN identifiers "
        "prior to database persistence or logging. To dismantle linguistic barriers, GrievanceIQ embeds a browser-native streaming voice "
        "dictation interface atop the W3C Web Speech API, featuring buffer-isolated state updates that eliminate transcript duplication loops "
        "across English, Hindi (hi-IN), and Marathi (mr-IN)."
    )
    p_abs3 = (
        "Incoming disputes are autonomously triaged by an NLP categorization pipeline combining Term Frequency-Inverse Document Frequency "
        "(TF-IDF) unigram/bigram tokenization with a Multinomial Naive Bayes classifier, validated against Sentence-BERT (all-MiniLM-L6-v2) "
        "embeddings for fine-grained subcategory prediction and historical dispute clustering. For documentary evidence verification, "
        "GrievanceIQ incorporates an optical character recognition (OCR) engine that extracts structured financial entities from transaction "
        "slips, passbooks, and ATM failure logs, executing a deterministic 4-point cross-validation (transaction reference, bank identity, "
        "account digits, and disputed amount) to score claim credibility."
    )
    p_abs4 = (
        "At the operational intelligence tier, GrievanceIQ operationalizes Kleinrock's M/M/c multi-server queueing theory via the Erlang-C "
        "analytical formulation. The engine computes real-time queue dwell times, traffic intensities, and statutory SLA breach probabilities, "
        "powering an interactive 'What-If' staffing sandbox that enables branch managers to simulate surge conditions and determine optimal "
        "officer allocations. For each registered grievance, the platform compiles a tamper-evident statutory PDF receipt embedding an "
        "ISO/IEC 18004 dynamic 2D QR code pointing to live, unauthenticated case status endpoints."
    )
    p_abs5 = (
        "The software architecture couples an asynchronous Python FastAPI backend utilizing SQLAlchemy ORM and SQLite/PostgreSQL with "
        "a reactive single-page frontend built on React 18, Vite, and Tailwind CSS. The system has been validated across a master suite of "
        "48 automated tests covering end-to-end complaint lifecycles, PII zero-leakage security, OCR precision, and SLA countdowns. On empirical "
        "benchmarks, the ML triage engine achieved 83.49% multi-class accuracy across 2,998 test records with a macro F1-score of 0.835, "
        "and sub-150ms endpoint latencies. GrievanceIQ is designed as an operational assistive triage prototype; final financial reversals "
        "and binding legal settlements remain under the formal jurisdiction of scheduled commercial banks and the Reserve Bank of India (RBI) "
        "Ombudsman."
    )
    add_p(doc, p_abs1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8, size=11)
    add_p(doc, p_abs2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8, size=11)
    add_p(doc, p_abs3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8, size=11)
    add_p(doc, p_abs4, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8, size=11)
    add_p(doc, p_abs5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=12, size=11)
    add_p(doc, "iv", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    
    doc.add_page_break()
    
    # =========================================================================
    # 6. TABLE OF CONTENTS
    # =========================================================================
    add_p(doc, "Contents", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=16, bold=True, size=16, color=COLOR_PRIMARY)
    
    toc_data = [
        ("Abstract", "iv"),
        ("List of Figures", "x"),
        ("List of Tables", "xii"),
        ("List of Abbreviations and Symbols", "xiii"),
        ("1   Introduction and Problem Definition", "1"),
        ("    1.1  Project Background", "1"),
        ("    1.2  Problem Statement", "1"),
        ("    1.3  Motivation", "2"),
        ("    1.4  Objectives", "2"),
        ("    1.5  Scope of the Project", "3"),
        ("         1.5.1  Features Included", "3"),
        ("         1.5.2  Features Outside the Scope", "4"),
        ("         1.5.3  Intended Users", "4"),
        ("         1.5.4  Operating Environment", "4"),
        ("         1.5.5  Expected Scale of Operation", "5"),
        ("    1.6  Proposed Solution", "5"),
        ("    1.7  Novelty and Originality", "6"),
        ("    1.8  Feasibility Analysis", "6"),
        ("         1.8.1  Technical Feasibility", "6"),
        ("         1.8.2  Economic Feasibility", "7"),
        ("         1.8.3  Operational Feasibility", "7"),
        ("         1.8.4  Time and Resource Feasibility", "7"),
        ("    1.9  Social Relevance and Practical Applications", "7"),
        ("    1.10 Success Criteria and Key Performance Indicators (KPIs)", "8"),
        ("2   Literature Review and Study of Existing Systems", "10"),
        ("    2.1  Study of Existing Systems", "10"),
        ("    2.2  Review of Research Papers and Technical Resources", "11"),
        ("    2.3  Comparative Analysis", "14"),
        ("    2.4  Limitations of Existing Systems", "15"),
        ("    2.5  Identified Research or Engineering Gap", "16"),
        ("    2.6  Proposed Improvements", "16"),
        ("3   Software Requirements Specification (SRS)", "18"),
        ("    3.1  Purpose and Scope of the SRS", "18"),
        ("    3.2  Intended Users and Stakeholders", "19"),
        ("    3.3  Overall Product Description", "19"),
        ("    3.4  Functional Requirements (FR-01 to FR-20)", "21"),
        ("    3.5  Non-Functional Requirements", "30"),
        ("    3.6  Hardware and Software Requirements", "33"),
        ("    3.7  Constraints and Assumptions", "35"),
        ("    3.8  Use Cases and User Stories", "36"),
        ("4   System Architecture and Detailed Design", "40"),
        ("    4.1  Overall System Architecture", "40"),
        ("    4.2  Component and Module Description", "41"),
        ("    4.3  Architecture Selection and Justification", "45"),
        ("    4.4  Data Flow Diagrams (DFD Level 0, Level 1, Level 2)", "47"),
        ("    4.5  UML Diagrams (Use Case, Class, Sequence, Activity, State, Flow)", "60"),
        ("    4.6  Database Design (Schema, Normalization, Indexing, Records)", "73"),
        ("    4.7  Security and Error Handling Design", "95"),
        ("5   Algorithm Design and Data Structures", "97"),
        ("    5.1  Identification of Critical Operations", "97"),
        ("    5.2  Algorithm Design (Algorithms 1 to 16)", "99"),
        ("    5.3  Flowcharts and State Transitions", "107"),
        ("    5.4  Data Structure Selection", "107"),
        ("    5.5  Algorithm Selection and Justification", "108"),
        ("    5.6  Time Complexity Analysis", "111"),
        ("    5.7  Space Complexity Analysis", "117"),
        ("    5.8  Optimization Opportunities", "122"),
        ("6   Subject-Wise Engineering Concepts and APNI Leap Alignment", "126"),
        ("    6.1  Software Engineering", "126"),
        ("    6.2  Computer Networks", "127"),
        ("    6.3  Database Management Systems", "127"),
        ("    6.4  Operating Systems", "128"),
        ("    6.5  Data Structures", "129"),
        ("    6.6  Design and Analysis of Algorithms", "130"),
        ("    6.7  Cloud Computing", "131"),
        ("    6.8  Master Mapping of Subjects to Project Implementation", "131"),
        ("7   Implementation and Module-Wise Coding", "134"),
        ("    7.1  Development Environment and Tools", "134"),
        ("    7.2  Overall Implementation Strategy", "134"),
        ("    7.3  Module-Wise Implementation (M0 to M7)", "135"),
        ("    7.4  Front-End Implementation", "141"),
        ("    7.5  Back-End Implementation", "142"),
        ("    7.6  Database Implementation", "142"),
        ("    7.7  Communication and Concurrency Implementation", "143"),
        ("    7.8  Git Repository Setup and Member Contributions", "143"),
        ("    7.9  Integration of Modules", "144"),
        ("    7.10 Implementation Challenges and Resolutions", "145"),
        ("8   Scalability, Performance and Resource Management", "147"),
        ("    8.1  Scalability Requirements", "147"),
        ("    8.2  Workload and Load Model", "147"),
        ("    8.3  Resource Utilization", "148"),
        ("    8.4  Concurrent Processing", "148"),
        ("    8.5  Scheduling and Synchronization Analysis", "149"),
        ("    8.6  Performance Measurement", "149"),
        ("    8.7  Performance Results", "149"),
        ("    8.8  Bottleneck Identification", "150"),
        ("    8.9  Optimization and Improvement", "150"),
        ("    8.10 Cloud Deployment and Resource Utilization", "151"),
        ("    8.11 Scalability Limitations", "152"),
        ("9   Testing and Validation", "153"),
        ("    9.1  Testing Strategy", "153"),
        ("    9.2  Unit Testing", "153"),
        ("    9.3  Integration Testing", "154"),
        ("    9.4  Functional Testing", "154"),
        ("    9.5  Non-Functional Testing", "154"),
        ("    9.6  Boundary and Invalid-Input Testing", "155"),
        ("    9.7  Concurrency and Stress Testing", "156"),
        ("    9.8  Test Case Specification (TC-01 to TC-23)", "156"),
        ("    9.9  Defect Identification and Resolution", "158"),
        ("    9.10 Validation Against KPIs", "158"),
        ("    9.11 Limitations and Untested Scenarios", "159"),
        ("10  Results, Demonstration and Discussion", "160"),
        ("    10.1 Implemented Features", "160"),
        ("    10.2 Screenshots and Demonstration Evidence", "161"),
        ("    10.3 Functional Results", "165"),
        ("    10.4 Performance Results", "167"),
        ("    10.5 Comparison with Existing Systems", "167"),
        ("    10.6 Achievement of Objectives", "168"),
        ("    10.7 Discussion of Findings", "169"),
        ("    10.8 Practical Applicability", "170"),
        ("11  Conclusion and Future Scope", "171"),
        ("    11.1 Conclusion", "171"),
        ("    11.2 Achievement of Objectives", "171"),
        ("    11.3 Major Engineering Contributions", "172"),
        ("    11.4 Current Limitations", "172"),
        ("    11.5 Future Enhancements", "173"),
        ("    11.6 Lessons Learned", "173"),
        ("References", "175")
    ]
    
    add_styled_table(doc, ["Section / Chapter Topic", "Page"], toc_data, col_widths=[5.0, 1.0])
    add_p(doc, "v", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    
    doc.add_page_break()
    
    # =========================================================================
    # 7. LIST OF FIGURES & LIST OF TABLES
    # =========================================================================
    add_p(doc, "List of Figures", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=14, bold=True, size=16, color=COLOR_PRIMARY)
    figures_data = [
        ("1", "Overall System Architecture of GrievanceIQ", "41"),
        ("2", "Level 0 DFD: Context Diagram", "48"),
        ("3", "Level 1 DFD, Diagram 1A: Intake, PII Redaction & NLP Triage", "49"),
        ("4", "Level 1 DFD, Diagram 1B: Evidence OCR & Bot Resolution", "50"),
        ("5", "Level 1 DFD, Diagram 1C: Officer Assignment & SLA Monitoring", "51"),
        ("6", "Level 1 DFD, Diagram 1D: Predictive Queueing, Audit & Receipt", "51"),
        ("7", "Level 2 DFD: Process 1.0, Intake and DPDP PII Sanitization", "53"),
        ("8", "Level 2 DFD: Process 2.0, OCR Extraction & 4-Point Entity Cross-Match", "54"),
        ("9", "Level 2 DFD: Process 3.0, TF-IDF and SBERT Classification Engine", "55"),
        ("10", "Level 2 DFD: Process 4.0, Kleinrock M/M/c Predictive Queue Simulator", "56"),
        ("11", "Level 2 DFD: Process 5.0, Officer Adjudication & Resolution Memo", "57"),
        ("12", "Level 2 DFD: Process 6.0, ReportLab PDF Receipt & Dynamic QR Encoding", "58"),
        ("13", "Relational Entity-Relationship Diagram (Master ERD across 18 Tables)", "59"),
        ("14", "Functional Dependency Graph & 3NF/BCNF Normalization Decomposition", "60"),
        ("15", "Use Case Diagram of GrievanceIQ", "61"),
        ("16", "Class Diagram, Part 1: Service & Orchestration Layer", "62"),
        ("17", "Class Diagram, Part 2: Relational Domain Entity Model", "63"),
        ("18", "Sequence Diagram, Part 1: Ingestion, Voice Dictation & Triage", "64"),
        ("19", "Sequence Diagram, Part 2: Tier-1 Bot Adjudication & Escalation", "65"),
        ("20", "Activity Diagram, Part 1: Multi-Attribute Intake & Redaction", "67"),
        ("21", "Activity Diagram, Part 2: Document Verification & Resolution", "68"),
        ("22", "State Machine Diagram, Part 1: Grievance Lifecycle Pipeline", "69"),
        ("23", "State Machine Diagram, Part 2: Officer Assignment Lifecycle", "70"),
        ("24", "User Flow Diagram, Part 1: Complainant Mobile & Web Flow", "71"),
        ("25", "User Flow Diagram, Part 2: Bank Officer Adjudication Flow", "72"),
        ("26", "Entity-Relationship Diagram of GrievanceIQ", "73"),
        ("26-B", "Database Indexing & B-Tree Query Execution Plan", "74"),
        ("27", "Citizen Landing Portal and Trilingual Language Selector", "161"),
        ("28", "Interactive Complaint Filing Form with Real-Time Voice Dictation", "161"),
        ("29", "DPDP Act 2023 Ingestion-Level PII Masking Live Preview", "162"),
        ("30", "Autonomous ML Categorization and Confidence Rating", "162"),
        ("31", "Tier-1 AI GrievanceBot Adjudication and Immediate Settlement", "162"),
        ("32", "Documentary Evidence Uploader with OCR 4-Point Entity Validation", "163"),
        ("33", "Statutory PDF Receipt with Dynamic ISO/IEC 18004 QR Tracking Code", "163"),
        ("34", "Public Grievance Status Tracker with Visual SLA Breach Countdown", "163"),
        ("35", "Grievance Redressal Officer Workspace and Priority Queue", "164"),
        ("36", "AI Copilot Memo Drafter and Formal Adjudication Console", "164"),
        ("37", "Executive Bank Health Scorecard and Systemic Risk Radar", "164"),
        ("38", "Predictive Operational Sandbox (M/M/c Erlang-C Staffing Modeler)", "165"),
        ("39", "Scheduled Commercial Banks Operational Leaderboard", "165"),
        ("40", "Immutable Append-Only Forensic Audit Trail Viewer", "165"),
        ("10-A", "Machine Learning Classification Performance by Category", "166"),
        ("10-B", "Multi-Class Classification Confusion Matrix across 2,998 Test Cases", "167"),
        ("10-C", "Statutory SLA Turnaround Time Reduction: Traditional vs GrievanceIQ", "168"),
        ("41", "Turnitin Plagiarism Report: 9% Overall Similarity Index", "169")
    ]
    add_styled_table(doc, ["Figure #", "Figure Title / Caption Description", "Page"], figures_data, col_widths=[0.8, 4.4, 0.8])
    add_p(doc, "x", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    
    doc.add_page_break()
    
    add_p(doc, "List of Tables", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=14, bold=True, size=16, color=COLOR_PRIMARY)
    tables_data = [
        ("3", "Key Performance Indicators and Target Benchmarks", "8"),
        ("4", "Comparative Analysis of Grievance Redressal Frameworks", "14"),
        ("5", "Intended Users and Primary Stakeholder Roles", "19"),
        ("6", "Six-Stage Autonomous Grievance Processing Pipeline", "20"),
        ("33", "Non-Functional Performance and Latency Requirements", "30"),
        ("34", "Security and Statutory DPDP Act Privacy Requirements", "31"),
        ("35", "System Business Rules and Operational Invariants", "32"),
        ("36", "Full-Stack Development and Production Runtime Stack", "33"),
        ("37", "Algorithmic Libraries and AI/ML Components", "34"),
        ("38", "Principal RESTful API Endpoints Directory", "34"),
        ("39", "Architecture Open Items and Production Roadmap (TBD)", "36"),
        ("49", "Comprehensive User Stories Specification", "39"),
        ("51", "Data Flow Diagram Relational Data Stores", "47"),
        ("52", "ER-to-Relational Mapping and Cardinality Rules", "75"),
        ("53", "Relational Foreign Key and Cardinality Summary", "76"),
        ("54", "Primary Key Specifications Across 18 Tables", "77"),
        ("55", "Foreign Key Referential Action Specifications (CASCADE vs SET NULL)", "78"),
        ("56", "Relational Database CHECK Constraints", "80"),
        ("57", "Nullable Relational Attributes and Justifications", "80"),
        ("58", "Relational Column DEFAULT Constraints", "81"),
        ("59", "Relational Data-Type Precision and Boundary Constraints", "81"),
        ("60", "Role-Based Access Control (RBAC) and Security Policies", "82"),
        ("61", "Application-Level Data Integrity Rules", "83"),
        ("62", "Summary of System Integrity Mechanisms", "83"),
        ("63", "Functional Dependencies and Normal Form Analysis (3NF/BCNF)", "85"),
        ("64", "Relational Database Anomalies Prevented by Schema Design", "86"),
        ("65", "Currently Implemented Database Indexes", "87"),
        ("66", "Primary Application Access Patterns and Query Shapes", "88"),
        ("67", "Proposed Secondary Performance Indexes", "89"),
        ("68", "Comprehensive Indexing Strategy Summary", "91"),
        ("69", "Operational Data Volume in Demonstration Database", "91"),
        ("70", "Sample Records: complaints and users", "92"),
        ("71", "Sample Records: evidence_docs and ocr_extractions", "92"),
        ("72", "Sample Records: predictions and similar_complaints", "93"),
        ("73", "Sample Records: audit_logs and resolutions", "94"),
        ("80", "Mathematical Notation for Time Complexity Analysis", "112"),
        ("81", "Comprehensive Time Complexity Summary for Algorithms 1-16", "112"),
        ("82", "Mathematical Notation for Space Complexity Analysis", "117"),
        ("83", "Comprehensive Space Complexity Summary for Algorithms 1-16", "118"),
        ("84", "Master Mapping of APNI Leap Subjects to Implementation", "131"),
        ("85", "Full Development Environment and Version Directory", "134"),
        ("95", "Frontend Application Views and Routing Table", "141"),
        ("96", "Backend RESTful Endpoints and HTTP Verbs", "142"),
        ("97", "Group Member Responsibilities and Module Contributions", "144"),
        ("98", "Processing Pipeline Execution Stages and Integration", "144"),
        ("99", "Technical Implementation Challenges and Mitigations", "145"),
        ("100", "System Scalability and Concurrency Limits", "147"),
        ("101", "Demonstration Workload and Experimental Data Volume", "147"),
        ("102", "Empirically Measured Latencies vs Target Benchmarks", "149"),
        ("104", "Architectural Optimizations and Empirical Speedups", "151"),
        ("106", "Test Suite Categories and Verification Scope", "153"),
        ("107", "Functional Requirement Test Coverage Matrix (FR-01 to FR-20)", "154"),
        ("108", "Boundary Condition and Invalid Input Scenarios", "155"),
        ("109", "Representative Master Test Cases Specification (TC-01 to TC-23)", "156"),
        ("110", "Final Validation of System Metrics Against Target KPIs", "158"),
        ("111", "Master Inventory of Implemented System Features", "160"),
        ("115", "Comparative Matrix: GrievanceIQ vs Existing Industry Portals", "168"),
        ("116", "Project Objective to Empirical Code Evidence Mapping", "168"),
        ("117", "Final Status of Project Engineering Objectives", "171")
    ]
    add_styled_table(doc, ["Table #", "Table Title / Context Description", "Page"], tables_data, col_widths=[0.8, 4.4, 0.8])
    add_p(doc, "xii", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    
    doc.add_page_break()
    
    # =========================================================================
    # 8. LIST OF ABBREVIATIONS AND SYMBOLS
    # =========================================================================
    add_p(doc, "List of Abbreviations and Symbols", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=14, bold=True, size=16, color=COLOR_PRIMARY)
    
    add_p(doc, "Abbreviations", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=6, bold=True, size=12, color=COLOR_SECONDARY)
    abbr_data = [
        ("AI", "Artificial Intelligence"),
        ("API", "Application Programming Interface"),
        ("ASGI", "Asynchronous Server Gateway Interface (Python Uvicorn)"),
        ("BFSI", "Banking, Financial Services, and Insurance"),
        ("CBS", "Core Banking Solution (e.g., Infosys Finacle, TCS BaNCS)"),
        ("CPGRAMS", "Centralized Public Grievance Redress and Monitoring System"),
        ("CSRF", "Cross-Site Request Forgery"),
        ("DFD", "Data Flow Diagram"),
        ("DPDP", "Digital Personal Data Protection Act of 2023 (India)"),
        ("FIFO", "First In, First Out"),
        ("IMPS", "Immediate Payment Service"),
        ("ISO", "International Organization for Standardization"),
        ("JWT", "JSON Web Token"),
        ("KYC", "Know Your Customer"),
        ("ML", "Machine Learning"),
        ("MNB", "Multinomial Naive Bayes"),
        ("M/M/c", "Kendall's Notation for Multi-Server Queue with c Parallel Servers"),
        ("NLP", "Natural Language Processing"),
        ("NPCI", "National Payments Corporation of India"),
        ("OCR", "Optical Character Recognition"),
        ("ORM", "Object-Relational Mapping (SQLAlchemy)"),
        ("PAN", "Permanent Account Number / Primary Account Number"),
        ("PCM", "Pulse Code Modulation"),
        ("PII", "Personally Identifiable Information"),
        ("QR", "Quick Response (2D Barcode ISO/IEC 18004)"),
        ("RAG", "Retrieval-Augmented Generation"),
        ("RBAC", "Role-Based Access Control"),
        ("RBI", "Reserve Bank of India"),
        ("RB-IOS", "Reserve Bank - Integrated Ombudsman Scheme 2021"),
        ("REST", "Representational State Transfer"),
        ("SBERT", "Sentence Bidirectional Encoder Representations from Transformers"),
        ("SLA", "Service Level Agreement"),
        ("SQL", "Structured Query Language"),
        ("SRS", "Software Requirements Specification"),
        ("TF-IDF", "Term Frequency - Inverse Document Frequency"),
        ("TLS", "Transport Layer Security"),
        ("UI / UX", "User Interface / User Experience"),
        ("UID", "Unique Identification / Student Enrollment Number"),
        ("UPI", "Unified Payments Interface"),
        ("W3C", "World Wide Web Consortium"),
        ("WAL", "Write-Ahead Logging (SQLite High-Concurrency Mode)")
    ]
    add_styled_table(doc, ["Abbreviation", "Full Form / Technical Meaning"], abbr_data, col_widths=[1.5, 4.5])
    
    add_p(doc, "Symbols and Units", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=6, bold=True, size=12, color=COLOR_SECONDARY)
    sym_data = [
        ("lambda", "Mean complaint arrival rate (complaints per hour)"),
        ("mu", "Mean service/resolution rate per officer (complaints per officer per hour)"),
        ("c", "Number of active, parallel grievance redressal officers"),
        ("rho", "Traffic intensity / system utilization (lambda / (c * mu))"),
        ("P_0", "Probability of zero complaints in the redressal system"),
        ("C(c, a)", "Erlang-C probability of an arriving grievance having to wait in queue"),
        ("W_q", "Expected waiting time in queue before an officer commences investigation"),
        ("W", "Expected total dwell time in system (W_q + 1 / mu)"),
        ("L_q", "Expected number of pending grievances waiting in queue"),
        ("L", "Expected total number of grievances currently in system"),
        ("T_SLA", "Statutory SLA threshold duration (hours)"),
        ("N", "Total number of documents in classification corpus"),
        ("V", "Size of NLP vocabulary dictionary"),
        ("alpha", "Laplace smoothing parameter (alpha = 1.0)"),
        ("ms", "Millisecond (10^-3 seconds)"),
        ("s", "Second"),
        ("INR (Rs.)", "Indian Rupee (ISO 4217 Currency Code)")
    ]
    add_styled_table(doc, ["Symbol", "Mathematical / Operational Meaning"], sym_data, col_widths=[1.5, 4.5])
    
    add_p(doc, "xiii", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
