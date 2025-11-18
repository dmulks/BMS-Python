"""
Excel Import Script for Bond Holdings

This script imports bond holdings from an Excel file (e.g., "Coupon Payment Calculations 2023.xlsx")
and creates:
1. BondIssue record
2. Member records (if they don't exist)
3. MemberBondHolding records

Usage:
    python scripts/import_bond_holdings.py <excel_file_path> [--sheet-name <name>]

Example:
    python scripts/import_bond_holdings.py "Coupon Payment Calculations 2023.xlsx"
"""

import sys
import argparse
from pathlib import Path
from datetime import date
from decimal import Decimal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.models import BondIssue, User, MemberBondHolding, BondTypeEnum, UserRole
from app.core.security import get_password_hash


def create_bond_issue(
    db: Session,
    issuer: str,
    issue_name: str,
    issue_date: date,
    maturity_date: date,
    bond_type: BondTypeEnum,
    coupon_rate: Decimal,
    discount_rate: Decimal,
    withholding_tax_rate: Decimal = Decimal("15.0"),
    boz_fee_rate: Decimal = Decimal("1.0"),
    coop_fee_rate: Decimal = Decimal("2.0")
) -> BondIssue:
    """Create a bond issue record."""
    bond = BondIssue(
        issuer=issuer,
        issue_name=issue_name,
        issue_date=issue_date,
        maturity_date=maturity_date,
        bond_type=bond_type,
        coupon_rate=coupon_rate,
        discount_rate=discount_rate,
        withholding_tax_rate=withholding_tax_rate,
        boz_fee_rate=boz_fee_rate,
        coop_fee_rate=coop_fee_rate
    )
    db.add(bond)
    db.commit()
    db.refresh(bond)
    print(f"✓ Created bond issue: {bond.issue_name} (ID: {bond.id})")
    return bond


def upsert_member(
    db: Session,
    member_code: str,
    first_name: str,
    last_name: str,
    email: str = None,
    members_cache: dict = None
) -> User:
    """
    Create or update a member.
    Uses cache to avoid repeated queries.
    """
    if members_cache is not None and member_code in members_cache:
        return members_cache[member_code]

    # Try to find by username (member_code)
    member = db.query(User).filter(User.username == member_code).first()

    if member is None:
        # Create new member
        if email is None or '@' not in email:
            email = f"{member_code}@placeholder.com"

        member = User(
            username=member_code,
            email=email.lower(),
            password_hash=get_password_hash("change123"),  # Default password
            first_name=first_name,
            last_name=last_name,
            user_role=UserRole.MEMBER,
            is_active=True
        )
        db.add(member)
        db.flush()
        print(f"  ✓ Created member: {first_name} {last_name} ({member_code})")
    else:
        # Update if names changed
        if member.first_name != first_name or member.last_name != last_name:
            member.first_name = first_name
            member.last_name = last_name
            print(f"  ✓ Updated member: {first_name} {last_name} ({member_code})")

    if members_cache is not None:
        members_cache[member_code] = member

    return member


