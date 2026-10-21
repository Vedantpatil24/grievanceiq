"""
test_e2e_workflows.py - End-to-End System Integration Test
Validates all major BFSI complaint workflows, ML classification,
GrievanceBot Tier-1 triage, Customer Decision, SLA engine,
Officer Assignment, Messaging, Reopening, and Analytics.
"""

import sys
import os
import io
from fastapi.testclient import TestClient

# Add Python_codes to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import app, get_db

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print(">>> GRIEVANCEIQ FULL END-TO-END INTEGRATION TEST SUITE <<<")
    print("=" * 60)

    # -----------------------------------------------------------
    # TEST 1: Validity Rejection on Incomplete / Junk Complaint
    # -----------------------------------------------------------
    print("\n[TEST 1] Testing Validity Gate on Incomplete Complaint (Score < 70)...")
    res = client.post("/api/complaints/submit", data={
        "company_id": 1,
        "service_type": "Other",
        "transaction_date": "2026-10-01",
        "amount": 10.0,
        "reference_id": "123",
        "branch": "Main Branch",
        "description": "Too brief description."
    })
    assert res.status_code == 422, f"Expected 422 but got {res.status_code}: {res.text}"
    detail = res.json()["detail"]
    if isinstance(detail, dict):
        assert detail["score"] < 70
        print(f"  [PASS] Successfully rejected incomplete complaint with score: {detail['score']}/100.")
        print(f"         Missing elements detected: {detail.get('missing_items')}")
    else:
        print(f"  [PASS] Successfully rejected with schema validation error: {detail}")

    # -----------------------------------------------------------
    # TEST 2: Valid Complaint Submission & Tier-1 GrievanceBot Analysis
    # -----------------------------------------------------------
    print("\n[TEST 2] Testing Valid Submission & Tier-1 GrievanceBot Assessment...")
    dummy_proof = io.BytesIO(b"MOCK RECEIPT CONTENT: TXN98765432 AMOUNT 4500.00 FAILED ATM")
    res = client.post(
        "/api/complaints/submit",
        data={
            "company_id": 1,
            "service_type": "UPI / Digital Payments",
            "transaction_date": "2026-10-05",
            "amount": 4500.00,
            "reference_id": "UPI-884910284710",
            "branch": "Mumbai Bandra",
            "description": "I transferred money via UPI to merchant account but funds were debited and not credited to beneficiary. Amount is stuck for 3 days."
        },
        files={"proof_file": ("receipt.jpg", dummy_proof, "image/jpeg")}
    )
    assert res.status_code == 200, f"Submission failed: {res.text}"
    sub_data = res.json()
    token_a = sub_data["token"]
    assert token_a.startswith("GRV-2026-")
    assert sub_data["validity_score"] >= 70
    assert "bot_assessment" in sub_data
    assert sub_data["bot_assessment"]["recommendation_type"] in ["SELF_SERVICE_GUIDANCE", "RECOMMEND_HUMAN_ESCALATION"]
    print(f"  [PASS] Complaint registered successfully with Token: {token_a}")
    print(f"         ML Category: {sub_data['category']} | Priority: {sub_data['priority']}")
    print(f"         Validity Score: {sub_data['validity_score']}/100")
    print(f"         Bot Proposed Solution: {sub_data['bot_assessment']['title']}")
    print(f"         OCR Extraction Mode: {sub_data['ocr_verification']['extraction_mode']}")

    # -----------------------------------------------------------
    # TEST 3: Customer Decision Scenario A (Accepts Bot Guidance -> RESOLVED)
    # -----------------------------------------------------------
    print("\n[TEST 3] Testing Customer Decision: SOLVED by Bot...")
    dec_res = client.post(f"/api/complaints/{token_a}/customer-decision", json={
        "decision": "SOLVED",
        "feedback_notes": "The UPI UTR turnaround guidance helped me understand the 48h settlement cycle."
    })
    assert dec_res.status_code == 200
    track_res = client.get(f"/api/complaints/{token_a}/track")
    track_data = track_res.json()
    assert track_data["status"] == "resolved"
    assert track_data["resolution_mode"] == "BOT"
    print(f"  [PASS] Token {token_a} status: {track_data['status']} | Mode: {track_data['resolution_mode']}")

    # Submit feedback rating
    fb_res = client.post(f"/api/complaints/{token_a}/feedback", json={
        "rating": 5,
        "comments": "Instant self-service resolution was very helpful!"
    })
    assert fb_res.status_code == 200
    print("  [PASS] Post-resolution feedback (5/5) recorded successfully.")

    # -----------------------------------------------------------
    # TEST 4: Customer Decision Scenario B (Escalate to Human Officer & SLA)
    # -----------------------------------------------------------
    print("\n[TEST 4] Testing Customer Decision: ESCALATE to Officer...")
    dummy_proof_b = io.BytesIO(b"MOCK CARD STATEMENT: FRAUDULENT INTERNATIONAL PURCHASE 65000.00")
    res_b = client.post(
        "/api/complaints/submit",
        data={
            "company_id": 2,  # HDFC Bank
            "service_type": "Credit Card Services",
            "transaction_date": "2026-10-06",
            "amount": 65000.00,
            "reference_id": "CRD-9988776655",
            "branch": "Delhi Connaught Place",
            "description": "Unauthorized high value transaction charged on my credit card without OTP or my consent while I was traveling."
        },
        files={"proof_file": ("card_stmt.pdf", dummy_proof_b, "application/pdf")}
    )
    token_b = res_b.json()["token"]
    
    # Customer escalates
    esc_res = client.post(f"/api/complaints/{token_b}/customer-decision", json={
        "decision": "ESCALATE",
        "feedback_notes": "Urgent fraudulent charge requires investigation and card dispute."
    })
    assert esc_res.status_code == 200
    esc_data = esc_res.json()
    assert esc_data["status"] == "escalated"
    assert esc_data["resolution_mode"] == "HUMAN"
    
    # Check SLA and assignment
    track_b = client.get(f"/api/complaints/{token_b}/track").json()
    assert track_b["sla"]["has_sla"] == True
    print(f"  [PASS] Token {token_b} escalated to Officer: {track_b['assigned_officer']}")
    print(f"         Active SLA: {track_b['sla']['formatted_remaining']}")

    # -----------------------------------------------------------
    # TEST 5: Customer <-> Officer Messaging
    # -----------------------------------------------------------
    print("\n[TEST 5] Testing Customer <-> Officer Messaging...")
    # Customer posts message
    client.post(f"/api/complaints/{token_b}/messages", json={
        "message_text": "I have already blocked my physical card via netbanking. Please confirm.",
        "sender_type": "customer",
        "sender_name": "Customer"
    })
    # Officer replies
    client.post(f"/api/complaints/{token_b}/messages", json={
        "message_text": "Noted. We have cross-checked with the VISA switch and initiated dispute chargeback.",
        "sender_type": "officer",
        "sender_name": "Rajesh Sharma (Cards Desk)"
    })
    msg_res = client.get(f"/api/complaints/{token_b}/messages")
    assert len(msg_res.json()) >= 2
    print(f"  [PASS] Verified message thread with {len(msg_res.json())} messages.")

    # -----------------------------------------------------------
    # TEST 6: Admin Workspace Login & 1-Click AI Copilot Letter
    # -----------------------------------------------------------
    print("\n[TEST 6] Testing Admin Authentication & AI Copilot Drafter...")
    login_res = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    adm_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {adm_token}"}

    copilot_res = client.post(f"/api/admin/complaints/{token_b}/draft-copilot-resolution", headers=headers)
    assert copilot_res.status_code == 200
    draft = copilot_res.json()["draft_resolution"]
    assert "OFFICIAL GRIEVANCE REDRESSAL MEMORANDUM" in draft
    assert token_b in draft
    print("  [PASS] Admin authenticated. 1-Click AI Copilot resolution letter generated:")
    print("         Snippet:", draft.splitlines()[0], draft.splitlines()[1])

    # -----------------------------------------------------------
    # TEST 7: Case Reopen within 7-Day Window
    # -----------------------------------------------------------
    print("\n[TEST 7] Testing Case Reopen Governance (Level 2 Senior Nodal Escalation)...")
    # Resolve token_b first
    client.put(f"/api/admin/complaints/{token_b}/status", json={"status": "resolved", "resolution_notes": "Temporary provisional credit applied."}, headers=headers)
    
    # Customer reopens case
    reopen_res = client.post(f"/api/complaints/{token_b}/reopen", json={
        "reopen_reason": "Merchant processed second debit again. Provisional credit reversed."
    })
    assert reopen_res.status_code == 200
    track_reopen = client.get(f"/api/complaints/{token_b}/track").json()
    assert track_reopen["status"] == "reopened"
    assert track_reopen["escalation_level"] == 2
    assert track_reopen["reopen_count"] == 1
    print(f"  [PASS] Case reopened successfully! Elevated to Level {track_reopen['escalation_level']} (Senior Nodal).")

    # -----------------------------------------------------------
    # TEST 8: Analytics & Audit Log Verification
    # -----------------------------------------------------------
    print("\n[TEST 8] Testing Analytics & Audit Log Verification...")
    analytics_res = client.get("/api/analytics/overview")
    assert analytics_res.status_code == 200
    overview = analytics_res.json()
    assert overview["total_complaints"] >= 2
    assert overview["bot_deflection_rate_pct"] >= 0
    print(f"  [PASS] Total Grievances: {overview['total_complaints']} | Bot Deflection: {overview['bot_deflection_rate_pct']}%")

    audit_res = client.get("/api/admin/audit-logs", headers=headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) >= 4
    print(f"  [PASS] Verified {len(logs)} audit trail events logged.")

    print("\n" + "=" * 60)
    print(">>> ALL 8 END-TO-END WORKFLOW INTEGRATION TESTS PASSED! <<<")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
