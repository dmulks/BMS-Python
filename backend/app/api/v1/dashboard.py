from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict
from datetime import date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import (
    User, BondIssue, MemberBondHolding, PaymentEvent,
    MemberPayment, BondPurchase
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=Dict)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard KPIs and upcoming events.
    Returns global statistics and upcoming payment events.
    """

    # Total number of bond issues
    total_bond_issues = db.query(func.count(BondIssue.id)).scalar() or 0

    # Total number of members with holdings
    total_members_with_holdings = db.query(
        func.count(func.distinct(MemberBondHolding.member_id))
    ).scalar() or 0

    # Total number of all members (from users)
    total_members = db.query(func.count(User.user_id)).filter(
        User.user_role == "member"
    ).scalar() or 0

    # Total face value across all holdings
    total_face_value = db.query(
        func.sum(MemberBondHolding.member_face_value)
    ).scalar() or 0

    # Total bond shares
    total_bond_shares = db.query(
        func.sum(MemberBondHolding.bond_shares)
    ).scalar() or 0

    # Upcoming payment events (next 90 days)
    today = date.today()
    upcoming_date = today + timedelta(days=90)

    upcoming_events = db.query(PaymentEvent, BondIssue).join(
        BondIssue, BondIssue.id == PaymentEvent.bond_id
    ).filter(
        PaymentEvent.payment_date >= today,
        PaymentEvent.payment_date <= upcoming_date
    ).order_by(PaymentEvent.payment_date.asc()).limit(10).all()

    upcoming_events_list = []
    for event, bond in upcoming_events:
        # Count payments generated for this event
        payments_count = db.query(func.count(MemberPayment.id)).filter(
            MemberPayment.payment_event_id == event.id
        ).scalar() or 0

        upcoming_events_list.append({
            "event_id": event.id,
            "event_name": event.event_name,
            "event_type": event.event_type.value,
            "payment_date": event.payment_date.isoformat(),
            "bond_id": bond.id,
            "bond_name": bond.issue_name,
            "bond_type": bond.bond_type.value,
            "boz_award_amount": float(event.boz_award_amount or 0),
            "payments_generated": payments_count > 0,
            "payments_count": payments_count
        })

    # Recent payment events (last 30 days)
    past_date = today - timedelta(days=30)

    recent_events = db.query(PaymentEvent, BondIssue).join(
        BondIssue, BondIssue.id == PaymentEvent.bond_id
    ).filter(
        PaymentEvent.payment_date >= past_date,
        PaymentEvent.payment_date < today
    ).order_by(PaymentEvent.payment_date.desc()).limit(5).all()

    recent_events_list = []
    for event, bond in recent_events:
        payments_count = db.query(func.count(MemberPayment.id)).filter(
            MemberPayment.payment_event_id == event.id
        ).scalar() or 0

        # Sum of total payments
        total_paid = db.query(
            func.coalesce(
                func.sum(MemberPayment.net_maturity_coupon + MemberPayment.net_coupon_payment),
                0
            )
        ).filter(
            MemberPayment.payment_event_id == event.id
        ).scalar() or 0

        recent_events_list.append({
            "event_id": event.id,
            "event_name": event.event_name,
            "event_type": event.event_type.value,
            "payment_date": event.payment_date.isoformat(),
            "bond_id": bond.id,
            "bond_name": bond.issue_name,
            "payments_count": payments_count,
            "total_paid": float(total_paid)
        })

    # Statistics for individual purchase system (existing)
    total_bond_purchases = db.query(func.count(BondPurchase.purchase_id)).scalar() or 0
    total_purchase_face_value = db.query(
        func.sum(BondPurchase.face_value)
    ).scalar() or 0

    total_purchase_bond_shares = db.query(
        func.sum(BondPurchase.bond_shares)
    ).scalar() or 0

    active_purchases = db.query(func.count(BondPurchase.purchase_id)).filter(
        BondPurchase.purchase_status == "active"
    ).scalar() or 0

    return {
        "kpis": {
            "total_bond_issues": total_bond_issues,
            "total_members": total_members,
            "total_members_with_holdings": total_members_with_holdings,
            "total_face_value": float(total_face_value),
            "total_bond_shares": float(total_bond_shares),
            "total_bond_purchases": total_bond_purchases,
            "total_purchase_face_value": float(total_purchase_face_value),
            "total_purchase_bond_shares": float(total_purchase_bond_shares),
            "active_purchases": active_purchases
        },
        "upcoming_events": upcoming_events_list,
        "recent_events": recent_events_list,
        "current_date": today.isoformat()
    }
