"""
Job Description Extraction API
"""

import uuid
import re
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.jd_intelligence import extract_jd_intelligence

router = APIRouter()

# In-memory store
jd_store: dict = {}


class JDInput(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


class JDResponse(BaseModel):
    jd_id: str
    role: str
    seniority: str
    hard_skills: list[str]
    soft_skills: list[str]
    tools: list[str]
    keywords: dict


@router.post("/jd/extract")
async def extract_jd(input_data: JDInput):
    """
    Extract job description from text or URL.
    Cleans noise and extracts key information.
    """
    if not input_data.text and not input_data.url:
        raise HTTPException(400, "Provide either text or URL")
    
    jd_id = f"jd-{uuid.uuid4().hex[:8]}"
    
    # Get JD text
    if input_data.url:
        # For MVP, just require text input
        raise HTTPException(400, "URL extraction not yet supported. Please paste JD text.")
    
    raw_text = input_data.text.strip()
    
    if len(raw_text) < 100:
        raise HTTPException(400, "Job description too short")
    
    # Clean JD (remove noise sections)
    cleaned_text = _clean_jd(raw_text)
    
    # Extract intelligence
    intelligence = extract_jd_intelligence(cleaned_text)
    
    # Store
    jd_store[jd_id] = {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        **intelligence,
    }
    
    return {
        "jd_id": jd_id,
        **intelligence,
    }


@router.get("/jd/{jd_id}")
async def get_jd(jd_id: str):
    """Get extracted JD by ID."""
    if jd_id not in jd_store:
        raise HTTPException(404, "JD not found")
    
    return {
        "jd_id": jd_id,
        **jd_store[jd_id],
    }


def _clean_jd(text: str) -> str:
    """
    Remove noise sections from JD:
    - Benefits/perks
    - Company about
    - Equal opportunity statements
    - Application instructions
    """
    lines = text.split('\n')
    cleaned_lines = []
    skip_section = False
    
    noise_patterns = [
        r'(?i)^(benefits|perks|what we offer)',
        r'(?i)^(about us|about the company|who we are)',
        r'(?i)^(equal opportunity|eeo|diversity)',
        r'(?i)^(how to apply|to apply)',
        r'(?i)^(salary|compensation|pay range)',
    ]
    
    for line in lines:
        # Check if entering noise section
        for pattern in noise_patterns:
            if re.match(pattern, line.strip()):
                skip_section = True
                break
        
        # Reset on new major section
        if re.match(r'^[A-Z][A-Za-z\s]+:?\s*$', line.strip()) and len(line.strip()) < 50:
            if not any(re.match(p, line.strip()) for p in noise_patterns):
                skip_section = False
        
        if not skip_section:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()
