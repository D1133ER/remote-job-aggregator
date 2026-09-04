from abc import ABC, abstractmethod
from typing import List, Dict, Any
import httpx
import logging
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    def __init__(self):
        self.source_name = "base"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RemoteJobBot/1.0; +https://yourdomain.com/bot)"
        }
        self.client = httpx.AsyncClient(timeout=30, headers=self.headers)

    @abstractmethod
    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def parse_job(self, raw_data: Dict) -> Dict[str, Any]:
        pass

    def normalize_job(self, job: Dict) -> Dict[str, Any]:
        return {
            "title": job.get("title"),
            "company_name": job.get("company_name"),
            "description": job.get("description"),
            "location": job.get("location", "Remote"),
            "remote_type": job.get("remote_type", "full_remote"),
            "source_url": job.get("source_url"),
            "apply_url": job.get("apply_url") or job.get("source_url"),
            "source_name": self.source_name,
            "posted_at": job.get("posted_at", datetime.now(timezone.utc)),
            "skills": job.get("skills", []),
            "tags": job.get("tags", []),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_url(self, url: str) -> httpx.Response:
        response = await self.client.get(url)
        response.raise_for_status()
        return response

    async def close(self):
        await self.client.aclose()