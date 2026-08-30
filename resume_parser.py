import re
from app.gemini_client import extract_structured_data, ResumeData
from app.skill_matcher import normalize_skill

SOFT_SKILLS = {
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "problem-solving",
    "adaptability",
    "creativity",
    "time management",
    "collaboration",
    "team player"
}

KNOWN_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "sql",
    "html",
    "css",
    "react",
    "nodejs",
    "angular",
    "vue",
    "git",
    "docker",
    "kubernetes",
    "terraform",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "rest api",
    "graphql",
    "machine learning",
    "deep learning",
    "natural language processing",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "pandas",
    "numpy",
    "spark",
    "hadoop",
    "aws",
    "amazon web services",
    "gcp",
    "google cloud platform",
    "azure",
    "linux",
    "jenkins",
    "github",
    "gitlab",
    "fastapi",
    "flask",
    "django",
    "spring",
    "spring boot",
    "nextjs",
    "next.js",
    "power bi",
    "tableau",
    "excel",
    "snowflake",
    "dbt",
    "airflow"
}

STOPWORDS = {
    "for", "with", "and", "the", "a", "an", "in", "on", "at", "to", "of",
    "looking", "strong", "motivated", "candidate", "good", "great", "expert",
    "skills", "skill", "experience", "years", "year", "work", "working",
    "developer", "engineer", "senior", "junior", "software", "professional",
    "required", "preferred", "knowledge", "using", "including", "etc"
}


def _clean_skill(value):
    if not value:
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)

    if value in STOPWORDS:
        return ""

    normalized = normalize_skill(value)

    if normalized in STOPWORDS:
        return ""

    return normalized


def _extract_known_skills(text):
    text_lower = text.lower()
    found = set()

    aliases = {
        "aws": "amazon web services",
        "amazon web services": "amazon web services",
        "gcp": "google cloud platform",
        "k8s": "kubernetes",
        "reactjs": "react",
        "react.js": "react",
        "node.js": "nodejs",
        "postgres": "postgresql",
        "psql": "postgresql",
        "ml": "machine learning",
        "nlp": "natural language processing",
        "restful api": "rest api",
        "restful apis": "rest api"
    }

    candidates = set(KNOWN_SKILLS) | set(aliases.keys())

    for skill in candidates:
        pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill) + r"(?![a-zA-Z0-9+#.])"

        if re.search(pattern, text_lower):
            found.add(aliases.get(skill, skill))

    return found


def _extract_years(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?"
    ]

    values = []

    for pattern in patterns:
        for match in re.finditer(pattern, text.lower()):
            try:
                values.append(float(match.group(1)))
            except ValueError:
                pass

    return max(values) if values else 0.0


def _extract_education(text):
    education = []

    patterns = [
        r"\b(?:bachelor|bachelors|b\.s\.|bs|b\.e\.|be|b\.tech|btech|bca)\b[^.\n;]*",
        r"\b(?:master|masters|m\.s\.|ms|m\.e\.|me|m\.tech|mtech|mca)\b[^.\n;]*",
        r"\b(?:phd|ph\.d|doctorate)\b[^.\n;]*"
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = re.sub(r"\s+", " ", match.group(0)).strip()

            if value and value not in education:
                education.append(value)

    return education


def _fallback_resume(text):
    skills = _extract_known_skills(text)
    years = _extract_years(text)
    education = _extract_education(text)

    soft = set()

    for skill in SOFT_SKILLS:
        if skill in text.lower():
            soft.add(skill)

    return ResumeData(
        name="",
        skills=sorted(skills),
        soft_skills=sorted(soft),
        experience=[],
        years_experience=years,
        education=education,
        projects=[],
        certifications=[],
        tools=[]
    )


def extract_resume_information(resume_text: str) -> ResumeData:
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    prompt = f"""
Extract structured resume information.

Return only the requested structured fields.

Rules:
- name = candidate name only
- skills = technical skills only
- soft_skills = soft skills only
- years_experience = numeric years of professional experience
- education = degree/education information only
- projects = project descriptions
- certifications = certifications
- tools = software/tools

Never put names, job titles, education, or complete sentences inside skills.

RESUME:
{resume_text}
"""

    try:
        data = extract_structured_data(prompt, ResumeData)

        technical = set()
        soft = set()

        for skill in data.skills or []:
            cleaned = _clean_skill(skill)

            if not cleaned:
                continue

            if cleaned in SOFT_SKILLS:
                soft.add(cleaned)
            elif cleaned in KNOWN_SKILLS or cleaned in {
                normalize_skill(x) for x in KNOWN_SKILLS
            }:
                technical.add(cleaned)

        for skill in data.soft_skills or []:
            cleaned = _clean_skill(skill)

            if cleaned:
                soft.add(cleaned)

        raw_skills = _extract_known_skills(resume_text)

        if not technical:
            technical.update(raw_skills)
        else:
            technical.update(raw_skills)

        years = data.years_experience

        if not years or years <= 0:
            years = _extract_years(resume_text)

        education = data.education or []

        if not education:
            education = _extract_education(resume_text)

        if not technical and not soft and not education and years == 0:
            return _fallback_resume(resume_text)

        data.skills = sorted(technical)
        data.soft_skills = sorted(soft)
        data.years_experience = float(years)
        data.education = education

        return data

    except Exception:
        return _fallback_resume(resume_text)