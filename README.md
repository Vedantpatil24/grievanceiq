# GrievanceIQ: Autonomous Banking Grievance Redressal and Predictive Operational Intelligence Platform

GrievanceIQ is an end-to-end autonomous banking grievance redressal platform that combines natural language processing, machine learning classification, computer vision-based evidence verification, and mathematical queueing theory to transform how Indian commercial banks handle customer complaints. The platform replaces manual, paper-driven triage workflows with an intelligent pipeline that classifies, prioritizes, verifies, and resolves grievances with minimal human intervention while maintaining strict compliance with the Digital Personal Data Protection (DPDP) Act, 2023 and the RBI Integrated Ombudsman Scheme, 2021.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Team](#team)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Project Overview

Indian banking institutions process millions of customer grievances annually through largely manual workflows, resulting in statutory SLA breaches, inconsistent categorization, and delayed resolution. GrievanceIQ addresses these inefficiencies through:

- Autonomous multi-class complaint triage using TF-IDF vectorization and Multinomial Naive Bayes classification, achieving 83.49% accuracy across six banking complaint categories with a macro F1-score of 0.835.
- Real-time ingestion-level PII redaction compliant with the DPDP Act 2023, masking 16-digit card numbers, 12-digit Aadhaar UIDs, and 10-character PAN identifiers with 100% zero-leakage.
- Vernacular voice intake through the W3C Web Speech API supporting English, Hindi, and Marathi with a dual-state buffer accumulator that eliminates repetitive text loops during continuous streaming dictation.
- Documentary evidence verification using EasyOCR and PyTesseract with 4-point entity cross-matching (amount, reference number, date, terminal) against filed claims.
- Predictive queue capacity planning using the Kleinrock M/M/c Erlang-C queueing formulation with an interactive what-if staffing sandbox for branch operations managers.
- Statutory PDF receipt generation via ReportLab with embedded ISO/IEC 18004 dynamic QR codes for real-time case tracking.
- Tamper-evident forensic audit trail using SHA-256 cryptographic hash chaining for regulatory compliance and dispute resolution.

The platform compresses average statutory grievance resolution turnaround from 96 hours (industry baseline) to 14.2 hours, representing an 85.2% latency reduction.

## Key Features

**Citizen-Facing Capabilities**
- Trilingual complaint submission portal (English, Hindi, Marathi) with real-time voice dictation
- Live DPDP Act 2023 PII masking preview before submission
- Statutory PDF receipt with embedded QR tracking code
- Public grievance status tracker with visual SLA countdown timer

**Grievance Redressal Officer (GRO) Workspace**
- Priority-sorted triage worklist with SLA expiry urgency indicators
- AI Copilot memo drafter for structured adjudication memos
- Evidence inspection panel with OCR 4-point cross-validation results
- One-click digital sign-off and citizen notification dispatch

**Executive Intelligence Dashboard**
- Branch health scorecard with systemic risk radar visualization
- Predictive M/M/c Erlang-C staffing sandbox with interactive parameter sliders
- Scheduled commercial banks operational performance leaderboard
- Immutable forensic audit trail viewer with hash chain integrity verification

**Tier-1 Autonomous Resolution Bot**
- Deterministic rule-engine validation against core banking system transaction logs
- Automatic dispute settlement for standard cases with zero human touch
- Exception routing to GRO worklist for non-standard disputes

## System Architecture

The platform is built on a 5-tier client-server architecture:

```
Tier 1: Client Presentation        React 18 + Vite + Tailwind CSS (SPA)
Tier 2: API Gateway & Security     FastAPI + Uvicorn ASGI + JWT RBAC + DPDP Regex Sanitizer
Tier 3: Core NLP & Redressal       TF-IDF/MNB Classifier + SBERT Matcher + OCR Engine + AutoBot
Tier 4: Predictive Intelligence    Erlang-C Simulator + LLM Copilot + SLA Dispatcher
Tier 5: Data Persistence           PostgreSQL 16 (18-table 3NF/BCNF schema) + Forensic Audit Vault
```

## Technology Stack

| Layer | Technologies |
|:---|:---|
| Frontend | React 18, Vite, Tailwind CSS, Lucide Icons, Recharts, Axios |
| Backend | Python 3.12, FastAPI, Uvicorn, Pydantic, python-jose (JWT) |
| Machine Learning | Scikit-Learn (TF-IDF, Multinomial Naive Bayes), Sentence-Transformers (all-MiniLM-L6-v2) |
| Computer Vision | EasyOCR, PyTesseract, Pillow, OpenCV (Otsu thresholding) |
| Database | PostgreSQL 16, psycopg2, SQLAlchemy |
| PDF Generation | ReportLab (Platypus), qrcode (ISO/IEC 18004) |
| Testing | pytest, unittest |
| Deployment | Docker, Nginx, Gunicorn |

## Project Structure

```
Mini_project/
|-- Python_codes/               # Backend application
|   |-- main.py                 # FastAPI application entry point (28 REST endpoints)
|   |-- ml_pipeline.py          # TF-IDF + Multinomial Naive Bayes training and inference
|   |-- ocr_engine.py           # EasyOCR and PyTesseract evidence extraction
|   |-- evidence_verifier.py    # 4-point entity cross-validation engine
|   |-- validity_checker.py     # DPDP Act 2023 PII regex sanitization
|   |-- sla_engine.py           # Statutory SLA countdown and escalation logic
|   |-- smart_assigner.py       # Workload-balanced officer assignment
|   |-- bot_resolver.py         # Tier-1 autonomous dispute resolution bot
|   |-- bank_intelligence.py    # Branch health scorecard and Erlang-C simulator
|   |-- semantic_engine.py      # SBERT cosine similarity and duplicate detection
|   |-- duplicate_detector.py   # Complaint deduplication service
|   |-- audit_service.py        # SHA-256 tamper-evident hash chain audit trail
|   |-- train_classifier.py     # Model training script
|   |-- model_metrics.json      # Trained model evaluation metrics
|   |-- test_e2e_workflows.py   # End-to-end integration tests
|   |-- test_phase2_extended.py # Extended test suite (48 test cases)
|   +-- uploads/                # User-uploaded evidence documents
|
|-- frontend/                   # React SPA client application
|   |-- src/
|   |   |-- App.jsx             # Root application component and routing
|   |   |-- pages/
|   |   |   |-- Login.jsx               # Authentication page
|   |   |   |-- SubmitComplaint.jsx      # Complaint intake with voice dictation
|   |   |   |-- TrackComplaint.jsx       # Public status tracker with SLA countdown
|   |   |   |-- EmployeeDashboard.jsx    # GRO workspace and triage queue
|   |   |   |-- AdminDashboard.jsx       # Executive intelligence console
|   |   |   +-- CustomerHistory.jsx      # Complainant case history
|   |   |-- components/
|   |   |   |-- Navbar.jsx              # Navigation bar
|   |   |   +-- NovaAssistant.jsx       # AI assistant interface
|   |   +-- context/                    # React context providers
|   +-- package.json
|
|-- Dataset/                    # Training and evaluation datasets
|-- docs/                       # Project documentation and SPIT report
|-- schema_dbms.sql             # PostgreSQL schema DDL
|-- sample_queries_dbms.sql     # Sample analytical queries
+-- run_backend.bat             # Backend startup script
```

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/vedantpatil24/Mini_project.git
cd Mini_project

# Create and activate a Python virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install Python dependencies
pip install fastapi uvicorn psycopg2-binary scikit-learn sentence-transformers easyocr pytesseract pillow reportlab qrcode python-jose passlib bcrypt pydantic

# Set up the PostgreSQL database
# Create a database named 'grievanceiq' in PostgreSQL
# Update the connection string in Python_codes/main.py

# Initialize the database schema
psql -U postgres -d grievanceiq -f schema_dbms.sql

# Train the ML classifier
cd Python_codes
python train_classifier.py

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.

## Running the Application

1. Start the PostgreSQL database server.
2. Start the backend: `cd Python_codes && uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
3. Start the frontend: `cd frontend && npm run dev`
4. Open `http://localhost:5173` in a browser.

Default administrative credentials can be created using:
```bash
python Python_codes/create_admin.py
```

## Machine Learning Pipeline

The classification pipeline processes complaint text through the following stages:

1. **Text Preprocessing**: Unicode NFKC normalization, lowercasing, stopword removal, and tokenization.
2. **Feature Extraction**: TF-IDF vectorization with a vocabulary of up to 10,000 unigram and bigram features.
3. **Classification**: Multinomial Naive Bayes classifier trained on banking complaint datasets.
4. **Subcategory Assignment**: SBERT (all-MiniLM-L6-v2) dense embeddings with cosine similarity matching against subcategory centroids.
5. **Priority and SLA Assignment**: Rule-based priority scoring with statutory SLA hour allocation per RBI guidelines.

**Model Performance (test set, N = 2,998)**

| Metric | Value |
|:---|:---|
| Multi-class Accuracy | 83.49% |
| Macro F1-Score | 0.835 |
| Macro Precision | 0.840 |
| Macro Recall | 0.831 |

## API Endpoints

The backend exposes 28 RESTful API endpoints. Key endpoints include:

| Method | Endpoint | Description |
|:---|:---|:---|
| POST | `/api/complaints` | Submit a new grievance |
| GET | `/api/complaints/{id}` | Retrieve complaint details |
| GET | `/api/complaints/track/{token}` | Public status tracking |
| POST | `/api/auth/login` | User authentication |
| POST | `/api/ocr/extract` | Upload and extract evidence via OCR |
| POST | `/api/evidence/verify/{id}` | Run 4-point cross-validation |
| GET | `/api/officer/worklist` | GRO priority triage queue |
| POST | `/api/resolve/{id}` | Submit resolution memo |
| GET | `/api/intelligence/health` | Branch health scorecard |
| POST | `/api/intelligence/erlang-c` | Run Erlang-C staffing simulation |
| GET | `/api/audit/trail/{id}` | Forensic audit trail for a case |
| GET | `/api/receipt/{id}` | Download statutory PDF receipt |

Full API documentation is available at `http://localhost:8000/docs` (Swagger UI) when the backend is running.

## Testing

The project includes 48 automated test cases covering unit, integration, boundary, and end-to-end scenarios:

```bash
# Run the full test suite
cd Python_codes
python -m pytest test_e2e_workflows.py test_phase2_extended.py -v

# Run individual test modules
python -m pytest test_e2e_workflows.py -v       # End-to-end workflow tests
python -m pytest test_phase2_extended.py -v      # Extended phase 2 tests
python -m pytest test_evidence_verification.py -v # OCR verification tests
```

## Team

This project was developed as a Mini Project for the Department of Computer Engineering at Bharatiya Vidya Bhavan's Sardar Patel Institute of Technology (Autonomous), Mumbai, affiliated to the University of Mumbai.

| Name | UID | Role |
|:---|:---|:---|
| Vedant Patil | 2024300170 | Full-Stack Development, ML Pipeline, System Architecture |
| Ashmit Patil | 2024300168 | Backend Services, Database Design, Testing |
| Mayuri Tarde | 2024300258 | Frontend Development, UI/UX, Documentation |

**Class**: T.E. Computer Engineering, Division C and D
**Academic Year**: 2026-2027
**Project Guide**: Dr. Rupali Sawant, Associate Professor
**Head of Department**: Dr. Sudhir Dhage, Professor and Head

## Acknowledgements

We express our sincere gratitude to our project guide Dr. Rupali Sawant for her continuous guidance and mentorship throughout the development of this project. We also thank Dr. Sudhir Dhage (Head of Department, Computer Engineering) and Dr. B. N. Chaudhari (Principal, SPIT) for providing the academic infrastructure and institutional support. We acknowledge the Reserve Bank of India for publicly available grievance redressal frameworks and the open-source community for the tools and libraries that made this project possible.

## License

This project was developed for academic purposes at Sardar Patel Institute of Technology, Mumbai. All rights reserved by the authors.
