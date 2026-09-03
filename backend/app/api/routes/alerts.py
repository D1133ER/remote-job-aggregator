from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.user import User, JobAlert
from app.services.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertCreate(BaseModel):
    name: str
    keywords: Optional[str] = None
    category: Optional[str] = None
    remote_type: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    frequency: str = "daily"


class AlertResponse(BaseModel):
    id: str
    name: str
    keywords: Optional[str]
    category: Optional[str]
    remote_type: Optional[str]
    location: Optional[str]
    salary_min: Optional[int]
    is_active: bool
    frequency: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    keywords: Optional[str] = None
    category: Optional[str] = None
    remote_type: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all alerts for current user"""
    result = await db.execute(
        select(JobAlert).where(JobAlert.user_id == current_user.id)
    )
    alerts = result.scalars().all()
    return alerts


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new job alert"""
    # Check if user has too many alerts (limit for free users)
    if not current_user.is_premium:
        result = await db.execute(
            select(JobAlert).where(JobAlert.user_id == current_user.id)
        )
        alert_count = len(result.scalars().all())
        if alert_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Free users can have up to 5 alerts. Upgrade to premium for unlimited alerts."
            )
    
    alert = JobAlert(
        user_id=current_user.id,
        name=alert_data.name,
        keywords=alert_data.keywords,
        category=alert_data.category,
        remote_type=alert_data.remote_type,
        location=alert_data.location,
        salary_min=alert_data.salary_min,
        frequency=alert_data.frequency
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_data: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a job alert"""
    result = await db.execute(
        select(JobAlert).where(
            JobAlert.id == alert_id,
            JobAlert.user_id == current_user.id
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update fields
    if alert_data.name is not None:
        alert.name = alert_data.name
    if alert_data.keywords is not None:
        alert.keywords = alert_data.keywords
    if alert_data.category is not None:
        alert.category = alert_data.category
    if alert_data.remote_type is not None:
        alert.remote_type = alert_data.remote_type
    if alert_data.location is not None:
        alert.location = alert_data.location
    if alert_data.salary_min is not None:
        alert.salary_min = alert_data.salary_min
    if alert_data.frequency is not None:
        alert.frequency = alert_data.frequency
    if alert_data.is_active is not None:
        alert.is_active = alert_data.is_active
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a job alert"""
    result = await db.execute(
        select(JobAlert).where(
            JobAlert.id == alert_id,
            JobAlert.user_id == current_user.id
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    await db.delete(alert)
    await db.commit()
    
    return {"status": "success", "message": "Alert deleted"}