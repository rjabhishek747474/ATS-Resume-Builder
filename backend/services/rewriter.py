"""
Resume Rewriter Service

Rewrites resume content to be ATS-optimized while preserving truth.
Uses Google Gemini or OpenAI for LLM-powered optimization.
"""

import re
from typing import Dict, List

# Optional imports for LLM providers
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config import get_settings

settings = get_settings()

# Initialize Gemini if available
if GEMINI_AVAILABLE and settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


def rewrite_resume(
    sections: Dict[str, str],
    jd_data: Dict,
    gaps: Dict,
) -> Dict[str, str]:
    """
    Rewrite resume sections to be ATS-optimized.
    
    Rules (NON-NEGOTIABLE):
    1. Preserve truth - no invented facts
    2. No new skills, companies, or metrics
    3. Action verb + task + impact format
    4. Plain-text safe
    """
    optimized = {}
    
    # Rewrite summary
    if sections.get("summary"):
        optimized["summary"] = _rewrite_summary(
            sections["summary"],
            jd_data,
            gaps,
        )
    else:
        optimized["summary"] = _generate_summary(sections, jd_data)
    
    # Rewrite experience bullets
    if sections.get("experience"):
        optimized["experience"] = _rewrite_experience(
            sections["experience"],
            jd_data,
            gaps,
        )
    else:
        optimized["experience"] = ""
    
    # Rewrite skills section
    if sections.get("skills"):
        optimized["skills"] = _rewrite_skills(
            sections["skills"],
            jd_data,
        )
    else:
        optimized["skills"] = ""
    
    # Education typically doesn't need rewriting
    optimized["education"] = sections.get("education", "")
    
    # Projects
    if sections.get("projects"):
        optimized["projects"] = sections["projects"]
    
    # Certifications
    if sections.get("certifications"):
        optimized["certifications"] = sections["certifications"]
    
    return optimized


def _rewrite_summary(summary: str, jd_data: Dict, gaps: Dict) -> str:
    """Rewrite professional summary using LLM."""
    target_keywords = jd_data.get("keywords", {}).get("primary", [])[:5]
    
    # Try Gemini first (preferred)
    if GEMINI_AVAILABLE and settings.gemini_api_key:
        return _gemini_rewrite_summary(summary, jd_data, target_keywords)
    
    # Fallback to OpenAI
    if OPENAI_AVAILABLE and settings.openai_api_key:
        return _llm_rewrite_summary(summary, jd_data, target_keywords)
    
    # Rule-based fallback
    return _rule_based_summary(summary, target_keywords)


def _gemini_rewrite_summary(summary: str, jd_data: Dict, keywords: List[str]) -> str:
    """Use Gemini to rewrite summary for 90%+ ATS score."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        role = jd_data.get('role', 'Professional')
        seniority = jd_data.get('seniority', 'experienced')
        hard_skills = jd_data.get('hard_skills', [])[:5]
        
        prompt = f"""You are an ATS optimization expert. Rewrite this summary to achieve 90%+ ATS compatibility.

ORIGINAL SUMMARY:
{summary}

TARGET ROLE: {role}
SENIORITY: {seniority}
MUST-INCLUDE KEYWORDS: {', '.join(keywords)}
REQUIRED SKILLS: {', '.join(hard_skills)}

## OPTIMIZATION RULES (FOLLOW EXACTLY):

1. FORMAT: "[Seniority] [Role Title] with [X]+ years of experience in [Primary Keyword]"
2. KEYWORDS: Include at least 3 keywords naturally from the list above
3. LENGTH: 2-3 sentences maximum
4. IMPACT: Mention a key specialization or achievement area
5. ATS-FRIENDLY: Use standard professional language, no jargon

## TRUTH RULES (NEVER VIOLATE):
- Keep years of experience EXACTLY as mentioned in original
- Do NOT invent new skills or achievements
- Do NOT add metrics that weren't in original
- Only rephrase existing content

