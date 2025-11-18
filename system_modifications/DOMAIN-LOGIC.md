
# Domain & Calculation Logic

## Bond Types & Issues

Bond types:

- 2-year
- 5-year
- 7-year
- 15-year

Enum values:

- `TWO_YEAR`
- `FIVE_YEAR`
- `SEVEN_YEAR`
- `FIFTEEN_YEAR`

Each `BondIssue` includes:

- `bond_type`
- `coupon_rate`
- `discount_rate`
- `withholding_tax_rate`
- `boz_fee_rate`
- `coop_fee_rate`
- `issue_date`
- `maturity_date`

---

## Holdings & Shares

Per member + bond:

- `bond_shares`
- `member_face_value`

Total shares for a bond at a given date:

```sql
SELECT SUM(bond_shares)
FROM member_bond_holdings
WHERE bond_id = :bond_id
  AND as_of_date <= :payment_date;
```

Member percentage share:

```text
percentage_share = member_bond_shares / total_members_bond_shares
```

---

## BOZ Award Allocation (Maturity)

Event-level:

- `payment_events.boz_award_amount`

Per member:

```text
boz_award_value = percentage_share * boz_award_amount
```

Saved in `member_payments.boz_award_value`.

---

## Discount Value at Maturity

```text
Discount Value = Face Value - BOZ Award Value
```

Saved as:

- `base_amount` (Discount Value)
- `coop_discount_fee = Discount Value * coop_fee_rate`
- `net_discount_value = Discount Value - coop_discount_fee`

---

## Maturity Coupon

Rate:

- `discount_rate` or `payment_event.base_rate`

Per member:

```text
gross_coupon_from_boz = member_face_value * effective_rate
withholding_tax        = gross_coupon_from_boz * WHT_rate
boz_fee                = gross_coupon_from_boz * BOZ_fee_rate
net_maturity_coupon    = gross_coupon_from_boz - withholding_tax - boz_fee
```

---

## Semi-Annual Coupon

Event type: `COUPON_SEMI_ANNUAL`

```text
coupon_rate_period    = coupon_rate / 2
base_amount           = member_face_value * coupon_rate_period
gross_coupon_from_boz = base_amount
withholding_tax       = base_amount * WHT_rate
boz_fee               = base_amount * BOZ_fee_rate
coop_fee_on_coupon    = base_amount * coop_fee_rate
net_coupon_payment    = base_amount - withholding_tax - boz_fee - coop_fee_on_coupon
```

---

## Preview vs Generate

- **Preview**:
  - Uses `calculate_payments_for_event`.
  - No DB writes.
  - Used by `GET /bonds/{bond_id}/payments/preview`.

- **Generate**:
  - Uses same logic.
  - Writes `MemberPayment` rows.
  - `POST /bonds/{bond_id}/payments/generate`.
  - `POST /bonds/{bond_id}/payments/recalculate` deletes then regenerates.

---

## Audit Logic

`GET /admin/audit` aggregates:

```text
total_net_maturity_coupon = SUM(member_payments.net_maturity_coupon)
total_net_coupon_payment  = SUM(member_payments.net_coupon_payment)
```

Compares these to:

- `expected_total_net_maturity`
- `expected_total_net_coupon`

Differences are shown in the frontend.

---

## BOZ Statement Upload

CSV format:

```csv
event_id,expected_total_net_maturity,expected_total_net_coupon
3,1500000.50,0
4,0,280000.75
```

Uploaded to `POST /admin/boz-statement-upload`, which updates `PaymentEvent` expected totals.
