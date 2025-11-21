#!/usr/bin/env python3
"""
Migration script to add member_documents table.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.core.database import Base
from app.models import MemberDocument, User
from app.core.config import settings

def migrate():
    """Run the migration."""
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)

    # Check if table exists
    if "member_documents" in inspector.get_table_names():
        print("✓ Table 'member_documents' already exists")
        return

    print("Creating member_documents table...")

    # Create table
    MemberDocument.__table__.create(engine)

    print("✅ Migration completed successfully!")
    print("  ✓ Created table: member_documents")

    # Create uploads directory
    upload_dir = os.path.join("uploads", "member_documents")
    os.makedirs(upload_dir, exist_ok=True)
    print(f"  ✓ Created uploads directory: {upload_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.parser(description="Add member_documents table")
    parser.add_argument("--auto", action="store_true", help="Run automatically without confirmation")
    args = parser.parse_args()

    if not args.auto:
        response = input("Run migration to add member_documents table? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Migration cancelled")
            sys.exit(0)

    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)
