"""
ocr_engine.py — Unified OCR Engine for GrievanceIQ
====================================================
Replaces pytesseract (requires system binary) with EasyOCR (pure Python).
Supports: JPG, JPEG, PNG, BMP, TIFF, WEBP, PDF (text + scanned).

Key exports:
    extract_text(file_path)           → {"text", "status", "page_count", "confidence"}
    extract_banking_fields(text)      → {"amount", "txn_id", "date", "status", "bank", "merchant"}
"""

import os
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy singleton EasyOCR reader — downloaded once, reused across all calls
# ---------------------------------------------------------------------------
_easyocr_reader = None


def _get_reader():
    """Return a cached EasyOCR Reader (en + hi). Downloads model on first call (~100 MB)."""
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
            logger.info("[OCR] Initializing EasyOCR reader (first run downloads model ~100 MB)…")
            # gpu=False ensures it works on CPU-only machines
            _easyocr_reader = easyocr.Reader(["en", "hi"], gpu=False, verbose=False)
            logger.info("[OCR] EasyOCR reader ready.")
        except Exception as exc:
            logger.error(f"[OCR] Failed to initialize EasyOCR: {exc}")
            raise
    return _easyocr_reader


# ---------------------------------------------------------------------------
# Image preprocessing (OpenCV + Pillow)
# ---------------------------------------------------------------------------

def _preprocess_image_for_ocr(file_path: str):
    """
    Return a preprocessed numpy array ready for EasyOCR.
    Steps: load → RGB → grayscale → CLAHE contrast → mild denoise.
    Falls back to raw Pillow load if OpenCV is unavailable.
    """
    try:
        import cv2
        import numpy as np

        img_bgr = cv2.imread(file_path)
        if img_bgr is None:
            # cv2.imread returns None for some edge cases — try via Pillow
            from PIL import Image
            import numpy as np
            pil_img = Image.open(file_path).convert("RGB")
            img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Adaptive histogram equalisation for low-contrast scans
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Fast denoising
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)

        # Convert back to 3-channel (EasyOCR works on RGB/BGR arrays)
        result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
        return result

    except Exception as exc:
        logger.warning(f"[OCR] Preprocessing failed ({exc}); using raw image.")
        try:
            from PIL import Image
            import numpy as np
            return np.array(Image.open(file_path).convert("RGB"))
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Core extraction functions
# ---------------------------------------------------------------------------

def _extract_from_image(file_path: str) -> dict:
    """Run EasyOCR on an image file. Returns {'text', 'confidence', 'status'}."""
    try:
        reader = _get_reader()
        preprocessed = _preprocess_image_for_ocr(file_path)
        if preprocessed is None:
            return {"text": "", "confidence": 0.0, "status": "PREPROCESS_FAILED"}

        results = reader.readtext(preprocessed, detail=1)
        # results: list of ([bbox], text, confidence)
        lines = []
        confidences = []
        for (_, text, conf) in results:
            text = text.strip()
            if text:
                lines.append(text)
                confidences.append(conf)

        combined = " ".join(lines)
        avg_conf = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
        status = "READABLE" if combined.strip() else "UNREADABLE"

        logger.info(f"[OCR] Image '{os.path.basename(file_path)}': {len(combined)} chars, avg_conf={avg_conf:.3f}")
        return {"text": combined, "confidence": avg_conf, "status": status}

    except Exception as exc:
        logger.error(f"[OCR] Image extraction failed for '{file_path}': {exc}")
        return {"text": "", "confidence": 0.0, "status": "ERROR"}


