import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect(r"G:\Mini_project\Dataset\grievanceiq.db")
c = conn.cursor()

# Map old department IDs to the 5 Indian target departments
# 1 ('Credit Reporting') -> 9 ('Account & Branch Operations')
# 2 ('Debt Collection') -> 7 ('Loans & Advances')
# 3 ('Loans') -> 7 ('Loans & Advances')
# 4 ('Bank Accounts and Services') -> 9 ('Account & Branch Operations')
# 5 ('Credit Card Services') -> 8 ('Cards & ATM Services')
dept_remap = {
    1: 9, # Account & Branch Operations
    2: 7, # Loans & Advances
    3: 7, # Loans & Advances
    4: 9, # Account & Branch Operations
    5: 8, # Cards & ATM Services
}

for old_id, new_id in dept_remap.items():
    c.execute("UPDATE complaints SET department_id = ? WHERE department_id = ?", (new_id, old_id))

conn.commit()

# Now assign bot workers fairly among each department
# Each department has 5 bots:
dept_workers = {
    6: ['BOT-DIG-01', 'BOT-DIG-02', 'BOT-DIG-03', 'BOT-DIG-04', 'BOT-DIG-05'],
    7: ['BOT-LND-01', 'BOT-LND-02', 'BOT-LND-03', 'BOT-LND-04', 'BOT-LND-05'],
    8: ['BOT-CRD-01', 'BOT-CRD-02', 'BOT-CRD-03', 'BOT-CRD-04', 'BOT-CRD-05'],
    9: ['BOT-ACC-01', 'BOT-ACC-02', 'BOT-ACC-03', 'BOT-ACC-04', 'BOT-ACC-05'],
    10: ['BOT-FRD-01', 'BOT-FRD-02', 'BOT-FRD-03', 'BOT-FRD-04', 'BOT-FRD-05']
}

for dept_id, workers in dept_workers.items():
    complaint_ids = [r[0] for r in c.execute("SELECT id FROM complaints WHERE department_id = ? ORDER BY id", (dept_id,)).fetchall()]
    print(f"Assigning {len(complaint_ids)} complaints in Dept {dept_id} across {len(workers)} bots...")
    for idx, cid in enumerate(complaint_ids):
        w_id = workers[idx % len(workers)]
        c.execute("UPDATE complaints SET assigned_worker_id = ? WHERE id = ?", (w_id, cid))

# Set SLA deadlines & escalations for existing records if null
now = datetime.now()
c.execute("""
    UPDATE complaints 
    SET due_date = datetime(created_at, '+24 hours')
    WHERE priority = 'High' AND (due_date IS NULL OR due_date = '')
""")
c.execute("""
    UPDATE complaints 
    SET due_date = datetime(created_at, '+7 days')
    WHERE priority = 'Medium' AND (due_date IS NULL OR due_date = '')
""")
c.execute("""
    UPDATE complaints 
    SET due_date = datetime(created_at, '+30 days')
    WHERE (priority = 'Low' OR priority IS NULL) AND (due_date IS NULL OR due_date = '')
""")

# Mark overdue open complaints as escalated
c.execute("""
    UPDATE complaints 
    SET is_escalated = 1 
    WHERE status IN ('open', 'in_progress') AND due_date < datetime('now')
""")

conn.commit()

# Verify counts per worker
counts = c.execute("SELECT assigned_worker_id, COUNT(*) FROM complaints GROUP BY assigned_worker_id LIMIT 10").fetchall()
print("Sample worker assignments:", counts)
print("Total assigned complaints:", c.execute("SELECT COUNT(*) FROM complaints WHERE assigned_worker_id IS NOT NULL").fetchone()[0])

conn.close()
