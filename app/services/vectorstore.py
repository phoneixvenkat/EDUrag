import chromadb
from typing import List, Dict, Any
from app.services.embeddings import embed_texts

# In-memory Chroma client & collection
_client = chromadb.Client()
_collection = _client.get_or_create_collection(name="edurag", embedding_function=None)

def vs_add_documents(texts: List[str], metadatas: List[Dict[str, Any]]):
    ids = [f"id_{_collection.count()+i}" for i in range(len(texts))]
    embs = embed_texts(texts)
    _collection.add(documents=texts, metadatas=metadatas, embeddings=embs, ids=ids)
    return ids

def vs_query(query: str, top_k: int = 8):
    q_emb = embed_texts([query])[0]
    out = _collection.query(query_embeddings=[q_emb], n_results=top_k)
    docs = out.get("documents", [[]])[0]
    metas = out.get("metadatas", [[]])[0]
    dists = out.get("distances", [[]])[0]  # smaller is better
    results = []
    for i, t in enumerate(docs):
        results.append({
            "text": t,
            "meta": metas[i] if i < len(metas) else {},
            "score": float(dists[i]) if i < len(dists) else 0.0
        })
    return results

def vs_dump_all_docs():
    # quick dump for summarization: returns [{"text":doc, "meta":{...}}]
    # Chroma has no simple "get all", so query with random vector or maintain your own copy.
    # Here we leverage get to read in blocks if needed; for demo, use a large query on empty string.
    out = _collection.query(query_texts=[""], n_results=max(1000, _collection.count()))
    docs = out.get("documents", [[]])[0]
    metas = out.get("metadatas", [[]])[0]
    return [{"text": d, "meta": metas[i] if i < len(metas) else {}} for i, d in enumerate(docs)]

def vs_stats():
    try:
        return {"count": _collection.count(), "collection": "edurag"}
    except Exception:
        return {"count": None, "collection": "edurag"}
