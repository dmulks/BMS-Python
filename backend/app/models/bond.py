from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class BondType(Base):
    """Bond type model (2-year, 5-year, 15-year bonds)."""
    __tablename__ = "bond_types"

    bond_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bond_name = Column(String(100), nullable=False)
    maturity_period_years = Column(Integer, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    interest_rates = relationship("InterestRate", back_populates="bond_type")
    bond_purchases = relationship("BondPurchase", back_populates="bond_type")

    def __repr__(self):
        return f"<BondType {self.bond_name} ({self.maturity_period_years} years)>"


class InterestRate(Base):
    """Monthly variable interest rates for each bond type."""
    __tablename__ = "interest_rates"

    rate_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bond_type_id = Column(Integer, ForeignKey("bond_types.bond_type_id"), nullable=False)
    effective_month = Column(Date, nullable=False, index=True)
    annual_rate = Column(Numeric(5, 4), nullable=False)  # e.g., 0.0902 for 9.02%
    daily_coupon_rate = Column(Numeric(10, 8), nullable=False)  # annual_rate / 365
    entered_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    bond_type = relationship("BondType", back_populates="interest_rates")
    entered_by_user = relationship("User", foreign_keys=[entered_by], back_populates="interest_rates_entered")

    def __repr__(self):
        return f"<InterestRate {self.annual_rate} for {self.effective_month}>"


class PurchaseStatus(str, enum.Enum):
    """Bond purchase status enum."""
    ACTIVE = "active"
    MATURED = "matured"
    REDEEMED = "redeemed"
    CANCELLED = "cancelled"


class BondPurchase(Base):
    """Bond purchase transaction records."""
    __tablename__ = "bond_purchases"

    purchase_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    bond_type_id = Column(Integer, ForeignKey("bond_types.bond_type_id"), nullable=False)
    purchase_date = Column(Date, nullable=False, index=True)
    purchase_month = Column(Date, nullable=False)  # First day of month
    bond_shares = Column(Numeric(15, 2), nullable=False)
    face_value = Column(Numeric(15, 2), nullable=False)
    discount_value = Column(Numeric(15, 2), nullable=False)
    coop_discount_fee = Column(Numeric(15, 2), nullable=False)  # 2% of discount
    net_discount_value = Column(Numeric(15, 2), nullable=False)
    purchase_price = Column(Numeric(15, 2), nullable=False)  # face_value - discount_value
    maturity_date = Column(Date, nullable=False, index=True)
    purchase_status = Column(Enum(PurchaseStatus), default=PurchaseStatus.ACTIVE, nullable=False)
    transaction_reference = Column(String(50), unique=True, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="bond_purchases")
    bond_type = relationship("BondType", back_populates="bond_purchases")
    coupon_payments = relationship("CouponPayment", back_populates="bond_purchase")

    def __repr__(self):
        return f"<BondPurchase {self.transaction_reference} - {self.bond_shares} shares>"
