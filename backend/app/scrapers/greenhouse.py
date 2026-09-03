from typing import List, Dict, Any
from .base import BaseScraper
import json
from urllib.parse import urlencode

class GreenhouseScraper(BaseScraper):
    """Scraper for Greenhouse ATS"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "greenhouse"
        self.api_base = "https://boards-api.greenhouse.io/v1/boards"
    
    async def fetch_jobs(self, company_token: str = None) -> List[Dict[str, Any]]:
        """Fetch jobs from Greenhouse API"""
        if company_token:
            url = f"{self.api_base}/{company_token}/jobs"
        else:
            # For demo, fetch from a known company
            url = f"{self.api_base}/stripe/jobs"
        
        response = await self.fetch_url(url)
        jobs_data = response.json()
        
        parsed_jobs = []
        for job in jobs_data.get("jobs", []):
            parsed_job = self.parse_job(job)
            if parsed_job:
                parsed_jobs.append(parsed_job)
        
        return parsed_jobs
    
    def parse_job(self, raw_job: Dict) -> Dict[str, Any]:
        """Parse Greenhouse job data"""
        # Check if remote
        location = raw_job.get("location", {}).get("name", "")
        is_remote = "remote" in location.lower() or "anywhere" in location.lower()
        
        if not is_remote:
            return None
        
        return {
            "title": raw_job.get("title"),
            "company_name": "Company Name",  # You'd fetch this from API
            "description": raw_job.get("content", ""),
            "location": location,
            "remote_type": "full_remote" if is_remote else "onsite",
            "source_url": raw_job.get("absolute_url"),
            "source_id": str(raw_job.get("id")),
            "posted_at": raw_job.get("updated_at"),
            "skills": self.extract_skills(raw_job.get("content", "")),
            "tags": self.extract_tags(raw_job.get("title", "")),
        }
    
    def extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description using keyword matching"""
        skills = []
        tech_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular",
            "vue", "node", "django", "flask", "fastapi", "aws", "azure",
            "gcp", "docker", "kubernetes", "sql", "postgresql", "mongodb",
            "redis", "elasticsearch", "graphql", "rest", "microservices"
        ]
        
        description_lower = description.lower()
        for keyword in tech_keywords:
            if keyword in description_lower:
                skills.append(keyword)
        
        return skills
    
    def extract_tags(self, title: str) -> List[str]:
        """Extract tags from job title"""
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