"""
ml_pipeline.py - TF-IDF + Linear SVM Classifier Pipeline
Loads the pre-trained CFPB 15k model and provides classification,
confidence calculation, and priority refinement.
"""

import os
import joblib
import numpy as np
from multilingual_engine import align_multilingual_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
VEC_PATH = os.path.join(BASE_DIR, "vectorizer.joblib")
CAT_PATH = os.path.join(BASE_DIR, "category_model.joblib")
PRI_PATH = os.path.join(BASE_DIR, "priority_model_balanced.joblib")

# Load models safely
vectorizer = None
cat_model = None
pri_model = None

try:
    if os.path.exists(VEC_PATH) and os.path.exists(CAT_PATH):
        vectorizer = joblib.load(VEC_PATH)
        cat_model = joblib.load(CAT_PATH)
        if os.path.exists(PRI_PATH):
            pri_model = joblib.load(PRI_PATH)
        print("[ML Pipeline] Pre-trained models loaded successfully.")
except Exception as e:
    print(f"[ML Pipeline Warning] Could not load joblib models: {e}")

# Department mapping (CFPB Category to Bank Department)
CATEGORY_TO_DEPT = {
    "Credit Card Services": "Card Disputes Team",
    "Loans": "Loan Servicing Team",
    "Bank Accounts and Services": "Retail Banking Team",
    "Debt Collection": "Collections Compliance Team",
    "Credit Reporting": "Credit Bureau Liaison Team",
}

# High-risk financial severity keywords for priority enhancement
HIGH_SEVERITY_KEYWORDS = [
    "unauthorized", "fraud", "hacked", "stolen", "scam", "phishing",
    "police", "harassment", "abusive", "legal notice", "cyber crime",
    "extortion", "threat", "fir", "blocked account", "freeze"
]
MEDIUM_SEVERITY_KEYWORDS = [
    "dispute", "delayed", "charged twice", "wrong emi", "cibil dropped",
    "penalty", "interest", "noc delay", "atm cash not", "failed transfer"
]

def clean_text(text: str) -> str:
    return (text or "").lower().strip()

def classify_complaint(text: str, amount: float = None) -> dict:
    cleaned = clean_text(text)
    aligned_text = align_multilingual_text(cleaned)
    processed_text = f"{cleaned} {aligned_text}".strip()
    
    # 1. Fallback if models not loaded
    if vectorizer is None or cat_model is None:
        return {
            "predicted_category": "Bank Accounts and Services",
            "department_name": "Retail Banking Team",
            "priority": "Medium",
            "confidence": 0.75,
            "model_version": "rule_based_fallback"
        }

    # 2. Transform text & predict category
    vec = vectorizer.transform([processed_text])
    pred_category = cat_model.predict(vec)[0]
    
    # Calculate decision confidence
    try:
        decision_scores = cat_model.decision_function(vec)[0]
        # Softmax-style approximation for confidence
        exp_scores = np.exp(decision_scores - np.max(decision_scores))
        probs = exp_scores / exp_scores.sum()
        confidence = float(np.max(probs))
    except Exception:
        confidence = 0.85

    # 3. Predict Priority (combine model with BFSI business risk rules)
    raw_priority = "Medium"
    if pri_model is not None:
        try:
            raw_priority = pri_model.predict(vec)[0]
        except Exception:
            raw_priority = "Medium"

    # Business Rule Refinement: High value or critical fraud elevates priority
    refined_priority = raw_priority
    if any(kw in cleaned for kw in HIGH_SEVERITY_KEYWORDS) or (amount and amount >= 50000):
        refined_priority = "High"
    elif any(kw in cleaned for kw in MEDIUM_SEVERITY_KEYWORDS):
        if refined_priority != "High":
            refined_priority = "Medium"
    elif raw_priority not in ["High", "Medium", "Low"]:
        refined_priority = "Medium"

    dept_name = CATEGORY_TO_DEPT.get(pred_category, "Retail Banking Team")

    return {
        "predicted_category": pred_category,
        "department_name": dept_name,
        "priority": refined_priority,
        "confidence": round(confidence, 3),
        "model_version": "svm_v1_tfidf8k"
    }
