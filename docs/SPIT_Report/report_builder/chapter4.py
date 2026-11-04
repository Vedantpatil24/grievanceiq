# chapter4.py
# Chapter 4: System Architecture and Detailed Design

import os
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table, add_figure_box,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter4(doc):
    add_h1(doc, "4   System Architecture and Detailed Design")
    
    # 4.1 Overall System Architecture
    add_h2(doc, "4.1 Overall System Architecture")
    p_arch1 = (
        "GrievanceIQ is engineered as a modern, layered, and decoupled Client-Server Architecture incorporating a modular "
        "service-oriented backend. Its architectural foundation enforces strict separation of concerns, guarantees zero plain-text "
        "PII persistence at the network boundary, isolates probabilistic machine learning inference from deterministic database "
        "transactions, and provides high-concurrency asynchronous I/O. The system is partitioned into five distinct architectural layers:"
    )
    add_p(doc, p_arch1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)
    
    add_p(doc, "1. Client Presentation Tier: Single-Page Application (SPA) built with React 18, Vite, and Tailwind CSS. Provides accessible "
               "views for public grievance intake, real-time voice streaming with live waveform canvas visualizer, public status tracking with "
               "dynamic SLA countdowns, officer resolution workspace, AI Copilot memo drafter, bank health scorecards, and interactive "
               "What-If queueing simulation sandboxes. Communicates with the backend exclusively via asynchronous RESTful JSON over HTTPS.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "2. API Gateway & Middleware Tier: Powered by Python FastAPI and Uvicorn ASGI server. Enforces CORS policies, validates request "
               "payloads via Pydantic v2 schemas (with extra=\"forbid\" enforcement), verifies Bearer JWT tokens, inspects user role permissions "
               "(Customer, Officer, Admin), and extracts dynamic base URLs to ensure QR code tracking links adapt to the host environment.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "3. Pipeline Orchestration Tier: Directs incoming disputes through a multi-stage state machine: Intake -> DPDP Sanitization -> "
               "TF-IDF / MNB Triage -> SBERT Subcategory Prediction -> OCR Evidence Validation -> Tier-1 AI GrievanceBot Adjudication -> "
               "SLA Calculation -> Smart Officer Assignment -> Statutory Receipt Generation. Tracks latency per stage and logs execution events.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "4. Application & Domain Services Tier: Houses core functional modules M0 through M7 (detailed in Section 4.2), including the "
               "DPDP 2023 regex engine, the Scikit-Learn text classifier, the Sentence-BERT semantic search engine, the 4-point OCR entity "
               "cross-matcher, the Kleinrock M/M/c Erlang-C queue simulator, and the ReportLab PDF receipt generator.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "5. Data Persistence & Forensic Audit Tier: Relational database layer running SQLite 3 in high-concurrency Write-Ahead Logging (WAL) "
               "mode or hosted PostgreSQL 15. The schema comprises 18 normalized tables governed by foreign keys, cascading deletions, CHECK "
               "constraints, and database rules ensuring an immutable, append-only audit trail.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=10)

    add_figure_box(doc, 1, "Overall System Architecture of GrievanceIQ")

    # 4.2 Component and Module Description
    add_h2(doc, "4.2 Component and Module Description")
    add_p(doc, "The platform decomposes complex banking grievance workflows into eight decoupled domain modules:", space_before=2, space_after=6)

    mods = [
        ("Module M0: Dispute Intake & DPDP Act 2023 PII Sanitizer",
         "Purpose: Collects multi-attribute grievance details and voice streams; enforces case-insensitive regex redaction to strip 16-digit payment card numbers, 12-digit Aadhaar identifiers, and 10-character PAN tokens before database insertion.\n"
         "Inputs: Raw user form payload, audio stream transcription, transaction metadata.\n"
         "Outputs: Scrubbed, legal-compliant complaint description, generated unique Grievance ID (GIQ-YYYY-XXXXX).\n"
         "Dependencies: Python re module, Pydantic v2 schemas, W3C Web Speech API."),
        
        ("Module M1: Autonomous NLP Categorization Engine",
         "Purpose: Autonomously classifies unstructured complaint descriptions into primary banking departments (Unauthorized Transactions, ATM Failures, UPI Issues, Net Banking, Loans, Account Maintenance).\n"
         "Inputs: Sanitized complaint description string.\n"
         "Outputs: Predicted category, department mapping, probabilistic confidence score.\n"
         "Dependencies: Scikit-Learn 1.5 (TfidfVectorizer, MultinomialNB), classifier.pkl, vectorizer.pkl."),
        
        ("Module M2: Sentence-BERT Semantic Subcategory & Similarity Engine",
         "Purpose: Generates 384-dimensional dense semantic embeddings to predict granular dispute subcategories and detect historical duplicate filings.\n"
         "Inputs: Sanitized complaint text, historical complaint embeddings database.\n"
         "Outputs: Subcategory prediction, nearest-neighbor similar complaints with cosine similarity indices.\n"
         "Dependencies: Sentence-Transformers (all-MiniLM-L6-v2), PyTorch, NumPy, Scipy spatial distance."),
        
        ("Module M3: Documentary Evidence OCR & 4-Point Entity Cross-Matcher",
         "Purpose: Extracts text from uploaded transaction receipts, passbooks, and ATM slips; executes deterministic 4-point cross-validation (Ref ID, Bank, Amount, Account digits) against customer assertions.\n"
         "Inputs: Uploaded receipt image (PNG/JPG) or PDF file, complaint metadata.\n"
         "Outputs: OCR raw text, individual match flags, composite credibility score (0 to 100%).\n"
         "Dependencies: EasyOCR, PyTesseract, Pillow (PIL), PyMuPDF (fitz)."),
        
        ("Module M4: Tier-1 AI GrievanceBot Adjudication Gate",
         "Purpose: Evaluates complaint validity and OCR evidence credibility to offer instant automated settlement proposals for routine disputes, deflecting human officer queues.\n"
         "Inputs: Complaint record, OCR evidence score, complaint validity score, KnowledgeBase rules.\n"
         "Outputs: Automated resolution proposal, refund recommendation, or escalation flag.\n"
         "Dependencies: bot_resolver.py, KnowledgeBaseArticle repository, SQLAlchemy Session."),
        
        ("Module M5: Dynamic SLA Calculation & Urgency Engine",
         "Purpose: Enforces statutory RBI turnaround directions (72h for unauthorized debits, 24h for ATM failures, 30 days for ombudsman), calculating live countdowns and urgency tiers.\n"
         "Inputs: Complaint submission timestamp, transaction date, category ID.\n"
         "Outputs: SLA deadline timestamp, remaining countdown hours, urgency level (CRITICAL, HIGH, MEDIUM, LOW), SLA breach flag.\n"
         "Dependencies: sla_engine.py, datetime, timedelta."),
        
        ("Module M6: Workload-Balanced Smart Assigner",
         "Purpose: Allocates escalated complaints to bank redressal officers based on department specialty, active backlog, and historical resolution speed to ensure equitable workload distribution.\n"
         "Inputs: Unassigned complaint record, department officer pool.\n"
         "Outputs: Assigned officer ID, assignment timestamp, assignment_history audit record.\n"
         "Dependencies: smart_assigner.py, User repository, SQLAlchemy query aggregations."),
        
        ("Module M7: Predictive Queue Modeling & Bank Intelligence",
         "Purpose: Implements Kleinrock M/M/c Erlang-C queueing formulations to calculate system utilization, queue dwell times, and SLA breach risks; powers interactive What-If staffing simulations and bank health scorecards.\n"
         "Inputs: Arrival rate lambda, service rate mu, officer count c, bank complaint history.\n"
         "Outputs: Dwell time W_q, queue size L_q, breach probability, bank health score (0-100), bank performance leaderboard.\n"
         "Dependencies: bank_intelligence.py, math, NumPy, Erlang-C closed-form solvers.")
    ]

    for m_title, m_desc in mods:
        add_p(doc, m_title, bold=True, size=11, color=COLOR_PRIMARY, space_before=4, space_after=2)
        add_p(doc, m_desc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=6, size=10.5)

    # 4.3 Architecture Selection and Justification
    add_h2(doc, "4.3 Architecture Selection and Justification")
    p_just = (
        "GrievanceIQ adopts a Layered Three-Tier Client-Server Architecture with Modular Domain Services. This architectural "
        "pattern was selected over monolithic or micro-frontend designs due to five compelling engineering requirements:"
    )
    add_p(doc, p_just, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    add_p(doc, "• Decoupling of Security and UI Boundaries: By enforcing DPDP Act 2023 PII sanitization at the API gateway layer, customer "
               "browser code cannot bypass redaction, ensuring zero plain-text sensitive data enters the persistence tier.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "• Deterministic Isolation of Financial and Operational Math: Probabilistic machine learning triage (TF-IDF/MNB) and OCR text extraction "
               "are strictly segregated from deterministic SLA calculations, Erlang-C queue formulas, and immutable audit logs.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "• High Asynchronous Concurrency: Utilizing FastAPI atop the Uvicorn ASGI event loop allows the server to handle non-blocking "
               "database queries and streaming voice transcription without thread starvation.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "• Independent Testability and Module Governance: Each domain module (M0 to M7) maintains dedicated unit tests and metrics, "
               "preventing cross-module regression and ensuring adherence to the Single Responsibility Principle.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=8)

    # 4.4 Data Flow Diagrams (DFD)
    add_h2(doc, "4.4 Data Flow Diagram (DFD)")
    add_p(doc, "Data flow across GrievanceIQ conforms to the Yourdon-DeMarco notation, utilizing open-ended bars (D1-D6) for data stores, "
               "rectangles for external entities, circles for operational processes, and directed arrows for data flows.", space_before=2, space_after=6)
    
    dfd_stores = [
        ("D1", "complaints (Central grievance records with masked text, status, SLA deadline, and verification scores)"),
        ("D2", "users (System users: Customers, Grievance Redressal Officers, Branch Managers, System Admins)"),
        ("D3", "evidence_docs & ocr_extractions (Uploaded transaction receipts, passbooks, and raw OCR text tokens)"),
        ("D4", "predictions & similar_complaints (ML category classifications, SBERT embeddings, similarity mappings)"),
        ("D5", "audit_logs (Immutable append-only forensic event log capturing all actions and state transitions)"),
        ("D6", "resolutions & investigation_notes (Officer adjudication memos, refund recommendations, case notes)")
    ]
    add_styled_table(doc, ["Store ID", "Logical Content and Relational Entity Scope"], dfd_stores, col_widths=[1.2, 4.82])
    add_p(doc, "Table 51: DFD Data Stores", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=10, italic=True, size=10, color=COLOR_MUTED)

    add_h3(doc, "4.4.1 Context-Level DFD (Level 0)")
    add_p(doc, "The Level 0 Context Diagram (Figure 2) depicts GrievanceIQ as a single centralized system interacting with five external entities: "
               "the Aggrieved Complainant, the Grievance Redressal Officer, the Branch Operations Manager, the Regulatory Auditor, and External Core Banking Systems.", space_before=2, space_after=4)
    add_figure_box(doc, 2, "Level 0 DFD: Context Diagram")

    add_h3(doc, "4.4.2 Level 1 DFD: Subsystem Decompositions")
    add_p(doc, "The operational workflow decomposes into four interconnected Level 1 functional diagrams:", space_before=2, space_after=4)
    add_p(doc, "• Diagram 1A: Intake, PII Redaction, and Autonomous ML Triage (Process 1.0 to 3.0)", space_before=1, space_after=2)
    add_figure_box(doc, 3, "Level 1 DFD, Diagram 1A: Intake, PII Redaction & NLP Triage")
    add_p(doc, "• Diagram 1B: Evidence OCR Extraction and Tier-1 Bot Adjudication (Process 4.0 to 5.0)", space_before=1, space_after=2)
    add_figure_box(doc, 4, "Level 1 DFD, Diagram 1B: Evidence OCR & Bot Resolution")
    add_p(doc, "• Diagram 1C: Smart Officer Assignment, SLA Tracking, and Senior Escalation (Process 6.0 to 7.0)", space_before=1, space_after=2)
    add_figure_box(doc, 5, "Level 1 DFD, Diagram 1C: Officer Assignment & SLA Monitoring")
    add_p(doc, "• Diagram 1D: Predictive Queueing Intelligence, Statutory Receipt, and Audit Trail (Process 8.0 to 10.0)", space_before=1, space_after=2)
    add_figure_box(doc, 6, "Level 1 DFD, Diagram 1D: Predictive Queueing, Audit & Receipt")

    add_h3(doc, "4.4.3 Level 2 DFD: Detailed Process Specifications")
    add_p(doc, "Core processes are decomposed further into fine-grained Level 2 workflows: Process 1.0 (Intake & DPDP Sanitization, Figure 7), "
               "Process 2.0 (OCR Extraction & 4-Point Entity Cross-Match, Figure 8), Process 3.0 (TF-IDF & SBERT Classification, Figure 9), "
               "Process 4.0 (Kleinrock M/M/c Queueing Simulator, Figure 10), Process 5.0 (Officer Adjudication & Memo Drafting, Figure 11), "
               "and Process 6.0 (Statutory PDF Receipt & Dynamic QR Encoding, Figure 12).", space_before=2, space_after=6)
    add_figure_box(doc, 7, "Level 2 DFD: Process 1.0, Intake and DPDP PII Sanitization")
    add_figure_box(doc, 8, "Level 2 DFD: Process 2.0, OCR Extraction & 4-Point Entity Cross-Match")
    add_figure_box(doc, 9, "Level 2 DFD: Process 3.0, TF-IDF and SBERT Classification Engine")
    add_figure_box(doc, 10, "Level 2 DFD: Process 4.0, Kleinrock M/M/c Predictive Queue Simulator")
    add_figure_box(doc, 11, "Level 2 DFD: Process 5.0, Officer Adjudication & Resolution Memo")
    add_figure_box(doc, 12, "Level 2 DFD: Process 6.0, ReportLab PDF Receipt & Dynamic QR Encoding")

    # 4.5 UML Diagrams
    add_h2(doc, "4.5 UML Diagrams")
    add_p(doc, "Comprehensive UML models document the system structure, object interactions, behavioral lifecycles, and deployment:", space_before=2, space_after=6)
    add_p(doc, "• 4.5.1 Use Case Diagram (Figure 15): Illustrates relationships between Actors (Customer, Officer, Manager, Auditor) and Use Cases (File Dispute, Dictate Voice, Verify Evidence, Run Queue Simulation, Generate Receipt).", space_before=1, space_after=2)
    add_figure_box(doc, 15, "Use Case Diagram of GrievanceIQ")
    add_p(doc, "• 4.5.2 Class Diagram, Part 1: Service Layer (Figure 16): Delineates service classes: IngestionHandler, DPDPFilter, MLClassifier, SBERTEngine, OCREngine, BotResolver, SLAEngine, SmartAssigner, QueueSimulator, ReportLabGenerator, AuditService.", space_before=1, space_after=2)
    add_figure_box(doc, 16, "Class Diagram, Part 1: Service & Orchestration Layer")
    add_p(doc, "• 4.5.3 Class Diagram, Part 2: Relational Domain Entity Model (Figure 17): Delineates persistent entities: Complaint, User, Company, Department, Category, EvidenceDoc, Prediction, SimilarComplaint, Resolution, AuditLog.", space_before=1, space_after=2)
    add_figure_box(doc, 17, "Class Diagram, Part 2: Relational Domain Entity Model")
    add_p(doc, "• 4.5.4 Sequence Diagrams (Figures 18 & 19): Chronological message flow between Browser Client, FastAPI Gateway, ML Pipeline, OCR Service, and Relational Database during grievance intake and adjudication.", space_before=1, space_after=2)
    add_figure_box(doc, 18, "Sequence Diagram, Part 1: Ingestion, Voice Dictation & Triage")
    add_figure_box(doc, 19, "Sequence Diagram, Part 2: Tier-1 Bot Adjudication & Escalation")
    add_p(doc, "• 4.5.5 Activity Diagrams (Figures 20 & 21): Swimlane execution flows across Customer, FastAPI Backend, and Background ML/OCR Workers.", space_before=1, space_after=2)
    add_figure_box(doc, 20, "Activity Diagram, Part 1: Multi-Attribute Intake & Redaction")
    add_figure_box(doc, 21, "Activity Diagram, Part 2: Document Verification & Resolution")
    add_p(doc, "• 4.5.6 State Machine Diagrams (Figures 22 & 23): Complete lifecycle transitions of complaints (Submitted -> Triaged -> In Review -> Evidence Verified -> Resolved / Reopened).", space_before=1, space_after=2)
    add_figure_box(doc, 22, "State Machine Diagram, Part 1: Grievance Lifecycle Pipeline")
    add_figure_box(doc, 23, "State Machine Diagram, Part 2: Officer Assignment Lifecycle")
    add_p(doc, "• 4.5.7 User Flow Diagrams (Figures 24 & 25): Step-by-step user decision trees for complainants and bank officers.", space_before=1, space_after=2)
    add_figure_box(doc, 24, "User Flow Diagram, Part 1: Complainant Mobile & Web Flow")
    add_figure_box(doc, 25, "User Flow Diagram, Part 2: Bank Officer Adjudication Flow")

    # 4.6 Database Design
    add_h2(doc, "4.6 Database Design")
    add_h3(doc, "4.6.1 ER Diagram")
    add_p(doc, "Figure 26 depicts the complete Entity-Relationship model comprising 18 relational entities, enforcing strict 1:N cardinalities with foreign-key referential integrity.", space_before=2, space_after=4)
    fig_dir = "G:/Mini_project/docs/SPIT_Report/figures"
    add_figure_box(doc, 26, "Entity-Relationship Diagram of GrievanceIQ", image_path=os.path.join(fig_dir, "fig13_master_erd.png"))

    add_h3(doc, "4.6.2 Relational Schema Specifications")
    add_p(doc, "The public database schema consists of 18 normalized relations:", space_before=2, space_after=4)
    schema_specs = [
        "users (id: integer primary key, email: text unique, password_hash: text, full_name: text, role: text, department_id: integer?, is_active: boolean, created_at: timestamptz)",
        "companies (id: integer primary key, name: text unique, code: text, created_at: timestamptz)",
        "departments (id: integer primary key, name: text unique, description: text, sla_hours: integer)",
        "categories (id: integer primary key, name: text unique, department_id: integer references departments(id), default_priority: text)",
        "complaints (id: integer primary key, complaint_id: text unique, user_id: integer references users(id), company_id: integer references companies(id), category_id: integer references categories(id), department_id: integer references departments(id), assigned_officer_id: integer? references users(id), description: text, description_sanitized: text, transaction_id: text, transaction_date: date, disputed_amount: numeric(15,2), status: text, priority: text, sla_deadline: timestamptz, evidence_doc_url: text?, verification_score: numeric(5,2), qr_code_url: text?, created_at: timestamptz, resolved_at: timestamptz?)",
        "evidence_docs (id: integer primary key, complaint_id: integer references complaints(id), file_name: text, file_path: text, mime_type: text, file_size_kb: integer, uploaded_at: timestamptz)",
        "ocr_extractions (id: integer primary key, doc_id: integer references evidence_docs(id), extracted_text: text, extracted_entities: jsonb, match_score: numeric(5,2), created_at: timestamptz)",
        "predictions (id: integer primary key, complaint_id: integer references complaints(id), predicted_category: text, confidence: numeric(5,4), model_version: text, created_at: timestamptz)",
        "similar_complaints (id: integer primary key, complaint_id: integer references complaints(id), matched_complaint_id: integer references complaints(id), similarity_score: numeric(5,4))",
        "resolutions (id: integer primary key, complaint_id: integer references complaints(id), resolving_officer_id: integer references users(id), memo_text: text, refund_amount: numeric(15,2), resolution_type: text, created_at: timestamptz)",
        "investigation_notes (id: integer primary key, complaint_id: integer references complaints(id), officer_id: integer references users(id), note_text: text, created_at: timestamptz)",
        "escalation_history (id: integer primary key, complaint_id: integer references complaints(id), escalation_level: integer, reason: text, escalated_to_id: integer references users(id), escalated_at: timestamptz)",
        "assignment_history (id: integer primary key, complaint_id: integer references complaints(id), officer_id: integer references users(id), assigned_by_id: integer? references users(id), assigned_at: timestamptz)",
        "status_history (id: integer primary key, complaint_id: integer references complaints(id), old_status: text, new_status: text, changed_by_id: integer? references users(id), changed_at: timestamptz)",
        "complaint_messages (id: integer primary key, complaint_id: integer references complaints(id), sender_id: integer references users(id), role: text, message_text: text, sent_at: timestamptz)",
        "notifications (id: integer primary key, user_id: integer references users(id), complaint_id: integer? references complaints(id), title: text, message: text, is_read: boolean, created_at: timestamptz)",
        "feedback (id: integer primary key, complaint_id: integer references complaints(id), csat_score: integer, comments: text?, submitted_at: timestamptz)",
        "audit_logs (id: integer primary key, action: text, entity_type: text, entity_id: integer?, user_id: integer? references users(id), details: jsonb, ip_address: text?, \"timestamp\": timestamptz)"
    ]
    for s in schema_specs:
        add_p(doc, f"• {s}", space_before=1, space_after=3, size=9.5)

    # 4.6.11 Normalization
    add_h3(doc, "4.6.11 Schema Normalization and Form Proofs")
    p_norm = (
        "The GrievanceIQ schema was developed strictly to Boyce-Codd Normal Form (BCNF) and Third Normal Form (3NF). "
        "Starting from an unnormalized flat record containing all customer details, complaint tokens, documents, predictions, "
        "and memos, repeating groups were separated into individual relations (1NF). All non-key attributes depend fully on "
        "their primary keys with zero partial dependencies on composite keys (2NF). Transitive dependencies such as "
        "complaint_id -> department_id -> sla_hours were systematically eliminated by factoring departments into a standalone relation (3NF). "
        "Every functional determinant in the relational model is a candidate key, satisfying BCNF across all primary relations."
    )
    add_p(doc, p_norm, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    add_figure_box(doc, "14", "Functional Dependency Graph & 3NF/BCNF Normalization Decomposition", image_path=os.path.join(fig_dir, "fig14_normalization_graph.png"))

    add_p(doc, "Table 64 summarizes the relational anomalies prevented by this normalized design.", space_before=2, space_after=4)
    anom_data = [
        ("Insertion Anomaly", "A department or category can be configured before any complaint exists; a bank customer profile exists independently of grievances."),
        ("Update Anomaly", "Modifying an officer's department or a bank's SLA policy is executed in a single row without scanning millions of historical complaint records."),
        ("Deletion Anomaly", "Purging an unverified draft complaint does not delete the customer's account or system category records (guaranteed via ON DELETE CASCADE / RESTRICT rules)."),
        ("Redundancy Minimization", "Document binary data and OCR text are held in dedicated tables rather than duplicated across repeated status history rows.")
    ]
    add_styled_table(doc, ["Database Anomaly", "Structural Prevention Mechanism in GrievanceIQ Schema"], anom_data, col_widths=[1.5, 4.52])
    add_p(doc, "Table 64: Anomalies Prevented by the Design", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=10, italic=True, size=10, color=COLOR_MUTED)

    # 4.6.12 Indexing Strategy
    add_h3(doc, "4.6.12 Database Indexing Strategy and DDL")
    p_idx = (
        "To guarantee sub-150ms endpoint latencies across high-volume grievance datasets, B-Tree indexes are deployed on all "
        "foreign keys and high-frequency filtering attributes. Table 67 specifies the secondary performance indexes."
    )
    add_p(doc, p_idx, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)
    
    idx_data = [
        ("idx_complaints_user", "complaints(user_id, created_at DESC)", "Speeds up complainant case listing queries"),
        ("idx_complaints_dept_status", "complaints(department_id, status)", "Optimizes officer triage queue retrieval"),
        ("idx_complaints_sla", "complaints(sla_deadline, status)", "Accelerates real-time SLA breach monitoring queries"),
        ("idx_evidence_complaint", "evidence_docs(complaint_id)", "Speeds up document loading during investigation"),
        ("idx_audit_entity_time", "audit_logs(entity_type, entity_id, timestamp DESC)", "Powers fast chronological audit inspections")
    ]
    add_styled_table(doc, ["Index Identifier", "Indexed Table and Column Specification", "Operational Query Acceleration Purpose"], idx_data, col_widths=[1.5, 2.5, 2.02])
    add_p(doc, "Table 67: Proposed Secondary Indexes", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=10, italic=True, size=10, color=COLOR_MUTED)

    add_figure_box(doc, "26-B", "Database Indexing & B-Tree Query Execution Plan", image_path=os.path.join(fig_dir, "fig26_indexing_btree_plan.png"))

    # 4.7 Security and Error Handling Design
    add_h2(doc, "4.7 Security and Error Handling Design")
    p_sec = (
        "Security in GrievanceIQ is designed defensively across four tiers: (1) Ingestion-Level PII Sanitization removing 16-digit cards, "
        "Aadhaar, and PAN tokens, (2) Cryptographic Security via bcrypt work factor 12 and HS256 JWT tokens with strict expiry, "
        "(3) Database Defense via parameterized ORM queries, foreign key referential integrity, and append-only audit rules, and "
        "(4) Structured Error Handling returning consistent JSON envelopes {error_code, message, request_id} while suppressing internal stack traces."
    )
    add_p(doc, p_sec, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=14)

    add_p(doc, "40", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
