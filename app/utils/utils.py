import numpy as np
import os
from django.conf import settings
import smart_open

# Load the Google News vectors model using smart_open
model_path = os.path.join(settings.BASE_DIR, 'app', 'GoogleNews-vectors-negative300.bin')




def load_word2vec_model(model_path):
    with smart_open.open(model_path, 'rb') as f:
        header = f.readline()
        vocab_size, vector_size = map(int, header.split())
        word_vectors = {}
        binary_len = np.dtype('float32').itemsize * vector_size
        for _ in range(vocab_size):
            word = []
            while True:
                ch = f.read(1)
                if ch == b' ':
                    word = b''.join(word).decode('utf-8')
                    break
                if ch != b'\n':
                    word.append(ch)
            word_vectors[word] = np.frombuffer(f.read(binary_len), dtype='float32')
    return word_vectors

word_vectors = load_word2vec_model(model_path)

# Function to get embeddings for a given text
def get_embedding(text):
    words = text.split()
    valid_words = [word for word in words if word in word_vectors]
    if not valid_words:
        return None
    embedding = np.mean([word_vectors[word] for word in valid_words], axis=0)
    return embedding

# Function to find similar books
def find_similar_books(query, books, top_n=45):
    query_embedding = get_embedding(query)
    if query_embedding is None:
        return []

    # Compute embeddings for all book titles
    book_titles = [book.book_title.lower() for book in books]
    book_embeddings = [get_embedding(title) for title in book_titles]

    # Compute cosine similarities
    similarities = []
    for embedding in book_embeddings:
        if embedding is not None:
            similarity = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
            similarities.append(similarity)
        else:
            similarities.append(0)

    # Get top_n similar books
    top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_n]
    similar_books = [(books[idx], similarities[idx]) for idx in top_indices]

    return similar_books
