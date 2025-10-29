from rank_bm25 import BM25Okapi
from typing import List, Dict, Any

_corpus: List[List[str]] = []
_meta: List[Dict[str, Any]] = []
_bm25 = None

def _tok(s: str):
    return [w.lower() for w in s.split()]

def bm25_add_documents(texts: List[str], metadatas: List[Dict[str, Any]]):
    global _bm25
    for t, m in zip(texts, metadatas):
        _corpus.append(_tok(t))
        _meta.append(m)
    _bm25 = BM25Okapi(_corpus) if _corpus else None

def bm25_query(query: str, top_k: int = 8):
    if not _bm25:
        return []
    toks = _tok(query)
    scores = _bm25.get_scores(toks)
    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    results = []
    for i in idxs:
        results.append({
            "text": " ".join(_corpus[i]),
            "meta": _meta[i],
            "score": float(scores[i])  # larger=better
        })
    return results
