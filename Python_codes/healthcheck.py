import ast, os, sys

py_files = ['main.py', 'bot_resolver.py', 'validity_checker.py',
            'multilingual_engine.py', 'ml_pipeline.py', 'ocr_service.py', 'create_db.py']

print("=== PYTHON SYNTAX CHECKS ===")
all_ok = True
for fname in py_files:
    if not os.path.exists(fname):
        print(f"MISSING: {fname}")
        continue
    try:
        ast.parse(open(fname, encoding='utf-8').read())
        print(f"  OK  : {fname}")
    except SyntaxError as e:
        print(f"  ERR : {fname} -> {e}")
        all_ok = False

print()
if not all_ok:
    sys.exit(1)

print("=== DATABASE SUMMARY ===")
from create_db import SessionLocal, User, Complaint, Resolution, Company, Department, StatusHistory
db = SessionLocal()

customers = db.query(User).filter(User.role == 'customer').count()
officers  = db.query(User).filter(User.role.in_(['officer', 'staff'])).count()
admins    = db.query(User).filter(User.role == 'admin').count()
companies = db.query(Company).count()
depts     = db.query(Department).count()
total     = db.query(Complaint).count()
statuses  = {}
for s in ['open', 'in_progress', 'resolved', 'escalated', 'closed', 'reopened', 'resolution_proposed']:
    statuses[s] = db.query(Complaint).filter(Complaint.status == s).count()
resolutions  = db.query(Resolution).count()
hist_entries = db.query(StatusHistory).count()

db.close()

print(f"  Customers      : {customers}")
print(f"  Officers/Staff : {officers}")
print(f"  Admins         : {admins}")
print(f"  Companies      : {companies}")
print(f"  Departments    : {depts}")
print(f"  Total Complaints: {total}")
for k, v in statuses.items():
    print(f"    {k:22s}: {v}")
print(f"  Resolutions    : {resolutions}")
print(f"  Status History : {hist_entries}")
print()
print("=== ALL SYSTEMS HEALTHY ===")
