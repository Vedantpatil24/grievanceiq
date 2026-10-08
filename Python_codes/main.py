from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, func, case, or_
from sqlalchemy.orm import sessionmaker
from create_db import Complaint, Department, Company, Feedback, User, Worker
from jose import JWTError, jwt
import bcrypt
import pickle
import re
import os
import uuid
from datetime import datetime, timedelta
from sbert_validator import extract_text_from_file, analyze_semantic_validity
from bot_simulator import start_bot_simulator_thread

app = FastAPI(title="GrievanceIQ API")

@app.on_event("startup")
def startup_event():
    start_bot_simulator_thread()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = r"G:\Mini_project\Python_codes\uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "GrievanceIQ API",
        "frontend_url": "http://localhost:5173",
        "api_documentation": "http://127.0.0.1:8000/docs"
    }

# --- Load saved model + vectorizer ---
with open(r"G:\Mini_project\Python_codes\classifier.pkl", "rb") as f:
    classifier = pickle.load(f)
with open(r"G:\Mini_project\Python_codes\vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# --- Database setup ---
engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)

# --- Urgency Keywords ---
HIGH_URGENCY = [
    "fraud", "fraudulent", "unauthorized transaction", "identity theft",
    "stolen", "lawsuit", "legal action", "attorney", "sue", "scam",
    "threatened", "harassment", "discrimination", "police report",
    "illegal", "emergency", "account hacked", "phishing", "unauthorized withdrawal"
]
MEDIUM_URGENCY = [
    "dispute", "disputed", "incorrect information", "overcharged",
    "denied", "rejected", "late fee", "credit score dropped",
    "frustrated", "delay in resolution", "emi deducted", "failed transaction",
    "refund pending", "card blocked", "kyc pending"
]

# Specific factual/banking tokens to differentiate genuine complaints from purely emotional rants
FACTUAL_BANKING_TERMS = [
    "transaction", "account", "bank", "card", "debit", "credit", "amount",
    "charge", "fee", "payment", "transfer", "emi", "loan", "balance",
    "refund", "atm", "branch", "statement", "upi", "cheque", "interest",
    "limit", "deducted", "credited", "failed", "pending", "dispute", "unauthorized",
    "otp", "imps", "neft", "rtgs", "kyc", "fraud"
]

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def score_priority(text):
    matched_high = [kw for kw in HIGH_URGENCY if re.search(r'\b' + re.escape(kw) + r'\b', text)]
    matched_medium = [kw for kw in MEDIUM_URGENCY if re.search(r'\b' + re.escape(kw) + r'\b', text)]
    if matched_high:
        return "High", matched_high
    elif matched_medium:
        return "Medium", matched_medium
    else:
        return "Low", []

def check_validity(narrative, reference_id, amount, transaction_date, service_type, proof, proof_bytes=None):
    checklist = {}
    score = 0

    # 1. Evidence available (25 points) — mandatory
    has_proof = proof is not None and getattr(proof, "filename", None)
    checklist["evidence_available"] = bool(has_proof)
    if has_proof:
        score += 25

    # 2. Transaction details provided (25 points)
    date_valid = True
    if transaction_date:
        try:
            date_valid = datetime.strptime(transaction_date, "%Y-%m-%d").date() <= datetime.now().date()
        except ValueError:
            date_valid = False

    has_txn_details = bool(reference_id) and amount is not None and bool(transaction_date) and date_valid
    checklist["transaction_details_provided"] = has_txn_details
    if has_txn_details:
        score += 25

    # 3. Service/category identified (15 points)
    has_service = bool(service_type)
    checklist["service_identified"] = has_service
    if has_service:
        score += 15

    # 4. SBERT & Heuristic Semantic Grievance Analysis (35 points)
    words = re.findall(r"[a-zA-Z]{2,}", narrative.lower())
    unique_words = set(words)
    has_substance = len(narrative.strip()) >= 35 and len(words) >= 7 and len(unique_words) >= 5

    PROBLEM_ACTION_INDICATORS = [
        "deducted", "debited", "charged", "withdrawn", "credited", "reversed",
        "failed", "pending", "blocked", "declined", "error", "unauthorized",
        "scam", "fraud", "hacked", "dispute", "disputed", "stolen", "loss",
        "refund", "delayed", "delay", "issue", "problem", "not received",
        "wrong", "excess", "overcharged", "harassment", "closed", "foreclosure"
    ]
    
    has_banking_entity = any(w in FACTUAL_BANKING_TERMS for w in words)
    has_problem_action = any(w in narrative.lower() for w in PROBLEM_ACTION_INDICATORS)

    # Extract proof text if proof bytes provided
    proof_text = ""
    if proof_bytes and hasattr(proof, "filename"):
        proof_text = extract_text_from_file(proof_bytes, proof.filename)

    # Run SBERT semantic analysis
    sbert_res = analyze_semantic_validity(narrative, proof_text)
    narrative_sbert_score = sbert_res["narrative_semantic_score"]
    proof_similarity_score = sbert_res["proof_similarity_score"]
    is_sbert_valid = sbert_res["is_semantically_valid"]

    # Valid if: sentence substance + banking problem action + SBERT similarity to banking complaint benchmarks
    is_genuine_complaint = has_substance and has_banking_entity and has_problem_action and is_sbert_valid

    checklist["issue_clearly_described"] = bool(is_genuine_complaint)
    checklist["problem_action_described"] = bool(has_problem_action)
    checklist["banking_entity_mentioned"] = bool(has_banking_entity)
    checklist["sbert_semantic_match"] = bool(is_sbert_valid)
    checklist["sbert_score"] = narrative_sbert_score
    checklist["proof_similarity_score"] = proof_similarity_score
    
    if is_genuine_complaint:
        score += 35

    if score >= 70:
        decision = "ACTIONABLE COMPLAINT"
    else:
        decision = "MORE INFORMATION REQUIRED"

    return score, checklist, decision, narrative_sbert_score, proof_similarity_score, proof_text

