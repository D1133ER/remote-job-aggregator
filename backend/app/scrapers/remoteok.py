from typing import List, Dict, Any, Optional
from .base import BaseScraper
from datetime import datetime, timezone


class RemoteOKScraper(BaseScraper):
    """Scraper for RemoteOK — one of the largest remote job boards."""

    def __init__(self):
        super().__init__()
        self.source_name = "remoteok"
        self.api_url = "https://remoteok.com/api"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        response = await self.fetch_url(self.api_url)
        data = response.json()

        parsed_jobs = []
        # First element is metadata, skip it
        for item in data:
            if not isinstance(item, dict) or "id" not in item:
                continue
            parsed = self.parse_job(item)
            if parsed:
                parsed_jobs.append(parsed)

        return parsed_jobs

    def parse_job(self, raw_job: Dict) -> Optional[Dict[str, Any]]:
        description = raw_job.get("description", "") or ""

        # RemoteOK is a remote-only job board, so all listings are remote.
        tags = raw_job.get("tags", []) or []

        salary_min = raw_job.get("salary_min") or None
        salary_max = raw_job.get("salary_max") or None

        # Parse salary from the salary string if structured fields missing
        # (e.g. "$100k - $150k")
        if not salary_min and raw_job.get("salary"):
            salary_min, salary_max = self._parse_salary(raw_job["salary"])

        # Parse posted_at — RemoteOK uses epoch seconds
        posted_at = None
        epoch = raw_job.get("epoch")
        if epoch:
            try:
                posted_at = datetime.fromtimestamp(int(epoch), tz=timezone.utc)
            except (ValueError, TypeError, OSError):
                pass

        return {
            "title": raw_job.get("position", "Unknown Title"),
            "company_name": raw_job.get("company", "Unknown"),
            "company_logo_url": raw_job.get("logo"),
            "company_website": raw_job.get("url"),
            "description": description,
            "location": raw_job.get("location") or "Remote",
            "remote_type": "full_remote",
            "source_url": f"https://remoteok.com/remote-jobs/{raw_job.get('id')}",
            "apply_url": raw_job.get("apply_url") or f"https://remoteok.com/remote-jobs/{raw_job.get('id')}",
            "source_id": str(raw_job.get("id")),
            "posted_at": posted_at,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": "USD",
            "skills": self.extract_skills(description),
            "tags": tags,
            "category": self._categorize(tags),
            "job_type": self._map_job_type(raw_job.get("full_time")),
            "experience_level": self._extract_experience(raw_job.get("position", "")),
        }

    def _parse_salary(self, salary_str: str) -> tuple:
        """Parse salary strings like '$100k - $150k' or '$50,000 - $80,000'."""
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

            if len(parsed) >= 2:
                return float(parsed[0]), float(parsed[1])
            elif len(parsed) == 1:
                return float(parsed[0]), None
        except (ValueError, TypeError):
            pass
        return None, None

    def extract_skills(self, description: str) -> List[str]:
        skills = []
        tech_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular",
            "vue", "node", "django", "flask", "fastapi", "aws", "azure",
            "gcp", "docker", "kubernetes", "sql", "postgresql", "mongodb",
            "redis", "elasticsearch", "graphql", "rest", "microservices",
            "ruby", "rails", "go", "golang", "rust", "php", "swift", "kotlin",
            "terraform", "ansible", "jenkins", "git", "linux", "css", "html",
            "nextjs", "svelte", "flutter", "react native", "typescript",
            "machine learning", "tensorflow", "pytorch", "pandas", "numpy",
        ]
        desc_lower = description.lower()
        for kw in tech_keywords:
            if kw in desc_lower:
                skills.append(kw)
        return skills

    def _categorize(self, tags: List[str]) -> str:
        tag_set = {t.lower() for t in tags}
        if tag_set & {"engineering", "backend", "frontend", "fullstack", "full-stack", "devops"}:
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
        if tag_set & {"product", "product-management"}:
            return "Product Management"
        return "Software Development"

    def _map_job_type(self, full_time) -> str:
        if full_time is True:
            return "full_time"
        if full_time is False:
            return "part_time"
        return "full_time"

    def _extract_experience(self, title: str) -> str:
        title_lower = title.lower()
        if "senior" in title_lower or "sr" in title_lower:
            return "senior"
        if "junior" in title_lower or "jr" in title_lower:
            return "junior"
        if "lead" in title_lower or "principal" in title_lower or "staff" in title_lower:
            return "lead"
        return "mid"
