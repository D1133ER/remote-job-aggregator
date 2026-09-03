from typing import List, Dict, Any
from .base import BaseScraper

class RemotiveScraper(BaseScraper):
    """Scraper for Remotive API"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "remotive"
        self.api_url = "https://remotive.com/api/remote-jobs"
    
    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        """Fetch jobs from Remotive API"""
        response = await self.fetch_url(self.api_url)
        jobs_data = response.json()
        
        parsed_jobs = []
        for job in jobs_data.get("jobs", []):
            parsed_job = self.parse_job(job)
            if parsed_job:
                parsed_jobs.append(parsed_job)
        
        return parsed_jobs
    
    def parse_job(self, raw_job: Dict) -> Dict[str, Any]:
        """Parse Remotive job data"""
        return {
            "title": raw_job.get("title"),
            "company_name": raw_job.get("company_name"),
            "company_logo_url": raw_job.get("company_logo_url"),
            "description": raw_job.get("description"),
            "location": raw_job.get("candidate_required_location", "Remote"),
            "remote_type": "full_remote",
            "source_url": raw_job.get("url"),
            "source_id": str(raw_job.get("id")),
            "posted_at": raw_job.get("publication_date"),
            "salary_min": self.parse_salary(raw_job.get("salary"), "min"),
            "salary_max": self.parse_salary(raw_job.get("salary"), "max"),
            "skills": self.extract_skills_from_description(raw_job.get("description", "")),
            "tags": raw_job.get("tags", []),
            "category": raw_job.get("category"),
        }
    
    def parse_salary(self, salary_str: str, type: str) -> float:
        """Parse salary string to float"""
        if not salary_str:
            return None
        
        # Simple parsing, you can make this more sophisticated
        try:
            # Extract numbers from string like "50k - 80k"
            numbers = [int(s.replace('k', '000').replace('K', '000')) 
                      for s in salary_str.split('-') if any(c.isdigit() for c in s)]
            
            if type == "min" and numbers:
                return float(numbers[0])
            elif type == "max" and len(numbers) > 1:
                return float(numbers[1])
        except:
            pass
        
        return None
    
    def extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from description"""
        # Similar to Greenhouse implementation
        return []