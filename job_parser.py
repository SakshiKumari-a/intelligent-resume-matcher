import re

from app.gemini_client import (
    extract_structured_data,
    JobRequirements,
)
from app.skill_matcher import normalize_skill


MAX_INPUT_LENGTH = 50000


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
    "nextjs",
    "power bi",
    "tableau",
    "excel",
    "snowflake",
    "dbt",
    "airflow",
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
    "restful apis": "rest api",
}


NORMALIZED_KNOWN_SKILLS = {
    normalize_skill(skill)
    for skill in KNOWN_SKILLS
}


def _extract_skills(text: str) -> set[str]:

    text_lower = text.lower()

    found = set()

    candidates = (
        set(KNOWN_SKILLS)
        | set(ALIASES.keys())
    )

    for skill in candidates:

        pattern = (
            r"(?<![a-zA-Z0-9+#.])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9+#.])"
        )

        if re.search(pattern, text_lower):
            found.add(
                ALIASES.get(skill, skill)
            )

    return found


def _extract_years(text: str) -> float:

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\+?\s*years?",
        r"minimum\s+(?:of\s+)?(\d+(?:\.\d+)?)\+?\s*years?",
        r"at least\s+(\d+(?:\.\d+)?)\+?\s*years?",
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


def _extract_education(
    text: str,
) -> list[str]:

    education = []

    text = text.lower()

    if re.search(
        r"\b(bachelor|bachelors|bs|b\.s\.|be|b\.e\.|btech|b\.tech|bca)\b",
        text,
    ):
        education.append(
            "Bachelor's Degree"
        )

    if re.search(
        r"\b(master|masters|ms|m\.s\.|me|m\.e\.|mtech|m\.tech|mca)\b",
        text,
    ):
        education.append(
            "Master's Degree"
        )

    if re.search(
        r"\b(phd|ph\.d|doctorate)\b",
        text,
    ):
        education.append("PhD")

    return education


def _extract_responsibilities(
    text: str,
) -> list[str]:

    responsibilities = []

    lines = text.splitlines()

    keywords = [
        "responsibilities",
        "duties",
        "what you will do",
        "role",
    ]

    capture = False

    for line in lines:

        line = line.strip()

        lower = line.lower()

        if any(
            key in lower
            for key in keywords
        ):
            capture = True
            continue

        if capture:

            if not line:
                continue

            if len(line) < 5:
                continue

            responsibilities.append(
                line
            )

            if len(
                responsibilities
            ) >= 10:
                break

    return responsibilities


def _fallback_job(
    job_text: str,
) -> JobRequirements:

    skills = _extract_skills(
        job_text
    )

    years = _extract_years(
        job_text
    )

    education = (
        _extract_education(
            job_text
        )
    )

    required = set()
    preferred = set()

    text_lower = job_text.lower()

    preference_words = [
        "preferred",
        "nice to have",
        "nice-to-have",
        "bonus",
        "plus",
        "optional",
    ]

    for skill in skills:

        position = text_lower.find(
            skill
        )

        if position == -1:
            required.add(skill)
            continue

        context = text_lower[
            max(0, position - 120):
            position + len(skill) + 120
        ]

        if any(
            word in context
            for word in preference_words
        ):
            preferred.add(skill)
        else:
            required.add(skill)

    return JobRequirements(
        required_skills=sorted(
            required
        ),
        preferred_skills=sorted(
            preferred
        ),
        experience_required=(
            f"{years:g} years"
            if years
            else ""
        ),
        required_experience_years=years,
        education_required=education,
        tools=[],
        technologies=[],
        responsibilities=_extract_responsibilities(
            job_text
        ),
    )


def extract_job_requirements(
    job_text: str,
) -> JobRequirements:

    if not job_text.strip():
        raise ValueError(
            "Job description cannot be empty."
        )

    job_text = job_text[
        :MAX_INPUT_LENGTH
    ]

    prompt = f"""
Extract structured job requirements.

Return JSON only.

Fields:
- required_skills
- preferred_skills
- experience_required
- required_experience_years
- education_required
- tools
- technologies
- responsibilities

Rules:

1. required_skills = mandatory technical skills.
2. preferred_skills = optional skills.
3. Do not invent information.
4. Separate required and preferred skills.
5. required_experience_years must be numeric.
6. responsibilities must be short bullet points.
7. Return empty lists if information is missing.

JOB DESCRIPTION:

{job_text}
"""

    try:

        data = extract_structured_data(
            prompt,
            JobRequirements,
        )

        required = set()
        preferred = set()

        for skill in (
            data.required_skills
            or []
        ):

            normalized = (
                normalize_skill(
                    skill
                )
            )

            if (
                normalized
                in NORMALIZED_KNOWN_SKILLS
            ):
                required.add(
                    normalized
                )

        for skill in (
            data.preferred_skills
            or []
        ):

            normalized = (
                normalize_skill(
                    skill
                )
            )

            if (
                normalized
                in NORMALIZED_KNOWN_SKILLS
            ):
                preferred.add(
                    normalized
                )

        raw_skills = (
            _extract_skills(
                job_text
            )
        )

        for skill in raw_skills:

            position = (
                job_text.lower().find(
                    skill
                )
            )

            if position == -1:
                required.add(skill)
                continue

            context = job_text.lower()[
                max(
                    0,
                    position - 120
                ):
                position
                + len(skill)
                + 120
            ]

            if any(
                word in context
                for word in [
                    "preferred",
                    "nice to have",
                    "nice-to-have",
                    "bonus",
                    "plus",
                    "optional",
                ]
            ):
                preferred.add(
                    skill
                )
            else:
                required.add(
                    skill
                )

        preferred -= required

        years = (
            data.required_experience_years
        )

        if years <= 0:
            years = _extract_years(
                job_text
            )

        education = (
            data.education_required
            or _extract_education(
                job_text
            )
        )

        data.required_skills = sorted(
            required
        )

        data.preferred_skills = sorted(
            preferred
        )

        data.required_experience_years = (
            float(years)
        )

        data.experience_required = (
            data.experience_required
            if data.experience_required
            else (
                f"{years:g} years"
                if years
                else ""
            )
        )

        data.education_required = (
            education
        )

        data.tools = (
            data.tools or []
        )

        data.technologies = (
            data.technologies or []
        )

        data.responsibilities = (
            data.responsibilities
            or _extract_responsibilities(
                job_text
            )
        )

        return data

    except Exception:

        return _fallback_job(
            job_text
        )
