from typing import List, Dict, Any, Optional
from .base import BaseScraper
import logging
import json

logger = logging.getLogger(__name__)


class WorkableScraper(BaseScraper):
    """Scraper for Workable ATS — configurable for multiple companies."""

    def __init__(self, companies: List[str] = None):
        super().__init__()
        self.source_name = "workable"
        self.companies = companies or []

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        if not self.companies:
            logger.info("Workable: No companies configured, skipping")
            return []

        all_jobs = []
        for company in self.companies:
            try:
                # Workable public widget API — returns JSON with a jobs array
                url = (
                    f"https://apply.workable.com/api/v1/widget/accounts/"
                    f"{company}/jobs?b=100&l=&p=0"
                )
                response = await self.fetch_url(url)
                data = response.json()

                remote_count = 0
                for job in data.get("jobs", []):
                    parsed = self.parse_job(job, company)
                    if parsed:
                        all_jobs.append(parsed)
                        remote_count += 1

                logger.info("Workable [%s]: Fetched %d remote jobs", company, remote_count)
            except Exception as e:
                logger.warning("Workable [%s]: %s", company, e)

        return all_jobs

    def parse_job(self, raw_job: Dict, company: str = "") -> Optional[Dict[str, Any]]:
        title = raw_job.get("title", "")
        location = raw_job.get("location", "")
        is_remote = raw_job.get("remote", False) or "remote" in location.lower()

        if not is_remote:
            return None

        description = raw_job.get("description", "") or raw_job.get("description_text", "") or ""
        department = raw_job.get("department", "")

        posted_at = None
        created = raw_job.get("created")
        if created:
            try:
                from datetime import datetime, timezone
                if isinstance(created, (int, float)):
                    posted_at = datetime.fromtimestamp(created, tz=timezone.utc)
                else:
                    posted_at = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
            except (ValueError, TypeError, OSError):
                pass

        return {
            "title": title,
            "company_name": company.title(),
            "description": description,
            "location": location,
            "remote_type": "full_remote",
            "source_url": f"https://{company}.workable.com/jobs/{raw_job.get('shortcode', '')}",
            "source_id": str(raw_job.get("shortcode", "")),
            "posted_at": posted_at,
            "skills": self.extract_skills(description),
            "tags": self.extract_tags(title, department),
            "salary_min": None,
            "salary_max": None,
            "category": department or self._categorize(title),
            "job_type": self._map_job_type(raw_job.get("employment_type", "")),
            "experience_level": self._extract_experience(title),
        }

    def _map_job_type(self, employment_type: str) -> str:
        t = employment_type.lower()
        if "full" in t:
            return "full_time"
        if "part" in t:
            return "part_time"
        if "contract" in t or "freelance" in t:
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
        if any(kw in t for kw in ["frontend", "backend", "fullstack", "engineer", "developer"]):
            return "Software Development"
        if "design" in t:
            return "Design"
        if "data" in t:
            return "Data Science"
        return "Software Development"

    def extract_skills(self, description: str) -> List[str]:
        skills = []
        tech_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular",
            "vue", "node", "django", "flask", "fastapi", "aws", "azure",
            "gcp", "docker", "kubernetes", "sql", "postgresql", "mongodb",
            "redis", "elasticsearch", "graphql", "rest", "microservices",
            "ruby", "rails", "go", "golang", "rust", "php", "swift", "kotlin",
        ]
        d = description.lower()
        for kw in tech_keywords:
            if kw in d:
                skills.append(kw)
        return skills

    def extract_tags(self, title: str, department: str) -> List[str]:
        tags = []
        t = title.lower()
        if "frontend" in t or "front-end" in t:
            tags.append("frontend")
        elif "backend" in t or "back-end" in t:
            tags.append("backend")
        elif "fullstack" in t or "full-stack" in t:
            tags.append("fullstack")
        if department:
            tags.append(department.lower())
        return tags
