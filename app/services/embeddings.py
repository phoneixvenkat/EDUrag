from sentence_transformers import SentenceTransformer
from typing import List

_model = None

def get_model(name: str = "all-MiniLM-L6-v2"):
    global _model
    if _model is None:
        _model = SentenceTransformer(name)
    return _model

def embed_texts(texts: List[str]):
    model = get_model()
    return model.encode(texts, normalize_embeddings=True)
