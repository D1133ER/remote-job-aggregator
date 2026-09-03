from celery import Celery
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User, JobAlert
from app.models.job import Job
from app.services.email import email_service
from sqlalchemy import select, or_
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Reuse the celery app from scraping_tasks
from app.tasks.scraping_tasks import celery_app


@celery_app.task(name="app.tasks.alert_tasks.check_and_send_alerts")
def check_and_send_alerts():
    """Check all active alerts and send notifications"""
    asyncio.run(_async_check_and_send_alerts())


async def _async_check_and_send_alerts():
    """Async implementation of alert checking"""
    async with AsyncSessionLocal() as session:
        # Get all active alerts
        result = await session.execute(
            select(JobAlert).where(JobAlert.is_active == True)
        )
        alerts = result.scalars().all()
        
        for alert in alerts:
            try:
                await process_alert(session, alert)
            except Exception as e:
                logger.error(f"Error processing alert {alert.id}: {str(e)}")


async def process_alert(session, alert: JobAlert):
    """Process a single alert and send email if matching jobs found"""
    # Build query based on alert criteria
    query = select(Job).where(Job.is_active == True)
    
    # Filter by keywords (search in title and description)
    if alert.keywords:
        keywords = alert.keywords.split(",")
        keyword_conditions = []
        for keyword in keywords:
            keyword = keyword.strip()
            if keyword:
                keyword_conditions.append(Job.title.ilike(f"%{keyword}%"))
                keyword_conditions.append(Job.description.ilike(f"%{keyword}%"))
        if keyword_conditions:
            query = query.where(or_(*keyword_conditions))
    
    # Filter by category
    if alert.category:
        query = query.where(Job.category == alert.category)
    
    # Filter by remote type
    if alert.remote_type:
        query = query.where(Job.remote_type == alert.remote_type)
    
    # Filter by location
    if alert.location:
        query = query.where(Job.location.ilike(f"%{alert.location}%"))
    
    # Filter by salary
    if alert.salary_min:
        query = query.where(Job.salary_min >= alert.salary_min)
    
    # Only jobs posted in the last 24 hours (for daily alerts) or 7 days (for weekly)
    if alert.frequency == "daily":
        cutoff = datetime.utcnow() - timedelta(hours=24)
    else:
        cutoff = datetime.utcnow() - timedelta(days=7)
    
    query = query.where(Job.created_at >= cutoff)
    
    # Get matching jobs
    result = await session.execute(query)
    jobs = result.scalars().all()
    
    if not jobs:
        logger.info(f"No new jobs for alert {alert.name}")
        return
    
    # Get user email
    user_result = await session.execute(
        select(User).where(User.id == alert.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user or not user.email:
        logger.warning(f"No user or email found for alert {alert.id}")
        return
    
    # Prepare job data for email
    job_data = []
    for job in jobs[:10]:  # Limit to 10 jobs per email
        job_data.append({
            "title": job.title,
            "company_name": job.company_name,
            "location": job.location or "Remote",
            "salary_display": job.salary_display or (f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}" if job.salary_min and job.salary_max else None),
            "skills": job.skills or [],
            "source_url": job.source_url
        })
    
    # Send email
    success = email_service.send_job_alert(
        to_email=user.email,
        alert_name=alert.name,
        jobs=job_data
    )
    
    if success:
        logger.info(f"Sent alert email to {user.email} for alert {alert.name}")
    else:
        logger.error(f"Failed to send alert email for {alert.name}")


@celery_app.task(name="app.tasks.alert_tasks.send_instant_alert")
def send_instant_alert(job_id: str):
    """Send instant alerts for a newly posted job"""
    asyncio.run(_async_send_instant_alert(job_id))


async def _async_send_instant_alert(job_id: str):
    """Send instant alerts for a specific job"""
    async with AsyncSessionLocal() as session:
        # Get the job
        job_result = await session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = job_result.scalar_one_or_none()
        
        if not job:
            return
        
        # Find matching alerts
        alerts_result = await session.execute(
            select(JobAlert).where(
                JobAlert.is_active == True,
                JobAlert.frequency == "instant"
            )
        )
        alerts = alerts_result.scalars().all()
        
        for alert in alerts:
            if matches_alert(job, alert):
                # Get user
                user_result = await session.execute(
                    select(User).where(User.id == alert.user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if user and user.email:
                    job_data = [{
                        "title": job.title,
                        "company_name": job.company_name,
                        "location": job.location or "Remote",
                        "salary_display": job.salary_display,
                        "skills": job.skills or [],
                        "source_url": job.source_url
                    }]
                    
                    email_service.send_job_alert(
                        to_email=user.email,
                        alert_name=f"Instant: {alert.name}",
                        jobs=job_data
                    )


def matches_alert(job: Job, alert: JobAlert) -> bool:
    """Check if a job matches an alert's criteria"""
    # Check keywords
    if alert.keywords:
        keywords = alert.keywords.split(",")
        job_text = f"{job.title} {job.description or ''}".lower()
        for keyword in keywords:
            if keyword.strip().lower() in job_text:
                break
        else:
            return False
    
    # Check category
    if alert.category and job.category != alert.category:
        return False
    
    # Check remote type
    if alert.remote_type and job.remote_type != alert.remote_type:
        return False
    
    # Check location
    if alert.location and alert.location.lower() not in (job.location or "").lower():
        return False
    
    # Check salary
    if alert.salary_min and job.salary_min and job.salary_min < alert.salary_min:
        return False
    
    return True