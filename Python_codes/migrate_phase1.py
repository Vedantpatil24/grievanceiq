"""
migrate_phase1.py - Safe, Idempotent Database Migration Script
Safely applies missing columns, creates new tables, and seeds initial master data
without deleting or overwriting any existing complaint or model records.
"""

import sqlite3
import os
from datetime import datetime
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

DB_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(DB_DIR, "grievanceiq.db")

print(f"[1/6] Connecting to SQLite database at: {db_path}")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# -------------------------------------------------------------
# 1. Safely add missing columns to 'complaints'
# -------------------------------------------------------------
print("[2/6] Checking columns in 'complaints' table...")
cur.execute("PRAGMA table_info(complaints)")
existing_complaint_cols = [row[1] for row in cur.fetchall()]

complaint_columns = [
    ("token", "TEXT"),
    ("service_type", "TEXT"),
    ("transaction_date", "TEXT"),
    ("amount", "REAL"),
    ("reference_id", "TEXT"),
    ("branch", "TEXT"),
    ("description", "TEXT"),
    ("proof_file_path", "TEXT"),
    ("priority", "TEXT DEFAULT 'Medium'"),
    ("status", "TEXT DEFAULT 'open'"),
    ("validity_score", "INTEGER DEFAULT 0"),
    ("validity_status", "TEXT DEFAULT 'valid'"),
    ("department_id", "INTEGER REFERENCES departments(department_id)"),
    ("resolution_mode", "TEXT DEFAULT 'NONE'"),
    ("matched_article_id", "INTEGER REFERENCES knowledge_base_articles(article_id)"),
    ("bot_confidence", "REAL"),
    ("escalation_level", "INTEGER DEFAULT 0"),
    ("current_assigned_officer_id", "INTEGER REFERENCES users(user_id)"),
    ("escalated_at", "DATETIME"),
    ("escalation_reason", "TEXT"),
    ("sla_deadline", "DATETIME"),
    ("sla_breached", "BOOLEAN DEFAULT 0"),
    ("resolved_at", "DATETIME"),
    ("resolution_notes", "TEXT"),
    ("reopen_count", "INTEGER DEFAULT 0"),
    ("can_reopen_until", "DATETIME"),
    ("created_at", "DATETIME"),
    ("updated_at", "DATETIME")
]

for col_name, col_type in complaint_columns:
    if col_name not in existing_complaint_cols:
        try:
            cur.execute(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_type};")
            print(f"  [+] Added column to complaints: {col_name}")
        except Exception as e:
            print(f"  [!] Note on {col_name}: {e}")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_complaints_token ON complaints(token);")
# Backfill token/description for any existing rows
cur.execute("SELECT complaint_id, raw_text, token FROM complaints")
for row in cur.fetchall():
    cid, raw_text, token = row
    if not token:
        new_token = f"GRV-2026-{str(cid).zfill(5)}"
        cur.execute("UPDATE complaints SET token = ?, description = ? WHERE complaint_id = ?", (new_token, raw_text, cid))
        print(f"  [~] Backfilled token {new_token} for existing complaint {cid}")

