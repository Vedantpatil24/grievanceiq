import time
import random
import threading
import uuid
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Complaint, Worker

DB_PATH = r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db"
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)

RESOLUTION_TEMPLATES = [
    {
        "notes": "Transaction reversal successfully executed through core banking settlement switch. Funds credited back to customer account.",
        "proof_type": "NEFT/UPI Settlement UTR: UTR-REV-{ref}-SUCCESS. System reconciliation confirmed 0 discrepancy.",
    },
    {
        "notes": "Disputed debit analyzed against merchant gateway logs. Chargeback initiated and provisional credit finalized.",
        "proof_type": "Merchant Chargeback Reference: CBK-NPCI-{ref}-APPROVED. Merchant acceptance log attached.",
    },
    {
        "notes": "Technical timeout exception verified with central payment switch. Auto-reversal processed per RBI guidelines.",
        "proof_type": "Switch Log Trace: RRN-{ref}-REVERSED-OK. Timed out at acquirer terminal, funds restored.",
    },
    {
        "notes": "Billing adjustment applied following verification of transaction history and bank statement records.",
        "proof_type": "CBS Ledger Voucher: VOUCH-{ref}-CREDIT. Account balance updated accordingly.",
    }
]

REJECTION_REASONS = [
    "Submitted transaction reference ID is invalid or cannot be traced in the core banking switch for the specified date.",
    "Uploaded document does not correspond to the reported transaction details (discrepancy in date, account number, or amount).",
    "Duplicate grievance detected: An identical dispute for this transaction reference is already under active processing.",
    "Insufficient supporting documentation provided: Required transaction receipt or SMS confirmation was illegible or incomplete."
]

def generate_resolution_proof(complaint_token, ref_id):
    """Generates an official automated resolution certificate text file in uploads."""
    ref_clean = (ref_id or "TXN9999").replace(" ", "")
    template = random.choice(RESOLUTION_TEMPLATES)
    filename = f"resolution_proof_{complaint_token}.txt"
    upload_dir = r"G:\Mini_project\Python_codes\uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)

    content = f"""=======================================================
GRIEVANCEIQ - OFFICIAL GRIEVANCE RESOLUTION RECEIPT
=======================================================
Complaint Token   : {complaint_token}
Resolution Date   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Core Banking Ref  : {ref_clean}
Status Outcome    : RESOLVED & VERIFIED

INVESTIGATION FINDINGS:
{template['notes']}

TECHNICAL AUDIT TRAIL / PROOF:
{template['proof_type'].format(ref=ref_clean)}

Verified by Automated BFSI Triage & Settlement Engine
======================================================="""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return template["notes"], f"/uploads/{filename}"

def simulate_bot_tick():
    """Runs a single simulation tick:
    1. Evaluates open complaints:
       - Either moves to Investigation (in_progress)
       - OR if semantic score / document similarity is very poor, rejects with a detailed reason
    2. Investigated complaints move to Resolved with generated Resolution Proof & Audit Notes
    """
    session = Session()
    try:
        now = datetime.now()

        # Step 1: Open -> In Progress OR Rejected
        open_complaints = session.query(Complaint).filter(
            Complaint.status == "open"
        ).order_by(Complaint.created_at.asc()).limit(4).all()

        for c in open_complaints:
            age_seconds = (now - (c.created_at or now)).total_seconds()
            if age_seconds >= 20:
                # Check for rejection criteria:
                # If sbert score is very low (< 0.35) or proof similarity is low and narrative has poor entities
                is_substandard = (
                    (c.sbert_narrative_score is not None and c.sbert_narrative_score < 0.32) or
                    (c.validity_score is not None and c.validity_score < 60)
                )

                if is_substandard and not c.rejection_reason:
                    # Reject complaint with clear explanation
                    c.status = "rejected"
                    c.stage = "Closed"
                    c.rejection_reason = random.choice(REJECTION_REASONS)
                    c.resolved_at = now
                    print(f"[BOT SIMULATOR] ❌ Bot {c.assigned_worker_id} rejected {c.token}. Reason: {c.rejection_reason}")
                else:
                    c.status = "in_progress"
                    c.stage = "Investigation"
                    print(f"[BOT SIMULATOR] 🤖 Bot {c.assigned_worker_id or 'Bot'} picked up {c.token} -> INVESTIGATION")

        # Step 2: In Progress -> Resolved with Resolution Proof
        in_progress_complaints = session.query(Complaint).filter(
            Complaint.status == "in_progress"
        ).order_by(Complaint.created_at.asc()).limit(3).all()

        for c in in_progress_complaints:
            baseline_time = c.created_at or now
            elapsed = (now - baseline_time).total_seconds()

            threshold_map = {
                "High": 60,     # 1 min in active simulation
                "Medium": 120,  # 2 min
                "Low": 240      # 4 min
            }
            required_wait = threshold_map.get(c.priority, 120)

            if elapsed >= required_wait:
                notes, proof_url = generate_resolution_proof(c.token, c.reference_id)
                c.status = "resolved"
                c.stage = "Resolved"
                c.resolved_at = now
                c.resolution_notes = notes
                c.resolution_proof_url = proof_url
                print(f"[BOT SIMULATOR] ✅ Bot {c.assigned_worker_id} resolved {c.token} with Proof: {proof_url}")

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"[BOT SIMULATOR ERROR] {e}")
    finally:
        session.close()

def run_bot_worker_loop(interval_seconds=25):
    """Background loop ticking every interval_seconds."""
    print("[BOT SIMULATOR] Started live bot automation engine with proof & rejection generator...")
    while True:
        try:
            simulate_bot_tick()
        except Exception as e:
            print(f"[BOT SIMULATOR LOOP ERROR] {e}")
        time.sleep(interval_seconds)

def start_bot_simulator_thread():
    """Spawns the background simulator thread."""
    t = threading.Thread(target=run_bot_worker_loop, daemon=True, name="BotSimulatorThread")
    t.start()
    return t

if __name__ == "__main__":
    simulate_bot_tick()
