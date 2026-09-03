from typing import List, Dict, Any
import asyncio
import logging
from .greenhouse import GreenhouseScraper
from .remotive import RemotiveScraper
from .weworkremotely import WeWorkRemotelyScraper

logger = logging.getLogger(__name__)

class ScraperManager:
    def __init__(self):
        self.scrapers = []
        self.register_scrapers()
    
    def register_scrapers(self):
        """Register all scrapers"""
        self.scrapers = [
            GreenhouseScraper(),
            RemotiveScraper(),
            WeWorkRemotelyScraper(),
        ]
    
    async def run_all_scrapers(self) -> List[Dict[str, Any]]:
        """Run all scrapers concurrently"""
        all_jobs = []
        
        tasks = []
        for scraper in self.scrapers:
            task = asyncio.create_task(self._run_scraper_safely(scraper))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraper failed: {result}")
        
        return all_jobs
    
    async def _run_scraper_safely(self, scraper) -> List[Dict[str, Any]]:
        """Run a single scraper with error handling"""
        try:
            jobs = await scraper.fetch_jobs()
            logger.info(f"{scraper.source_name}: Fetched {len(jobs)} jobs")
            return jobs
        except Exception as e:
            logger.error(f"Error in {scraper.source_name}: {str(e)}")
            raise
        finally:
            await scraper.close()