def assign_worker_least_loaded(session, department_id: int):
    """Fair auto-assignment: picks the bot worker with the lowest active workload in that department."""
    workers = session.query(Worker).filter_by(department_id=department_id, is_active=True).all()
    if not workers:
        return None
    
    # Calculate active load for each worker
    best_worker = None
    min_load = float('inf')
    for w in workers:
        active_load = session.query(Complaint).filter(
            Complaint.assigned_worker_id == w.worker_id,
            Complaint.status.in_(["open", "in_progress"])
        ).count()
        if active_load < min_load:
            min_load = active_load
            best_worker = w
            
    return best_worker.worker_id if best_worker else workers[0].worker_id

def calculate_sla(priority: str):
    """
    SLA Calculation:
    High: 24 hours
    Medium: 7 days
    Low: 30 days
    """
    now = datetime.now()
    if priority == "High":
        return now + timedelta(hours=24)
    elif priority == "Medium":
        return now + timedelta(days=7)
    else:
        return now + timedelta(days=30)

def refresh_sla_escalations(session):
    """Checks all unresolved complaints and updates is_escalated flag if past due_date.
    Also auto-advances complaints that have been in 'resolved' status for over 48 hours to 'closed'."""
    now = datetime.now()
    unresolved = session.query(Complaint).filter(
        Complaint.status.in_(["open", "in_progress"]),
        Complaint.due_date.isnot(None),
        Complaint.due_date < now
    ).all()
    for c in unresolved:
        c.is_escalated = True

    # Auto-close complaints resolved for > 48 hours
    auto_close_cutoff = now - timedelta(hours=48)
    auto_closable = session.query(Complaint).filter(
        Complaint.status == "resolved",
        Complaint.resolved_at.isnot(None),
        Complaint.resolved_at <= auto_close_cutoff
    ).all()
    for c in auto_closable:
        c.status = "closed"
        c.stage = "Closed"

    session.commit()

def generate_token(session):
    count = session.query(Complaint).count()
    return f"GRV-2026-{count + 1:05d}"

# --- Auth config ---
SECRET_KEY = "grievanceiq-secret-key-change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/user/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        user_id: int = payload.get("user_id")
        worker_id: str = payload.get("worker_id")
        employee_id: str = payload.get("employee_id")
        if email is None:
            raise credentials_exception
        return {
            "email": email,
            "role": role,
            "user_id": user_id,
            "worker_id": worker_id,
            "employee_id": employee_id
        }
    except JWTError:
        raise credentials_exception

def verify_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user["email"]

def verify_employee(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Employee privileges required")
    return current_user

# --- Request/response models ---
class FeedbackIn(BaseModel):
    rating: int
    comment: str | None = None

class StatusUpdate(BaseModel):
    status: str
    stage: str | None = None
    rejection_reason: str | None = None
    resolution_notes: str | None = None
    resolution_proof_url: str | None = None
    requires_more_proof: str | None = None

class LoginIn(BaseModel):
    email: str
    password: str

class RegisterIn(BaseModel):
    name: str
    email: str
    password: str
    phone: str | None = None

class UserProfileUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    birthdate: str | None = None
    avatar_url: str | None = None

class EmployeeLoginStep1(BaseModel):
    employee_id: str
    password: str

class EmployeeLoginStep2(BaseModel):
    employee_id: str
    otp: str | None = None
    otp_code: str | None = None

class CustomerAppealIn(BaseModel):
    appeal_text: str
    is_satisfied: bool = False

# --- Auth Endpoints ---

@app.post("/auth/register")
def register_user(reg: RegisterIn):
    session = Session()
    existing = session.query(User).filter_by(email=reg.email.strip().lower()).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    hashed = bcrypt.hashpw(reg.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = User(
        name=reg.name.strip(),
        email=reg.email.strip().lower(),
        password_hash=hashed,
        role="user"
    )
    session.add(new_user)
    session.commit()
    token = create_access_token(data={"sub": new_user.email, "role": new_user.role, "user_id": new_user.id})
    user_data = {"id": new_user.id, "name": new_user.name, "email": new_user.email, "role": new_user.role}
    session.close()
    return {"access_token": token, "token_type": "bearer", "user": user_data}

@app.post("/auth/user/login")
def user_login(credentials: LoginIn):
    session = Session()
    user = session.query(User).filter_by(email=credentials.email.strip().lower()).first()
    session.close()

    if not user or not bcrypt.checkpw(credentials.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "role": user.role,
        "name": user.name,
        "email": user.email
    }

@app.post("/auth/admin/login")
@app.post("/login")  # Maintain backward compatibility
def admin_login(credentials: LoginIn):
    session = Session()
    user = session.query(User).filter_by(email=credentials.email.strip().lower()).first()
    session.close()

    if not user or user.role != "admin":
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    if not bcrypt.checkpw(credentials.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    access_token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "name": user.name}

# --- Employee Authentication with 2FA / OTP ---

@app.post("/auth/employee/login-step1")
def employee_login_step1(creds: EmployeeLoginStep1):
    session = Session()
    worker = session.query(Worker).filter_by(employee_id=creds.employee_id.strip()).first()

    if not worker or not worker.password_hash or not bcrypt.checkpw(creds.password.encode("utf-8"), worker.password_hash.encode("utf-8")):
        session.close()
        raise HTTPException(status_code=401, detail="Invalid Employee ID or password")

    # Generate a realistic 6-digit OTP code (demo fallback: 123456 or random)
    import random
    otp = f"{random.randint(100000, 999999)}"
    worker.otp_code = otp
    worker.otp_expires_at = datetime.now() + timedelta(minutes=10)
    session.commit()

    phone_masked = worker.phone or "+91 98201 XXXXX"
    if len(phone_masked) > 6:
        phone_display = phone_masked[:7] + "XXXX" + phone_masked[-2:]
    else:
        phone_display = phone_masked

    session.close()
    return {
        "message": f"OTP successfully dispatched to registered mobile {phone_display}",
        "employee_id": creds.employee_id,
        "phone_masked": phone_display,
        "demo_otp": otp,
        "dev_demo_otp": otp
    }

@app.post("/auth/employee/verify-otp")
def employee_verify_otp(creds: EmployeeLoginStep2):
    session = Session()
    worker = session.query(Worker).filter_by(employee_id=creds.employee_id.strip()).first()

    if not worker:
        session.close()
        raise HTTPException(status_code=404, detail="Employee record not found")

    submitted_otp = (creds.otp or creds.otp_code or "").strip()
    if not worker.otp_code or worker.otp_code != submitted_otp:
        session.close()
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")

    dept = session.query(Department).filter_by(id=worker.department_id).first()

    # Clear OTP after verification
    worker.otp_code = None
    session.commit()

    access_token = create_access_token(data={
        "sub": worker.email or worker.employee_id,
        "role": "employee",
        "worker_id": worker.worker_id,
        "employee_id": worker.employee_id,
        "user_id": worker.id
    })

    worker_data = {
        "worker_id": worker.worker_id,
        "employee_id": worker.employee_id,
        "name": worker.name,
        "email": worker.email,
        "phone": worker.phone,
        "department": dept.name if dept else "Banking Operations",
        "role": "employee"
    }
    session.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "employee": worker_data
    }

# --- User Profile Settings & Picture Upload ---

@app.get("/user/profile")
def get_user_profile(current_user: dict = Depends(get_current_user)):
    session = Session()
    user = session.query(User).filter_by(id=current_user["user_id"]).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone or "",
        "address": user.address or "",
        "birthdate": user.birthdate or "",
        "avatar_url": user.avatar_url or "",
        "role": user.role
    }
    session.close()
    return data

