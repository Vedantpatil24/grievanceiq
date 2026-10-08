import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Base, Department, Company, User, Complaint, StatusHistory, PredictionsLog, Feedback

with open(r"G:\Mini_project\db_url.txt", "r") as f:
    postgres_url = f.read().strip()

if postgres_url.startswith("postgres://"):
    postgres_url = postgres_url.replace("postgres://", "postgresql+pg8000://", 1)
elif postgres_url.startswith("postgresql://"):
    postgres_url = postgres_url.replace("postgresql://", "postgresql+pg8000://", 1)

sqlite_engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SqliteSession()

# pool_pre_ping checks the connection is alive before each use, reconnecting if not
postgres_engine = create_engine(postgres_url, pool_pre_ping=True, pool_recycle=280)
Base.metadata.create_all(postgres_engine)
PostgresSession = sessionmaker(bind=postgres_engine)
postgres_session = PostgresSession()

print("Clearing any existing data in Postgres...")
for model in [Feedback, PredictionsLog, StatusHistory, Complaint, User, Company, Department]:
    postgres_session.query(model).delete()
postgres_session.commit()
print("Cleared.\n")

def copy_table(model, name, chunk_size=100, max_retries=5):
    existing_ids = {row.id for row in postgres_session.query(model.id).all()}
    rows = sqlite_session.query(model).all()
    rows = [r for r in rows if r.id not in existing_ids]
    print(f"{name}: {len(existing_ids)} already present, {len(rows)} remaining to copy...")
    if not rows:
        print(f"Done: {name} (nothing to do)")
        return
    data_list = [
        {c.name: getattr(row, c.name) for c in model.__table__.columns}
        for row in rows
    ]
    for i in range(0, len(data_list), chunk_size):
        chunk = data_list[i:i + chunk_size]
        for attempt in range(1, max_retries + 1):
            try:
                postgres_session.bulk_insert_mappings(model, chunk)
                postgres_session.commit()
                break
            except Exception as e:
                postgres_session.rollback()
                print(f"  Retry {attempt}/{max_retries} for a chunk ({type(e).__name__})")
                time.sleep(2 * attempt)
                if attempt == max_retries:
                    raise
        print(f"  {min(i + chunk_size, len(data_list))}/{len(data_list)} rows committed")
    print(f"Done: {name}")

copy_table(Department, "departments")
copy_table(Company, "companies")
copy_table(User, "users")
copy_table(Complaint, "complaints")
copy_table(StatusHistory, "status_history")
copy_table(PredictionsLog, "predictions_log")
copy_table(Feedback, "feedback")

sqlite_session.close()
postgres_session.close()
print("\nMigration complete!")