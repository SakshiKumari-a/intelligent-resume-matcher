from app.gemini_client import get_gemini_client

def generate_ai_explanation(score_result: dict, resume_name: str) -> str:
    client = get_gemini_client()
    prompt = f"""
    You are an AI hiring assistant. Write an objective summary for candidate: {resume_name}.
    Do NOT modify or recalculate the scores provided below.
    
    Calculated Metrics:
    - Overall Score: {score_result['final_score']}% ({score_result['recommendation']})
    - Matched Required Skills: {', '.join(score_result['matched_required']) or 'None'}
    - Missing Required Skills: {', '.join(score_result['missing_required']) or 'None'}
    - Experience Match: {score_result['breakdown']['experience_score']}%
    - Education Match: {score_result['breakdown']['education_score']}%
    
    Provide:
    1. Candidate Strengths
    2. Skill & Experience Gaps
    3. Recommended Next Steps / Upskilling Areas
    """
    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt
    )
    return response.text
