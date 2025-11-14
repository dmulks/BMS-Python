from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.bond import PurchaseStatus


class BondTypeBase(BaseModel):
    """Base bond type schema."""
    bond_name: str
    maturity_period_years: int = Field(..., gt=0)
    description: Optional[str] = None


class BondTypeCreate(BondTypeBase):
    """Schema for creating a bond type."""
    pass


class BondTypeResponse(BondTypeBase):
    """Schema for bond type response."""
    bond_type_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InterestRateBase(BaseModel):
    """Base interest rate schema."""
    bond_type_id: int
    effective_month: date
    annual_rate: Decimal = Field(..., gt=0, le=1)
    notes: Optional[str] = None


class InterestRateCreate(InterestRateBase):
    """Schema for creating an interest rate."""
    pass


class InterestRateResponse(InterestRateBase):
    """Schema for interest rate response."""
    rate_id: int
    daily_coupon_rate: Decimal
    entered_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class BondPurchaseBase(BaseModel):
    """Base bond purchase schema."""
    user_id: int
    bond_type_id: int
    purchase_date: date
    bond_shares: Decimal = Field(..., gt=0)
    discount_rate: Optional[Decimal] = Decimal("0.10")
    notes: Optional[str] = None


class BondPurchaseCreate(BondPurchaseBase):
    """Schema for creating a bond purchase."""
    pass


class BondPurchaseResponse(BaseModel):
    """Schema for bond purchase response."""
    purchase_id: int
    user_id: int
    bond_type_id: int
    purchase_date: date
    purchase_month: date
    bond_shares: Decimal
    face_value: Decimal
    discount_value: Decimal
    coop_discount_fee: Decimal
    net_discount_value: Decimal
    purchase_price: Decimal
    maturity_date: date
    purchase_status: PurchaseStatus
    transaction_reference: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
