import re

from app.gemini_client import (
    extract_structured_data,
    ResumeData,
)
from app.skill_matcher import normalize_skill


MAX_INPUT_LENGTH = 50000


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
    "team player",
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
    "amazon web services",
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
    "power bi",
    "tableau",
    "snowflake",
    "airflow",
}


NORMALIZED_KNOWN_SKILLS = {
    normalize_skill(skill)
    for skill in KNOWN_SKILLS
}


def _clean_skill(skill: str) -> str:
    if not skill:
        return ""

    skill = str(skill).strip().lower()
    skill = re.sub(r"\s+", " ", skill)

    return normalize_skill(skill)


def _extract_known_skills(text: str) -> set[str]:

    text = text.lower()

    aliases = {
        "aws": "amazon web services",
        "gcp": "google cloud platform",
        "k8s": "kubernetes",
        "react.js": "react",
        "reactjs": "react",
        "node.js": "nodejs",
        "postgres": "postgresql",
        "ml": "machine learning",
        "nlp": "natural language processing",
        "restful api": "rest api",
        "restful apis": "rest api",
    }

    found = set()

    candidates = (
        set(KNOWN_SKILLS)
        | set(aliases.keys())
    )

    for skill in candidates:

        pattern = (
            r"(?<![a-zA-Z0-9+#.])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9+#.])"
        )

        if re.search(pattern, text):
            found.add(
                aliases.get(skill, skill)
            )

    return found


def _extract_years(text: str) -> float:

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\+?\s*years?",
        r"(\d+(?:\.\d+)?)\+?\s*years?",
    ]

    values = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text.lower()
        ):
            try:
                values.append(
                    float(match.group(1))
                )
            except ValueError:
                pass

    return max(values) if values else 0.0


def _extract_education(text: str) -> list[str]:

    education = []

    patterns = [
        r"\b(?:bachelor|bachelors|bs|b\.s\.|be|b\.e\.|btech|b\.tech|bca)\b[^\n.;]*",
        r"\b(?:master|masters|ms|m\.s\.|me|m\.e\.|mtech|m\.tech|mca)\b[^\n.;]*",
        r"\b(?:phd|ph\.d|doctorate)\b[^\n.;]*",
    ]

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE,
        ):

            value = re.sub(
                r"\s+",
                " ",
                match.group(0)
            ).strip()

            if value and value not in education:
                education.append(value)

    return education


def _fallback_resume(
    resume_text: str,
) -> ResumeData:

    skills = sorted(
        _extract_known_skills(
            resume_text
        )
    )

    years = _extract_years(
        resume_text
    )

    education = _extract_education(
        resume_text
    )

    soft_skills = []

    for skill in SOFT_SKILLS:

        if skill in resume_text.lower():
            soft_skills.append(skill)

    return ResumeData(
        name="",
        skills=skills,
        soft_skills=sorted(
            soft_skills
        ),
        experience=[],
        years_experience=years,
        education=education,
        projects=[],
        certifications=[],
        tools=[],
    )


def extract_resume_information(
    resume_text: str,
) -> ResumeData:

    if not resume_text.strip():
        raise ValueError(
            "Resume text cannot be empty."
        )

    resume_text = resume_text[
        :MAX_INPUT_LENGTH
    ]

    prompt = f"""
Extract structured resume information.

Return JSON only.

Fields:
- name
- skills
- soft_skills
- experience
- years_experience
- education
- projects
- certifications
- tools

Rules:
1. Extract only information present in the resume.
2. Do not invent information.
3. Skills must contain technical skills only.
4. Soft skills must contain interpersonal skills only.
5. years_experience must be numeric.
6. Return empty lists if information is missing.

Resume:

{resume_text}
"""

    try:

        data = extract_structured_data(
            prompt,
            ResumeData,
        )

        technical_skills = set()
        soft_skills = set()

        for skill in data.skills:

            cleaned = _clean_skill(
                skill
            )

            if not cleaned:
                continue

            if cleaned in SOFT_SKILLS:
                soft_skills.add(
                    cleaned
                )
            elif (
                cleaned
                in NORMALIZED_KNOWN_SKILLS
            ):
                technical_skills.add(
                    cleaned
                )

        for skill in data.soft_skills:

            cleaned = _clean_skill(
                skill
            )

            if cleaned:
                soft_skills.add(
                    cleaned
                )

        technical_skills.update(
            _extract_known_skills(
                resume_text
            )
        )

        years = (
            data.years_experience
            if data.years_experience > 0
            else _extract_years(
                resume_text
            )
        )

        education = (
            data.education
            if data.education
            else _extract_education(
                resume_text
            )
        )

        data.skills = sorted(
            technical_skills
        )

        data.soft_skills = sorted(
            soft_skills
        )

        data.years_experience = float(
            years
        )

        data.education = education

        data.projects = (
            data.projects or []
        )

        data.certifications = (
            data.certifications or []
        )

        data.tools = (
            data.tools or []
        )

        data.experience = (
            data.experience or []
        )

        return data

    except Exception:
        return _fallback_resume(
            resume_text
        )
