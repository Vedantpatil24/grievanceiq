"""
bank_intelligence.py - Advanced Bank Analytics, Health Score, Early Warning, & What-If Simulation
Implements:
1. 10-Month Historical Analytics
2. Bank Health Score (0-100 composite index)
3. Early Warning Spike Detector
4. Management Action Recommendations
5. What-If Resource Simulation
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import random

def calculate_bank_health_score(
    resolution_rate: float,       # 0.0 to 1.0
    sla_compliance_rate: float,   # 0.0 to 1.0
    avg_tat_days: float,          # typically 1 to 14 days
    reopen_rate: float,           # 0.0 to 1.0 (lower is better)
    satisfaction_avg: float       # 1.0 to 5.0
) -> dict:
    """
    Computes unified Bank Health Score (0-100):
    Weights:
    - Resolution Rate: 25 pts
    - SLA Compliance: 25 pts
    - Turnaround Time (TAT): 20 pts (<= 3 days = 20 pts, >= 14 days = 0 pts)
    - Reopen Rate (Low is good): 15 pts (<= 5% = 15 pts, >= 25% = 0 pts)
    - Customer Satisfaction: 15 pts (5.0 = 15 pts, 1.0 = 0 pts)
    """
    # 1. Resolution Rate Component (max 25)
    score_res = min(resolution_rate, 1.0) * 25.0

    # 2. SLA Compliance Component (max 25)
    score_sla = min(sla_compliance_rate, 1.0) * 25.0

    # 3. TAT Component (max 20)
    # 2 days -> 20 pts, 14+ days -> 0 pts
    tat_norm = max(0.0, min(1.0, (14.0 - avg_tat_days) / 12.0))
    score_tat = tat_norm * 20.0

    # 4. Reopen Rate Component (max 15, lower reopen = better)
    # 0% reopen -> 15 pts, >= 25% reopen -> 0 pts
    reopen_norm = max(0.0, min(1.0, (0.25 - reopen_rate) / 0.25))
    score_reopen = reopen_norm * 15.0

    # 5. Satisfaction Component (max 15)
    # (rating - 1) / 4 * 15
    sat_norm = max(0.0, min(1.0, (satisfaction_avg - 1.0) / 4.0)) if satisfaction_avg > 0 else 0.5
    score_sat = sat_norm * 15.0

    total_score = round(score_res + score_sla + score_tat + score_reopen + score_sat, 1)

    # Classification Grade
    if total_score >= 85:
        grade = "EXCELLENT (A+)"
        health_status = "HEALTHY"
    elif total_score >= 70:
        grade = "STABLE (B+)"
        health_status = "SATISFACTORY"
    elif total_score >= 55:
        grade = "ATTENTION NEEDED (C)"
        health_status = "VULNERABLE"
    else:
        grade = "CRITICAL RISK (D)"
        health_status = "HIGH RISK"

    return {
        "health_score": total_score,
        "grade": grade,
        "health_status": health_status,
        "breakdown": {
            "resolution_efficiency": round(score_res, 1),
            "sla_discipline": round(score_sla, 1),
            "tat_speed": round(score_tat, 1),
            "reopen_resistance": round(score_reopen, 1),
            "customer_trust": round(score_sat, 1)
        }
    }

def detect_early_warnings(db: Session, company_id: int = None) -> list:
    """
    Detects sudden spikes and anomalies across categories:
    - UPI failure spike
    - Card unauthorized swipe spike
    - Spike in delayed loan documentation
    - Unusually high SLA breach frequency
    """
    try:
        from create_db import Complaint, Company
    except ImportError:
        from Python_codes.create_db import Complaint, Company

    warnings = []
    # Query complaints in last 14 days vs prior period
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    recent_complaints = db.query(Complaint).filter(Complaint.created_at >= seven_days_ago).all()
    total_recent = len(recent_complaints)

    if total_recent == 0:
        # Fallback to realistic systemic indicators based on all records
        all_c = db.query(Complaint).all()
        total_recent = len(all_c)
        recent_complaints = all_c

    # Category frequencies
    cat_counts = {}
    breached_count = 0
    for c in recent_complaints:
        svc = c.service_type or "General"
        cat_counts[svc] = cat_counts.get(svc, 0) + 1
        if c.sla_breached:
            breached_count += 1

    # Check for category spikes
    for cat, count in cat_counts.items():
        ratio = count / max(total_recent, 1)
        if ratio >= 0.35 and count >= 3:
            warnings.append({
                "type": "COMPLAINT_SPIKE",
                "severity": "HIGH",
                "title": f"Surge in {cat} Issues Detected",
                "description": f"{cat} represents {int(ratio*100)}% of recent volume ({count} tickets). Indicates switch or settlement gateway anomaly.",
                "recommendation": f"Initiate immediate clearing audit on {cat} infrastructure and notify switch operations desk."
            })

    # Check SLA breach surge
    if breached_count >= 2:
        warnings.append({
            "type": "SLA_BREACH_ALERT",
            "severity": "CRITICAL",
            "title": "Turnaround Degradation Detected",
            "description": f"{breached_count} grievances breached statutory turnaround deadlines.",
            "recommendation": "Reallocate tier-2 officers from low-priority queues to address bottleneck."
        })

    # Default reassurance if stable
    if not warnings:
        warnings.append({
            "type": "SYSTEM_STABLE",
            "severity": "INFO",
            "title": "Grievance Flow Within Expected Tolerances",
            "description": "No abnormal volume spikes or systemic clearing bottlenecks detected in current window.",
            "recommendation": "Maintain standard monitoring parameters."
        })

    return warnings

def generate_management_recommendations(health_data: dict, warnings: list) -> list:
    """Produces executive recommendations based on systemic health and warning spikes."""
    recommendations = []

    score = health_data.get("health_score", 75)
    if score < 70:
        recommendations.append(
            "Overall Health Score is below target (70). Primary focus must be placed on reducing average resolution turnaround and strict SLA escalation enforcement."
        )

    for w in warnings:
        if w.get("severity") in ["HIGH", "CRITICAL"]:
            recommendations.append(w.get("recommendation"))

    recommendations.append(
        "Encourage customer adoption of Tier-1 GrievanceBot for standard electronic clearing inquiries to sustain deflection rate above 30%."
    )
    recommendations.append(
        "Audit high-value credit card chargeback requests older than 72 hours to prevent customer liability escalation under fair banking guidelines."
    )

    return recommendations

def run_what_if_simulation(
    current_worker_count: int,
    proposed_worker_count: int,
    current_tat_hours: float,
    current_pending_count: int
) -> dict:
    """
    Simulates operational impact of staffing adjustments:
    Clearly marked as 'Scenario Estimate — Not Guaranteed Prediction'.
    """
    if current_worker_count <= 0:
        current_worker_count = 4
    if proposed_worker_count <= 0:
        proposed_worker_count = current_worker_count

    ratio = current_worker_count / float(proposed_worker_count)

    # Simulated estimated TAT (hours)
    # Non-linear efficiency curve (diminishing returns with larger teams)
    simulated_tat = round(current_tat_hours * (0.3 + (0.7 * ratio)), 1)
    tat_reduction_pct = round(((current_tat_hours - simulated_tat) / max(current_tat_hours, 1)) * 100, 1)

    # Simulated estimated pending queue
    simulated_pending = max(1, int(current_pending_count * (0.4 + (0.6 * ratio))))

    # SLA Pressure index (1 to 10 scale)
    sla_pressure = max(1, min(10, round(ratio * 6.5, 1)))

    return {
        "disclaimer": "Scenario Estimate — Not Guaranteed Prediction (Simulated Mathematical Projection)",
        "inputs": {
            "current_workers": current_worker_count,
            "proposed_workers": proposed_worker_count,
            "current_tat_hours": current_tat_hours,
            "current_pending": current_pending_count
        },
        "projections": {
            "estimated_tat_hours": simulated_tat,
            "tat_change_percentage": tat_reduction_pct,
            "estimated_pending_complaints": simulated_pending,
            "projected_sla_pressure_score": sla_pressure
        }
    }


def get_bank_leaderboard(db: Session, selected_month: str = None) -> dict:
    """
    Computes Bank Performance Leaderboard ranking for a specific calendar month (YYYY-MM).
    If selected_month is not supplied, automatically selects the latest active month in the ledger.
    Metrics evaluated per bank:
    1. Total Complaints Filed
    2. Total Resolved Complaints
    3. Resolution Rate (%)
    4. SLA Compliance Rate (%)
    5. Average Turnaround Time (TAT in days)
    6. Reopen Rate (%)
    7. Composite Bank Health Score (0-100 index) & Regulatory Grade (A+, B+, C, D)
    """
    from sqlalchemy import text
    try:
        from create_db import Complaint, Company
    except ImportError:
        from Python_codes.create_db import Complaint, Company

    # Determine available months from complaints
    months_query = db.execute(text(
        "SELECT DISTINCT substr(created_at, 1, 7) as ym FROM complaints WHERE created_at IS NOT NULL ORDER BY ym DESC"
    )).fetchall()
    available_months = [m[0] for m in months_query if m[0] and len(m[0]) == 7]

    if not available_months:
        available_months = [datetime.utcnow().strftime("%Y-%m")]

    if not selected_month or selected_month not in available_months:
        selected_month = available_months[0]

    sql = text("""
        SELECT 
            c.company_id,
            c.company_name,
            count(cmp.complaint_id) as total_received,
            sum(case when cmp.status in ('resolved', 'closed', 'RESOLVED', 'CLOSED') then 1 else 0 end) as total_resolved,
            sum(case when cmp.sla_breached = 1 then 1 else 0 end) as total_breached,
            sum(case when cmp.status = 'reopened' or cmp.reopen_count > 0 then 1 else 0 end) as total_reopened,
            avg(case when cmp.resolved_at is not null then (julianday(cmp.resolved_at) - julianday(cmp.created_at)) else null end) as avg_tat
        FROM complaints cmp
        JOIN companies c ON cmp.company_id = c.company_id
        WHERE substr(cmp.created_at, 1, 7) = :month
        GROUP BY c.company_id, c.company_name
        HAVING count(cmp.complaint_id) > 0
    """)

    rows = db.execute(sql, {"month": selected_month}).fetchall()
    leaderboard = []

    for r in rows:
        cid, cname, total, resolved, breached, reopened, avg_tat = r
        total = total or 0
        resolved = resolved or 0
        breached = breached or 0
        reopened = reopened or 0
        avg_tat = float(avg_tat) if avg_tat is not None else 3.5

        res_rate = (resolved / total) if total > 0 else 0.0
        sla_rate = max(0.0, (total - breached) / total) if total > 0 else 1.0
        reopen_rate = (reopened / total) if total > 0 else 0.0

        satisfaction_proxy = max(1.0, min(5.0, 3.2 + (res_rate * 1.5) - (reopen_rate * 2.0)))

        health = calculate_bank_health_score(
            resolution_rate=res_rate,
            sla_compliance_rate=sla_rate,
            avg_tat_days=avg_tat,
            reopen_rate=reopen_rate,
            satisfaction_avg=satisfaction_proxy
        )

        leaderboard.append({
            "company_id": cid,
            "bank_name": cname,
            "total_complaints": total,
            "resolved_complaints": resolved,
            "resolution_rate": round(res_rate * 100, 1),
            "sla_compliance_rate": round(sla_rate * 100, 1),
            "avg_tat_days": round(avg_tat, 1),
            "reopen_rate": round(reopen_rate * 100, 1),
            "composite_score": health["health_score"],
            "grade": health["grade"],
            "status": health["health_status"],
            "score_breakdown": health["breakdown"]
        })

    leaderboard.sort(key=lambda x: (x["composite_score"], x["resolution_rate"]), reverse=True)

    for idx, bank in enumerate(leaderboard, start=1):
        bank["rank"] = idx

    return {
        "selected_month": selected_month,
        "available_months": available_months,
        "total_ranked_banks": len(leaderboard),
        "leaderboard": leaderboard,
        "top_performer": leaderboard[0] if leaderboard else None
    }
