from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.job import Job
from sqlalchemy import select, and_, or_, func, desc
from app.models.user import User, HiddenJob
from app.services.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/")
async def get_jobs(
    category: Optional[str] = None,
    remote_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    location: Optional[str] = None,
    salary_min: Optional[float] = None,
    skills: Optional[List[str]] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get jobs with filters"""
    query = select(Job).where(Job.is_active == True).order_by(desc(Job.posted_at), desc(Job.created_at))
    
    # Apply filters
    if category:
        query = query.where(Job.category == category)
    
    if remote_type:
        query = query.where(Job.remote_type == remote_type)
    
    if experience_level:
        query = query.where(Job.experience_level == experience_level)
    
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    
    if salary_min:
        query = query.where(Job.salary_min >= salary_min)
    
    if skills:
        # Check if any of the skills match
        skill_conditions = []
        for skill in skills:
            skill_conditions.append(Job.skills.contains([skill]))
        query = query.where(or_(*skill_conditions))

    if q:
        search_term = f"%{q}%"
        query = query.where(or_(
            Job.title.ilike(search_term),
            Job.company_name.ilike(search_term),
            Job.description.ilike(search_term)
        ))

    if current_user:
        hidden_job_ids = select(HiddenJob.job_id).where(HiddenJob.user_id == current_user.id)
        query = query.where(~Job.id.in_(hidden_job_ids))

    total_result = await db.execute(
        select(func.count()).select_from(query.order_by(None).subquery())
    )
    total = total_result.scalar_one()
    
    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return {"jobs": jobs, "page": page, "limit": limit, "total": total}

@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific job by ID"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.is_active == True)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.post("/{job_id}/hide")
async def hide_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Hide a job for the authenticated user."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = await db.execute(select(HiddenJob).where(
        HiddenJob.user_id == current_user.id,
        HiddenJob.job_id == job_id
    ))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job already hidden")

    db.add(HiddenJob(user_id=current_user.id, job_id=job_id))
    return {"status": "success", "message": "Job hidden"}