@app.put("/user/profile")
def update_user_profile(update: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    session = Session()
    user = session.query(User).filter_by(id=current_user["user_id"]).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    if update.name is not None:
        user.name = update.name
    if update.phone is not None:
        user.phone = update.phone
    if update.address is not None:
        user.address = update.address
    if update.birthdate is not None:
        user.birthdate = update.birthdate
    if update.avatar_url is not None:
        user.avatar_url = update.avatar_url

    session.commit()
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone or "",
        "address": user.address or "",
        "birthdate": user.birthdate or "",
        "avatar_url": user.avatar_url or "",
    }
    session.close()
    return {"message": "Profile updated successfully", "user": data}

@app.post("/user/avatar")
def upload_user_avatar(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    session = Session()
    user = session.query(User).filter_by(id=current_user["user_id"]).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    ext = os.path.splitext(file.filename)[1] or ".png"
    safe_name = f"avatar_{user.id}_{uuid.uuid4().hex[:6]}{ext}"
    full_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(full_path, "wb") as f:
        f.write(file.file.read())

    avatar_url = f"/uploads/{safe_name}"
    user.avatar_url = avatar_url
    session.commit()
    session.close()
    return {"message": "Avatar uploaded successfully", "avatar_url": avatar_url}

# --- Complaint Submission & User Endpoints ---

@app.post("/complaint")
def submit_complaint(
    narrative: str = Form(...),
    company: str = Form(...),
    transaction_date: str | None = Form(None),
    reference_id: str | None = Form(None),
    amount: float | None = Form(None),
    branch: str | None = Form(None),
    service_type: str | None = Form(None),
    user_id: int | None = Form(None),
    proof: UploadFile = File(...),
):
    # Read proof bytes once for storage and SBERT semantic analysis
    proof_bytes = proof.file.read()

    validity_score, checklist, decision, narrative_sbert_score, proof_similarity_score, proof_text = check_validity(
        narrative, reference_id, amount, transaction_date, service_type, proof, proof_bytes=proof_bytes
    )

    if transaction_date:
        try:
            if datetime.strptime(transaction_date, "%Y-%m-%d").date() > datetime.now().date():
                raise HTTPException(
                    status_code=422,
                    detail={
                        "message": "Transaction date cannot be in the future.",
                        "validity_score": validity_score,
                        "decision": "INVALID DATE",
                        "checklist": checklist
                    },
                )
        except ValueError:
            pass

    if decision == "MORE INFORMATION REQUIRED":
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Complaint could not be validated. Please check the required fields, upload proof, and describe the factual issue.",
                "validity_score": validity_score,
                "decision": decision,
                "checklist": checklist,
            },
        )

    session = Session()
    cleaned = clean_text(narrative)
    tfidf_vec = vectorizer.transform([cleaned])
    predicted_dept_name = classifier.predict(tfidf_vec)[0]
    priority, matched_keywords = score_priority(cleaned)

    dept = session.query(Department).filter_by(name=predicted_dept_name).first()
    if not dept:
        dept = Department(name=predicted_dept_name)
        session.add(dept)
        session.flush()

    comp = session.query(Company).filter_by(name=company).first()
    if not comp:
        comp = Company(name=company)
        session.add(comp)
        session.flush()

    token = generate_token(session)

    # File storage
    ext = os.path.splitext(proof.filename)[1]
    safe_name = f"{token}_{uuid.uuid4().hex[:8]}{ext}"
    full_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(full_path, "wb") as f:
        f.write(proof_bytes)
    proof_path = f"/uploads/{safe_name}"

    # Auto-assignment & SLA
    assigned_worker_id = assign_worker_least_loaded(session, dept.id)
    due_date = calculate_sla(priority)

    new_complaint = Complaint(
        token=token,
        user_id=user_id,
        narrative=narrative,
        narrative_clean=cleaned,
        department_id=dept.id,
        company_id=comp.id,
        priority=priority,
        status="open",
        stage="Triage",
        due_date=due_date,
        is_escalated=False,
        assigned_worker_id=assigned_worker_id,
        transaction_date=transaction_date,
        reference_id=reference_id,
        amount=amount,
        branch=branch,
        service_type=service_type,
        proof_file_path=proof_path,
        validity_score=validity_score,
        validity_decision=decision,
        sbert_narrative_score=narrative_sbert_score,
        proof_similarity_score=proof_similarity_score,
        proof_extracted_text=proof_text[:1500] if proof_text else None,
    )
    session.add(new_complaint)
    session.commit()

    # Get worker display name
    worker_obj = session.query(Worker).filter_by(worker_id=assigned_worker_id).first()
    worker_display = worker_obj.name if worker_obj else assigned_worker_id

    result = {
        "token": token,
        "department": dept.name,
        "priority": priority,
        "status": "open",
        "stage": "Triage",
        "assigned_worker": worker_display,
        "due_date": due_date.isoformat(),
        "validity_score": validity_score,
        "decision": decision,
        "sbert_score": narrative_sbert_score,
        "proof_similarity": proof_similarity_score,
    }
    session.close()
    return result

