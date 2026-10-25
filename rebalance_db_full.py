import sqlite3
import random
import os
from datetime import datetime, timedelta

db_path = r'G:\Mini_project\Python_codes\grievanceiq.db'
dataset_db_path = r'G:\Mini_project\Dataset\grievanceiq.db'

sample_proofs = {
    'upi': [
        r'uploads\samples\upi_imps_statement_proof.png',
        r'uploads\samples\upi_imps_statement_proof.pdf',
        r'uploads\samples\upi_imps_statement_proof.txt'
    ],
    'cards': [
        r'uploads\samples\credit_card_statement_proof.png',
        r'uploads\samples\credit_card_statement_proof.pdf',
        r'uploads\samples\credit_card_statement_proof.txt',
        r'uploads\samples\atm_dispense_failure_slip.png',
        r'uploads\samples\atm_dispense_failure_slip.pdf',
        r'uploads\samples\atm_dispense_failure_slip.txt',
        r'uploads\samples\police_fir_lost_card.png',
        r'uploads\samples\police_fir_lost_card.pdf'
    ],
    'loans': [
        r'uploads\samples\loan_foreclosure_noc_receipt.txt',
        r'uploads\samples\cibil_credit_report_dispute.txt',
        r'uploads\samples\recovery_call_log_harassment.txt',
        r'uploads\samples\kyc_compliance_pan_aadhaar.txt'
    ]
}

def rebalance_db(path):
    if not os.path.exists(path):
        print(f"File {path} does not exist, skipping.")
        return
    print(f"\nProcessing {path}...")
    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute("SELECT complaint_id, department_id FROM complaints ORDER BY complaint_id")
    rows = c.fetchall()
    total = len(rows)
    print(f"Total complaints found: {total}")

    bot_target_count = int(total * 0.57) # ~57% AI resolved
    print(f"Target BOT resolved: {bot_target_count}, Human queue: {total - bot_target_count}")

    # Randomly shuffle indices for balanced distribution
    random.seed(42)
    shuffled_rows = list(rows)
    random.shuffle(shuffled_rows)

    bot_set = set(r[0] for r in shuffled_rows[:bot_target_count])

    updates = []
    # Department mapping:
    # 6 (Digital & UPI) -> 1 (Retail Banking Team, officer 9 Pooja Sharma)
    # 7 (Loans & Advances) -> 3 (Loan Servicing Team, officer 11 Vikram Mehta)
    # 8 (Cards & ATM) -> 2 (Card Disputes Team, officer 10 Rahul Nair)
    # 9 (Account & Branch Operations) -> 1 (Retail Banking Team, officer 9)
    # 10 (Fraud & Risk Management) -> split across 1, 2, 3

    dept_officer_map = {
        1: 9,   # Pooja Sharma
        2: 10,  # Rahul Nair
        3: 11   # Vikram Mehta
    }

    dept_service_map = {
        1: ('Digital & UPI Banking', 'upi'),
        2: ('Card & ATM Services', 'cards'),
        3: ('Loans & Advances', 'loans')
    }

    fraud_target_depts = [1, 2, 3]

    for idx, (cid, old_dept) in enumerate(rows):
        if old_dept == 6 or old_dept == 9:
            new_dept = 1
        elif old_dept == 7:
            new_dept = 3
        elif old_dept == 8:
            new_dept = 2
        elif old_dept == 10:
            new_dept = fraud_target_depts[cid % 3]
        elif old_dept in (1, 2, 3):
            new_dept = old_dept
        else:
            new_dept = (cid % 3) + 1

        service_type, cat_key = dept_service_map[new_dept]
        proof_file = random.choice(sample_proofs[cat_key])

        is_bot = cid in bot_set

        if is_bot:
            status = 'resolved'
            resolution_mode = 'BOT'
            assigned_officer = None # Fully autonomous
            validity_score = random.randint(86, 99)
            resolution_notes = (
                "Statutory settlement memorandum executed autonomously under RBI Turn Around Time (TAT) Framework. "
                "Disputed amount verified against gateway ledger and credited/settled successfully."
            )
            resolved_at = (datetime.utcnow() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S')
            evidence_status = 'VERIFIED'
        else:
            status = random.choice(['in_progress', 'pending', 'under_review'])
            resolution_mode = 'HUMAN'
            assigned_officer = dept_officer_map[new_dept]
            validity_score = random.randint(60, 85)
            resolution_notes = None
            resolved_at = None
            evidence_status = random.choice(['VERIFIED', 'NEEDS_REVIEW', 'PENDING'])

        updates.append((
            new_dept,
            service_type,
            proof_file,
            validity_score,
            resolution_mode,
            assigned_officer,
            status,
            resolution_notes,
            resolved_at,
            evidence_status,
            cid
        ))

    c.executemany("""
        UPDATE complaints SET
            department_id = ?,
            service_type = ?,
            proof_file_path = ?,
            validity_score = ?,
            resolution_mode = ?,
            current_assigned_officer_id = ?,
            status = ?,
            resolution_notes = ?,
            resolved_at = ?,
            evidence_status = ?
        WHERE complaint_id = ?
    """, updates)

    conn.commit()

    print("--- POST REBALANCE STATS ---")
    c.execute("SELECT department_id, COUNT(*) FROM complaints GROUP BY department_id")
    for r in c.fetchall():
        print(f"Dept {r[0]}: {r[1]} complaints")

    c.execute("SELECT resolution_mode, COUNT(*) FROM complaints GROUP BY resolution_mode")
    for r in c.fetchall():
        print(f"Resolution mode {r[0]}: {r[1]} complaints")

    c.execute("SELECT current_assigned_officer_id, COUNT(*) FROM complaints GROUP BY current_assigned_officer_id")
    for r in c.fetchall():
        print(f"Officer {r[0]}: {r[1]} complaints")

    conn.close()
    print("Database update complete!")

if __name__ == '__main__':
    rebalance_db(db_path)
    rebalance_db(dataset_db_path)
