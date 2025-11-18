from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PaymentType(str, enum.Enum):
    """Payment type enum."""
    SEMI_ANNUAL = "semi-annual"
    MATURITY = "maturity"
    EARLY_REDEMPTION = "early_redemption"


class PaymentStatus(str, enum.Enum):
    """Payment status enum."""
    PENDING = "pending"
    PROCESSED = "processed"
    PAID = "paid"
    CANCELLED = "cancelled"


class CouponPayment(Base):
    """Interest payment tracking with fee deductions."""
    __tablename__ = "coupon_payments"

    payment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey("bond_purchases.purchase_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    payment_period_start = Column(Date, nullable=False)
    payment_period_end = Column(Date, nullable=False)
    calendar_days = Column(Integer, nullable=False)
    gross_coupon_amount = Column(Numeric(15, 2), nullable=False)
    withholding_tax = Column(Numeric(15, 2), nullable=False)  # 15%
    boz_fees = Column(Numeric(15, 2), nullable=False)  # 1%
    coop_fees = Column(Numeric(15, 2), nullable=False)  # 2% after WHT and BOZ
    net_payment_amount = Column(Numeric(15, 2), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    payment_reference = Column(String(50), unique=True, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    bond_purchase = relationship("BondPurchase", back_populates="coupon_payments")
    user = relationship("User", foreign_keys=[user_id], back_populates="coupon_payments")
    voucher = relationship("PaymentVoucher", back_populates="payment", uselist=False)

    def __repr__(self):
        return f"<CouponPayment {self.payment_reference} - ${self.net_payment_amount}>"


class VoucherStatus(str, enum.Enum):
    """Voucher status enum."""
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentVoucher(Base):
    """Payment vouchers for printing and record-keeping."""
    __tablename__ = "payment_vouchers"

    voucher_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    voucher_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("coupon_payments.payment_id"), nullable=True)
    voucher_date = Column(Date, nullable=False)
    voucher_type = Column(Enum(PaymentType), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    voucher_status = Column(Enum(VoucherStatus), default=VoucherStatus.DRAFT, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    paid_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    payment_method = Column(String(50), nullable=True)  # bank_transfer, cheque, cash, mobile_money
    payment_reference = Column(String(100), nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    payment = relationship("CouponPayment", back_populates="voucher")

    def __repr__(self):
        return f"<PaymentVoucher {self.voucher_number} - {self.voucher_status.value}>"


class EventType(str, enum.Enum):
    """Payment event type enum."""
    DISCOUNT_MATURITY = "DISCOUNT_MATURITY"
    COUPON_SEMI_ANNUAL = "COUPON_SEMI_ANNUAL"


class PaymentEvent(Base):
    """
    Payment events for bond issues (maturity or coupon events).
    Defines when payments should be calculated and distributed.
    """
    __tablename__ = "payment_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bond_id = Column(Integer, ForeignKey("bond_issues.id"), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    event_name = Column(String(200), nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    calculation_period = Column(String(100), nullable=True)
    base_rate = Column(Numeric(8, 6), nullable=True)  # Override rate if needed
    withholding_tax_rate = Column(Numeric(5, 2), nullable=True)
    boz_fee_rate = Column(Numeric(5, 2), nullable=True)
    coop_fee_rate = Column(Numeric(5, 2), nullable=True)
    boz_award_amount = Column(Numeric(15, 2), nullable=True, default=0)  # Total BOZ award for distribution
    expected_total_net_maturity = Column(Numeric(15, 2), nullable=True, default=0)
    expected_total_net_coupon = Column(Numeric(15, 2), nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    bond_issue = relationship("BondIssue", back_populates="payment_events")
    member_payments = relationship("MemberPayment", back_populates="payment_event")

    def __repr__(self):
        return f"<PaymentEvent {self.event_name} - {self.event_type.value}>"


class MemberPayment(Base):
    """
    Calculated payment records per member per event.
    Stores all payment breakdown fields for audit and reporting.
    """
    __tablename__ = "member_payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    bond_id = Column(Integer, ForeignKey("bond_issues.id"), nullable=False, index=True)
    payment_event_id = Column(Integer, ForeignKey("payment_events.id"), nullable=False, index=True)

    # BOZ Award fields (for maturity)
    boz_award_value = Column(Numeric(15, 2), nullable=True, default=0)

    # Discount value fields (for maturity)
    base_amount = Column(Numeric(15, 2), nullable=True, default=0)  # Discount Value
    coop_discount_fee = Column(Numeric(15, 2), nullable=True, default=0)
    net_discount_value = Column(Numeric(15, 2), nullable=True, default=0)

    # Coupon payment fields
    gross_coupon_from_boz = Column(Numeric(15, 2), nullable=True, default=0)
    withholding_tax = Column(Numeric(15, 2), nullable=True, default=0)
    boz_fee = Column(Numeric(15, 2), nullable=True, default=0)
    coop_fee_on_coupon = Column(Numeric(15, 2), nullable=True, default=0)
    net_maturity_coupon = Column(Numeric(15, 2), nullable=True, default=0)
    net_coupon_payment = Column(Numeric(15, 2), nullable=True, default=0)

    calculation_period = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    member = relationship("User", foreign_keys=[member_id])
    bond_issue = relationship("BondIssue", foreign_keys=[bond_id])
    payment_event = relationship("PaymentEvent", back_populates="member_payments")

    def __repr__(self):
        return f"<MemberPayment Member {self.member_id} Event {self.payment_event_id}>"
