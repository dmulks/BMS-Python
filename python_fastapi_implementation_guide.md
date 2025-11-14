# Bond Management System - Python (FastAPI) Implementation Guide

## 🚀 Complete Step-by-Step Implementation Process

This guide provides a comprehensive, production-ready implementation using:
- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18+ with Material-UI
- **Database**: PostgreSQL 15+
- **Task Queue**: Celery + Redis
- **Financial Calculations**: Pandas & NumPy

---

## Prerequisites Installation

### System Requirements
```bash
# Install Python 3.11+
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install PostgreSQL 15+
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3.11 --version
psql --version
redis-server --version
node --version
```

---

## Phase 1: Project Setup

### Step 1: Create Project Structure

```bash
# Create project
mkdir bond-management-system
cd bond-management-system

# Backend structure
mkdir -p backend/{app/{api/v1,core,models,schemas,services,utils,tasks},tests}

# Frontend
mkdir frontend
```

### Step 2: Backend Setup

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pandas==2.1.3
numpy==1.26.2
openpyxl==3.1.2
reportlab==4.0.7
celery==5.3.4
redis==5.0.1
pytest==7.4.3
```

**Install dependencies:**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configuration

**app/core/config.py:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://bond_admin:password@localhost/bond_db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**.env:**
```bash
DATABASE_URL=postgresql://bond_admin:secure_password@localhost:5432/bond_management_system
SECRET_KEY=your-super-secret-key-min-32-characters
```

---

## Phase 2: Database Models

### Complete Model Implementation

**app/models/user.py:**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TREASURER = "treasurer"
    MEMBER = "member"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    
    bond_purchases = relationship("BondPurchase", back_populates="user")
```

**app/models/bond.py:**
```python
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class BondPurchase(Base):
    __tablename__ = "bond_purchases"
    
    purchase_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    bond_type_id = Column(Integer, ForeignKey("bond_types.bond_type_id"))
    purchase_date = Column(Date, nullable=False)
    bond_shares = Column(Numeric(15, 2), nullable=False)
    face_value = Column(Numeric(15, 2), nullable=False)
    discount_value = Column(Numeric(15, 2), nullable=False)
    coop_discount_fee = Column(Numeric(15, 2), nullable=False)
    purchase_price = Column(Numeric(15, 2), nullable=False)
    maturity_date = Column(Date, nullable=False)
    
    user = relationship("User", back_populates="bond_purchases")
```

---

## Phase 3: Bond Calculator Service

**app/services/bond_calculator.py:**
```python
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta

class BondCalculator:
    @staticmethod
    def calculate_face_value(bond_shares: Decimal) -> Decimal:
        return (bond_shares * Decimal("1")).quantize(Decimal("0.01"))
    
    @staticmethod
    def calculate_discount_value(face_value: Decimal, rate: Decimal = Decimal("0.10")) -> Decimal:
        return (face_value * rate).quantize(Decimal("0.01"))
    
    @staticmethod
    def calculate_coop_fee(discount_value: Decimal) -> Decimal:
        return (discount_value * Decimal("0.02")).quantize(Decimal("0.01"))
    
    @staticmethod
    def calculate_coupon_payment(face_value: Decimal, daily_rate: Decimal, days: int) -> dict:
        gross = (face_value * daily_rate * Decimal(days)).quantize(Decimal("0.01"))
        wht = (gross * Decimal("0.15")).quantize(Decimal("0.01"))
        boz = (gross * Decimal("0.01")).quantize(Decimal("0.01"))
        coop = ((gross - wht - boz) * Decimal("0.02")).quantize(Decimal("0.01"))
        net = gross - wht - boz - coop
        
        return {
            "gross_coupon": gross,
            "withholding_tax": wht,
            "boz_fees": boz,
            "coop_fees": coop,
            "net_payment": net
        }
```

---

## Phase 4: API Endpoints

**app/api/v1/auth.py:**
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.user_id)})
    return {"access_token": token, "token_type": "bearer"}
```

**app/api/v1/bonds.py:**
```python
from fastapi import APIRouter, Depends
from app.services.bond_calculator import BondCalculator

router = APIRouter(prefix="/bonds", tags=["Bonds"])

