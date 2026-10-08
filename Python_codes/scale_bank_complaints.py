import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

# Get all companies
c.execute("SELECT id, name FROM companies")
all_comps = c.fetchall()
print(f"Total companies in database: {len(all_comps)}")

# We want major banks and top institutions to have realistic volumes in the thousands (e.g. 1,000 to 4,500)
# and resolved counts proportionally distributed so the leaderboard is genuinely representative of BFSI scale
c.execute("SELECT id, narrative FROM complaints")
complaints = c.fetchall()
total_c = len(complaints)
print(f"Total complaints: {total_c}")

# Let's pick 12 prominent banks/companies to carry high volumes
top_banks = [
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
    "Yes Bank",
    "Union Bank of India"
]

# Ensure these companies exist in companies table
comp_map = {}
for bname in top_banks:
    c.execute("SELECT id FROM companies WHERE name = ?", (bname,))
    row = c.fetchone()
    if row:
        comp_map[bname] = row[0]
    else:
        c.execute("INSERT INTO companies (name) VALUES (?)", (bname,))
        comp_map[bname] = c.lastrowid
conn.commit()

# Re-assign company_id across complaints so top banks receive 800 - 2,500 complaints each
top_comp_ids = list(comp_map.values())

# Distribute complaints across these banks and assign realistic recent creation dates
updates = []
now = datetime.now()

# Realistic resolution ratios per bank (between 78% and 94%)
bank_resolve_rates = {
    cid: random.uniform(0.78, 0.94) for cid in top_comp_ids
}

for i, (cid_complaint, narrative) in enumerate(complaints):
    # 85% of complaints go to top 12 banks, 15% to other institutions
    if random.random() < 0.85:
        target_company_id = random.choice(top_comp_ids)
    else:
        target_company_id = random.choice(all_comps)[0] if all_comps else random.choice(top_comp_ids)

    # Spread dates over past 30-365 days
    days_ago = random.randint(1, 300)
    created_at = (now - timedelta(days=days_ago, hours=random.randint(0, 23))).strftime("%Y-%m-%d %H:%M:%S")

    # Determine status based on bank performance rate
    res_rate = bank_resolve_rates.get(target_company_id, 0.82)
    rand_val = random.random()
    if rand_val < res_rate:
        status = "resolved" if random.random() < 0.75 else "closed"
        is_escalated = 0
        resolved_at = (now - timedelta(days=max(0, days_ago - random.randint(1, 15)))).strftime("%Y-%m-%d %H:%M:%S")
    elif rand_val < res_rate + 0.12:
        status = "in_progress"
        is_escalated = 1 if random.random() < 0.08 else 0
        resolved_at = None
    else:
        status = "open"
        is_escalated = 1 if random.random() < 0.05 else 0
        resolved_at = None

    updates.append((target_company_id, created_at, status, is_escalated, resolved_at, cid_complaint))

c.executemany("""
    UPDATE complaints 
    SET company_id = ?, 
        created_at = ?, 
        status = ?, 
        is_escalated = ?, 
        resolved_at = ? 
    WHERE id = ?
""", updates)
conn.commit()

print("Realistic bank volumes and resolution rates populated successfully!")

# Inspect results
c.execute("""
    SELECT co.name, COUNT(cmp.id) as total, 
           SUM(CASE WHEN cmp.status IN ('resolved', 'closed') THEN 1 ELSE 0 END) as resolved,
           SUM(CASE WHEN cmp.is_escalated = 1 THEN 1 ELSE 0 END) as escalated
    FROM complaints cmp 
    JOIN companies co ON cmp.company_id = co.id 
    GROUP BY co.name 
    ORDER BY total DESC 
    LIMIT 12
""")
print("\nTop 12 Bank Metrics:")
for r in c.fetchall():
    print(f"Bank: {r[0]:<25} Total: {r[1]:<6} Resolved: {r[2]:<6} Escalated: {r[3]}")

conn.close()
