from typing import List, Dict, Any
from .base import BaseScraper
import re

class WeWorkRemotelyScraper(BaseScraper):
    """Scraper for We Work Remotely RSS feed"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "weworkremotely"
        self.rss_url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    
    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        """Fetch jobs from We Work Remotely RSS"""
        try:
            response = await self.fetch_url(self.rss_url)
            return self.parse_rss(response.text)
        except Exception as e:
            print(f"Error fetching We Work Remotely: {e}")
            return []
    
    def parse_rss(self, rss_content: str) -> List[Dict[str, Any]]:
        """Parse RSS feed content"""
        jobs = []
        
        # Simple regex parsing (in production, use feedparser)
        items = re.findall(r'<item>(.*?)</item>', rss_content, re.DOTALL)
        
        for item in items[:50]:  # Limit to 50 jobs
            title = re.search(r'<title>(.*?)</title>', item)
            link = re.search(r'<link>(.*?)</link>', item)
            description = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
            
            if title and link:
                job = {
                    "title": title.group(1).strip(),
                    "company_name": "We Work Remotely Company",  # Extract from description
                    "description": description.group(1).strip() if description else "",
                    "location": "Remote",
                    "remote_type": "full_remote",
                    "source_url": link.group(1).strip(),
                    "source_id": link.group(1).strip(),
                    "posted_at": None,
                    "skills": self.extract_skills(title.group(1) + " " + (description.group(1) if description else "")),
                    "tags": ["remote"],
                }
                jobs.append(job)
        
        return jobs
    
    def parse_job(self, raw_data: Dict) -> Dict[str, Any]:
        """Parse raw job data"""
        return raw_data
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        skills = []
        tech_keywords = [
            "python", "javascript", "typescript", "react", "vue", "node",
            "django", "flask", "fastapi", "aws", "docker", "kubernetes",
            "sql", "postgresql", "mongodb", "redis", "graphql", "rest",
            "ruby", "rails", "go", "golang", "rust", "java", "php"
        ]
        
        text_lower = text.lower()
        for keyword in tech_keywords:
            if keyword in text_lower:
                skills.append(keyword)
        
        return skills