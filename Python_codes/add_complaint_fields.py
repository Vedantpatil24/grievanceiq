from sqlalchemy import create_engine, text

engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")

new_columns = [
    ("transaction_date", "TEXT"),
    ("reference_id", "TEXT"),
    ("amount", "FLOAT"),
    ("branch", "TEXT"),
    ("service_type", "TEXT"),
    ("proof_file_path", "TEXT"),
]

with engine.connect() as conn:
    for col_name, col_type in new_columns:
        try:
            conn.execute(text(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_type}"))
            print(f"Added column: {col_name}")
        except Exception as e:
            print(f"Skipped {col_name} (likely already exists): {e}")
    conn.commit()

print("Migration done.")