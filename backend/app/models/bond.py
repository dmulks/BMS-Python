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


class BondTypeEnum(str, enum.Enum):
    """Bond type enum for bond issues."""
    TWO_YEAR = "TWO_YEAR"
    FIVE_YEAR = "FIVE_YEAR"
    SEVEN_YEAR = "SEVEN_YEAR"
    FIFTEEN_YEAR = "FIFTEEN_YEAR"


class BondIssue(Base):
    """
    Bond issue model for cooperative bond investments.
    Represents a specific bond batch with fixed rates and dates.
    """
    __tablename__ = "bond_issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    issuer = Column(String(100), nullable=False)
    issue_name = Column(String(200), nullable=False, index=True)
    issue_date = Column(Date, nullable=False, index=True)
    maturity_date = Column(Date, nullable=False, index=True)
    bond_type = Column(Enum(BondTypeEnum), nullable=False)
    coupon_rate = Column(Numeric(8, 6), nullable=False)  # Annual coupon rate (e.g., 0.1850)
    discount_rate = Column(Numeric(8, 6), nullable=False)  # Maturity discount rate (e.g., 0.2050)
    face_value_per_unit = Column(Numeric(15, 2), nullable=True, default=1.00)
    withholding_tax_rate = Column(Numeric(5, 2), nullable=False, default=15.0)  # Percentage
    boz_fee_rate = Column(Numeric(5, 2), nullable=False, default=1.0)  # Percentage
    coop_fee_rate = Column(Numeric(5, 2), nullable=False, default=2.0)  # Percentage
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    member_holdings = relationship("MemberBondHolding", back_populates="bond_issue")
    payment_events = relationship("PaymentEvent", back_populates="bond_issue")

    def __repr__(self):
        return f"<BondIssue {self.issue_name} ({self.bond_type.value})>"


class MemberBondHolding(Base):
    """
    Member bond holding snapshots.
    Tracks each member's position in a specific bond issue as of a given date.
    """
    __tablename__ = "member_bond_holdings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    bond_id = Column(Integer, ForeignKey("bond_issues.id"), nullable=False, index=True)
    as_of_date = Column(Date, nullable=False, index=True)
    bond_shares = Column(Numeric(15, 2), nullable=False, default=0)
    opening_balance = Column(Numeric(15, 2), nullable=True, default=0)
    total_bond_share = Column(Numeric(15, 2), nullable=True, default=0)
    percentage_share = Column(Numeric(8, 6), nullable=True, default=0)
    award_value_plus_balance_bf = Column(Numeric(15, 2), nullable=True, default=0)
    variance_cf_next_period = Column(Numeric(15, 2), nullable=True, default=0)
    member_face_value = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    member = relationship("User", foreign_keys=[member_id])
    bond_issue = relationship("BondIssue", back_populates="member_holdings")

    def __repr__(self):
        return f"<MemberBondHolding Member {self.member_id} Bond {self.bond_id} - {self.bond_shares} shares>"