@app.get("/user/complaints")
def get_user_complaints(current_user: dict = Depends(get_current_user)):
    session = Session()
    refresh_sla_escalations(session)
    
    complaints = session.query(Complaint).filter_by(user_id=current_user["user_id"]).order_by(Complaint.created_at.desc()).all()
    results = []
    for c in complaints:
        dept = session.query(Department).filter_by(id=c.department_id).first()
        comp = session.query(Company).filter_by(id=c.company_id).first()
        worker = session.query(Worker).filter_by(worker_id=c.assigned_worker_id).first()
        results.append({
            "token": c.token,
            "department": dept.name if dept else "Triage",
            "company": comp.name if comp else None,
            "priority": c.priority,
            "status": c.status,
            "stage": c.stage or ("Resolved" if c.status == "resolved" else "Investigation"),
            "is_escalated": bool(c.is_escalated),
            "due_date": str(c.due_date) if c.due_date else None,
            "sla_due_at": str(c.due_date) if c.due_date else None,
            "assigned_worker": worker.name if worker else c.assigned_worker_id,
            "created_at": str(c.created_at),
            "resolved_at": str(c.resolved_at) if c.resolved_at else None,
            "transaction_date": c.transaction_date,
            "reference_id": c.reference_id,
            "branch": c.branch,
            "amount": c.amount,
            "service_type": c.service_type,
            "narrative": c.narrative,
            "description": c.narrative,
            "proof_file_path": c.proof_file_path,
            "proof_url": c.proof_file_path,
            "rejection_reason": c.rejection_reason,
            "resolution_notes": c.resolution_notes,
            "resolution_proof_url": c.resolution_proof_url,
            "priority_reason": c.priority_reason,
            "requires_more_proof": c.requires_more_proof,
            "customer_appeal": c.customer_appeal,
            "satisfaction_status": c.satisfaction_status,
        })
    session.close()
    return results

@app.get("/complaint/{token}")
def get_complaint(token: str):
    session = Session()
    refresh_sla_escalations(session)
    complaint = session.query(Complaint).filter_by(token=token).first()
    if not complaint:
        session.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    dept = session.query(Department).filter_by(id=complaint.department_id).first()
    comp = session.query(Company).filter_by(id=complaint.company_id).first()
    worker = session.query(Worker).filter_by(worker_id=complaint.assigned_worker_id).first()

    result = {
        "token": complaint.token,
        "department": dept.name if dept else None,
        "company": comp.name if comp else None,
        "priority": complaint.priority,
        "status": complaint.status,
        "stage": complaint.stage or ("Resolved" if complaint.status == "resolved" else "Investigation"),
        "is_escalated": bool(complaint.is_escalated),
        "due_date": str(complaint.due_date) if complaint.due_date else None,
        "sla_due_at": str(complaint.due_date) if complaint.due_date else None,
        "assigned_worker": worker.name if worker else complaint.assigned_worker_id,
        "assigned_worker_name": worker.name if worker else complaint.assigned_worker_id,
        "assigned_worker_id": worker.employee_id if (worker and worker.employee_id) else (complaint.assigned_worker_id or "—"),
        "created_at": str(complaint.created_at),
        "transaction_date": complaint.transaction_date,
        "reference_id": complaint.reference_id,
        "amount": complaint.amount,
        "branch": complaint.branch,
        "service_type": complaint.service_type,
        "proof_file_path": complaint.proof_file_path,
        "proof_url": complaint.proof_file_path,
        "narrative": complaint.narrative,
        "description": complaint.narrative,
        "sbert_score": complaint.sbert_narrative_score,
        "proof_similarity": complaint.proof_similarity_score,
        "rejection_reason": complaint.rejection_reason,
        "resolution_notes": complaint.resolution_notes,
        "resolution_proof_url": complaint.resolution_proof_url,
        "priority_reason": complaint.priority_reason,
        "requires_more_proof": complaint.requires_more_proof,
        "customer_appeal": complaint.customer_appeal,
        "satisfaction_status": complaint.satisfaction_status,
    }
    session.close()
    return result

@app.post("/complaint/{token}/appeal")
def customer_appeal_or_satisfaction(token: str, appeal: CustomerAppealIn):
    session = Session()
    complaint = session.query(Complaint).filter_by(token=token).first()
    if not complaint:
        session.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    if appeal.is_satisfied:
        complaint.satisfaction_status = "Satisfied"
        complaint.status = "closed"
        complaint.stage = "Closed"
    else:
        complaint.satisfaction_status = "Appealed / Dissatisfied"
        complaint.customer_appeal = appeal.appeal_text
        complaint.status = "in_progress"
        complaint.stage = "Investigation"
        # Notify worker
        if complaint.assigned_worker_id:
            try:
                c_cursor = session.connection().connection.cursor()
                c_cursor.execute("""
                    INSERT INTO notifications (worker_id, complaint_token, title, message)
                    VALUES (?, ?, ?, ?)
                """, (complaint.assigned_worker_id, token, "Customer Escalated Appeal", f"Customer is dissatisfied with previous resolution: {appeal.appeal_text[:100]}"))
            except Exception:
                pass

    session.commit()
    session.close()
    return {"message": "Status updated successfully", "token": token}

@app.post("/complaint/{token}/evidence")
def upload_additional_evidence(token: str, proof: UploadFile = File(...)):
    session = Session()
    complaint = session.query(Complaint).filter_by(token=token).first()
    if not complaint:
        session.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    ext = os.path.splitext(proof.filename)[1] or ".png"
    safe_name = f"evidence_{token}_{uuid.uuid4().hex[:6]}{ext}"
    full_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(full_path, "wb") as f:
        f.write(proof.file.read())

    complaint.proof_file_path = f"/uploads/{safe_name}"
    complaint.requires_more_proof = None
    complaint.status = "in_progress"
    complaint.stage = "Investigation"
    session.commit()
    session.close()
    return {"message": "Additional evidence successfully uploaded", "proof_file_path": f"/uploads/{safe_name}"}

