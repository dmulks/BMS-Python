"""
Reporting Service for generating monthly summaries and reports.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List

from app.models.bond import BondPurchase, BondType
from app.models.payment import CouponPayment
from app.models.balance import MemberBalance, MonthlySummary
from app.models.user import User


class ReportingService:
    """Service for generating reports and summaries."""

    @staticmethod
    def generate_monthly_summary(db: Session, month: date, generated_by: int) -> MonthlySummary:
        """
        Generate monthly summary for dashboard.

        Args:
            db: Database session
            month: First day of the month to summarize
            generated_by: User ID generating the report

        Returns:
            MonthlySummary object
        """
        # Ensure month is first day
        month = date(month.year, month.month, 1)

        # Calculate totals from active bond purchases
        bond_totals = db.query(
            func.sum(BondPurchase.bond_shares).label('total_shares'),
            func.sum(BondPurchase.face_value).label('total_face_value'),
            func.count(BondPurchase.purchase_id).label('active_count')
        ).filter(
            BondPurchase.purchase_status == "active"
        ).first()

        # Calculate purchases in this month
        purchases_totals = db.query(
            func.sum(BondPurchase.purchase_price).label('total_purchases'),
            func.sum(BondPurchase.coop_discount_fee).label('coop_discount_fees'),
            func.count(BondPurchase.purchase_id).label('new_purchases')
        ).filter(
            func.date_trunc('month', BondPurchase.purchase_date) == month
        ).first()

        # Calculate payment totals for this month
        payment_totals = db.query(
            func.sum(CouponPayment.gross_coupon_amount).label('total_gross'),
            func.sum(CouponPayment.withholding_tax).label('total_wht'),
            func.sum(CouponPayment.boz_fees).label('total_boz'),
            func.sum(CouponPayment.coop_fees).label('total_coop_fees'),
            func.sum(CouponPayment.net_payment_amount).label('total_net')
        ).filter(
            func.date_trunc('month', CouponPayment.payment_date) == month
        ).first()

        # Count matured bonds this month
        matured_count = db.query(func.count(BondPurchase.purchase_id)).filter(
            func.date_trunc('month', BondPurchase.maturity_date) == month,
            BondPurchase.purchase_status == "matured"
        ).scalar() or 0

        # Count active members
        active_members = db.query(func.count(func.distinct(BondPurchase.user_id))).filter(
            BondPurchase.purchase_status == "active"
        ).scalar() or 0

        # Calculate net cooperative income (discount fees + coupon fees)
        net_coop_income = (
            (purchases_totals.coop_discount_fees or Decimal("0")) +
            (payment_totals.total_coop_fees or Decimal("0"))
        )

        # Create summary
        summary = MonthlySummary(
            summary_month=month,
            total_bond_shares=bond_totals.total_shares or Decimal("0"),
            total_face_value=bond_totals.total_face_value or Decimal("0"),
            total_purchases=purchases_totals.total_purchases or Decimal("0"),
            total_gross_coupons=payment_totals.total_gross or Decimal("0"),
            total_withholding_tax=payment_totals.total_wht or Decimal("0"),
            total_boz_fees=payment_totals.total_boz or Decimal("0"),
            total_coop_fees=payment_totals.total_coop_fees or Decimal("0"),
            total_net_payments=payment_totals.total_net or Decimal("0"),
            net_cooperative_income=net_coop_income,
            active_members_count=active_members,
            new_purchases_count=purchases_totals.new_purchases or 0,
            matured_bonds_count=matured_count,
            generated_by=generated_by
        )

        # Check if summary already exists
        existing = db.query(MonthlySummary).filter(
            MonthlySummary.summary_month == month
        ).first()

        if existing:
            # Update existing
            for key, value in summary.__dict__.items():
                if not key.startswith('_') and key != 'summary_id':
                    setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new
            db.add(summary)
            db.commit()
            db.refresh(summary)
            return summary

    @staticmethod
    def generate_member_balances(db: Session, month: date) -> List[MemberBalance]:
        """
        Generate monthly balance snapshots for all members.

        Args:
            db: Database session
            month: First day of the month

        Returns:
            List of MemberBalance objects
        """
        # Ensure month is first day
        month = date(month.year, month.month, 1)

        # Get all users with active bonds
        users_with_bonds = db.query(User.user_id).join(
            BondPurchase, User.user_id == BondPurchase.user_id
        ).filter(BondPurchase.purchase_status == "active").distinct().all()

        # Get all bond types
        bond_types = db.query(BondType).filter(BondType.is_active == True).all()

        balances = []

        for user_id_tuple in users_with_bonds:
            user_id = user_id_tuple[0]

            for bond_type in bond_types:
                # Get previous month balance
                previous_balance = db.query(MemberBalance).filter(
                    MemberBalance.user_id == user_id,
                    MemberBalance.bond_type_id == bond_type.bond_type_id,
                    MemberBalance.balance_date < month
                ).order_by(MemberBalance.balance_date.desc()).first()

                opening_balance = previous_balance.closing_balance if previous_balance else Decimal("0")

                # Calculate purchases this month
                purchases_month = db.query(
                    func.sum(BondPurchase.purchase_price)
                ).filter(
                    BondPurchase.user_id == user_id,
                    BondPurchase.bond_type_id == bond_type.bond_type_id,
                    func.date_trunc('month', BondPurchase.purchase_date) == month
                ).scalar() or Decimal("0")

                # Calculate payments received this month
                payments_received = db.query(
                    func.sum(CouponPayment.net_payment_amount)
                ).filter(
                    CouponPayment.user_id == user_id,
                    func.date_trunc('month', CouponPayment.payment_date) == month
                ).scalar() or Decimal("0")

                # Get current totals
                current_totals = db.query(
                    func.sum(BondPurchase.bond_shares).label('shares'),
                    func.sum(BondPurchase.face_value).label('face_value')
                ).filter(
                    BondPurchase.user_id == user_id,
                    BondPurchase.bond_type_id == bond_type.bond_type_id,
                    BondPurchase.purchase_status == "active"
                ).first()

                total_shares = current_totals.shares or Decimal("0")
                total_face_value = current_totals.face_value or Decimal("0")

                # Calculate cooperative total for percentage
                coop_total = db.query(
                    func.sum(BondPurchase.face_value)
                ).filter(
                    BondPurchase.bond_type_id == bond_type.bond_type_id,
                    BondPurchase.purchase_status == "active"
                ).scalar() or Decimal("1")  # Avoid division by zero

                percentage_share = (total_face_value / coop_total * Decimal("100")).quantize(Decimal("0.00001"))

                closing_balance = opening_balance + purchases_month

                # Skip if no activity
                if total_shares == 0 and purchases_month == 0:
                    continue

                balance = MemberBalance(
                    user_id=user_id,
                    bond_type_id=bond_type.bond_type_id,
                    balance_date=month,
                    opening_balance=opening_balance,
                    purchases_month=purchases_month,
                    payments_received=payments_received,
                    closing_balance=closing_balance,
                    total_bond_shares=total_shares,
                    total_face_value=total_face_value,
                    percentage_share=percentage_share
                )

                # Check if balance already exists
                existing = db.query(MemberBalance).filter(
                    MemberBalance.user_id == user_id,
                    MemberBalance.bond_type_id == bond_type.bond_type_id,
                    MemberBalance.balance_date == month
                ).first()

                if existing:
                    # Update existing
                    for key, value in balance.__dict__.items():
                        if not key.startswith('_') and key != 'balance_id':
                            setattr(existing, key, value)
                    balances.append(existing)
                else:
                    db.add(balance)
                    balances.append(balance)

        db.commit()
        return balances

    @staticmethod
    def get_member_portfolio(db: Session, user_id: int) -> Dict:
        """
        Get complete portfolio for a member.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with portfolio details
        """
        # Get all active purchases
        purchases = db.query(BondPurchase).filter(
            BondPurchase.user_id == user_id,
            BondPurchase.purchase_status == "active"
        ).all()

        # Calculate totals
        total_investment = sum(p.purchase_price for p in purchases)
        total_face_value = sum(p.face_value for p in purchases)
        total_shares = sum(p.bond_shares for p in purchases)

        # Get recent payments
        recent_payments = db.query(CouponPayment).filter(
            CouponPayment.user_id == user_id
        ).order_by(CouponPayment.payment_date.desc()).limit(10).all()

        return {
            "user_id": user_id,
            "total_investment": float(total_investment),
            "total_face_value": float(total_face_value),
            "total_shares": float(total_shares),
            "active_bonds_count": len(purchases),
            "purchases": purchases,
            "recent_payments": recent_payments
        }
