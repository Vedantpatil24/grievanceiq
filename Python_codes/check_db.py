import sqlite3

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM complaints WHERE assigned_worker_id IS NOT NULL")
print("assigned complaints:", c.fetchone())

c.execute("SELECT token, assigned_worker_id, due_date, priority, narrative FROM complaints WHERE assigned_worker_id IS NOT NULL LIMIT 3")
for row in c.fetchall():
    print(row)

print("\n=== DEPARTMENTS TABLE ===")
c.execute("PRAGMA table_info(departments)")
for row in c.fetchall():
    print(row)
c.execute("SELECT * FROM departments")
for row in c.fetchall():
    print(row)

print("\n=== WORKER DEPT IDS ===")
c.execute("SELECT worker_id, name, department_id FROM workers")
for row in c.fetchall():
    print(row)

print("\n=== COMPANY COUNTS ===")
c.execute("SELECT co.name, COUNT(cmp.id) FROM complaints cmp JOIN companies co ON cmp.company_id = co.id GROUP BY co.name ORDER BY COUNT(cmp.id) DESC LIMIT 10")
for row in c.fetchall():
    print(row)

print("\n=== USER COMPLAINTS (assigned) ===")
c.execute("SELECT token, user_id, assigned_worker_id, due_date, status FROM complaints WHERE user_id IS NOT NULL LIMIT 5")
for row in c.fetchall():
    print(row)

conn.close()
