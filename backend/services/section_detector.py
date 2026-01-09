"""
Resume Section Detection Service

Deterministic rules-based section detection.
"""

import re
from typing import Dict, List, Tuple


# Section header patterns
SECTION_PATTERNS = {
    "summary": [
        r"(?i)^(professional\s+)?summary\b",
        r"(?i)^(career\s+)?objective\b",
        r"(?i)^profile\b",
        r"(?i)^about(\s+me)?\b",
        r"(?i)^overview\b",
    ],
    "experience": [
        r"(?i)^(work\s+)?experience\b",
        r"(?i)^(employment|work)\s+history\b",
        r"(?i)^professional\s+experience\b",
        r"(?i)^career\s+history\b",
    ],
    "skills": [
        r"(?i)^(technical\s+)?skills\b",
        r"(?i)^technologies\b",
        r"(?i)^competencies\b",
        r"(?i)^expertise\b",
        r"(?i)^tools\s*(and|&)\s*technologies\b",
    ],
    "education": [
        r"(?i)^education\b",
        r"(?i)^academic\s+(background|qualifications)\b",
        r"(?i)^degrees?\b",
        r"(?i)^qualifications\b",
    ],
    "projects": [
        r"(?i)^(personal\s+)?projects\b",
        r"(?i)^portfolio\b",
        r"(?i)^key\s+projects\b",
    ],
    "certifications": [
        r"(?i)^certifications?\b",
        r"(?i)^licenses?\s*(and|&)?\s*certifications?\b",
        r"(?i)^professional\s+certifications?\b",
    ],
}


def detect_sections(text: str) -> Dict[str, str]:
    """
    Detect resume sections from text.
    
    Returns dict with section names as keys and content as values.
    """
    lines = text.split('\n')
    
    # Find section boundaries
    section_markers: List[Tuple[int, str]] = []
    
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            continue
        
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, line_clean):
                    section_markers.append((i, section_name))
                    break
    
    # Extract section content
    sections = {}
    
    for idx, (line_num, section_name) in enumerate(section_markers):
        # Find end of section (next section or end of document)
        if idx + 1 < len(section_markers):
            end_line = section_markers[idx + 1][0]
        else:
            end_line = len(lines)
        
        # Extract content (skip header line)
        content_lines = lines[line_num + 1:end_line]
        content = '\n'.join(line for line in content_lines if line.strip())
        
        sections[section_name] = content.strip()
    
    # Handle case where no sections detected
    if not sections:
        # Try to infer from content
        sections = _infer_sections(text)
    
    # Ensure required sections exist
    for required in ["summary", "experience", "skills", "education"]:
        if required not in sections:
            sections[required] = ""
    
    return sections


def _infer_sections(text: str) -> Dict[str, str]:
    """
    Infer sections when no clear headers found.
    Uses content patterns to guess sections.
    """
    sections = {}
    lines = text.split('\n')
    
    # Look for experience-like content (company names, dates)
    experience_lines = []
    skill_lines = []
    other_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Date pattern suggests experience
        if re.search(r'\b(19|20)\d{2}\b', line):
            experience_lines.append(line)
        # Skill-like content (comma-separated tech terms)
        elif re.search(r'(Python|Java|SQL|AWS|React|Node)', line, re.I):
            skill_lines.append(line)
        else:
            other_lines.append(line)
    
    if experience_lines:
        sections["experience"] = '\n'.join(experience_lines)
    if skill_lines:
        sections["skills"] = '\n'.join(skill_lines)
    if other_lines:
        # First few lines likely summary
        sections["summary"] = '\n'.join(other_lines[:5])
    
    return sections


def format_section_for_display(section_name: str, content: str) -> str:
    """Format section for display."""
    title = section_name.replace('_', ' ').title()
    return f"## {title}\n\n{content}"