def _extract_from_pdf(file_path: str) -> dict:
    """
    PDF extraction:
    1. Try pypdf for text-based PDFs.
    2. If text is empty/short, render each page as image and run EasyOCR (scanned PDF).
    """
    text = ""
    page_count = 1

    # --- Attempt 1: pypdf text extraction (fast, works for digital PDFs) ---
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        page_count = len(reader.pages)
        for page in reader.pages[:15]:
            t = page.extract_text()
            if t:
                text += t + "\n"
        text = text.strip()
        if len(text) >= 80:
            logger.info(f"[OCR] PDF '{os.path.basename(file_path)}': text-based, {len(text)} chars extracted.")
            return {"text": text, "confidence": 1.0, "status": "READABLE", "page_count": page_count}
    except Exception as exc:
        logger.warning(f"[OCR] pypdf failed for '{file_path}': {exc}")

    # --- Attempt 2: Render pages as images (scanned PDF) via Pillow/pdf2image ---
    logger.info(f"[OCR] PDF '{os.path.basename(file_path)}': text-based extraction yielded <80 chars. Trying image OCR…")
    try:
        from PIL import Image as PILImage
        import io, struct, zlib

        # Try pdf2image if available
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, dpi=200, first_page=1, last_page=min(page_count, 5))
            ocr_texts = []
            for pil_img in images:
                import tempfile, numpy as np
                import cv2
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    pil_img.save(tmp.name)
                    tmp_path = tmp.name
                result = _extract_from_image(tmp_path)
                os.unlink(tmp_path)
                if result["text"]:
                    ocr_texts.append(result["text"])
            combined = " ".join(ocr_texts)
            if combined.strip():
                return {"text": combined, "confidence": 0.7, "status": "READABLE", "page_count": page_count}
        except ImportError:
            pass  # pdf2image not installed, continue

        # Fallback: return whatever pypdf gave us (possibly empty)
        return {
            "text": text,
            "confidence": 0.0,
            "status": "READABLE" if text else "UNREADABLE",
            "page_count": page_count
        }

    except Exception as exc:
        logger.error(f"[OCR] PDF OCR fallback failed: {exc}")
        return {"text": text, "confidence": 0.0, "status": "UNREADABLE", "page_count": page_count}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_text(file_path: str) -> dict:
    """
    Main entry point. Dispatches to the correct extractor based on file extension.

    Returns:
        {
          "text": str,           # full extracted text
          "status": str,         # READABLE | UNREADABLE | FILE_NOT_FOUND | INVALID_FILE | ERROR
          "page_count": int,
          "confidence": float,   # 0.0–1.0 (OCR avg confidence; 1.0 for text PDFs)
          "file_ext": str,
          "char_count": int
        }
    """
    if not file_path:
        return {"text": "", "status": "FILE_NOT_FOUND", "page_count": 0, "confidence": 0.0, "file_ext": "", "char_count": 0}

    if not os.path.exists(file_path):
        logger.warning(f"[OCR] File not found: {file_path}")
        return {"text": "", "status": "FILE_NOT_FOUND", "page_count": 0, "confidence": 0.0, "file_ext": "", "char_count": 0}

    file_ext = Path(file_path).suffix.lower().lstrip(".")
    page_count = 1
    result = {}

    IMAGE_EXTS = {"jpg", "jpeg", "png", "bmp", "tiff", "tif", "webp"}
    TEXT_EXTS = {"txt", "csv"}

    if file_ext == "pdf":
        result = _extract_from_pdf(file_path)
        page_count = result.get("page_count", 1)

    elif file_ext in IMAGE_EXTS:
        result = _extract_from_image(file_path)

    elif file_ext in TEXT_EXTS:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read(20000)
            result = {"text": text.strip(), "confidence": 1.0, "status": "READABLE" if text.strip() else "UNREADABLE"}
        except Exception as exc:
            logger.error(f"[OCR] Text file read failed: {exc}")
            result = {"text": "", "confidence": 0.0, "status": "ERROR"}

    else:
        logger.warning(f"[OCR] Unsupported file type: .{file_ext}")
        result = {"text": "", "confidence": 0.0, "status": "INVALID_FILE"}

    return {
        "text": result.get("text", ""),
        "status": result.get("status", "UNREADABLE"),
        "page_count": page_count,
        "confidence": result.get("confidence", 0.0),
        "file_ext": file_ext,
        "char_count": len(result.get("text", "")),
    }


# ---------------------------------------------------------------------------
# Banking field extraction
# ---------------------------------------------------------------------------