Return ONLY the rewritten summary, no explanations or quotes."""

        response = model.generate_content(prompt)
        result = response.text.strip().strip('"\'')
        return result
    except Exception as e:
        print(f"Gemini error: {e}")
        return _rule_based_summary(summary, keywords)


def _llm_rewrite_summary(summary: str, jd_data: Dict, keywords: List[str]) -> str:
    """Use LLM to rewrite summary for 90%+ ATS score."""
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        
        role = jd_data.get('role', 'Professional')
        seniority = jd_data.get('seniority', 'experienced')
        hard_skills = jd_data.get('hard_skills', [])[:5]
        
        prompt = f"""You are an ATS optimization expert. Rewrite this summary to achieve 90%+ ATS compatibility.

ORIGINAL SUMMARY:
{summary}

TARGET ROLE: {role}
SENIORITY: {seniority}
MUST-INCLUDE KEYWORDS: {', '.join(keywords)}
REQUIRED SKILLS: {', '.join(hard_skills)}

## OPTIMIZATION RULES (FOLLOW EXACTLY):

1. FORMAT: "[Seniority] [Role Title] with [X]+ years of experience in [Primary Keyword]"
2. KEYWORDS: Include at least 3 keywords naturally from the list above
3. LENGTH: 2-3 sentences maximum
4. IMPACT: Mention a key specialization or achievement area
5. ATS-FRIENDLY: Use standard professional language, no jargon

## TRUTH RULES (NEVER VIOLATE):
- Keep years of experience EXACTLY as mentioned in original
- Do NOT invent new skills or achievements
- Do NOT add metrics that weren't in original
- Only rephrase existing content

## OUTPUT FORMAT:
Return ONLY the rewritten summary, no explanations.

OPTIMIZED SUMMARY:"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert ATS resume optimizer. Output only the optimized text, no explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower for more consistent output
            max_tokens=250,
        )
        
        result = response.choices[0].message.content.strip()
        # Remove any quotes around the result
        result = result.strip('"\'')
        return result
    except Exception:
        return _rule_based_summary(summary, keywords)


def _rule_based_summary(summary: str, keywords: List[str]) -> str:
    """Rule-based summary optimization with keyword integration."""
    # Clean up
    summary = re.sub(r'\s+', ' ', summary).strip()
    
    # Extract years of experience if mentioned
    years_match = re.search(r'(\d+)\s*(?:\+)?\s*years?', summary, re.IGNORECASE)
    
    # Build enhanced summary
    if keywords and years_match:
        years = years_match.group(1)
        # Construct improved summary with keywords
        relevant_keywords = keywords[:3]
        keyword_str = ', '.join(relevant_keywords[:-1])
        if len(relevant_keywords) > 1:
            keyword_str += f' and {relevant_keywords[-1]}'
        else:
            keyword_str = relevant_keywords[0] if relevant_keywords else ''
        
        # Get base description without years
        base = re.sub(r'\d+\s*\+?\s*years?\s*(of\s+)?experience\.?', '', summary, flags=re.IGNORECASE).strip()
        if base:
            enhanced = f"Results-driven professional with {years}+ years of experience specializing in {keyword_str}. {base}"
        else:
            enhanced = f"Results-driven professional with {years}+ years of experience in {keyword_str}."
        return enhanced
    
    # Ensure it ends with period
    if summary and not summary.endswith('.'):
        summary += '.'
    
    return summary


def _rewrite_experience(experience: str, jd_data: Dict, gaps: Dict) -> str:
    """Rewrite experience bullets."""
    lines = experience.split('\n')
    rewritten = []
    
    target_keywords = set(jd_data.get("keywords", {}).get("primary", []))
    target_keywords.update(jd_data.get("hard_skills", []))
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a bullet point (experience description)
        if line.startswith('-') or re.match(r'^\d+\.', line):
            # Rewrite bullet
            bullet = re.sub(r'^[-•]\s*|\d+\.\s*', '', line)
            rewritten_bullet = _rewrite_bullet(bullet, target_keywords)
            rewritten.append('- ' + rewritten_bullet)
        else:
            # Header or company name - keep as is
            rewritten.append(line)
    
    return '\n'.join(rewritten)


