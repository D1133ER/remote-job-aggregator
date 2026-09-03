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
    db: AsyncSession = Depends(get_db),
):
    query = select(Company)

    if industry:
        query = query.where(Company.industry == industry)

    if remote_policy:
        query = query.where(Company.remote_policy == remote_policy)

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    companies = result.scalars().all()

    return companies


@router.get("/{company_name}", response_model=CompanyResponse)
async def get_company(
    company_name: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.name == company_name)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


@router.get("/{company_name}/stats", response_model=CompanyStats)
async def get_company_stats(
    company_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get company statistics using SQL aggregation"""
    base_filter = (Job.company_name == company_name, Job.is_active == True)

    # Total and remote counts in one query
    counts_result = await db.execute(
        select(
            func.count(Job.id).label("total_jobs"),
            func.count(Job.id).filter(Job.remote_type == "full_remote").label("remote_jobs"),
            func.avg(Job.salary_min).label("avg_salary_min"),
            func.avg(Job.salary_max).label("avg_salary_max"),
        ).where(*base_filter)
    )
    row = counts_result.one()

    if row.total_jobs == 0:
        raise HTTPException(status_code=404, detail="No jobs found for this company")

    # Get skills from the JSON column — fetch only the skills column
    skills_result = await db.execute(
        select(Job.skills).where(*base_filter).where(Job.skills.isnot(None))
    )
    all_skills = []
    for (skills_list,) in skills_result:
        if isinstance(skills_list, list):
            all_skills.extend(skills_list)

    skill_counts: dict = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    top_skills = sorted(skill_counts, key=lambda x: skill_counts[x], reverse=True)[:10]

    # Categories
    cat_result = await db.execute(
        select(Job.category).where(*base_filter).where(Job.category.isnot(None)).distinct()
    )
    categories = [cat for (cat,) in cat_result]

    return CompanyStats(
        total_jobs=row.total_jobs,
        remote_jobs=row.remote_jobs,
        average_salary_min=round(row.avg_salary_min, 2) if row.avg_salary_min else None,
        average_salary_max=round(row.avg_salary_max, 2) if row.avg_salary_max else None,
        top_skills=top_skills,
        categories=categories,
    )


@router.get("/{company_name}/jobs")
async def get_company_jobs(
    company_name: str,
    remote_only: bool = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Job).where(
        Job.company_name == company_name,
        Job.is_active == True,
    )

    if remote_only:
        query = query.where(Job.remote_type == "full_remote")

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return {"jobs": jobs, "company": company_name}