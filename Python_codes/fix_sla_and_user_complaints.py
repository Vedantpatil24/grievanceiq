import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

# Check complaints without due_date
c.execute("SELECT COUNT(*) FROM complaints WHERE due_date IS NULL OR due_date = ''")
missing_due = c.fetchone()[0]
print(f"Complaints missing due_date: {missing_due}")

# Ensure all complaints have a realistic due_date based on their priority
# High: created_at + 24 hours
# Medium: created_at + 7 days
# Low: created_at + 30 days
c.execute("SELECT id, priority, created_at FROM complaints WHERE due_date IS NULL OR due_date = ''")
rows = c.fetchall()

updates = []
for cid, priority, created_at in rows:
    try:
        base_time = datetime.fromisoformat(created_at) if created_at else datetime.now()
    except Exception:
        base_time = datetime.now()

    if priority == "High":
        due = base_time + timedelta(hours=24)
    elif priority == "Medium":
        due = base_time + timedelta(days=7)
    else:
        due = base_time + timedelta(days=30)

    updates.append((due.strftime("%Y-%m-%d %H:%M:%S"), cid))

if updates:
    c.executemany("UPDATE complaints SET due_date = ? WHERE id = ?", updates)
    conn.commit()
    print(f"Updated {len(updates)} complaints with calculated due_date.")

# Also make sure there are some complaints assigned to user_id = 1 (if user test accounts exist)
c.execute("SELECT id, email FROM users LIMIT 5")
users = c.fetchall()
print("Users in DB:", users)

if users:
    test_user_id = users[0][0]
    # Assign 5 recent complaints to this user so they see history immediately
    c.execute("UPDATE complaints SET user_id = ? WHERE id IN (SELECT id FROM complaints ORDER BY id DESC LIMIT 5)", (test_user_id,))
    conn.commit()
    print(f"Assigned 5 sample grievances to user id {test_user_id} ({users[0][1]}) for testing.")

conn.close()
