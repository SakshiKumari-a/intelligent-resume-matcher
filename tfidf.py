from sklearn.feature_extraction.text import TfidfVectorizer
from app.preprocessing import clean_text

def compute_tfidf_vectors(doc1: str, doc2: str):
    c1 = clean_text(doc1)
    c2 = clean_text(doc2)
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([c1, c2])
    return matrix, vectorizer