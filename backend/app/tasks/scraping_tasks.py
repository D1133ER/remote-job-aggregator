from celery import Celery
from app.core.config import settings
from app.core.metrics import inc, set_gauge
from app.scrapers.manager import ScraperManager
from app.services.ai_enrichment import AIEnrichmentService
from app.services.elasticsearch_service import ElasticsearchService
from app.core.database import AsyncSessionLocal
from app.models.job import Job
from sqlalchemy import select, text, asc, func, update
import asyncio
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

celery_app = Celery(
    "remote_job_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "scrape-jobs-every-hour": {
            "task": "app.tasks.scraping_tasks.scrape_all_jobs",
            "schedule": 3600.0,
        },
        "check-alerts-every-15-minutes": {
            "task": "app.tasks.alert_tasks.check_and_send_alerts",
            "schedule": 900.0,
        },
        "retire-expired-jobs-daily": {
            "task": "app.tasks.scraping_tasks.retire_expired_jobs",
            "schedule": 86400.0,
        },
    },
)


def _run_async(coro):
    """Run an async coroutine in a fresh event loop (for Celery sync workers)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.scraping_tasks.scrape_all_jobs")
def scrape_all_jobs():
    _run_async(_async_scrape_all_jobs())


async def _async_scrape_all_jobs():
    inc("scrape_runs_total")
    set_gauge("scrape_runs_active", 1)
    manager = ScraperManager()
    enrichment = AIEnrichmentService(settings.OPENAI_API_KEY)
    search_service = ElasticsearchService(settings.ELASTICSEARCH_URL)

    per_source = {"scrapers": {}}
    try:
        jobs = await manager.run_all_scrapers()
        logger.info(f"Fetched {len(jobs)} jobs from all sources")

        # Per-source metrics (jobs carry their source_name from the manager).
        source_counts = {}
        for job in jobs:
            source = job.get("source_name", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        for source, count in source_counts.items():
            inc("scrape_jobs_fetched_total", {"source": source}, value=count)

        new_job_ids = []
        async with AsyncSessionLocal() as session:
            for job_data in jobs:
                job_data = await enrichment.enrich_job(job_data)

                result = await session.execute(
                    select(Job).where(Job.source_url == job_data.get("source_url"))
                )
                existing_job = result.scalar_one_or_none()

                if existing_job:
                    for key, value in job_data.items():
                        if value is not None and hasattr(existing_job, key):
                            setattr(existing_job, key, value)
                    existing_job.updated_at = datetime.now(timezone.utc)
                    job_data["id"] = existing_job.id
                else:
                    new_job = Job(**job_data)
                    session.add(new_job)
                    await session.flush()
                    new_job_ids.append(new_job.id)
                    job_data["id"] = new_job.id

            await session.commit()
            logger.info("Job database updated successfully")

        for job_data in jobs:
            try:
                search_service.index_job(job_data)
            except Exception as e:
                logger.error(f"Failed to index job {job_data.get('id')}: {e}")

        from app.tasks.alert_tasks import send_instant_alert

        for job_id in new_job_ids:
            send_instant_alert.delay(job_id)

        # Expose current active-job count for monitoring.
        async with AsyncSessionLocal() as session:
            total = (
                await session.execute(select(func.count()).select_from(Job).where(Job.is_active == True))
            ).scalar_one()
            set_gauge("jobs_total_db", total)

    except Exception as e:
        inc("scrape_errors_total", {"source": "all"})
        logger.error(f"Scraping task failed: {str(e)}")
        raise
    finally:
        set_gauge("scrape_runs_active", 0)


@celery_app.task(name="app.tasks.scraping_tasks.retire_expired_jobs")
def retire_expired_jobs(max_age_days: int = 90):
    """Data retention: deactivate postings older than max_age_days or past expires_at.

    This keeps the feed healthy and bounds table growth. Old jobs are flagged
    is_active=False (soft-delete) so they drop out of queries/search while
    history and foreign keys remain intact. A hard purge can be layered on top
    later if disk usage demands it.
    """
    _run_async(_async_retire_expired_jobs(max_age_days))


async def _async_retire_expired_jobs(max_age_days: int):
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    async with AsyncSessionLocal() as session:
        # 1) Any posting that explicitly expired.
        await session.execute(
            update(Job)
            .where(Job.expires_at.is_not(None), Job.expires_at < datetime.now(timezone.utc))
            .values(is_active=False, updated_at=datetime.now(timezone.utc))
        )
        # 2) Any active posting older than the retention window.
        result = await session.execute(
            update(Job)
            .where(
                Job.is_active == True,
                Job.expires_at.is_(None),
                Job.posted_at.is_not(None),
                Job.posted_at < cutoff,
            )
            .values(is_active=False, updated_at=datetime.now(timezone.utc))
        )
        await session.commit()
        logger.info("Retired expired/old jobs: %s", result.rowcount)


@celery_app.task(name="app.tasks.scraping_tasks.deduplicate_jobs")
def deduplicate_jobs():
    _run_async(_async_deduplicate_jobs())


async def _async_deduplicate_jobs():
    async with AsyncSessionLocal() as session:
        query = """
        SELECT title, company_name, COUNT(*)
        FROM jobs
        WHERE is_active = true
        GROUP BY title, company_name
        HAVING COUNT(*) > 1
        """

        result = await session.execute(text(query))
        duplicates = result.fetchall()

        for dup in duplicates:
            title, company, count = dup
            result = await session.execute(
                select(Job)
                .where(Job.title == title, Job.company_name == company)
                .order_by(asc(Job.created_at))
            )
            jobs = result.scalars().all()

            for job in jobs[1:]:
                await session.delete(job)

        await session.commit()