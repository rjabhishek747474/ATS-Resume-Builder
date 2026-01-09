"""
ATS Optimization Prompts

Structured prompts for LLM-based resume optimization targeting 90%+ ATS scores.
"""

# Master prompt for full resume optimization
FULL_RESUME_OPTIMIZATION_PROMPT = """
You are an expert ATS (Applicant Tracking System) optimization specialist. Your task is to rewrite the provided resume to achieve a 90%+ ATS compatibility score for the target job.

## INPUT DATA

### ORIGINAL RESUME:
{resume_sections}

### TARGET JOB DESCRIPTION:
{job_description}

### EXTRACTED JD REQUIREMENTS:
- Role: {role}
- Seniority: {seniority}
- Required Hard Skills: {hard_skills}
- Required Soft Skills: {soft_skills}
- Key Technologies/Tools: {tools}
- Primary Keywords (MUST include): {primary_keywords}
- Secondary Keywords (should include): {secondary_keywords}

## ATS OPTIMIZATION RULES (MANDATORY)

### 1. KEYWORD INTEGRATION (40% of ATS score)
- Include ALL primary keywords from the JD naturally in the resume
- Place most important keywords in Summary, Skills, and first bullet of each role
- Use EXACT keyword phrases from JD (e.g., "REST APIs" not "RESTful services")
- Repeat critical keywords 2-3 times across different sections
- Match keyword density: aim for 3-5% of total content

### 2. FORMAT REQUIREMENTS (20% of ATS score)
- Use standard section headers: SUMMARY, EXPERIENCE, SKILLS, EDUCATION
- No tables, columns, graphics, or special characters
- Use simple bullet points (-)
- Chronological order for experience (most recent first)
- Include dates in MM/YYYY or YYYY format
- Keep to single-column layout

### 3. EXPERIENCE BULLETS (25% of ATS score)
Each bullet MUST follow this formula:
[Strong Action Verb] + [What you did] + [Technology/Skill used] + [Quantified Result if available]

Strong Action Verbs to use:
- Technical: Developed, Engineered, Architected, Implemented, Deployed, Optimized, Automated, Integrated, Configured, Migrated
- Leadership: Led, Managed, Directed, Spearheaded, Coordinated, Mentored, Supervised
- Achievement: Achieved, Delivered, Improved, Reduced, Increased, Accelerated, Streamlined

### 4. SKILLS SECTION (15% of ATS score)
- List skills matching JD requirements FIRST
- Group by category: Programming Languages | Frameworks | Databases | Cloud/DevOps | Tools
- Use exact skill names from JD
- Include both acronyms and full names for important skills (e.g., "AWS (Amazon Web Services)")

## TRUTH PRESERVATION RULES (CRITICAL - NEVER VIOLATE)

1. **NO fabricated metrics**: Do not invent percentages, dollar amounts, or numbers
2. **NO new skills**: Only include skills the candidate actually has
3. **NO invented companies/roles**: Keep all company names and job titles exactly as provided
4. **NO timeline changes**: Keep dates exactly as provided
5. **PRESERVE meaning**: Rewording is allowed, but the core meaning must stay the same

If a JD requirement cannot be matched because the candidate lacks that skill/experience:
- Do NOT add it to the resume
- Instead, emphasize transferable skills that are closest

## OUTPUT FORMAT

Provide the optimized resume in this exact structure:

```
SUMMARY
[2-3 sentences incorporating role title, years of experience, and 3-5 primary keywords]

EXPERIENCE

[Job Title] | [Company Name] | [Start Date] - [End Date]
- [Bullet 1: Most impressive achievement with primary keyword]
- [Bullet 2: Technical accomplishment with technology keyword]
- [Bullet 3: Leadership/collaboration with soft skill keyword]
- [Bullet 4-6: Additional relevant achievements]

[Repeat for each role]

SKILLS
[Category 1]: [Skill 1], [Skill 2], [Skill 3]
[Category 2]: [Skill 1], [Skill 2], [Skill 3]

EDUCATION
[Degree] | [Institution] | [Year]
[Certifications if any]
```

## OPTIMIZATION CHECKLIST (verify before output)

□ All primary JD keywords appear at least once
□ Role title from JD appears in Summary
□ Every bullet starts with strong action verb
□ Skills section lists JD requirements first
□ No tables, graphics, or special formatting
□ Standard section headers used
□ No fabricated information added
□ Dates are in consistent format

Now optimize the resume:
"""

# Prompt for summary section only
SUMMARY_OPTIMIZATION_PROMPT = """
Rewrite this professional summary to achieve maximum ATS compatibility for the target role.

ORIGINAL SUMMARY:
{summary}

TARGET ROLE: {role}
SENIORITY LEVEL: {seniority}
MUST-INCLUDE KEYWORDS: {keywords}

RULES:
1. Start with: "[Seniority] [Role] with [X] years of experience"
2. Include 3-5 keywords from the list naturally
3. Mention 1-2 key achievements or specializations
4. Keep to 2-3 sentences maximum
5. DO NOT invent new facts - only rephrase existing content

OUTPUT (summary only, no explanation):
"""

# Prompt for experience bullets
BULLET_OPTIMIZATION_PROMPT = """
Rewrite this experience bullet point to be ATS-optimized.

ORIGINAL BULLET: {bullet}
TARGET KEYWORDS: {keywords}
CONTEXT (role/company): {context}

RULES:
1. Format: [Action Verb] + [Task] + [Technology/Skill] + [Result]
2. Start with strong action verb (Developed, Led, Implemented, etc.)
3. Include relevant keyword if the bullet relates to it
4. Keep original facts - do NOT invent metrics or achievements
5. Keep under 2 lines

OPTIMIZED BULLET (one line only):
"""

# Prompt for skills reorganization
SKILLS_OPTIMIZATION_PROMPT = """
Reorganize these skills to maximize ATS score for the target job.

CURRENT SKILLS: {skills}
JD REQUIRED SKILLS: {jd_skills}
JD PREFERRED SKILLS: {preferred_skills}

RULES:
1. List matching JD skills FIRST
2. Group by category (Languages, Frameworks, Databases, Cloud, Tools)
3. Use exact skill names from JD
4. For important skills, include both short and full names
5. Remove irrelevant skills that don't match JD at all
6. DO NOT add skills the candidate doesn't have

OUTPUT FORMAT:
[Category]: [Skill1], [Skill2], [Skill3]

OPTIMIZED SKILLS:
"""

# Validation prompt to check for hallucinations
VALIDATION_PROMPT = """
Compare the original and optimized resume sections. Identify any hallucinations.

ORIGINAL:
{original}

OPTIMIZED:
{optimized}

Check for these violations:
1. New metrics/percentages not in original (e.g., "increased by 50%")
2. New skills not mentioned in original
3. New company names or job titles
4. Changed dates or timelines
5. Invented achievements or responsibilities

RESPONSE FORMAT:
- If NO violations: "VALID"
- If violations found: "INVALID: [list each violation]"

VALIDATION RESULT:
"""
