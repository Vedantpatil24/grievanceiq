-- =====================================================================
-- GrievanceIQ Database Management System (DBMS) Schema & Relational DDL
-- Standard SQL / Relational Architecture for Academic & Production Demo
-- =====================================================================

-- 1. DEPARTMENTS (Core organizational hierarchy)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. COMPANIES / FINANCIAL INSTITUTIONS (BFSI Regulated Entities)
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- 3. USERS (Customer, Admin & Role-based authentication)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120),
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'user',
    phone VARCHAR(20),
    address TEXT,
    birthdate VARCHAR(30),
    avatar_url TEXT
);

-- 4. WORKERS / GRIEVANCE OFFICERS (Department assignment & 2-factor OTP credentials)
CREATE TABLE IF NOT EXISTS workers (
    id SERIAL PRIMARY KEY,
    worker_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    employee_id VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(150),
    otp_code VARCHAR(10),
    otp_expires_at TIMESTAMP
);

-- 5. COMPLAINTS (Primary transaction entity with AI validation & SLA lifecycle)
CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    token VARCHAR(60) NOT NULL UNIQUE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    narrative TEXT NOT NULL,
    narrative_clean TEXT,
    department_id INTEGER REFERENCES departments(id) ON DELETE RESTRICT,
    company_id INTEGER REFERENCES companies(id) ON DELETE RESTRICT,
    priority VARCHAR(20) CHECK (priority IN ('High', 'Medium', 'Low')),
    status VARCHAR(30) DEFAULT 'open',
    stage VARCHAR(50) DEFAULT 'Submitted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    due_date TIMESTAMP,
    is_escalated BOOLEAN DEFAULT FALSE,
    transaction_date VARCHAR(30),
    reference_id VARCHAR(100),
    amount NUMERIC(15, 2),
    branch VARCHAR(120),
    service_type VARCHAR(100),
    proof_file_path TEXT,
    validity_score REAL,
    validity_decision VARCHAR(50),
    assigned_worker_id VARCHAR(50),
    sbert_narrative_score REAL,
    proof_similarity_score REAL,
    proof_extracted_text REAL,
    rejection_reason TEXT,
    resolution_notes TEXT,
    resolution_proof_url TEXT,
    closed_at VARCHAR(40),
    priority_reason TEXT,
    requires_more_proof TEXT,
    customer_appeal TEXT,
    satisfaction_status VARCHAR(50)
);

-- 6. STATUS HISTORY (Audit trail for complaint state transitions)
CREATE TABLE IF NOT EXISTS status_history (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES complaints(id) ON DELETE CASCADE,
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. PREDICTIONS LOG (ML SVM Classification & NLP Inference tracking)
CREATE TABLE IF NOT EXISTS predictions_log (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES complaints(id) ON DELETE CASCADE,
    predicted_department VARCHAR(100),
    svm_confidence REAL,
    matched_keywords TEXT,
    priority_score REAL
);

-- 8. CUSTOMER FEEDBACK (Post-resolution CSAT ratings)
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER UNIQUE REFERENCES complaints(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. NOTIFICATIONS (Officer activity alerting)
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    worker_id VARCHAR(50),
    complaint_token VARCHAR(60),
    title VARCHAR(150),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- RELATIONAL PERFORMANCE INDEXES
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_complaints_token ON complaints(token);
CREATE INDEX IF NOT EXISTS idx_complaints_dept ON complaints(department_id);
CREATE INDEX IF NOT EXISTS idx_complaints_company ON complaints(company_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_priority ON complaints(priority);
CREATE INDEX IF NOT EXISTS idx_complaints_assigned ON complaints(assigned_worker_id);
CREATE INDEX IF NOT EXISTS idx_complaints_escalated ON complaints(is_escalated);
CREATE INDEX IF NOT EXISTS idx_workers_emp_id ON workers(employee_id);
