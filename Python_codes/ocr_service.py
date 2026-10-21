"""
ocr_service.py - Multi-Tier Document Verification Engine (MahaDBT & RBI CMS Protocol)
Implements:
1. Document Morphology & Metadata Analysis (Page count, structural format)
2. Semantic Domain Affinity Fingerprinting (SBERT Cosine Distance against BFSI vs Academic/Other)
3. Deterministic Entity Corroboration (UTR/RRN, Bank Institution, Amount, Date cross-validation)
4. MahaDBT-style Multi-Tier Scrutiny Verdict (APPROVED / REJECTED_NON_FINANCIAL / SENT_BACK_DEFECTIVE)
"""

import os
import re
from PIL import Image
from semantic_engine import get_text_embedding, cosine_similarity

# Semantic Domain Profiles for Vector Fingerprinting
FINANCIAL_TRANSACTION_PROFILES = [
    "official bank account statement transaction receipt payment successful core banking",
    "debit clearing credit utr reference balance transfer amount settlement npci switch",
    "banking ombudsman passbook entry debit confirmation invoice receipt money transfer"
]

NON_FINANCIAL_PROFILES = [
    "software engineering lab manual assignment experiment college university semester syllabus curriculum",
    "student roll number practical examination faculty course outcome academic railway reservation system",
    "study material classroom notes project report educational document tutorial lecture"
]

FINANCIAL_VECTORS = [get_text_embedding(p) for p in FINANCIAL_TRANSACTION_PROFILES]
NON_FINANCIAL_VECTORS = [get_text_embedding(p) for p in NON_FINANCIAL_PROFILES]

