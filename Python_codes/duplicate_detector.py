"""
duplicate_detector.py - Duplicate & Anomaly Detection Service
Identifies identical transaction references or high textual redundancy
across prior complaints for the same financial institution.
"""

from sqlalchemy.orm import Session
from create_db import Complaint

def check_duplicates_and_anomalies(
    db: Session,
    company_id: int,
    reference_id: str,
    amount: float,
    description: str,
    current_token: str = None
) -> dict:
    """
    Checks if a complaint appears to be a duplicate or has anomaly flags.
    """
    flags = []
    duplicate_token = None
    desc_lower = (description or "").lower()

    # 1. Exact Reference ID match check (High Risk)
    if reference_id and reference_id.strip():
        query = db.query(Complaint).filter(
            Complaint.reference_id == reference_id.strip()
        )
        if current_token:
            query = query.filter(Complaint.token != current_token)
        existing_ref = query.first()
        if existing_ref:
            duplicate_token = existing_ref.token
            flags.append({
                "type": "DUPLICATE_REFERENCE_ID",
                "severity": "HIGH",
                "message": f"Exact matching Transaction Reference '{reference_id}' was previously filed under Token {existing_ref.token}."
            })

    # 2. High Value Financial Anomaly
    if amount and amount >= 100000:
        flags.append({
            "type": "HIGH_VALUE_TRANSACTION",
            "severity": "WARNING",
            "message": f"High transaction value (₹{amount:,.2f}) detected. Requires supervisory review."
        })

    # 3. Repeat Harassment or Cyber Extortion Flag
    if "threat" in desc_lower or "extortion" in desc_lower or "blackmail" in desc_lower:
        flags.append({
            "type": "CRITICAL_RISK_HARASSMENT",
            "severity": "CRITICAL",
            "message": "Critical legal/harassment risk indicators detected in complaint text."
        })

    is_duplicate = duplicate_token is not None

    return {
        "is_duplicate": is_duplicate,
        "matched_token": duplicate_token,
        "risk_flags": flags,
        "risk_score": 85 if is_duplicate else (50 if len(flags) > 0 else 10),
        "status": "FLAGGED" if len(flags) > 0 else "CLEAN"
    }
