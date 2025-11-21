from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.bond import BondPurchase, InterestRate
from app.models.payment import CouponPayment, PaymentVoucher, PaymentType, PaymentStatus
from app.schemas.payment import CouponPaymentCreate, CouponPaymentResponse, PaymentVoucherResponse
from app.services.bond_calculator import BondCalculator

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/calculate-coupons", status_code=status.HTTP_200_OK)
def calculate_coupon_payments(
    period_start: date = Query(...),
    period_end: date = Query(...),
    create_payments: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Calculate coupon payments for a specific period.
    If create_payments is True, this will create pending payment records.
    Otherwise, it returns a preview of calculations.
    """
    # Get all active bond purchases
    active_purchases = db.query(BondPurchase).filter(
        BondPurchase.purchase_status == "active",
        BondPurchase.purchase_date <= period_end
    ).all()

    calculations = []
    total_gross = Decimal("0")
    total_net = Decimal("0")

    for purchase in active_purchases:
        # Determine payment type
        is_maturity = purchase.maturity_date <= period_end
        payment_type = PaymentType.MATURITY if is_maturity else PaymentType.SEMI_ANNUAL

        # Get interest rate for the period
        rate = db.query(InterestRate).filter(
            InterestRate.bond_type_id == purchase.bond_type_id,
            InterestRate.effective_month <= period_start
        ).order_by(InterestRate.effective_month.desc()).first()

        if not rate:
            continue

        # Calculate calendar days
        calc_start = max(purchase.purchase_date, period_start)
        calc_end = min(purchase.maturity_date, period_end)
        calendar_days = BondCalculator.calculate_calendar_days(calc_start, calc_end)

        if calendar_days <= 0:
            continue

        # Calculate payment breakdown
        payment_calc = BondCalculator.calculate_coupon_payment(
            face_value=purchase.face_value,
            daily_rate=rate.daily_coupon_rate,
            calendar_days=calendar_days
        )

        # Add to calculations
        calculations.append({
            "user_id": purchase.user_id,
            "purchase_id": purchase.purchase_id,
            "payment_type": payment_type.value,
            "gross_coupon": float(payment_calc["gross_coupon"]),
            "net_payment": float(payment_calc["net_payment"]),
            "calendar_days": calendar_days
        })

        total_gross += payment_calc["gross_coupon"]
        total_net += payment_calc["net_payment"]

        # Create payment record if requested
        if create_payments:
            db_payment = CouponPayment(
                purchase_id=purchase.purchase_id,
                user_id=purchase.user_id,
                payment_type=payment_type,
                payment_date=period_end,
                payment_period_start=calc_start,
                payment_period_end=calc_end,
                calendar_days=calendar_days,
                gross_coupon_amount=payment_calc["gross_coupon"],
                withholding_tax=payment_calc["withholding_tax"],
                boz_fees=payment_calc["boz_fees"],
                coop_fees=payment_calc["coop_fees"],
                net_payment_amount=payment_calc["net_payment"],
                payment_status=PaymentStatus.PENDING,
                payment_reference=f"PAY{period_end.strftime('%Y%m%d')}{purchase.purchase_id:06d}"
            )
            db.add(db_payment)

    if create_payments:
        db.commit()
        return {
            "message": f"Created {len(calculations)} coupon payment records",
            "count": len(calculations),
            "payments_created": len(calculations)
        }
    else:
        return {
            "message": "Calculation preview",
            "calculations": calculations,
            "calculations_count": len(calculations),
            "total_gross_amount": float(total_gross),
            "total_net_amount": float(total_net)
        }


@router.get("/coupons", response_model=List[CouponPaymentResponse])
def get_coupon_payments(
    user_id: int = Query(None),
    payment_status: PaymentStatus = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get coupon payments, optionally filtered."""
    query = db.query(CouponPayment)

    # Members can only see their own payments
    if current_user.user_role.value == "member":
        query = query.filter(CouponPayment.user_id == current_user.user_id)
    elif user_id:
        query = query.filter(CouponPayment.user_id == user_id)

    if payment_status:
        query = query.filter(CouponPayment.payment_status == payment_status)

    return query.order_by(CouponPayment.payment_date.desc()).all()


@router.get("/coupons/{payment_id}", response_model=CouponPaymentResponse)
def get_coupon_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific coupon payment by ID."""
    payment = db.query(CouponPayment).filter(CouponPayment.payment_id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Members can only see their own payments
    if current_user.user_role.value == "member" and payment.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )

    return payment


@router.patch("/coupons/{payment_id}/status")
def update_payment_status(
    payment_id: int,
    new_status: PaymentStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """Update payment status (Admin/Treasurer only)."""
    payment = db.query(CouponPayment).filter(CouponPayment.payment_id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    payment.payment_status = new_status

    if new_status == PaymentStatus.PROCESSED:
        from datetime import datetime
        payment.processed_by = current_user.user_id
        payment.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(payment)

    return {"message": "Payment status updated successfully", "payment": payment}


@router.get("/vouchers", response_model=List[PaymentVoucherResponse])
def get_payment_vouchers(
    user_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment vouchers."""
    query = db.query(PaymentVoucher)

    if current_user.user_role.value == "member":
        query = query.filter(PaymentVoucher.user_id == current_user.user_id)
    elif user_id:
        query = query.filter(PaymentVoucher.user_id == user_id)

    return query.order_by(PaymentVoucher.voucher_date.desc()).all()
