from typing import List, Dict, Any
import asyncio
import logging
from .greenhouse import GreenhouseScraper
from .lever import LeverScraper
from .remotive import RemotiveScraper
from .weworkremotely import WeWorkRemotelyScraper
from .workable import WorkableScraper
from .remoteok import RemoteOKScraper
from .arbeitnow import ArbeitnowScraper
from .jobicy import JobicyScraper
from app.core.config import settings

logger = logging.getLogger(__name__)


class ScraperManager:
    def __init__(self):
        self.scrapers = []
        self.register_scrapers()

    def register_scrapers(self):
        """Register all scrapers"""

        def _parse_tokens(raw: str) -> List[str]:
            if raw and raw.strip():
                return [t.strip() for t in raw.split(",") if t.strip()]
            return []

        greenhouse_tokens = _parse_tokens(settings.GREENHOUSE_COMPANY_TOKENS)
        lever_tokens = _parse_tokens(settings.LEVER_COMPANY_TOKENS)
        workable_tokens = _parse_tokens(settings.WORKABLE_COMPANY_TOKENS)

        self.scrapers = [
            # Real job boards (no config needed — thousands of real remote jobs)
            RemotiveScraper(),
            RemoteOKScraper(),
            ArbeitnowScraper(),
            JobicyScraper(),
            WeWorkRemotelyScraper(),
            # ATS scrapers (configurable company lists)
            GreenhouseScraper(company_tokens=greenhouse_tokens),
            LeverScraper(companies=lever_tokens),
            WorkableScraper(companies=workable_tokens),
        ]

    async def run_all_scrapers(self) -> List[Dict[str, Any]]:
        """Run all scrapers concurrently"""
        all_jobs = []

        tasks = [asyncio.create_task(self._run_scraper_safely(s)) for s in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                logger.error("Scraper failed: %s", result)

        logger.info("Total jobs fetched: %d", len(all_jobs))
        return all_jobs

    async def _run_scraper_safely(self, scraper) -> List[Dict[str, Any]]:
        try:
            jobs = await scraper.fetch_jobs()
            # Ensure every job carries the source name and matches the schema
            for job in jobs:
                job["source_name"] = scraper.source_name
                job.setdefault("remote_type", "full_remote")
                job.setdefault("job_type", "full_time")
            logger.info("%s: Fetched %d jobs", scraper.source_name, len(jobs))
            return jobs
        except Exception as e:
            logger.error("Error in %s: %s", scraper.source_name, str(e))
            return []
        finally:
            await scraper.close()