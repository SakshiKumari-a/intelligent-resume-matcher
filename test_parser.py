import unittest
from app.resume_parser import extract_resume_information
from app.job_parser import extract_job_requirements

class TestParser(unittest.TestCase):

    def test_empty_resume(self):
        """
        TC01 – Empty Resume
        Input: ""
        Expected: Raises ValueError
        """
        resume_text = ""
        with self.assertRaises(ValueError):
            extract_resume_information(resume_text)

    def test_soft_skills_only(self):
        """
        TC02 – Resume with Only Soft Skills
        Input: "Team player, good communication, leadership"
        Expected: Soft skills captured, technical empty
        """
        resume_text = "Team player, good communication, leadership"
        result = extract_resume_information(resume_text)

        normalized_skills = [s.lower() for s in result.skills]
        self.assertIn("communication", normalized_skills)
        self.assertIn("leadership", normalized_skills)
        self.assertEqual(result.experience, [])
        self.assertEqual(result.education, [])

    def test_job_missing_required_skills(self):
        """
        TC03 – Job Description Missing Required Skills
        Input: "Looking for a motivated candidate with strong teamwork"
        Expected: Required empty, preferred contains teamwork
        """
        job_description = "Looking for a motivated candidate with strong teamwork"
        result = extract_job_requirements(job_description)

        self.assertEqual(result.required_skills, [])
        self.assertIn("teamwork", [s.lower() for s in result.preferred_skills])

    def test_resume_with_abbreviations(self):
        """
        TC04 – Resume with Abbreviations
        Input: "Expert in JS, ML, NLP"
        Expected: Normalized skills → ["javascript", "machine learning", "natural language processing"]
        """
        resume_text = "Expert in JS, ML, NLP"
        result = extract_resume_information(resume_text)

        normalized_skills = [s.lower() for s in result.skills]
        self.assertIn("javascript", normalized_skills)
        self.assertIn("machine learning", normalized_skills)
        self.assertIn("natural language processing", normalized_skills)

if __name__ == "__main__":
    unittest.main()