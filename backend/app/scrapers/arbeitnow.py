from typing import List, Dict, Any, Optional
from .base import BaseScraper
from datetime import datetime, timezone


class ArbeitnowScraper(BaseScraper):
    """Scraper for Arbeitnow — 10k+ remote-friendly jobs."""

    def __init__(self):
        super().__init__()
        self.source_name = "arbeitnow"
        self.api_url = "https://www.arbeitnow.com/api/job-board-api"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        all_jobs = []
        page = 1

        while True:
            response = await self.fetch_url(f"{self.api_url}?page={page}")
            data = response.json()

            jobs = data.get("data", [])
            if not jobs:
                break

            for job in jobs:
                parsed = self.parse_job(job)
                if parsed:
                    all_jobs.append(parsed)

            # Check pagination
            if not data.get("links", {}).get("next"):
                break

            page += 1
            if page > 10:  # Safety limit
                break

        return all_jobs

    def parse_job(self, raw_job: Dict) -> Optional[Dict[str, Any]]:
        remote = raw_job.get("remote", False)
        if not remote:
            return None

        description = raw_job.get("description", "") or ""
        tags = raw_job.get("tags", []) or []

        # Parse posted_at (Unix epoch timestamp)
        posted_at = None
        created_at = raw_job.get("created_at")
        if created_at:
            try:
                posted_at = datetime.fromtimestamp(int(created_at), tz=timezone.utc)
            except (ValueError, TypeError, OSError):
                pass

        return {
            "title": raw_job.get("title", "Unknown Title"),
            "company_name": raw_job.get("company_name", "Unknown"),
            "company_logo_url": raw_job.get("company_logo"),
            "company_website": raw_job.get("url"),
            "description": description,
            "location": raw_job.get("location", "Remote"),
            "remote_type": "full_remote",
            "source_url": raw_job.get("url", ""),
            "apply_url": raw_job.get("url", ""),
            "source_id": raw_job.get("slug", ""),
            "posted_at": posted_at,
            "salary_min": None,
            "salary_max": None,
            "skills": self.extract_skills(description, tags),
            "tags": tags,
            "category": self._categorize(tags),
            "job_type": "full_time",
            "experience_level": self._extract_experience(raw_job.get("title", "")),
        }

    def extract_skills(self, description: str, tags: List[str]) -> List[str]:
        # Prefer tags if they look like tech skills
        tech_tags = []
        tech_keywords = {
            "python", "java", "javascript", "typescript", "react", "angular",
            "vue", "node", "django", "flask", "fastapi", "aws", "azure",
            "gcp", "docker", "kubernetes", "sql", "postgresql", "mongodb",
            "redis", "elasticsearch", "graphql", "rest", "microservices",
            "ruby", "rails", "go", "golang", "rust", "php", "swift", "kotlin",
            "terraform", "ansible", "jenkins", "git", "linux", "css", "html",
            "nextjs", "svelte", "flutter", "react native",
        }

        for tag in tags:
            if tag.lower() in tech_keywords:
                tech_tags.append(tag)

        if tech_tags:
            return tech_tags

        # Fallback: extract from description
        skills = []
        desc_lower = description.lower()
        for kw in tech_keywords:
            if kw in desc_lower:
                skills.append(kw)
        return skills

    def _categorize(self, tags: List[str]) -> str:
        tag_set = {t.lower() for t in tags}
        if tag_set & {"engineering", "backend", "frontend", "fullstack", "devops", "software"}:
            return "Software Development"
        if tag_set & {"design", "ui", "ux"}:
            return "Design"
        if tag_set & {"marketing", "growth"}:
            return "Marketing"
        if tag_set & {"data", "data-science", "machine-learning"}:
            return "Data Science"
        if tag_set & {"support", "customer-success"}:
            return "Customer Support"
        if tag_set & {"sales", "business"}:
            return "Sales"
        return "Software Development"

    def _extract_experience(self, title: str) -> str:
        title_lower = title.lower()
        if "senior" in title_lower or "sr" in title_lower:
            return "senior"
        if "junior" in title_lower or "jr" in title_lower:
            return "junior"
        if "lead" in title_lower or "principal" in title_lower or "staff" in title_lower:
            return "lead"
        return "mid"
