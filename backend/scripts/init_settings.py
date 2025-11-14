"""
Script to initialize system settings.
Run this after creating the database schema.
"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.settings import SystemSetting, SettingType


def init_settings():
    """Initialize system settings."""
    db = SessionLocal()

    settings = [
        {
            "setting_key": "cooperative_name",
            "setting_value": "Bond Portfolio Management Cooperative",
            "setting_type": SettingType.STRING,
            "category": "general",
            "description": "Name of the cooperative society",
            "is_editable": True
        },
        {
            "setting_key": "currency_code",
            "setting_value": "ZMW",
            "setting_type": SettingType.STRING,
            "category": "general",
            "description": "Currency code (ISO 4217)",
            "is_editable": True
        },
        {
            "setting_key": "default_discount_rate",
            "setting_value": "0.10",
            "setting_type": SettingType.NUMBER,
            "category": "bonds",
            "description": "Default discount rate for bond purchases (10%)",
            "is_editable": True
        },
        {
            "setting_key": "enable_email_notifications",
            "setting_value": "true",
            "setting_type": SettingType.BOOLEAN,
            "category": "notifications",
            "description": "Enable email notifications for members",
            "is_editable": True
        },
        {
            "setting_key": "maturity_warning_days",
            "setting_value": "30",
            "setting_type": SettingType.NUMBER,
            "category": "notifications",
            "description": "Days before maturity to send warning notification",
            "is_editable": True
        },
        {
            "setting_key": "require_payment_approval",
            "setting_value": "true",
            "setting_type": SettingType.BOOLEAN,
            "category": "payments",
            "description": "Require admin approval for payments",
            "is_editable": True
        },
        {
            "setting_key": "max_bond_purchase_amount",
            "setting_value": "1000000.00",
            "setting_type": SettingType.NUMBER,
            "category": "bonds",
            "description": "Maximum amount for a single bond purchase",
            "is_editable": True
        },
        {
            "setting_key": "payment_voucher_template",
            "setting_value": "default",
            "setting_type": SettingType.STRING,
            "category": "reports",
            "description": "Payment voucher template to use",
            "is_editable": True
        },
        {
            "setting_key": "cooperative_address",
            "setting_value": "Lusaka, Zambia",
            "setting_type": SettingType.STRING,
            "category": "general",
            "description": "Cooperative physical address",
            "is_editable": True
        },
        {
            "setting_key": "cooperative_phone",
            "setting_value": "+260 XXX XXX XXX",
            "setting_type": SettingType.STRING,
            "category": "general",
            "description": "Cooperative contact phone number",
            "is_editable": True
        },
        {
            "setting_key": "cooperative_email",
            "setting_value": "info@bondcoop.com",
            "setting_type": SettingType.STRING,
            "category": "general",
            "description": "Cooperative contact email",
            "is_editable": True
        },
        {
            "setting_key": "auto_generate_monthly_summaries",
            "setting_value": "true",
            "setting_type": SettingType.BOOLEAN,
            "category": "reports",
            "description": "Automatically generate monthly summaries via scheduled tasks",
            "is_editable": True
        }
    ]

    try:
        for setting_data in settings:
            existing = db.query(SystemSetting).filter(
                SystemSetting.setting_key == setting_data["setting_key"]
            ).first()

            if not existing:
                setting = SystemSetting(**setting_data)
                db.add(setting)
                print(f"✅ Created setting: {setting_data['setting_key']}")
            else:
                print(f"⏭️  Setting already exists: {setting_data['setting_key']}")

        db.commit()
        print("\n✅ System settings initialized successfully!")

    except Exception as e:
        print(f"❌ Error initializing settings: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_settings()