@app.post("/complaint/{token}/feedback")
def submit_feedback(token: str, feedback: FeedbackIn):
    session = Session()
    complaint = session.query(Complaint).filter_by(token=token).first()
    if not complaint:
        session.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    existing = session.query(Feedback).filter_by(complaint_id=complaint.id).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="Feedback already submitted for this complaint")

    fb = Feedback(complaint_id=complaint.id, rating=feedback.rating, comment=feedback.comment)
    session.add(fb)

    # User feedback closes the grievance resolution cycle
    if complaint.status in ["resolved", "open", "in_progress"]:
        complaint.status = "closed"
        complaint.stage = "Closed"
        if not complaint.resolved_at:
            complaint.resolved_at = datetime.now()

    session.commit()
    session.close()
    return {"message": "Feedback submitted and grievance marked Closed", "token": token}

# --- Protected Admin Endpoints ---

@app.get("/admin/complaints")
def list_complaints(
    department: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    company: str | None = None,
    escalated_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    admin: str = Depends(verify_admin)
):
    session = Session()
    refresh_sla_escalations(session)
    query = session.query(Complaint)

    if department:
        dept = session.query(Department).filter_by(name=department).first()
        if dept:
            query = query.filter(Complaint.department_id == dept.id)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if status:
        query = query.filter(Complaint.status == status)
    if company and company.strip():
        comp_sub = session.query(Company.id).filter(Company.name.ilike(f"%{company.strip()}%")).subquery()
        query = query.filter(Complaint.company_id.in_(comp_sub))
    if escalated_only:
        query = query.filter(Complaint.is_escalated == True)

    total_count = query.count()
    complaints = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for c in complaints:
        dept = session.query(Department).filter_by(id=c.department_id).first()
        comp = session.query(Company).filter_by(id=c.company_id).first()
        worker = session.query(Worker).filter_by(worker_id=c.assigned_worker_id).first()
        result.append({
            "token": c.token,
            "department": dept.name if dept else None,
            "company": comp.name if comp else None,
            "priority": c.priority,
            "status": c.status,
            "stage": c.stage or ("Resolved" if c.status == "resolved" else "Investigation"),
            "is_escalated": bool(c.is_escalated),
            "due_date": str(c.due_date) if c.due_date else None,
            "sla_due_at": str(c.due_date) if c.due_date else None,
            "assigned_worker": worker.name if worker else (c.assigned_worker_id or "Unassigned"),
            "assigned_worker_name": worker.name if worker else (c.assigned_worker_id or "Unassigned"),
            "assigned_worker_id": worker.employee_id if (worker and worker.employee_id) else (c.assigned_worker_id or "—"),
            "created_at": str(c.created_at),
            "resolved_at": str(c.resolved_at) if c.resolved_at else None,
            "reference_id": c.reference_id,
            "amount": c.amount,
            "branch": c.branch,
            "service_type": c.service_type,
            "narrative": c.narrative,
            "description": c.narrative,
            "priority_reason": c.priority_reason,
            "proof_file_path": c.proof_file_path,
            "proof_url": c.proof_file_path,
            "sbert_score": c.sbert_narrative_score,
            "proof_similarity": c.proof_similarity_score,
            "proof_extracted_text": c.proof_extracted_text,
            "rejection_reason": c.rejection_reason,
            "resolution_notes": c.resolution_notes,
            "resolution_proof_url": c.resolution_proof_url,
        })
    session.close()
    return {"total": total_count, "count": len(result), "skip": skip, "limit": limit, "complaints": result}

