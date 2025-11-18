"""
Database Migration Script - Add Bond Issues System

This script adds the new tables for the Bond Issues system:
- bond_issues
- member_bond_holdings
- payment_events
- member_payments

Run this script to update your database with the new schema.

Usage:
    python scripts/migrate_add_bond_issues.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.models import (
    BondIssue, MemberBondHolding, PaymentEvent, MemberPayment
)


def run_migration(auto_confirm=False):
    """Run the migration to add new tables."""
    print("=" * 60)
    print("Bond Management System - Database Migration")
    print("Adding Bond Issues System Tables")
    print("=" * 60)

    print("\nTables to be created:")
    print("  1. bond_issues")
    print("  2. member_bond_holdings")
    print("  3. payment_events")
    print("  4. member_payments")

    if not auto_confirm:
        response = input("\nProceed with migration? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Migration cancelled.")
            return
    else:
        print("\nAuto-confirming migration...")

    try:
        print("\nCreating tables...")

        # Create only the new tables
        BondIssue.__table__.create(engine, checkfirst=True)
        print("  ✓ Created table: bond_issues")

        MemberBondHolding.__table__.create(engine, checkfirst=True)
        print("  ✓ Created table: member_bond_holdings")

        PaymentEvent.__table__.create(engine, checkfirst=True)
        print("  ✓ Created table: payment_events")

        MemberPayment.__table__.create(engine, checkfirst=True)
        print("  ✓ Created table: member_payments")

        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Import bond holdings using: python scripts/import_bond_holdings.py <excel_file>")
        print("  2. Create payment events via the API or web interface")
        print("  3. Use preview/generate endpoints to calculate member payments")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import sys
    auto_confirm = '--auto' in sys.argv or '-y' in sys.argv
    run_migration(auto_confirm=auto_confirm)
