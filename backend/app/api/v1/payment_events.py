from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models import User, BondIssue, PaymentEvent, EventType, MemberPayment
from app.services.payment_calculator import PaymentCalculatorService

router = APIRouter(prefix="/bonds", tags=["Payment Events"])


class PaymentEventCreate(BaseModel):
    event_type: str  # "DISCOUNT_MATURITY" or "COUPON_SEMI_ANNUAL"
    event_name: str
    payment_date: date
    calculation_period: Optional[str] = None
    base_rate: Optional[Decimal] = None
    withholding_tax_rate: Optional[Decimal] = None
    boz_fee_rate: Optional[Decimal] = None
    coop_fee_rate: Optional[Decimal] = None
    boz_award_amount: Optional[Decimal] = Decimal("0")
    expected_total_net_maturity: Optional[Decimal] = Decimal("0")
    expected_total_net_coupon: Optional[Decimal] = Decimal("0")


class PaymentEventUpdate(BaseModel):
    event_name: Optional[str] = None
    payment_date: Optional[date] = None
    calculation_period: Optional[str] = None
    base_rate: Optional[Decimal] = None
    withholding_tax_rate: Optional[Decimal] = None
    boz_fee_rate: Optional[Decimal] = None
    coop_fee_rate: Optional[Decimal] = None
    boz_award_amount: Optional[Decimal] = None
    expected_total_net_maturity: Optional[Decimal] = None
    expected_total_net_coupon: Optional[Decimal] = None


@router.post("/{bond_id}/events", status_code=status.HTTP_201_CREATED)
def create_payment_event(
    bond_id: int,
    event_data: PaymentEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "treasurer"))
):
    """
    Create a new payment event for a bond issue (Admin/Treasurer only).
    """
    # Verify bond exists
    bond = db.query(BondIssue).filter(BondIssue.id == bond_id).first()
    if not bond:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bond issue not found"
        )

    # Validate event type
    try:
        event_type = EventType(event_data.event_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event type. Must be one of: {[e.value for e in EventType]}"
        )

    # Create event
    event = PaymentEvent(
        bond_id=bond_id,
        event_type=event_type,
        event_name=event_data.event_name,
        payment_date=event_data.payment_date,
        calculation_period=event_data.calculation_period,
        base_rate=event_data.base_rate,
        withholding_tax_rate=event_data.withholding_tax_rate,
        boz_fee_rate=event_data.boz_fee_rate,
        coop_fee_rate=event_data.coop_fee_rate,
        boz_award_amount=event_data.boz_award_amount or Decimal("0"),
        expected_total_net_maturity=event_data.expected_total_net_maturity or Decimal("0"),
        expected_total_net_coupon=event_data.expected_total_net_coupon or Decimal("0")
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "message": "Payment event created successfully",
        "event_id": event.id,
        "event_name": event.event_name,
        "event_type": event.event_type.value,
        "payment_date": event.payment_date.isoformat()
    }


