from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.models import (
    BondIssue, MemberBondHolding, PaymentEvent, MemberPayment,
    User, EventType
)


class PaymentCalculationResult:
    """Data class for payment calculation results."""
    def __init__(
        self,
        member_id: int,
        member_code: str,
        member_name: str,
        bond_shares: Decimal,
        percentage_share: Decimal,
        member_face_value: Decimal,
        # BOZ Award fields
        boz_award_value: Decimal = Decimal("0"),
        # Discount fields
        base_amount: Decimal = Decimal("0"),
        coop_discount_fee: Decimal = Decimal("0"),
        net_discount_value: Decimal = Decimal("0"),
        # Coupon fields
        gross_coupon_from_boz: Decimal = Decimal("0"),
        withholding_tax: Decimal = Decimal("0"),
        boz_fee: Decimal = Decimal("0"),
        coop_fee_on_coupon: Decimal = Decimal("0"),
        net_maturity_coupon: Decimal = Decimal("0"),
        net_coupon_payment: Decimal = Decimal("0"),
        calculation_period: str = ""
    ):
        self.member_id = member_id
        self.member_code = member_code
        self.member_name = member_name
        self.bond_shares = bond_shares
        self.percentage_share = percentage_share
        self.member_face_value = member_face_value
        self.boz_award_value = boz_award_value
        self.base_amount = base_amount
        self.coop_discount_fee = coop_discount_fee
        self.net_discount_value = net_discount_value
        self.gross_coupon_from_boz = gross_coupon_from_boz
        self.withholding_tax = withholding_tax
        self.boz_fee = boz_fee
        self.coop_fee_on_coupon = coop_fee_on_coupon
        self.net_maturity_coupon = net_maturity_coupon
        self.net_coupon_payment = net_coupon_payment
        self.calculation_period = calculation_period

    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            "member_id": self.member_id,
            "member_code": self.member_code,
            "member_name": self.member_name,
            "bond_shares": float(self.bond_shares),
            "percentage_share": float(self.percentage_share),
            "member_face_value": float(self.member_face_value),
            "boz_award_value": float(self.boz_award_value),
            "base_amount": float(self.base_amount),
            "coop_discount_fee": float(self.coop_discount_fee),
            "net_discount_value": float(self.net_discount_value),
            "gross_coupon_from_boz": float(self.gross_coupon_from_boz),
            "withholding_tax": float(self.withholding_tax),
            "boz_fee": float(self.boz_fee),
            "coop_fee_on_coupon": float(self.coop_fee_on_coupon),
            "net_maturity_coupon": float(self.net_maturity_coupon),
            "net_coupon_payment": float(self.net_coupon_payment),
            "calculation_period": self.calculation_period
        }


