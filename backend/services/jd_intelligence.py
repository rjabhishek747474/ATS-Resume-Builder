"""
Job Description Intelligence Service

Extracts structured information from job descriptions.
"""

import re
from typing import Dict, List, Set


# Common tech skills database
TECH_SKILLS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html", "css",
    
    # Frameworks
    "react", "angular", "vue", "node.js", "nodejs", "express", "django", "flask",
    "fastapi", "spring", "spring boot", ".net", "rails", "laravel", "nextjs",
    
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
    "oracle", "sql server", "sqlite", "cassandra", "neo4j",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "jenkins", "gitlab", "github actions", "ci/cd",
    
    # Data & ML
    "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "spark",
    "hadoop", "kafka", "airflow", "machine learning", "deep learning",
    
    # Tools
    "git", "jira", "confluence", "figma", "postman", "linux", "unix",
}

# Soft skills
SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving",
    "analytical", "collaboration", "mentoring", "agile", "scrum",
    "project management", "stakeholder management", "presentation",
    "critical thinking", "attention to detail", "time management",
}

# Seniority indicators
SENIORITY_PATTERNS = {
    "senior": [r"(?i)\bsenior\b", r"(?i)\bsr\.?\b", r"(?i)\blead\b", r"(?i)\bstaff\b"],
    "mid": [r"(?i)\bmid[\s-]?level\b", r"(?i)\bintermediate\b"],
    "junior": [r"(?i)\bjunior\b", r"(?i)\bjr\.?\b", r"(?i)\bentry[\s-]?level\b"],
    "principal": [r"(?i)\bprincipal\b", r"(?i)\barchitect\b", r"(?i)\bdirector\b"],
}


def extract_jd_intelligence(text: str) -> Dict:
    """
    Extract structured intelligence from job description.
    """
    text_lower = text.lower()
    
    # Extract role
    role = _extract_role(text)
    seniority = _detect_seniority(text)
    
    # Extract skills
    hard_skills = _extract_hard_skills(text_lower)
    soft_skills = _extract_soft_skills(text_lower)
    tools = _extract_tools(text_lower)
    
    # Extract keywords
    keywords = _extract_keywords(text, hard_skills)
    
    return {
        "role": role,
        "seniority": seniority,
        "hard_skills": list(hard_skills),
        "soft_skills": list(soft_skills),
        "tools": list(tools),
        "keywords": keywords,
    }


def _extract_role(text: str) -> str:
    """Extract job title from JD."""
    lines = text.split('\n')
    
    # Usually first non-empty line is the title
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) < 100:
            # Clean up common prefixes
            line = re.sub(r'^(job\s+title|position|role):\s*', '', line, flags=re.I)
            if line:
                return line
    
    return "Software Engineer"


def _detect_seniority(text: str) -> str:
    """Detect seniority level from JD."""
    for level, patterns in SENIORITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return level
    return "mid"


def _extract_hard_skills(text: str) -> Set[str]:
    """Extract technical/hard skills."""
    found = set()
    
    for skill in TECH_SKILLS:
        # Match whole words
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.I):
            found.add(skill.title() if len(skill) > 3 else skill.upper())
    
    return found


def _extract_soft_skills(text: str) -> Set[str]:
    """Extract soft skills."""
    found = set()
    
    for skill in SOFT_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.I):
            found.add(skill.title())
    
    return found


def _extract_tools(text: str) -> Set[str]:
    """Extract tools and platforms."""
    tools = set()
    
    tool_patterns = [
        r'\b(Jira|Confluence|Slack|Teams)\b',
        r'\b(VS\s*Code|Visual Studio|IntelliJ|PyCharm)\b',
        r'\b(Figma|Sketch|Adobe\s+\w+)\b',
        r'\b(Datadog|Splunk|New Relic|Grafana)\b',
    ]
    
    for pattern in tool_patterns:
        matches = re.findall(pattern, text, re.I)
        tools.update(m.strip() for m in matches)
    
    return tools


def _extract_keywords(text: str, hard_skills: Set[str]) -> Dict[str, List[str]]:
    """
    Extract ATS keywords categorized by importance.
    
    Primary: Likely used for filtering
    Secondary: Used for ranking
    """
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    word_freq = {}
    
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Primary keywords: hard skills that appear multiple times
    primary = [s for s in hard_skills if word_freq.get(s.lower(), 0) >= 2]
    
    # Secondary: other skills
    secondary = [s for s in hard_skills if s not in primary]
    
    return {
        "primary": primary[:10],
        "secondary": secondary[:10],
    }
