from sqlalchemy import Column, String, Text, Boolean, JSON, Float, DateTime, Integer, Index
from app.core.database import BaseModel
from sqlalchemy.dialects.postgresql import TSVECTOR

class Job(BaseModel):
    __tablename__ = "jobs"
    
    # Basic Info
    title = Column(String(500), nullable=False, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    company_logo_url = Column(String(500))
    company_website = Column(String(500))
    
    # Description
    description = Column(Text)
    description_html = Column(Text)
    summary = Column(Text)  # AI-generated summary
    
    # Location & Remote
    location = Column(String(200))
    remote_type = Column(String(50))  # full_remote, hybrid, onsite
    geo_restrictions = Column(JSON)  # ["USA", "Europe", "Global"]
    timezone_requirements = Column(String(200))
    
    # Compensation
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10), default="USD")
    salary_display = Column(String(200))
    
    # Metadata
    source_url = Column(String(1000), unique=True)
    source_name = Column(String(100))
    source_id = Column(String(200))
    job_type = Column(String(50))  # full_time, part_time, contract
    experience_level = Column(String(50))  # junior, mid, senior, lead
    
    # Skills & Tags
    skills = Column(JSON)  # ["Python", "React", "AWS"]
    tags = Column(JSON)
    category = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    posted_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Search
    search_vector = Column(TSVECTOR)
    
    __table_args__ = (
        Index('ix_jobs_search_vector', 'search_vector', postgresql_using='gin'),
        Index('ix_jobs_title_company', 'title', 'company_name'),
    )

class Company(BaseModel):
    __tablename__ = "companies"
    
    name = Column(String(200), unique=True, index=True)
    logo_url = Column(String(500))
    website = Column(String(500))
    description = Column(Text)
    industry = Column(String(100))
    remote_policy = Column(String(50))  # full_remote, hybrid, onsite
    average_response_time = Column(String(50))
    total_jobs_posted = Column(Integer, default=0)
    total_jobs_remote = Column(Integer, default=0)