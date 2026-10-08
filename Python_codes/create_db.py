from sqlalchemy import create_engine, Column, Integer, String, Text, Float, TIMESTAMP, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Worker(Base):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True)
    worker_id = Column(String, unique=True, nullable=False)  # e.g. BOT-DIG-01
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    employee_id = Column(String, unique=True)
    password_hash = Column(String)
    phone = Column(String)
    email = Column(String)
    otp_code = Column(String)
    otp_expires_at = Column(TIMESTAMP)

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    phone = Column(String)
    address = Column(String)
    birthdate = Column(String)
    avatar_url = Column(String)

class Complaint(Base):
    __tablename__ = "complaints"
    validity_score = Column(Float)
    validity_decision = Column(String)
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    narrative = Column(Text, nullable=False)
    narrative_clean = Column(Text)
    department_id = Column(Integer, ForeignKey("departments.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    priority = Column(String, CheckConstraint("priority IN ('High','Medium','Low')"))
    status = Column(String, default="open", server_default="open")
    stage = Column(String, default="Submitted") # Submitted, Triage, Investigation, Resolution, Closed
    created_at = Column(TIMESTAMP, server_default=func.now())
    resolved_at = Column(TIMESTAMP)
    due_date = Column(TIMESTAMP)
    is_escalated = Column(Boolean, default=False)
    assigned_worker_id = Column(String)
    transaction_date = Column(String)
    reference_id = Column(String)
    amount = Column(Float)
    branch = Column(String)
    service_type = Column(String)
    proof_file_path = Column(String)
    sbert_narrative_score = Column(Float)
    proof_similarity_score = Column(Float)
    proof_extracted_text = Column(Text)
    rejection_reason = Column(Text)
    resolution_notes = Column(Text)
    resolution_proof_url = Column(Text)
    closed_at = Column(TIMESTAMP)
    priority_reason = Column(Text)
    requires_more_proof = Column(Text)
    customer_appeal = Column(Text)
    satisfaction_status = Column(String)

class StatusHistory(Base):
    __tablename__ = "status_history"
    id = Column(Integer, primary_key=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    old_status = Column(String)
    new_status = Column(String)
    changed_at = Column(TIMESTAMP, server_default=func.now())

class PredictionsLog(Base):
    __tablename__ = "predictions_log"
    id = Column(Integer, primary_key=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    predicted_department = Column(String)
    svm_confidence = Column(Float)
    matched_keywords = Column(Text)
    priority_score = Column(Float)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), unique=True)
    rating = Column(Integer, CheckConstraint("rating BETWEEN 1 AND 5"))
    comment = Column(Text)
    submitted_at = Column(TIMESTAMP, server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String, nullable=True)
    role = Column(String, nullable=False)  # admin, employee, user
    action = Column(String, default="LOGIN")  # LOGIN, LOGOUT, FAILED_LOGIN, STATUS_CHANGE
    ip_address = Column(String, default="127.0.0.1")
    machine = Column(String, default="Unknown Device")
    os_name = Column(String, default="Windows")
    browser = Column(String, default="Chrome")
    location = Column(String, default="Mumbai, India")
    status = Column(String, default="SUCCESS")  # SUCCESS, FAILED
    details = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

if __name__ == "__main__":
    engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
    Base.metadata.create_all(engine)
    print("Database updated successfully at G:\\Mini_project\\Dataset\\grievanceiq.db")
    print("Tables created:", list(Base.metadata.tables.keys()))