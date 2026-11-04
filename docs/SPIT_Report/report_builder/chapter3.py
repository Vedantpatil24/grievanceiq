# chapter3.py
# Chapter 3: Software Requirements Specification (SRS)

import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter3(doc):
    add_h1(doc, "3   Software Requirements Specification (SRS)")
    
    # 3.1 Purpose and Scope of the SRS
    add_h2(doc, "3.1 Purpose and Scope of the SRS")
    p_srs_p = (
        "This Software Requirements Specification (SRS) delineates the functional, non-functional, interface, security, "
        "and operational requirements governing Version 1.0 of the GrievanceIQ platform. It serves as the authoritative technical "
        "contract between engineering design and practical deployment, providing explicit verification criteria, boundary invariants, "
        "and traceability matrices for academic and institutional evaluation. In all requirement specifications, the auxiliary verb "
        "'shall' denotes a mandatory contractual requirement, while 'should' denotes a recommended design enhancement."
    )
    add_p(doc, p_srs_p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)

    add_h3(doc, "3.1.1 In Scope")
    add_p(doc, "The functional scope of GrievanceIQ encompasses:", space_before=2, space_after=4)
    scope_in = [
        "• Multi-attribute dispute intake with manual entry, receipt attachment, and browser-native voice dictation.",
        "• Ingestion-level regular expression redaction of 16-digit payment card numbers, 12-digit Aadhaar identifiers, and 10-character Permanent Account Numbers (PAN) to guarantee 100% compliance with India's DPDP Act of 2023.",
        "• Autonomous NLP categorization of complaints into high-level banking departments using TF-IDF and Multinomial Naive Bayes.",
        "• SBERT semantic embedding analysis for granular subcategory prediction and similar complaint clustering.",
        "• Deterministic optical character recognition (OCR) and 4-point entity cross-matching against uploaded transaction proofs.",
        "• Tier-1 AI GrievanceBot automated resolution gate offering instant settlement workflows for high-validity routine disputes.",
        "• Dynamic calculation of statutory SLA countdowns (24h/72h/30d) based on RBI customer liability directions.",
        "• Workload-balanced smart officer assignment algorithm prioritizing department specialty, active backlog, and historical speed.",
        "• Senior Nodal Officer (Level 2) escalation and governance for reopened grievances.",
        "• Predictive operations modeling using Kleinrock M/M/c Erlang-C queueing theory and interactive What-If staffing simulation.",
        "• ReportLab generation of statutory PDF receipts with embedded ISO/IEC 18004 dynamic tracking QR codes.",
        "• Immutable append-only forensic audit logging of all system events, state transitions, memos, and officer assignments.",
        "• Full-stack trilingual dynamic UI localization across 222 dictionary keys in English, Hindi, and Marathi."
    ]
    for s in scope_in:
        add_p(doc, s, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=2)

    add_h3(doc, "3.1.2 Out of Scope")
    add_p(doc, "The following capabilities are excluded from Version 1.0 release boundaries:", space_before=2, space_after=4)
    scope_out = [
        "• Direct write-back integration into proprietary Core Banking Solutions (CBS) like Infosys Finacle or TCS BaNCS (mocked via standard RESTful JSON interfaces).",
        "• Direct execution of interbank financial debit reversals or automated clearinghouse settlements across NPCI/RBI networks.",
        "• Recognition of handwritten physical complaint slips (system requires typed text, voice dictation, or printed receipts).",
        "• Languages beyond English, Hindi, and Marathi.",
        "• Autonomous filing of formal legal complaints into the RBI Integrated Ombudsman CMS portal without human officer review."
    ]
    for s in scope_out:
        add_p(doc, s, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=2)

    # 3.2 Intended Users and Stakeholders
    add_h2(doc, "3.2 Intended Users and Stakeholders")
    add_p(doc, "Table 5 delineates the primary user personas and their system interaction characteristics.", space_before=2, space_after=6)
    
    users_headers = ["Stakeholder Persona", "Primary Role and Interaction Workflow"]
    users_rows = [
        ("Bank Customer / Complainant", "Primary end-user filing banking disputes. May have limited technical literacy or English proficiency. Utilizes voice dictation in Hindi or Marathi, uploads transaction proofs, views live status, and downloads statutory QR receipts."),
        ("Grievance Redressal Officer", "Bank operations specialist assigned to investigate complaints. Reviews OCR evidence matches, inspects AI copilot resolution suggestions, conducts internal inquiries, and executes formal resolution memos."),
        ("Branch Operations Manager", "Administrative supervisor monitoring branch-level SLA compliance, evaluating officer productivity, running Erlang-C What-If queue simulations, and auditing DPDP Act privacy adherence."),
        ("Regulatory / Internal Auditor", "Independent compliance officer inspecting immutable audit logs, validating PII masking enforcement, and analyzing systemic bank failure trends."),
        ("Project Maintainer / Developer", "Engineering personnel deploying backend services, maintaining ML classification datasets, monitoring API health, and managing CI/CD test pipelines.")
    ]
    add_styled_table(doc, users_headers, users_rows, col_widths=[2.0, 4.02])
    add_p(doc, "Table 5: Users and Stakeholders", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    # 3.3 Overall Product Description
    add_h2(doc, "3.3 Overall Product Description")
    add_h3(doc, "3.3.1 Product Perspective")
    p_persp = (
        "GrievanceIQ operates as a modern, decoupled three-tier software architecture comprising a reactive single-page frontend (React 18), "
        "an asynchronous RESTful API gateway (Python FastAPI / Uvicorn), and a relational data persistence layer (SQLite WAL / PostgreSQL). "
        "The system coordinates deterministic data sanitization, probabilistic machine learning classification, deep learning semantic similarity, "
        "optical character recognition, and mathematical queueing theory into a unified operational pipeline."
    )
    add_p(doc, p_persp, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    add_h3(doc, "3.3.2 System Environment and Data Flow")
    add_p(doc, "The end-to-end complaint processing pipeline executes across six distinct stages summarized in Table 6.", space_before=2, space_after=6)
    
    pipeline_headers = ["# Stage", "Operational Activity", "Generated Architectural Output"]
    pipeline_rows = [
        ("1. Ingestion & Sanitization", "Multi-attribute dispute data and audio stream are received. DPDP regex filters scrub Cards, Aadhaar, and PAN tokens.", "Sanitized complaint record, unmasked PII eliminated."),
        ("2. ML Triage & Routing", "TF-IDF vectorizer extracts unigram/bigram tokens; Multinomial Naive Bayes and SBERT predict department and subcategory.", "Assigned category, subcategory, confidence score."),
        ("3. Evidence OCR Validation", "Uploaded receipt images/PDFs are parsed via OCR. 4-point entity matcher checks Ref, Bank, Account, and Amount.", "Document text, entity match badges, credibility score (0-100%)."),
        ("4. Tier-1 Bot & SLA Gating", "Claim validity is scored; bot evaluates knowledge-base rules; statutory SLA deadline is computed based on RBI rules.", "Immediate settlement offer or escalated queue status with SLA countdown."),
        ("5. Smart Assignment & Memo", "Unresolved disputes are assigned to optimal officer based on workload; officer conducts review with AI memo copilot.", "Officer assignment record, internal notes, draft memo."),
        ("6. Resolution, Receipt & Audit", "Officer executes formal resolution memo; ReportLab generates statutory PDF receipt with dynamic QR; audit log is written.", "Resolved status, downloadable QR PDF receipt, immutable audit event.")
    ]
    add_styled_table(doc, pipeline_headers, pipeline_rows, col_widths=[1.5, 2.5, 2.02])
    add_p(doc, "Table 6: Six-Stage Processing Pipeline", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    # 3.4 Functional Requirements (FR-01 to FR-20)
    add_h2(doc, "3.4 Functional Requirements")
    add_p(doc, "The formal functional requirements for GrievanceIQ are detailed in Tables FR-01 through FR-20, specifying input, processing logic, output, and testable acceptance criteria.", space_before=2, space_after=8)

    fr_specs = [
        ("FR-01", "H", "Authentication and Role-Based Access Control",
         "Email, password, role claim; on subsequent requests, Bearer JWT access token.",
         "Password is hash-verified using bcrypt with work factor 12. FastAPI OAuth2 middleware decodes JWT, validates expiry, and checks role permissions (Customer, Officer, Admin).",
         "Authenticated session token, user profile payload, or structured 401/403 HTTP error.",
         "Valid credentials yield signed JWT; invalid credentials return 401; customers accessing officer endpoints receive 403 Forbidden; raw passwords are never persisted."),
        
        ("FR-02", "H", "Multi-Attribute Complaint Ingestion",
         "Complainant name, email, phone, bank name, transaction ID, date, amount, dispute description.",
         "Backend validates presence, data types, and positive transaction amount. Assigns unique identifier GIQ-YYYY-XXXXX.",
         "Persisted complaint record in state 'Submitted', HTTP 201 Created.",
         "Valid payloads are saved within 100 ms; non-positive amounts or missing required fields return 422 Unprocessable Entity."),
        
        ("FR-03", "H", "Real-Time Vernacular Voice Dictation",
         "Streaming audio microphone capture via browser W3C Web Speech API.",
         "Client-side speech recognizer configured for en-US, hi-IN, or mr-IN. Dual-state buffer accumulates session-final text while streaming interim hypotheses.",
         "Real-time text transcript streaming into description field with zero duplicate line emissions.",
         "Continuous speech across 60 seconds generates single coherent transcript with 0% phrase duplication."),
        
        ("FR-04", "H", "DPDP Act 2023 Ingestion-Level PII Sanitization",
         "Raw natural-language complaint narrative containing potential PII tokens.",
         "Compiled regex filters scan text for 16-digit card numbers, 12-digit Aadhaar numbers, and 10-character PAN strings (case-insensitive). Replaces matches with masked strings.",
         "Scrubbed complaint description with zero unredacted PII tokens.",
         "100% of tested valid and formatted Card, Aadhaar, and PAN tokens are redacted; database contains zero raw PII."),
        
        ("FR-05", "H", "Autonomous ML Categorization (TF-IDF + MNB)",
         "Sanitized complaint description string.",
         "Pipeline converts text to unigram/bigram TF-IDF sparse matrix and executes Multinomial Naive Bayes inference.",
         "Predicted primary category, confidence score (0.0 to 1.0).",
         "Classification accuracy >= 80% on test benchmark; execution latency < 10 ms per complaint."),
        
        ("FR-06", "H", "SBERT Semantic Subcategory & Duplicate Detection",
         "Complaint description string.",
         "Sentence-BERT all-MiniLM-L6-v2 model calculates 384-dimensional dense embedding, computing cosine similarity against historical disputes.",
         "Predicted subcategory and list of similar historical complaints with similarity index.",
         "Subcategory predicted within 50 ms; duplicate complaints with similarity > 0.85 flagged immediately."),
        
        ("FR-07", "H", "Documentary Evidence Upload and Validation",
         "Uploaded binary file (PNG, JPG, or PDF up to 5 MB).",
         "Server verifies MIME type, magic bytes, and file size. Stores file securely under unique UUID in uploads/ directory.",
         "Validated evidence record with persistent storage path and document URL.",
         "Valid files saved; executables, non-image/non-PDF files, and files > 5 MB rejected with 400 Bad Request."),
        
        ("FR-08", "H", "Evidence OCR Extraction & 4-Point Cross-Validation",
         "Validated transaction receipt image or PDF file, complaint metadata.",
         "OCR extracts raw text tokens. Deterministic matching checks: (1) Transaction Ref, (2) Bank Name, (3) Disputed Amount, (4) Account last 4 digits.",
         "Extracted text, individual entity match boolean flags, and composite credibility score (0 to 100%).",
         "Matching all 4 entities yields score >= 90%; matching 0 entities yields score < 25%; execution completes within 2.5 s."),
        
        ("FR-09", "H", "Tier-1 AI GrievanceBot Adjudication Gate",
         "Complaint record, extracted OCR evidence score, complaint validity score.",
         "Bot evaluates whether validity >= 70% and evidence >= 50%. Matches dispute against KnowledgeBase FAQs and circulars.",
         "Automated resolution memo, instant refund recommendation, or escalation to human queue.",
         "Eligible minor disputes resolved immediately with customer confirmation; non-qualifying disputes cleanly escalated."),
        
        ("FR-10", "H", "Dynamic SLA Deadline & Urgency Radar",
         "Complaint category, transaction date, submission timestamp.",
         "Engine applies statutory RBI rules: 72 hours for unauthorized electronic debits, 24 hours for ATM failures, 30 days for general grievances.",
         "Explicit SLA deadline timestamp, remaining countdown hours, urgency level (CRITICAL, HIGH, MEDIUM, LOW).",
         "Deadlines computed deterministically; complaints exceeding deadline flagged with visual SLA_BREACH warning."),
        
        ("FR-11", "H", "Workload-Balanced Smart Officer Assignment",
         "Escalated complaint, department ID, active officers pool.",
         "Assigner queries active officer ticket counts, historical resolution velocities, and specialty skills. Allocates to officer with lowest active load.",
         "Updated complaint assignment record, notification to officer, assignment_history audit entry.",
         "Assignment executed in O(c) time; officer active ticket distribution remains balanced across department."),
        
        ("FR-12", "M", "Duplicate and Fraudulent Grievance Detection",
         "Incoming complaint details (user_id, bank, transaction ID, amount).",
         "Database checks for identical transaction IDs and matching SBERT embeddings filed within preceding 30 days.",
         "Duplicate flag and reference to original master complaint.",
         "Repeated submissions of identical transaction ID by same user within 30 days flagged as DUPLICATE."),
        
        ("FR-13", "H", "Officer Adjudication and AI Copilot Memo Drafting",
         "Officer review inputs, investigation notes, resolution decision.",
         "Backend generates formal resolution memo incorporating dispute findings, bank policy, and refund amounts.",
         "Updated complaint state 'Resolved', resolution record, timestamp, officer signature.",
         "Complaint state transitions to Resolved; customer receives notification; resolution memo is permanently logged."),
        
        ("FR-14", "M", "Case Reopening and Senior Nodal Escalation (Level 2)",
         "Customer dissatisfaction request submitted within 7 days of resolution.",
         "System verifies 7-day eligibility window. Escalates dispute to Senior Nodal Officer with priority set to CRITICAL.",
         "Complaint state 'Reopened', escalation_history entry, notification to Senior Nodal Officer.",
         "Reopened cases bypass frontline officers and appear exclusively in Senior Nodal Officer queue."),
        
        ("FR-15", "H", "Statutory PDF Receipt with Dynamic ISO QR Code",
         "Resolved or registered complaint ID, metadata.",
         "ReportLab generates formal two-column PDF receipt embedding bank logos, metadata, DPDP masked text, and ISO/IEC 18004 2D QR code.",
         "Downloadable PDF document (< 150 KB) with scannable QR tracking URL.",
         "PDF conforms to formal layout; QR code scans cleanly on standard mobile cameras to live tracking endpoint."),
        
        ("FR-16", "H", "Predictive Queue Modeling (Kleinrock M/M/c & Erlang-C)",
         "Hourly arrival rate lambda, officer service rate mu, active officer count c.",
         "Engine computes traffic intensity rho, probability of zero jobs P_0, Erlang-C delay probability C(c, lambda/mu), queue wait time W_q, and SLA breach risk.",
         "Operational metrics payload: utilization, queue length, dwell time, and breach risk percentage.",
         "Formulas produce exact analytical outputs in O(c) time; stability condition rho < 1 enforced."),
        
        ("FR-17", "M", "Interactive 'What-If' Staffing Sandbox",
         "Baseline parameters, simulated arrival multiplier, simulated officer adjustment delta_c.",
         "Engine recalculates Erlang-C queue metrics under hypothetical surge and staffing configurations.",
         "Side-by-side comparative table showing impact on wait times, queue sizes, and SLA breach probability.",
         "Sandbox recalculates within 10 ms upon slider adjustment in browser UI."),
        
        ("FR-18", "M", "Bank Health Score & Systemic Vulnerability Radar",
         "Aggregated complaints dataset across scheduled commercial banks.",
         "Engine computes composite health score (0 to 100) based on resolution speed, SLA breach rate, customer reopen rate, and evidence quality.",
         "Bank health scorecard, vulnerability radar dimensions, and operational leaderboard.",
         "Leaderboard ranks all banks objectively; systemic failure spikes highlighted with early warnings."),
        
        ("FR-19", "H", "Trilingual Dynamic UI Localization (EN / HI / MR)",
         "User language selection event ('en', 'hi', 'mr').",
         "React Context provider swaps dictionary lookup across 222 localized string keys across all navigation, labels, and alerts.",
         "Instantaneous UI language update without page reload or state loss.",
         "100% of 222 keys render properly in English, Hindi, and Marathi with zero untranslated fallbacks."),
        
        ("FR-20", "H", "Immutable Append-Only Forensic Audit Trail",
         "System event trigger (submission, triage, OCR, assignment, memo, resolution).",
         "Audit service captures action, entity_type, entity_id, user_id, details, and UTC timestamp, inserting into audit_logs table.",
         "Persistent audit record, visible in administrator audit viewer.",
         "Audit records are append-only; database rules reject all UPDATE and DELETE commands on audit_logs.")
    ]

    for req_id, pri, title, inp, proc, outp, acc in fr_specs:
        add_p(doc, f"{req_id} [Priority: {pri}] – {title}", bold=True, size=11, color=COLOR_PRIMARY, space_before=4, space_after=2)
        tbl_req = [
            ("Description", f"The system shall provide {title.lower()} as an automated, verifiable capability."),
            ("Input", inp),
            ("Processing", proc),
            ("Output", outp),
            ("Acceptance Criteria", acc)
        ]
        add_styled_table(doc, ["Attribute", "Specification Details"], tbl_req, col_widths=[1.5, 4.52])

    # 3.5 Non-Functional Requirements
    add_h2(doc, "3.5 Non-Functional Requirements")
    add_h3(doc, "3.5.1 Performance Requirements")
    add_p(doc, "Table 33 formalizes the performance and response time constraints.", space_before=2, space_after=4)
    nfr_perf = [
        ("NFR-01", "H", "Transactional API Endpoint Latency", "All core transactional REST endpoints (/api/complaints/submit, /api/auth/login) shall complete within 150 ms under standard load."),
        ("NFR-02", "H", "ML Categorization Inference Time", "The TF-IDF and Naive Bayes classification pipeline shall infer category and confidence in under 15 ms per document."),
        ("NFR-03", "M", "Erlang-C Queue Model Execution", "The analytical M/M/c queueing simulation engine shall compute waiting times, utilization, and breach risks in under 5 ms."),
        ("NFR-04", "M", "Documentary OCR Extraction Time", "OCR extraction and 4-point entity cross-matching shall complete in under 3.0 seconds per uploaded receipt document."),
        ("NFR-05", "M", "Statutory PDF Receipt Generation", "ReportLab PDF compilation with embedded dynamic QR code shall complete in under 500 ms and produce files under 150 KB.")
    ]
    add_styled_table(doc, ["ID", "Pri.", "Requirement Title", "Formal Specification Constraint"], nfr_perf, col_widths=[0.9, 0.5, 2.0, 2.62])
    add_p(doc, "Table 33: Performance Requirements", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=10, italic=True, size=10, color=COLOR_MUTED)

    add_h3(doc, "3.5.2 Scalability Requirements")
    add_p(doc, "• NFR-06 [H]: The backend ASGI server and database connection pool shall sustain at least 100 concurrent HTTP requests without connection timeouts or thread starvation.", space_before=1, space_after=3)
    add_p(doc, "• NFR-07 [M]: The relational database design shall accommodate at least 500,000 historical complaint records and 2,000,000 audit log entries without degradation of primary key lookup latency.", space_before=1, space_after=6)

    add_h3(doc, "3.5.3 Availability and Reliability")
    add_p(doc, "• NFR-08 [H]: The system shall maintain 99.9% uptime during operational banking hours.", space_before=1, space_after=3)
    add_p(doc, "• NFR-09 [H]: All database write operations shall execute under explicit ACID transactions. In case of unexpected server termination, Write-Ahead Logging (WAL) ensures zero database corruption.", space_before=1, space_after=6)

    add_h3(doc, "3.5.4 Security and Privacy Requirements")
    add_p(doc, "Table 34 formalizes the security and DPDP Act 2023 privacy requirements.", space_before=2, space_after=4)
    sec_reqs = [
        ("SEC-01", "H", "DPDP Act 2023 PII Masking", "All 16-digit debit/credit card credentials, 12-digit Aadhaar numbers, and 10-character PAN tokens shall be masked at API ingestion with 100% precision."),
        ("SEC-02", "H", "Bcrypt Password Hashing", "User passwords shall be salted and hashed using bcrypt with a work factor of at least 12. Raw passwords shall never be persisted or logged."),
        ("SEC-03", "H", "OAuth2 JWT Token Authentication", "Protected administrative and officer endpoints shall require valid Bearer JSON Web Tokens signed with HS256 algorithm and 24-hour expiration."),
        ("SEC-04", "H", "Role-Based Access Control (RBAC)", "The API gateway shall strictly enforce role separation: Customer, Officer, and Admin. Privilege escalation attempts shall be rejected with 403 Forbidden."),
        ("SEC-05", "H", "Parameterised SQL Execution", "All database interactions shall utilize SQLAlchemy ORM parameterised statements. Raw string concatenation into SQL queries is strictly prohibited to prevent SQL injection."),
        ("SEC-06", "H", "Forensic Audit Immutability", "The audit_logs table shall be append-only. Database rules shall block all UPDATE and DELETE queries to guarantee legal evidentiary non-repudiation.")
    ]
    add_styled_table(doc, ["ID", "Pri.", "Security Requirement", "Formal Technical Invariant"], sec_reqs, col_widths=[0.9, 0.5, 2.0, 2.62])
    add_p(doc, "Table 34: Security Requirements", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=10, italic=True, size=10, color=COLOR_MUTED)

    add_h3(doc, "3.5.5 Usability and Accessibility")
    add_p(doc, "• NFR-10 [H]: The interface shall provide trilingual localization in English, Hindi, and Marathi across 100% of UI labels, buttons, and alerts.", space_before=1, space_after=3)
    add_p(doc, "• NFR-11 [H]: The system shall support real-time voice dictation with visual waveform feedback to assist elderly and visually challenged depositors.", space_before=1, space_after=3)
    add_p(doc, "• NFR-12 [M]: The UI shall support high-contrast light and dark themes with WCAG 2.1 AA compliant color contrast ratios.", space_before=1, space_after=6)

    add_h3(doc, "3.5.6 Maintainability and Portability")
    add_p(doc, "• NFR-13 [H]: Decoupled modular architecture separating frontend (React 18) and backend (FastAPI) via standardized RESTful JSON interfaces.", space_before=1, space_after=3)
    add_p(doc, "• NFR-14 [M]: The entire system shall execute seamlessly across Windows 10/11, Linux (Ubuntu 22.04 LTS), and macOS environments.", space_before=1, space_after=3)
    add_p(doc, "• NFR-15 [M]: Codebase shall maintain strict automated unit and integration test suites with zero syntax or linting violations.", space_before=1, space_after=8)

    # 3.5.9 Business Rules
    add_h3(doc, "3.5.7 Business Rules and Operational Invariants")
    add_p(doc, "Table 35 details the core business rules governing BFSI dispute adjudication.", space_before=2, space_after=4)
    br_data = [
        ("BR-01", "PII Redaction Invariant: Zero plain-text payment card numbers, Aadhaar numbers, or PANs may be stored in database tables or logs."),
        ("BR-02", "Statutory 72-Hour RBI SLA: Unauthorized electronic banking transactions reported by customers must be resolved within 72 hours."),
        ("BR-03", "Statutory 24-Hour ATM SLA: ATM cash dispensing failures without customer debit reversal must be triaged within 24 hours."),
        ("BR-04", "Statutory 30-Day Ombudsman Window: Banking grievances not resolved within 30 days are automatically flagged for RBI Ombudsman escalation."),
        ("BR-05", "Customer-Gated AI Settlement: Tier-1 AI GrievanceBot settlement proposals require explicit affirmative customer acceptance."),
        ("BR-06", "Deterministic Evidence Primacy: Customer assertions of payment amounts are verified against OCR extracted receipts before approval."),
        ("BR-07", "Workload Fairness Invariant: No officer shall be assigned a new complaint if another qualified officer in the department has lower active load."),
        ("BR-08", "7-Day Reopen Governance: Customers may request case reopening within 7 calendar days of resolution; reopened cases escalate to Senior Nodal Officers."),
        ("BR-09", "Audit Non-Repudiation: Every complaint status transition, officer reassignment, and memo creation must generate an immutable audit log entry."),
        ("BR-10", "Base-URL Dynamic QR Invariant: Statutory PDF receipt QR codes must encode the live server host dynamically to ensure scannable tracking.")
    ]
    add_styled_table(doc, ["Rule ID", "Business Rule / Operational Policy Invariant"], br_data, col_widths=[1.2, 4.82])
    add_p(doc, "Table 35: Business Rules", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    # 3.6 Hardware and Software Requirements
    add_h2(doc, "3.6 Hardware and Software Requirements")
    add_p(doc, "Table 36 documents the complete development, runtime, and deployment technology stack.", space_before=2, space_after=4)
    stack_data = [
        ("Backend Framework", "Python 3.10+, FastAPI 0.115.0, Uvicorn (ASGI Server), Pydantic v2"),
        ("Database Engine", "SQLite 3 with Write-Ahead Logging (WAL) / PostgreSQL 15, SQLAlchemy 2.0 ORM"),
        ("Frontend Framework", "React 18.3.1, Vite 5.4.14, Tailwind CSS 3.4.1, Lucide React Icons, Recharts 2.15"),
        ("Audio & Speech", "W3C Web Speech API (SpeechRecognition), Web Audio API (AudioContext Waveform)"),
        ("Machine Learning", "Scikit-Learn 1.5.0 (TF-IDF Vectorizer, Multinomial Naive Bayes Classifier)"),
        ("Semantic NLP", "Sentence-Transformers (all-MiniLM-L6-v2, 384-dimensional dense cosine embeddings)"),
        ("OCR Engine", "EasyOCR 1.7.1, PyTesseract 0.3.10, Pillow (PIL) 10.4.0"),
        ("Document Generation", "ReportLab 4.2.2 (canvas, platypus layout), Qrcode 7.4.2 (ISO/IEC 18004 QR)"),
        ("Testing & Quality", "FastAPI TestClient, Pytest 8.2, Requests, Pre-Commit, Flake8, Black")
    ]
    add_styled_table(doc, ["Technology Layer", "Software Package, Framework and Version"], stack_data, col_widths=[2.0, 4.02])
    add_p(doc, "Table 36: Development and Runtime Stack", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    # 3.7 Constraints and Assumptions
    add_h2(doc, "3.7 Constraints and Assumptions")
    add_p(doc, "3.7.1 Technical Constraints: System requires modern web browsers with Web Speech API support for voice dictation. Backend executes on standard Python 3.10+ runtimes.", space_before=1, space_after=3)
    add_p(doc, "3.7.2 Financial Constraints: Engineered exclusively with open-source software libraries, eliminating commercial software licensing fees.", space_before=1, space_after=3)
    add_p(doc, "3.7.3 Operational Constraints: GrievanceIQ functions as an assistive operational tool; binding financial debits and legal rulings remain under formal banking authority.", space_before=1, space_after=3)
    add_p(doc, "3.7.4 Time Constraints: Formulated and deployed within the 12-week academic sprint schedule of the APNI Leap semester.", space_before=1, space_after=6)

    # Open items TBD
    add_p(doc, "Table 39 outlines technical items reserved for future production deployment.", space_before=2, space_after=4)
    tbd_data = [
        ("TBD-01", "Production Core Banking Integration: Certified adapter specifications for Finacle and BaNCS write-backs."),
        ("TBD-02", "On-Device Whisper ASR: Local compilation of Whisper.tflite for offline voice recognition in rural kiosks."),
        ("TBD-03", "NPCI UPI Auto-Reversal API: Direct integration with automated clearinghouse debit reversal webhooks."),
        ("TBD-04", "Account Aggregator (AA) Connectivity: Automated retrieval of banking statements under RBI AA guidelines."),
        ("TBD-05", "Distributed Message Bus: Migration of event queues to Apache Kafka for multi-datacenter replication."),
        ("TBD-06", "Multi-Language Expansion: Inclusion of 10 additional scheduled Indian languages (Tamil, Telugu, Bengali, etc.)."),
        ("TBD-07", "Disaster Recovery & Hot Standby: Geographically distributed multi-region failover configuration.")
    ]
    add_styled_table(doc, ["ID", "Architecture Open Item / Production Roadmap Task"], tbd_data, col_widths=[1.2, 4.82])
    add_p(doc, "Table 39: Open Items (TBD)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    # 3.8 Use Cases and User Stories
    add_h2(doc, "3.8 Use Cases and User Stories")
    add_h3(doc, "3.8.1 Formal Use Cases")
    
    uc_specs = [
        ("UC-01", "Register and Authenticate User", "Bank Customer / Officer", "None",
         "User opens /auth, enters credentials. Backend verifies password hash with bcrypt, issues signed Bearer JWT.",
         "Invalid credentials return 401 Unauthorized with descriptive error message.",
         "Authenticated session established; role-specific dashboard views enabled."),
        
        ("UC-02", "File Grievance with Voice Dictation & PII Redaction", "Bank Customer", "Customer is signed in or guest on public portal",
         "Customer selects language (Hindi/Marathi/English), activates microphone, dictates dispute, attaches receipt slip, submits form. System masks PII tokens, executes ML triage, stores complaint, and creates audit event.",
         "If description is < 15 characters, validity gate rejects submission with 422 error requesting details.",
         "Complaint persisted in 'Submitted' state; unique ID (GIQ-YYYY-XXXXX) returned; dynamic QR PDF receipt generated."),
        
        ("UC-03", "Tier-1 GrievanceBot Adjudication & Settlement", "Bank Customer", "Complaint submitted with valid evidence",
         "GrievanceBot evaluates validity and OCR score. If complaint meets criteria, bot presents immediate refund settlement dialog. Customer accepts settlement.",
         "Customer declines automated settlement or dispute requires manual inquiry; dispute escalates to officer queue.",
         "Complaint state transitions to 'Resolved'; settlement memo recorded; customer notified."),
        
        ("UC-04", "Documentary Evidence OCR Cross-Verification", "Grievance Officer", "Complaint has attached receipt image/PDF",
         "Officer opens complaint dossier. Clicks 'Verify Evidence'. OCR engine extracts text tokens and matches Ref, Bank, Amount, and Account. Scores displayed with visual badges.",
         "Uploaded document is blurry or unreadable; OCR returns low confidence (< 30%); manual inspection required.",
         "Credibility score saved to complaint record; match badges visible in officer workspace."),
        
        ("UC-05", "Dynamic SLA Tracking and Urgency Escalation", "Grievance Officer / Admin", "Active complaints exist in database",
         "Engine computes time delta between submission and statutory deadline (24h/72h/30d). Visual radar updates countdown timers and highlights urgent cases.",
         "None.",
         "Complaints within 12 hours of breach highlighted in Amber; breached complaints highlighted in Red with critical alert."),
        
        ("UC-06", "Officer Adjudication and Resolution Memo Drafting", "Grievance Officer", "Complaint assigned to officer in state 'In Review'",
         "Officer reviews complaint details, evidence match, and AI Copilot suggestions. Enters resolution memo and executes resolution action.",
         "Investigation incomplete; officer adds internal investigation note and keeps complaint in review.",
         "Complaint marked 'Resolved'; resolution memo persisted; customer notification dispatched; audit log updated."),
        
        ("UC-07", "Case Reopening Governance (Level 2 Escalation)", "Bank Customer", "Complaint resolved within preceding 7 days",
         "Customer enters dissatisfaction reason on tracking portal. System validates 7-day window, reopens case, sets priority to CRITICAL, and routes to Senior Nodal Officer.",
         "Attempted reopen after 7 calendar days rejected with informational message advising RBI Ombudsman contact.",
         "Complaint marked 'Reopened'; escalation logged in escalation_history; Senior Nodal Officer alerted."),
        
        ("UC-08", "Predictive Queueing Simulation (Erlang-C What-If)", "Branch Operations Manager", "Manager authenticated on Analytics portal",
         "Manager adjusts arrival rate multiplier and officer staffing count sliders. Engine recomputes Erlang-C formulas and updates charts in real time.",
         "Traffic intensity exceeds 1.0 (unstable queue); system displays 'Queue Instability Warning' in red.",
         "Predicted wait times, queue sizes, and SLA breach risks displayed with comparative baseline metrics."),
        
        ("UC-09", "Generate and Verify Statutory QR Receipt", "Bank Customer / Officer", "Valid complaint ID exists",
         "User clicks 'Download Official Receipt'. Backend compiles ReportLab PDF with embedded ISO/IEC 18004 dynamic QR code.",
         "None.",
         "Tamper-evident statutory PDF downloaded; mobile camera scanning QR navigates directly to live tracking page."),
        
        ("UC-10", "Forensic Audit Log Inspection", "Compliance Auditor / Admin", "Admin credentials authenticated",
         "Auditor navigates to /audit, filters by entity or date range. System renders immutable chronological event history.",
         "None.",
         "Complete, unalterable forensic record of all submissions, redacting events, assignments, and memos displayed.")
    ]

    for ucid, title, actor, pre, main_flow, alt_flow, post in uc_specs:
        add_p(doc, f"{ucid}: {title}", bold=True, size=11, color=COLOR_PRIMARY, space_before=4, space_after=2)
        uc_tbl = [
            ("Actor", actor),
            ("Precondition", pre),
            ("Main Flow", main_flow),
            ("Alternative Flow", alt_flow),
            ("Postcondition", post)
        ]
        add_styled_table(doc, ["Attribute", "Specification Details"], uc_tbl, col_widths=[1.5, 4.52])

    add_h3(doc, "3.8.2 User Stories Specification")
    add_p(doc, "Table 49 articulates the core functional requirements from user persona perspectives.", space_before=2, space_after=4)
    user_stories = [
        ("US-01", "As an aggrieved customer with limited typing skills, I want to dictate my dispute in Hindi or Marathi so that I can register my complaint effortlessly."),
        ("US-02", "As a privacy-conscious depositor, I want my payment card numbers, Aadhaar, and PAN masked automatically so that my private financial credentials are never exposed."),
        ("US-03", "As a bank customer, I want an instant statutory PDF receipt with a QR code so that I have verifiable legal proof of submission."),
        ("US-04", "As a bank customer, I want a live status tracker with an SLA countdown timer so that I know exactly when my bank will resolve my dispute."),
        ("US-05", "As a grievance redressal officer, I want automated OCR entity matching on uploaded receipts so that I can instantly verify claim authenticity without manual cross-referencing."),
        ("US-06", "As a grievance redressal officer, I want an AI Copilot that drafts formal resolution memos so that I can resolve routine complaints 5x faster."),
        ("US-07", "As an operations manager, I want an M/M/c queueing simulation sandbox so that I can forecast queue bottlenecks and optimize officer staffing before SLA breaches occur."),
        ("US-08", "As an operations manager, I want a bank health scorecard and vulnerability radar so that I can detect systemic transaction failure points early."),
        ("US-09", "As a customer whose dispute was rejected, I want the ability to escalate to a Senior Nodal Officer within 7 days so that I receive impartial secondary review."),
        ("US-10", "As a regulatory compliance auditor, I want an immutable, append-only audit trail so that every status change and officer memo is forensically traceable."),
        ("US-11", "As a system administrator, I want role-based access control so that customer dispute records are strictly segregated from administrative functions."),
        ("US-12", "As a software engineer, I want decoupled, modular architecture and comprehensive automated test suites so that system components can be maintained without regression.")
    ]
    add_styled_table(doc, ["Story ID", "User Persona Story & Acceptance Objective"], user_stories, col_widths=[1.2, 4.82])
    add_p(doc, "Table 49: User Stories", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    add_p(doc, "18", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
