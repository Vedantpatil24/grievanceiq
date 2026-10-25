"""
test_evidence_verification.py
Regression tests for the strict evidence verification engine.

Tests:
  A. Random unrelated screenshot (no text, suspicious filename)   -> FAILED
  B. Unrelated screenshot WITH readable text (WhatsApp chat)      -> FAILED
  C. Banking doc with mismatched amount/ref                       -> NEEDS_REVIEW
  D. Relevant evidence with incomplete details                    -> NEEDS_REVIEW
  E. Relevant evidence with sufficient matching details           -> VERIFIED
  F. No evidence                                                  -> NO_EVIDENCE
  G. Replaced evidence -> old result not reused (new file gives new verdict)
  H. Gaming screenshot with banking words in it                   -> FAILED
  I. /api/validate-document endpoint - gaming screenshot          -> valid=False
  J. /api/validate-document endpoint - correct banking doc        -> valid=True
"""

import os
import sys
import io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from evidence_verifier import verify_evidence, check_evidence_for_submission

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

results = []

def check(test_name, verdict, expected_verdict, extra=""):
    ok = verdict == expected_verdict
    status = PASS if ok else FAIL
    print(f"  [{status}] {test_name}")
    print(f"         verdict={verdict!r}  expected={expected_verdict!r}  {extra}")
    results.append((test_name, ok))
    return ok


def make_image(filename, text_lines, bg=(10,10,50), text_color=(255,255,255)):
    img = Image.new('RGB', (400, 300), color=bg)
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(text_lines):
        draw.text((10, 10 + i * 30), line, fill=text_color)
    img.save(filename)
    return filename


def make_text_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename


print("=" * 70)
print("  EVIDENCE VERIFICATION REGRESSION TESTS")
print("=" * 70)

# ─── TEST A: Random unrelated image - no text, suspicious filename ────────
print("\n--- A. Random unrelated screenshot (no text, suspicious filename)")
make_image("_test_gaming_screenshot.png", [
    "GAME OVER", "Score: 45500", "Level 12 Complete", "Coins: 340"
])
r = verify_evidence(
    "_test_gaming_screenshot.png",
    service_type="UPI / IMPS / Digital Fund Transfer",
    submitted_bank="HDFC Bank", submitted_amount=45500
)
check("A. Gaming screenshot -> FAILED", r["verdict"], "FAILED",
      f"text_len={r['extracted_text_length']}")

# ─── TEST B: WhatsApp chat screenshot ────────────────────────────────────
print("\n--- B. WhatsApp chat screenshot (readable text, non-banking)")
make_image("_test_whatsapp_chat.png", [
    "WhatsApp Chat", "Hey! How are you?",
    "Good! Lets meet tomorrow at 5pm", "Sure! Cafe?"
], bg=(255,255,255), text_color=(0,0,0))
r = verify_evidence(
    "_test_whatsapp_chat.png",
    service_type="UPI / IMPS / Digital Fund Transfer",
    submitted_bank="HDFC Bank", submitted_amount=45500
)
check("B. WhatsApp chat -> FAILED", r["verdict"], "FAILED",
      f"text_len={r['extracted_text_length']}")

# ─── TEST C: Real banking doc, mismatched amount and ref ID ──────────────
print("\n--- C. Banking doc with wrong amount/ref (entity mismatch)")
make_text_file("_test_banking_wrong_amount.txt", """HDFC Bank
UPI Transaction Receipt
Transaction ID: UPI999888777
Date: 05-10-2026
Amount: Rs. 500
Status: DEBITED
From: Customer Account 1234
NPCI Reference: 9988776655
""")
r = verify_evidence(
    "_test_banking_wrong_amount.txt",
    service_type="UPI / IMPS / Digital Fund Transfer",
    submitted_bank="HDFC Bank",
    submitted_amount=45500,
    submitted_ref_id="UPI123456789012"
)
check("C. Banking doc - amount/ref mismatch -> NEEDS_REVIEW", r["verdict"], "NEEDS_REVIEW",
      f"warnings={r['warnings'][:1]}")

# ─── TEST D: Relevant banking doc but entities not fully submitted ────────
print("\n--- D. Banking doc (financial keywords present, no entity fields submitted)")
make_text_file("_test_banking_incomplete.txt", """Bank Statement
Payment Advice - NPCI Switching
UPI Transfer Transaction
Debit Amount: credited beneficiary account
Transaction Status: Pending
""")
r = verify_evidence(
    "_test_banking_incomplete.txt",
    service_type="UPI / IMPS / Digital Fund Transfer"
    # No bank, amount, or ref_id submitted
)
check("D. Banking doc - no entity fields -> NEEDS_REVIEW", r["verdict"], "NEEDS_REVIEW",
      f"domain={r.get('domain_scores',{}).get('classification','?')}")

# ─── TEST E: Full matching UPI receipt ────────────────────────────────────
print("\n--- E. Correct UPI receipt with all fields matching")
make_text_file("_test_upi_correct.txt", """HDFC Bank Payment Confirmation
UPI Transaction ID: UPI123456789012
Transaction Date: 15-10-2026
Amount Debited: Rs. 45500
Status: Beneficiary Not Credited - NPCI Dispute Raised
From Account: 1234
UTR Reference: 1234567890
NPCI Switch Reference: NPCI2026XYZ
""")
r = verify_evidence(
    "_test_upi_correct.txt",
    service_type="UPI / IMPS / Digital Fund Transfer",
    submitted_bank="HDFC Bank",
    submitted_amount=45500,
    submitted_ref_id="UPI123456789012"
)
check("E. Correct UPI receipt -> VERIFIED", r["verdict"], "VERIFIED",
      f"primary={r.get('keyword_check',{}).get('primary_matched',[])} domain={r.get('domain_scores',{}).get('classification','?')}")

