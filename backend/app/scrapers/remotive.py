from typing import List, Dict, Any
from datetime import datetime, timezone
from .base import BaseScraper


class RemotiveScraper(BaseScraper):
    """Scraper for Remotive API"""

    def __init__(self):
        super().__init__()
        self.source_name = "remotive"
        self.api_url = "https://remotive.com/api/remote-jobs"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        response = await self.fetch_url(self.api_url)
        jobs_data = response.json()

        parsed_jobs = []
        for job in jobs_data.get("jobs", []):
            parsed_job = self.parse_job(job)
            if parsed_job:
                parsed_jobs.append(parsed_job)

        return parsed_jobs

    def parse_job(self, raw_job: Dict) -> Dict[str, Any]:
        description = raw_job.get("description", "") or ""

        # Remotive's publication_date is an ISO-8601 string — coerce to a
        # timezone-aware datetime so asyncpg can persist it.
        posted_at = None
        publication_date = raw_job.get("publication_date")
        if publication_date:
            try:
                posted_at = datetime.fromisoformat(str(publication_date).replace("Z", "+00:00"))
                if posted_at.tzinfo is None:
                    posted_at = posted_at.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass

        return {
            "title": raw_job.get("title"),
            "company_name": raw_job.get("company_name"),
            "company_logo_url": raw_job.get("company_logo_url"),
            "description": description,
            "location": raw_job.get("candidate_required_location", "Remote"),
            "remote_type": "full_remote",
            "source_url": raw_job.get("url"),
            "apply_url": raw_job.get("url"),
            "source_id": str(raw_job.get("id")),
            "posted_at": posted_at,
            "salary_min": self._parse_salary(raw_job.get("salary"), "min"),
            "salary_max": self._parse_salary(raw_job.get("salary"), "max"),
            "skills": self.extract_skills(description),
            "tags": raw_job.get("tags", []),
            "category": raw_job.get("category"),
        }

    def _parse_salary(self, salary_str: str, sal_type: str):
        if not salary_str:
            return None
        try:
            import re
            numbers = re.findall(r'[\d,]+[kK]?', salary_str)
            parsed = []
            for n in numbers:
                n_clean = n.replace(",", "")
                if n_clean.lower().endswith("k"):
                    parsed.append(int(float(n_clean[:-1]) * 1000))
                else:
                    parsed.append(int(n_clean))
            if sal_type == "min" and parsed:
                return float(parsed[0])
            elif sal_type == "max" and len(parsed) > 1:
                return float(parsed[1])
        except (ValueError, TypeError):
            pass
        return None

    def extract_skills(self, description: str) -> List[str]:
        skills = []
        tech_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular",
            "vue", "node", "django", "flask", "fastapi", "aws", "azure",
            "gcp", "docker", "kubernetes", "sql", "postgresql", "mongodb",
            "redis", "elasticsearch", "graphql", "rest", "microservices",
            "ruby", "rails", "go", "golang", "rust", "php", "swift", "kotlin",
            "terraform", "ansible", "jenkins", "git", "linux", "css", "html",
        ]
        desc_lower = description.lower()
        for kw in tech_keywords:
            if kw in desc_lower:
                skills.append(kw)
        return skills