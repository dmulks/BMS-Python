from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.payment import PaymentVoucher
from app.services.voucher_service import VoucherService
from app.services.email_service import EmailService

router = APIRouter(prefix="/vouchers", tags=["Vouchers"])


@router.post("/generate/{payment_id}")
def generate_voucher(
    payment_id: int,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Generate a payment voucher PDF (Admin/Treasurer only).

    Args:
        payment_id: ID of the coupon payment
        send_email: Whether to email the voucher to the member

    Returns:
        Voucher details and PDF path
    """
    try:
        result = VoucherService.generate_voucher(
            db=db,
            payment_id=payment_id,
            generated_by=current_user.user_id
        )

        # Optionally send email
        if send_email:
            from app.models.payment import CouponPayment
            payment = db.query(CouponPayment).filter(
                CouponPayment.payment_id == payment_id
            ).first()
            if payment:
                EmailService.send_payment_notification(db, payment)

        return {
            "message": "Voucher generated successfully",
            "voucher_number": result["voucher_number"],
            "pdf_path": result["pdf_path"],
            "voucher_id": result["voucher"].voucher_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating voucher: {str(e)}"
        )


@router.get("/download/{voucher_id}")
def download_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a voucher PDF."""
    voucher = db.query(PaymentVoucher).filter(
        PaymentVoucher.voucher_id == voucher_id
    ).first()

    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher not found"
        )

    # Members can only download their own vouchers
    if current_user.user_role.value == "member" and voucher.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this voucher"
        )

    # Construct file path
    import os
    temp_dir = os.path.join(os.path.dirname(__file__), '../../../temp')
    filename = f"voucher_{voucher.voucher_number}.pdf"
    filepath = os.path.join(temp_dir, filename)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher PDF file not found"
        )

    return FileResponse(
        path=filepath,
        media_type='application/pdf',
        filename=filename
    )


@router.patch("/{voucher_id}/status")
def update_voucher_status(
    voucher_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """Update voucher status (Admin/Treasurer only)."""
    voucher = db.query(PaymentVoucher).filter(
        PaymentVoucher.voucher_id == voucher_id
    ).first()

    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher not found"
        )

    from app.models.payment import VoucherStatus
    from datetime import datetime

    try:
        voucher.voucher_status = VoucherStatus(new_status)

        if new_status == "issued":
            voucher.issued_at = datetime.utcnow()
        elif new_status == "paid":
            voucher.paid_at = datetime.utcnow()
            voucher.paid_by = current_user.user_id

        db.commit()
        db.refresh(voucher)

        return {
            "message": "Voucher status updated successfully",
            "voucher": voucher
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}"
        )
