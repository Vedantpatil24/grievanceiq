import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Department, Company, Complaint, Base

# Connect to your existing database
engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)
session = Session()

# Load the CSV
df = pd.read_csv(r"G:\Mini_project\Dataset\grievanceiq_15k_priority.csv")
print("Loaded", len(df), "rows")

# Step 1: Insert unique departments (from product_5 column)
departments = df["product_5"].unique()
dept_map = {}
for dept_name in departments:
    dept = Department(name=dept_name)
    session.add(dept)
    session.flush()  # gets the auto-generated id immediately
    dept_map[dept_name] = dept.id
session.commit()
print("Inserted", len(dept_map), "departments")

# Step 2: Insert unique companies
companies = df["Company"].dropna().unique()
company_map = {}
for i, comp_name in enumerate(companies):
    comp = Company(name=comp_name)
    session.add(comp)
    session.flush()
    company_map[comp_name] = comp.id
session.commit()
print("Inserted", len(company_map), "companies")

# Step 3: Insert complaints with generated tokens
count = 0
for idx, row in df.iterrows():
    token = f"GRV-2026-{idx+1:05d}"  # e.g. GRV-2026-00001

    dept_id = dept_map.get(row["product_5"])
    comp_id = company_map.get(row["Company"]) if pd.notna(row["Company"]) else None

    complaint = Complaint(
        token=token,
        narrative=row["narrative"],
        narrative_clean=row["narrative_clean"],
        department_id=dept_id,
        company_id=comp_id,
        priority=row["priority"],
        status="open"
    )
    session.add(complaint)
    count += 1

    if count % 1000 == 0:
        session.commit()  # commit in batches so it doesn't hold everything in memory
        print("Inserted", count, "complaints so far...")

session.commit()  # final commit for remaining rows
print("Done. Total complaints inserted:", count)

session.close()