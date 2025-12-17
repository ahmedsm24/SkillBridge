"""
API routes using MongoDB for the SkillBridge application.
Provides secure endpoints for resume analysis, gap detection, and training generation.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
import os
import io

from src.database.mongodb import get_database, get_gridfs
from src.database.mongo_models import (
    ResumeCreate, ResumeResponse,
    JobDescriptionCreate, JobDescriptionResponse,
    GapAnalysisResponse, TrainingModuleResponse
)
from src.services.resume_parser import ResumeParser
from src.services.gap_analyzer import GapAnalyzer
from src.services.training_generator import TrainingGenerator

router = APIRouter()

# Initialize services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
resume_parser = ResumeParser(openai_api_key=OPENAI_API_KEY)
gap_analyzer = GapAnalyzer(openai_api_key=OPENAI_API_KEY)
training_generator = TrainingGenerator(openai_api_key=OPENAI_API_KEY)


def validate_object_id(id_str: str) -> ObjectId:
    """Validate and convert string to ObjectId."""
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    return ObjectId(id_str)


@router.post("/resumes/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database),
    gridfs: AsyncIOMotorGridFSBucket = Depends(get_gridfs)
):
    """
    Upload and parse a resume file.
    
    - Stores the original file securely in GridFS
    - Extracts text and parses skills/experience
    - Returns extracted information
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Store file in GridFS
        file_id = await gridfs.upload_from_stream(
            file.filename,
            io.BytesIO(file_content),
            metadata={
                "content_type": file.content_type,
                "uploaded_at": datetime.utcnow().isoformat(),
                "original_filename": file.filename
            }
        )
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(file_content, file.filename)
        
        # Create resume document
        resume_doc = {
            "filename": parsed_data["filename"],
            "raw_text": parsed_data["raw_text"],
            "file_id": str(file_id),
            "parsed_data": parsed_data["parsed_data"],
            "skills": parsed_data["skills"],
            "experience": parsed_data["experience"],
            "education": parsed_data["education"],
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        result = await db.resumes.insert_one(resume_doc)
        
        return ResumeResponse(
            id=str(result.inserted_id),
            filename=resume_doc["filename"],
            skills=resume_doc["skills"],
            experience=resume_doc["experience"],
            education=resume_doc["education"],
            created_at=resume_doc["created_at"].isoformat(),
            message="Resume uploaded and parsed successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process resume: {str(e)}")


@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get resume by ID."""
    oid = validate_object_id(resume_id)
    resume = await db.resumes.find_one({"_id": oid})
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return ResumeResponse(
        id=str(resume["_id"]),
        filename=resume["filename"],
        skills=resume.get("skills"),
        experience=resume.get("experience"),
        education=resume.get("education"),
        created_at=resume["created_at"].isoformat() if resume.get("created_at") else None
    )


@router.delete("/resumes/{resume_id}")
async def delete_resume(
    resume_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    gridfs: AsyncIOMotorGridFSBucket = Depends(get_gridfs)
):
    """Delete a resume and its associated file."""
    oid = validate_object_id(resume_id)
    resume = await db.resumes.find_one({"_id": oid})
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file from GridFS if exists
    if resume.get("file_id"):
        try:
            await gridfs.delete(ObjectId(resume["file_id"]))
        except Exception:
            pass  # File may already be deleted
    
    # Delete resume document
    await db.resumes.delete_one({"_id": oid})
    
    return {"message": "Resume deleted successfully"}


@router.post("/job-descriptions", response_model=JobDescriptionResponse)
async def create_job_description(
    job_input: JobDescriptionCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new job description and extract required skills."""
    # Extract skills from job description
    job_skills = gap_analyzer.extract_job_skills(job_input.description)
    
    job_doc = {
        "title": job_input.title,
        "company": job_input.company,
        "description": job_input.description,
        "required_skills": job_skills.get("required", []),
        "preferred_skills": job_skills.get("preferred", []),
        "domain": job_input.domain,
        "created_at": datetime.utcnow()
    }
    
    result = await db.job_descriptions.insert_one(job_doc)
    
    return JobDescriptionResponse(
        id=str(result.inserted_id),
        title=job_doc["title"],
        company=job_doc["company"],
        required_skills=job_doc["required_skills"],
        preferred_skills=job_doc["preferred_skills"],
        domain=job_doc["domain"]
    )


@router.get("/job-descriptions/{job_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    job_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get job description by ID."""
    oid = validate_object_id(job_id)
    job = await db.job_descriptions.find_one({"_id": oid})
    
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    return JobDescriptionResponse(
        id=str(job["_id"]),
        title=job["title"],
        company=job.get("company"),
        required_skills=job.get("required_skills"),
        preferred_skills=job.get("preferred_skills"),
        domain=job.get("domain")
    )


@router.post("/gap-analysis", response_model=GapAnalysisResponse)
async def perform_gap_analysis(
    resume_id: str = Form(...),
    job_description_id: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Perform gap analysis between a resume and job description.
    
    Compares candidate skills against job requirements and identifies gaps.
    """
    # Validate IDs
    resume_oid = validate_object_id(resume_id)
    job_oid = validate_object_id(job_description_id)
    
    # Get resume and job description
    resume = await db.resumes.find_one({"_id": resume_oid})
    job_desc = await db.job_descriptions.find_one({"_id": job_oid})
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not job_desc:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Perform gap analysis
    gap_results = gap_analyzer.analyze_gaps(
        resume_skills=resume.get("skills") or [],
        resume_experience=resume.get("experience") or [],
        job_description=job_desc["description"],
        job_title=job_desc["title"],
        domain=job_desc.get("domain")
    )
    
    # Create gap analysis document
    gap_doc = {
        "resume_id": resume_id,
        "job_description_id": job_description_id,
        "existing_skills": gap_results["existing_skills"],
        "missing_skills": gap_results["missing_skills"],
        "skill_gaps": gap_results["skill_gaps"],
        "gap_priority": gap_results["gap_priority"],
        "confidence_score": gap_results["confidence_score"],
        "analysis_notes": gap_results["analysis_notes"],
        "created_at": datetime.utcnow()
    }
    
    result = await db.gap_analyses.insert_one(gap_doc)
    
    return GapAnalysisResponse(
        id=str(result.inserted_id),
        resume_id=resume_id,
        job_description_id=job_description_id,
        existing_skills=gap_results["existing_skills"],
        missing_skills=gap_results["missing_skills"],
        skill_gaps=gap_results["skill_gaps"],
        gap_priority=gap_results["gap_priority"],
        confidence_score=gap_results["confidence_score"],
        analysis_notes=gap_results["analysis_notes"]
    )


@router.get("/gap-analysis/{analysis_id}", response_model=GapAnalysisResponse)
async def get_gap_analysis(
    analysis_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get gap analysis by ID."""
    oid = validate_object_id(analysis_id)
    analysis = await db.gap_analyses.find_one({"_id": oid})
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")
    
    return GapAnalysisResponse(
        id=str(analysis["_id"]),
        resume_id=analysis["resume_id"],
        job_description_id=analysis["job_description_id"],
        existing_skills=analysis.get("existing_skills"),
        missing_skills=analysis.get("missing_skills"),
        skill_gaps=analysis.get("skill_gaps"),
        gap_priority=analysis.get("gap_priority"),
        confidence_score=analysis.get("confidence_score"),
        analysis_notes=analysis.get("analysis_notes")
    )


@router.post("/training-modules/generate", response_model=TrainingModuleResponse)
async def generate_training_modules(
    gap_analysis_id: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generate personalized training modules based on gap analysis.
    
    Creates a comprehensive training program targeting identified skill gaps.
    """
    oid = validate_object_id(gap_analysis_id)
    gap_analysis = await db.gap_analyses.find_one({"_id": oid})
    
    if not gap_analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")
    
    # Get job description for context
    job_oid = validate_object_id(gap_analysis["job_description_id"])
    job_desc = await db.job_descriptions.find_one({"_id": job_oid})
    
    if not job_desc:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Prepare gap analysis data
    gap_data = {
        "existing_skills": gap_analysis.get("existing_skills") or [],
        "missing_skills": gap_analysis.get("missing_skills") or [],
        "skill_gaps": gap_analysis.get("skill_gaps") or [],
        "gap_priority": gap_analysis.get("gap_priority") or []
    }
    
    # Generate training modules
    training_data = training_generator.generate_training_modules(
        gap_analysis=gap_data,
        job_title=job_desc["title"],
        domain=job_desc.get("domain") or "general",
        existing_skills=gap_analysis.get("existing_skills") or []
    )
    
    # Create training module document
    training_doc = {
        "resume_id": gap_analysis["resume_id"],
        "gap_analysis_id": gap_analysis_id,
        "title": training_data.get("title", "Training Program"),
        "description": training_data.get("description"),
        "learning_objectives": training_data.get("learning_objectives"),
        "modules": training_data.get("modules", []),
        "case_studies": training_data.get("case_studies"),
        "practical_exercises": training_data.get("practical_exercises"),
        "resources": training_data.get("resources"),
        "status": "pending",
        "progress": 0.0,
        "estimated_duration": training_data.get("estimated_duration"),
        "difficulty_level": "intermediate",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.training_modules.insert_one(training_doc)
    
    return TrainingModuleResponse(
        id=str(result.inserted_id),
        title=training_doc["title"],
        description=training_doc["description"],
        learning_objectives=training_doc["learning_objectives"],
        modules=training_doc["modules"],
        case_studies=training_doc["case_studies"],
        practical_exercises=training_doc["practical_exercises"],
        resources=training_doc["resources"],
        status=training_doc["status"],
        progress=training_doc["progress"],
        estimated_duration=training_doc["estimated_duration"],
        difficulty_level=training_doc["difficulty_level"]
    )


@router.get("/training-modules/{module_id}", response_model=TrainingModuleResponse)
async def get_training_module(
    module_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get training module by ID."""
    oid = validate_object_id(module_id)
    module = await db.training_modules.find_one({"_id": oid})
    
    if not module:
        raise HTTPException(status_code=404, detail="Training module not found")
    
    return TrainingModuleResponse(
        id=str(module["_id"]),
        title=module["title"],
        description=module.get("description"),
        learning_objectives=module.get("learning_objectives"),
        modules=module.get("modules", []),
        case_studies=module.get("case_studies"),
        practical_exercises=module.get("practical_exercises"),
        resources=module.get("resources"),
        status=module.get("status", "pending"),
        progress=module.get("progress", 0.0),
        estimated_duration=module.get("estimated_duration"),
        difficulty_level=module.get("difficulty_level")
    )


@router.get("/training-modules")
async def list_training_modules(
    resume_id: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List all training modules, optionally filtered by resume."""
    query = {}
    if resume_id:
        query["resume_id"] = resume_id
    
    cursor = db.training_modules.find(query).sort("created_at", -1)
    modules = await cursor.to_list(length=100)
    
    return [
        {
            "id": str(m["_id"]),
            "title": m["title"],
            "status": m.get("status", "pending"),
            "progress": m.get("progress", 0.0),
            "estimated_duration": m.get("estimated_duration"),
            "created_at": m["created_at"].isoformat() if m.get("created_at") else None
        }
        for m in modules
    ]


@router.patch("/training-modules/{module_id}/progress")
async def update_module_progress(
    module_id: str,
    progress: float = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update training module progress."""
    oid = validate_object_id(module_id)
    
    if progress < 0 or progress > 100:
        raise HTTPException(status_code=400, detail="Progress must be between 0 and 100")
    
    status = "completed" if progress >= 100 else "in_progress" if progress > 0 else "pending"
    
    result = await db.training_modules.update_one(
        {"_id": oid},
        {
            "$set": {
                "progress": progress,
                "status": status,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Training module not found")
    
    return {"message": "Progress updated", "progress": progress, "status": status}

