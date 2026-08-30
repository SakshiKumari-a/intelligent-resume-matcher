import re


# ---------------------------------------------------------
# SKILL ALIASES
# ---------------------------------------------------------

SKILL_ALIASES = {
    # Python
    "py": "python",
    "python3": "python",
    "python 3": "python",

    # JavaScript
    "js": "javascript",
    "javascript es6": "javascript",
    "javascript es2015": "javascript",

    # TypeScript
    "ts": "typescript",

    # React
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",

    # Node
    "node.js": "nodejs",
    "node js": "nodejs",

    # PostgreSQL
    "postgres": "postgresql",
    "psql": "postgresql",
    "postgre": "postgresql",
    "postgres db": "postgresql",

    # REST
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",
    "restful": "rest api",

    # Kubernetes
    "k8s": "kubernetes",
    "kube": "kubernetes",

    # AWS
    "aws": "amazon web services",
    "amazon aws": "amazon web services",

    # GCP
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",

    # Machine Learning
    "ml": "machine learning",

    # Natural Language Processing
    "nlp": "natural language processing",

    # Artificial Intelligence
    "ai": "artificial intelligence",

    # Databases
    "sql server": "sql",
    "mysql database": "mysql",

    # CI/CD
    "ci cd": "ci/cd",
    "cicd": "ci/cd",

    # Version control
    "git scm": "git",

    # C++
    "cpp": "c++",
    "c plus plus": "c++",

    # C#
    "c sharp": "c#",
    "csharp": "c#",
}


# ---------------------------------------------------------
# RELATED SKILLS
# ---------------------------------------------------------

RELATED_SKILLS = {
    "python": {
        "python",
        "python programming",
    },

    "javascript": {
        "javascript",
        "js",
        "ecmascript",
    },

    "typescript": {
        "typescript",
        "ts",
    },

    "react": {
        "react",
        "reactjs",
        "react.js",
    },

    "nodejs": {
        "nodejs",
        "node.js",
        "node js",
    },

    "postgresql": {
        "postgresql",
        "postgres",
        "psql",
    },

    "amazon web services": {
        "amazon web services",
        "aws",
        "amazon aws",
    },

    "google cloud platform": {
        "google cloud platform",
        "google cloud",
        "gcp",
    },

    "machine learning": {
        "machine learning",
        "ml",
    },

    "natural language processing": {
        "natural language processing",
        "nlp",
    },

    "kubernetes": {
        "kubernetes",
        "k8s",
    },

    "rest api": {
        "rest api",
        "restful api",
        "rest apis",
        "restful",
    },
}


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name consistently.
    """

    if not skill:
        return ""

    cleaned = str(skill).strip().lower()

    cleaned = cleaned.replace("&", " and ")

    # Preserve # and + for C# / C++
    cleaned = re.sub(r"[^a-z0-9+#./\s-]", " ", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Remove common trailing punctuation
    cleaned = cleaned.rstrip(".,;:")

    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]

    return cleaned


def skill_matches(candidate_skill: str, target_skill: str) -> bool:
    """
    Determine whether two skill strings represent the same skill.
    """

    candidate = normalize_skill(candidate_skill)
    target = normalize_skill(target_skill)

    if not candidate or not target:
        return False

    if candidate == target:
        return True

    candidate_aliases = RELATED_SKILLS.get(candidate, {candidate})
    target_aliases = RELATED_SKILLS.get(target, {target})

    if candidate_aliases.intersection(target_aliases):
        return True

    return False


def match_skills(
    candidate_skills: list[str],
    target_skills: list[str]
) -> dict:

    candidate_normalized = [
        normalize_skill(skill)
        for skill in candidate_skills
        if skill
    ]

    candidate_normalized = list(
        dict.fromkeys(
            skill for skill in candidate_normalized
            if skill
        )
    )

    if not target_skills:
        return {
            "matched": [],
            "missing": [],
            "score": 1.0,
        }

    matched = []
    missing = []

    for target in target_skills:

        found = any(
            skill_matches(candidate, target)
            for candidate in candidate_normalized
        )

        if found:
            matched.append(target)
        else:
            missing.append(target)

    score = len(matched) / len(target_skills)

    return {
        "matched": matched,
        "missing": missing,
        "score": score,
    }