# Compiled regex patterns
_AMOUNT_RE = re.compile(
    r'(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d{1,2})?)'
    r'|(?:Amount|Amt|Total|Paid|Debit(?:ed)?|Credit(?:ed)?)[:\s₹]+([\d,]+(?:\.\d{1,2})?)',
    re.IGNORECASE
)
_TXN_ID_RE = re.compile(
    r'(?:UTR|UPI(?:\s*Ref(?:erence)?(?:\s*No\.?)?)?|Ref(?:erence)?(?:\s*(?:ID|No\.?))?'
    r'|Transaction\s*(?:ID|No\.?)|TxnID|IMPS\s*Ref|RRN)[:\s#]*([A-Z0-9]{8,24})'
    r'|\b(UPI\d{10,})\b'
    r'|\b([A-Z]{3,6}\d{8,})\b',
    re.IGNORECASE
)
_DATE_RE = re.compile(
    r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})'
    r'|(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{2,4})'
    r'|(\d{4}[\/\-\.]\d{2}[\/\-\.]\d{2})',
    re.IGNORECASE
)
_STATUS_RE = re.compile(
    r'\b(Failed|Success(?:ful)?|Pending|Declined|Rejected|Debited|Credited'
    r'|Reversed|Refunded|Cancelled|Timeout|Bounced)\b',
    re.IGNORECASE
)
_BANK_RE = re.compile(
    r'\b(SBI|State Bank(?: of India)?|HDFC(?:\s+Bank)?|ICICI(?:\s+Bank)?|Axis(?:\s+Bank)?'
    r'|Kotak(?:\s+Mahindra(?:\s+Bank)?)?|Bank of Baroda|BOB|Punjab National Bank|PNB'
    r'|Union Bank(?:\s+of India)?|Canara Bank|IndusInd Bank|Yes Bank|RBL Bank'
    r'|Bank of India|Central Bank|Indian Bank|UCO Bank|Federal Bank|IDBI(?:\s+Bank)?'
    r'|Paytm(?:\s+Payments Bank)?|PayZapp|PhonePe|GPay|Google Pay|Amazon Pay|Airtel'
    r'|NPCI|BHIM)\b',
    re.IGNORECASE
)
_MERCHANT_RE = re.compile(
    r'(?:To|Merchant|Payee|Beneficiary|Paid\s+to|Transfer\s+to)[:\s]+([A-Za-z0-9 &\.\-]{3,60})',
    re.IGNORECASE
)


def extract_banking_fields(text: str) -> dict:
    """
    Extract key banking transaction fields from OCR text.
    Returns a dict with keys: amount, txn_id, date, status, bank, merchant.
    Missing fields are set to None.
    """
    if not text:
        return {"amount": None, "txn_id": None, "date": None, "status": None, "bank": None, "merchant": None}

    fields = {}

    # Amount
    m = _AMOUNT_RE.search(text)
    if m:
        raw = m.group(1) or m.group(2)
        fields["amount"] = raw.replace(",", "") if raw else None
    else:
        fields["amount"] = None

    # Transaction ID
    m = _TXN_ID_RE.search(text)
    if m:
        fields["txn_id"] = (m.group(1) or m.group(2) or m.group(3) or "").strip().upper() or None
    else:
        fields["txn_id"] = None

    # Date
    m = _DATE_RE.search(text)
    if m:
        fields["date"] = (m.group(1) or m.group(2) or m.group(3) or "").strip() or None
    else:
        fields["date"] = None

    # Payment status
    m = _STATUS_RE.search(text)
    fields["status"] = m.group(1).capitalize() if m else None

    # Bank / payment provider
    m = _BANK_RE.search(text)
    fields["bank"] = m.group(0).strip() if m else None

    # Merchant / beneficiary
    m = _MERCHANT_RE.search(text)
    if m:
        merchant = m.group(1).strip()
        fields["merchant"] = merchant if len(merchant) >= 3 else None
    else:
        fields["merchant"] = None

    return fields


# ---------------------------------------------------------------------------
# Legacy compatibility alias (used by ocr_service.py callers)
# ---------------------------------------------------------------------------

def extract_text_from_file(file_path: str) -> str:
    """
    Simple string-returning wrapper for backward compatibility.
    Use extract_text() for the full result dict.
    """
    result = extract_text(file_path)
    return result.get("text", "")
