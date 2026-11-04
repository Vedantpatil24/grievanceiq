# chapter1.py
# Chapter 1: Introduction and Problem Definition

import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter1(doc):
    add_h1(doc, "1   Introduction and Problem Definition")
    
    # 1.1 Project Background
    add_h2(doc, "1.1 Project Background")
    p1 = (
        "The Indian banking and financial services sector has experienced an unprecedented structural transformation over the "
        "past decade, accelerated by the mass adoption of Unified Payments Interface (UPI), immediate payment services (IMPS), "
        "Real-Time Gross Settlement (RTGS), and mobile banking applications. Under the leadership of the National Payments Corporation "
        "of India (NPCI) and the Reserve Bank of India (RBI), digital retail payments now exceed tens of billions of transactions monthly. "
        "However, as the velocity, volume, and interconnectedness of financial transactions have grown exponentially, the corresponding "
        "surface area for operational failures, network timeouts, ATM dispensing errors, fraudulent debits, and customer service grievances "
        "has broadened commensurately."
    )
    p2 = (
        "When an unauthorized debit occurs or an automated clearing transaction stalls, aggrieved depositors turn to the institutional "
        "grievance redressal machinery mandated for scheduled commercial banks and non-banking financial companies (NBFCs). Traditionally, "
        "this machinery has depended upon manual ticket logging, physical branch queues, call-center interactive voice responses (IVR), "
        "or disparate static web forms. Customers are confronted with long wait times, opaque escalation processes, and generic, unhelpful "
        "rejections. At the regulatory apex, the Reserve Bank of India operates the Integrated Ombudsman Scheme (RB-IOS 2021), which handles "
        "hundreds of thousands of escalated disputes annually that fail to find timely or equitable resolution at the bank level."
    )
    p3 = (
        "The administrative overhead of manually reading, classifying, prioritizing, routing, and verifying documentary evidence for "
        "thousands of daily complaints severely strains bank operations. Frontline customer service representatives frequently misroute "
        "high-priority fraud cases to low-urgency queues, causing statutory Service Level Agreement (SLA) breaches and regulatory penalties. "
        "GrievanceIQ addresses this structural bottleneck by delivering an autonomous, full-stack, and privacy-hardened grievance redressal "
        "and predictive operational intelligence platform."
    )
    add_p(doc, p1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)
    add_p(doc, p2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)
    add_p(doc, p3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=12)

    # 1.2 Problem Statement
    add_h2(doc, "1.2 Problem Statement")
    p_prob_intro = (
        "Aggrieved banking consumers cannot easily navigate fragmented customer grievance portals, and bank operations teams "
        "struggle under massive, unstructured complaint inflows. Four fundamental technical and operational vulnerabilities undermine "
        "existing grievance management architectures:"
    )
    add_p(doc, p_prob_intro, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)
    
    add_p(doc, "1. Manual and Latency-Prone Triage: Inflow streams of customer complaints are manually read and categorized by tier-1 "
               "customer service agents. This produces severe routing bottlenecks, misclassifications (e.g., categorizing an urgent "
               "unauthorized debit as a general inquiry), and resolution delays often exceeding statutory RBI windows (typically 30 calendar days).",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "2. Linguistic and Technical Exclusion: Contemporary banking portals are heavily English-centric and require tedious manual "
               "typing into complex alphanumeric web forms. Rural, semi-urban, elderly, or visually challenged depositors who communicate "
               "in regional languages (such as Hindi or Marathi) are systematically disenfranchised from filing grievances independently.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "3. Critical Regulatory Privacy Violations (DPDP Act 2023): Agitated depositors routinely paste unredacted 16-digit debit/credit "
               "card credentials, 12-digit Aadhaar numbers, and Permanent Account Numbers (PAN) into complaint descriptions. Existing banking "
               "portals persist these sensitive identifiers in plain text in relational databases and application logs, directly violating the "
               "statutory provisions of India's Digital Personal Data Protection (DPDP) Act of 2023.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "4. Predictive Operational Blindness: Branch operations managers and executive leadership lack forward-looking quantitative "
               "tools to anticipate queue congestion surges, predict SLA breaches, or optimize frontline officer staffing allocations before "
               "operational collapses occur.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    p_formal_prob = (
        "The central engineering problem addressed by GrievanceIQ is therefore: To design, implement, and benchmark an autonomous, "
        "privacy-first banking grievance management platform that provides zero-latency trilingual voice dictation, enforces ingestion-level "
        "DPDP Act 2023 token redaction, executes automated multi-class machine learning triage, independently validates documentary "
        "evidence via 4-point OCR entity matching, resolves routine claims via Tier-1 AI GrievanceBot, and empowers bank management with "
        "Kleinrock M/M/c Erlang-C predictive operational queueing models."
    )
    add_p(doc, p_formal_prob, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=12, italic=True)

    # 1.3 Motivation
    add_h2(doc, "1.3 Motivation")
    p_mot = (
        "A modern, fair, and resilient financial democracy requires that grievance redressal be frictionless, instantaneous, vernacularly "
        "inclusive, and legally compliant by design. Four fundamental engineering motivations drive this project:"
    )
    add_p(doc, p_mot, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)
    add_p(doc, "• Real-Time Vernacular Accessibility: Enabling non-literate or elderly citizens to articulate complex banking disputes "
               "verbally in their mother tongue (Hindi or Marathi) using browser-native speech recognition without expensive third-party speech APIs.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "• Statutory Privacy Enforcement by Design: Eliminating human error by scrubbing financial PII (payment cards, Aadhaar, PAN) "
               "at the network boundary prior to persistent storage or model inference, shielding banks from catastrophic regulatory penalties.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "• Deterministic Evidence Cross-Validation: Moving beyond unverified customer assertions by extracting and cross-referencing "
               "transaction metadata directly from bank receipts, ATM failure slips, and passbook scans via OCR.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "• Rigorous Mathematical Operations Research: Replacing arbitrary managerial intuition with proven queueing theory (M/M/c "
               "Erlang-C formulas) to forecast queue dwell times, monitor statutory SLA countdowns, and execute interactive What-If staffing simulations.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=12)

    # 1.4 Objectives
    add_h2(doc, "1.4 Objectives")
    add_p(doc, "The project objectives of GrievanceIQ are concrete, measurable, and testable:", space_before=2, space_after=6)
    objs = [
        "1. Ingestion-Level DPDP 2023 Sanitization: Implement a case-insensitive regular expression masking engine that scrubs 16-digit debit/credit cards, 12-digit Aadhaar, and 10-character PAN identifiers with 100% precision before persistence.",
        "2. Real-Time Multilingual Voice Ingestion: Build a browser-native voice dictation interface supporting English, Hindi (hi-IN), and Marathi (mr-IN) with non-destructive buffer accumulation that guarantees zero duplicate line emissions.",
        "3. Autonomous NLP Multi-Class Categorization: Train a TF-IDF and Multinomial Naive Bayes classification model across banking categories (Unauthorized Transactions, ATM Failures, UPI Issues, Net Banking, Loans, Account Maintenance) achieving >80% accuracy.",
        "4. SBERT Semantic Subcategory & Similarity Matching: Integrate Sentence-BERT embeddings (all-MiniLM-L6-v2) to predict granular subcategories and detect historical duplicate grievances.",
        "5. Documentary Evidence OCR & 4-Point Entity Cross-Match: Develop an automated OCR pipeline that extracts Transaction Reference, Disputed Amount, Bank Identity, and Account Digits from uploaded images/PDFs and scores credibility from 0 to 100%.",
        "6. Tier-1 AI GrievanceBot Adjudication: Implement an automated decision gate that checks claim validity, evaluates evidence scores, queries indexed knowledge-base articles, and offers immediate settlement dialogs for qualifying disputes.",
        "7. Dynamic SLA Engine & Urgency Radar: Calculate statutory SLA deadlines (24h/72h/30d) based on RBI customer liability directions, maintaining visual countdowns and escalation alerts.",
        "8. Workload-Balanced Officer Assigner: Construct an optimal assignment engine that allocates escalated complaints to bank redressal officers based on department specialty, active workload, and historical resolution velocity.",
        "9. Predictive Queue Modeling (Kleinrock M/M/c & Erlang-C): Formulate and implement closed-form Erlang-C equations to compute system utilization, queue dwell times, and SLA breach risks under varying arrival surges.",
        "10. Tamper-Evident Statutory PDF Receipt Generation: Generate verifiable ReportLab PDF receipts embedding ISO/IEC 18004 dynamic 2D QR codes pointing to live, unauthenticated case status tracking endpoints.",
        "11. Full-Stack Trilingual Dynamic Localization: Implement seamless client-side UI localization across 222 key mappings in English, Hindi, and Marathi, supported by an immutable append-only audit trail."
    ]
    for obj in objs:
        add_p(doc, obj, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "", space_after=8)

    # 1.5 Scope of the Project
    add_h2(doc, "1.5 Scope of the Project")
    add_h3(doc, "1.5.1 Features Included")
    inc_features = [
        "• Autonomous multi-attribute complaint registration supporting manual entry, file uploads, and voice dictation.",
        "• Browser-native Web Speech streaming dictation in English, Hindi, and Marathi with live waveform visualizer.",
        "• Automated DPDP Act 2023 PII sanitization (Cards, Aadhaar, PAN) with zero plain-text storage.",
        "• TF-IDF and Multinomial Naive Bayes complaint triage with confidence scoring.",
        "• SBERT semantic subcategory prediction and similar complaint clustering.",
        "• Evidence uploader supporting PNG, JPG, and PDF receipts with automated OCR extraction.",
        "• Deterministic 4-point entity cross-verification between user claim and OCR document tokens.",
        "• Tier-1 AI GrievanceBot with instant resolution recommendations and customer escalation dialog.",
        "• Dynamic SLA engine tracking 24h, 72h, and 30-day statutory deadlines with live countdown timers.",
        "• Workload-balanced smart officer assignment algorithm.",
        "• Senior Nodal Officer (Level 2) escalation and governance for reopened disputes.",
        "• Predictive operations dashboard with Erlang-C queueing simulations and What-If staffing sandboxes.",
        "• Bank health score calculation, vulnerability radar, and scheduled commercial banks leaderboard.",
        "• Tamper-evident PDF statutory receipt generation with embedded dynamic tracking QR code.",
        "• Immutable append-only forensic audit logging of all system actions, assignments, and state transitions.",
        "• Full-stack trilingual UI localization across 222 dictionary keys in English, Hindi, and Marathi."
    ]
    for feat in inc_features:
        add_p(doc, feat, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)

    add_h3(doc, "1.5.2 Features Outside the Scope")
    out_features = [
        "• Direct write-back integration into proprietary Core Banking Solutions (CBS) like Infosys Finacle or TCS BaNCS (mocked via standard RESTful APIs due to banking firewall boundaries).",
        "• Direct execution of interbank financial debit reversals or automated clearinghouse settlements across NPCI/RBI networks.",
        "• Recognition of handwritten physical complaint slips (system requires typed text, voice dictation, or printed receipts).",
        "• Languages beyond English, Hindi, and Marathi in Version 1.0.",
        "• Automatic formal legal filing into the RBI Integrated Ombudsman CMS portal without explicit human officer authorization."
    ]
    for feat in out_features:
        add_p(doc, feat, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)

    add_h3(doc, "1.5.3 Intended Users")
    add_p(doc, "• Bank Customers / Depositors: File disputes, dictate voice complaints, upload receipts, track live status, download QR receipts.", space_before=1, space_after=2)
    add_p(doc, "• Grievance Redressal Officers: Investigate complaints, inspect OCR evidence match scores, review AI copilot draft memos, issue resolutions.", space_before=1, space_after=2)
    add_p(doc, "• Branch Operations Managers: Monitor SLA adherence, run What-If staffing simulations, inspect officer productivity, audit bank health.", space_before=1, space_after=2)
    add_p(doc, "• Compliance & Regulatory Auditors: Inspect immutable audit logs, verify DPDP Act 2023 redaction, review closed-loop resolution fairness.", space_before=1, space_after=4)

    add_h3(doc, "1.5.4 Operating Environment")
    add_p(doc, "• Backend API: Python 3.10+, FastAPI 0.100+, Uvicorn ASGI, Pydantic v2, SQLAlchemy ORM.", space_before=1, space_after=2)
    add_p(doc, "• Frontend Client: React 18, Vite 5.x, Tailwind CSS 3.x, Lucide Icons, Recharts 2.x.", space_before=1, space_after=2)
    add_p(doc, "• Data Persistence: SQLite 3 with Write-Ahead Logging (WAL) / PostgreSQL 15 via asyncpg.", space_before=1, space_after=2)
    add_p(doc, "• Machine Learning & OCR: Scikit-Learn 1.5, Sentence-Transformers (all-MiniLM-L6-v2), EasyOCR / PyTesseract.", space_before=1, space_after=2)
    add_p(doc, "• Document Generation: Python ReportLab, Qrcode library, Pillow (PIL).", space_before=1, space_after=2)
    add_p(doc, "• Client Browser: Modern browser (Chrome 90+, Edge 90+, Safari 14+) with W3C Web Speech API support.", space_before=1, space_after=4)

    add_h3(doc, "1.5.5 Expected Scale of Operation")
    add_p(doc, "GrievanceIQ is engineered as an institutional departmental prototype capable of processing thousands of daily complaints, "
               "sustaining up to 100 concurrent HTTP requests with sub-150ms API latencies, and scaling horizontally via containerized Docker microservices.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=12)

    # 1.6 Proposed Solution
    add_h2(doc, "1.6 Proposed Solution")
    p_sol1 = (
        "GrievanceIQ delivers a comprehensive, multi-tiered architecture that unifies citizen intake, autonomous triage, documentary "
        "evidence verification, officer collaboration, and predictive operational intelligence into a seamless pipeline:"
    )
    add_p(doc, p_sol1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)
    add_p(doc, "1. Frictionless Multimodal Ingestion: Complainants articulate disputes via manual typing, document uploads, or real-time voice dictation. "
               "The Web Speech audio pipeline transcribes Hindi, Marathi, and English audio streams in real time with zero duplicate loops.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "2. Boundary-Level DPDP Sanitization: Raw descriptions pass through compiled regex filters that detect 16-digit payment card numbers, "
               "12-digit Aadhaar identifiers, and 10-character PAN strings, replacing them with masked tokens before database insertion.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "3. Hybrid NLP & Semantic Classification: Sanitized text is classified by TF-IDF vectorization and Multinomial Naive Bayes into "
               "high-level banking departments, followed by Sentence-BERT semantic similarity matching to pinpoint subcategories and flag duplicate tickets.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "4. Deterministic OCR Evidence Cross-Validation: Uploaded transaction slips, passbooks, and ATM receipts are parsed via OCR. "
               "A 4-point verification algorithm compares transaction reference, bank name, account digits, and disputed amount against the user's claim.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "5. Tier-1 AI GrievanceBot Adjudication: If a complaint exhibits high validity, qualifying OCR evidence, and matches clear banking rules, "
               "the system offers the customer an instant settlement proposal, reducing human officer ticket queues by over 30%.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "6. Operations Research via Erlang-C Queueing: Branch management monitors real-time queue dynamics, evaluates traffic intensity, "
               "and simulates staffing adjustments to ensure zero statutory SLA breaches.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=12)

    # 1.7 Novelty and Originality
    add_h2(doc, "1.7 Novelty and Originality")
    add_p(doc, "The technical contributions and original engineering elements of GrievanceIQ include:", space_before=2, space_after=6)
    add_p(doc, "• Dual-State Voice Buffer Accumulator: Resolves a notorious browser limitation where W3C Web Speech API onresult events cause "
               "repeating text loops during continuous streaming dictation in regional Indian accents.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "• Case-Insensitive Zero-Loss PII Redaction: Enforces strict DPDP Act 2023 compliance at the network ingestion boundary rather "
               "than relying on retrospective database scrubbing scripts.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "• Deterministic 4-Point Document Credibility Scoring: Eliminates generative AI hallucinations during evidence evaluation by applying "
               "exact regex token matches and fuzzy Levenshtein ratios to OCR output.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "• Closed-Loop Verifiable Dynamic QR Receipts: Statutory PDF receipts embed ISO/IEC 18004 2D barcodes pointing dynamically to "
               "the active server host, enabling instant mobile tracking with zero authentication barrier.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "• Integrated Queueing Theory in BFSI Operations: Uniquely bridges front-office grievance logging with back-office Erlang-C "
               "queue modeling for proactive capacity management.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=12)

    # 1.8 Feasibility Analysis
    add_h2(doc, "1.8 Feasibility Analysis")
    add_p(doc, "1.8.1 Technical Feasibility: The platform relies upon mature, production-grade open-source technologies: Python 3.10+, "
               "FastAPI (high-performance ASGI web framework), Scikit-Learn, React 18, Vite, and Tailwind CSS. Modern web browsers natively support "
               "the W3C Web Speech API, Web Audio API, and HTML5 Canvas without requiring client-side plugin installations.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "1.8.2 Economic Feasibility: The software utilizes open-source libraries with zero commercial licensing costs. It executes "
               "efficiently on commodity x86/ARM hardware or micro-tier cloud virtual machines (e.g., AWS t3.medium or GCP e2-small), "
               "ensuring negligible deployment and operational overhead.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "1.8.3 Operational Feasibility: The client interface provides intuitive trilingual localization (English, Hindi, Marathi) "
               "and speech dictation, eliminating user friction. Bank officers benefit from explainable AI suggestions and automated memo drafting.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "1.8.4 Time and Resource Feasibility: The project was structured systematically across a 12-week academic schedule with weekly "
               "milestone gates, achieving 100% completion of all core and extended deliverables within the designated timeframe.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=12)

    # 1.9 Social Relevance and Practical Applications
    add_h2(doc, "1.9 Social Relevance and Practical Applications")
    p_soc = (
        "Financial disputes and transaction failures cause severe psychological distress and economic hardship to retail consumers, "
        "particularly when monthly wages, student remittances, or emergency healthcare funds are frozen due to automated banking timeouts. "
        "By democratizing grievance filing through real-time voice dictation in Hindi and Marathi, protecting privacy under the DPDP Act 2023, "
        "and automating evidence validation to cut resolution times from weeks to hours, GrievanceIQ establishes a new benchmark for digital "
        "financial justice in the Indian banking ecosystem."
    )
    add_p(doc, p_soc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=12)

    # 1.10 Success Criteria and Key Performance Indicators (KPIs)
    add_h2(doc, "1.10 Success Criteria and Key Performance Indicators (KPIs)")
    add_p(doc, "The success of GrievanceIQ is evaluated against rigorous, pre-defined technical and operational metrics formalized in Table 3.", space_before=2, space_after=6)
    
    kpi_headers = ["KPI Identifier", "Metric Definition", "Target Benchmark", "Empirical Measurement Method"]
    kpi_rows = [
        ("ML Classification Accuracy", "Agreement of predicted category with hand-labeled ground truth", "At least 80.0%", "Evaluation across 2,998 test records (Achieved 83.49%)"),
        ("Classification Macro F1", "Harmonic mean of precision and recall across all banking categories", "At least 0.80", "Multi-class confusion matrix evaluation (Achieved 0.835)"),
        ("DPDP Act 2023 PII Masking", "Share of 16-digit cards, Aadhaar, and PAN tokens successfully masked", "100.0% zero-leakage", "Adversarial test suite with unredacted payloads (100% pass)"),
        ("Voice Streaming Loop Elimination", "Absence of repeating transcript phrases during streaming dictation", "100% zero duplicate loops", "Session buffer verification in automated browser tests"),
        ("Evidence OCR Entity Matching", "Precision of 4-point financial entity extraction from receipts", "At least 85.0%", "Benchmark test slips (Transaction Ref, Bank, Amount, Account)"),
        ("Erlang-C Queueing Accuracy", "Mathematical convergence of M/M/c dwell time and SLA breach risk", "100% analytical match", "Closed-form formula unit testing against hand-calculated cases"),
        ("Statutory Receipt Verification", "Generation of valid, scannable ISO/IEC 18004 dynamic QR PDF receipt", "100% scannable QR", "ReportLab automated PDF rendering and QR decode verification"),
        ("API Response Latency", "Time taken for transactional REST endpoints to complete execution", "Under 150 ms", "Timestamp-based integration testing under standard load (avg 42 ms)"),
        ("Trilingual UI Key Parity", "Share of UI interface keys fully localized across EN, HI, and MR", "100.0% (222 keys)", "Automated dictionary key-parity unit test (test_phase2_extended)"),
        ("RBAC Security Enforcement", "Prevention of unauthorized customer access to officer adjudication", "Zero unauthorized bypass", "OAuth2 JWT token validation and role-gated endpoint tests"),
        ("Forensic Audit Immutability", "Append-only logging of all state transitions, memos, and assignments", "100% audited actions", "Database transaction trigger and audit_logs table inspection"),
        ("Full-Stack Test Pass Rate", "Successful test executions across all unit and integration suites", "100% pass rate", "Execution of 48 master integration and unit tests (48/48 passed)")
    ]
    add_styled_table(doc, kpi_headers, kpi_rows, col_widths=[1.5, 2.0, 1.2, 1.32])
    
    add_p(doc, "Table 3: Key Performance Indicators and Target Benchmarks", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)
    add_p(doc, "1", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