# -------------------------------------------------------------
# 2. Safely create or update 'users' table
# -------------------------------------------------------------
print("[3/6] Checking 'users' table...")
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT DEFAULT 'Banking Officer',
    role TEXT DEFAULT 'staff',
    department_id INTEGER REFERENCES departments(department_id),
    is_active BOOLEAN DEFAULT 1
);
""")

cur.execute("PRAGMA table_info(users)")
existing_user_cols = [row[1] for row in cur.fetchall()]
for col_name, col_type in [("department_id", "INTEGER"), ("is_active", "BOOLEAN DEFAULT 1"), ("full_name", "TEXT DEFAULT 'Banking Officer'")]:
    if col_name not in existing_user_cols:
        cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")
        print(f"  [+] Added column to users: {col_name}")

# Seed default admin and officers if not present
default_users = [
    ("admin", "admin123", "System Administrator", "admin", None),
    ("officer_cards", "officer123", "Rajesh Sharma (Cards Desk)", "officer", 1),
    ("officer_loans", "officer123", "Priya Nair (Loans Desk)", "officer", 2),
    ("officer_retail", "officer123", "Amit Verma (Retail Accounts)", "officer", 3),
]
for username, pwd, full_name, role, dept_id in default_users:
    cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    if not cur.fetchone():
        hashed = hash_password(pwd)
        cur.execute(
            "INSERT INTO users (username, hashed_password, full_name, role, department_id, is_active) VALUES (?, ?, ?, ?, ?, 1)",
            (username, hashed, full_name, role, dept_id)
        )
        print(f"  [+] Seeded user: {username} ({role})")

# -------------------------------------------------------------
# 3. Create New Workflow Tables
# -------------------------------------------------------------
print("[4/6] Creating workflow & audit tables...")

cur.execute("""
CREATE TABLE IF NOT EXISTS knowledge_base_articles (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER REFERENCES departments(department_id),
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    keywords TEXT NOT NULL,
    guidance_steps TEXT NOT NULL,
    regulatory_reference TEXT,
    can_self_resolve BOOLEAN DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS complaint_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    sender_type TEXT NOT NULL,
    sender_id INTEGER,
    sender_name TEXT DEFAULT 'Customer',
    message_text TEXT NOT NULL,
    attachment_path TEXT,
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    recipient_type TEXT NOT NULL,
    recipient_id INTEGER,
    notification_type TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS assignment_history (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    officer_id INTEGER NOT NULL REFERENCES users(user_id),
    assigned_at DATETIME,
    unassigned_at DATETIME,
    reason TEXT,
    assigned_by INTEGER REFERENCES users(user_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS escalation_history (
    escalation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    from_level INTEGER DEFAULT 0,
    to_level INTEGER DEFAULT 1,
    reason TEXT NOT NULL,
    triggered_by TEXT NOT NULL,
    previous_officer_id INTEGER REFERENCES users(user_id),
    new_officer_id INTEGER REFERENCES users(user_id),
    created_at DATETIME
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_type TEXT NOT NULL,
    actor_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    details TEXT,
    timestamp DATETIME
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS status_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_by TEXT DEFAULT 'system',
    changed_at DATETIME,
    comment TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL UNIQUE REFERENCES complaints(complaint_id),
    rating INTEGER NOT NULL,
    comments TEXT,
    submitted_at DATETIME
);
""")

# -------------------------------------------------------------
# 4. Seed Banks / Companies (7 Indian Banks + Other)
# -------------------------------------------------------------
print("[5/6] Checking Indian banking institutions in 'companies'...")
indian_banks = [
    "State Bank of India (SBI)",
    "HDFC Bank",
    "ICICI Bank",
    "Punjab National Bank",
    "Axis Bank",
    "Kotak Mahindra Bank",
    "Bank of Baroda",
    "Other"
]
for bank in indian_banks:
    cur.execute("SELECT company_id FROM companies WHERE company_name = ?", (bank,))
    if not cur.fetchone():
        cur.execute("INSERT INTO companies (company_name) VALUES (?)", (bank,))
        print(f"  [+] Added bank: {bank}")

# -------------------------------------------------------------
# 5. Seed Neutral Knowledge Base Articles
# -------------------------------------------------------------
print("[6/6] Checking knowledge base articles...")
cur.execute("SELECT COUNT(*) FROM knowledge_base_articles")
kb_count = cur.fetchone()[0]

if kb_count == 0:
    now_iso = datetime.utcnow().isoformat()
    cur.execute("SELECT department_id, department_name FROM departments")
    dept_map = {name: dept_id for dept_id, name in cur.fetchall()}

    sample_articles = [
        (
            dept_map.get("Retail Banking Team", 3),
            "Failed UPI / Digital Payment Debited but Beneficiary Uncredited",
            "Bank Accounts and Services",
            "upi, gpay, phonepe, paytm, imps, debited not credited, transfer failure, payment stuck",
            (
                "1. Check your transaction SMS or mini-statement for the 12-digit UPI Reference Number (UTR/RRN).\n"
                "2. Standard inter-bank clearing cycles typically reconcile pending transactions within 1 to 2 business days.\n"
                "3. Check with the beneficiary if the transaction was automatically credited or reversed.\n"
                "4. If funds remain uncredited after 48 hours, file a dispute request with your bank using your UTR number."
            ),
            "Banking Ombudsman Guidelines for Electronic Banking Transactions",
            1, 1, now_iso, now_iso
        ),
        (
            dept_map.get("Retail Banking Team", 3),
            "ATM Cash Not Dispensed but Account Debited",
            "Bank Accounts and Services",
            "atm, cash not dispensed, machine, atm withdrawal, cash failed, atm debited",
            (
                "1. Keep the ATM transaction slip and record the ATM ID, date, and exact timestamp.\n"
                "2. Automated inter-bank switch reconciliation processes typically settle failed ATM debits within 5 business days.\n"
                "3. Regularly check your account statement for an automated credit reversal entry.\n"
                "4. If funds are not restored within the standard settlement period, present your transaction receipt to your branch."
            ),
            "Bank ATM Operations SOP",
            1, 1, now_iso, now_iso
        ),
        (
            dept_map.get("Retail Banking Team", 3),
            "Account Maintenance or Minimum Balance Charge Review",
            "Bank Accounts and Services",
            "minimum balance, average quarterly balance, service charge, penalty, maintenance fee",
            (
                "1. Review your account agreement for the required Average Monthly/Quarterly Balance (AMB/AQB) threshold.\n"
                "2. Verify whether balance shortfall notifications were delivered to your registered mobile or email.\n"
                "3. If balance notification was missing, submit an account fee review request at your home branch."
            ),
            "Standard Retail Banking Terms & Conditions",
            1, 1, now_iso, now_iso
        ),
        (
            dept_map.get("Card Disputes Team", 1),
            "Unrecognized or Suspicious Credit Card Transaction",
            "Credit Card Services",
            "fraud, unauthorized, suspicious, card stolen, unknown transaction, otp, scam, hacked, galat charge, transaction, dispute, credit card, card, bill, anadhikrit, jaanch, nahi kiya, charge, charges, बिल, गलत चार्ज",
            (
                "1. Immediately block or freeze your credit card through your official mobile banking app or customer hotline.\n"
                "2. Review your recent transactions to confirm if this was an unfamiliar international charge or recurring subscription.\n"
                "3. File an official dispute claim with your bank's 24/7 card services desk within 3 days.\n"
                "4. Case flagged for urgent investigation: human officer escalation is recommended."
            ),
            "Card Safety & Customer Liability Guidelines",
            0, 1, now_iso, now_iso  # can_self_resolve = False
        ),
        (
            dept_map.get("Card Disputes Team", 1),
            "Credit Card Annual Fee or Membership Charge Dispute",
            "Credit Card Services",
            "annual fee, renewal fee, membership charge, joining fee, fee waiver, reward fee",
            (
                "1. Check your card cardholder terms to see if an annual fee waiver spend threshold applies.\n"
                "2. Review your total annual spends across the prior 12 billing cycles.\n"
                "3. Submit a service request through online banking asking for fee waiver verification or card variant review."
            ),
            "Cardholder Agreement Terms",
            1, 1, now_iso, now_iso
        ),
        (
            dept_map.get("Credit Bureau Liaison Team", 5),
            "Inaccurate Account or Balance Status on Credit Bureau Report",
            "Credit Reporting",
            "cibil, experian, score, credit report, wrong overdue, settled, written off, loan wrong",
            (
                "1. Obtain your recent Credit Information Report (CIR) and note the specific Account Number in dispute.\n"
                "2. Ensure you have your official No Dues Certificate (NDC) or closure letter from the issuing lender.\n"
                "3. Raise a dispute through the official credit bureau portal with your NDC attached.\n"
                "4. Lenders submit updated portfolio files to credit bureaus on a monthly cycle (approximately every 30 days)."
            ),
            "Credit Information Companies Framework",
            1, 1, now_iso, now_iso
        ),
        (
            dept_map.get("Loan Servicing Team", 2),
            "Loan Closure Documentation & NOC Dispatch Delay",
            "Loans",
            "noc, no objection, property documents, loan closure, deeds, title documents, mortgage",
            (
                "1. Confirm that all outstanding principal, interest, and processing fees have been cleared.\n"
                "2. Obtain your final payment confirmation and closure acknowledgment letter.\n"
                "3. Request the document tracking or consignment number from your loan operations center.\n"
                "4. If unaddressed beyond standard turnaround, escalate to the central loan servicing desk."
            ),
            "Loan Servicing & Document Return Procedures",
            1, 1, now_iso, now_iso
        ),
        (
            dept_map.get("Collections Compliance Team", 4),
            "Inquiry on Recovery Communication Guidelines & Timings",
            "Debt Collection",
            "agent, harassment, recovery, calling, recovery agent, rude, threats, timing",
            (
                "1. Request the representative's official name, employee ID, and authorized recovery agency name.\n"
                "2. Regulatory fair practice guidelines stipulate debt communication should only occur during daytime hours.\n"
                "3. Request an official, updated statement of dues directly from the bank.\n"
                "4. Case flagged for urgent investigation: human officer escalation is recommended."
            ),
            "Fair Practices Code for Lenders",
            0, 1, now_iso, now_iso  # can_self_resolve = False
        )
    ]

    cur.executemany("""
    INSERT INTO knowledge_base_articles (
        department_id, title, category, keywords, guidance_steps, 
        regulatory_reference, can_self_resolve, is_active, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_articles)
    print(f"  [OK] Successfully seeded {len(sample_articles)} knowledge base articles.")

conn.commit()
conn.close()
print("\n>>> Migration completed successfully! Database is ready for GrievanceIQ <<<")
