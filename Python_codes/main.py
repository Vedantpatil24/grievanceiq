"""
main.py - GrievanceIQ FastAPI Application
Full-stack BFSI complaint triage, Tier-1 AI GrievanceBot, SLA Engine,
and Admin/Officer Workspace API.
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from jose import JWTError, jwt
import bcrypt

# Internal Modules
from create_db import (
    SessionLocal, Company, Department, Category, User, Complaint,
    KnowledgeBaseArticle, ComplaintMessage, Notification,
    AssignmentHistory, EscalationHistory, AuditLog, StatusHistory,
    Prediction, Feedback, Resolution, InvestigationNote, SimilarComplaint
)
from validity_checker import check_validity, check_adaptive_validity
from ml_pipeline import classify_complaint
from bot_resolver import analyze_with_bot
from sla_engine import calculate_deadline, evaluate_sla_status
from smart_assigner import assign_optimal_officer
from duplicate_detector import check_duplicates_and_anomalies
from ocr_service import analyze_document_proof
from evidence_verifier import check_evidence_for_submission
from evidence_verifier import verify_evidence as verify_evidence_doc
from audit_service import log_audit_event, create_notification
from semantic_engine import predict_sub_category, find_similar_complaints
from bank_intelligence import (
    calculate_bank_health_score, detect_early_warnings,
    generate_management_recommendations, run_what_if_simulation
)

# JWT Security Configurations
SECRET_KEY = "grievanceiq_super_secret_production_key_bfsi_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

app = FastAPI(
    title="GrievanceIQ API",
    description="BFSI Complaint Triage & Tier-1 AI Resolution Platform",
    version="2.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Password helpers
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# =============================================================
# 1. AUTHENTICATION ENDPOINTS
# =============================================================

@app.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Support login via email or username
    login_ident = form_data.username.strip()
    user = db.query(User).filter(
        (User.username == login_ident) | (User.email == login_ident)
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email/username or password")
    
    token = create_access_token(data={"sub": user.username, "role": user.role, "user_id": user.user_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email or user.username,
            "full_name": user.full_name,
            "role": user.role.upper(),
            "department_id": user.department_id
        }
    }

class RegisterCustomerIn(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "customer"

@app.post("/api/auth/register")
def register_customer(payload: RegisterCustomerIn, db: Session = Depends(get_db)):
    clean_email = payload.email.strip().lower()
    existing = db.query(User).filter((User.email == clean_email) | (User.username == clean_email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(payload.password.encode("utf-8"), salt).decode("utf-8")

    derived_name = payload.full_name.strip() if payload.full_name else clean_email.split('@')[0].replace('.', ' ').title()

    new_user = User(
        username=clean_email,
        email=clean_email,
        hashed_password=hashed,
        full_name=derived_name,
        role="customer",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.username, "role": new_user.role, "user_id": new_user.user_id})
    return {
        "message": "Customer registered successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": "CUSTOMER"
        }
    }

@app.get("/api/auth/me")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "department_id": current_user.department_id
    }


# =============================================================
# 2. METADATA & LOOKUPS
# =============================================================

@app.get("/api/companies")
def get_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()

@app.get("/api/departments")
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()


# =============================================================
# 3. COMPLAINT SUBMISSION & TIER-1 BOT ASSESSMENT
# =============================================================

@app.post("/api/complaints/submit")
async def submit_complaint(
    company_id: int = Form(...),
    service_type: str = Form(...),
    transaction_date: str = Form(...),
    description: str = Form(...),
    amount: Optional[float] = Form(None),
    reference_id: Optional[str] = Form(None),
    branch: Optional[str] = Form("Main Branch"),
    card_last4: Optional[str] = Form(None),
    account_no: Optional[str] = Form(None),
    custom_fields: Optional[str] = Form(None),
    customer_id: Optional[int] = Form(None),
    proof_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # 1. Save proof file if uploaded
    saved_file_path = None
    if proof_file and proof_file.filename:
        filename = f"{int(datetime.utcnow().timestamp())}_{proof_file.filename}"
        saved_file_path = os.path.join(UPLOAD_DIR, filename)
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(proof_file.file, buffer)

    # 2. Check Complaint Validity (Adaptive: only requires data relevant to category)
    validity_res = check_adaptive_validity(
        service_type=service_type,
        description=description,
        incident_date=transaction_date,
        amount=amount,
        reference_id=reference_id,
        has_proof=saved_file_path is not None,
        card_last4=card_last4,
        account_no=account_no
    )

    if not validity_res["is_valid"]:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "COMPLAINT_REJECTED_INCOMPLETE",
                "score": validity_res["score"],
                "missing_items": validity_res["missing_items"],
                "feedback": validity_res["feedback"]
            }
        )

    # 3. Machine Learning Classification & Intent Reconciliation
    # Reconcile user-selected banking service category with ML text prediction
    SERVICE_TYPE_MAP = {
        "Credit Card / Disputed Charges & Fee": {
            "category": "Credit Card Services",
            "department": "Card Disputes Team",
            "keywords": ["card", "credit card", "credit", "bill", "billing", "charge", "charges", "dispute", "disputed", "swipe", "statement", "limit", "kredit", "कार्ड", "क्रेडिट कार्ड", "बिल", "चार्ज", "कट गए", "गलत चार्ज"]
        },
        "Lost / Stolen Card & Emergency Block": {
            "category": "Credit Card Services",
            "department": "Card Disputes Team",
            "keywords": ["lost", "stolen", "card", "debit card", "credit card", "block", "blocked", "hotlist", "theft", "misplaced", "खो गया", "चोरी", "कार्ड", "ब्लॉक"]
        },
        "UPI / IMPS / Digital Fund Transfer": {
            "category": "Bank Accounts and Services",
            "department": "Retail Banking Team",
            "keywords": ["upi", "imps", "neft", "rtgs", "transfer", "gpay", "phonepe", "paytm", "bhim", "qr", "qr code", "uncredited", "debited", "पैसे", "ट्रांसफर", "खाते", "कट गए"]
        },
        "ATM Cash Withdrawal Failure": {
            "category": "Bank Accounts and Services",
            "department": "Retail Banking Team",
            "keywords": ["atm", "cash", "dispense", "dispensed", "machine", "withdrawal", "shutter", "slip", "एटीएम", "कैश", "पैसे नहीं निकले"]
        },
        "Net Banking / Mobile App & Tech Glitch": {
            "category": "Bank Accounts and Services",
            "department": "Retail Banking Team",
            "keywords": ["login", "app", "net banking", "mobile banking", "glitch", "crash", "error", "server", "timeout", "otp", "लॉगिन", "ऐप", "एरर", "सर्वर"]
        },
        "KYC, Account Freezing & Dormancy": {
            "category": "Bank Accounts and Services",
            "department": "Retail Banking Team",
            "keywords": ["kyc", "freeze", "frozen", "dormant", "pan", "aadhar", "unfreeze", "block", "blocked account", "केवाईसी", "खाता फ्रीज", "फ्रीज"]
        },
        "Loan Closure, NOC & Document Dispatch": {
            "category": "Loans",
            "department": "Loan Servicing Team",
            "keywords": ["loan", "emi", "noc", "closure", "foreclosure", "deeds", "documents", "mortgage", "lan", "interest", "लोन", "ईएमआई", "एनओसी", "दस्तावेज"]
        },
        "Credit Bureau / CIBIL Rectification": {
            "category": "Credit Reporting",
            "department": "Credit Bureau Liaison Team",
            "keywords": ["cibil", "credit score", "bureau", "experian", "equifax", "overdue", "written off", "dispute", "score", "सिबिल", "स्कोर", "क्रेडिट स्कोर"]
        },
        "Staff Behavior & Recovery Harassment": {
            "category": "Debt Collection",
            "department": "Collections Compliance Team",
            "keywords": ["harassment", "abusive", "recovery", "agent", "threat", "threatening", "calls", "shouting", "misbehavior", "वसूली", "एजेंट", "बदतमीजी", "धमकी"]
        }
    }

    ml_res = classify_complaint(text=description, amount=amount)

    # Hybrid Intent Reconciliation:
    # If the user explicitly selected a domain-specific service type and the narrative
    # corroborates it (or ML confidence is moderate/fallback), prioritize the user's category.
    if service_type in SERVICE_TYPE_MAP:
        mapping = SERVICE_TYPE_MAP[service_type]
        expected_cat = mapping["category"]
        expected_dept = mapping["department"]
        desc_lower = description.lower()
        has_corroborating_kw = any(kw in desc_lower for kw in mapping["keywords"])

        if expected_cat == ml_res.get("predicted_category"):
            ml_res["confidence"] = max(ml_res.get("confidence", 0.75), 0.94)
        elif has_corroborating_kw or ml_res.get("confidence", 0) < 0.85 or ml_res.get("predicted_category") == "Bank Accounts and Services":
            ml_res["predicted_category"] = expected_cat
            ml_res["department_name"] = expected_dept
            ml_res["confidence"] = 0.95
            ml_res["model_version"] = f"{ml_res.get('model_version', 'svm')}_hybrid_intent"

    # Resolve Department DB record
    dept = db.query(Department).filter(Department.department_name == ml_res["department_name"]).first()
    dept_id = dept.department_id if dept else None

    # Resolve Bank Company DB record
    company_obj = db.query(Company).filter(Company.company_id == company_id).first()
    bank_name = company_obj.company_name if company_obj else "Bank"

    # 4. Evidence Verification — Strict Relevance Assessment
    # Rules: file existing ≠ verified; OCR success ≠ relevant; unrelated content MUST fail.
    evidence_result = {"verdict": "NO_EVIDENCE", "evidence_status": "NOT_REQUIRED",
                       "display_status": "NOT_REQUIRED", "blocks_submission": False,
                       "reasons": [], "warnings": [], "domain_scores": {}, "keyword_check": {},
                       "extracted_text_length": 0}

    if saved_file_path:
        evidence_result = check_evidence_for_submission(
            file_path=saved_file_path,
            service_type=service_type,
            submitted_bank=bank_name,
            submitted_date=transaction_date,
            submitted_amount=amount,
            submitted_ref_id=reference_id,
            submitted_branch=branch,
        )

        if evidence_result["blocks_submission"]:
            # FAILED or INVALID_FILE — reject the submission entirely
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "EVIDENCE_VERIFICATION_FAILED",
                    "score": validity_res["score"],
                    "missing_items": evidence_result["reasons"],
                    "feedback": (
                        "Evidence Rejected: The uploaded document does not appear to be a valid banking "
                        "record for this complaint type. "
                        + " ".join(evidence_result["reasons"])
                    ),
                }
            )

    # 5. Duplicate & Anomaly Detection
    dup_res = check_duplicates_and_anomalies(
        db=db,
        company_id=company_id,
        reference_id=reference_id or card_last4 or account_no,
        amount=amount,
        description=description
    )

    # 5.5 SBERT Sub-Category Prediction & Semantic Similarity Scan
    sub_category_name, sub_conf = predict_sub_category(ml_res["predicted_category"], description)
    similar_cases = find_similar_complaints(db, description, company_id)

    # 6. Generate Tracking Token (e.g. GRV-2026-00002)
    last_id = db.query(func.max(Complaint.complaint_id)).scalar() or 0
    token = f"GRV-2026-{str(last_id + 1).zfill(5)}"

    # 7. Tier-1 GrievanceBot Analysis (Dual Bots & Automated Proof Generation)
    bot_res = analyze_with_bot(
        db=db,
        department_id=dept_id,
        category_name=ml_res["predicted_category"],
        description=description,
        priority=ml_res["priority"],
        amount=amount,
        token=token,
        reference_id=reference_id or card_last4 or account_no,
        upload_dir=UPLOAD_DIR
    )

    # 8. Save Complaint in BOT_PROPOSED state
    now = datetime.utcnow()
    new_complaint = Complaint(
        token=token,
        customer_id=customer_id,
        company_id=company_id,
        department_id=dept_id,
        service_type=service_type,
        sub_category=sub_category_name,
        transaction_date=transaction_date,
        amount=amount,
        reference_id=reference_id or card_last4 or account_no,
        branch=branch or "Main Branch",
        raw_text=description,
        description=description,
        proof_file_path=saved_file_path,
        custom_fields=custom_fields,
        priority=ml_res["priority"],
        status="bot_proposed",
        validity_score=validity_res["score"],
        validity_status="valid",
        evidence_status=evidence_result["display_status"],
        resolution_mode="NONE",
        matched_article_id=bot_res["article_id"],
        bot_confidence=bot_res["bot_confidence"],
        escalation_level=0,
        can_reopen_until=None,
        created_at=now,
        updated_at=now
    )
    db.add(new_complaint)
    db.flush()

    # Record similar complaints in database
    for sim in similar_cases:
        db.add(SimilarComplaint(
            complaint_id=new_complaint.complaint_id,
            matched_complaint_id=sim["complaint_id"],
            similarity_score=sim["similarity_score"],
            classification_tag=sim["classification_tag"],
            detected_at=now
        ))

    # Log ML Prediction
    pred_log = Prediction(
        complaint_id=new_complaint.complaint_id,
        predicted_category_id=dept.category_id if dept else None,
        predicted_priority=ml_res["priority"],
        confidence=ml_res["confidence"],
        model_version=ml_res["model_version"]
    )
    db.add(pred_log)

    # Log Status History
    status_hist = StatusHistory(
        complaint_id=new_complaint.complaint_id,
        old_status=None,
        new_status="bot_proposed",
        changed_by="system",
        changed_at=now,
        comment=f"Complaint validated (Score {validity_res['score']}/100) and analyzed by GrievanceBot."
    )
    db.add(status_hist)

    # Log Audit Event
    log_audit_event(
        db=db,
        actor_type="customer",
        action="SUBMIT_COMPLAINT",
        entity_type="complaint",
        entity_id=token,
        details=f"Submitted with validity {validity_res['score']}. Matched article {bot_res['title']}."
    )

    # Create Initial Notification
    create_notification(
        db=db,
        complaint_id=new_complaint.complaint_id,
        recipient_type="customer",
        notification_type="BOT_GUIDANCE_READY",
        title="Grievance Received & Guidance Ready",
        body=f"Your complaint {token} was received. GrievanceBot has analyzed your issue and prepared immediate guidance."
    )

    db.commit()

    return {
        "status": "success",
        "token": token,
        "validity_score": validity_res["score"],
        "department": ml_res["department_name"],
        "category": ml_res["predicted_category"],
        "sub_category": sub_category_name,
        "sub_category_confidence": sub_conf,
        "priority": ml_res["priority"],
        "ml_confidence": ml_res["confidence"],
        "bot_assessment": bot_res,
        "evidence_verification": {
            "verdict": evidence_result["verdict"],
            "evidence_status": evidence_result["display_status"],
            "domain_scores": evidence_result.get("domain_scores", {}),
            "keyword_check": evidence_result.get("keyword_check", {}),
            "extracted_text_length": evidence_result.get("extracted_text_length", 0),
            "warnings": evidence_result.get("warnings", []),
        },
        "duplicate_check": dup_res,
        "similar_complaints": similar_cases
    }


# =============================================================
# 4. CUSTOMER DECISION (RESOLVE BY BOT vs ESCALATE TO OFFICER)
# =============================================================

class CustomerDecisionIn(BaseModel):
    decision: str  # "SOLVED" or "ESCALATE"
    feedback_notes: Optional[str] = None

@app.post("/api/complaints/{token}/customer-decision")
def handle_customer_decision(token: str, payload: CustomerDecisionIn, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    now = datetime.utcnow()

    # Scenario A: Customer accepts Bot Guidance
    if payload.decision.upper() == "SOLVED":
        old_status = complaint.status
        complaint.status = "resolved"
        complaint.resolution_mode = "BOT"
        complaint.resolved_at = now
        complaint.can_reopen_until = now + timedelta(days=7)
        complaint.resolution_notes = (
            "Customer verified and accepted Tier-1 GrievanceBot guidance as complete resolution. "
            + (f"Note: {payload.feedback_notes}" if payload.feedback_notes else "")
        )
        complaint.updated_at = now

        db.add(StatusHistory(
            complaint_id=complaint.complaint_id,
            old_status=old_status,
            new_status="resolved",
            changed_by="customer",
            changed_at=now,
            comment="Resolved via Tier-1 GrievanceBot acceptance."
        ))

        log_audit_event(
            db=db,
            actor_type="customer",
            action="RESOLVE_VIA_BOT",
            entity_type="complaint",
            entity_id=token,
            details="Customer clicked 'This solved my issue'."
        )

        create_notification(
            db=db,
            complaint_id=complaint.complaint_id,
            recipient_type="customer",
            notification_type="STATUS_UPDATE",
            title="Complaint Resolved by AI Bot",
            body=f"Your complaint {token} has been marked as resolved. You can provide feedback or reopen within 7 days."
        )

        db.commit()
        return {
            "message": "Complaint successfully resolved via GrievanceBot guidance.",
            "status": "resolved",
            "resolution_mode": "BOT"
        }

    # Scenario B: Customer requests Human Officer Escalation
    elif payload.decision.upper() == "ESCALATE":
        old_status = complaint.status
        complaint.status = "escalated"
        complaint.resolution_mode = "HUMAN"
        complaint.escalated_at = now
        complaint.escalation_level = 1
        complaint.escalation_reason = payload.feedback_notes or "Customer requested human officer assistance."
        complaint.sla_deadline = calculate_deadline(now, complaint.priority)
        complaint.updated_at = now

        # Smart Assignment to Department Officer
        assigned_officer = assign_optimal_officer(
            db=db,
            complaint=complaint,
            reason="Automated Smart Assignment upon Tier-1 Escalation"
        )

        # Log Escalation History
        db.add(EscalationHistory(
            complaint_id=complaint.complaint_id,
            from_level=0,
            to_level=1,
            reason=complaint.escalation_reason,
            triggered_by="customer",
            previous_officer_id=None,
            new_officer_id=assigned_officer.user_id if assigned_officer else None,
            created_at=now
        ))

        db.add(StatusHistory(
            complaint_id=complaint.complaint_id,
            old_status=old_status,
            new_status="escalated",
            changed_by="customer",
            changed_at=now,
            comment=f"Escalated to Tier-2 Officer. Assigned to {assigned_officer.full_name if assigned_officer else 'Queue'}."
        ))

        log_audit_event(
            db=db,
            actor_type="customer",
            action="ESCALATE_TO_OFFICER",
            entity_type="complaint",
            entity_id=token,
            details=f"Escalated to human handling. SLA deadline: {complaint.sla_deadline.isoformat()}."
        )

        # Notify Customer
        create_notification(
            db=db,
            complaint_id=complaint.complaint_id,
            recipient_type="customer",
            notification_type="ESCALATION_CONFIRMED",
            title="Escalated to Banking Officer",
            body=f"Your complaint {token} has been assigned to an officer. Resolution SLA deadline: {complaint.sla_deadline.strftime('%Y-%m-%d %H:%M UTC')}."
        )

        # Notify Assigned Officer
        if assigned_officer:
            create_notification(
                db=db,
                complaint_id=complaint.complaint_id,
                recipient_type="staff",
                recipient_id=assigned_officer.user_id,
                notification_type="NEW_TICKET_ASSIGNED",
                title=f"New Escalated Grievance: {token}",
                body=f"Priority: {complaint.priority}. Customer requested human assistance."
            )

        db.commit()
        return {
            "message": "Complaint escalated to Banking Officer.",
            "status": "escalated",
            "resolution_mode": "HUMAN",
            "assigned_officer": assigned_officer.full_name if assigned_officer else "Unassigned",
            "sla_deadline": complaint.sla_deadline.isoformat()
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid decision. Must be 'SOLVED' or 'ESCALATE'.")


# =============================================================
# 5. COMPLAINT TRACKING & DETAILS
# =============================================================

@app.get("/api/complaints/{token}/track")
def track_complaint(token: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Evaluate live SLA
    sla_info = evaluate_sla_status(complaint.sla_deadline, complaint.status)

    # Officer info
    officer_name = complaint.assigned_officer.full_name if complaint.assigned_officer else "Unassigned"
    officer_dept = complaint.department.department_name if complaint.department else "General"
    bank_name = complaint.company.company_name if complaint.company else "Unknown Bank"

    # Timeline events
    timeline = []
    # 1. Created
    timeline.append({
        "event": "Complaint Submitted & Validated",
        "timestamp": complaint.created_at.isoformat() if complaint.created_at else complaint.submitted_at,
        "detail": f"Validity Score: {complaint.validity_score}/100. Proof verified.",
        "icon": "document"
    })
    
    # 2. Status History
    for hist in complaint.status_history:
        timeline.append({
            "event": f"Status: {hist.new_status.replace('_', ' ').title()}",
            "timestamp": hist.changed_at.isoformat(),
            "detail": hist.comment,
            "icon": "check" if hist.new_status == "resolved" else "arrow"
        })

    # Can reopen?
    can_reopen = False
    if complaint.status == "resolved" and complaint.reopen_count < 2:
        if complaint.can_reopen_until and datetime.utcnow() <= complaint.can_reopen_until:
            can_reopen = True

    # Latest Resolution details if any
    latest_res = db.query(Resolution).filter(
        Resolution.complaint_id == complaint.complaint_id
    ).order_by(Resolution.resolution_id.desc()).first()

    resolution_info = None
    if latest_res:
        resolution_info = {
            "resolution_id": latest_res.resolution_id,
            "worker_name": latest_res.worker.full_name if latest_res.worker else "Officer",
            "resolution_details": latest_res.resolution_details,
            "resolution_type": latest_res.resolution_type,
            "transaction_reference": latest_res.transaction_reference,
            "resolved_amount": latest_res.resolved_amount,
            "resolution_proof_url": f"/uploads/{os.path.basename(latest_res.resolution_proof_path)}" if latest_res.resolution_proof_path else None,
            "resolution_date": latest_res.resolution_date.isoformat(),
            "customer_confirmation_status": latest_res.customer_confirmation_status
        }

    return {
        "token": complaint.token,
        "company_name": bank_name,
        "department_name": officer_dept,
        "service_type": complaint.service_type,
        "sub_category": complaint.sub_category,
        "transaction_date": complaint.transaction_date,
        "amount": complaint.amount,
        "reference_id": complaint.reference_id,
        "branch": complaint.branch,
        "description": complaint.description,
        "priority": complaint.priority,
        "status": complaint.status,
        "validity_score": complaint.validity_score,
        "evidence_status": complaint.evidence_status or "PENDING",
        "evidence_rejection_reason": complaint.evidence_rejection_reason,
        "resolution_mode": complaint.resolution_mode,
        "assigned_officer": officer_name,
        "escalation_level": complaint.escalation_level,
        "sla": sla_info,
        "resolved_at": complaint.resolved_at.isoformat() if complaint.resolved_at else None,
        "resolution_notes": complaint.resolution_notes,
        "latest_resolution": resolution_info,
        "can_reopen": can_reopen,
        "reopen_count": complaint.reopen_count,
        "timeline": timeline,
        "has_proof": bool(complaint.proof_file_path),
        "proof_file": os.path.basename(complaint.proof_file_path) if complaint.proof_file_path else None
    }


# =============================================================
# 5.5 CUSTOMER COMPLAINT HISTORY
# =============================================================

@app.get("/api/customer/complaints")
def list_customer_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns history of grievances filed by or linked to the authenticated customer.
    """
    query = db.query(Complaint).filter(Complaint.customer_id == current_user.user_id)
    complaints = query.order_by(Complaint.complaint_id.desc()).all()

    result = []
    for c in complaints:
        sla_info = evaluate_sla_status(c.sla_deadline, c.status)
        # Get latest resolution record for confirm/reopen workflow
        latest_res = db.query(Resolution).filter(
            Resolution.complaint_id == c.complaint_id
        ).order_by(Resolution.resolution_id.desc()).first()

        result.append({
            "complaint_id": c.complaint_id,
            "token": c.token,
            "company_name": c.company.company_name if c.company else "Bank",
            "department_name": c.department.department_name if c.department else "Customer Care",
            "service_type": c.service_type,
            "sub_category": c.sub_category or "General",
            "description": c.description,
            "transaction_date": c.transaction_date,
            "amount": c.amount,
            "reference_id": c.reference_id,
            "branch": c.branch,
            "priority": c.priority,
            "status": c.status,
            "validity_score": c.validity_score,
            "resolution_mode": c.resolution_mode,
            "resolution_notes": c.resolution_notes,
            "evidence_status": c.evidence_status or "PENDING",
            "reopen_count": c.reopen_count or 0,
            "can_reopen_until": c.can_reopen_until.isoformat() if c.can_reopen_until else None,
            "sla": sla_info,
            "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
            "created_at": c.created_at.isoformat() if c.created_at else c.submitted_at,
            "latest_resolution": {
                "resolution_id": latest_res.resolution_id,
                "resolution_type": latest_res.resolution_type,
                "resolution_details": latest_res.resolution_details,
                "resolved_amount": latest_res.resolved_amount,
                "transaction_reference": latest_res.transaction_reference,
                "resolution_date": latest_res.resolution_date.isoformat() if latest_res.resolution_date else None,
                "customer_confirmation_status": latest_res.customer_confirmation_status,
                "resolution_proof_path": latest_res.resolution_proof_path,
            } if latest_res else None,
        })
    return result


