from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Complaint, Department, Company, Feedback, User
from jose import JWTError, jwt
import bcrypt
import pickle
import re
from datetime import datetime, timedelta

app = FastAPI(title="GrievanceIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load saved model + vectorizer ---
with open(r"G:\Mini_project\Python_codes\classifier.pkl", "rb") as f:
    classifier = pickle.load(f)
with open(r"G:\Mini_project\Python_codes\vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# --- Database setup ---
engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Session = sessionmaker(bind=engine)

# --- Priority keyword lists ---
HIGH_URGENCY = [
    "fraud", "fraudulent", "unauthorized transaction", "identity theft",
    "stolen", "lawsuit", "legal action", "attorney", "sue", "scam",
    "threatened", "harassment", "discrimination", "police report",
    "illegal", "emergency"
]
MEDIUM_URGENCY = [
    "dispute", "disputed", "incorrect information", "overcharged",
    "denied", "rejected", "late fee", "credit score dropped",
    "frustrated", "delay in resolution"
]

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'X{2,}', ' ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
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

def generate_token(session):
    count = session.query(Complaint).count()
    return f"GRV-2026-{count + 1:05d}"

# --- Auth config ---
SECRET_KEY = "grievanceiq-secret-key-change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return email

# --- Request/response models ---
class ComplaintIn(BaseModel):
    narrative: str
    company: str | None = None

class FeedbackIn(BaseModel):
    rating: int
    comment: str | None = None

class StatusUpdate(BaseModel):
    status: str

class LoginIn(BaseModel):
    email: str
    password: str

# --- Auth endpoint ---
@app.post("/login")
def login(credentials: LoginIn):
    session = Session()
    user = session.query(User).filter_by(email=credentials.email).first()
    session.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(credentials.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

# --- Public endpoints ---

@app.post("/complaint")
def submit_complaint(complaint: ComplaintIn):
    session = Session()

    cleaned = clean_text(complaint.narrative)

    tfidf_vec = vectorizer.transform([cleaned])
    predicted_dept = classifier.predict(tfidf_vec)[0]

    priority, matched_keywords = score_priority(cleaned)

    dept = session.query(Department).filter_by(name=predicted_dept).first()

    comp = None
    if complaint.company:
        comp = session.query(Company).filter_by(name=complaint.company).first()
        if not comp:
            comp = Company(name=complaint.company)
            session.add(comp)
            session.flush()

    token = generate_token(session)

    new_complaint = Complaint(
        token=token,
        narrative=complaint.narrative,
        narrative_clean=cleaned,
        department_id=dept.id if dept else None,
        company_id=comp.id if comp else None,
        priority=priority,
        status="open"
    )
    session.add(new_complaint)
    session.commit()

    result = {
        "token": token,
        "department": predicted_dept,
        "priority": priority,
        "status": "open"
    }
    session.close()
    return result


@app.get("/complaint/{token}")
def get_complaint(token: str):
    session = Session()
    complaint = session.query(Complaint).filter_by(token=token).first()
    if not complaint:
        session.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    dept = session.query(Department).filter_by(id=complaint.department_id).first()

    result = {
        "token": complaint.token,
        "department": dept.name if dept else None,
        "priority": complaint.priority,
        "status": complaint.status,
        "created_at": str(complaint.created_at)
    }
    session.close()
    return result


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
    session.commit()
    session.close()
    return {"message": "Feedback submitted", "token": token}

# --- Protected admin endpoints ---

@app.get("/admin/complaints")
def list_complaints(
    department: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    admin: str = Depends(verify_admin)
):
    session = Session()
    query = session.query(Complaint)

    if department:
        dept = session.query(Department).filter_by(name=department).first()
        if dept:
            query = query.filter(Complaint.department_id == dept.id)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if status:
        query = query.filter(Complaint.status == status)

    total_count = query.count()
    complaints = query.offset(skip).limit(limit).all()

    result = []
    for c in complaints:
        dept = session.query(Department).filter_by(id=c.department_id).first()
        result.append({
            "token": c.token,
            "department": dept.name if dept else None,
            "priority": c.priority,
            "status": c.status,
            "created_at": str(c.created_at)
        })
    session.close()
    return {"total": total_count, "count": len(result), "skip": skip, "limit": limit, "complaints": result}


@app.patch("/admin/complaint/{token}/status")
def update_status(token: str, update: StatusUpdate, admin: str = Depends(verify_admin)):
    valid_statuses = ["open", "in_progress", "resolved"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")

    session = Session()
    complaint = session.query(Complaint).filter_by(token=token).first()
    if not complaint:
        session.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    old_status = complaint.status
    complaint.status = update.status

    if update.status == "resolved":
        complaint.resolved_at = datetime.now()

    session.commit()
    session.close()

    return {"token": token, "old_status": old_status, "new_status": update.status}


@app.get("/admin/stats")
def get_stats(admin: str = Depends(verify_admin)):
    session = Session()

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

    all_feedback = session.query(Feedback).all()
    feedback_count = len(all_feedback)
    if feedback_count > 0:
        avg_rating = sum(f.rating for f in all_feedback) / feedback_count
        positive_count = sum(1 for f in all_feedback if f.rating >= 4)
        positive_percentage = round((positive_count / feedback_count) * 100, 1)
    else:
        avg_rating = None
        positive_percentage = None

    session.close()

    return {
        "total": total,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "department_breakdown": department_breakdown,
        "feedback_count": feedback_count,
        "avg_rating": round(avg_rating, 2) if avg_rating is not None else None,
        "positive_percentage": positive_percentage,
    }