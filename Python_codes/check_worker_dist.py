import sqlite3

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

c.execute("SELECT assigned_worker_id, COUNT(*) FROM complaints GROUP BY assigned_worker_id")
rows = c.fetchall()
print("Worker assignment distribution:")
for r in rows:
    print(r)

c.execute("SELECT worker_id, name, employee_id, department_id FROM workers")
workers = c.fetchall()
print("\nWorkers in DB:")
for w in workers:
    print(w)

conn.close()
