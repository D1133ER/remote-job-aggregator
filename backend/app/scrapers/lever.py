from typing import List, Dict, Any
from .base import BaseScraper

class LeverScraper(BaseScraper):
    """Scraper for Lever ATS"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "lever"
        self.api_base = "https://api.lever.co/v0"
    
    async def fetch_jobs(self, company: str = None) -> List[Dict[str, Any]]:
        """Fetch jobs from Lever API"""
        if not company:
            company = "lever"  # Default demo company
        
        url = f"{self.api_base}/postings/{company}?mode=json"
        
        try:
            response = await self.fetch_url(url)
            jobs_data = response.json()
            
            parsed_jobs = []
            for job in jobs_data:
                parsed_job = self.parse_job(job)
                if parsed_job:
                    parsed_jobs.append(parsed_job)
            
            return parsed_jobs
        except Exception as e:
            print(f"Error fetching Lever jobs for {company}: {e}")
            return []
    
    def parse_job(self, raw_job: Dict) -> Dict[str, Any]:
        """Parse Lever job data"""
        # Check if remote
        categories = raw_job.get("categories", {})
        location = categories.get("location", "")
        is_remote = "remote" in location.lower() or "anywhere" in location.lower()
        
        if not is_remote:
            return None
        
        # Extract salary if available
        salary_min = None
        salary_max = None
        
        # Lever sometimes has salary range in the description
        description = raw_job.get("descriptionPlain", "") or raw_job.get("description", "")
        
        return {
            "title": raw_job.get("text"),
            "company_name": raw_job.get("company", "Unknown"),
            "description": description,
            "location": location,
            "remote_type": "full_remote" if is_remote else "hybrid",
            "source_url": raw_job.get("hostedUrl"),
            "source_id": raw_job.get("id"),
            "posted_at": raw_job.get("createdAt"),
            "job_type": self.map_job_type(categories.get("commitment", "")),
            "experience_level": self.extract_experience_level(raw_job.get("text", "")),
            "skills": self.extract_skills(description),
            "tags": self.extract_tags(raw_job.get("text", "")),
            "salary_min": salary_min,
            "salary_max": salary_max,
        }
    
    def map_job_type(self, commitment: str) -> str:
        """Map Lever commitment to our job types"""
        commitment_lower = commitment.lower()
        if "full" in commitment_lower:
            return "full_time"
        elif "part" in commitment_lower:
            return "part_time"
        elif "contract" in commitment_lower or "freelance" in commitment_lower:
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
            "redis", "elasticsearch", "graphql", "rest", "microservices",
            "ruby", "rails", "go", "golang", "rust", "php", "swift", "kotlin"
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
        
        if "frontend" in title_lower or "front-end" in title_lower:
            tags.append("frontend")
        elif "backend" in title_lower or "back-end" in title_lower:
            tags.append("backend")
        elif "fullstack" in title_lower or "full-stack" in title_lower:
            tags.append("fullstack")
        elif "devops" in title_lower:
            tags.append("devops")
        elif "data" in title_lower:
            tags.append("data")
        elif "mobile" in title_lower:
            tags.append("mobile")
        
        return tags