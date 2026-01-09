"""
ATS Scoring Service

Calculates ATS compatibility score for a resume.
"""

import re
from typing import Dict, List, Set


def calculate_ats_score(resume_sections: Dict[str, str], jd_data: Dict) -> Dict:
    """
    Calculate ATS compatibility score.
    
    Scoring factors:
    - Keyword match (40%)
    - Section completeness (20%)
    - Format compatibility (20%)
    - Content quality (20%)
    """
    scores = {}
    improvements = []
    
    # 1. Keyword match (40%)
    keyword_score, keyword_details = _score_keywords(resume_sections, jd_data)
    scores["keywords"] = keyword_score
    improvements.extend(keyword_details)
    
    # 2. Section completeness (20%)
    section_score, section_details = _score_sections(resume_sections)
    scores["sections"] = section_score
    improvements.extend(section_details)
    
    # 3. Format compatibility (20%)
    format_score, format_details = _score_format(resume_sections)
    scores["format"] = format_score
    improvements.extend(format_details)
    
    # 4. Content quality (20%)
    quality_score, quality_details = _score_quality(resume_sections)
    scores["quality"] = quality_score
    improvements.extend(quality_details)
    
    # Calculate weighted total
    total_score = (
        scores["keywords"] * 0.40 +
        scores["sections"] * 0.20 +
        scores["format"] * 0.20 +
        scores["quality"] * 0.20
    )
    
    return {
        "score": round(total_score),
        "breakdown": scores,
        "improvements": [i for i in improvements if i.startswith("+")],
        "remaining_gaps": [i for i in improvements if i.startswith("-")],
    }


def _score_keywords(sections: Dict[str, str], jd_data: Dict) -> tuple:
    """Score keyword matching."""
    all_text = ' '.join(sections.values()).lower()
    
    # Get target keywords
    primary = jd_data.get("keywords", {}).get("primary", [])
    secondary = jd_data.get("keywords", {}).get("secondary", [])
    hard_skills = jd_data.get("hard_skills", [])
    
    all_keywords = set(primary + secondary + hard_skills)
    
    if not all_keywords:
        return 100, []
    
    # Count matches
    matched = 0
    matched_keywords = []
    missing_keywords = []
    
    for keyword in all_keywords:
        if keyword.lower() in all_text:
            matched += 1
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    score = int((matched / len(all_keywords)) * 100)
    
    details = []
    if matched_keywords:
        details.append(f"+ Matched {len(matched_keywords)} keywords: {', '.join(matched_keywords[:5])}")
    if missing_keywords:
        details.append(f"- Missing keywords: {', '.join(missing_keywords[:5])}")
    
    return score, details


def _score_sections(sections: Dict[str, str]) -> tuple:
    """Score section completeness."""
    required = ["summary", "experience", "skills", "education"]
    present = 0
    details = []
    
    for section in required:
        if sections.get(section) and len(sections[section]) > 20:
            present += 1
            details.append(f"+ {section.title()} section present")
        else:
            details.append(f"- Missing or empty {section.title()} section")
    
    score = int((present / len(required)) * 100)
    return score, details


def _score_format(sections: Dict[str, str]) -> tuple:
    """Score ATS format compatibility."""
    all_text = ' '.join(sections.values())
    score = 100
    details = []
    
    # Check for problematic characters
    special_chars = re.findall(r'[│║╔╗╚╝═─┌┐└┘├┤┬┴┼]', all_text)
    if special_chars:
        score -= 20
        details.append("- Contains special characters that may break ATS parsing")
    else:
        details.append("+ No problematic special characters")
    
    # Check for images/tables indicators
    if re.search(r'\[image\]|\[table\]', all_text, re.I):
        score -= 15
        details.append("- Contains images or tables (not ATS-friendly)")
    
    # Check for reasonable length
    word_count = len(all_text.split())
    if word_count < 200:
        score -= 15
        details.append("- Resume too short (under 200 words)")
    elif word_count > 1500:
        score -= 10
        details.append("- Resume may be too long (over 1500 words)")
    else:
        details.append("+ Good resume length")
    
    return max(0, score), details


def _score_quality(sections: Dict[str, str]) -> tuple:
    """Score content quality."""
    experience = sections.get("experience", "")
    score = 100
    details = []
    
    if not experience:
        return 50, ["- No experience section to evaluate"]
    
    # Check for action verbs
    action_verbs = r'\b(led|developed|built|created|managed|designed|implemented|achieved|increased|reduced|delivered|launched|optimized)\b'
    action_count = len(re.findall(action_verbs, experience, re.I))
    
    if action_count >= 5:
        details.append(f"+ Strong use of action verbs ({action_count} found)")
    elif action_count >= 2:
        details.append(f"+ Some action verbs used ({action_count} found)")
        score -= 10
    else:
        details.append("- Few action verbs - bullets may be weak")
        score -= 25
    
    # Check for metrics
    metrics = re.findall(r'\d+%|\$[\d,]+|\d+ (users|customers|projects|team members)', experience, re.I)
    
    if metrics:
        details.append(f"+ Contains quantifiable achievements ({len(metrics)} metrics)")
    else:
        details.append("- No metrics/numbers to quantify impact")
        score -= 20
    
    # Check for bullet points
    bullet_count = len(re.findall(r'\n[-•]\s', experience))
    
    if bullet_count >= 5:
        details.append(f"+ Well-structured with {bullet_count} bullet points")
    else:
        details.append("- Could use more bullet points for readability")
        score -= 10
    
    return max(0, score), details
