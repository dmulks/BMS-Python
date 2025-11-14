# Bond Management System - Backend

FastAPI-based backend for the Bond Portfolio Management System.

## Setup

### 1. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Create Database

```bash
# Using PostgreSQL
createdb bond_management_system
createuser bond_admin
psql bond_management_system
# In psql:
ALTER USER bond_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bond_management_system TO bond_admin;
```

### 5. Run Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 6. Create Admin User

Create a script to add the first admin user:

```python
# scripts/create_admin.py
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole

db = SessionLocal()

admin = User(
    username="admin",
    email="admin@bondcoop.com",
    password_hash=get_password_hash("admin123"),
    first_name="System",
    last_name="Administrator",
    user_role=UserRole.ADMIN,
    is_active=True
)

db.add(admin)
db.commit()
print("Admin user created successfully!")
```

Run it:
```bash
python scripts/create_admin.py
```

### 7. Start Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Bonds
- `POST /api/v1/bonds/types` - Create bond type (Admin)
- `GET /api/v1/bonds/types` - List bond types
- `POST /api/v1/bonds/rates` - Create interest rate (Admin/Treasurer)
- `GET /api/v1/bonds/rates` - List interest rates
- `POST /api/v1/bonds/purchases` - Create bond purchase (Admin/Treasurer)
- `GET /api/v1/bonds/purchases` - List purchases
- `GET /api/v1/bonds/purchases/{id}` - Get purchase details

### Payments
- `POST /api/v1/payments/calculate-coupons` - Calculate coupon payments (Admin/Treasurer)
- `GET /api/v1/payments/coupons` - List coupon payments
- `GET /api/v1/payments/coupons/{id}` - Get payment details
- `PATCH /api/v1/payments/coupons/{id}/status` - Update payment status
- `GET /api/v1/payments/vouchers` - List payment vouchers

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── bonds.py
│   │       └── payments.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── user.py
│   │   ├── bond.py
│   │   ├── payment.py
│   │   └── fee.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── bond.py
│   │   └── payment.py
│   ├── services/
│   │   └── bond_calculator.py
│   └── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
├── requirements.txt
└── .env
```

## Features Implemented

- ✅ JWT Authentication
- ✅ Role-based Access Control (Admin, Treasurer, Member)
- ✅ Bond Type Management
- ✅ Interest Rate Management
- ✅ Bond Purchase Recording with Automatic Calculations
- ✅ Coupon Payment Calculations
- ✅ Payment Tracking
- ✅ Portfolio Viewing

## Next Steps

1. Implement payment voucher PDF generation
2. Add reporting endpoints
3. Implement Excel import/export
4. Set up Celery for background tasks
5. Add email notifications
6. Write comprehensive tests
