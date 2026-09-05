import re

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
    "postgre": "postgresql",
    "psql": "postgresql",
    "postgres db": "postgresql",

    # REST APIs
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

    # AI/ML
    "ml": "machine learning",
    "nlp": "natural language processing",
    "ai": "artificial intelligence",

    # Databases
    "sql server": "sql",
    "mysql database": "mysql",

    # CI/CD
    "cicd": "ci/cd",
    "ci cd": "ci/cd",

    # Version Control
    "git scm": "git",

    # C++
    "cpp": "c++",
    "c plus plus": "c++",

    # C#
    "csharp": "c#",
    "c sharp": "c#",
}

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
        "predictive modeling",
    },

    "natural language processing": {
        "natural language processing",
        "nlp",
        "text mining",
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

    "docker": {
        "docker",
        "docker containers",
    },

    "tensorflow": {
        "tensorflow",
        "tf",
    },

    "pytorch": {
        "pytorch",
        "torch",
    },

    "sql": {
        "sql",
        "sql server",
    },

    "git": {
        "git",
        "git scm",
    },
}


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name consistently.
    """

    if not skill:
        return ""

    skill = str(skill).strip().lower()

    skill = skill.replace("&", " and ")

    # Keep + and # for C++ / C#
    skill = re.sub(
        r"[^a-z0-9+#./\s-]",
        " ",
        skill
    )

    skill = re.sub(
        r"\s+",
        " ",
        skill
    ).strip()

    skill = skill.rstrip(".,;:")

    if skill in SKILL_ALIASES:
        return SKILL_ALIASES[skill]

    return skill


def skill_matches(
    candidate_skill: str,
    target_skill: str,
) -> bool:
    """
    Determine whether two skills
    represent the same technology.
    """

    candidate = normalize_skill(
        candidate_skill
    )

    target = normalize_skill(
        target_skill
    )

    if not candidate or not target:
        return False

    if candidate == target:
        return True

    candidate_aliases = RELATED_SKILLS.get(
        candidate,
        {candidate},
    )

    target_aliases = RELATED_SKILLS.get(
        target,
        {target},
    )

    if candidate_aliases.intersection(
        target_aliases
    ):
        return True

    if candidate in target:
        return True

    if target in candidate:
        return True

    return False

def match_skills(
    candidate_skills: list[str],
    target_skills: list[str],
) -> dict:
    """
    Compare candidate skills
    against job skills.
    """

    candidate_normalized = [
        normalize_skill(skill)
        for skill in candidate_skills
        if skill
    ]

    candidate_normalized = list(
        dict.fromkeys(
            skill
            for skill in candidate_normalized
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
            skill_matches(
                candidate,
                target,
            )
            for candidate in candidate_normalized
        )

        if found:
            matched.append(target)
        else:
            missing.append(target)

    score = (
        len(matched)
        / len(target_skills)
        if target_skills
        else 1.0
    )

    return {
        "matched": matched,
        "missing": missing,
        "score": round(score, 4),
    }
