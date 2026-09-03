from typing import Dict, Any, List
from openai import AsyncOpenAI
import json
import logging

logger = logging.getLogger(__name__)


class AIEnrichmentService:
    """Uses OpenAI to enrich and clean job data"""

    def __init__(self, api_key: str = None):
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def enrich_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        if self.client is None:
            return job

        try:
            summary = await self.generate_summary(job)
            if summary:
                job["summary"] = summary

            skills = await self.extract_skills(job)
            if skills:
                job["skills"] = list(set(job.get("skills", []) + skills))

            is_remote = await self.verify_remote(job)
            if not is_remote:
                job["is_active"] = False

            if not job.get("salary_min") and job.get("description"):
                salary = await self.extract_salary(job["description"])
                if salary:
                    job.update(salary)

            return job

        except Exception as e:
            logger.error("AI enrichment failed for job '%s': %s", job.get("title", "unknown"), e)
            return job

    async def generate_summary(self, job: Dict) -> str:
        prompt = f"""
        Create a 2-3 sentence summary for this job posting:

        Title: {job.get('title')}
        Company: {job.get('company_name')}
        Description: {job.get('description', '')[:500]}

        Include key responsibilities, required skills, and any standout perks.
        """

        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes job postings concisely."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.5,
        )

        return response.choices[0].message.content.strip()

    async def extract_skills(self, job: Dict) -> List[str]:
        prompt = f"""
        Extract technical skills and technologies from this job posting.
        Return ONLY a JSON array of strings.

        Title: {job.get('title')}
        Description: {job.get('description', '')[:1000]}

        Example: ["Python", "React", "Docker", "AWS"]
        """

        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You extract technical skills from job descriptions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        try:
            skills_text = response.choices[0].message.content
            skills_text = skills_text.replace("```json", "").replace("```", "").strip()
            return json.loads(skills_text)
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            logger.warning("Failed to parse skills from AI response: %s", e)
            return []

    async def verify_remote(self, job: Dict) -> bool:
        prompt = f"""
        Determine if this job is truly 100% remote (no office visits required).
        Return "true" or "false" only.

        Title: {job.get('title')}
        Location: {job.get('location')}
        Description: {job.get('description', '')[:500]}
        """

        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You verify if jobs are truly remote."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content.strip().lower() == "true"

    async def extract_salary(self, description: str) -> Dict:
        prompt = f"""
        Extract salary information from this job description.
        Return JSON format: {{"salary_min": number, "salary_max": number, "salary_currency": "USD"}}

        Description: {description[:1000]}
        """

        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You extract salary information from job descriptions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        try:
            salary_data = response.choices[0].message.content
            salary_data = salary_data.replace("```json", "").replace("```", "").strip()
            return json.loads(salary_data)
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            logger.warning("Failed to parse salary from AI response: %s", e)
            return {}