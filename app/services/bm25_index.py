# app/services/bm25_index.py
"""
Simple in-memory BM25 index for keyword retrieval.

This file MUST provide:
    - add_chunks(doc_id: str, chunks: list[str])  -> None

Optionally, we also expose:
    - query_bm25(query: str, top_k: int = 6) -> list[dict]
    - query(query: str, top_k: int = 6)      -> list[dict]

If the rest of the app imports only `add_chunks`, that's fine.
If it later wants `query(...)`, we also have it implemented here.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------
# Internal global state: VERY simple in-memory BM25 index
# ---------------------------------------------------------------------

_DOCS: List[str] = []          # raw chunk text
_DOC_IDS: List[str] = []       # doc_id for each chunk
_TOKENS: List[List[str]] = []  # tokenized chunks

_IDF: Dict[str, float] = {}    # word -> idf
_AVG_DL: float = 0.0           # average document length

# BM25 parameters
_K1: float = 1.5
_B: float = 0.75


def _tokenize(text: str) -> List[str]:
    """Lowercase + simple word tokenization."""
    return re.findall(r"\b\w+\b", text.lower())


def _recompute_idf() -> None:
    """Recompute IDF and average document length. Called after indexing."""
    global _IDF, _AVG_DL

    n_docs = len(_DOCS)
    if n_docs == 0:
        _IDF = {}
        _AVG_DL = 0.0
        return

    df: Dict[str, int] = {}
    lengths: List[int] = []

    for toks in _TOKENS:
        lengths.append(len(toks))
        seen = set()
        for t in toks:
            if t not in seen:
                df[t] = df.get(t, 0) + 1
                seen.add(t)

    _AVG_DL = sum(lengths) / float(n_docs)
    _IDF = {}

    # Standard BM25-ish idf
    for term, freq in df.items():
        _IDF[term] = math.log(1.0 + (n_docs - freq + 0.5) / (freq + 0.5))


def add_chunks(doc_id: str, chunks: List[str]) -> None:
    """
    Add a list of text chunks for a given document into the BM25 index.

    pipeline.py imports this as:
        from app.services.bm25_index import add_chunks as bm25_add_chunks

    Parameters
    ----------
    doc_id : str
        Identifier for the source document (e.g., filename, UUID).
    chunks : list[str]
        The text chunks to index.
    """
    global _DOCS, _DOC_IDS, _TOKENS

    for ch in chunks:
        if not ch or not ch.strip():
            continue

        _DOCS.append(ch)
        _DOC_IDS.append(doc_id)
        _TOKENS.append(_tokenize(ch))

    _recompute_idf()


def _bm25_score(query_tokens: List[str], doc_tokens: List[str]) -> float:
    """Compute BM25 score of one query against one document."""
    if not doc_tokens or not query_tokens:
        return 0.0

    # Term frequencies in document
    tf: Dict[str, int] = {}
    for t in doc_tokens:
        tf[t] = tf.get(t, 0) + 1

    doc_len = len(doc_tokens)
    score = 0.0

    for term in query_tokens:
        if term not in _IDF:
            continue

        idf = _IDF[term]
        freq = tf.get(term, 0)
        if freq == 0:
            continue

        denom = freq + _K1 * (1.0 - _B + _B * (doc_len / (_AVG_DL or 1.0)))
        score += idf * (freq * (_K1 + 1.0) / denom)

    return score


def query_bm25(query: str, top_k: int = 6) -> List[Dict[str, Any]]:
    """
    Keyword/BM25 search over the indexed chunks.

    Returns a list of dicts:
        {
            "text": <chunk_text>,
            "score": <bm25_score>,
            "meta": {
                "doc_id": <doc_id>,
                "chunk_index": <index_in_internal_list>
            }
        }
    """
    if not _DOCS:
        return []

    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    scored: List[Tuple[int, float]] = []

    for idx, tokens in enumerate(_TOKENS):
        s = _bm25_score(q_tokens, tokens)
        if s > 0.0:
            scored.append((idx, s))

    # sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    scored = scored[:top_k]

    results: List[Dict[str, Any]] = []
    for idx, s in scored:
        results.append(
            {
                "text": _DOCS[idx],
                "score": s,
                "meta": {
                    "doc_id": _DOC_IDS[idx],
                    "chunk_index": idx,
                },
            }
        )

    return results


def query(query: str, top_k: int = 6) -> List[Dict[str, Any]]:
    """
    Generic query function. If the rest of the app imports:
        from app.services.bm25_index import query as bm25_query
    this will also work.
    """
    return query_bm25(query, top_k=top_k)
