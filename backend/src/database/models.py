"""
Database models for the Resume-to-Training Module Generator.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Resume(Base):
    """Resume model"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)  # Structured resume data
    skills = Column(JSON, nullable=True)  # Extracted skills
    experience = Column(JSON, nullable=True)  # Work experience
    education = Column(JSON, nullable=True)  # Education history
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    training_modules = relationship("TrainingModule", back_populates="resume")


class JobDescription(Base):
    """Job description model"""
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=True)
    preferred_skills = Column(JSON, nullable=True)
    domain = Column(String, nullable=True)  # e.g., "biotech", "finance"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    gap_analyses = relationship("GapAnalysis", back_populates="job_description")


class GapAnalysis(Base):
    """Gap analysis model - links resume to job description"""
    __tablename__ = "gap_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    
    # Gap analysis results
    existing_skills = Column(JSON, nullable=True)  # Skills the candidate has
    missing_skills = Column(JSON, nullable=True)  # Skills the candidate lacks
    skill_gaps = Column(JSON, nullable=True)  # Detailed gap analysis
    gap_priority = Column(JSON, nullable=True)  # Prioritized gaps
    
    # Analysis metadata
    confidence_score = Column(Float, nullable=True)
    analysis_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume")
    job_description = relationship("JobDescription", back_populates="gap_analyses")
    training_modules = relationship("TrainingModule", back_populates="gap_analysis")


class TrainingModule(Base):
    """Training module model"""
    __tablename__ = "training_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    gap_analysis_id = Column(Integer, ForeignKey("gap_analyses.id"), nullable=False)
    
    # Module content
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    learning_objectives = Column(JSON, nullable=True)
    modules = Column(JSON, nullable=False)  # Array of module content
    case_studies = Column(JSON, nullable=True)
    practical_exercises = Column(JSON, nullable=True)
    resources = Column(JSON, nullable=True)  # Links, papers, tutorials
    
    # Progress tracking
    status = Column(String, default="pending")  # pending, in_progress, completed
    progress = Column(Float, default=0.0)
    
    # Metadata
    estimated_duration = Column(String, nullable=True)  # e.g., "2 weeks"
    difficulty_level = Column(String, nullable=True)  # beginner, intermediate, advanced
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="training_modules")
    gap_analysis = relationship("GapAnalysis", back_populates="training_modules")

