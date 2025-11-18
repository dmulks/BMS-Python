
# Excel Import Guide

## Goal

From `Coupon Payment Calculations 2023.xlsx` you will:

- Create a `BondIssue`
- Create `Member` records
- Create `MemberBondHolding` snapshots

Then you can define payment events, preview, and generate member payments.

---

## Prerequisites

- File: `Coupon Payment Calculations 2023.xlsx`
- Python packages:
  - `pandas`
  - `sqlalchemy`
  - `psycopg2-binary` (or psycopg 3)
- Working `db.py` and `models.py`

---

## Script Outline (`scripts/import_excel.py`)

### 1. Read Excel

```python
import pandas as pd

EXCEL_FILE = "Coupon Payment Calculations 2023.xlsx"
df = pd.read_excel(EXCEL_FILE, sheet_name=0)
```

### 2. Insert a `BondIssue`

```python
from datetime import date
from models import BondIssue, BondType

bond = BondIssue(
    issuer="Bank of Zambia",
    issue_name="BOZ Coupon Dec 2023",
    issue_date=date(2023, 12, 26),
    maturity_date=date(2025, 12, 26),
    bond_type=BondType.TWO_YEAR,
    coupon_rate=0.1850,
    discount_rate=0.2050,
    withholding_tax_rate=15.0,
    boz_fee_rate=1.0,
    coop_fee_rate=2.0,
)
session.add(bond)
session.commit()
session.refresh(bond)
```

### 3. Upsert Members

```python
from models import Member

members_cache = {}

for _, row in df.iterrows():
    member_code = str(row["No"])
    first_name = row["First Name"]
    last_name = row["Last Name"]
    email = row.get("Email")

    member = members_cache.get(member_code)
    if member is None:
        member = (
            session.query(Member)
            .filter(Member.member_code == member_code)
            .one_or_none()
        )
        if member is None:
            member = Member(
                member_code=member_code,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            session.add(member)
            session.flush()
        members_cache[member_code] = member
```

### 4. Insert Holdings

```python
from models import MemberBondHolding
from datetime import date

for _, row in df.iterrows():
    member_code = str(row["No"])
    member = members_cache[member_code]

    holding = MemberBondHolding(
        member_id=member.id,
        bond_id=bond.id,
        as_of_date=date(2023, 11, 30),  # adjust per sheet
        bond_shares=row.get("Bond Shares") or 0,
        opening_balance=row.get("Nov '23 b/f") or 0,
        total_bond_share=row.get("Total Bond share") or 0,
        percentage_share=row.get("Percentage Share (%)") or 0,
        award_value_plus_balance_bf=row.get(
            "BOZ Award Costs Value Plus bal b/f"
        ) or 0,
        variance_cf_next_period=row.get(
            "Variance (Difference) C/F Jan 2024"
        ) or 0,
        member_face_value=row.get("FACE Value") or 0,
    )
    session.add(holding)

session.commit()
```

### 5. After Import

- Create payment events (maturity and coupons).
- Set `boz_award_amount` and rates.
- Use preview endpoint to check against Excel.
- When satisfied, generate & save.
