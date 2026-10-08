import random
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Complaint, Department

engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)
session = Session()

departments = session.query(Department).all()

for dept in departments:
    complaints = session.query(Complaint).filter_by(department_id=dept.id).all()
    total = len(complaints)
    if total == 0:
        continue

    random.shuffle(complaints)

    # Give each department its own distinct, randomized split
    open_pct = random.uniform(0.30, 0.65)
    progress_pct = random.uniform(0.15, 0.40)
    # whatever remains goes to resolved
    remaining = max(0.05, 1 - open_pct - progress_pct)
    total_pct = open_pct + progress_pct + remaining
    open_pct, progress_pct, remaining = open_pct / total_pct, progress_pct / total_pct, remaining / total_pct

    n_open = int(total * open_pct)
    n_progress = int(total * progress_pct)
    n_resolved = total - n_open - n_progress

    for c in complaints[:n_open]:
        c.status = "open"
    for c in complaints[n_open:n_open + n_progress]:
        c.status = "in_progress"
    for c in complaints[n_open + n_progress:]:
        c.status = "resolved"
        c.resolved_at = c.created_at + timedelta(days=random.randint(1, 14)) if c.created_at else None

    print(f"{dept.name}: total={total}, open={n_open}, in_progress={n_progress}, resolved={n_resolved}")

session.commit()
session.close()
print("Done.")