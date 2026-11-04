# chapter6.py
# Chapter 6: Subject-Wise Engineering Concepts and APNI Leap Alignment

import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter6(doc):
    add_h1(doc, "6   Subject-Wise Engineering Concepts and APNI Leap Alignment")
    
    p_intro = (
        "The APNI Leap educational initiative at Sardar Patel Institute of Technology bridges undergraduate classroom "
        "theories from Semesters I through VI with authentic, industry-standard engineering implementations. This chapter "
        "maps foundational concepts from seven core Computer Engineering disciplines directly to functional modules, mathematical "
        "formulations, and code artifacts within the GrievanceIQ repository."
    )
    add_p(doc, p_intro, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8)

    # 6.1 Software Engineering
    add_h2(doc, "6.1 Software Engineering")
    p_se = (
        "• Modularity and Separation of Concerns: The system is structured into eight decoupled domain modules (M0 to M7). "
        "Business logic in `validity_checker.py`, `ml_pipeline.py`, `ocr_service.py`, `sla_engine.py`, and `smart_assigner.py` "
        "operates completely independently of the FastAPI web router layer (`main.py`).\n"
        "• Single Source of Truth & DRY: Database schemas and data models are defined uniquely in `create_db.py`. API request "
        "schemas are centralized in Pydantic v2 models. No data transfer structure is duplicated across frontend and backend.\n"
        "• State Machine Pattern: The grievance resolution workflow follows an explicit state machine: Submitted -> Triaged -> "
        "In Review -> Evidence Verified -> Resolved -> Reopened. State transitions are strictly validated, preventing invalid bypasses.\n"
        "• Defensive Programming: Boundary requests are validated with Pydantic `extra=\"forbid\"`, blocking unexpected payload attributes. "
        "Negative amounts, future transaction dates, and empty strings are rejected at the boundary with structured error envelopes.\n"
        "• Test-Driven Verification: The project incorporates automated integration suites (`test_e2e_workflows.py`, `test_phase2_extended.py`) "
        "exercising all 48 test cases before deployment."
    )
    add_p(doc, p_se, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    # 6.2 Computer Networks
    add_h2(doc, "6.2 Computer Networks")
    p_net = (
        "• Client-Server REST Architecture: All communication between the React 18 browser SPA and the Python backend executes "
        "over HTTP/1.1 and HTTP/2 on TCP/IP using structured RESTful JSON payloads, except for binary multipart file uploads.\n"
        "• OSI Layer Mapping: Application Layer (HTTP/REST, JSON, Web Speech), Transport Layer (TCP connection management, port 8000), "
        "Network Layer (IPv4/IPv6 routing), Data Link/Physical Layers (Ethernet/Wi-Fi).\n"
        "• Transport Layer Security (TLS): Production deployment enforces HTTPS encryption via TLS 1.3, ensuring end-to-end "
        "cryptographic confidentiality between depositors and banking servers.\n"
        "• Cross-Origin Resource Sharing (CORS): FastAPI CORSMiddleware restricts incoming requests to authorized origins, "
        "preventing cross-site request forgery and unauthorized domain scraping.\n"
        "• Dynamic Network Base URL Resolution: ReportLab QR generation dynamically resolves the request host headers (`request.base_url`), "
        "guaranteeing that 2D QR codes function identically across localhost, local area network (LAN), and cloud domains."
    )
    add_p(doc, p_net, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    # 6.3 Database Management Systems
    add_h2(doc, "6.3 Database Management Systems")
    p_dbms = (
        "• 3NF and BCNF Relational Normalization: The relational schema decomposes complex grievance records across 18 distinct tables, "
        "eliminating insertion, update, and deletion anomalies while maintaining Boyce-Codd Normal Form across all primary entities.\n"
        "• ACID Transaction Guarantees: All state updates (e.g., complaint assignment + status transition + audit log entry) execute "
        "within atomic SQLAlchemy database transactions with explicit commit/rollback blocks.\n"
        "• Foreign Key Referential Integrity: Cascading deletions (`ON DELETE CASCADE`) maintain referential integrity for dependent "
        "evidence and predictions, while `ON DELETE RESTRICT` protects core master entities (users, companies, departments).\n"
        "• Write-Ahead Logging (WAL) Mode: The SQLite persistence tier is configured with `PRAGMA journal_mode = WAL`, enabling "
        "concurrent read transactions without acquiring exclusive write locks, boosting concurrency 4.8x.\n"
        "• Forensic Immutability via Database Invariants: The `audit_logs` relation is protected against UPDATE and DELETE operations, "
        "ensuring strict tamper-evidence required for banking regulatory compliance."
    )
    add_p(doc, p_dbms, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    # 6.4 Operating Systems
    add_h2(doc, "6.4 Operating Systems")
    p_os = (
        "• Asynchronous Event Loop (ASGI Concurrency): Uvicorn and FastAPI operate atop the Python `asyncio` event loop. "
        "I/O-bound tasks (database queries, network file transfers) yield control cooperatively, allowing a single server process "
        "to sustain over 100 concurrent HTTP connections with minimal memory overhead.\n"
        "• CPU-Bound vs. I/O-Bound Task Partitioning: Intensive OCR image rasterization and transformer embeddings execute in dedicated "
        "thread pools (`run_in_executor`), preventing CPU-bound tasks from blocking the main asynchronous event loop.\n"
        "• Process and Resource Management: In containerized deployment, Docker allocates bounded CPU shares and RAM limits, "
        "protecting host operating systems against resource starvation during complaint arrival surges."
    )
    add_p(doc, p_os, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    # 6.5 Data Structures
    add_h2(doc, "6.5 Data Structures")
    p_ds = (
        "• Sparse Matrices (`scipy.sparse.csr_matrix`): Compactly represent high-dimensional TF-IDF feature vectors, storing only non-zero "
        "term frequencies to achieve O(nnz) memory efficiency during Naive Bayes categorization.\n"
        "• Dense Continuous Arrays (`numpy.ndarray`): Align 384-dimensional SBERT sentence embeddings in contiguous memory for high-speed "
        "SIMD-accelerated BLAS cosine distance computations.\n"
        "• Priority Queues / Min-Heaps: Optimize smart officer assignment, maintaining active officer workloads in min-heap structures for "
        "O(log c) optimal load-balancing selection.\n"
        "• Hash Tables & Dictionaries: Enable average O(1) key resolution across 222 localized trilingual UI tokens and JSON metadata blobs."
    )
    add_p(doc, p_ds, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    # 6.6 Design and Analysis of Algorithms
    add_h2(doc, "6.6 Design and Analysis of Algorithms")
    p_daa = (
        "• Closed-Form Queueing Formulations: Kleinrock M/M/c Erlang-C formulas compute delay probabilities in O(c) time, eliminating "
        "the massive computational overhead of iterative discrete-event Monte Carlo simulations.\n"
        "• Probabilistic Bayesian Inference: The Multinomial Naive Bayes algorithm applies Laplace smoothing (alpha = 1.0) to eliminate "
        "zero-frequency anomalies, evaluating posterior class probabilities in linear O(L + V) time.\n"
        "• Deterministic Finite Automata (DFA) Regex Scanning: String sanitization executes in linear O(L) time via compiled regular expressions, "
        "guaranteeing constant-time token replacement per match without recursive backtracking.\n"
        "• Greedy Workload Optimization: The smart officer assignment algorithm utilizes greedy selection over officer load indices to "
        "achieve optimal equitable backlog distribution."
    )
    add_p(doc, p_daa, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=8)

    # 6.7 Cloud Computing and Microservices
    add_h2(doc, "6.7 Cloud Computing and Microservices")
    p_cloud = (
        "• Stateless Service Design: The FastAPI backend maintains zero session state in server memory; authentication is validated via "
        "cryptographic JWT tokens, enabling seamless horizontal auto-scaling behind cloud load balancers.\n"
        "• Microservice Decoupling: Presentation, API, and Data tiers are containerized via Docker and orchestrated via Docker Compose, "
        "enabling independent vertical and horizontal scaling across cloud providers (AWS, GCP, Azure)."
    )
    add_p(doc, p_cloud, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=12)

    # 6.8 Master Mapping Table
    add_h2(doc, "6.8 Master Mapping of Subjects to Project Implementation")
    add_p(doc, "Table 84 provides the comprehensive master mapping connecting Computer Engineering subjects to concrete implementation artifacts in GrievanceIQ.", space_before=2, space_after=6)

    map_headers = ["Academic Subject", "Theoretical Concept Applied", "GrievanceIQ Module", "Concrete Repository Code Evidence"]
    map_rows = [
        ("Software Engineering", "Modularity & Single Source of Truth", "M0, M1, M5, M6", "create_db.py, validity_checker.py, ml_pipeline.py, test_module_imports"),
        ("Software Engineering", "State Machine Pattern & Invariants", "Pipeline Orchestrator", "Status transitions (Submitted->Resolved), StatusHistory model in create_db.py"),
        ("Software Engineering", "Defensive Input Validation", "API Gateway", "Pydantic v2 schemas with extra='forbid' in main.py"),
        ("Software Engineering", "Test-Driven Integration", "Testing Suite", "test_e2e_workflows.py, test_phase2_extended.py (48/48 tests passing)"),
        ("Computer Networks", "Client-Server REST over HTTP/JSON", "API Gateway / Frontend", "FastAPI routes (/api/complaints/submit), Axios client in frontend/"),
        ("Computer Networks", "OAuth2 Bearer JWT Authentication", "Auth Middleware", "jose.jwt token encoding/decoding with HS256, OAuth2PasswordBearer in main.py"),
        ("Computer Networks", "CORS & Host Header Resolution", "API Middleware", "CORSMiddleware, dynamic request.base_url in pdf_generator / main.py"),
        ("DBMS", "Normalized 3NF / BCNF Schema", "Persistence Tier", "18 relational tables in create_db.py, schema_dbms.sql"),
        ("DBMS", "ACID Transactions & WAL Journaling", "Persistence Tier", "SQLAlchemy session.commit(), PRAGMA journal_mode=WAL in create_db.py"),
        ("DBMS", "Forensic Audit Immutability", "Audit Service", "audit_logs table, log_audit_event() in audit_service.py"),
        ("DBMS", "Secondary Performance Indexing", "Persistence Tier", "idx_complaints_user, idx_complaints_sla in schema_dbms.sql"),
        ("Operating Systems", "Asynchronous Event Loop (ASGI)", "Backend Runtime", "FastAPI async def route handlers, Uvicorn ASGI server"),
        ("Operating Systems", "CPU vs I/O Task Partitioning", "OCR / ML Modules", "run_in_executor for EasyOCR and SBERT embeddings in ocr_service.py"),
        ("Data Structures", "Sparse Feature Matrices", "M1 ML Triage", "scipy.sparse.csr_matrix from TfidfVectorizer in ml_pipeline.py"),
        ("Data Structures", "Dense High-Dimensional Vectors", "M2 Semantic Engine", "NumPy 384-dimensional float32 arrays in semantic_engine.py"),
        ("Data Structures", "Priority Queue / Min-Heap", "M6 Smart Assigner", "Workload min-heap allocation in smart_assigner.py"),
        ("Data Structures", "Hash Maps for Localization", "Trilingual Engine", "Translations dictionary across 222 keys in frontend/TranslationsContext"),
        ("Algorithms (DAA)", "Erlang-C Multi-Server Queue Math", "M7 Queue Simulator", "calculate_erlang_c(), solve_waiting_time() in bank_intelligence.py"),
        ("Algorithms (DAA)", "Multinomial Naive Bayes Inference", "M1 ML Triage", "MultinomialNB posterior probability maximization in ml_pipeline.py"),
        ("Algorithms (DAA)", "DFA Regular Expression Scanning", "M0 DPDP Sanitizer", "Compiled re.sub() for 16-digit cards, Aadhaar, PAN in validity_checker.py"),
        ("Cloud Computing", "Stateless Microservices & Docker", "Deployment Tier", "Dockerfile, docker-compose.yml with API and Frontend services")
    ]
    add_styled_table(doc, map_headers, map_rows, col_widths=[1.2, 1.6, 1.2, 2.02])
    add_p(doc, "Table 84: Mapping of Subjects to Project Implementation", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    add_p(doc, "126", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
