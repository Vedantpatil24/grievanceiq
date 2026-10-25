"""
test_entity_matching.py  — Regression tests for improved entity corroboration.
Uses synthetic data only. Temp files are created and deleted during the test.
"""
import sys, os, tempfile
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Stub semantic_engine ───────────────────────────────────────────────────
# Return financial_score > non_financial for financial-keyword-rich text,
# non_financial_score > financial for academic/unrelated text.
import types
FINANCIAL_KEYWORDS = {'upi','imps','bank','payment','transaction','receipt','debit','credit',
                      'amount','transfer','utr','npci','hdfc','icici','axis'}
NONFIN_KEYWORDS    = {'assignment','student','experiment','college','university',
                      'syllabus','lecture','academic','faculty','library'}

def _stub_embedding(text):
    t = text.lower()
    fin  = sum(1 for w in FINANCIAL_KEYWORDS if w in t)
    nfin = sum(1 for w in NONFIN_KEYWORDS   if w in t)
    # Return a simple 2-element "vector" (cosine just compares these)
    return [float(fin), float(nfin)]

def _stub_cosine(a, b):
    # Dot-product similarity (vectors are non-negative so this is fine)
    dot = sum(x*y for x,y in zip(a,b))
    na  = sum(x*x for x in a)**0.5 or 1
    nb  = sum(x*x for x in b)**0.5 or 1
    return dot / (na * nb)

stub = types.ModuleType("semantic_engine")
stub.get_text_embedding = _stub_embedding
stub.cosine_similarity  = _stub_cosine
sys.modules["semantic_engine"] = stub  # force replace (already loaded)

# Force reload evidence_verifier so it picks up the new stub
import importlib
if "evidence_verifier" in sys.modules:
    del sys.modules["evidence_verifier"]
import evidence_verifier as ev

PASS_STR = "PASS"
FAIL_STR = "FAIL"
results = []

def check(label, condition, detail=""):
    status = PASS_STR if condition else FAIL_STR
    print(f"  [{status}] {label}" + (f"  ({detail})" if detail else ""))
    results.append((label, condition))


def run_verifier(extracted_text, **kwargs):
    """Create a real temp file so os.path.exists passes, patch _extract_text."""
    original = ev._extract_text
    def fake_extract(path):
        return {"text": extracted_text, "page_count": 1, "file_ext": "png",
                "status": "READABLE" if extracted_text.strip() else "UNREADABLE"}
    ev._extract_text = fake_extract
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(b"\x89PNG\r\n\x1a\n")
            tmp_path = tmp.name
        result = ev.verify_evidence(file_path=tmp_path, **kwargs)
    finally:
        ev._extract_text = original
        try: os.unlink(tmp_path)
        except Exception: pass
    return result


# ─── Fixtures ────────────────────────────────────────────────────────────────
SVC = "UPI / IMPS / Digital Fund Transfer"

GOOD_DOC = ("HDFC Bank UPI Payment Receipt\n"
            "Transaction Status: FAILED\n"
            "Amount: Rs. 3,500.00\n"
            "UPI Reference: HDFC2026251099872\n"
            "Transaction Date: 25/10/2026\n"
            "Merchant: QuickMart Retail\n"
            "UPI IMPS Transfer debit payment bank transaction")

ICICI_DOC = ("ICICI Bank UPI Transaction\n"
             "Amount: INR 1,999.00\n"
             "UTR No: TEST-UPI-000123\n"
             "Date: 25-10-2026\n"
             "Status: Failed\n"
             "Payment via UPI IMPS transfer debit bank receipt")

WRONG_BANK_DOC = ("Axis Bank Payment Receipt\n"
                  "Amount: Rs. 3500\nDate: 25/10/2026\n"
                  "UTR: HDFC2026251099872\n"
                  "UPI transfer debit IMPS payment bank transaction")

WRONG_AMOUNT_DOC = ("HDFC Bank UPI Receipt\n"
                    "Amount: Rs. 9,999.00\nDate: 25/10/2026\n"
                    "UTR: HDFC2026251099872\n"
                    "UPI IMPS transaction debit payment bank")

WRONG_DATE_DOC = ("HDFC Bank UPI Receipt\n"
                  "Amount: Rs. 3500\nDate: 01/01/2025\n"
                  "UTR: HDFC2026251099872\n"
                  "UPI IMPS transaction debit payment bank")

WRONG_REF_DOC = ("HDFC Bank UPI Receipt\n"
                 "Amount: Rs. 3500\nDate: 25/10/2026\n"
                 "UTR: WRONGREF999999\n"
                 "UPI IMPS transaction debit payment bank")

UNRELATED_DOC = ("Assignment 3 - Database Management Systems\n"
                 "Student: John Doe  Roll: CS101\n"
                 "Experiment: ER diagram for library system\n"
                 "college university faculty academic syllabus lecture experiment student")

