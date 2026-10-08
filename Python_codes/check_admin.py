import sqlite3

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

c.execute("SELECT id, name, email, role FROM users WHERE role = 'admin'")
admins = c.fetchall()
print("Admins in DB:", admins)

conn.close()
