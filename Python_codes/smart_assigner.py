"""
smart_assigner.py - Smart Agent & Department Assignment Engine
Routes escalated grievances to the optimal active officer in the matching
banking department based on current workload.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from create_db import User, Complaint, AssignmentHistory
from datetime import datetime

def assign_optimal_officer(
    db: Session,
    complaint: Complaint,
    reason: str = "Automated Department Routing upon Escalation",
    assigned_by_id: int = None
) -> User:
    """
    Finds active officers in complaint.department_id and assigns the one
    with the fewest open/in-progress tickets (workload balancing).
    """
    # 1. Query candidate officers
    query = db.query(User).filter(
        User.is_active == True,
        User.role.in_(["officer", "staff", "admin"])
    )
    if complaint.department_id:
        dept_officers = query.filter(User.department_id == complaint.department_id).all()
        if dept_officers:
            candidates = dept_officers
        else:
            candidates = query.all()
    else:
        candidates = query.all()

    if not candidates:
        return None

    # 2. Count active assigned tickets for each candidate
    best_officer = candidates[0]
    min_workload = 999999

    for officer in candidates:
        active_count = db.query(func.count(Complaint.complaint_id)).filter(
            Complaint.current_assigned_officer_id == officer.user_id,
            Complaint.status.in_(["open", "in_progress", "escalated", "reopened"])
        ).scalar()

        if active_count < min_workload:
            min_workload = active_count
            best_officer = officer

    # 3. Apply assignment
    prev_officer_id = complaint.current_assigned_officer_id
    complaint.current_assigned_officer_id = best_officer.user_id

    # 4. Log in AssignmentHistory
    now = datetime.utcnow()
    # Close previous assignment if exists
    if prev_officer_id and prev_officer_id != best_officer.user_id:
        last_assignment = db.query(AssignmentHistory).filter(
            AssignmentHistory.complaint_id == complaint.complaint_id,
            AssignmentHistory.officer_id == prev_officer_id,
            AssignmentHistory.unassigned_at == None
        ).first()
        if last_assignment:
            last_assignment.unassigned_at = now

    new_hist = AssignmentHistory(
        complaint_id=complaint.complaint_id,
        officer_id=best_officer.user_id,
        assigned_at=now,
        reason=reason,
        assigned_by=assigned_by_id
    )
    db.add(new_hist)
    db.commit()

    return best_officer
