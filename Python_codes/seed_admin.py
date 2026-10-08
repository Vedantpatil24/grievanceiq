import bcrypt
import sqlite3

conn = sqlite3.connect('../Dataset/grievanceiq.db')
c = conn.cursor()

# Check or insert default admin: admin@grievanceiq.in / admin123
admin_email = "admin@grievanceiq.in"
hashed = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

c.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
exists = c.fetchone()
if exists:
    c.execute("UPDATE users SET password_hash = ?, role = 'admin' WHERE email = ?", (hashed, admin_email))
else:
    c.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('System Administrator', ?, ?, 'admin')", (admin_email, hashed))

conn.commit()
print("admin@grievanceiq.in password set to 'admin123' successfully!")
conn.close()
