from app.resume_parser import extract_resume_information
from app.job_parser import extract_job_requirements

resume = "Sam Brown. Executive Head Chef with 10 years experience in culinary arts, menu planning, food safety, and kitchen team management."

job = "Machine Learning Engineer. Required: Python, PyTorch, Machine Learning, SQL. Preferred: Docker. Experience: 2 years."

resume_data = extract_resume_information(resume)
job_data = extract_job_requirements(job)

print("\nRESUME DATA")
print(resume_data.model_dump())

print("\nJOB DATA")
print(job_data.model_dump())