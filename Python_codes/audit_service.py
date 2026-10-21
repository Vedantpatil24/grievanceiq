"""
audit_service.py - Audit Trail & In-App Notification Dispatcher
Records all security/operational actions into audit_logs
and generates in-app notifications for staff and customers.
"""

from sqlalchemy.orm import Session
from create_db import AuditLog, Notification
from datetime import datetime

def log_audit_event(
    db: Session,
    actor_type: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: str,
    actor_id: int = None
):
    """Writes an immutable record into audit_logs."""
    event = AuditLog(
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()

def create_notification(
    db: Session,
    complaint_id: int,
    recipient_type: str,
    notification_type: str,
    title: str,
    body: str,
    recipient_id: int = None
):
    """Creates an in-app notification record."""
    notif = Notification(
        complaint_id=complaint_id,
        recipient_type=recipient_type,
        recipient_id=recipient_id,
        notification_type=notification_type,
        title=title,
        body=body,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(notif)
    db.commit()
