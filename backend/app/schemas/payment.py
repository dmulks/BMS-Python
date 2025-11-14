from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.payment import PaymentType, PaymentStatus, VoucherStatus


class CouponPaymentBase(BaseModel):
    """Base coupon payment schema."""
    purchase_id: int
    user_id: int
    payment_type: PaymentType
    payment_period_start: date
    payment_period_end: date


class CouponPaymentCreate(CouponPaymentBase):
    """Schema for creating a coupon payment."""
    notes: Optional[str] = None


class CouponPaymentResponse(CouponPaymentBase):
    """Schema for coupon payment response."""
    payment_id: int
    payment_date: date
    calendar_days: int
    gross_coupon_amount: Decimal
    withholding_tax: Decimal
    boz_fees: Decimal
    coop_fees: Decimal
    net_payment_amount: Decimal
    payment_status: PaymentStatus
    payment_reference: Optional[str]
    processed_by: Optional[int]
    processed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentVoucherBase(BaseModel):
    """Base payment voucher schema."""
    user_id: int
    payment_id: Optional[int] = None
    voucher_type: PaymentType
    payment_method: Optional[str] = None


class PaymentVoucherCreate(PaymentVoucherBase):
    """Schema for creating a payment voucher."""
    notes: Optional[str] = None


class PaymentVoucherResponse(PaymentVoucherBase):
    """Schema for payment voucher response."""
    voucher_id: int
    voucher_number: str
    voucher_date: date
    total_amount: Decimal
    voucher_status: VoucherStatus
    generated_by: int
    approved_by: Optional[int]
    paid_by: Optional[int]
    payment_reference: Optional[str]
    issued_at: Optional[datetime]
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
