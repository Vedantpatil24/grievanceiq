# GrievanceIQ 🏦

> **Intelligent BFSI Grievance Redressal & Predictive Resource Management Platform**  
> *Compliant with the Reserve Bank of India (RBI) Integrated Ombudsman Scheme, 2021*

---

## 🌟 Key Features

### 1. 🌐 Native Multilingual Grievance Support (English, हिंदी & Hinglish)
- **Automatic Language Detection**: Detects Devanagari Unicode (`\u0900–\u097F`) for Hindi, romanized tokens for Hinglish, and standard English.
- **Whole-App Bilingual Experience**: One-click language switch between **English** and **हिंदी (Hindi)** across the entire portal:
  - Citizen Grievance Lodging & Status Tracking
  - Officer Workspace & Settlement Console
  - Admin Command Room & Macro Analytics
  - Authentication, Registration & Modals

### 2. 🧠 SBERT & 3-Tier Human Coherence Validity Engine
- **Tier 1 (Gibberish Detection)**: Character entropy, vowel density (15–70%), and consonant run analysis to block keyboard mashing.
- **Tier 2 (Keyword Bombing Defense)**: Grammatical glue token ratio check ($\ge 8\%$) to reject tag clouds or keyword stuffing.
- **Tier 3 (Grievance Action & Distress Intent)**:
  - English contraction normalization (`hasn't` $\rightarrow$ `has not`, `didn't` $\rightarrow$ `did not`, `haven't` $\rightarrow$ `have not`).
  - Negation and contrastive patterns (`"payment done ... but receiver hasn't received"`).
  - Native Devanagari dispute markers (`कट गए`, `नहीं मिला`, `वापस`, `धोखा`, `अनधिकृत`, `ब्लॉक`).
  - **Sentence-BERT (`all-MiniLM-L6-v2`) Semantic Fallback**: Evaluates deep-learning cosine similarity against Indian BFSI anchor complaints to validate natural human emotion.

### 3. 📊 Operational What-If Capacity & TAT Simulation
- **Dynamic Context**: Pre-fills real operational data (active officers, pending complaints, historical TAT) per bank and department from live database queries.
- **Mathematical Projection**: Models changes in officer staffing and complaint intake volume ($\pm 50\%$ to $+100\%$) to project:
  - Simulated Turnaround Time (TAT in hours)
  - Estimated Pending Caseload
  - Dynamic SLA Pressure Score ($1.0 - 10.0$) and Breach Risk Probability (%)
  - Clearly marked as mathematical estimates, not guaranteed predictions.

### 4. 📄 MahaDBT / RBI CMS 4-Layer Evidence Scrutiny
- **Document Morphology Check**: Page count, MIME verification, and academic PDF manual filtering.
- **AI Relevance & Confidence Score ($0-100$)**:
  - File format validation (PDF, JPG, PNG, DOCX)
  - OCR text extraction & keyword alignment
  - Semantic cross-similarity between narrative and document text
  - Officer actionable verdicts (`HIGH CONFIDENCE`, `REVIEW REQUIRED`, `REJECT`)

---

## 🏗️ Tech Stack

- **Frontend**: React 19, Vite, React Router DOM, Axios, Recharts, Lucide Icons
- **Backend**: Python 3.12, FastAPI, Uvicorn ASGI Server, Pydantic, SQLAlchemy ORM
- **Machine Learning & NLP**:
  - `sentence-transformers` (`all-MiniLM-L6-v2`, PyTorch)
  - `scikit-learn` (`LinearSVC`, `TfidfVectorizer`)
  - `pypdf`, `python-docx`, `Pillow`
- **Database**: SQLite (`grievanceiq.db`) / PostgreSQL compatible
- **Security**: JWT (`python-jose`), bcrypt password hashing, role-based access control (Customer, Officer, Admin)

---

## 🚀 Quickstart Guide

### 1. Backend Setup
```bash
cd Python_codes
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt # or install fastapi uvicorn sqlalchemy sentence-transformers scikit-learn pypdf python-docx bcrypt python-jose
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Running Coherence & Semantic Tests
```bash
cd Python_codes
python test_semantic_cases.py
```

---

## 👤 Author
- **Ashmit Patil** ([@Ashmit-Patil](https://github.com/Ashmit-Patil))
- Repository: [Vedantpatil24/grievanceiq](https://github.com/Vedantpatil24/grievanceiq)
