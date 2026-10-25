"""
evidence_verifier.py - Strict Evidence Relevance Verification Engine
=====================================================================
Replaces the broken heuristic-based approach in ocr_service.py.

MANDATORY VERIFICATION RULES:
1. A file existing does NOT mean it is verified.
2. Successful OCR does NOT mean the evidence is relevant.
3. A readable but unrelated screenshot MUST NOT pass.
4. Relevant banking content MUST be assessed against the specific complaint.
5. Critical mismatches MUST block automatic approval.
6. Insufficient or ambiguous evidence → NEEDS_REVIEW.
7. Missing evidence → NO_EVIDENCE.
8. Corrupted or unsupported files → INVALID_FILE.

VERDICT STATES:
- VERIFIED       : High-confidence domain match + entity corroboration
- NEEDS_REVIEW   : Domain looks financial but entities incomplete/uncertain
- FAILED         : Confirmed non-financial content or critical entity mismatch
- NO_EVIDENCE    : No file provided
- INVALID_FILE   : Cannot read or unsupported format

The key principle: UNCERTAIN or UNREADABLE never becomes VERIFIED automatically.
"""

import os
import re
from semantic_engine import get_text_embedding, cosine_similarity

# ─── DOMAIN PROFILES ─────────────────────────────────────────────────────────

FINANCIAL_PROFILES = [
    "bank account statement debit credit transaction utr reference npci clearing settlement",
    "payment receipt transfer successful amount debited credited balance statement passbook",
    "upi imps neft rtgs mobile banking net banking transaction id reference number",
    "credit card debit card statement billing charge merchant pos swipe invoice",
    "loan emi repayment noc closure interest principal outstanding mortgage",
    "atm cash withdrawal dispensed receipt slip machine transaction failed",
    "cibil credit score bureau report overdue dpd outstanding settled",
]

NON_FINANCIAL_PROFILES = [
    "lab manual assignment experiment college university semester syllabus course outcome",
    "student practical examination faculty chapter notes project report tutorial lecture",
    "chat message hello hi friend meet tomorrow cafe social media post",
    "game score level coins player health power kill enemy mission achievement",
    "recipe ingredient cooking food meal preparation instructions kitchen steps",
    "news article politics government election vote party leader country",
    "movie film actor director scene plot review rating entertainment streaming",
    "social media instagram twitter facebook like comment share follower post",
    "fitness exercise workout gym muscle calories weight training sport",
    "travel tourism destination hotel resort booking flight itinerary",
]

FINANCIAL_VECTORS = [get_text_embedding(p) for p in FINANCIAL_PROFILES]
NON_FINANCIAL_VECTORS = [get_text_embedding(p) for p in NON_FINANCIAL_PROFILES]

