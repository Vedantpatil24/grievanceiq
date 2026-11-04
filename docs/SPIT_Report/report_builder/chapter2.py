# chapter2.py
# Chapter 2: Literature Review and Study of Existing Systems

import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter2(doc):
    add_h1(doc, "2   Literature Review and Study of Existing Systems")
    
    # 2.1 Study of Existing Systems
    add_h2(doc, "2.1 Study of Existing Systems")
    p_intro = (
        "Grievance redressal in the financial domain comprises multiple interconnected activities: customer dispute intake, "
        "documentary evidence verification, categorical routing, statutory SLA monitoring, officer adjudication, and operational "
        "capacity management. Historically, public sector institutions, commercial banks, and regulatory bodies have developed individual "
        "software platforms to manage specific aspects of this workflow. However, each system exhibits distinct architectural limitations."
    )
    add_p(doc, p_intro, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)
    
    add_h3(doc, "2.1.1 Manual Branch Filing and Call-Center Logging")
    p_manual = (
        "In the conventional approach, an aggrieved customer visits a physical branch office or dials an interactive voice response (IVR) "
        "call center. A bank clerk or telephone operator manually writes down the complaint details, assigns an internal token number, "
        "and routes the physical file to the relevant operations desk. While this process allows human empathy and individualized "
        "listening, it suffers from extreme operational latency, geographic dependency, high transaction costs, and an absence of verifiable "
        "digital audit trails. Misplaced paper dockets and undocumented verbal complaints frequently evade statutory SLA monitoring entirely."
    )
    add_p(doc, p_manual, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    add_h3(doc, "2.1.2 CPGRAMS (Centralized Public Grievance Redress and Monitoring System)")
    p_cpgrams = (
        "Operated by the Department of Administrative Reforms and Public Grievances (DARPG), Government of India, CPGRAMS serves as a "
        "national web-based portal connecting citizens with central government ministries, departments, and public sector banks. While CPGRAMS "
        "centralizes complaint registration, it functions essentially as an electronic post office. It lacks automated NLP triage, meaning "
        "human nodal officers must manually read and transfer tickets. Furthermore, it offers no voice-assisted intake for vernacular citizens, "
        "lacks automated documentary OCR verification, and does not provide predictive queueing intelligence to participating bank departments."
    )
    add_p(doc, p_cpgrams, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    add_h3(doc, "2.1.3 Reserve Bank of India CMS and the Integrated Ombudsman Scheme (RB-IOS 2021)")
    p_rbi = (
        "The RBI launched the Complaint Management System (CMS) to operationalize the Reserve Bank - Integrated Ombudsman Scheme of 2021. "
        "RB-IOS unifies grievance redressal across scheduled commercial banks, NBFCs, and non-bank payment system participants under a single "
        "'One Nation, One Ombudsman' umbrella. However, by statutory mandate, the RBI Ombudsman is an appellate body of last resort: "
        "depositors are permitted to approach the Ombudsman only after 30 calendar days have elapsed without resolution at the bank level, "
        "or if the bank rejects the complaint unfairly. The primary institutional bottleneck resides inside the commercial banks themselves, "
        "which lack automated triage mechanisms to resolve routine disputes before they escalate to the RBI."
    )
    add_p(doc, p_rbi, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    add_h3(doc, "2.1.4 Commercial Enterprise CRM Systems (Salesforce Service Cloud, Freshdesk, Zendesk)")
    p_crm = (
        "Leading commercial scheduled banks frequently deploy proprietary enterprise Customer Relationship Management (CRM) solutions. "
        "While these platforms offer sophisticated omnichannel ticket routing, customizable workflows, and agent assignment rules, they "
        "suffer from severe shortcomings in the Indian context: (a) exorbitant per-seat licensing costs running into millions of dollars annually, "
        "(b) vendor lock-in with closed-source codebases, (c) absence of out-of-the-box DPDP Act 2023 token redaction for Indian financial PII, "
        "and (d) generic customer support workflows that lack specialized BFSI dispute logic, such as RBI 72-hour customer liability directives."
    )
    add_p(doc, p_crm, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    add_h3(doc, "2.1.5 General-Purpose Large Language Model Assistants")
    p_llm = (
        "Recent advances in Generative Artificial Intelligence (LLMs such as GPT-4, Llama-3, and Gemini) enable automated document "
        "summarization and conversational interaction. However, relying solely on generative LLMs for banking grievance adjudication "
        "introduces catastrophic operational risks: LLMs are prone to hallucinating non-existent banking rules, misinterpreting transaction numbers, "
        "generating incorrect refund promises, and incurring heavy cloud API subscription costs and latency penalties (often >2000 ms per query). "
        "Financial systems require deterministic, reproducible, and explainable decision boundaries."
    )
    add_p(doc, p_llm, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=12)

    # 2.2 Review of Research Papers and Technical Resources
    add_h2(doc, "2.2 Review of Research Papers and Technical Resources")
    add_p(doc, "GrievanceIQ synthesizes established methodologies across seven computational disciplines:", space_before=2, space_after=6)

    add_p(doc, "2.2.1 Deterministic and Probabilistic NLP Text Classification: Text categorization literature highlights the proven "
               "efficiency of Term Frequency-Inverse Document Frequency (TF-IDF) feature representations combined with Multinomial Naive Bayes (MNB) "
               "classifiers (Manning et al., 2008). In domain-specific customer service contexts with clean vocabulary sets, MNB achieves high "
               "multi-class accuracy (>80%) with microscopic training and inference times (<5 ms per document), vastly outperforming heavyweight "
               "deep learning models on resource-constrained commodity servers.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)

    add_p(doc, "2.2.2 Sentence Transformers and Semantic Embeddings: Reimers and Gurevych (2019) introduced Sentence-BERT (SBERT), which "
               "employs siamese and triplet network structures to generate semantically meaningful sentence embeddings. Utilizing pre-trained "
               "models like all-MiniLM-L6-v2 allows fast cosine similarity computation across high-dimensional vector spaces, providing an "
               "ideal mechanism for matching incoming customer grievances against historical bank knowledge bases and detecting duplicate tickets.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)

    add_p(doc, "2.2.3 Optical Character Recognition and Entity Verification: Research in document image analysis demonstrates that "
               "combining deep-learning-based text detection (e.g., CRAFT) with character recognition (Tesseract / EasyOCR) reliably parses "
               "scanned financial receipts (Smith, 2007). Implementing deterministic regular-expression token matchers over raw OCR bounding boxes "
               "enables verifiable 4-point cross-validation (Transaction ID, Amount, Bank Name, Account Digits) without model hallucination.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)

    add_p(doc, "2.2.4 Browser-Native Speech Recognition and Vernacular Accessibility: The W3C Web Speech API specification provides "
               "standardized JavaScript interfaces for browser-native speech synthesis and recognition. By offloading acoustic processing to "
               "optimized browser runtimes, client applications achieve continuous zero-latency voice transcription in Indic locales (hi-IN, mr-IN) "
               "without streaming uncompressed raw audio to expensive third-party speech recognition cloud servers.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)

    add_p(doc, "2.2.5 Regulatory Privacy and Statutory Token Redaction: India's Digital Personal Data Protection (DPDP) Act of 2023 mandates "
               "strict data minimization and technical safeguards against the unauthorized storage or processing of Personally Identifiable Information (PII). "
               "Software engineering best practices in financial systems mandate that PII token redaction occur at the earliest API gateway layer "
               "prior to relational persistence or model ingestion (Garfinkel, 2015).",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)

    add_p(doc, "2.2.6 Queueing Theory and Operations Research in Service Systems: Leonard Kleinrock's foundational treatise on Queueing Systems (1975) "
               "formalizes the multi-server M/M/c queueing model. Agner Krarup Erlang's Erlang-C formulation calculates the exact probability "
               "that an arriving job must wait in queue given arrival rate lambda, service rate mu, and c parallel servers. In financial service centers, "
               "Erlang-C enables precise analytical forecasting of queue dwell times and staffing requirements necessary to guarantee statutory SLA adherence.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4)

    add_p(doc, "2.2.7 Automated Software Verification and Quality Assurance: Modern dependable systems engineering emphasizes test-driven "
               "development (TDD), regression test automation, and continuous integration (Beck, 2002). Rigorous evaluation requires isolating "
               "deterministic arithmetic and regex verification from probabilistic machine learning inference.",
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=12)

    # 2.3 Comparative Analysis
    add_h2(doc, "2.3 Comparative Analysis")
    add_p(doc, "Table 4 compares conventional and contemporary grievance handling paradigms against the proposed GrievanceIQ platform.", space_before=2, space_after=6)

    comp_headers = ["Functional Criterion", "Manual Review", "CPGRAMS Portal", "RBI CMS (RB-IOS)", "Commercial CRM", "GrievanceIQ (Proposed)"]
    comp_rows = [
        ("Dispute Intake Channels", "Physical branch, Paper", "Static Web Form", "Online Web Form", "Web, Email, Chat", "Multimodal (Web, Voice, OCR)"),
        ("Vernacular Voice Dictation", "None (Physical only)", "None (English/Hindi text)", "None (Text only)", "Requires costly add-on", "Native Hindi, Marathi & English"),
        ("Autonomous NLP Triage", "Manual human sorting", "Manual nodal routing", "Manual clerk routing", "Rule-based / Paid AI", "TF-IDF + Multinomial Naive Bayes"),
        ("DPDP 2023 PII Masking", "None (Paper exposed)", "None (Plain text stored)", "None (Plain text stored)", "Custom setup required", "Ingestion-level regex redaction (100%)"),
        ("Evidence Verification", "Manual paper check", "Manual officer review", "Manual officer review", "Manual agent inspection", "Automated OCR 4-point cross-validation"),
        ("Tier-1 Autonomous Bot", "None", "None", "None", "Basic keyword bot", "AI GrievanceBot with instant settlement"),
        ("Predictive Queue Modeling", "None", "None", "None", "Limited analytics", "Kleinrock M/M/c Erlang-C simulation"),
        ("What-If Staffing Sandbox", "None", "None", "None", "None / Costly BI tool", "Built-in interactive staffing modeler"),
        ("Dynamic SLA Countdowns", "None (Static calendar)", "Static days elapsed", "Static 30-day clock", "Standard SLA timer", "Real-time urgency radar & countdowns"),
        ("Statutory Receipt & QR", "Carbon paper slip", "Plain text printout", "Basic PDF acknowledgement", "Email confirmation", "ReportLab PDF with dynamic ISO QR"),
        ("Software Licensing Cost", "Labor intensive", "Government funded", "Regulatory funded", "High recurring SaaS fees", "100% Free & Open-Source Software"),
        ("Deployment & Footprint", "Physical branches", "Monolithic data center", "Centralized server", "Proprietary cloud lock-in", "Lightweight, containerized, portable")
    ]
    add_styled_table(doc, comp_headers, comp_rows, col_widths=[1.2, 0.9, 0.9, 0.9, 1.0, 1.12])
    add_p(doc, "Table 4: Comparison of Existing Solutions and GrievanceIQ", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14, italic=True, size=10, color=COLOR_MUTED)

    # 2.4 Limitations of Existing Systems
    add_h2(doc, "2.4 Limitations of Existing Systems")
    add_p(doc, "The comprehensive literature review and comparative analysis reveal four overarching systemic limitations:", space_before=2, space_after=6)
    add_p(doc, "• Static and Unresponsive Intake Modalities: Existing grievance portals force users into dense text-input fields, creating severe accessibility barriers for non-tech-savvy or non-English-speaking citizens.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "• Regulatory Non-Compliance in Data Handling: Nearly all existing banking portals lack automated PII redaction at intake, resulting in persistent plaintext storage of customer credit cards and Aadhaar credentials in violation of the DPDP Act 2023.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "• Unverified Customer Assertions: Traditional systems accept customer claim amounts and transaction IDs on faith until human investigation days later, lacking instant OCR verification against transaction receipts.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "• Reactive Rather Than Predictive Operations: Bank leadership relies on retrospective end-of-month reporting rather than real-time mathematical queue modeling, causing preventable SLA breaches during transaction failure surges.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=8)

    # 2.5 Identified Research or Engineering Gap
    add_h2(doc, "2.5 Identified Research or Engineering Gap")
    p_gap = (
        "The critical engineering gap is the complete absence of an integrated, privacy-hardened software pipeline that "
        "bridges zero-latency vernacular voice intake, autonomous machine learning triage, deterministic documentary OCR validation, "
        "and predictive Erlang-C queueing intelligence into an open-source, full-stack architecture tailored to Indian banking regulations."
    )
    add_p(doc, p_gap, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=10, italic=True)

    # 2.6 Proposed Improvements
    add_h2(doc, "2.6 Proposed Improvements")
    add_p(doc, "GrievanceIQ delivers seven core architectural improvements over conventional systems:", space_before=2, space_after=6)
    add_p(doc, "1. Ingestion-Level DPDP Act 2023 PII Masking: 100% automated redaction of sensitive credentials prior to database insertion.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "2. Continuous Streaming Voice Dictation: Dual-state buffer accumulator eliminating repeating text loops in Hindi and Marathi.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "3. Sub-10ms NLP Classification: Lightweight TF-IDF + Multinomial Naive Bayes model providing instant triage without cloud API latency.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "4. Deterministic 4-Point OCR Validation: High-precision cross-matching of transaction tokens against physical receipts.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "5. Tier-1 Automated Settlement Gate: Deflecting routine grievances through instant AI copilot self-service resolutions.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "6. Closed-Form Erlang-C Queueing Operations: Real-time calculation of dwell times and interactive What-If staffing capacity simulation.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
    add_p(doc, "7. Dynamic ISO/IEC 18004 QR PDF Receipts: Verifiable legal documentation with zero-friction mobile tracking.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=14)

    add_p(doc, "10", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
    doc.add_page_break()
