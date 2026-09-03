from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Preferences
    preferred_categories = Column(JSON)  # ["Software Development", "Design"]
    preferred_remote_types = Column(JSON)  # ["full_remote"]
    preferred_locations = Column(JSON)  # ["USA", "Europe"]
    preferred_skills = Column(JSON)  # ["Python", "React"]
    salary_expectation_min = Column(Integer)
    salary_expectation_max = Column(Integer)
    
    # Relationships
    saved_jobs = relationship("SavedJob", back_populates="user")
    job_alerts = relationship("JobAlert", back_populates="user")
    hidden_companies = relationship("HiddenCompany", back_populates="user")
    hidden_jobs = relationship("HiddenJob", back_populates="user")


class SavedJob(BaseModel):
    __tablename__ = "saved_jobs"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job")


class JobAlert(BaseModel):
    __tablename__ = "job_alerts"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    keywords = Column(String(500))  # "React, TypeScript, Remote"
    category = Column(String(100))
    remote_type = Column(String(50))
    location = Column(String(200))
    salary_min = Column(Integer)
    is_active = Column(Boolean, default=True)
    frequency = Column(String(20), default="daily")  # daily, weekly, instant
    
    # Relationships
    user = relationship("User", back_populates="job_alerts")


class HiddenCompany(BaseModel):
    __tablename__ = "hidden_companies"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    company_name = Column(String(200), nullable=False)
    reason = Column(String(500))  # "Ghosted me", "Bad reviews", etc.
    
    # Relationships
    user = relationship("User", back_populates="hidden_companies")


class HiddenJob(BaseModel):
    __tablename__ = "hidden_jobs"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)

    user = relationship("User", back_populates="hidden_jobs")
    job = relationship("Job")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_hidden_jobs_user_job"),
    )