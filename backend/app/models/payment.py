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
