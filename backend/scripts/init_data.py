"""
Script to initialize the database with sample data.
Run this after creating the admin user.
"""
import sys
sys.path.append('.')

from datetime import date
from decimal import Decimal
from app.core.database import SessionLocal
from app.models.bond import BondType
from app.models.fee import FeeStructure, FeeType, AppliesTo


def init_bond_types(db):
    """Initialize bond types."""
    bond_types = [
        {
            "bond_name": "2-Year Bond",
            "maturity_period_years": 2,
            "description": "Short-term bond with 2-year maturity period",
            "is_active": True
        },
        {
            "bond_name": "5-Year Bond",
            "maturity_period_years": 5,
            "description": "Medium-term bond with 5-year maturity period",
            "is_active": True
        },
        {
            "bond_name": "15-Year Bond",
            "maturity_period_years": 15,
            "description": "Long-term bond with 15-year maturity period",
            "is_active": True
        }
    ]

    for bt_data in bond_types:
        existing = db.query(BondType).filter(
            BondType.bond_name == bt_data["bond_name"]
        ).first()

        if not existing:
            bond_type = BondType(**bt_data)
            db.add(bond_type)
            print(f"✅ Created bond type: {bt_data['bond_name']}")
        else:
            print(f"⏭️  Bond type already exists: {bt_data['bond_name']}")

    db.commit()


def init_fee_structure(db):
    """Initialize fee structure."""
    fees = [
        {
            "fee_name": "Withholding Tax",
            "fee_type": FeeType.PERCENTAGE,
            "fee_value": Decimal("0.15"),
            "applies_to": AppliesTo.COUPON,
            "effective_from": date(2020, 1, 1),
            "is_active": True,
            "description": "15% withholding tax on gross coupon payments"
        },
        {
            "fee_name": "BOZ Fees",
            "fee_type": FeeType.PERCENTAGE,
            "fee_value": Decimal("0.01"),
            "applies_to": AppliesTo.COUPON,
            "effective_from": date(2020, 1, 1),
            "is_active": True,
            "description": "1% Bank of Zambia fees on gross coupon"
        },
        {
            "fee_name": "Co-op Discount Fee",
            "fee_type": FeeType.PERCENTAGE,
            "fee_value": Decimal("0.02"),
            "applies_to": AppliesTo.DISCOUNT,
            "effective_from": date(2020, 1, 1),
            "is_active": True,
            "description": "2% co-operative fee on discount value"
        },
        {
            "fee_name": "Co-op Coupon Fee",
            "fee_type": FeeType.PERCENTAGE,
            "fee_value": Decimal("0.02"),
            "applies_to": AppliesTo.COUPON,
            "effective_from": date(2020, 1, 1),
            "is_active": True,
            "description": "2% co-operative fee on coupon after WHT and BOZ"
        }
    ]

    for fee_data in fees:
        existing = db.query(FeeStructure).filter(
            FeeStructure.fee_name == fee_data["fee_name"]
        ).first()

        if not existing:
            fee = FeeStructure(**fee_data)
            db.add(fee)
            print(f"✅ Created fee: {fee_data['fee_name']}")
        else:
            print(f"⏭️  Fee already exists: {fee_data['fee_name']}")

    db.commit()


def main():
    """Main initialization function."""
    print("🚀 Initializing database with sample data...\n")

    db = SessionLocal()

    try:
        # Initialize bond types
        print("📊 Initializing bond types...")
        init_bond_types(db)
        print()

        # Initialize fee structure
        print("💰 Initializing fee structure...")
        init_fee_structure(db)
        print()

        print("✅ Database initialization complete!")
        print("\nYou can now:")
        print("  1. Start the API server: uvicorn app.main:app --reload")
        print("  2. Access API docs: http://localhost:8000/api/docs")
        print("  3. Login with admin credentials")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
