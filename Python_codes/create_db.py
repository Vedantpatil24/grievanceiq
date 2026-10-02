from sqlalchemy import create_engine, Column, Integer, String, Text, Float, TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

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

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    narrative = Column(Text, nullable=False)
    narrative_clean = Column(Text)
    department_id = Column(Integer, ForeignKey("departments.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    priority = Column(String, CheckConstraint("priority IN ('High','Medium','Low')"))
    status = Column(String, default="open", server_default="open")
    created_at = Column(TIMESTAMP, server_default=func.now())
    resolved_at = Column(TIMESTAMP)

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

# Create the database file inside Dataset folder
engine = create_engine(r"sqlite:///G:\Mini_project\Dataset\grievanceiq.db")
Base.metadata.create_all(engine)

print("Database created successfully at G:\\Mini_project\\Dataset\\grievanceiq.db")
print("Tables created:", list(Base.metadata.tables.keys()))