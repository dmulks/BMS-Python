
# Backend Architecture

## Data Model (Tables)

### 1. `members`

Stores cooperative members.

- `id` (PK)
- `member_code` (from Excel "No")
- `first_name`
- `last_name`
- `email`
- `created_at`

### 2. `bond_issues`

Represents a specific bond purchase/issue.

- `id` (PK)
- `issuer`
- `issue_name`
- `issue_date`
- `maturity_date`
- `bond_type` (enum: `TWO_YEAR`, `FIVE_YEAR`, `SEVEN_YEAR`, `FIFTEEN_YEAR`)
- `coupon_rate` (annual)
- `discount_rate` (maturity rate)
- `face_value_per_unit` (optional)
- `withholding_tax_rate`
- `boz_fee_rate`
- `coop_fee_rate`
- `created_at`

### 3. `member_bond_holdings`

Snapshot of each member’s bond position.

- `id` (PK)
- `member_id` (FK → `members`)
- `bond_id` (FK → `bond_issues`)
- `as_of_date`
- `bond_shares`
- `opening_balance`
- `total_bond_share`
- `percentage_share`
- `award_value_plus_balance_bf`
- `variance_cf_next_period`
- `member_face_value`
- `created_at`

Recommended unique constraint:

```sql
UNIQUE (member_id, bond_id, as_of_date)
```

### 4. `payment_events`

Defines a coupon or maturity event for a bond.

- `id` (PK)
- `bond_id` (FK → `bond_issues`)
- `event_type` (`DISCOUNT_MATURITY`, `COUPON_SEMI_ANNUAL`)
- `event_name`
- `payment_date`
- `calculation_period`
- `base_rate`
- `withholding_tax_rate`
- `boz_fee_rate`
- `coop_fee_rate`
- `boz_award_amount`
- `expected_total_net_maturity`
- `expected_total_net_coupon`
- `created_at`

### 5. `member_payments`

Stores calculated payment records per member and event.

- `id` (PK)
- `member_id` (FK → `members`)
- `bond_id` (FK → `bond_issues`)
- `payment_event_id` (FK → `payment_events`)
- `boz_award_value`
- `base_amount`
- `coop_discount_fee`
- `net_discount_value`
- `gross_coupon_from_boz`
- `withholding_tax`
- `boz_fee`
- `coop_fee_on_coupon`
- `net_maturity_coupon`
- `net_coupon_payment`
- `calculation_period`
- `created_at`

---

## Core Services (`services/payments.py`)

### `calculate_payments_for_event(db, event_id) -> list[PaymentCalcResult]`

- Reads `PaymentEvent`, `BondIssue`, `MemberBondHolding`, `Member`.
- Calculates all payment fields in-memory.
- Used by preview endpoint.

### `generate_payments_for_event(db, event_id) -> int`

- Calls `calculate_payments_for_event`.
- Writes `MemberPayment` rows.
- Returns number of rows created.

---

## Routers

### `dashboard.py`

- `GET /dashboard` → global KPIs + upcoming events.

### `members.py`

- CRUD for members.
- `GET /members/{member_id}/payments` → member payment report.

### `payment_events.py` (prefix `/bonds`)

- `POST /{bond_id}/events` → create event.
- `GET /{bond_id}/events` → list events.
- `GET /{bond_id}/payments/preview?event_id=...` → preview calculations.
- `POST /{bond_id}/payments/generate` → generate & save.
- `POST /{bond_id}/payments/recalculate` → delete & regenerate.

### `admin.py`

- `GET /admin/audit` → event-level totals vs expected.
- `POST /admin/boz-statement-upload` → upload BOZ CSV and update expected totals.
