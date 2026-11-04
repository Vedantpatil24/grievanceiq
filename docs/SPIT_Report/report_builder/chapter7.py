# chapter7.py
# Chapter 7: Implementation and Module-Wise Coding

import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter7(doc):
    add_h1(doc, "7   Implementation and Module-Wise Coding")
    
    # 7.1 Development Environment
    add_h2(doc, "7.1 Development Environment")
    p_dev = (
        "The development and execution environment of GrievanceIQ integrates modern open-source software frameworks, "
        "relational persistence mechanisms, machine learning runtimes, and frontend build tooling. Table 85 summarizes the technical environment."
    )
    add_p(doc, p_dev, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)

    env_headers = ["Technical Area", "Software Tools, Packages and Pinned Versions"]
    env_rows = [
        ("Backend Framework & Server", "Python 3.10+, FastAPI 0.115.0, Uvicorn (ASGI web server), Pydantic v2"),
        ("Database & ORM", "SQLite 3 with Write-Ahead Logging (WAL) / PostgreSQL 15, SQLAlchemy 2.0.30"),
        ("Frontend Application", "React 18.3.1 (Single-Page App), Vite 5.4.14, Tailwind CSS 3.4.1, Lucide React, Recharts 2.15"),
        ("Speech & Audio", "W3C Web Speech API, Web Audio API (AudioContext streaming waveform)"),
        ("NLP & Machine Learning", "Scikit-Learn 1.5.0 (TfidfVectorizer, MultinomialNB), Sentence-Transformers 3.0 (all-MiniLM-L6-v2)"),
        ("OCR & Document Processing", "EasyOCR 1.7.1, PyTesseract 0.3.10, Pillow (PIL) 10.4.0, PyMuPDF (fitz) 1.24.0"),
        ("Statutory Document Engine", "ReportLab 4.2.2 (canvas, platypus layout), Qrcode 7.4.2 (ISO/IEC 18004 QR generation)"),
        ("Testing & Quality Assurance", "FastAPI TestClient, Pytest 8.2, Requests, Pre-Commit, Flake8, Black"),
        ("Version Control & CI/CD", "Git with main branch protection, GitHub repository (https://github.com/Vedantpatil24/grievanceiq)")
    ]
    add_styled_table(doc, env_headers, env_rows, col_widths=[2.2, 3.82])
    add_p(doc, "Table 85: Development Environment and Tools", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 7.2 Overall Implementation Strategy
    add_h2(doc, "7.2 Overall Implementation Strategy")
    p_strat = (
        "Implementation proceeded across a 12-week phased development plan divided into weekly sprints. To ensure system "
        "dependability, engineering followed an outside-in security-first methodology: relational schemas and API boundary validation "
        "were implemented first, followed by deterministic regex PII sanitizers, then probabilistic machine learning classifiers, "
        "OCR evidence cross-validation, Erlang-C queue simulations, and finally frontend reactive integration. A strict milestone gate "
        "was enforced at the conclusion of each sprint; no phase was closed until all corresponding automated tests passed."
    )
    add_p(doc, p_strat, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    # 7.3 Module-Wise Implementation
    add_h2(doc, "7.3 Module-Wise Implementation")
    add_p(doc, "The eight core functional modules are formally documented below with their input/output contracts, processing logic, dependencies, and test evidence.", space_before=2, space_after=6)

    mod_specs = [
        ("M0: Complaint Intake & DPDP Act 2023 PII Sanitizer",
         "Collects user grievance form data and audio stream; scrubs all 16-digit cards, Aadhaar, and PAN tokens before DB insertion.",
         "Input: Raw complaint description text, transaction metadata. Output: Sanitized description, unique Grievance ID.",
         "Compiled regex filters scan text for card numbers (\\b(?:\\d{4}[ -]?){3}\\d{4}\\b), Aadhaar (\\b\\d{4}[ -]?\\d{4}[ -]?\\d{4}\\b), and PAN (\\b[A-Za-z]{5}\\d{4}[A-Za-z]\\b) with case-insensitivity. Matches are replaced with masked tokens.",
         "Zero plain-text PII persists. Token masking occurs in < 1 ms. Validated via adversarial test cases with unredacted payloads.",
         "Python re module, Pydantic v2 schemas, SQLAlchemy Session.",
         "validity_checker.py, main.py (/api/complaints/submit).",
         "test_e2e_workflows.py (TEST 1, TEST 2); 100% PII masking pass rate."),
        
        ("M1: Autonomous NLP Triage & Multi-Class Categorization",
         "Classifies complaint descriptions into 6 banking categories (Unauthorized Transactions, ATM Failures, UPI Issues, Net Banking, Loans, Accounts).",
         "Input: Sanitized complaint text. Output: Predicted category, department ID, confidence score (0.0 to 1.0).",
         "Converts text to lower-case, extracts unigrams and bigrams using TF-IDF vectorizer (vocab 2,998 terms), and executes Multinomial Naive Bayes posterior probability estimation with Laplace smoothing (alpha=1.0).",
         "Inference executes in ~3 ms. Confidence scores >= 0.50 route automatically; low-confidence cases flag for human supervisor review.",
         "Scikit-Learn 1.5, NumPy, Pickle.",
         "ml_pipeline.py, classifier.pkl, vectorizer.pkl.",
         "model_metrics.json (83.49% accuracy across 2,998 test cases, macro F1 0.835)."),
        
        ("M2: Sentence-BERT Semantic Subcategory & Duplicate Engine",
         "Generates 384-dimensional dense semantic embeddings to predict granular subcategories and detect historical duplicate grievances.",
         "Input: Sanitized complaint text. Output: Predicted subcategory, duplicate flag, top similar complaint IDs.",
         "Text is encoded via Sentence-BERT (all-MiniLM-L6-v2). Cosine similarity is computed against historical complaint embeddings. Similarity >= 0.85 flags duplicate tickets.",
         "Embeddings are normalized to unit sphere for fast dot-product cosine calculations.",
         "Sentence-Transformers 3.0, PyTorch, NumPy, Scipy spatial.",
         "semantic_engine.py, main.py (/api/complaints/similar).",
         "test_semantic_cases.py; 100% detection of semantic duplicates."),
        
        ("M3: Documentary Evidence OCR & 4-Point Entity Cross-Matcher",
         "Parses uploaded transaction slips, passbooks, and ATM receipts; verifies claim authenticity against physical proof.",
         "Input: Scanned receipt image (PNG/JPG) or PDF, complaint metadata. Output: Extracted text, 4-point match flags, credibility score (0-100%).",
         "Rasterizes PDF pages at 300 DPI. OCR extracts text tokens. Evaluates 4 points: (1) Transaction Ref ID (30 pts), (2) Bank Name (25 pts), (3) Amount (30 pts), (4) Account last 4 digits (15 pts).",
         "Score >= 80% marks evidence as 'Strong Verified'; score < 50% flags for manual officer inspection.",
         "EasyOCR 1.7, PyTesseract, Pillow, PyMuPDF (fitz).",
         "ocr_service.py, evidence_verifier.py, main.py (/api/evidence/verify).",
         "test_ocr_engine.py, test_evidence_verification.py (100% test slip match)."),
        
        ("M4: Tier-1 AI GrievanceBot Adjudication Gate",
         "Automates resolution for qualifying minor disputes, deflecting human officer queues.",
         "Input: Complaint record, validity score, OCR credibility score. Output: Automated settlement memo, instant refund approval, or escalation.",
         "If complaint validity >= 70% and OCR credibility >= 80% for ATM dispensing failures or UPI timeouts <= INR 5,000, bot presents immediate provisional refund proposal.",
         "Requires customer confirmation. If accepted, case transitions to 'Resolved' immediately.",
         "SQLAlchemy Session, KnowledgeBaseArticle repository.",
         "bot_resolver.py, main.py (/api/complaints/{id}/bot-decision).",
         "test_e2e_workflows.py (TEST 3: SOLVED by Bot, TEST 4: ESCALATE)."),
        
        ("M5: Dynamic SLA Calculation & Urgency Engine",
         "Enforces statutory RBI turnaround directions (72h for unauthorized debits, 24h for ATM failures, 30 days for general grievances).",
         "Input: Category ID, transaction date, submission timestamp. Output: SLA deadline timestamp, remaining countdown hours, urgency level.",
         "Applies RBI customer liability rules: <= 3 days reporting yields 72h zero-liability SLA. Dynamic time delta calculates remaining hours; h_rem <= 12h triggers CRITICAL alert.",
         "Visual countdown timers render in real time on tracking portals.",
         "datetime, timedelta, Python math.",
         "sla_engine.py, main.py (/api/complaints/{id}/sla).",
         "test_e2e_workflows.py (TEST 5); 100% compliance with RBI circulars."),
        
        ("M6: Workload-Balanced Smart Assigner",
         "Allocates escalated complaints to bank redressal officers based on department specialty, active load, and historical resolution speed.",
         "Input: Unassigned complaint, department officer pool. Output: Assigned officer ID, assignment record, notification.",
         "Queries active ticket counts per officer; calculates load index Load(o) = Active(o) - 0.1 * Velocity(o). Allocates to officer with minimum load.",
         "Execution in O(c) time. Guarantees balanced workload distribution across frontline teams.",
         "SQLAlchemy query aggregations, User model.",
         "smart_assigner.py, main.py.",
         "test_phase2_extended.py (TEST 7); verified balanced officer allocations."),
        
        ("M7: Predictive Queue Modeling & Bank Intelligence",
         "Implements Kleinrock M/M/c Erlang-C queue formulations; powers What-If staffing simulations and bank health scorecards.",
         "Input: Arrival rate lambda, service rate mu, officer count c, bank complaint dataset. Output: Utilization rho, dwell time W_q, breach risk, health score (0-100).",
         "Evaluates closed-form Erlang-C equations. Solves expected waiting times and breach probabilities. Aggregates resolution velocity and CSAT for bank leaderboard.",
         "Recalculates within 5 ms upon slider adjustment in browser UI.",
         "bank_intelligence.py, math, NumPy.",
         "bank_intelligence.py, main.py (/api/analytics/queue-simulate).",
         "test_phase2_extended.py (TEST 8); 100% mathematical convergence.")
    ]

    for m_id, purp, inout, proc, impl, dep, code, test in mod_specs:
        add_p(doc, f"Module {m_id}", bold=True, size=11, color=COLOR_PRIMARY, space_before=4, space_after=2)
        tbl_m = [
            ("Purpose", purp),
            ("Input & Output", inout),
            ("Processing Logic", proc),
            ("Implementation Details", impl),
            ("Dependencies", dep),
            ("Code References", code),
            ("Test Evidence", test)
        ]
        add_styled_table(doc, ["Module Specification Attribute", "Engineering Implementation Details"], tbl_m, col_widths=[1.6, 4.42])

    # 7.4 Front-End Implementation
    add_h2(doc, "7.4 Front-End Implementation")
    p_fe = (
        "The frontend is architected as a responsive Single-Page Application (SPA) using React 18, Vite, and Tailwind CSS. "
        "It communicates with the FastAPI backend exclusively via Axios HTTP calls, rendering dynamic UI components without page reloads. "
        "Table 95 delineates the primary application routes."
    )
    add_p(doc, p_fe, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    fe_routes = [
        ("/", "Public Landing Page: Platform overview, feature highlights, trilingual language selector (EN/HI/MR)"),
        ("/file-complaint", "Dispute Filing Console: Multi-attribute intake form, streaming voice dictation, live waveform, PII masking preview"),
        ("/track/:id", "Public Status Tracker: Real-time SLA breach countdown, state timeline, downloadable official QR PDF receipt"),
        ("/officer/workspace", "Officer Resolution Console: Priority triage queue, urgency radar, evidence OCR inspector, AI memo drafter"),
        ("/admin/analytics", "Operational Intelligence Dashboard: Kleinrock M/M/c Erlang-C queue simulator, interactive What-If staffing sandbox"),
        ("/admin/leaderboard", "Executive Bank Leaderboard: Health scorecard, systemic vulnerability radar across scheduled commercial banks"),
        ("/admin/audit", "Forensic Audit Log Viewer: Immutable chronological history of all state changes, memos, and assignments"),
        ("/auth", "Authentication Portal: Role-gated sign-in with bcrypt password verification and JWT token issuance")
    ]
    add_styled_table(doc, ["Frontend Application Route", "Functional View and Interactive Capabilities"], fe_routes, col_widths=[1.8, 4.22])
    add_p(doc, "Table 95: Frontend Pages", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 7.5 Back-End Implementation
    add_h2(doc, "7.5 Back-End Implementation")
    p_be = (
        "The backend is structured as an asynchronous RESTful service implemented in Python FastAPI and hosted on Uvicorn ASGI. "
        "Table 96 lists the principal REST endpoints."
    )
    add_p(doc, p_be, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    be_endpoints = [
        ("GET", "/api/health", "System health check, database connectivity, and ML model status"),
        ("POST", "/api/auth/login", "OAuth2 password authentication, bcrypt verification, JWT access token issuance"),
        ("POST", "/api/complaints/submit", "Ingestion-level PII masking, TF-IDF triage, SBERT prediction, complaint creation"),
        ("GET", "/api/complaints/{id}", "Public complaint tracking, SLA countdown, evidence match summary, QR URL"),
        ("POST", "/api/evidence/upload", "Documentary evidence binary upload (PNG/JPG/PDF) and integrity validation"),
        ("POST", "/api/evidence/verify", "OCR extraction and deterministic 4-point entity cross-matching"),
        ("POST", "/api/complaints/{id}/bot-decision", "Tier-1 AI GrievanceBot settlement evaluation and customer confirmation"),
        ("POST", "/api/complaints/{id}/resolve", "Officer adjudication, formal resolution memo logging, state transition to Resolved"),
        ("POST", "/api/complaints/{id}/reopen", "Case reopening governance within 7 days, Senior Nodal Officer (Level 2) escalation"),
        ("GET", "/api/complaints/{id}/receipt/pdf", "ReportLab statutory PDF compilation with embedded dynamic ISO/IEC 18004 QR code"),
        ("GET", "/api/analytics/queue-simulate", "Kleinrock M/M/c Erlang-C queue dwell time calculation and What-If staffing sandbox"),
        ("GET", "/api/analytics/bank-health", "Bank health scorecard, vulnerability radar, and commercial banks leaderboard"),
        ("GET", "/api/audit/logs", "Immutable append-only forensic audit trail retrieval (admin role gated)")
    ]
    add_styled_table(doc, ["Method", "RESTful API Endpoint", "Operational Functionality and Security Constraints"], be_endpoints, col_widths=[0.8, 2.2, 3.02])
    add_p(doc, "Table 96: Principal REST Endpoints", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 7.8 Git Repository Setup
    add_h2(doc, "7.8 Git Repository Setup and Member Contributions")
    add_p(doc, "Repository URL: https://github.com/Vedantpatil24/grievanceiq", bold=True, size=10.5, color=COLOR_PRIMARY, space_before=2, space_after=4)
    p_git = (
        "The repository maintains a protected `main` branch with atomic feature commits. Sensitive secrets (.env) are excluded "
        "from version control, with `.env.example` providing template configurations. Table 97 documents the group member contributions."
    )
    add_p(doc, p_git, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    contrib_headers = ["Project Member", "Student UID", "Core Module Responsibilities and Engineering Deliverables"]
    contrib_rows = [
        ("Vedant Patil", "2024300170", "Backend Architecture, FastAPI REST gateways, DPDP Act 2023 PII Sanitizer, TF-IDF + Multinomial Naive Bayes ML pipeline, Kleinrock M/M/c Erlang-C queueing formulation, and ReportLab dynamic QR PDF generation."),
        ("Ashmit Patil", "2024300168", "Frontend Engineering, React 18 SPA architecture, W3C Web Speech API voice dictation hook with dual-state buffer accumulator, Tailwind CSS styling, Recharts visualization, and Trilingual UI localization context."),
        ("Mayuri Tarde", "2024300258", "Document Image Processing, OCR pipeline integration (EasyOCR / PyTesseract), 4-point entity cross-matching algorithm, SQLite/PostgreSQL relational schema design, 3NF normalization, and master automated test suite.")
    ]
    add_styled_table(doc, contrib_headers, contrib_rows, col_widths=[1.5, 1.2, 3.32])
    add_p(doc, "Table 97: Contribution of Group Members", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 7.10 Implementation Challenges and Resolutions
    add_h2(doc, "7.10 Implementation Challenges and Resolutions")
    add_p(doc, "Table 99 documents key technical challenges encountered during development and their architectural resolutions.", space_before=2, space_after=6)

    chal_headers = ["Engineering Challenge", "Underlying Technical Root Cause", "Applied Architectural Resolution"]
    chal_rows = [
        ("Voice Streaming Loop Duplication", "W3C Web Speech API fires repetitive onresult events containing cumulative text alongside interim hypotheses; naive concatenation causes repeating text loops.", "Engineered a dual-state buffer accumulator separating committed session-final text from transient interim hypotheses, guaranteeing zero duplicate line emissions."),
        ("Case-Sensitive PII Leakage", "Traditional uppercase PAN regex failed to detect mixed-case or lowercase PAN entries (e.g., 'abcde1234f'), allowing unredacted PII to leak into databases.", "Updated regex compilation to use re.IGNORECASE across all PII patterns, achieving 100% case-insensitive redaction."),
        ("OCR Character Confusion on Slips", "Low-resolution dot-matrix ATM slips caused OCR confusion between digit '0' and letter 'O', or digit '1' and letter 'I'.", "Implemented heuristic monetary and alphanumeric normalization, stripping currency symbols and evaluating Levenshtein similarity ratios."),
        ("Queue Instability under Surge", "When simulated arrival rate lambda exceeded service capacity c*mu (traffic intensity rho >= 1.0), Erlang-C formulas produced negative or infinite delays.", "Added an algorithmic guard in bank_intelligence.py detecting rho >= 1.0, returning a controlled 'Queue Instability Alert' and capping visual sliders."),
        ("Dynamic QR Code Base URL Mismatch", "Hardcoded localhost URLs in generated PDF receipts prevented mobile cameras on external networks from opening the live tracking portal.", "Configured ReportLab generator to resolve request.base_url dynamically from FastAPI HTTP request headers, ensuring universal mobile tracking compatibility.")
    ]
    add_styled_table(doc, chal_headers, chal_rows, col_widths=[1.8, 2.0, 2.22])
    add_p(doc, "Table 99: Implementation Challenges and Resolutions", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    add_p(doc, "134", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
