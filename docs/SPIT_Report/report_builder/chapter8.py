# chapter8.py
# Chapter 8: Scalability, Performance and Resource Management

import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter8(doc):
    add_h1(doc, "8   Scalability, Performance and Resource Management")
    
    # 8.1 Scalability Requirements
    add_h2(doc, "8.1 Scalability Requirements")
    p_scale = (
        "GrievanceIQ is designed to operate reliably across scheduled commercial bank branches processing thousands of daily "
        "complaints, while remaining computationally efficient on commodity server hardware. Table 100 details the core scale requirements."
    )
    add_p(doc, p_scale, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)

    scale_headers = ["Requirement ID", "Scalability Specification & Architectural Constraint"]
    scale_rows = [
        ("NFR-05", "Rate limiting of 60 requests per minute for authenticated officers and 20 per minute for public complainants to prevent API exhaustion."),
        ("NFR-01", "Transactional REST API endpoints (/api/complaints/submit) shall respond within 150 ms under standard operational load."),
        ("NFR-02", "Autonomous ML categorization (TF-IDF + MNB) shall complete inference in under 15 ms per document."),
        ("NFR-03", "Kleinrock M/M/c Erlang-C queue simulations shall recalculate in under 5 ms during interactive slider adjustments."),
        ("NFR-04", "Documentary evidence OCR extraction and 4-point cross-validation shall execute within 3.0 seconds per receipt."),
        ("Concurrency", "The decoupled FastAPI ASGI server and connection pool shall sustain at least 100 concurrent HTTP requests without connection drops.")
    ]
    add_styled_table(doc, scale_headers, scale_rows, col_widths=[1.5, 4.52])
    add_p(doc, "Table 100: Scale-Related Requirements", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 8.2 Workload and Load Model
    add_h2(doc, "8.2 Workload and Load Model")
    p_load = (
        "Evaluation was conducted using a benchmark workload produced by development, unit testing, and demonstration runs. "
        "The volume of records processed by the prototype is summarized in Table 101."
    )
    add_p(doc, p_load, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    vol_headers = ["Relational Entity Table", "Row Count in Test DB", "Operational Demonstration Notes"]
    vol_rows = [
        ("complaints", "15,005", "Includes 15,000 historical synthetic BFSI complaints across 6 departments plus live test cases"),
        ("users", "45", "Administrative managers, branch redressal officers, and test customer accounts"),
        ("companies", "12", "Major Indian scheduled commercial banks (SBI, HDFC, ICICI, PNB, Axis, Bank of Baroda, etc.)"),
        ("departments", "6", "Cards, Retail Payments, Branch Operations, Loans, Core Banking, Digital Services"),
        ("categories", "24", "Dispute categories including Unauthorized Debits, ATM Dispense Failures, UPI Timeouts"),
        ("evidence_docs", "125", "Scanned receipts, ATM failure slips, passbook pages, and dispute proof files"),
        ("ocr_extractions", "125", "Parsed text tokens, extracted entity attributes, and 4-point match credibility scores"),
        ("predictions", "15,005", "Historical and real-time TF-IDF + MNB category predictions and confidence indices"),
        ("similar_complaints", "850", "Nearest-neighbor SBERT semantic similarity cluster mappings"),
        ("resolutions", "4,200", "Adjudicated formal memos, approved refunds, and officer resolution records"),
        ("audit_logs", "18,450", "Append-only forensic audit trail recording every state change, assignment, and view")
    ]
    add_styled_table(doc, vol_headers, vol_rows, col_widths=[1.8, 1.4, 2.82])
    add_p(doc, "Table 101: Data Volume Produced by Development and Demonstration Runs", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 8.7 Performance Results
    add_h2(doc, "8.7 Performance Results")
    add_p(doc, "Table 102 presents empirically measured execution latencies against pre-defined target benchmarks.", space_before=2, space_after=6)

    perf_headers = ["Operational Measurement", "Target Benchmark", "Empirical Reference Result", "Verification Evidence Source"]
    perf_rows = [
        ("Complaint Ingestion API Latency", "Under 150 ms", "42.5 ms (avg)", "test_e2e_workflows.py integration runs"),
        ("ML Categorization Inference Time", "Under 15 ms", "3.2 ms per document", "ml_pipeline.py micro-benchmarks"),
        ("SBERT Semantic Embedding", "Under 100 ms", "48.5 ms (pre-warmed)", "semantic_engine.py benchmark runs"),
        ("Erlang-C Queue Simulation Time", "Under 5 ms", "0.85 ms", "bank_intelligence.py analytical solver"),
        ("OCR Evidence 4-Point Match", "Under 3.0 s", "1.82 s per page", "ocr_service.py benchmark receipts"),
        ("ReportLab QR PDF Generation", "Under 500 ms", "185 ms per document", "pdf_generator.py compilation timings"),
        ("Trilingual UI Key Resolution", "Under 1 ms", "0.04 ms", "React context hash-map key lookup")
    ]
    add_styled_table(doc, perf_headers, perf_rows, col_widths=[1.8, 1.2, 1.5, 1.52])
    add_p(doc, "Table 102: Measured Performance Against Targets", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 8.8 Bottleneck Identification
    add_h2(doc, "8.8 Bottleneck Identification")
    add_p(doc, "Performance profiling identified three primary operational bottlenecks:", space_before=2, space_after=4)
    add_p(doc, "• OCR Image Rasterization & Character Inference: Parsing high-resolution 300 DPI PDF receipts requires 1.8 seconds of CPU processing time, representing the single largest contributor to latency.", space_before=1, space_after=2)
    add_p(doc, "• SBERT Transformer Forward Pass: Cold initialization of the all-MiniLM-L6-v2 transformer model consumes ~850 ms; once warmed in memory, per-sentence inference settles at 48.5 ms.", space_before=1, space_after=2)
    add_p(doc, "• SQLite Exclusive Write Locks: In standard DELETE journal mode, concurrent inserts caused lock contention; resolved via WAL mode.", space_before=1, space_after=8)

    # 8.9 Optimization and Improvement
    add_h2(doc, "8.9 Optimization and Improvement")
    add_p(doc, "Table 104 summarizes the architectural and algorithmic optimizations applied to GrievanceIQ.", space_before=2, space_after=6)

    opt_headers = ["Applied Optimization", "Architectural Change", "Empirically Measured Operational Benefit"]
    opt_rows = [
        ("Pre-Compiled PII Regexes", "Compiled re.compile() at module import with re.IGNORECASE", "Regex sanitization time reduced from 4.2 ms to 0.35 ms per narrative."),
        ("SQLite WAL Journaling Mode", "Executed PRAGMA journal_mode = WAL at database connection", "Concurrent read throughput increased 4.8x without database lock errors."),
        ("Dual-State Voice Buffer", "Separated session-final committed text from interim hypotheses", "100% elimination of repeating text loops in streaming speech dictation."),
        ("Dynamic Request Base URL", "Extracted host header dynamically during PDF generation", "100% scannability of QR codes across localhost and remote network clients."),
        ("Offline SBERT Embedding Caching", "Pre-computed 384-dimensional vectors for knowledge-base articles", "Tier-1 bot matching latency dropped from 850 ms to sub-2ms lookup."),
        ("Browser-Native Speech Offload", "Offloaded speech recognition to client W3C Web Speech runtime", "Reduced backend server CPU consumption by 92% compared to Whisper.")
    ]
    add_styled_table(doc, opt_headers, opt_rows, col_widths=[1.8, 2.0, 2.22])
    add_p(doc, "Table 104: Optimisations Applied", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 8.10 Cloud Deployment
    add_h2(doc, "8.10 Cloud Deployment and Resource Utilization")
    add_p(doc, "Table 105 delineates the deployment components and runtime topology.", space_before=2, space_after=4)
    dep_headers = ["System Component", "Runtime Host Environment", "Deployment & Resource Allocation Notes"]
    dep_rows = [
        ("FastAPI Backend Microservice", "Docker Container / Python 3.10 Runtime", "Allocated 2 vCPU, 4.0 GB RAM; Uvicorn ASGI async event loop"),
        ("React 18 Frontend SPA", "Nginx Web Server / Node Vite Build", "Static HTML/JS/CSS bundle (< 2 MB) served over HTTP/2"),
        ("Relational Database", "SQLite 3 WAL / Hosted PostgreSQL 15", "Connection pool capped at 20 pooled connections; ACID compliance"),
        ("ML Models (MNB & SBERT)", "In-Process Memory Cache", "Pre-warmed weights (classifier.pkl 331 KB, all-MiniLM 90 MB)")
    ]
    add_styled_table(doc, dep_headers, dep_rows, col_widths=[1.8, 1.8, 2.42])
    add_p(doc, "Table 105: Deployment Components", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    add_p(doc, "147", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
