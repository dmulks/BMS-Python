from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.balance import MemberBalance, MonthlySummary
from app.schemas.reporting import MemberBalanceResponse, MonthlySummaryResponse
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate-monthly-summary", response_model=MonthlySummaryResponse)
def generate_monthly_summary(
    month: date = Query(..., description="First day of month to summarize"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Generate monthly summary report (Admin/Treasurer only).

    This creates or updates a comprehensive summary for the specified month including:
    - Total bond holdings
    - Purchase activity
    - Payment breakdown
    - Cooperative income
    """
    # Ensure month is first day
    month = date(month.year, month.month, 1)

    summary = ReportingService.generate_monthly_summary(
        db=db,
        month=month,
        generated_by=current_user.user_id
    )

    return summary


@router.post("/generate-member-balances")
def generate_member_balances(
    month: date = Query(..., description="First day of month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Generate member balance snapshots for all members (Admin/Treasurer only).

    Creates monthly balance records showing each member's:
    - Opening balance
    - Purchases during month
    - Payments received
    - Closing balance
    - Percentage share of cooperative
    """
    # Ensure month is first day
    month = date(month.year, month.month, 1)

    balances = ReportingService.generate_member_balances(db=db, month=month)

    return {
        "message": f"Generated {len(balances)} member balance records",
        "count": len(balances),
        "month": month
    }


@router.get("/monthly-summaries", response_model=List[MonthlySummaryResponse])
def get_monthly_summaries(
    limit: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly summaries (latest first)."""
    summaries = db.query(MonthlySummary).order_by(
        MonthlySummary.summary_month.desc()
    ).limit(limit).all()

    return summaries


@router.get("/monthly-summary/{month}", response_model=MonthlySummaryResponse)
def get_monthly_summary(
    month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly summary for a specific month."""
    # Ensure month is first day
    month = date(month.year, month.month, 1)

    summary = db.query(MonthlySummary).filter(
        MonthlySummary.summary_month == month
    ).first()

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary found for {month}"
        )

    return summary


@router.get("/member-balances", response_model=List[MemberBalanceResponse])
def get_member_balances(
    user_id: int = Query(None),
    month: date = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get member balance records.

    Members can only view their own balances.
    Admin/Treasurer can view all balances.
    """
    query = db.query(MemberBalance)

    # Members can only see their own balances
    if current_user.user_role.value == "member":
        query = query.filter(MemberBalance.user_id == current_user.user_id)
    elif user_id:
        query = query.filter(MemberBalance.user_id == user_id)

    if month:
        # Ensure month is first day
        month = date(month.year, month.month, 1)
        query = query.filter(MemberBalance.balance_date == month)

    return query.order_by(MemberBalance.balance_date.desc()).all()


@router.get("/portfolio/{user_id}")
def get_member_portfolio(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete portfolio for a member.

    Includes:
    - Total investment
    - Active bonds
    - Recent payments
    - Current holdings
    """
    # Members can only view their own portfolio
    if current_user.user_role.value == "member" and user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this portfolio"
        )

    portfolio = ReportingService.get_member_portfolio(db=db, user_id=user_id)

    return portfolio


@router.get("/dashboard")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard data based on user role.

    Members: Personal portfolio summary
    Admin/Treasurer: Cooperative-wide statistics
    """
    if current_user.user_role.value == "member":
        # Return member's portfolio
        portfolio = ReportingService.get_member_portfolio(
            db=db,
            user_id=current_user.user_id
        )
        return {
            "type": "member",
            "data": portfolio
        }
    else:
        # Return latest monthly summary
        latest_summary = db.query(MonthlySummary).order_by(
            MonthlySummary.summary_month.desc()
        ).first()

        return {
            "type": "admin",
            "data": latest_summary
        }
