"""
Resume Upload & Parsing API
"""

import os
import uuid
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel

from config import get_settings
from services.parser import extract_text_from_pdf, extract_text_from_txt
from services.section_detector import detect_sections

settings = get_settings()
router = APIRouter()

# In-memory store (replace with DB in production)
resume_store: dict = {}


class ResumeTextInput(BaseModel):
    text: str


class ResumeSection(BaseModel):
    content: str
    start_line: int
    end_line: int


class ParsedResume(BaseModel):
    resume_id: str
    raw_text: str
    sections: dict


@router.post("/resume/upload")
async def upload_resume(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    """
    Upload resume file (PDF/TXT) or raw text.
    Returns parsed resume with detected sections.
    """
    if not file and not text:
        raise HTTPException(400, "Provide either a file or text")
    
    resume_id = f"res-{uuid.uuid4().hex[:8]}"
    raw_text = ""
    
    if file:
        # Validate file
        if file.size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(400, f"File too large. Max {settings.max_file_size_mb}MB")
        
        filename = file.filename.lower()
        if not (filename.endswith('.pdf') or filename.endswith('.txt')):
            raise HTTPException(400, "Only PDF and TXT files are supported")
        
        # Read file
        content = await file.read()
        
        # Extract text
        if filename.endswith('.pdf'):
            raw_text = extract_text_from_pdf(content)
        else:
            raw_text = extract_text_from_txt(content)
    else:
        raw_text = text.strip()
    
    if not raw_text:
        raise HTTPException(400, "Could not extract text from resume")
    
    # Detect sections
    sections = detect_sections(raw_text)
    
    # Store
    resume_store[resume_id] = {
        "raw_text": raw_text,
        "sections": sections,
    }
    
    return {
        "resume_id": resume_id,
        "sections": sections,
        "raw_text": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
    }


@router.get("/resume/{resume_id}")
async def get_resume(resume_id: str):
    """Get parsed resume by ID."""
    if resume_id not in resume_store:
        raise HTTPException(404, "Resume not found")
    
    return {
        "resume_id": resume_id,
        **resume_store[resume_id],
    }


@router.put("/resume/{resume_id}/sections")
async def update_sections(resume_id: str, sections: dict):
    """Update resume sections (user edits)."""
    if resume_id not in resume_store:
        raise HTTPException(404, "Resume not found")
    
    resume_store[resume_id]["sections"] = sections
    return {"status": "updated", "resume_id": resume_id}
