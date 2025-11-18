# Bond Management System - Integration Guide

## Overview

This Bond Management System now includes **two complementary systems**:

1. **Individual Purchase System** (Original)
   - Track individual member bond purchases
   - Variable monthly interest rates
   - Individual coupon calculations

2. **Bond Issues System** (New - Cooperative)
   - Track bond issues with fixed rates
   - Member holdings with percentage shares
   - BOZ award allocation
   - Preview and generate payment functionality
   - Admin audit reports

---

## What's New

### Backend Additions

#### Models
- **BondIssue**: Represents cooperative bond investments with fixed rates
- **MemberBondHolding**: Snapshot of member positions in bond issues
- **PaymentEvent**: Maturity and coupon payment events
- **MemberPayment**: Calculated payment records per member

#### Services
- **PaymentCalculatorService**: BOZ award logic, discount calculations, coupon payments

#### API Endpoints
- **Dashboard** (`/api/v1/dashboard`): KPIs and upcoming events
- **Members** (`/api/v1/members`): Member management and payment reports
- **Payment Events** (`/api/v1/bonds/{id}/events`): Event management, preview, generate
- **Admin** (`/api/v1/admin`): Audit reports, BOZ statement upload

#### Scripts
- **import_bond_holdings.py**: Import holdings from Excel
- **migrate_add_bond_issues.py**: Database migration script

### Frontend Additions

#### Pages
- **BondDetail**: View bond issue and manage payment events
- **BondPaymentPreview**: Preview calculations and generate payments
- **MemberPaymentsReport**: Member-specific payment history
- **AdminAuditReport**: Compare calculated vs expected totals
- **BozStatementUpload**: Upload BOZ CSV statements

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database
- Existing Bond Management System installation

### Backend Setup

#### 1. Install Dependencies

The required dependencies should already be installed. If needed:

```bash
cd backend
pip install pandas  # For Excel import
```

#### 2. Run Database Migration

```bash
cd backend
python scripts/migrate_add_bond_issues.py
```

This creates four new tables:
- `bond_issues`
- `member_bond_holdings`
- `payment_events`
- `member_payments`

#### 3. Verify API

Start the backend server:

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/api/docs` to see the new endpoints.

### Frontend Setup

The frontend routes are already configured. Simply:

```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` (or configured port)

---

## Usage Guide

### 1. Import Bond Holdings

Use the import script to load member holdings from Excel:

```bash
cd backend
python scripts/import_bond_holdings.py "path/to/Coupon Payment Calculations 2023.xlsx" \
  --bond-name "BOZ Coupon Dec 2023" \
  --issue-date "2023-12-26" \
  --maturity-date "2025-12-26" \
  --bond-type "TWO_YEAR" \
  --coupon-rate 0.1850 \
  --discount-rate 0.2050
