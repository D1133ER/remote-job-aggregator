"""Script to seed the database with sample job data for development"""
import asyncio
import random
from datetime import datetime, timedelta, timezone
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.job import Job, Company
from app.models.user import User, SavedJob, JobAlert, HiddenCompany
from app.services.auth import get_password_hash


SAMPLE_COMPANIES = [
    {"name": "Stripe", "website": "https://stripe.com", "industry": "FinTech", "remote_policy": "full_remote"},
    {"name": "GitLab", "website": "https://gitlab.com", "industry": "DevTools", "remote_policy": "full_remote"},
    {"name": "Shopify", "website": "https://shopify.com", "industry": "E-commerce", "remote_policy": "full_remote"},
    {"name": "Automattic", "website": "https://automattic.com", "industry": "Internet", "remote_policy": "full_remote"},
    {"name": "Zapier", "website": "https://zapier.com", "industry": "Automation", "remote_policy": "full_remote"},
    {"name": "Mozilla", "website": "https://mozilla.org", "industry": "Internet", "remote_policy": "full_remote"},
    {"name": "Doist", "website": "https://doist.com", "industry": "Productivity", "remote_policy": "full_remote"},
    {"name": "Prezi", "website": "https://prezi.com", "industry": "Productivity", "remote_policy": "full_remote"},
]

SAMPLE_JOBS = [
    {
        "title": "Senior React Developer",
        "company_name": "Stripe",
        "description": "We're looking for a Senior React Developer to help build the future of online payments. You'll work on our merchant dashboard and developer tools. 5+ years of experience with React, TypeScript, and modern frontend development required. Experience with GraphQL and Node.js is a plus. Fully remote position with opportunities to work in global time zones.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 150000,
        "salary_max": 220000,
        "salary_display": "$150k - $220k",
        "skills": ["React", "TypeScript", "GraphQL", "Node.js", "JavaScript"],
        "tags": ["senior", "frontend"],
        "category": "Software Development",
        "experience_level": "senior",
    },
    {
        "title": "DevOps Engineer",
        "company_name": "GitLab",
        "description": "Join our infrastructure team to help build and scale GitLab's cloud platform. You'll work with Kubernetes, Terraform, and AWS to manage our multi-cloud infrastructure. Experience with CI/CD pipelines, containers, and infrastructure as code required. Fully remote, work from anywhere in the world.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 120000,
        "salary_max": 180000,
        "salary_display": "$120k - $180k",
        "skills": ["DevOps", "Kubernetes", "Terraform", "AWS", "CI/CD", "Docker"],
        "tags": ["devops", "infrastructure"],
        "category": "DevOps",
        "experience_level": "mid",
    },
    {
        "title": "Python Backend Developer",
        "company_name": "Shopify",
        "description": "Looking for a Python Developer to work on our commerce platform's backend services. You'll build and maintain APIs using FastAPI and Django, work with PostgreSQL and Redis, and scale services handling millions of requests per day. Experience with microservices architecture required.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 110000,
        "salary_max": 170000,
        "salary_display": "$110k - $170k",
        "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "Microservices"],
        "tags": ["backend"],
        "category": "Software Development",
        "experience_level": "mid",
    },
    {
        "title": "UX Designer",
        "company_name": "Automattic",
        "description": "We're seeking a talented UX Designer to create beautiful, intuitive interfaces for our WordPress products. You'll work with a distributed team across the globe. Experience with Figma, design systems, and user research required. This is a fully remote position.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 80000,
        "salary_max": 120000,
        "salary_display": "$80k - $120k",
        "skills": ["UX", "Figma", "Design Systems", "User Research"],
        "tags": ["design"],
        "category": "Design",
        "experience_level": "mid",
    },
    {
        "title": "Customer Support Specialist",
        "company_name": "Zapier",
        "description": "Help Zapier customers get the most out of our automation platform. You'll answer questions via chat and email, write documentation, and provide feedback to our product team. Excellent written communication skills required. Fully remote position with flexible hours.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 45000,
        "salary_max": 65000,
        "salary_display": "$45k - $65k",
        "skills": ["Customer Support", "Communication", "Writing"],
        "tags": ["support"],
        "category": "Customer Support",
        "experience_level": "junior",
    },
    {
        "title": "Data Scientist",
        "company_name": "Mozilla",
        "description": "Join Mozilla's data science team to work on browser insights and machine learning models. You'll work with Python, pandas, and PyTorch to analyze large datasets and build predictive models. Experience with statistical analysis and data visualization required.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 120000,
        "salary_max": 180000,
        "salary_display": "$120k - $180k",
        "skills": ["Python", "PyTorch", "pandas", "Machine Learning", "SQL"],
        "tags": ["data"],
        "category": "Data Science",
        "experience_level": "senior",
    },
    {
        "title": "Product Manager",
        "company_name": "Prezi",
        "description": "We're looking for a Product Manager to lead our presentation software product. You'll work with engineering, design, and marketing to define the roadmap and ship new features. Experience with SaaS products and agile methodologies required.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 100000,
        "salary_max": 150000,
        "salary_display": "$100k - $150k",
        "skills": ["Product Management", "SaaS", "Agile", "Roadmapping"],
        "tags": ["product"],
        "category": "Product Management",
        "experience_level": "senior",
    },
    {
        "title": "Digital Marketing Manager",
        "company_name": "Shopify",
        "description": "Help grow Shopify's merchant base through digital marketing. You'll manage paid campaigns, email marketing, and SEO. Experience with Google Ads, Meta Ads, and marketing analytics required. Fully remote with great benefits.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 70000,
        "salary_max": 110000,
        "salary_display": "$70k - $110k",
        "skills": ["Marketing", "Google Ads", "SEO", "Email Marketing"],
        "tags": ["marketing"],
        "category": "Marketing",
        "experience_level": "mid",
    },
    {
        "title": "Solutions Engineer",
        "company_name": "Stripe",
        "description": "Work as a Solutions Engineer helping enterprise customers integrate Stripe's APIs. You'll provide technical guidance, build sample implementations, and solve complex integration challenges. Experience with REST APIs, JavaScript, and strong communication skills required.",
        "location": "Remote",
        "remote_type": "full_remote",
        "salary_min": 130000,
        "salary_max": 190000,
        "salary_display": "$130k - $190k",
        "skills": ["API", "JavaScript", "Integration", "Technical Sales"],
        "tags": ["sales", "engineering"],
        "category": "Sales",
        "experience_level": "senior",
    },
]


