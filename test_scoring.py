import unittest
from app.scoring import compute_overall_match

class TestScoring(unittest.TestCase):

    def test_excellent_candidate(self):
        """
        TC13 – Excellent Candidate
        Candidate matches all required skills and exceeds experience.
        Expected: Final score > 90%, classification → Excellent Match
        """
        resume_data = type("ResumeData", (), {
            "skills": ["Python", "SQL", "Docker", "AWS", "Git"],
            "years_experience": 5,
            "education": ["Bachelor"]
        })()

        job_data = type("JobRequirements", (), {
            "required_skills": ["Python", "SQL", "Docker", "AWS"],
            "preferred_skills": [],
            "required_experience_years": 3,
            "education_required": ["Bachelor"]
        })()

        result = compute_overall_match(resume_data, job_data,
                                       " ".join(resume_data.skills),
                                       " ".join(job_data.required_skills))
        score = result["final_score"]
        classification = result["recommendation"]

        self.assertGreater(score, 90)
        self.assertEqual(classification, "Excellent Match")

    def test_moderate_candidate(self):
        """
        TC14 – Moderate Candidate
        Candidate matches some skills and meets experience.
        Expected: Final score ~60–75%, classification → Moderate Match
        """
        resume_data = type("ResumeData", (), {
            "skills": ["Python", "SQL", "Git"],
            "years_experience": 3,
            "education": ["Bachelor"]
        })()

        job_data = type("JobRequirements", (), {
            "required_skills": ["Python", "SQL", "Docker", "AWS"],
            "preferred_skills": [],
            "required_experience_years": 3,
            "education_required": ["Bachelor"]
        })()

        result = compute_overall_match(resume_data, job_data,
                                       " ".join(resume_data.skills),
                                       " ".join(job_data.required_skills))
        score = result["final_score"]
        classification = result["recommendation"]

        self.assertTrue(60 <= score <= 75)
        self.assertEqual(classification, "Moderate Match")

    def test_poor_candidate(self):
        """
        TC15 – Poor Candidate
        Candidate has unrelated skills and low experience.
        Expected: Final score < 40%, classification → Poor Match
        """
        resume_data = type("ResumeData", (), {
            "skills": ["Photoshop", "Illustrator"],
            "years_experience": 1,
            "education": ["Bachelor"]
        })()

        job_data = type("JobRequirements", (), {
            "required_skills": ["Python", "SQL", "Docker", "AWS"],
            "preferred_skills": [],
            "required_experience_years": 3,
            "education_required": ["Bachelor"]
        })()

        result = compute_overall_match(resume_data, job_data,
                                       " ".join(resume_data.skills),
                                       " ".join(job_data.required_skills))
        score = result["final_score"]
        classification = result["recommendation"]

        self.assertLess(score, 40)
        self.assertEqual(classification, "Poor Match")

if __name__ == "__main__":
    unittest.main()
