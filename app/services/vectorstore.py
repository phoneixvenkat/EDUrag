# app/services/vectorstore.py
"""
Thin wrapper around ChromaDB for:
- creating/getting a collection
- adding chunks
- semantic query
"""

from __future__ import annotations

from typing import List, Dict, Any
import chromadb

# Use a persistent client if available, fall back to in-memory
try:
    client = chromadb.PersistentClient(path="chroma_db")
except Exception:
    client = chromadb.Client()

COLLECTION_NAME = "docs"


def get_collection():
    """
    Get or create the main Chroma collection used for document chunks.
    """
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def _collection():
    """
    Helper used by /v1/health route.
    """
    return get_collection()


def vs_add(chunks: List[Dict[str, Any]]):
    """
    Add chunk dicts to Chroma.

    Each chunk is expected to look like:
        {
            "id": str,              # unique ID per chunk
            "text": str,            # chunk text
            "meta": { ... }         # metadata (page, chunk_id, etc.)
        }

    Returns:
        (ids, info)
        ids:  list of IDs added
        info: {"collection": ..., "count": ...}
    """
    if not chunks:
        return [], {"collection": COLLECTION_NAME, "count": 0}

    col = get_collection()

    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []

    for i, ch in enumerate(chunks):
        cid = str(ch.get("id", f"chunk-{i}"))
        text = ch.get("text", "")
        meta = ch.get("meta", {})

        ids.append(cid)
        docs.append(text)
        metas.append(meta)

    col.add(ids=ids, documents=docs, metadatas=metas)

    info = {
        "collection": col.name,
        "count": col.count(),
    }
    return ids, info


def semantic_query(query: str, top_k: int = 6) -> List[Dict[str, Any]]:
    """
    Run a semantic (vector) query against Chroma.
    Returns a list of dicts with keys: text, score, meta
    """
    col = get_collection()

    if not query.strip():
        return []

    res = col.query(query_texts=[query], n_results=top_k)

    # Chroma returns lists of documents, metadatas, distances
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    results: List[Dict[str, Any]] = []
    for text, meta, dist in zip(docs, metas, dists):
        # Convert distance to a "score" where higher is better
        score = -float(dist)
        results.append(
            {
                "text": text,
                "score": score,
                "meta": meta or {},
            }
        )

    return results
