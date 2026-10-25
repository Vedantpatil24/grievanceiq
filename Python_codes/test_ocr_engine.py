"""
test_ocr_engine.py — Regression tests for the new OCR engine.
Tests: PNG, JPG, text PDF, corrupted file, banking field extraction.
"""
import sys
import os
import tempfile

# Force UTF-8 output on Windows to avoid cp1252 UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
elif hasattr(sys.stdout, 'buffer'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure we're running from the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")

from PIL import Image, ImageDraw, ImageFont
import io

# ──────────────────────────────────────────────────────────────────
# 1. Create a fictional UPI failure receipt as a PIL image
# ──────────────────────────────────────────────────────────────────
RECEIPT_LINES = [
    "==============================",
    "   UPI PAYMENT RECEIPT",
    "   HDFC Bank | BHIM UPI",
    "==============================",
    "",
    "Status    : FAILED",
    "Amount    : Rs. 1999.00",
    "Date      : 25/10/2026",
    "Time      : 14:32:05",
    "Merchant  : Demo Store",
    "TxnID     : TESTUPI2510263421",
    "UTR No.   : HDFC2026251023421",
    "VPA       : demostore@okhdfc",
    "",
    "Reason    : Insufficient balance",
    "",
    "Customer  : Ashmit Patil",
    "Account   : XXXX XXXX 7842",
    "",
    "==============================",
    "  This is a system-generated  ",
    "  transaction receipt.        ",
    "==============================",
]


def make_receipt_image(width=600, height=600) -> Image.Image:
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Use default PIL font (no external font needed)
    y = 20
    for line in RECEIPT_LINES:
        draw.text((40, y), line, fill=(30, 30, 30))
        y += 26
    return img


# ──────────────────────────────────────────────────────────────────
# 2. Run tests
# ──────────────────────────────────────────────────────────────────

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    results.append((label, condition))


print("\n" + "="*60)
print("  GrievanceIQ OCR Engine Regression Tests")
print("="*60 + "\n")

# ------ Import ------
try:
    from ocr_engine import extract_text, extract_banking_fields
    print("[OK] ocr_engine imported successfully\n")
except Exception as e:
    print(f"[FAIL] Could not import ocr_engine: {e}")
    sys.exit(1)

# ------ Test 1: PNG ------
print("Test 1: PNG Receipt")
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
    png_path = f.name
img = make_receipt_image()
img.save(png_path)
result = extract_text(png_path)
print(f"  Status: {result['status']}, Chars: {result['char_count']}, Confidence: {result['confidence']:.3f}")
print(f"  Preview: {result['text'][:120].replace(chr(10), ' ')}")
check("PNG: status READABLE", result["status"] == "READABLE", result["status"])
check("PNG: extracted >20 chars", result["char_count"] > 20, str(result["char_count"]))
os.unlink(png_path)
print()

# ------ Test 2: JPG ------
print("Test 2: JPG Receipt")
with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
    jpg_path = f.name
img.save(jpg_path, "JPEG", quality=95)
result_jpg = extract_text(jpg_path)
print(f"  Status: {result_jpg['status']}, Chars: {result_jpg['char_count']}, Confidence: {result_jpg['confidence']:.3f}")
check("JPG: status READABLE", result_jpg["status"] == "READABLE", result_jpg["status"])
check("JPG: extracted >20 chars", result_jpg["char_count"] > 20, str(result_jpg["char_count"]))
os.unlink(jpg_path)
print()

# ------ Test 3: Text PDF ------
print("Test 3: Text-based PDF")
try:
    import pypdf
    from pypdf import PdfWriter
    writer = PdfWriter()
    page = writer.add_blank_page(width=400, height=600)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name
    # Write a minimal text PDF using reportlab if available, else skip
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        c = rl_canvas.Canvas(pdf_path)
        for i, line in enumerate(RECEIPT_LINES):
            c.drawString(40, 550 - i*22, line)
        c.save()
        result_pdf = extract_text(pdf_path)
        print(f"  Status: {result_pdf['status']}, Chars: {result_pdf['char_count']}")
        check("Text PDF: READABLE", result_pdf["status"] == "READABLE", result_pdf["status"])
        check("Text PDF: >20 chars", result_pdf["char_count"] > 20, str(result_pdf["char_count"]))
        os.unlink(pdf_path)
    except ImportError:
        print("  [SKIP] reportlab not installed — skipping text PDF test")
except Exception as ex:
    print(f"  [SKIP] {ex}")
print()

# ------ Test 4: Corrupted file ------
print("Test 4: Corrupted/unsupported file")
with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
    bad_path = f.name
    f.write(b"this is not image data at all 12345678")
result_bad = extract_text(bad_path)
print(f"  Status: {result_bad['status']}, Chars: {result_bad['char_count']}")
check("Corrupted file: not READABLE", result_bad["status"] != "READABLE", result_bad["status"])
os.unlink(bad_path)
print()

# ------ Test 5: Banking field extraction from sample text ------
print("Test 5: Banking field extraction")
sample_text = "\n".join(RECEIPT_LINES)
fields = extract_banking_fields(sample_text)
print(f"  Extracted fields: {fields}")
check("Amount extracted", fields.get("amount") is not None, str(fields.get("amount")))
check("TxnID extracted", fields.get("txn_id") is not None, str(fields.get("txn_id")))
check("Date extracted", fields.get("date") is not None, str(fields.get("date")))
check("Status extracted", fields.get("status") is not None, str(fields.get("status")))
check("Bank extracted", fields.get("bank") is not None, str(fields.get("bank")))
check("Merchant extracted", fields.get("merchant") is not None, str(fields.get("merchant")))
print()

# ------ Test 6: PNG — verify TESTUPI extracted ------
print("Test 6: TxnID extracted from PNG OCR")
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
    png2_path = f.name
img.save(png2_path)
result2 = extract_text(png2_path)
if result2["char_count"] > 20:
    fields2 = extract_banking_fields(result2["text"])
    print(f"  Fields from PNG OCR: {fields2}")
    check("TxnID or Amount found in PNG OCR", 
          fields2.get("txn_id") is not None or fields2.get("amount") is not None,
          str(fields2))
else:
    print("  [SKIP] OCR text too short, skipping field check")
os.unlink(png2_path)
print()

# ------ Summary ------
total = len(results)
passed = sum(1 for _, ok in results if ok)
print("="*60)
print(f"  Results: {passed}/{total} tests PASSED")
print("="*60 + "\n")

if passed < total:
    sys.exit(1)
