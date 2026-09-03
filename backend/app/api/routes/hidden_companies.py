from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.user import User, HiddenCompany
from app.services.auth import get_current_user

router = APIRouter(prefix="/hidden-companies", tags=["hidden-companies"])


class HiddenCompanyCreate(BaseModel):
    company_name: str
    reason: Optional[str] = None


class HiddenCompanyResponse(BaseModel):
    id: str
    company_name: str
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[HiddenCompanyResponse])
async def get_hidden_companies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all hidden companies for current user"""
    result = await db.execute(
        select(HiddenCompany).where(HiddenCompany.user_id == current_user.id)
    )
    hidden_companies = result.scalars().all()
    return hidden_companies


@router.post("/", response_model=HiddenCompanyResponse)
async def hide_company(
    hidden_company_data: HiddenCompanyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Hide a company from job listings"""
    # Check if already hidden
    existing = await db.execute(
        select(HiddenCompany).where(
            HiddenCompany.user_id == current_user.id,
            HiddenCompany.company_name == hidden_company_data.company_name
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company already hidden"
        )
    
    hidden_company = HiddenCompany(
        user_id=current_user.id,
        company_name=hidden_company_data.company_name,
        reason=hidden_company_data.reason
    )
    db.add(hidden_company)
    await db.commit()
    await db.refresh(hidden_company)
    
    return hidden_company


@router.delete("/{company_name}")
async def unhide_company(
    company_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unhide a company"""
    result = await db.execute(
        select(HiddenCompany).where(
            HiddenCompany.user_id == current_user.id,
            HiddenCompany.company_name == company_name
        )
    )
    hidden_company = result.scalar_one_or_none()
    
    if not hidden_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hidden company not found"
        )
    
    await db.delete(hidden_company)
    await db.commit()
    
    return {"status": "success", "message": f"Company {company_name} unhidden"}