# ─── TEST F: No evidence ──────────────────────────────────────────────────
print("\n--- F. No evidence file provided")
r = verify_evidence(
    None,
    service_type="UPI / IMPS / Digital Fund Transfer"
)
check("F. No file -> NO_EVIDENCE", r["verdict"], "NO_EVIDENCE")

# ─── TEST G: Replace evidence — new file gets fresh verdict ───────────────
print("\n--- G. Old result not reused when evidence replaced")
make_text_file("_test_old_gaming_receipt.txt", "Game score 12000 coins level 45 player epic win")
r_old = verify_evidence(
    "_test_old_gaming_receipt.txt",
    service_type="UPI / IMPS / Digital Fund Transfer",
    submitted_bank="HDFC Bank"
)
make_text_file("_test_new_upi_receipt.txt", """HDFC Bank
UPI Transfer NPCI Reference
Transaction: UPI123456789012
Debit Amount: 45500
Payment IMPS Status: Debited
""")
r_new = verify_evidence(
    "_test_new_upi_receipt.txt",
    service_type="UPI / IMPS / Digital Fund Transfer",
    submitted_bank="HDFC Bank",
    submitted_amount=45500,
    submitted_ref_id="UPI123456789012"
)
verdicts_differ = r_old["verdict"] != r_new["verdict"]
ok = verdicts_differ and r_new["verdict"] == "VERIFIED"
status = PASS if ok else FAIL
print(f"  [{status}] G. Replaced evidence: old={r_old['verdict']} new={r_new['verdict']}")
results.append(("G. Replaced evidence -> different verdicts", ok))

# ─── TEST H: Gaming screenshot containing banking keywords ────────────────
print("\n--- H. Gaming screenshot WITH 'HDFC', 'UPI', amount in text (suspicious filename)")
make_image("_test_game_with_bank_words.png", [
    "GAME OVER - HDFC Challenge", "Score: 45500 UPI Coins",
    "Transaction Defeated!", "NPCI Level Complete"
])
r = verify_evidence(
    "_test_game_with_bank_words.png",
    service_type="UPI / IMPS / Digital Fund Transfer",
    submitted_bank="HDFC Bank", submitted_amount=45500
)
check("H. Game with banking words -> FAILED (suspicious filename)", r["verdict"], "FAILED",
      f"text_len={r['extracted_text_length']}")

# ─── TEST I + J: API endpoint tests ──────────────────────────────────────
print("\n--- I+J. /api/validate-document endpoint tests via TestClient")
try:
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)

    # TEST I: Gaming screenshot via API
    with open("_test_gaming_screenshot.png", "rb") as f:
        img_bytes = f.read()
    fd = {"proof_file": ("_test_gaming_screenshot.png", io.BytesIO(img_bytes), "image/png")}
    data = {
        "service_type": "UPI / IMPS / Digital Fund Transfer",
        "submitted_bank": "HDFC Bank",
        "submitted_amount": "45500",
        "submitted_ref_id": "UPI123456789012"
    }
    res = client.post("/api/validate-document", data=data, files=fd)
    api_result = res.json()
    verdict_i = api_result.get("verdict", "UNKNOWN")
    valid_i = api_result.get("valid", True)
    ok_i = not valid_i and verdict_i == "FAILED"
    status_i = PASS if ok_i else FAIL
    print(f"  [{status_i}] I. API: gaming screenshot -> valid={valid_i} verdict={verdict_i!r}")
    if not ok_i:
        print(f"         PROBLEM: API returned valid={valid_i} verdict={verdict_i!r}")
        print(f"         Full response: {api_result}")
    results.append(("I. API gaming screenshot -> valid=False, verdict=FAILED", ok_i))

    # TEST J: Correct UPI receipt via API
    with open("_test_upi_correct.txt", "rb") as f:
        txt_bytes = f.read()
    fd2 = {"proof_file": ("_test_upi_correct.txt", io.BytesIO(txt_bytes), "text/plain")}
    data2 = {
        "service_type": "UPI / IMPS / Digital Fund Transfer",
        "submitted_bank": "HDFC Bank",
        "submitted_amount": "45500",
        "submitted_ref_id": "UPI123456789012"
    }
    res2 = client.post("/api/validate-document", data=data2, files=fd2)
    api_result2 = res2.json()
    verdict_j = api_result2.get("verdict", "UNKNOWN")
    valid_j = api_result2.get("valid", False)
    ok_j = valid_j and verdict_j == "VERIFIED"
    status_j = PASS if ok_j else FAIL
    print(f"  [{status_j}] J. API: correct UPI receipt -> valid={valid_j} verdict={verdict_j!r}")
    results.append(("J. API correct UPI receipt -> valid=True, verdict=VERIFIED", ok_j))

except Exception as ex:
    print(f"  [SKIP] API tests skipped: {ex}")
    results.append(("I. API gaming screenshot", False))
    results.append(("J. API correct UPI receipt", False))

# ─── CLEANUP ──────────────────────────────────────────────────────────────
for f in [
    "_test_gaming_screenshot.png", "_test_whatsapp_chat.png",
    "_test_banking_wrong_amount.txt", "_test_banking_incomplete.txt",
    "_test_upi_correct.txt", "_test_old_gaming_receipt.txt",
    "_test_new_upi_receipt.txt", "_test_game_with_bank_words.png"
]:
    try:
        os.remove(f)
    except Exception:
        pass

# ─── SUMMARY ──────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"  TOTAL: {passed} passed / {total} tests")
if passed == total:
    print("  ALL TESTS PASSED")
else:
    print(f"  {total - passed} FAILED:")
    for name, ok in results:
        if not ok:
            print(f"    - {name}")
print("=" * 70)
sys.exit(0 if passed == total else 1)
