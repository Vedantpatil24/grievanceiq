"""
upgrade_phase2_db.py - Upgrades database schema to support:
1. Resolutions with proof and confirmation status
2. Investigation notes
3. Similar complaints index & duplicate tracking
4. Evidence verification fields on complaints
5. Customer linking on complaints (customer_id)
6. Sub-category field
"""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grievanceiq.db")
print("Connecting to:", db_path)
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Add missing columns to complaints table
cur.execute("PRAGMA table_info(complaints)")
existing_cols = [r[1] for r in cur.fetchall()]

new_complaint_cols = [
    ("customer_id", "INTEGER REFERENCES users(user_id)"),
    ("sub_category", "TEXT"),
    ("evidence_status", "TEXT DEFAULT 'PENDING'"),  # PENDING, VERIFIED, REJECTED
    ("evidence_verified_by", "INTEGER REFERENCES users(user_id)"),
    ("evidence_verified_at", "DATETIME"),
    ("evidence_rejection_reason", "TEXT")
]

for col_name, col_type in new_complaint_cols:
    if col_name not in existing_cols:
        cur.execute(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_type};")
        print(f"[+] Added to complaints: {col_name}")
    else:
        print(f"[.] Exists in complaints: {col_name}")

# 2. Create resolutions table
cur.execute("""
CREATE TABLE IF NOT EXISTS resolutions (
    resolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    worker_id INTEGER NOT NULL REFERENCES users(user_id),
    resolution_details TEXT NOT NULL,
    resolution_type TEXT NOT NULL,
    transaction_reference TEXT,
    resolved_amount REAL,
    resolution_proof_path TEXT,
    resolution_date DATETIME NOT NULL,
    customer_confirmation_status TEXT DEFAULT 'PENDING', -- PENDING, ACCEPTED, REJECTED
    customer_feedback TEXT,
    customer_action_date DATETIME
);
""")
print("[OK] Table verified: resolutions")

# 3. Create investigation_notes table
cur.execute("""
CREATE TABLE IF NOT EXISTS investigation_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    worker_id INTEGER NOT NULL REFERENCES users(user_id),
    note_text TEXT NOT NULL,
    created_at DATETIME NOT NULL
);
""")
print("[OK] Table verified: investigation_notes")

# 4. Create similar_complaints table (for SBERT semantic similarity & duplicate tracking)
cur.execute("""
CREATE TABLE IF NOT EXISTS similar_complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    matched_complaint_id INTEGER NOT NULL REFERENCES complaints(complaint_id),
    similarity_score REAL NOT NULL,
    classification_tag TEXT NOT NULL, -- DUPLICATE, SIMILAR, RELATED
    detected_at DATETIME NOT NULL
);
""")
print("[OK] Table verified: similar_complaints")

conn.commit()
conn.close()
print("\nPhase 2 Schema Upgrade Complete.")
