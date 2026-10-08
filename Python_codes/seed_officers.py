import sqlite3
import bcrypt

conn = sqlite3.connect(r"G:\Mini_project\Dataset\grievanceiq.db")
c = conn.cursor()

real_names = [
    ('Pooja Sharma', 'EMP-DIG-101', 'pooja.sharma@grievanceiq.in', '+91 98201 11234'),
    ('Rahul Verma', 'EMP-DIG-102', 'rahul.verma@grievanceiq.in', '+91 98201 11235'),
    ('Ananya Iyer', 'EMP-DIG-103', 'ananya.iyer@grievanceiq.in', '+91 98201 11236'),
    ('Karthik Nair', 'EMP-DIG-104', 'karthik.nair@grievanceiq.in', '+91 98201 11237'),
    ('Simran Kaur', 'EMP-DIG-105', 'simran.kaur@grievanceiq.in', '+91 98201 11238'),
    
    ('Vikram Malhotra', 'EMP-LND-201', 'vikram.m@grievanceiq.in', '+91 98202 22341'),
    ('Meera Deshmukh', 'EMP-LND-202', 'meera.d@grievanceiq.in', '+91 98202 22342'),
    ('Rohan Kulkarni', 'EMP-LND-203', 'rohan.k@grievanceiq.in', '+91 98202 22343'),
    ('Tanvi Joshi', 'EMP-LND-204', 'tanvi.j@grievanceiq.in', '+91 98202 22344'),
    ('Aditya Sen', 'EMP-LND-205', 'aditya.s@grievanceiq.in', '+91 98202 22345'),
    
    ('Neha Reddy', 'EMP-CRD-301', 'neha.r@grievanceiq.in', '+91 98203 33451'),
    ('Siddharth Menon', 'EMP-CRD-302', 'siddharth.m@grievanceiq.in', '+91 98203 33452'),
    ('Deepika Pillai', 'EMP-CRD-303', 'deepika.p@grievanceiq.in', '+91 98203 33453'),
    ('Gaurav Mehta', 'EMP-CRD-304', 'gaurav.m@grievanceiq.in', '+91 98203 33454'),
    ('Shreya Bose', 'EMP-CRD-305', 'shreya.b@grievanceiq.in', '+91 98203 33455'),
    
    ('Amitabh Saxena', 'EMP-ACC-401', 'amitabh.s@grievanceiq.in', '+91 98204 44561'),
    ('Sunita Rao', 'EMP-ACC-402', 'sunita.r@grievanceiq.in', '+91 98204 44562'),
    ('Manoj Bhattacharya', 'EMP-ACC-403', 'manoj.b@grievanceiq.in', '+91 98204 44563'),
    ('Priyanka Das', 'EMP-ACC-404', 'priyanka.d@grievanceiq.in', '+91 98204 44564'),
    ('Suresh Hegde', 'EMP-ACC-405', 'suresh.h@grievanceiq.in', '+91 98204 44565'),
    
    ('Arjun Kapoor', 'EMP-FRD-501', 'arjun.k@grievanceiq.in', '+91 98205 55671'),
    ('Kavita Krishnan', 'EMP-FRD-502', 'kavita.k@grievanceiq.in', '+91 98205 55672'),
    ('Devendra Rathore', 'EMP-FRD-503', 'devendra.r@grievanceiq.in', '+91 98205 55673'),
    ('Sneha Chatterjee', 'EMP-FRD-504', 'sneha.c@grievanceiq.in', '+91 98205 55674'),
    ('Abhishek Pandey', 'EMP-FRD-505', 'abhishek.p@grievanceiq.in', '+91 98205 55675')
]

default_hash = bcrypt.hashpw(b"emp123", bcrypt.gensalt()).decode("utf-8")

workers = c.execute("SELECT id, worker_id FROM workers ORDER BY id ASC").fetchall()
print(f"Total workers: {len(workers)}")

for idx, (w_db_id, w_code) in enumerate(workers):
    if idx < len(real_names):
        name, emp_id, email, phone = real_names[idx]
        c.execute("""
            UPDATE workers 
            SET name = ?, employee_id = ?, email = ?, phone = ?, password_hash = ?
            WHERE id = ?
        """, (name, emp_id, email, phone, default_hash, w_db_id))

# Default priority reasons
c.execute("""
UPDATE complaints 
SET priority_reason = CASE 
    WHEN priority = 'High' THEN 'Assigned High Urgency: Detection of unauthorized transactions / fraud threat requires mandatory 24-hour statutory redressal.'
    WHEN priority = 'Medium' THEN 'Assigned Medium Urgency: Disputed charges / failed payment settlement requires 7-day inter-bank clearing cycle.'
    ELSE 'Assigned Standard Urgency: General service, branch, or account query managed under standard 30-day resolution timeline.'
END
WHERE priority_reason IS NULL OR priority_reason = ''
""")

conn.commit()
print("Success! Updated 25 officers and seeded priority reasons.")
conn.close()
