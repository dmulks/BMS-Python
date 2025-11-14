from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.bond import BondType, InterestRate, BondPurchase
from app.schemas.bond import (
    BondTypeCreate,
    BondTypeResponse,
    InterestRateCreate,
    InterestRateResponse,
    BondPurchaseCreate,
    BondPurchaseResponse
)
from app.services.bond_calculator import BondCalculator

router = APIRouter(prefix="/bonds", tags=["Bonds"])


# Bond Types Endpoints
@router.post("/types", response_model=BondTypeResponse, status_code=status.HTTP_201_CREATED)
def create_bond_type(
    bond_type_data: BondTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create a new bond type (Admin only)."""
    db_bond_type = BondType(**bond_type_data.dict())
    db.add(db_bond_type)
    db.commit()
    db.refresh(db_bond_type)
    return db_bond_type


@router.get("/types", response_model=List[BondTypeResponse])
def get_bond_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bond types."""
    return db.query(BondType).filter(BondType.is_active == True).all()


# Interest Rates Endpoints
@router.post("/rates", response_model=InterestRateResponse, status_code=status.HTTP_201_CREATED)
def create_interest_rate(
    rate_data: InterestRateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "treasurer"))
):
    """Create a new interest rate (Admin/Treasurer only)."""
    # Calculate daily rate
    daily_rate = BondCalculator.calculate_daily_rate(rate_data.annual_rate)

    # Check if rate already exists for this bond type and month
    existing = db.query(InterestRate).filter(
        InterestRate.bond_type_id == rate_data.bond_type_id,
        InterestRate.effective_month == rate_data.effective_month
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interest rate already exists for this bond type and month"
        )

    db_rate = InterestRate(
        bond_type_id=rate_data.bond_type_id,
        effective_month=rate_data.effective_month,
        annual_rate=rate_data.annual_rate,
        daily_coupon_rate=daily_rate,
        entered_by=current_user.user_id,
        notes=rate_data.notes
    )

    db.add(db_rate)
    db.commit()
    db.refresh(db_rate)
    return db_rate


@router.get("/rates", response_model=List[InterestRateResponse])
def get_interest_rates(
    bond_type_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get interest rates, optionally filtered by bond type."""
    query = db.query(InterestRate)

    if bond_type_id:
        query = query.filter(InterestRate.bond_type_id == bond_type_id)

    return query.order_by(InterestRate.effective_month.desc()).all()


# Bond Purchases Endpoints
@router.post("/purchases", response_model=BondPurchaseResponse, status_code=status.HTTP_201_CREATED)
def create_bond_purchase(
    purchase_data: BondPurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "treasurer"))
):
    """Create a new bond purchase (Admin/Treasurer only)."""
    # Verify user exists
    user = db.query(User).filter(User.user_id == purchase_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify bond type exists
    bond_type = db.query(BondType).filter(BondType.bond_type_id == purchase_data.bond_type_id).first()
    if not bond_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bond type not found"
        )

    # Calculate all values using Bond Calculator
    calc_results = BondCalculator.calculate_purchase_breakdown(
        bond_shares=purchase_data.bond_shares,
        purchase_date=purchase_data.purchase_date,
        maturity_years=bond_type.maturity_period_years,
        discount_rate=purchase_data.discount_rate or Decimal("0.10")
    )

    # Create purchase record
    db_purchase = BondPurchase(
        user_id=purchase_data.user_id,
        bond_type_id=purchase_data.bond_type_id,
        purchase_date=purchase_data.purchase_date,
        purchase_month=date(purchase_data.purchase_date.year, purchase_data.purchase_date.month, 1),
        bond_shares=purchase_data.bond_shares,
        face_value=calc_results["face_value"],
        discount_value=calc_results["discount_value"],
        coop_discount_fee=calc_results["coop_discount_fee"],
        net_discount_value=calc_results["net_discount_value"],
        purchase_price=calc_results["purchase_price"],
        maturity_date=calc_results["maturity_date"],
        transaction_reference=f"TXN{purchase_data.purchase_date.strftime('%Y%m%d')}{purchase_data.user_id:04d}",
        notes=purchase_data.notes
    )

    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


@router.get("/purchases", response_model=List[BondPurchaseResponse])
def get_bond_purchases(
    user_id: int = Query(None),
    bond_type_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bond purchases, optionally filtered by user and/or bond type."""
    query = db.query(BondPurchase)

    # Members can only see their own purchases
    if current_user.user_role.value == "member":
        query = query.filter(BondPurchase.user_id == current_user.user_id)
    elif user_id:
        query = query.filter(BondPurchase.user_id == user_id)

    if bond_type_id:
        query = query.filter(BondPurchase.bond_type_id == bond_type_id)

    return query.order_by(BondPurchase.purchase_date.desc()).all()


@router.get("/purchases/{purchase_id}", response_model=BondPurchaseResponse)
def get_bond_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific bond purchase by ID."""
    purchase = db.query(BondPurchase).filter(BondPurchase.purchase_id == purchase_id).first()

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bond purchase not found"
        )

    # Members can only see their own purchases
    if current_user.user_role.value == "member" and purchase.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this purchase"
        )

    return purchase
