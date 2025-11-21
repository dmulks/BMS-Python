from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import pandas as pd
import io

from app.core.database import get_db
from app.core.security import get_current_user, require_role, get_password_hash
from app.models.user import User, UserRole
from app.models.bond import BondType, InterestRate, BondPurchase, PurchaseStatus
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
    current_user: User = Depends(require_role("admin", "account_manager"))
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
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
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
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
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

    # Reload with relationships
    db_purchase = db.query(BondPurchase).options(
        joinedload(BondPurchase.user),
        joinedload(BondPurchase.bond_type)
    ).filter(BondPurchase.purchase_id == db_purchase.purchase_id).first()

    return db_purchase


@router.get("/purchases", response_model=List[BondPurchaseResponse])
def get_bond_purchases(
    user_id: int = Query(None),
    bond_type_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bond purchases, optionally filtered by user and/or bond type."""
    query = db.query(BondPurchase).options(
        joinedload(BondPurchase.user),
        joinedload(BondPurchase.bond_type)
    )

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
    purchase = db.query(BondPurchase).options(
        joinedload(BondPurchase.user),
        joinedload(BondPurchase.bond_type)
    ).filter(BondPurchase.purchase_id == purchase_id).first()

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


# Excel Import Endpoint
@router.post("/import-excel")
async def import_excel(
    file: UploadFile = File(...),
    purchase_date: Optional[str] = Query(None, description="Purchase date in YYYY-MM-DD format"),
    bond_type_name: str = Query("2-Year Bond", description="Bond type name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """Import users and bond purchases from Excel file (Admin/Treasurer only)."""

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )

    # Parse purchase date
    if purchase_date:
        try:
            parsed_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        parsed_date = date.today()

    # Get bond type
    bond_type = db.query(BondType).filter(BondType.bond_name == bond_type_name).first()
    if not bond_type:
        available_types = db.query(BondType).filter(BondType.is_active == True).all()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bond type '{bond_type_name}' not found. Available types: {[bt.bond_name for bt in available_types]}"
        )

    # Read Excel file
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents), sheet_name=0, header=1)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read Excel file: {str(e)}"
        )

    # Import statistics
    stats = {
        "users_created": 0,
        "users_updated": 0,
        "bonds_created": 0,
        "errors": []
    }

    # Process each row
    for index, row in df.iterrows():
        try:
            # Skip rows without bond shares or with 0 shares
            if pd.isna(row.get('Bond Shares')) or float(row.get('Bond Shares', 0)) == 0:
                continue

            # Extract user data
            email = str(row['Email']).strip().lower()
            first_name = str(row['First Name']).strip()
            last_name = str(row['Last Name']).strip()

            # Validate email
            if '@' not in email:
                stats["errors"].append(f"Row {index + 2}: Invalid email '{email}'")
                continue

            # Create or update user
            user = db.query(User).filter(User.email == email).first()

            if not user:
                # Create new user
                username = email.split('@')[0]
                user = User(
                    username=username,
                    email=email,
                    password_hash=get_password_hash("change123"),
                    first_name=first_name,
                    last_name=last_name,
                    user_role=UserRole.MEMBER,
                    is_active=True
                )
                db.add(user)
                db.flush()
                stats["users_created"] += 1
            else:
                # Update existing user if names changed
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    stats["users_updated"] += 1

            # Extract bond data
            bond_shares = float(row['Bond Shares'])
            face_value = float(row['FACE Value '])  # Note trailing space
            discount_value = float(row['Discount Value Paid on Maturity'])

            # Calculate values
            coop_discount_fee = discount_value * Decimal("0.02")
            net_discount_value = Decimal(str(discount_value)) - coop_discount_fee
            purchase_price = Decimal(str(face_value)) - Decimal(str(discount_value))
            purchase_month = date(parsed_date.year, parsed_date.month, 1)
            maturity_date = date(
                parsed_date.year + bond_type.maturity_period_years,
                parsed_date.month,
                parsed_date.day
            )

            # Check for duplicates
            existing = db.query(BondPurchase).filter(
                BondPurchase.user_id == user.user_id,
                BondPurchase.bond_type_id == bond_type.bond_type_id,
                BondPurchase.purchase_date == parsed_date,
                BondPurchase.face_value == Decimal(str(face_value))
            ).first()

            if existing:
                continue

            # Create bond purchase
            bond_purchase = BondPurchase(
                user_id=user.user_id,
                bond_type_id=bond_type.bond_type_id,
                purchase_date=parsed_date,
                purchase_month=purchase_month,
                bond_shares=Decimal(str(bond_shares)),
                face_value=Decimal(str(face_value)),
                discount_value=Decimal(str(discount_value)),
                coop_discount_fee=coop_discount_fee,
                net_discount_value=net_discount_value,
                purchase_price=purchase_price,
                maturity_date=maturity_date,
                purchase_status=PurchaseStatus.ACTIVE,
                transaction_reference=f"TXN{parsed_date.strftime('%Y%m%d')}{user.user_id:04d}"
            )

            db.add(bond_purchase)
            stats["bonds_created"] += 1

        except Exception as e:
            stats["errors"].append(f"Row {index + 2}: {str(e)}")
            continue

    # Commit all changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save data: {str(e)}"
        )

    return {
        "success": True,
        "message": "Import completed successfully",
        "statistics": stats
    }