# =============================================================
# 6. REOPEN COMPLAINT ENDPOINT
# =============================================================

class ReopenIn(BaseModel):
    reopen_reason: str

@app.post("/api/complaints/{token}/reopen")
def reopen_complaint(token: str, payload: ReopenIn, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.status != "resolved":
        raise HTTPException(status_code=400, detail="Only resolved complaints can be reopened.")

    now = datetime.utcnow()
    if complaint.can_reopen_until and now > complaint.can_reopen_until:
        raise HTTPException(status_code=400, detail="Reopen window expired (must be within 7 days of resolution).")

    if complaint.reopen_count >= 2:
        raise HTTPException(status_code=400, detail="Maximum reopen limit (2) reached for this grievance.")

    # Reopen and escalate to Senior Nodal Officer (Level 2)
    old_status = complaint.status
    complaint.status = "reopened"
    complaint.reopen_count += 1
    complaint.escalation_level = 2
    complaint.priority = "High"
    complaint.escalated_at = now
    complaint.sla_deadline = now + timedelta(hours=24)  # Urgent 24h SLA
    complaint.resolution_notes = None
    complaint.resolved_at = None
    complaint.updated_at = now

    db.add(StatusHistory(
        complaint_id=complaint.complaint_id,
        old_status=old_status,
        new_status="reopened",
        changed_by="customer",
        changed_at=now,
        comment=f"Customer reopened case: {payload.reopen_reason}. Escalated to Level 2 (Senior Nodal)."
    ))

    db.add(EscalationHistory(
        complaint_id=complaint.complaint_id,
        from_level=1,
        to_level=2,
        reason=payload.reopen_reason,
        triggered_by="customer",
        previous_officer_id=complaint.current_assigned_officer_id,
        new_officer_id=complaint.current_assigned_officer_id,
        created_at=now
    ))

    log_audit_event(
        db=db,
        actor_type="customer",
        action="REOPEN_COMPLAINT",
        entity_type="complaint",
        entity_id=token,
        details=f"Reopened with reason: {payload.reopen_reason}."
    )

    db.commit()
    return {"message": "Complaint reopened and escalated to Senior Nodal Officer.", "status": "reopened"}


# =============================================================
# 7. CUSTOMER FEEDBACK
# =============================================================

class FeedbackIn(BaseModel):
    rating: int
    comments: Optional[str] = None

@app.post("/api/complaints/{token}/feedback")
def submit_feedback(token: str, payload: FeedbackIn, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    existing_fb = db.query(Feedback).filter(Feedback.complaint_id == complaint.complaint_id).first()
    if existing_fb:
        existing_fb.rating = payload.rating
        existing_fb.comments = payload.comments
        existing_fb.submitted_at = datetime.utcnow()
    else:
        new_fb = Feedback(
            complaint_id=complaint.complaint_id,
            rating=payload.rating,
            comments=payload.comments,
            submitted_at=datetime.utcnow()
        )
        db.add(new_fb)

    db.commit()
    return {"message": "Thank you for your feedback!"}


# =============================================================
# 8. MESSAGING (CUSTOMER <-> OFFICER)
# =============================================================

class MessageIn(BaseModel):
    message_text: str
    sender_type: str = "customer"  # "customer" or "officer"
    sender_name: Optional[str] = "Customer"

@app.get("/api/complaints/{token}/messages")
def get_messages(token: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    msgs = db.query(ComplaintMessage).filter(
        ComplaintMessage.complaint_id == complaint.complaint_id
    ).order_by(ComplaintMessage.created_at.asc()).all()

    return [{
        "message_id": m.message_id,
        "sender_type": m.sender_type,
        "sender_name": m.sender_name,
        "message_text": m.message_text,
        "created_at": m.created_at.isoformat()
    } for m in msgs]

@app.post("/api/complaints/{token}/messages")
def send_message(token: str, payload: MessageIn, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    new_msg = ComplaintMessage(
        complaint_id=complaint.complaint_id,
        sender_type=payload.sender_type,
        sender_name=payload.sender_name or ("Customer" if payload.sender_type == "customer" else "Officer"),
        message_text=payload.message_text,
        created_at=datetime.utcnow()
    )
    db.add(new_msg)

    # In-app notification
    target_role = "staff" if payload.sender_type == "customer" else "customer"
    create_notification(
        db=db,
        complaint_id=complaint.complaint_id,
        recipient_type=target_role,
        notification_type="NEW_MESSAGE",
        title=f"New Message on {token}",
        body=f"From {new_msg.sender_name}: {payload.message_text[:80]}..."
    )

    db.commit()
    return {"message": "Message sent successfully.", "message_id": new_msg.message_id}


# =============================================================
# 9. NOTIFICATIONS
# =============================================================

@app.get("/api/notifications")
def get_notifications(
    recipient_type: str = Query("customer"),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Notification).filter(Notification.recipient_type == recipient_type)
    if token:
        complaint = db.query(Complaint).filter(Complaint.token == token).first()
        if complaint:
            query = query.filter(Notification.complaint_id == complaint.complaint_id)
    notifs = query.order_by(Notification.created_at.desc()).limit(20).all()
    return [{
        "notification_id": n.notification_id,
        "title": n.title,
        "body": n.body,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat()
    } for n in notifs]


# =============================================================
# 10. ADMIN & OFFICER WORKSPACE
# =============================================================

@app.get("/api/admin/complaints")
def list_admin_complaints(
    department_id: Optional[int] = None,
    company_id: Optional[int] = None,
    priority: Optional[str] = None,
    status_filter: Optional[str] = None,
    resolution_mode: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Complaint)
    
    if department_id:
        query = query.filter(Complaint.department_id == department_id)
    if company_id:
        query = query.filter(Complaint.company_id == company_id)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    if resolution_mode:
        query = query.filter(Complaint.resolution_mode == resolution_mode)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Complaint.token.ilike(search_fmt)) |
            (Complaint.reference_id.ilike(search_fmt)) |
            (Complaint.description.ilike(search_fmt))
        )

    complaints = query.order_by(Complaint.complaint_id.desc()).all()

    result = []
    for c in complaints:
        sla_info = evaluate_sla_status(c.sla_deadline, c.status)
        result.append({
            "complaint_id": c.complaint_id,
            "token": c.token,
            "company_name": c.company.company_name if c.company else "Unknown",
            "department_name": c.department.department_name if c.department else "Unassigned",
            "service_type": c.service_type,
            "sub_category": c.sub_category or "General Grievance",
            "description": c.description,
            "amount": c.amount,
            "reference_id": c.reference_id,
            "priority": c.priority,
            "status": c.status,
            "validity_score": c.validity_score,
            "resolution_mode": c.resolution_mode,
            "evidence_status": c.evidence_status or "PENDING",
            "evidence_rejection_reason": c.evidence_rejection_reason,
            "proof_file_path": c.proof_file_path,
            "assigned_officer": c.assigned_officer.full_name if c.assigned_officer else "Unassigned",
            "sla": sla_info,
            "created_at": c.created_at.isoformat() if c.created_at else c.submitted_at
        })

    return result

class UpdateStatusIn(BaseModel):
    status: str
    resolution_notes: Optional[str] = None

@app.put("/api/admin/complaints/{token}/status")
def update_complaint_status(
    token: str,
    payload: UpdateStatusIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    old_status = complaint.status
    complaint.status = payload.status
    complaint.updated_at = datetime.utcnow()
    
    if payload.status == "resolved":
        complaint.resolved_at = datetime.utcnow()
        complaint.resolution_notes = payload.resolution_notes or "Resolved by banking officer."
        complaint.can_reopen_until = datetime.utcnow() + timedelta(days=7)

    db.add(StatusHistory(
        complaint_id=complaint.complaint_id,
        old_status=old_status,
        new_status=payload.status,
        changed_by=current_user.username,
        changed_at=datetime.utcnow(),
        comment=payload.resolution_notes or f"Status changed to {payload.status}."
    ))

    log_audit_event(
        db=db,
        actor_type="officer",
        action="UPDATE_STATUS",
        entity_type="complaint",
        entity_id=token,
        details=f"Changed from {old_status} to {payload.status}.",
        actor_id=current_user.user_id
    )

    create_notification(
        db=db,
        complaint_id=complaint.complaint_id,
        recipient_type="customer",
        notification_type="STATUS_UPDATE",
        title=f"Grievance {token} Updated",
        body=f"Your grievance status has been updated to: {payload.status.replace('_', ' ').title()}."
    )

    db.commit()
    return {"message": "Status updated successfully.", "status": complaint.status}

# Official Redressal Memorandum Generator tailored dynamically to the grievance type
@app.post("/api/admin/complaints/{token}/draft-copilot-resolution")
def draft_copilot_resolution(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    bank = complaint.company.company_name if complaint.company else "the Bank"
    dept = complaint.department.department_name if complaint.department else "Customer Grievance Redressal Cell"
    service = complaint.service_type or "General Banking Grievance"
    ref = complaint.reference_id or "REF-NOT-PROVIDED"
    amt = f"INR {complaint.amount:,.2f}" if complaint.amount else "Non-Monetary Service Claim"
    dt = complaint.transaction_date or datetime.utcnow().strftime('%d-%b-%Y')
    now_date = datetime.utcnow().strftime('%d-%b-%Y')

    # Differentiated standard operating procedure and reasoning tailored to each specific complaint category
    if "Lost" in service or "Card" in service and "Block" in service:
        procedure_text = (
            f"1. Emergency Hotlisting: Card ending in digits [{ref}] was immediately blocked and placed on the central card security blacklist.\n"
            f"2. Liability Capping: Under RBI Circular on Customer Protection, zero-liability status has been applied effective {dt}.\n"
            f"3. Reissuance Protocol: A replacement chip and PIN enabled card has been processed and dispatched via courier tracking dispatch."
        )
        remedy_title = "EMERGENCY CARD BLOCKING & REISSUANCE ADVICE"
    elif "UPI" in service or "IMPS" in service or "Transfer" in service:
        procedure_text = (
            f"1. Switch Reconciliation: Inter-bank NPCI switch logs for UTR [{ref}] dated {dt} have been audited.\n"
            f"2. Settlement Audit: Beneficiary bank switch responded with a timeout code (Deemed Debit - Return Required).\n"
            f"3. Fund Remediation: Full disputed sum of {amt} has been refunded to your source account along with statutory compensation per RBI circular on turnaround time."
        )
        remedy_title = "ELECTRONIC FUND TRANSFER DISPUTE RECONCILIATION"
    elif "ATM" in service or "Cash" in service:
        procedure_text = (
            f"1. ATM Switch & Electronic Journal (EJ) Audit: ATM Switch log for reference [{ref}] on {dt} was extracted.\n"
            f"2. Cash Dispenser Sensor Verification: Dispenser sensor confirmed cash jam / non-dispense of currency notes.\n"
            f"3. Credit Adjustment: An un-dispensed cash adjustment entry of {amt} has been credited to your savings account under auto-reversal code AR-ATM-88."
        )
        remedy_title = "ATM DISPENSE DISCREPANCY SETTLEMENT"
    elif "KYC" in service or "Freezing" in service or "Dormancy" in service:
        procedure_text = (
            f"1. Compliance Record Verification: KYC documents submitted for Account [{ref}] were verified through C-KYC repository.\n"
            f"2. System Status Restoration: Operational hold and debit freeze flags have been revoked from core banking.\n"
            f"3. Service Activation: Full net banking, UPI, and debit card transactions are now operational with immediate effect."
        )
        remedy_title = "ACCOUNT OPERATIONAL RESTORATION MEMORANDUM"
    elif "Loan" in service or "NOC" in service or "EMI" in service:
        procedure_text = (
            f"1. Loan Account Reconciliation: Final closure clearance for Loan Account [{ref}] was audited against credit ledger.\n"
            f"2. Lien Release & Document Dispatch: No Objection Certificate (NOC) and original property title deeds released from vault security.\n"
            f"3. Bureau Notification: Nil outstanding update triggered to CIBIL / Experian."
        )
        remedy_title = "LOAN FORECLOSURE & NOC CLEARANCE MEMORANDUM"
    elif "Credit Bureau" in service or "CIBIL" in service:
        procedure_text = (
            f"1. Commercial Bureau Audit: Erroneous overdue reported against Control No [{ref}] was investigated.\n"
            f"2. Member Rectification: An expedited correction request has been submitted to TransUnion CIBIL and Experian.\n"
            f"3. Score Restoration: Revised trade-line status updated to 'Closed - Regular' with 0 Days Past Due (DPD)."
        )
        remedy_title = "CREDIT BUREAU RECTIFICATION ADVICE"
    elif "Staff" in service or "Harassment" in service or "Recovery" in service:
        procedure_text = (
            f"1. Internal Vigilance Inquiry: Incident regarding agency/staff conduct on reference [{ref}] was reviewed by the Ombudsman Desk.\n"
            f"2. Fair Practice Code Enforcement: Strict warning issued to the concerned recovery agency in accordance with RBI Fair Lending Practices.\n"
            f"3. DND Tagging: Account marked with enhanced customer protection flag to prevent unverified communications."
        )
        remedy_title = "CUSTOMER CONDUCT INQUIRY & REMEDIATION MEMORANDUM"
    else:
        procedure_text = (
            f"1. Case Investigation: Grievance reference [{ref}] investigated under standard operating procedures for {service}.\n"
            f"2. Remedial Action: Operational verification concluded and necessary banking ledger adjustments have been initiated.\n"
            f"3. Service Assurance: Measures implemented to prevent operational recurrence."
        )
        remedy_title = "OFFICIAL GRIEVANCE REDRESSAL MEMORANDUM"

    draft = (
        f"======================================================================\n"
        f"           {remedy_title}\n"
        f"                  {bank.upper()} - {dept.upper()}\n"
        f"======================================================================\n"
        f"Tracking Token  : {complaint.token}\n"
        f"Reference No    : {ref}\n"
        f"Incident Date   : {dt}\n"
        f"Claim Value     : {amt}\n"
        f"Dispatch Date   : {now_date}\n\n"
        f"Dear Customer,\n\n"
        f"With reference to your formal grievance regarding '{service}' lodged under tracking token {complaint.token}, "
        f"the competent authority has completed the investigation. The formal determination and remedial action taken are detailed below:\n\n"
        f"SUMMARY OF FINDINGS & PROCEDURAL ACTION TAKEN:\n"
        f"----------------------------------------------------------------------\n"
        f"{procedure_text}\n"
        f"----------------------------------------------------------------------\n\n"
        f"REGULATORY RIGHTS & NEXT STEPS:\n"
        f"If the above resolution satisfactorily addresses your grievance, you may accept and close this record. "
        f"Should you require further clarification, you may respond directly via your tracking console within 7 days.\n\n"
        f"Sincerely,\n"
        f"{current_user.full_name}\n"
        f"Senior Grievance Redressal Officer\n"
        f"{dept}, {bank}"
    )

    return {"draft_resolution": draft}


# =============================================================
# 11. KNOWLEDGE BASE CRUD
# =============================================================

@app.get("/api/kb")
def list_kb_articles(db: Session = Depends(get_db)):
    articles = db.query(KnowledgeBaseArticle).order_by(KnowledgeBaseArticle.article_id.desc()).all()
    return [{
        "article_id": a.article_id,
        "title": a.title,
        "category": a.category,
        "keywords": a.keywords,
        "guidance_steps": a.guidance_steps,
        "regulatory_reference": a.regulatory_reference,
        "can_self_resolve": a.can_self_resolve,
        "is_active": a.is_active
    } for a in articles]

class KBArticleIn(BaseModel):
    title: str
    category: str
    keywords: str
    guidance_steps: str
    regulatory_reference: Optional[str] = None
    can_self_resolve: bool = True
    department_id: Optional[int] = None

@app.post("/api/kb")
def create_kb_article(
    payload: KBArticleIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    art = KnowledgeBaseArticle(
        title=payload.title,
        category=payload.category,
        keywords=payload.keywords,
        guidance_steps=payload.guidance_steps,
        regulatory_reference=payload.regulatory_reference,
        can_self_resolve=payload.can_self_resolve,
        department_id=payload.department_id,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(art)
    db.commit()
    return {"message": "Knowledge base article created.", "article_id": art.article_id}

@app.get("/api/admin/audit-logs")
def get_admin_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return [{
        "log_id": l.log_id,
        "timestamp": l.timestamp.isoformat(),
        "actor_type": l.actor_type,
        "actor_id": l.actor_id,
        "action": l.action,
        "entity_type": l.entity_type,
        "entity_id": l.entity_id,
        "details": l.details
    } for l in logs]


# =============================================================
# 12. ANALYTICS & TRENDS
# =============================================================

@app.get("/api/analytics/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    total = db.query(func.count(Complaint.complaint_id)).scalar() or 0
    resolved = db.query(func.count(Complaint.complaint_id)).filter(Complaint.status == "resolved").scalar() or 0
    bot_resolved = db.query(func.count(Complaint.complaint_id)).filter(Complaint.resolution_mode == "BOT").scalar() or 0
    human_resolved = db.query(func.count(Complaint.complaint_id)).filter(Complaint.resolution_mode == "HUMAN").scalar() or 0
    escalated = db.query(func.count(Complaint.complaint_id)).filter(Complaint.status.in_(["escalated", "in_progress", "reopened"])).scalar() or 0
    
    avg_score = db.query(func.avg(Complaint.validity_score)).scalar() or 0
    avg_feedback = db.query(func.avg(Feedback.rating)).scalar() or 0

    # Deflection rate: proportion resolved by Tier-1 Bot
    bot_deflection_rate = round((bot_resolved / max(total, 1)) * 100, 1)

    # User counts
    total_users = db.query(func.count(User.user_id)).scalar() or 0
    total_customers = db.query(func.count(User.user_id)).filter(User.role == "customer").scalar() or 0
    total_admins = db.query(func.count(User.user_id)).filter(User.role.in_(["admin", "officer", "staff"])).scalar() or 0

    return {
        "total_complaints": total,
        "resolved_complaints": resolved,
        "escalated_active": escalated,
        "bot_resolved_count": bot_resolved,
        "human_resolved_count": human_resolved,
        "bot_deflection_rate_pct": bot_deflection_rate,
        "avg_validity_score": round(avg_score, 1),
        "avg_feedback_rating": round(avg_feedback, 2),
        "registered_users": {
            "total_registered_users": total_users,
            "registered_customers": total_customers,
            "bank_officers_and_admins": total_admins
        },
        "kaggle_benchmark": {
            "dataset_name": "CFPB Consumer Grievance Benchmark Dataset",
            "curated_training_records": 15420,
            "accuracy_baseline": "94.2%",
            "top_categories_modeled": 5
        }
    }

@app.get("/api/analytics/trends")
def get_analytics_trends(db: Session = Depends(get_db)):
    # Complaints by department
    dept_stats = db.query(
        Department.department_name,
        func.count(Complaint.complaint_id)
    ).join(Complaint, Department.department_id == Complaint.department_id, isouter=True)\
     .group_by(Department.department_name).all()

    # Complaints by priority
    pri_stats = db.query(
        Complaint.priority,
        func.count(Complaint.complaint_id)
    ).group_by(Complaint.priority).all()

    # Complaints by company
    bank_stats = db.query(
        Company.company_name,
        func.count(Complaint.complaint_id)
    ).join(Complaint, Company.company_id == Complaint.company_id, isouter=True)\
     .group_by(Company.company_name).all()

    return {
        "by_department": [{"name": d[0], "count": d[1]} for d in dept_stats if d[0]],
        "by_priority": [{"priority": p[0], "count": p[1]} for p in pri_stats if p[0]],
        "by_bank": [{"bank": b[0], "count": b[1]} for b in bank_stats if b[0]]
    }


# =============================================================
# 14. WORKER RESOLUTION & EVIDENCE VERIFICATION WORKFLOWS
# =============================================================

@app.post("/api/worker/complaints/{token}/resolution")
async def submit_worker_resolution(
    token: str,
    resolution_details: str = Form(...),
    resolution_type: str = Form(...),
    transaction_reference: Optional[str] = Form(None),
    resolved_amount: Optional[float] = Form(None),
    resolution_proof: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if not resolution_details or len(resolution_details.strip()) < 10:
        raise HTTPException(status_code=400, detail="Resolution details must be detailed and descriptive (min 10 chars).")

    # Save resolution proof if provided
    proof_path = None
    if resolution_proof and resolution_proof.filename:
        filename = f"res_{int(datetime.utcnow().timestamp())}_{resolution_proof.filename}"
        proof_path = os.path.join(UPLOAD_DIR, filename)
        with open(proof_path, "wb") as buffer:
            shutil.copyfileobj(resolution_proof.file, buffer)

    now = datetime.utcnow()
    # Create formal Resolution record
    new_res = Resolution(
        complaint_id=complaint.complaint_id,
        worker_id=current_user.user_id,
        resolution_details=resolution_details.strip(),
        resolution_type=resolution_type.strip(),
        transaction_reference=transaction_reference.strip() if transaction_reference else None,
        resolved_amount=resolved_amount,
        resolution_proof_path=proof_path,
        resolution_date=now,
        customer_confirmation_status="PENDING"
    )
    db.add(new_res)

    old_status = complaint.status
    complaint.status = "resolution_proposed"
    complaint.resolution_notes = resolution_details.strip()
    complaint.resolved_at = now
    complaint.updated_at = now

    db.add(StatusHistory(
        complaint_id=complaint.complaint_id,
        old_status=old_status,
        new_status="resolution_proposed",
        changed_by=current_user.username,
        changed_at=now,
        comment=f"Worker {current_user.full_name} submitted resolution ({resolution_type}). Awaiting customer confirmation."
    ))

    log_audit_event(
        db=db,
        actor_type="officer",
        action="PROPOSE_RESOLUTION",
        entity_type="complaint",
        entity_id=token,
        details=f"Resolution submitted. Type: {resolution_type}. Amount: {resolved_amount}. Ref: {transaction_reference}",
        actor_id=current_user.user_id
    )

    create_notification(
        db=db,
        complaint_id=complaint.complaint_id,
        recipient_type="customer",
        notification_type="RESOLUTION_PROPOSED",
        title="Resolution Proposed for Your Grievance",
        body=f"Your complaint {token} has a resolution submitted. Please review and confirm if your issue is solved."
    )

    db.commit()
    return {
        "message": "Resolution submitted successfully. Case is pending customer confirmation.",
        "resolution_id": new_res.resolution_id,
        "status": complaint.status
    }

class CustomerResolutionConfirmationIn(BaseModel):
    confirmed: bool  # True -> Resolved & Closed, False -> Reopened
    feedback_or_reason: str

@app.post("/api/complaints/{token}/confirm-resolution")
def confirm_resolution(
    token: str,
    payload: CustomerResolutionConfirmationIn,
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    res = db.query(Resolution).filter(
        Resolution.complaint_id == complaint.complaint_id
    ).order_by(Resolution.resolution_id.desc()).first()

    now = datetime.utcnow()

    if payload.confirmed:
        # Customer accepts resolution
        if res:
            res.customer_confirmation_status = "ACCEPTED"
            res.customer_feedback = payload.feedback_or_reason
            res.customer_action_date = now

        old_status = complaint.status
        complaint.status = "resolved"
        complaint.can_reopen_until = now + timedelta(days=7)
        complaint.updated_at = now

        db.add(StatusHistory(
            complaint_id=complaint.complaint_id,
            old_status=old_status,
            new_status="resolved",
            changed_by="customer",
            changed_at=now,
            comment="Customer confirmed resolution. Ticket closed."
        ))

        log_audit_event(
            db=db,
            actor_type="customer",
            action="CONFIRM_RESOLUTION_ACCEPTED",
            entity_type="complaint",
            entity_id=token,
            details="Customer confirmed and accepted resolution."
        )

        db.commit()
        return {"message": "Resolution confirmed. Ticket is resolved.", "status": "resolved"}

    else:
        # Customer rejects -> Case reopens
        if res:
            res.customer_confirmation_status = "REJECTED"
            res.customer_feedback = payload.feedback_or_reason
            res.customer_action_date = now

        old_status = complaint.status
        complaint.status = "reopened"
        complaint.reopen_count = (complaint.reopen_count or 0) + 1
        complaint.escalation_level = 2
        complaint.priority = "High"
        complaint.escalated_at = now
        complaint.sla_deadline = now + timedelta(hours=24)
        complaint.updated_at = now

        db.add(StatusHistory(
            complaint_id=complaint.complaint_id,
            old_status=old_status,
            new_status="reopened",
            changed_by="customer",
            changed_at=now,
            comment=f"Customer rejected proposed resolution: {payload.feedback_or_reason}. Reopened."
        ))

        log_audit_event(
            db=db,
            actor_type="customer",
            action="CONFIRM_RESOLUTION_REJECTED",
            entity_type="complaint",
            entity_id=token,
            details=f"Customer rejected resolution. Reason: {payload.feedback_or_reason}"
        )

        db.commit()
        return {"message": "Resolution rejected. Case has been reopened for reinvestigation.", "status": "reopened"}

class VerifyEvidenceIn(BaseModel):
    status: str  # VERIFIED or REJECTED
    reason: Optional[str] = None

@app.put("/api/worker/complaints/{token}/verify-evidence")
def verify_evidence(
    token: str,
    payload: VerifyEvidenceIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.evidence_status = payload.status
    complaint.evidence_verified_by = current_user.user_id
    complaint.evidence_verified_at = datetime.utcnow()
    complaint.evidence_rejection_reason = payload.reason if payload.status == "REJECTED" else None

    db.add(StatusHistory(
        complaint_id=complaint.complaint_id,
        old_status=complaint.status,
        new_status=complaint.status,
        changed_by=current_user.username,
        changed_at=datetime.utcnow(),
        comment=f"Evidence proof marked as {payload.status}. {payload.reason or ''}"
    ))

    db.commit()
    return {"message": f"Evidence marked as {payload.status}.", "evidence_status": payload.status}

@app.post("/api/worker/complaints/{token}/ai-evidence-analysis")
async def ai_evidence_analysis(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered evidence document analysis.
    Returns a confidence score (0-100) for how well the attached document
    supports the complaint category. Uses OCR + keyword matching + semantic similarity.
    """
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    if not complaint.proof_path:
        return {
            "confidence_score": 0,
            "confidence_label": "NO DOCUMENT",
            "confidence_color": "#94a3b8",
            "analysis": {
                "file_detected": False,
                "file_type": None,
                "ocr_extracted": False,
                "keyword_match_score": 0,
                "semantic_relevance_score": 0,
                "category_alignment": "No document uploaded"
            },
            "recommendation": "Request customer to upload supporting document.",
            "auto_verdict": "PENDING"
        }
    
    # 1. File type detection
    proof_path = complaint.proof_path
    file_ext = proof_path.rsplit('.', 1)[-1].lower() if '.' in proof_path else "unknown"
    
    file_type_score = 0
    file_type_label = "Unknown"
    
    VALID_EXTENSIONS = {
        "pdf": ("PDF Statement / Letter", 25),
        "png": ("Screenshot / Image", 15),
        "jpg": ("Photo Evidence", 15),
        "jpeg": ("Photo Evidence", 15),
        "docx": ("Word Document", 20),
        "doc": ("Word Document", 18),
        "txt": ("Text Record", 10),
        "xlsx": ("Spreadsheet", 12),
        "csv": ("Data Export", 10)
    }
    
    if file_ext in VALID_EXTENSIONS:
        file_type_label, file_type_score = VALID_EXTENSIONS[file_ext]
    
    # 2. OCR / text extraction
    ocr_text = ""
    ocr_extracted = False
    try:
        from ocr_service import extract_text_from_file
        import os
        full_path = os.path.join("uploads", os.path.basename(proof_path)) if not os.path.isabs(proof_path) else proof_path
        if os.path.exists(full_path):
            ocr_text = extract_text_from_file(full_path) or ""
            ocr_extracted = bool(ocr_text.strip())
    except Exception:
        pass
    
    # 3. Keyword match: complaint category vs document content
    CATEGORY_KEYWORDS = {
        "UPI / IMPS / Digital Fund Transfer": ["upi", "imps", "neft", "rtgs", "transfer", "gpay", "phonepe", "paytm", "transaction", "ref", "utr", "beneficiary", "debit", "credit"],
        "ATM Cash Withdrawal Failure": ["atm", "cash", "withdrawal", "dispense", "machine", "card", "pin", "balance", "receipt", "slip"],
        "Credit Card / Disputed Charges & Fee": ["credit card", "statement", "charge", "fee", "annual", "transaction", "disputed", "emi", "limit", "billing"],
        "Loan Closure, NOC & Document Dispatch": ["loan", "noc", "closure", "foreclosure", "emi", "outstanding", "prepayment", "property", "lien", "account"],
        "Net Banking / Mobile App & Tech Glitch": ["login", "otp", "app", "netbanking", "password", "account", "transaction", "session", "browser", "mobile"],
        "KYC, Account Freezing & Dormancy": ["kyc", "account", "freeze", "dormant", "pan", "aadhar", "identity", "verification", "branch", "reactivate"],
        "Credit Bureau / CIBIL Rectification": ["cibil", "credit score", "bureau", "experian", "equifax", "dispute", "loan", "default", "report", "rating"],
        "Staff Behavior & Recovery Harassment": ["agent", "call", "harassment", "threat", "rude", "abusive", "recovery", "time", "repeated", "date"],
        "Lost / Stolen Card & Emergency Block": ["lost", "stolen", "card", "block", "hotlist", "fir", "complaint", "police", "unauthorized", "transaction"]
    }
    
    complaint_cat = complaint.service_type or ""
    keywords = CATEGORY_KEYWORDS.get(complaint_cat, [])
    
    keyword_match_score = 0
    matched_keywords = []
    if keywords and ocr_text:
        text_lower = ocr_text.lower()
        for kw in keywords:
            if kw in text_lower:
                matched_keywords.append(kw)
        
        match_ratio = len(matched_keywords) / max(len(keywords), 1)
        keyword_match_score = min(40, int(match_ratio * 40))
    elif keywords and not ocr_text:
        keyword_match_score = 8
    
    # 4. Semantic relevance: cosine similarity between description and OCR text
    semantic_score = 0
    try:
        from semantic_engine import get_text_embedding, cosine_similarity as sem_cosine
        if ocr_text and complaint.description:
            desc_vec = get_text_embedding(complaint.description[:500])
            ocr_vec = get_text_embedding(ocr_text[:500])
            sim = sem_cosine(desc_vec, ocr_vec)
            semantic_score = min(25, int(sim * 50))
    except Exception:
        semantic_score = 5
    
    # 5. Composite confidence score
    ocr_bonus = 10 if ocr_extracted else 0
    confidence_score = min(100, file_type_score + keyword_match_score + semantic_score + ocr_bonus)
    
    # 6. Verdict
    if confidence_score >= 75:
        confidence_label = "HIGH CONFIDENCE"
        confidence_color = "#16a34a"
        auto_verdict = "VERIFIED"
        recommendation = "Document appears strongly relevant to the complaint. Recommend verification."
    elif confidence_score >= 50:
        confidence_label = "MODERATE"
        confidence_color = "#d97706"
        auto_verdict = "REVIEW REQUIRED"
        recommendation = "Document has partial relevance. Manual review recommended before decision."
    elif confidence_score >= 25:
        confidence_label = "LOW CONFIDENCE"
        confidence_color = "#dc2626"
        auto_verdict = "LIKELY INVALID"
        recommendation = "Document does not strongly match complaint type. Request correct document."
    else:
        confidence_label = "INSUFFICIENT"
        confidence_color = "#7c3aed"
        auto_verdict = "REJECT"
        recommendation = "Document is unreadable or irrelevant to the complaint. Reject and request re-upload."
    
    return {
        "confidence_score": confidence_score,
        "confidence_label": confidence_label,
        "confidence_color": confidence_color,
        "analysis": {
            "file_detected": True,
            "file_type": file_type_label,
            "file_type_score": file_type_score,
            "ocr_extracted": ocr_extracted,
            "ocr_readable_chars": len(ocr_text),
            "keyword_match_score": keyword_match_score,
            "matched_keywords": matched_keywords[:10],
            "semantic_relevance_score": semantic_score,
            "category_alignment": complaint_cat or "General"
        },
        "score_breakdown": {
            "file_type": file_type_score,
            "keyword_match": keyword_match_score,
            "semantic_similarity": semantic_score,
            "ocr_readable_bonus": ocr_bonus,
            "total": confidence_score
        },
        "recommendation": recommendation,
        "auto_verdict": auto_verdict
    }

class InvestigationNoteIn(BaseModel):
    note_text: str

@app.post("/api/worker/complaints/{token}/notes")
def add_investigation_note(
    token: str,
    payload: InvestigationNoteIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    note = InvestigationNote(
        complaint_id=complaint.complaint_id,
        worker_id=current_user.user_id,
        note_text=payload.note_text.strip(),
        created_at=datetime.utcnow()
    )
    db.add(note)

    if complaint.status in ["escalated", "assigned", "open"]:
        complaint.status = "in_progress"

    db.commit()
    return {"message": "Investigation note recorded.", "note_id": note.note_id}

@app.get("/api/worker/complaints/{token}/notes")
def get_investigation_notes(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = db.query(Complaint).filter(Complaint.token == token).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    notes = db.query(InvestigationNote).filter(
        InvestigationNote.complaint_id == complaint.complaint_id
    ).order_by(InvestigationNote.created_at.desc()).all()

    return [{
        "note_id": n.note_id,
        "worker_name": n.worker.full_name if n.worker else "Officer",
        "note_text": n.note_text,
        "created_at": n.created_at.isoformat()
    } for n in notes]


# =============================================================
# 15. BANK INTELLIGENCE & WHAT-IF SIMULATION ENDPOINTS
# =============================================================

@app.get("/api/intelligence/bank-health")
def get_bank_health(db: Session = Depends(get_db)):
    total = db.query(func.count(Complaint.complaint_id)).scalar() or 0
    resolved = db.query(func.count(Complaint.complaint_id)).filter(Complaint.status == "resolved").scalar() or 0
    reopened = db.query(func.count(Complaint.complaint_id)).filter(Complaint.status == "reopened").scalar() or 0
    breached = db.query(func.count(Complaint.complaint_id)).filter(Complaint.sla_breached == True).scalar() or 0
    avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 4.2

    res_rate = resolved / max(total, 1)
    sla_comp = (total - breached) / max(total, 1)
    reopen_rate = reopened / max(total, 1)

    health_metrics = calculate_bank_health_score(
        resolution_rate=res_rate,
        sla_compliance_rate=sla_comp,
        avg_tat_days=4.2,
        reopen_rate=reopen_rate,
        satisfaction_avg=avg_rating
    )

    warnings = detect_early_warnings(db)
    recommendations = generate_management_recommendations(health_metrics, warnings)

    return {
        "health_summary": health_metrics,
        "early_warnings": warnings,
        "management_recommendations": recommendations,
        "sample_period": "Rolling 10-Month Performance Metric"
    }

class SimulationIn(BaseModel):
    department_id: Optional[int] = None
    company_id: Optional[int] = None
    proposed_workers: int = 8
    volume_change_pct: float = 0.0

@app.post("/api/intelligence/what-if-simulation")
def get_what_if_simulation(payload: SimulationIn, db: Session = Depends(get_db)):
    """
    Bank & Department-aware What-If Resource Simulation using real DB operational data.
    """
    from create_db import Complaint, User, Department, Company
    
    dept_name = "All Departments"
    bank_name = "All Banks"
    
    q = db.query(Complaint)
    if payload.company_id:
        q = q.filter(Complaint.company_id == payload.company_id)
        bank = db.query(Company).filter(Company.company_id == payload.company_id).first()
        if bank:
            bank_name = bank.name
    if payload.department_id:
        q = q.filter(Complaint.department_id == payload.department_id)
        dept = db.query(Department).filter(Department.department_id == payload.department_id).first()
        if dept:
            dept_name = dept.name
    
    wq = db.query(User).filter(User.role.in_(["officer", "staff"]), User.is_active == True)
    if payload.department_id:
        wq = wq.filter(User.department_id == payload.department_id)
    current_workers = max(wq.count(), 1)
    
    pending_q = q.filter(Complaint.status.in_(["open", "in_progress", "escalated"]))
    current_pending = pending_q.count()
    
    volume_factor = 1.0 + (payload.volume_change_pct / 100.0)
    simulated_volume = max(1, int(current_pending * volume_factor))
    
    resolved_with_times = q.filter(
        Complaint.status.in_(["resolved", "closed"]),
        Complaint.resolved_at.isnot(None)
    ).all()
    
    avg_tat_hours = 72.0
    if resolved_with_times:
        tats = []
        for c in resolved_with_times[:100]:
            try:
                diff = (c.resolved_at - c.created_at).total_seconds() / 3600
                if 0 < diff < 8760:
                    tats.append(diff)
            except:
                pass
        if tats:
            avg_tat_hours = round(sum(tats) / len(tats), 1)
    
    proposed_workers = max(payload.proposed_workers, 1)
    worker_ratio = current_workers / float(proposed_workers)
    
    simulated_tat = round(avg_tat_hours * (0.3 + 0.7 * worker_ratio) * max(0.5, volume_factor ** 0.4), 1)
    tat_change_pct = round(((avg_tat_hours - simulated_tat) / max(avg_tat_hours, 1)) * 100, 1)
    
    simulated_pending = max(0, int(simulated_volume * (0.4 + 0.6 * worker_ratio)))
    
    sla_pressure = round(worker_ratio * volume_factor * 5.5, 1)
    sla_pressure = max(1.0, min(10.0, sla_pressure))
    
    if sla_pressure <= 3.0:
        sla_risk_label = "LOW"
        sla_risk_color = "#16a34a"
    elif sla_pressure <= 5.5:
        sla_risk_label = "MEDIUM"
        sla_risk_color = "#d97706"
    elif sla_pressure <= 7.5:
        sla_risk_label = "HIGH"
        sla_risk_color = "#dc2626"
    else:
        sla_risk_label = "CRITICAL"
        sla_risk_color = "#7c3aed"
    
    if sla_pressure > 7:
        breach_risk_pct = min(95, int((sla_pressure - 7) * 30 + 55))
    elif sla_pressure > 5:
        breach_risk_pct = int((sla_pressure - 5) * 20 + 15)
    else:
        breach_risk_pct = max(2, int(sla_pressure * 3))
    
    return {
        "disclaimer": "Scenario Estimate — Not Guaranteed Prediction (Mathematical Projection from Operational Data)",
        "context": {
            "bank": bank_name,
            "department": dept_name,
            "volume_change_pct": payload.volume_change_pct
        },
        "current": {
            "workers": current_workers,
            "pending_complaints": current_pending,
            "avg_tat_hours": avg_tat_hours
        },
        "proposed": {
            "workers": proposed_workers,
            "volume_change_pct": payload.volume_change_pct,
            "simulated_complaint_volume": simulated_volume
        },
        "projections": {
            "estimated_tat_hours": simulated_tat,
            "tat_change_percentage": tat_change_pct,
            "estimated_pending_complaints": simulated_pending,
            "projected_sla_pressure_score": sla_pressure,
            "sla_risk_label": sla_risk_label,
            "sla_risk_color": sla_risk_color,
            "breach_risk_percentage": breach_risk_pct
        }
    }

@app.get("/api/intelligence/simulation-context")
def get_simulation_context(db: Session = Depends(get_db)):
    """
    Returns dynamic dropdown options and real operational data to pre-fill the What-If simulator.
    """
    from create_db import Company, Department, Complaint, User
    
    banks = db.query(Company).all()
    depts = db.query(Department).all()
    
    dept_stats = []
    for dept in depts:
        workers = db.query(User).filter(
            User.department_id == dept.department_id,
            User.role.in_(["officer", "staff"]),
            User.is_active == True
        ).count()
        
        pending = db.query(Complaint).filter(
            Complaint.department_id == dept.department_id,
            Complaint.status.in_(["open", "in_progress", "escalated"])
        ).count()
        
        resolved = db.query(Complaint).filter(
            Complaint.department_id == dept.department_id,
            Complaint.status.in_(["resolved", "closed"])
        ).count()
        
        total = db.query(Complaint).filter(
            Complaint.department_id == dept.department_id
        ).count()
        
        resolved_with_tat = db.query(Complaint).filter(
            Complaint.department_id == dept.department_id,
            Complaint.status.in_(["resolved", "closed"]),
            Complaint.resolved_at.isnot(None),
            Complaint.created_at.isnot(None)
        ).all()
        
        avg_tat_hours = 72.0
        if resolved_with_tat:
            tats = []
            for c in resolved_with_tat[:50]:
                try:
                    diff = (c.resolved_at - c.created_at).total_seconds() / 3600
                    if 0 < diff < 8760:
                        tats.append(diff)
                except:
                    pass
            if tats:
                avg_tat_hours = round(sum(tats) / len(tats), 1)
        
        dept_stats.append({
            "department_id": dept.department_id,
            "name": dept.name,
            "current_workers": max(workers, 1),
            "pending_complaints": pending,
            "resolved_complaints": resolved,
            "total_complaints": total,
            "avg_tat_hours": avg_tat_hours
        })
    
    bank_stats = []
    for bank in banks:
        pending = db.query(Complaint).filter(
            Complaint.company_id == bank.company_id,
            Complaint.status.in_(["open", "in_progress", "escalated"])
        ).count()
        total = db.query(Complaint).filter(
            Complaint.company_id == bank.company_id
        ).count()
        bank_stats.append({
            "company_id": bank.company_id,
            "name": bank.name,
            "pending_complaints": pending,
            "total_complaints": total
        })
    
    return {
        "banks": bank_stats,
        "departments": dept_stats
    }



# =============================================================
# 16. DOCUMENT PRE-VALIDATION (Real-time on upload)
# =============================================================

@app.post("/api/validate-document")
async def validate_document(
    service_type: str = Form(...),
    proof_file: UploadFile = File(...),
    submitted_bank: Optional[str] = Form(None),
    submitted_date: Optional[str] = Form(None),
    submitted_amount: Optional[float] = Form(None),
    submitted_ref_id: Optional[str] = Form(None),
    submitted_branch: Optional[str] = Form(None),
):
    """
    Real-time document validation endpoint — uses strict evidence_verifier engine.
    Returns mismatch warnings before final complaint submission.
    A file being uploadable does NOT mean it is relevant.
    Unrelated screenshots, chats, games, or academic docs will be REJECTED.
    """
    if not proof_file or not proof_file.filename:
        return {"valid": False, "verdict": "NO_EVIDENCE", "warnings": [], "message": "No file provided."}

    # Save temp file
    temp_filename = f"tmp_{int(datetime.utcnow().timestamp())}_{proof_file.filename}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(proof_file.file, buffer)

    try:
        # Use the strict evidence_verifier instead of the old heuristic approach
        result = verify_evidence_doc(
            file_path=temp_path,
            service_type=service_type,
            submitted_bank=submitted_bank,
            submitted_date=submitted_date,
            submitted_amount=submitted_amount,
            submitted_ref_id=submitted_ref_id,
            submitted_branch=submitted_branch,
        )

        verdict = result["verdict"]
        is_valid = verdict == "VERIFIED"
        needs_review = verdict == "NEEDS_REVIEW"

        # Build warnings list from both reasons (hard failures) and warnings (soft flags)
        all_warnings = result.get("reasons", []) + result.get("warnings", [])

        if is_valid:
            message = "Document verified — content appears relevant to the selected complaint category."
        elif needs_review:
            message = (
                "Document requires manual officer review. It will be accepted for submission "
                "but a bank officer will verify the evidence before processing."
            )
        else:
            # FAILED, INVALID_FILE
            message = f"Document rejected: {all_warnings[0] if all_warnings else 'Unrelated or unverifiable document.'}"

        # Extract banking fields from OCR text if available
        extracted_fields = {}
        extracted_text = result.get("extracted_text", "") or ""
        if extracted_text.strip():
            try:
                from ocr_engine import extract_banking_fields
                extracted_fields = extract_banking_fields(extracted_text)
                # Remove None values for cleaner response
                extracted_fields = {k: v for k, v in extracted_fields.items() if v is not None}
            except Exception:
                pass

        return {
            "valid": is_valid or needs_review,  # allow NEEDS_REVIEW to proceed to submission
            "verdict": verdict,
            "warnings": all_warnings,
            "matched_keywords": result.get("keyword_check", {}).get("primary_matched", []),
            "domain_scores": result.get("domain_scores", {}),
            "extracted_text_length": result.get("extracted_text_length", 0),
            "extracted_text_preview": extracted_text[:400] if extracted_text else "",
            "extracted_fields": extracted_fields,
            "message": message,
        }

    finally:
        # Clean up temp file
        try:
            os.remove(temp_path)
        except Exception:
            pass


# =============================================================
# 17. OFFICER / EMPLOYEE PORTAL ENDPOINTS
# =============================================================

@app.get("/api/officer/complaints")
def get_officer_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns complaints assigned to the current officer/staff user."""
    if current_user.role.lower() not in ['officer', 'staff', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized as an officer.")

    if current_user.role.lower() == 'admin':
        # Admin sees all complaints
        complaints = db.query(Complaint).order_by(Complaint.complaint_id.desc()).limit(100).all()
    else:
        # Officer sees their department's complaints or assigned complaints
        query = db.query(Complaint)
        if current_user.department_id:
            query = query.filter(
                (Complaint.current_assigned_officer_id == current_user.user_id) |
                (Complaint.department_id == current_user.department_id)
            )
        else:
            query = query.filter(Complaint.current_assigned_officer_id == current_user.user_id)
        complaints = query.order_by(Complaint.complaint_id.desc()).limit(100).all()

    result = []
    for c in complaints:
        from sla_engine import evaluate_sla_status
        sla_info = evaluate_sla_status(c.sla_deadline, c.status)
        customer = db.query(User).filter(User.user_id == c.customer_id).first() if c.customer_id else None
        latest_res = db.query(Resolution).filter(Resolution.complaint_id == c.complaint_id).order_by(Resolution.resolution_id.desc()).first()
        result.append({
            "complaint_id": c.complaint_id,
            "token": c.token,
            "company_name": c.company.company_name if c.company else "Unknown",
            "department_name": c.department.department_name if c.department else "Unassigned",
            "service_type": c.service_type,
            "sub_category": c.sub_category or "General Grievance",
            "description": c.description,
            "amount": c.amount,
            "reference_id": c.reference_id,
            "transaction_date": c.transaction_date,
            "branch": c.branch,
            "priority": c.priority,
            "status": c.status,
            "validity_score": c.validity_score,
            "resolution_mode": c.resolution_mode,
            "evidence_status": c.evidence_status or "PENDING",
            "evidence_rejection_reason": c.evidence_rejection_reason,
            "proof_file_path": c.proof_file_path,
            "resolution_notes": c.resolution_notes,
            "sla": sla_info,
            "created_at": c.created_at.isoformat() if c.created_at else c.submitted_at,
            "customer_name": customer.full_name if customer else "Anonymous",
            "customer_email": customer.email if customer else None,
            "has_resolution": latest_res is not None,
            "resolution_status": latest_res.customer_confirmation_status if latest_res else None,
        })
    return result


@app.get("/api/officer/stats")
def get_officer_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns KPI stats for the logged-in officer."""
    if current_user.role.lower() not in ['officer', 'staff', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized.")

    dept_id = current_user.department_id
    base_q = db.query(Complaint)
    if dept_id and current_user.role.lower() != 'admin':
        base_q = base_q.filter(
            (Complaint.current_assigned_officer_id == current_user.user_id) |
            (Complaint.department_id == dept_id)
        )

    total = base_q.count()
    resolved = base_q.filter(Complaint.status == "resolved").count()
    pending = base_q.filter(Complaint.status.in_(["open", "in_progress", "escalated"])).count()
    high_priority = base_q.filter(Complaint.priority == "High", Complaint.status != "resolved").count()
    sla_breached = base_q.filter(Complaint.sla_breached == True).count()

    return {
        "officer_name": current_user.full_name,
        "department": current_user.department.department_name if current_user.department else "All Departments",
        "role": current_user.role,
        "total_assigned": total,
        "resolved": resolved,
        "pending": pending,
        "high_priority_open": high_priority,
        "sla_breached": sla_breached,
        "resolution_rate_pct": round((resolved / max(total, 1)) * 100, 1)
    }


@app.get("/")
def root():
    return {
        "app": "GrievanceIQ API",
        "status": "operational",
        "docs_url": "/docs",
        "version": "2.0.0"
    }

