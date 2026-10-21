"""
Full test suite for the 3-Tier Human Coherence Engine in validity_checker.py.
Tests: genuine complaints (EN/Hinglish/Hindi), keyword bombing, gibberish, edge cases.
"""
from validity_checker import check_adaptive_validity

COMMON_ARGS = dict(
    service_type="ATM Cash Withdrawal Failure",
    incident_date="2026-10-10",
    amount=5000,
    reference_id="ATM-882199"
)

test_cases = [
    # ─── SHOULD PASS ───
    ("✅ 1. Genuine English (emotional + narrative)",
     "I went to the ATM yesterday to withdraw cash for my sick mother's medicine. The machine beeped and said dispensed, but no cash came out. However, my account was debited Rs.5000. I am very worried please help me urgently."),

    ("✅ 2. Genuine Hinglish (emotional)",
     "Mere account se 5000 rupaye kat gaye lekin ATM se cash nahi nikla. Main bahut pareshan hu please jaldi refund karo."),

    ("✅ 3. Genuine Hindi (Devanagari)",
     "मेरे खाते से पैसे कट गए हैं लेकिन एटीएम से नकदी नहीं निकली। कृपया मेरी सहायता करें और पैसे वापस करें।"),

    ("✅ 4. Minimal but valid English",
     "My ATM card was declined but the amount was deducted."),

    ("✅ 5. Valid — uses 'issue' without banking vocab overload",
     "I have an issue with my account. The money was transferred but not received by the beneficiary."),

    ("✅ 6. Valid — Natural contraction & transfer dispute",
     "The Payment is done from my side but the receiver hasn't received the amount yet of INR 45500."),

    # ─── SHOULD FAIL ───
    ("❌ 7. KEYWORD BOMBING — pure banking word list",
     "atm bank cash money debit transfer cibil account card fraud payment loan transaction charges penalty"),

    ("❌ 8. KEYWORD BOMBING — varied but no sentence/verb",
     "upi imps neft account number branch code ifsc debit credit savings current hdfc sbi icici"),

    ("❌ 9. GIBBERISH — random keyboard mashing",
     "aslkdjf aweoijfa aweofijasd awoiefjawoeif lkjsdhfkjsdhf kjsdhfkjsd"),

    ("❌ 10. GIBBERISH — consonant clusters",
     "bcrftplk mnxqzt vwrblq skdfmwrpqst"),

    ("❌ 11. TOO SHORT",
     "atm money"),

    ("❌ 12. No grievance verb — just describes a process with no problem",
     "The ATM machine stands at the bank branch near the highway and many customers use it daily for their transactions."),

    ("❌ 13. KEYWORD BOMBING — Hinglish keywords no sentence",
     "atm paise account bank card transfer imps upi neft cibil loan emi penalty"),
]

print("=" * 75)
print("  3-TIER COHERENCE ENGINE — TEST RESULTS")
print("=" * 75)

pass_count = 0
fail_count = 0

for name, desc in test_cases:
    should_pass = name.startswith("✅")
    res = check_adaptive_validity(description=desc, **COMMON_ARGS)
    score = res["score"]
    is_valid = res["is_valid"]
    sem_score = res["breakdown"].get("semantic_and_emotional_validity", 0)
    feedback = res["feedback"]
    lang = res["detected_language"]

    actual = "PASS" if is_valid else "FAIL"
    expected = "PASS" if should_pass else "FAIL"
    correct = "✓" if actual == expected else "✗ WRONG!"

    if actual == expected:
        pass_count += 1
    else:
        fail_count += 1

    print(f"\n{name}")
    print(f"  Score: {score}/100  | Semantic: {sem_score}/35 | Lang: {lang}")
    print(f"  Result: {actual}  | Expected: {expected}  {correct}")
    print(f"  Feedback: {feedback[:100]}")

print()
print("=" * 75)
print(f"  TOTAL: {pass_count} correct / {pass_count + fail_count} tests")
print(f"  {'ALL TESTS PASSED ✅' if fail_count == 0 else f'{fail_count} TESTS FAILED ❌ — review above'}")
print("=" * 75)
