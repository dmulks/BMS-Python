"""
Script to import bond purchases and users from Excel file.
"""
import sys
sys.path.append('.')

import pandas as pd
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.bond import BondPurchase, BondType, PurchaseStatus
from decimal import Decimal


def import_excel_data(file_path: str, purchase_date: date = None, bond_type_name: str = "2-Year Bond"):
    """
    Import bond purchases from Excel file.

    Args:
        file_path: Path to the Excel file
        purchase_date: Date of bond purchase (default: today)
        bond_type_name: Name of the bond type (default: "2-Year Bond")
    """
    db = SessionLocal()

    try:
        # Read Excel file
        print(f"📊 Reading Excel file: {file_path}")
        df = pd.read_excel(file_path, sheet_name=0, header=1)

        # Get or create bond type
        bond_type = db.query(BondType).filter(BondType.bond_name == bond_type_name).first()
        if not bond_type:
            print(f"❌ Bond type '{bond_type_name}' not found in database")
            print("Available bond types:")
            for bt in db.query(BondType).all():
                print(f"  - {bt.bond_name}")
            return

        print(f"✅ Using bond type: {bond_type.bond_name}")

        # Set default purchase date
        if purchase_date is None:
            purchase_date = date.today()

        # Track statistics
        users_created = 0
        users_updated = 0
        bonds_created = 0
        errors = []

        # Process each row
        for index, row in df.iterrows():
            try:
                # Skip rows with missing essential data
                if pd.isna(row['First Name']) or pd.isna(row['Email']):
                    continue

                # Extract user data
                first_name = str(row['First Name']).strip()
                last_name = str(row['Last Name']).strip() if pd.notna(row['Last Name']) else ""
                email = str(row['Email']).strip().lower()

                # Skip invalid emails
                if not email or '@' not in email:
                    errors.append(f"Row {index + 2}: Invalid email '{email}'")
                    continue

                # Check if user exists
                user = db.query(User).filter(User.email == email).first()

                if not user:
                    # Create new user
                    username = email.split('@')[0]
                    # Ensure unique username
                    base_username = username
                    counter = 1
                    while db.query(User).filter(User.username == username).first():
                        username = f"{base_username}{counter}"
                        counter += 1

                    user = User(
                        username=username,
                        email=email,
                        password_hash=get_password_hash("change123"),  # Default password
                        first_name=first_name,
                        last_name=last_name,
                        user_role=UserRole.MEMBER,
                        is_active=True
                    )
                    db.add(user)
                    db.flush()  # Get user_id
                    users_created += 1
                    print(f"  ✅ Created user: {email} (username: {username})")
                else:
                    # Update user name if different
                    if user.first_name != first_name or user.last_name != last_name:
                        user.first_name = first_name
                        user.last_name = last_name
                        users_updated += 1
                        print(f"  📝 Updated user: {email}")

                # Extract bond data
                bond_shares = float(row['Bond Shares']) if pd.notna(row['Bond Shares']) else 0

                # Skip if no bond shares
                if bond_shares <= 0:
                    continue

                # Parse face value (column has trailing space)
                face_value = float(row['FACE Value ']) if pd.notna(row.get('FACE Value ')) else bond_shares

                # Parse discount value
                discount_value = float(row['Discount Value Paid on Maturity']) if pd.notna(row.get('Discount Value Paid on Maturity')) else 0

                # Parse coop discount fee (2% of discount)
                coop_fee = float(row['Less 2%\n Co-op  Discount Fee']) if pd.notna(row['Less 2%\n Co-op  Discount Fee']) else (discount_value * 0.02)

                # Calculate net discount value
                net_discount = discount_value - coop_fee

                # Calculate price paid (face value - discount)
                price_paid = face_value - discount_value if discount_value > 0 else face_value

                # Calculate purchase month (first day of month)
                purchase_month = purchase_date.replace(day=1)

                # Calculate maturity date
                maturity_date = purchase_date.replace(year=purchase_date.year + bond_type.maturity_period_years)

                # Check if bond purchase already exists for this user and date
                existing_bond = db.query(BondPurchase).filter(
                    BondPurchase.user_id == user.user_id,
                    BondPurchase.bond_type_id == bond_type.bond_type_id,
                    BondPurchase.purchase_date == purchase_date,
                    BondPurchase.face_value == Decimal(str(face_value))
                ).first()

                if existing_bond:
                    print(f"  ⏭️  Skipped duplicate bond for {email}: {face_value}")
                    continue

                # Create bond purchase
                bond_purchase = BondPurchase(
                    user_id=user.user_id,
                    bond_type_id=bond_type.bond_type_id,
                    purchase_date=purchase_date,
                    purchase_month=purchase_month,
                    bond_shares=Decimal(str(bond_shares)),
                    face_value=Decimal(str(face_value)),
                    discount_value=Decimal(str(discount_value)),
                    coop_discount_fee=Decimal(str(coop_fee)),
                    net_discount_value=Decimal(str(net_discount)),
                    purchase_price=Decimal(str(price_paid)),
                    maturity_date=maturity_date,
                    purchase_status=PurchaseStatus.ACTIVE
                )
                db.add(bond_purchase)
                bonds_created += 1
                print(f"  💰 Created bond for {email}: Face Value={face_value}, Price Paid={price_paid}")

            except Exception as e:
                error_msg = f"Row {index + 2}: {str(e)}"
                errors.append(error_msg)
                print(f"  ❌ {error_msg}")
                continue

        # Commit all changes
        db.commit()

        # Print summary
        print("\n" + "="*60)
        print("📈 IMPORT SUMMARY")
        print("="*60)
        print(f"✅ Users created: {users_created}")
        print(f"📝 Users updated: {users_updated}")
        print(f"💰 Bond purchases created: {bonds_created}")

        if errors:
            print(f"\n⚠️  Errors encountered: {len(errors)}")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")

        print("="*60)

        if users_created > 0:
            print(f"\n🔑 Default password for new users: change123")
            print("   Users should change their password after first login.")

    except Exception as e:
        print(f"❌ Error during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Import bond purchases from Excel file')
    parser.add_argument('file_path', help='Path to Excel file')
    parser.add_argument('--date', help='Purchase date (YYYY-MM-DD)', default=None)
    parser.add_argument('--bond-type', help='Bond type name', default='2-Year Bond')

    args = parser.parse_args()

    # Parse date if provided
    purchase_date = None
    if args.date:
        try:
            purchase_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD")
            sys.exit(1)

    import_excel_data(args.file_path, purchase_date, args.bond_type)
