"""
MongoDB document models using Pydantic for data validation.
These models define the structure of documents stored in MongoDB.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return v
            raise ValueError("Invalid ObjectId")
        raise ValueError("ObjectId required")


class MongoBaseModel(BaseModel):
    """Base model with common MongoDB document fields."""
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


# Resume Models
class ResumeCreate(MongoBaseModel):
    """Model for creating a new resume."""
    filename: str
    raw_text: str
    file_id: Optional[str] = None  # GridFS file ID
    parsed_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None


class ResumeDocument(MongoBaseModel):
    """Full resume document model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    filename: str
    raw_text: str
    file_id: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class ResumeResponse(MongoBaseModel):
    """Resume response model for API."""
    id: str
    filename: str
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[str] = None
    message: Optional[str] = None


# Job Description Models
class JobDescriptionCreate(MongoBaseModel):
    """Model for creating a job description."""
    title: str
    company: Optional[str] = None
    description: str
    domain: Optional[str] = None


class JobDescriptionDocument(MongoBaseModel):
    """Full job description document model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str
    company: Optional[str] = None
    description: str
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    domain: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class JobDescriptionResponse(MongoBaseModel):
    """Job description response model."""
    id: str
    title: str
    company: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    domain: Optional[str] = None


# Gap Analysis Models
class GapPriority(MongoBaseModel):
    """Model for a prioritized skill gap."""
    skill: str
    importance: str  # critical, important, nice_to_have
    priority: int
    reason: str
    related_skills: Optional[List[str]] = None


class GapAnalysisCreate(MongoBaseModel):
    """Model for creating a gap analysis."""
    resume_id: str
    job_description_id: str


class GapAnalysisDocument(MongoBaseModel):
    """Full gap analysis document model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    resume_id: str
    job_description_id: str
    existing_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    skill_gaps: Optional[List[Dict[str, Any]]] = None
    gap_priority: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    analysis_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class GapAnalysisResponse(MongoBaseModel):
    """Gap analysis response model."""
    id: str
    resume_id: str
    job_description_id: str
    existing_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    skill_gaps: Optional[List[Dict[str, Any]]] = None
    gap_priority: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    analysis_notes: Optional[str] = None


# Training Module Models
class ModuleContent(MongoBaseModel):
    """Model for a training module's content section."""
    section: str
    content: str


class PracticalExercise(MongoBaseModel):
    """Model for a practical exercise."""
    title: str
    description: str
    difficulty: Optional[str] = None
    estimated_time: Optional[str] = None


class CaseStudy(MongoBaseModel):
    """Model for a case study."""
    title: str
    description: str
    learning_outcomes: Optional[List[str]] = None


class Resource(MongoBaseModel):
    """Model for a learning resource."""
    title: str
    type: str  # paper, tutorial, course, video
    url: Optional[str] = None
    description: Optional[str] = None


class TrainingSubModule(MongoBaseModel):
    """Model for a sub-module within training."""
    title: str
    description: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    content: Optional[List[Dict[str, Any]]] = None
    practical_exercises: Optional[List[Dict[str, Any]]] = None
    estimated_duration: Optional[str] = None
    difficulty: Optional[str] = None


class TrainingModuleCreate(MongoBaseModel):
    """Model for creating a training module."""
    gap_analysis_id: str


class TrainingModuleDocument(MongoBaseModel):
    """Full training module document model."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    resume_id: str
    gap_analysis_id: str
    title: str
    description: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    modules: List[Dict[str, Any]] = []
    case_studies: Optional[List[Dict[str, Any]]] = None
    practical_exercises: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    status: str = "pending"  # pending, in_progress, completed
    progress: float = 0.0
    estimated_duration: Optional[str] = None
    difficulty_level: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class TrainingModuleResponse(MongoBaseModel):
    """Training module response model."""
    id: str
    title: str
    description: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    modules: List[Dict[str, Any]] = []
    case_studies: Optional[List[Dict[str, Any]]] = None
    practical_exercises: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    status: str = "pending"
    progress: float = 0.0
    estimated_duration: Optional[str] = None
    difficulty_level: Optional[str] = None

