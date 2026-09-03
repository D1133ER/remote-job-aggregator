from typing import List, Dict, Any
from .base import BaseScraper

class WorkableScraper(BaseScraper):
    """Scraper for Workable ATS"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "workable"
        self.api_base = "https://www.workable.com/api/v1"
    
    async def fetch_jobs(self, company: str = None) -> List[Dict[str, Any]]:
        """Fetch jobs from Workable API"""
        if not company:
            return []
        
        url = f"https://{company}.workable.com/spider/v3/api/jobs?callback=&team=&department=&location=&remote=true"
        
        try:
            response = await self.fetch_url(url)
            # Workable returns JSONP, need to parse it
            text = response.text
            # Remove JSONP wrapper
            if text.startswith("callback("):
                text = text[9:-1]
            
            import json
            jobs_data = json.loads(text)
            
            parsed_jobs = []
            for job in jobs_data.get("jobs", []):
                parsed_job = self.parse_job(job, company)
                if parsed_job:
                    parsed_jobs.append(parsed_job)
            
            return parsed_jobs
        except Exception as e:
            print(f"Error fetching Workable jobs for {company}: {e}")
            return []
    
    def parse_job(self, raw_job: Dict, company: str) -> Dict[str, Any]:
        """Parse Workable job data"""
        title = raw_job.get("title", "")
        department = raw_job.get("department", "")
        location = raw_job.get("location", "")
        
        # Check if remote
        is_remote = raw_job.get("remote", False) or "remote" in location.lower()
        
        if not is_remote:
            return None
        
        # Build the job URL
        job_url = f"https://{company}.workable.com/jobs/{raw_job.get('shortcode', '')}"
        
        return {
            "title": title,
            "company_name": company.title(),
            "description": raw_job.get("description", "") or raw_job.get("description_text", ""),
            "location": location,
            "remote_type": "full_remote",
            "source_url": job_url,
            "source_id": raw_job.get("shortcode"),
            "posted_at": raw_job.get("created"),
            "job_type": self.map_job_type(raw_job.get("employment_type", "")),
            "experience_level": self.extract_experience_level(title),
            "skills": self.extract_skills(raw_job.get("description", "") or ""),
            "tags": self.extract_tags(title, department),
            "category": department,
        }
    
    def map_job_type(self, employment_type: str) -> str:
        """Map Workable employment type to our job types"""
        type_lower = employment_type.lower()
        if "full" in type_lower:
            return "full_time"
        elif "part" in type_lower:
            return "part_time"
        elif "contract" in type_lower or "freelance" in type_lower:
            return "contract"
        return "full_time"
    
    def extract_experience_level(self, title: str) -> str:
        """Extract experience level from title"""
        title_lower = title.lower()
        if "senior" in title_lower or "sr" in title_lower:
            return "senior"
        elif "junior" in title_lower or "jr" in title_lower:
            return "junior"
        elif "lead" in title_lower or "principal" in title_lower or "staff" in title_lower:
            return "lead"
        return "mid"
    
    def extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description"""
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
    
    def extract_tags(self, title: str, department: str) -> List[str]:
        """Extract tags from job title and department"""
        tags = []
        
        # From title
        title_lower = title.lower()
        if "frontend" in title_lower or "front-end" in title_lower:
            tags.append("frontend")
        elif "backend" in title_lower or "back-end" in title_lower:
            tags.append("backend")
        elif "fullstack" in title_lower or "full-stack" in title_lower:
            tags.append("fullstack")
        
        # From department
        if department:
            tags.append(department.lower())
        
        return tags