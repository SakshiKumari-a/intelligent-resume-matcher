
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from pypdf import PdfReader
from app.resume_parser import extract_resume_information
from app.job_parser import extract_job_requirements
from app.scoring import compute_overall_match
from app.explaination import generate_ai_explanation

st.set_page_config(page_title="Intelligent Resume Matcher", layout="wide")
st.title("🎯 INTELLIGENT RESUME MATCHER")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Candidate Resume")
    pdf_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    pasted_resume = st.text_area("Or Paste Resume Text", height=260)
    
    resume_text = ""
    if pdf_file:
        reader = PdfReader(pdf_file)
        resume_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif pasted_resume:
        resume_text = pasted_resume

with col2:
    st.subheader("Job Description")
    job_text = st.text_area("Paste Job Description", height=330)

if st.button("ANALYZE RESUME", type="primary", use_container_width=True):
    if not resume_text.strip() or not job_text.strip():
        st.error("Please provide both a valid resume and a job description.")
    else:
        with st.spinner("Extracting entities with Gemini and running NLP scoring..."):
            try:
                resume_data = extract_resume_information(resume_text)
                job_data = extract_job_requirements(job_text)
                results = compute_overall_match(resume_data, job_data, resume_text, job_text)
                explanation = generate_ai_explanation(results, resume_data.name)
                
                st.markdown("---")
                st.header(f"MATCH SCORE: {results['final_score']}% ({results['recommendation']})")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Experience Match", f"{results['breakdown']['experience_score']}%")
                c2.metric("Education Match", f"{results['breakdown']['education_score']}%")
                c3.metric("TF-IDF Similarity", f"{results['breakdown']['tfidf_similarity']}%")
                
                s1, s2 = st.columns(2)
                
                with s1:
                    st.subheader("Matched Skills")
                    matched_req = [f"✓ {s} *(Required)*" for s in results.get("matched_required", [])]
                    matched_pref = [f"✓ {s} *(Preferred)*" for s in results.get("matched_preferred", [])]
                    all_matched = matched_req + matched_pref
                    
                    if all_matched:
                        for s in all_matched:
                            st.write(s)
                    else:
                        st.info("No matching skills found.")
                        
                with s2:
                    st.subheader("Missing Skills")
                    missing_req = [f"✗ {s} *(Required)*" for s in results.get("missing_required", [])]
                    missing_pref = [f"✗ {s} *(Preferred)*" for s in results.get("missing_preferred", [])]
                    all_missing = missing_req + missing_pref
                    
                    if all_missing:
                        for s in all_missing:
                            st.write(s)
                    else:
                        st.success("None (all required & preferred skills matched).")
                        
                st.markdown("---")
                st.subheader("AI Analysis")
                st.markdown(explanation)
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")