```

This will:
- Create a bond issue
- Import or update member records
- Create member bond holdings

### 2. Create Payment Events

Via API or Web Interface:

**API Example:**
```bash
POST /api/v1/bonds/{bond_id}/events
{
  "event_type": "DISCOUNT_MATURITY",
  "event_name": "Maturity Payment Dec 2025",
  "payment_date": "2025-12-26",
  "calculation_period": "2023-2025",
  "boz_award_amount": 1500000.00,
  "expected_total_net_maturity": 1500000.00,
  "expected_total_net_coupon": 0
}
```

**Web Interface:**
1. Navigate to `/bonds/{bondId}`
2. Click "Create Event"
3. Fill in event details
4. Submit

### 3. Preview Payments

Before generating, preview the calculations:

1. Navigate to bond detail page
2. Click "Preview/Generate" on an event
3. Review all calculated fields
4. Export to CSV if needed

### 4. Generate Payments

Once satisfied with preview:

1. Click "Generate & Save Payments"
2. Payments are saved to database
3. Can be recalculated if needed

### 5. Upload BOZ Statement

To set expected totals:

1. Navigate to `/admin/boz-upload`
2. Upload CSV with format:
   ```csv
   event_id,expected_total_net_maturity,expected_total_net_coupon
   3,1500000.50,0
   4,0,280000.75
   ```
3. Review results

### 6. View Audit Report

Compare calculated vs expected:

1. Navigate to `/admin/audit`
2. Review event-level discrepancies
3. Check overall totals

---

## Key Features

### BOZ Award Allocation

For maturity events, BOZ award is distributed based on percentage shares:

```
Member BOZ Award = (Member Shares / Total Shares) × Total BOZ Award
```

### Discount Value Calculation

```
Discount Value = Face Value - BOZ Award Value
Co-op Discount Fee = Discount Value × 2%
Net Discount Value = Discount Value - Co-op Discount Fee
```

### Maturity Coupon

```
Gross Coupon = Face Value × Discount Rate
WHT = Gross Coupon × 15%
BOZ Fee = Gross Coupon × 1%
Net Maturity Coupon = Gross Coupon - WHT - BOZ Fee
```

### Semi-Annual Coupon

```
Semi-Annual Rate = Annual Coupon Rate / 2
Base Amount = Face Value × Semi-Annual Rate
WHT = Base Amount × 15%
BOZ Fee = Base Amount × 1%
Co-op Fee = Base Amount × 2%
Net Coupon = Base Amount - WHT - BOZ Fee - Co-op Fee
```

---

## API Endpoints Reference

### Dashboard
- `GET /api/v1/dashboard` - Get KPIs and upcoming events

### Members
- `GET /api/v1/members` - List all members
- `GET /api/v1/members/{id}` - Get member details
- `GET /api/v1/members/{id}/payments` - Member payment report
- `GET /api/v1/members/{id}/holdings` - Member bond holdings

### Bond Issues & Events
- `GET /api/v1/admin/bond-issues` - List all bond issues
- `POST /api/v1/bonds/{id}/events` - Create payment event
- `GET /api/v1/bonds/{id}/events` - List events for bond
- `PATCH /api/v1/bonds/{id}/events/{event_id}` - Update event

### Payments
- `GET /api/v1/bonds/{id}/payments/preview?event_id={id}` - Preview calculations
- `POST /api/v1/bonds/{id}/payments/generate?event_id={id}` - Generate payments
- `POST /api/v1/bonds/{id}/payments/recalculate?event_id={id}` - Recalculate payments

### Admin
- `GET /api/v1/admin/audit` - Get audit report
- `POST /api/v1/admin/boz-statement-upload` - Upload BOZ CSV

---

## Performance Optimizations

### Database Indexes

The models include indexes on:
- Foreign keys (member_id, bond_id, payment_event_id)
- Date fields (payment_date, as_of_date, issue_date, maturity_date)
- Frequently queried fields (event_type, bond_type)

### Query Optimization

- Uses SQLAlchemy `joinedload` for eager loading relationships
- Aggregations use database-level `func.sum()` and `func.count()`
- Pagination available on member and payment lists

### Recommendations

1. **Database Connection Pooling**: Configure in `database.py`
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=40
   )
   ```

2. **Response Caching**: Use Redis for dashboard KPIs
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=128)
   def get_dashboard_data():
       # Cache for 5 minutes
       ...
   ```

3. **Background Jobs**: Use Celery for heavy calculations
   - Payment generation for large member bases
   - Report generation
   - Excel exports

4. **Frontend Optimization**:
   - React.lazy() for code splitting
   - useMemo() for expensive calculations
   - Virtualized lists for large tables

---

## Troubleshooting

### Common Issues

**1. Import fails with "Member already exists"**
- Solution: The script updates existing members by username/email

**2. Preview shows zero values**
- Check that member holdings exist for the bond
- Verify event rates are set correctly
- Ensure BOZ award amount is set for maturity events

**3. Audit report shows discrepancies**
- Upload correct BOZ statement CSV
- Recalculate payments after updating event parameters

**4. Cannot generate payments**
- Check if payments already exist (use recalculate instead)
- Verify user has admin/treasurer role

---

## Data Flow

1. **Import**: Excel → BondIssue + Members + MemberBondHoldings
2. **Event Creation**: BondIssue → PaymentEvent (with rates and BOZ award)
3. **Preview**: PaymentEvent → Calculate (in-memory, no DB writes)
4. **Generate**: PaymentEvent → MemberPayments (saved to DB)
5. **Audit**: MemberPayments aggregated → compared with expected totals

---

## Excel Import Format

Required columns:
- `No`: Member code
- `First Name`: Member first name
- `Last Name`: Member last name
- `Email`: Member email
- `Bond Shares`: Number of shares
- `FACE Value `: Face value amount (note trailing space!)
- `Discount Value Paid on Maturity`: Discount value

Optional columns:
- `Nov '23 b/f`: Opening balance
- `Total Bond share`: Total bond share
- `Percentage Share (%)`: Percentage share
- `BOZ Award Costs Value Plus bal b/f`: Award value plus balance
- `Variance (Difference) C/F Jan 2024`: Variance

---

## Security Considerations

- All admin endpoints require admin or treasurer role
- Members can only view their own data
- CORS configured for frontend origins only
- Input validation on all endpoints
- SQL injection protection via SQLAlchemy ORM

---

## Support

For issues or questions:
1. Check API docs at `/api/docs`
2. Review error messages in backend logs
3. Check browser console for frontend errors
4. Verify database migration completed successfully

---

## License

This is an enhancement to the existing Bond Management System.