async def seed_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        for company_data in SAMPLE_COMPANIES:
            existing = await session.execute(
                select(Company).where(Company.name == company_data["name"])
            )
            if not existing.scalar_one_or_none():
                company = Company(**company_data)
                session.add(company)

        now = datetime.now(timezone.utc)
        for i, job_data in enumerate(SAMPLE_JOBS):
            job_data = dict(job_data)
            job_data["source_url"] = f"https://example.com/jobs/{i}"
            job_data["apply_url"] = job_data["source_url"]
            job_data["source_name"] = random.choice(["greenhouse", "remotive", "lever", "weworkremotely"])
            job_data["source_id"] = f"sample-{i}"
            job_data["posted_at"] = now - timedelta(days=i % 10)

            job = Job(**job_data)
            session.add(job)

        demo_user = User(
            email="demo@remotejobhub.com",
            username="demo",
            hashed_password=get_password_hash("Demo1234"),
            full_name="Demo User",
            is_verified=True,
        )
        session.add(demo_user)

        await session.commit()

        print("Database seeded successfully!")
        print(f"   Companies: {len(SAMPLE_COMPANIES)}")
        print(f"   Jobs: {len(SAMPLE_JOBS)}")
        print("   Demo user: demo@remotejobhub.com / Demo1234")


if __name__ == "__main__":
    asyncio.run(seed_database())