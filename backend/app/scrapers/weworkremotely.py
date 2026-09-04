from typing import List, Dict, Any
from .base import BaseScraper
import feedparser
from bs4 import BeautifulSoup
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
        except Exception:
            return []

    def parse_rss(self, rss_content: str) -> List[Dict[str, Any]]:
        jobs = []
        feed = feedparser.parse(rss_content)

        for entry in feed.entries[:50]:
            company_name = self._extract_company_from_description(
                getattr(entry, "description", "")
            )

            clean_description = self._clean_html(
                getattr(entry, "description", "")
            )

            skills = self.extract_skills(
                entry.get("title", "") + " " + clean_description
            )

            jobs.append({
                "title": entry.get("title", "").strip(),
                "company_name": company_name,
                "description": clean_description,
                "location": "Remote",
                "remote_type": "full_remote",
                "source_url": entry.get("link", ""),
                "apply_url": entry.get("link", ""),
                "source_id": entry.get("link", ""),
                "posted_at": entry.get("published"),
                "skills": skills,
                "tags": ["remote"],
            })

        return jobs

    def parse_job(self, raw_data: Dict) -> Dict[str, Any]:
        return raw_data

    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def _extract_company_from_description(self, description: str) -> str:
        """Try to extract company name from the description HTML."""
        soup = BeautifulSoup(description, "html.parser")
        company_tag = soup.find("span", class_="company")
        if company_tag:
            return company_tag.get_text(strip=True)

        bold_tag = soup.find("b")
        if bold_tag:
            return bold_tag.get_text(strip=True)

        return "We Work Remotely"

    def extract_skills(self, text: str) -> List[str]:
        skills = []
        tech_keywords = [
            "python", "javascript", "typescript", "react", "vue", "node",
            "django", "flask", "fastapi", "aws", "docker", "kubernetes",
            "sql", "postgresql", "mongodb", "redis", "graphql", "rest",
            "ruby", "rails", "go", "golang", "rust", "java", "php",
        ]
        text_lower = text.lower()
        for keyword in tech_keywords:
            if keyword in text_lower:
                skills.append(keyword)
        return skills