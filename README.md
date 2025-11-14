# Bond Portfolio Management System

A comprehensive Bond Portfolio Management System for a Cooperative Society, built with Python FastAPI and React.

## 🎯 Project Overview

This system manages bond purchases, tracks coupon interest payments with automatic fee deductions, manages transactions, and generates comprehensive reports for a Cooperative Society with 21 members.

### Business Rules

- **Discount Structure**: Bonds purchased at discount from face value
- **Co-op Discount Fee**: 2% on discount value
- **Coupon Calculations**: Face value × daily rate × calendar days
- **Withholding Tax**: 15% on gross coupon
- **BOZ Fees**: 1% of gross coupon
- **Co-op Fees**: 2% after WHT and BOZ fees
- **Payment Types**: Semi-annual and maturity payments

## 🏗️ Technology Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL 15+** for database
- **SQLAlchemy 2.0** for ORM
- **Alembic** for migrations
- **Redis** for caching
- **Celery** for background tasks
- **JWT** for authentication

### Frontend (Coming Soon)
- **React 18+** with Vite
- **Material-UI** for components
- **Axios** for API calls
- **React Router** for routing

## 📁 Project Structure

```
BMS-Python/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Core configuration
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── scripts/             # Utility scripts
│   ├── tests/               # Test files
│   └── requirements.txt     # Python dependencies
├── frontend/                # React frontend (TBD)
└── docs/                    # Documentation guides
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (for background tasks)
- Node.js 18+ (for frontend)

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Create Database**
```bash
createdb bond_management_system
```

5. **Run Migrations**
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

6. **Initialize Data**
```bash
python scripts/create_admin.py
python scripts/init_data.py
python scripts/init_settings.py
```

7. **Start Server**
```bash
uvicorn app.main:app --reload
```

8. **Access API Documentation**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 📊 Database Schema

### Core Tables

1. **users** - Member and staff management
2. **bond_types** - Bond maturity period definitions (2-year, 5-year, 15-year)
3. **interest_rates** - Variable monthly interest rates
4. **bond_purchases** - Transaction records
5. **coupon_payments** - Interest payment tracking
6. **payment_vouchers** - Payment forms
7. **fee_structure** - Configurable fees
8. **member_balances** - Monthly balance snapshots
9. **monthly_summaries** - Pre-calculated dashboard summaries
10. **audit_logs** - Complete audit trail
11. **notifications** - System notifications
12. **system_settings** - Configurable settings

## 🔐 Authentication

The system uses JWT (JSON Web Tokens) for authentication with role-based access control:

- **Admin**: Full system access
- **Treasurer**: Manage bonds, rates, and payments
- **Member**: View own portfolio and payments

### Login
```bash
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Bond Management
- `POST /api/v1/bonds/types` - Create bond type (Admin)
- `GET /api/v1/bonds/types` - List bond types
- `POST /api/v1/bonds/rates` - Create interest rate (Admin/Treasurer)
- `GET /api/v1/bonds/rates` - List interest rates
- `POST /api/v1/bonds/purchases` - Create bond purchase (Admin/Treasurer)
- `GET /api/v1/bonds/purchases` - List purchases
- `GET /api/v1/bonds/purchases/{id}` - Get purchase details

### Payments
- `POST /api/v1/payments/calculate-coupons` - Calculate coupon payments
- `GET /api/v1/payments/coupons` - List coupon payments
- `GET /api/v1/payments/coupons/{id}` - Get payment details
- `PATCH /api/v1/payments/coupons/{id}/status` - Update payment status

### Reports
- `POST /api/v1/reports/generate-monthly-summary` - Generate monthly summary
- `POST /api/v1/reports/generate-member-balances` - Generate member balances
- `GET /api/v1/reports/monthly-summaries` - List monthly summaries
- `GET /api/v1/reports/member-balances` - List member balances
- `GET /api/v1/reports/portfolio/{user_id}` - Get member portfolio
- `GET /api/v1/reports/dashboard` - Get dashboard data

### Notifications
- `GET /api/v1/notifications/` - List notifications
- `GET /api/v1/notifications/unread` - Get unread notifications
- `GET /api/v1/notifications/unread/count` - Get unread count
- `PATCH /api/v1/notifications/{id}/read` - Mark as read
- `PATCH /api/v1/notifications/read-all` - Mark all as read

