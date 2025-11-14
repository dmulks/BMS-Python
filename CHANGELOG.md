# Changelog

All notable changes to the Bond Management System will be documented in this file.

## [1.1.0] - 2024-11-14

### Added
- **Additional Database Models**
  - `MemberBalance` - Monthly balance snapshots for members
  - `MonthlySummary` - Pre-calculated dashboard summaries
  - `AuditLog` - Complete audit trail for compliance
  - `Notification` - System notifications for members
  - `SystemSetting` - Configurable system settings

- **Reporting System**
  - Monthly summary generation service
  - Member balance tracking service
  - Portfolio reporting service
  - Dashboard data endpoints

- **Notification System**
  - User notification creation and management
  - Real-time notification delivery
  - Notification types: payment_due, payment_processed, maturity_approaching, rate_update, system
  - Mark as read functionality
  - Unread notification count

- **Audit Logging**
  - Comprehensive audit trail utility
  - Track CREATE, UPDATE, DELETE, LOGIN, LOGOUT actions
  - Store old and new values for changes
  - IP address and user agent tracking

- **System Settings**
  - Configurable system-wide settings
  - Category-based organization
  - Editable/non-editable setting support
  - Settings API endpoints for management

- **New API Endpoints**
  - `/api/v1/reports/generate-monthly-summary` - Generate monthly summaries
  - `/api/v1/reports/generate-member-balances` - Generate balance snapshots
  - `/api/v1/reports/monthly-summaries` - List monthly summaries
  - `/api/v1/reports/member-balances` - List member balances
  - `/api/v1/reports/portfolio/{user_id}` - Get member portfolio
  - `/api/v1/reports/dashboard` - Get role-based dashboard data
  - `/api/v1/notifications/` - List notifications
  - `/api/v1/notifications/unread` - Get unread notifications
  - `/api/v1/notifications/{id}/read` - Mark notification as read
  - `/api/v1/notifications/read-all` - Mark all as read
  - `/api/v1/settings/` - List system settings
  - `/api/v1/settings/{key}` - Get/update specific setting

- **Utility Scripts**
  - `init_settings.py` - Initialize default system settings
  - Enhanced `init_data.py` with more comprehensive seed data

### Enhanced
- Updated Alembic environment to include all new models
- Improved main application with all router integrations
- Extended README with new features documentation

## [1.0.0] - 2024-11-13

### Added
- **Core Backend Implementation**
  - FastAPI application with comprehensive API
  - SQLAlchemy database models
  - JWT authentication with role-based access control
  - Bond Calculator service with financial calculations
  - Alembic database migrations

- **Database Models**
  - User management (Admin, Treasurer, Member roles)
  - Bond types (2-year, 5-year, 15-year)
  - Interest rate management
  - Bond purchases with automatic calculations
  - Coupon payment tracking
  - Payment vouchers
  - Fee structure

- **API Endpoints**
  - Authentication (register, login, get current user)
  - Bond management (types, rates, purchases)
  - Payment processing (calculate coupons, track payments)

- **Services**
  - Bond Calculator with Excel-matching formulas
  - Automatic calculation of:
    - Face value
    - Discount value (10% default)
    - Co-op discount fee (2%)
    - Coupon payments with deductions
    - Withholding tax (15%)
    - BOZ fees (1%)
    - Co-op fees (2%)
    - Net payment amounts

- **Security Features**
  - Password hashing with bcrypt
  - JWT token authentication
  - Role-based authorization
  - Input validation with Pydantic

- **Documentation**
  - Comprehensive README
  - API documentation (Swagger/ReDoc)
  - Multiple implementation guides
  - Database schema documentation

### Technical Details
- Python 3.11+ with FastAPI
- PostgreSQL 15+ database
- SQLAlchemy 2.0 ORM
- Alembic for migrations
- Pydantic for validation
- JWT for authentication
- pytest for testing

---

**Repository**: https://github.com/dmulks/BMS-Python
**License**: Proprietary