class PaymentCalculatorService:
    """
    Payment calculation service for bond issues.
    Implements the Excel logic for BOZ awards, discount values, and coupon payments.
    """

    @staticmethod
    def _round(value: Decimal) -> Decimal:
        """Round to 2 decimal places."""
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_payments_for_event(
        db: Session,
        event_id: int
    ) -> List[PaymentCalculationResult]:
        """
        Calculate all member payments for a specific event.
        This is used for both preview and generate operations.

        Returns a list of PaymentCalculationResult objects.
        """
        # Get payment event
        event = db.query(PaymentEvent).filter(PaymentEvent.id == event_id).first()
        if not event:
            raise ValueError(f"Payment event {event_id} not found")

        # Get bond issue
        bond = db.query(BondIssue).filter(BondIssue.id == event.bond_id).first()
        if not bond:
            raise ValueError(f"Bond issue {event.bond_id} not found")

        # Get all member holdings for this bond as of the payment date
        holdings = db.query(MemberBondHolding, User).join(
            User, User.user_id == MemberBondHolding.member_id
        ).filter(
            MemberBondHolding.bond_id == event.bond_id,
            MemberBondHolding.as_of_date <= event.payment_date
        ).all()

        if not holdings:
            return []

        # Calculate total shares for percentage calculation
        total_shares = sum(Decimal(str(h.MemberBondHolding.bond_shares)) for h in holdings)

        if total_shares == 0:
            return []

        # Get rates from event or bond
        wht_rate = Decimal(str(event.withholding_tax_rate or bond.withholding_tax_rate)) / Decimal("100")
        boz_fee_rate = Decimal(str(event.boz_fee_rate or bond.boz_fee_rate)) / Decimal("100")
        coop_fee_rate = Decimal(str(event.coop_fee_rate or bond.coop_fee_rate)) / Decimal("100")

        # BOZ award amount (total to distribute)
        total_boz_award = Decimal(str(event.boz_award_amount or 0))

        results = []

        for holding, user in holdings:
            member_shares = Decimal(str(holding.bond_shares))
            member_face_value = Decimal(str(holding.member_face_value))

            # Calculate percentage share
            percentage_share = PaymentCalculatorService._round(
                (member_shares / total_shares) * Decimal("100")
            ) if total_shares > 0 else Decimal("0")

            # Calculate BOZ award allocation
            boz_award_value = PaymentCalculatorService._round(
                (member_shares / total_shares) * total_boz_award
            ) if total_shares > 0 else Decimal("0")

            result = PaymentCalculationResult(
                member_id=user.user_id,
                member_code=user.username,
                member_name=f"{user.first_name} {user.last_name}",
                bond_shares=member_shares,
                percentage_share=percentage_share,
                member_face_value=member_face_value,
                boz_award_value=boz_award_value,
                calculation_period=event.calculation_period or ""
            )

            # Calculate based on event type
            if event.event_type == EventType.DISCOUNT_MATURITY:
                # Discount Value = Face Value - BOZ Award Value
                discount_value = member_face_value - boz_award_value
                result.base_amount = PaymentCalculatorService._round(discount_value)

                # Co-op discount fee = Discount Value * coop_fee_rate
                result.coop_discount_fee = PaymentCalculatorService._round(
                    discount_value * coop_fee_rate
                )

                # Net discount value = Discount Value - coop_discount_fee
                result.net_discount_value = PaymentCalculatorService._round(
                    discount_value - result.coop_discount_fee
                )

                # Maturity Coupon calculation
                effective_rate = Decimal(str(event.base_rate or bond.discount_rate))
                gross_coupon = PaymentCalculatorService._round(
                    member_face_value * effective_rate
                )
                result.gross_coupon_from_boz = gross_coupon

                result.withholding_tax = PaymentCalculatorService._round(
                    gross_coupon * wht_rate
                )
                result.boz_fee = PaymentCalculatorService._round(
                    gross_coupon * boz_fee_rate
                )
                result.net_maturity_coupon = PaymentCalculatorService._round(
                    gross_coupon - result.withholding_tax - result.boz_fee
                )

            elif event.event_type == EventType.COUPON_SEMI_ANNUAL:
                # Semi-annual coupon rate (annual rate / 2)
                annual_rate = Decimal(str(event.base_rate or bond.coupon_rate))
                coupon_rate_period = annual_rate / Decimal("2")

                # Base amount = member_face_value * coupon_rate_period
                base_amount = PaymentCalculatorService._round(
                    member_face_value * coupon_rate_period
                )
                result.base_amount = base_amount
                result.gross_coupon_from_boz = base_amount

                # Withholding tax
                result.withholding_tax = PaymentCalculatorService._round(
                    base_amount * wht_rate
                )

                # BOZ fee
                result.boz_fee = PaymentCalculatorService._round(
                    base_amount * boz_fee_rate
                )

                # Co-op fee on coupon
                result.coop_fee_on_coupon = PaymentCalculatorService._round(
                    base_amount * coop_fee_rate
                )

                # Net coupon payment
                result.net_coupon_payment = PaymentCalculatorService._round(
                    base_amount - result.withholding_tax - result.boz_fee - result.coop_fee_on_coupon
                )

            results.append(result)

        return results

    @staticmethod
    def generate_payments_for_event(
        db: Session,
        event_id: int
    ) -> int:
        """
        Generate and save member payment records for an event.
        Returns the number of payment records created.
        """
        # Calculate payments
        calculations = PaymentCalculatorService.calculate_payments_for_event(db, event_id)

        # Get event and bond
        event = db.query(PaymentEvent).filter(PaymentEvent.id == event_id).first()

        # Create MemberPayment records
        count = 0
        for calc in calculations:
            payment = MemberPayment(
                member_id=calc.member_id,
                bond_id=event.bond_id,
                payment_event_id=event_id,
                boz_award_value=calc.boz_award_value,
                base_amount=calc.base_amount,
                coop_discount_fee=calc.coop_discount_fee,
                net_discount_value=calc.net_discount_value,
                gross_coupon_from_boz=calc.gross_coupon_from_boz,
                withholding_tax=calc.withholding_tax,
                boz_fee=calc.boz_fee,
                coop_fee_on_coupon=calc.coop_fee_on_coupon,
                net_maturity_coupon=calc.net_maturity_coupon,
                net_coupon_payment=calc.net_coupon_payment,
                calculation_period=calc.calculation_period
            )
            db.add(payment)
            count += 1

        db.commit()
        return count

    @staticmethod
    def recalculate_payments_for_event(
        db: Session,
        event_id: int
    ) -> int:
        """
        Delete existing payments and regenerate them for an event.
        Returns the number of payment records created.
        """
        # Delete existing payments
        db.query(MemberPayment).filter(
            MemberPayment.payment_event_id == event_id
        ).delete()
        db.commit()

        # Regenerate
        return PaymentCalculatorService.generate_payments_for_event(db, event_id)

    @staticmethod
    def get_member_payments(
        db: Session,
        member_id: int,
        bond_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get all payments for a specific member, optionally filtered by bond.
        Returns payment records with event and bond details.
        """
        query = db.query(MemberPayment, PaymentEvent, BondIssue, User).join(
            PaymentEvent, PaymentEvent.id == MemberPayment.payment_event_id
        ).join(
            BondIssue, BondIssue.id == MemberPayment.bond_id
        ).join(
            User, User.user_id == MemberPayment.member_id
        ).filter(
            MemberPayment.member_id == member_id
        )

        if bond_id:
            query = query.filter(MemberPayment.bond_id == bond_id)

        results = query.order_by(PaymentEvent.payment_date.desc()).all()

        payments = []
        for payment, event, bond, user in results:
            # Get member's bond holding for shares and face value
            holding = db.query(MemberBondHolding).filter(
                MemberBondHolding.member_id == member_id,
                MemberBondHolding.bond_id == payment.bond_id
            ).first()

            bond_shares = float(holding.bond_shares) if holding else 0
            member_face_value = float(holding.member_face_value) if holding else 0

            payments.append({
                "payment_id": payment.id,
                "member_id": payment.member_id,
                "member_name": f"{user.first_name} {user.last_name}",
                "bond_id": payment.bond_id,
                "bond_name": bond.issue_name,
                "bond_shares": bond_shares,
                "member_face_value": member_face_value,
                "event_id": payment.payment_event_id,
                "event_name": event.event_name,
                "event_type": event.event_type.value,
                "payment_date": event.payment_date.isoformat(),
                "boz_award_value": float(payment.boz_award_value or 0),
                "base_amount": float(payment.base_amount or 0),
                "coop_discount_fee": float(payment.coop_discount_fee or 0),
                "net_discount_value": float(payment.net_discount_value or 0),
                "gross_coupon_from_boz": float(payment.gross_coupon_from_boz or 0),
                "withholding_tax": float(payment.withholding_tax or 0),
                "boz_fee": float(payment.boz_fee or 0),
                "coop_fee_on_coupon": float(payment.coop_fee_on_coupon or 0),
                "net_maturity_coupon": float(payment.net_maturity_coupon or 0),
                "net_coupon_payment": float(payment.net_coupon_payment or 0),
                "calculation_period": payment.calculation_period or ""
            })

        return payments

    @staticmethod
    def get_audit_report(db: Session) -> List[Dict]:
        """
        Generate audit report comparing calculated totals vs expected totals from BOZ.
        Returns event-level aggregations with discrepancies.
        """
        events = db.query(PaymentEvent, BondIssue).join(
            BondIssue, BondIssue.id == PaymentEvent.bond_id
        ).all()

        report = []
        for event, bond in events:
            # Aggregate calculated totals
            totals = db.query(
                func.sum(MemberPayment.net_maturity_coupon).label('total_net_maturity'),
                func.sum(MemberPayment.net_coupon_payment).label('total_net_coupon')
            ).filter(
                MemberPayment.payment_event_id == event.id
            ).first()

            total_net_maturity = Decimal(str(totals.total_net_maturity or 0))
            total_net_coupon = Decimal(str(totals.total_net_coupon or 0))

            expected_net_maturity = Decimal(str(event.expected_total_net_maturity or 0))
            expected_net_coupon = Decimal(str(event.expected_total_net_coupon or 0))

            # Calculate differences
            maturity_diff = total_net_maturity - expected_net_maturity
            coupon_diff = total_net_coupon - expected_net_coupon

            report.append({
                "event_id": event.id,
                "event_name": event.event_name,
                "event_type": event.event_type.value,
                "payment_date": event.payment_date.isoformat(),
                "bond_name": bond.issue_name,
                "calculated_net_maturity": float(total_net_maturity),
                "expected_net_maturity": float(expected_net_maturity),
                "maturity_difference": float(maturity_diff),
                "calculated_net_coupon": float(total_net_coupon),
                "expected_net_coupon": float(expected_net_coupon),
                "coupon_difference": float(coupon_diff),
                "has_discrepancy": abs(maturity_diff) > Decimal("0.01") or abs(coupon_diff) > Decimal("0.01")
            })

        return report