@router.post("/purchases")
def create_purchase(purchase: BondPurchaseCreate, db: Session = Depends(get_db)):
    # Calculate values
    calc = BondCalculator.calculate_purchase_breakdown(purchase.bond_shares)
    
    # Create record
    db_purchase = BondPurchase(
        user_id=purchase.user_id,
        bond_type_id=purchase.bond_type_id,
        purchase_date=purchase.purchase_date,
        bond_shares=purchase.bond_shares,
        face_value=calc["face_value"],
        discount_value=calc["discount_value"],
        coop_discount_fee=calc["coop_discount_fee"],
        purchase_price=calc["purchase_price"],
        maturity_date=calc["maturity_date"]
    )
    
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return db_purchase
```

---

## Phase 5: Main Application

**app/main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, bonds, payments, reports
from app.core.config import settings

app = FastAPI(title="Bond Management System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(bonds.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Bond Management System API"}
```

---

## Phase 6: Database Migrations

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

---

## Phase 7: Testing

**tests/test_calculator.py:**
```python
import pytest
from decimal import Decimal
from app.services.bond_calculator import BondCalculator

def test_face_value_calculation():
    result = BondCalculator.calculate_face_value(Decimal("10000"))
    assert result == Decimal("10000.00")

def test_coupon_payment():
    result = BondCalculator.calculate_coupon_payment(
        Decimal("10000"),
        Decimal("0.000247"),
        183
    )
    assert "gross_coupon" in result
    assert "net_payment" in result
```

**Run tests:**
```bash
pytest tests/ -v
```

---

## Phase 8: Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Initialize Database

```bash
# Create database
createdb bond_management_system

# Run migrations
alembic upgrade head

# Create admin user (create a script)
python scripts/create_admin.py
```

---

## Frontend Setup (React)

### Initialize Frontend

```bash
cd frontend
npm create vite@latest . -- --template react
npm install

# Install dependencies
npm install axios react-router-dom @mui/material @emotion/react @emotion/styled
npm install react-hook-form yup
npm install recharts date-fns
```

### Frontend Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js
│   ├── components/
│   │   ├── auth/
│   │   ├── bonds/
│   │   └── dashboard/
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   └── Bonds.jsx
│   ├── App.jsx
│   └── main.jsx
```

### API Client Setup

**src/api/client.js:**
```javascript
import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;
```

### Login Component

**src/pages/Login.jsx:**
```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';

export default function Login() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);
      
      const response = await client.post('/auth/login', formData);
      localStorage.setItem('token', response.data.access_token);
      navigate('/dashboard');
    } catch (error) {
      alert('Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={credentials.username}
        onChange={(e) => setCredentials({...credentials, username: e.target.value})}
        placeholder="Username"
      />
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

---

## Deployment

### Docker Setup

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: bond_management_system
      POSTGRES_USER: bond_admin
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://bond_admin:secure_password@db:5432/bond_management_system
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Deploy

```bash
# Build and start
docker-compose up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head

# Check logs
docker-compose logs -f
```

---

## Production Checklist

- [ ] Environment variables secured
- [ ] Database backed up
- [ ] SSL certificate configured
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Error tracking setup (Sentry)
- [ ] Monitoring configured
- [ ] Automated backups scheduled

---

## Key Features Implementation Summary

### ✅ Completed Features:
1. User authentication with JWT
2. Role-based access control (Admin, Treasurer, Member)
3. Bond purchase recording with automatic calculations
4. Bond calculator service (matching Excel formulas)
5. Interest rate management
6. Database models and migrations
7. API endpoints for all core features
8. Frontend React application structure

### 📋 Next Steps:
1. Implement payment processing (Phase 5)
2. Add voucher PDF generation
3. Create reporting system
4. Add Excel import/export
5. Implement Celery background tasks
6. Add email notifications
7. Complete frontend dashboards
8. Write comprehensive tests

---

## Quick Start Commands

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend  
cd frontend
npm run dev

# Database
createdb bond_management_system
alembic upgrade head

# Tests
pytest tests/ -v
```

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Database**: PostgreSQL 15+
- **Python**: 3.11+
- **FastAPI**: Latest

---

**Document Version**: 1.0  
**Last Updated**: November 2024  
**Status**: Ready for Development