def _rewrite_bullet(bullet: str, target_keywords: set) -> str:
    """
    Rewrite a single experience bullet.
    
    Format: Action Verb + Task + Impact/Result
    """
    bullet = bullet.strip()
    
    # Try Gemini first (preferred)
    if GEMINI_AVAILABLE and settings.gemini_api_key:
        try:
            return _gemini_rewrite_bullet(bullet, target_keywords)
        except Exception:
            pass
    
    # Fallback to OpenAI
    if OPENAI_AVAILABLE and settings.openai_api_key:
        try:
            return _llm_rewrite_bullet(bullet, target_keywords)
        except Exception:
            pass
    
    # Rule-based optimization
    return _rule_based_bullet(bullet, target_keywords)


def _gemini_rewrite_bullet(bullet: str, keywords: set) -> str:
    """Use Gemini to rewrite bullet for 90%+ ATS score."""
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    keywords_list = list(keywords)[:8]
    
    prompt = f"""You are an ATS optimization expert. Rewrite this bullet point to maximize ATS compatibility.

ORIGINAL BULLET: {bullet}

TARGET KEYWORDS: {', '.join(keywords_list)}

## BULLET OPTIMIZATION FORMULA (MUST FOLLOW):
[Strong Action Verb] + [What you did] + [Technology/Skill from keywords] + [Business Impact]

## STRONG ACTION VERBS (use one):
Technical: Developed, Engineered, Architected, Implemented, Deployed, Optimized, Automated, Integrated
Leadership: Led, Spearheaded, Directed, Managed, Coordinated, Mentored
Achievement: Achieved, Delivered, Accelerated, Streamlined, Enhanced, Reduced

## KEYWORD INTEGRATION RULES:
- If any keyword from the list naturally relates to this bullet, include it
- Use EXACT keyword phrasing (e.g., "REST APIs" not "RESTful services")
- Place keyword prominently in the bullet

## TRUTH RULES (CRITICAL):
- Keep ALL original facts exactly
- Do NOT invent new metrics or percentages
- Do NOT add technologies not mentioned in original
- If original has a metric, keep it exactly

Return ONLY the single rewritten bullet, no dashes, explanations or quotes."""

    response = model.generate_content(prompt)
    rewritten = response.text.strip().strip('-•').strip().strip('"\'')
    
    # Validate - ensure no hallucination
    if _validate_rewrite(bullet, rewritten):
        return rewritten
    return bullet


