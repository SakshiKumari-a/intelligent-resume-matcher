import re

from app.skill_matcher import match_skills
from app.similarity import calculate_tfidf_similarity
from app.gemini_client import ResumeData, JobRequirements

WEIGHTS = {
    "required_skills": 0.55,
    "preferred_skills": 0.10,
    "tfidf": 0.05,
    "experience": 0.15,
    "education": 0.10,
    "project_bonus": 0.05,
}

DEGREE_MAPPINGS = {
    "bachelor": [
        "bachelor", "bachelors", "b.s", "bs", "bsc", "b.sc",
        "btech", "b.tech", "be", "b.e", "bca", "undergraduate"
    ],
    "master": [
        "master", "masters", "m.s", "ms", "msc", "m.sc",
        "mtech", "m.tech", "mca", "postgraduate"
    ],
    "phd": ["phd", "ph.d", "doctorate"],
}

DISCIPLINE_MAPPINGS = {
    "computer science": ["computer science", "computer sciences", "cs", "cse"],
    "information technology": ["information technology", "it"],
    "software engineering": ["software engineering"],
    "data": ["data science", "analytics", "statistics", "mathematics", "math"],
}


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_experience_score(candidate_exp, required_exp):
    candidate_exp = _safe_float(candidate_exp)
    required_exp = _safe_float(required_exp)

    if required_exp <= 0:
        return 1.0

    return min(1.0, max(0.0, candidate_exp / required_exp))


def normalize_edu_string(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-zA-Z0-9.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _contains_alias(text, aliases):
    text = normalize_edu_string(text)

    for alias in aliases:
        alias = normalize_edu_string(alias)

        if not alias:
            continue

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(alias)
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, text):
            return True

    return False


def _education_requirement_matches(candidate_text, requirement):
    requirement = normalize_edu_string(requirement)
    candidate_text = normalize_edu_string(candidate_text)

    if not requirement or not candidate_text:
        return False

    required_degree = None

    for degree_name, aliases in DEGREE_MAPPINGS.items():
        if _contains_alias(requirement, aliases):
            required_degree = degree_name
            break

    if required_degree:
        if not _contains_alias(
            candidate_text,
            DEGREE_MAPPINGS[required_degree]
        ):
            return False

    required_fields = []

    for field_name, aliases in DISCIPLINE_MAPPINGS.items():
        if _contains_alias(requirement, aliases):
            required_fields.append(field_name)

    if required_fields:
        if not any(
            _contains_alias(
                candidate_text,
                DISCIPLINE_MAPPINGS[field_name]
            )
            for field_name in required_fields
        ):
            return False

    if not required_degree and not required_fields:
        req_words = {
            word
            for word in re.findall(r"[a-z0-9]+", requirement)
            if len(word) >= 4
        }

        candidate_words = set(
            re.findall(r"[a-z0-9]+", candidate_text)
        )

        return bool(req_words.intersection(candidate_words))

    return True


def calculate_education_score(candidate_edu, required_edu):
    candidate_edu = candidate_edu or []
    required_edu = required_edu or []

    if not required_edu:
        return 1.0

    if not candidate_edu:
        return 0.0

    candidate_text = " ".join(
        str(item)
        for item in candidate_edu
        if item
    )

    if not candidate_text.strip():
        return 0.0

    matches = sum(
        1
        for requirement in required_edu
        if _education_requirement_matches(
            candidate_text,
            requirement
        )
    )

    return matches / len(required_edu)


def calculate_project_bonus(resume_data, job_data):
    projects = resume_data.projects or []
    required_skills = job_data.required_skills or []

    if not projects or not required_skills:
        return 0.0

    project_text = " ".join(
        str(project)
        for project in projects
    ).lower()

    if not project_text.strip():
        return 0.0

    from app.skill_matcher import normalize_skill

    matched = 0

    for skill in required_skills:
        normalized = normalize_skill(skill)

        if normalized in project_text:
            matched += 1
            continue

        words = normalized.split()

        if words and all(word in project_text for word in words):
            matched += 1

    return min(1.0, matched / len(required_skills))


def compute_overall_match(
    resume_data: ResumeData,
    job_data: JobRequirements,
    raw_resume: str,
    raw_job: str
):
    req_match = match_skills(
        resume_data.skills or [],
        job_data.required_skills or []
    )

    pref_match = match_skills(
        resume_data.skills or [],
        job_data.preferred_skills or []
    )

    try:
        tfidf_sim = _safe_float(
            calculate_tfidf_similarity(
                raw_resume or "",
                raw_job or ""
            )
        )
        tfidf_sim = min(1.0, max(0.0, tfidf_sim))
    except Exception:
        tfidf_sim = 0.0

    exp_score = calculate_experience_score(
        getattr(resume_data, "years_experience", 0.0),
        getattr(job_data, "required_experience_years", 0.0)
    )

    edu_score = calculate_education_score(
        getattr(resume_data, "education", []) or [],
        getattr(job_data, "education_required", []) or []
    )

    project_bonus = calculate_project_bonus(
        resume_data,
        job_data
    )

    required_score = req_match["score"]
    preferred_score = pref_match["score"]

    candidate_years = _safe_float(
        getattr(resume_data, "years_experience", 0.0)
    )

    required_years = _safe_float(
        getattr(job_data, "required_experience_years", 0.0)
    )

    if candidate_years <= 0 and required_years > 0:
        effective_experience = min(
            0.50,
            project_bonus
        )
    else:
        effective_experience = exp_score

    final_score = (
        required_score * WEIGHTS["required_skills"]
        + preferred_score * WEIGHTS["preferred_skills"]
        + tfidf_sim * WEIGHTS["tfidf"]
        + effective_experience * WEIGHTS["experience"]
        + edu_score * WEIGHTS["education"]
        + project_bonus * WEIGHTS["project_bonus"]
    ) * 100

    final_score = round(
        min(100.0, max(0.0, final_score)),
        2
    )

    if required_score >= 0.90 and final_score >= 90:
        recommendation = "Excellent Match"
    elif required_score >= 0.75 and final_score >= 75:
        recommendation = "Strong Match"
    elif required_score >= 0.50 and final_score >= 60:
        recommendation = "Moderate Match"
    elif required_score > 0 and final_score >= 40:
        recommendation = "Weak Match"
    else:
        recommendation = "Poor Match"

    return {
        "final_score": final_score,
        "recommendation": recommendation,
        "breakdown": {
            "required_skills_score": round(
                required_score * 100,
                2
            ),
            "preferred_skills_score": round(
                preferred_score * 100,
                2
            ),
            "tfidf_similarity": round(
                tfidf_sim * 100,
                2
            ),
            "experience_score": round(
                effective_experience * 100,
                2
            ),
            "education_score": round(
                edu_score * 100,
                2
            ),
            "project_bonus": round(
                project_bonus * 100,
                2
            ),
        },
        "matched_required": req_match["matched"],
        "missing_required": req_match["missing"],
        "matched_preferred": pref_match["matched"],
        "missing_preferred": pref_match["missing"],
    }