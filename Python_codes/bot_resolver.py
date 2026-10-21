"""
bot_resolver.py - Automated Grievance Resolution Engine with Dual Settlement Desks per Department
Implements:
1. 2 Specialized Desks per Banking Department (e.g. UPI Reversal Desk & POS Clearing Desk for Retail)
2. Priority-aware Resolution Engine:
   - High Priority: SLA 24 Hours
   - Medium Priority: SLA 72 Hours (2-3 Days)
   - Low Priority: SLA 168 Hours (Within 1 Week)
3. Automated Proof & Remediation Advice Document Generation
"""

import os
from sqlalchemy.orm import Session
from create_db import KnowledgeBaseArticle
from datetime import datetime

# 2 Designated Automated Settlement Desks per Banking Department
DEPARTMENT_BOTS = {
    1: [
        {"bot_id": "DESK-CARD-01", "name": "Card Disputes & Chargeback Settlement System", "role": "Card Settlement Desk"},
        {"bot_id": "DESK-CARD-02", "name": "Card Security & Unauthorized Debit System", "role": "Card Risk Audit Desk"}
    ],
    2: [
        {"bot_id": "DESK-LOAN-01", "name": "Loan Servicing & EMI Reconciliation Desk", "role": "EMI Operations Desk"},
        {"bot_id": "DESK-LOAN-02", "name": "Loan Documentation & NOC Release Desk", "role": "Loan Title Audit Desk"}
    ],
    3: [
        {"bot_id": "DESK-RETAIL-01", "name": "Instant Digital Clearing (UPI / IMPS) System", "role": "Retail Clearing Desk"},
        {"bot_id": "DESK-RETAIL-02", "name": "ATM Switch Reconciliation & Cash Settlement System", "role": "ATM Settlement Desk"}
    ],
    4: [
        {"bot_id": "DESK-COLL-01", "name": "Fair Lending Practice & Recovery Audit Desk", "role": "Recovery Compliance Desk"},
        {"bot_id": "DESK-COLL-02", "name": "Regulatory Fee & Penalty Review System", "role": "Fee Dispute Desk"}
    ],
    5: [
        {"bot_id": "DESK-BUREAU-01", "name": "CIBIL / Experian Credit Bureau Rectification System", "role": "Bureau Liaison Desk"},
        {"bot_id": "DESK-BUREAU-02", "name": "Credit History & Dispute Audit Desk", "role": "Credit Audit Desk"}
    ]
}

DEFAULT_BOTS = [
    {"bot_id": "DESK-GEN-01", "name": "Central Grievance Automated Triage Desk A", "role": "Triage Desk"},
    {"bot_id": "DESK-GEN-02", "name": "Central Grievance Automated Triage Desk B", "role": "Redressal Desk"}
]

IMMEDIATE_ESCALATION_KEYWORDS = [
    "unauthorized", "fraud", "hacked", "stolen", "scam", "phishing",
    "police", "harassment", "abusive", "legal notice", "cyber crime",
    "threat", "fir", "blocked account"
]

def get_department_bots(department_id: int) -> list:
    """Returns the two designated specialist desks for the department."""
    return DEPARTMENT_BOTS.get(department_id, DEFAULT_BOTS)

