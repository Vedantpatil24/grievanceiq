"""
create_db.py - SQLAlchemy ORM Models for GrievanceIQ
BFSI Complaint Management & AI Triage Platform
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, 
    Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'grievanceiq.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==========================================
# 1. CORE MASTERS
# ==========================================

class Company(Base):
    __tablename__ = "companies"
    
    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), unique=True, nullable=False)
    
    complaints = relationship("Complaint", back_populates="company")


class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False)
    
    departments = relationship("Department", back_populates="category")


class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)

    category = relationship("Category", back_populates="departments")
    users = relationship("User", back_populates="department")
    complaints = relationship("Complaint", back_populates="department")
    kb_articles = relationship("KnowledgeBaseArticle", back_populates="department")


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), default="Banking Officer")
    role = Column(String(20), default="staff")  # "admin", "officer", "staff", "customer"
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    is_active = Column(Boolean, default=True)

    department = relationship("Department", back_populates="users")
    assigned_complaints = relationship("Complaint", back_populates="assigned_officer", foreign_keys="Complaint.current_assigned_officer_id")


# ==========================================
# 2. KNOWLEDGE BASE & AUDIT
# ==========================================

class KnowledgeBaseArticle(Base):
    __tablename__ = "knowledge_base_articles"
    
    article_id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    keywords = Column(Text, nullable=False)  # comma-separated tokens
    guidance_steps = Column(Text, nullable=False)
    regulatory_reference = Column(String(255), nullable=True)
    can_self_resolve = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = relationship("Department", back_populates="kb_articles")
    complaints = relationship("Complaint", back_populates="matched_article")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    actor_type = Column(String(20), nullable=False)  # 'user', 'customer', 'system'
    actor_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


# ==========================================
# 3. COMPLAINTS & WORKFLOW
# ==========================================

class Complaint(Base):
    __tablename__ = "complaints"
    
    complaint_id = Column(Integer, primary_key=True, index=True)
    token = Column(String(30), unique=True, index=True, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    
    # Original submission fields
    submitted_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    raw_text = Column(Text, nullable=True)
    state = Column(String(50), nullable=True)
    
    service_type = Column(String(100), nullable=True)
    transaction_date = Column(String(50), nullable=True)
    amount = Column(Float, nullable=True)
    reference_id = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    proof_file_path = Column(String(255), nullable=True)
    custom_fields = Column(Text, nullable=True)
    priority = Column(String(20), default="Medium")  # "High", "Medium", "Low"
    status = Column(String(30), default="open")  # "open", "in_progress", "resolved", "reopened", "closed", "escalated"
    
    # Validity fields
    validity_score = Column(Integer, default=0)
    validity_status = Column(String(20), default="valid")

    # Tier-1 Bot & Triage
    resolution_mode = Column(String(20), default="NONE")  # "NONE", "BOT", "HUMAN"
    matched_article_id = Column(Integer, ForeignKey("knowledge_base_articles.article_id"), nullable=True)
    bot_confidence = Column(Float, nullable=True)

    # Human Handling, Assignment & SLA
    escalation_level = Column(Integer, default=0)  # 0: None, 1: Officer, 2: Senior Nodal
    current_assigned_officer_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    sla_deadline = Column(DateTime, nullable=True)
    sla_breached = Column(Boolean, default=False)

    # Resolution & Reopen Governance
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    reopen_count = Column(Integer, default=0)
    can_reopen_until = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Customer Ownership & Sub-category
    customer_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    sub_category = Column(String(100), nullable=True)

    # Evidence Verification Fields
    evidence_status = Column(String(20), default="PENDING")  # PENDING, VERIFIED, REJECTED
    evidence_verified_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    evidence_verified_at = Column(DateTime, nullable=True)
    evidence_rejection_reason = Column(Text, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")
    assigned_officer = relationship("User", back_populates="assigned_complaints", foreign_keys=[current_assigned_officer_id])
    matched_article = relationship("KnowledgeBaseArticle", back_populates="complaints")
    
    messages = relationship("ComplaintMessage", back_populates="complaint", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="complaint", cascade="all, delete-orphan")
    assignments = relationship("AssignmentHistory", back_populates="complaint", cascade="all, delete-orphan")
    escalations = relationship("EscalationHistory", back_populates="complaint", cascade="all, delete-orphan")
    status_history = relationship("StatusHistory", back_populates="complaint", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="complaint", cascade="all, delete-orphan")
    resolutions = relationship("Resolution", back_populates="complaint", cascade="all, delete-orphan")
    investigation_notes = relationship("InvestigationNote", back_populates="complaint", cascade="all, delete-orphan")


# ==========================================
# 4. MESSAGING & NOTIFICATIONS
# ==========================================

class ComplaintMessage(Base):
    __tablename__ = "complaint_messages"
    
    message_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    sender_type = Column(String(20), nullable=False)  # 'customer', 'officer', 'system'
    sender_id = Column(Integer, nullable=True)  # user_id if officer, NULL if customer
    sender_name = Column(String(100), default="Customer")
    message_text = Column(Text, nullable=False)
    attachment_path = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="messages")


class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    recipient_type = Column(String(20), nullable=False)  # 'customer', 'staff'
    recipient_id = Column(Integer, nullable=True)  # user_id if staff, NULL if customer
    notification_type = Column(String(50), nullable=False)
    title = Column(String(150), nullable=False)
    body = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="notifications")


# ==========================================
# 5. ASSIGNMENT & ESCALATION HISTORIES
# ==========================================

class AssignmentHistory(Base):
    __tablename__ = "assignment_history"
    
    assignment_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    officer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    unassigned_at = Column(DateTime, nullable=True)
    reason = Column(Text, nullable=True)
    assigned_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    complaint = relationship("Complaint", back_populates="assignments")
    officer = relationship("User", foreign_keys=[officer_id])


class EscalationHistory(Base):
    __tablename__ = "escalation_history"
    
    escalation_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    from_level = Column(Integer, default=0)
    to_level = Column(Integer, default=1)
    reason = Column(Text, nullable=False)
    triggered_by = Column(String(20), nullable=False)  # 'customer', 'bot', 'sla_breach', 'officer'
    previous_officer_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    new_officer_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="escalations")


# ==========================================
# 6. HISTORICAL & PREDICTION TABLES
# ==========================================

class StatusHistory(Base):
    __tablename__ = "status_history"
    
    history_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    old_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    changed_by = Column(String(50), default="system")
    changed_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text, nullable=True)

    complaint = relationship("Complaint", back_populates="status_history")


class Prediction(Base):
    __tablename__ = "predictions"
    
    prediction_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    predicted_category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    predicted_priority = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)
    model_version = Column(String(50), default="svm_v1_tfidf8k")

    complaint = relationship("Complaint", back_populates="predictions")


class Ticket(Base):
    __tablename__ = "tickets"
    
    ticket_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    status = Column(String(30), default="open")
    assigned_at = Column(String(50), nullable=True)
    resolved_at = Column(String(50), nullable=True)


class Feedback(Base):
    __tablename__ = "feedback"
    
    feedback_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False, unique=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comments = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="feedback")


class Resolution(Base):
    __tablename__ = "resolutions"

    resolution_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    resolution_details = Column(Text, nullable=False)
    resolution_type = Column(String(50), nullable=False)
    transaction_reference = Column(String(100), nullable=True)
    resolved_amount = Column(Float, nullable=True)
    resolution_proof_path = Column(String(255), nullable=True)
    resolution_date = Column(DateTime, default=datetime.utcnow)
    customer_confirmation_status = Column(String(30), default="PENDING")  # PENDING, ACCEPTED, REJECTED
    customer_feedback = Column(Text, nullable=True)
    customer_action_date = Column(DateTime, nullable=True)

    complaint = relationship("Complaint", back_populates="resolutions")
    worker = relationship("User")


class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    note_id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="investigation_notes")
    worker = relationship("User")


class SimilarComplaint(Base):
    __tablename__ = "similar_complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    matched_complaint_id = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    classification_tag = Column(String(50), nullable=False)  # DUPLICATE, SIMILAR, RELATED
    detected_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", foreign_keys=[complaint_id])
    matched_complaint = relationship("Complaint", foreign_keys=[matched_complaint_id])


def init_db():
    Base.metadata.create_all(bind=engine)
    print("All GrievanceIQ tables initialized successfully.")


if __name__ == "__main__":
    init_db()
