import sqlite3

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

c.execute("SELECT department_id, COUNT(*) FROM complaints GROUP BY department_id")
print("Complaints by department_id in DB:")
for r in c.fetchall():
    print(r)

c.execute("SELECT id, name FROM departments")
print("\nDepartments in DB:")
for d in c.fetchall():
    print(d)

conn.close()
