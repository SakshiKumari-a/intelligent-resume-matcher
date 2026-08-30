import unittest
from app.similarity import calculate_tfidf_similarity

class TestSimilarity(unittest.TestCase):

    def test_high_similarity(self):
        """
        TC10 – High Similarity
        Resume and job description are very close.
        Expected: TF-IDF similarity reasonably high (>0.4)
        """
        resume_text = "Python developer with SQL and REST API experience"
        job_description = "Looking for Python developer skilled in SQL and REST APIs"

        similarity_score = calculate_tfidf_similarity(resume_text, job_description)
        self.assertGreater(similarity_score, 0.4)  # relaxed threshold

    def test_low_similarity(self):
        """
        TC11 – Low Similarity
        Resume and job description are unrelated.
        Expected: TF-IDF similarity very low (<0.2)
        """
        resume_text = "Graphic designer skilled in Photoshop"
        job_description = "Backend developer with Python and SQL"

        similarity_score = calculate_tfidf_similarity(resume_text, job_description)
        self.assertLess(similarity_score, 0.2)

    def test_extremely_long_resume(self):
        """
        TC12 – Extremely Long Resume
        Resume text is very large (10,000+ words).
        Expected: Function handles input gracefully and returns a float.
        """
        resume_text = "Python " * 10000  # simulate very long resume
        job_description = "Python developer"

        similarity_score = calculate_tfidf_similarity(resume_text, job_description)
        self.assertIsInstance(similarity_score, float)  # fixed type check

if __name__ == "__main__":
    unittest.main()
