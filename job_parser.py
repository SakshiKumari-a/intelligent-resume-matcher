import re
from app.gemini_client import extract_structured_data, JobRequirements
from app.skill_matcher import normalize_skill

SOFT_SKILLS = {
    "communication",
    "teamwork",
    "collaboration",
    "leadership",
    "adaptability",
    "problem solving",
    "problem-solving",
    "creativity"
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

ALIASES = {
    "aws": "amazon web services",
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


def _extract_skills(text):
    text_lower = text.lower()
    found = set()

    candidates = set(KNOWN_SKILLS) | set(ALIASES.keys())

    for skill in candidates:
        pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill) + r"(?![a-zA-Z0-9+#.])"

        if re.search(pattern, text_lower):
            found.add(ALIASES.get(skill, skill))

    return found


def _extract_years(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"minimum\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"at least\s+(\d+(?:\.\d+)?)\s*\+?\s*years?"
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
    result = []
    text_lower = text.lower()

    if re.search(r"\b(bachelor|bachelors|b\.s\.|bs|b\.e\.|be|b\.tech|btech|bca)\b", text_lower):
        result.append("Bachelor's degree")

    if re.search(r"\b(master|masters|m\.s\.|ms|m\.e\.|me|m\.tech|mtech|mca)\b", text_lower):
        result.append("Master's degree")

    if re.search(r"\b(phd|ph\.d|doctorate)\b", text_lower):
        result.append("PhD")

    return result


def _fallback_job(text):
    skills = _extract_skills(text)
    years = _extract_years(text)
    education = _extract_education(text)

    preferred = set()
    required = set()

    text_lower = text.lower()

    for skill in skills:
        pos = text_lower.find(skill)

        if pos == -1:
            required.add(skill)
            continue

        context = text_lower[max(0, pos - 100):pos + len(skill) + 100]

        if any(word in context for word in [
            "preferred",
            "nice to have",
            "nice-to-have",
            "bonus",
            "plus",
            "optional"
        ]):
            preferred.add(skill)
        else:
            required.add(skill)

    return JobRequirements(
        required_skills=sorted(required),
        preferred_skills=sorted(preferred),
        experience_required=f"{years:g} years" if years else "",
        required_experience_years=years,
        education_required=education
    )


def extract_job_requirements(job_text: str) -> JobRequirements:
    if not job_text or not job_text.strip():
        raise ValueError("Job description text cannot be empty.")

    prompt = f"""
Extract structured job requirements.

Rules:
- required_skills = mandatory technical skills only
- preferred_skills = optional/nice-to-have technical skills only
- required_experience_years = numeric minimum years
- education_required = degree requirements only
- experience_required = human-readable experience requirement

Never put job titles, sentences, education, or experience descriptions inside skills.

JOB DESCRIPTION:
{job_text}
"""

    try:
        data = extract_structured_data(prompt, JobRequirements)

        required = set()
        preferred = set()

        for skill in data.required_skills or []:
            normalized = normalize_skill(skill)

            if normalized in KNOWN_SKILLS:
                required.add(normalized)

        for skill in data.preferred_skills or []:
            normalized = normalize_skill(skill)

            if normalized in KNOWN_SKILLS:
                preferred.add(normalized)

        raw_skills = _extract_skills(job_text)

        for skill in raw_skills:
            pos = job_text.lower().find(skill)

            if pos == -1:
                required.add(skill)
                continue

            context = job_text.lower()[max(0, pos - 120):pos + len(skill) + 120]

            if any(word in context for word in [
                "preferred",
                "nice to have",
                "nice-to-have",
                "bonus",
                "plus",
                "optional"
            ]):
                preferred.add(skill)
            else:
                required.add(skill)

        preferred -= required

        years = data.required_experience_years

        if not years or years <= 0:
            years = _extract_years(job_text)

        education = data.education_required or []

        if not education:
            education = _extract_education(job_text)

        if not required and not preferred:
            return _fallback_job(job_text)

        data.required_skills = sorted(required)
        data.preferred_skills = sorted(preferred)
        data.required_experience_years = float(years)
        data.experience_required = (
            data.experience_required
            if data.experience_required
            else f"{years:g} years" if years else ""
        )
        data.education_required = education

        return data

    except Exception:
        return _fallback_job(job_text)