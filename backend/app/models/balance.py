from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MemberBalance(Base):
    """Monthly balance snapshots for members by bond type."""
    __tablename__ = "member_balances"

    balance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    bond_type_id = Column(Integer, ForeignKey("bond_types.bond_type_id"), nullable=False)
    balance_date = Column(Date, nullable=False, index=True)  # First day of month
    opening_balance = Column(Numeric(15, 2), default=0, nullable=False)
    purchases_month = Column(Numeric(15, 2), default=0, nullable=False)
    payments_received = Column(Numeric(15, 2), default=0, nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    total_bond_shares = Column(Numeric(15, 2), nullable=False)
    total_face_value = Column(Numeric(15, 2), nullable=False)
    percentage_share = Column(Numeric(8, 5), nullable=False)  # % of total cooperative holdings
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Add unique constraint for user + bond_type + date
    __table_args__ = (
        UniqueConstraint('user_id', 'bond_type_id', 'balance_date', name='uk_user_bond_date'),
        Index('idx_user_date', 'user_id', 'balance_date'),
    )

    def __repr__(self):
        return f"<MemberBalance user={self.user_id} date={self.balance_date}>"


class MonthlySummary(Base):
    """Pre-calculated monthly summaries for dashboards."""
    __tablename__ = "monthly_summaries"

    summary_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    summary_month = Column(Date, nullable=False, unique=True, index=True)  # First day of month
    total_bond_shares = Column(Numeric(15, 2), nullable=False)
    total_face_value = Column(Numeric(15, 2), nullable=False)
    total_purchases = Column(Numeric(15, 2), nullable=False)
    total_gross_coupons = Column(Numeric(15, 2), nullable=False)
    total_withholding_tax = Column(Numeric(15, 2), nullable=False)
    total_boz_fees = Column(Numeric(15, 2), nullable=False)
    total_coop_fees = Column(Numeric(15, 2), nullable=False)
    total_net_payments = Column(Numeric(15, 2), nullable=False)
    net_cooperative_income = Column(Numeric(15, 2), nullable=False)  # Co-op discount fees + Co-op coupon fees
    active_members_count = Column(Integer, nullable=False)
    new_purchases_count = Column(Integer, nullable=False)
    matured_bonds_count = Column(Integer, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<MonthlySummary {self.summary_month}>"
