"""
API routes for the Resume-to-Training Module Generator.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import os

from src.database.models import Resume, JobDescription, GapAnalysis, TrainingModule
from src.database.database import SessionLocal
from src.services.resume_parser import ResumeParser
from src.services.gap_analyzer import GapAnalyzer
from src.services.training_generator import TrainingGenerator

router = APIRouter()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
resume_parser = ResumeParser(openai_api_key=OPENAI_API_KEY)
gap_analyzer = GapAnalyzer(openai_api_key=OPENAI_API_KEY)
training_generator = TrainingGenerator(openai_api_key=OPENAI_API_KEY)


# Request/Response models
class JobDescriptionInput(BaseModel):
    title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    description: str = Field(..., description="Job description text")
    domain: Optional[str] = Field(None, description="Industry domain (e.g., biotech, finance)")


class ProjectInput(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description and goals")
    organization: Optional[str] = Field(None, description="Organization or company name")
    team_role: str = Field(..., description="Role of the person being trained (e.g., ML Intern, Backend Developer)")
    tech_stack: Optional[List[str]] = Field(default=[], description="Technologies used in the project")
    goals: Optional[List[str]] = Field(default=[], description="Project goals and objectives")
    timeline: Optional[str] = Field(None, description="Expected timeline for onboarding")


class TrainingModuleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    learning_objectives: Optional[List[str]]
    modules: List[Dict[str, Any]]
    case_studies: Optional[List[Dict[str, Any]]]
    practical_exercises: Optional[List[Dict[str, Any]]]
    resources: Optional[List[Dict[str, Any]]]
    status: str
    progress: float
    estimated_duration: Optional[str]
    difficulty_level: Optional[str]


@router.post("/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a resume file.
    
    Supports PDF and text files.
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(file_content, file.filename)
        
        # Save to database
        resume = Resume(
            filename=parsed_data["filename"],
            raw_text=parsed_data["raw_text"],
            parsed_data=parsed_data["parsed_data"],
            skills=parsed_data["skills"],
            experience=parsed_data["experience"],
            education=parsed_data["education"]
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return {
            "id": resume.id,
            "filename": resume.filename,
            "skills": resume.skills,
            "experience": resume.experience,
            "education": resume.education,
            "message": "Resume uploaded and parsed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process resume: {str(e)}")


@router.get("/resumes/{resume_id}")
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Get resume by ID"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "id": resume.id,
        "filename": resume.filename,
        "skills": resume.skills,
        "experience": resume.experience,
        "education": resume.education,
        "created_at": resume.created_at.isoformat()
    }


@router.post("/job-descriptions")
async def create_job_description(
    job_input: JobDescriptionInput,
    db: Session = Depends(get_db)
):
    """Create a new job description"""
    # Extract skills from job description
    job_skills = gap_analyzer.extract_job_skills(job_input.description)
    
    job_desc = JobDescription(
        title=job_input.title,
        company=job_input.company,
        description=job_input.description,
        required_skills=job_skills.get("required", []),
        preferred_skills=job_skills.get("preferred", []),
        domain=job_input.domain
    )
    db.add(job_desc)
    db.commit()
    db.refresh(job_desc)
    
    return {
        "id": job_desc.id,
        "title": job_desc.title,
        "company": job_desc.company,
        "required_skills": job_desc.required_skills,
        "preferred_skills": job_desc.preferred_skills,
        "domain": job_desc.domain
    }


@router.post("/gap-analysis")
async def perform_gap_analysis(
    resume_id: int = Form(...),
    job_description_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Perform gap analysis between a resume and job description.
    """
    # Get resume and job description
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    job_desc = db.query(JobDescription).filter(JobDescription.id == job_description_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not job_desc:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Perform gap analysis
    gap_results = gap_analyzer.analyze_gaps(
        resume_skills=resume.skills or [],
        resume_experience=resume.experience or [],
        job_description=job_desc.description,
        job_title=job_desc.title,
        domain=job_desc.domain
    )
    
    # Save gap analysis
    gap_analysis = GapAnalysis(
        resume_id=resume_id,
        job_description_id=job_description_id,
        existing_skills=gap_results["existing_skills"],
        missing_skills=gap_results["missing_skills"],
        skill_gaps=gap_results["skill_gaps"],
        gap_priority=gap_results["gap_priority"],
        confidence_score=gap_results["confidence_score"],
        analysis_notes=gap_results["analysis_notes"]
    )
    db.add(gap_analysis)
    db.commit()
    db.refresh(gap_analysis)
    
    return {
        "id": gap_analysis.id,
        "resume_id": resume_id,
        "job_description_id": job_description_id,
        "existing_skills": gap_results["existing_skills"],
        "missing_skills": gap_results["missing_skills"],
        "skill_gaps": gap_results["skill_gaps"],
        "gap_priority": gap_results["gap_priority"],
        "confidence_score": gap_results["confidence_score"],
        "analysis_notes": gap_results["analysis_notes"]
    }


@router.post("/training-modules/generate")
async def generate_training_modules(
    gap_analysis_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Generate training modules based on gap analysis.
    """
    # Get gap analysis
    gap_analysis = db.query(GapAnalysis).filter(GapAnalysis.id == gap_analysis_id).first()
    if not gap_analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")
    
    # Get related resume and job description
    resume = gap_analysis.resume
    job_desc = gap_analysis.job_description
    
    # Prepare gap analysis data
    gap_data = {
        "existing_skills": gap_analysis.existing_skills or [],
        "missing_skills": gap_analysis.missing_skills or [],
        "skill_gaps": gap_analysis.skill_gaps or [],
        "gap_priority": gap_analysis.gap_priority or []
    }
    
    # Generate training modules
    training_data = training_generator.generate_training_modules(
        gap_analysis=gap_data,
        job_title=job_desc.title,
        domain=job_desc.domain or "general",
        existing_skills=gap_analysis.existing_skills or []
    )
    
    # Save training module
    training_module = TrainingModule(
        resume_id=gap_analysis.resume_id,
        gap_analysis_id=gap_analysis_id,
        title=training_data.get("title", "Training Program"),
        description=training_data.get("description"),
        learning_objectives=training_data.get("learning_objectives"),
        modules=training_data.get("modules", []),
        case_studies=training_data.get("case_studies"),
        practical_exercises=training_data.get("practical_exercises"),
        resources=training_data.get("resources"),
        estimated_duration=training_data.get("estimated_duration"),
        difficulty_level="intermediate"
    )
    db.add(training_module)
    db.commit()
    db.refresh(training_module)
    
    return {
        "id": training_module.id,
        "title": training_module.title,
        "description": training_module.description,
        "learning_objectives": training_module.learning_objectives,
        "modules": training_module.modules,
        "case_studies": training_module.case_studies,
        "practical_exercises": training_module.practical_exercises,
        "resources": training_module.resources,
        "status": training_module.status,
        "progress": training_module.progress,
        "estimated_duration": training_module.estimated_duration,
        "difficulty_level": training_module.difficulty_level
    }


@router.get("/training-modules/{module_id}")
async def get_training_module(module_id: int, db: Session = Depends(get_db)):
    """Get training module by ID"""
    module = db.query(TrainingModule).filter(TrainingModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Training module not found")
    
    return {
        "id": module.id,
        "title": module.title,
        "description": module.description,
        "learning_objectives": module.learning_objectives,
        "modules": module.modules,
        "case_studies": module.case_studies,
        "practical_exercises": module.practical_exercises,
        "resources": module.resources,
        "status": module.status,
        "progress": module.progress,
        "estimated_duration": module.estimated_duration,
        "difficulty_level": module.difficulty_level,
        "created_at": module.created_at.isoformat()
    }


@router.get("/training-modules")
async def list_training_modules(
    resume_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all training modules, optionally filtered by resume"""
    query = db.query(TrainingModule)
    if resume_id:
        query = query.filter(TrainingModule.resume_id == resume_id)
    
    modules = query.all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "status": m.status,
            "progress": m.progress,
            "estimated_duration": m.estimated_duration,
            "created_at": m.created_at.isoformat()
        }
        for m in modules
    ]