# Category-specific banking keywords that MUST appear for domain confirmation
CATEGORY_REQUIRED_KEYWORDS = {
    "UPI / IMPS / Digital Fund Transfer": {
        "primary": ["upi", "imps", "neft", "rtgs", "transfer", "utr", "rrn", "npci", "transaction"],
        "secondary": ["debit", "credit", "amount", "payment", "sent", "received", "failed", "gpay", "phonepe", "paytm", "bhim"],
        "min_primary": 1, "min_secondary": 1
    },
    "Credit Card / Disputed Charges & Fee": {
        "primary": ["credit card", "card", "statement", "billing", "charge", "chargeback", "dispute"],
        "secondary": ["transaction", "merchant", "pos", "amount", "debit", "fee", "annual", "emi"],
        "min_primary": 1, "min_secondary": 1
    },
    "ATM Cash Withdrawal Failure": {
        "primary": ["atm", "cash", "withdraw", "dispense", "machine", "withdrawal"],
        "secondary": ["slip", "receipt", "debit", "amount", "failed", "balance", "transaction"],
        "min_primary": 1, "min_secondary": 1
    },
    "Net Banking / Mobile App & Tech Glitch": {
        "primary": ["net banking", "netbanking", "mobile banking", "internet banking", "login", "app"],
        "secondary": ["otp", "session", "error", "account", "password", "transaction", "bank"],
        "min_primary": 1, "min_secondary": 1
    },
    "Loan Closure, NOC & Document Dispatch": {
        "primary": ["loan", "emi", "noc", "closure", "repayment", "outstanding", "principal"],
        "secondary": ["interest", "foreclosure", "property", "mortgage", "amount", "paid", "balance"],
        "min_primary": 1, "min_secondary": 1
    },
    "KYC, Account Freezing & Dormancy": {
        "primary": ["account", "kyc", "freeze", "frozen", "dormant", "savings", "current"],
        "secondary": ["pan", "aadhaar", "balance", "statement", "branch", "bank", "identity"],
        "min_primary": 1, "min_secondary": 1
    },
    "Credit Bureau / CIBIL Rectification": {
        "primary": ["cibil", "credit score", "bureau", "experian", "equifax", "credit report", "dpd"],
        "secondary": ["score", "overdue", "settled", "outstanding", "loan", "account", "report"],
        "min_primary": 1, "min_secondary": 1
    },
    "Lost / Stolen Card & Emergency Block": {
        "primary": ["card", "lost", "stolen", "block", "hotlist", "deactivate"],
        "secondary": ["replacement", "fir", "police", "complaint", "bank", "debit", "credit"],
        "min_primary": 1, "min_secondary": 1
    },
    "Staff Behavior & Recovery Harassment": {
        "primary": ["complaint", "harassment", "recovery", "agent", "misconduct", "staff"],
        "secondary": ["threat", "calling", "abuse", "behavior", "bank", "loan"],
        "min_primary": 1, "min_secondary": 1
    },
}

# Filenames containing these strings suggest the document is NOT a banking receipt
SUSPICIOUS_FILENAME_PATTERNS = [
    "screenshot", "screen_shot", "img", "image", "photo", "pic", "picture",
    "snap", "capture", "selfie", "photo", "thumbnail", "wallpaper", "avatar",
    "whatsapp", "instagram", "facebook", "twitter", "chat", "message",
    "game", "gaming", "level", "score", "play",
    "lab", "manual", "assignment", "syllabus", "experiment", "homework",
    "notes", "lecture", "tutorial", "report", "project", "study",
    "recipe", "food", "movie", "film", "news", "blog",
]

# Filenames suggesting LEGITIMATE banking documents
LEGITIMATE_FILENAME_PATTERNS = [
    "receipt", "statement", "passbook", "invoice", "slip", "advice",
    "upi", "paytm", "gpay", "phonepe", "bhim", "npci",
    "noc", "closure", "repayment", "loan", "emi",
    "cibil", "credit_report", "bureau",
    "atm_slip", "transaction",
]