def import_excel(
    excel_file: str,
    sheet_name: str = 0,
    bond_params: dict = None
):
    """
    Import bond holdings from Excel file.

    Args:
        excel_file: Path to Excel file
        sheet_name: Sheet name or index (default: 0)
        bond_params: Dict with bond issue parameters
    """
    print(f"\n📊 Importing from: {excel_file}")
    print(f"📄 Sheet: {sheet_name}")

    # Read Excel file
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"✓ Read {len(df)} rows from Excel")
    except Exception as e:
        print(f"✗ Failed to read Excel file: {e}")
        return

    # Create database session
    db = SessionLocal()

    try:
        # Create bond issue
        if bond_params is None:
            bond_params = {
                "issuer": "Bank of Zambia",
                "issue_name": "BOZ Coupon Dec 2023",
                "issue_date": date(2023, 12, 26),
                "maturity_date": date(2025, 12, 26),
                "bond_type": BondTypeEnum.TWO_YEAR,
                "coupon_rate": Decimal("0.1850"),
                "discount_rate": Decimal("0.2050"),
                "withholding_tax_rate": Decimal("15.0"),
                "boz_fee_rate": Decimal("1.0"),
                "coop_fee_rate": Decimal("2.0")
            }

        bond = create_bond_issue(db, **bond_params)

        # Cache for members
        members_cache = {}

        # Import holdings
        holdings_created = 0
        holdings_skipped = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                # Skip rows without bond shares
                if pd.isna(row.get('Bond Shares')) or float(row.get('Bond Shares', 0)) == 0:
                    holdings_skipped += 1
                    continue

                # Extract member data
                member_code = str(row.get('No', '')).strip()
                first_name = str(row.get('First Name', '')).strip()
                last_name = str(row.get('Last Name', '')).strip()
                email = str(row.get('Email', '')).strip() if not pd.isna(row.get('Email')) else None

                if not member_code or not first_name or not last_name:
                    errors.append(f"Row {idx + 2}: Missing member information")
                    continue

                # Upsert member
                member = upsert_member(db, member_code, first_name, last_name, email, members_cache)

                # Extract holding data
                bond_shares = Decimal(str(row.get('Bond Shares', 0)))
                member_face_value = Decimal(str(row.get('FACE Value ', 0)))  # Note: trailing space in column name
                opening_balance = Decimal(str(row.get("Nov '23 b/f", 0))) if not pd.isna(row.get("Nov '23 b/f")) else Decimal("0")
                total_bond_share = Decimal(str(row.get('Total Bond share', 0))) if not pd.isna(row.get('Total Bond share')) else Decimal("0")
                percentage_share = Decimal(str(row.get('Percentage Share (%)', 0))) if not pd.isna(row.get('Percentage Share (%)')) else Decimal("0")
                award_value_plus_balance = Decimal(str(row.get('BOZ Award Costs Value Plus bal b/f', 0))) if not pd.isna(row.get('BOZ Award Costs Value Plus bal b/f')) else Decimal("0")
                variance = Decimal(str(row.get('Variance (Difference) C/F Jan 2024', 0))) if not pd.isna(row.get('Variance (Difference) C/F Jan 2024')) else Decimal("0")

                # Set as_of_date (adjust as needed)
                as_of_date = date(2023, 11, 30)

                # Create holding
                holding = MemberBondHolding(
                    member_id=member.user_id,
                    bond_id=bond.id,
                    as_of_date=as_of_date,
                    bond_shares=bond_shares,
                    opening_balance=opening_balance,
                    total_bond_share=total_bond_share,
                    percentage_share=percentage_share,
                    award_value_plus_balance_bf=award_value_plus_balance,
                    variance_cf_next_period=variance,
                    member_face_value=member_face_value
                )
                db.add(holding)
                holdings_created += 1

            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
                continue

        # Commit all changes
        db.commit()

        print(f"\n📈 Import Summary:")
        print(f"  ✓ Bond issue created: {bond.issue_name}")
        print(f"  ✓ Members processed: {len(members_cache)}")
        print(f"  ✓ Holdings created: {holdings_created}")
        print(f"  ⊘ Holdings skipped (0 shares): {holdings_skipped}")

        if errors:
            print(f"\n⚠️  Errors ({len(errors)}):")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")

        print("\n✅ Import completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Import failed: {e}")
        raise
    finally:
        db.close()


def main():
    """Main entry point for the import script."""
    parser = argparse.ArgumentParser(
        description="Import bond holdings from Excel file"
    )
    parser.add_argument(
        "excel_file",
        help="Path to Excel file"
    )
    parser.add_argument(
        "--sheet-name",
        default=0,
        help="Sheet name or index (default: 0)"
    )
    parser.add_argument(
        "--bond-name",
        default="BOZ Coupon Dec 2023",
        help="Bond issue name"
    )
    parser.add_argument(
        "--issuer",
        default="Bank of Zambia",
        help="Bond issuer"
    )
    parser.add_argument(
        "--issue-date",
        default="2023-12-26",
        help="Issue date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--maturity-date",
        default="2025-12-26",
        help="Maturity date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--bond-type",
        default="TWO_YEAR",
        choices=["TWO_YEAR", "FIVE_YEAR", "SEVEN_YEAR", "FIFTEEN_YEAR"],
        help="Bond type"
    )
    parser.add_argument(
        "--coupon-rate",
        type=float,
        default=0.1850,
        help="Annual coupon rate (e.g., 0.1850 for 18.50%%)"
    )
    parser.add_argument(
        "--discount-rate",
        type=float,
        default=0.2050,
        help="Maturity discount rate (e.g., 0.2050 for 20.50%%)"
    )

    args = parser.parse_args()

    # Parse dates
    issue_date = date.fromisoformat(args.issue_date)
    maturity_date = date.fromisoformat(args.maturity_date)

    # Bond parameters
    bond_params = {
        "issuer": args.issuer,
        "issue_name": args.bond_name,
        "issue_date": issue_date,
        "maturity_date": maturity_date,
        "bond_type": BondTypeEnum[args.bond_type],
        "coupon_rate": Decimal(str(args.coupon_rate)),
        "discount_rate": Decimal(str(args.discount_rate)),
        "withholding_tax_rate": Decimal("15.0"),
        "boz_fee_rate": Decimal("1.0"),
        "coop_fee_rate": Decimal("2.0")
    }

    # Run import
    import_excel(args.excel_file, args.sheet_name, bond_params)


if __name__ == "__main__":
    main()
