from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Complaint

engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)
session = Session()

fixed = session.query(Complaint).filter(
    Complaint.status != "resolved",
    Complaint.resolved_at.isnot(None)
).update({"resolved_at": None}, synchronize_session=False)

session.commit()
print(f"Cleared resolved_at on {fixed} complaints.")
session.close()