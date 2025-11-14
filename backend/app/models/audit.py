from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime, Text, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    """Complete audit trail for compliance and security."""
    __tablename__ = "audit_logs"

    log_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    action_type = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    old_values = Column(JSON, nullable=True)  # Stores previous state
    new_values = Column(JSON, nullable=True)  # Stores new state
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)  # Browser/client info
    action_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'action_timestamp'),
        Index('idx_table_record', 'table_name', 'record_id'),
    )

    def __repr__(self):
        return f"<AuditLog {self.action_type} on {self.table_name}:{self.record_id}>"
