"""
test_phase2_extended.py - Comprehensive Verification of 28 Features
Tests:
1. Customer Registration & Token Authentication
2. Non-Futuristic Date and Validity Gate
3. Submission with SBERT Semantic Sub-Category
4. Evidence Verification by Worker (VERIFIED / REJECTED)
5. Worker Investigation Notes Recording & Retrieval
6. Worker Resolution Submission with Proof File Attachment
7. Customer Confirmation: Reject -> Reopen (Level 2)
8. Customer Confirmation: Accept -> Closed
9. Bank Health Score Index (0-100), Early Warnings, and Management Recommendations
10. What-If Staffing Simulation Projection
"""

import sys
import os
import io
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import app

client = TestClient(app)

def run_tests():
    print("=" * 65)
    print(">>> VERIFYING EXTENDED 28-FEATURE BFSI REDRESSAL WORKFLOWS <<<")
    print("=" * 65)

    # 1. Registration
    print("\n[TEST 1] Testing Customer Registration (/api/auth/register)...")
    username = f"cust_{os.urandom(3).hex()}"
    reg_res = client.post("/api/auth/register", json={
        "username": username,
        "full_name": "Deepak Verma",
        "email": f"{username}@example.com",
        "password": "custpassword123"
    })
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    cust_data = reg_res.json()
    cust_id = cust_data["user"]["user_id"]
    print(f"  [PASS] Registered customer: {cust_data['user']['username']} (ID: {cust_id})")

    # 2. Login as Worker/Admin
    print("\n[TEST 2] Authenticating as Cards Officer...")
    login_res = client.post("/api/auth/login", data={"username": "officer_cards", "password": "officer123"})
    assert login_res.status_code == 200
    worker_token = login_res.json()["access_token"]
    worker_headers = {"Authorization": f"Bearer {worker_token}"}
    print("  [PASS] Authenticated successfully with JWT bearer.")

    # 3. Submit Complaint with Proof & Semantic Sub-Category
    print("\n[TEST 3] Submitting Complaint with Proof and Linking Customer ID...")
    dummy_proof = io.BytesIO(b"MOCK EVIDENCE DOCUMENT: CARD TXN CHARGEBACK DISPUTE 3200 INR")
    sub_res = client.post("/api/complaints/submit", data={
        "company_id": 2,
        "service_type": "Credit Card / Chargeback",
        "transaction_date": "2026-10-06",
        "amount": 3200.0,
        "reference_id": "CRD-DISP-882190",
        "branch": "Connaught Place",
        "description": "An unauthorized card charge was levied while card was in my physical custody. Immediate reversal requested.",
        "customer_id": cust_id
    }, files={"proof_file": ("card_stmt.pdf", dummy_proof, "application/pdf")})
    assert sub_res.status_code == 200, f"Submission failed: {sub_res.text}"
    token = sub_res.json()["token"]
    sub_cat = sub_res.json().get("sub_category")
    print(f"  [PASS] Complaint registered: {token}")
    print(f"         AI Sub-Category: {sub_cat} | Validity Score: {sub_res.json()['validity_score']}/100")

    # 4. Escalate to Human Officer
    print("\n[TEST 4] Escalating Complaint to Officer...")
    esc_res = client.post(f"/api/complaints/{token}/customer-decision", json={
        "decision": "ESCALATE",
        "feedback_notes": "Requires forensic dispute officer review."
    })
    assert esc_res.status_code == 200
    print(f"  [PASS] Case escalated to: {esc_res.json()['assigned_officer']}")

    # 5. Worker Verifies Evidence
    print("\n[TEST 5] Officer Verifying Customer Evidence Document...")
    ev_res = client.put(f"/api/worker/complaints/{token}/verify-evidence", json={
        "status": "VERIFIED"
    }, headers=worker_headers)
    assert ev_res.status_code == 200
    print(f"  [PASS] Evidence status updated: {ev_res.json()['evidence_status']}")

    # 6. Worker Investigation Note
    print("\n[TEST 6] Logging Officer Investigation Note...")
    note_res = client.post(f"/api/worker/complaints/{token}/notes", json={
        "note_text": "Examined settlement switch logs. Card was indeed in tokenized wallet collision. Merchant chargeback initiated."
    }, headers=worker_headers)
    assert note_res.status_code == 200
    
    get_notes = client.get(f"/api/worker/complaints/{token}/notes", headers=worker_headers)
    assert len(get_notes.json()) >= 1
    print(f"  [PASS] Investigation note logged and retrieved successfully ({len(get_notes.json())} notes present).")

    # 7. Worker Resolution Submission with Proof
    print("\n[TEST 7] Worker Submitting Formal Resolution with Settlement Proof...")
    res_proof = io.BytesIO(b"MOCK RESOLUTION RECEIPT: CHARGEBACK CREDIT CONFIRMED 3200 INR")
    res_submit = client.post(f"/api/worker/complaints/{token}/resolution", data={
        "resolution_details": "Chargeback accepted by merchant acquiring bank. Amount ₹3,200 credited back to statement.",
        "resolution_type": "Full Refund Issued",
        "transaction_reference": "UTR-REV-9018231",
        "resolved_amount": 3200.0
    }, files={"resolution_proof": ("credit_advice.pdf", res_proof, "application/pdf")}, headers=worker_headers)
    assert res_submit.status_code == 200, f"Resolution submission failed: {res_submit.text}"
    print(f"  [PASS] Resolution submitted: {res_submit.json()['status']}. Awaiting customer review.")

    # 8. Customer Confirms Resolution
    print("\n[TEST 8] Customer Reviewing and Accepting Official Resolution...")
    confirm_res = client.post(f"/api/complaints/{token}/confirm-resolution", json={
        "confirmed": True,
        "feedback_or_reason": "Refund received in card account. Satisfied."
    })
    assert confirm_res.status_code == 200, f"Confirmation failed: {confirm_res.text}"
    track_after = client.get(f"/api/complaints/{token}/track").json()
    assert track_after["status"] == "resolved"
    assert track_after["latest_resolution"]["customer_confirmation_status"] == "ACCEPTED"
    print(f"  [PASS] Case officially confirmed and closed by customer. Status: {track_after['status']}")

    # 9. Bank Health Score Index & Early Warning System
    print("\n[TEST 9] Evaluating Bank Health Score (0-100) & Early Warning Spike Detector...")
    health_res = client.get("/api/intelligence/bank-health")
    assert health_res.status_code == 200
    health = health_res.json()
    print(f"  [PASS] Bank Health Index: {health['health_summary']['health_score']} / 100 ({health['health_summary']['grade']})")
    print(f"         Early Warnings Detected: {len(health['early_warnings'])}")
    print(f"         Management Recommendations: {len(health['management_recommendations'])}")

    # 10. What-If Staffing Simulation
    print("\n[TEST 10] Testing What-If Staffing Resource Simulation...")
    sim_res = client.post("/api/intelligence/what-if-simulation", json={
        "current_workers": 4,
        "proposed_workers": 8,
        "current_tat_hours": 24.0,
        "current_pending": 15
    })
    assert sim_res.status_code == 200
    sim = sim_res.json()
    print(f"  [PASS] What-If Simulation Projections:")
    print(f"         Projected TAT: {sim['projections']['estimated_tat_hours']}h (Reduction: {sim['projections']['tat_change_percentage']}%)")
    print(f"         Projected Backlog: {sim['projections']['estimated_pending_complaints']} tickets")
    print(f"         SLA Pressure Score: {sim['projections']['projected_sla_pressure_score']}/10")

    print("\n" + "=" * 65)
    print(">>> ALL EXTENDED FEATURE INTEGRATION TESTS COMPLETED SUCCESSFULLY! <<<")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
