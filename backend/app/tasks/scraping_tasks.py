from celery import Celery
from app.core.config import settings
from app.scrapers.manager import ScraperManager
from app.services.ai_enrichment import AIEnrichmentService
from app.services.elasticsearch_service import ElasticsearchService
from app.core.database import AsyncSessionLocal
from app.models.job import Job
from sqlalchemy import select, text, asc
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

celery_app = Celery(
    "remote_job_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'scrape-jobs-every-hour': {
            'task': 'app.tasks.scraping_tasks.scrape_all_jobs',
            'schedule': 3600.0,  # Every hour
        },
        'check-alerts-every-15-minutes': {
            'task': 'app.tasks.alert_tasks.check_and_send_alerts',
            'schedule': 900.0,  # Every 15 minutes
        },
    }
)

@celery_app.task(name="app.tasks.scraping_tasks.scrape_all_jobs")
def scrape_all_jobs():
    """Main task to scrape all jobs"""
    asyncio.run(_async_scrape_all_jobs())

async def _async_scrape_all_jobs():
    """Async implementation of job scraping"""
    manager = ScraperManager()
    enrichment = AIEnrichmentService(settings.OPENAI_API_KEY)
    search = ElasticsearchService(settings.ELASTICSEARCH_URL)
    
    try:
        # Fetch all jobs
        jobs = await manager.run_all_scrapers()
        logger.info(f"Fetched {len(jobs)} jobs from all sources")
        
        # Process jobs
        new_job_ids = []
        async with AsyncSessionLocal() as session:
            for job_data in jobs:
                # Enrich with AI
                job_data = await enrichment.enrich_job(job_data)
                
                # Check if job exists
                result = await session.execute(
                    select(Job).where(Job.source_url == job_data.get('source_url'))
                )
                existing_job = result.scalar_one_or_none()
                
                if existing_job:
                    # Update existing job
                    for key, value in job_data.items():
                        if value is not None and hasattr(existing_job, key):
                            setattr(existing_job, key, value)
                    existing_job.updated_at = datetime.utcnow()
                    job_data['id'] = existing_job.id
                else:
                    # Create new job
                    new_job = Job(**job_data)
                    session.add(new_job)
                    await session.flush()  # Get the ID
                    new_job_ids.append(new_job.id)
                    job_data['id'] = new_job.id
            
            await session.commit()
            logger.info("Job database updated successfully")

        for job_data in jobs:
            try:
                search.index_job(job_data)
            except Exception as e:
                logger.error(f"Failed to index job {job_data.get('id')}: {e}")
        
        # Trigger instant alerts for new jobs
        from app.tasks.alert_tasks import send_instant_alert
        for job_id in new_job_ids:
            send_instant_alert.delay(job_id)
            
    except Exception as e:
        logger.error(f"Scraping task failed: {str(e)}")
        raise

@celery_app.task(name="app.tasks.scraping_tasks.deduplicate_jobs")
def deduplicate_jobs():
    """Deduplicate jobs in database"""
    asyncio.run(_async_deduplicate_jobs())

async def _async_deduplicate_jobs():
    """Remove duplicate jobs"""
    async with AsyncSessionLocal() as session:
        # Find duplicates based on title + company
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
            # Keep the oldest job, delete others
            result = await session.execute(
                select(Job).where(
                    Job.title == title,
                    Job.company_name == company
                ).order_by(asc(Job.created_at))
            )
            jobs = result.scalars().all()
            
            for job in jobs[1:]:  # Keep first job, delete rest
                await session.delete(job)
        
        await session.commit()