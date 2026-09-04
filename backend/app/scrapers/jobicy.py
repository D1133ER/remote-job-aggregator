from typing import List, Dict, Any, Optional
from .base import BaseScraper
from datetime import datetime, timezone


class JobicyScraper(BaseScraper):
    """Scraper for Jobicy — remote jobs with built-in salary data."""

    def __init__(self):
        super().__init__()
        self.source_name = "jobicy"
        self.api_url = "https://jobicy.com/api/v2/remote-jobs"

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        # Jobicy supports count-based fetching; a single call with count=100
        # returns a solid batch of real remote jobs
        response = await self.fetch_url(f"{self.api_url}?count=100")
        data = response.json()

        jobs = data.get("jobs", [])
        all_jobs = []
        for job in jobs:
            parsed = self.parse_job(job)
            if parsed:
                all_jobs.append(parsed)

        return all_jobs

    def parse_job(self, raw_job: Dict) -> Optional[Dict[str, Any]]:
        description = raw_job.get("jobDescription", "") or ""
        tags = raw_job.get("jobTags", []) or []

        # Parse salary from Jobicy's structured data
        salary_min = None
        salary_max = None
        salary_currency = raw_job.get("annualSalaryCurrency", "USD")

        annual_min = raw_job.get("annualSalaryMin")
        annual_max = raw_job.get("annualSalaryMax")
        if annual_min:
            salary_min = float(annual_min)
        if annual_max:
            salary_max = float(annual_max)

        # Parse posted_at
        posted_at = None
        pub_date = raw_job.get("pubDate")
        if pub_date:
            try:
                posted_at = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        # Build salary display
        salary_display = None
        if salary_min and salary_max:
            salary_display = f"${salary_min:,.0f} - ${salary_max:,.0f} {salary_currency}"
        elif salary_min:
            salary_display = f"From ${salary_min:,.0f} {salary_currency}"

        # Map Jobicy's job type (array of strings)
        job_type_raw = raw_job.get("jobType", [])
        if isinstance(job_type_raw, str):
            job_type_raw = [job_type_raw]
        job_type = self._map_job_type(" ".join(job_type_raw))

        # Map experience level
        exp_level = raw_job.get("jobLevel", "")

        return {
            "title": raw_job.get("jobTitle", "Unknown Title"),
            "company_name": raw_job.get("companyName", "Unknown"),
            "company_logo_url": raw_job.get("companyLogo"),
            "company_website": raw_job.get("url"),
            "description": description,
            "location": raw_job.get("jobGeo", "Remote"),
            "remote_type": "full_remote",
            "source_url": raw_job.get("url", ""),
            "apply_url": raw_job.get("url", ""),
            "source_id": str(raw_job.get("id", "")),
            "posted_at": posted_at,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": salary_currency,
            "salary_display": salary_display,
            "skills": self.extract_skills(description, tags),
            "tags": tags,
            "category": raw_job.get("jobIndustry", ["Other"])[0] if raw_job.get("jobIndustry") else "Software Development",
            "job_type": job_type,
            "experience_level": self._map_experience(exp_level),
        }

    def extract_skills(self, description: str, tags: List[str]) -> List[str]:
        # Use tags first — Jobicy tags are usually tech skills
        if tags:
            return [t for t in tags if len(t) < 50]

        # Fallback: extract from description
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

    def _map_job_type(self, job_type: str) -> str:
        jt = job_type.lower()
        if "full" in jt:
            return "full_time"
        if "part" in jt:
            return "part_time"
        if "contract" in jt or "freelance" in jt:
            return "contract"
        if "intern" in jt:
            return "internship"
        return "full_time"

    def _map_experience(self, experience: str) -> str:
        exp = experience.lower()
        if "senior" in exp or "sr" in exp or "5" in exp or "8" in exp or "10" in exp:
            return "senior"
        if "junior" in exp or "jr" in exp or "entry" in exp:
            return "junior"
        if "lead" in exp or "principal" in exp or "staff" in exp:
            return "lead"
        return "mid"
