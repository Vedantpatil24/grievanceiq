import time
from sqlalchemy import create_engine, text

with open(r"G:\Mini_project\db_url.txt", "r") as f:
    url = f.read().strip()
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql+pg8000://", 1)
elif url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+pg8000://", 1)

print("Connecting...")
start = time.time()
engine = create_engine(url)
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
print(f"Connected in {time.time() - start:.2f} seconds")