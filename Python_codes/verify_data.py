from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from create_db import Complaint, Department, Company

engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)
session = Session()

print("Total complaints:", session.query(Complaint).count())
print()

print("Complaints per department:")
results = session.query(Department.name, func.count(Complaint.id)).join(
    Complaint, Complaint.department_id == Department.id
).group_by(Department.name).all()
for name, count in results:
    print(f"  {name}: {count}")
print()

print("Complaints per priority:")
results = session.query(Complaint.priority, func.count(Complaint.id)).group_by(Complaint.priority).all()
for priority, count in results:
    print(f"  {priority}: {count}")
print()

print("Sample complaint:")
sample = session.query(Complaint).first()
print("  Token:", sample.token)
print("  Priority:", sample.priority)
print("  Status:", sample.status)
print("  Narrative (first 100 chars):", sample.narrative[:100])

session.close()