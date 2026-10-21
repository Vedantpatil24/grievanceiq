"""
seed_bulk_data.py - GrievanceIQ Bulk Data Seeder
Creates 200 realistic Indian customer accounts + 250+ valid complaints for analytics.
Run: python seed_bulk_data.py  (from Python_codes directory)
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from sqlalchemy.orm import Session
from create_db import SessionLocal, User, Company, Department, Complaint, Resolution, StatusHistory, ComplaintMessage

# ============================================================
# REALISTIC INDIAN NAMES POOL
# ============================================================
FIRST_NAMES = [
    "Aarav", "Aditya", "Akash", "Amit", "Ananya", "Ankit", "Anuj", "Arjun",
    "Aryan", "Ashok", "Bhavesh", "Chetan", "Chirag", "Deepak", "Deepika",
    "Devika", "Dhruv", "Divya", "Esha", "Farhan", "Gaurav", "Geeta", "Girish",
    "Harish", "Heena", "Isha", "Ishaan", "Jagruti", "Jai", "Jaya", "Jayesh",
    "Karan", "Kavita", "Kavya", "Kedar", "Kirti", "Komal", "Kunal", "Lalit",
    "Lata", "Mahesh", "Manisha", "Manish", "Manoj", "Meena", "Megha", "Milan",
    "Minal", "Mohan", "Mukesh", "Nandita", "Neha", "Nikhil", "Nilesh", "Nitin",
    "Nisha", "Omkar", "Pallavi", "Paras", "Payal", "Pooja", "Poonam", "Pranav",
    "Prashant", "Pratik", "Preethi", "Priya", "Purva", "Rachna", "Rahul",
    "Rajesh", "Rajiv", "Rakesh", "Ranjit", "Rashmi", "Ravi", "Ritika", "Rohit",
    "Roshan", "Sachin", "Sagar", "Sahil", "Saket", "Saloni", "Sandeep",
    "Sandesh", "Sanjay", "Sarita", "Seema", "Shailesh", "Shivam", "Shilpa",
    "Shruti", "Shweta", "Siddhant", "Sneha", "Soham", "Suhas", "Sujata",
    "Suman", "Sunil", "Suresh", "Swati", "Tanvi", "Tejas", "Tushar", "Usha",
    "Vaibhav", "Vandana", "Varun", "Vijay", "Vikas", "Vikram", "Vishal",
    "Vivek", "Vrushali", "Yash", "Yogesh", "Zara", "Zeeshan"
]

LAST_NAMES = [
    "Agarwal", "Bapat", "Bhatt", "Chavan", "Chopra", "Dalvi", "Desai",
    "Deshpande", "Dubey", "Gadkari", "Gaikwad", "Gandhe", "Garg", "Ghosh",
    "Godse", "Gokhale", "Goyal", "Gupta", "Iyer", "Jain", "Joshi", "Kadam",
    "Kapoor", "Kapse", "Karnik", "Khatri", "Khot", "Kulkarni", "Kumar",
    "Lad", "Lokhande", "Mahajan", "Malhotra", "Mane", "Mehta", "Mishra",
    "Modi", "More", "Mukherjee", "Naik", "Nair", "Narayan", "Parekh",
    "Patel", "Patil", "Pawar", "Pillai", "Prasad", "Rathod", "Rao",
    "Reddy", "Roy", "Shah", "Sharma", "Shinde", "Shirke", "Shukla",
    "Singh", "Sinha", "Thakur", "Tiwari", "Verma", "Wagh", "Yadav"
]

# ============================================================
# COMPLAINT DATA TEMPLATES
# ============================================================
COMPLAINT_TEMPLATES = {
    "UPI/IMPS Transfer Dispute": {
        "dept_id": 1,
        "descriptions": [
            "I transferred ₹{amount} via UPI to a merchant on {date}, but the amount was deducted from my account and the transaction shows failed at the receiver's end. UTR number is {ref}. The money has not been reversed even after 5 business days.",
            "Amount of ₹{amount} was debited from my account on {date} through UPI/IMPS transfer (Reference: {ref}) but the beneficiary did not receive it. I have contacted the recipient bank but they say no credit was made.",
            "Mera UPI transaction fail ho gaya lekin paise deduct ho gaye. Transaction date {date} thi aur amount ₹{amount} tha. Reference number {ref} hai. Please help karo refund karne mein.",
            "On {date}, I made an IMPS transfer of ₹{amount} with reference {ref}. The amount got debited but the transfer status shows 'Pending' for over 48 hours. Requesting immediate investigation.",
            "UPI payment of ₹{amount} dated {date} (UTR: {ref}) was charged to my account but shows as declined on the merchant app. I need a refund or confirmation of credit."
        ],
        "service_types": ["UPI/IMPS Transfer Dispute"],
    },
    "Credit/Debit Card Dispute": {
        "dept_id": 1,
        "descriptions": [
            "An unauthorized transaction of ₹{amount} was made on my credit card on {date} at an unknown merchant. I did not make this purchase. Reference: {ref}. I request immediate chargeback.",
            "My debit card was charged ₹{amount} on {date} for a transaction I never authorized (Ref: {ref}). The merchant is unrecognized. Requesting investigation and refund.",
            "I was charged twice for the same transaction of ₹{amount} on {date}. Both debits appear on my statement with reference {ref}. This is a double charge error and needs to be reversed.",
            "Card fraud complaint: On {date}, someone used my card details to make a purchase of ₹{amount}. My card is physically with me. Reference: {ref}. Please block and initiate chargeback.",
        ],
        "service_types": ["Credit/Debit Card Dispute"],
    },
    "Net Banking / Mobile App Issue": {
        "dept_id": 3,
        "descriptions": [
            "I am unable to login to net banking for the past {days} days. I keep getting 'Session Expired' error even after entering correct credentials. This is very inconvenient as I need to do urgent transactions.",
            "My mobile banking app is showing wrong balance. My passbook shows ₹{amount} but the app shows a different figure. I am concerned about data integrity.",
            "After the recent app update, I cannot make any fund transfers. The OTP is not being received on my registered mobile number {ref}. Please fix this urgently.",
            "Internet banking ka password reset nahi ho raha. Email par OTP aa raha hai but 'Invalid OTP' error aa raha hai. Kal se yeh problem hai. Mera account access band ho gaya hai.",
        ],
        "service_types": ["Net Banking / Mobile App Issue"],
    },
    "Loan & EMI Dispute": {
        "dept_id": 2,
        "descriptions": [
            "My loan account {ref} shows an outstanding EMI of ₹{amount} for {date} even though I have already made the payment. The amount was debited but not credited to the loan account.",
            "I foreclosed my personal loan (Account: {ref}) on {date} and paid the complete outstanding amount of ₹{amount}. However, I have not received the NOC and my CIBIL still shows outstanding.",
            "I have been charged extra EMI of ₹{amount} for loan account {ref}. The EMI schedule shows {date} payment as missed but I have the bank receipt. This is a system error.",
            "Pre-payment penalty charged wrongly on my home loan account {ref}. I paid ₹{amount} as principal pre-payment on {date} and was charged ₹5000 penalty which is not applicable per my loan agreement.",
        ],
        "service_types": ["Loan & EMI Dispute"],
    },
    "Account Services Issue": {
        "dept_id": 3,
        "descriptions": [
            "My savings account {ref} has been marked dormant without any prior notice. I cannot make transactions. I have been a customer for 8 years and need this resolved immediately.",
            "KYC update request submitted on {date} with all required documents. However, my account {ref} still shows 'KYC Pending' status and transactions are getting blocked.",
            "I submitted a cheque of ₹{amount} on {date} (Cheque No: {ref}) which was returned unpaid citing 'Insufficient Funds' even though I had adequate balance. This is a bank error.",
            "My FD (Fixed Deposit) with reference {ref} matured on {date} for ₹{amount} but the renewal was done without my consent at a lower interest rate. I want it reversed to my savings account.",
            "Account freezing notice received but I have committed no fraud. My account {ref} was frozen on {date} without prior intimation. I need urgent unfreezing.",
        ],
        "service_types": ["Account Services Issue"],
    },
    "CIBIL / Credit Score Complaint": {
        "dept_id": 5,
        "descriptions": [
            "My CIBIL score has dropped drastically due to an incorrect overdue shown for account {ref}. This loan was closed on {date} and I have the NOC, but CIBIL still shows it as outstanding.",
            "Bank has reported me as defaulter to credit bureau for EMI of ₹{amount} dated {date} which I had paid (Reference: {ref}). Requesting correction and bureau update.",
            "Mera CIBIL report mein ek account dikh raha hai jo mera nahi hai. Account number {ref} kisi aur ka lagta hai. Yeh meri identity theft ka case ho sakta hai. Please investigate.",
            "Loan Account {ref} closed in {date} but still showing 'Active' with overdue in CIBIL report. Due to this my credit card application was rejected. Need immediate rectification.",
        ],
        "service_types": ["CIBIL / Credit Score Complaint"],
    },
    "Lost / Stolen Card": {
        "dept_id": 1,
        "descriptions": [
            "I lost my debit card yesterday. My card number ends with {ref}. Please block it immediately and issue a replacement. No unauthorized transaction has occurred so far.",
            "My credit card (last 4 digits: {ref}) was stolen. I need it blocked ASAP. I also want to check if any unauthorized transactions have been made in the last 24 hours.",
            "Mera ATM card kho gaya hai. Mujhe turant block karana hai aur naya card chahiye. Card number ke last 4 digits hain {ref}. Koi bhi fraud na ho isliye jaldi block karo.",
        ],
        "service_types": ["Lost / Stolen Card"],
    },
    "ATM Cash Dispute": {
        "dept_id": 1,
        "descriptions": [
            "I attempted to withdraw ₹{amount} from ATM (Location: {ref}) on {date}. The amount was debited from my account but cash was not dispensed. I have the ATM receipt showing failed transaction.",
            "ATM se paise nahi nikle lekin account se ₹{amount} kat gaye on {date}. ATM ID: {ref}. Yeh third time hai aisi problem ho rahi hai. Please reversal karo.",
            "Cash withdrawal failure at ATM reference {ref} on {date}. Amount ₹{amount} debited but not received. Machine was making unusual noise and did not open cash tray.",
        ],
        "service_types": ["ATM Cash Dispute"],
    },
    "Staff / Recovery Agent Harassment": {
        "dept_id": 4,
        "descriptions": [
            "A recovery agent called me multiple times today (reference complaint: {ref}) using abusive language regarding my loan EMI. This is harassment and violates RBI Fair Practice Code.",
            "Bank's recovery staff visited my home on {date} and behaved in an intimidating manner in front of my family. This is completely unacceptable conduct. Agent name mentioned was {ref}.",
            "I am receiving threatening calls from an agency claiming to collect debt for your bank. They are calling at odd hours and using pressure tactics. This needs to stop immediately.",
        ],
        "service_types": ["Staff / Recovery Agent Harassment"],
    },
}

BANKS = [
    "State Bank of India (SBI)", "HDFC Bank", "ICICI Bank", "Axis Bank",
    "Kotak Mahindra Bank", "Bank of Baroda", "Punjab National Bank",
    "Union Bank of India", "Canara Bank", "IndusInd Bank"
]

STATUSES_WEIGHTS = [
    ("resolved", 30), ("in_progress", 25), ("open", 20),
    ("escalated", 15), ("closed", 7), ("resolution_proposed", 3)
]

PRIORITIES_WEIGHTS = [("High", 15), ("Medium", 60), ("Low", 25)]

RESOLUTION_TYPES = [
    "FULL_REFUND", "PARTIAL_REFUND", "ACCOUNT_CORRECTED",
    "CARD_BLOCKED_REPLACED", "KYC_UPDATED", "CIBIL_RECTIFICATION",
    "LOAN_NOC_ISSUED", "TECHNICAL_ISSUE_FIXED"
]

RESOLUTION_TEXTS = {
    "FULL_REFUND": "Full refund of disputed amount has been processed. Funds credited to your account within 3-5 business days as per RBI Circular on TAT for digital transactions.",
    "PARTIAL_REFUND": "Partial refund of ₹{amount} has been processed after investigation. The remaining amount was applicable charges per terms and conditions.",
    "ACCOUNT_CORRECTED": "Account records have been corrected. The discrepancy was a system error which has been fixed. Your account is now fully operational.",
    "CARD_BLOCKED_REPLACED": "Card has been blocked and replacement dispatched via courier. Expected delivery: 5-7 working days. New card will be activated after KYC verification.",
    "KYC_UPDATED": "KYC documents verified and account updated. All transaction restrictions have been lifted. Your account is now fully compliant.",
    "CIBIL_RECTIFICATION": "Incorrect entry in CIBIL bureau has been corrected. An update request has been submitted to TransUnion CIBIL. Score will be updated within 30-45 days.",
    "LOAN_NOC_ISSUED": "Loan account fully settled. NOC has been issued and dispatched to your registered address. CIBIL update has been initiated.",
    "TECHNICAL_ISSUE_FIXED": "Technical issue identified and resolved. The service is now functioning normally. We apologize for the inconvenience.",
}


def weighted_choice(weighted_list):
    items, weights = zip(*weighted_list)
    return random.choices(items, weights=weights, k=1)[0]


def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def random_ref_id(service_type: str) -> str:
    if "UPI" in service_type or "IMPS" in service_type:
        return f"UPI{random.randint(100000000000, 999999999999)}"
    elif "Card" in service_type or "ATM" in service_type:
        return f"{random.randint(1000, 9999)}"  # last 4 digits
    elif "Loan" in service_type or "CIBIL" in service_type:
        return f"LN{random.randint(10000000, 99999999)}"
    elif "Account" in service_type:
        return f"ACC{random.randint(10000000, 99999999)}"
    else:
        return f"REF{random.randint(100000, 999999)}"


def generate_complaint_description(template_key, service_type):
    template_data = COMPLAINT_TEMPLATES[template_key]
    template_str = random.choice(template_data["descriptions"])
    
    amount = random.choice([500, 1000, 1500, 2000, 2500, 3000, 5000, 7500, 10000, 15000, 20000, 25000, 50000, 75000, 100000])
    days_back = random.randint(1, 60)
    date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%d-%b-%Y")
    ref = random_ref_id(service_type)
    days = random.randint(2, 7)
    
    return template_str.format(amount=f"{amount:,}", date=date, ref=ref, days=days), amount, ref


def main():
    db: Session = SessionLocal()
    
    print("=" * 60)
    print("GrievanceIQ Bulk Data Seeder")
    print("=" * 60)
    
    # -----------------------------------------------
    # Load companies and departments
    # -----------------------------------------------
    companies = db.query(Company).all()
    if not companies:
        print("No companies found! Creating default companies...")
        for bank_name in BANKS:
            c = Company(company_name=bank_name)
            db.add(c)
        db.commit()
        companies = db.query(Company).all()
    
    company_map = {c.company_name: c.company_id for c in companies}
    all_company_ids = [c.company_id for c in companies]
    
    departments = db.query(Department).all()
    dept_ids = [d.department_id for d in departments] if departments else [1]
    
    print(f"Found {len(companies)} banks, {len(departments)} departments\n")
    
    # -----------------------------------------------
    # CREATE 200 CUSTOMER ACCOUNTS
    # -----------------------------------------------
    print("Creating 200 customer accounts...\n")
    
    created_users = []
    used_emails = set()
    
    # Get all existing emails to avoid duplicates
    existing_emails = {u.email for u in db.query(User).all()}
    used_emails.update(existing_emails)
    
    attempts = 0
    while len(created_users) < 200 and attempts < 1000:
        attempts += 1
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        num = random.randint(100, 999)
        email = f"{first.lower()}.{last.lower()}{num}@gmail.com"
        
        if email in used_emails:
            continue
        
        used_emails.add(email)
        full_name = f"{first} {last}"
        password_plain = "User@1234"
        hashed = hash_password(password_plain)
        
        user = User(
            username=email,
            email=email,
            hashed_password=hashed,
            full_name=full_name,
            role="customer",
            is_active=True
        )
        db.add(user)
        created_users.append({
            "name": full_name,
            "email": email,
            "password": password_plain
        })
        
        if len(created_users) % 50 == 0:
            db.commit()
            print(f"  Created {len(created_users)} users...")
    
    db.commit()
    
    # Reload users to get IDs
    all_customers = db.query(User).filter(User.role == "customer").all()
    customer_ids = [u.user_id for u in all_customers]
    
    print(f"\nTotal customer accounts: {len(all_customers)}\n")
    
    # -----------------------------------------------
    # CREATE 250+ COMPLAINTS
    # -----------------------------------------------
    print("Creating 250+ complaints...\n")
    
    template_keys = list(COMPLAINT_TEMPLATES.keys())
    existing_complaint_count = db.query(Complaint).count()
    
    complaints_created = 0
    for i in range(260):
        # Random assignment
        template_key = random.choice(template_keys)
        template_data = COMPLAINT_TEMPLATES[template_key]
        service_type = random.choice(template_data["service_types"])
        dept_id = template_data["dept_id"]
        
        # Ensure dept_id exists
        if dept_id not in dept_ids:
            dept_id = dept_ids[0] if dept_ids else 1
        
        company_id = random.choice(all_company_ids)
        customer_id = random.choice(customer_ids)
        status = weighted_choice(STATUSES_WEIGHTS)
        priority = weighted_choice(PRIORITIES_WEIGHTS)
        
        # Generate description
        description, amount, ref_id = generate_complaint_description(template_key, service_type)
        
        # Random dates
        days_ago = random.randint(1, 90)
        created_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
        txn_date = (created_at - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d")
        
        # Token
        token = f"GRV{int(created_at.timestamp())}{random.randint(100, 999)}"
        
        # Validity score
        validity_score = random.randint(65, 95)
        
        # SLA deadline
        sla_hours = {"High": 24, "Medium": 72, "Low": 168}[priority]
        sla_deadline = created_at + timedelta(hours=sla_hours)
        sla_breached = sla_deadline < datetime.utcnow() and status not in ["resolved", "closed"]
        
        resolved_at = None
        resolution_notes = None
        can_reopen_until = None
        
        if status in ["resolved", "closed"]:
            resolved_at = created_at + timedelta(hours=random.randint(4, sla_hours))
            resolution_type = random.choice(RESOLUTION_TYPES)
            resolution_notes = RESOLUTION_TEXTS.get(resolution_type, "Complaint resolved by banking officer.").replace("{amount}", f"{amount:,}")
            can_reopen_until = resolved_at + timedelta(days=7)
        
        complaint = Complaint(
            token=token,
            company_id=company_id,
            department_id=dept_id,
            service_type=service_type,
            transaction_date=txn_date,
            raw_text=description,  # NOT NULL in DB
            amount=float(amount) if "Lost" not in service_type and "Staff" not in service_type else None,
            reference_id=ref_id,
            branch=random.choice(["Main Branch", "Andheri West", "Bandra", "Pune Camp", "Dadar", "Thane", "Vashi", "Borivali", "Kolhapur"]),
            description=description,
            priority=priority,
            status=status,
            validity_score=validity_score,
            validity_status="valid",
            resolution_mode=random.choice(["BOT", "HUMAN", "NONE"]) if status in ["resolved", "closed"] else "NONE",
            escalation_level=2 if status == "escalated" else 0,
            sla_deadline=sla_deadline,
            sla_breached=sla_breached,
            resolved_at=resolved_at,
            resolution_notes=resolution_notes,
            can_reopen_until=can_reopen_until,
            customer_id=customer_id,
            evidence_status="NOT_REQUIRED" if "Lost" in service_type or "Staff" in service_type else ("VERIFIED" if status in ["resolved", "closed"] else "PENDING"),
            created_at=created_at,
            updated_at=created_at,
            submitted_at=created_at.isoformat(),
        )
        db.add(complaint)
        
        if (i + 1) % 50 == 0:
            db.commit()
            print(f"  Created {i + 1} complaints...")
    
    db.commit()
    
    # Create Resolution records for resolved complaints
    print("\nCreating resolution records for resolved complaints...")
    resolved_complaints = db.query(Complaint).filter(
        Complaint.status.in_(["resolved", "closed"]),
        Complaint.resolution_notes.isnot(None)
    ).all()
    
    # Get admin/officer user IDs
    officers = db.query(User).filter(User.role.in_(["officer", "staff", "admin"])).all()
    officer_ids = [o.user_id for o in officers] if officers else [1]
    
    res_created = 0
    for comp in resolved_complaints:
        # Check if resolution already exists
        existing_res = db.query(Resolution).filter(Resolution.complaint_id == comp.complaint_id).first()
        if existing_res:
            continue
        
        resolution_type = random.choice(RESOLUTION_TYPES)
        resolved_by = random.choice(officer_ids)
        
        new_res = Resolution(
            complaint_id=comp.complaint_id,
            worker_id=resolved_by,
            resolution_details=comp.resolution_notes or "Resolved per standard banking procedures.",
            resolution_type=resolution_type,
            transaction_reference=f"REFUND-{comp.token[-8:]}",
            resolved_amount=comp.amount,
            resolution_proof_path=None,
            resolution_date=comp.resolved_at or comp.created_at,
            customer_confirmation_status=random.choice(["ACCEPTED", "ACCEPTED", "ACCEPTED", "PENDING"]),
        )
        db.add(new_res)
        res_created += 1
    
    db.commit()
    print(f"  Created {res_created} resolution records.")
    
    # Status history for all complaints
    print("\nAdding status history records...")
    all_complaints = db.query(Complaint).all()
    status_added = 0
    for comp in all_complaints:
        existing_hist = db.query(StatusHistory).filter(StatusHistory.complaint_id == comp.complaint_id).count()
        if existing_hist == 0:
            db.add(StatusHistory(
                complaint_id=comp.complaint_id,
                old_status=None,
                new_status=comp.status,
                changed_by="system",
                changed_at=comp.created_at,
                comment="Initial complaint registered."
            ))
            status_added += 1
    
    db.commit()
    print(f"  Added {status_added} status history records.")
    
    # Final Stats
    total_complaints = db.query(Complaint).count()
    total_users = db.query(User).filter(User.role == "customer").count()
    
    print("\n" + "=" * 60)
    print("SEED COMPLETE")
    print("=" * 60)
    print(f"Total Customers in DB: {total_users}")
    print(f"Total Complaints in DB: {total_complaints}")
    print()
    
    # Print credentials
    print("=" * 60)
    print("CUSTOMER CREDENTIALS (all passwords: User@1234)")
    print("=" * 60)
    for idx, u in enumerate(created_users, 1):
        print(f"{idx:3}. {u['name']:<25} | {u['email']}")
    
    print()
    print("=" * 60)
    print("ADMIN CREDENTIALS")
    print("=" * 60)
    print("1. ashmit.patil@spit.ac.in  / spit@123  (Admin)")
    print("2. vedant.patil24@spit.ac.in / spit@123 (Admin)")
    print("3. mayuri.tarde24@spit.ac.in / spit@123 (Admin)")
    print()
    print("OFFICER LOGIN - Check db for DESK-* usernames / spit@123")
    
    db.close()


if __name__ == "__main__":
    main()
