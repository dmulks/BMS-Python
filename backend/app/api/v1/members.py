from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models import User, UserRole, MemberBondHolding, BondIssue
from app.services.payment_calculator import PaymentCalculatorService

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("", response_model=List[dict])
def get_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "account_manager", "treasurer"))
):
    """
    Get all members (Admin/Treasurer only).
    Supports pagination.
    """
    members = db.query(User).filter(
        User.user_role == UserRole.MEMBER
    ).offset(skip).limit(limit).all()

    return [
        {
            "user_id": member.user_id,
            "username": member.username,
            "email": member.email,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "phone_number": member.phone_number,
            "is_active": member.is_active,
            "created_at": member.created_at.isoformat()
        }
        for member in members
    ]


@router.get("/{member_id}", response_model=dict)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get member details.
    Members can only view their own details, Admin/Treasurer can view any member.
    """
    # Members can only see their own details
    if current_user.user_role == UserRole.MEMBER and current_user.user_id != member_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this member"
        )

    member = db.query(User).filter(User.user_id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Get member's bond holdings
    holdings = db.query(MemberBondHolding, BondIssue).join(
        BondIssue, BondIssue.id == MemberBondHolding.bond_id
    ).filter(
        MemberBondHolding.member_id == member_id
    ).all()

    holdings_list = []
    for holding, bond in holdings:
        holdings_list.append({
            "holding_id": holding.id,
            "bond_id": bond.id,
            "bond_name": bond.issue_name,
            "bond_type": bond.bond_type.value,
            "as_of_date": holding.as_of_date.isoformat(),
            "bond_shares": float(holding.bond_shares),
            "member_face_value": float(holding.member_face_value),
            "percentage_share": float(holding.percentage_share or 0)
        })

    return {
        "user_id": member.user_id,
        "username": member.username,
        "email": member.email,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "phone_number": member.phone_number,
        "address": member.address,
        "is_active": member.is_active,
        "created_at": member.created_at.isoformat(),
        "bond_holdings": holdings_list
    }


@router.get("/{member_id}/payments", response_model=dict)
def get_member_payments_report(
    member_id: int,
    bond_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get member payment report showing all payments for a member.
    Members can only view their own payments, Admin/Treasurer can view any member.
    """
    # Members can only see their own payments
    if current_user.user_role == UserRole.MEMBER and current_user.user_id != member_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these payments"
        )

    # Verify member exists
    member = db.query(User).filter(User.user_id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Get payments using the service
    payments = PaymentCalculatorService.get_member_payments(db, member_id, bond_id)

    # Calculate totals
    total_boz_award = sum(Decimal(str(p["boz_award_value"])) for p in payments)
    total_net_discount = sum(Decimal(str(p["net_discount_value"])) for p in payments)
    total_net_maturity_coupon = sum(Decimal(str(p["net_maturity_coupon"])) for p in payments)
    total_net_coupon = sum(Decimal(str(p["net_coupon_payment"])) for p in payments)
    total_gross = sum(Decimal(str(p["gross_coupon_from_boz"])) for p in payments)
    total_taxes = sum(Decimal(str(p["withholding_tax"])) for p in payments)
    total_fees = sum(
        Decimal(str(p["boz_fee"])) +
        Decimal(str(p["coop_fee_on_coupon"])) +
        Decimal(str(p["coop_discount_fee"]))
        for p in payments
    )

    return {
        "member_id": member_id,
        "member_name": f"{member.first_name} {member.last_name}",
        "member_email": member.email,
        "payments": payments,
        "totals": {
            "total_boz_award_value": float(total_boz_award),
            "total_net_discount_value": float(total_net_discount),
            "total_net_maturity_coupon": float(total_net_maturity_coupon),
            "total_net_coupon_payment": float(total_net_coupon),
            "total_gross_coupon": float(total_gross),
            "total_taxes": float(total_taxes),
            "total_fees": float(total_fees)
        },
        "payment_count": len(payments)
    }


@router.get("/{member_id}/holdings", response_model=List[dict])
def get_member_holdings(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bond holdings for a specific member.
    Members can only view their own holdings, Admin/Treasurer can view any member.
    """
    # Members can only see their own holdings
    if current_user.user_role == UserRole.MEMBER and current_user.user_id != member_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these holdings"
        )

    holdings = db.query(MemberBondHolding, BondIssue).join(
        BondIssue, BondIssue.id == MemberBondHolding.bond_id
    ).filter(
        MemberBondHolding.member_id == member_id
    ).order_by(MemberBondHolding.as_of_date.desc()).all()

    return [
        {
            "holding_id": holding.id,
            "bond_id": bond.id,
            "bond_name": bond.issue_name,
            "bond_type": bond.bond_type.value,
            "issuer": bond.issuer,
            "issue_date": bond.issue_date.isoformat(),
            "maturity_date": bond.maturity_date.isoformat(),
            "as_of_date": holding.as_of_date.isoformat(),
            "bond_shares": float(holding.bond_shares),
            "member_face_value": float(holding.member_face_value),
            "percentage_share": float(holding.percentage_share or 0),
            "opening_balance": float(holding.opening_balance or 0),
            "total_bond_share": float(holding.total_bond_share or 0),
            "award_value_plus_balance_bf": float(holding.award_value_plus_balance_bf or 0),
            "variance_cf_next_period": float(holding.variance_cf_next_period or 0)
        }
        for holding, bond in holdings
    ]
