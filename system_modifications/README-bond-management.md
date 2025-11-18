
# Bond Management System

## Project Overview

Full-stack Bond Management System for a cooperative that:

- Tracks **members** and their **bond holdings**
- Supports multiple **bond types** (2, 5, 7, 15-year maturities)
- Handles **variable coupon and discount (maturity) rates per bond issue**
- Mirrors Excel logic for:
  - Percentage share
  - BOZ award allocation
  - Discount value at maturity
  - Coupon payments with taxes and fees
- Provides:
  - **Preview** mode (read-only) for validation against Excel
  - **Generate & Save** of member payments
  - Member payment reports
  - Admin audit report vs BOZ totals
  - Dashboard with KPIs
  - Upload of **BOZ statement CSV** to set expected totals

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy 2.0 ORM
- PostgreSQL
- Pandas (for Excel import)
- Alembic (recommended for migrations)
- Uvicorn (for dev server)

### Frontend

- React
- React Router
- Axios
- (Optional) TailwindCSS or Material UI for styling

---

## High-Level Folder Structure

```text
backend/
  app.py
  db.py
  models.py
  routers/
    dashboard.py
    members.py
    payment_events.py
    admin.py
  schemas/
    dashboard.py
    payment_events.py
    payment_preview.py
    member_payments.py
    admin_audit.py
    admin_boz.py
  services/
    payments.py
  scripts/
    import_excel.py

frontend/
  src/
    api/
      client.js
    pages/
      Dashboard.jsx
      BondList.jsx
      BondDetail.jsx
      BondPaymentPreview.jsx
      MemberList.jsx
      MemberDetail.jsx
      MemberPaymentsReport.jsx
      AdminAuditReport.jsx
      BozStatementUpload.jsx
    layout/
      AppLayout.jsx
    main.jsx (or index.jsx)
```

---

## Core Domain Concepts (Summary)

- **Bond Types**: 2, 5, 7, 15 years  
  Enum: `TWO_YEAR`, `FIVE_YEAR`, `SEVEN_YEAR`, `FIFTEEN_YEAR`.

- **Bond Issues**: each batch with its own rates and dates.
- **Members**: cooperative members.
- **Holdings**: member shares + face value snapshots.
- **Payment Events**: maturity / coupon events per bond.
- **Member Payments**: calculated rows per member per event, based on Excel logic.
