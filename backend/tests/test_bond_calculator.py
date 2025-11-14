"""
Tests for the Bond Calculator service.
"""
import pytest
from decimal import Decimal
from datetime import date
from app.services.bond_calculator import BondCalculator


def test_calculate_face_value():
    """Test face value calculation."""
    result = BondCalculator.calculate_face_value(Decimal("10000"))
    assert result == Decimal("10000.00")

    result = BondCalculator.calculate_face_value(Decimal("5000.50"))
    assert result == Decimal("5000.50")


def test_calculate_discount_value():
    """Test discount value calculation."""
    face_value = Decimal("10000")
    result = BondCalculator.calculate_discount_value(face_value)
    assert result == Decimal("1000.00")  # 10% of 10000

    result = BondCalculator.calculate_discount_value(face_value, Decimal("0.15"))
    assert result == Decimal("1500.00")  # 15% of 10000


def test_calculate_coop_discount_fee():
    """Test co-op discount fee calculation."""
    discount_value = Decimal("1000")
    result = BondCalculator.calculate_coop_discount_fee(discount_value)
    assert result == Decimal("20.00")  # 2% of 1000


def test_calculate_purchase_price():
    """Test purchase price calculation."""
    face_value = Decimal("10000")
    discount_value = Decimal("1000")
    result = BondCalculator.calculate_purchase_price(face_value, discount_value)
    assert result == Decimal("9000")


def test_calculate_maturity_date():
    """Test maturity date calculation."""
    purchase_date = date(2024, 1, 1)
    result = BondCalculator.calculate_maturity_date(purchase_date, 2)
    expected = date(2026, 1, 1)
    assert result == expected


def test_calculate_calendar_days():
    """Test calendar days calculation."""
    start = date(2024, 1, 1)
    end = date(2024, 7, 1)
    result = BondCalculator.calculate_calendar_days(start, end)
    assert result == 182  # Days between dates


def test_calculate_daily_rate():
    """Test daily rate calculation from annual rate."""
    annual_rate = Decimal("0.0902")  # 9.02%
    result = BondCalculator.calculate_daily_rate(annual_rate)
    expected = annual_rate / Decimal("365")
    assert abs(result - expected) < Decimal("0.00000001")


def test_calculate_coupon_payment():
    """Test complete coupon payment calculation."""
    face_value = Decimal("10000")
    daily_rate = Decimal("0.000247")  # 9.02% annual / 365
    calendar_days = 183  # Semi-annual period

    result = BondCalculator.calculate_coupon_payment(
        face_value, daily_rate, calendar_days
    )

    # Verify all components are present
    assert "gross_coupon" in result
    assert "withholding_tax" in result
    assert "boz_fees" in result
    assert "coop_fees" in result
    assert "net_payment" in result

    # Verify calculations
    gross = result["gross_coupon"]
    assert gross > 0

    wht = result["withholding_tax"]
    assert wht == (gross * Decimal("0.15")).quantize(Decimal("0.01"))

    boz = result["boz_fees"]
    assert boz == (gross * Decimal("0.01")).quantize(Decimal("0.01"))

    # Verify net payment
    calculated_net = gross - wht - boz - result["coop_fees"]
    assert result["net_payment"] == calculated_net


def test_calculate_purchase_breakdown():
    """Test complete purchase breakdown calculation."""
    bond_shares = Decimal("10000")
    purchase_date = date(2024, 1, 1)
    maturity_years = 2
    discount_rate = Decimal("0.10")

    result = BondCalculator.calculate_purchase_breakdown(
        bond_shares, purchase_date, maturity_years, discount_rate
    )

    # Verify all components
    assert "face_value" in result
    assert "discount_value" in result
    assert "coop_discount_fee" in result
    assert "net_discount_value" in result
    assert "purchase_price" in result
    assert "maturity_date" in result

    # Verify values
    assert result["face_value"] == Decimal("10000.00")
    assert result["discount_value"] == Decimal("1000.00")
    assert result["coop_discount_fee"] == Decimal("20.00")
    assert result["purchase_price"] == Decimal("9000.00")
    assert result["maturity_date"] == date(2026, 1, 1)


def test_rounding_precision():
    """Test that all calculations maintain 2 decimal places."""
    face_value = Decimal("10000.33")
    daily_rate = Decimal("0.00024657")
    calendar_days = 183

    result = BondCalculator.calculate_coupon_payment(
        face_value, daily_rate, calendar_days
    )

    # All monetary values should have exactly 2 decimal places
    for key, value in result.items():
        # Convert to string and check decimal places
        str_value = str(value)
        if "." in str_value:
            decimal_places = len(str_value.split(".")[1])
            assert decimal_places == 2, f"{key} should have 2 decimal places, has {decimal_places}"
