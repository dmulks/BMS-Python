from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enum."""
    ADMIN = "admin"
    TREASURER = "treasurer"
    MEMBER = "member"


class User(Base):
    """User model for members, treasurers, and administrators."""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=True)
    address = Column(String, nullable=True)
    user_role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    bond_purchases = relationship("BondPurchase", back_populates="user")
    coupon_payments = relationship(
        "CouponPayment",
        foreign_keys="CouponPayment.user_id",
        back_populates="user"
    )
    interest_rates_entered = relationship(
        "InterestRate",
        foreign_keys="InterestRate.entered_by",
        back_populates="entered_by_user"
    )

    def __repr__(self):
        return f"<User {self.username} ({self.user_role.value})>"