@router.post("/projects/training")
async def generate_project_training(
    resume_id: int = Form(...),
    gap_analysis_id: int = Form(...),
    project_name: str = Form(...),
    project_description: str = Form(...),
    team_role: str = Form(...),
    organization: str = Form(None),
    tech_stack: str = Form(""),  # Comma-separated
    goals: str = Form(""),  # Comma-separated
    timeline: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Generate project-specific training modules.
    
    This creates a two-phase training program:
    1. Foundation Phase: Fill skill gaps from resume analysis
    2. Project Phase: Project-specific skills and knowledge
    """
    # Get resume and gap analysis
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    gap_analysis = db.query(GapAnalysis).filter(GapAnalysis.id == gap_analysis_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not gap_analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")
    
    # Parse comma-separated values
    tech_stack_list = [t.strip() for t in tech_stack.split(",") if t.strip()] if tech_stack else []
    goals_list = [g.strip() for g in goals.split(",") if g.strip()] if goals else []
    
    # Prepare project info
    project_info = {
        "name": project_name,
        "description": project_description,
        "organization": organization or "",
        "team_role": team_role,
        "tech_stack": tech_stack_list,
        "goals": goals_list,
        "timeline": timeline or ""
    }
    
    # Prepare gap analysis data
    gap_data = {
        "existing_skills": gap_analysis.existing_skills or [],
        "missing_skills": gap_analysis.missing_skills or [],
        "skill_gaps": gap_analysis.skill_gaps or [],
        "gap_priority": gap_analysis.gap_priority or []
    }
    
    # Generate project-specific training
    training_data = training_generator.generate_project_training(
        gap_analysis=gap_data,
        project_info=project_info,
        existing_skills=resume.skills or []
    )
    
    # Save training module
    training_module = TrainingModule(
        resume_id=resume_id,
        gap_analysis_id=gap_analysis_id,
        title=training_data.get("title", f"Training for {project_name}"),
        description=training_data.get("description"),
        learning_objectives=training_data.get("learning_objectives"),
        modules=training_data.get("modules", []),
        case_studies=training_data.get("case_studies"),
        practical_exercises=training_data.get("practical_exercises"),
        resources=training_data.get("resources"),
        estimated_duration=training_data.get("estimated_duration"),
        difficulty_level="intermediate"
    )
    db.add(training_module)
    db.commit()
    db.refresh(training_module)
    
    return {
        "id": training_module.id,
        "title": training_module.title,
        "description": training_module.description,
        "team_role": training_data.get("team_role"),
        "project_name": training_data.get("project_name"),
        "organization": training_data.get("organization"),
        "phases": training_data.get("phases"),
        "learning_objectives": training_module.learning_objectives,
        "modules": training_module.modules,
        "case_studies": training_module.case_studies,
        "resources": training_module.resources,
        "milestones": training_data.get("milestones"),
        "estimated_duration": training_module.estimated_duration,
        "status": training_module.status
    }

