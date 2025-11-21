from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.services.excel_service import ExcelService

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/monthly-summary/{month}")
def export_monthly_summary(
    month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Export monthly summary to Excel (Admin/Treasurer only).

    Args:
        month: Month to export (first day of month)

    Returns:
        Excel file download
    """
    try:
        # Ensure month is first day
        month = date(month.year, month.month, 1)

        filepath = ExcelService.export_monthly_summary(db, month)

        return FileResponse(
            path=filepath,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"monthly_summary_{month.strftime('%Y_%m')}.xlsx"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting summary: {str(e)}"
        )


@router.get("/payment-register")
def export_payment_register(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Export payment register to Excel (Admin/Treasurer only).

    Args:
        start_date: Start date for payments
        end_date: End date for payments

    Returns:
        Excel file download
    """
    try:
        filepath = ExcelService.export_payment_register(db, start_date, end_date)

        return FileResponse(
            path=filepath,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"payment_register_{start_date}_{end_date}.xlsx"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting register: {str(e)}"
        )


@router.post("/import-purchases")
def import_bond_purchases(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager"))
):
    """
    Import bond purchases from Excel (Admin only).

    The Excel file should have the following columns:
    - email (required): Member email address
    - bond_shares (required): Number of bond shares
    - purchase_date (required): Purchase date (YYYY-MM-DD)
    - bond_type (required): Bond type name (e.g., "2-Year Bond")
    - discount_rate (optional): Discount rate (default: 0.10)
    - notes (optional): Additional notes

    Returns:
        Import results with success and error counts
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )

    try:
        # Save uploaded file temporarily
        import os
        temp_dir = os.path.join(os.path.dirname(__file__), '../../../temp')
        os.makedirs(temp_dir, exist_ok=True)

        filepath = os.path.join(temp_dir, f"import_{file.filename}")
        with open(filepath, "wb") as buffer:
            buffer.write(file.file.read())

        # Import data
        results = ExcelService.import_bond_purchases(
            db=db,
            file_path=filepath,
            imported_by=current_user.user_id
        )

        # Clean up temp file
        os.remove(filepath)

        return {
            "message": f"Import completed: {len(results['success'])} successful, {len(results['errors'])} errors",
            "total": results['total'],
            "success_count": len(results['success']),
            "error_count": len(results['errors']),
            "successes": results['success'],
            "errors": results['errors']
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing purchases: {str(e)}"
        )
