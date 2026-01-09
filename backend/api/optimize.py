"""
Resume Optimization API
"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.resume import resume_store
from api.jd import jd_store
from services.gap_analyzer import analyze_gaps
from services.rewriter import rewrite_resume
from services.scorer import calculate_ats_score

router = APIRouter()

# Job store for async processing
job_store: dict = {}


class OptimizeRequest(BaseModel):
    resume_id: str
    jd_id: str


@router.post("/optimize")
async def start_optimization(request: OptimizeRequest):
    """
    Start resume optimization job.
    """
    # Validate inputs
    if request.resume_id not in resume_store:
        raise HTTPException(404, "Resume not found")
    if request.jd_id not in jd_store:
        raise HTTPException(404, "JD not found")
    
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    
    # Get data
    resume_data = resume_store[request.resume_id]
    jd_data = jd_store[request.jd_id]
    
    # For MVP, process synchronously (add Celery later)
    job_store[job_id] = {
        "status": "processing",
        "progress": 0,
        "step": "Starting optimization",
        "resume_id": request.resume_id,
        "jd_id": request.jd_id,
    }
    
    try:
        # Step 1: Gap Analysis (20%)
        job_store[job_id]["step"] = "Analyzing gaps"
        job_store[job_id]["progress"] = 20
        
        gaps = analyze_gaps(resume_data["sections"], jd_data)
        
        # Step 2: Rewrite (60%)
        job_store[job_id]["step"] = "Rewriting resume"
        job_store[job_id]["progress"] = 40
        
        optimized_sections = rewrite_resume(
            resume_data["sections"],
            jd_data,
            gaps,
        )
        
        job_store[job_id]["progress"] = 70
        
        # Step 3: Score (90%)
        job_store[job_id]["step"] = "Calculating ATS score"
        job_store[job_id]["progress"] = 90
        
        score_result = calculate_ats_score(optimized_sections, jd_data)
        
        # Complete
        job_store[job_id] = {
            "status": "completed",
            "progress": 100,
            "step": "Complete",
            "result": {
                "optimized_resume": optimized_sections,
                "ats_score": score_result["score"],
                "improvements": score_result["improvements"],
                "remaining_gaps": gaps["optional"],
            },
        }
        
    except Exception as e:
        job_store[job_id] = {
            "status": "failed",
            "error": str(e),
        }
    
    return {
        "job_id": job_id,
        "status": job_store[job_id]["status"],
    }
