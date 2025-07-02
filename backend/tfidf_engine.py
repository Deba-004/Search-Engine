# backend/tfidf_engine.py
import json
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

class SearchEngine:
    def __init__(self):
        with open('../data/problems.json', 'r') as f:
            self.data = json.load(f)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))

        self.corpus = [self.preprocess(problem['title']) for problem in self.data]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def preprocess(self, text):
        tokens = nltk.word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(w) for w in tokens if w.isalnum() and w not in self.stopwords]
        return " ".join(tokens)

    def search(self, query, difficulty=None, language=None):
        query = self.preprocess(query)
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        results = []
        for idx, score in enumerate(scores):
            if score > 0:
                item = self.data[idx]
                if (not difficulty or item['difficulty'] == difficulty) and \
                   (not language or item['language'] == language):
                    item['score'] = float(score)
                    results.append(item)

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:5]