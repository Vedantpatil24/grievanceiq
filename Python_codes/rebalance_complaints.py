import sqlite3

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

# Get department IDs for the 5 target departments: 6 (Digital/UPI), 7 (Loans), 8 (Cards), 9 (Accounts), 10 (Fraud)
c.execute("SELECT id, name FROM departments WHERE id IN (6, 7, 8, 9, 10)")
depts = dict(c.fetchall())
print("Target departments:", depts)

# Re-distribute the 15,004 complaints across all 5 departments evenly so each department has real complaints
# Dept 6 (Digital/UPI): ~2,500
# Dept 7 (Loans & Advances): ~3,500
# Dept 8 (Cards & ATM): ~3,000
# Dept 9 (Account & Branch): ~3,500
# Dept 10 (Fraud & Risk): ~2,504
c.execute("SELECT id, narrative FROM complaints ORDER BY id ASC")
all_complaints = c.fetchall()
total_c = len(all_complaints)
print(f"Total complaints to balance: {total_c}")

# Distribute by keywords or round-robin to ensure each dept gets appropriate complaints
dept_ids = [6, 7, 8, 9, 10]
dept_workers = {
    6: ['BOT-DIG-01', 'BOT-DIG-02', 'BOT-DIG-03', 'BOT-DIG-04', 'BOT-DIG-05'],
    7: ['BOT-LND-01', 'BOT-LND-02', 'BOT-LND-03', 'BOT-LND-04', 'BOT-LND-05'],
    8: ['BOT-CRD-01', 'BOT-CRD-02', 'BOT-CRD-03', 'BOT-CRD-04', 'BOT-CRD-05'],
    9: ['BOT-ACC-01', 'BOT-ACC-02', 'BOT-ACC-03', 'BOT-ACC-04', 'BOT-ACC-05'],
    10: ['BOT-FRD-01', 'BOT-FRD-02', 'BOT-FRD-03', 'BOT-FRD-04', 'BOT-FRD-05'],
}

worker_idx = {d: 0 for d in dept_ids}

updates = []
for i, (cid, narrative) in enumerate(all_complaints):
    # Determine department
    text = (narrative or "").lower()
    if any(k in text for k in ['fraud', 'scam', 'unauthorized', 'stolen', 'phishing', 'hacked']):
        d_id = 10
    elif any(k in text for k in ['upi', 'paytm', 'gpay', 'phonepe', 'net banking', 'online transfer', 'digital']):
        d_id = 6
    elif any(k in text for k in ['card', 'atm', 'debit', 'credit card', 'pos', 'cvv']):
        d_id = 8
    elif any(k in text for k in ['loan', 'emi', 'mortgage', 'interest', 'cibil', 'credit score']):
        d_id = 7
    elif any(k in text for k in ['account', 'cheque', 'deposit', 'branch', 'balance', 'savings']):
        d_id = 9
    else:
        # Round robin across all 5 departments
        d_id = dept_ids[i % len(dept_ids)]

    # Assign to one of the 5 officers of that department evenly
    w_list = dept_workers[d_id]
    w_id = w_list[worker_idx[d_id] % len(w_list)]
    worker_idx[d_id] += 1

    updates.append((d_id, w_id, cid))

c.executemany("UPDATE complaints SET department_id = ?, assigned_worker_id = ? WHERE id = ?", updates)
conn.commit()

print("Rebalance completed!")
c.execute("SELECT department_id, COUNT(*) FROM complaints GROUP BY department_id")
for r in c.fetchall():
    print(f"Dept {r[0]} ({depts.get(r[0], 'Unknown')}): {r[1]} complaints")

print("\nWorker assignment sample:")
c.execute("SELECT assigned_worker_id, COUNT(*) FROM complaints GROUP BY assigned_worker_id")
for r in c.fetchall():
    print(r)

conn.close()
