from sentence_transformers import SentenceTransformer
from typing import List

# Load pre-trained sentence-transformer model
EMB = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """
    Convert text chunks into embeddings (vector representation).

    :param chunks: A list of document chunks.
    :return: A list of embeddings (vectors) for each chunk.
    """
    embeddings = EMB.encode(chunks, normalize_embeddings=True).tolist()
    return embeddings
