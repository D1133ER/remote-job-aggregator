"""One-time script to run a scraping session without Celery"""
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select
from app.scrapers.manager import ScraperManager
from app.services.ai_enrichment import AIEnrichmentService
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.job import Job
from app.core.config import settings
from datetime import datetime


async def run_scrape():
    """Run a one-time scraping session"""
    logging.basicConfig(level=logging.INFO)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    manager = ScraperManager()
    enrichment = AIEnrichmentService(settings.OPENAI_API_KEY)
    
    print("🚀 Starting scraping session...")
    
    # Fetch jobs
    jobs = await manager.run_all_scrapers()
    print(f"📊 Fetched {len(jobs)} jobs total")
    
    # Process jobs
    async with AsyncSessionLocal() as session:
        new_count = 0
        updated_count = 0
        
        for job_data in jobs:
            # Enrich with AI (will skip if no API key)
            job_data = await enrichment.enrich_job(job_data)
            
            # Check if job exists
            existing_job = await session.execute(
                select(Job).where(
                    Job.source_url == job_data.get('source_url')
                )
            )
            existing = existing_job.scalar_one_or_none()
            
            if existing:
                for key, value in job_data.items():
                    if value is not None and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                new_job = Job(**job_data)
                session.add(new_job)
                new_count += 1
        
        await session.commit()
    
    print(f"✅ New jobs: {new_count}")
    print(f"🔄 Updated jobs: {updated_count}")


if __name__ == "__main__":
    asyncio.run(run_scrape())