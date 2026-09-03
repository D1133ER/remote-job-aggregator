from typing import List, Dict, Any, Optional
from .base import BaseScraper
from datetime import datetime, timezone


class GreenhouseScraper(BaseScraper):
    """Scraper for Greenhouse ATS"""

    def __init__(self, company_tokens: Optional[List[str]] = None):
        super().__init__()
        self.source_name = "greenhouse"
        self.api_base = "https://boards-api.greenhouse.io/v1/boards"
        self.company_tokens = company_tokens or ["stripe"]

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        """Fetch jobs from Greenhouse API for all configured companies"""
        all_jobs = []
        for token in self.company_tokens:
            try:
                url = f"{self.api_base}/{token}/jobs"
                response = await self.fetch_url(url)
                jobs_data = response.json()

                for job in jobs_data.get("jobs", []):
                    parsed_job = self.parse_job(job, company_name=token.title())
                    if parsed_job:
                        all_jobs.append(parsed_job)
            except Exception:
                continue
        return all_jobs

    def parse_job(self, raw_job: Dict, company_name: str = "Unknown") -> Optional[Dict[str, Any]]:
        """Parse Greenhouse job data"""
        location = raw_job.get("location", {}).get("name", "")
        is_remote = "remote" in location.lower() or "anywhere" in location.lower()

        if not is_remote:
            return None

        description = raw_job.get("content", "")

        # Parse posted_at (ISO 8601)
        posted_at = None
        updated = raw_job.get("updated_at")
        if updated:
            try:
                posted_at = datetime.fromisoformat(str(updated).replace("Z", "+00:00"))
                if posted_at.tzinfo is None:
                    posted_at = posted_at.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass

        return {
            "title": raw_job.get("title"),
            "company_name": company_name,
            "description": description,
            "location": location,
            "remote_type": "full_remote",
            "source_url": raw_job.get("absolute_url"),
            "source_id": str(raw_job.get("id")),
            "posted_at": posted_at,
            "skills": self.extract_skills(description),
            "tags": self.extract_tags(raw_job.get("title", "")),
            "experience_level": self.extract_experience_level(raw_job.get("title", "")),
        }

    def extract_skills(self, description: str) -> List[str]:
        skills = []
        tech_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular",
            "vue", "node", "django", "flask", "fastapi", "aws", "azure",
            "gcp", "docker", "kubernetes", "sql", "postgresql", "mongodb",
            "redis", "elasticsearch", "graphql", "rest", "microservices",
            "ruby", "rails", "go", "golang", "rust", "php", "swift", "kotlin",
        ]
        description_lower = description.lower()
        for keyword in tech_keywords:
            if keyword in description_lower:
                skills.append(keyword)
        return skills

    def extract_tags(self, title: str) -> List[str]:
        tags = []
        title_lower = title.lower()
        if "senior" in title_lower:
            tags.append("senior")
        elif "junior" in title_lower:
            tags.append("junior")
        elif "lead" in title_lower or "principal" in title_lower:
            tags.append("lead")
        if "frontend" in title_lower or "front-end" in title_lower:
            tags.append("frontend")
        elif "backend" in title_lower or "back-end" in title_lower:
            tags.append("backend")
        elif "fullstack" in title_lower or "full-stack" in title_lower:
            tags.append("fullstack")
        return tags

    def extract_experience_level(self, title: str) -> str:
        title_lower = title.lower()
        if "senior" in title_lower or "sr" in title_lower:
            return "senior"
        elif "junior" in title_lower or "jr" in title_lower:
            return "junior"
        elif "lead" in title_lower or "principal" in title_lower or "staff" in title_lower:
            return "lead"
        return "mid"