from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class MemberBalanceResponse(BaseModel):
    """Schema for member balance response."""
    balance_id: int
    user_id: int
    bond_type_id: int
    balance_date: date
    opening_balance: Decimal
    purchases_month: Decimal
    payments_received: Decimal
    closing_balance: Decimal
    total_bond_shares: Decimal
    total_face_value: Decimal
    percentage_share: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class MonthlySummaryResponse(BaseModel):
    """Schema for monthly summary response."""
    summary_id: int
    summary_month: date
    total_bond_shares: Decimal
    total_face_value: Decimal
    total_purchases: Decimal
    total_gross_coupons: Decimal
    total_withholding_tax: Decimal
    total_boz_fees: Decimal
    total_coop_fees: Decimal
    total_net_payments: Decimal
    net_cooperative_income: Decimal
    active_members_count: int
    new_purchases_count: int
    matured_bonds_count: int
    generated_by: int
    generated_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    notification_id: int
    user_id: int
    notification_type: str
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime]
    related_entity_type: Optional[str]
    related_entity_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class SystemSettingResponse(BaseModel):
    """Schema for system setting response."""
    setting_id: int
    setting_key: str
    setting_value: str
    setting_type: str
    category: str
    description: Optional[str]
    is_editable: bool
    updated_by: Optional[int]
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemSettingUpdate(BaseModel):
    """Schema for updating system setting."""
    setting_value: str
