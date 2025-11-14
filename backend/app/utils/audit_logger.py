"""
Audit Logger Utility for tracking all database changes.
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional
from app.models.audit import AuditLog


class AuditLogger:
    """Utility class for audit logging."""

    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[int],
        action_type: str,
        table_name: str,
        record_id: int,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an action to the audit trail.

        Args:
            db: Database session
            user_id: User performing the action (None for system actions)
            action_type: Type of action (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.)
            table_name: Name of the table affected
            record_id: ID of the record affected
            old_values: Previous state (for UPDATE/DELETE)
            new_values: New state (for CREATE/UPDATE)
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            Created AuditLog object
        """
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(audit_log)
        db.commit()

        return audit_log

    @staticmethod
    def log_create(
        db: Session,
        user_id: int,
        table_name: str,
        record_id: int,
        new_values: Dict,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log a CREATE action."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            action_type="CREATE",
            table_name=table_name,
            record_id=record_id,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_update(
        db: Session,
        user_id: int,
        table_name: str,
        record_id: int,
        old_values: Dict,
        new_values: Dict,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an UPDATE action."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            action_type="UPDATE",
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_delete(
        db: Session,
        user_id: int,
        table_name: str,
        record_id: int,
        old_values: Dict,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log a DELETE action."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            action_type="DELETE",
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_login(
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log a LOGIN action."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            action_type="LOGIN",
            table_name="users",
            record_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_logout(
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log a LOGOUT action."""
        return AuditLogger.log_action(
            db=db,
            user_id=user_id,
            action_type="LOGOUT",
            table_name="users",
            record_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
