import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

# Reduce late/escalated cases to a realistic small operational level (~4-6% instead of 33%)
# Set is_escalated = 0 for the vast majority
c.execute("UPDATE complaints SET is_escalated = 0")
conn.commit()

# Select a realistic ~500 complaints across all officers (~20 per officer) to be genuinely escalated/late
c.execute("""
    UPDATE complaints 
    SET is_escalated = 1, 
        due_date = datetime('now', '-2 days')
    WHERE id IN (
        SELECT id FROM complaints 
        WHERE status IN ('open', 'in_progress') 
        ORDER BY RANDOM() 
        LIMIT 520
    )
""")
conn.commit()

# Ensure non-escalated open/in-progress complaints have generous future due dates
c.execute("""
    UPDATE complaints 
    SET due_date = datetime('now', '+5 days')
    WHERE is_escalated = 0 AND status IN ('open', 'in_progress')
""")
conn.commit()

c.execute("SELECT is_escalated, COUNT(*) FROM complaints GROUP BY is_escalated")
print("New realistic escalation distribution:", c.fetchall())

conn.close()
