from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Enum, Index
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enum."""
    PAYMENT_DUE = "payment_due"
    PAYMENT_PROCESSED = "payment_processed"
    MATURITY_APPROACHING = "maturity_approaching"
    RATE_UPDATE = "rate_update"
    SYSTEM = "system"


class Notification(Base):
    """System notifications for members."""
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    notification_type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    related_entity_type = Column(String(50), nullable=True)  # e.g., "bond_purchase", "coupon_payment"
    related_entity_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_user_unread', 'user_id', 'is_read'),
    )

    def __repr__(self):
        return f"<Notification {self.title} for user={self.user_id}>"
