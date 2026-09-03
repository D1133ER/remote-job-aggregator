from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.job import Job, Company

router = APIRouter(prefix="/companies", tags=["companies"])


class CompanyResponse(BaseModel):
    id: str
    name: str
    logo_url: Optional[str]
    website: Optional[str]
    description: Optional[str]
    industry: Optional[str]
    remote_policy: Optional[str]
    average_response_time: Optional[str]
    total_jobs_posted: int
    total_jobs_remote: int
    
    class Config:
        from_attributes = True


class CompanyStats(BaseModel):
    total_jobs: int
    remote_jobs: int
    average_salary_min: Optional[float]
    average_salary_max: Optional[float]
    top_skills: List[str]
    categories: List[str]


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    industry: Optional[str] = None,
    remote_policy: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get list of companies"""
    query = select(Company)
    
    if industry:
        query = query.where(Company.industry == industry)
    
    if remote_policy:
        query = query.where(Company.remote_policy == remote_policy)
    
    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    return companies


@router.get("/{company_name}", response_model=CompanyResponse)
async def get_company(
    company_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get company details by name"""
    result = await db.execute(
        select(Company).where(Company.name == company_name)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    return company


@router.get("/{company_name}/stats", response_model=CompanyStats)
async def get_company_stats(
    company_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get company statistics"""
    # Get all jobs for this company
    result = await db.execute(
        select(Job).where(
            Job.company_name == company_name,
            Job.is_active == True
        )
    )
    jobs = result.scalars().all()
    
    if not jobs:
        raise HTTPException(
            status_code=404,
            detail="No jobs found for this company"
        )
    
    # Calculate stats
    total_jobs = len(jobs)
    remote_jobs = sum(1 for job in jobs if job.remote_type == "full_remote")
    
    # Salary stats
    salaries_min = [job.salary_min for job in jobs if job.salary_min]
    salaries_max = [job.salary_max for job in jobs if job.salary_max]
    
    avg_salary_min = sum(salaries_min) / len(salaries_min) if salaries_min else None
    avg_salary_max = sum(salaries_max) / len(salaries_max) if salaries_max else None
    
    # Top skills
    all_skills = []
    for job in jobs:
        if job.skills:
            all_skills.extend(job.skills)
    
    skill_counts = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_skills = sorted(skill_counts.keys(), key=lambda x: skill_counts[x], reverse=True)[:10]
    
    # Categories
    categories = list(set(job.category for job in jobs if job.category))
    
    return CompanyStats(
        total_jobs=total_jobs,
        remote_jobs=remote_jobs,
        average_salary_min=avg_salary_min,
        average_salary_max=avg_salary_max,
        top_skills=top_skills,
        categories=categories
    )


@router.get("/{company_name}/jobs")
async def get_company_jobs(
    company_name: str,
    remote_only: bool = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get jobs for a specific company"""
    query = select(Job).where(
        Job.company_name == company_name,
        Job.is_active == True
    )
    
    if remote_only:
        query = query.where(Job.remote_type == "full_remote")
    
    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return {"jobs": jobs, "company": company_name}