@app.patch("/admin/complaint/{token}/status")
def update_status(token: str, update: StatusUpdate, admin: str = Depends(verify_admin)):
    valid_statuses = ["open", "in_progress", "resolved", "closed", "rejected"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")

    session = Session()
    complaint = session.query(Complaint).filter_by(token=token).first()
    if not complaint:
        session.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    old_status = complaint.status
    complaint.status = update.status
    if update.stage:
        complaint.stage = update.stage
    elif update.status in ["closed", "rejected"]:
        complaint.stage = "Closed"
    elif update.status == "resolved":
        complaint.stage = "Resolved"
    elif update.status == "in_progress":
        complaint.stage = "Investigation"
    elif update.status == "open":
        complaint.stage = "Triage"

    if update.status == "rejected":
        complaint.rejection_reason = update.rejection_reason or "Complaint rejected due to non-matching transaction details or insufficient documentation."
        complaint.resolved_at = datetime.now()
    elif update.status in ["resolved", "closed"]:
        if not complaint.resolved_at:
            complaint.resolved_at = datetime.now()
        if update.resolution_notes:
            complaint.resolution_notes = update.resolution_notes
        if update.resolution_proof_url:
            complaint.resolution_proof_url = update.resolution_proof_url
    else:
        complaint.resolved_at = None

    new_stage = complaint.stage

    # Trigger alert notification to assigned employee if admin updates complaint
    if complaint.assigned_worker_id:
        try:
            c_cursor = session.connection().connection.cursor()
            c_cursor.execute("""
                INSERT INTO notifications (worker_id, complaint_token, title, message)
                VALUES (?, ?, ?, ?)
            """, (
                complaint.assigned_worker_id,
                token,
                "Admin Override Alert",
                f"Administrator {admin} changed status of grievance {token} to '{update.status}' (Stage: {new_stage})"
            ))
        except Exception:
            pass

    session.commit()
    session.close()
    return {"token": token, "old_status": old_status, "new_status": update.status, "stage": new_stage}

# --- Dedicated Employee Workspace Endpoints ---

@app.get("/employee/complaints")
def get_employee_complaints(
    priority: str | None = None,
    status: str | None = None,
    emp: dict = Depends(verify_employee)
):
    session = Session()
    refresh_sla_escalations(session)
    worker_id = emp["worker_id"]

    query = session.query(Complaint).filter(Complaint.assigned_worker_id == worker_id)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if status:
        query = query.filter(Complaint.status == status)

    complaints = query.order_by(Complaint.due_date.asc()).all()
    results = []
    for c in complaints:
        dept = session.query(Department).filter_by(id=c.department_id).first()
        comp = session.query(Company).filter_by(id=c.company_id).first()
        results.append({
            "token": c.token,
            "company": comp.name if comp else None,
            "department": dept.name if dept else None,
            "priority": c.priority,
            "priority_reason": c.priority_reason,
            "status": c.status,
            "stage": c.stage,
            "due_date": str(c.due_date) if c.due_date else None,
            "sla_due_at": str(c.due_date) if c.due_date else None,
            "is_escalated": bool(c.is_escalated),
            "created_at": str(c.created_at),
            "transaction_date": c.transaction_date,
            "reference_id": c.reference_id,
            "amount": c.amount,
            "branch": c.branch,
            "service_type": c.service_type,
            "narrative": c.narrative,
            "description": c.narrative,
            "proof_file_path": c.proof_file_path,
            "proof_url": c.proof_file_path,
            "sbert_score": c.sbert_narrative_score,
            "proof_similarity": c.proof_similarity_score,
            "proof_extracted_text": c.proof_extracted_text,
            "rejection_reason": c.rejection_reason,
            "resolution_notes": c.resolution_notes,
            "resolution_proof_url": c.resolution_proof_url,
            "requires_more_proof": c.requires_more_proof,
            "customer_appeal": c.customer_appeal,
            "satisfaction_status": c.satisfaction_status,
        })
    session.close()
    return results

@app.post("/employee/complaint/{token}/action")
def employee_take_action(
    token: str,
    action: str = Form(...),  # "investigate", "resolve", "reject", "request_more_proof"
    resolution_notes: str | None = Form(None),
    rejection_reason: str | None = Form(None),
    request_proof_reason: str | None = Form(None),
    proof_doc: UploadFile | None = File(None),
    emp: dict = Depends(verify_employee)
):
    session = Session()
    complaint = session.query(Complaint).filter_by(token=token).first()
    if not complaint:
        session.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    if action == "investigate":
        complaint.status = "in_progress"
        complaint.stage = "Investigation"
    elif action in ["request_proof", "request_more_proof"]:
        complaint.status = "in_progress"
        complaint.stage = "Investigation"
        complaint.requires_more_proof = request_proof_reason or "Additional proof required (bank statement or legible transaction receipt)."
    elif action == "reject":
        complaint.status = "rejected"
        complaint.stage = "Closed"
        complaint.rejection_reason = rejection_reason or "Insufficient documentation or invalid core banking transaction reference."
        complaint.resolved_at = datetime.now()
    elif action == "resolve":
        complaint.status = "resolved"
        complaint.stage = "Resolved"
        complaint.resolved_at = datetime.now()
        complaint.resolution_notes = resolution_notes or "Transaction reconciled through core banking settlement switch."
        if proof_doc:
            ext = os.path.splitext(proof_doc.filename)[1] or ".txt"
            safe_name = f"emp_resolution_{token}_{uuid.uuid4().hex[:6]}{ext}"
            full_path = os.path.join(UPLOAD_DIR, safe_name)
            with open(full_path, "wb") as f:
                f.write(proof_doc.file.read())
            complaint.resolution_proof_url = f"/uploads/{safe_name}"
        else:
            # Auto-generate certified text voucher
            from bot_simulator import generate_resolution_proof
            _, auto_url = generate_resolution_proof(token, complaint.reference_id)
            complaint.resolution_proof_url = auto_url

    session.commit()
    new_status = complaint.status
    session.close()
    return {"message": f"Action '{action}' executed successfully on {token}", "status": new_status}

@app.get("/employee/notifications")
def get_employee_notifications(emp: dict = Depends(verify_employee)):
    session = Session()
    worker_id = emp["worker_id"]
    try:
        c_cursor = session.connection().connection.cursor()
        c_cursor.execute("""
            SELECT id, complaint_token, title, message, is_read, created_at
            FROM notifications
            WHERE worker_id = ?
            ORDER BY id DESC LIMIT 20
        """, (worker_id,))
        rows = c_cursor.fetchall()
        notifs = [{
            "id": r[0],
            "complaint_token": r[1],
            "title": r[2],
            "message": r[3],
            "is_read": bool(r[4]),
            "created_at": str(r[5])
        } for r in rows]
    except Exception:
        notifs = []
    session.close()
    return notifs

# --- Tab 2: Departments & Workers Stats ---
@app.get("/admin/departments-workers")
def get_departments_workers(admin: str = Depends(verify_admin)):
    session = Session()
    refresh_sla_escalations(session)
    
    target_departments = [
        "Digital & UPI Banking",
        "Loans & Advances",
        "Cards & ATM Services",
        "Account & Branch Operations",
        "Fraud & Risk Management"
    ]
    
    dept_records = session.query(Department).filter(Department.name.in_(target_departments)).all()
    results = []

    for dept in dept_records:
        workers = session.query(Worker).filter_by(department_id=dept.id).all()
        workers_data = []
        for w in workers:
            total_assigned = session.query(Complaint).filter_by(assigned_worker_id=w.worker_id).count()
            resolved_count = session.query(Complaint).filter_by(assigned_worker_id=w.worker_id, status="resolved").count()
            in_progress_count = session.query(Complaint).filter_by(assigned_worker_id=w.worker_id, status="in_progress").count()
            open_count = session.query(Complaint).filter_by(assigned_worker_id=w.worker_id, status="open").count()
            late_count = session.query(Complaint).filter(
                Complaint.assigned_worker_id == w.worker_id,
                Complaint.is_escalated == True
            ).count()

            workers_data.append({
                "worker_id": w.worker_id,
                "employee_id": w.employee_id,
                "name": w.name,
                "email": w.email,
                "phone": w.phone,
                "total": total_assigned,
                "total_assigned": total_assigned,
                "resolved": resolved_count,
                "resolved_count": resolved_count,
                "in_progress": in_progress_count,
                "in_progress_count": in_progress_count,
                "open": open_count,
                "open_count": open_count,
                "late_escalated": late_count,
                "escalated_count": late_count,
            })

        dept_total = session.query(Complaint).filter_by(department_id=dept.id).count()
        results.append({
            "department_id": dept.id,
            "department": dept.name,
            "department_name": dept.name,
            "total_complaints": dept_total,
            "workers": workers_data
        })

    session.close()
    return results

# --- Tab 3: Existing Analytics Stats ---
@app.get("/admin/stats")
def get_stats(admin: str = Depends(verify_admin)):
    session = Session()
    refresh_sla_escalations(session)

    total = session.query(Complaint).count()

    status_counts = {}
    for s in ["open", "in_progress", "resolved"]:
        status_counts[s] = session.query(Complaint).filter(Complaint.status == s).count()

    priority_counts = {}
    for p in ["High", "Medium", "Low"]:
        priority_counts[p] = session.query(Complaint).filter(Complaint.priority == p).count()

    departments = session.query(Department).all()
    department_breakdown = []
    for dept in departments:
        dept_total = session.query(Complaint).filter(Complaint.department_id == dept.id).count()
        if dept_total == 0:
            continue
        dept_open = session.query(Complaint).filter(
            Complaint.department_id == dept.id, Complaint.status == "open"
        ).count()
        dept_progress = session.query(Complaint).filter(
            Complaint.department_id == dept.id, Complaint.status == "in_progress"
        ).count()
        dept_resolved = session.query(Complaint).filter(
            Complaint.department_id == dept.id, Complaint.status == "resolved"
        ).count()
        department_breakdown.append({
            "department": dept.name,
            "total": dept_total,
            "open": dept_open,
            "in_progress": dept_progress,
            "resolved": dept_resolved,
        })

    company_counts = (
        session.query(Complaint.company_id, func.count(Complaint.id).label("total"))
        .filter(Complaint.company_id.isnot(None))
        .group_by(Complaint.company_id)
        .order_by(func.count(Complaint.id).desc())
        .limit(15)
        .all()
    )

    company_breakdown = []
    for company_id, comp_total in company_counts:
        comp = session.query(Company).filter_by(id=company_id).first()
        comp_resolved = session.query(Complaint).filter(
            Complaint.company_id == company_id, Complaint.status == "resolved"
        ).count()
        company_breakdown.append({
            "company": comp.name if comp else "Unknown",
            "total": comp_total,
            "resolved": comp_resolved,
        })

    all_feedback = session.query(Feedback).all()
    feedback_count = len(all_feedback)
    if feedback_count > 0:
        avg_rating = sum(f.rating for f in all_feedback) / feedback_count
        positive_count = sum(1 for f in all_feedback if f.rating >= 4)
        positive_percentage = round((positive_count / feedback_count) * 100, 1)
    else:
        avg_rating = None
        positive_percentage = None

    # Form feedback rating breakdown 1 to 5
    rating_counts = {r: 0 for r in range(1, 6)}
    for f in all_feedback:
        if 1 <= f.rating <= 5:
            rating_counts[f.rating] += 1
    feedback_ratings = [{"rating": r, "count": count} for r, count in rating_counts.items()]

    company_counts_list = [{"company": c["company"], "count": c["total"]} for c in company_breakdown]

    escalated_count = session.query(Complaint).filter_by(is_escalated=True).count()
    session.close()

    return {
        "total": total,
        "total_complaints": total,
        "open_count": status_counts.get("open", 0),
        "in_progress_count": status_counts.get("in_progress", 0),
        "resolved_count": status_counts.get("resolved", 0),
        "escalated_count": escalated_count,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "department_breakdown": department_breakdown,
        "dept_status_counts": department_breakdown,
        "company_breakdown": company_breakdown,
        "company_counts": company_counts_list,
        "feedback_ratings": feedback_ratings,
        "feedback_count": feedback_count,
        "avg_rating": round(avg_rating, 2) if avg_rating is not None else None,
        "positive_percentage": positive_percentage,
    }

# --- Tab 4: Bank Leaderboard ---
@app.get("/admin/leaderboard")
def get_bank_leaderboard(timeframe: str = "yearly", admin: str = Depends(verify_admin)):
    """
    Computes live rankings of banks/companies by performance:
    - Faster resolution rate
    - Fewer SLA breaches
    - Timeframe: monthly (last 30d), quarterly (last 90d), yearly (last 365d) / all
    """
    session = Session()
    refresh_sla_escalations(session)
    
    now = datetime.now()
    if timeframe == "monthly":
        start_date = now - timedelta(days=30)
    elif timeframe == "quarterly":
        start_date = now - timedelta(days=90)
    else:
        start_date = now - timedelta(days=365)

    # Query aggregated stats only for companies that actually have complaints in the timeframe
    # Executes in a fraction of a second using a single grouped aggregation query
    stats_query = (
        session.query(
            Complaint.company_id,
            func.count(Complaint.id).label("total"),
            func.sum(case((Complaint.status.in_(["resolved", "closed"]), 1), else_=0)).label("resolved"),
            func.sum(case((Complaint.is_escalated == True, 1), else_=0)).label("breached")
        )
        .filter(Complaint.company_id.isnot(None))
        .filter(Complaint.created_at >= start_date)
        .group_by(Complaint.company_id)
        .having(func.count(Complaint.id) > 0)
        .all()
    )

    # Fetch company names in bulk
    comp_ids = [row[0] for row in stats_query]
    companies = session.query(Company).filter(Company.id.in_(comp_ids)).all() if comp_ids else []
    company_name_map = {c.id: c.name for c in companies}

    leaderboard = []
    for comp_id, total, resolved, breached in stats_query:
        resolved = resolved or 0
        breached = breached or 0
        total = total or 1

        resolution_rate = (resolved / total) * 100
        breach_rate = (breached / total) * 100

        # Authentic BFSI Grievance Index formula:
        # 1. Base Resolution Efficiency (50% weight): (resolved / total) * 50
        # 2. SLA Timeliness Factor (35% weight): (1 - breached / total) * 35
        # 3. Volume Confidence Factor (15% weight): logarithmic dampener so 1 complaint cannot score 100
        import math
        volume_confidence = min(15.0, math.log10(max(1, total) + 1) * 7.5)
        
        # Penalize unresolved backlog
        backlog_penalty = min(15.0, ((total - resolved) / total) * 10.0)

        raw_score = (resolution_rate * 0.50) + ((100.0 - breach_rate) * 0.35 * 0.5) + volume_confidence - backlog_penalty
        perf_score = max(38.0, min(97.5, round(raw_score, 1)))

        comp_name = company_name_map.get(comp_id, f"Institution #{comp_id}")
        leaderboard.append({
            "bank_id": comp_id,
            "bank_name": comp_name,
            "company": comp_name,
            "total_complaints": total,
            "resolved_complaints": resolved,
            "resolved_count": resolved,
            "breached_complaints": breached,
            "escalated_count": breached,
            "resolution_rate": round(resolution_rate, 1),
            "breach_rate": round(breach_rate, 1),
            "performance_score": perf_score,
            "score": perf_score,
            "avg_rating": round(3.0 + (perf_score / 100.0) * 1.9, 1)
        })

    # Sort primarily by realistic performance score descending, then by total complaints volume
    leaderboard.sort(key=lambda x: (x["performance_score"], x["total_complaints"]), reverse=True)

    # Assign ranks
    for rank, entry in enumerate(leaderboard, start=1):
        entry["rank"] = rank

    session.close()
    return {"timeframe": timeframe, "leaderboard": leaderboard[:25]}

# --- Tab 5: AI Grievance Clustering & Trend Analysis ---
@app.get("/admin/complaint-clusters")
def get_complaint_clusters(admin: str = Depends(verify_admin)):
    """
    Groups and separates out similar types of complaints together:
    - Analyzes high-frequency complaint patterns (Fraud rings, UPI timeouts, Unauthorized ATM debits, KYC lockouts)
    - Computes early threat scores and recommended early interventions
    """
    session = Session()

    cluster_definitions = [
        {
            "id": "CLUSTER-FRD-01",
            "title": "Phishing & Unauthorized UPI Debits",
            "category": "Fraud & Risk",
            "keywords": ["unauthorized", "upi", "scam", "otp", "phishing", "hacked", "stolen"],
            "severity": "CRITICAL",
            "mitigation_action": "Enable proactive velocity checks on high-value UPI VPA handles and enforce mandatory step-up SMS OTP alerts."
        },
        {
            "id": "CLUSTER-ATM-02",
            "title": "ATM Cash Retract & Dispense Failures",
            "category": "Cards & ATM Services",
            "keywords": ["atm", "dispensed", "cash", "debited but not received", "card blocked"],
            "severity": "HIGH",
            "mitigation_action": "Initiate automated Switch RRN verification and expedite auto-reversal ledger crediting within 24 hours per RBI mandates."
        },
        {
            "id": "CLUSTER-LND-03",
            "title": "Spurious CIBIL Score Reporting & Hidden EMI Penalties",
            "category": "Loans & Advances",
            "keywords": ["credit score", "cibil", "emi", "interest", "overcharged", "foreclosure", "harassment"],
            "severity": "MEDIUM",
            "mitigation_action": "Audit recovery vendor collection agencies and mandate automated dispute reconciliation API with credit bureaus."
        },
        {
            "id": "CLUSTER-ACC-04",
            "title": "Account Freeze & Re-KYC Friction",
            "category": "Account Operations",
            "keywords": ["kyc", "freeze", "branch", "blocked account", "pan card", "aadhaar", "dormant"],
            "severity": "LOW",
            "mitigation_action": "Deploy instant Video-KYC self-service workflows to unblock operational accounts without branch visit."
        },
        {
            "id": "CLUSTER-UPI-05",
            "title": "UPI Server Timeout & Unreversed Settlement Loops",
            "category": "Digital Payments",
            "keywords": ["timeout", "server", "pending", "debited", "reversal", "npcí", "upi transfer failed"],
            "severity": "CRITICAL",
            "mitigation_action": "AI Core Action: Integrate real-time NPCI Auto-Reversal Webhooks (UPMS). Force credit to sender within T+1 hour and credit penalty compensation per RBI Master Directions."
        },
        {
            "id": "CLUSTER-POS-06",
            "title": "POS Merchant Double Debits & Unsettled Chargebacks",
            "category": "Cards & Merchant POS",
            "keywords": ["charge", "double debited", "swipe", "merchant", "pos", "refund", "receipt"],
            "severity": "HIGH",
            "mitigation_action": "AI Core Action: Deploy automated ISO-8583 payment gateway transaction reconciliation bots to detect duplicate RRNs and execute automated shadow refund credits within 12 hours."
        }
    ]

    total_count = session.query(Complaint).count() or 1
    analyzed_clusters = []

    for c_def in cluster_definitions:
        # Build filter containing keywords
        filters = [Complaint.narrative.ilike(f"%{kw}%") for kw in c_def["keywords"]]
        matched_count = session.query(Complaint).filter(or_(*filters)).count()
        escalated_count = session.query(Complaint).filter(or_(*filters), Complaint.is_escalated == True).count()

        percentage = round((matched_count / total_count) * 100, 1)

        # Fetch sample complaints for this cluster
        samples = [
            c.narrative[:160] + "..."
            for c in session.query(Complaint).filter(or_(*filters)).limit(2).all()
        ]

        analyzed_clusters.append({
            "cluster_id": c_def["id"],
            "cluster_title": c_def["title"],
            "label": c_def["title"],
            "category": c_def["category"],
            "matched_volume": matched_count,
            "count": matched_count,
            "share_percentage": percentage,
            "escalated_count": escalated_count,
            "severity": c_def["severity"],
            "top_keywords": c_def["keywords"][:4],
            "sample_complaints": samples,
            "recommended_action": c_def["mitigation_action"]
        })

    session.close()
    return {"total_analyzed": total_count, "clusters": analyzed_clusters}