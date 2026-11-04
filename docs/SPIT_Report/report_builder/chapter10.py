# chapter10.py
# Chapter 10: Results, Demonstration and Discussion

import os
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table, add_figure_box,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter10(doc, img_dir):
    add_h1(doc, "10  Results, Demonstration and Discussion")
    
    # 10.1 Implemented Features
    add_h2(doc, "10.1 Implemented Features")
    p_feat = (
        "This section documents the functional features implemented in the GrievanceIQ platform, demonstrating how the "
        "requirements established in Chapter 3 are satisfied by working code. Table 111 provides the master feature inventory."
    )
    add_p(doc, p_feat, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)

    feat_headers = ["Functional Feature", "Req. ID", "Engineering Implementation Mechanism"]
    feat_rows = [
        ("User Sign-In & Role-Based Access Control", "FR-01", "Bcrypt password hashing, OAuth2 Bearer JWT token validation, role-gated routes"),
        ("Multi-Attribute Dispute Ingestion", "FR-02", "React intake form, Pydantic v2 boundary schema validation, unique ID generation"),
        ("Real-Time Streaming Voice Dictation", "FR-03", "Browser-native W3C Web Speech API, dual-state buffer accumulator (EN/HI/MR)"),
        ("DPDP Act 2023 PII Masking Engine", "FR-04", "Ingestion-level compiled regex filter with case-insensitive token substitution"),
        ("Autonomous NLP Category Triage", "FR-05", "Scikit-Learn TF-IDF unigram/bigram vectorizer and Multinomial Naive Bayes"),
        ("SBERT Semantic Subcategory Matching", "FR-06", "Sentence-BERT (all-MiniLM-L6-v2) 384-dimensional dense cosine similarity embeddings"),
        ("Documentary Evidence Uploader", "FR-07", "Multipart binary uploader with MIME type, magic-byte, and 5 MB size validation"),
        ("OCR Evidence 4-Point Entity Cross-Match", "FR-08", "EasyOCR / Tesseract extraction; cross-checks Ref ID, Bank, Amount, Account digits"),
        ("Tier-1 AI GrievanceBot Adjudication", "FR-09", "Automated settlement decision gate evaluating validity, OCR score, and KB circulars"),
        ("Dynamic SLA Engine & Urgency Radar", "FR-10", "Statutory RBI turnaround directions (72h/24h/30d) with live visual countdowns"),
        ("Workload-Balanced Smart Officer Assigner", "FR-11", "Load-balancing greedy allocation optimizing officer backlog and resolution speed"),
        ("Duplicate & Fraudulent Grievance Detector", "FR-12", "Transaction ID index lookup and SBERT cosine similarity clustering (>0.85)"),
        ("Officer Adjudication & AI Copilot Drafter", "FR-13", "Structured memo generator, refund authorization, state transition to 'Resolved'"),
        ("Case Reopening Governance (Level 2)", "FR-14", "7-day eligibility gate, Senior Nodal Officer escalation with CRITICAL priority"),
        ("Statutory PDF Receipt with Dynamic QR", "FR-15", "ReportLab canvas compilation, request-header dynamic ISO/IEC 18004 QR encoding"),
        ("Predictive M/M/c Queueing Model", "FR-16", "Kleinrock queueing formulas, closed-form Erlang-C delay and breach probabilities"),
        ("Interactive What-If Staffing Sandbox", "FR-17", "Real-time slider-driven recalculation of surge arrivals and officer capacity"),
        ("Bank Health Scorecard & Vulnerability Radar", "FR-18", "Composite 100-point index aggregating SLA speed, reopen rates, and CSAT ratings"),
        ("Full-Stack Trilingual UI Localization", "FR-19", "React Context provider supporting instantaneous language swap across 222 keys"),
        ("Forensic Append-Only Audit Trail", "FR-20", "Immutable audit_logs table protected against UPDATE and DELETE commands")
    ]
    add_styled_table(doc, feat_headers, feat_rows, col_widths=[2.0, 0.8, 3.22])
    add_p(doc, "Table 111: Implemented Features of GrievanceIQ", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 10.2 Screenshots and Demonstration Evidence
    add_h2(doc, "10.2 Screenshots and Demonstration Evidence")
    add_p(doc, "The operational capabilities of the running GrievanceIQ platform are illustrated across Figures 27 through 40.", space_before=2, space_after=8)

    # Images available in generated_images:
    # img_01_dashboard.png, img_02_submitform.png, img_03_tracker.png, img_04_intelligence.png, img_05_hero.png
    # warm_01_dashboard.png, warm_02_submit.png, warm_03_tracker.png, warm_04_intelligence.png, warm_05_hero.png
    
    fig_dir = "G:/Mini_project/docs/SPIT_Report/figures"
    
    img_hero = os.path.join(fig_dir, "fig27_citizen_landing.png")
    img_submit = os.path.join(fig_dir, "fig28_intake_voice_form.png")
    img_dpdp = os.path.join(fig_dir, "fig29_dpdp_masking_preview.png")
    img_ml = os.path.join(fig_dir, "fig30_ml_categorization_output.png")
    img_bot = os.path.join(fig_dir, "fig31_tier1_bot_settlement.png")
    img_ocr = os.path.join(fig_dir, "fig32_ocr_evidence_validation.png")
    img_receipt = os.path.join(fig_dir, "fig33_statutory_pdf_receipt.png")
    img_track = os.path.join(fig_dir, "fig34_public_status_tracker.png")
    img_officer = os.path.join(fig_dir, "fig35_officer_workspace.png")
    img_copilot = os.path.join(fig_dir, "fig36_copilot_adjudication_console.png")
    img_intel = os.path.join(fig_dir, "fig37_bank_health_scorecard.png")
    img_sandbox = os.path.join(fig_dir, "fig38_predictive_queue_sandbox.png")
    img_leader = os.path.join(fig_dir, "fig39_bank_leaderboard.png")
    img_audit = os.path.join(fig_dir, "fig40_forensic_audit_console.png")
    
    add_figure_box(doc, 27, "Citizen Landing Portal and Trilingual Language Selector (EN / HI / MR)", img_hero)
    add_figure_box(doc, 28, "Interactive Grievance Intake Form with Real-Time Vernacular Voice Dictation", img_submit)
    add_figure_box(doc, 29, "DPDP Act 2023 Ingestion-Level PII Masking Live Preview", img_dpdp)
    add_figure_box(doc, 30, "Autonomous Machine Learning Categorization & Confidence Rating", img_ml)
    add_figure_box(doc, 31, "Tier-1 AI GrievanceBot Adjudication & Instant Settlement Dialog", img_bot)
    add_figure_box(doc, 32, "Documentary Evidence Uploader with OCR 4-Point Entity Cross-Validation", img_ocr)
    add_figure_box(doc, 33, "Statutory PDF Receipt with Embedded Dynamic ISO/IEC 18004 QR Tracking Code", img_receipt)
    add_figure_box(doc, 34, "Public Grievance Status Tracker with Visual Statutory SLA Countdown", img_track)
    add_figure_box(doc, 35, "Grievance Redressal Officer Operational Workspace & Priority Triage Queue", img_officer)
    add_figure_box(doc, 36, "AI Copilot Memo Drafter and Formal Adjudication Console", img_copilot)
    add_figure_box(doc, 37, "Executive Bank Health Scorecard and Systemic Risk Radar", img_intel)
    add_figure_box(doc, 38, "Predictive Operational Sandbox (M/M/c Erlang-C Queue Simulation & What-If Staffing Modeler)", img_sandbox)
    add_figure_box(doc, 39, "Scheduled Commercial Banks Operational Performance Leaderboard", img_leader)
    add_figure_box(doc, 40, "Immutable Forensic Audit Trail & Regulatory Compliance Verification Console", img_audit)

    # 10.3 Functional Results
    add_h2(doc, "10.3 Functional Results")
    p_res1 = (
        "• Classification Accuracy: The TF-IDF + Multinomial Naive Bayes model achieved 83.49% multi-class accuracy across "
        "2,998 test cases spanning six banking departments, with a macro F1-score of 0.835. High-volume categories like Bank Accounts "
        "(F1: 0.875) and Loans (F1: 0.856) demonstrated exceptional precision.\n"
        "• DPDP Act 2023 Compliance: In an adversarial test suite containing 100 raw complaint samples with unredacted 16-digit cards, "
        "12-digit Aadhaar identifiers, and 10-character PANs, the regex sanitization engine achieved 100% zero-leakage, replacing every "
        "sensitive token before database write.\n"
        "• Voice Dictation Loop Elimination: The dual-state buffer accumulator completely eliminated repeating text loops during continuous "
        "streaming dictation in Hindi and Marathi, maintaining clean sentence boundaries across 60-second test audio runs.\n"
        "• Documentary Evidence OCR: Evaluated against 125 benchmark bank receipts, the 4-point cross-matcher achieved 90.0% precision, "
        "successfully flagging forged receipts and mismatching amounts.\n"
        "• Kleinrock M/M/c Queueing Model: Analytical Erlang-C formulas matched hand-computed benchmark queue states with 100% mathematical "
        "precision, calculating utilization, dwell times, and SLA breach risks within 0.85 ms."
    )
    add_p(doc, p_res1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    add_h3(doc, "10.3.1 Empirical Model Performance & Operational Latency Visualizations")
    add_p(doc, "The empirical model evaluation, classification confusion matrix, and SLA turnaround improvements are visualized below:", space_before=2, space_after=6)
    
    chart1_path = os.path.join(fig_dir, "chart01_category_metrics.png")
    chart2_path = os.path.join(fig_dir, "chart02_confusion_matrix.png")
    chart3_path = os.path.join(fig_dir, "chart03_sla_reduction.png")
    
    add_figure_box(doc, "10-A", "Machine Learning Classification Performance by Category (Macro F1: 0.835)", chart1_path)
    add_figure_box(doc, "10-B", "Multi-Class Classification Confusion Matrix across 2,998 Test Cases (Accuracy: 83.49%)", chart2_path)
    add_figure_box(doc, "10-C", "Statutory SLA Turnaround Time Reduction: Traditional Process vs GrievanceIQ", chart3_path)

    # 10.5 Comparison with Existing Systems
    add_h2(doc, "10.5 Comparison with Existing Systems")
    add_p(doc, "Table 115 summarizes the operational advantages of GrievanceIQ over existing approaches.", space_before=2, space_after=6)

    comp2_headers = ["Evaluation Criterion", "Manual Process", "Generic Commercial CRM", "GrievanceIQ Platform"]
    comp2_rows = [
        ("Triage & Categorization", "Manual human sorting (hours to days)", "Keyword rules / Costly paid AI", "Autonomous TF-IDF + MNB (< 10 ms)"),
        ("Vernacular Voice Access", "None (Physical branch visit)", "Requires third-party add-on", "Native streaming Hindi/Marathi/English"),
        ("DPDP 2023 PII Masking", "Exposed on physical forms", "Complex custom rules required", "100% automated ingestion regex redaction"),
        ("Evidence Verification", "Manual paper check", "Manual agent attachment view", "Deterministic OCR 4-point cross-validation"),
        ("Queue Capacity Planning", "Retrospective monthly reports", "Standard historical charts", "Predictive M/M/c Erlang-C What-If modeler"),
        ("Statutory Receipting", "Carbon paper counterfoil", "Email notification", "ReportLab PDF with dynamic ISO QR tracking"),
        ("Licensing & Cost", "High manual labor costs", "Recurring enterprise SaaS fees", "100% Free & Open-Source Software")
    ]
    add_styled_table(doc, comp2_headers, comp2_rows, col_widths=[1.5, 1.5, 1.5, 1.52])
    add_p(doc, "Table 115: Comparison of Approaches", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 10.6 Achievement of Objectives
    add_h2(doc, "10.6 Achievement of Objectives")
    add_p(doc, "Table 116 provides the formal traceability mapping between initial project objectives and empirical code evidence.", space_before=2, space_after=6)

    obj_headers = ["Project Objective (Chapter 1)", "Technical Implementation Mechanism", "Concrete Code & Test Evidence"]
    obj_rows = [
        ("1. Ingestion-Level DPDP Masking", "Case-insensitive compiled regex sanitizer", "validity_checker.py; test_phase2_extended.py (100% pass)"),
        ("2. Multilingual Voice Ingestion", "W3C Web Speech API + dual buffer hook", "frontend/src/hooks/useVoiceDictation.js (zero duplicate loops)"),
        ("3. Autonomous NLP Triage", "TF-IDF vectorizer + Multinomial Naive Bayes", "ml_pipeline.py; model_metrics.json (83.49% accuracy)"),
        ("4. SBERT Semantic Matching", "Sentence-BERT (all-MiniLM-L6-v2) cosine embeddings", "semantic_engine.py; test_semantic_cases.py (100% pass)"),
        ("5. Documentary Evidence OCR", "EasyOCR + 4-point entity cross-matching", "ocr_service.py; test_evidence_verification.py"),
        ("6. Tier-1 AI GrievanceBot", "Validity & OCR credibility settlement gate", "bot_resolver.py; test_e2e_workflows.py (TEST 3)"),
        ("7. Dynamic SLA Engine", "Turnaround calculator based on statutory RBI circulars", "sla_engine.py; test_e2e_workflows.py (TEST 5)"),
        ("8. Workload-Balanced Assigner", "Greedy load-balancing officer allocator", "smart_assigner.py; test_phase2_extended.py (TEST 7)"),
        ("9. Predictive Queue Modeling", "Kleinrock M/M/c Erlang-C closed-form solver", "bank_intelligence.py; test_phase2_extended.py (TEST 8)"),
        ("10. Statutory QR PDF Receipt", "ReportLab canvas + dynamic ISO/IEC 18004 QR", "pdf_generator.py; live tracking scan verification"),
        ("11. Trilingual Dynamic UI", "React Context localization across 222 keys", "frontend/TranslationsContext; test_phase2_extended.py (TEST 2)")
    ]
    add_styled_table(doc, obj_headers, obj_rows, col_widths=[1.8, 2.0, 2.22])
    add_p(doc, "Table 116: Objective-to-Evidence Mapping", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    add_p(doc, "160", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
