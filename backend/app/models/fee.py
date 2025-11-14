from sqlalchemy import Column, Integer, String, Numeric, Date, Enum, Boolean, DateTime, Text
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class FeeType(str, enum.Enum):
    """Fee type enum."""
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class AppliesTo(str, enum.Enum):
    """What the fee applies to."""
    COUPON = "coupon"
    DISCOUNT = "discount"
    REDEMPTION = "redemption"
    ALL = "all"


class FeeStructure(Base):
    """Configurable fee percentages and amounts."""
    __tablename__ = "fee_structure"

    fee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fee_name = Column(String(100), nullable=False)
    fee_type = Column(Enum(FeeType), nullable=False)
    fee_value = Column(Numeric(10, 4), nullable=False)  # e.g., 0.15 for 15%
    applies_to = Column(Enum(AppliesTo), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<FeeStructure {self.fee_name} - {self.fee_value}>"
