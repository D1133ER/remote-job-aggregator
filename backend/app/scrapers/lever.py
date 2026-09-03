from typing import List, Dict, Any, Optional
from .base import BaseScraper
import logging

logger = logging.getLogger(__name__)


class LeverScraper(BaseScraper):
    """Scraper for Lever ATS — configurable for multiple companies."""

    def __init__(self, companies: List[str] = None):
        super().__init__()
        self.source_name = "lever"
        self.api_base = "https://api.lever.co/v0"
        self.companies = companies or ["lever"]

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        all_jobs = []
        for company in self.companies:
            try:
                url = f"{self.api_base}/postings/{company}?mode=json"
                response = await self.fetch_url(url)
                jobs_data = response.json()

                for job in jobs_data:
                    parsed = self.parse_job(job, company)
                    if parsed:
                        all_jobs.append(parsed)

                logger.info("Lever [%s]: Fetched %d remote jobs", company, len(jobs_data))
            except Exception as e:
                logger.warning("Lever [%s]: %s", company, e)
        return all_jobs

    def parse_job(self, raw_job: Dict, company: str = "") -> Optional[Dict[str, Any]]:
        categories = raw_job.get("categories", {})
        location = categories.get("location", "")
        is_remote = "remote" in location.lower() or "anywhere" in location.lower()

        if not is_remote:
            return None

        description = raw_job.get("descriptionPlain", "") or raw_job.get("description", "") or ""

        posted_at = None
        created_at = raw_job.get("createdAt")
        if created_at:
            try:
                from datetime import datetime, timezone
                posted_at = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
            except (ValueError, TypeError, OSError):
                pass

        return {
            "title": raw_job.get("text", "Unknown Title"),
            "company_name": raw_job.get("company", company.title()),
            "description": description,
            "location": location,
            "remote_type": "full_remote",
            "source_url": raw_job.get("hostedUrl", ""),
            "source_id": str(raw_job.get("id", "")),
            "posted_at": posted_at,
            "skills": self.extract_skills(description),
            "tags": self.extract_tags(raw_job.get("text", "")),
            "salary_min": None,
            "salary_max": None,
            "category": self._categorize(raw_job.get("text", "")),
            "job_type": self._map_job_type(categories.get("commitment", "")),
            "experience_level": self._extract_experience(raw_job.get("text", "")),
        }

    def _map_job_type(self, commitment: str) -> str:
        c = commitment.lower()
        if "full" in c:
            return "full_time"
        if "part" in c:
            return "part_time"
        if "contract" in c or "freelance" in c:
            return "contract"
        return "full_time"

    def _extract_experience(self, title: str) -> str:
        t = title.lower()
        if "senior" in t or "sr " in t:
            return "senior"
        if "junior" in t or "jr " in t:
            return "junior"
        if "lead" in t or "principal" in t or "staff" in t:
            return "lead"
        return "mid"

    def _categorize(self, title: str) -> str:
        t = title.lower()
        if any(kw in t for kw in ["frontend", "backend", "fullstack", "full-stack", "engineer", "developer"]):
            return "Software Development"
        if "design" in t:
            return "Design"
        if "data" in t:
            return "Data Science"
        if "marketing" in t:
            return "Marketing"
        return "Software Development"

    def extract_skills(self, description: str) -> List[str]:
        skills = []
        tech_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular",
            "vue", "node", "django", "flask", "fastapi", "aws", "azure",
            "gcp", "docker", "kubernetes", "sql", "postgresql", "mongodb",
            "redis", "elasticsearch", "graphql", "rest", "microservices",
            "ruby", "rails", "go", "golang", "rust", "php", "swift", "kotlin",
            "terraform", "ansible", "jenkins", "git", "linux",
        ]
        d = description.lower()
        for kw in tech_keywords:
            if kw in d:
                skills.append(kw)
        return skills

    def extract_tags(self, title: str) -> List[str]:
        tags = []
        t = title.lower()
        if "frontend" in t or "front-end" in t:
            tags.append("frontend")
        elif "backend" in t or "back-end" in t:
            tags.append("backend")
        elif "fullstack" in t or "full-stack" in t:
            tags.append("fullstack")
        elif "devops" in t:
            tags.append("devops")
        elif "data" in t:
            tags.append("data")
        elif "mobile" in t:
            tags.append("mobile")
        return tags
