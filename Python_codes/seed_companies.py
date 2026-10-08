from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Company

engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)
session = Session()

companies = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "Punjab National Bank", "Bank of Baroda"]

for name in companies:
    if not session.query(Company).filter_by(name=name).first():
        session.add(Company(name=name))

session.commit()
print("Companies seeded.")
session.close()