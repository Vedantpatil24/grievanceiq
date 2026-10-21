"""
seed_demo_analytics_data.py - Seeds Realistic Multi-Bank Complaint Data
Populates 25+ realistic grievances across all 8 Indian banks and 5 departments
so the Admin Dashboard charts, statistics, SLA countdowns, and deflection rates
display rich, professional analytics during viva demonstrations.
"""

import os
import random
from datetime import datetime, timedelta
import sqlite3

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grievanceiq.db")
print(f"Connecting to database: {db_path}")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Fetch Banks and Departments
cur.execute("SELECT company_id, company_name FROM companies")
companies = cur.fetchall()

cur.execute("SELECT department_id, department_name FROM departments")
departments = cur.fetchall()

cur.execute("SELECT user_id, full_name, department_id FROM users WHERE role = 'officer'")
officers = cur.fetchall()

if not companies or not departments:
    print("Error: Companies or departments missing. Run migrate_phase1.py first.")
    exit(1)

# Sample realistic complaints bank
SAMPLE_TEMPLATES = [
    # Retail Banking
    (
        "UPI / Digital Payments",
        "Failed UPI transfer of Rs. 3,500 to grocery merchant. Amount debited from savings account but not credited. UTR received.",
        "Retail Banking Team",
        3500.0,
        "Medium",
        "BOT",
        "resolved"
    ),
    (
        "ATM Cash Withdrawal",
        "Withdrew Rs. 10,000 from ATM. Machine made counting sound but dispensed no cash. Account immediately debited.",
        "Retail Banking Team",
        10000.0,
        "Medium",
        "BOT",
        "resolved"
    ),
    (
        "Savings / Current Account",
        "Penalty of Rs. 650 charged for non-maintenance of minimum balance without any prior SMS or email alert.",
        "Retail Banking Team",
        650.0,
        "Low",
        "BOT",
        "resolved"
    ),
    (
        "UPI / Digital Payments",
        "IMPS transfer of Rs. 25,000 to hospital account stuck in pending state for 4 days. Urgently need reversal.",
        "Retail Banking Team",
        25000.0,
        "High",
        "HUMAN",
        "in_progress"
    ),

    # Credit Card Services
    (
        "Credit Card Services",
        "Unauthorized international online charge of Rs. 42,000 from unknown merchant while card was in my possession.",
        "Card Disputes Team",
        42000.0,
        "High",
        "HUMAN",
        "escalated"
    ),
    (
        "Credit Card Services",
        "Annual renewal fee of Rs. 1,500 charged despite meeting annual spend threshold of Rs. 1,00,000 for waiver.",
        "Card Disputes Team",
        1500.0,
        "Low",
        "BOT",
        "resolved"
    ),
    (
        "Credit Card Services",
        "Card bill charged twice through auto-debit facility on the same due date. Overdraft fee also incurred.",
        "Card Disputes Team",
        18500.0,
        "High",
        "HUMAN",
        "in_progress"
    ),
    (
        "Credit Card Services",
        "Suspicious OTP SMS received followed by unauthorized swipe of Rs. 55,000 at POS terminal.",
        "Card Disputes Team",
        55000.0,
        "High",
        "HUMAN",
        "escalated"
    ),

    # Loans
    (
        "Loan Servicing & EMI",
        "Original property deeds and No Objection Certificate (NOC) not dispatched even after 45 days of home loan closure.",
        "Loan Servicing Team",
        0.0,
        "High",
        "HUMAN",
        "escalated"
    ),
    (
        "Loan Servicing & EMI",
        "Double EMI deducted for the month of September from my salary account. Bank helpline not responding.",
        "Loan Servicing Team",
        28000.0,
        "High",
        "HUMAN",
        "in_progress"
    ),
    (
        "Loan Servicing & EMI",
        "Interest rate reset without prior written notification, altering my loan tenure by 36 months.",
        "Loan Servicing Team",
        0.0,
        "Medium",
        "BOT",
        "resolved"
    ),
    (
        "Loan Servicing & EMI",
        "Foreclosure charges levied on floating rate housing loan contrary to regulatory guidelines.",
        "Loan Servicing Team",
        14000.0,
        "Medium",
        "HUMAN",
        "resolved"
    ),

    # Credit Reporting
    (
        "Credit Bureau (CIBIL/Experian)",
        "Fully paid vehicle loan settled in 2024 still reporting as 'Written Off' on TransUnion CIBIL report, dropping my score by 80 points.",
        "Credit Bureau Liaison Team",
        0.0,
        "High",
        "HUMAN",
        "in_progress"
    ),
    (
        "Credit Bureau (CIBIL/Experian)",
        "Overdue credit card payment reflecting on bureau report for an account number that does not belong to my PAN.",
        "Credit Bureau Liaison Team",
        0.0,
        "High",
        "HUMAN",
        "escalated"
    ),
    (
        "Credit Bureau (CIBIL/Experian)",
        "Requesting update of CIBIL record post submission of No Dues Certificate to branch manager.",
        "Credit Bureau Liaison Team",
        0.0,
        "Low",
        "BOT",
        "resolved"
    ),

    # Debt Collection
    (
        "Debt Collection & Recovery",
        "Recovery agents calling repeatedly at 10:30 PM and contacting family members, violating fair practices code.",
        "Collections Compliance Team",
        0.0,
        "High",
        "HUMAN",
        "escalated"
    ),
    (
        "Debt Collection & Recovery",
        "Abusive language used by third party agency representative despite agreeing to visit branch for settlement.",
        "Collections Compliance Team",
        0.0,
        "High",
        "HUMAN",
        "reopened"
    ),
    (
        "Debt Collection & Recovery",
        "Inquiry on procedure to request authorized agency credentials and official statement of dues.",
        "Collections Compliance Team",
        0.0,
        "Low",
        "BOT",
        "resolved"
    )
]

