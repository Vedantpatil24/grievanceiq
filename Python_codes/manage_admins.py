from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import User
import bcrypt

engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)
session = Session()

# --- 1. Remove the test admin account ---
old_admin = session.query(User).filter_by(email="admin@grievanceiq.com").first()
if old_admin:
    session.delete(old_admin)
    session.commit()
    print("Removed test admin account.")
else:
    print("Test admin account not found (already removed?).")

# --- 2. Add your real admin accounts ---
new_admins = [
    {"name": "Your Name", "email": "vedant.patil24@spit.ac.in", "password": "vedant@123"},
    {"name": "Teammate 1", "email": "mayuri.tarde24@spit.ac.in", "password": "mayuri@123"},
    {"name": "Teammate 2", "email": "ashmit.patil24@spit.ac.in", "password": "ashmit@123"},
]

for admin in new_admins:
    existing = session.query(User).filter_by(email=admin["email"]).first()
    if existing:
        print(f"Already exists: {admin['email']}")
        continue
    hashed = bcrypt.hashpw(admin["password"].encode("utf-8"), bcrypt.gensalt())
    user = User(name=admin["name"], email=admin["email"], password_hash=hashed.decode("utf-8"), role="admin")
    session.add(user)
    print(f"Created admin: {admin['email']} / {admin['password']}")

session.commit()
session.close()