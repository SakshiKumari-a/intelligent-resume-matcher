from app.gemini_client import extract_structured_data, ResumeData

text = """
John Doe
Python SQL Docker AWS
5 years experience
Bachelor Computer Science
"""

try:
    result = extract_structured_data(text, ResumeData)
    print("SUCCESS")
    print(result.model_dump())
except Exception as e:
    print("ERROR")
    print(e)