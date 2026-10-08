import sqlite3

conn = sqlite3.connect(r"G:\Mini_project\Dataset\grievanceiq.db")
c = conn.cursor()

# Ensure stage column in complaints
cols = [r[1] for r in c.execute("PRAGMA table_info(complaints)").fetchall()]
if "stage" not in cols:
    c.execute("ALTER TABLE complaints ADD COLUMN stage TEXT DEFAULT 'Submitted'")
    print("Added stage column")

# Seed the 5 departments
target_depts = [
    "Digital & UPI Banking",
    "Loans & Advances",
    "Cards & ATM Services",
    "Account & Branch Operations",
    "Fraud & Risk Management"
]

dept_id_map = {}
for dname in target_depts:
    c.execute("INSERT OR IGNORE INTO departments (name) VALUES (?)", (dname,))
    conn.commit()
    dept_id = c.execute("SELECT id FROM departments WHERE name = ?", (dname,)).fetchone()[0]
    dept_id_map[dname] = dept_id

# Seed 5 bot workers per department (25 total)
dept_prefixes = {
    "Digital & UPI Banking": ("BOT-DIG", "Digital Bot"),
    "Loans & Advances": ("BOT-LND", "Loan Bot"),
    "Cards & ATM Services": ("BOT-CRD", "Card Bot"),
    "Account & Branch Operations": ("BOT-ACC", "Branch Bot"),
    "Fraud & Risk Management": ("BOT-FRD", "Fraud Bot")
}

for dept_name, dept_id in dept_id_map.items():
    prefix, bot_title = dept_prefixes[dept_name]
    for i in range(1, 6):
        w_id = f"{prefix}-{i:02d}"
        w_name = f"{bot_title} #{i}"
        c.execute("""
            INSERT OR IGNORE INTO workers (worker_id, name, department_id, is_active)
            VALUES (?, ?, ?, 1)
        """, (w_id, w_name, dept_id))

# Seed Indian banks into companies table
indian_banks = [
    "State Bank of India",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Kotak Mahindra Bank",
    "Punjab National Bank",
    "Bank of Baroda",
    "Canara Bank",
    "IndusInd Bank",
    "IDFC FIRST Bank",
    "Federal Bank",
    "Yes Bank"
]

for b in indian_banks:
    c.execute("INSERT OR IGNORE INTO companies (name) VALUES (?)", (b,))

conn.commit()

# Report counts
w_count = c.execute("SELECT COUNT(*) FROM workers").fetchone()[0]
d_count = c.execute("SELECT COUNT(*) FROM departments").fetchone()[0]
b_count = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]

print(f"Database setup verified:\n- Departments: {d_count}\n- Bot Workers: {w_count} (5 per target dept)\n- Companies: {b_count}")

workers_sample = c.execute("SELECT worker_id, name, department_id FROM workers LIMIT 10").fetchall()
print("Sample workers:", workers_sample)
conn.close()
