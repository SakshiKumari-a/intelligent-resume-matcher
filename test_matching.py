import unittest
from app.skill_matcher import match_skills

class TestMatching(unittest.TestCase):

    def test_exact_skill_match_success(self):
        """
        TC05 – Exact Skill Match Success
        Resume: ["Python", "SQL", "Git"]
        Job: ["Python", "SQL", "Docker", "AWS"]
        Expected: Matched → ["Python", "SQL"]
                  Missing → ["Docker", "AWS"]
        """
        resume_skills = ["Python", "SQL", "Git"]
        job_required_skills = ["Python", "SQL", "Docker", "AWS"]

        result = match_skills(resume_skills, job_required_skills)

        self.assertIn("Python", result["matched"])
        self.assertIn("SQL", result["matched"])
        self.assertIn("Docker", result["missing"])
        self.assertIn("AWS", result["missing"])
        self.assertNotIn("Git", result["matched"])

    def test_missing_required_skills(self):
        """
        TC06 – Resume lacks job skills
        Resume: ["HTML", "CSS"]
        Job: ["Python", "SQL"]
        Expected: No matches, all job skills missing
        """
        resume_skills = ["HTML", "CSS"]
        job_required_skills = ["Python", "SQL"]

        result = match_skills(resume_skills, job_required_skills)

        self.assertEqual(result["matched"], [])
        self.assertIn("Python", result["missing"])
        self.assertIn("SQL", result["missing"])

    def test_synonym_recognition(self):
        """
        TC07 – Synonym Recognition
        Resume: ["Machine Learning"]
        Job: ["ML"]
        Expected: Match recognized via alias dictionary
        """
        resume_skills = ["Machine Learning"]
        job_required_skills = ["ML"]

        result = match_skills(resume_skills, job_required_skills)

        self.assertIn("ML", result["matched"])

    def test_false_positive_prevention(self):
        """
        TC08 – False Positive Prevention
        Resume: ["JavaScript"]
        Job: ["Java"]
        Expected: No match (Java ≠ JavaScript)
        """
        resume_skills = ["JavaScript"]
        job_required_skills = ["Java"]

        result = match_skills(resume_skills, job_required_skills)

        self.assertEqual(result["matched"], [])

    def test_keyword_repetition(self):
        """
        TC09 – Keyword Repetition
        Resume: ["Python", "Python", "Python"]
        Job: ["Python", "SQL"]
        Expected: Match counted once, repetition does not inflate score
        """
        resume_skills = ["Python", "Python", "Python"]
        job_required_skills = ["Python", "SQL"]

        result = match_skills(resume_skills, job_required_skills)

        self.assertEqual(result["matched"].count("Python"), 1)
        self.assertIn("SQL", result["missing"])

if __name__ == "__main__":
    unittest.main()
