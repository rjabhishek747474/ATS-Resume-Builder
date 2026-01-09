"""
Gap Analysis Service

Compares resume against JD to identify gaps.
"""

import re
from typing import Dict, List, Set


def analyze_gaps(resume_sections: Dict[str, str], jd_data: Dict) -> Dict:
    """
    Analyze gaps between resume and JD.
    
    Returns:
        - critical: Skills that are likely ATS filter requirements
        - optional: Nice-to-have skills for ranking
        - weak_bullets: Experience bullets that could be improved
    """
    # Get resume skills
    resume_skills = _extract_resume_skills(resume_sections)
    resume_text = ' '.join(resume_sections.values()).lower()
    
    # Get JD requirements
    jd_primary = set(s.lower() for s in jd_data.get("keywords", {}).get("primary", []))
    jd_secondary = set(s.lower() for s in jd_data.get("keywords", {}).get("secondary", []))
    jd_hard_skills = set(s.lower() for s in jd_data.get("hard_skills", []))
    
    # Find missing skills
    missing_primary = jd_primary - resume_skills
    missing_secondary = jd_secondary - resume_skills
    missing_hard = jd_hard_skills - resume_skills
    
    # Critical gaps: primary keywords not in resume
    critical = list(missing_primary | (missing_hard & jd_primary))
    
    # Optional gaps: secondary keywords not in resume
    optional = list(missing_secondary | (missing_hard - jd_primary))
    
    # Find weak bullets
    weak_bullets = _identify_weak_bullets(resume_sections.get("experience", ""))
    
    # Skills that match
    matched = resume_skills & (jd_hard_skills | jd_primary | jd_secondary)
    
    return {
        "critical": critical[:10],
        "optional": optional[:10],
        "weak_bullets": weak_bullets,
        "matched_skills": list(matched)[:15],
        "missing_count": len(missing_primary) + len(missing_hard),
    }


def _extract_resume_skills(sections: Dict[str, str]) -> Set[str]:
    """Extract skills mentioned in resume."""
    all_text = ' '.join(sections.values()).lower()
    
    # Common tech skills
    skills = set()
    
    skill_patterns = [
        r'\b(python|java|javascript|typescript|c\+\+|c#|go|rust|ruby|php)\b',
        r'\b(react|angular|vue|node\.?js|django|flask|spring|\.net)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|terraform)\b',
        r'\b(postgresql|mysql|mongodb|redis|elasticsearch)\b',
        r'\b(git|linux|agile|scrum|ci/cd)\b',
        r'\b(machine learning|deep learning|data science)\b',
        r'\b(sql|html|css|rest|api|microservices)\b',
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, all_text, re.I)
        skills.update(m.lower() for m in matches)
    
    return skills


def _identify_weak_bullets(experience_text: str) -> List[Dict]:
    """
    Identify weak experience bullets that could be improved.
    
    Weak indicators:
    - No action verb at start
    - No metrics/impact
    - Too short
    - Passive voice
    """
    weak = []
    
    # Split into bullet points
    bullets = re.split(r'\n[-•]\s*|\n\d+\.\s*', experience_text)
    
    for i, bullet in enumerate(bullets):
        bullet = bullet.strip()
        if not bullet or len(bullet) < 20:
            continue
        
        issues = []
        
        # Check for action verb
        action_verbs = r'^(led|developed|built|created|managed|designed|implemented|achieved|increased|reduced|delivered|launched|optimized)'
        if not re.match(action_verbs, bullet, re.I):
            issues.append("missing_action_verb")
        
        # Check for metrics
        if not re.search(r'\d+%|\d+x|\$\d+|\d+ (users|customers|team|projects)', bullet, re.I):
            issues.append("no_metrics")
        
        # Check for passive voice
        passive_patterns = r'\b(was|were|been|being)\s+\w+ed\b'
        if re.search(passive_patterns, bullet, re.I):
            issues.append("passive_voice")
        
        # Too short
        if len(bullet) < 50:
            issues.append("too_short")
        
        if issues:
            weak.append({
                "index": i,
                "text": bullet[:100] + "..." if len(bullet) > 100 else bullet,
                "issues": issues,
            })
    
    return weak[:5]  # Return top 5 weakest
