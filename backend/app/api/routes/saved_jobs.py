from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.user import User, SavedJob
from app.models.job import Job
from app.services.auth import get_current_user

router = APIRouter(prefix="/saved-jobs", tags=["saved-jobs"])


class SavedJobCreate(BaseModel):
    job_id: str
    notes: Optional[str] = None


class SavedJobResponse(BaseModel):
    id: str
    job_id: str
    notes: Optional[str]
    created_at: datetime
    job: Optional[dict] = None

    class Config:
        from_attributes = True


class SavedJobUpdate(BaseModel):
    notes: Optional[str] = None


def serialize_job(job: Job) -> Optional[dict]:
    if not job:
        return None
    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "company_logo_url": job.company_logo_url,
        "location": job.location,
        "remote_type": job.remote_type,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_display": job.salary_display,
        "summary": job.summary,
        "skills": job.skills,
        "experience_level": job.experience_level,
        "posted_at": job.posted_at.isoformat() if job.posted_at else None,
    }


@router.get("/", response_model=List[SavedJobResponse])
async def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all saved jobs for current user (single query with JOIN)"""
    result = await db.execute(
        select(SavedJob, Job)
        .join(Job, SavedJob.job_id == Job.id, isouter=True)
        .where(SavedJob.user_id == current_user.id)
    )
    rows = result.all()

    return [
        SavedJobResponse(
            id=saved_job.id,
            job_id=saved_job.job_id,
            notes=saved_job.notes,
            created_at=saved_job.created_at,
            job=serialize_job(job),
        )
        for saved_job, job in rows
    ]


@router.post("/", response_model=SavedJobResponse)
async def save_job(
    saved_job_data: SavedJobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a job"""
    job_result = await db.execute(
        select(Job).where(Job.id == saved_job_data.job_id)
    )
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    existing = await db.execute(
        select(SavedJob).where(
            SavedJob.user_id == current_user.id,
            SavedJob.job_id == saved_job_data.job_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already saved",
        )

    saved_job = SavedJob(
        user_id=current_user.id,
        job_id=saved_job_data.job_id,
        notes=saved_job_data.notes,
    )
    db.add(saved_job)
    await db.commit()
    await db.refresh(saved_job)

    return SavedJobResponse(
        id=saved_job.id,
        job_id=saved_job.job_id,
        notes=saved_job.notes,
        created_at=saved_job.created_at,
        job=serialize_job(job),
    )


@router.put("/{saved_job_id}", response_model=SavedJobResponse)
async def update_saved_job(
    saved_job_id: str,
    update_data: SavedJobUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update notes on a saved job"""
    result = await db.execute(
        select(SavedJob, Job)
        .join(Job, SavedJob.job_id == Job.id, isouter=True)
        .where(
            SavedJob.id == saved_job_id,
            SavedJob.user_id == current_user.id,
        )
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found",
        )

    saved_job, job = row

    if update_data.notes is not None:
        saved_job.notes = update_data.notes

    await db.commit()
    await db.refresh(saved_job)

    return SavedJobResponse(
        id=saved_job.id,
        job_id=saved_job.job_id,
        notes=saved_job.notes,
        created_at=saved_job.created_at,
        job=serialize_job(job),
    )


@router.delete("/{saved_job_id}")
async def unsave_job(
    saved_job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a job from saved jobs"""
    result = await db.execute(
        select(SavedJob).where(
            SavedJob.id == saved_job_id,
            SavedJob.user_id == current_user.id,
        )
    )
    saved_job = result.scalar_one_or_none()

    if not saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found",
        )

    await db.delete(saved_job)
    await db.commit()

    return {"status": "success", "message": "Job removed from saved"}