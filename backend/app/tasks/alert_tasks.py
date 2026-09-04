from celery import Celery
from app.core.config import settings
from app.core.metrics import inc
from app.core.database import AsyncSessionLocal
from app.models.user import User, JobAlert
from app.models.job import Job
from app.services.email import email_service
from sqlalchemy import select, or_
import asyncio
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

from app.tasks.scraping_tasks import celery_app, _run_async


@celery_app.task(name="app.tasks.alert_tasks.check_and_send_alerts")
def check_and_send_alerts():
    _run_async(_async_check_and_send_alerts())


async def _async_check_and_send_alerts():
    async with AsyncSessionLocal() as session:
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
    query = select(Job).where(Job.is_active == True)

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

    if alert.category:
        query = query.where(Job.category == alert.category)

    if alert.remote_type:
        query = query.where(Job.remote_type == alert.remote_type)

    if alert.location:
        query = query.where(Job.location.ilike(f"%{alert.location}%"))

    if alert.salary_min:
        query = query.where(Job.salary_min >= alert.salary_min)

    now = datetime.now(timezone.utc)
    if alert.frequency == "daily":
        cutoff = now - timedelta(hours=24)
    else:
        cutoff = now - timedelta(days=7)

    query = query.where(Job.created_at >= cutoff)

    result = await session.execute(query)
    jobs = result.scalars().all()

    if not jobs:
        return

    user_result = await session.execute(
        select(User).where(User.id == alert.user_id)
    )
    user = user_result.scalar_one_or_none()

    if not user or not user.email:
        return

    job_data = []
    for job in jobs[:10]:
        salary_display = job.salary_display
        if not salary_display and job.salary_min and job.salary_max:
            salary_display = f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}"
        job_data.append({
            "title": job.title,
            "company_name": job.company_name,
            "location": job.location or "Remote",
            "salary_display": salary_display,
            "skills": job.skills or [],
            "source_url": job.source_url,
        })

    success = email_service.send_job_alert(
        to_email=user.email,
        alert_name=alert.name,
        jobs=job_data,
    )

    if success:
        inc("alerts_sent_total", {"type": "scheduled"})
        logger.info(f"Sent alert email to {user.email} for alert {alert.name}")


@celery_app.task(name="app.tasks.alert_tasks.send_instant_alert")
def send_instant_alert(job_id: str):
    _run_async(_async_send_instant_alert(job_id))


async def _async_send_instant_alert(job_id: str):
    async with AsyncSessionLocal() as session:
        job_result = await session.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()

        if not job:
            return

        alerts_result = await session.execute(
            select(JobAlert).where(
                JobAlert.is_active == True,
                JobAlert.frequency == "instant",
            )
        )
        alerts = alerts_result.scalars().all()

        for alert in alerts:
            if matches_alert(job, alert):
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
                        "source_url": job.source_url,
                    }]
                    email_service.send_job_alert(
                        to_email=user.email,
                        alert_name=f"Instant: {alert.name}",
                        jobs=job_data,
                    )
                    inc("alerts_sent_total", {"type": "instant"})


def matches_alert(job: Job, alert: JobAlert) -> bool:
    if alert.keywords:
        keywords = alert.keywords.split(",")
        job_text = f"{job.title} {job.description or ''}".lower()
        for keyword in keywords:
            if keyword.strip().lower() in job_text:
                break
        else:
            return False

    if alert.category and job.category != alert.category:
        return False

    if alert.remote_type and job.remote_type != alert.remote_type:
        return False

    if alert.location and alert.location.lower() not in (job.location or "").lower():
        return False

    if alert.salary_min and job.salary_min and job.salary_min < alert.salary_min:
        return False

    return True