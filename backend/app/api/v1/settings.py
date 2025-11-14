from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.settings import SystemSetting
from app.schemas.reporting import SystemSettingResponse, SystemSettingUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=List[SystemSettingResponse])
def get_settings(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get system settings."""
    query = db.query(SystemSetting)

    if category:
        query = query.filter(SystemSetting.category == category)

    return query.all()


@router.get("/{setting_key}", response_model=SystemSettingResponse)
def get_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific setting by key."""
    setting = db.query(SystemSetting).filter(
        SystemSetting.setting_key == setting_key
    ).first()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{setting_key}' not found"
        )

    return setting


@router.patch("/{setting_key}", response_model=SystemSettingResponse)
def update_setting(
    setting_key: str,
    setting_update: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update a system setting (Admin only)."""
    setting = db.query(SystemSetting).filter(
        SystemSetting.setting_key == setting_key
    ).first()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{setting_key}' not found"
        )

    if not setting.is_editable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This setting is not editable"
        )

    setting.setting_value = setting_update.setting_value
    setting.updated_by = current_user.user_id

    db.commit()
    db.refresh(setting)

    return setting
