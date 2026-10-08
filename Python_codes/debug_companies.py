from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Complaint, Company

engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)
session = Session()

total_companies = session.query(Company).count()
print(f"Total companies in 'companies' table: {total_companies}")

total_complaints_with_company = session.query(Complaint).filter(Complaint.company_id.isnot(None)).count()
print(f"Complaints that have a company_id set: {total_complaints_with_company}")

# Show first 10 companies and how many complaints each has
companies = session.query(Company).limit(10).all()
for c in companies:
    count = session.query(Complaint).filter(Complaint.company_id == c.id).count()
    print(f"Company id={c.id}, name='{c.name}', complaint_count={count}")