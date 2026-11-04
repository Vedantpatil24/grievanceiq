# chapter11.py
# Chapter 11: Conclusion, Future Scope and References

import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_builder.style_utils import (
    add_p, add_h1, add_h2, add_h3, add_styled_table, add_figure_box,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED
)

def build_chapter11(doc):
    add_h1(doc, "11  Conclusion and Future Scope")
    
    # 11.1 Conclusion
    add_h2(doc, "11.1 Conclusion")
    p_c1 = (
        "In the contemporary Indian banking ecosystem, the exponential expansion of digital retail payments has outpaced "
        "conventional grievance redressal mechanisms, resulting in severe triage backlogs, accessibility barriers for vernacular citizens, "
        "and critical regulatory vulnerabilities under the Digital Personal Data Protection (DPDP) Act of 2023. This project resolved "
        "these challenges through the successful engineering of GrievanceIQ, an autonomous, full-stack banking grievance management "
        "and predictive operational intelligence platform."
    )
    p_c2 = (
        "GrievanceIQ delivers an integrated, privacy-first software pipeline: browser-native streaming voice dictation in Hindi and Marathi "
        "empowers underserved citizens to articulate disputes verbally without duplicate phrase loops; ingestion-level regular expression "
        "sanitization achieves 100% zero-leakage redaction of sensitive financial identifiers; autonomous machine learning (TF-IDF + MNB) "
        "and Sentence-BERT achieve 83.49% multi-class triage accuracy in sub-10ms inference; automated OCR executes deterministic 4-point "
        "entity cross-validation against physical transaction proofs; Tier-1 AI GrievanceBot deflects routine claims through instant settlement "
        "dialogs; and Kleinrock M/M/c Erlang-C queueing formulations provide branch management with predictive operational foresight "
        "and interactive What-If staffing sandboxes."
    )
    p_c3 = (
        "The software architecture has been thoroughly verified across a master test suite of 48 automated tests, demonstrating "
        "sub-150ms endpoint latencies, strict ACID transaction reliability, and 100% trilingual dictionary parity across 222 localized keys. "
        "By synthesizing mathematical operations research, machine learning, and secure software engineering, GrievanceIQ establishes "
        "a scalable, dependable, and socially transformative model for digital financial justice."
    )
    add_p(doc, p_c1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)
    add_p(doc, p_c2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)
    add_p(doc, p_c3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=12)

    # 11.2 Status of Project Objectives
    add_h2(doc, "11.2 Status of Project Objectives")
    add_p(doc, "Table 117 details the final achievement status across all engineering objectives established in Chapter 1.", space_before=2, space_after=6)

    stat_headers = ["Project Engineering Objective", "Final Status", "Primary Supporting Evidence & Verification Metric"]
    stat_rows = [
        ("1. Ingestion-Level DPDP 2023 Masking", "Achieved", "100% zero-leakage masking across 16-digit cards, Aadhaar, and PAN tokens."),
        ("2. Multilingual Streaming Voice Ingestion", "Achieved", "W3C Web Speech hook with dual-state buffer; 0% phrase loop duplication."),
        ("3. Autonomous NLP Multi-Class Triage", "Achieved", "83.49% accuracy and 0.835 macro F1 across 2,998 test cases in model_metrics.json."),
        ("4. SBERT Semantic Subcategory Matching", "Achieved", "Sentence-BERT embeddings (all-MiniLM-L6-v2) achieving 100% duplicate detection."),
        ("5. Documentary Evidence OCR Validation", "Achieved", "EasyOCR + 4-point entity cross-matching scoring 90% precision on benchmark slips."),
        ("6. Tier-1 AI GrievanceBot Adjudication", "Achieved", "Automated instant refund settlement gate verified in test_e2e_workflows.py."),
        ("7. Dynamic SLA Engine & Urgency Radar", "Achieved", "Statutory RBI turnaround directions (72h/24h/30d) verified with live countdowns."),
        ("8. Workload-Balanced Officer Assigner", "Achieved", "Greedy allocation algorithm balancing active loads and resolution velocity."),
        ("9. Predictive M/M/c Queueing Model", "Achieved", "Kleinrock Erlang-C formulas matching hand-calculated benchmarks in 0.85 ms."),
        ("10. Statutory PDF Receipt with Dynamic QR", "Achieved", "ReportLab PDF compilation embedding live base-URL dynamic ISO/IEC 18004 QR."),
        ("11. Full-Stack Trilingual Dynamic UI", "Achieved", "React Context provider with 100% parity across 222 keys in EN, HI, and MR.")
    ]
    add_styled_table(doc, stat_headers, stat_rows, col_widths=[2.0, 1.0, 3.02])
    add_p(doc, "Table 117: Status of the Project Objectives", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10, color=COLOR_MUTED)

    # 11.3 Major Engineering Contributions
    add_h2(doc, "11.3 Major Engineering Contributions")
    add_p(doc, "• Architectural Decoupling: Strict separation between presentation, API gateway, business logic, and forensic persistence tiers.", space_before=1, space_after=2)
    add_p(doc, "• Privacy-by-Design Enforcement: Ingestion-level case-insensitive regex masking eliminating sensitive financial credentials before database writes.", space_before=1, space_after=2)
    add_p(doc, "• Dual-State Audio Buffer Algorithm: Practical client-side innovation resolving W3C Web Speech API repetitive phrase duplication.", space_before=1, space_after=2)
    add_p(doc, "• Deterministic 4-Point Document Validation: Verifiable OCR entity matching replacing unconstrained generative AI hallucinations.", space_before=1, space_after=2)
    add_p(doc, "• Mathematical Operations Research Integration: Application of Kleinrock's M/M/c Erlang-C queueing theory to banking capacity management.", space_before=1, space_after=2)
    add_p(doc, "• Dynamic Host-Aware Barcoding: Dynamic request header extraction ensuring mobile-verifiable ISO/IEC 18004 QR codes across any network host.", space_before=1, space_after=8)

    # 11.4 Current Limitations
    add_h2(doc, "11.4 Current Limitations")
    add_p(doc, "• Synthetic Core Banking Interfaces: CBS debit reversal and ledger writebacks are mocked via RESTful APIs due to live banking network security boundaries.", space_before=1, space_after=2)
    add_p(doc, "• Printed Document OCR Dependency: OCR engine is optimized for printed transaction receipts; handwritten dispute dockets are outside current scope.", space_before=1, space_after=2)
    add_p(doc, "• Single-Node Persistence: Demonstration database operates on a single SQLite/PostgreSQL instance rather than a multi-region distributed cluster.", space_before=1, space_after=8)

    # 11.5 Future Enhancements
    add_h2(doc, "11.5 Future Enhancements")
    add_p(doc, "• Direct Core Banking Integration: Implement certified Finacle and BaNCS ISO 20022 message adapters for real-time ledger debit reversals.", space_before=1, space_after=2)
    add_p(doc, "• Account Aggregator (AA) Integration: Connect with RBI-regulated Account Aggregators to fetch authenticated bank statements automatically.", space_before=1, space_after=2)
    add_p(doc, "• On-Device Whisper Voice Models: Compile quantized Whisper.tflite models to enable offline voice dictation in rural banking kiosks.", space_before=1, space_after=2)
    add_p(doc, "• Multi-Lingual Expansion: Extend dynamic UI localization to 10 additional scheduled Indian languages (Bengali, Tamil, Telugu, Gujarati, etc.).", space_before=1, space_after=2)
    add_p(doc, "• Distributed Kafka Message Bus: Deploy Apache Kafka event streams for high-throughput multi-bank inter-branch message synchronization.", space_before=1, space_after=8)

    # 11.6 Lessons Learned
    add_h2(doc, "11.6 Lessons Learned")
    add_p(doc, "• Early Privacy Gating Prevents Downstream Catastrophe: Redacting PII at API ingestion simplifies compliance and guarantees that downstream logs and models never store illegal tokens.", space_before=1, space_after=2)
    add_p(doc, "• Deterministic Math Beats Generative Fluency: In financial operations, deterministic formulas (Erlang-C, SLA rules, 4-point OCR match) provide the explainability and legal defensibility that LLMs cannot guarantee.", space_before=1, space_after=2)
    add_p(doc, "• Buffer Isolation is Essential for Streaming Audio: Handling browser event streams requires strict separation between provisional hypotheses and committed history.", space_before=1, space_after=14)

    # 11.7 Plagiarism Check Report
    add_h2(doc, "11.7 Plagiarism Check Report (Turnitin)")
    add_p(doc, "The complete project report was submitted to Turnitin for academic integrity verification. "
          "The system returned an Overall Similarity Index of 9%, which is well within the acceptable threshold "
          "prescribed by the University of Mumbai and Sardar Patel Institute of Technology guidelines. "
          "The breakdown of match sources is presented below:", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)

    import os
    turnitin_img = os.path.join("G:/Mini_project/docs/SPIT_Report/figures", "fig_turnitin_plagiarism_report.png")
    add_figure_box(doc, "41", "Turnitin Plagiarism Report: 9% Overall Similarity Index (Submission ID: trn:oid::3618:157175442)", turnitin_img)

    add_p(doc, "As evidenced by the Turnitin Integrity Overview, the report demonstrates original academic work with "
          "minimal textual overlap. The 9% similarity is attributable to standard technical terminology, IEEE citation "
          "formats, and commonly used regulatory references (RBI circulars, DPDP Act 2023 statutory language) that are "
          "inherent to the banking technology domain.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=14)

    # References
    add_h1(doc, "References")
    refs = [
        "[1] Reserve Bank of India, \"Reserve Bank - Integrated Ombudsman Scheme, 2021 (RB-IOS),\" RBI Master Circulars, Mumbai, India, Nov. 2021.",
        "[2] Ministry of Law and Justice, Government of India, \"The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023),\" The Gazette of India, Aug. 2023.",
        "[3] Reserve Bank of India, \"Customer Protection – Limiting Liability of Customers in Unauthorised Electronic Banking Transactions,\" RBI/2017-18/15, DBR.No.Leg.BC.78/09.07.005/2017-18, Jul. 2017.",
        "[4] L. Kleinrock, \"Queueing Systems, Volume 1: Theory,\" New York: John Wiley & Sons, 1975.",
        "[5] A. K. Erlang, \"The Theory of Probabilities and Telephone Conversations,\" Nyt Tidsskrift for Matematik B, vol. 20, pp. 33–39, 1909.",
        "[6] C. D. Manning, P. Raghavan, and H. Schütze, \"Introduction to Information Retrieval,\" Cambridge University Press, 2008.",
        "[7] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
        "[8] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,\" in Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP), Hong Kong, pp. 3982–3992, Nov. 2019.",
        "[9] R. Smith, \"An Overview of the Tesseract OCR Engine,\" in Proceedings of the Ninth International Conference on Document Analysis and Recognition (ICDAR), Curitiba, Brazil, pp. 629–633, 2007.",
        "[10] S. Tiwary, \"FastAPI: Modern, High-Performance Web Framework for Python,\" O'Reilly Media, 2023.",
        "[11] World Wide Web Consortium (W3C), \"Web Speech API Specification,\" W3C Community Group Report, Oct. 2012. [Online]. Available: https://wicg.github.io/speech-api/",
        "[12] S. Garfinkel, \"De-Identification of Personally Identifiable Information,\" National Institute of Standards and Technology (NIST) Special Publication 800-122, 2015.",
        "[13] R. Fielding, \"Architectural Styles and the Design of Network-based Software Architectures,\" Ph.D. dissertation, Department of Information and Computer Science, University of California, Irvine, 2000.",
        "[14] M. Fowler, \"Patterns of Enterprise Application Architecture,\" Boston: Addison-Wesley, 2002.",
        "[15] K. Beck, \"Test-Driven Development: By Example,\" Boston: Addison-Wesley, 2002.",
        "[16] R. C. Martin, \"Clean Architecture: A Craftsman's Guide to Software Structure and Design,\" Prentice Hall, 2017.",
        "[17] ISO/IEC, \"Information technology — Automatic identification and data capture techniques — QR Code bar code symbology specification,\" ISO/IEC 18004:2015, Feb. 2015.",
        "[18] National Payments Corporation of India (NPCI), \"Unified Payments Interface (UPI) System Specifications and Dispute Management Framework,\" NPCI Circulars, 2022.",
        "[19] D. Kalbande and R. Sawant, \"Predictive Analytics in Distributed Software Systems,\" Journal of Engineering Education Transformations, vol. 35, no. 1, 2021.",
        "[20] A. Vaswani et al., \"Attention Is All You Need,\" in Advances in Neural Information Processing Systems (NeurIPS 2017), Long Beach, CA, pp. 5998–6008, Dec. 2017.",
        "[21] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, \"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,\" in Proceedings of NAACL-HLT 2019, Minneapolis, MN, pp. 4171–4186, 2019.",
        "[22] S. Russell and P. Norvig, \"Artificial Intelligence: A Modern Approach,\" 4th ed., Pearson, 2020.",
        "[23] E. F. Codd, \"A Relational Model of Data for Large Shared Data Banks,\" Communications of the ACM, vol. 13, no. 6, pp. 377–387, Jun. 1970.",
        "[24] A. Silberschatz, P. B. Galvin, and G. Gagne, \"Operating System Concepts,\" 10th ed., Wiley, 2018.",
        "[25] A. S. Tanenbaum and D. J. Wetherall, \"Computer Networks,\" 5th ed., Pearson, 2011.",
        "[26] ReportLab Inc., \"ReportLab PDF Generation User Guide,\" Version 4.2, 2024. [Online]. Available: https://www.reportlab.com/docs/reportlab-userguide.pdf"
    ]
    for r in refs:
        add_p(doc, r, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4, size=10)

    add_p(doc, "171", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=0, italic=True, size=10, color=COLOR_MUTED)
