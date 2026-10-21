"""
verify_phase1.py - Validation script for Phase 1 Database Integrity
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grievanceiq.db")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

tables_to_check = [
    "companies", "departments", "categories", "users", "complaints", 
    "status_history", "predictions", "tickets", "feedback", 
    "knowledge_base_articles", "complaint_messages", "notifications", 
    "assignment_history", "escalation_history", "audit_logs"
]

print("=== GRIEVANCEIQ PHASE 1 DATABASE INTEGRITY CHECK ===")
all_ok = True
for table in tables_to_check:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  [PASS] Table: {table:<25} | Row count: {count}")
    except sqlite3.OperationalError as e:
        print(f"  [FAIL] Table: {table:<25} | Error: {e}")
        all_ok = False

# Check newly added columns on complaints
cur.execute("PRAGMA table_info(complaints)")
cols = [r[1] for r in cur.fetchall()]
required_cols = [
    "token", "resolution_mode", "matched_article_id", "bot_confidence",
    "escalation_level", "current_assigned_officer_id", "escalated_at",
    "sla_deadline", "sla_breached", "reopen_count", "can_reopen_until"
]
missing = [c for c in required_cols if c not in cols]

print("\n=== COMPLAINTS NEW FIELDS CHECK ===")
if not missing:
    print("  [PASS] All approved fields are present on the complaints table.")
else:
    print(f"  [FAIL] Missing columns on complaints: {missing}")
    all_ok = False

conn.close()

if all_ok:
    print("\n>>> Phase 1 database verification SUCCESSFUL! <<<")
else:
    print("\n>>> Verification encountered issues. Review errors above. <<<")