### Settings
- `GET /api/v1/settings/` - List system settings
- `GET /api/v1/settings/{key}` - Get specific setting
- `PATCH /api/v1/settings/{key}` - Update setting (Admin only)

## 🧮 Bond Calculator

The system includes a sophisticated Bond Calculator service that handles:

- Face value calculation
- Discount calculation
- Co-op discount fee (2%)
- Purchase price calculation
- Maturity date calculation
- Coupon payment calculation with:
  - Gross coupon amount
  - Withholding tax (15%)
  - BOZ fees (1%)
  - Co-op fees (2%)
  - Net payment amount

Example:
```python
from app.services.bond_calculator import BondCalculator
from decimal import Decimal
from datetime import date

# Calculate purchase breakdown
result = BondCalculator.calculate_purchase_breakdown(
    bond_shares=Decimal("10000"),
    purchase_date=date(2024, 1, 1),
    maturity_years=2,
    discount_rate=Decimal("0.10")
)

# result contains:
# - face_value: 10000.00
# - discount_value: 1000.00
# - coop_discount_fee: 20.00
# - purchase_price: 9000.00
# - maturity_date: 2026-01-01
```

## 🧪 Testing

Run tests with pytest:

```bash
cd backend
pytest tests/ -v
```

## 📚 Documentation

Additional documentation is available in the following guides:

1. **bond_management_system_complete_guide.md** - Complete system guide
2. **python_fastapi_implementation_guide.md** - Backend implementation
3. **payment_processing_voucher_guide.md** - Payment processing
4. **reporting_excel_export_guide.md** - Reporting system
5. **frontend_react_components_guide.md** - Frontend guide
6. **celery_background_tasks_guide.md** - Background tasks
7. **IMPLEMENTATION_ROADMAP.md** - 8-week implementation plan

## ✨ Features Implemented

### Core Features
- ✅ JWT Authentication
- ✅ Role-based Access Control (Admin, Treasurer, Member)
- ✅ Bond Type Management
- ✅ Interest Rate Management
- ✅ Bond Purchase Recording with Automatic Calculations
- ✅ Coupon Payment Calculations
- ✅ Payment Status Tracking
- ✅ Portfolio Viewing
- ✅ API Documentation (Swagger/ReDoc)
- ✅ Database Migrations (Alembic)
- ✅ Unit Tests

### Reporting & Analytics
- ✅ Monthly Summary Reports
- ✅ Member Balance Tracking
- ✅ Portfolio Reports
- ✅ Dashboard Data (Role-based)
- ✅ Payment Registers

### Notifications & Alerts
- ✅ System Notifications
- ✅ Payment Due Notifications
- ✅ Payment Processed Notifications
- ✅ Maturity Approaching Warnings
- ✅ Interest Rate Update Alerts

### Audit & Compliance
- ✅ Complete Audit Trail
- ✅ Action Logging (CREATE, UPDATE, DELETE)
- ✅ User Activity Tracking
- ✅ IP Address & User Agent Logging

### System Configuration
- ✅ Configurable System Settings
- ✅ Category-based Settings Organization
- ✅ Admin-controlled Settings Management

## 🎯 Roadmap

### Phase 1: Backend (In Progress)
- ✅ Core API endpoints
- ✅ Authentication system
- ✅ Bond calculator
- 🔄 Payment voucher PDF generation
- 🔄 Excel import/export
- 🔄 Background tasks with Celery

### Phase 2: Frontend (Upcoming)
- React application setup
- Authentication UI
- Dashboard components
- Bond management UI
- Payment processing UI
- Reporting interface

### Phase 3: Production (Future)
- Docker deployment
- CI/CD pipeline
- Monitoring and logging
- Email notifications
- Automated backups

## 🤝 Contributing

This is a private project for a Cooperative Society. For questions or issues, please contact the development team.

## 📄 License

Proprietary - All rights reserved by the Cooperative Society.

## 📞 Support

For support, please contact:
- Email: admin@bondcoop.com
- Phone: +260 XXX XXX XXX

---

**Version**: 1.0.0
**Last Updated**: November 2024
**Status**: Active Development
