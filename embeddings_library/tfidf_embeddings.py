# tfidf_embeddings.py
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def generate_tfidf_embedding(text, max_features=100):
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform([text])
    return tfidf_matrix.toarray()[0].tolist()