def _extract_text(file_path: str) -> dict:
    """Extract text from file using appropriate method."""
    if not file_path or not os.path.exists(file_path):
        return {"text": "", "page_count": 0, "status": "FILE_NOT_FOUND", "file_ext": ""}

    file_ext = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ""
    text = ""
    page_count = 1

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

    elif file_ext in ["txt", "csv"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read(15000)
        except Exception:
            pass

    elif file_ext in ["jpg", "jpeg", "png", "bmp", "tiff", "webp"]:
        try:
            import pytesseract
            from PIL import Image
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        except Exception:
            pass

    return {
        "text": text.strip(),
        "page_count": page_count,
        "file_ext": file_ext,
        "status": "READABLE" if text.strip() else "UNREADABLE"
    }


def _compute_domain_scores(text_sample: str) -> dict:
    """Compute financial vs non-financial domain similarity scores."""
    if not text_sample or len(text_sample) < 30:
        return {"financial_score": 0.0, "non_financial_score": 0.0, "classification": "INSUFFICIENT_TEXT"}

    vec = get_text_embedding(text_sample[:1500])
    financial_score = max(cosine_similarity(vec, v) for v in FINANCIAL_VECTORS)
    non_financial_score = max(cosine_similarity(vec, v) for v in NON_FINANCIAL_VECTORS)

    # Classification thresholds (calibrated by testing)
    if non_financial_score >= financial_score and non_financial_score >= 0.20:
        classification = "NON_FINANCIAL"
    elif financial_score >= 0.25:
        classification = "FINANCIAL"
    else:
        # Both scores are low — unreadable or truly generic
        classification = "UNCLASSIFIABLE"

    return {
        "financial_score": round(financial_score, 3),
        "non_financial_score": round(non_financial_score, 3),
        "classification": classification,
    }


def _check_category_keywords(text: str, service_type: str) -> dict:
    """Check if text contains enough category-specific keywords."""
    text_lower = text.lower()
    req = CATEGORY_REQUIRED_KEYWORDS.get(service_type)
    if not req:
        # Generic check if no specific category defined
        generic_banking = ["bank", "account", "transaction", "amount", "debit", "credit", "payment"]
        matched = [k for k in generic_banking if k in text_lower]
        return {
            "primary_matched": matched,
            "secondary_matched": [],
            "primary_count": len(matched),
            "secondary_count": 0,
            "sufficient": len(matched) >= 1,
        }

    primary_matched = [k for k in req["primary"] if k in text_lower]
    secondary_matched = [k for k in req["secondary"] if k in text_lower]

    sufficient = (
        len(primary_matched) >= req["min_primary"]
        and len(secondary_matched) >= req["min_secondary"]
    )

    return {
        "primary_matched": primary_matched,
        "secondary_matched": secondary_matched,
        "primary_count": len(primary_matched),
        "secondary_count": len(secondary_matched),
        "sufficient": sufficient,
    }


def _filename_risk_assessment(filename: str) -> dict:
    """
    Assess whether the filename suggests a suspicious (non-banking) or legitimate file.
    Returns: suspicious (bool), legitimate (bool), matched_suspicious_pattern, matched_legitimate_pattern
    """
    fn_lower = filename.lower()

    suspicious_match = next(
        (p for p in SUSPICIOUS_FILENAME_PATTERNS if p in fn_lower), None
    )
    legitimate_match = next(
        (p for p in LEGITIMATE_FILENAME_PATTERNS if p in fn_lower), None
    )

    return {
        "suspicious": suspicious_match is not None and legitimate_match is None,
        "legitimate": legitimate_match is not None,
        "suspicious_pattern": suspicious_match,
        "legitimate_pattern": legitimate_match,
    }


def verify_evidence(
    file_path: str,
    service_type: str,
    submitted_bank: str = None,
    submitted_date: str = None,
    submitted_amount: float = None,
    submitted_ref_id: str = None,
    submitted_branch: str = None,
) -> dict:
    """
    Main evidence verification function. Returns a strict verdict.

    Verdict logic:
    - NO_EVIDENCE      : no file provided
    - INVALID_FILE     : file cannot be found or is unsupported format
    - FAILED           : confirmed non-financial content, or critical entity mismatch
    - NEEDS_REVIEW     : file looks financial but entities incomplete or domain uncertain
    - VERIFIED         : financial domain confirmed + at least 1 category keyword matched

    NOTE: UNREADABLE images alone NEVER become VERIFIED. They become NEEDS_REVIEW
    only if the filename strongly suggests a legitimate banking document.
    """
    reasons = []
    warnings = []

    # ─── STEP 0: File existence ───────────────────────────────────────────────
    if not file_path:
        return {
            "verdict": "NO_EVIDENCE",
            "evidence_status": "NO_EVIDENCE",
            "reasons": ["No document was provided."],
            "warnings": [],
            "domain_scores": {},
            "keyword_check": {},
            "extracted_text_length": 0,
        }

    if not os.path.exists(file_path):
        return {
            "verdict": "INVALID_FILE",
            "evidence_status": "INVALID_FILE",
            "reasons": ["The uploaded file could not be found on the server."],
            "warnings": [],
            "domain_scores": {},
            "keyword_check": {},
            "extracted_text_length": 0,
        }

    filename = os.path.basename(file_path)
    file_ext = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ""

    supported_exts = {"pdf", "txt", "csv", "jpg", "jpeg", "png", "bmp", "tiff", "webp"}
    if file_ext not in supported_exts:
        return {
            "verdict": "INVALID_FILE",
            "evidence_status": "INVALID_FILE",
            "reasons": [
                f"Unsupported file type '.{file_ext}'. "
                f"Accepted formats: PDF, JPG, PNG, TXT, CSV."
            ],
            "warnings": [],
            "domain_scores": {},
            "keyword_check": {},
            "extracted_text_length": 0,
        }

    # ─── STEP 1: Extract text ─────────────────────────────────────────────────
    extraction = _extract_text(file_path)
    extracted_text = extraction["text"]
    page_count = extraction["page_count"]
    text_length = len(extracted_text)

    # ─── STEP 2: Structural checks ────────────────────────────────────────────
    if page_count > 5:
        warnings.append(
            f"Document has {page_count} pages. Legitimate banking receipts are typically 1-2 pages. "
            "Please upload only the relevant page."
        )

    # ─── STEP 3: Filename risk assessment ─────────────────────────────────────
    fn_risk = _filename_risk_assessment(filename)

    # ─── STEP 4: Domain scoring (only if text was extracted) ──────────────────
    domain_scores = {}
    keyword_check = {}
    entity_mismatches = []

    if text_length >= 30:
        # We have readable text — do full analysis
        domain_scores = _compute_domain_scores(extracted_text)
        classification = domain_scores["classification"]

        if classification == "NON_FINANCIAL":
            reasons.append(
                f"Content Domain: This document is classified as NON-FINANCIAL "
                f"(financial_score={domain_scores['financial_score']}, "
                f"non_financial_score={domain_scores['non_financial_score']}). "
                f"It does not contain banking transaction content."
            )
            return {
                "verdict": "FAILED",
                "evidence_status": "FAILED",
                "reasons": reasons,
                "warnings": warnings,
                "domain_scores": domain_scores,
                "keyword_check": {},
                "extracted_text_length": text_length,
            }

        # For FINANCIAL or UNCLASSIFIABLE text, check category-specific keywords
        keyword_check = _check_category_keywords(extracted_text, service_type)

        if classification == "UNCLASSIFIABLE" and not keyword_check["sufficient"]:
            # Text exists but doesn't match financial domain or category keywords
            reasons.append(
                f"Content Mismatch: Text was extracted ({text_length} characters) but does not contain "
                f"banking terminology relevant to '{service_type}'. "
                f"Matched primary keywords: {keyword_check['primary_matched'] or 'none'}."
            )
            return {
                "verdict": "FAILED",
                "evidence_status": "FAILED",
                "reasons": reasons,
                "warnings": warnings,
                "domain_scores": domain_scores,
                "keyword_check": keyword_check,
                "extracted_text_length": text_length,
            }

        # ─── STEP 5: Entity corroboration ─────────────────────────────────────
        text_lower = extracted_text.lower()

        if submitted_bank and submitted_bank.strip():
            bank_tokens = [
                w for w in re.findall(r'\b[a-zA-Z]{3,}\b', submitted_bank.lower())
                if w not in {"bank", "of", "india", "the", "ltd", "limited"}
            ]
            bank_matched = any(tok in text_lower for tok in bank_tokens) if bank_tokens else False
            if not bank_matched:
                entity_mismatches.append(
                    f"Bank Not Found: '{submitted_bank}' is not mentioned in the document."
                )

        if submitted_ref_id and len(submitted_ref_id.strip()) >= 5:
            if submitted_ref_id.strip().lower() not in text_lower:
                entity_mismatches.append(
                    f"Reference ID Not Found: '{submitted_ref_id}' is not present in the document."
                )

        if submitted_amount and submitted_amount > 0:
            int_amt = str(int(submitted_amount))
            fmt_amt = f"{submitted_amount:,.2f}"
            if int_amt not in extracted_text and fmt_amt not in extracted_text:
                entity_mismatches.append(
                    f"Amount Not Found: ₹{submitted_amount:,.2f} does not match any value in the document."
                )

        if submitted_date and submitted_date.strip():
            date_digits = re.sub(r'[^0-9]', '', submitted_date.strip())
            doc_digits = re.sub(r'[^0-9]', '', extracted_text)
            if date_digits and date_digits not in doc_digits:
                entity_mismatches.append(
                    f"Date Not Matched: '{submitted_date}' is not corroborated by the document."
                )

        # Determine verdict with text present
        has_enough_keywords = keyword_check.get("sufficient", False)
        is_financial_domain = classification == "FINANCIAL"

        if entity_mismatches:
            # Entity mismatches present
            # If BOTH domain and keywords confirm banking → NEEDS_REVIEW (flag for officer)
            # If domain unclear OR keywords insufficient → FAILED
            if is_financial_domain and has_enough_keywords:
                warnings.extend(entity_mismatches)
                return {
                    "verdict": "NEEDS_REVIEW",
                    "evidence_status": "NEEDS_REVIEW",
                    "reasons": [
                        "Entity Mismatch: Document appears to be a financial record but transaction "
                        "details (amount, reference ID, bank, or date) do not match complaint fields. "
                        "A bank officer will manually review the evidence."
                    ],
                    "warnings": entity_mismatches,
                    "domain_scores": domain_scores,
                    "keyword_check": keyword_check,
                    "extracted_text_length": text_length,
                }
            else:
                reasons.extend(entity_mismatches)
                return {
                    "verdict": "FAILED",
                    "evidence_status": "FAILED",
                    "reasons": reasons,
                    "warnings": warnings,
                    "domain_scores": domain_scores,
                    "keyword_check": keyword_check,
                    "extracted_text_length": text_length,
                }

        # All entity checks passed (or no entity fields were submitted)
        # Key rule: if NO entity fields were submitted at all (bank, amount, ref, date all None)
        # we cannot fully corroborate the document → NEEDS_REVIEW regardless of domain.
        no_entity_fields_submitted = (
            not submitted_bank
            and not submitted_ref_id
            and not submitted_amount
            and not submitted_date
        )
        if no_entity_fields_submitted:
            return {
                "verdict": "NEEDS_REVIEW",
                "evidence_status": "NEEDS_REVIEW",
                "reasons": [],
                "warnings": [
                    "No transaction details (amount, reference ID, bank, or date) were provided "
                    "to cross-verify against the document. A bank officer will manually review this evidence."
                ],
                "domain_scores": domain_scores,
                "keyword_check": keyword_check,
                "extracted_text_length": text_length,
            }

        # If no entity fields provided AND domain is uncertain → NEEDS_REVIEW
        if not is_financial_domain and not has_enough_keywords:
            return {
                "verdict": "NEEDS_REVIEW",
                "evidence_status": "NEEDS_REVIEW",
                "reasons": ["Document domain is uncertain. A bank officer will manually review this evidence."],
                "warnings": warnings,
                "domain_scores": domain_scores,
                "keyword_check": keyword_check,
                "extracted_text_length": text_length,
            }

        if not has_enough_keywords:
            return {
                "verdict": "NEEDS_REVIEW",
                "evidence_status": "NEEDS_REVIEW",
                "reasons": [
                    f"Incomplete Evidence: Document appears financial but lacks specific keywords for "
                    f"'{service_type}'. An officer will verify manually."
                ],
                "warnings": warnings,
                "domain_scores": domain_scores,
                "keyword_check": keyword_check,
                "extracted_text_length": text_length,
            }

        # Domain is financial + keywords match + no critical entity mismatches → VERIFIED
        return {
            "verdict": "VERIFIED",
            "evidence_status": "VERIFIED",
            "reasons": [],
            "warnings": warnings,
            "domain_scores": domain_scores,
            "keyword_check": keyword_check,
            "extracted_text_length": text_length,
        }

    else:
        # ─── STEP 6: No readable text extracted ───────────────────────────────
        # An unreadable file NEVER automatically passes.
        # It can only go to NEEDS_REVIEW if filename strongly suggests a legit banking doc.
        # Otherwise → FAILED.

        if fn_risk["suspicious"]:
            # Filename matches a suspicious pattern (screenshot, chat, game, etc.)
            reasons.append(
                f"Unrelated File Detected: The filename '{filename}' suggests this is not a banking document "
                f"(matched pattern: '{fn_risk['suspicious_pattern']}'). No financial text could be extracted."
            )
            return {
                "verdict": "FAILED",
                "evidence_status": "FAILED",
                "reasons": reasons,
                "warnings": warnings,
                "domain_scores": {},
                "keyword_check": {},
                "extracted_text_length": 0,
            }

        if fn_risk["legitimate"]:
            # Filename looks like a banking doc but text couldn't be read
            warnings.append(
                f"Unreadable Document: '{filename}' appears to be a banking document "
                f"(matched pattern: '{fn_risk['legitimate_pattern']}') but text could not be extracted. "
                "An officer will manually review this document."
            )
            return {
                "verdict": "NEEDS_REVIEW",
                "evidence_status": "NEEDS_REVIEW",
                "reasons": [],
                "warnings": warnings,
                "domain_scores": {},
                "keyword_check": {},
                "extracted_text_length": 0,
            }

        # Neutral filename, no text → NEEDS_REVIEW (human to decide)
        warnings.append(
            f"No text could be extracted from '{filename}'. "
            "A bank officer will manually review the uploaded document."
        )
        return {
            "verdict": "NEEDS_REVIEW",
            "evidence_status": "NEEDS_REVIEW",
            "reasons": [],
            "warnings": warnings,
            "domain_scores": {},
            "keyword_check": {},
            "extracted_text_length": 0,
        }


def check_evidence_for_submission(
    file_path: str,
    service_type: str,
    submitted_bank: str = None,
    submitted_date: str = None,
    submitted_amount: float = None,
    submitted_ref_id: str = None,
    submitted_branch: str = None,
) -> dict:
    """
    Wrapper for submit_complaint endpoint.
    Returns result + a 'blocks_submission' flag.
    
    FAILED → blocks_submission = True (raise 422)
    NEEDS_REVIEW → blocks_submission = False (accept but flag for officer)
    VERIFIED → blocks_submission = False (accept with confidence)
    NO_EVIDENCE / INVALID_FILE → blocks_submission = True if service_type requires proof
    """
    result = verify_evidence(
        file_path=file_path,
        service_type=service_type,
        submitted_bank=submitted_bank,
        submitted_date=submitted_date,
        submitted_amount=submitted_amount,
        submitted_ref_id=submitted_ref_id,
        submitted_branch=submitted_branch,
    )

    verdict = result["verdict"]
    blocks_submission = verdict in ("FAILED", "INVALID_FILE")

    result["blocks_submission"] = blocks_submission
    result["display_status"] = {
        "VERIFIED":      "VERIFIED",
        "NEEDS_REVIEW":  "PENDING",
        "FAILED":        "REJECTED",
        "NO_EVIDENCE":   "NOT_REQUIRED",
        "INVALID_FILE":  "REJECTED",
    }.get(verdict, "PENDING")

    return result
