from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import csv
import io
from decimal import Decimal

from app.core.database import get_db
from app.core.security import require_role
from app.models import User, PaymentEvent
from app.services.payment_calculator import PaymentCalculatorService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/audit", response_model=dict)
def get_audit_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Get audit report comparing calculated totals vs expected BOZ totals.
    Shows event-level aggregations and highlights discrepancies (Admin/Treasurer only).
    """
    report = PaymentCalculatorService.get_audit_report(db)

    # Calculate overall totals
    total_calculated_maturity = sum(Decimal(str(r["calculated_net_maturity"])) for r in report)
    total_expected_maturity = sum(Decimal(str(r["expected_net_maturity"])) for r in report)
    total_calculated_coupon = sum(Decimal(str(r["calculated_net_coupon"])) for r in report)
    total_expected_coupon = sum(Decimal(str(r["expected_net_coupon"])) for r in report)

    maturity_difference = total_calculated_maturity - total_expected_maturity
    coupon_difference = total_calculated_coupon - total_expected_coupon

    # Count discrepancies
    discrepancy_count = sum(1 for r in report if r["has_discrepancy"])

    return {
        "report": report,
        "summary": {
            "total_events": len(report),
            "events_with_discrepancies": discrepancy_count,
            "total_calculated_net_maturity": float(total_calculated_maturity),
            "total_expected_net_maturity": float(total_expected_maturity),
            "total_maturity_difference": float(maturity_difference),
            "total_calculated_net_coupon": float(total_calculated_coupon),
            "total_expected_net_coupon": float(total_expected_coupon),
            "total_coupon_difference": float(coupon_difference),
            "has_overall_discrepancy": abs(maturity_difference) > Decimal("0.01") or abs(coupon_difference) > Decimal("0.01")
        }
    }


@router.post("/boz-statement-upload", status_code=status.HTTP_200_OK)
async def upload_boz_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Upload BOZ statement CSV to set expected totals for payment events.

    CSV format:
    event_id,expected_total_net_maturity,expected_total_net_coupon
    3,1500000.50,0
    4,0,280000.75

    (Admin/Treasurer only)
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )

    # Read CSV file
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read CSV file: {str(e)}"
        )

    # Validate headers
    expected_headers = {'event_id', 'expected_total_net_maturity', 'expected_total_net_coupon'}
    if not expected_headers.issubset(set(csv_reader.fieldnames or [])):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV must contain headers: {', '.join(expected_headers)}"
        )

    # Process rows
    updates = {
        "successful": 0,
        "failed": 0,
        "errors": []
    }

    for row_num, row in enumerate(csv_reader, start=2):
        try:
            event_id = int(row['event_id'])
            expected_maturity = Decimal(row['expected_total_net_maturity'])
            expected_coupon = Decimal(row['expected_total_net_coupon'])

            # Find event
            event = db.query(PaymentEvent).filter(PaymentEvent.id == event_id).first()

            if not event:
                updates["errors"].append(f"Row {row_num}: Event {event_id} not found")
                updates["failed"] += 1
                continue

            # Update expected totals
            event.expected_total_net_maturity = expected_maturity
            event.expected_total_net_coupon = expected_coupon

            updates["successful"] += 1

        except ValueError as e:
            updates["errors"].append(f"Row {row_num}: Invalid number format - {str(e)}")
            updates["failed"] += 1
        except KeyError as e:
            updates["errors"].append(f"Row {row_num}: Missing column - {str(e)}")
            updates["failed"] += 1
        except Exception as e:
            updates["errors"].append(f"Row {row_num}: {str(e)}")
            updates["failed"] += 1

    # Commit changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save updates: {str(e)}"
        )

    return {
        "message": "BOZ statement processed",
        "successful_updates": updates["successful"],
        "failed_updates": updates["failed"],
        "errors": updates["errors"]
    }


@router.get("/bond-issues", response_model=List[dict])
def get_all_bond_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Get all bond issues with summary statistics (Admin/Treasurer only).
    """
    from app.models import BondIssue, MemberBondHolding, PaymentEvent
    from sqlalchemy import func

    bonds = db.query(BondIssue).all()

    result = []
    for bond in bonds:
        # Count holdings
        holdings_count = db.query(func.count(MemberBondHolding.id)).filter(
            MemberBondHolding.bond_id == bond.id
        ).scalar() or 0

        # Sum face values
        total_face_value = db.query(func.sum(MemberBondHolding.member_face_value)).filter(
            MemberBondHolding.bond_id == bond.id
        ).scalar() or 0

        # Count events
        events_count = db.query(func.count(PaymentEvent.id)).filter(
            PaymentEvent.bond_id == bond.id
        ).scalar() or 0

        result.append({
            "id": bond.id,
            "issuer": bond.issuer,
            "issue_name": bond.issue_name,
            "issue_date": bond.issue_date.isoformat(),
            "maturity_date": bond.maturity_date.isoformat(),
            "bond_type": bond.bond_type.value,
            "coupon_rate": float(bond.coupon_rate),
            "discount_rate": float(bond.discount_rate),
            "withholding_tax_rate": float(bond.withholding_tax_rate),
            "boz_fee_rate": float(bond.boz_fee_rate),
            "coop_fee_rate": float(bond.coop_fee_rate),
            "holdings_count": holdings_count,
            "total_face_value": float(total_face_value),
            "events_count": events_count,
            "created_at": bond.created_at.isoformat()
        })

    return result
