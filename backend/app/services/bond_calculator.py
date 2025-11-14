from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import Dict


class BondCalculator:
    """
    Bond calculation service matching Excel formulas from the current system.

    Business Rules:
    - Face Value = Bond Shares × 1
    - Discount Value = Face Value × Discount Rate (default 10%)
    - Co-op Discount Fee = Discount Value × 2%
    - Purchase Price = Face Value - Discount Value
    - Maturity Date = Purchase Date + Maturity Years

    Coupon Payment Calculations:
    - Gross Coupon = Face Value × Daily Rate × Calendar Days
    - Withholding Tax = Gross Coupon × 15%
    - BOZ Fees = Gross Coupon × 1%
    - Co-op Fees = (Gross Coupon - WHT - BOZ) × 2%
    - Net Payment = Gross Coupon - WHT - BOZ - Co-op Fees
    """

    @staticmethod
    def calculate_face_value(bond_shares: Decimal, unit_value: Decimal = Decimal("1")) -> Decimal:
        """Calculate face value from bond shares."""
        return (bond_shares * unit_value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_discount_value(face_value: Decimal, discount_rate: Decimal = Decimal("0.10")) -> Decimal:
        """Calculate discount value."""
        return (face_value * discount_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_coop_discount_fee(discount_value: Decimal) -> Decimal:
        """Calculate co-op discount fee (2% of discount value)."""
        return (discount_value * Decimal("0.02")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_purchase_price(face_value: Decimal, discount_value: Decimal) -> Decimal:
        """Calculate purchase price."""
        return face_value - discount_value

    @staticmethod
    def calculate_maturity_date(purchase_date: date, maturity_years: int) -> date:
        """Calculate maturity date."""
        return purchase_date + timedelta(days=365 * maturity_years)

    @staticmethod
    def calculate_calendar_days(start_date: date, end_date: date) -> int:
        """Calculate calendar days between two dates."""
        return (end_date - start_date).days

    @staticmethod
    def calculate_daily_rate(annual_rate: Decimal) -> Decimal:
        """Calculate daily coupon rate from annual rate."""
        return (annual_rate / Decimal("365")).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_coupon_payment(
        face_value: Decimal,
        daily_rate: Decimal,
        calendar_days: int
    ) -> Dict[str, Decimal]:
        """
        Calculate complete coupon payment breakdown.

        Returns:
            Dict with: gross_coupon, withholding_tax, boz_fees, coop_fees, net_payment
        """
        # Calculate gross coupon
        gross_coupon = (face_value * daily_rate * Decimal(calendar_days)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Calculate deductions
        withholding_tax = (gross_coupon * Decimal("0.15")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        boz_fees = (gross_coupon * Decimal("0.01")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Co-op fees = 2% of (gross - WHT - BOZ)
        after_wht_boz = gross_coupon - withholding_tax - boz_fees
        coop_fees = (after_wht_boz * Decimal("0.02")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Net payment
        net_payment = gross_coupon - withholding_tax - boz_fees - coop_fees

        return {
            "gross_coupon": gross_coupon,
            "withholding_tax": withholding_tax,
            "boz_fees": boz_fees,
            "coop_fees": coop_fees,
            "net_payment": net_payment
        }

    @staticmethod
    def calculate_purchase_breakdown(
        bond_shares: Decimal,
        purchase_date: date,
        maturity_years: int,
        discount_rate: Decimal = Decimal("0.10")
    ) -> Dict[str, any]:
        """
        Calculate complete purchase breakdown.

        Returns all calculated values for a bond purchase.
        """
        face_value = BondCalculator.calculate_face_value(bond_shares)
        discount_value = BondCalculator.calculate_discount_value(face_value, discount_rate)
        coop_discount_fee = BondCalculator.calculate_coop_discount_fee(discount_value)
        net_discount_value = discount_value - coop_discount_fee
        purchase_price = BondCalculator.calculate_purchase_price(face_value, discount_value)
        maturity_date = BondCalculator.calculate_maturity_date(purchase_date, maturity_years)

        return {
            "face_value": face_value,
            "discount_value": discount_value,
            "coop_discount_fee": coop_discount_fee,
            "net_discount_value": net_discount_value,
            "purchase_price": purchase_price,
            "maturity_date": maturity_date
        }
