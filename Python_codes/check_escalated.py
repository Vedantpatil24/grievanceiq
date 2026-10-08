import sqlite3

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

c.execute("SELECT is_escalated, COUNT(*) FROM complaints GROUP BY is_escalated")
print("Complaints escalated count:", c.fetchall())

c.execute("SELECT status, is_escalated, COUNT(*) FROM complaints GROUP BY status, is_escalated")
print("By status and escalation:", c.fetchall())

conn.close()
