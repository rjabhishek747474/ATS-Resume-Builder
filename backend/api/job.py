"""
Job Status API
"""

from fastapi import APIRouter, HTTPException

from api.optimize import job_store

router = APIRouter()


@router.get("/job/{job_id}/status")
async def get_job_status(job_id: str):
    """Get optimization job status."""
    if job_id not in job_store:
        raise HTTPException(404, "Job not found")
    
    job = job_store[job_id]
    
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "progress": job.get("progress", 0),
        "step": job.get("step", ""),
    }


@router.get("/job/{job_id}/result")
async def get_job_result(job_id: str):
    """Get optimization job result."""
    if job_id not in job_store:
        raise HTTPException(404, "Job not found")
    
    job = job_store[job_id]
    
    if job.get("status") != "completed":
        raise HTTPException(400, f"Job not completed. Status: {job.get('status')}")
    
    return {
        "job_id": job_id,
        **job.get("result", {}),
    }
