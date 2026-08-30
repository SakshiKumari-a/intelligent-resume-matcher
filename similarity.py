from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_tfidf_similarity(
    resume_text: str,
    job_text: str
) -> float:

    if not resume_text or not job_text:
        return 0.0

    resume_text = resume_text.strip()
    job_text = job_text.strip()

    if not resume_text or not job_text:
        return 0.0

    try:

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
        )

        matrix = vectorizer.fit_transform(
            [resume_text, job_text]
        )

        similarity = cosine_similarity(
            matrix[0:1],
            matrix[1:2]
        )[0][0]

        return float(
            max(
                0.0,
                min(
                    1.0,
                    similarity
                )
            )
        )

    except Exception:
        return 0.0