@router.get("/{bond_id}/events", response_model=List[dict])
def get_payment_events(
    bond_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all payment events for a bond issue.
    """
    # Verify bond exists
    bond = db.query(BondIssue).filter(BondIssue.id == bond_id).first()
    if not bond:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bond issue not found"
        )

    events = db.query(PaymentEvent).filter(
        PaymentEvent.bond_id == bond_id
    ).order_by(PaymentEvent.payment_date.desc()).all()

    return [
        {
            "event_id": event.id,
            "bond_id": event.bond_id,
            "event_type": event.event_type.value,
            "event_name": event.event_name,
            "payment_date": event.payment_date.isoformat(),
            "calculation_period": event.calculation_period,
            "base_rate": float(event.base_rate) if event.base_rate else None,
            "withholding_tax_rate": float(event.withholding_tax_rate) if event.withholding_tax_rate else None,
            "boz_fee_rate": float(event.boz_fee_rate) if event.boz_fee_rate else None,
            "coop_fee_rate": float(event.coop_fee_rate) if event.coop_fee_rate else None,
            "boz_award_amount": float(event.boz_award_amount or 0),
            "expected_total_net_maturity": float(event.expected_total_net_maturity or 0),
            "expected_total_net_coupon": float(event.expected_total_net_coupon or 0),
            "created_at": event.created_at.isoformat()
        }
        for event in events
    ]


@router.get("/{bond_id}/payments/preview", response_model=dict)
def preview_payments(
    bond_id: int,
    event_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Preview payment calculations for a specific event.
    Does not save to database.
    """
    # Verify bond exists
    bond = db.query(BondIssue).filter(BondIssue.id == bond_id).first()
    if not bond:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bond issue not found"
        )

    # Verify event exists and belongs to this bond
    event = db.query(PaymentEvent).filter(
        PaymentEvent.id == event_id,
        PaymentEvent.bond_id == bond_id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment event not found for this bond"
        )

    # Calculate payments (preview mode)
    try:
        calculations = PaymentCalculatorService.calculate_payments_for_event(db, event_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Convert to dictionaries
    payments_preview = [calc.to_dict() for calc in calculations]

    # Calculate totals
    total_boz_award = sum(Decimal(str(p["boz_award_value"])) for p in payments_preview)
    total_net_discount = sum(Decimal(str(p["net_discount_value"])) for p in payments_preview)
    total_net_maturity_coupon = sum(Decimal(str(p["net_maturity_coupon"])) for p in payments_preview)
    total_net_coupon = sum(Decimal(str(p["net_coupon_payment"])) for p in payments_preview)
    total_gross = sum(Decimal(str(p["gross_coupon_from_boz"])) for p in payments_preview)

    return {
        "bond_id": bond_id,
        "bond_name": bond.issue_name,
        "event_id": event_id,
        "event_name": event.event_name,
        "event_type": event.event_type.value,
        "payment_date": event.payment_date.isoformat(),
        "preview": True,
        "payments": payments_preview,
        "summary": {
            "total_members": len(payments_preview),
            "total_boz_award_value": float(total_boz_award),
            "total_net_discount_value": float(total_net_discount),
            "total_net_maturity_coupon": float(total_net_maturity_coupon),
            "total_net_coupon_payment": float(total_net_coupon),
            "total_gross_coupon": float(total_gross)
        }
    }


@router.post("/{bond_id}/payments/generate", status_code=status.HTTP_201_CREATED)
def generate_payments(
    bond_id: int,
    event_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "treasurer"))
):
    """
    Generate and save payment records for a specific event (Admin/Treasurer only).
    """
    # Verify bond exists
    bond = db.query(BondIssue).filter(BondIssue.id == bond_id).first()
    if not bond:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bond issue not found"
        )

    # Verify event exists and belongs to this bond
    event = db.query(PaymentEvent).filter(
        PaymentEvent.id == event_id,
        PaymentEvent.bond_id == bond_id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment event not found for this bond"
        )

    # Check if payments already exist
    existing_count = db.query(MemberPayment).filter(
        MemberPayment.payment_event_id == event_id
    ).count()

    if existing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payments already exist for this event ({existing_count} records). Use recalculate endpoint to regenerate."
        )

    # Generate payments
    try:
        count = PaymentCalculatorService.generate_payments_for_event(db, event_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {
        "message": "Payments generated successfully",
        "event_id": event_id,
        "event_name": event.event_name,
        "payments_created": count
    }


@router.post("/{bond_id}/payments/recalculate", status_code=status.HTTP_200_OK)
def recalculate_payments(
    bond_id: int,
    event_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "treasurer"))
):
    """
    Delete existing payments and regenerate them for an event (Admin/Treasurer only).
    """
    # Verify bond exists
    bond = db.query(BondIssue).filter(BondIssue.id == bond_id).first()
    if not bond:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bond issue not found"
        )

    # Verify event exists and belongs to this bond
    event = db.query(PaymentEvent).filter(
        PaymentEvent.id == event_id,
        PaymentEvent.bond_id == bond_id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment event not found for this bond"
        )

    # Recalculate payments
    try:
        count = PaymentCalculatorService.recalculate_payments_for_event(db, event_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {
        "message": "Payments recalculated successfully",
        "event_id": event_id,
        "event_name": event.event_name,
        "payments_created": count
    }


@router.patch("/{bond_id}/events/{event_id}", status_code=status.HTTP_200_OK)
def update_payment_event(
    bond_id: int,
    event_id: int,
    event_data: PaymentEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "treasurer"))
):
    """
    Update a payment event (Admin/Treasurer only).
    """
    # Verify event exists and belongs to this bond
    event = db.query(PaymentEvent).filter(
        PaymentEvent.id == event_id,
        PaymentEvent.bond_id == bond_id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment event not found for this bond"
        )

    # Update fields
    if event_data.event_name is not None:
        event.event_name = event_data.event_name
    if event_data.payment_date is not None:
        event.payment_date = event_data.payment_date
    if event_data.calculation_period is not None:
        event.calculation_period = event_data.calculation_period
    if event_data.base_rate is not None:
        event.base_rate = event_data.base_rate
    if event_data.withholding_tax_rate is not None:
        event.withholding_tax_rate = event_data.withholding_tax_rate
    if event_data.boz_fee_rate is not None:
        event.boz_fee_rate = event_data.boz_fee_rate
    if event_data.coop_fee_rate is not None:
        event.coop_fee_rate = event_data.coop_fee_rate
    if event_data.boz_award_amount is not None:
        event.boz_award_amount = event_data.boz_award_amount
    if event_data.expected_total_net_maturity is not None:
        event.expected_total_net_maturity = event_data.expected_total_net_maturity
    if event_data.expected_total_net_coupon is not None:
        event.expected_total_net_coupon = event_data.expected_total_net_coupon

    db.commit()
    db.refresh(event)

    return {
        "message": "Payment event updated successfully",
        "event_id": event.id,
        "event_name": event.event_name
    }