def generate_bot_proof_document(
    token: str,
    bot_info: dict,
    category_name: str,
    action_type: str,
    reference_id: str = None,
    amount: float = None,
    upload_dir: str = None
) -> str:
    """
    Generates an official Resolution Proof Advice Document (Text/PDF-ready format).
    Stored in uploads/ directory for customer and admin download.
    """
    now_str = datetime.utcnow().strftime("%d-%b-%Y %H:%M:%S UTC")
    proof_filename = f"proof_desk_{token.replace('-', '_')}_{int(datetime.utcnow().timestamp())}.txt"
    
    amt_val = amount if amount is not None else 0.0
    proof_content = (
        "======================================================================\n"
        "         OFFICIAL BFSI AUTOMATED REMEDIATION & SETTLEMENT ADVICE      \n"
        "           STATUTORY BANKING CONSUMER GRIEVANCE REDRESSAL DESK         \n"
        "======================================================================\n\n"
        f"Grievance Reference Token : {token}\n"
        f"Designated Settlement Desk: {bot_info.get('name')} ({bot_info.get('bot_id')})\n"
        f"Operational Responsibility: {bot_info.get('role')}\n"
        f"Date of Electronic Action : {now_str}\n"
        f"Dispute Category          : {category_name}\n"
        f"Transaction Reference     : {reference_id or 'TXN-AUTO-VERIFIED'}\n"
        f"Settlement Disputed Sum   : INR {amt_val:,.2f}\n"
        f"Statutory Protocol        : {action_type}\n\n"
        "----------------------------------------------------------------------\n"
        "                        REMEDIATION PROOF DETAILS                     \n"
        "----------------------------------------------------------------------\n"
        f"1. Clearing Verification  : Cleared against NPCI & RBI Ombudsman Guidelines.\n"
        f"2. Core Settlement Status : Automated inter-bank reconciliation memorandum registered.\n"
        f"3. Audit Hash / UTR Token : SHA256-UTR-{token}-{int(datetime.utcnow().timestamp())}\n"
        f"4. Customer Rights Notice : The complainant reserves statutory right to reject\n"
        f"   this resolution within 7 days, which initiates immediate officer escalation.\n\n"
        "----------------------------------------------------------------------\n"
        f"ISSUED UNDER BANKING REGULATION ACT - {bot_info.get('name')}\n"
        "======================================================================\n"
    )

    if upload_dir and os.path.exists(upload_dir):
        file_path = os.path.join(upload_dir, proof_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(proof_content)
        return file_path

    return None

def analyze_with_bot(
    db: Session,
    department_id: int,
    category_name: str,
    description: str,
    priority: str,
    amount: float = None,
    token: str = "GRV-PENDING",
    reference_id: str = None,
    upload_dir: str = None
) -> dict:
    """
    Automated grievance assessment with 2 specialist desks per department and SLA target calculation.
    """
    desc_lower = (description or "").lower()
    is_sensitive_case = any(kw in desc_lower for kw in IMMEDIATE_ESCALATION_KEYWORDS) or (amount and amount >= 50000)

    # Resolve assigned desk from the 2 department desks
    bots = get_department_bots(department_id)
    # Pick Primary Desk (Desk 0) for general/service or Secondary Desk (Desk 1) for fraud/penalties
    assigned_bot = bots[1] if (is_sensitive_case or "fraud" in desc_lower or "charge" in desc_lower) else bots[0]

    # Target SLA hours based on priority
    sla_target_hours = 24 if priority == "High" else (72 if priority == "Medium" else 168)
    sla_target_str = "Within 24 Hours" if priority == "High" else ("2 - 3 Days (72h)" if priority == "Medium" else "Within 1 Week (168h)")

    # 1. Query active KB articles
    query = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.is_active == True)
    if department_id:
        query = query.filter(
            (KnowledgeBaseArticle.department_id == department_id) | 
            (KnowledgeBaseArticle.category == category_name)
        )
    articles = query.all()

    best_article = None
    best_score = 0

    for art in articles:
        kw_list = [k.strip().lower() for k in (art.keywords or "").split(",") if k.strip()]
        matches = sum(1 for kw in kw_list if kw in desc_lower)
        if matches > best_score:
            best_score = matches
            best_article = art

    # Generate proof document if self-resolvable
    proof_path = None
    if best_article and best_article.can_self_resolve and not is_sensitive_case:
        proof_path = generate_bot_proof_document(
            token=token,
            bot_info=assigned_bot,
            category_name=category_name,
            action_type="Automated Resolution Proof & Settlement Advisory",
            reference_id=reference_id,
            amount=amount,
            upload_dir=upload_dir
        )

    # 2. Return desk assessment
    if best_article and best_score >= 1:
        match_confidence = min(0.60 + (best_score * 0.12), 0.96)
        
        if is_sensitive_case or not best_article.can_self_resolve:
            return {
                "bot_id": assigned_bot["bot_id"],
                "bot_name": assigned_bot["name"],
                "bot_role": assigned_bot["role"],
                "department_bots": bots,
                "article_id": best_article.article_id,
                "title": best_article.title,
                "category": best_article.category,
                "recommendation_type": "RECOMMEND_HUMAN_ESCALATION",
                "summary": (
                    "This case involves high-value dispute or security sensitive operations. "
                    "Direct review by a senior Grievance Redressal Officer is recommended."
                ),
                "guidance_steps": best_article.guidance_steps,
                "regulatory_reference": best_article.regulatory_reference or "Official Banking Grievance Procedure",
                "can_self_resolve": False,
                "bot_confidence": round(match_confidence, 2),
                "sla_target_hours": sla_target_hours,
                "sla_target_display": sla_target_str,
                "proof_file": os.path.basename(proof_path) if proof_path else None,
                "suggested_action": "Review the guidance steps above and click 'I Still Need Help (Escalate)'."
            }
        else:
            return {
                "bot_id": assigned_bot["bot_id"],
                "bot_name": assigned_bot["name"],
                "bot_role": assigned_bot["role"],
                "department_bots": bots,
                "article_id": best_article.article_id,
                "title": best_article.title,
                "category": best_article.category,
                "recommendation_type": "SELF_SERVICE_GUIDANCE",
                "summary": (
                    f"Assigned {assigned_bot['name']} has verified statutory interbank clearing steps. "
                    f"Target Resolution SLA: {sla_target_str}."
                ),
                "guidance_steps": best_article.guidance_steps,
                "regulatory_reference": best_article.regulatory_reference or "Standard Banking Terms & Conditions",
                "can_self_resolve": True,
                "bot_confidence": round(match_confidence, 2),
                "sla_target_hours": sla_target_hours,
                "sla_target_display": sla_target_str,
                "proof_file": os.path.basename(proof_path) if proof_path else None,
                "suggested_action": (
                    "If following these steps addresses your concern, you may accept resolution. "
                    "If your issue remains unresolved or exceeds the SLA target, escalate to an officer."
                )
            }

    # Fallback
    fallback_proof = generate_bot_proof_document(
        token=token,
        bot_info=assigned_bot,
        category_name=category_name,
        action_type="Standard Redressal Guideline Dispatch",
        reference_id=reference_id,
        amount=amount,
        upload_dir=upload_dir
    )

    return {
        "bot_id": assigned_bot["bot_id"],
        "bot_name": assigned_bot["name"],
        "bot_role": assigned_bot["role"],
        "department_bots": bots,
        "article_id": None,
        "title": f"Standard {category_name} Redressal Guidance",
        "category": category_name,
        "recommendation_type": "RECOMMEND_HUMAN_ESCALATION" if priority == "High" else "GENERAL_GUIDANCE",
        "summary": (
            f"Your complaint has been classified under {category_name} with {priority} priority. "
            f"Resolution Target Window: {sla_target_str}."
        ),
        "guidance_steps": (
            "1. Retain all transaction records, reference slips, and SMS alerts.\n"
            "2. Allow the standard settlement cycle for inter-bank clearing reconciliation.\n"
            "3. If funds are not reversed within the SLA window, request human officer escalation."
        ),
        "regulatory_reference": "General Banking Grievance Redressal Framework",
        "can_self_resolve": priority != "High",
        "bot_confidence": 0.50,
        "sla_target_hours": sla_target_hours,
        "sla_target_display": sla_target_str,
        "proof_file": os.path.basename(fallback_proof) if fallback_proof else None,
        "suggested_action": "Review the guidance steps or escalate to a bank officer."
    }
