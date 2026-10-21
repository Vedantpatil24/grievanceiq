"""
sla_engine.py - SLA Resolution Engine & Deadline Tracker
Strict Banking Principle: SLA begins ONLY when a complaint enters
human handling/escalation (escalated_at). Bot-only guidance does NOT run SLA.
"""

from datetime import datetime, timedelta

# SLA hours by Priority level
SLA_HOURS = {
    "High": 24,        # 24 hours (1 day) for urgent/fraud/reopened
    "Medium": 72,      # 72 hours (3 days) for standard disputes
    "Low": 168         # 168 hours (1 week) for low-priority inquiries
}

def calculate_deadline(escalated_at: datetime, priority: str) -> datetime:
    """Calculates strict deadline from the exact moment of escalation."""
    hours = SLA_HOURS.get(priority, 48)
    return escalated_at + timedelta(hours=hours)

def evaluate_sla_status(sla_deadline: datetime, status: str) -> dict:
    """
    Evaluates current SLA countdown, remaining time, warning flags,
    and breach status for an escalated ticket.
    """
    if not sla_deadline:
        return {
            "has_sla": False,
            "sla_status": "NOT_APPLICABLE",
            "hours_remaining": None,
            "formatted_remaining": "N/A (Pre-Escalation)",
            "is_breached": False,
            "badge_color": "gray"
        }

    if status in ["resolved", "closed"]:
        return {
            "has_sla": True,
            "sla_status": "COMPLETED",
            "hours_remaining": 0,
            "formatted_remaining": "Resolved within SLA",
            "is_breached": False,
            "badge_color": "green"
        }

    now = datetime.utcnow()
    diff = sla_deadline - now
    total_seconds = diff.total_seconds()
    hours_left = total_seconds / 3600.0

    if total_seconds <= 0:
        overdue_hours = abs(int(hours_left))
        return {
            "has_sla": True,
            "sla_status": "BREACHED",
            "hours_remaining": round(hours_left, 1),
            "formatted_remaining": f"BREACHED by {overdue_hours}h",
            "is_breached": True,
            "badge_color": "red"
        }
    elif hours_left <= 6:
        return {
            "has_sla": True,
            "sla_status": "CRITICAL_WARNING",
            "hours_remaining": round(hours_left, 1),
            "formatted_remaining": f"{int(hours_left)}h {int((total_seconds % 3600) // 60)}m left (Urgent)",
            "is_breached": False,
            "badge_color": "orange"
        }
    elif hours_left <= 18:
        return {
            "has_sla": True,
            "sla_status": "APPROACHING_DEADLINE",
            "hours_remaining": round(hours_left, 1),
            "formatted_remaining": f"{int(hours_left)}h {int((total_seconds % 3600) // 60)}m left",
            "is_breached": False,
            "badge_color": "yellow"
        }
    else:
        days = int(hours_left // 24)
        hrs = int(hours_left % 24)
        time_str = f"{days}d {hrs}h left" if days > 0 else f"{hrs}h left"
        return {
            "has_sla": True,
            "sla_status": "ON_TRACK",
            "hours_remaining": round(hours_left, 1),
            "formatted_remaining": time_str,
            "is_breached": False,
            "badge_color": "green"
        }
