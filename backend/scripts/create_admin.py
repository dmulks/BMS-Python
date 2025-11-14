"""
Script to create an initial admin user.
Run this after setting up the database.
"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole


def create_admin():
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists!")
            return

        # Create admin user
        admin = User(
            username="admin",
            email="admin@bondcoop.com",
            password_hash=get_password_hash("admin123"),
            first_name="System",
            last_name="Administrator",
            phone_number="+260 123 456 789",
            address="Bond Cooperative Society Headquarters",
            user_role=UserRole.ADMIN,
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("✅ Admin user created successfully!")
        print("\nLogin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n⚠️  Please change the password after first login!")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
