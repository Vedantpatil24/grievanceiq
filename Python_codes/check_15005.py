import sqlite3

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

c.execute("SELECT token, company_id, reference_id, transaction_date, branch, amount, service_type FROM complaints WHERE token = 'GRV-2026-15005'")
row = c.fetchone()
print("GRV-2026-15005 DB record:", row)

c.execute("SELECT token, company_id, reference_id, transaction_date, branch, amount, service_type FROM complaints ORDER BY id DESC LIMIT 5")
print("\nLast 5 complaints in DB:")
for r in c.fetchall():
    print(r)

conn.close()
