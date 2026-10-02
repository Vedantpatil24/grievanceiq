from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import User
import bcrypt

engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)
session = Session()

admin_email = "admin@grievanceiq.com"
admin_password = "admin123"  # change this before your real demo

existing = session.query(User).filter_by(email=admin_email).first()
if existing:
    print("Admin already exists.")
else:
    hashed = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt())
    admin = User(name="Admin", email=admin_email, password_hash=hashed.decode("utf-8"), role="admin")
    session.add(admin)
    session.commit()
    print(f"Admin created: {admin_email} / {admin_password}")

session.close()