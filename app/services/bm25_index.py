from __future__ import annotations
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

_CORPUS: List[str] = []
_IDS: List[str] = []
_TOKENS: List[List[str]] = []
_BM25: BM25Okapi | None = None

def _rebuild():
    global _BM25
    if _CORPUS:
        _BM25 = BM25Okapi(_TOKENS)
    else:
        _BM25 = None

def bm25_add(docs: List[Dict[str, Any]]) -> int:
    global _CORPUS, _IDS, _TOKENS
    if not docs: return len(_CORPUS)
    for d in docs:
        _IDS.append(d["id"])
        _CORPUS.append(d["text"])
        _TOKENS.append(d["text"].lower().split())
    _rebuild()
    return len(_CORPUS)

def bm25_search(query: str, k: int = 6) -> List[Dict[str, Any]]:
    if not _BM25 or not _CORPUS:
        return []
    toks = query.lower().split()
    scores = _BM25.get_scores(toks)
    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    out = []
    for i in idxs:
        out.append({"id": _IDS[i], "text": _CORPUS[i], "meta": {}, "score": float(scores[i])})
    return out
