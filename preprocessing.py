import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')

STOP_WORDS = set(stopwords.words('english'))

def clean_text(text: str) -> str:
    """Preprocesses text: lowercases, removes non-alphanumerics, strips stop words."""
    if not text:
        return ""
    text = text.lower()
    # Keep +, #, . for terms like C++, C#, .NET, React.js
    text = re.sub(r'[^a-zA-Z0-9\s+#.]', ' ', text)
    tokens = word_tokenize(text)
    filtered = [w for w in tokens if w not in STOP_WORDS and len(w) > 1]
    return " ".join(filtered)