# ─── Tests ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  Entity Matching Regression Tests")
print("="*60 + "\n")

print("Test 1: All fields match → VERIFIED")
r = run_verifier(GOOD_DOC, service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500,
    submitted_ref_id="HDFC2026251099872", submitted_date="25/10/2026")
print(f"  verdict={r['verdict']} fields={r.get('field_match_details',{})}")
check("Perfect match → VERIFIED", r["verdict"] == "VERIFIED", r["verdict"])
check("All 4 fields matched", all(v == "matched" for v in r.get("field_match_details", {}).values()))
print()

print("Test 2: Amount '3,500.00' in doc matches submitted 3500")
r = run_verifier(GOOD_DOC, service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500.0, submitted_date="25/10/2026")
check("Amount matched (comma format)", r.get("field_match_details",{}).get("amount") == "matched")
print()

print("Test 3: Date 25-10-2026 == 25/10/2026")
r = run_verifier(GOOD_DOC, service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500, submitted_date="25-10-2026")
print(f"  fields={r.get('field_match_details',{})}")
check("Date format equivalence", r.get("field_match_details",{}).get("date") == "matched")
print()

print("Test 4: Ref ID TEST-UPI-000123 vs TESTUPI000123 (hyphens stripped by OCR)")
doc_no_hyphen = ICICI_DOC.replace("TEST-UPI-000123", "TESTUPI000123")
r = run_verifier(doc_no_hyphen, service_type=SVC,
    submitted_bank="ICICI Bank", submitted_amount=1999,
    submitted_ref_id="TEST-UPI-000123", submitted_date="25-10-2026")
check("Ref ID normalised match", r.get("field_match_details",{}).get("ref_id") == "matched")
print()

print("Test 5: Wrong bank → not VERIFIED, bank=not_found")
r = run_verifier(WRONG_BANK_DOC, service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500, submitted_date="25/10/2026")
check("Wrong bank → not VERIFIED", r["verdict"] != "VERIFIED", r["verdict"])
check("bank = not_found", r.get("field_match_details",{}).get("bank") == "not_found")
print()

print("Test 6: Wrong amount → not VERIFIED")
r = run_verifier(WRONG_AMOUNT_DOC, service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500, submitted_date="25/10/2026")
check("Wrong amount → not VERIFIED", r["verdict"] != "VERIFIED", r["verdict"])
check("amount = not_found", r.get("field_match_details",{}).get("amount") == "not_found")
print()

print("Test 7: Wrong date → not VERIFIED")
r = run_verifier(WRONG_DATE_DOC, service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500, submitted_date="25/10/2026")
check("Wrong date → not VERIFIED", r["verdict"] != "VERIFIED", r["verdict"])
check("date = not_found", r.get("field_match_details",{}).get("date") == "not_found")
print()

print("Test 8: Wrong ref ID → not VERIFIED")
r = run_verifier(WRONG_REF_DOC, service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500,
    submitted_ref_id="HDFC2026251099872", submitted_date="25/10/2026")
check("Wrong ref → not VERIFIED", r["verdict"] != "VERIFIED", r["verdict"])
check("ref_id = not_found", r.get("field_match_details",{}).get("ref_id") == "not_found")
print()

print("Test 9: Unrelated doc (lab manual) → never VERIFIED")
r = run_verifier(UNRELATED_DOC, service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500, submitted_date="25/10/2026")
check("Lab manual → not VERIFIED", r["verdict"] != "VERIFIED", r["verdict"])
print()

print("Test 10: No entity fields → NEEDS_REVIEW")
r = run_verifier(GOOD_DOC, service_type=SVC)
check("No fields → NEEDS_REVIEW", r["verdict"] == "NEEDS_REVIEW", r["verdict"])
print()

print("Test 11: Empty OCR → never VERIFIED")
r = run_verifier("", service_type=SVC,
    submitted_bank="HDFC Bank", submitted_amount=3500)
check("Empty OCR → not VERIFIED", r["verdict"] != "VERIFIED", r["verdict"])
print()

print("Test 12: ICICI / 1999 / 25-10-2026 / TEST-UPI-000123 → VERIFIED")
r = run_verifier(ICICI_DOC, service_type=SVC,
    submitted_bank="ICICI Bank", submitted_amount=1999,
    submitted_ref_id="TEST-UPI-000123", submitted_date="25-10-2026")
print(f"  verdict={r['verdict']} fields={r.get('field_match_details',{})}")
check("ICICI test case → VERIFIED", r["verdict"] == "VERIFIED", r["verdict"])
print()

# ─── Summary ─────────────────────────────────────────────────────────────────
total  = len(results)
passed = sum(1 for _, ok in results if ok)
print("="*60)
print(f"  Results: {passed}/{total} tests PASSED")
print("="*60 + "\n")
sys.exit(0 if passed == total else 1)