# Fetch existing highest token number
cur.execute("SELECT MAX(complaint_id) FROM complaints")
max_id = cur.fetchone()[0] or 10

dept_dict = {name: did for did, name in departments}
officer_dict = {dept_id: uid for uid, name, dept_id in officers}

now = datetime.utcnow()
count_inserted = 0

print(f"Seeding realistic banking complaints...")

for i, template in enumerate(SAMPLE_TEMPLATES):
    service_type, desc, dept_name, amount, priority, res_mode, status = template
    comp_id, comp_name = random.choice(companies)
    dept_id = dept_dict.get(dept_name, 1)
    
    # Calculate token
    token_num = max_id + i + 1
    token = f"GRV-2026-{str(token_num).zfill(5)}"
    
    # Dates
    days_ago = random.randint(1, 20)
    created_time = now - timedelta(days=days_ago, hours=random.randint(1, 10))
    ref_id = f"{comp_name[:3].upper()}{random.randint(10000000, 99999999)}"
    
    # SLA deadline calculation for escalated tickets
    sla_deadline = None
    escalated_at = None
    sla_breached = 0
    assigned_officer_id = None

    if res_mode == "HUMAN":
        escalated_at = created_time + timedelta(minutes=15)
        assigned_officer_id = officer_dict.get(dept_id, 1)
        
        hours_sla = 24 if priority == "High" else (48 if priority == "Medium" else 120)
        sla_deadline = escalated_at + timedelta(hours=hours_sla)
        
        # Simulate SLA breach on a couple older tickets
        if status in ["escalated", "in_progress"] and days_ago > 5:
            sla_breached = 1

    resolved_at = None
    resolution_notes = None
    reopen_count = 0
    can_reopen_until = None

    if status == "resolved":
        resolved_at = created_time + timedelta(hours=random.randint(2, 36))
        can_reopen_until = resolved_at + timedelta(days=7)
        if res_mode == "BOT":
            resolution_notes = "Customer accepted Tier-1 GrievanceBot automated resolution guidance."
        else:
            resolution_notes = "Investigated by Banking Officer. Inter-bank switch reconciliation and adjustment completed."
    elif status == "reopened":
        reopen_count = 1
        escalated_at = now - timedelta(hours=6)
        sla_deadline = now + timedelta(hours=18)
        priority = "High"

    validity_score = random.randint(82, 98)

    # Insert complaint
    cur.execute("""
    INSERT INTO complaints (
        token, company_id, department_id, submitted_at, raw_text,
        service_type, transaction_date, amount, reference_id, branch,
        description, priority, status, validity_score, validity_status,
        resolution_mode, escalation_level, current_assigned_officer_id,
        escalated_at, sla_deadline, sla_breached, resolved_at,
        resolution_notes, reopen_count, can_reopen_until, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        token, comp_id, dept_id, created_time.isoformat(), desc,
        service_type, (created_time - timedelta(days=2)).strftime("%Y-%m-%d"),
        amount, ref_id, f"{comp_name} City Central",
        desc, priority, status, validity_score, "valid",
        res_mode, 2 if status == "reopened" else (1 if res_mode == "HUMAN" else 0),
        assigned_officer_id, escalated_at, sla_deadline, sla_breached,
        resolved_at, resolution_notes, reopen_count, can_reopen_until,
        created_time, now
    ))
    new_cid = cur.lastrowid

    # Add Status History
    cur.execute("""
    INSERT INTO status_history (complaint_id, old_status, new_status, changed_by, changed_at, comment)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (new_cid, None, "bot_proposed", "system", created_time, "Complaint registered and validated."))

    if status != "bot_proposed":
        cur.execute("""
        INSERT INTO status_history (complaint_id, old_status, new_status, changed_by, changed_at, comment)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (new_cid, "bot_proposed", status, "system" if res_mode == "BOT" else "officer", now, f"Status transitioned to {status}."))

    # Add Feedback for some resolved tickets
    if status == "resolved" and random.random() > 0.3:
        cur.execute("""
        INSERT OR IGNORE INTO feedback (complaint_id, rating, comments, submitted_at)
        VALUES (?, ?, ?, ?)
        """, (new_cid, random.choice([4, 5, 5, 4, 3]), "Resolved promptly. Good guidance provided.", resolved_at))

    count_inserted += 1

conn.commit()
conn.close()

print(f"\n[OK] Successfully seeded {count_inserted} realistic banking complaints across all 8 banks and 5 departments!")
print(f"Database location: {os.path.abspath(db_path)}")