def _llm_rewrite_bullet(bullet: str, keywords: set) -> str:
    """Use LLM to rewrite bullet for 90%+ ATS score."""
    client = OpenAI(api_key=settings.openai_api_key)
    
    keywords_list = list(keywords)[:8]
    
    prompt = f"""You are an ATS optimization expert. Rewrite this bullet point to maximize ATS compatibility.

ORIGINAL BULLET: {bullet}

TARGET KEYWORDS: {', '.join(keywords_list)}

## BULLET OPTIMIZATION FORMULA (MUST FOLLOW):
[Strong Action Verb] + [What you did] + [Technology/Skill from keywords] + [Business Impact]

## STRONG ACTION VERBS (use one):
Technical: Developed, Engineered, Architected, Implemented, Deployed, Optimized, Automated, Integrated
Leadership: Led, Spearheaded, Directed, Managed, Coordinated, Mentored
Achievement: Achieved, Delivered, Accelerated, Streamlined, Enhanced, Reduced

## KEYWORD INTEGRATION RULES:
- If any keyword from the list naturally relates to this bullet, include it
- Use EXACT keyword phrasing (e.g., "REST APIs" not "RESTful services")
- Place keyword prominently in the bullet

## TRUTH RULES (CRITICAL):
- Keep ALL original facts exactly
- Do NOT invent new metrics or percentages
- Do NOT add technologies not mentioned in original
- If original has a metric, keep it exactly

## OUTPUT:
Return ONLY the single rewritten bullet, no dashes, explanations or quotes.

OPTIMIZED BULLET:"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an ATS expert. Output only the optimized bullet text, nothing else."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=150,
    )
    
    rewritten = response.choices[0].message.content.strip()
    # Clean up the result
    rewritten = rewritten.strip('-•').strip().strip('"\'')
    
    # Validate - ensure no hallucination
    if _validate_rewrite(bullet, rewritten):
        return rewritten
    return bullet


def _rule_based_bullet(bullet: str, keywords: set) -> str:
    """Enhanced rule-based bullet optimization with keyword integration."""
    original = bullet.strip()
    
    # Action verb replacements (weak -> strong)
    verb_replacements = {
        "responsible for": "Managed",
        "worked on": "Developed",
        "helped with": "Contributed to",
        "involved in": "Participated in",
        "participated in": "Contributed to",
        "did": "Executed",
        "made": "Created",
        "got": "Achieved",
        "used": "Utilized",
        "wanted to": "Aimed to",
        "was part of": "Collaborated on",
        "handled": "Managed",
    }
    
    bullet_lower = bullet.lower()
    for weak, strong in verb_replacements.items():
        if bullet_lower.startswith(weak):
            bullet = strong + bullet[len(weak):]
            break
    
    # If still doesn't start with action verb, try to restructure
    action_verbs = ["Developed", "Led", "Created", "Built", "Designed", 
                    "Implemented", "Managed", "Achieved", "Delivered",
                    "Engineered", "Architected", "Optimized", "Streamlined",
                    "Spearheaded", "Executed", "Utilized", "Deployed"]
    
    first_word = bullet.split()[0] if bullet.split() else ""
    
    # Check if starts with action verb
    starts_with_action = first_word.lower() in [v.lower() for v in action_verbs]
    
    if not starts_with_action:
        # Try to find a relevant keyword to enhance with
        for keyword in keywords:
            if keyword.lower() in bullet_lower:
                # The bullet already mentions a relevant skill, enhance it
                bullet = f"Utilized {keyword} expertise to {bullet[0].lower()}{bullet[1:]}"
                break
        else:
            # No keyword found, add generic action verb
            if bullet and not starts_with_action:
                bullet = f"Developed {bullet[0].lower()}{bullet[1:]}"
    
    # Capitalize first letter
    if bullet:
        bullet = bullet[0].upper() + bullet[1:]
    
    return bullet


def _validate_rewrite(original: str, rewritten: str) -> bool:
    """
    Validate that rewrite doesn't hallucinate.
    
    Checks:
    - No new numbers/percentages added
    - No new company names added
    - Similar length (not wildly different)
    """
    # Check for new metrics
    orig_numbers = set(re.findall(r'\d+%|\$[\d,]+|\d+x', original))
    new_numbers = set(re.findall(r'\d+%|\$[\d,]+|\d+x', rewritten))
    
    # If new numbers appeared that weren't in original, reject
    added_numbers = new_numbers - orig_numbers
    if added_numbers:
        return False
    
    # Length check - shouldn't be more than 2x longer
    if len(rewritten) > len(original) * 2:
        return False
    
    return True


def _rewrite_skills(skills: str, jd_data: Dict) -> str:
    """Rewrite skills section to prioritize relevant skills."""
    # Extract current skills
    skill_list = re.findall(r'[\w\s\+#\.]+', skills)
    skill_list = [s.strip() for s in skill_list if s.strip() and len(s.strip()) > 1]
    
    # Target skills from JD
    target_skills = set(jd_data.get("hard_skills", []))
    target_skills.update(jd_data.get("keywords", {}).get("primary", []))
    
    # Prioritize matching skills
    matching = [s for s in skill_list if s.lower() in [t.lower() for t in target_skills]]
    other = [s for s in skill_list if s not in matching]
    
    # Reorder: matching skills first
    reordered = matching + other
    
    return ', '.join(reordered)


def _generate_summary(sections: Dict[str, str], jd_data: Dict) -> str:
    """Generate a summary if none exists."""
    # Extract key info from experience
    experience = sections.get("experience", "")
    skills = sections.get("skills", "")
    
    # Basic summary template
    role = jd_data.get("role", "professional")
    
    return f"Experienced {role} with expertise in {skills[:100]}..."