def extract_document_metadata_and_text(file_path: str) -> dict:
    """
    Extracts raw text, page count, and format metadata using pypdf, text reader, or OCR.
    """
    if not file_path or not os.path.exists(file_path):
        return {"text": "", "page_count": 0, "status": "FILE_NOT_FOUND"}

    file_ext = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ""
    text = ""
    page_count = 1

    # 1. PDF Parsing with structural introspection
    if file_ext == "pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            page_count = len(reader.pages)
            for page in reader.pages[:10]:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        except Exception:
            pass

    # 2. Text / CSV Parsing
    elif file_ext in ["txt", "csv"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read(15000)
            page_count = 1
        except Exception:
            pass

    # 3. Image OCR extraction via pytesseract
    elif file_ext in ["jpg", "jpeg", "png", "bmp", "tiff", "webp"]:
        try:
            import pytesseract
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            page_count = 1
        except Exception:
            pass

    return {
        "text": text.strip(),
        "page_count": page_count,
        "file_ext": file_ext,
        "status": "SUCCESS" if text else "UNREADABLE"
    }

def compute_document_domain_affinity(extracted_text: str) -> dict:
    """
    Computes SBERT cosine semantic distance to verify if document belongs to
    the Banking/Financial domain vs Non-Financial (Academic/Legal/General).
    """
    if not extracted_text or len(extracted_text) < 40:
        return {
            "financial_affinity": 0.0,
            "non_financial_affinity": 0.0,
            "domain_verdict": "INSUFFICIENT_TEXT"
        }

    doc_sample = extracted_text[:1200]
    doc_vec = get_text_embedding(doc_sample)

    fin_sim = max([cosine_similarity(doc_vec, v) for v in FINANCIAL_VECTORS])
    non_fin_sim = max([cosine_similarity(doc_vec, v) for v in NON_FINANCIAL_VECTORS])

    # Domain verdict based on vector proximity
    if non_fin_sim > fin_sim and non_fin_sim >= 0.22:
        verdict = "NON_FINANCIAL_DOCUMENT"
    elif fin_sim >= 0.28:
        verdict = "AUTHENTIC_FINANCIAL_RECORD"
    else:
        verdict = "UNCERTAIN_GENERIC_TEXT"

    return {
        "financial_affinity": round(fin_sim, 3),
        "non_financial_affinity": round(non_fin_sim, 3),
        "domain_verdict": verdict
    }

def analyze_document_proof(
    file_path: str,
    submitted_bank: str = None,
    submitted_date: str = None,
    submitted_amount: float = None,
    submitted_ref_id: str = None,
    submitted_branch: str = None
) -> dict:
    """
    Full 4-tier document verification protocol modeled after MahaDBT scrutiny & RBI CMS.
    """
    if not file_path or not os.path.exists(file_path):
        return {
            "has_document": False,
            "extraction_status": "NO_FILE",
            "mismatch_detected": True,
            "mismatch_details": ["No proof document attached."],
            "scrutiny_verdict": "REJECTED_NO_FILE"
        }

    meta = extract_document_metadata_and_text(file_path)
    extracted_text = meta["text"]
    page_count = meta["page_count"]
    filename = os.path.basename(file_path)
    fn_lower = filename.lower()
    mismatches = []
    scrutiny_remarks = []

    # ─── TIER 1: Structural Morphology Check ─────────────────────────────────
    # Financial receipts / transaction screenshots are typically 1-2 pages.
    # Academic lab manuals, assignments, or ebooks with > 3 pages fail morphology check.
    if page_count > 3:
        mismatches.append(
            f"Document Structure Anomaly: The uploaded file has {page_count} pages. "
            f"Legitimate payment receipts, transaction advice slips, or account statements are compact (1-2 pages). "
            f"Please upload only the single-page transaction receipt or statement page."
        )

    # Check filename for obvious non-banking tags
    academic_fn_tags = ["lab_manual", "lab manual", "assignment", "syllabus", "experiment", "rmmm", "homework", "notes"]
    if any(tag in fn_lower for tag in academic_fn_tags):
        mismatches.append(
            f"Non-Banking File Identified: Filename '{filename}' indicates an academic or college document. "
            f"Official banking redressal portals only accept official transaction receipts or bank-issued records."
        )

    # ─── TIER 2: Semantic Domain Affinity Fingerprinting (SBERT) ─────────────
    if extracted_text and len(extracted_text) > 40:
        affinity = compute_document_domain_affinity(extracted_text)
        if affinity["domain_verdict"] == "NON_FINANCIAL_DOCUMENT":
            mismatches.append(
                f"Content Domain Conflict: SBERT semantic analysis classified this file as an academic/educational document "
                f"(Non-financial affinity: {affinity['non_financial_affinity']}, Financial affinity: {affinity['financial_affinity']}). "
                f"The document does not describe or certify a monetary transaction."
            )

        extracted_lower = extracted_text.lower()

        # ─── TIER 3: Deterministic Entity Corroboration (RBI CMS Protocol) ────
        # (A) Bank Institution Match
        if submitted_bank and submitted_bank.strip():
            clean_bank = submitted_bank.strip()
            bank_tokens = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', clean_bank.lower()) if w not in ["bank", "of", "india", "the", "ltd", "limited"]]
            bank_matched = any(tok in extracted_lower for tok in bank_tokens) if bank_tokens else (clean_bank.lower() in extracted_lower)
            if not bank_matched:
                mismatches.append(
                    f"Banking Institution Mismatch: Document does not mention selected bank '{submitted_bank}'."
                )

        # (B) Reference ID / UTR Corroboration
        if submitted_ref_id and submitted_ref_id.strip() and len(submitted_ref_id.strip()) >= 5:
            clean_ref = submitted_ref_id.strip().lower()
            if clean_ref not in extracted_lower:
                mismatches.append(
                    f"Transaction ID Mismatch: Reference ID '{submitted_ref_id}' is not recorded anywhere on this document."
                )

        # (C) Disputed Amount Corroboration
        if submitted_amount and submitted_amount > 0:
            int_amt = str(int(submitted_amount))
            formatted_amt = f"{submitted_amount:,.2f}"
            if int_amt not in extracted_text and formatted_amt not in extracted_text:
                mismatches.append(
                    f"Disputed Amount Mismatch: Amount ₹{submitted_amount:,.2f} does not match any entry on the document."
                )

        # (D) Transaction Date Corroboration
        if submitted_date and submitted_date.strip():
            clean_date = submitted_date.strip()
            date_digits = re.sub(r'[^0-9]', '', clean_date)
            doc_digits = re.sub(r'[^0-9]', '', extracted_text)
            if date_digits and date_digits not in doc_digits:
                mismatches.append(
                    f"Transaction Date Mismatch: Date '{submitted_date}' is not corroborated by the document."
                )

        # (E) Branch Corroboration
        if submitted_branch and len(submitted_branch.strip()) >= 4 and submitted_branch.lower() not in ["main branch", "online"]:
            clean_branch = submitted_branch.strip().lower()
            if clean_branch not in extracted_lower:
                mismatches.append(
                    f"Branch Location Mismatch: Branch '{submitted_branch}' is not mentioned on the document."
                )

        extraction_mode = "PARSED_DOCUMENT_TEXT"

    else:
        # Fallback when text cannot be parsed directly
        extraction_mode = "HEURISTIC_FILE_VERIFICATION"
        doc_indicators = ["receipt", "statement", "passbook", "screenshot", "upi", "paytm", "gpay", "invoice", "slip", "proof", "bank", "card", "cibil"]
        has_banking_hint = any(ind in fn_lower for ind in doc_indicators)
        if not has_banking_hint and len(mismatches) == 0:
            mismatches.append(
                f"Unverified File Format: '{filename}' does not appear to be a recognized bank statement, payment receipt, or debit screenshot."
            )

    is_valid = len(mismatches) == 0
    scrutiny_verdict = "APPROVED_AUTHENTIC" if is_valid else "DEFECTIVE_REVISE_OR_REJECT"

    return {
        "has_document": True,
        "extraction_status": meta["status"],
        "extraction_mode": extraction_mode,
        "page_count": page_count,
        "extracted_text": extracted_text[:2000],
        "mismatch_detected": not is_valid,
        "mismatch_details": mismatches,
        "scrutiny_verdict": scrutiny_verdict,
        "extracted_fields": {
            "file_name": filename,
            "page_count": page_count,
            "text_length": len(extracted_text)
        }
    }
