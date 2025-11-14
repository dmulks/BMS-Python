"""
Notification Service for creating and managing user notifications.
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.models.notification import Notification, NotificationType
from app.models.user import User


class NotificationService:
    """Service for managing notifications."""

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        related_entity_type: str = None,
        related_entity_id: int = None
    ) -> Notification:
        """
        Create a new notification for a user.

        Args:
            db: Database session
            user_id: User to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            related_entity_type: Optional related entity type
            related_entity_id: Optional related entity ID

        Returns:
            Created Notification object
        """
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> Notification:
        """Mark a notification as read."""
        notification = db.query(Notification).filter(
            Notification.notification_id == notification_id
        ).first()

        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)

        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })

        db.commit()
        return count

    @staticmethod
    def get_unread_notifications(db: Session, user_id: int) -> List[Notification]:
        """Get all unread notifications for a user."""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        limit: int = 50,
        include_read: bool = True
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if not include_read:
            query = query.filter(Notification.is_read == False)

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def notify_payment_due(db: Session, user_id: int, payment_id: int, amount: float):
        """Create a payment due notification."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.PAYMENT_DUE,
            title="Payment Due",
            message=f"A coupon payment of ZMW {amount:.2f} is due.",
            related_entity_type="coupon_payment",
            related_entity_id=payment_id
        )

    @staticmethod
    def notify_payment_processed(db: Session, user_id: int, payment_id: int, amount: float):
        """Create a payment processed notification."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.PAYMENT_PROCESSED,
            title="Payment Processed",
            message=f"Your coupon payment of ZMW {amount:.2f} has been processed.",
            related_entity_type="coupon_payment",
            related_entity_id=payment_id
        )

    @staticmethod
    def notify_maturity_approaching(db: Session, user_id: int, purchase_id: int, maturity_date: str):
        """Create a maturity approaching notification."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.MATURITY_APPROACHING,
            title="Bond Maturity Approaching",
            message=f"Your bond will mature on {maturity_date}. Please prepare for redemption.",
            related_entity_type="bond_purchase",
            related_entity_id=purchase_id
        )

    @staticmethod
    def notify_rate_update(db: Session, bond_type_name: str, new_rate: float):
        """Notify all members with bonds of this type about rate update."""
        # Get all users with active bonds of this type
        from app.models.bond import BondPurchase, BondType

        bond_type = db.query(BondType).filter(BondType.bond_name == bond_type_name).first()
        if not bond_type:
            return []

        user_ids = db.query(BondPurchase.user_id).filter(
            BondPurchase.bond_type_id == bond_type.bond_type_id,
            BondPurchase.purchase_status == "active"
        ).distinct().all()

        notifications = []
        for (user_id,) in user_ids:
            notification = NotificationService.create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.RATE_UPDATE,
                title="Interest Rate Update",
                message=f"The interest rate for {bond_type_name} has been updated to {new_rate:.2%}.",
                related_entity_type="bond_type",
                related_entity_id=bond_type.bond_type_id
            )
            notifications.append(notification)

        return notifications
